"""Assert RULES.md Rule 1: nothing loose at the repository root.

Rule 1 mandates a single master folder `Kailash/`, with the git root holding
*only* that folder, this project's one root document `RULES.md`, and the
unavoidable VCS/CI plumbing (`.github/` — GitHub Actions reads it from the root
and it cannot be nested — and `.gitignore`). "In GitHub I don't want to see a
single file outside this."

`doc_singletons` makes Rule 3 executable and `workflow_singletons` makes Rule 5's
file-set executable; this makes Rule 1 executable, so a stray file or folder at
the root fails CI instead of drifting in unnoticed.

One property: the git top level's tracked entries are exactly the allowed set.
Read from `git ls-tree HEAD` (tracked, top level only), so an untracked local
scratch file is not a CI failure but a committed stray one is.
"""
from __future__ import annotations

import subprocess

from .common import (
    Finding,
    Report,
    Unavailable,
    base_parser,
    git_top_level,
    resolve_root,
    run,
)

# The only entries allowed at the git repository root (RULES.md Rule 1).
ALLOWED_ROOT = frozenset({
    "RULES.md",
    "Kailash",
    ".github",
    ".gitignore",
})

# Rule 1 also requires the master folder itself to be present.
REQUIRED_ROOT = frozenset({"RULES.md", "Kailash"})


def _root_entries(git_root) -> list[str]:
    """Top-level tracked entries at the git root (names only)."""
    out = subprocess.run(
        ["git", "ls-tree", "--name-only", "HEAD"],
        cwd=git_root, capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        raise Unavailable(f"git ls-tree failed in {git_root}")
    return sorted(n for n in out.stdout.splitlines() if n)


def build_report(args) -> Report:
    # Rule 1 is about the git top level, one level above the Kailash/ master
    # folder every other gate resolves under (workflow_gate uses the same anchor).
    root = resolve_root(args.root)
    git_root = root if (root / ".github").is_dir() and (root / "RULES.md").is_file() else None
    if git_root is None:
        try:
            git_root = git_top_level(root)
        except Unavailable:
            git_root = root.parent

    report = Report()
    present = set(_root_entries(git_root))

    # Property 1: the master folder and the one root doc exist.
    for name in sorted(REQUIRED_ROOT):
        if name not in present:
            report.add(Finding(
                rule="missing-root-entry", path=name, observed="<absent>",
                expected=f"{name} at the repository root",
                message="Rule 1: the root holds RULES.md and the Kailash/ master folder"))

    # Property 2: nothing else at the root.
    for name in sorted(present - ALLOWED_ROOT):
        report.add(Finding(
            rule="loose-root-entry", path=name, observed=name,
            expected="only RULES.md, Kailash/, .github/, .gitignore at the root",
            message="Rule 1: no source file, document, config or asset lives at "
                    "the repository root — put it under Kailash/"))

    report.notes.append(f"{len(present)} tracked root entr(y/ies)")
    return report


def main(argv=None) -> int:
    parser = base_parser(
        "Assert Rule 1: only RULES.md + Kailash/ + plumbing at the repository root.")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
