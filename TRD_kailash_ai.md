# Technical Requirements Document — Kailash-Ai

## 1. Document Control

| Field | Value |
|---|---|
| **Document title** | Technical Requirements Document — Kailash-Ai (Kailash AI Platform) |
| **Product** | Kailash — Go4Garage internal ML/AI platform |
| **Document type** | TRD (Product level) |
| **Version** | 1.0 |
| **Date** | 2026-07-31 |
| **Status** | Draft |
| **Owner** | TBD |
| **Author** | Go4Garage Documentation Workstream |
| **Reviewers** | TBD (Platform Engineering, Security, SRE) |
| **Approvers** | TBD |
| **Classification** | Internal — Proprietary (see `LICENSE`) |
| **Companion BRD** | `BRD_kailash_ai.md` |
| **Source of truth** | Local working copy at `C:\Go4Garage( Eka)\Kailash-Ai`, HEAD commit `40cca17` dated 2026-07-31 |

### 1.1 Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-31 | Documentation Workstream | Initial draft, derived from on-disk source, configuration, Compose files and deploy scripts |

---

## 2. System / Architecture Overview

### 2.1 Shape of the system

Kailash is a **modular monolith with independently testable capability modules**. A single FastAPI application (`backend/app/main.py`) hosts the operational API, the department-agent layer and the guardian layer. Alongside it, nine "platform service" modules under `backend/services/` are each built from a shared `build_app()` factory in `backend/shared/app.py`, which means each can be run and tested as an isolated FastAPI app while still being deployable inside one process today. A React 19 single-page application in `frontend/` is the human surface. MongoDB is the primary datastore, with PostgreSQL and Redis in supporting roles.

Three architectural decisions define the platform:

1. **One shared library, one contract.** `backend/shared/` provides `build_app()`, `BaseServiceSettings`, `require_internal_token`, `ApiResponse`/`ErrorDetail`/`HealthResponse` envelopes, a `PlatformError` hierarchy, and structured JSON logging. Every module built through it automatically exposes `/health`, `/`, `/metrics` and `/docs`, and returns identical error shapes.
2. **Agents as first-class modules.** Domain behaviour is decomposed into 20 registered department classes and 3 guardian agents rather than into anonymous service functions, so capability, knowledge slice and ownership align.
3. **Provider abstraction at the edge.** All upstream model access flows through Kailash with a defined precedence chain, so no consumer product ever holds a model vendor credential.

### 2.2 Component diagram

