# RULES — the Kailash project constitution

**Read this file before you touch anything.** It is the first mandate for
every person and every agent working on this repository. Nothing gets designed,
written, moved, or deployed until you have read and understood these rules.

They are few, deliberate, and enforced. Where a rule says *single*, it means
exactly one — no second copy, no per-tool fork, no "temporary" duplicate.

---

## Rule 0 — Read the rules, then enter the project

The order is fixed: **rules first, project second.** Whoever starts work — a new
contributor, an AI agent, a reviewer — reads this file first. The agent brief in
[`Kailash/AGENT.md`](./Kailash/AGENT.md) sits *under* these rules and points back
to them.

## Rule 1 — One master folder; nothing loose at the root

The entire project lives inside a **single master folder named after the
project: [`Kailash/`](./Kailash/)**. The repository root contains only this
file and that folder — plus the unavoidable VCS/CI plumbing that platforms
require to sit at the git root and nothing else:

```
<repo root>
├── RULES.md          ← this file (the only document allowed at the root)
├── Kailash/          ← the master folder: the whole project lives here
├── .github/          ← GitHub Actions + issue templates (GitHub reads these
│                       from the repo root — they physically cannot move)
├── .gitignore        ← minimal; the real ignore file is Kailash/.gitignore
└── .git/
```

**No source file, document, config, or asset is ever added at the repository
root.** If you are about to create a file at the root, you are breaking this
rule — put it under `Kailash/` instead. On GitHub, the root must show only
`RULES.md` and `Kailash/` as content.

> **Why `.github/` is the one exception:** GitHub Actions only runs workflows
> found at `.github/workflows/` at the repository root. It cannot be nested. The
> deploy-safety gates know this: they resolve every project path against the
> `Kailash/` master folder and resolve `.github/` against the git root
> (`scripts/verify/common.py::project_root`).

## Rule 2 — Departments, then features (department-first, mirrored)

Inside `Kailash/`, the top level is **departments** — the disciplines the
software is built from:

```
Kailash/
├── frontend/     ← department
├── backend/      ← department
├── …             ← other departments (AI, mobile apps, extension, …) as they exist
```

Inside each department, work is organised by **feature**. Every feature is a
folder, and the same feature appears as a matching folder under each department
that implements it — the frontend of a feature lives under `frontend/<feature>/`
and its server side under `backend/<feature>/`:

```
Kailash/
├── frontend/
│   ├── <feature-a>/      ← that feature's UI
│   └── <feature-b>/
└── backend/
    ├── <feature-a>/      ← that feature's API / server code
    └── <feature-b>/
```

**Every new feature is built this way**: create the feature folder under each
department it touches, and keep the names identical across departments so a
feature's frontend and server halves line up one-to-one.

### Concrete realization (the canonical, to-be-locked shape)

The toolchain fixes where features physically sit:

```
Kailash/
├── frontend/            ← department
│   └── src/
│       ├── platform/    ← shared, non-feature code: ui/ (design system), layout/,
│       │                  stores/, hooks/, lib/ (api client, firebase), utils, styles, data/
│       └── features/    ← one folder per feature (CRA requires src/; import via the `@` alias)
└── backend/             ← department
    ├── platform/        ← shared library (build_app factory) + core infra (config/db/rbac/firebase)
    ├── features/        ← one folder per feature, names MIRRORED with frontend/src/features/
    └── services/        ← the platform microservices (each an independently-built container)
```

**Canonical feature set** (vision naming; the locked list). Intelligence &
telemetry: `eka-brain` (the AI orchestrator/mind), `shiv`, `parvati`,
`analytics`, `kailash-command`. Data-core segment with software: `company`
(financials). Products: `eka-ai`, `website`, `urja`, `ev-vidya`, `gst-saas`,
`ignition`. Platform features: `auth`, `users`, `departments`, `knowledge-base`,
`legal`. Legacy names map in: `eka-brain ← ganesha`, `gst-saas ← gst/GSTSAAS`,
`urja ← urjaa/URGAA`, `company ← go4garage`. A new feature is added to this set
deliberately (a reviewed change), never created ad hoc.

**Naming across departments.** The frontend uses kebab-case folders
(`eka-brain`, `automobile-pricing`, `knowledge-base`); Python packages cannot
contain hyphens, so the backend mirrors those same features in snake_case
(`eka_brain`, `automobile_pricing`, `knowledge_base`). They are the same
feature — the mirror check treats the kebab- and snake-case of one name as equal.

