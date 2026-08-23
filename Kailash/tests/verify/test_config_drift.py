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


NODE = config_drift.EXPECTED_NODE_VERSION


DOMAIN = config_drift.EXPECTED_PRODUCTION_DOMAIN


def _ci_yml(frontend="20", infra="20", domain=DOMAIN):
    """`ci.yml` reduced to the two jobs that pin Node.

    `company-infra` is present in every fixture because the rule has to keep
    ignoring it: that pin is the CDK toolchain, not the frontend build runtime.
    """
    body = "jobs:\n"
    body += ("  company-infra:\n    steps:\n"
             "      - uses: actions/setup-node@v4\n"
             f"        with: {{ node-version: \"{infra}\" }}\n") if infra else ""
    env = ("        env:\n"
           f"          REACT_APP_DOMAIN: {domain}\n") if domain else ""
    if frontend:
        body += ("  frontend:\n    steps:\n"
                 "      - uses: actions/setup-node@v4\n"
                 "        with:\n"
                 f"          node-version: \"{frontend}\"\n"
                 "      - run: yarn build\n" + env)
    else:
        body += "  frontend:\n    steps:\n      - run: yarn build\n" + env
    return body


def _deploy_frontend_yml(project=GOOD, node="20", staging_node="20",
                         domain=DOMAIN, staging_domain="staging.kailash-ai.com"):
    """Both frontend-building jobs: staging channel and live."""
    def job(name, channel, version, dom):
        return ("" if version is None else
                f"  {name}:\n    steps:\n"
                "      - uses: actions/setup-node@v4\n"
                "        with:\n"
                f"          node-version: '{version}'\n"
                "      - run: yarn build\n"
                + ("        env:\n"
                   f"          REACT_APP_DOMAIN: {dom}\n" if dom else "")
                + "      - uses: FirebaseExtended/action-hosting-deploy@v0\n"
                "        with:\n"
                f"          channelId: {channel}\n"
                f"          projectId: {project}\n")

    return "jobs:\n" + job("deploy-staging", "staging", staging_node, staging_domain) \
        + job("build-and-deploy", "live", node, domain)


def _node_sites(repo, ci="20", deploy="20", staging="20", docker="20", project=GOOD):
    repo.write(".github/workflows/ci.yml", _ci_yml(frontend=ci))
    repo.write(".github/workflows/deploy-frontend.yml",
               _deploy_frontend_yml(project, node=deploy, staging_node=staging))
    repo.write("frontend/Dockerfile",
               (f"FROM node:{docker}-alpine AS builder\n" if docker else "FROM scratch\n")
               + "RUN yarn build\n\nFROM nginx:alpine\n")


def _minimal(repo, project=GOOD, url=f"https://github.com/{SLUG}.git"):
    repo.all_firebase_sites(project)
    repo.env_production(project, extra=f"REACT_APP_DOMAIN={DOMAIN}\n")
    repo.firebase_js(project, "1:794735482892:web:abc", "794735482892")
    repo.deploy_sh(url)
    # The node-version and production-domain rules read these files in every
    # run, so a fixture that omitted them would fail on absent required sources
    # rather than on the thing the test is about.
    _node_sites(repo, project=project)


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
                       "      - uses: actions/setup-node@v4\n"
                       f"        with: {{ node-version: '{NODE}' }}\n"
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