```
                    ┌──────────────────────────────────────────────────────────┐
                    │            CONSUMER PRODUCTS (internal)                  │
                    │  URGAA · GSTSAAS · Ignition · ARJUN (ev-vidya-arjun)     │
                    │  each configured with KAILASH_AI_URL + X-Platform-Token  │
                    └───────────────────────────┬──────────────────────────────┘
                                                │ HTTPS (REST, ApiResponse envelope)
                                                │
  ┌──────────────────────────────┐              │
  │  KAILASH FRONTEND            │              │
  │  React 19 SPA (CRA + CRACO)  │  HTTPS       │
  │  Firebase Hosting            │──────────────┤
  │  project: kailash-38268      │  Bearer JWT  │
  └──────────────────────────────┘              │
                                                ▼
                    ┌──────────────────────────────────────────────────────────┐
                    │        NGINX REVERSE PROXY (api.kailash-ai.in)           │
                    │  TLS 1.2/1.3 (Let's Encrypt) · security headers          │
                    │  rate limit: api 30 r/s · auth 5 r/s · upstream keepalive │
                    └───────────────────────────┬──────────────────────────────┘
                                                │ proxy_pass → 127.0.0.1:8000
                                                ▼
  ┌───────────────────────────────────────────────────────────────────────────────────┐
  │                    KAILASH BACKEND — FastAPI (Python 3.11)                        │
  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │
  │  │ MIDDLEWARE   security headers · error handler · CORS · request-id · metrics  │  │
  │  └─────────────────────────────────────────────────────────────────────────────┘  │
  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │
  │  │ API LAYER  backend/app/api/  (~24 routers)                                  │  │
  │  │ auth · users · rbac · departments · department_intelligence · tasks ·       │  │
  │  │ gaps_tasks_crud · analytics · dashboard · conversations · knowledge ·       │  │
  │  │ knowledge_base · live_data · guardians · ganesha · ganesha_multimodel ·     │  │
  │  │ ganesha_orchestrator · ganesha_v2 · shiv_auto_rectify · scheduler_api ·     │  │
  │  │ system_health · simple_health · automobile                                  │  │
  │  └─────────────────────────────────────────────────────────────────────────────┘  │
  │  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────────┐  │
  │  │ GUARDIANS            │  │ DEPARTMENTS (20)     │  │ AUTOMOBILE MODULE      │  │
  │  │ GANESHA  orchestrate │──│ VISHWAKARMA LAKSHMI  │  │ pricing_engine         │  │
  │  │ SHIV     security    │  │ SURYA SARASWATI VAYU │  │ market_data            │  │
  │  │ PARVATI  workload    │  │ KUBERA INDRA YAMA    │  │ gst_integration        │  │
  │  └──────────────────────┘  │ VARUNA AGNI CHANDRA  │  │ router                 │  │
  │                            │ BRIHASPATI VISHNU    │  └────────────────────────┘  │
  │  ┌──────────────────────┐  │ BRAHMA KARTIKEYA     │  ┌────────────────────────┐  │
  │  │ APP SERVICES         │  │ DURGA HANUMAN NARADA │  │ AGENTS                 │  │
  │  │ ganesha_ai           │  │ ASHWINI DHARMA       │  │ c5_multimodel_strategy │  │
  │  │ orchestrator (v1/v2) │  │  (registry.py)       │  │ prompts/               │  │
  │  │ rag_service          │  └──────────────────────┘  └────────────────────────┘  │
  │  │ rag_knowledge_base   │                                                         │
  │  │ live_api_connector   │  ┌──────────────────────────────────────────────────┐  │
  │  │ email_service        │  │ PLATFORM SERVICES  backend/services/  (9)        │  │
  │  │ scheduler            │  │ document-ai · forecasting · anomaly · rag ·      │  │
  │  └──────────────────────┘  │ vision-gateway · speech · model-registry ·       │  │
  │                            │ knowledge-graph · automobile-llm                  │  │
  │  ┌──────────────────────┐  │ each: routes.py → service.py, own .env.example   │  │
  │  │ CORE                 │  └──────────────────────────────────────────────────┘  │
  │  │ config · mongodb     │                                                         │
  │  │ database · rbac      │  ┌──────────────────────────────────────────────────┐  │
  │  │ permissions          │  │ SHARED LIBRARY  backend/shared/                  │  │
  │  │ security · firebase  │  │ build_app() · BaseServiceSettings · auth ·       │  │
  │  │ seeder · db_indexes  │  │ schemas · errors · logging                        │  │
  │  │ celery_app           │  └──────────────────────────────────────────────────┘  │
  │  │ performance          │                                                         │
  │  └──────────────────────┘  ┌──────────────────────────────────────────────────┐  │
  │                            │ KNOWLEDGE  backend/knowledge/                     │  │
  │  ┌──────────────────────┐  │ config/api_sources.json · pre-data/ ·            │  │
  │  │ TASKS                │  │ post-data/daily-digest/<date>/<dept>.json ·      │  │
  │  │ daily_learning       │  │ post-data/department-specific/                    │  │
  │  └──────────────────────┘  └──────────────────────────────────────────────────┘  │
  └───────────┬──────────────────────┬─────────────────────┬──────────────────────────┘
              │                      │                     │
              ▼                      ▼                     ▼
    ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────────────────┐
    │ MongoDB 7        │   │ PostgreSQL 16    │   │ Redis 7                      │
    │ PRIMARY store    │   │ relational       │   │ cache · Celery broker        │
    │ db: "kailash"    │   │ postgres_models  │   │ maxmemory 256mb allkeys-lru  │
    └──────────────────┘   └──────────────────┘   └──────────────────────────────┘
              │
              ▼  UPSTREAM AI PROVIDERS (precedence order)
    ┌────────────────────────────────────────────────────────────────────────────┐
    │  1. OpenRouter (OPENROUTER_API_KEY)  →  2. Anthropic (ANTHROPIC_API_KEY)   │
    │  → 3. keyword / non-LLM fallback                                           │
    │  Also available: Google Gemini SDKs · AWS (boto3) · Pinecone (optional)    │
    └────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Request lifecycle

1. A caller (browser SPA or consumer product) sends an HTTPS request to `api.kailash-ai.in`.
2. Nginx terminates TLS, applies rate limits (`api_limit` 30 r/s, `auth_limit` 5 r/s per client IP), adds security headers, and proxies to `127.0.0.1:8000` over a keep-alive upstream.
3. FastAPI middleware attaches or generates a request ID, injects security headers, and installs the structured-logging context.
4. Authentication resolves: `Authorization: Bearer <JWT>` for human sessions, `X-Platform-Token` for internal service calls.
5. RBAC evaluates the caller's role against the named permission required by the route.
6. The router dispatches to a guardian, a department, a platform service, or the automobile module.
7. Where AI inference is needed, the provider chain is consulted in precedence order; retrieval context is fetched from the knowledge/RAG layer first where applicable.
8. State changes are persisted to MongoDB (and PostgreSQL where relational structure applies); activity records are written.
9. The response is wrapped in the `ApiResponse` envelope with the request ID echoed; metrics counters and histograms are updated.

---

## 3. Technology Stack

### 3.1 Backend

| Layer | Technology | Notes |
|---|---|---|
| Language / runtime | **Python 3.11** | Container base is `python:3.11-slim` |
| Web framework | **FastAPI 0.110.1** | ASGI; OpenAPI 3 auto-generated at `/docs` |
| ASGI server | **Uvicorn** | `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` |
| Settings | **pydantic-settings** | `backend/app/core/config.py`, `BaseServiceSettings` in `shared/config.py` |
| Validation | **Pydantic** | Models under `app/models/`, request/response schemas under `app/schemas/` |
| Mongo driver | **Motor / PyMongo (async)** | `app/core/mongodb.py`, `app/core/database.py` |
| Postgres driver | **asyncpg 0.31.0** | `app/models/postgres_models.py`, SQLAlchemy-style async URL |
| Task queue | **Celery 5.6.0** with **Redis** broker | `app/core/celery_app.py`; `amqp`/`billiard`/`kombu` present |
| Scheduling | **APScheduler 3.11.1** | `app/services/scheduler.py`, `api/scheduler_api.py`, `app/tasks/daily_learning.py` |
| Password hashing | **bcrypt 4.1.3** | With `passlib`-style usage in `core/security.py` |
| Tokens | **python-jose / ecdsa**, HS256 JWT | 24-hour access token expiry (`ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24`) |
| Crypto | **cryptography 46.0.3** | TOTP secrets, backup codes, general primitives |
| ML / numeric | **NumPy**, **scikit-learn** (`IsolationForest`) | Forecasting (EMA + trend + seasonal) and anomaly detection |
| Document handling | **pypdf**, **CairoSVG / cairocffi** | `document-ai` service, rendering/export paths |
| AI SDKs | **anthropic 0.73.0**, **google-genai 1.50.1**, **google-generativeai 0.8.5**, OpenAI-compatible client against OpenRouter | Provider chain |
| Cloud SDK | **boto3 1.40.67** | AWS access where required |
| Identity (admin) | **Firebase Admin SDK** | `app/core/firebase.py`; can be disabled via `FIREBASE_DISABLED` |
| Email | Application email service | `app/services/email_service.py` |
| Lint / format | **ruff**, plus `black` and `flake8` in requirements | `ruff.toml`, `make lint`, `make fmt` |
| Test | **pytest** | `tests/platform`, `tests/backend`, `tests/integration`, per-service suites |

### 3.2 Frontend

| Layer | Technology | Version |
|---|---|---|
| Framework | **React** | 19.0.0 |
| Build tooling | **react-scripts (CRA) 5.0.1** wrapped by **CRACO 7.1.0** | `craco start` / `craco build` |
| Routing | **react-router-dom** | 7.5.1 |
| Server state | **@tanstack/react-query** | 4.42.0 |
| Client state | **zustand** | 5.0.8 |
| HTTP | **axios** | 1.8.4 |
| UI primitives | **Radix UI** (26 packages: dialog, dropdown-menu, select, tabs, toast, tooltip, popover, accordion, and others) | 1.x/2.x |
| Styling | **Tailwind CSS** 3.4.17, `tailwindcss-animate`, `tailwind-merge`, `class-variance-authority`, `clsx` | — |
| Icons | **lucide-react** | 0.507.0 |
| Motion | **framer-motion** | 12.23.24 |
| 3D | **three** 0.160.0, **@react-three/fiber** 8.15, **@react-three/drei** 9.100 | Dashboard visualisation |
| Forms | **react-hook-form** 7.56.2 with **zod** 3.24.4 via **@hookform/resolvers** 5.0.1 | — |
| Notifications | **sonner** 2.0.3 | — |
| Dates | **date-fns** 4.1.0, **react-day-picker** 8.10.1 | — |
| Client SDK | **firebase** 11.7.1 | Hosting-adjacent client features |
| Theming | **next-themes** 0.4.6 | Light/dark |
| Lint | **eslint 9.23.0** with react, import and jsx-a11y plugins | Accessibility linting present |
| Package manager | **yarn 1.22.22** (declared via `packageManager`) | — |
| Browser automation (dev) | **puppeteer** 24.33.1 | Dev dependency |

### 3.3 Data and infrastructure

| Layer | Technology |
|---|---|
| Primary datastore | **MongoDB 7** (`mongo:7`), database name `kailash` |
| Relational store | **PostgreSQL 16** (`postgres:16-alpine`) |
| Cache / broker | **Redis 7** (`redis:7-alpine`), `maxmemory 256mb`, `allkeys-lru` |
| Service-local store | **SQLite** — used by the `model-registry` platform service |
| Vector store (optional) | **Pinecone** — `PINECONE_API_KEY`, `PINECONE_INDEX=kailashai`, `PINECONE_HOST` (blank in the template) |
| Containers | **Docker**, **Docker Compose** |
| Reverse proxy | **Nginx** with **Let's Encrypt / certbot** |
| Compute | **Vultr VPS** |
| Static hosting | **Firebase Hosting**, project `kailash-38268` |
| CI/CD | **GitHub Actions** (`ci.yml`, `deploy-backend.yml`, `deploy-frontend.yml`) |
| Metrics | Prometheus text-format exposition at `/metrics` |
| Logging | Structured JSON logging with a `service` field injected via a `logging.Filter` |

---

## 4. Functional Requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| **FR-1** | **Standard service contract.** Every module built via `build_app()` shall expose `GET /health` returning `{ service, version, uptime_s }`, `GET /` returning service metadata, `GET /metrics` in Prometheus text format, and `GET /docs` serving OpenAPI 3. | For each of the nine platform services and the main app, all four endpoints return 200 with the documented shape. |
| **FR-2** | **Uniform response envelope.** All domain routes shall return the `ApiResponse` envelope on success. Typed errors (`NotFoundError`, `ValidationError`, `UpstreamError`) shall map to `{ "ok": false, "error": { "code", "message", "hint" }, "request_id" }` with a stable `code` string. | Force one of each error type; assert the envelope shape, the correct `code`, and a non-null `request_id`. |
| **FR-3** | **Request correlation.** Middleware shall accept an inbound `x-request-id` header or generate a hex UUID, echo it on the response, and inject it into every log record produced during the request. | Send a request with a known `x-request-id`; find that exact value in the response header and in the corresponding JSON log lines. |
| **FR-4** | **Dual authentication.** Human callers authenticate with a JWT bearer token (HS256, 24-hour expiry) obtained from the auth router; internal service callers authenticate with `X-Platform-Token` validated by `require_internal_token` against `PLATFORM_INTERNAL_TOKEN`. Domain routes on platform services are guarded by the internal-token dependency. | Four cases tested: valid JWT accepted; expired/invalid JWT rejected with 401; valid platform token accepted on a guarded route; missing/incorrect platform token rejected. |
| **FR-5** | **Two-factor authentication.** The user record shall support `totp_secret`, `is_2fa_enabled` and a list of single-use `backup_codes`. When 2FA is enabled, a valid TOTP or an unused backup code shall be required to complete login, and a consumed backup code shall not be reusable. | Enable 2FA; login without a code fails; login with a valid TOTP succeeds; a backup code works once and fails on reuse. |
| **FR-6** | **RBAC enforcement.** Five roles (`super_admin`, `admin`, `manager`, `operator`, `viewer`) shall be evaluated against granular permissions across at least these families: departments (view/invoke/manage), guardians (view/manage/configure), users (view/create/update/delete), analytics (view/export/configure), pricing (view/manage), market data (view/manage), job cards (view/analyze), settings (view/update), tasks (view/create/assign/delete). | Role-by-permission matrix test; every denied combination returns an authorisation error with no data leakage in the body. |
| **FR-7** | **Department registry and invocation.** `initialize_departments()` shall instantiate every class in `DEPARTMENT_CLASSES` at startup; `get_department(name)` shall be case-insensitive; `list_departments()` shall return the full set. Each department shall be invocable through the departments API and viewable at `/department/:name` in the SPA. | Registry length equals `DEPARTMENT_CLASSES` length; lookup succeeds for lowercase and uppercase names; unknown names return a not-found error, not a crash. |
| **FR-8** | **Guardian orchestration.** GANESHA shall accept a natural-language request, select one or more departments, invoke them, and compose a response. A multimodel strategy (`agents/c5_multimodel_strategy.py`) shall select the model tier. SHIV shall apply security checks and auto-rectification. PARVATI shall track workload. The v2 GANESHA router shall be optional — if unavailable, the application shall log a warning and start with v2 endpoints disabled rather than failing. | Orchestrated request returns a composed answer naming the departments engaged; removing the v2 router module still allows startup with a logged warning. |
| **FR-9** | **Nine platform capabilities.** The platform shall provide: PDF text extraction with field validation (`document-ai`); demand/uptime/breakdown/energy forecasting via EMA plus trend plus seasonal baseline (`forecasting`); SLA/fraud/trust anomaly detection via `IsolationForest` (`anomaly`); embedding plus cosine retrieval with a SHA-256 hash fallback when no embedding provider is configured (`rag`); tier-based routing across vision models (`vision-gateway`); ASR and TTS with Indic locales (`speech`); an MLflow-shaped registry with evaluations backed by SQLite (`model-registry`); a typed graph over regulations, parts, HSN codes, workflows and certifications with BFS neighbour lookup (`knowledge-graph`); and domain-pinned automotive chat (`automobile-llm`). | Each service's test suite passes; each capability produces a correct result on a representative fixture. |
| **FR-10** | **Provider precedence and fallback.** AI calls shall attempt `OPENROUTER_API_KEY` first, then `ANTHROPIC_API_KEY`, then a non-LLM keyword fallback. Exhausting all options shall raise `UpstreamError`, never an unhandled exception. | Disable each tier in turn; observe the documented order in logs; final state returns the `upstream_error` envelope with a 5xx status, not a stack trace. |
| **FR-11** | **Retrieval-augmented answers.** The RAG layer shall index ingested documents and the dated per-department digests under `backend/knowledge/post-data/daily-digest/`, and shall return the top-k most similar chunks as context for department and guardian answers. Ingestion shall be possible via `database/rag_upload_script.py` without redeploying. | Ingest a document containing a unique token; query for it; the retrieved context contains the token and the answer reflects it. |
| **FR-12** | **Automobile domain computation.** The automobile module shall provide a pricing engine, market data lookup, and GST integration, exposed through its own router, returning a priced result with the applicable HSN/GST treatment for a given part or vehicle input. | Post a representative payload; response includes base price, applied market adjustment, HSN code and GST rate/amount. |
| **FR-13** | **Persistence and indexing.** On startup the application shall initialise the MongoDB connection, create required indexes (`core/db_indexes.py`), optionally seed reference data (`core/seeder.py`), and validate datastore permissions before accepting traffic, logging an explicit, actionable message if read or write permission on critical collections is missing. | Start against a permission-restricted user; the documented critical log block appears with the remediation steps; `SKIP_PERMISSION_CHECK=true` bypasses it in test environments only. |
| **FR-14** | **Scheduled and background work.** Celery (Redis broker) and APScheduler shall be wired, with at least a daily-learning task that refreshes department knowledge, and a scheduler API for inspection and control. | Trigger the daily-learning task; a new dated digest or knowledge update is produced and visible via the scheduler API. |
| **FR-15** | **Operations dashboard API.** The backend shall serve the SPA's needs across authentication, dashboard rollups, department detail and intelligence, tasks and GAPS CRUD, conversations, analytics, reports, users, RBAC administration, knowledge base, live data, guardians and system health. | Every authenticated SPA route loads with populated data against a seeded database; no route depends on an undocumented endpoint. |
| **FR-16** | **Health and metrics.** In addition to per-service `/health`, the main application shall expose a simple health endpoint at `/api/health` (used by the container healthcheck) and a richer system-health endpoint reporting datastore connectivity and dependency status. | `docker compose up` reaches a healthy container state; the system-health endpoint reports each dependency individually. |
| **FR-17** | **Configuration by environment only.** All environment-specific values — datastore URLs, secrets, provider keys, CORS origins, Firebase settings, domain URLs — shall come from environment variables with a checked-in `.env.example` template per module and no real value in version control. | Grep the repository for credential patterns; only placeholder values appear. Changing an environment variable changes behaviour without a code edit. |
| **FR-18** | **Graceful optional dependencies.** Firebase (`FIREBASE_DISABLED`), Pinecone (blank keys), and the v2 GANESHA router shall each be optional; absence shall degrade functionality with a logged warning rather than preventing startup. | Start with each optional dependency absent; the application reaches a healthy state with a warning per absent dependency. |
| **FR-19** | **Service scaffolding.** A new platform service shall be creatable from the existing pattern (`routes.py` → `service.py`, `.env.example`, tests) using the provided scaffolding script, and shall be picked up by the CI service matrix. | Scaffold a throwaway service; it exposes the four standard endpoints and its tests run in CI without pipeline edits beyond the matrix entry. |
| **FR-20** | **Data lifecycle tooling.** The platform shall provide MongoDB initialisation with collections and indexes, seed data for users, departments and activities, department data population, a RAG upload path, a health-check script and an automated backup routine. | Each script in `database/` runs to completion against a clean MongoDB instance and produces the documented artefacts. |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| ID | Requirement | Measurement |
|---|---|---|
| NFR-P1 | Non-LLM API endpoints shall return within **500 ms at p95** under nominal load. | Server-side histogram from `/metrics`, excluding upstream-model routes. |
| NFR-P2 | LLM-backed department/guardian responses shall complete within **8 s at p95** and **20 s at p99**, or return a typed timeout error. | End-to-end timing per request ID. |
| NFR-P3 | Health endpoints shall respond within **200 ms** and shall not perform expensive dependency work on the simple health path. | Probe timing under the container healthcheck's 10 s timeout. |
| NFR-P4 | The frontend production bundle shall be served with immutable long-lived caching on hashed static assets (`Cache-Control: public, max-age=31536000, immutable`). | Inspect response headers from Firebase Hosting. |
| NFR-P5 | Retrieval over the RAG index shall add no more than **300 ms at p95** to a grounded answer at the current corpus size. | Instrument retrieval separately from generation. |
| NFR-P6 | Redis shall be bounded at 256 MB with `allkeys-lru` eviction so cache growth cannot exhaust host memory. | Confirmed in `docker-compose.yml` command line. |

### 5.2 Scalability

| ID | Requirement |
|---|---|
| NFR-S1 | The backend shall be **stateless per request** (session state in the JWT, data in MongoDB/Postgres/Redis) so that additional instances can be added behind a load balancer without sticky sessions. |
| NFR-S2 | The current single-container deployment shall support at least **50 concurrent authenticated users** and **4 consumer products** at portfolio traffic levels; capacity headroom shall be monitored via `/metrics`. |
| NFR-S3 | Long-running or bursty work shall be offloaded to Celery workers rather than executed inline in a request. |
| NFR-S4 | Each platform service shall remain independently extractable into its own container without code change, by virtue of the `build_app()` contract. |
| NFR-S5 | MongoDB indexes required by hot query paths shall be created at startup (`core/db_indexes.py`), not left to ad-hoc creation. |
| NFR-S6 | Scale-out shall be triggered before sustained CPU or memory utilisation exceeds **60%** on the VPS. |

### 5.3 Security

| ID | Requirement |
|---|---|
| NFR-Sec1 | All external traffic shall be TLS 1.2 or 1.3 only, with HTTP redirected to HTTPS at the proxy. |
| NFR-Sec2 | The application port shall bind to loopback (`127.0.0.1:8000`) and never be published directly to the public interface. |
| NFR-Sec3 | Passwords shall be stored only as bcrypt hashes; plaintext passwords shall never be logged. |
| NFR-Sec4 | `SECRET_KEY` shall be a long random value in every non-development environment; the default `dev-secret-key-change-in-production` shall be rejected at startup in production. |
| NFR-Sec5 | CORS shall be restricted to the explicit `ALLOWED_ORIGINS` list in production (`kailash-ai.in`, `www.kailash-ai.in`, and the Firebase hosting domains); the permissive development default shall not reach production. |
| NFR-Sec6 | Security headers shall be applied at both the proxy and the hosting layer: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Referrer-Policy: strict-origin-when-cross-origin`, and a `Permissions-Policy` denying camera and geolocation while allowing microphone to self. |
| NFR-Sec7 | Rate limiting shall be enforced at the proxy: 30 requests/second for general API traffic and 5 requests/second for authentication endpoints, per client address. |
| NFR-Sec8 | The container shall run as a non-root user (`appuser`), as defined in the Dockerfile. |
| NFR-Sec9 | Internal service-to-service traffic shall require `X-Platform-Token`; this token shall be rotated on a defined schedule and on any suspected exposure. |
| NFR-Sec10 | No secret shall be committed. `.gitignore` shall exclude `.env`, `.venv/`, build artefacts and caches; pre-commit hooks and CI secret scanning shall enforce this. |
| NFR-Sec11 | Privileged accounts (`super_admin`, `admin`) shall have TOTP 2FA enabled. |
| NFR-Sec12 | Error responses shall not leak stack traces, internal paths, connection strings or upstream provider errors verbatim; the typed error envelope is the only external error surface. |