> **Migration status:** both departments have been relocated into the shape
> above. The frontend lives in `frontend/src/features/` + `frontend/src/platform/`;
> the backend lives in `backend/features/` + `backend/platform/`, with the
> independently-built microservices under `backend/services/`. Each move was made
> CI-green — imports converted to the `@/features/…` alias (frontend) or the
> `backend.…` namespace (backend, so `backend/platform/` cannot shadow the stdlib
> `platform` module), and the coupled Docker/CI/verify references updated in the
> same change. New work follows the department→feature rule directly.

This rule is **enforced**: `scripts/verify/structure_gate.py` fails CI on a
feature folder outside the canonical registry (adding one is a deliberate edit
to that registry — the lock), on source loose at `frontend/src/`, `backend/` or
inside `features/`, and on a frontend↔backend mirror that drifted.

## Rule 3 — One BRD, one TRD, one PRD

The project has exactly **one** of each, and they live in
[`Kailash/docs/`](./Kailash/docs/):

- [`docs/BRD.md`](./Kailash/docs/BRD.md) — business requirements
- [`docs/TRD.md`](./Kailash/docs/TRD.md) — technical requirements
- [`docs/PRD.md`](./Kailash/docs/PRD.md) — product requirements

Per-platform or per-module requirements are **sections inside** these files, not
separate documents. Do not create `BRD_<anything>.md`, a per-app spec, or a
duplicate under another folder. Edit the single document.

This rule is **enforced**: `scripts/verify/doc_singletons.py` fails CI if a
canonical document is missing or if any tracked file is named like a BRD/TRD/PRD
anywhere else in the tree.

## Rule 4 — One agent copy

There is a **single agent definition**, [`Kailash/AGENT.md`](./Kailash/AGENT.md),
no matter how many AI tools or agents work on the project. Per-tool instruction
files (`CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, …) are
git-ignored on purpose so no second copy can drift. **All agent edits happen in
`AGENT.md`.**

## Rule 5 — One deployment pipeline, neat and clean

Deployment flows through **one gated pipeline**. Every deploy passes through the
same CI gate, then staging, then production, with automated verification at each
step — no side doors, no ungated path to production. The pipeline is enforced,
not merely documented: `scripts/verify/workflow_gate.py` asserts by graph
reachability that every production deploy is preceded by its staging deploy and
its verification, that the CI gate is upstream of every deploy, and that no gate
can be silently defeated.

The pipeline lives in `.github/workflows/` (it must, per Rule 1's exception):
a single CI gate (`ci.yml`) that both deploy entrypoints call, driving
`push → CI → staging → verify → production → verify`. There are no auxiliary or
one-off workflows. Keep it that way: a new deploy need is a change to the one
pipeline, never a new workflow file.

This rule is **enforced** on two axes: `scripts/verify/workflow_singletons.py`
fails CI if `.github/workflows/` holds any file beyond `ci.yml` and the two
deploy entrypoints (the *membership* clause), and `scripts/verify/workflow_gate.py`
asserts the *topology* — that every production deploy is preceded by its staging
deploy and verification, that the CI gate is upstream of every deploy, and that
no gate can be silently defeated.

## Rule 6 — Enforcement

These rules are checked, not trusted:

- **`scripts/verify/`** gates run in CI (`config_drift`, `repo_state`,
  `secret_scan`, `root_singletons`, `structure_gate`, `workflow_gate`,
  `workflow_singletons`, `build_audit`, `doc_singletons`) and resolve their paths
  against the `Kailash/` master folder (except the root-level ones, which resolve
  against the git top level). Each rule that can be checked is checked —
  `root_singletons` enforces Rule 1, `structure_gate` enforces Rule 2,
  `doc_singletons` enforces Rule 3, and `workflow_singletons` + `workflow_gate`
  together enforce Rule 5.
- **`repo_state`** refuses to deploy from a working tree with uncommitted
  changes under a deployment-critical path, because `deploy/host/deploy.sh`
  runs `git reset --hard` + `git clean -fd` on the production host.
- A **pre-commit hook** blocks commits that touch a critical path unless
  `CONFIRM_CRITICAL_PATH=1` is set.
- Secrets never live in the repository — they come from environment variables
  and the deploy secret store.

---

*Everything else — commands, architecture, conventions — is in
[`Kailash/AGENT.md`](./Kailash/AGENT.md) and [`Kailash/README.md`](./Kailash/README.md).
Start there, after this.*
