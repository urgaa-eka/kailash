# Kailash — Business Requirements Document (BRD)

> **Single source of truth.** This is the one and only BRD for the entire
> Kailash project (RULES.md Rule 3). It consolidates the former company-wide BRD
> and the per-platform (Android / iOS / Web) BRDs into one document, organised as
> sections. Do not create separate or duplicate BRD files — edit this one.

---

## 0. Vision & Canonical Framing (Center Lake)

> This section is the **authoritative present-day frame**; the detailed sections
> below remain the grounded, repo-accurate record and are read through it. The
> product north-star is [`PRD.md`](./PRD.md).

**Kailash is the central data lake and command center** for the whole Eka
software ecosystem — the single nexus every component, product, and process
routes through and is monitored in real time. In the **Center Lake** model,
**Kailash is the heart** (the data that pumps through the organization) and
**Eka Brain is the mind** (the AI that orchestrates the agent matrix and
answers). All data flows into Kailash first; Kailash then dictates where and to
which agent or interface it is distributed. Kailash is **internal
infrastructure**, not a product sold to customers.

**The data core has four segments** — the canonical organization of Kailash's
data and documentation:

| Segment | Function |
| --- | --- |
| **Product** | The product lines: per-product scope, deployment status, blueprints, live-vs-pending tracking. |
| **Sprint** | Agile cycles + critical financial events: the 18-day sprint artifacts, funding-round records. |
| **Company** | Master operational ledger + statutory financials; the CA-vs-internal reconciliation (the segment that is live today). |
| **Goal** | Forward-looking strategy: missions, milestones, open-ended planning. |

**The command dashboard has three tiers**: Governance & Intelligence (**Eka
Brain**, **Shiv**, **Parvati**) → **Analytics & Telemetry** (FE→API→BE pulse;
green healthy, red isolates the failing layer) → the **Product ecosystem**.

**The six products** (automotive / multi-brand-workshop focus, each AI-driven
via Eka Brain): **Eka AI**, **Website**, **Urja**, **EV Vidya**, **GST SaaS**,
**Ignition**.

**Canonical naming (adopted 2026-08).** The repo adopts the vision names; the
grounded sections below use the legacy names, which map as: **Eka Brain ←
GANESHA orchestrator**; **GST SaaS ← GSTSAAS**; **Urja ← URGAA**; **Company ←
the Go4Garage financials segment**; **Eka AI / EV Vidya ← the automobile-LLM /
`ev-vidya-arjun` surfaces**. Repository structure follows RULES.md
(department → feature) with these names.

**Resource prerequisites (launch checklist).** The Company/financials segment
runs today on Firebase + Supabase (provisioned). Running the full platform
(products + Eka Brain) additionally requires — and these must be supplied before
that phase: an **AI-provider key** (`OPENROUTER_API_KEY`/`ANTHROPIC_API_KEY`), a
**backend host** (`BACKEND_SSH_*`), **MongoDB** (`MONGO_URL`), **Redis**
(`REDIS_URL`), a **Firebase Admin service account**
(`FIREBASE_SERVICE_ACCOUNT_JSON`), and **valid AWS credentials** (Route 53 DNS).

---

## Section 1 — Company / Platform (Kailash)
## 1.1 Business Requirements Document — Kailash-Ai

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

A knowledge/RAG layer (`backend/knowledge/` plus `app/services/rag_service.py` and `rag_knowledge_base.py`) provides retrieval-augmented context to the departments, fed by dated daily-digest JSON payloads and an API-source manifest. A dedicated top-level `database/` folder carries MongoDB initialisation, seeding, health-check, backup and RAG-upload tooling. Deployment tooling exists for Docker (a single-container `Dockerfile` plus a four-service `docker-compose.yml`) and for a managed host behind Nginx with Let's Encrypt TLS, with the frontend targeted at Firebase Hosting (project `kailash-38268`).

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
- **Deployment tooling** — Dockerfile, Docker Compose (backend plus MongoDB 7, PostgreSQL 16, Redis 7), managed host setup/deploy scripts, Nginx reverse-proxy configuration with rate limiting and TLS, and Firebase Hosting configuration for the frontend.
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
| C-4 | Single-VPS deployment shape (managed host, Nginx, Docker Compose) caps horizontal scale until orchestration is introduced. | Infrastructure |
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
| R-14 | **Repository/remote ambiguity** — deploy tooling and README reference a different GitHub remote than the one configured locally, risking a deploy from the wrong source. | Medium | Medium | Reconcile the remote in `README.md`, `deploy/host/deploy.sh` and the local Git configuration to a single canonical URL before the next production deploy. |

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
| VPS deploy tooling | **Built (scripts exist)** | `deploy/host/{setup-vps.sh,deploy.sh,nginx-api.conf}`, `deploy/docker/{docker-compose.prod.yml,docker-compose.platform.yml,nginx.conf}`. |
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
| **Git remote consistency** | ~~Resolved~~ — `urgaa-eka/kailash` confirmed canonical; all `README.md` badges, `deploy/host/*.sh` and `docs/DEPLOYMENT.md` references updated to match `origin`. |
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

---

## Section 2 — Android App
### 2.1 Business Requirements Document — Kailash-Ai Android Application

## 1. Document Control

| Field | Value |
|---|---|
| **Document title** | Business Requirements Document — Kailash-Ai Android Application |
| **Product** | Kailash — Go4Garage internal ML/AI platform |
| **Surface** | Android (phone / tablet native client) |
| **Document type** | BRD (Application level) |
| **Version** | 1.0 |
| **Date** | 2026-07-31 |
| **Status** | Draft |
| **Owner** | TBD |
| **Author** | Go4Garage Documentation Workstream |
| **Reviewers** | TBD (Platform Lead, Mobile Lead if appointed, Security, Compliance) |
| **Approvers** | TBD |
| **Classification** | Internal — Proprietary |
| **Parent product BRD** | `../BRD_kailash_ai.md` |
| **Parent product TRD** | `../TRD_kailash_ai.md` |
| **Companion document** | `TRD_android_app_kailash_ai.md` (same directory) |
| **Source of truth** | `C:\Go4Garage( Eka)\Kailash-Ai\android_app_kailash_ai`, product HEAD commit `40cca17` dated 2026-07-31 |

### 1.1 Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-31 | Documentation Workstream | Initial draft. Records the current no-native-client position and defines conditional requirements should that position be revisited. |

---

## 2. Executive Summary

### 2.1 The headline finding

**There is no Kailash Android application.** No Kotlin, Java, React Native, Expo or Flutter project exists in this repository for Kailash, and none is currently planned. The directory `android_app_kailash_ai/` contains exactly two empty placeholder subdirectories — `deployed/` and `not_deployed/` — and nothing else. There is no Gradle build, no `AndroidManifest.xml`, no application ID, no Play Console record, no signing keystore and no release track.

This is a **deliberate consequence of what Kailash is**, not an oversight. Kailash is Go4Garage's internal ML/AI platform — the shared AI engine behind URGAA, GSTSAAS, Ignition and ARJUN. Its own README states plainly that it is not a product sold to customers. Its human users are Go4Garage staff doing analytical and supervisory work on dense, multi-panel screens: reading dashboards, comparing forecasts, triaging anomalies, curating knowledge, administering roles. That work belongs on a large screen with a keyboard. Kailash is, by design, a **backend and web-only service**.

### 2.2 The Android-specific consideration

There is one argument that applies more strongly to Android than to iOS: **India runs on Android**. Go4Garage is an Indian EV/automotive business, and its staff, field partners and garage network overwhelmingly carry Android devices. If Kailash ever needed a mobile client, Android would almost certainly be the higher-priority platform, not the second one.

That observation strengthens the *ordering* of a hypothetical mobile programme without changing the *decision*. The question is not "which platform first" but "is any mobile client warranted for an internal analytics and orchestration platform." On the evidence in this repository, it is not — and the Android device-diversity problem (thousands of device/OEM/OS-version combinations, aggressive vendor battery management that suppresses background delivery, and a wide performance floor) makes an Android client materially more expensive to build well than the same client on iOS.

### 2.3 What this document is for

A BRD for an application that does not exist has three legitimate jobs, and this document does all three:

1. **Record the position unambiguously**, so no future reader, auditor, investor or new engineer mistakes an empty directory for lost work or an unmet commitment.
2. **State the decision criteria** — what would have to become true for an Android client to be justified.
3. **Pre-specify the business requirements** that would apply *if* that threshold were crossed.

Every numbered requirement in §6 is therefore **conditional**, except BR-AND-0 in §6.1, which is in force today.

### 2.4 The alternative that already exists

Go4Garage staff who need Kailash on an Android device are not without recourse. The Kailash web application (`../web_app_kailash_ai/`) is a responsive React 19 SPA, and Chrome for Android is in its supported browser matrix for read journeys and core actions, with responsive requirements down to 360 px. What Chrome does not provide is an installed app icon, FCM push notifications, offline access, biometric unlock or camera integration. Those are the entirety of what a native Android client would add — and §3.2 assesses whether any of them justifies the cost.

---

## 3. Business Objectives & Strategic Fit

### 3.1 The strategic question

The parent BRD sets out Kailash's objectives: be the single AI engine for the portfolio, insulate product teams from AI vendor churn, accumulate an automotive data moat, provide an operations cockpit, encode Indian regulatory knowledge, reduce AI time-to-market, be operationally credible, and build toward a licensable Automobile-LLM.

An Android client advances **none of them directly**. It is a delivery channel for objective O-4 (the operations cockpit) only, and that objective is already served by the web app. The question is narrow: *is there a class of Kailash work that must happen away from a desk, frequently and urgently enough to justify a second client codebase, a Play Console relationship, a device-fragmentation test matrix and permanent maintenance?*

On the evidence, the answer today is no.

### 3.2 Assessment of candidate justifications

| Candidate justification | Assessment | Verdict |
|---|---|---|
| **India is an Android market, so staff carry Android phones** | True and relevant — but it argues for *platform ordering*, not for building at all. The web app already runs in Chrome for Android. | Ordering argument, not a build argument |
| **Push notifications for anomalies and SLA breaches** | Genuinely useful — but email, SMS or a chat integration delivers the same alert without an app, and Android vendor battery management (Xiaomi, Oppo, Vivo, Samsung) actively suppresses background delivery, making push *less* reliable here than on iOS. | Addressable more cheaply, and harder here |
| **Offline access for field staff** | Kailash data is live platform state; a stale anomaly list is close to useless and potentially misleading. | Not sufficient |
| **Camera capture for document AI** | The strongest technical argument. But this capture need belongs to the *consumer products* (URGAA certifications, GSTSAAS invoices, Ignition RC documents), which have their own mobile surfaces, not to the internal platform. | Belongs to consumer products |
| **Voice input for GANESHA** | The `speech` service exists and Chrome for Android supports the Web Speech API; the web app's Permissions-Policy already allows microphone to `self`. | Addressable on web |
| **Biometric unlock for a privileged internal tool** | Real ergonomics gain — but Android BiometricPrompt has an equivalent in WebAuthn platform authenticators in Chrome. | Addressable on web |
| **Field garage-network staff need Kailash** | If true, this would be decisive. But the garage network is served by the *consumer products*, not by the internal AI platform. No evidence in this repository suggests platform access is needed in the field. | Not evidenced |
| **Cheaper distribution than iOS (no Apple ecosystem cost)** | Partly true — no annual developer fee equivalent, and sideloading or managed Google Play is simpler. But device fragmentation testing costs more than the distribution saving. | Net neutral at best |

### 3.3 Objectives, conditional on a future decision

Were an Android client ever approved, its objectives would be:

| # | Objective |
|---|---|
| **AO-1** | Deliver time-critical platform alerts (anomalies, SLA breaches, guardian escalations) to on-call staff wherever they are — reliably, in spite of Android vendor battery restrictions — with one-tap navigation to context. |
| **AO-2** | Give leadership a genuinely mobile-native read experience of the executive dashboard, designed for a phone rather than reflowed from desktop. |
| **AO-3** | Enable fast triage away from a desk — acknowledge, assign, comment, escalate — on the devices Indian staff actually carry. |
| **AO-4** | Perform acceptably on the mid-range and budget devices common in the Indian market, not merely on flagships. |
| **AO-5** | Do all of the above without forking business logic — the app is a client of the same backend contract, never a second implementation. |

### 3.4 Strategic fit conclusion

An Android client is a **channel investment, not a capability investment**. Kailash's strategic priorities per the parent BRD are the Automobile-LLM moat, consumer-product integration, durable retrieval and production hardening. A mobile client competes for the same scarce engineering attention while advancing none of those. The recommended position is: **do not build; revisit only against the explicit criteria in §11.1 — and if any mobile client is ever built, build Android first.**

---

## 4. Target Users / Personas / Stakeholders

### 4.1 Current position

**There are no Android app users, because there is no Android app.** All Kailash users are web users. Users who access the web app from an Android phone or tablet are served by the responsive web surface documented in `../web_app_kailash_ai/BRD_web_app_kailash_ai.md`.

### 4.2 Prospective personas, conditional on a future decision

| Persona | Mobile need | Would an app help? | Likely device class |
|---|---|---|---|
| **On-call platform engineer** | Receive an alert that Kailash is degraded or a guardian escalated; assess and acknowledge | **Yes** — the one unambiguous native case | Mid to high-end Android |
| **Operations manager (in the field)** | Check department status; reassign an urgent task; see today's anomalies | **Partly** — web covers reading; native improves action speed | Mid-range Android |
| **Executive** | Glance at portfolio health between meetings | **Marginal** — Chrome for Android already renders it | High-end Android or iPhone |
| **Business analyst** | Multi-panel analysis, filtering, export | **No** — desktop work by nature | Desktop |
| **Domain SME** | Curate knowledge, review digests | **No** — long-form reading and editing | Desktop |
| **Administrator** | User and role administration | **No** — and arguably should be blocked on mobile for security | Desktop |
| **Compliance officer / external reviewer** | Read a policy page and cite it | **No** — policy pages are public web URLs by design | Any |

One of seven personas has an unambiguous native need, and that need (alerting) is satisfiable by channels that require no app.

### 4.3 Device profile, conditional

If an Android client were built for an Indian internal user base, the realistic target profile would be:

| Attribute | Expected distribution |
|---|---|
| OEM | Samsung, Xiaomi/Redmi/Poco, Vivo, Oppo/OnePlus, Realme, Motorola, Google Pixel |
| Android version | Predominantly current minus 1 through current minus 4 |
| RAM | 4 GB to 8 GB typical; 3 GB devices present |
| Screen | 5.5-inch to 6.8-inch phones; some 10-inch tablets |
| Connectivity | 4G predominant, 5G growing, intermittent coverage common |
| Vendor customisation | **Aggressive battery management on Xiaomi, Oppo, Vivo and Realme** — the single largest technical risk to notification reliability |

### 4.4 Stakeholders in the decision

