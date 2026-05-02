# Changelog

All notable changes to the Kailash project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Changed

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

[Unreleased]: https://github.com/flywithvvk/kailash/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/flywithvvk/kailash/releases/tag/v1.1.0
[1.0.0]: https://github.com/flywithvvk/kailash/commit/130ba14976709daa9b2523f1ca56e6456852ef78
