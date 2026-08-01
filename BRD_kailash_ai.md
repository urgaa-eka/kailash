# Business Requirements Document — Kailash-Ai

## 1. Document Control

| Field | Value |
|---|---|
| **Document title** | Business Requirements Document — Kailash-Ai (Kailash AI Platform) |
| **Product** | Kailash — Go4Garage internal ML/AI platform |
| **Document type** | BRD (Product level) |
| **Version** | 1.0 |
| **Date** | 2026-07-31 |
| **Status** | Draft |
| **Owner** | TBD |
| **Author** | Go4Garage Documentation Workstream |
| **Reviewers** | TBD (Engineering Lead, Platform Lead, Compliance) |
| **Approvers** | TBD |
| **Classification** | Internal — Proprietary (see `LICENSE`) |
| **Source of truth** | Local working copy at `C:\Go4Garage( Eka)\Kailash-Ai`, HEAD commit `40cca17` dated 2026-07-31 |

### 1.1 Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-31 | Documentation Workstream | Initial draft, grounded in the on-disk repository state as of HEAD `40cca17` |

### 1.2 Related Documents

| Document | Location |
|---|---|
| Product TRD | `TRD_kailash_ai.md` |
| Repository README | `README.md` |
| Architecture map | `ARCHITECTURE.md` |
| Platform overview | `docs/architecture/platform-overview.md` |
| Knowledge architecture | `docs/architecture/knowledge-architecture.md` |
| Security policy | `SECURITY.md` |
| Contribution model | `CONTRIBUTING.md` |

---

## 2. Executive Summary

Kailash is Go4Garage's internal ML/AI platform — described in its own README as *"the internal ML/AI platform powering India's EV revolution."* It is explicitly **not** a product sold to external customers. It is the shared AI engine that other Go4Garage products call into: URGAA (certifications and SLA intelligence), GSTSAAS (invoice, fraud and voice intelligence), Ignition (charger trust and RC verification), ARJUN / `ev-vidya-arjun` (ID proofing and speech), and the Kailash operations dashboard itself.

Architecturally, Kailash is a Python 3.11 FastAPI backend paired with a React 19 single-page frontend, storing operational data in MongoDB. The backend is organised in a distinctive "department-style AI agent" model: the application package `backend/app/` is split into `agents`, `api`, `automobile`, `core`, `departments`, `guardians`, `middleware`, `models`, `schemas`, `services` and `tasks`. Twenty deity-named department agents (VISHWAKARMA, LAKSHMI, SURYA, SARASWATI, VAYU, KUBERA, INDRA, YAMA, VARUNA, AGNI, CHANDRA, BRIHASPATI, VISHNU, BRAHMA, KARTIKEYA, DURGA, HANUMAN, NARADA, ASHWINI, DHARMA) are registered through `backend/app/departments/registry.py`, and three "guardian" agents — GANESHA (orchestration), SHIV (security / auto-rectification) and PARVATI (workload) — sit above them. A separate tier of nine platform AI services (`document-ai`, `forecasting`, `anomaly`, `rag`, `vision-gateway`, `speech`, `model-registry`, `knowledge-graph`, `automobile-llm`) lives under `backend/services/`, each following a consistent `routes.py` → `service.py` pattern built on a shared `build_app()` factory.

A knowledge/RAG layer (`backend/knowledge/` plus `app/services/rag_service.py` and `rag_knowledge_base.py`) provides retrieval-augmented context to the departments, fed by dated daily-digest JSON payloads and an API-source manifest. A dedicated top-level `database/` folder carries MongoDB initialisation, seeding, health-check, backup and RAG-upload tooling. Deployment tooling exists for Docker (a single-container `Dockerfile` plus a four-service `docker-compose.yml`) and for a Vultr VPS behind Nginx with Let's Encrypt TLS, with the frontend targeted at Firebase Hosting (project `kailash-38268`).

The platform has genuinely been built and run locally: a populated Python virtual environment exists at `backend/.venv/`, and the frontend has both an installed `node_modules/` tree (~1,000 packages) and a produced `frontend/build/` output including compiled static assets and brand video files. Development is active — the most recent commit landed on 2026-07-31 (today).

The commercial thesis behind Kailash is the **Automobile-LLM moat**: today the `automobile-llm` service is an OpenRouter wrapper pinned to an automotive-domain system prompt; the stated productisation path is to fine-tune an open-weights base model on automotive regulations and service-manual-derived Q&A, then compound that with anonymised operational data flowing in from URGAA, GSTSAAS, Ignition and ARJUN, ultimately yielding a domain model licensable to OEMs and DISCOMs. This BRD captures the business requirements for Kailash as a platform: what it must do for its internal consumers, how success is measured, and what is honestly built versus aspirational today.

---

## 3. Business Objectives & Strategic Fit

### 3.1 Go4Garage strategic context

Go4Garage's portfolio spans EV and automotive intelligence across several distinct commercial surfaces — certification and SLA (URGAA), GST/invoice and financial compliance (GSTSAAS), charger and RC trust (Ignition), identity and speech for EV education/enablement (ARJUN / `ev-vidya-arjun`), and the group's own operations cockpit. Each of these needs document understanding, forecasting, anomaly detection, retrieval over Indian automotive regulation, vision, Indic speech, and domain-tuned language reasoning. Building those capabilities four or five times independently would be economically indefensible and would fragment the group's most valuable long-term asset: automotive domain data.

Kailash exists to concentrate that capability in one place.

### 3.2 Objectives