class TestNodeVersion:
    """Task 5.5. The runtime the frontend is built on, wherever it is declared."""

    def test_all_declarations_agree_passes(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_ci_pinned_to_18_fails_and_names_it(self, tmp_repo, capsys):
        """The live defect: CI validating a build on a runtime no deploy uses.
        On 18 the install fails outright -- react-router-dom@7.9.6 declares
        engines.node >=20."""
        _minimal(tmp_repo)
        _node_sites(tmp_repo, ci="18")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert ".github/workflows/ci.yml" in out
        assert "18" in out
        # Requirement 3.7: the agreeing files too, so a reader sees which
        # version the rest of the repository actually carries.
        assert "frontend/Dockerfile=20" in out
        assert ".github/workflows/deploy-frontend.yml=20,20" in out

    def test_dockerfile_on_another_major_fails_and_names_it(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        _node_sites(tmp_repo, docker="18")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "frontend/Dockerfile" in out
        assert "18" in out

    def test_absent_ci_pin_is_a_finding_not_a_skip(self, tmp_repo, capsys):
        """Deleting the pin hands the choice to the runner default, which is the
        same defect as a disagreeing pin: nobody can tell what it builds on."""
        _minimal(tmp_repo)
        _node_sites(tmp_repo, ci=None)
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert ".github/workflows/ci.yml" in out
        assert "<absent>" in out

    def test_staging_building_on_another_major_is_drift(self, tmp_repo, capsys):
        """Both jobs in deploy-frontend.yml build the frontend. A staging build
        on another Node means verify-staging clears an artifact production never
        builds, so a first-match extractor over this file would miss it."""
        _minimal(tmp_repo)
        _node_sites(tmp_repo, staging="22")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert ".github/workflows/deploy-frontend.yml" in out
        assert "22" in out

    def test_cdk_toolchain_pin_does_not_participate(self, tmp_repo, capsys):
        """`company-infra` pins Node for `npx cdk synth`. That is a toolchain
        version, independent of the runtime the shipped bundle is built on;
        coupling them would make a CDK bump a frontend finding."""
        _minimal(tmp_repo)
        tmp_repo.write(".github/workflows/ci.yml", _ci_yml(frontend="20", infra="22"))
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out

    def test_patch_pin_reads_as_its_major(self, tmp_repo, capsys):
        """`node-version: "20.11.1"` and `node:20-alpine` are the same runtime
        written two ways; the obligation engines.node >=20 states is a major."""
        _minimal(tmp_repo)
        _node_sites(tmp_repo, ci="20.11.1")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out

    def test_unreadable_pin_is_reported_with_its_literal(self, tmp_repo, capsys):
        """`lts/*` resolves to whatever is current at run time, so it is not a
        pin at all -- and it must be reported as itself, not as "<absent>"."""
        _minimal(tmp_repo)
        _node_sites(tmp_repo, ci="lts/*")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "lts/*" in out
        assert "<absent>" not in out


class TestProductionDomain:
    """The domain the production bundle is built with, wherever it is declared.

    The defect: the production build baked `kailash-ai.in` while the deployment
    check verified `kailash-ai.com`. Both domains are owned and both serve the
    same site, so neither half was wrong on its own -- which is why nothing
    caught it. One declared constant is the fix.
    """

    def test_all_declarations_agree_passes(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out

    def test_ci_building_another_domain_fails_and_names_it(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        tmp_repo.write(".github/workflows/ci.yml",
                       _ci_yml(domain="kailash-ai.com"))
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert ".github/workflows/ci.yml" in out
        assert "kailash-ai.com" in out
        # Requirement 3.7: the agreeing files too, so a reader sees which value
        # the rest of the repository carries.
        assert f".github/workflows/deploy-frontend.yml={DOMAIN}" in out
        assert f"frontend/.env.production={DOMAIN}" in out

    def test_deploy_building_another_domain_fails_and_names_it(self, tmp_repo, capsys):
        """The authoritative source: this is the build Firebase serves live."""
        _minimal(tmp_repo)
        tmp_repo.write(".github/workflows/deploy-frontend.yml",
                       _deploy_frontend_yml(domain="kailash-ai.com"))
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert ".github/workflows/deploy-frontend.yml" in out
        assert "kailash-ai.com" in out

    def test_env_production_disagreeing_fails(self, tmp_repo, capsys):
        """The workflows override it, so this does not change what ships -- it
        makes a local `yarn build` and the deployed bundle differ, which is the
        same defect one step removed."""
        _minimal(tmp_repo)
        tmp_repo.env_production(GOOD, extra="REACT_APP_DOMAIN=kailash-ai.com\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "frontend/.env.production" in out
        assert "kailash-ai.com" in out

    def test_absent_declaration_is_a_finding_not_a_skip(self, tmp_repo, capsys):
        """Deleting the line hands the value to CRA's default (undefined),
        which is the same "nobody can tell" defect as a disagreeing one."""
        _minimal(tmp_repo)
        tmp_repo.write(".github/workflows/ci.yml", _ci_yml(domain=None))
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert ".github/workflows/ci.yml" in out
        assert "<absent>" in out

    def test_staging_domain_does_not_participate(self, tmp_repo, capsys):
        """`deploy-staging` legitimately builds with a staging hostname. Folding
        it in would make a correct staging value a finding, and the rule would
        then be loosened until it caught nothing."""
        _minimal(tmp_repo)
        tmp_repo.write(".github/workflows/deploy-frontend.yml",
                       _deploy_frontend_yml(staging_domain="staging.kailash-ai.com"))
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out

    def test_a_second_declaration_in_the_production_job_is_drift(self, tmp_repo, capsys):
        """A later step of the same build declaring another domain cannot hide
        behind the first: `finditer`, not `search`."""
        _minimal(tmp_repo)
        body = _deploy_frontend_yml()
        body += ("      - run: yarn build:legacy\n"
                 "        env:\n"
                 "          REACT_APP_DOMAIN: kailash-ai.com\n")
        tmp_repo.write(".github/workflows/deploy-frontend.yml", body)
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "kailash-ai.com" in out

    def test_crlf_checkout_is_read_the_same_as_lf(self, tmp_repo, capsys):
        """The developer host checks these files out CRLF and CI checks them out
        LF. A `\\s*$` anchor would match nothing on one of the two, and a rule
        that silently reads no declarations is worse than no rule."""
        _minimal(tmp_repo)
        for rel in (".github/workflows/ci.yml", ".github/workflows/deploy-frontend.yml"):
            text = (tmp_repo.root / rel).read_text(encoding="utf-8")
            (tmp_repo.root / rel).write_bytes(
                text.replace("\n", "\r\n").encode("utf-8"))
            tmp_repo.git("add", "--", rel)
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out

    def test_expression_literal_is_reported_as_itself(self, tmp_repo, capsys):
        """`${{ vars.DOMAIN || '...' }}` is not a declaration a reader can
        resolve, so it is reported rather than silently accepted."""
        _minimal(tmp_repo)
        tmp_repo.write(".github/workflows/ci.yml",
                       _ci_yml(domain="${{ vars.DOMAIN || 'kailash-ai.in' }}"))
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "vars.DOMAIN" in out


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
    from scripts.verify.common import project_root
    root = project_root()
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


def test_the_project_cli_flag_form_is_extracted_like_projectid():
    """The WIF-era deploy steps declare the project as `--project <id>` on the
    firebase CLI rather than as an action `projectId:` input. Both forms are
    declarations; dropping one made the required source read as absent."""
    text = (
        "      - name: Deploy to Firebase Hosting\n"
        "        run: npx --yes firebase-tools@13 deploy --only hosting "
        "--project kailash-29111 --non-interactive\n"
        "      - name: Staging channel\n"
        "        run: npx --yes firebase-tools@13 hosting:channel:deploy "
        "staging --expires 30d --project kailash-29111\n"
    )
    values = [d.value for d in config_drift._workflow_project_id(text)]
    assert values == ["kailash-29111", "kailash-29111"]
