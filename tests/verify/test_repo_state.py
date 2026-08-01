"""Repository state: nothing uncommitted on a path deploy.sh will destroy."""
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scripts.verify import repo_state
from scripts.verify.common import Exit


class TestPorcelainParsing:
    def test_plain_entry(self):
        assert repo_state.parse_porcelain(" M docker-compose.yml") == [
            (" M", "docker-compose.yml")]

    def test_rename_yields_both_sides(self):
        """Either side landing on a critical path matters: the old name is
        what disappears, the new name is what arrives."""
        entries = repo_state.parse_porcelain("R  deploy/old.sh -> deploy/new.sh")
        assert ("R ", "deploy/old.sh") in entries
        assert ("R ", "deploy/new.sh") in entries

    def test_quoted_path_with_spaces(self):
        entries = repo_state.parse_porcelain(' M "deploy/a file.sh"')
        assert entries == [(" M", "deploy/a file.sh")]

    def test_staged_and_unstaged_both_seen(self):
        entries = repo_state.parse_porcelain("M  a.txt\n M b.txt\n?? c.txt")
        assert len(entries) == 3


class TestPrefixMatching:
    def test_directory_prefix_matches_children(self):
        assert repo_state._under_critical_path("deploy/vultr/deploy.sh") == "deploy/"

    def test_prefix_is_segment_aware(self):
        """`deploy/` must not match `deployment-notes.md`."""
        assert repo_state._under_critical_path("deployment-notes.md") is None

    def test_exact_file_paths(self):
        assert repo_state._under_critical_path("docker-compose.yml") == "docker-compose.yml"
        assert repo_state._under_critical_path("docker-compose.override.yml") is None

    def test_unrelated_path_ignored(self):
        assert repo_state._under_critical_path("frontend/src/App.js") is None


class TestNormaliseRemote:
    @pytest.mark.parametrize("url", [
        "git@github.com:urgaa-eka/kailash.git",
        "https://github.com/urgaa-eka/kailash.git",
        "https://github.com/urgaa-eka/kailash",
        "ssh://git@github.com/urgaa-eka/kailash.git",
        "https://user@github.com/urgaa-eka/kailash.git",
        "https://github.com/urgaa-eka/kailash/",
    ])
    def test_every_form_reduces_to_the_same_slug(self, url):
        assert repo_state.normalise_remote(url) == "urgaa-eka/kailash"

    def test_empty_is_none(self):
        assert repo_state.normalise_remote("") is None
        assert repo_state.normalise_remote("   ") is None


class TestEndToEnd:
    def _clean(self, repo):
        repo.deploy_sh("https://github.com/urgaa-eka/kailash.git")
        repo.commit()

    def test_clean_repo_passes(self, tmp_repo, capsys):
        self._clean(tmp_repo)
        rc = repo_state.main(["--root", str(tmp_repo.root)])
        assert rc == int(Exit.OK), capsys.readouterr().out

    def test_dirty_critical_path_fails(self, tmp_repo, capsys):
        self._clean(tmp_repo)
        (tmp_repo.root / "docker-compose.yml").write_text("services: {}\n")
        rc = repo_state.main(["--root", str(tmp_repo.root)])
        out = capsys.readouterr().out
        assert rc == int(Exit.FAILED)
        assert "docker-compose.yml" in out
        assert "git clean -fd" in out

    def test_dirty_non_critical_path_passes(self, tmp_repo, capsys):
        self._clean(tmp_repo)
        (tmp_repo.root / "README.md").write_text("hello\n")
        rc = repo_state.main(["--root", str(tmp_repo.root)])
        assert rc == int(Exit.OK), capsys.readouterr().out

    def test_wrong_slug_in_deploy_script_fails(self, tmp_repo, capsys):
        tmp_repo.deploy_sh("https://github.com/flywithvvk/kailash.git")  # secret-scan: allow negative fixture for the slug rule
        tmp_repo.commit()
        rc = repo_state.main(["--root", str(tmp_repo.root)])
        out = capsys.readouterr().out
        assert rc == int(Exit.FAILED)
        assert "flywithvvk/kailash" in out  # secret-scan: allow negative fixture for the slug rule


@given(
    owner=st.text(alphabet="abcdefghijklmnopqrstuvwxyz-", min_size=1, max_size=12),
    name=st.text(alphabet="abcdefghijklmnopqrstuvwxyz-", min_size=1, max_size=12),
    form=st.sampled_from(["git@github.com:{}/{}.git",
                          "https://github.com/{}/{}.git",
                          "https://github.com/{}/{}",
                          "ssh://git@github.com/{}/{}.git"]),
)
def test_property_normalisation_is_form_independent(owner, name, form):
    """A normaliser that silently returns the URL unchanged makes the deploy
    guard reject every valid checkout -- a safety feature turned into an
    outage. So: same slug from every form, and never the raw URL."""
    url = form.format(owner, name)
    slug = repo_state.normalise_remote(url)
    assert slug == f"{owner}/{name}"
    assert slug != url


@given(paths=st.lists(st.sampled_from([
    "deploy/vultr/deploy.sh", "docker-compose.yml", ".github/workflows/ci.yml",
    "README.md", "deployment-notes.md", "frontend/src/App.js",
]), min_size=0, max_size=6))
def test_property_only_critical_paths_are_findings(paths):
    critical = {"deploy/vultr/deploy.sh", "docker-compose.yml", ".github/workflows/ci.yml"}
    for p in paths:
        assert (repo_state._under_critical_path(p) is not None) == (p in critical)