| # | Objective | Strategic rationale |
|---|---|---|
| **O-1** | **Be the single AI engine for the Go4Garage portfolio.** One backend, one auth model, one response envelope, consumed by every product. | Eliminates duplicated ML spend and duplicated vendor contracts; a capability built once ships to all products. |
| **O-2** | **Insulate product teams from AI vendor churn.** Consumer products call Kailash, never OpenRouter/Anthropic/Google directly. | Model prices, availability and terms change constantly. Centralising the provider chain (`OPENROUTER_API_KEY` → `ANTHROPIC_API_KEY` → keyword fallback) means a vendor switch is one platform change, not five product migrations. |
| **O-3** | **Accumulate a proprietary automotive/EV data moat.** Route all product AI traffic through one platform so the resulting corpus is centrally governed. | Data flowing from certifications, invoices, charger telemetry and job cards is the raw material for Automobile-LLM. Fragmented across products it is worthless; centralised it is a defensible asset. |
| **O-4** | **Deliver an operations cockpit for Go4Garage leadership.** Departments, tasks, analytics, reports, executive and investor dashboards in one React application. | Converts platform telemetry into management visibility without a separate BI purchase. |
| **O-5** | **Encode Indian regulatory and domain knowledge as a first-class, retrievable asset.** Knowledge graph plus RAG over regulations, parts, HSN codes, workflows and certifications. | Indian EV/automotive compliance (GST/HSN, DISCOM interconnection, certification regimes) is the hardest part to replicate and the highest-value context to inject into every AI answer. |
| **O-6** | **Reduce time-to-market for new AI features across the portfolio.** A new capability equals a new platform service module scaffolded from the shared `build_app()` factory. | A standard service contract (`/health`, `/`, `/metrics`, `/docs`, typed errors) makes each new capability predictable to build, test and operate. |
| **O-7** | **Establish an operationally credible platform** — health endpoints, Prometheus metrics, structured JSON logging, request IDs, CI, backups. | Internal platforms that other products depend on become a single point of failure; operational maturity is a business requirement, not a technical nicety. |
| **O-8** | **Build toward an externally licensable Automobile-LLM.** | The only element of the stack with standalone commercial value to OEMs and DISCOMs. |

### 3.3 Strategic fit summary

Kailash is the "horizontal" in a portfolio of "verticals." Its business value is realised indirectly — through the margin, speed and differentiation it confers on URGAA, GSTSAAS, Ignition and ARJUN — plus one direct future revenue line (Automobile-LLM licensing). Consequently its KPIs are largely internal-adoption and reliability KPIs rather than revenue KPIs, with the explicit exception of the Automobile-LLM roadmap.

---

## 4. Target Users / Personas / Stakeholders

### 4.1 Primary personas (direct users of the Kailash web dashboard)

| Persona | Description | Needs from Kailash | Representative surface |
|---|---|---|---|
| **Platform / AI engineer** | Go4Garage engineer building and maintaining Kailash's departments, guardians and platform services. | Local dev loop (`make install/lint/test/up`), OpenAPI docs at `/docs`, structured logs with request IDs, service scaffolding scripts, CI feedback. | `/docs`, `/metrics`, repo tooling |
| **Consumer-product engineer** | Engineer on URGAA / GSTSAAS / Ignition / ARJUN integrating AI capability. | A stable, documented, token-authenticated REST contract reachable via a base-URL environment variable (the `KAILASH_AI_URL` pattern); consistent `ApiResponse` envelopes; predictable error codes. | Backend REST API |
| **Operations manager** | Runs day-to-day Go4Garage operations. | Department status, task management, GAPS/task CRUD, activity feed, alerts. | `/departments`, `/tasks`, `/management` |
| **Business analyst** | Turns platform telemetry into decisions. | Analytics, reports, GANESHA analytics, knowledge base browsing. | `/analytics`, `/reports`, `/ganesha-analytics`, `/knowledge-base` |
| **Executive / leadership** | Go4Garage leadership and board-facing users. | Executive dashboard, investor-facing rollups, portfolio-level health. | `/dashboard/executive`, investor executive dashboard |
| **Security / compliance officer** | Owns the security and legal posture. | RBAC enforcement, 2FA, audit trail, incident response, the published policy pages. | `/compliance`, `/security-policy`, `/transparency`, RBAC admin |
| **Domain SME (automotive/EV)** | Curates automotive and regulatory knowledge. | Knowledge base ingestion, RAG upload, daily-digest review, knowledge-graph curation. | `/knowledge-base`, `database/rag_upload_script.py` |

### 4.2 Consuming systems (machine "users")

| System | Relationship to Kailash |
|---|---|
| **URGAA** | Certification and SLA intelligence — consumes document-ai, anomaly, forecasting. |
| **GSTSAAS** | Invoice/fraud/voice intelligence — consumes document-ai, anomaly, speech, automobile-llm. |
| **Ignition** | Charger trust and RC verification — consumes vision-gateway, knowledge-graph, anomaly. |
| **ARJUN / ev-vidya-arjun** | ID proofing and speech — integrates against the Kailash backend base URL via a `KAILASH_AI_URL`-style environment variable. |
| **Kailash Dashboard (frontend)** | The platform's own React 19 operations cockpit. |

### 4.3 Stakeholder map

| Stakeholder | Interest | Influence |
|---|---|---|
| Go4Garage founders / leadership | Moat creation, portfolio velocity, investor narrative | High |
| Kailash AI Team (platform engineering) | Architecture, reliability, delivery | High |
| Consumer product leads | Contract stability, latency, uptime | High |
| Finance | AI vendor spend, VPS/hosting cost | Medium |
| Legal / Compliance | Data residency, DPDP-style obligations, licensing terms | Medium–High |
| Prospective OEM / DISCOM licensees (future) | Automobile-LLM capability and evaluation evidence | Low today, high in the long term |

