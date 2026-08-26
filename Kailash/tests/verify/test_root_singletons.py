"""Tests for the Rule 1 gate: only RULES.md + Kailash/ + plumbing at the root."""
from __future__ import annotations

from scripts.verify import root_singletons as rs
from scripts.verify.common import Exit, git_top_level


def _clean_root(repo):
    """A repo whose git root holds exactly the allowed entries."""
    repo.write("RULES.md", "# rules\n")
    repo.write("Kailash/README.md", "# project\n")
    repo.write(".github/workflows/ci.yml", "on: [push]\njobs:\n  a:\n    steps: [{run: true}]\n")
    repo.write(".gitignore", "*.log\n")


def _run(root, capsys):
    rc = rs.main(["--root", str(root)])
    return rc, capsys.readouterr().out


class TestGate:
    def test_clean_root_passes(self, tmp_repo, capsys):
        _clean_root(tmp_repo)
        tmp_repo.commit()
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out

    def test_a_loose_root_file_fails(self, tmp_repo, capsys):
        _clean_root(tmp_repo)
        tmp_repo.write("stray-notes.md", "# oops, at the root\n")
        tmp_repo.commit()
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "loose-root-entry" in out
        assert "stray-notes.md" in out

    def test_a_loose_root_folder_fails(self, tmp_repo, capsys):
        _clean_root(tmp_repo)
        tmp_repo.write("scripts/tool.sh", "#!/bin/sh\n")  # a folder at the root
        tmp_repo.commit()
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "loose-root-entry" in out
        assert "scripts" in out

    def test_missing_master_folder_fails(self, tmp_repo, capsys):
        repo = tmp_repo
        repo.write("RULES.md", "# rules\n")
        repo.write(".gitignore", "*.log\n")
        repo.commit()  # no Kailash/
        rc, out = _run(repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "missing-root-entry" in out
        assert "Kailash" in out


def test_passes_on_real_repository(capsys):
    """The real repo root holds only RULES.md + Kailash/ + .github/ + .gitignore.
    If this fails the finding is real: move the stray entry under Kailash/, do
    not relax the rule."""
    rc = rs.main(["--root", str(git_top_level())])
    out = capsys.readouterr().out
    assert rc == int(Exit.OK), f"real repository violates Rule 1:\n{out}"
