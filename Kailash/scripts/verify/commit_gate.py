"""Refuse an unconfirmed commit that touches a Deployment_Critical_Path.

Wired as a `repo: local` hook in `.pre-commit-config.yaml`, which passes the
staged filenames as arguments. A commit staging anything under
`repo_state.CRITICAL_PATHS` is refused until the operator re-runs with
`CONFIRM_CRITICAL_PATH=1` in the environment.

An environment token, not an interactive prompt: pre-commit hooks have no
reliable TTY, from an IDE's git integration a prompt hangs or silently fails,
and a safety gate that hangs gets disabled. Setting a variable is a
deliberate, auditable act with the same intent and none of the fragility.

This hook catches the accidental case, which is the common one. `--no-verify`
bypasses it entirely -- that is a property of git hooks, not a defect here --
and the unbypassable enforcement is the CI `preflight` job plus branch
protection on `main`.
"""
from __future__ import annotations

import os
import sys

from .repo_state import _under_critical_path

CONFIRM_VARIABLE = "CONFIRM_CRITICAL_PATH"


def gate(paths: list[str], env: dict | None = None) -> tuple[int, list[str]]:
    """(exit code, message lines). Pure given `paths` and `env`."""
    environment = os.environ if env is None else env
    hits = [(p, c) for p in paths if (c := _under_critical_path(p))]
    if not hits:
        return 0, []

    if environment.get(CONFIRM_VARIABLE) == "1":
        return 0, [f"critical-path commit confirmed via {CONFIRM_VARIABLE}=1:"] + [
            f"  {path}  ({crit})" for path, crit in hits
        ]

    lines = ["Commit touches Deployment_Critical_Path files:"]
    lines += [f"  {path}  (critical path: {crit})" for path, crit in hits]
    lines += [
        "",
        "These files steer what production runs. If this change is deliberate,",
        f"re-run with the confirmation token:  {CONFIRM_VARIABLE}=1 git commit ...",
        "",
        "`git commit --no-verify` also bypasses this hook -- it is a convenience",
        "gate for the accidental case. The enforcement that cannot be bypassed",
        "is the CI `preflight` job plus branch protection on `main`.",
    ]
    return 1, lines


def main(argv: list[str] | None = None) -> int:
    paths = sys.argv[1:] if argv is None else argv
    code, lines = gate(paths)
    if lines:
        print("\n".join(lines))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
