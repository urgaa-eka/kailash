# Changelog

All notable changes to the Kailash project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Security

- **Removed a self-healing super-admin backdoor.** `app/core/seeder.py` ran on
  every startup and created `KAILASH001` / `admin@kailash.ai` as `super_admin`
  with 2FA off, hashed from a literal in the source file. Its else-branch
  re-inserted the account whenever it was missing, so deleting it only lasted
  until the next boot. The password now comes from `ADMIN_SEED_PASSWORD` with no
  default, seeding happens only into a database with no users at all, and the
  recreate branch is gone. `database/seed_data.py` likewise requires
  `SEED_ADMIN_PASSWORD` and no longer prints credentials to stdout;
  `app/schemas/auth.py` no longer publishes them as OpenAPI examples at `/docs`.
- **Production startup rejects the published `SECRET_KEY`.** It fell back to
  `dev-secret-key-change-in-production`, which is in this repository and signs
  every JWT, so any account could be forged without a password. With
  `ENV=production`, `app/core/config.py` now refuses to start on that value or
  on `CORS_ORIGINS="*"` (TRD NFR-Sec4 / TR-2). `CORS_ORIGINS` also reads the
  environment, which it previously did not.
- **Compose credentials are required, not defaulted.** `POSTGRES_PASSWORD`,
  `REDIS_PASSWORD` and `PLATFORM_INTERNAL_TOKEN` use `${VAR:?...}` at all seven
  sites, so every compose subcommand aborts at parse time before a container
  exists. `PLATFORM_INTERNAL_TOKEN` previously defaulted to empty, which
  `require_internal_token` treats as matching a caller that sends no header.
  See `docs/DEPLOYMENT.md` section 0 — compose reads `/opt/kailash/.env`, never
  `backend/.env`.
- Existing exposure is **not** undone by these changes: the literals are already
  on `origin/main` and must be rotated.

### Added

- **Company segment — master operational ledger** (`company-segment/` +
  `backend/services/company/`), the full double-entry statutory
  system-of-record per `Company_Segment_Technical_Specification.md`:
  - PostgreSQL schema (v1.1 hardened): FY-partitioned immutable journal,
    DB-trigger-enforced Σdr=Σcr, maker-checker, no un-posting, frozen
    posted lines, append-only audit log, `source_hash` idempotency,
    GST-rate-split CHECK, composite document→journal FKs, DEFAULT
    partitions for historical FYs, fiscal-calendar populator.
  - 10th platform service on the shared `build_app()` factory: ingestion
    APIs (sales/purchase/bank per the JSON contracts), posting engine
    with gap-free per-GSTIN voucher series, correction-by-reversal,
    Tally opening-balance migration endpoint.
  - GST engine: GSTR-1 builder (B2B/B2CL/B2CS/EXP/SEZ + HSN summary +
    docs-issued, GSTN-shaped JSONB, effective-dated GST 2.0 rates,
    place-of-supply CGST/SGST vs IGST), GSTR-3B summary, ITC register.
  - Schedule III trial balance / P&L / Balance Sheet views with an
    accounting-equation probe; versioned financial-statement snapshots.
  - Reconciliation engine: the 10 CA-vs-internal control points with
    tolerance-banded severity and a resolution workflow.
  - Compliance calendar API (GST/TDS/IT/ROC due dates with status) and a
    self-contained L4 HTML FY dashboard.
  - 32 tests including adversarial raw-SQL attacks proving each ledger
    invariant is enforced by the database; dedicated CI job with a
    `postgres:16` service container.
  - `docker-compose.override.yml` publishing Postgres on loopback for
    local development.
  - Compose profile **`kailash-ai`** — the full stack end-to-end with one
    command (`docker compose --profile kailash-ai up -d --build`): core
    backend + MongoDB/Postgres/Redis (always-on, prod-unchanged) plus
    profile-gated services: the React frontend on nginx (:3000, `/api`
    proxied to backend, same-origin build via new `REACT_APP_BACKEND_URL`
    build arg), the Company ledger (:8110), and all 9 platform/ML services
    (:8101-:8109) built from a new generic
    `backend/services/Dockerfile.service` (the per-service Dockerfiles
    referenced pre-consolidation paths and could not build). Postgres
    fresh-volume init enables `pgcrypto`/`uuid-ossp`
    (`database/postgres_init.sql`); Mongo fresh-volume init runs
    `database/mongodb_init.js`; model-registry gets a persistent volume.
    Root `Dockerfile` no longer fails on the private
    `emergentintegrations` package (installed best-effort from the Emergent
    index after the rest of `requirements.txt`); frontend build is
    lockfile-strict and builds same-origin via a new
    `REACT_APP_BACKEND_URL` build arg. `backend/.env` made optional in
    compose.

