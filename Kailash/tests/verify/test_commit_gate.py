"""The critical-path commit confirmation gate (task 7.3).

The pure half is tested directly; the end-to-end half installs the gate as a
real `pre-commit` git hook in a throwaway repository and asserts git itself
refuses or accepts the commit. The end-to-end case matters because the failure
mode being guarded against is "the hook is wired wrong and every commit sails
through" -- only a real `git commit` exercises the wiring.
"""
from __future__ import annotations

import stat
import subprocess

from scripts.verify import commit_gate

# --------------------------------------------------------------------------
# The pure gate
# --------------------------------------------------------------------------


def test_non_critical_paths_pass_silently():
    code, lines = commit_gate.gate(["backend/app/main.py", "README.md"], env={})
    assert code == 0
    assert lines == []


def test_critical_path_without_token_is_refused_naming_the_path():
    code, lines = commit_gate.gate(["docker-compose.yml"], env={})
    assert code == 1
    text = "\n".join(lines)
    assert "docker-compose.yml" in text
    assert "CONFIRM_CRITICAL_PATH=1" in text
    # Honest about its own limits: the bypass and the real enforcement.
    assert "--no-verify" in text
    assert "preflight" in text


def test_critical_path_with_token_proceeds_and_says_so():
    code, lines = commit_gate.gate(
        ["deploy/host/deploy.sh"], env={"CONFIRM_CRITICAL_PATH": "1"})
    assert code == 0
    assert "deploy/host/deploy.sh" in "\n".join(lines)


def test_prefix_matching_is_segment_aware():
    """`deploy/` must not match `deployment-notes.md`."""
    code, _ = commit_gate.gate(["deployment-notes.md"], env={})
    assert code == 0


def test_workflow_files_are_critical():
    code, _ = commit_gate.gate([".github/workflows/ci.yml"], env={})
    assert code == 1


# --------------------------------------------------------------------------
# End to end, through a real git hook
# --------------------------------------------------------------------------

HOOK = """#!/bin/sh
# What the pre-commit framework does, reduced to one line: staged names in,
# gate's exit code out.
exec python -m scripts.verify.commit_gate $(git diff --cached --name-only)
"""


def _install_hook(repo) -> None:
    hook = repo.root / ".git" / "hooks" / "pre-commit"
    hook.write_text(HOOK, encoding="utf-8", newline="\n")
    # Linux git silently skips a hook without the execute bit -- the commit
    # then succeeds and the "refuses" half of the test fails. Windows git
    # ignores the bit entirely, so this is load-bearing only on CI.
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _commit(repo, message, *, env_extra=None, project_root=None) -> subprocess.CompletedProcess:
    import os
    env = dict(os.environ)
    env["PYTHONPATH"] = str(project_root)
    env.pop("CONFIRM_CRITICAL_PATH", None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(["git", "commit", "-m", message],
                          cwd=repo.root, env=env,
                          capture_output=True, text=True, check=False)


def test_real_git_refuses_then_accepts_with_the_token(tmp_repo, request):
    project_root = request.config.rootpath
    _install_hook(tmp_repo)
    tmp_repo.write("docker-compose.yml", "services: {}\n")

    refused = _commit(tmp_repo, "critical", project_root=project_root)
    assert refused.returncode != 0
    assert "CONFIRM_CRITICAL_PATH" in refused.stdout + refused.stderr
    assert tmp_repo.git("log", "--oneline") == ""

    accepted = _commit(tmp_repo, "critical",
                       env_extra={"CONFIRM_CRITICAL_PATH": "1"},
                       project_root=project_root)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    assert "critical" in tmp_repo.git("log", "--oneline")


def test_real_git_passes_non_critical_without_a_token(tmp_repo, request):
    project_root = request.config.rootpath
    _install_hook(tmp_repo)
    tmp_repo.write("README.md", "hello\n")

    result = _commit(tmp_repo, "docs", project_root=project_root)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "docs" in tmp_repo.git("log", "--oneline")