---

## 5. Scope

### 5.1 In scope

- **Unified internal AI backend** exposing REST endpoints for authentication, departments, tasks, analytics, dashboard, conversations, knowledge, RBAC, users, guardians, system health, scheduling and automobile-domain capabilities.
- **Twenty department AI agents** registered in `backend/app/departments/registry.py`, each with its own domain behaviour and knowledge slice.
- **Three guardian agents** — GANESHA (orchestrator; v1, multimodel, orchestrator and v2 variants exist), SHIV (security and auto-rectification), PARVATI (workload).
- **Nine platform AI services** as internal modules under `backend/services/`: document-ai, forecasting, anomaly, rag, vision-gateway, speech, model-registry, knowledge-graph, automobile-llm.
- **Automobile domain module** (`backend/app/automobile/`) covering GST integration, market data, and a pricing engine, surfaced through its own router.
- **Knowledge / RAG layer** — `backend/knowledge/` (config manifest, pre-data, post-data daily digests per department) plus RAG services and the `database/rag_upload_script.py` ingestion path.
- **React 19 web dashboard** with roughly 21 authenticated application routes and roughly 35 legal/compliance/policy pages.
- **Identity, authorisation and account security** — JWT sessions, bcrypt password hashing, TOTP-based 2FA fields with backup codes, a five-tier role model (super_admin, admin, manager, operator, viewer) and granular permission strings.
- **MongoDB data platform operations** — initialisation, index creation, seeding, health checks, scheduled backups.
- **Deployment tooling** — Dockerfile, Docker Compose (backend plus MongoDB 7, PostgreSQL 16, Redis 7), Vultr VPS setup/deploy scripts, Nginx reverse-proxy configuration with rate limiting and TLS, and Firebase Hosting configuration for the frontend.
- **CI pipeline** — lint, shared-library tests, a nine-way platform-service test matrix, backend smoke tests, frontend build, and a Compose build sanity check.
- **Scheduled/background work** — Celery and APScheduler wiring, plus a daily-learning task.

### 5.2 Out of scope

- **Any externally sold, customer-facing SaaS product.** Kailash is internal; the README states this explicitly.
- **Native mobile applications for Kailash.** No iOS or Android client exists or is planned for Kailash itself; the platform is backend/web-only. (See the iOS and Android BRDs listed in the Appendix, which record this position formally.)
- **End-customer billing, subscription management or payment collection inside Kailash.** Monetisation lives in the consumer products; Kailash carries no payment gateway.
- **Replacement of the consumer products' own domain logic.** Kailash provides AI capability, not URGAA's certification workflow or GSTSAAS's filing logic.
- **Training foundation models from scratch.** The stated path is fine-tuning existing open-weights models, not pre-training.
- **Public self-service signup.** Access is provisioned to Go4Garage staff and internal services only.
- **Real-time vehicle telematics ingestion / IoT device management.** Not present in this codebase.
- **On-premise customer installations.** Deployment targets are Go4Garage-controlled cloud infrastructure.

---

## 6. Business Requirements