### Fixed

- **No `.dockerignore` existed**, so every image build shipped the entire
  working tree — virtualenvs, all `node_modules`, `.git`, CDK output — to
  the builder. Measured on the backend build: 572 MB of context still
  climbing after 7 minutes, versus **667 KB in 4.8 s** once ignored.
  Painful locally, far worse against a remote/cloud builder. Added a
  root `.dockerignore` (keeps `company-segment/` schema + seed CSVs, which
  the ledger service reads at runtime).
- **Backend container ran the app under the wrong module path.** The
  `Dockerfile` served `backend.app.main:app` from `/app`, but 20 modules
  across 7 files use absolute `from app.…` imports (there are zero
  `from backend.…` imports and 156 relative ones), so startup died with
  `ModuleNotFoundError: No module named 'app'`. Now runs `app.main:app`
  with `WORKDIR /app/backend`, matching `backend/server.py`.
- **Mongo healthcheck was too tight for a loaded host** — `mongosh` boots
  a Node runtime and exceeded the 10 s timeout, marking a perfectly
  healthy Mongo unhealthy and blocking dependents. Now 20 s with a 60 s
  start period.
- **Backend container could never start.** `app/middleware/error_handler.py`
  creates `/var/log/kailash` at import time, but the root `Dockerfile`
  switches to the non-root `appuser` without creating that directory —
  every run died with `PermissionError: [Errno 13] ... '/var/log/kailash'`.
  The Dockerfile now creates and chowns the log directory before dropping
  privileges, and `error_handler.py` no longer raises when the directory is
  not writable — it falls back to stdout-only logging. The `mkdir` runs at
  import, so raising there made the app unimportable on any CI runner or
  non-root process outside the container; `KAILASH_LOG_DIR` overrides the
  location.
- **`deploy.sh` and `setup-vps.sh` pointed at the wrong repository**
  (`flywithvvk/kailash`, not `urgaa-eka/kailash`), so the VPS deploy fetched and
  hard-reset against a repo that is not this one. `README.md`'s CI badge had the
  same URL.
- **`.firebaserc` named a different Firebase project** (`kailash-15365`) than
  `deploy-frontend.yml` deploys to (`kailash-38268`).
- **Import casing broke case-sensitive builds.** Eight components under
  `src/components/UI/` imported from `@/components/ui/…`; `components.json`'s
  `ui` alias was the source. Fine on Windows, unresolvable in the Linux image.
- **BRAHMA and VARUNA had the wrong system prompts.** Both files defined
  `get_system_prompt` and `process_task` twice; the second definition wins, so
  BRAHMA identified as "the Architecture Department" and VARUNA as "the Data
  Department" — truncated leftovers of the same redaction damage that corrupted
  the seed scripts. Duplicates removed.

### Changed

- **Deploys are gated on CI.** `ci.yml` gained a `workflow_call` trigger and both
  deploy workflows gained a `ci-gate` job, so nothing reaches Firebase or the VPS
  until CI passes. Previously they were independent triggers on the same push.
- **Un-masked the jobs that could not fail**: removed `|| true` from the backend
  smoke step, `yarn build` and the deploy test step, and the `|| yarn install`
  fallback that resolved lockfile drift into a different dependency set than the
  one deployed. CI's frontend Node moved 18 → 20 to match `frontend/Dockerfile`
  and the deploy workflow; on 18 the install could not succeed at all.
- Both workflows now import the app and run `backend/tests` instead of
  `tests/backend`, which collects one test against a decommissioned host and
  passes without asserting anything.
