"""The shared contract: exit-code precedence, the renderer, root resolution."""
from __future__ import annotations

import json

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scripts.verify.common import (
    Exit,
    Finding,
    Report,
    Suppression,
    Unavailable,
    Usage,
    base_parser,
    load_corpus,
    resolve_root,
    run,
)


class TestExitPrecedence:
    def test_empty_report_is_ok(self):
        assert Report().exit_code() is Exit.OK

    def test_findings_fail(self):
        r = Report()
        r.add(Finding(rule="x"))
        assert r.exit_code() is Exit.FAILED

    def test_unavailable_outranks_findings(self):
        """A check that could not run part of itself must not report OK, and
        must not report a plain failure either -- the absence of findings from
        the part that did not run means nothing."""
        r = Report()
        r.add(Finding(rule="x"))
        r.unavailable.append("no network")
        assert r.exit_code() is Exit.UNAVAILABLE

    def test_unavailable_alone(self):
        r = Report()
        r.unavailable.append("no docker")
        assert r.exit_code() is Exit.UNAVAILABLE


class TestRenderer:
    def test_rule_only(self):
        assert Finding(rule="r").render() == "FAIL r"

    def test_path_without_line(self):
        assert Finding(rule="r", path="a/b").render() == "FAIL r a/b"

    def test_path_with_line(self):
        assert Finding(rule="r", path="a/b", line=7).render() == "FAIL r a/b:7"

    def test_observed_and_expected(self):
        out = Finding(rule="r", path="p", line=1, observed="x", expected="y").render()
        assert out == "FAIL r p:1 observed=x expected=y"

    def test_observed_without_expected(self):
        """Not every finding has a singular required value -- an orphan
        container has an observed image and nothing to compare it against."""
        assert Finding(rule="r", path="p", observed="x").render() == "FAIL r p observed=x"

    def test_expected_without_observed(self):
        assert Finding(rule="r", path="p", expected="y").render() == "FAIL r p expected=y"

    def test_message_appended(self):
        out = Finding(rule="r", observed=1, expected=2, message="why").render()
        assert out.endswith("-- why")

    def test_collection_values_are_sorted(self):
        out = Finding(rule="r", observed=["b", "a"]).render()
        assert "observed=a,b" in out

    def test_line_zero_is_rendered_not_dropped(self):
        assert Finding(rule="r", path="p", line=0).render() == "FAIL r p:0"


class TestReportRendering:
    def test_ok_when_nothing_found(self):
        assert Report().render() == "OK"

    def test_suppressions_printed_even_on_success(self):
        """A suppression list that grows silently is a path to green nobody
        reviews."""
        r = Report()
        r.suppressions.append(Suppression("rule", "p", 3, "because"))
        out = r.render()
        assert "suppressed rule p:3 -- because" in out
        assert "1 suppression(s) in force" in out
        assert r.exit_code() is Exit.OK

    def test_json_carries_exit_code(self):
        r = Report()
        r.add(Finding(rule="r"))
        assert json.loads(r.to_json())["exit_code"] == int(Exit.FAILED)