> Each requirement is written to be independently verifiable. "Verification" indicates the evidence that would satisfy an auditor or QA reviewer.

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| **BR-1** | Kailash **shall expose one authenticated internal API surface** that every Go4Garage consumer product integrates against using a single documented base-URL environment variable (the `KAILASH_AI_URL` pattern), such that no consumer product ever holds an AI vendor API key of its own. | Must | Inspect each consumer product's configuration; confirm zero occurrences of `OPENROUTER_API_KEY`/`ANTHROPIC_API_KEY` outside Kailash, and one base-URL variable pointing at Kailash. |
| **BR-2** | Every Kailash API response **shall use a single consistent envelope** — success responses carry the `ApiResponse` shape, and failures carry `{ ok: false, error: { code, message, hint }, request_id }` with a stable machine-readable `code`. | Must | Contract test hitting at least one success and one failure path per router; assert schema conformance and presence of `request_id`. |
| **BR-3** | Kailash **shall authenticate human users with email plus password and optional TOTP two-factor authentication**, issuing time-limited session tokens, and **shall authenticate internal service callers with a separate shared platform token** (`X-Platform-Token`) that is distinct from human credentials. | Must | Attempt each of: valid login, wrong password, 2FA-enabled login without OTP, service call with and without the platform token. Only the correct paths succeed. |
| **BR-4** | Kailash **shall enforce role-based access control** across at least five roles (super_admin, admin, manager, operator, viewer) using granular named permissions covering departments, guardians, users, analytics, pricing, market data, job cards, settings and tasks — such that a `viewer` cannot invoke a department, manage users, or change settings. | Must | Matrix test: for each role, attempt one allowed and one forbidden operation per permission family; forbidden operations return an authorisation error, never data. |
| **BR-5** | Kailash **shall provide at least nine distinct AI capability services** — document understanding, forecasting, anomaly detection, retrieval-augmented generation, vision routing, speech (ASR/TTS with Indic locales), model registry, knowledge graph and automobile-domain chat — each independently callable, independently testable, and each exposing `/health`, `/`, `/metrics` and `/docs`. | Must | Enumerate `backend/services/`; for each, run its test suite and curl its four standard endpoints. |
| **BR-6** | Kailash **shall provide a department-agent model of at least twenty named domain departments**, discoverable through a registry, individually addressable via the API, and individually viewable in the dashboard. | Must | `GET` the departments list endpoint and confirm the registry count matches `DEPARTMENT_CLASSES`; open `/department/:name` in the dashboard for each. |
| **BR-7** | Kailash **shall orchestrate multi-department work through a guardian layer** — GANESHA routing a user request to the correct department(s) and composing a response; SHIV applying security checks and auto-rectification; PARVATI managing workload — with the routing decision recorded for each request. | Must | Submit a request that plausibly spans two departments; confirm the response records which department(s) were engaged and that a corresponding activity/conversation record is persisted. |
| **BR-8** | Kailash **shall ground AI answers in a maintained knowledge layer** — a curated knowledge base plus retrieval over ingested documents and dated department digests — and **shall allow a domain SME to add new knowledge without a code deployment**. | Must | Upload a new document via the RAG ingestion path; ask a question answerable only from that document; confirm the answer reflects it and the knowledge base view lists it. |
| **BR-9** | Kailash **shall degrade gracefully when an upstream AI provider is unavailable**, following a defined provider order (OpenRouter, then Anthropic, then a non-LLM keyword fallback) and returning a typed upstream error rather than a generic 500 when all options are exhausted. | Must | Simulate provider failure (invalid key / network block) at each tier; confirm the documented fallback order is followed and the final failure returns the `UpstreamError` envelope. |
| **BR-10** | Kailash **shall give Go4Garage leadership an operations and executive view** covering department status, task and GAPS progress, activity history, analytics and reports, accessible from a browser without engineering assistance. | Must | Log in as an executive-role user and reach the executive dashboard, analytics and reports pages with populated data. |
| **BR-11** | Kailash **shall protect operational data with automated backups and a health-check regime for its primary datastore**, including scheduled MongoDB backups and a documented restore path. | Must | Execute the backup script, then restore into a scratch database and verify collection counts and indexes match. |
| **BR-12** | Kailash **shall support automobile-domain commercial logic** — pricing computation, market data, and GST integration for automotive line items — sufficient for consumer products to obtain a priced, tax-aware answer for a vehicle/part scenario. | Should | Call the automobile router with a representative part/vehicle payload; confirm a priced response with an HSN/GST treatment is returned. |
| **BR-13** | Kailash **shall publish and maintain its legal, privacy, security and compliance position** through in-product policy pages (privacy, terms, GDPR, CCPA, data retention, data breach, data transfer, sub-processors, user rights, SLA, accessibility, transparency, security policy, incident response, bug bounty). | Should | Navigate each documented policy route; confirm each renders substantive content and is dated and owned. |
| **BR-14** | Kailash **shall be reproducibly buildable and deployable by a single engineer** from a clean machine using documented commands, with configuration supplied entirely through environment variables and **no secret committed to version control**. | Must | On a clean checkout: copy `.env.example` to `.env`, run the documented Docker Compose command, and reach a passing health check. Run a secret scan across history; expect zero real credentials. |
| **BR-15** | Kailash **shall gate every change through automated CI** covering lint, shared-library tests, per-service tests, backend smoke tests, frontend build and container build, such that a change failing any gate cannot be merged to the main branch. | Must | Open a pull request with a deliberate lint error and a deliberate test failure; confirm CI blocks it. |
| **BR-16** | Kailash **shall record an auditable trail of who did what** — user identity, role, department invoked, task changes and system activity — retained per the published data-retention policy. | Should | Perform a privileged action; confirm a corresponding activity record exists with actor, timestamp and target. |
| **BR-17** | Kailash **shall advance the Automobile-LLM from a prompt-pinned vendor wrapper toward an owned fine-tuned model**, with each stage evidenced by a model registry entry and a recorded evaluation result before promotion. | Should | Inspect the model registry for a versioned entry per stage with an attached evaluation record; no promotion without one. |
| **BR-18** | Kailash **shall keep Indian regulatory context (GST/HSN treatment, certification regimes, DISCOM-relevant rules) in a maintained, queryable knowledge structure**, so that consumer products inherit compliance context rather than re-deriving it. | Should | Query the knowledge graph for HSN, regulation and certification node types; confirm non-empty, dated content and traversal to related nodes. |
| **BR-19** | Kailash **shall remain deployable to Go4Garage-controlled infrastructure in India-appropriate regions** with TLS termination, rate limiting on public entry points, and no direct public exposure of the application port. | Must | Confirm the reverse proxy binds TLS and rate limits, and that the backend port is bound to loopback only, not `0.0.0.0`. |
| **BR-20** | Kailash **shall document its integration contract sufficiently for a new consumer product to integrate without direct platform-team involvement**, including endpoint reference, auth headers, error codes and environment variables. | Should | An engineer unfamiliar with Kailash completes a first authenticated call using only `docs/` and `/docs`, within one working day. |

---

## 7. Success Metrics / KPIs

### 7.1 Adoption and leverage

| KPI | Definition | Target (first 12 months) |
|---|---|---|
| Consumer products integrated | Distinct Go4Garage products making authenticated Kailash calls in production | 4 of 4 (URGAA, GSTSAAS, Ignition, ARJUN) |
| AI-capability duplication | Count of AI vendor SDK integrations living outside Kailash across the portfolio | 0 |
| Time-to-first-call for a new consumer | Elapsed working days from "product wants Kailash" to first successful authenticated call | 1 day or less |
| Platform services in active use | Of the nine platform services, how many receive production traffic | 6 or more |
| Departments exercised | Of the registered departments, how many are invoked at least weekly | 12 or more |

### 7.2 Reliability and performance

