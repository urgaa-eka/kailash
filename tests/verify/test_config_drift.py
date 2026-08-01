"""Configuration drift: one value, several files, all must agree."""
from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from scripts.verify import config_drift
from scripts.verify.common import Exit, Report

GOOD = config_drift.EXPECTED_FIREBASE_PROJECT
SLUG = config_drift.EXPECTED_REPO_SLUG


def _run(root, capsys) -> tuple[int, str]:
    rc = config_drift.main(["--root", str(root)])
    return rc, capsys.readouterr().out


def _minimal(repo, project=GOOD, url=f"https://github.com/{SLUG}.git"):
    repo.all_firebase_sites(project)
    repo.firebase_js(project, "1:794735482892:web:abc", "794735482892")
    repo.deploy_sh(url)


class TestFirebaseProjectId:
    def test_all_four_agree_passes(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_one_disagreeing_file_fails_and_names_it(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        tmp_repo.env_production("kailash-38268")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "frontend/.env.production" in out
        assert "kailash-38268" in out

    def test_missing_declaration_is_a_finding_not_a_skip(self, tmp_repo, capsys):
        """Otherwise the check passes by deleting a line: three files agree
        while the fourth targets nothing."""
        _minimal(tmp_repo)
        tmp_repo.write("frontend/.env.production", "# nothing here\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "<absent>" in out

    def test_every_participant_is_printed_on_disagreement(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        tmp_repo.firebaserc("other-project")
        _, out = _run(tmp_repo.root, capsys)
        for path in ("frontend/.firebaserc", "frontend/.env.production",
                     ".github/workflows/deploy-frontend.yml", "backend/.env.example"):
            assert path in out

    def test_a_second_declaration_in_the_workflow_is_drift(self, tmp_repo, capsys):
        """The staging channel deploys from a second step in this same file. A
        first-match extractor reads the live step, reports agreement, and lets
        the staging step name any project at all."""
        _minimal(tmp_repo)
        tmp_repo.write(".github/workflows/deploy-frontend.yml",
                       "jobs:\n  deploy-live:\n    steps:\n"
                       "      - uses: FirebaseExtended/action-hosting-deploy@v0\n"
                       "        with:\n"
                       "          channelId: live\n"
                       f"          projectId: {GOOD}\n"
                       "  deploy-staging:\n    steps:\n"
                       "      - uses: FirebaseExtended/action-hosting-deploy@v0\n"
                       "        with:\n"
                       "          channelId: staging\n"
                       "          projectId: kailash-38268\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert ".github/workflows/deploy-frontend.yml" in out
        assert "kailash-38268" in out

    def test_a_duplicate_dotenv_declaration_is_drift(self, tmp_repo, capsys):
        """Two values for one key: which one the build honours is not something
        a reader of the file can tell, so the ambiguity is itself the defect."""
        _minimal(tmp_repo)
        tmp_repo.env_production(GOOD, extra="REACT_APP_FIREBASE_PROJECT_ID=kailash-38268\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "frontend/.env.production" in out
        assert "kailash-38268" in out


class TestRepoSlug:
    def test_matching_slug_passes(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_wrong_owner_fails(self, tmp_repo, capsys):
        _minimal(tmp_repo, url="https://github.com/flywithvvk/kailash.git")  # secret-scan: allow negative fixture for the slug rule
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "flywithvvk/kailash" in out  # secret-scan: allow negative fixture for the slug rule

    def test_vacuous_required_source_fails(self, tmp_repo, capsys):
        """deploy.sh with no repository URL at all is the most dangerous
        outcome: it runs git reset --hard against whatever it resolves."""
        _minimal(tmp_repo)
        tmp_repo.write("deploy/vultr/deploy.sh", "#!/bin/bash\necho hi\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "no match" in out

    def test_ssh_form_normalises(self, tmp_repo, capsys):
        _minimal(tmp_repo, url=f"git@github.com:{SLUG}.git")
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_suppression_cannot_discharge_the_required_source(self, tmp_repo, capsys):
        """A wrong slug in deploy.sh behind `verify: allow` is a vacuous pass in
        the one file that runs git reset --hard and git clean -fd. Requirement
        9.2 is an exact-match obligation there, so the marker is refused."""
        _minimal(tmp_repo)
        tmp_repo.write("deploy/vultr/deploy.sh",
                       "#!/usr/bin/env bash\n"
                       "# verify: allow legacy remote kept for reference\n"
                       'REPO_URL="https://github.com/flywithvvk/kailash.git"\n'  # secret-scan: allow negative fixture for the slug rule
                       "git reset --hard origin/main\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "deploy/vultr/deploy.sh" in out
        assert "flywithvvk/kailash" in out  # secret-scan: allow negative fixture for the slug rule
        assert "suppression ignored" in out


class TestFirebaseAppIdentity:
    def test_consistent_and_mapped_passes(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_partial_copy_paste_fails(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        tmp_repo.firebase_js(GOOD, "1:111111111111:web:abc", "794735482892")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "firebase-app-identity" in out

    def test_project_absent_from_map_fails(self, tmp_repo, capsys):
        """A wholesale copy of another project's config is internally
        consistent. Only the reviewed map catches it -- which is exactly how
        the kailash-38268 drift survived review."""
        tmp_repo.all_firebase_sites("kailash-99999")
        tmp_repo.firebase_js("kailash-99999", "1:555555555555:web:x", "555555555555")
        tmp_repo.deploy_sh(f"https://github.com/{SLUG}.git")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "reviewed map" in out

    def test_malformed_app_id_fails(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        tmp_repo.firebase_js(GOOD, "not-an-app-id", "794735482892")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "malformed" in out


def test_passes_on_real_repository(capsys):
    """Task 5.3. If this fails the finding is a real defect: fix the
    disagreeing file, do not relax the rule."""
    from scripts.verify.common import git_top_level
    root = git_top_level()
    rc = config_drift.main(["--root", str(root)])
    out = capsys.readouterr().out
    assert rc == int(Exit.OK), f"real repository has drift:\n{out}"


class _StubCorpus:
    """Just enough Corpus for the rule: it only ever calls read().

    Deliberately not a real repository -- `git init` per generated example
    costs ~600ms and turns a property test into a timeout.
    """

    def __init__(self, contents: dict[str, str | None]):
        self._contents = contents

    def read(self, rel: str) -> str | None:
        return self._contents.get(rel)


@given(values=st.lists(
    st.one_of(st.none(), st.sampled_from([GOOD, "kailash-38268", "other"])),
    min_size=4, max_size=4))
def test_property_agreement_iff_all_present_and_equal(values):
    """Feature: production-readiness, Property 7.

    No findings iff all four are present and identical to the expected value;
    on any disagreement every participating path appears in the rendered output
    together with the value found in it.

    **Validates: Requirements 3.1, 3.7**
    """
    import json as _json
    paths = ["frontend/.firebaserc", "frontend/.env.production",
             ".github/workflows/deploy-frontend.yml", "backend/.env.example"]
    renderers = [
        lambda v: _json.dumps({"projects": {"default": v}}),
        lambda v: f"REACT_APP_FIREBASE_PROJECT_ID={v}\n",
        lambda v: f"          projectId: {v}\n",
        lambda v: f"FIREBASE_PROJECT_ID={v}\n",
    ]
    contents = {p: (r(v) if v is not None else None)
                for p, r, v in zip(paths, renderers, values)}

    report = Report()
    config_drift.check_firebase_project_id(_StubCorpus(contents), report)

    all_good = all(v == GOOD for v in values)
    assert (not report.findings) == all_good

    if not all_good:
        rendered = report.render()
        # Every participant, not only the disagreeing ones: whoever fixes the
        # drift needs to see which value the other files carry.
        for path, value in zip(paths, values):
            assert path in rendered
            assert (value if value is not None else "<absent>") in rendered