class TestRootResolution:
    def test_explicit_root(self, tmp_repo):
        assert resolve_root(tmp_repo.root) == tmp_repo.root.resolve()

    def test_missing_root_is_usage(self, tmp_path):
        with pytest.raises(Usage):
            resolve_root(tmp_path / "nope")

    def test_defaults_to_the_git_top_level(self, tmp_repo, monkeypatch):
        """Absent `--root`, a check reads the repository it is standing in, from
        any depth. Resolving against the cwd instead would make the same check
        pass or fail depending on which directory it was invoked from."""
        deep = tmp_repo.root / "nested" / "deeper"
        deep.mkdir(parents=True)
        monkeypatch.chdir(deep)
        assert resolve_root(None).resolve() == tmp_repo.root.resolve()

    def test_outside_a_work_tree_is_unavailable(self, tmp_path, monkeypatch):
        """No repository is a missing prerequisite, not a defect in one."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(Unavailable):
            resolve_root(None)


class TestCliSurface:
    """`[--root PATH] [--json] [--emit-record PATH]`, identical for every check,
    so a caller learns the surface once."""

    def _failing_check(self, _args):
        r = Report()
        r.add(Finding(rule="r", path="p", line=2, observed="x", expected="y"))
        return r

    def test_json_flag_emits_json(self, capsys):
        rc = run(self._failing_check, ["--json"], base_parser("t"))
        payload = json.loads(capsys.readouterr().out)
        assert rc == int(Exit.FAILED)
        assert payload["exit_code"] == int(Exit.FAILED)
        assert payload["findings"][0] == {
            "rule": "r", "path": "p", "line": 2,
            "observed": "x", "expected": "y", "message": "",
        }

    def test_emit_record_writes_the_record(self, tmp_path, capsys):
        """Records are generated by the check that has the evidence, not written
        by hand, so the destination directory may not exist yet."""
        target = tmp_path / "docs" / "records" / "rec.json"
        rc = run(self._failing_check, ["--emit-record", str(target)], base_parser("t"))
        capsys.readouterr()
        assert rc == int(Exit.FAILED)
        assert json.loads(target.read_text(encoding="utf-8"))["exit_code"] == int(Exit.FAILED)

    def test_text_output_by_default(self, capsys):
        rc = run(self._failing_check, [], base_parser("t"))
        assert rc == int(Exit.FAILED)
        assert capsys.readouterr().out.strip() == "FAIL r p:2 observed=x expected=y"


class TestCorpus:
    def test_lists_tracked_files_only(self, tmp_repo):
        tmp_repo.write("tracked.txt", "hi")
        (tmp_repo.root / "untracked.txt").write_text("hi")
        corpus = load_corpus(tmp_repo.root)
        assert "tracked.txt" in corpus.files
        assert "untracked.txt" not in corpus.files

    def test_non_utf8_is_skipped_and_counted(self, tmp_repo):
        tmp_repo.write("good.txt", "text")
        tmp_repo.write_bytes("bad.bin", b"\xff\xfe\x00\x01binary")
        corpus = load_corpus(tmp_repo.root)
        seen = dict(corpus.texts())
        assert "good.txt" in seen
        assert "bad.bin" not in seen
        assert corpus.skipped_binary == 1

    def test_paths_with_spaces_survive(self, tmp_repo):
        tmp_repo.write("dir with space/a b.txt", "x")
        corpus = load_corpus(tmp_repo.root)
        assert "dir with space/a b.txt" in corpus.files


class TestNeverRaises:
    """An unhandled traceback exits 1, which is indistinguishable from a check
    that ran and found something. That ambiguity makes a broken check look
    like a working gate."""

    def test_unexpected_exception_becomes_unavailable(self, capsys):
        def boom(_args):
            raise ValueError("kaboom")
        rc = run(boom, [], base_parser("t"))
        assert rc == int(Exit.UNAVAILABLE)
        assert "kaboom" in capsys.readouterr().err

    def test_unavailable_maps_to_2(self):
        def missing(_args):
            raise Unavailable("no git")
        assert run(missing, [], base_parser("t")) == int(Exit.UNAVAILABLE)

    def test_usage_maps_to_3(self):
        def bad(_args):
            raise Usage("wrong")
        assert run(bad, [], base_parser("t")) == int(Exit.USAGE)

    def test_bad_flag_maps_to_usage(self):
        assert run(lambda a: Report(), ["--nonexistent"], base_parser("t")) == int(Exit.USAGE)


@given(
    findings=st.integers(min_value=0, max_value=5),
    unavailable=st.integers(min_value=0, max_value=3),
)
def test_property_exit_code_precedence(findings, unavailable):
    r = Report()
    for i in range(findings):
        r.add(Finding(rule=f"r{i}"))
    for i in range(unavailable):
        r.unavailable.append(f"u{i}")
    if unavailable:
        assert r.exit_code() is Exit.UNAVAILABLE
    elif findings:
        assert r.exit_code() is Exit.FAILED
    else:
        assert r.exit_code() is Exit.OK


@given(
    rule=st.text(min_size=1, max_size=12, alphabet=st.characters(whitelist_categories=("Ll", "Nd"))),
    path=st.text(min_size=1, max_size=12, alphabet=st.characters(whitelist_categories=("Ll",))),
    line=st.integers(min_value=0, max_value=9999),
)
def test_property_render_contains_every_field(rule, path, line):
    out = Finding(rule=rule, path=path, line=line, observed="o", expected="e").render()
    assert rule in out and path in out and str(line) in out
    assert "observed=o" in out and "expected=e" in out