| KPI | Definition | Target |
|---|---|---|
| Backend availability | Successful `/api/health` probes divided by total probes, monthly | 99.5% or better |
| Non-LLM API p95 latency | 95th percentile server-side response time for endpoints not calling an upstream model | 500 ms or less |
| LLM-backed p95 latency | 95th percentile end-to-end time for department/guardian chat responses | 8 s or less |
| Upstream failure containment | Share of upstream provider failures that return a typed error or fallback rather than an unhandled 500 | 99% or better |
| Backup success rate | Successful scheduled MongoDB backups divided by scheduled runs | 100% |
| Restore drill | Documented restore exercise completed and timed | 1 or more per quarter, RTO 4 h or less |

### 7.3 Quality and delivery

| KPI | Definition | Target |
|---|---|---|
| CI pass rate on main | Green pipeline runs divided by total runs on the default branch | 95% or better |
| Automated test count | Total tests across shared, platform services, backend and integration suites | Growing quarter on quarter; no suite permanently skipped |
| Lint debt | `ruff check` violations on `backend/` | 0 |
| Mean time to restore service | Incident detection to service restoration | 2 h or less |
| Change failure rate | Deployments requiring rollback or hotfix within 24 h | 10% or less |

### 7.4 Moat and knowledge

| KPI | Definition | Target |
|---|---|---|
| Knowledge corpus size | Documents/nodes in the RAG index and knowledge graph | Growing monthly; at least 1 curated ingest per week |
| Digest freshness | Age of the newest department daily-digest payload | 7 days or less |
| Grounded-answer rate | Share of automobile-domain answers citing at least one retrieved knowledge item | 70% or better |
| Registered model versions | Versioned entries in the model registry with attached evaluations | 1 or more per Automobile-LLM stage |
| Automobile-LLM eval score | Accuracy on a held-out automotive/EV regulatory Q&A set | Baseline established, then monotonic improvement per stage |

### 7.5 Security and compliance

| KPI | Definition | Target |
|---|---|---|
| Committed secrets | Real credentials found in version control by automated scanning | 0 |
| 2FA coverage | Privileged users (super_admin, admin) with TOTP enabled | 100% |
| RBAC violations | Successful requests by a role lacking the required permission | 0 |
| Policy page currency | Published policy pages reviewed within the last 12 months | 100% |
| Open critical vulnerabilities | Unremediated critical findings older than the SLA in `SECURITY.md` | 0 |

---

## 8. Assumptions & Constraints

### 8.1 Assumptions

| # | Assumption | If false |
|---|---|---|
| A-1 | Kailash remains internal-only and is never sold directly to end customers. | The security model, tenancy model and commercial terms would all need redesign. |
| A-2 | Consumer products are willing to depend on a shared platform and accept its release cadence. | Teams re-implement AI locally and the moat fragments (defeating O-3). |
| A-3 | Third-party model access (OpenRouter, Anthropic, Google) stays commercially available at workable prices. | The fine-tuning roadmap becomes urgent rather than strategic. |
| A-4 | MongoDB remains the primary operational store, with PostgreSQL and Redis in supporting roles. | Data-model and backup requirements change materially. |
| A-5 | Go4Garage staff access Kailash from desktop browsers on trusted networks. | A mobile client and a stronger untrusted-network posture become necessary. |
| A-6 | Indian data-residency expectations can be satisfied by Go4Garage-controlled hosting choices. | Region-specific deployment obligations must be added. |
| A-7 | Domain SMEs are available to curate the knowledge layer on an ongoing cadence. | Grounded-answer quality degrades and the knowledge KPIs miss. |
| A-8 | The deity-department metaphor remains acceptable as an internal organising model. | A renaming exercise is required across code, API and UI. |

### 8.2 Constraints

| # | Constraint | Nature |
|---|---|---|
| C-1 | Proprietary licence — the codebase cannot be open-sourced or shared externally without approval. | Legal |
| C-2 | No secrets in version control; every module ships a `.env.example` and real values are supplied at deploy time. | Policy (`SECURITY.md`) |
| C-3 | Backend is Python 3.11 / FastAPI; frontend is React 19 built through CRA plus CRACO. Substituting either is a major undertaking. | Technical |
| C-4 | Single-VPS deployment shape (Vultr, Nginx, Docker Compose) caps horizontal scale until orchestration is introduced. | Infrastructure |
| C-5 | Small platform team — scope must favour depth on the shared engine over breadth of new surfaces. | Resource |
| C-6 | Upstream model rate limits, token costs and latency bound what the platform can promise. | Vendor |
| C-7 | Compliance surface spans GST/HSN treatment, DISCOM-adjacent obligations for charger/energy data, and Indian personal-data expectations. | Regulatory |
| C-8 | Kailash is a shared dependency: an outage affects the whole portfolio simultaneously. Change management must reflect blast radius. | Operational |

---

