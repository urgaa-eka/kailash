"""Tests for the Rule 5 membership gate: one pipeline, no auxiliary workflows."""
from __future__ import annotations

from scripts.verify import workflow_singletons as ws
from scripts.verify.common import Exit, project_root

CANONICAL = ("ci.yml", "deploy-backend.yml", "deploy-frontend.yml")


def _run(root, capsys):
    rc = ws.main(["--root", str(root)])
    return rc, capsys.readouterr().out


def _canonical_pipeline(repo):
    for name in CANONICAL:
        repo.workflow(name, "on: [push]\njobs:\n  a:\n    steps: [{run: true}]\n")


class TestGate:
    def test_passes_with_the_canonical_pipeline(self, tmp_repo, capsys):
        _canonical_pipeline(tmp_repo)
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out

    def test_an_auxiliary_workflow_fails(self, tmp_repo, capsys):
        _canonical_pipeline(tmp_repo)
        # The exact defect: a one-off workflow beside the pipeline.
        tmp_repo.workflow("rollback-hosting.yml", "on: workflow_dispatch\njobs:\n"
                          "  r:\n    steps: [{run: true}]\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "auxiliary-workflow" in out
        assert "rollback-hosting.yml" in out

    def test_a_yaml_extension_is_also_caught(self, tmp_repo, capsys):
        _canonical_pipeline(tmp_repo)
        tmp_repo.workflow("extra.yaml", "on: [push]\njobs:\n  e:\n    steps: [{run: true}]\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "auxiliary-workflow" in out
        assert "extra.yaml" in out

    def test_a_missing_canonical_workflow_fails(self, tmp_repo, capsys):
        # ci.yml + deploy-frontend.yml present, deploy-backend.yml absent.
        tmp_repo.workflow("ci.yml", "on: [push]\njobs:\n  a:\n    steps: [{run: true}]\n")
        tmp_repo.workflow("deploy-frontend.yml",
                          "on: [push]\njobs:\n  a:\n    steps: [{run: true}]\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "missing-pipeline-workflow" in out
        assert "deploy-backend.yml" in out

    def test_absent_workflows_dir_is_unavailable(self, tmp_path, capsys):
        # A directory with no `.github/workflows/` (and whose parent has none
        # either) cannot run the check -- that is UNAVAILABLE, not a violation.
        empty = tmp_path / "proj"
        empty.mkdir()
        rc = ws.main(["--root", str(empty)])
        assert rc == int(Exit.UNAVAILABLE)


def test_passes_on_real_repository(capsys):
    """The real repo carries exactly the canonical pipeline and no auxiliary
    workflows. If this fails the finding is real: fold the need into the one
    pipeline, do not relax the rule."""
    rc = ws.main(["--root", str(project_root())])
    out = capsys.readouterr().out
    assert rc == int(Exit.OK), f"real repository violates Rule 5:\n{out}"