| Stakeholder | Interest |
|---|---|
| Go4Garage leadership | Whether the investment is justified against the moat roadmap |
| Platform engineering | Second codebase, second release cadence, contract-drift risk across clients |
| Security / Compliance | Device-level data exposure, MDM posture, sideloading versus managed Play distribution |
| Finance | Mobile engineering capacity, device test matrix, ongoing OS-version maintenance |
| Consumer-product teams | Whether platform mobile effort would be better spent on *their* customer-facing Android apps — which serve the Indian market directly |

---

## 5. Scope

### 5.1 Current scope

**Empty.** There is no Android application in scope. This document's scope is limited to recording the position and pre-specifying conditional requirements.

### 5.2 Conditional in-scope (if an Android client is ever approved)

- **Authentication** — email and password against the Kailash backend, TOTP two-factor challenge, and biometric unlock via BiometricPrompt for session resumption.
- **Push notifications via FCM** for anomaly alerts, SLA breaches, guardian escalations, task assignments and system-health incidents, with deep links into the relevant screen — **including explicit handling of OEM battery-optimisation suppression**.
- **Read surfaces** — executive dashboard, department list and detail, task list and detail, alert feed, system health, designed for a phone rather than reflowed.
- **Focused write actions** — acknowledge an alert, assign or reassign a task, change task status, add a comment.
- **GANESHA conversational access** — ask a question, read the composed answer, see which departments were engaged.
- **Role-aware presentation** consistent with the backend's five-role model.
- **Session security** — EncryptedSharedPreferences or Android Keystore-backed storage, biometric gate, auto-lock on background, remote sign-out.
- **Material 3 (Material You) design conformance**, including dynamic colour on Android 12 and above.
- **Distribution** — managed Google Play (private app) for Go4Garage, or internal-track distribution; **not** a public Play Store listing.
- **Tablet support** — at minimum a correct scaled experience; ideally an adaptive layout.
- **Performance on mid-range and budget devices**, not only flagships.

### 5.3 Conditional out-of-scope

- **Public Google Play listing.** Kailash is internal; distribution would be private.
- **Offline data editing.** Live platform state must not be mutated from a stale local copy.
- **Feature parity with the web app.** A phone client covers alerting, triage and glanceable read — not analytics deep-dives, user administration or knowledge curation.
- **User administration and RBAC changes from mobile.** Excluded on security grounds.
- **In-app purchases, subscriptions or Google Play Billing.** Kailash has no billing surface anywhere.
- **A second implementation of business logic.** All computation stays in the backend.
- **Wear OS, Android TV, Android Auto or ChromeOS-specific builds.**
- **Third-party analytics or advertising SDKs.**
- **Support for Android versions below the defined minimum** (see BR-AND-15).

---

## 6. Business Requirements

### 6.1 Operative requirement (in force today)

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| **BR-AND-0** | Go4Garage **shall maintain and communicate the position that Kailash has no Android application and none is planned**, and shall not represent a Kailash mobile app as existing, in progress or forthcoming in any internal document, investor material, roadmap or job specification. The `android_app_kailash_ai/` directory shall be understood as documentation scaffolding, not as an abandoned or partial project. | Must | Inspect `android_app_kailash_ai/` — it contains only empty `deployed/` and `not_deployed/` directories. Review internal and external collateral for any contrary claim; there should be none. |

### 6.2 Conditional requirements (dormant until an Android client is approved)

> The following take effect **only** upon a documented, approved decision to build an Android client, satisfying the criteria in §11.1.

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| **BR-AND-1** | The app **shall authenticate against the same Kailash backend** used by the web client, honouring the same JWT session model and the same five-role RBAC, with **no separate user database, no separate credential store and no mobile-only authentication path**. | Must | A role change made on the web takes effect in the app on next token refresh; no account is valid in one client but not the other. |
| **BR-AND-2** | The app **shall support two-factor authentication** where enabled on the account, accepting a TOTP code or a single-use backup code, matching the web flow exactly, with SMS autofill support where the code is delivered that way. | Must | A 2FA-enabled account cannot sign in without a valid code; a consumed backup code is rejected on reuse. |
| **BR-AND-3** | The app **shall support biometric session unlock** via BiometricPrompt (fingerprint, face or device credential), with a device-credential fallback, and **shall automatically lock when backgrounded** beyond a configured interval. | Must | Background past the interval; resumption requires biometric or device credential. Cancelling returns to a locked state, never to content. |
| **BR-AND-4** | The app **shall deliver push notifications via Firebase Cloud Messaging** for at least: anomaly above a configured severity, SLA breach, guardian escalation, task assignment to the signed-in user, and system-health incident. Each notification **shall deep-link to the relevant in-app screen**. | Must | Trigger each server-side; the device receives it within 60 seconds on an unrestricted device; tapping opens the correct screen with the correct record. |
| **BR-AND-5** | The app **shall detect and mitigate OEM battery-optimisation suppression of notifications** — detecting when the app is battery-restricted, guiding the user through the OEM-specific exemption flow (Xiaomi, Oppo, Vivo, Realme, Samsung and others), and **shall degrade to a secondary channel (email or SMS) when push delivery cannot be assured**. | Must | On a Xiaomi or Oppo device with default battery settings, verify delivery; verify the in-app guidance appears when restricted; verify the fallback channel fires when push is undeliverable. |
| **BR-AND-6** | Notification permission (Android 13 and above) **shall be requested in context**, after the user has seen why it matters — never on first launch — and the app **shall remain fully usable if permission is denied**. | Must | Decline at first prompt; all non-alerting functionality still works; the app does not re-prompt aggressively. |
| **BR-AND-7** | The app **shall request the minimum runtime permissions necessary**, with clear rationale shown before each request, and **shall request none at all unless a feature requiring it is used**. At MVP scope only `POST_NOTIFICATIONS` (Android 13+) and biometric access are expected. | Must | Fresh install requests no permission until the relevant feature is invoked; the manifest declares no unused permission. |
| **BR-AND-8** | The app **shall provide a phone-native executive read experience** — not a reflowed desktop dashboard — covering portfolio health, department status, open alerts by severity and task load, legible at a glance in under five seconds. | Must | Usability test: an executive extracts current platform status within five seconds on a mid-range device. |
| **BR-AND-9** | The app **shall support focused triage actions**: acknowledge an alert, assign or reassign a task, change task status, and add a comment — each completable in three taps or fewer from the relevant notification. | Must | Tap-count measurement for each action from a cold notification tap. |
| **BR-AND-10** | The app **shall provide GANESHA conversational access** — submit a question, read the composed answer, and see which departments were engaged. | Should | The same prompt returns equivalent content on Android and web; long responses show progress rather than appearing frozen. |
| **BR-AND-11** | The app **shall enforce role-aware presentation** — a `viewer` shall see no action control, and no control visible to any role shall produce an authorisation error when used. | Must | Sign in as each of the five roles; enumerate visible controls; exercise each; zero authorisation errors. |
| **BR-AND-12** | The app **shall not permit user administration, RBAC changes or platform settings changes**; those remain web-only on security grounds. | Must | Confirm no such screen exists for any role. |
| **BR-AND-13** | The app **shall be distributed privately** — via managed Google Play (private app targeted at the Go4Garage organisation) or an equivalent controlled channel — and **shall not be published as a public Play Store listing**. | Must | Confirm the distribution method; the app is not discoverable in public Play Store search. |
| **BR-AND-14** | The app **shall satisfy Google Play policy requirements** for the chosen track, including the Data Safety declaration, target-API-level requirements, permissions declarations, and any policy provisions specific to private/enterprise apps. | Must | A Play Console submission passes review; a completed policy checklist is retained. |
| **BR-AND-15** | The app **shall conform to Material Design 3 (Material You)** — standard navigation components, dynamic colour on Android 12+, correct elevation and motion, edge-to-edge layout with proper insets, predictive back gesture support, and system theme (light/dark) adherence. | Must | Material Design review checklist completed; the app is visually and behaviourally native on a Pixel and on a heavily-skinned OEM device. |
| **BR-AND-16** | The app **shall support a minimum API level covering at least 90% of the target user base** (expected: API 26 / Android 8.0 or later at time of build) and **shall target the current API level required by Google Play policy**, with functional support on both phones and tablets. | Must | Functional pass on the minimum supported version, the target version, one budget device, one mid-range device, one flagship and one tablet. |
| **BR-AND-17** | The app **shall perform acceptably on mid-range and budget Indian-market devices** — not merely flagships — with defined cold-launch, scroll and memory budgets met on a 4 GB device. | Must | Performance test on a representative budget device (4 GB RAM, mid-tier SoC); budgets in the companion TRD met. |
| **BR-AND-18** | The app **shall meet Android accessibility expectations** — full TalkBack support, respect for system font scaling up to the largest setting without layout breakage, sufficient contrast, minimum 48 dp touch targets, and respect for reduced-motion settings. | Must | TalkBack traversal completes every core journey; largest font scale produces no clipped or overlapping content. |
| **BR-AND-19** | The app **shall behave predictably without connectivity** — cached content clearly labelled as stale with its retrieval time, no write action silently queued or lost, and an explicit offline state rather than a hang or a blank screen. This matters more on Android given intermittent Indian network coverage. | Must | Enable Airplane Mode mid-session; cached views show staleness labels; attempted writes are refused with a clear message. |
| **BR-AND-20** | The app **shall store credentials only in Android Keystore-backed encrypted storage**, **shall never write session tokens or platform data to unprotected storage, logs or backups**, and **shall support remote sign-out** invalidating the device session. Auto-backup shall exclude all sensitive data. | Must | Filesystem, logcat and backup-content inspection finds no token in the clear; a server-side revocation signs the device out on next request. |
| **BR-AND-21** | The app **shall be released through a controlled process** — internal testing track, then closed testing, then the private production track — with staged rollout, a documented rollback position, and release notes for every build. | Must | A release passes through the internal track before production; a staged rollout halt and rollback are demonstrated. |
| **BR-AND-22** | The app **shall not fork business logic** — all computation, orchestration, pricing, GST treatment and AI inference remain in the Kailash backend, with the app strictly a presentation and interaction client. | Must | Code review confirms no domain rule is reimplemented; changing a backend rule changes app behaviour with no app release. |
| **BR-AND-23** | The app **shall include no third-party analytics, advertising or attribution SDK**, and its Play Data Safety declaration shall accurately reflect that. | Must | Dependency audit; the Data Safety form matches actual data collection (minimal and internal). |
| **BR-AND-24** | Before a build is authorised, **a written business case shall demonstrate that the alerting and triage need cannot be adequately met by email, SMS, chat integration or web push**, and shall account for the Android device-fragmentation test matrix cost. | Must | The business case exists, is dated, and is signed off by the platform owner and leadership. |

---

## 7. Success Metrics / KPIs

### 7.1 Metrics that apply today

| KPI | Definition | Target |
|---|---|---|
| Documentation accuracy | Internal or external materials claiming a Kailash mobile app exists | **0** |
| Android-mobile web sessions | Kailash web app sessions originating from Chrome for Android | Tracked as the primary demand signal for a future decision |
| Unmet mobile requests | Logged staff requests for capability genuinely impossible in mobile web | Tracked; a sustained rise is a decision trigger |
| Alert-channel adequacy | Share of time-critical platform alerts successfully delivered by existing channels | 95% or better — while this holds, an app is unjustified |

### 7.2 Metrics that would apply to a delivered Android app

| KPI | Definition | Target |
|---|---|---|
| Adoption | Installs among the intended staff group | 80% or better within 60 days |
| Weekly active users | Distinct users opening the app weekly | 60% or better of installs |
| **Notification delivery rate** | Pushes delivered ÷ pushes dispatched, **segmented by OEM** | 95% or better overall; **no OEM below 90%** |
| Notification-to-action time | Median from push delivery to acknowledging action | Under 5 minutes |
| Notification opt-in rate | Users granting `POST_NOTIFICATIONS` | 80% or better |
| Battery-exemption grant rate | Users completing the OEM battery-exemption flow when prompted | 70% or better |
| Triage completion rate | Alerts triaged in-app rather than deferred to desktop | 50% or better |
| Crash-free session rate | Sessions without a crash | 99.5% or better |
| ANR rate | Application Not Responding events per session | Under 0.47% (Play Console bad-behaviour threshold) |
| Cold-launch time | Time to interactive from cold start **on a 4 GB mid-range device** | Under 3 s |
| Device-model coverage | Distinct device models with a passing functional test | Top 20 models covering 80% or more of the user base |
| OS-version coverage | Users on a supported Android version | 95% or better |
| Contract-drift incidents | Production breakages caused by backend changes not reflected in the app | 0 |

Note the Android-specific KPIs — notification delivery **segmented by OEM**, battery-exemption grant rate, ANR rate and device-model coverage — which have no iOS equivalent and represent the additional cost of the platform.

---

## 8. Assumptions & Constraints

### 8.1 Assumptions

| # | Assumption | If false |
|---|---|---|
| AA-1 | Kailash remains an internal platform, not a customer-facing product. | The entire mobile question reopens on different economics. |
| AA-2 | Kailash's human work remains desk-based analytical and supervisory work. | Field-based use cases would justify reassessment — and Android would lead. |
| AA-3 | Existing alert channels (email, SMS, chat) adequately reach on-call staff. | Alerting alone could justify a lightweight app — or, more cheaply, web push. |
| AA-4 | Go4Garage's mobile engineering capacity is better spent on customer-facing consumer products, which serve the Indian Android market directly. | If capacity frees up, the calculus changes. |
| AA-5 | Staff have Android devices capable of running a modern app (API 26+, 4 GB RAM or better). | The minimum-spec floor would need lowering, raising cost. |
| AA-6 | The responsive web app remains usable in Chrome for Android for read journeys. | If mobile web regresses, an app becomes more attractive — but fixing the web app is cheaper. |
| AA-7 | Document capture belongs to consumer products, not the internal platform. | A platform-level capture need would be the strongest single argument for a client. |
| AA-8 | Managed Google Play or an equivalent private channel is available for internal distribution. | Sideloading or an MDM-pushed APK would be needed, with weaker update control. |

### 8.2 Constraints

| # | Constraint | Nature |
|---|---|---|
| AC-1 | **No Android codebase, no Gradle project, no application ID, no Play Console record exists.** Any build starts from zero. | Absolute |
| AC-2 | **Android device fragmentation** — thousands of device/OEM/OS combinations — makes a credible test matrix materially more expensive than iOS. | Technical / cost |
| AC-3 | **OEM battery management** (Xiaomi, Oppo, Vivo, Realme, Samsung) actively suppresses background work and notification delivery, undermining the single strongest use case. | Technical |
| AC-4 | Google Play target-API-level policy forces annual compatibility work regardless of feature development. | External / ongoing |
| AC-5 | A second client doubles the surface exposed to backend contract changes. | Technical |
| AC-6 | The parent product roadmap prioritises the Automobile-LLM moat, consumer integration and production hardening — a mobile client competes with all three. | Resource |
| AC-7 | Distributing an internal tool with privileged platform access onto personal devices raises security and MDM obligations. | Security |
| AC-8 | No push infrastructure of any kind exists in the Kailash backend today. | Prerequisite |