## 9. Risks & Mitigations

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | **Single point of failure** — a Kailash outage takes down AI features in every consumer product at once. | Medium | High | Health checks on every service, restart policies in Compose, documented fallbacks in consumers, and a defined incident-response path; medium-term move to redundant instances behind a load balancer. |
| R-2 | **AI vendor dependency** — pricing, availability or terms change unfavourably at OpenRouter/Anthropic/Google. | High | High | Provider chain with documented precedence and a non-LLM keyword fallback; model registry to make swaps auditable; fine-tuning roadmap to reduce dependence over time. |
| R-3 | **Automobile-LLM moat never materialises** — the wrapper is never replaced by an owned model. | Medium | High | Stage-gate the roadmap with registry entries and evaluations (BR-17); treat "no eval, no promotion" as a hard rule; assign a named owner for the moat programme. |
| R-4 | **Knowledge layer decays** — digests go stale, retrieval quality drops, answers become ungrounded. | Medium | Medium | Digest-freshness KPI (7 days or less), weekly SME curation cadence, grounded-answer-rate monitoring. |
| R-5 | **Secret leakage** — an API key or service-account JSON is committed or logged. | Medium | High | `.gitignore` coverage for `.env`, pre-commit hooks, `SECURITY.md` playbook, automated secret scanning in CI, key rotation runbook. |
| R-6 | **Datastore permission/config drift in production** (for example an Atlas user without `readWrite` on the application database) silently breaks authentication. | Medium | High | Startup permission validation with explicit, actionable log output; promote it from warning to hard-fail in production; add a synthetic login probe to monitoring. |
| R-7 | **Scale ceiling** — a single VPS cannot absorb portfolio-wide growth. | Medium | Medium | Capacity monitoring via `/metrics`; documented vertical-scale path; plan container orchestration before sustained utilisation exceeds 60%. |
| R-8 | **Key-person concentration** — deep platform knowledge held by very few engineers. | High | High | Enforce README/ARCHITECTURE currency, keep `docs/` authoritative, pair on incidents, record runbooks for backup/restore/deploy. |
| R-9 | **Documentation/code drift** — published counts and claims diverge from the registry (for example department counts, test counts). | High | Low | Generate counts from the registry at build time; add a CI check that asserts documented counts match code. |
| R-10 | **Regulatory change** in GST/HSN treatment or EV/DISCOM rules invalidates encoded knowledge. | Medium | Medium | Version knowledge entries with effective dates; subscribe SMEs to regulatory sources listed in the API-source manifest; re-validate quarterly. |
| R-11 | **Over-broad CORS or permissive defaults** carried from development into production. | Medium | High | Environment-driven allowed-origins list; production configuration review as a deploy gate; security headers enforced at the proxy and hosting layers. |
| R-12 | **Cost overrun on model spend** as usage grows across four products. | Medium | Medium | Per-product usage attribution, token accounting in metrics, tiered model routing (cheap model first, escalate only when needed). |
| R-13 | **Data-residency challenge** — personal or commercially sensitive Indian data processed by offshore model providers. | Medium | High | Minimise and redact payloads sent upstream; document sub-processors publicly; prioritise in-region or self-hosted inference for sensitive classes. |
| R-14 | **Repository/remote ambiguity** — deploy tooling and README reference a different GitHub remote than the one configured locally, risking a deploy from the wrong source. | Medium | Medium | Reconcile the remote in `README.md`, `deploy/vultr/deploy.sh` and the local Git configuration to a single canonical URL before the next production deploy. |

---

## 10. Current Implementation Status

*Assessed 2026-07-31 against the working copy at `C:\Go4Garage( Eka)\Kailash-Ai`, HEAD `40cca17`.*

### 10.1 Built and present on disk

| Area | Status | Evidence |
|---|---|---|
| FastAPI backend application | **Built** | `backend/app/main.py` with lifespan startup, CORS, security and error middleware, and roughly 24 API router modules under `backend/app/api/`. |
| Department agents | **Built** | 20 department classes registered in `backend/app/departments/registry.py`. |
| Guardian agents | **Built** | `backend/app/guardians/{ganesha,shiv,parvati}.py`, plus `api/ganesha.py`, `ganesha_multimodel.py`, `ganesha_orchestrator.py`, `ganesha_v2.py`, `shiv_auto_rectify.py`. |
| Nine platform AI services | **Built (varying depth)** | `backend/services/{document-ai,forecasting,anomaly,rag,vision-gateway,speech,model-registry,knowledge-graph,automobile-llm}`, each with its own `.env.example`. |
| Knowledge / RAG layer | **Built, partially populated** | `backend/knowledge/config/api_sources.json`, `pre-data/`, `post-data/daily-digest/` with dated per-department JSON; `app/services/rag_service.py` and `rag_knowledge_base.py`; `database/rag_upload_script.py`. |
| Automobile domain module | **Built** | `backend/app/automobile/{gst_integration,market_data,pricing_engine,router}.py`. |
| Auth, RBAC, 2FA | **Built** | JWT settings in `core/config.py`; 5 roles and granular permissions in `core/rbac.py`; `totp_secret`, `is_2fa_enabled`, `backup_codes` on the user model. |
| React 19 frontend | **Built and compiled** | `frontend/src/pages/` with roughly 70 page modules; `frontend/build/` contains compiled `static/`, `index.html`, brand video and OG assets; `node_modules/` populated (roughly 1,000 entries). |
| MongoDB operations tooling | **Built** | `database/{mongodb_init.js,seed_data.py,populate_department_data.py,backup_mongodb.py,mongodb_backup.sh,mongodb_health_check.sh}`. |
| Containerisation | **Built** | `Dockerfile` (python:3.11-slim, non-root `appuser`) and `docker-compose.yml` (backend, mongo:7, postgres:16-alpine, redis:7-alpine, all with healthchecks). |
| VPS deploy tooling | **Built (scripts exist)** | `deploy/vultr/{setup-vps.sh,deploy.sh,nginx-api.conf}`, `deploy/docker/{docker-compose.prod.yml,docker-compose.platform.yml,nginx.conf}`. |
| Firebase Hosting config | **Built** | `frontend/firebase.json` with SPA rewrite, immutable static caching and security headers; project `kailash-38268` referenced in `backend/.env.example`. |
| CI pipeline | **Built** | `.github/workflows/{ci.yml,deploy-backend.yml,deploy-frontend.yml}`; `ci.yml` defines `lint`, `shared`, `services`, `backend`, `frontend`, `compose-build` jobs. |
| Test suites | **Built** | `tests/{platform,backend,integration,scripts}/` with pytest suites plus ad-hoc scripts. |
| Developer tooling | **Built** | `Makefile`, `ruff.toml`, `.pre-commit-config.yaml`, `.editorconfig`, `.devcontainer/`, `scripts/{generate_services.ps1,health_check.sh}`. |
| Local build evidence | **Confirmed** | `backend/.venv/` present with `Lib/`, `Scripts/`, `pyvenv.cfg`; frontend `build/` and `node_modules/` present — the stack has been installed and run locally. |
| Documentation set | **Built** | `README.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`, and a substantial `docs/` tree (architecture, api, guides, business, archived). |

