"""Assert RULES.md Rule 2: department→feature, mirrored, nothing loose.

Rule 2 organises each department (`frontend/`, `backend/`) as a `platform/`
shared layer plus one folder per feature under `features/`, with the same
feature appearing under both departments. This makes that executable:

1. **Locked feature set.** Every folder under `frontend/src/features/` and
   `backend/features/` must be in the canonical feature registry below. A new
   ad-hoc feature folder fails CI until it is added to the registry
   deliberately -- that deliberate edit *is* the lock. The frontend names the
   feature in kebab-case (`eka-brain`); Python packages cannot contain hyphens,
   so the backend mirrors it in snake_case (`eka_brain`); the two are the same
   feature.

2. **Nothing loose.** Source lives under `features/`, `platform/` or (backend)
   `services/` -- never loose at `frontend/src/`, `backend/` or inside
   `features/` itself, apart from a small, named set of entry points and
   support files.

3. **Mirror.** Every feature the registry marks as spanning both departments
   has a folder on both sides; a set-difference names any that drifted.

`root_singletons` locks Rule 1, `doc_singletons` Rule 3, `workflow_singletons`
Rule 5; this locks Rule 2. Read from `git ls-files` (tracked, so an untracked
scratch file is not a failure but a committed stray one is).
"""
from __future__ import annotations

from .common import (
    Finding,
    Report,
    base_parser,
    resolve_root,
    run,
    tracked_files,
)

# ---------------------------------------------------------------------------
# The canonical feature registry (RULES.md Rule 2). Kebab-case, as the frontend
# names them. A feature is added here by a reviewed change, never ad hoc.
# ---------------------------------------------------------------------------
CANONICAL_FEATURES = frozenset({
    # intelligence & telemetry
    "eka-brain", "guardians", "analytics", "kailash-command",
    # the six products (+ company financials)
    "gst-saas", "ignition", "urja", "company",
    # platform features
    "auth", "users", "departments", "knowledge-base", "legal",
    "executive-dashboard", "management", "reports", "settings",
    "tasks", "tattoos", "automobile-pricing",
})

# Features that also have a backend implementation under `backend/features/`.
# (`company`'s backend is a container service under `backend/services/company/`,
# not a `backend/features/` package, so it is deliberately NOT here.)
BACKEND_FEATURES = frozenset({
    "analytics", "auth", "automobile-pricing", "departments", "eka-brain",
    "executive-dashboard", "guardians", "knowledge-base", "management",
    "tasks", "users",
})

# The only non-feature entries allowed directly under each location.
FRONTEND_SRC_ALLOWED = frozenset({
    "features", "platform",
    # Create-React-App entry points / standard root files.
    "App.js", "App.css", "index.js", "index.css",
    "setupTests.js", "reportWebVitals.js", "react-app-env.d.ts",
    "logo.svg", "service-worker.js", "serviceWorkerRegistration.js",
})
BACKEND_TOP_ALLOWED = frozenset({
    "features", "platform", "services",
    "tests", "knowledge",                       # test suite + knowledge corpus
    "main.py", "__init__.py", "server.py", "conftest.py",
    "requirements.txt", ".env.example",
})


def _kebab(name: str) -> str:
    return name.replace("_", "-")


def _snake(name: str) -> str:
    return name.replace("-", "_")


def _children(files: list[str], prefix: str) -> set[str]:
    """First path segment under `prefix/` across tracked files (files + dirs)."""
    pre = prefix + "/"
    return {f[len(pre):].split("/", 1)[0] for f in files if f.startswith(pre)}


def _dir_children(files: list[str], prefix: str) -> set[str]:
    """First path segment under `prefix/` that is itself a directory."""
    pre = prefix + "/"
    out: set[str] = set()
    for f in files:
        if f.startswith(pre):
            rest = f[len(pre):]
            if "/" in rest:
                out.add(rest.split("/", 1)[0])
    return out


def build_report(args) -> Report:
    root = resolve_root(args.root)
    files = tracked_files(root)
    report = Report()

    fe_feats = _dir_children(files, "frontend/src/features")
    be_feats_snake = _dir_children(files, "backend/features")
    be_feats = {_kebab(d) for d in be_feats_snake}

    # --- 1. locked feature set --------------------------------------------
    for f in sorted(_children(files, "frontend/src/features") - CANONICAL_FEATURES):
        report.add(Finding(
            rule="unregistered-feature", path=f"frontend/src/features/{f}",
            observed=f, expected="a feature in the RULES.md Rule 2 registry",
            message="Rule 2: add the feature to CANONICAL_FEATURES in "
                    "structure_gate.py deliberately, or it is loose source"))
    allowed_be = {_snake(f) for f in BACKEND_FEATURES} | {"__init__.py"}
    for d in sorted(_children(files, "backend/features") - allowed_be):
        report.add(Finding(
            rule="unregistered-feature", path=f"backend/features/{d}",
            observed=d, expected="a backend feature in the Rule 2 registry",
            message="Rule 2: add it to BACKEND_FEATURES (snake-case mirror of a "
                    "canonical feature), or it is loose source"))

    # --- 2. nothing loose --------------------------------------------------
    for name in sorted(_children(files, "frontend/src") - FRONTEND_SRC_ALLOWED):
        report.add(Finding(
            rule="loose-frontend-source", path=f"frontend/src/{name}",
            observed=name, expected="features/, platform/, or a named entry point",
            message="Rule 2: frontend source lives under features/ or platform/"))
    for name in sorted(_children(files, "backend") - BACKEND_TOP_ALLOWED):
        report.add(Finding(
            rule="loose-backend-source", path=f"backend/{name}",
            observed=name, expected="features/, platform/, services/, or a named support file",
            message="Rule 2: backend source lives under features/, platform/ or services/"))

    # --- 3. mirror ---------------------------------------------------------
    # The registry is not stale: every canonical feature has a frontend folder.
    for feat in sorted(CANONICAL_FEATURES - fe_feats):
        report.add(Finding(
            rule="missing-feature-folder", path=f"frontend/src/features/{feat}",
            observed="<absent>", expected=f"{feat} folder (it is in the registry)",
            message="Rule 2: a registered feature has no frontend folder -- "
                    "remove it from CANONICAL_FEATURES or add the folder"))
    # Every feature marked backend-present exists under backend/features/.
    for feat in sorted(BACKEND_FEATURES - be_feats):
        report.add(Finding(
            rule="mirror-drift", path=f"backend/features/{_snake(feat)}",
            observed="<absent>", expected=f"{_snake(feat)} (mirrors frontend/src/features/{feat})",
            message="Rule 2: feature present on the frontend is missing its "
                    "backend mirror -- add it or drop it from BACKEND_FEATURES"))

    report.notes.append(
        f"{len(fe_feats)} frontend feature(s), {len(be_feats)} backend feature(s), "
        f"{len(CANONICAL_FEATURES)} registered")
    return report


def main(argv=None) -> int:
    parser = base_parser(
        "Assert Rule 2: department→feature, mirrored, no loose source.")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
