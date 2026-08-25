"""The destructive-operation guard in deploy/host/deploy.sh (task 7.2).

The two guard functions are *extracted* and evaluated in isolation. Sourcing
deploy.sh is not an option: it ends with `main "$@"`, so sourcing it would
install Docker and deploy the stack from inside the test suite.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "deploy" / "host" / "deploy.sh"


def _find_bash() -> str | None:
    """Prefer Git bash over WSL: WSL cannot see Windows temp paths."""
    for candidate in (
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ):
        if Path(candidate).is_file():
            return candidate
    found = shutil.which("bash")
    if found and "system32" in found.lower():
        return None  # WSL; its filesystem view is not ours
    return found


BASH = _find_bash()
pytestmark = pytest.mark.skipif(BASH is None, reason="no usable bash")


def _extract(name: str, text: str) -> str:
    """Pull one `name() { ... }` definition out by brace matching."""
    m = re.search(rf"^{name}\(\)\s*\{{", text, re.M)
    assert m, f"{name}() not found in deploy.sh"
    depth, i = 0, m.end() - 1
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[m.start():i + 1]
        i += 1
    raise AssertionError(f"unbalanced braces in {name}()")


def _harness() -> str:
    text = SCRIPT.read_text(encoding="utf-8")
    body = "\n\n".join(_extract(n, text)
                       for n in ("normalise_remote", "assert_expected_checkout"))
    fd, path = tempfile.mkstemp(suffix=".sh", text=True)
    # utf-8 explicitly: the guard's messages contain non-ASCII, and Python on
    # Windows would otherwise write cp1252 and fail.
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("#!/usr/bin/env bash\n" + body + "\n")
    return path


def _posix(p: Path | str) -> str:
    s = str(p).replace("\\", "/")
    if len(s) > 1 and s[1] == ":":
        s = f"/{s[0].lower()}{s[2:]}"
    return s


def _call(func: str, *args: str) -> tuple[int, str, str]:
    harness = _harness()
    try:
        quoted = " ".join(f'"{a}"' for a in args)
        script = f'source "{_posix(harness)}"\n{func} {quoted}\n'
        r = subprocess.run([BASH, "-c", script], capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr
    finally:
        os.unlink(harness)


def _git_repo(path: Path, origin: str) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "remote", "add", "origin", origin], cwd=path, check=True)
    return path


class TestNormaliseRemote:
    @pytest.mark.parametrize("url", [
        "git@github.com:urgaa-eka/kailash.git",  # secret-scan: allow negative fixture for the slug rule
        "https://github.com/urgaa-eka/kailash.git",
        "https://github.com/urgaa-eka/kailash",
        "ssh://git@github.com/urgaa-eka/kailash.git",
        "https://user@github.com/urgaa-eka/kailash.git",
        "https://github.com/urgaa-eka/kailash/",
    ])
    def test_every_form_reduces_to_the_same_slug(self, url):
        rc, out, err = _call("normalise_remote", url)
        assert out.strip() == "urgaa-eka/kailash", f"{url} -> {out!r} {err}"

    def test_matches_the_python_normaliser(self):
        """The shell guard and the CI check must agree, or one is enforcing a
        different rule than the other and only one of them will be right."""
        from scripts.verify.repo_state import normalise_remote
        for url in ("git@github.com:urgaa-eka/kailash.git",
                    "https://github.com/urgaa-eka/kailash",
                    "ssh://git@github.com/urgaa-eka/kailash.git",
                    "https://user@github.com/urgaa-eka/kailash.git"):
            _, out, _ = _call("normalise_remote", url)
            assert out.strip() == normalise_remote(url), url


class TestAssertExpectedCheckout:
    def test_accepts_the_expected_repository(self, tmp_path):
        d = _git_repo(tmp_path / "ok", "https://github.com/urgaa-eka/kailash.git")
        rc, out, err = _call("assert_expected_checkout", _posix(d))
        assert rc == 0, f"{out}{err}"

    def test_accepts_the_ssh_form(self, tmp_path):
        d = _git_repo(tmp_path / "ssh", "git@github.com:urgaa-eka/kailash.git")
        rc, out, err = _call("assert_expected_checkout", _posix(d))
        assert rc == 0, f"{out}{err}"

    def test_refuses_a_different_repository(self, tmp_path):
        """The exact defect that was live: the script named flywithvvk while
        origin was urgaa-eka."""  # secret-scan: allow negative fixture for the slug rule
        d = _git_repo(tmp_path / "wrong",
                      "https://github.com/flywithvvk/kailash.git")  # secret-scan: allow negative fixture for the slug rule
        rc, _, err = _call("assert_expected_checkout", _posix(d))
        assert rc != 0
        assert "flywithvvk/kailash" in err  # secret-scan: allow negative fixture for the slug rule

    def test_refuses_a_non_git_directory(self, tmp_path):
        d = tmp_path / "plain"
        d.mkdir()
        (d / "important.txt").write_text("data")
        rc, _, err = _call("assert_expected_checkout", _posix(d))
        assert rc != 0
        assert "not a git work tree" in err

    def test_refuses_a_repository_with_no_origin(self, tmp_path):
        d = tmp_path / "noremote"
        d.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=d, check=True)
        rc, _, err = _call("assert_expected_checkout", _posix(d))
        assert rc != 0
        assert "no origin remote" in err

    def test_refuses_a_missing_directory(self, tmp_path):
        rc, _, _ = _call("assert_expected_checkout", _posix(tmp_path / "absent"))
        assert rc != 0


class TestGuardIsActuallyWired:
    """A guard that is defined but never called is decoration."""

    def test_called_before_every_destructive_operation(self):
        body = SCRIPT.read_text(encoding="utf-8").split("update_code()", 1)[1]
        guard_at = body.index("assert_expected_checkout")
        for destructive in ("git reset --hard", "git clean -fd"):
            assert body.index(destructive) > guard_at, (
                f"{destructive} appears before the guard")

    def test_clone_path_refuses_a_non_empty_directory(self):
        assert "refusing to clone over it" in SCRIPT.read_text(encoding="utf-8")

    def test_sourcing_deploy_sh_would_run_it(self):
        """Documents why these tests extract rather than source. If this ever
        stops being true the harness can be simplified -- but silently
        sourcing a script that ends in `main "$@"` deploys from a test run."""
        assert SCRIPT.read_text(encoding="utf-8").rstrip().endswith('main "$@"')