### 10.2 Partial, aspirational, or not yet verified

| Area | Honest status |
|---|---|
| **Automobile-LLM as a moat** | The service exists, but the README itself describes the current implementation as an OpenRouter wrapper with a pinned domain system prompt. No fine-tuned Go4Garage-owned model exists on disk. Stages 2 to 4 of the moat roadmap are aspiration, not delivery. |
| **Production deployment** | Deployment *tooling* is present and credible; this working copy contains **no evidence of a currently live production environment**. Domains (`kailash-ai.in`, `api.kailash-ai.in`) and a Firebase project ID are configured in `.env.example`, but running-service status was not verified from this copy. |
| **Consumer-product integrations** | The `KAILASH_AI_URL`-style contract is the specified integration pattern for ARJUN / `ev-vidya-arjun`. In this workspace, the `ev-vidya-arjun` directory currently contains only empty platform scaffolding folders, so the integration is **specified but not evidenced in code here**. URGAA and GSTSAAS integrations were likewise not confirmed from this copy. |
| **Department count** | `README.md` and `ARCHITECTURE.md` refer to "24 AI departments"; the registry (`DEPARTMENT_CLASSES`) actually registers **20**. Additional deity names (marut, pragya, rudra, tvashta) appear in knowledge digest payloads without corresponding department classes. This is a documentation/code drift to reconcile. |
| **Test counts** | The README publishes a table (5 shared, 53 service, 10+ backend, 3+ integration tests). Suite files are present; the exact current counts were not re-executed as part of this assessment. |
| **Speech service** | Described in the README as provider-agnostic stubs with Indic locales — that is, the interface exists ahead of a production ASR/TTS provider binding. |
| **Knowledge graph and RAG index** | Documented as in-memory structures (typed graph with BFS lookup; cosine index with a SHA-256 hash embedding fallback). Durable, vector-database-backed retrieval is optional (`PINECONE_*` variables exist but are blank in the template) and not evidenced as active. |
| **PostgreSQL usage** | `postgres_models.py`, `asyncpg` and a Postgres container are present; MongoDB remains the primary described store. The precise split of responsibilities is not fully documented. |
| **Git remote consistency** | ~~Resolved~~ — `urgaa-eka/kailash` confirmed canonical; all `README.md` badges, `deploy/vultr/*.sh` and `docs/DEPLOYMENT.md` references updated to match `origin`. |
| **Mobile clients** | **None exist.** `ios_app_kailash_ai/` and `android_app_kailash_ai/` contain only empty `deployed/` and `not_deployed/` placeholder directories. |

### 10.3 Summary judgement

Kailash is a **substantially built, locally-running internal platform with production-grade scaffolding and an unproven production footprint**. The engineering foundations — shared library, service contract, RBAC, CI matrix, containerisation, backup tooling — are real and unusually mature for an internal tool. The gap between the platform as documented and the platform as deployed sits in three places: live production evidence, consumer-product integration evidence, and the Automobile-LLM moat itself.

---

## 11. Roadmap / Milestones

### 11.1 Near term (0 to 3 months) — *make what exists trustworthy*

| # | Milestone | Success criterion |
|---|---|---|
| N-1 | **Reconcile documentation with code.** Fix the 20-versus-24 department count, refresh test counts, and unify the Git remote across README, deploy script and local config. | CI check asserts documented counts equal registry counts; one canonical remote. |
| N-2 | **Verify and record the production footprint.** Confirm whether `api.kailash-ai.in` and the Firebase-hosted frontend are live; document the deployed commit. | A dated deployment record exists naming environment, commit and owner. |
| N-3 | **Harden production configuration.** Replace wildcard CORS with the explicit allowed-origins list, enforce a non-default `SECRET_KEY`, and promote the datastore permission check from warning to hard-fail in production. | Production start-up fails fast on any misconfiguration. |
| N-4 | **Prove backup and restore.** Execute a full restore drill from a scheduled backup into a scratch environment. | Documented RTO/RPO with evidence. |
| N-5 | **Stand up observability.** Scrape `/metrics`, alert on health-probe failure, error rate and upstream failure rate. | Alerts fire in a deliberate failure test. |
| N-6 | **Publish the integration contract.** A single guide covering base URL, headers, error codes and a worked example for a consumer product. | A new engineer completes a first authenticated call in 1 day or less. |

### 11.2 Mid term (3 to 9 months) — *make it the portfolio default*