### 5.4 Availability and reliability

| ID | Requirement |
|---|---|
| NFR-A1 | Target availability of the backend API is **99.5% monthly**, measured by successful health probes. |
| NFR-A2 | Every container shall define a healthcheck and a `restart: unless-stopped` policy; the backend healthcheck shall use `/api/health` with a 40 s start period, 30 s interval, 10 s timeout and 3 retries. |
| NFR-A3 | The backend shall not start serving traffic until MongoDB, PostgreSQL and Redis report healthy (`depends_on: condition: service_healthy`). |
| NFR-A4 | MongoDB shall be backed up on a scheduled basis with a tested restore procedure; target **RPO 24 h**, **RTO 4 h**. |
| NFR-A5 | Container logs shall be rotated (`json-file` driver with size and file caps: 50 MB × 5 for the backend, smaller for datastores) so disk exhaustion cannot take down the host. |
| NFR-A6 | Failure of an optional dependency (Firebase, Pinecone, GANESHA v2) shall degrade rather than disable the platform. |
| NFR-A7 | Named data volumes shall be used for MongoDB, PostgreSQL and Redis so that container recreation does not destroy data. |

### 5.5 Compliance

| ID | Requirement |
|---|---|
| NFR-C1 | **GST / HSN.** Automobile pricing and GST integration shall apply the correct HSN classification and GST rate for automotive goods, with rates configurable rather than hard-coded, and each computed tax line traceable to the HSN code used. Rate changes shall be applicable without a code deployment. |
| NFR-C2 | **DISCOM / energy.** Where Kailash processes charger, energy or DISCOM-adjacent data on behalf of Ignition or URGAA, it shall retain the source and timestamp of every reading, shall not silently interpolate missing readings into billing-relevant outputs, and shall mark derived/forecast values distinctly from measured values. |
| NFR-C3 | **Data residency.** Personal and commercially sensitive Indian data shall be stored on Go4Garage-controlled infrastructure in India-appropriate regions. Any transfer to an offshore model provider shall be minimised, documented in the published sub-processor list, and subject to redaction of direct identifiers where the use case permits. |
| NFR-C4 | **Personal data handling.** Data subject rights (access, correction, erasure) shall be operationally supportable, backed by the published data-retention, data-transfer, data-breach and user-rights policies surfaced in the SPA. |
| NFR-C5 | **Auditability.** Privileged actions shall produce activity records with actor identity, role, timestamp and target, retained per the published retention policy. |
| NFR-C6 | **Licensing.** The codebase is proprietary; third-party dependency licences shall be reviewed before any external distribution of the Automobile-LLM or its artefacts. |
| NFR-C7 | **Accessibility.** The SPA shall target WCAG 2.1 AA; `eslint-plugin-jsx-a11y` is already in the toolchain and its findings shall be treated as build-blocking over time. |

