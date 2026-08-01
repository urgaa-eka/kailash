"""Build audit: every COPY/ADD source must resolve inside its build context."""
from __future__ import annotations

import json
import posixpath
import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from scripts.verify import build_audit
from scripts.verify.common import Exit, Report, git_top_level, tracked_files

# The nine platform services docker-compose.yml builds from Dockerfile.service.
NINE_SERVICES = (
    "document-ai", "forecasting", "anomaly", "rag", "vision-gateway",
    "speech", "model-registry", "knowledge-graph", "automobile-llm",
)


def _run(root, capsys) -> tuple[int, str]:
    rc = build_audit.main(["--root", str(root)])
    return rc, capsys.readouterr().out


def _compose_single(dockerfile: str = "Dockerfile", context: str = ".",
                    args: dict | None = None, service: str = "app") -> str:
    body = (f"services:\n  {service}:\n    build:\n"
            f"      context: {context}\n      dockerfile: {dockerfile}\n")
    if args:
        rendered = ", ".join(f"{k}: \"{v}\"" for k, v in args.items())
        body += f"      args: {{ {rendered} }}\n"
    return body


class TestDockerfileParsing:
    def test_json_form_copy_parses(self, tmp_repo, capsys):
        tmp_repo.write("app/main.py", "print('hi')\n")
        tmp_repo.write("Dockerfile",
                       'FROM python:3.11-slim\nCOPY ["app", "/srv/app"]\n')
        tmp_repo.compose(_compose_single())
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_json_form_missing_source_is_reported(self, tmp_repo, capsys):
        tmp_repo.write("Dockerfile",
                       'FROM python:3.11-slim\nCOPY ["nowhere", "/srv"]\n')
        tmp_repo.compose(_compose_single())
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "nowhere" in out

    def test_continuations_and_crlf_checkout_parse(self, tmp_repo, capsys):
        """The repo is checked out CRLF on the Windows host and LF in CI. A
        trailing \\r after the continuation backslash must not break the join,
        and a comment inside a continuation must not end it."""
        tmp_repo.write("app/main.py", "x\n")
        tmp_repo.write_bytes(
            "Dockerfile",
            b"FROM python:3.11-slim\r\n"
            b"RUN apt-get update \\\r\n"
            b"    # a comment inside the continuation\r\n"
            b"    && apt-get install -y curl\r\n"
            b"COPY app /srv/app\r\n")
        tmp_repo.compose(_compose_single())
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_compose_shorthand_and_list_args_parse(self):
        """`build: ./sub` and the `- KEY=value` args spelling are both real
        compose grammar; a parser that only reads the mapping form would treat
        such a service as referencing nothing."""
        report = Report()
        refs = build_audit.parse_compose(
            "services:\n"
            "  short:\n    build: ./sub\n"
            "  listy:\n    build:\n      context: .\n"
            "      dockerfile: Dockerfile.x\n"
            "      args:\n        - NAME=value\n        - FROM_ENV\n",
            report)
        assert not report.findings
        assert [r.service for r in refs["sub/Dockerfile"]] == ["short"]
        (listy,) = refs["Dockerfile.x"]
        assert listy.args == {"NAME": "value"}
        assert listy.passthrough == frozenset({"FROM_ENV"})

    def test_unparseable_compose_is_a_finding(self, tmp_repo, capsys):
        tmp_repo.write("Dockerfile", "FROM python:3.11-slim\n")
        tmp_repo.compose("services: [unbalanced\n  nonsense: {")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "compose-unparseable" in out

    def test_scope_is_root_and_backend_only(self):
        assert build_audit.in_scope("Dockerfile")
        assert build_audit.in_scope("Dockerfile.dev")
        assert build_audit.in_scope("backend/services/Dockerfile.service")
        assert not build_audit.in_scope("frontend/Dockerfile")
        assert not build_audit.in_scope("my-extension/Dockerfile")
        assert not build_audit.in_scope("backend/services/company/requirements.txt")


