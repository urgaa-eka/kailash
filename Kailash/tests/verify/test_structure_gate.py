"""Tests for the Rule 2 gate: department→feature, mirrored, nothing loose."""
from __future__ import annotations

from scripts.verify import structure_gate as sg
from scripts.verify.common import Exit, project_root
from scripts.verify.structure_gate import BACKEND_FEATURES, CANONICAL_FEATURES, _snake


def _clean(repo, *, skip_backend=None):
    """A department→feature tree that satisfies Rule 2.

    Generated from the gate's own registry so the fixture cannot drift from the
    rule it exercises: every canonical feature gets a frontend folder, every
    backend-present feature gets its snake_case mirror.
    """
    for feat in CANONICAL_FEATURES:
        repo.write(f"frontend/src/features/{feat}/index.js", "export default {}\n")
    repo.write("frontend/src/platform/lib/api.js", "export const x = 1\n")
    repo.write("frontend/src/App.js", "export default function App() {}\n")
    repo.write("frontend/src/index.js", "// entry\n")

    for feat in BACKEND_FEATURES:
        if feat == skip_backend:
            continue
        repo.write(f"backend/features/{_snake(feat)}/__init__.py", "")
    repo.write("backend/features/__init__.py", "")
    repo.write("backend/platform/__init__.py", "")
    repo.write("backend/services/company/app/main.py", "app = 1\n")
    repo.write("backend/main.py", "app = 1\n")
    repo.write("backend/__init__.py", "")


def _run(root, capsys):
    rc = sg.main(["--root", str(root)])
    return rc, capsys.readouterr().out


class TestGate:
    def test_clean_tree_passes(self, tmp_repo, capsys):
        _clean(tmp_repo)
        tmp_repo.commit()
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out

    def test_unregistered_frontend_feature_fails(self, tmp_repo, capsys):
        _clean(tmp_repo)
        tmp_repo.write("frontend/src/features/wombat/index.js", "// ad hoc\n")
        tmp_repo.commit()
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "unregistered-feature" in out and "wombat" in out

    def test_unregistered_backend_feature_fails(self, tmp_repo, capsys):
        _clean(tmp_repo)
        tmp_repo.write("backend/features/wombat/__init__.py", "")
        tmp_repo.commit()
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "unregistered-feature" in out and "wombat" in out

    def test_loose_frontend_source_fails(self, tmp_repo, capsys):
        """A folder at frontend/src/ that is neither features/ nor platform/."""
        _clean(tmp_repo)
        tmp_repo.write("frontend/src/pages/Legacy.jsx", "// loose\n")
        tmp_repo.commit()
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "loose-frontend-source" in out and "pages" in out

    def test_loose_backend_source_fails(self, tmp_repo, capsys):
        """A package at backend/ outside features/ / platform/ / services/."""
        _clean(tmp_repo)
        tmp_repo.write("backend/app/main.py", "# the old monolith root\n")
        tmp_repo.commit()
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "loose-backend-source" in out and "app" in out

    def test_loose_file_inside_backend_features_fails(self, tmp_repo, capsys):
        _clean(tmp_repo)
        tmp_repo.write("backend/features/helpers.py", "# not a feature\n")
        tmp_repo.commit()
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "unregistered-feature" in out and "helpers.py" in out

    def test_missing_backend_mirror_fails(self, tmp_repo, capsys):
        """A feature present on the frontend but missing its backend package."""
        _clean(tmp_repo, skip_backend="auth")
        tmp_repo.commit()
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "mirror-drift" in out and "auth" in out

    def test_kebab_snake_equivalence_holds(self, tmp_repo, capsys):
        """eka-brain (frontend) and eka_brain (backend) are the same feature and
        must not be reported as drift."""
        _clean(tmp_repo)
        tmp_repo.commit()
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)
        assert "eka-brain" not in out and "eka_brain" not in out


def test_registry_is_internally_consistent():
    """Every backend feature is a canonical feature (the snake mirror of one)."""
    assert BACKEND_FEATURES <= CANONICAL_FEATURES


def test_passes_on_real_repository(capsys):
    """The real repo satisfies Rule 2. If this fails the finding is real: move
    the stray source under features/ or platform/, or register the feature
    deliberately -- do not relax the gate."""
    rc = sg.main(["--root", str(project_root())])
    out = capsys.readouterr().out
    assert rc == int(Exit.OK), f"real repository violates Rule 2:\n{out}"