| # | Milestone | Success criterion |
|---|---|---|
| M-1 | **Integrate all four consumer products** (URGAA, GSTSAAS, Ignition, ARJUN) against Kailash in production. | Four products with production traffic; zero AI vendor keys outside Kailash. |
| M-2 | **Durable retrieval.** Move RAG from in-memory cosine to a persistent vector store; version knowledge entries with effective dates. | Retrieval survives restart; grounded-answer rate 70% or better. |
| M-3 | **Per-product usage attribution and cost control.** Token and request accounting by caller, with tiered model routing. | Monthly cost report by product; measurable reduction in cost per grounded answer. |
| M-4 | **Speech to production.** Bind a real ASR/TTS provider with Indic locale coverage, replacing stubs. | Measured word-error-rate baseline on Indian-language automotive audio. |
| M-5 | **Model registry discipline.** Every model change recorded with an evaluation before promotion. | No un-evaluated model reaches production. |
| M-6 | **Scale path.** Introduce redundant backend instances behind a load balancer, or container orchestration. | No single-instance dependency for the backend tier. |
| M-7 | **Formal compliance posture.** Document data flows, sub-processors, retention and residency decisions for GST-adjacent, DISCOM-adjacent and personal data. | Signed-off data-protection record; policy pages reviewed and dated. |

### 11.3 Long term (9 to 24 months) — *build the moat*

| # | Milestone | Success criterion |
|---|---|---|
| L-1 | **Automobile-LLM v1 fine-tune.** Fine-tune an open-weights base model on automotive regulations and synthetic service-manual Q&A. | Beats the prompt-pinned wrapper baseline on a held-out automotive/EV eval set. |
| L-2 | **Compounding data loop.** Continuously fine-tune on anonymised, consented operational data from the four consumer products. | Documented anonymisation pipeline; measurable eval improvement per cycle. |
| L-3 | **Automotive knowledge graph at depth.** Regulations, parts, HSN codes, workflows and certifications curated to production quality with traceable sources. | Answers cite graph nodes with source and effective date. |
| L-4 | **Automobile-LLM as a licensable product.** Package the model with an API, evaluation evidence and commercial terms for OEMs and DISCOMs. | First external evaluation engagement or licence. |
| L-5 | **Portfolio-wide AI governance.** Centralised prompt/model versioning, red-teaming, bias and safety evaluation across all products. | Governance review completed for every production model. |

---

## 12. Appendix

### 12.1 Sibling documents

This product-level BRD is one of eight documents in the Kailash-Ai documentation set. Its companion technical document is **`TRD_kailash_ai.md`** (product level, same directory).

The application-level documents are:

| # | Document | Location relative to product root | Surface |
|---|---|---|---|
| 1 | `BRD_web_app_kailash_ai.md` | `web_app_kailash_ai/` | Web application — business requirements |
| 2 | `TRD_web_app_kailash_ai.md` | `web_app_kailash_ai/` | Web application — technical requirements |
| 3 | `BRD_ios_app_kailash_ai.md` | `ios_app_kailash_ai/` | iOS application — business requirements (records that no iOS client exists) |
| 4 | `TRD_ios_app_kailash_ai.md` | `ios_app_kailash_ai/` | iOS application — technical requirements (conditional design for a client not yet built) |
| 5 | `BRD_android_app_kailash_ai.md` | `android_app_kailash_ai/` | Android application — business requirements (records that no Android client exists) |
| 6 | `TRD_android_app_kailash_ai.md` | `android_app_kailash_ai/` | Android application — technical requirements (conditional design for a client not yet built) |

### 12.2 Glossary

| Term | Meaning |
|---|---|
| **Department** | A named domain AI agent inside Kailash (deity-named, for example LAKSHMI, VISHWAKARMA), registered in `backend/app/departments/registry.py`. |
| **Guardian** | A supervisory agent above the departments: GANESHA (orchestration), SHIV (security/auto-rectify), PARVATI (workload). |
| **Platform service** | One of the nine internal capability modules under `backend/services/`. |
| **`ApiResponse` envelope** | The standard success/error response wrapper returned by all Kailash endpoints. |
| **Internal platform token** | The `X-Platform-Token` shared secret used for service-to-service authentication. |
| **`KAILASH_AI_URL`** | The environment-variable convention by which a consumer product locates the Kailash backend base URL. |
| **Automobile-LLM** | The automotive-domain language capability identified as Kailash's commercial moat. |
| **RAG** | Retrieval-augmented generation — grounding model answers in retrieved knowledge. |
| **Daily digest** | Dated per-department JSON knowledge payloads under `backend/knowledge/post-data/daily-digest/`. |
| **DISCOM** | Electricity distribution company — relevant to EV charging and energy-related obligations in India. |
| **HSN** | Harmonised System of Nomenclature — goods classification codes underpinning GST treatment. |

### 12.3 Consumer products referenced

| Product | Role in the portfolio |
|---|---|
| URGAA | Certifications and SLA intelligence |
| GSTSAAS | Invoices, fraud detection, voice |
| Ignition | Charger trust, RC verification |
| ARJUN / ev-vidya-arjun | ID proofing, speech, EV education |
| Kailash Dashboard | The platform's own operations cockpit |

### 12.4 Open questions for the document owner

1. Who is the accountable owner for Kailash as a platform, and who owns the Automobile-LLM moat programme specifically?
2. Is `api.kailash-ai.in` live today, and against which commit?
3. ~~Which Git remote is canonical?~~ Resolved: `urgaa-eka/kailash` (matches `origin`); all references updated.
4. Should the department count be corrected to 20, or should four additional departments be implemented to match the documented 24?
5. What is the agreed data-residency position for payloads sent to offshore model providers?
6. Is there any scenario in which Kailash would be exposed to parties outside Go4Garage, and if so under what commercial and security terms?
