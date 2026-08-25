"""Repository state: nothing uncommitted on a path deploy.sh will destroy."""
from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from scripts.verify import repo_state
from scripts.verify.common import Exit

# Every remote form git accepts for one repository. Used by the Python
# property and by the bash-parity property, so the two cannot drift apart by
# one of them quietly testing a smaller set.
URL_FORMS = (
    "git@github.com:{owner}/{name}.git",
    "git@github.com:{owner}/{name}",
    "https://github.com/{owner}/{name}.git",
    "https://github.com/{owner}/{name}",
    "https://github.com/{owner}/{name}/",
    "https://github.com/{owner}/{name}.git/",
    "http://github.com/{owner}/{name}.git",
    "https://user@github.com/{owner}/{name}.git",
    "https://user:pass@github.com/{owner}/{name}.git",
    "https://github.com:443/{owner}/{name}.git",
    "ssh://git@github.com/{owner}/{name}.git",
    "ssh://git@github.com:22/{owner}/{name}.git",
    "ssh://github.com/{owner}/{name}",
    "git://github.com/{owner}/{name}.git",
    "github.com:{owner}/{name}.git",
    "{owner}/{name}",
    "{owner}/{name}.git",
)


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

    def test_copy_yields_both_sides(self):
        entries = repo_state.parse_porcelain("C  deploy/a.sh -> deploy/b.sh")
        assert ("C ", "deploy/a.sh") in entries
        assert ("C ", "deploy/b.sh") in entries

    def test_quoted_path_with_spaces(self):
        entries = repo_state.parse_porcelain(' M "deploy/a file.sh"')
        assert entries == [(" M", "deploy/a file.sh")]

    def test_quoted_rename_with_spaces_on_both_sides(self):
        """git quotes each side of a rename independently."""
        entries = repo_state.parse_porcelain(
            'R  "deploy/old name.sh" -> "deploy/new name.sh"')
        assert ("R ", "deploy/old name.sh") in entries
        assert ("R ", "deploy/new name.sh") in entries

    def test_arrow_in_a_filename_is_not_a_rename(self):
        """Only R and C entries carry ` -> `. Splitting an untracked path on
        its own arrow would report two paths that do not exist and miss the one
        that does -- which lives under deploy/."""
        entries = repo_state.parse_porcelain('?? "deploy/a -> b.sh"')
        assert entries == [("??", "deploy/a -> b.sh")]
        assert repo_state._under_critical_path(entries[0][1]) == "deploy/"

    def test_quoted_rename_source_containing_an_arrow(self):
        entries = repo_state.parse_porcelain(
            'R  "deploy/a -> b.sh" -> deploy/c.sh')
        assert ("R ", "deploy/a -> b.sh") in entries
        assert ("R ", "deploy/c.sh") in entries

    def test_octal_escaped_non_ascii_path(self):
        """git escapes non-ASCII one octal sequence per byte, so the escapes
        resolve to bytes before they decode as UTF-8."""
        entries = repo_state.parse_porcelain(' M "deploy/caf\\303\\251.sh"')
        assert entries == [(" M", "deploy/café.sh")]

    def test_staged_and_unstaged_both_seen(self):
        entries = repo_state.parse_porcelain("M  a.txt\n M b.txt\n?? c.txt")
        assert len(entries) == 3

    def test_staged_and_unstaged_status_preserved(self):
        """`M ` is staged, ` M` is not. Both are uncommitted, and the finding
        must say which so the operator knows what to do about it."""
        staged = repo_state.findings_in_porcelain("M  docker-compose.yml")
        unstaged = repo_state.findings_in_porcelain(" M docker-compose.yml")
        assert staged[0].observed == "status=M"
        assert unstaged[0].observed == "status=M"
        assert staged[0].rule == unstaged[0].rule == "critical-path-dirty"


class TestPrefixMatching:
    def test_directory_prefix_matches_children(self):
        assert repo_state._under_critical_path("deploy/host/deploy.sh") == "deploy/"

    def test_prefix_is_segment_aware(self):
        """`deploy/` must not match `deployment-notes.md`. A check that fires
        on unrelated files is a check that gets switched off."""
        assert repo_state._under_critical_path("deployment-notes.md") is None
        assert repo_state.findings_in_porcelain(" M deployment-notes.md") == []

    def test_sibling_directory_sharing_a_prefix_is_not_matched(self):
        assert repo_state._under_critical_path(
            ".github/workflows-old/ci.yml") is None

    def test_exact_file_paths(self):
        assert repo_state._under_critical_path("docker-compose.yml") == "docker-compose.yml"
        assert repo_state._under_critical_path("docker-compose.override.yml") is None

    def test_unrelated_path_ignored(self):
        assert repo_state._under_critical_path("frontend/src/App.js") is None

    def test_collapsed_untracked_directory_is_reported_for_its_pathspec(self):
        """git collapses an untracked tree to a directory entry. `?? .github/
        workflows/` is not a descendant of `.github/workflows/`, so it is the
        pathspec that was queried -- not a prefix filter -- that accounts for
        it."""
        assert repo_state._under_critical_path(".github/workflows/") == ".github/workflows/"
        findings = repo_state.findings_in_porcelain(
            "?? .github/", queried=".github/workflows/")
        assert [f.path for f in findings] == [".github/"]


