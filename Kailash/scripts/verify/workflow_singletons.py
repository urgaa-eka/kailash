"""Assert RULES.md Rule 5's membership clause: one pipeline, no stray workflows.

Rule 5 mandates a single gated deploy pipeline -- a CI gate (`ci.yml`) that both
deploy entrypoints call -- and states there are *no auxiliary or one-off
workflows*: "a new deploy need is a change to the one pipeline, never a new
workflow file."

`workflow_gate.py` enforces the pipeline's *topology* (every deploy is gated,
staged and verified) over whatever workflow files exist. It never asserts *which*
files may exist, so a one-off workflow that carries no deploy marker -- a
`rollback-hosting.yml`, say -- passes it untouched. This check closes that gap by
enforcing *membership*: the set of workflow files is exactly the canonical
pipeline, so a stray workflow cannot reappear unnoticed. It is to Rule 5 what
`doc_singletons.py` is to Rule 3.

Two properties:

1. Each canonical pipeline workflow exists.
2. No other `*.yml`/`*.yaml` workflow file is present.

`.github/workflows/` is read from the git top level -- the parent of the
`Kailash/` master folder every other project path resolves under -- because
GitHub Actions only runs workflows from there (RULES.md Rule 1's exception). The
same anchoring `workflow_gate.build_report` uses; a flat checkout keeps both at
one directory.
"""
from __future__ import annotations

from .common import (
    Finding,
    Report,
    Unavailable,
    base_parser,
    resolve_root,
    run,
)

# The one gated pipeline (RULES.md Rule 5): a single CI gate both deploy
# entrypoints call. These are the only workflow files allowed to exist. A
# genuine new pipeline need is a reviewed change to this set, exactly as a new
# canonical document is a reviewed change to doc_singletons.CANONICAL.
CANONICAL_WORKFLOWS = frozenset({
    "ci.yml",
    "deploy-backend.yml",
    "deploy-frontend.yml",
})


def build_report(args) -> Report:
    root = resolve_root(args.root)
    # GitHub reads `.github/workflows/` from the git top level, which is the
    # parent of the `Kailash/` master folder every other path resolves under
    # (RULES.md Rule 1). A flat checkout -- the synthetic test repos -- keeps
    # both at one directory, so the presence of the directory picks the anchor.
    wf_root = root if (root / ".github" / "workflows").is_dir() else root.parent
    wf_dir = wf_root / ".github" / "workflows"
    if not wf_dir.is_dir():
        raise Unavailable(f"{wf_dir} does not exist")

    report = Report()
    present = {p.name for p in wf_dir.glob("*.yml")}
    present |= {p.name for p in wf_dir.glob("*.yaml")}

    # Property 1: each canonical pipeline workflow exists.
    for name in sorted(CANONICAL_WORKFLOWS):
        if name not in present:
            report.add(Finding(
                rule="missing-pipeline-workflow",
                path=f".github/workflows/{name}", observed="<absent>",
                expected=f"the canonical {name}",
                message="Rule 5: the one pipeline is ci.yml plus the two "
                        "deploy entrypoints"))

    # Property 2: no auxiliary / one-off workflow files.
    for name in sorted(present - CANONICAL_WORKFLOWS):
        report.add(Finding(
            rule="auxiliary-workflow",
            path=f".github/workflows/{name}", observed=name,
            expected="only the one gated pipeline "
                     "(ci.yml + the two deploy entrypoints)",
            message="Rule 5: a new deploy need is a change to the one "
                    "pipeline, never a new workflow file"))

    report.notes.append(f"{len(present)} workflow file(s) present")
    return report


def main(argv=None) -> int:
    parser = base_parser(
        "Assert Rule 5: exactly the one gated pipeline, no auxiliary workflows.")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