class TestReferencedBuildFiles:
    def test_resolving_sources_pass(self, tmp_repo, capsys):
        tmp_repo.write("backend/requirements.txt", "fastapi\n")
        tmp_repo.write("backend/app/main.py", "x\n")
        tmp_repo.write("Dockerfile",
                       "FROM python:3.11-slim\n"
                       "COPY backend/requirements.txt /app/requirements.txt\n"
                       "COPY backend/ /app/backend/\n")
        tmp_repo.compose(_compose_single())
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)
        assert "OK" in out

    def test_missing_source_reported_with_build_file(self, tmp_repo, capsys):
        """Requirement 5.5: the build file and the missing path, together."""
        tmp_repo.write("Dockerfile",
                       "FROM python:3.11-slim\nCOPY platform /opt/platform\n")
        tmp_repo.compose(_compose_single())
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "unresolved-copy-source" in out
        assert "Dockerfile:2" in out
        assert "platform" in out

    def test_templated_copy_reports_each_failing_service_value(self, tmp_repo, capsys):
        """One templated build file, three referencing services, one of which
        names a service directory that does not exist. The finding must name
        the failing value -- that is the whole point of checking all values
        instead of trusting whichever one somebody happened to build."""
        for svc in ("alpha", "beta"):
            tmp_repo.write(f"backend/services/{svc}/requirements.txt", "x\n")
        tmp_repo.write("backend/services/Dockerfile.service",
                       "FROM python:3.11-slim\n"
                       "ARG SERVICE\n"
                       "COPY backend/services/${SERVICE}/requirements.txt ./r.txt\n")
        compose = "services:\n"
        for svc in ("alpha", "beta", "gamma"):
            compose += (f"  {svc}:\n    build:\n      context: .\n"
                        f"      dockerfile: backend/services/Dockerfile.service\n"
                        f"      args: {{ SERVICE: {svc} }}\n")
        tmp_repo.compose(compose)
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "backend/services/gamma/requirements.txt" in out
        assert "'gamma'" in out
        assert out.count("FAIL") == 1  # alpha and beta resolve; no false findings

    def test_compose_args_override_dockerfile_defaults(self, tmp_repo, capsys):
        """`docker build --build-arg` semantics: the compose value wins over
        the ARG default. The default names a directory that does not exist, so
        a checker that ignored the override would fail a working build."""
        tmp_repo.write("real/requirements.txt", "x\n")
        tmp_repo.write("Dockerfile",
                       "FROM python:3.11-slim\n"
                       "ARG DIR=missing-default\n"
                       "COPY ${DIR}/requirements.txt ./r.txt\n")
        tmp_repo.compose(_compose_single(args={"DIR": "real"}))
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_unset_build_arg_is_reported(self, tmp_repo, capsys):
        tmp_repo.write("Dockerfile",
                       "FROM python:3.11-slim\n"
                       "ARG SERVICE\n"
                       "COPY backend/${SERVICE}/app /srv/app\n")
        tmp_repo.compose(_compose_single())
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "SERVICE" in out

    def test_from_stage_sources_are_not_resolved_against_context(self, tmp_repo, capsys):
        """`--from=` sources live in an earlier stage's filesystem. Resolving
        them against the context would fail every multi-stage build ever
        written."""
        tmp_repo.write("Dockerfile",
                       "FROM node:20 AS builder\n"
                       "FROM nginx:alpine\n"
                       "COPY --from=builder /app/dist /usr/share/nginx/html\n")
        tmp_repo.compose(_compose_single())
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_glob_source_resolves_with_at_least_one_match(self, tmp_repo, capsys):
        tmp_repo.write("wheels/pkg-1.0-py3-none-any.whl", "not a real wheel\n")
        tmp_repo.write("Dockerfile",
                       "FROM python:3.11-slim\nCOPY wheels/*.whl /wheels/\n")
        tmp_repo.compose(_compose_single())
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_glob_source_with_no_match_fails(self, tmp_repo, capsys):
        """An empty glob fails the real `docker build` exactly like a missing
        literal path, so it fails here too."""
        tmp_repo.write("keep.txt", "x\n")
        tmp_repo.write("Dockerfile",
                       "FROM python:3.11-slim\nCOPY wheels/*.whl /wheels/\n")
        tmp_repo.compose(_compose_single())
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "wheels/*.whl" in out

    def test_context_other_than_root_is_honoured(self, tmp_repo, capsys):
        """`context: ./sub` means sources resolve under sub/, not the repo
        root. A file that exists at the root but not in the context must
        still be a finding."""
        tmp_repo.write("app.py", "x\n")  # exists at the root only
        tmp_repo.write("backend/Dockerfile",
                       "FROM python:3.11-slim\nCOPY app.py /srv/app.py\n")
        tmp_repo.compose(_compose_single(dockerfile="Dockerfile",
                                         context="./backend", service="subapp"))
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "backend/Dockerfile" in out
        assert "'backend'" in out


