"""Assert RULES.md Rule 3: one BRD, one TRD, one PRD -- and no duplicates.

Rule 3 mandates a single business (BRD), technical (TRD) and product (PRD)
requirements document, each at a fixed path under docs/, with per-platform or
per-module requirements written as sections *inside* them rather than as
separate files. Written rules drift; this makes Rule 3 executable so a second
copy cannot reappear unnoticed (the way the former per-app
BRD_android_app_kailash_ai.md and its siblings had).

Two properties:

1. Each canonical document exists and is tracked, at its one path.
2. No other tracked file is named like a BRD/TRD/PRD. Identity here is the
   name: a file whose stem carries a `brd`/`trd`/`prd` token is a requirements
   document by declaration, and if it is not the one canonical path for its
   kind it is a duplicate. Word-delimited matching, so `business-requirements.md`
   and `dashboard.py` -- which are not *named* BRD/TRD/PRD -- never match.

Paths resolve against the Kailash/ master folder (common.project_root), so the
canonical set is stated relative to it.
"""
from __future__ import annotations

import re
from pathlib import PurePosixPath

from .common import (
    Finding,
    Report,
    base_parser,
    load_corpus,
    resolve_root,
    run,
)

# The one canonical path per kind, relative to the project (master) root.
CANONICAL = {
    "BRD": "docs/BRD.md",
    "TRD": "docs/TRD.md",
    "PRD": "docs/PRD.md",
}

_DELIMITER = re.compile(r"[^A-Za-z]+")


def _kind_of(stem: str) -> str | None:
    """The BRD/TRD/PRD kind a filename stem declares, or None.

    Exact, word-delimited token match rather than a substring search: `brd` as
    a substring lives inside no common English word, but matching on tokens is
    unmistakable and keeps `hybrid`, `cardboard` and the like from ever reading
    as a requirements document.
    """
    for token in _DELIMITER.split(stem):
        if token.lower() in ("brd", "trd", "prd"):
            return token.upper()
    return None


def build_report(args) -> Report:
    root = resolve_root(args.root)
    report = Report()
    corpus = load_corpus(root)
    tracked = set(corpus.files)

    # Property 1: each canonical document exists and is tracked.
    for kind, rel in CANONICAL.items():
        if rel not in tracked:
            report.add(Finding(
                rule="missing-canonical-doc", path=rel, observed="<absent>",
                expected=f"the single {kind} at {rel}",
                message=f"Rule 3 requires exactly one {kind}; it lives at this path"))

    # Property 2: no other tracked file is named like a BRD/TRD/PRD.
    canonical_paths = set(CANONICAL.values())
    for rel in corpus.files:
        if rel in canonical_paths:
            continue
        kind = _kind_of(PurePosixPath(rel).stem)
        if kind:
            report.add(Finding(
                rule="duplicate-doc", path=rel, observed=f"a {kind}-named file",
                expected=f"the single {kind} at {CANONICAL[kind]}",
                message="Rule 3: per-platform / per-module requirements are "
                        "sections inside the one document, not separate files"))
    return report


def main(argv=None) -> int:
    parser = base_parser(
        "Assert Rule 3: one BRD, one TRD, one PRD, and no duplicate copies.")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
