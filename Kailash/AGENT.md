# AGENT.md — the single agent definition

This is the **one and only** agent-instruction file for the Kailash project.
Every AI assistant and coding agent (Claude Code, Copilot, Cursor, Codex,
Gemini, …) uses **this** file — there are no per-tool copies (`CLAUDE.md`,
`.cursorrules`, `.github/copilot-instructions.md` are git-ignored on purpose).
Edit this file; never fork it.

> **Read [`../RULES.md`](../RULES.md) first.** It is the project constitution
> and the mandatory first read before touching anything. This file is the
> working brief that sits under those rules.

## Where things live

The entire project is nested under the `Kailash/` master folder (see RULES.md).
The git repository root holds only `RULES.md`, `Kailash/`, and VCS/CI plumbing
(`.git/`, `.github/`, `.gitignore`). **Run every command from inside
`Kailash/`.**

## Commands (run from `Kailash/`)

```bash
make lint            # ruff check backend   (CI pins ruff==0.5.0)
make fmt             # ruff format backend
make test            # pytest -q tests/
make test-platform   # each of the 9 platform services, in its own dir
make up / make down  # docker compose up -d --build / down
```

There is **no root pytest config**; each suite has its own import root, so `cd`
and `PYTHONPATH` matter:

| Suite | How to run (from `Kailash/`) |
| --- | --- |
| Shared library — `tests/platform/` | `PYTHONPATH=. pytest -q tests/platform` |
| A platform service — `backend/services/<name>/` | `cd backend/services/<name> && pytest -q` (imports `from app.main`) |
| `company` service | `cd backend/services/company && PYTHONPATH=../../.. pytest -q` (needs **PostgreSQL**) |
| Deploy-safety gates — `tests/verify/` | `pip install -r requirements-dev.txt && PYTHONPATH=. pytest -q tests/verify -m "not docker and not network"` |

Frontend (Corepack-pinned Yarn — do **not** `npm install -g yarn` or regenerate
`frontend/yarn.lock` with npm):

```bash
corepack enable && corepack prepare yarn@1.22.22 --activate   # once
cd frontend && yarn install --frozen-lockfile && yarn build   # craco, not plain CRA
```

## Architecture

The backend is **two tiers sharing one library**:

1. **Main application** — `backend/app/`. A hand-wired FastAPI app
   (`backend/app/main.py`) with JWT auth + RBAC, MongoDB, a custom middleware
   stack, and ~20 routers under `backend/app/api/` mounted at `/api`. Themed as
   Hindu deities: `departments/` (deity "AI departments"), `guardians/` (GANESHA
   orchestrator, SHIV security/auto-rectify, PARVATI workload), `agents/prompts/`
   (per-product system prompts). This app does **not** use `build_app()`.

2. **Platform services** — `backend/services/<name>/` (document-ai, forecasting,
   anomaly, rag, vision-gateway, speech, model-registry, knowledge-graph,
   automobile-llm). Each is an independent FastAPI microservice following
   `main.py` → `routes.py` → `service.py` → `settings.py`, where `main.py` is one
   line: `app = build_app(settings, routers=[register])`.

Both depend on **`backend/shared/`** — read `backend/shared/app.py` first.
`build_app()` wires CORS, request-id middleware, `/health` `/` `/metrics`
`/docs`, and the `PlatformError` handler. Responses use `ApiResponse` /
`ErrorDetail` / `HealthResponse`; typed errors (`NotFoundError`,
`ValidationError`, `UpstreamError`) map to stable `code` strings.

**Auth differs by tier**: the main app uses JWT (`Authorization: Bearer`);
platform services guard mutating routes with `X-Platform-Token`
(`require_internal_token` vs `PLATFORM_INTERNAL_TOKEN`; no-op in dev).

The **`company`** service (`backend/services/company/`) is a PostgreSQL
double-entry statutory ledger (journal → GSTR-1/3B → Schedule III →
reconciliation); posted journals are immutable (corrections are reversals).

LLM/embedding provider order: `OPENROUTER_API_KEY` → `ANTHROPIC_API_KEY` →
keyword fallback, so services degrade rather than hard-fail without keys.

## Deploy-safety gates — `scripts/verify/`

Enforcement, not ordinary tooling: CI runs each as `python -m scripts.verify.<name>`
(config_drift, repo_state, secret_scan, workflow_gate, build_audit,
deployment_check). They exist because `deploy/host/deploy.sh` does
`git reset --hard` + `git clean -fd` on the production host.

Because the project is nested, the gates resolve their paths against the
**`Kailash/` master folder** (`common.project_root()`), while `.github/workflows/`
is resolved against the **git top level** (it cannot move — GitHub Actions reads
it from the repo root). `repo_state.py` keeps `normalise_remote()` byte-for-byte
in step with the bash `normalise_remote()` in `deploy/host/deploy.sh`
(property-tested) — change one, change the other. Committing a critical-path
file (`deploy/`, `docker-compose.yml`, workflows, `frontend/.firebaserc`,
`frontend/.env.production`) triggers the `commit_gate` pre-commit hook, which
refuses unless `CONFIRM_CRITICAL_PATH=1` is set.

When you touch `scripts/verify/`, the workflows, or `docker-compose.yml`, run
`tests/verify/` before assuming green.

## Conventions

- **Lint/format is ruff** (`ruff.toml`, line-length 100, py311, only over
  `backend/`). CI pins `ruff==0.5.0` — newer local ruff may report extra
  findings that CI does not.
- **Commits** follow Conventional Commits with a module scope, e.g.
  `feat(backend): ...`, `fix(frontend): ...`, `feat(agents/ganesha): ...`.
- Pre-commit also runs gitleaks and hygiene hooks; run it from `Kailash/`.
- Secrets live in environment variables / the deploy secret store — never in the
  repo.