### 5.6 Maintainability and observability

| ID | Requirement |
|---|---|
| NFR-M1 | `ruff check backend/` shall report zero violations; formatting shall be enforced by `ruff format` and pre-commit hooks. |
| NFR-M2 | Every module shall emit structured JSON logs including `service`, level, message and request ID. |
| NFR-M3 | `/metrics` shall expose Prometheus counters and histograms sufficient to compute request rate, error rate and latency distribution per route. |
| NFR-M4 | New capability shall follow the `routes.py` → `service.py` pattern; deviation requires an architecture decision record in `docs/architecture/`. |
| NFR-M5 | `README.md` and `ARCHITECTURE.md` shall remain accurate; a CI check shall assert that documented component counts match the code registry. |

---

## 6. Data Model / Storage

### 6.1 Storage allocation

| Store | Role | Rationale |
|---|---|---|
| **MongoDB 7** (database `kailash`) | Primary operational store: users, departments, tasks, activities, conversations, GANESHA records, system health, knowledge metadata | Document shape fits heterogeneous agent output and evolving schemas |
| **PostgreSQL 16** | Relational structures defined in `app/models/postgres_models.py` | Where referential integrity and relational querying matter |
| **Redis 7** | Cache and Celery broker/result backend | Bounded memory, LRU eviction |
| **SQLite** | `model-registry` service-local persistence | Simple, file-backed registry of model versions and evaluations |
| **Filesystem** | `backend/knowledge/` JSON corpus (config manifest, pre-data, dated daily digests, department-specific data) | Version-controllable, human-reviewable knowledge assets |
| **Pinecone** (optional, unconfigured) | External vector index, `PINECONE_INDEX=kailashai` | Reserved for durable vector retrieval at scale |
| **In-memory** | RAG cosine index; knowledge-graph adjacency structure | Current implementation; rebuilt on startup |

### 6.2 Core entities (MongoDB)

| Entity | Key fields | Notes |
|---|---|---|
| **User** (`app/models/user.py`) | `id` (UUID string), `email`, `kailash_code`, `full_name`, `hashed_password`, `is_active`, `is_admin`, `role`, `totp_secret`, `is_2fa_enabled`, `backup_codes[]`, `created_at`, `updated_at` | `role` defaults to `viewer`; `kailash_code` is an internal staff identifier; 2FA fields are optional |
| **Department** (`app/models/department.py`) | Department identity, deity name, domain, status, capability metadata, knowledge linkage | Mirrors the code registry in `departments/registry.py` |
| **Task** (`app/models/task.py`) | Task identity, title, description, assignee, department, status, priority, timestamps | Backs `/tasks` and the GAPS/task CRUD API |
| **Activity** (`app/models/activity.py`) | Actor, action, target, department, timestamp, metadata | The audit/activity trail |
| **GANESHA record** (`app/models/ganesha.py`) | Conversation/orchestration records: prompt, selected departments, model tier, response, timing | Backs conversations, GANESHA analytics and the multimodel strategy |

### 6.3 Knowledge layer layout

```
backend/knowledge/
├── config/
│   └── api_sources.json                 # manifest of external knowledge sources
├── pre-data/                            # curated source material prior to processing
└── post-data/
    ├── daily-digest/
    │   ├── 2025-12-15/  agni.json · ashwini.json · brahma.json · brihaspati.json ·
    │   │                chandra.json · indra.json · kartikeya.json · kubera.json ·
    │   │                lakshmi.json · marut.json · narada.json · pragya.json ·
    │   │                rudra.json · saraswati.json · surya.json · tvashta.json ·
    │   │                varuna.json · vayu.json · vishwakarma.json · yama.json ·
    │   │                summary.json
    │   └── 2025-12-18/  (same per-department shape)
    └── department-specific/             # longer-lived per-department knowledge
```

Note: the digest set includes deity names (`marut`, `pragya`, `rudra`, `tvashta`) that have **no corresponding department class** in `registry.py`. Either the digest producer or the registry is ahead of the other; this must be reconciled.

### 6.4 Indexing, seeding and backup

| Concern | Mechanism |
|---|---|
| Collection and index creation | `database/mongodb_init.js` (`createCollection`, `createIndex`) and `backend/app/core/db_indexes.py` at startup |
| Reference data seeding | `database/seed_data.py` (users, departments, activities), `backend/app/core/seeder.py` |
| Department content population | `database/populate_department_data.py` |
| RAG ingestion | `database/rag_upload_script.py` |
| Health verification | `database/mongodb_health_check.sh` |
| Backup | `database/backup_mongodb.py` (in-container daily automation) and `database/mongodb_backup.sh` |
| Startup permission validation | `validate_database_permissions()` in `backend/app/main.py`, checking read on `users` and write on `system_health`, bypassable with `SKIP_PERMISSION_CHECK=true` for testing only |

