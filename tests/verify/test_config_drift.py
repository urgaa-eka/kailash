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


class TestRepoSlug:
    def test_matching_slug_passes(self, tmp_repo, capsys):
        _minimal(tmp_repo)
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_wrong_owner_fails(self, tmp_repo, capsys):
        _minimal(tmp_repo, url="https://github.com/flywithvvk/kailash.git")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "flywithvvk/kailash" in out

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
    """No findings iff all four are present and identical to the expected
    value, and every participating path appears in the output otherwise."""
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
        for path, value in zip(paths, values):
            if value != GOOD:
                assert path in rendered