---

## 9. Risks & Mitigations

### 9.1 Risks of the current position (no app)

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| AR-1 | **The empty `android_app_kailash_ai/` directory is misread** as an abandoned or half-finished project. | High | Low | This document, plus a README in the directory stating the position explicitly. |
| AR-2 | **Time-critical alerts are missed** because on-call staff are away from a desk. | Medium | High | Ensure email/SMS/chat alerting is reliable and monitored; measure alert-channel adequacy; consider web push before an app. |
| AR-3 | **Leadership expectation gap** — an executive assumes a phone app exists, particularly given the Indian Android context. | Medium | Low | Communicate the position; demonstrate the responsive web app on an Android phone. |
| AR-4 | **Mobile web experience degrades** unnoticed in Chrome for Android, creating latent pressure for an app. | Medium | Medium | Keep Chrome for Android in the web app's tested browser matrix; test at 414 px and 360 px each release. |
| AR-5 | **A reactive, unplanned mobile build** is commissioned under pressure without a business case or the prerequisites. | Low | High | BR-AND-24 requires a written, signed-off business case before any build is authorised. |

### 9.2 Risks that would attach to building an Android app

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| AR-6 | **OEM battery optimisation silently suppresses notifications**, defeating the app's primary justification on the very devices most common in India. | **High** | **High** | High-priority FCM messages; in-app detection and OEM-specific exemption guidance (BR-AND-5); mandatory secondary channel fallback; per-OEM delivery-rate monitoring. |
| AR-7 | **Device fragmentation** produces defects that only appear on specific OEM skins or Android versions. | **High** | Medium | Cloud device-farm testing across the top 20 models; per-model crash and ANR monitoring; staged rollout with halt criteria. |
| AR-8 | **Performance floor on budget devices** — an app tuned on a flagship is unusable on a 4 GB mid-range phone. | High | Medium | Set budgets against a mid-range reference device (BR-AND-17); profile on that device, not on a flagship. |
| AR-9 | **Ongoing maintenance burden** — annual target-API-level bumps, OEM skin changes, new device form factors (foldables). | High | Medium | Scope narrowly; budget maintenance explicitly; reassess annually against usage KPIs. |
| AR-10 | **Feature-parity creep** — pressure to reproduce the whole web app on a phone. | High | High | Hard scope boundary (BR-AND-12, §5.3); written justification for every addition. |
| AR-11 | **Contract drift between clients** — a backend change breaks Android but not web. | High | High | Shared, versioned API contract with schema validation on all clients; contract tests in CI. |
| AR-12 | **Play policy change** delays or blocks release. | Medium | Medium | Private/managed distribution reduces exposure; complete a policy checklist before each submission. |
| AR-13 | **Platform data on personal devices** widens the breach surface, with Android's more open filesystem and sideloading culture increasing exposure. | Medium | High | Keystore-backed encrypted storage, biometric gate, auto-lock, remote sign-out, backup exclusion, root detection, MDM for privileged roles. |
| AR-14 | **Notification fatigue** trains users to dismiss pushes. | High | Medium | Severity thresholds, per-category preferences, quiet hours, digest batching. |
| AR-15 | **Framework choice locks in a wrong bet** (Kotlin/Compose vs React Native vs Flutter). | Medium | Medium | Decide by ADR against explicit criteria; weight existing React competency and iOS intent heavily. |
| AR-16 | **ANR and crash rates breach Play Console bad-behaviour thresholds**, harming distribution even on a private track. | Medium | Medium | Enforce main-thread discipline; monitor ANR rate against the 0.47% threshold; profile on budget hardware. |
| AR-17 | **Two release cadences diverge**, with the app lagging backend capability. | Medium | Medium | Version the API; enforce a minimum-supported-app-version check; tolerate additive backend changes. |
| AR-18 | **Intermittent Indian network coverage** produces a poor experience without careful offline and retry design. | High | Medium | Explicit offline states (BR-AND-19), bounded retry with backoff, small payloads, pagination everywhere. |

---

## 10. Current Implementation Status

### 10.1 Platform existence statement — Android