### 6.5 Data retention and classification

| Class | Examples | Handling |
|---|---|---|
| Credential | Password hashes, TOTP secrets, backup codes, API keys | Never logged; never returned by any API; secrets only via environment |
| Personal | Staff name, email, `kailash_code` | Access restricted by RBAC; retained per published retention policy |
| Operational | Tasks, activities, conversations, department outputs | Retained for audit and analytics; subject to the retention policy |
| Domain knowledge | Regulations, HSN mappings, certifications, digests | Versioned with effective dates; long retention by design |
| Derived | Forecasts, anomaly scores, model outputs | Marked as derived; not to be treated as measured fact (see NFR-C2) |

---

## 7. API & Integration Points

### 7.1 Internal API surface (main application)

| Router module | Responsibility |
|---|---|
| `auth.py` | Login, token issue, 2FA challenge |
| `users.py` | User CRUD and profile |
| `rbac.py` | Role and permission administration |
| `departments.py`, `department_intelligence.py` | Department listing, detail, invocation, intelligence rollups |
| `tasks.py`, `gaps_tasks_crud.py` | Task and GAPS lifecycle |
| `analytics.py`, `dashboard.py` | Analytics aggregates and dashboard rollups |
| `conversations.py` | Conversation history |
| `knowledge.py`, `knowledge_base.py` | Knowledge browsing and management |
| `live_data.py` | Live/external data surface (via `live_api_connector`) |
| `guardians.py` | Guardian status and control |
| `ganesha.py`, `ganesha_multimodel.py`, `ganesha_orchestrator.py`, `ganesha_v2.py` | Orchestration entry points across versions and strategies |
| `shiv_auto_rectify.py` | Security auto-rectification |
| `scheduler_api.py` | Scheduled job inspection and control |
| `system_health.py`, `simple_health.py` | Rich and lightweight health |
| `automobile.py` plus `app/automobile/router.py` | Pricing, market data, GST integration |

### 7.2 Platform service endpoints

Each of the nine services under `backend/services/` exposes the standard contract (`/health`, `/`, `/metrics`, `/docs`) plus its domain routes, which are guarded by `require_internal_token`.

| Service | Representative domain capability |
|---|---|
| `document-ai` | Extract text and validate fields from PDFs against validation profiles |
| `forecasting` | Demand, uptime, breakdown and energy forecasts |
| `anomaly` | SLA, fraud and trust anomaly scoring |
| `rag` | Embed, index and retrieve document chunks |
| `vision-gateway` | Route vision requests to an appropriate model tier |
| `speech` | ASR and TTS with Indic locales |
| `model-registry` | Register model versions and record evaluations |
| `knowledge-graph` | Query regulations, parts, HSN, workflows and certifications; BFS neighbours |
| `automobile-llm` | Automotive-domain chat with a pinned system prompt |

### 7.3 Authentication headers

| Header | Used by | Validated by |
|---|---|---|
| `Authorization: Bearer <JWT>` | Human users via the SPA | Auth dependency in `app/api/deps.py` / `core/security.py` |
| `X-Platform-Token: <value>` | Internal service callers and consumer products | `backend.shared.auth.require_internal_token` against `PLATFORM_INTERNAL_TOKEN`; no-op in dev mode |
| `x-request-id` | Optional, any caller | Request-id middleware; echoed on the response |

### 7.4 Internal Go4Garage integrations

| Consumer | Integration pattern | Status in this workspace |
|---|---|---|
| **ARJUN / ev-vidya-arjun** | Configured with a `KAILASH_AI_URL` environment variable pointing at the Kailash backend base URL, plus the internal platform token; consumes ID-proofing and speech capability | Specified as the integration contract. The `ev-vidya-arjun` directory in this workspace currently contains only empty platform scaffolding folders, so **no integration code was found here to verify against**. |
| **URGAA** | Certification and SLA intelligence — document-ai, anomaly, forecasting | Not evidenced from this copy |
| **GSTSAAS** | Invoice, fraud and voice intelligence — document-ai, anomaly, speech, automobile-llm | Not evidenced from this copy |
| **Ignition** | Charger trust and RC verification — vision-gateway, knowledge-graph, anomaly | Not evidenced from this copy |
| **Kailash SPA** | Same REST API with JWT bearer auth | Present and built |

### 7.5 Third-party integrations

| Provider | Purpose | Configuration | Status |
|---|---|---|---|
| **OpenRouter** | Primary LLM gateway (OpenAI-compatible), multi-model access | `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`, `OPENROUTER_SITE_URL`, `OPENROUTER_APP_NAME` | Primary provider in the precedence chain |
| **Anthropic** | Direct model access | `ANTHROPIC_API_KEY` (SDK `anthropic 0.73.0`) | Second in the chain |
| **Google Gemini** | Additional model access | `google-genai`, `google-generativeai` SDKs present | Available via the vision/multimodel routing |
| **Firebase (Admin SDK)** | Backend identity/administrative integration | `FIREBASE_SERVICE_ACCOUNT_PATH` or `FIREBASE_SERVICE_ACCOUNT_JSON`, `FIREBASE_PROJECT_ID=kailash-38268`, `FIREBASE_STORAGE_BUCKET`, `FIREBASE_DISABLED` | Configured; optional via kill-switch |
| **Firebase Hosting** | Frontend static hosting and CDN | `frontend/firebase.json`, project `kailash-38268` | Configured; deploy scripts present |
| **Firebase (client SDK)** | Frontend client features | `firebase@11.7.1` in the SPA | Present |
| **Pinecone** | Optional durable vector index | `PINECONE_API_KEY`, `PINECONE_INDEX=kailashai`, `PINECONE_HOST` | Placeholders blank — **not active** |
| **AWS** | Cloud SDK access | `boto3` | Present as a dependency; specific usage not documented |
| **Let's Encrypt / certbot** | TLS certificate issuance and renewal | `deploy/vultr/nginx-api.conf`, `setup-vps.sh` | Configured for `api.kailash-ai.in` |
| **GitHub Actions** | CI and deployment automation | `.github/workflows/` | Configured |
| **Email provider** | Transactional email | `app/services/email_service.py` | Service module present; provider binding via environment |

### 7.6 Integrations explicitly NOT present

The following were **not found** in this codebase and must not be assumed: any **payment gateway** (Kailash carries no billing surface), any **Slack** integration, any **SMS or voice telephony provider** integration at the platform level (speech capability exists as provider-agnostic stubs, which is a different thing), and any **push notification** service (there is no mobile client to notify).

---

## 8. Infrastructure & Deployment

### 8.1 Container definition

The `Dockerfile` builds from `python:3.11-slim`, installs `gcc`, `libpq-dev` and `curl`, installs `backend/requirements.txt`, copies `backend/` and `database/`, creates a non-root `appuser`, exposes port 8000, and runs `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`.

### 8.2 Compose topology

`docker-compose.yml` defines four services on a bridge network `kailash-network`:

| Service | Image / build | Notes |
|---|---|---|
| `backend` | Built from the root `Dockerfile` | Published to `127.0.0.1:8000` only; `env_file: backend/.env`; healthcheck on `/api/health`; log rotation 50 MB × 5 |
| `mongo` | `mongo:7` | Volumes `mongo_data`, `mongo_config`; healthcheck via `mongosh ping` |
| `postgres` | `postgres:16-alpine` | Database/user `kailash`; password from `POSTGRES_PASSWORD`; healthcheck via `pg_isready` |
| `redis` | `redis:7-alpine` | `--maxmemory 256mb --maxmemory-policy allkeys-lru`; healthcheck via `redis-cli ping` |

All four use `restart: unless-stopped`. The backend declares `depends_on` with `condition: service_healthy` for all three datastores.

Additional Compose variants exist under `deploy/docker/`: `docker-compose.prod.yml` and `docker-compose.platform.yml`, plus an `nginx.conf`.

### 8.3 VPS deployment (Vultr)

`deploy/vultr/setup-vps.sh` provisions the host; `deploy/vultr/deploy.sh` runs on the server, installing Docker, the Compose plugin, Nginx and certbot if absent, then syncing `/opt/kailash` from Git (`git fetch` plus `git reset --hard origin/<branch>` plus `git clean -fd`), verifying `backend/.env` exists (copying from `.env.example` with a loud warning if not), and bringing the stack up.