- **`ruff check backend` passes.** 2745 findings cleared, including 129 syntax
  errors confined to four unrecoverable test files that imported a
  `backend/agents/` package which does not exist; those were removed.

- **Redis now requires authentication** (`--requirepass ${REDIS_PASSWORD}`,
  which has no default — see the Security section below). The backend's
  `REDIS_URL` and the container healthcheck carry the credential; Celery
  picks it up from `REDIS_URL` unchanged. Previously the cache/broker was
  reachable without auth by anything on the compose network.
  - **AWS backend for the Company segment** (`infra/company/` —
    `KailashCompanyStack`, CDK TypeScript, 94 resources, synth-verified in
    CI): Aurora Serverless v2 (PostgreSQL 16, KMS, PITR, deletion-protected)
    behind RDS Proxy in private subnets; REST API Gateway + WAFv2 fronting
    the full FastAPI surface on Lambda via Mangum; SQS-buffered ingestion
    worker with DLQ; DynamoDB idempotency fast-path + S3 FY-partitioned
    document vault (both env-gated no-ops locally); Step Functions
    period-end close (lock → GSTR-1 → 3B → statements → recon → publish
    facts) and Tally-migration state machines; EventBridge
    `kailash-center-lake` bus with typed events (`JournalPosted`,
    `ReturnGenerated`, `ReconciliationCompleted`,
    `FinancialFactsPublished`, `ComplianceDue`); daily compliance-calendar
    sweep (09:00 IST); Secrets Manager for DB + GSTN credentials;
    ap-south-1 default. Step handlers are covered by local tests
    (`test_z_close_flow.py`) running the same code as Lambda — 37 tests
    total.
  - AWS deployment architecture for the segment
    (`Company_Segment_Backend_Architecture_AWS.md` +
    `company-segment/docs/aws/` with rendered architecture/dataflow
    diagrams and Mermaid sources): Aurora Serverless v2 for the `company`
    schema, Lambda engines, Step Functions period-end close, EventBridge
    as the Center Lake backbone, GSTN/IRP integration, KMS/Secrets
    Manager/WAF hardening, CDK `KailashCompanyStack`.

- **Monorepo consolidation** — merged three layers into a single unified
  structure:
  - `apps/backend/` + `services/` + `platform/` → `backend/`
  - `apps/frontend/` → `frontend/` at repo root
  - 9 platform services now live as internal modules under
    `backend/services/`
  - Shared library moved to `backend/shared/` (was `platform/kailash_shared/`)
  - Gateway eliminated — single backend serves all consumers directly
  - Single `Dockerfile` at root, single `docker-compose.yml`
  - All Python imports updated (`kailash_shared` → `backend.shared`)
- **Branding** — all AEGIS references (~650 occurrences across ~70 files)
  replaced with Kailash branding:
  - Database name: `kailash_aegis` → `kailash`
  - Field name: `aegis_code` → `kailash_code`
  - UI text, cookies, localStorage keys, CSS classes, video filenames,
    email domains updated
- **Documentation** — README, ARCHITECTURE, CONTRIBUTING, and CHANGELOG
  rewritten for the consolidated structure
- **CI/CD** — all workflows updated for new paths; deploy scripts use
  root `docker-compose.yml`
- **Makefile** — simplified for unified backend (removed multi-service
  orchestration targets)

### Removed

- `apps/` directory (merged into `backend/` and `frontend/`)
- `services/` directory (merged into `backend/services/`)
- `platform/` directory (merged into `backend/shared/`; gateway eliminated)
- `deploy/docker/docker-compose.platform.yml` (replaced by root compose)

---

## [1.1.0] - 2026-01-18

### Added

- **`backend/shared`** — shared library (`__init__`, `schemas`, `auth`,
  `config`, `logging`, `errors`, `app`) exposing `build_app()` with CORS,
  request-id middleware, `/health`, `/`, `/metrics`, and typed
  `PlatformError` mapping.