class TestUnreferencedBuildFiles:
    def test_reintroduced_dead_dockerfile_fails_with_its_path(self, tmp_repo, capsys):
        """The exact regression task 8.2 deletes: a per-service Dockerfile
        copying `platform`, referenced by nothing, with no `platform/` in the
        repository. It must fail CI and name the file."""
        tmp_repo.write("backend/services/thing/app/main.py", "x\n")
        tmp_repo.write("backend/services/thing/Dockerfile",
                       "FROM python:3.11-slim\n"
                       "COPY platform /opt/platform\n"
                       "COPY services/thing/app ./app\n")
        tmp_repo.compose(_compose_single())  # references the root Dockerfile...
        tmp_repo.write("Dockerfile", "FROM python:3.11-slim\n")  # ...which is fine
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "dead-build-file" in out
        assert "backend/services/thing/Dockerfile" in out
        assert "platform" in out

    def test_unreferenced_but_resolving_is_a_note_not_a_finding(self, tmp_repo, capsys):
        """Design 5.3 makes the finding conditional on unreferenced AND
        unresolvable. Buildable-but-unwired is a review question, and a check
        that fails on it would have to be suppressed for every experiment."""
        tmp_repo.write("backend/tool/app.py", "x\n")
        tmp_repo.write("backend/tool/Dockerfile",
                       "FROM python:3.11-slim\nCOPY app.py /srv/app.py\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)
        assert "unreferenced build file backend/tool/Dockerfile" in out

    def test_own_directory_counts_as_a_candidate_context(self, tmp_repo, capsys):
        """The file above resolves from its own directory, not the repo root.
        Failing it would punish `docker build .` run from that directory."""
        tmp_repo.write("backend/tool/app.py", "x\n")
        tmp_repo.write("backend/tool/Dockerfile",
                       "FROM python:3.11-slim\nCOPY app.py /srv/app.py\n")
        report = Report()
        build_audit._audit_unreferenced(
            "backend/tool/Dockerfile",
            (tmp_repo.root / "backend/tool/Dockerfile").read_text(encoding="utf-8"),
            tmp_repo.root, report)
        assert not report.findings


class TestRealRepository:
    def test_compose_builds_dockerfile_service_with_all_nine_values(self):
        """The task's list of nine, verified against the compose file that is
        actually deployed rather than against this test's opinion."""
        root = git_top_level()
        report = Report()
        refs = build_audit.parse_compose(
            (root / "docker-compose.yml").read_text(encoding="utf-8"), report)
        assert not report.findings
        service_refs = refs["backend/services/Dockerfile.service"]
        assert sorted(r.args["SERVICE"] for r in service_refs) == sorted(NINE_SERVICES)
        assert all(r.context == "." for r in service_refs)

    def test_real_repository_referenced_build_files_all_resolve(self, capsys):
        """Two-state assertion, deliberately.

        Task 8.2 deletes the nine dead per-service Dockerfiles; until it
        lands, this repository legitimately carries exactly those
        `dead-build-file` findings and nothing else. So: no finding may ever
        touch a compose-referenced build file (that would be a real defect --
        fix the file, not this test), and once the dead files are gone the
        check must exit 0. After 8.2 the first branch is unreachable and this
        becomes the sibling-style clean-repo test.
        """
        root = git_top_level()
        rc = build_audit.main(["--root", str(root), "--json"])
        data = json.loads(capsys.readouterr().out)

        known_dead = {f"backend/services/{s}/Dockerfile" for s in NINE_SERVICES}
        dead_still_tracked = known_dead & set(tracked_files(root))

        unexpected = [f for f in data["findings"]
                      if not (f["rule"] == "dead-build-file"
                              and f["path"] in dead_still_tracked)]
        assert unexpected == [], (
            "real repository has a broken referenced build definition:\n"
            + "\n".join(str(f) for f in unexpected))

        if dead_still_tracked:
            assert rc == int(Exit.FAILED)
            assert {f["path"] for f in data["findings"]} == dead_still_tracked
        else:
            assert rc == int(Exit.OK)


# --------------------------------------------------------------------------
# Property 11
# --------------------------------------------------------------------------

_SEGMENT = st.sampled_from(["a", "b", "c", "dd"])
_RELPATH = st.lists(_SEGMENT, min_size=1, max_size=3).map("/".join)


def _resolvable(source: str, files: set[str]) -> bool:
    """Ground truth, computed without touching build_audit: a source resolves
    iff it names a written file or a directory some written file lives in."""
    norm = posixpath.normpath(source)
    return any(f == norm or f.startswith(norm + "/") for f in files)


def _prefix_free(files: set[str]) -> set[str]:
    """Drop entries that collide with another entry's directory: a path
    cannot be both a file and a directory on any real filesystem, and the
    generator does not know that. Sorted iteration keeps the result a pure
    function of the generated set."""
    kept: set[str] = set()
    for rel in sorted(files):
        if not any(k == rel or k.startswith(rel + "/") or rel.startswith(k + "/")
                   for k in kept):
            kept.add(rel)
    return kept


@settings(max_examples=50, deadline=None)
@given(files=st.sets(_RELPATH, min_size=0, max_size=6),
       sources=st.lists(_RELPATH, min_size=1, max_size=6))
def test_property_finding_iff_source_does_not_resolve(files, sources):
    """Feature: production-readiness, Property 11.

    For any build context and any COPY source paths, a source is reported
    missing iff it does not resolve inside that context, and every reported
    miss carries the line of the COPY that named it.

    **Validates: Requirements 5.2, 5.3, 5.5**

    A real directory tree per example rather than a stub: resolution *is* the
    filesystem question, and stubbing it would test the stub. No `git init`
    though -- `missing_sources` is driven directly, which keeps an example in
    the low milliseconds.
    """
    files = _prefix_free(files)
    with tempfile.TemporaryDirectory() as tmp:
        context = Path(tmp)
        for rel in files:
            p = context / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x", encoding="utf-8")

        text = "FROM python:3.11-slim\n" + "".join(
            f"COPY {src} /dest{i}\n" for i, src in enumerate(sources))
        missing = build_audit.missing_sources(text, context, {})

        reported = {m.line: m.resolved for m in missing}
        for i, src in enumerate(sources):
            line = i + 2  # one COPY per line, after FROM
            if _resolvable(src, files):
                assert line not in reported, (src, files)
            else:
                assert reported.get(line) == src, (src, files)
