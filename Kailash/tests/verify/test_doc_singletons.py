"""Tests for the Rule 3 gate: one BRD, one TRD, one PRD, no duplicates."""
from __future__ import annotations

import pytest

from scripts.verify import doc_singletons as ds
from scripts.verify.common import Exit, project_root


def _run(root, capsys):
    rc = ds.main(["--root", str(root)])
    return rc, capsys.readouterr().out


def _canonical_trio(repo):
    repo.write("docs/BRD.md", "# BRD\nbusiness\n")
    repo.write("docs/TRD.md", "# TRD\ntechnical\n")
    repo.write("docs/PRD.md", "# PRD\nproduct\n")


class TestKindOf:
    @pytest.mark.parametrize("stem,kind", [
        ("BRD", "BRD"),
        ("TRD", "TRD"),
        ("PRD", "PRD"),
        ("BRD_kailash_ai", "BRD"),
        ("TRD_android_app_kailash_ai", "TRD"),
        ("prd-v2", "PRD"),
        ("brd", "BRD"),
    ])
    def test_declares_a_kind(self, stem, kind):
        assert ds._kind_of(stem) == kind

    @pytest.mark.parametrize("stem", [
        "business-requirements",   # not *named* BRD, a different doc
        "dashboard",               # substring 'brd'? no token
        "hybrid",
        "cardboard",
        "README",
        "kailash-overview",
        "AGENT",
    ])
    def test_ignores_non_requirements_names(self, stem):
        assert ds._kind_of(stem) is None


class TestGate:
    def test_passes_with_the_canonical_trio(self, tmp_repo, capsys):
        _canonical_trio(tmp_repo)
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out

    def test_a_missing_canonical_doc_fails(self, tmp_repo, capsys):
        tmp_repo.write("docs/BRD.md", "# BRD\n")
        tmp_repo.write("docs/TRD.md", "# TRD\n")
        # PRD absent
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "missing-canonical-doc" in out
        assert "docs/PRD.md" in out

    def test_a_duplicate_named_file_fails(self, tmp_repo, capsys):
        _canonical_trio(tmp_repo)
        # A second BRD, wherever in the tree, is drift.
        tmp_repo.write("android/BRD_android_app.md", "# stray BRD\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "duplicate-doc" in out
        assert "android/BRD_android_app.md" in out

    def test_a_duplicate_in_docs_itself_fails(self, tmp_repo, capsys):
        _canonical_trio(tmp_repo)
        tmp_repo.write("docs/TRD_v1.md", "# old TRD\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "duplicate-doc" in out

    def test_a_similarly_named_but_distinct_doc_passes(self, tmp_repo, capsys):
        _canonical_trio(tmp_repo)
        # 'business-requirements' is not *named* BRD, so it is not a duplicate.
        tmp_repo.write("docs/business/business-requirements.md", "# biz\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out


def test_passes_on_real_repository(capsys):
    """The real repo carries exactly the canonical trio and no duplicates.
    If this fails the finding is real: consolidate the stray file, do not relax
    the rule."""
    rc = ds.main(["--root", str(project_root())])
    out = capsys.readouterr().out
    assert rc == int(Exit.OK), f"real repository violates Rule 3:\n{out}"