- **Real implementations** for every platform AI service (replacing the
  previous 501 stubs):
  - `document-ai` — PDF text extraction via `pypdf`, field-validation
    profiles (RC book, invoice, certificate, ID proof).
  - `forecasting` — EMA + trend + seasonal baseline, numpy-only.
  - `anomaly` — scikit-learn `IsolationForest`.
  - `rag` — OpenRouter embeddings + in-memory cosine store, with a
    chained SHA-256 hash-embedding fallback for offline mode.
  - `vision-gateway` — tier-based router (`fast` / `balanced` / `long`)
    over OpenRouter with per-tier model selection.
  - `speech` — provider-agnostic ASR + TTS interface with Indic locales.
  - `model-registry` — SQLite-backed MLflow-shape registry for models,
    versions and evaluations.
  - `knowledge-graph` — in-memory typed graph with BFS neighbour lookup.
  - `automobile-llm` — OpenRouter chat bound to an automobile-domain
    system prompt (the moat service).
- **Test coverage** — `tests/platform/test_shared.py` (5 tests) plus
  per-service route tests (53 tests total); all green.
- **Dev tooling** — top-level `Makefile`, `ruff.toml`, and
  `.pre-commit-config.yaml`.
- **CI matrix** — `.github/workflows/ci.yml` with six jobs: `lint`,
  `shared`, `services` (9-way matrix), `backend`, `frontend`,
  `compose-build`.
- **`SECURITY.md`** — secret-handling playbook and vulnerability
  reporting process.
- Professional top-level `README.md` and `ARCHITECTURE.md` with Mermaid
  diagrams, service catalog, and contract documentation.

### Fixed

- `shared/logging.py` — replaced `logging.setLogRecordFactory` (which
  clobbers the `service` attribute across multiple apps in the same
  process) with an idempotent `logging.Filter`.
- `services/rag/app/service.py` — replaced single `blake2b(digest_size=768)`
  (which fails: max digest is 64) with chained SHA-256 to produce the
  768-byte hash-embedding fallback.
- `services/document-ai/requirements.txt` — added `python-multipart`
  (required by FastAPI `UploadFile`).
- All service `pytest.ini` — dropped unknown `asyncio_mode=auto`
  directive that broke test discovery without `pytest-asyncio`.

---

## [1.0.0] - 2025-12-19

### Initial Release

Complete initialization of the Kailash project.

#### Backend (154 Python files)

- **FastAPI Application** — 20+ API endpoints for authentication,
  departments, tasks, analytics
- **24 AI Departments** themed after Hindu deities (Vishwakarma, Lakshmi,
  Surya, Brahma, Saraswati, Hanuman, and 18 more)
- **3 Guardian Agents**: GANESHA (AI orchestrator), SHIV (security),
  PARVATI (workload)
- JWT-based authentication with RBAC, rate limiting, 3-factor auth
- MongoDB (Motor async), PostgreSQL (asyncpg), Redis
- **Core Services**: RAG knowledge base, GANESHA orchestrator (v1/v2),
  live API connector, email service, task scheduler
- **Security**: bcrypt hashing, JWT tokens, input sanitization, CORS/HSTS/CSP
  headers, XSS/CSRF protection

#### Frontend (187 JS/JSX files)

- React 19 with React Router v6, Tailwind CSS, Lucide Icons
- Authentication (3-factor), protected routes, session management
- Executive dashboard with KPI metrics, department cards, activity feed
- Department management (24 specialized components)
- GANESHA chat interface, orchestrator dashboard
- Task management with filtering, creation, status tracking
- Knowledge base UI with RAG query interface

#### Statistics

- **Total Files:** 679 · **Total Lines:** 166,274
- **Python Files:** 154 · **JavaScript Files:** 187 · **Markdown Files:** 156
- **Backend API Endpoints:** 20+ · **React Components:** 100+
- **AI Departments:** 24 · **Guardian Agents:** 3

#### Known Issues (from initial release)

- MongoDB Atlas permissions may require manual configuration
- Some frontend visualizations need production data
- Real-time WebSocket features need extensive testing
- Mobile responsiveness needs enhancement

### Contributors

- Kailash AI Team
- Go4Garage Development Team

---

**Made with dedication for India's EV Revolution**

[Unreleased]: https://github.com/urgaa-eka/kailash/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/urgaa-eka/kailash/releases/tag/v1.1.0
[1.0.0]: https://github.com/urgaa-eka/kailash/commit/130ba14976709daa9b2523f1ca56e6456852ef78