class TestNormaliseRemote:
    @pytest.mark.parametrize("form", URL_FORMS)
    def test_every_form_reduces_to_the_same_slug(self, form):
        url = form.format(owner="urgaa-eka", name="kailash")
        assert repo_state.normalise_remote(url) == "urgaa-eka/kailash", url

    def test_empty_is_none(self):
        assert repo_state.normalise_remote("") is None
        assert repo_state.normalise_remote("   ") is None

    @pytest.mark.parametrize("url", [
        "not a url",
        "https://github.com/urgaa-eka",
        "https://api.kailash-ai.in/api/health",
    ])
    def test_non_repository_input_is_refused(self, url):
        """Refusing beats guessing: the guard compares against an exact slug,
        so anything that is not a two-segment repository path must not resolve
        to one."""
        assert repo_state.normalise_remote(url) != "urgaa-eka/kailash"


class TestAgreesWithTheShellGuard:
    """`deploy.sh` normalises the origin URL in bash before `git reset --hard`
    and `git clean -fd`. If that normaliser and this one disagree, one of them
    is enforcing a different rule, and the shell one is the one standing in
    front of an irreversible command on the production host."""

    def test_every_form_agrees(self, bash_normalise):
        urls = [f.format(owner="urgaa-eka", name="kailash") for f in URL_FORMS]
        assert bash_normalise(urls) == [repo_state.normalise_remote(u) for u in urls]

    def test_both_refuse_the_same_non_repository_input(self, bash_normalise):
        """Where the two cannot agree on a value -- input that is not a
        repository path at all -- they must still agree on the verdict. bash
        echoes the input, this returns None; neither equals the expected slug,
        so both refuse."""
        urls = ["not a url", "https://github.com/urgaa-eka",
                "https://github.com/urgaa-eka/kailash/extra",
                "https://api.kailash-ai.in/api/health", ""]
        shell = bash_normalise(urls)
        for url, shell_slug in zip(urls, shell, strict=True):
            python_slug = repo_state.normalise_remote(url)
            assert shell_slug != repo_state.EXPECTED_SLUG, url
            assert python_slug != repo_state.EXPECTED_SLUG, url


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

    def test_prefix_collision_passes_end_to_end(self, tmp_repo, capsys):
        """The live shape of the segment-aware rule: a real file named
        deployment-notes.md must not fail the check."""
        self._clean(tmp_repo)
        (tmp_repo.root / "deployment-notes.md").write_text("notes\n")
        rc = repo_state.main(["--root", str(tmp_repo.root)])
        out = capsys.readouterr().out
        assert rc == int(Exit.OK), out

    def test_untracked_file_under_a_critical_path_fails(self, tmp_repo, capsys):
        """git collapses a wholly untracked tree: globally this shows as
        `?? .github/`, which no prefix of `.github/workflows/` matches. The
        per-pathspec query is what catches it -- and it must, because
        `git clean -fd` deletes untracked files."""
        self._clean(tmp_repo)
        wf = tmp_repo.root / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text("on: push\n")
        rc = repo_state.main(["--root", str(tmp_repo.root)])
        out = capsys.readouterr().out
        assert rc == int(Exit.FAILED), out
        assert ".github/" in out

    def test_quoted_path_with_spaces_fails_end_to_end(self, tmp_repo, capsys):
        self._clean(tmp_repo)
        (tmp_repo.root / "deploy" / "a file.sh").write_text("#!/bin/sh\n")
        rc = repo_state.main(["--root", str(tmp_repo.root)])
        out = capsys.readouterr().out
        assert rc == int(Exit.FAILED), out
        assert "a file.sh" in out

    def test_rename_under_a_critical_path_fails(self, tmp_repo, capsys):
        self._clean(tmp_repo)
        tmp_repo.git("mv", "deploy/host/deploy.sh", "deploy/host/renamed.sh")
        rc = repo_state.main(["--root", str(tmp_repo.root)])
        out = capsys.readouterr().out
        assert rc == int(Exit.FAILED), out
        assert "renamed.sh" in out or "deploy.sh" in out

    def test_wrong_slug_in_deploy_script_fails(self, tmp_repo, capsys):
        tmp_repo.deploy_sh("https://github.com/flywithvvk/kailash.git")  # secret-scan: allow negative fixture for the slug rule
        tmp_repo.commit()
        rc = repo_state.main(["--root", str(tmp_repo.root)])
        out = capsys.readouterr().out
        assert rc == int(Exit.FAILED)
        assert "flywithvvk/kailash" in out  # secret-scan: allow negative fixture for the slug rule

    @pytest.mark.parametrize("form", [
        "git@github.com:{owner}/{name}.git",
        "ssh://git@github.com:22/{owner}/{name}.git",
        "https://github.com:443/{owner}/{name}.git",
        "git://github.com/{owner}/{name}.git",
    ])
    def test_expected_slug_in_any_form_passes(self, tmp_repo, capsys, form):
        """A valid checkout declared in an unusual form must not fail the gate.
        The rule reads whatever URL the script carries, so the normaliser's
        blind spots become false failures that block a deploy."""
        tmp_repo.deploy_sh(form.format(owner="urgaa-eka", name="kailash"))
        tmp_repo.commit()
        rc = repo_state.main(["--root", str(tmp_repo.root)])
        assert rc == int(Exit.OK), capsys.readouterr().out

    def test_absent_deploy_script_is_a_finding(self, tmp_repo, capsys):
        """A vacuous pass is the dangerous outcome: the script is what runs
        git reset --hard on the production host."""
        tmp_repo.write("README.md", "x\n")
        tmp_repo.commit()
        rc = repo_state.main(["--root", str(tmp_repo.root)])
        out = capsys.readouterr().out
        assert rc == int(Exit.FAILED)
        assert "deploy/host/deploy.sh" in out