> **No Kailash Android application exists.**
>
> As of 2026-07-31, at product HEAD commit `40cca17`, the directory `C:\Go4Garage( Eka)\Kailash-Ai\android_app_kailash_ai\` contains **only two empty subdirectories**: `deployed/` and `not_deployed/`. There are no source files of any kind.
>
> Specifically, there is:
> - **No Gradle project** (`build.gradle`, `build.gradle.kts`, `settings.gradle`, `gradle.properties`, `gradlew`)
> - **No Kotlin or Java source**
> - **No `AndroidManifest.xml`**, no application ID, no `res/` directory
> - **No React Native, Expo or Flutter project** (no `android/` platform folder, no `pubspec.yaml`, no `app.json`, no `metro.config.js`)
> - **No `google-services.json`**
> - **No signing keystore, no Play Console record, no release track, no App Bundle**
> - **No Android CI job** — `.github/workflows/ci.yml` defines `lint`, `shared`, `services`, `backend`, `frontend` and `compose-build`; there is no mobile job
> - **No FCM configuration anywhere in the backend** — no push service, no device-token model, no notification dispatch code
>
> Kailash is presently a **backend and web-only internal service**. It is Go4Garage's internal ML/AI platform, consumed by other Go4Garage products over HTTP and operated by staff through a single React 19 web dashboard. **No dedicated mobile client is planned**, unless the reader decides otherwise on the basis of the decision criteria in §11.1.

### 10.2 What exists instead

| Surface | Status | Location |
|---|---|---|
| **Backend (FastAPI)** | **Built and run locally** — populated `.venv`, roughly 24 API routers, 20 department agents, 3 guardians, 9 platform services | `Kailash-Ai/backend/` |
| **Web app (React 19)** | **Built and compiled** — roughly 70 page modules, populated `node_modules/`, compiled `build/` output, Firebase Hosting configuration | `Kailash-Ai/frontend/` |
| **Android app** | **Does not exist** — two empty placeholder directories | `Kailash-Ai/android_app_kailash_ai/` |
| **iOS app** | **Does not exist** — two empty placeholder directories | `Kailash-Ai/ios_app_kailash_ai/` |

### 10.3 Android access available today

An Android user reaches Kailash through **Chrome for Android against the web application**. Per the web app's browser matrix, Chrome for Android (current) is supported for read journeys and core actions, with responsive requirements specifying readable, navigable layouts down to 360 px and no horizontal overflow of primary content.

What that gives an Android user today: dashboard, departments and department detail, tasks, analytics, reports, GANESHA chat, knowledge base and the policy corpus — all in the browser.

What it does not give: an installed app icon, FCM push notifications, offline access, biometric unlock, camera capture or background execution.

### 10.4 Prerequisites, were a build ever approved

| # | Prerequisite | Status |
|---|---|---|
| 1 | Written, approved business case per BR-AND-24 | Not started |
| 2 | Google Play Console developer account | Not held (unverified) |
| 3 | Managed Google Play / private app distribution channel | Not established |
| 4 | Framework decision (Kotlin + Jetpack Compose vs React Native vs Flutter) recorded as an ADR | Not made |
| 5 | Backend push infrastructure — device-token model, FCM credentials, dispatch service | **Does not exist** in the backend |
| 6 | FCM project configuration (Firebase project `kailash-38268` exists for hosting; FCM is not configured) | Not configured |
| 7 | Versioned, schema-validated API contract shared across clients | Partially — the `ApiResponse` envelope exists; no client-side schema validation |
| 8 | Device test matrix and cloud device-farm access | Not established |
| 9 | Signing keystore and secure key management | Not created |
| 10 | Mobile engineering capacity | Not allocated |
| 11 | MDM baseline for privileged roles | Not defined |

Note that Go4Garage **already uses Firebase** (project `kailash-38268` for web hosting, and the Firebase Admin SDK in the backend). This lowers the barrier to FCM specifically: the account relationship exists, only the messaging configuration would be new.

---

## 11. Roadmap / Milestones

### 11.1 Near term (0 to 3 months) — *hold the position and measure*

| # | Milestone | Success criterion |
|---|---|---|
| AN-1 | **Record the position visibly.** Place a short README in `android_app_kailash_ai/` stating that no app exists and pointing to this BRD. | No reader mistakes the empty directory for lost work. |
| AN-2 | **Define the decision criteria** (below) and socialise them with leadership. | Written, agreed trigger conditions. |
| AN-3 | **Verify mobile web quality on Android.** Test core read journeys in Chrome for Android at 414 px and 360 px, on at least one mid-range device. | Documented pass/fail per journey; defects raised against the web app. |
| AN-4 | **Audit alert-channel reliability.** Confirm time-critical alerts reliably reach on-call staff by existing means. | Alert-channel adequacy KPI measured at 95% or better. |
| AN-5 | **Instrument mobile web demand.** Measure Android-originated web sessions and log unmet mobile requests. | A demand signal exists to inform any future decision. |

**Decision criteria — an Android client is reconsidered only if all four hold:**

1. Android-originated mobile web sessions exceed a sustained, material share of total sessions for three consecutive months.
2. A specific, repeatable work task is demonstrably impossible or unacceptably slow in Chrome for Android.
3. The alerting need is proven not satisfiable by email, SMS, chat integration or web push — **and** OEM battery-optimisation testing shows that a native app would actually deliver more reliably, not less.
4. Mobile engineering capacity exists that does not displace the Automobile-LLM moat, consumer-product integration or production hardening.

Criterion 3 is deliberately harder than its iOS equivalent, because on Android the native path is not automatically the more reliable one.

### 11.2 Mid term (3 to 9 months) — *cheaper alternatives before an app*

| # | Milestone | Success criterion |
|---|---|---|
| AM-1 | **Improve the mobile web experience** at phone breakpoints — larger touch targets, collapsed dense tables, a mobile-first executive read view. | Core read journeys complete comfortably at 360 px on a mid-range Android device. |
| AM-2 | **Evaluate PWA installability and web push on Chrome for Android** — which supports both, and which would deliver the two genuine native benefits (icon, notifications) at a fraction of the cost. **Android supports web push natively, unlike iOS's more limited position.** | A written comparison of PWA versus native cost and capability, including OEM battery-restriction testing of web push. |
| AM-3 | **Build backend notification infrastructure channel-agnostically** — a device/subscription model and a dispatch service targeting email, SMS, web push or, later, FCM. | Alerts deliverable through at least two channels without any app. |
| AM-4 | **Harden the API contract** with schema validation and versioning, so any future client inherits safety rather than risk. | Contract tests in CI; a breaking backend change fails the build. |
| AM-5 | **Re-evaluate against the decision criteria.** | A dated written decision: build, defer, or close. |

The PWA route deserves particular emphasis on Android: Chrome for Android supports both installability and web push, which means a service worker added to the existing React app could deliver the app icon and the notifications — the two genuine native benefits — without a second codebase. This should be exhausted before any native build is contemplated.

### 11.3 Long term (9 to 24 months) — *conditional build path*

Applicable **only** if the §11.1 criteria are met and a business case is approved.

| # | Milestone | Success criterion |
|---|---|---|
| AL-1 | **Framework decision recorded as an ADR** (Kotlin + Jetpack Compose, React Native, or Flutter), weighing team skills, iOS intent and native-capability depth. | Signed ADR. |
| AL-2 | **Provision the build and distribution environment** — Play Console account, managed Google Play channel, signing keystore with secure key management, CI build capacity. | A signed App Bundle produced by CI. |
| AL-3 | **Backend FCM support** — device-token registration, FCM credentials, notification dispatch with deep-link payloads and high-priority delivery. | A test push reaches a device and deep-links correctly. |
| AL-4 | **OEM battery-restriction mitigation** — detection, guidance flows for the major Indian OEMs, and fallback-channel wiring. | Delivery rate 90% or better on Xiaomi, Oppo, Vivo and Samsung with default settings. |
| AL-5 | **MVP: alerting and triage only** — auth with 2FA and biometric unlock, push with deep links, executive read view, alert feed, task acknowledge/assign/status. | All MVP-scoped requirements in §6.2 verified. |
| AL-6 | **Internal and closed testing tracks** with a defined tester group across at least five OEM skins. | Crash-free session rate 99.5% or better; ANR rate under threshold; feedback triaged. |
| AL-7 | **Private production release** via managed Google Play with staged rollout. | 80% or better install rate among the intended group within 60 days. |
| AL-8 | **Post-launch review at 6 months** against the §7.2 KPIs, with particular attention to per-OEM notification delivery. | A written decision to continue, narrow or retire the app. |

---

## 12. Appendix

### 12.1 Parent product documents

This application-level BRD narrows the Kailash platform requirements to the Android surface — a surface that does not currently exist. The authoritative product-level documents are:

| Document | Location |
|---|---|
| **`BRD_kailash_ai.md`** | `../BRD_kailash_ai.md` — product-level business requirements for the whole Kailash platform |
| **`TRD_kailash_ai.md`** | `../TRD_kailash_ai.md` — product-level technical requirements, including the backend API any client would consume |

Its direct companion is **`TRD_android_app_kailash_ai.md`** in this same directory, which sets out the conditional technical design.

Sibling surfaces: `../web_app_kailash_ai/` (the one client that does exist) and `../ios_app_kailash_ai/` (which records the equivalent no-app position for iOS).

### 12.2 Directory contents, verbatim

```
android_app_kailash_ai/
├── deployed/            (empty)
├── not_deployed/        (empty)
├── BRD_android_app_kailash_ai.md   ← this document
└── TRD_android_app_kailash_ai.md
```

No application source of any kind is present.

### 12.3 What the web app already provides on Android

| Capability | Chrome for Android | Native app would add |
|---|---|---|
| Dashboard, departments, tasks, analytics, reports | Yes | Phone-optimised layout |
| GANESHA chat | Yes | Nothing material |
| Knowledge base | Yes | Nothing material |
| Policy corpus | Yes | Nothing — these are public web URLs by design |
| App icon on home screen | Possible via PWA install — **but no manifest or service worker exists today** | Proper installability |
| Push notifications | **Possible via web push** — but no service worker exists today | FCM push (and not necessarily more reliable, given OEM restrictions) |
| Offline access | No (no service worker) | Cached read (of limited value on live data) |
| Biometric unlock | Possible via WebAuthn platform authenticator | BiometricPrompt natively |
| Camera capture | Via file input | Native camera integration |
| Background execution | No | Constrained by OEM battery management anyway |

The critical Android-specific observation: **two of the four genuine native benefits (icon, notifications) are achievable by adding a service worker and manifest to the existing React app.** Chrome for Android supports both. That is a fraction of the cost of a native client and should be evaluated first.

### 12.4 Comparison with the iOS position

| Dimension | iOS | Android |
|---|---|---|
| App exists | No | No |
| Web fallback | Mobile Safari | Chrome for Android |
| Web push available today | Limited on iOS | **Fully supported on Chrome for Android** |
| PWA installability | Limited ("Add to Home Screen") | **Full install support** |
| Notification reliability if built | High | **Compromised by OEM battery management** |
| Device fragmentation | Low | **High** |
| Market relevance to Go4Garage | Lower | **Higher — India is Android-first** |
| Development environment barrier | macOS required | None (Windows/Linux fine) |
| Recommended priority if any mobile client is built | Second | **First** |

The net position: Android is the higher-priority platform *if* a mobile client is ever built, but it also has the strongest cheaper alternative (PWA), and the weakest guarantee that a native app would actually improve notification reliability.

### 12.5 Glossary

| Term | Meaning |
|---|---|
| **FCM** | Firebase Cloud Messaging — Google's push notification service |
| **Managed Google Play** | Google's private app distribution channel for organisations |
| **Material 3 / Material You** | Google's current design system, including dynamic colour |
| **BiometricPrompt** | Android's unified biometric authentication API |
| **ANR** | Application Not Responding — a Play Console bad-behaviour metric |
| **API level** | Android's SDK version identifier (for example API 26 = Android 8.0) |
| **App Bundle (AAB)** | Google Play's required publishing format |
| **OEM battery management** | Vendor-specific background restrictions (Xiaomi, Oppo, Vivo, Realme, Samsung) that suppress notifications |
| **MDM** | Mobile Device Management |
| **ADR** | Architecture Decision Record |
| **PWA** | Progressive Web App — installable, offline-capable web app; the cheaper Android alternative |

### 12.6 Open questions for the document owner

1. Does Go4Garage hold a Google Play Console developer account, and is managed Google Play available?
2. Should the PWA route (service worker plus manifest on the existing React app) be evaluated and costed before any native Android decision? (Strongly recommended — Chrome for Android supports both installability and web push.)
3. Are time-critical Kailash alerts currently reaching on-call staff reliably, and through which channel?
4. Has any staff member actually requested a Kailash mobile app, and for what specific task?
5. Given the Indian market, should Android lead any mobile programme — and does that change the framework choice toward React Native (shared with a later iOS client) rather than Kotlin?
6. What is the realistic OEM distribution across Go4Garage staff devices, and what would per-OEM notification testing cost?
7. Who would own and maintain a mobile codebase, given the current team's composition?
8. Should the backend's channel-agnostic notification dispatcher be built now regardless of the mobile decision? (Recommended: yes — it improves alerting today.)

---

## Section 3 — iOS App
### 3.1 Business Requirements Document — Kailash-Ai iOS Application

## 1. Document Control

| Field | Value |
|---|---|
| **Document title** | Business Requirements Document — Kailash-Ai iOS Application |
| **Product** | Kailash — Go4Garage internal ML/AI platform |
| **Surface** | iOS (iPhone / iPad native client) |
| **Document type** | BRD (Application level) |
| **Version** | 1.0 |
| **Date** | 2026-07-31 |
| **Status** | Draft |
| **Owner** | TBD |
| **Author** | Go4Garage Documentation Workstream |
| **Reviewers** | TBD (Platform Lead, Mobile Lead if appointed, Security, Compliance) |
| **Approvers** | TBD |
| **Classification** | Internal — Proprietary |
| **Parent product BRD** | `../BRD_kailash_ai.md` |
| **Parent product TRD** | `../TRD_kailash_ai.md` |
| **Companion document** | `TRD_ios_app_kailash_ai.md` (same directory) |
| **Source of truth** | `C:\Go4Garage( Eka)\Kailash-Ai\ios_app_kailash_ai`, product HEAD commit `40cca17` dated 2026-07-31 |

### 1.1 Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-31 | Documentation Workstream | Initial draft. Records the current no-native-client position and defines conditional requirements should that position be revisited. |

---

## 2. Executive Summary

### 2.1 The headline finding

**There is no Kailash iOS application.** No Swift, Objective-C, React Native, Expo or Flutter project exists in this repository for Kailash, and none is currently planned. The directory `ios_app_kailash_ai/` contains exactly two empty placeholder subdirectories — `deployed/` and `not_deployed/` — and nothing else. There is no Xcode project, no `Info.plist`, no bundle identifier, no App Store Connect record, no TestFlight build and no provisioning profile.

This is a **deliberate consequence of what Kailash is**, not an oversight. Kailash is Go4Garage's internal ML/AI platform — the shared AI engine behind URGAA, GSTSAAS, Ignition and ARJUN. It is explicitly not a product sold to customers. Its human users are Go4Garage staff performing analytical and supervisory work: reading multi-panel dashboards, comparing forecasts, triaging anomalies, curating knowledge, and administering users and roles. That work belongs on a large screen with a keyboard. Kailash is, by design, a **backend and web-only service**.

### 2.2 What this document is for

A BRD for an application that does not exist has three legitimate jobs, and this document does all three:

1. **Record the position unambiguously**, so that no future reader, auditor, investor or new engineer mistakes an empty directory for lost work or an unshipped commitment.
2. **State the decision criteria** — what would have to become true for an iOS client to be justified.
3. **Pre-specify the business requirements** that would apply *if* that threshold were ever crossed, so a future decision starts from an informed position rather than a blank page.

Every numbered requirement in §6 is therefore **conditional**: it takes effect only upon an approved decision to build an iOS client. Until then the requirements are dormant, and the operative requirement is BR-iOS-0 in §6.1.

### 2.3 The alternative that already exists

Go4Garage staff who need Kailash on an iPhone or iPad are not without recourse. The Kailash web application (`../web_app_kailash_ai/`) is a responsive React 19 SPA, and mobile Safari on iOS is in its supported browser matrix for read journeys and core actions. A user on an iPad can reach the dashboard, departments, tasks and analytics today. What they cannot do is install an app icon, receive a push notification, work offline, or use device capabilities such as the camera for document capture. Those four gaps are the entirety of what a native iOS client would add — and §4 assesses whether any of them is worth an app.

---

## 3. Business Objectives & Strategic Fit

### 3.1 The strategic question

The parent BRD sets out Kailash's objectives: be the single AI engine for the Go4Garage portfolio, insulate product teams from AI vendor churn, accumulate an automotive data moat, provide an operations cockpit, encode Indian regulatory knowledge, reduce AI time-to-market, be operationally credible, and build toward a licensable Automobile-LLM.

An iOS client advances **none of them directly**. It is a delivery channel for objective O-4 (the operations cockpit) only, and that objective is already served by the web app. The strategic question is therefore narrow: *is there a class of Kailash work that must happen away from a desk, frequently enough and urgently enough to justify a second client codebase, an Apple Developer Program membership, an App Store review relationship and an ongoing maintenance burden?*

On the evidence in this repository, the answer today is no.

### 3.2 Assessment of candidate justifications

| Candidate justification | Assessment | Verdict |
|---|---|---|
| **Executives want dashboards on their phone** | The executive and investor dashboards are read-only summary views. Mobile Safari renders them today. A native app adds an icon, not a capability. | Not sufficient |
| **Push notifications for anomalies and SLA breaches** | Genuinely useful — but email, SMS or a chat integration delivers the same alert without an app. Web push would need a service worker, which the web app also lacks today. | Addressable more cheaply |
| **Offline access in the field** | Kailash data is live platform state; a stale forecast or a stale anomaly list is close to useless and potentially misleading. | Not sufficient |
| **Camera capture for document AI** | The strongest technical argument. The `document-ai` service ingests PDFs, and a phone camera is a natural capture device. But this capture need belongs to the *consumer products* (URGAA certifications, GSTSAAS invoices, Ignition RC documents), which have their own mobile surfaces, not to the internal platform. | Belongs to consumer products |
| **Voice input for GANESHA using device speech** | The `speech` service exists, and the web app's Permissions-Policy already allows microphone to `self`. Browser speech APIs cover this. | Addressable on web |
| **Biometric authentication (Face ID) for a privileged internal tool** | A real security ergonomics gain, but it does not on its own justify a client. WebAuthn provides platform-authenticator support in Safari. | Addressable on web |
| **Presenting the platform to investors on an iPad** | The investor executive dashboard renders in mobile Safari; an app adds polish, not function. | Not sufficient |

### 3.3 Objectives, conditional on a future decision

Were an iOS client ever approved, its objectives would be:

| # | Objective |
|---|---|
| **IO-1** | Deliver time-critical platform alerts (anomalies, SLA breaches, guardian escalations) to on-call staff wherever they are, with one-tap navigation to context. |
| **IO-2** | Give leadership a genuinely mobile-native read experience of the executive dashboard, designed for a phone rather than reflowed from a desktop layout. |
| **IO-3** | Enable fast triage away from a desk — acknowledge, assign, comment, escalate — without requiring a laptop. |
| **IO-4** | Use device capability where it adds real value: biometric unlock, native notifications, and camera capture *if* a platform-level capture use case emerges. |
| **IO-5** | Do all of the above without forking business logic — the app is a client of the same backend contract, never a second implementation. |

### 3.4 Strategic fit conclusion

An iOS client is a **channel investment, not a capability investment**. Kailash's strategic priorities per the parent BRD are the Automobile-LLM moat, consumer-product integration, durable retrieval and production hardening. A mobile client competes for the same scarce engineering attention while advancing none of those. The recommended position is: **do not build; revisit only against the explicit criteria in §11.1.**

---

## 4. Target Users / Personas / Stakeholders

### 4.1 Current position

**There are no iOS app users, because there is no iOS app.** All Kailash users are web users. Users who access the web app from an iPhone or iPad are served by the responsive web surface documented in `../web_app_kailash_ai/BRD_web_app_kailash_ai.md`.

### 4.2 Prospective personas, conditional on a future decision

| Persona | Mobile need | Would an app help? |
|---|---|---|
| **On-call platform engineer** | Receive an alert that Kailash is degraded or a guardian escalated; assess severity; acknowledge | **Yes** — push notification and one-tap context are genuinely native strengths |
| **Operations manager (in the field)** | Check a department's status; reassign an urgent task; see today's anomalies | **Partly** — the responsive web app covers reading; native would improve action speed |
| **Executive** | Glance at portfolio health between meetings | **Marginal** — a phone-optimised read view, but mobile Safari already renders it |
| **Business analyst** | Deep multi-panel analysis, filtering, export | **No** — this is desktop work by nature |
| **Domain SME** | Curate knowledge, review digests | **No** — long-form reading and editing work |
| **Administrator** | User and role administration | **No** — and arguably should not be possible from a phone on security grounds |
| **Compliance officer / external reviewer** | Read a policy page and cite it | **No** — policy pages are public web URLs by design |

Of seven personas, exactly one has an unambiguous native need, and that need (alerting) is satisfiable by channels that do not require an app.

### 4.3 Stakeholders in the decision

| Stakeholder | Interest |
|---|---|
| Go4Garage leadership | Whether the investment is justified against the moat roadmap |
| Platform engineering | Second codebase, second release cadence, contract-drift risk across two clients |
| Security / Compliance | Device-level data exposure, MDM posture, App Store distribution of an internal tool |
| Finance | Apple Developer Program membership, mobile engineering capacity, ongoing OS-version maintenance |
| Consumer-product teams | Whether platform mobile effort would be better spent on *their* customer-facing apps |

---

## 5. Scope

### 5.1 Current scope

**Empty.** There is no iOS application in scope. This document's scope is limited to recording the position and pre-specifying conditional requirements.

### 5.2 Conditional in-scope (if an iOS client is ever approved)

- **Authentication** — email and password against the Kailash backend, TOTP two-factor challenge, and biometric unlock (Face ID / Touch ID) for session resumption.
- **Push notifications via APNs** for anomaly alerts, SLA breaches, guardian escalations, task assignments and system-health incidents, with deep links into the relevant screen.
- **Read surfaces** — executive dashboard, department list and detail, task list and detail, anomaly and alert feed, system health, redesigned for a phone rather than reflowed.
- **Focused write actions** — acknowledge an alert, assign or reassign a task, change task status, add a comment.
- **GANESHA conversational access** — ask a question, read the composed answer, see which departments were engaged.
- **Role-aware presentation** consistent with the backend's five-role model.
- **Session security** — Keychain-stored credentials, biometric gate, automatic lock on backgrounding, remote sign-out.
- **Internal distribution** — Apple Business Manager custom app distribution or Ad Hoc/enterprise distribution, with TestFlight for pre-release.
- **iPad support** — at minimum a well-behaved scaled experience; ideally an adaptive layout using the larger canvas.

### 5.3 Conditional out-of-scope

- **Public App Store listing.** Kailash is internal; the app would be distributed privately.
- **Offline data editing.** Live platform state must not be mutated from a stale local copy.
- **Feature parity with the web app.** A phone client covers alerting, triage and glanceable read — not analytics deep-dives, user administration or knowledge curation.
- **User administration and RBAC changes from mobile.** Excluded on security grounds.
- **In-app purchases, subscriptions or any payment surface.** Kailash has no billing anywhere.
- **A second implementation of business logic.** All computation stays in the backend.
- **Apple Watch, tvOS, visionOS or macOS Catalyst variants.**
- **Third-party analytics or advertising SDKs.**

---

## 6. Business Requirements

### 6.1 Operative requirement (in force today)

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| **BR-iOS-0** | Go4Garage **shall maintain and communicate the position that Kailash has no iOS application and none is planned**, and shall not represent a Kailash mobile app as existing, in progress or forthcoming in any internal document, investor material, roadmap or job specification. The `ios_app_kailash_ai/` directory shall be understood as documentation scaffolding, not as an abandoned or partial project. | Must | Inspect `ios_app_kailash_ai/` — it contains only empty `deployed/` and `not_deployed/` directories. Review internal and external collateral for any contrary claim; there should be none. |

### 6.2 Conditional requirements (dormant until an iOS client is approved)

> The following take effect **only** upon a documented, approved decision to build an iOS client, satisfying the criteria in §11.1.

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| **BR-iOS-1** | The app **shall authenticate against the same Kailash backend** used by the web client, honouring the same JWT session model and the same five-role RBAC, with **no separate user database, no separate credential store and no mobile-only authentication path**. | Must | A user's role change made on the web takes effect in the app on next token refresh; no account exists that is valid in one client and not the other. |
| **BR-iOS-2** | The app **shall support two-factor authentication** where the account has it enabled, accepting a TOTP code or a single-use backup code, matching the web flow exactly. | Must | A 2FA-enabled account cannot complete sign-in in the app without a valid code; a consumed backup code is rejected on reuse. |
| **BR-iOS-3** | The app **shall support biometric session unlock** (Face ID or Touch ID) with a device-passcode fallback, and **shall automatically lock when backgrounded** for longer than a configured interval. | Must | Background the app past the interval; returning requires biometric or passcode. Disabling biometrics at OS level falls back to passcode, never to unauthenticated access. |
| **BR-iOS-4** | The app **shall deliver push notifications via APNs** for at least: anomaly detection above a configured severity, SLA breach, guardian escalation, task assignment to the signed-in user, and system-health incident. Each notification **shall deep-link to the relevant in-app screen**. | Must | Trigger one of each server-side; the device receives it within 60 seconds; tapping opens the correct screen with the correct record loaded. |
| **BR-iOS-5** | Notification permission **shall be requested in context**, after the user has seen why it matters — never on first launch — and the app **shall remain fully usable if permission is denied**. | Must | Decline notifications at first prompt; all non-alerting functionality still works; the app does not re-prompt aggressively. |
| **BR-iOS-6** | The app **shall request the minimum device permissions necessary**, with a clear, specific purpose string for each, and **shall request none at all unless a feature requiring it is used**. | Must | Fresh install requests no permission until the relevant feature is invoked. Each `Info.plist` purpose string names the concrete user benefit. |
| **BR-iOS-7** | The app **shall provide a phone-native executive read experience** — not a reflowed desktop dashboard — covering portfolio health, department status and the current alert set, legible at a glance in under five seconds. | Must | Usability test: an executive extracts the current platform status within five seconds of opening the app. |
| **BR-iOS-8** | The app **shall support focused triage actions**: acknowledge an alert, assign or reassign a task, change task status, and add a comment — each completable in three taps or fewer from the relevant notification. | Must | Time and count the taps for each action from a cold notification tap. |
| **BR-iOS-9** | The app **shall provide GANESHA conversational access** — submit a question, read the composed answer, and see which departments were engaged. | Should | Ask a multi-department question on mobile; the answer and department attribution match what the web client returns for the same prompt. |
| **BR-iOS-10** | The app **shall enforce role-aware presentation** — a `viewer` shall see no action control, and no control visible to any role shall produce an authorisation error when used. | Must | Sign in as each of the five roles; enumerate visible controls; exercise each; zero authorisation errors. |
| **BR-iOS-11** | The app **shall not permit user administration, RBAC changes or settings changes**; those remain web-only on security grounds. | Must | Confirm no such screen exists in the app for any role. |
| **BR-iOS-12** | The app **shall be distributed privately** — via Apple Business Manager custom app distribution or an equivalent managed channel — and **shall not be published to the public App Store**. | Must | Confirm the distribution method; the app is not discoverable in public App Store search. |
| **BR-iOS-13** | The app **shall satisfy App Store Review Guidelines** for whichever distribution channel is chosen, including the guidelines governing business/enterprise apps, account deletion where accounts are created in-app (not applicable if accounts are admin-provisioned only), and accurate privacy disclosures. | Must | A review submission passes without rejection; the guideline compliance checklist is completed and retained. |
| **BR-iOS-14** | The app **shall conform to the iOS Human Interface Guidelines** — native navigation patterns, standard controls, Dynamic Type support, Dark Mode support, safe-area respect, and correct handling of the Home indicator and Dynamic Island where present. | Must | HIG review checklist completed; the app is visually and behaviourally indistinguishable from a well-built native app in these respects. |
| **BR-iOS-15** | The app **shall support the current and previous two major iOS versions** at release, and **shall support both iPhone and iPad** with at minimum a well-behaved scaled iPad experience. | Must | Functional test across the supported version range on at least one small phone, one large phone and one iPad. |
| **BR-iOS-16** | The app **shall meet Apple's accessibility expectations** — full VoiceOver support, Dynamic Type up to the largest accessibility sizes without layout breakage, sufficient contrast, and respect for Reduce Motion. | Must | VoiceOver traversal completes every core journey; the largest Dynamic Type size produces no clipped or overlapping content. |
| **BR-iOS-17** | The app **shall behave predictably without connectivity** — cached content clearly labelled as stale with its retrieval time, no write action silently queued or lost, and an explicit offline state rather than a hang or a blank screen. | Must | Enable Airplane Mode mid-session; cached views show a staleness label; attempted writes are refused with a clear message, not silently dropped. |
| **BR-iOS-18** | The app **shall store credentials only in the iOS Keychain** with appropriate protection class, **shall never write session tokens or platform data to unprotected storage or logs**, and **shall support remote sign-out** invalidating the device session. | Must | Filesystem and log inspection finds no token outside the Keychain; a server-side session revocation signs the device out on next request. |
| **BR-iOS-19** | The app **shall be released through a controlled process** — TestFlight for internal testing with a defined tester group, staged rollout, a documented rollback position, and release notes for every build. | Must | A release passes through TestFlight before production; a rollback path is demonstrated. |
| **BR-iOS-20** | The app **shall not fork business logic** — all computation, orchestration, pricing, GST treatment and AI inference remain in the Kailash backend, with the app strictly a presentation and interaction client. | Must | Code review confirms no domain rule is reimplemented in the app; changing a backend rule changes app behaviour with no app release. |
| **BR-iOS-21** | The app **shall include no third-party analytics, advertising or attribution SDK**, and its App Privacy disclosure shall accurately reflect that. | Must | Dependency audit; the privacy nutrition label matches the actual data collection (which should be minimal and internal). |
| **BR-iOS-22** | Before a build is authorised, **a written business case shall demonstrate that the alerting and triage need cannot be adequately met by email, SMS, chat integration or web push**, with the comparison recorded. | Must | The business case document exists, is dated, and is signed off by the platform owner and leadership. |

---

## 7. Success Metrics / KPIs

### 7.1 Metrics that apply today

| KPI | Definition | Target |
|---|---|---|
| Documentation accuracy | Internal or external materials claiming a Kailash mobile app exists | **0** |
| iOS-mobile web sessions | Kailash web app sessions originating from iOS Safari | Tracked as the primary demand signal for a future decision |
| Unmet mobile requests | Logged staff requests for capability genuinely impossible in mobile web | Tracked; a sustained rise is a decision trigger |
| Alert-channel adequacy | Share of time-critical platform alerts successfully delivered by existing channels (email/SMS/chat) | 95% or better — while this holds, an app is unjustified |

### 7.2 Metrics that would apply to a delivered iOS app

| KPI | Definition | Target |
|---|---|---|
| Adoption | Installs among the intended staff group | 80% or better within 60 days |
| Weekly active users | Distinct users opening the app weekly | 60% or better of installs |
| Notification-to-action time | Median elapsed time from push delivery to an acknowledging action | Under 5 minutes |
| Notification opt-in rate | Users granting notification permission | 80% or better |
| Triage completion rate | Alerts triaged in-app rather than deferred to desktop | 50% or better |
| Crash-free session rate | Sessions without a crash | 99.5% or better |
| Cold-launch time | Time to interactive from a cold start | Under 2 s |
| App Review rejection rate | Submissions rejected on review | Under 10% |
| VoiceOver journey completion | Core journeys completable with VoiceOver | 100% |
| OS-version coverage | Users on a supported iOS version | 95% or better |
| Contract-drift incidents | Production breakages caused by backend changes not reflected in the app | 0 |

---

## 8. Assumptions & Constraints

### 8.1 Assumptions

| # | Assumption | If false |
|---|---|---|
| IA-1 | Kailash remains an internal platform, not a customer-facing product. | The entire mobile question reopens on different terms — a customer app has different economics. |
| IA-2 | Kailash's human work remains desk-based analytical and supervisory work. | Field-based use cases would justify reassessment. |
| IA-3 | Existing alert channels (email, SMS, chat) adequately reach on-call staff. | Alerting alone could justify a lightweight app — or, more cheaply, web push. |
| IA-4 | Go4Garage's mobile engineering capacity is better spent on customer-facing consumer products. | If capacity frees up, the calculus changes. |
| IA-5 | Staff have Go4Garage-managed or personally-owned iOS devices suitable for a managed internal app. | MDM and device-provisioning cost would need to be added to any business case. |
| IA-6 | The responsive web app remains usable on iOS Safari for read journeys. | If the web app regresses on mobile, an app becomes more attractive — but fixing the web app is cheaper. |
| IA-7 | Document capture belongs to consumer products (URGAA, GSTSAAS, Ignition), not to the internal platform. | A platform-level capture need would be the strongest single argument for a client. |

### 8.2 Constraints

| # | Constraint | Nature |
|---|---|---|
| IC-1 | **No iOS codebase, no Xcode project, no bundle identifier, no App Store Connect record exists.** Any build starts from zero. | Absolute |
| IC-2 | iOS development requires macOS hardware and Xcode; the observed development environment for this workspace is Windows 11. | Tooling |
| IC-3 | An Apple Developer Program membership (and, for private distribution, Apple Business Manager enrolment) would be required. | Commercial |
| IC-4 | Apple's review process and guideline changes impose an ongoing external dependency on release timing. | External |
| IC-5 | Annual iOS major releases impose a recurring compatibility maintenance cost regardless of feature work. | Ongoing |
| IC-6 | A second client doubles the surface exposed to backend contract changes. | Technical |
| IC-7 | The parent product roadmap prioritises the Automobile-LLM moat, consumer integration and production hardening — a mobile client competes with all three. | Resource |
| IC-8 | Distributing an internal tool with privileged platform access onto personal devices raises security and MDM obligations. | Security |

---

## 9. Risks & Mitigations

### 9.1 Risks of the current position (no app)

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| IR-1 | **The empty `ios_app_kailash_ai/` directory is misread** as an abandoned or half-finished project by an auditor, investor or new engineer. | High | Low | This document, plus a README in the directory stating the position explicitly. |
| IR-2 | **Time-critical alerts are missed** because on-call staff are away from a desk. | Medium | High | Ensure email/SMS/chat alerting is reliable and monitored; measure the alert-channel adequacy KPI; consider web push before considering an app. |
| IR-3 | **Leadership expectation gap** — an executive assumes a phone app exists. | Medium | Low | Communicate the position; demonstrate the responsive web app on a phone. |
| IR-4 | **Mobile web experience degrades** unnoticed because nobody tests it, creating latent pressure for an app. | Medium | Medium | Include iOS Safari in the web app's tested browser matrix (already specified in the web BRD); test at 414 px and 360 px each release. |
| IR-5 | **A reactive, unplanned mobile build** is commissioned under pressure without a business case. | Low | High | BR-iOS-22 requires a written, signed-off business case before any build is authorised. |

### 9.2 Risks that would attach to building an iOS app

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| IR-6 | **Ongoing maintenance burden** — annual OS releases, deprecations, device-size changes, toolchain upgrades, with no corresponding feature value. | High | Medium | Scope narrowly (alerting and triage only); budget maintenance explicitly; reassess annually against usage. |
| IR-7 | **Feature-parity creep** — pressure to reproduce the whole web app on a phone. | High | High | Hard scope boundary in BR-iOS-11 and §5.3; every addition requires a written justification. |
| IR-8 | **Contract drift between two clients** — a backend change breaks the app but not the web, or vice versa. | High | High | Shared, versioned API contract with schema validation on both clients; contract tests in CI covering both. |
| IR-9 | **App Store review rejection or policy change** delays or blocks release. | Medium | Medium | Private distribution via Apple Business Manager reduces exposure; complete a guideline checklist before submission. |
| IR-10 | **Platform data on personal devices** increases the breach surface. | Medium | High | Keychain-only credential storage, biometric gate, auto-lock on background, remote sign-out, MDM requirement for privileged roles. |
| IR-11 | **Notification fatigue** — over-alerting trains users to ignore pushes. | High | Medium | Severity thresholds, per-user notification preferences, digest batching for non-urgent classes. |
| IR-12 | **Cross-platform framework choice locks in a wrong bet** (React Native vs Flutter vs native Swift). | Medium | Medium | Decide against explicit criteria (team skills, Android intent, native-capability depth) and record an architecture decision. |
| IR-13 | **No macOS build capacity** in a Windows-based development environment. | High | Medium | Provision a Mac build machine or a hosted macOS CI runner as a prerequisite, budgeted in the business case. |
| IR-14 | **Two release cadences diverge** — the app lags backend capability and misrepresents platform state. | Medium | Medium | Version the API; make the app degrade gracefully against a newer backend; enforce a minimum-supported-app-version check. |
| IR-15 | **Security review of an internal tool on mobile** becomes a recurring compliance obligation. | Medium | Medium | Budget for annual mobile security review; define the device-management baseline up front. |

---

## 10. Current Implementation Status

### 10.1 Platform existence statement — iOS

> **No Kailash iOS application exists.**
>
> As of 2026-07-31, at product HEAD commit `40cca17`, the directory `C:\Go4Garage( Eka)\Kailash-Ai\ios_app_kailash_ai\` contains **only two empty subdirectories**: `deployed/` and `not_deployed/`. There are no source files of any kind.
>
> Specifically, there is:
> - **No Xcode project or workspace** (`.xcodeproj`, `.xcworkspace`)
> - **No Swift or Objective-C source**
> - **No React Native, Expo or Flutter project** (no `ios/` platform folder, no `pubspec.yaml`, no `app.json`, no `metro.config.js`)
> - **No `Info.plist`, no bundle identifier, no entitlements file**
> - **No Podfile, no Swift Package manifest, no `GoogleService-Info.plist`**
> - **No App Store Connect record, no TestFlight build, no provisioning profile, no signing certificate**
> - **No iOS-related CI job** — `.github/workflows/ci.yml` defines `lint`, `shared`, `services`, `backend`, `frontend` and `compose-build`; there is no mobile job
> - **No APNs configuration anywhere in the backend** — no push service, no device-token model, no notification dispatch code
>
> Kailash is presently a **backend and web-only internal service**. This is by design, not by omission: it is an internal ML/AI platform consumed by other Go4Garage products over HTTP, with a single human-facing React 19 web dashboard. **No dedicated mobile client is planned**, unless the reader, on reviewing the decision criteria in §11.1, decides otherwise.

### 10.2 What exists instead

| Surface | Status | Location |
|---|---|---|
| **Backend (FastAPI)** | **Built and run locally** — populated `.venv`, roughly 24 API routers, 20 department agents, 3 guardians, 9 platform services | `Kailash-Ai/backend/` |
| **Web app (React 19)** | **Built and compiled** — roughly 70 page modules, populated `node_modules/`, compiled `build/` output, Firebase Hosting configuration | `Kailash-Ai/frontend/` |
| **iOS app** | **Does not exist** — two empty placeholder directories | `Kailash-Ai/ios_app_kailash_ai/` |
| **Android app** | **Does not exist** — two empty placeholder directories | `Kailash-Ai/android_app_kailash_ai/` |

### 10.3 iOS access available today

An iOS user reaches Kailash through **mobile Safari against the web application**. Per the web app's browser matrix, iOS Safari (current and previous major version) is supported for read journeys and core actions, and the responsive requirements specify readable, navigable layouts down to 360 px with no horizontal overflow of primary content.

What that gives an iOS user today: dashboard, departments and department detail, tasks, analytics, reports, GANESHA chat, knowledge base and the policy corpus — all in the browser.

What it does not give: an app icon, APNs push notifications, offline access, Face ID unlock, camera capture, or background execution.

### 10.4 Prerequisites, were a build ever approved

| # | Prerequisite | Status |
|---|---|---|
| 1 | Written, approved business case per BR-iOS-22 | Not started |
| 2 | Apple Developer Program membership | Not held (unverified) |
| 3 | Apple Business Manager enrolment for private distribution | Not held (unverified) |
| 4 | macOS build capacity (physical Mac or hosted macOS CI) | Not available in the observed Windows environment |
| 5 | Framework decision (native Swift/SwiftUI vs React Native vs Flutter) recorded as an ADR | Not made |
| 6 | Backend push infrastructure — device-token model, APNs credentials, dispatch service | **Does not exist** in the backend |
| 7 | Versioned, schema-validated API contract shared across clients | Partially — the `ApiResponse` envelope exists; no client-side schema validation |
| 8 | Mobile engineering capacity | Not allocated |
| 9 | Device-management (MDM) baseline for privileged roles | Not defined |

---

## 11. Roadmap / Milestones

### 11.1 Near term (0 to 3 months) — *hold the position and measure*

| # | Milestone | Success criterion |
|---|---|---|
| IN-1 | **Record the position visibly.** Place a short README in `ios_app_kailash_ai/` stating that no app exists and pointing to this BRD. | No reader mistakes the empty directory for lost work. |
| IN-2 | **Define the decision criteria** (below) and socialise them with leadership. | Written, agreed trigger conditions. |
| IN-3 | **Verify mobile web quality on iOS.** Test the core read journeys in iOS Safari at 414 px and 360 px. | Documented pass/fail per journey; defects raised against the web app, not against a hypothetical native app. |
| IN-4 | **Audit alert-channel reliability.** Confirm time-critical platform alerts reliably reach on-call staff by existing means. | Alert-channel adequacy KPI measured at 95% or better. |
| IN-5 | **Instrument mobile web demand.** Measure iOS-originated web sessions and log unmet mobile requests. | A demand signal exists to inform any future decision. |

**Decision criteria — an iOS client is reconsidered only if all four hold:**

1. iOS-originated mobile web sessions exceed a sustained, material share of total sessions for three consecutive months.
2. A specific, repeatable work task is demonstrably impossible or unacceptably slow in mobile web.
3. The alerting need is proven not satisfiable by email, SMS, chat integration or web push.
4. Mobile engineering capacity exists that does not displace the Automobile-LLM moat, consumer-product integration or production hardening.

### 11.2 Mid term (3 to 9 months) — *cheaper alternatives before an app*

| # | Milestone | Success criterion |
|---|---|---|
| IM-1 | **Improve the mobile web experience** at the phone breakpoints — larger touch targets, collapsed dense tables, a mobile-first executive read view. | Core read journeys complete comfortably at 360 px. |
| IM-2 | **Evaluate web push and PWA installability** as a materially cheaper route to the two genuine native benefits (icon, notifications). | A written comparison of PWA versus native cost and capability. |
| IM-3 | **Build backend notification infrastructure channel-agnostically** — a device/subscription model and a dispatch service that can target email, SMS, web push or, later, APNs. | Alerts deliverable through at least two channels without a client. |
| IM-4 | **Harden the API contract** with schema validation and versioning, so that any future second client inherits safety rather than risk. | Contract tests in CI; a breaking backend change fails the build. |
| IM-5 | **Re-evaluate against the decision criteria.** | A dated written decision: build, defer, or close. |

### 11.3 Long term (9 to 24 months) — *conditional build path*

Applicable **only** if the §11.1 criteria are met and a business case is approved.

| # | Milestone | Success criterion |
|---|---|---|
| IL-1 | **Framework decision recorded as an ADR** (native SwiftUI, React Native, or Flutter), weighing team skills, Android intent and native-capability depth. | Signed ADR. |
| IL-2 | **Provision the build environment** — Apple Developer Program, Apple Business Manager, macOS CI capacity, signing and provisioning. | A signed build produced by CI. |
| IL-3 | **Backend APNs support** — device-token registration, APNs credentials, notification dispatch with deep-link payloads. | A test push reaches a device and deep-links correctly. |
| IL-4 | **MVP: alerting and triage only** — auth with 2FA and biometric unlock, push with deep links, executive read view, alert feed, task acknowledge/assign/status. | All MVP-scoped requirements in §6.2 verified. |
| IL-5 | **TestFlight beta** with a defined internal tester group. | Crash-free session rate 99.5% or better; feedback triaged. |
| IL-6 | **Private production release** via Apple Business Manager. | 80% or better install rate among the intended group within 60 days. |
| IL-7 | **Post-launch review at 6 months** against the §7.2 KPIs. | A written decision to continue, narrow or retire the app. |

---

## 12. Appendix

### 12.1 Parent product documents

This application-level BRD narrows the Kailash platform requirements to the iOS surface — a surface that does not currently exist. The authoritative product-level documents are:

| Document | Location |
|---|---|
| **`BRD_kailash_ai.md`** | `../BRD_kailash_ai.md` — product-level business requirements for the whole Kailash platform |
| **`TRD_kailash_ai.md`** | `../TRD_kailash_ai.md` — product-level technical requirements, including the backend API any client would consume |

Its direct companion is **`TRD_ios_app_kailash_ai.md`** in this same directory, which sets out the conditional technical design.

Sibling surfaces: `../web_app_kailash_ai/` (the one client that does exist) and `../android_app_kailash_ai/` (which records the equivalent no-app position for Android).

### 12.2 Directory contents, verbatim

```
ios_app_kailash_ai/
├── deployed/            (empty)
├── not_deployed/        (empty)
├── BRD_ios_app_kailash_ai.md   ← this document
└── TRD_ios_app_kailash_ai.md
```

No application source of any kind is present.

### 12.3 What the web app already provides on iOS

| Capability | Mobile Safari | Native app would add |
|---|---|---|
| Dashboard, departments, tasks, analytics, reports | Yes | Phone-optimised layout |
| GANESHA chat | Yes | Nothing material |
| Knowledge base | Yes | Nothing material |
| Policy corpus | Yes | Nothing — these are public web URLs by design |
| App icon on home screen | Only via "Add to Home Screen" (no manifest present) | Proper installability |
| Push notifications | No (no service worker present) | **APNs push** |
| Offline access | No | Cached read (of limited value on live data) |
| Biometric unlock | Possible via WebAuthn | **Face ID / Touch ID** natively |
| Camera capture | Via file input | Native camera integration |
| Background execution | No | Background refresh |

Four genuine additions; two of them (push, biometric) have web-based alternatives.

### 12.4 Glossary

| Term | Meaning |
|---|---|
| **APNs** | Apple Push Notification service |
| **TestFlight** | Apple's pre-release distribution and beta testing service |
| **Apple Business Manager** | Apple's private/custom app distribution channel for organisations |
| **HIG** | Apple's Human Interface Guidelines |
| **MDM** | Mobile Device Management |
| **Dynamic Type** | iOS user-controlled text sizing that apps must respect |
| **Keychain** | iOS secure credential storage |
| **ADR** | Architecture Decision Record |
| **PWA** | Progressive Web App — an installable, offline-capable web app; a cheaper alternative to a native client |

### 12.5 Open questions for the document owner

1. Does Go4Garage hold an Apple Developer Program membership, and is Apple Business Manager enrolled?
2. Is there macOS build capacity available, or would it need provisioning?
3. Are time-critical Kailash alerts currently reaching on-call staff reliably, and through which channel?
4. Has any staff member actually requested a Kailash mobile app, and for what specific task?
5. Should the cheaper PWA route (installability plus web push) be evaluated before any native decision?
6. If a mobile client is ever built, is Android the higher priority given the Indian device market?
7. Who would own and maintain a mobile codebase, given the current team's composition?

---

## Section 4 — Web App
### 4.1 Business Requirements Document — Kailash-Ai Web Application

## 1. Document Control

| Field | Value |
|---|---|
| **Document title** | Business Requirements Document — Kailash-Ai Web Application |
| **Product** | Kailash — Go4Garage internal ML/AI platform |
| **Surface** | Web application (browser client) — `frontend/` in the Kailash repository |
| **Document type** | BRD (Application level) |
| **Version** | 1.0 |
| **Date** | 2026-07-31 |
| **Status** | Draft |
| **Owner** | TBD |
| **Author** | Go4Garage Documentation Workstream |
| **Reviewers** | TBD (Frontend Lead, Platform Lead, Design, Compliance) |
| **Approvers** | TBD |
| **Classification** | Internal — Proprietary |
| **Parent product BRD** | `../BRD_kailash_ai.md` |
| **Parent product TRD** | `../TRD_kailash_ai.md` |
| **Companion document** | `TRD_web_app_kailash_ai.md` (same directory) |
| **Source of truth** | `C:\Go4Garage( Eka)\Kailash-Ai\frontend`, HEAD commit `40cca17` dated 2026-07-31 |

### 1.1 Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-31 | Documentation Workstream | Initial draft, scoped to the web surface only |

---

## 2. Executive Summary

The Kailash web application is the **only human-facing surface of the Kailash platform**. It is a React 19 single-page application that gives Go4Garage staff a browser-based cockpit over the platform's AI departments, guardian orchestration, tasks, analytics, knowledge base and automobile-domain intelligence. Everything a person can do with Kailash, they do here — there is no desktop client, no CLI product, and no mobile app.

The application ships roughly **70 page modules** under `frontend/src/pages/`, split into two distinct families. The first is the **operational cockpit**: roughly 21 authenticated routes including a login gate, the main Kailash dashboard, GANESHA chat (v1 and v2), department listing and per-department detail, tasks, GAPS/task management, analytics, GANESHA analytics, reports, knowledge base, guardians, users, settings, an automobile pricing surface, an executive dashboard, an investor-facing executive dashboard, and product-adjacent views for GST, Ignition, Urjaa and a tattoos tool. The second family is a **published policy and compliance corpus** of roughly 35 static pages — privacy, terms, cookies, disclaimer, acceptable use, intellectual property, DMCA, age restriction, GDPR, CCPA, data retention, data breach, data transfer, sub-processors, user rights, SLA, refund, shipping, warranty, API terms, OEM/SG registration, community and moderator guidelines, code of conduct, ethics, security policy, incident response, penetration testing, bug bounty, accessibility statement, compliance and transparency.

Technically the client is built with Create React App wrapped by CRACO, styled with Tailwind CSS and Radix UI primitives, animated with Framer Motion, and enhanced with a Three.js / react-three-fiber visualisation layer. Server state is managed with TanStack Query, client state with Zustand, forms with React Hook Form and Zod, and HTTP with Axios against the FastAPI backend. It is deployed as static assets to **Firebase Hosting** (project `kailash-38268`) with SPA rewrites, immutable long-lived caching on hashed assets, and a hardened security-header set.

The application has genuinely been built: `frontend/node_modules/` is populated with roughly 1,000 packages and `frontend/build/` contains a compiled bundle including `index.html`, hashed `static/` assets, brand video files and Open Graph imagery.

This BRD covers the web surface only. Backend capability, data model and platform-wide requirements live in the parent product documents.

---

## 3. Business Objectives & Strategic Fit

### 3.1 Why a web app, and why only a web app

Kailash's users are Go4Garage staff performing analytical, supervisory and administrative work: reading dashboards, comparing forecasts, reviewing anomalies, triaging tasks, curating knowledge, and administering users and roles. That work is dense, multi-panel, keyboard-driven and desk-bound. A browser client on a large screen is the correct medium for it, and the absence of a mobile app is a deliberate consequence of that user profile rather than a gap.

The web app also carries a second, non-obvious job: it is where Go4Garage's **published legal and compliance posture** lives. Roughly half the page count is policy content, and it is the artefact an auditor, a partner or an investor would be shown.

### 3.2 Objectives

| # | Objective | How the web app serves it |
|---|---|---|
| **WO-1** | **Make platform capability usable without engineering.** | Every department, guardian and analytics capability reachable through a UI, so non-engineers exercise the platform directly rather than filing tickets. |
| **WO-2** | **Give leadership a single operational picture.** | Executive dashboard, investor executive dashboard, analytics and reports consolidate portfolio health in one place. |
| **WO-3** | **Make the AI conversational and explainable.** | GANESHA chat (v1 and v2) plus GANESHA analytics let a user ask, see which departments answered, and inspect orchestration behaviour. |
| **WO-4** | **Turn the knowledge layer into a curatable asset.** | The knowledge base view makes the RAG corpus visible and maintainable by domain SMEs. |
| **WO-5** | **Provide the administrative control plane.** | Users, RBAC and settings administration performed in-browser by an admin, not by a database edit. |
| **WO-6** | **Surface automobile-domain commercial intelligence.** | The automobile pricing view exposes the pricing engine, market data and GST treatment to commercial staff. |
| **WO-7** | **Publish and maintain Go4Garage's compliance posture.** | Roughly 35 policy pages covering privacy, data protection, security, community and commercial terms. |
| **WO-8** | **Present the platform credibly to investors and partners.** | Investor executive dashboard plus branded video and Open Graph assets in the build output. |
| **WO-9** | **Cost-efficient delivery.** | Static hosting on a CDN with immutable caching keeps the human surface effectively free to serve relative to backend compute. |

### 3.3 Strategic fit

The parent BRD identifies Kailash's value as leverage across the Go4Garage portfolio. The web app is where that leverage becomes visible to the business: a forecast is only worth what a manager does with it, and an anomaly is only worth the investigation it triggers. The web app converts platform capability into organisational action, and it does so with zero marginal infrastructure cost per user.

---

## 4. Target Users / Personas / Stakeholders

### 4.1 Personas and their journeys

| Persona | Primary journey in the web app | Key routes |
|---|---|---|
| **Operations manager** | Log in → dashboard → scan department status → open a flagged department → create or reassign a task → track it to closure | `/`, `/kailash`, `/departments`, `/department/:name`, `/tasks`, `/management` |
| **Business analyst** | Log in → analytics → filter and compare → open reports → export a view for a stakeholder | `/analytics`, `/reports`, `/ganesha-analytics` |
| **Executive** | Log in → executive dashboard → portfolio-level rollups → drill into a single metric | `/dashboard/executive`, investor executive dashboard |
| **Platform / AI engineer** | Log in → GANESHA chat v2 → test an orchestration → check guardians → inspect system health | `/ganesha`, `/ganesha-v2`, `/chat`, `/guardians` |
| **Domain SME** | Log in → knowledge base → review ingested knowledge and digests → flag stale content | `/knowledge-base` |
| **Commercial / pricing staff** | Log in → automobile pricing → price a part or vehicle → review GST/HSN treatment | `/automobile` |
| **Administrator** | Log in → users → create or deactivate an account → assign a role → adjust settings | `/users`, `/settings` |
| **Compliance officer / external reviewer** | Reach a policy page directly by URL → read the current position → cite it | `/privacy`, `/gdpr-compliance`, `/data-retention`, `/security-policy`, `/transparency`, and roughly 30 others |
| **Consumer-product engineer** | Log in → view the platform they depend on → check department and system health before blaming their own service | `/kailash`, `/guardians`, health views |

### 4.2 Stakeholders

| Stakeholder | Interest in the web app |
|---|---|
| Go4Garage leadership | Executive and investor dashboards; the platform's public face |
| Platform engineering | The surface they must keep in sync with backend API changes |
| Design | Visual consistency across roughly 70 pages built with Radix and Tailwind |
| Compliance / Legal | Currency and accuracy of the roughly 35 policy pages |
| Finance | Hosting cost (currently minimal — static CDN) |
| Consumer-product teams | Visibility into the shared platform's health |

### 4.3 Access model

The application is **not** a public product. Access requires an account provisioned by an administrator, authenticated at `/`, with role-based visibility thereafter. Policy pages are the exception — they are reachable without authentication, by design, since their purpose is to be citable.

---

## 5. Scope

### 5.1 In scope

**Authenticated operational surface**

- Login gate at `/` with session establishment and, where enabled, a two-factor challenge.
- Main dashboard at `/kailash` (with `/dashboard` and `/applications` redirecting to it).
- Departments list at `/departments` and per-department detail at `/department/:name`.
- GANESHA conversational surfaces: `/ganesha`, `/ganesha-v2`, `/chat`.
- GANESHA analytics at `/ganesha-analytics`.
- Guardians view at `/guardians`.
- Tasks at `/tasks` and GAPS/task management at `/management`.
- Analytics at `/analytics` and reports at `/reports`.
- Knowledge base at `/knowledge-base`.
- Users administration at `/users` and settings at `/settings`.
- Automobile pricing at `/automobile`.
- Executive dashboard at `/dashboard/executive`, plus the investor-facing executive dashboard.
- Product-adjacent views: `/gst`, `/ignition`, `/urjaa`, `/tattoos`.

**Public policy surface (roughly 35 pages)**

- Core legal: terms and conditions, privacy policy, cookie policy, disclaimer, acceptable use, intellectual property, DMCA, age restriction.
- Data protection: GDPR compliance, CCPA compliance, data retention, data breach, data transfer, sub-processor list, user rights.
- Commercial: SLA, refund policy, shipping policy, warranty policy, API terms, OEM/SG registration.
- Community: community guidelines, moderator guidelines, code of conduct, ethics.
- Security: security policy, incident response, penetration testing, bug bounty.
- Assurance: accessibility statement, compliance, transparency.

**Cross-cutting**

- Role-aware navigation and view gating consistent with backend RBAC.
- Responsive layout across desktop, laptop and tablet breakpoints, with tablet-usable read paths.
- Light/dark theming.
- Toast notifications and consistent form validation.
- Branded assets: intro/HD/optimised video, Open Graph image set, favicon.
- Static deployment to Firebase Hosting with SPA rewrites, caching and security headers.

### 5.2 Out of scope

- **Any native mobile application.** See §10.2. The web app is responsive; it is not packaged for an app store.
- **A Progressive Web App with offline capability.** No service worker or manifest-driven install flow is in scope for v1 (see §11 for the considered position).
- **Public self-service signup, billing or payment collection.** No payment gateway exists anywhere in Kailash.
- **A public marketing website.** Go4Garage's marketing presence is a separate property; only the policy corpus here is publicly reachable.
- **Direct database or model-provider access from the browser.** All data flows through the backend API; the client never holds an AI vendor key.
- **Server-side rendering.** The app is a client-rendered SPA served from static hosting.
- **Rich text/document authoring.** Knowledge ingestion is a backend script path, not an in-browser editor, in v1.
- **Real-time collaborative editing.** Not a requirement for this user base.

---

## 6. Business Requirements

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| **WBR-1** | The web app **shall be the complete human interface to Kailash** — every capability an authenticated user is entitled to exercise shall be reachable through the UI without recourse to `curl`, the OpenAPI page, or direct database access. | Must | Walk the permission matrix; for each granted permission, identify the UI route that exercises it. Any permission with no UI path is a defect. |
| **WBR-2** | The web app **shall gate all operational content behind authentication**, redirecting unauthenticated users to the login route, while leaving the policy corpus publicly reachable by design. | Must | Request each operational route with no session — all redirect to `/`. Request each policy route with no session — all render. |
| **WBR-3** | The web app **shall render only what the signed-in user's role permits**, hiding or disabling actions the backend would reject, so that a `viewer` never sees a control that will fail. | Must | Log in as each of the five roles; capture the visible navigation and action set; confirm no visible control produces an authorisation error when used. |
| **WBR-4** | The web app **shall present department status and detail for every registered department**, with a detail view reachable at a stable per-department URL. | Must | The count of departments listed equals the backend registry count; `/department/:name` resolves for each; an unknown name shows a friendly not-found state, not a blank screen or crash. |
| **WBR-5** | The web app **shall provide a conversational interface to GANESHA** that shows the user's question, the composed answer, and which departments were engaged, with conversation history retrievable across sessions. | Must | Ask a multi-department question; the response names the departments engaged; log out and back in; the conversation is still listed. |
| **WBR-6** | The web app **shall provide task and GAPS management** — create, view, assign, update status and close — with changes persisted and reflected on the dashboard. | Must | Create a task, assign it, close it; confirm dashboard counts update and the item appears in the activity trail. |
| **WBR-7** | The web app **shall provide analytics and reporting views** that render populated data for the current period and support filtering by department and by date range. | Must | Load analytics against a seeded dataset; apply a department and date filter; confirm the rendered figures change consistently with the filter. |
| **WBR-8** | The web app **shall provide an executive dashboard and an investor-facing dashboard** that summarise platform and portfolio health in a form presentable without further explanation. | Must | An executive-role user reaches both views and every tile renders a real value or an explicit "no data" state — never a spinner that never resolves or a raw error. |
| **WBR-9** | The web app **shall surface the knowledge base**, showing what knowledge exists, how recent it is, and which department it belongs to. | Should | Open the knowledge base; entries display department attribution and a date; the newest dated digest is visible. |
| **WBR-10** | The web app **shall provide user and role administration** — create, view, update, deactivate users and assign roles — restricted to administrator roles. | Must | An admin performs the full lifecycle; a non-admin cannot reach the view or perform the action. |
| **WBR-11** | The web app **shall provide the automobile pricing surface**, returning a priced result with the market adjustment and the applicable HSN/GST treatment shown to the user. | Should | Price a representative part; the result displays base price, adjustment, HSN code and GST amount. |
| **WBR-12** | The web app **shall publish the full policy corpus** — at minimum privacy, terms, cookies, disclaimer, acceptable use, intellectual property, DMCA, age restriction, GDPR, CCPA, data retention, data breach, data transfer, sub-processors, user rights, SLA, refund, shipping, warranty, API terms, community guidelines, moderator guidelines, code of conduct, ethics, security policy, incident response, penetration testing, bug bounty, accessibility statement, compliance, and transparency — each at a stable, linkable URL. | Must | Every listed route returns substantive content at a permanent URL. |
| **WBR-13** | Each policy page **shall carry a visible effective date and an owning function**, and shall be reviewed at least annually. | Should | Inspect each page for a date and owner; maintain a review register. |
| **WBR-14** | The web app **shall be usable on the browsers Go4Garage staff actually use** — the two most recent major versions of Chrome, Edge, Firefox and Safari on desktop, and current mobile Safari and Chrome for read-only access. | Must | Execute the core journey matrix (§7.6 of the companion TRD) on each supported browser. |
| **WBR-15** | The web app **shall be responsive from 1920 px down to 768 px for full functionality, and shall remain readable and navigable down to 360 px** for consultation on a phone, with no horizontal scrolling of primary content. | Must | Test at 1920, 1440, 1280, 1024, 768, 414 and 360 px; confirm no clipped controls or horizontal overflow on primary content. |
| **WBR-16** | The web app **shall meet WCAG 2.1 Level AA** for the authenticated operational surface and the public policy corpus — keyboard operability, visible focus, sufficient contrast, correct labelling and landmark structure. | Should | Automated audit (axe or Lighthouse) reports no Level AA violations on a representative page sample; manual keyboard-only traversal completes the core journeys. |
| **WBR-17** | The web app **shall load fast enough not to obstruct work** — first contentful paint under 2 s and interactive under 4 s on a typical office connection, with static assets served immutably from a CDN. | Should | Lighthouse performance run against the production deployment; verify `Cache-Control: public, max-age=31536000, immutable` on hashed assets. |
| **WBR-18** | The web app **shall communicate state honestly** — every asynchronous view shall render a loading state, an empty state and an error state, and shall never leave a user staring at an indefinite spinner or a blank panel. | Must | Force a slow response, an empty dataset and a backend error on each major view; confirm all three states render. |
| **WBR-19** | The web app **shall never expose secrets to the browser** — no AI provider key, no service-account credential, no database connection string shall appear in the bundle, in network payloads or in client storage. | Must | Grep the production bundle for credential patterns; inspect network traffic and browser storage after a full session. Expect zero findings. |
| **WBR-20** | The web app **shall be deployable as an immutable static build with a single documented command**, and any deployment shall be reversible to the previous version. | Must | Run the documented deploy command from a clean checkout; confirm the live site updates; roll back and confirm restoration. |
| **WBR-21** | The web app **shall present a coherent Go4Garage/Kailash brand** across all pages — consistent typography, colour, spacing and iconography, with light and dark modes both complete. | Should | Design review across a representative sample of both page families in both themes. |
| **WBR-22** | The web app **shall support the platform's SEO and social-preview needs for its public policy pages only**, with correct titles, descriptions and Open Graph imagery, while keeping authenticated surfaces out of search indexes. | Should | Inspect meta tags and Open Graph assets on policy pages; confirm authenticated routes are excluded from indexing. |

---

## 7. Success Metrics / KPIs

### 7.1 Adoption

| KPI | Definition | Target |
|---|---|---|
| Weekly active internal users | Distinct authenticated users per week | Growing to cover the full intended staff group |
| Route coverage | Share of the roughly 21 authenticated routes visited at least monthly | 80% or better — unvisited routes are candidates for removal |
| Self-service rate | Share of routine platform questions answered in-app rather than by asking an engineer | 80% or better |
| Executive dashboard usage | Distinct leadership users per month | Every intended leadership user at least monthly |

### 7.2 Experience and quality

| KPI | Definition | Target |
|---|---|---|
| First contentful paint | Lighthouse FCP on the production deployment | Under 2 s |
| Time to interactive | Lighthouse TTI | Under 4 s |
| Lighthouse performance score | Production, desktop profile | 85 or better |
| Lighthouse accessibility score | Production, representative sample | 90 or better |
| WCAG 2.1 AA violations | Automated audit findings | 0 on audited pages |
| Client-side error rate | Uncaught JavaScript errors per 1,000 sessions | Under 5 |
| Broken-state incidents | Views rendering an indefinite spinner or blank panel, reported per month | 0 |

### 7.3 Reach and compatibility

| KPI | Definition | Target |
|---|---|---|
| Supported-browser pass rate | Core journeys passing on each browser in the support matrix | 100% |
| Responsive defects | Layout defects reported at any supported breakpoint | 0 open at release |
| Tablet read-path success | Core read journeys completable on a 768 px viewport | 100% |

### 7.4 Delivery and operations

| KPI | Definition | Target |
|---|---|---|
| Build success rate | Green `yarn build` runs in CI | 95% or better |
| Deploy frequency | Frontend deployments per month | At least fortnightly during active development |
| Rollback time | Time to restore the previous version | Under 15 minutes |
| Bundle size regression | Increase in main bundle size per release | Under 5% without written justification |
| Policy currency | Policy pages reviewed within 12 months | 100% |

---

## 8. Assumptions & Constraints

### 8.1 Assumptions

| # | Assumption | If false |
|---|---|---|
| WA-1 | Users work primarily on desktop or laptop browsers on office or home broadband. | Mobile-first redesign and offline capability become necessary. |
| WA-2 | The backend API contract is stable, versioned, and changes are communicated before release. | The SPA breaks on backend deploys; contract testing becomes mandatory. |
| WA-3 | Firebase Hosting remains the deployment target and satisfies performance and residency expectations. | Hosting migration required (self-hosted CDN or alternative provider). |
| WA-4 | Users have modern evergreen browsers; no Internet Explorer or legacy support is required. | Polyfill and transpilation targets widen; bundle size grows. |
| WA-5 | The policy corpus is drafted and maintained by Legal/Compliance, not by engineering. | Engineering absorbs unbudgeted content maintenance. |
| WA-6 | No offline access is needed because all data is live platform state. | A service worker and caching strategy must be designed. |
| WA-7 | Session-based JWT auth in the browser is acceptable for an internal tool on trusted networks. | Stronger client-side session protections and shorter token lifetimes are required. |
| WA-8 | The Three.js visualisation layer is a differentiator worth its bundle cost. | It should be lazy-loaded or removed. |

### 8.2 Constraints

| # | Constraint | Nature |
|---|---|---|
| WC-1 | Build toolchain is Create React App 5.0.1 via CRACO — a maintenance-mode path for a React 19 application. | Technical debt |
| WC-2 | Client-rendered SPA only; no SSR, so public policy pages rely on client rendering for crawlers. | Architectural |
| WC-3 | Static hosting means all dynamic behaviour requires a live backend; there is no server-side fallback. | Architectural |
| WC-4 | The design system is Radix primitives plus Tailwind — component choices must stay within it for consistency. | Design |
| WC-5 | Roughly 70 page modules with a small team means consistency must be enforced by shared components, not by discipline alone. | Resource |
| WC-6 | Bundle weight is influenced by Three.js, Framer Motion, the Firebase client SDK and 26 Radix packages. | Performance |
| WC-7 | Content in the policy corpus has legal significance; engineering must not edit it unilaterally. | Governance |
| WC-8 | Yarn 1.22.22 is the declared package manager; lockfile discipline is required. | Tooling |

---

## 9. Risks & Mitigations

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| WR-1 | **Backend contract change breaks the SPA silently** — a renamed field yields a blank panel rather than an error. | High | High | Typed API client with runtime validation (Zod is already a dependency); contract tests in CI; explicit error states (WBR-18). |
| WR-2 | **Bundle bloat degrades load time** as pages and dependencies accumulate. | High | Medium | Route-level code splitting; lazy-load the Three.js and video-heavy surfaces; enforce a bundle-size budget in CI. |
| WR-3 | **CRA maintenance mode** leaves the build path unsupported and slow. | Medium | Medium | Plan a Vite migration; keep CRACO customisation minimal so migration cost stays bounded. |
| WR-4 | **Inconsistent UX across roughly 70 pages** built at different times by different hands. | High | Medium | Shared component library; design review gate on new pages; visual regression testing. |
| WR-5 | **Policy pages drift out of date** and misrepresent the actual position. | Medium | High | Effective date and owner on every page (WBR-13); annual review register; Legal sign-off in the release checklist. |
| WR-6 | **Accessibility regressions** despite `eslint-plugin-jsx-a11y` being present but not build-blocking. | High | Medium | Promote a11y lint findings to errors; add an automated audit to CI; manual keyboard testing before release. |
| WR-7 | **Client-side auth token exposure** through XSS or careless storage. | Medium | High | Strict security headers (already configured), no `dangerouslySetInnerHTML` on untrusted content, short token lifetime, sanitise any rendered model output. |
| WR-8 | **Rendered model output as an injection vector** — an LLM answer containing markup or a link that executes or misleads. | Medium | High | Treat all model output as untrusted; sanitise before render; never render it as raw HTML. |
| WR-9 | **Backend outage renders the app useless** with no graceful message. | Medium | Medium | A global offline/backend-unreachable banner; retry with backoff; cached last-known values where safe and clearly labelled as stale. |
| WR-10 | **Search engines index authenticated routes** or, conversely, fail to index policy pages because they are client-rendered. | Medium | Low–Medium | `robots` directives excluding app routes; verify policy-page indexing with Search Console; consider prerendering the policy corpus if indexing proves unreliable. |
| WR-11 | **Firebase Hosting dependency** — outage or policy change at the hosting provider. | Low | Medium | Build output is portable static assets; document an alternative hosting path. |
| WR-12 | **Video and image assets inflate the deployment** and slow first load. | Medium | Low | Serve video lazily and only where it adds value; keep it out of the critical path; compress aggressively (an optimised variant already exists). |
| WR-13 | **Role gating implemented only in the UI** creates a false sense of security. | Medium | High | Treat UI gating as ergonomics only; the backend remains the enforcement point; test that hidden actions are also server-rejected. |
| WR-14 | **Tablet and small-screen users hit unusable dense tables.** | Medium | Medium | Responsive table patterns (card collapse or horizontal scroll containers) at the breakpoints in WBR-15. |

---

## 10. Current Implementation Status

*Assessed 2026-07-31 against `C:\Go4Garage( Eka)\Kailash-Ai\frontend`, HEAD `40cca17`.*

### 10.1 Does the web app exist in code?

**Yes.** This is the one Kailash client surface that is genuinely built, compiled and demonstrably run locally.

| Item | Status | Evidence |
|---|---|---|
| Source tree | **Present** | `frontend/src/` with `components/`, `pages/`, `services/`, `stores/`, `hooks/`, `context/`, `data/`, `lib/`, `styles/`, plus `App.js`, `index.js` and stylesheets |
| Page modules | **Present — roughly 70** | `frontend/src/pages/` includes the operational views and the full policy corpus, with dedicated CSS modules for several (Analytics, Chat, Departments, Executive, GaneshaAI, GaneshaChat, GaneshaChatV2, Reports, Settings, Tasks, Urjaa, Users, LegalPages, DepartmentDetail) |
| Routing | **Present** | `App.js` defines roughly 21 authenticated routes plus roughly 35 policy routes, with redirects from `/dashboard` and `/applications` to `/kailash` |
| Dependencies installed | **Confirmed** | `frontend/node_modules/` populated with roughly 1,000 entries |
| Production build | **Confirmed** | `frontend/build/` contains `index.html`, `asset-manifest.json`, hashed `static/`, `favicon.png`, `og-image.png`, `og-image.svg`, `og-background.jpg`, and three video files (`kailash_intro_video.mp4`, `kailash_video_hd.mp4`, `kailash_video_optimized.mp4`) |
| Hosting configuration | **Present** | `frontend/firebase.json` with SPA rewrite, immutable static caching and a full security-header set |
| Deploy scripts | **Present** | `yarn firebase:deploy` and `yarn firebase:preview` in `package.json` |
| CI coverage | **Present** | The `frontend` job in `.github/workflows/ci.yml` runs `yarn install` and `yarn build`; `deploy-frontend.yml` exists |
| Lint tooling | **Present** | ESLint 9.23.0 with react, import and `jsx-a11y` plugins |

### 10.2 Platform existence statement — WEB

> **The Kailash web application EXISTS in code and has been built.** It is a React 19 single-page application located at `Kailash-Ai/frontend/`, with an installed dependency tree and a compiled production bundle present on disk. It is the platform's only human-facing client. There is no native mobile counterpart — see `../ios_app_kailash_ai/BRD_ios_app_kailash_ai.md` and `../android_app_kailash_ai/BRD_android_app_kailash_ai.md`, both of which record that no mobile client exists or is planned.

### 10.3 Not verified or not present

| Item | Honest status |
|---|---|
| **Live production deployment** | `firebase.json` targets project `kailash-38268`, and `backend/.env.example` lists `kailash-ai.in`, `www.kailash-ai.in`, `kailash-38268.web.app` and `kailash-38268.firebaseapp.com` as allowed origins. **Whether the site is currently live was not verified from this working copy.** |
| **PWA capability** | No service worker, no web app manifest, no install prompt found. The app is not installable and has no offline capability. |
| **Automated frontend tests** | `craco test` is wired as a script, but no meaningful test suite was found under `frontend/src/`. CI verifies that the bundle builds, not that it behaves. |
| **Accessibility conformance** | `eslint-plugin-jsx-a11y` is installed; there is no evidence of a formal WCAG audit or of a11y findings being build-blocking. |
| **Performance measurement** | No Lighthouse budget, bundle-size budget or performance regression gate found in CI. |
| **Code splitting** | Not verified. With Three.js, Framer Motion, 26 Radix packages and the Firebase client SDK in the dependency set, route-level splitting matters; no evidence of it was found in the configuration reviewed. |
| **Policy page currency** | Roughly 35 policy pages exist as components. Whether each carries an effective date and a named owner, and when each was last legally reviewed, was not verified. |
| **Analytics / RUM** | No product analytics or real-user-monitoring integration was found in the client. |
| **Error tracking** | No client-side error reporting service (Sentry or equivalent) was found. |
| **Design system documentation** | Radix plus Tailwind are used consistently as dependencies, but no Storybook or documented component inventory was found. |

### 10.4 Summary judgement

The web app is **substantially complete as a feature surface and materially under-instrumented as a product**. It has the pages, the routing, the design primitives, a working build and a hardened hosting configuration. What it lacks is the measurement layer: no frontend tests, no accessibility gate, no performance budget, no error tracking, no usage analytics. Those gaps do not stop it working; they stop anyone knowing whether it works well.

---

## 11. Roadmap / Milestones

### 11.1 Near term (0 to 3 months) — *instrument and verify*

| # | Milestone | Success criterion |
|---|---|---|
| WN-1 | **Confirm and document the live deployment.** Establish whether the Firebase-hosted site is live and at which commit. | A dated deployment record naming URL, commit and owner. |
| WN-2 | **Add client-side error tracking.** Capture uncaught errors with release and route context. | Errors visible in a dashboard within one minute of occurrence. |
| WN-3 | **Establish the state contract.** Ensure every asynchronous view renders loading, empty and error states (WBR-18). | Audit sheet covering all roughly 21 authenticated routes, all three states present. |
| WN-4 | **Promote accessibility linting to build-blocking** and run a baseline axe audit on a representative page sample. | Zero new a11y lint errors merge; baseline audit report published. |
| WN-5 | **Set performance and bundle budgets in CI.** | A pull request exceeding the bundle budget fails the build. |
| WN-6 | **Verify the browser support matrix** against the core journey list. | Signed-off compatibility matrix. |
| WN-7 | **Policy corpus audit.** Add an effective date and owning function to every policy page; build a review register. | 100% of policy pages dated and owned. |

### 11.2 Mid term (3 to 9 months) — *harden and refine*

| # | Milestone | Success criterion |
|---|---|---|
| WM-1 | **Route-level code splitting**, lazy-loading the Three.js and video-heavy surfaces. | Main bundle materially smaller; TTI under 4 s. |
| WM-2 | **Frontend test suite** — component tests for shared primitives plus end-to-end coverage of the top five journeys (Puppeteer is already a dev dependency). | Journeys run in CI on every pull request. |
| WM-3 | **Typed, validated API client** using Zod schemas shared with backend contracts. | A backend field rename fails CI rather than producing a blank panel in production. |
| WM-4 | **Responsive refinement for tablet**, especially dense analytics tables. | All core read journeys complete cleanly at 768 px. |
| WM-5 | **Component inventory and design documentation.** | A documented shared component set; new pages composed from it. |
| WM-6 | **Usage analytics** (privacy-respecting, internal-only) to identify unvisited routes. | Route coverage KPI measurable; dead routes identified for removal. |
| WM-7 | **WCAG 2.1 AA conformance** on the operational surface and the policy corpus. | Independent audit reports no Level AA violations. |

### 11.3 Long term (9 to 24 months) — *modernise*

| # | Milestone | Success criterion |
|---|---|---|
| WL-1 | **Migrate off CRA/CRACO** to a maintained build toolchain. | Faster builds, no functional regression, no visual regression. |
| WL-2 | **Decide the PWA question explicitly.** Either implement a service worker with a defined offline read scope and installability, or formally record that the app remains online-only. | A written decision, implemented or recorded. |
| WL-3 | **Consider prerendering or static generation for the policy corpus** so it is reliably indexable and instantly loadable without the SPA shell. | Policy pages served as prerendered HTML with correct meta and Open Graph tags. |
| WL-4 | **Real-time platform state** via streaming or subscriptions for dashboards and GANESHA responses. | Dashboards update without a manual refresh; chat streams tokens. |
| WL-5 | **In-browser knowledge curation**, allowing SMEs to add and correct knowledge without a backend script. | An SME completes an ingestion end to end in the UI. |

---

## 12. Appendix

### 12.1 Parent product documents

This application-level BRD narrows the Kailash platform requirements to the web surface. The authoritative product-level documents are:

| Document | Location |
|---|---|
| **`BRD_kailash_ai.md`** | `../BRD_kailash_ai.md` — product-level business requirements for the whole Kailash platform |
| **`TRD_kailash_ai.md`** | `../TRD_kailash_ai.md` — product-level technical requirements, including the backend API this client consumes |

Its direct companion is **`TRD_web_app_kailash_ai.md`** in this same directory.

The sibling application surfaces are documented in `../ios_app_kailash_ai/` and `../android_app_kailash_ai/`; both record that no native client exists.

### 12.2 Route inventory

**Authenticated operational routes (roughly 21)**

| Route | View |
|---|---|
| `/` | Login |
| `/kailash` | Main Kailash dashboard (target of `/dashboard` and `/applications` redirects) |
| `/departments` | Departments list |
| `/department/:name` | Department detail |
| `/ganesha` | GANESHA AI |
| `/ganesha-v2` | GANESHA chat v2 |
| `/chat` | Chat |
| `/ganesha-analytics` | GANESHA analytics |
| `/guardians` | Guardians |
| `/tasks` | Tasks |
| `/management` | GAPS/task management |
| `/analytics` | Analytics |
| `/reports` | Reports |
| `/knowledge-base` | Knowledge base |
| `/users` | User administration |
| `/settings` | Settings |
| `/automobile` | Automobile pricing |
| `/dashboard/executive` | Executive dashboard |
| `/gst` | GST product view |
| `/ignition` | Ignition product view |
| `/urjaa` | Urjaa view |
| `/tattoos` | Tattoos tool |

**Public policy routes (roughly 35)**

`/terms` · `/privacy` · `/cookie-policy` · `/disclaimer` · `/acceptable-use` · `/intellectual-property` · `/dmca` · `/age-restriction` · `/gdpr-compliance` · `/ccpa-compliance` · `/data-retention` · `/data-breach` · `/data-transfer` · `/subprocessors` · `/user-rights` · `/sla` · `/refund-policy` · `/shipping-policy` · `/warranty-policy` · `/api-terms` · `/oemsg` · `/community-guidelines` · `/moderator-guidelines` · `/code-of-conduct` · `/ethics` · `/security-policy` · `/incident-response` · `/penetration-testing` · `/bug-bounty` · `/accessibility` · `/compliance` · `/transparency`

### 12.3 Browser support matrix (business view)

| Browser | Platform | Support level |
|---|---|---|
| Chrome (current and current−1) | Windows, macOS, Linux | Full — primary |
| Edge (current and current−1) | Windows | Full |
| Firefox (current and current−1) | Windows, macOS, Linux | Full |
| Safari (current and current−1) | macOS | Full |
| Safari | iOS/iPadOS (current and current−1) | Read paths and core journeys |
| Chrome | Android (current) | Read paths and core journeys |
| Internet Explorer | Any | Not supported |

The `package.json` production browserslist target is `>0.2%`, `not dead`, `not op_mini all`, which is consistent with this matrix.

### 12.4 Responsive breakpoints (business view)

| Breakpoint | Class of device | Expectation |
|---|---|---|
| 1920 px and above | Large desktop | Full multi-panel layout |
| 1440 px | Desktop | Full functionality |
| 1280 px | Small desktop / large laptop | Full functionality |
| 1024 px | Laptop / landscape tablet | Full functionality; denser layout |
| 768 px | Tablet portrait | All read journeys; write journeys usable |
| 414 px | Large phone | Consultation and simple actions |
| 360 px | Small phone | Readable and navigable; no horizontal overflow |

### 12.5 Glossary

| Term | Meaning |
|---|---|
| **SPA** | Single-page application — client-rendered, routed in the browser |
| **PWA** | Progressive Web App — installable, offline-capable web application (not implemented) |
| **CRA / CRACO** | Create React App, and the configuration override layer wrapping it |
| **GANESHA** | The orchestrating guardian agent; the conversational entry point in the UI |
| **GAPS** | The task/gap management concept surfaced at `/management` |
| **Policy corpus** | The roughly 35 public legal, compliance and security pages |
| **WCAG 2.1 AA** | The accessibility conformance level targeted |

### 12.6 Open questions for the document owner

1. Is the Firebase-hosted site live today, and at which domain — `kailash-ai.in` or the `web.app` default?
2. Who owns the content of the policy corpus, and when was each page last legally reviewed?
3. Should authenticated routes be explicitly excluded from search indexing, and are policy pages currently indexed?
4. Are the product-adjacent views (`/gst`, `/ignition`, `/urjaa`, `/tattoos`) intended to remain in the Kailash dashboard, or migrate to their own products?
5. Is offline access ever required, or is the online-only position permanent?
6. What is the accepted budget for main bundle size, given the Three.js and video assets?
7. Is a formal WCAG 2.1 AA audit commissioned, and by when?