`deploy/vultr/nginx-api.conf` terminates TLS for `api.kailash-ai.in` with Let's Encrypt certificates, redirects HTTP to HTTPS, applies TLS 1.2/1.3 with `HIGH:!aNULL:!MD5` ciphers and session caching, sets security headers, defines two rate-limit zones (`api_limit` at 30 r/s, `auth_limit` at 5 r/s, each with a 10 MB state zone) and proxies to an upstream `kailash_backend` at `127.0.0.1:8000` with `keepalive 32`.

### 8.4 Frontend hosting

`frontend/firebase.json` publishes the `build` directory to Firebase Hosting with a catch-all SPA rewrite to `/index.html`, immutable one-year caching on `/static/**`, and security headers on all responses (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(self), geolocation=()`). Deploy scripts `yarn firebase:deploy` and `yarn firebase:preview` are defined in `package.json`.

### 8.5 CI/CD

`.github/workflows/ci.yml` defines six jobs — `lint` (ruff across `backend/`), `shared` (`tests/platform/`), `services` (a nine-way matrix, one job per platform service), `backend` (application smoke tests), `frontend` (`yarn install` plus `yarn build`), and `compose-build` (`docker compose build`). Separate workflows exist for `deploy-backend.yml` and `deploy-frontend.yml`.

### 8.6 Environments

| Environment | Definition | Status |
|---|---|---|
| **Local developer** | `docker compose up -d --build`, or `uvicorn` plus `yarn start` directly | **Confirmed working.** `backend/.venv/` is populated; `frontend/node_modules/` and `frontend/build/` exist. |
| **CI** | GitHub-hosted runners executing the six-job matrix | Configured in the repository |
| **Production backend** | Docker Compose on a Vultr VPS behind Nginx at `api.kailash-ai.in` | **Tooling present; live status not verified from this working copy.** |
| **Production frontend** | Firebase Hosting, project `kailash-38268`, domains `kailash-ai.in` / `www.kailash-ai.in` / `kailash-38268.web.app` | **Configuration present; live status not verified from this working copy.** |
| **Staging** | Not defined in this repository | Absent |

### 8.7 Source control reality

The local working copy is a Git repository on branch `main` with an `origin/main` tracking ref. `origin` is configured as `https://github.com/urgaa-eka/kailash.git`, and every in-repo reference (CI badges in `README.md`, `REPO_URL` in `deploy/vultr/deploy.sh`, `deploy/vultr/setup-vps.sh`, `docs/DEPLOYMENT.md`, `CHANGELOG.md` compare links) now points at that same remote. This was previously inconsistent and deploy-relevant, because `deploy.sh` clones and hard-resets from `REPO_URL`.

The most recent commit is `40cca17` — *"refactor: introduce top-level database/ folder, fix corrupted seed scripts"* — dated 2026-07-31 02:53 +0530, preceded by `92adca5` (frontend lockfile sync) and `07ea50f` (consolidation into a single backend and single frontend). Development is active as of today.

---

## 9. Security & Compliance Requirements

### 9.1 Identity and access

| ID | Requirement |
|---|---|
| SEC-1 | Human authentication: email plus bcrypt-verified password, issuing an HS256 JWT with a 24-hour lifetime. |
| SEC-2 | Optional TOTP 2FA per user with single-use backup codes; mandatory for `super_admin` and `admin`. |
| SEC-3 | Service authentication: `X-Platform-Token` shared secret, distinct per environment, rotated on schedule and on suspected exposure. |
| SEC-4 | Five-role RBAC with granular permission strings, enforced server-side on every protected route. Client-side hiding of UI is never the enforcement point. |
| SEC-5 | Least privilege on datastore credentials: the application user holds `readWrite` on the `kailash` database only, never cluster-admin rights. |

### 9.2 Transport and network

| ID | Requirement |
|---|---|
| SEC-6 | TLS 1.2/1.3 only, HTTP to HTTPS redirect, `HIGH:!aNULL:!MD5` cipher policy, server cipher preference on, session cache enabled. |
| SEC-7 | Application port bound to loopback; only Nginx faces the public network. |
| SEC-8 | Rate limiting at the proxy: 30 r/s general, 5 r/s on authentication paths. |
| SEC-9 | Datastore containers are reachable only on the internal Compose network and publish no host ports. |

### 9.3 Application security

| ID | Requirement |
|---|---|
| SEC-10 | Security headers applied by middleware and at the proxy and hosting layers (see NFR-Sec6). |
| SEC-11 | All input validated by Pydantic schemas; validation failures return `ValidationError` envelopes, not stack traces. |
| SEC-12 | Errors surfaced through the typed `PlatformError` hierarchy only; internal details are logged, never returned. |
| SEC-13 | SHIV auto-rectification shall record every automated security action as an activity record with actor `SHIV` and a rationale. |
| SEC-14 | Prompt-injection and data-exfiltration risk in RAG and agent flows shall be mitigated by constraining retrieved context to the authorised knowledge scope for the caller's role. |

### 9.4 Secrets management

| ID | Requirement |
|---|---|
| SEC-15 | Secrets exist only in environment variables or the secret store of the CI/CD provider; every module ships a `.env.example` with placeholders. |
| SEC-16 | `.gitignore` excludes `.env`, `.venv/`, build artefacts and caches; pre-commit hooks and CI secret scanning enforce this. |
| SEC-17 | Firebase service-account material shall be supplied by path or inline JSON at deploy time, never committed. |
| SEC-18 | Documented rotation procedure for `SECRET_KEY`, `PLATFORM_INTERNAL_TOKEN`, all model-provider keys, database credentials and Firebase service accounts. |

### 9.5 Compliance controls

| ID | Requirement |
|---|---|
| SEC-19 | **GST/HSN:** every tax computation traceable to an HSN code and a configurable rate; rate changes deployable as configuration. |
| SEC-20 | **DISCOM/energy:** measured versus derived values distinguished; source and timestamp retained for readings used in downstream decisions. |
| SEC-21 | **Data residency:** Indian personal and sensitive data stored on Go4Garage-controlled India-appropriate infrastructure; offshore model-provider transfers minimised, redacted where possible, and disclosed in the sub-processor list. |
| SEC-22 | **Retention and rights:** the published data-retention, data-transfer, data-breach and user-rights policies are operationally implemented, not merely displayed. |
| SEC-23 | **Audit:** activity records for all privileged actions with actor, role, timestamp and target. |
| SEC-24 | **Incident response:** the process in `SECURITY.md` and the in-product incident-response page shall be exercised at least annually. |
| SEC-25 | **Vulnerability management:** dependency scanning in CI; critical findings remediated within the `SECURITY.md` SLA. |

---

## 10. Testing Strategy

### 10.1 Test layers

| Layer | Location | Scope |
|---|---|---|
| Shared-library unit tests | `tests/platform/test_shared.py` | `build_app()` wiring, envelopes, typed errors, auth dependency, logging filter |
| Platform service tests | Per-service suites under `backend/services/<service>/` | Domain logic for each of the nine capability modules; run as a nine-way CI matrix |
| Backend integration tests | `tests/backend/{backend_test.py, comprehensive_backend_test.py, quick_ganesha_test.py}` | Router behaviour, auth flows, GANESHA paths against a running application |
| End-to-end / scenario | `tests/integration/investor_demo_test.py` | Full-journey demonstration scenarios |
| Exploratory / diagnostic scripts | `tests/scripts/` (`test_db_connection.py`, `debug_api_key.py`, `ganesha_orchestrator_test.py`, `kailash_comprehensive_test.py`, and others) | Developer diagnostics; not CI gates |
| Frontend build verification | CI `frontend` job | `yarn install` plus `yarn build` must succeed |
| Container verification | CI `compose-build` job | `docker compose build` must succeed |

### 10.2 Requirements

| ID | Requirement |
|---|---|
| TEST-1 | Every platform service shall have an independently runnable test suite that passes without network access to model providers (providers stubbed or the keyword fallback exercised). |
| TEST-2 | Contract tests shall assert the `ApiResponse` envelope and the `request_id` field on at least one success and one failure per router. |
| TEST-3 | An RBAC matrix test shall cover every role against every permission family, asserting both allow and deny outcomes. |
| TEST-4 | Authentication tests shall cover valid login, invalid password, expired token, 2FA-required, valid TOTP, backup-code single use, and platform-token accept/reject. |
| TEST-5 | Provider-fallback tests shall simulate failure at each tier and assert the documented precedence order and the terminal `UpstreamError`. |
| TEST-6 | Data-layer tests shall verify index creation, seed idempotency (re-running the seeder does not duplicate records) and the backup/restore round trip. |
| TEST-7 | Startup tests shall confirm graceful degradation when Firebase, Pinecone or the GANESHA v2 router is absent. |
| TEST-8 | The frontend shall have at least smoke coverage that the production bundle builds and the SPA mounts; accessibility linting (`jsx-a11y`) findings shall trend to zero. |
| TEST-9 | A CI check shall assert that documented component counts (departments, services) match the code registry, preventing the current 20-versus-24 style drift. |
| TEST-10 | Performance tests shall establish and track p95 latency baselines for both non-LLM and LLM-backed routes. |
| TEST-11 | Security tests shall include a secret scan across history, a check that the production configuration rejects the default `SECRET_KEY`, and a check that CORS is not wildcarded in production. |
| TEST-12 | Restore drills shall be performed quarterly and their RTO recorded. |

### 10.3 Gating

No change merges to `main` unless `lint`, `shared`, `services` (all nine), `backend`, `frontend` and `compose-build` are green. The pre-commit configuration in `.pre-commit-config.yaml` runs the same lint/format checks locally before commit.

---

## 11. Current Implementation Status

*Assessed 2026-07-31 against the working copy at `C:\Go4Garage( Eka)\Kailash-Ai`, HEAD `40cca17`.*

### 11.1 Verified present

| Component | Evidence |
|---|---|
| FastAPI application with lifespan startup, CORS, security and error middleware | `backend/app/main.py` |
| Roughly 24 API router modules | `backend/app/api/*.py` |
| 20 registered department classes | `backend/app/departments/registry.py` (`DEPARTMENT_CLASSES`) |
| 3 guardian agents | `backend/app/guardians/{ganesha,shiv,parvati}.py` |
| Multi-model strategy and prompt library | `backend/app/agents/c5_multimodel_strategy.py`, `backend/app/agents/prompts/` |
| 9 platform services, each with `.env.example` | `backend/services/*/` |
| Automobile module (pricing, market data, GST, router) | `backend/app/automobile/` |
| Core layer: config, mongodb, database, db_indexes, seeder, firebase, rbac, permissions, security, security_enhancements, performance, celery_app | `backend/app/core/` |
| Application services: ganesha_ai, orchestrator v1/v2, rag_service, rag_knowledge_base, live_api_connector, email_service, scheduler | `backend/app/services/` |
| Models: user, department, task, activity, ganesha, postgres_models | `backend/app/models/` |
| Schemas: auth, ganesha, task | `backend/app/schemas/` |
| Background task: daily learning | `backend/app/tasks/daily_learning.py` |
| Knowledge corpus with dated digests | `backend/knowledge/` |
| React 19 SPA with roughly 70 page modules and roughly 21 authenticated routes | `frontend/src/pages/`, `frontend/src/App.js` |
| Compiled frontend bundle | `frontend/build/` including `static/`, `index.html`, brand video and OG assets |
| Installed dependency trees | `backend/.venv/` (Lib, Scripts, pyvenv.cfg) and `frontend/node_modules/` (roughly 1,000 entries) |
| Database tooling | `database/` (init, seed, populate, RAG upload, health check, backup ×2) |
| Container and Compose definitions | `Dockerfile`, `docker-compose.yml`, `deploy/docker/` |
| VPS and proxy configuration | `deploy/vultr/{setup-vps.sh,deploy.sh,nginx-api.conf}` |
| Firebase Hosting configuration | `frontend/firebase.json` |
| CI/CD workflows | `.github/workflows/{ci.yml,deploy-backend.yml,deploy-frontend.yml}` |
| Test suites | `tests/{platform,backend,integration,scripts}/` |
| Developer tooling | `Makefile`, `ruff.toml`, `.pre-commit-config.yaml`, `.editorconfig`, `.devcontainer/`, `scripts/` |
| Documentation | `README.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`, `docs/` tree |

### 11.2 Present but shallow, stubbed, or unverified

| Item | Honest status |
|---|---|
| `automobile-llm` | An OpenRouter wrapper with a pinned domain system prompt, per the README. No owned fine-tuned model exists. |
| `speech` | Provider-agnostic stubs with Indic locale scaffolding; no production ASR/TTS provider is bound. |
| `rag` retrieval | In-memory cosine index with a SHA-256 hash embedding fallback when no embedding provider is configured. Not durable across restarts. |
| `knowledge-graph` | In-memory typed graph with BFS neighbour lookup. Not backed by a graph database. |
| Pinecone | Environment placeholders present and blank. **Not active.** |
| PostgreSQL | Container, driver and `postgres_models.py` present; the split of responsibility versus MongoDB is not documented. |
| Production environments | Deploy tooling and domain configuration exist; **no evidence in this copy that anything is currently live**. |
| Consumer-product integrations | The `KAILASH_AI_URL` contract is specified. `ev-vidya-arjun` in this workspace contains only empty scaffolding folders — the integration could not be verified here. URGAA, GSTSAAS and Ignition integrations were likewise not verifiable from this copy. |
| Department count | Code registers 20; `README.md` and `ARCHITECTURE.md` state 24; knowledge digests reference 4 additional deity names (`marut`, `pragya`, `rudra`, `tvashta`) with no matching classes. Unreconciled. |
| Test counts | README publishes 5 / 53 / 10+ / 3+; suites exist but were not re-executed for this assessment. |
| Git remote | Resolved — `urgaa-eka/kailash` is canonical (matches `origin`); README badges, `deploy/vultr/*.sh` and `docs/DEPLOYMENT.md` all updated. |
| `CORS_ORIGINS` default | `Settings.CORS_ORIGINS` defaults to `"*"` in `core/config.py`, with the restrictive list living in `.env.example`. The permissive default must not reach production. |
| `SECRET_KEY` default | Falls back to `dev-secret-key-change-in-production` if unset. Production startup must reject this. |
| Startup permission check | Currently logs a critical block and continues; the hard-fail line is commented out in `main.py`. |
| Mobile clients | **None.** `ios_app_kailash_ai/` and `android_app_kailash_ai/` contain only empty `deployed/` and `not_deployed/` directories. |

### 11.3 Summary

The technical foundation is real, coherent and unusually well-structured for an internal platform: a genuine shared library, a consistent service contract, a nine-way CI matrix, container and proxy hardening, and working local builds of both tiers. The credible gaps are (a) the difference between deployment tooling and a verified live deployment, (b) three configuration defaults that are safe for development and unsafe for production, (c) the remote-URL mismatch that makes the deploy script hazardous, and (d) the capability depth of `automobile-llm`, `speech` and durable retrieval.

---

## 12. Technical Risks & Dependencies

### 12.1 Technical risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| TR-1 | **Deploy script pulls from the wrong repository** because `REPO_URL` in `deploy/vultr/deploy.sh` does not match the configured `origin`. `deploy.sh` performs `git reset --hard` plus `git clean -fd`, so a wrong-source deploy is destructive. | Medium | High | Reconcile all three references to one canonical remote before the next deploy; parameterise `REPO_URL` from the environment; add a pre-deploy assertion that the resolved remote matches an allowlist. |
| TR-2 | **Permissive development defaults reach production** — `CORS_ORIGINS="*"`, `SECRET_KEY="dev-secret-key-change-in-production"`, `require_internal_token` being a no-op in dev mode. | Medium | High | Fail fast at startup when `ENV=production` and any of these hold an unsafe value; add a CI check on production configuration. |
| TR-3 | **Startup permission validation is advisory, not blocking** — the hard-fail is commented out, so the app can start into a state where authentication is guaranteed to fail. | Medium | High | Enable the hard-fail in production; add a synthetic login probe to monitoring so the failure is detected in seconds, not by users. |
| TR-4 | **In-memory RAG and knowledge graph lose state on restart** and cannot scale beyond a single process. | High | Medium | Move to a persistent vector store (the Pinecone configuration is already scaffolded) and a durable graph representation. |
| TR-5 | **Single-instance backend** — one container, one VPS, no redundancy. | Medium | High | Introduce a second instance behind a load balancer, or container orchestration; verify statelessness first (NFR-S1). |
| TR-6 | **Upstream model dependency** — rate limits, price changes, deprecations or outages at OpenRouter/Anthropic/Google. | High | High | Provider precedence chain with keyword fallback; model registry for auditable swaps; fine-tuning roadmap. |
| TR-7 | **Three datastores for one application** raises operational complexity and the chance of an unbacked-up store. | Medium | Medium | Document the responsibility split; extend backup coverage to PostgreSQL, not only MongoDB; verify restore for both. |
| TR-8 | **Dependency surface is very large** — the backend requirements span AI SDKs from three vendors, AWS, Celery, Postgres, Cairo/SVG rendering and more. | High | Medium | Dependency scanning in CI; periodic pruning of unused dependencies; pin and review upgrades. |
| TR-9 | **CRA is in maintenance mode** — `react-scripts 5.0.1` with CRACO is an ageing build path for a React 19 application. | Medium | Medium | Plan a migration to Vite or Next.js; treat build-tool risk as a scheduled item, not an emergency. |
| TR-10 | **Documentation/code drift** — the 20-versus-24 department discrepancy demonstrates the failure mode. | High | Low | CI assertion that documented counts match the registry (TEST-9). |
| TR-11 | **Prompt injection through RAG content** — ingested documents influencing agent behaviour. | Medium | High | Constrain retrieved context to the caller's authorised scope; separate instruction and data channels; red-team the ingestion path. |
| TR-12 | **Cost blowout** as four products drive traffic through paid model APIs. | Medium | Medium | Per-caller token accounting in metrics; tiered routing with cheap-model-first escalation; budget alerts. |
| TR-13 | **Secret exposure through logs** — request/response logging capturing tokens or personal data. | Medium | High | Redaction filters in the logging pipeline; assert in tests that known credential patterns never appear in log output. |
| TR-14 | **Optional-dependency drift** — code paths that are only exercised when Firebase or Pinecone are configured rot silently. | Medium | Low | Cover both configured and unconfigured states in CI. |

### 12.2 External dependencies

| Dependency | Type | Criticality | Failure impact |
|---|---|---|---|
| OpenRouter | Model gateway | Critical | Falls back to Anthropic, then keyword fallback; quality degrades |
| Anthropic | Model provider | High | Second-tier fallback lost |
| Google Gemini SDKs | Model provider | Medium | Vision/multimodel routing options reduced |
| MongoDB 7 | Datastore | Critical | Platform unavailable |
| PostgreSQL 16 | Datastore | Medium | Relational features unavailable |
| Redis 7 | Cache/broker | High | Background tasks stall; cache misses increase load |
| Firebase Hosting | Frontend CDN | High | Dashboard unreachable; backend API unaffected |
| Firebase Admin SDK | Backend identity | Medium | Disable via `FIREBASE_DISABLED`; related features degrade |
| Vultr | Compute host | Critical | Backend unavailable |
| Let's Encrypt | TLS certificates | High | Certificate expiry breaks HTTPS; automate renewal monitoring |
| GitHub Actions | CI/CD | High | Manual deploy required |
| Pinecone | Vector index | Low today | Not active; would become High after TR-4 remediation |
| PyPI / npm registries | Build-time | High | Build reproducibility; mitigate with lockfiles and pinned versions |

### 12.3 Internal dependencies

| Dependency | Note |
|---|---|
| `backend/shared/` | Every module depends on it; a breaking change there breaks everything. Treat as a versioned internal API. |
| `departments/registry.py` | Single point of truth for department availability; keep documentation generated from it. |
| `core/config.py` | Single point of truth for settings; environment-variable naming changes are breaking. |
| Knowledge corpus | Answer quality depends on SME curation cadence, not on code. |
| Consumer products | Kailash's API contract is load-bearing for four products; contract changes require coordinated releases. |

---

## 13. Appendix

### 13.1 Sibling documents

This product-level TRD accompanies **`BRD_kailash_ai.md`** (product level, same directory). The application-level documents are:

| Document | Location |
|---|---|
| `BRD_web_app_kailash_ai.md` | `web_app_kailash_ai/` |
| `TRD_web_app_kailash_ai.md` | `web_app_kailash_ai/` |
| `BRD_ios_app_kailash_ai.md` | `ios_app_kailash_ai/` |
| `TRD_ios_app_kailash_ai.md` | `ios_app_kailash_ai/` |
| `BRD_android_app_kailash_ai.md` | `android_app_kailash_ai/` |
| `TRD_android_app_kailash_ai.md` | `android_app_kailash_ai/` |

### 13.2 Repository layout reference

```
Kailash-Ai/
├── backend/
│   ├── app/          agents · api · automobile · core · departments · guardians ·
│   │                 middleware · models · schemas · services · tasks · main.py
│   ├── services/     document-ai · forecasting · anomaly · rag · vision-gateway ·
│   │                 speech · model-registry · knowledge-graph · automobile-llm
│   ├── shared/       app.py · auth.py · schemas.py · errors.py · config.py · logging.py
│   ├── knowledge/    config/ · pre-data/ · post-data/
│   ├── routers/      v2 GANESHA router
│   ├── tests/        backend tests
│   ├── requirements.txt · server.py · .env.example · .venv/
├── frontend/         src/ (components, pages, services, stores, hooks, context, data,
│                     lib, styles) · build/ · node_modules/ · package.json · firebase.json
├── database/         mongodb_init.js · seed_data.py · populate_department_data.py ·
│                     rag_upload_script.py · backup_mongodb.py · mongodb_backup.sh ·
│                     mongodb_health_check.sh
├── deploy/           docker/ (compose.prod, compose.platform, nginx.conf)
│                     vultr/  (setup-vps.sh, deploy.sh, nginx-api.conf)
├── docs/             architecture/ · api/ · guides/ · business/ · archived/
├── tests/            platform/ · backend/ · integration/ · scripts/
├── scripts/          generate_services.ps1 · health_check.sh
├── .github/workflows/ ci.yml · deploy-backend.yml · deploy-frontend.yml
├── Dockerfile · docker-compose.yml · Makefile · ruff.toml
├── README.md · ARCHITECTURE.md · CHANGELOG.md · CONTRIBUTING.md · SECURITY.md · LICENSE
├── BRD_kailash_ai.md · TRD_kailash_ai.md
├── web_app_kailash_ai/ · ios_app_kailash_ai/ · android_app_kailash_ai/
```

### 13.3 Environment variable reference (from `backend/.env.example`)

| Variable | Purpose |
|---|---|
| `MONGO_URL`, `DATABASE_NAME` | MongoDB connection and database (`kailash`) |
| `SECRET_KEY` | JWT signing key |
| `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`, `OPENROUTER_SITE_URL`, `OPENROUTER_APP_NAME` | Primary model provider |
| `ANTHROPIC_API_KEY` | Secondary model provider |
| `PINECONE_API_KEY`, `PINECONE_INDEX`, `PINECONE_HOST` | Optional vector store |
| `BACKEND_URL`, `FRONTEND_URL`, `ALLOWED_ORIGINS` | Domain and CORS configuration |
| `FIREBASE_SERVICE_ACCOUNT_PATH` / `FIREBASE_SERVICE_ACCOUNT_JSON`, `FIREBASE_PROJECT_ID`, `FIREBASE_STORAGE_BUCKET`, `FIREBASE_DISABLED` | Firebase Admin SDK |
| `POSTGRES_URL`, `POSTGRES_PASSWORD` | PostgreSQL (set in Compose) |
| `REDIS_URL` | Redis (set in Compose) |
| `PLATFORM_INTERNAL_TOKEN` | Internal service authentication (shared library) |
| `SKIP_PERMISSION_CHECK` | Testing-only bypass of startup datastore permission validation |

### 13.4 Standard error codes

| Exception | `error.code` | Typical HTTP status |
|---|---|---|
| `NotFoundError` | `not_found` | 404 |
| `ValidationError` | `validation_error` | 422 |
| `UpstreamError` | `upstream_error` | 502 / 503 |

### 13.5 Make targets

| Target | Action |
|---|---|
| `make install` | Install backend requirements |
| `make lint` | `ruff check backend/` |
| `make fmt` | `ruff format backend/` |
| `make test` | `pytest tests/` |
| `make test-platform` | Run each platform service's suite |
| `make up` / `make down` | `docker compose up -d --build` / `docker compose down` |

### 13.6 Open technical questions

1. What is the intended responsibility split between MongoDB and PostgreSQL?
2. Which Git remote is canonical, and who owns updating `deploy/vultr/deploy.sh`?
3. Is a persistent vector store approved (Pinecone versus a self-hosted alternative), given the data-residency position in NFR-C3?
4. Should the startup permission hard-fail be enabled now, and behind which environment flag?
5. Which ASR/TTS provider will replace the speech stubs, and does it satisfy Indic language coverage and residency requirements?
6. What is the migration plan and timeline off CRA/CRACO for the frontend build?
7. Are 20 departments correct, or are 4 more to be implemented to match the documented 24?