# --------------------------------------------------------------------------
# Property 18: URL normalisation across every form
# --------------------------------------------------------------------------

_SEGMENT = st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
                   min_size=1, max_size=12)


@given(owner=_SEGMENT, name=_SEGMENT, form=st.sampled_from(URL_FORMS))
def test_property_normalisation_is_form_independent(owner, name, form):
    """A normaliser that silently returns the URL unchanged makes the deploy
    guard reject every valid checkout -- a safety feature turned into an
    outage. So: same slug from every form, and never the raw URL."""
    url = form.format(owner=owner, name=name)
    slug = repo_state.normalise_remote(url)
    assert slug == f"{owner}/{name}"
    assert slug != url or url == f"{owner}/{name}"


@settings(max_examples=20, deadline=None)
@given(pairs=st.lists(st.tuples(_SEGMENT, _SEGMENT, st.sampled_from(URL_FORMS)),
                      min_size=1, max_size=10))
def test_property_shell_and_python_normalisers_agree(bash_normalise, pairs):
    """Property 18 across both implementations.

    Batched into one bash call per example on purpose: the guard in deploy.sh
    stands in front of `git reset --hard` and `git clean -fd` on the production
    host, so agreement has to be checked over generated input rather than a
    handful of examples, and that has to be affordable enough to keep running.
    """
    urls = [form.format(owner=o, name=n) for o, n, form in pairs]
    assert bash_normalise(urls) == [repo_state.normalise_remote(u) for u in urls]


# --------------------------------------------------------------------------
# Property 17: working-tree cleanliness
# --------------------------------------------------------------------------

_CRITICAL = ("deploy/host/deploy.sh", "docker-compose.yml",
             ".github/workflows/ci.yml", "frontend/.firebaserc",
             "frontend/.env.production", "deploy/staging/compose.yml")
_INNOCENT = ("README.md", "deployment-notes.md", "frontend/src/App.js",
             "docker-compose.override.yml", ".github/dependabot.yml",
             ".github/workflows-old/ci.yml", "frontend/.env.development")


@given(paths=st.lists(st.sampled_from(_CRITICAL + _INNOCENT), max_size=8))
def test_property_only_critical_paths_are_findings(paths):
    for p in paths:
        assert (repo_state._under_critical_path(p) is not None) == (p in _CRITICAL)


@given(entries=st.lists(
    st.tuples(st.sampled_from(["M ", " M", "MM", "A ", "??", "D ", "AM"]),
              st.sampled_from(_CRITICAL + _INNOCENT)),
    max_size=8))
def test_property_working_tree_findings_name_every_dirty_critical_path(entries):
    """Property 17: findings exactly when something under a Deployment_Critical_Path
    is uncommitted, and every such path printed. Requirement 9.6 is the print,
    not just the exit code -- an operator who cannot see which file is dirty
    cannot clear the gate."""
    output = "\n".join(f"{status} {path}" for status, path in entries)
    findings = repo_state.findings_in_porcelain(output)
    dirty = {p for _, p in entries if p in _CRITICAL}

    assert bool(findings) == bool(dirty)
    assert {f.path for f in findings} == dirty
    rendered = "\n".join(f.render() for f in findings)
    for path in dirty:
        assert path in rendered


@given(entries=st.lists(
    st.tuples(st.sampled_from(["R ", "C ", "RM"]),
              st.sampled_from(_CRITICAL + _INNOCENT),
              st.sampled_from(_CRITICAL + _INNOCENT)),
    max_size=6))
def test_property_both_sides_of_a_rename_are_checked(entries):
    """The old name is what disappears from the critical path; the new name is
    what arrives on it. Either alone is a change to a file deploy.sh will
    destroy, so both sides count."""
    output = "\n".join(f"{s} {old} -> {new}" for s, old, new in entries)
    found = {f.path for f in repo_state.findings_in_porcelain(output)}
    expected = {p for _, old, new in entries for p in (old, new) if p in _CRITICAL}
    assert found == expected
