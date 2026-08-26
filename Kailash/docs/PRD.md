# Kailash — Product Requirements Document (PRD)

> **Single source of truth.** This is the one and only PRD for the entire
> Kailash project (RULES.md Rule 3). Do not create separate or duplicate PRD
> files — edit this one. Business context lives in [`BRD.md`](./BRD.md);
> technical design lives in [`TRD.md`](./TRD.md).

## 1. Vision — the Center Lake

**Kailash is the central data lake and command center for the entire Eka
software ecosystem** — the single nexus every component, process, and product
routes through, and where each is regulated and monitored in real time. In the
"Center Lake" model, **Kailash is the heart** (the data that pumps through the
organization) and **Eka Brain is the mind** (the AI that decides, orchestrates,
and answers). As a strict protocol, all organizational data flows into Kailash
first; Kailash then dictates how, where, and to which agent or interface it is
distributed.

Kailash is **internal infrastructure**, not a product sold to customers: it
powers the customer-facing products and the internal operations cockpit from one
unified backend and one set of AI capabilities.

## 2. The command dashboard — three tiers

On login, an operator lands on a tiered command dashboard:

| Tier | Purpose | Contents |
| --- | --- | --- |
| **Upper — Governance & Intelligence** | The cognitive/governance engines | **Eka Brain** (AI orchestration), **Shiv** (security / auto-rectification), **Parvati** (workload) |
| **Middle — Analytics & Telemetry** | Live health and performance | End-to-end **pulse diagnostics** across Front-End → API → Back-End; green = healthy, red isolates the exact failing layer per product |
| **Lower — Product Ecosystem** | The shipped products | The six products (§4) |

## 3. The data core — four segments

Kailash's data is partitioned into four segments (nomenclature is intentionally
flexible as the portfolio grows):

| Segment | Function |
| --- | --- |
| **Product** | Lifecycle + operational management of the product lines: per-product BRD/TRD, deployment status, blueprints, and a binary live-vs-pending tracker. |
| **Sprint** | Agile cycles and critical financial-event records: the 18-day sprint artifacts and funding-round documentation. |
| **Company** | Master operational ledger and corporate system-of-record: Day-1 records, statutory financials, and the CA-vs-internal reconciliation dashboard. |
| **Goal** | Forward-looking strategy: missions, milestones, and open-ended planning. |

## 4. Products (the six)

Automotive / multi-brand-workshop focused, each AI-driven via Eka Brain:

| Product | Focus |
| --- | --- |
| **Eka AI** | The core automotive AI assistant (chat over the domain knowledge base). |
| **Website** | The public web presence / marketing + entry surface. |
| **Urja** | EV / energy operations for charging networks and partners. |
| **EV Vidya** | EV knowledge & learning surface. |
| **GST SaaS** | Enterprise-grade GST reconciliation and board dashboard for workshops. |
| **Ignition** | Workshop/charger onboarding, trust scoring, and verification. |

> **Naming note.** The repo adopts these vision names as canonical. Current code
> maps in: Eka Brain ← the Ganesha orchestrator; GST SaaS ← GSTSAAS/`gst`; Urja ←
> URGAA/`urjaa`; Company ← the Go4Garage financials segment. Migration is
> incremental (see TRD); the target names are the baseline.

## 5. Target users

| User | Surface | Primary need |
| --- | --- | --- |
| Multi-brand workshops / operators | Eka AI, Ignition | Instant, domain-precise automotive answers; onboarding & trust scoring |
| EV charging operators & partners | Urja | Uptime, SLA tracking, energy operations |
| Businesses filing GST | GST SaaS | Invoice OCR, reconciliation, fraud detection, board dashboard |
| Learners / field users | EV Vidya, Website | EV knowledge, public information |
| Internal operators / leadership | Kailash command dashboard | Cross-product ops cockpit, telemetry, KPIs, financials |
| Finance / CA | Company segment | Statutory financials, CA-vs-internal reconciliation |

## 6. Eka Brain & the agent matrix

Eka Brain is the centralized intelligence hub, built and deployed inside
Kailash. It runs a matrix of specialized AI agents — dedicated solvers for the
distinct, complex automotive-industry problems, plus generic automotive agents
and custom methodological frameworks for unstructured queries — tuned for
multi-brand-workshop environments. Queries pass through a **multi-gated
filtration**: gate 1 categorizes the domain (passenger car / charging station /
commercial vehicle); gate 2 filters by domain (EV vs ICE), brand, variant, and
year — so retrieval is fast and answers are precise. Agent training is a
continuous function (external routing via VPS/Colab today; native in-Kailash
training a later phase).

## 7. Product goals

1. **One backend, many products.** Every product calls the same Kailash/Eka
   Brain API rather than reimplementing AI.
2. **Domain moat.** An automobile-domain LLM competitors cannot trivially
   replicate.
3. **Statutory-grade finance.** The Company segment is an auditable double-entry
   system-of-record producing Indian statutory financials (GSTR-1/3B, Schedule
   III) that reconcile against the CA/Tally books.
4. **Real-time governance.** End-to-end telemetry so any product's failing layer
   is isolated instantly.
5. **India-first.** Indic locales, GST/HSN knowledge, rupee-native workflows.

## 8. Functional scope

- **Intelligence & governance** — Eka Brain orchestration + the agent matrix;
  Shiv (security/auto-rectification); Parvati (workload).
- **Analytics & telemetry** — FE→API→BE pulse/health per product; performance
  and AI-integration metrics.
- **Data core** — the four segments (Product, Sprint, Company, Goal).
- **Products** — the six (§4).
- **Platform services** — document-ai, forecasting, anomaly, rag,
  vision-gateway, speech, model-registry, knowledge-graph, automobile-llm — each
  an internal microservice behind an internal-token contract.
- **Frontend** — React 19 command dashboard + product surfaces.

## 9. Non-functional requirements

- **Security** — internal-token auth between services; JWT + RBAC for the main
  app; no secrets in the repo (env vars / secret store only).
- **Observability** — every service exposes `/health`, `/metrics`, structured
  JSON logs with a request id; the dashboard renders these as the pulse.
- **Deployability** — one gated CI/CD pipeline, safe from any clean checkout
  (enforced by `scripts/verify/`); no auxiliary workflows (Rule 5).
- **Reliability** — staging precedes production; every deploy is health-verified
  before it counts.
- **Structure** — the repo follows RULES.md (one master folder; department →
  feature; single BRD/TRD/PRD; one agent file; one pipeline) and is enforced.

## 10. Resource prerequisites (launch checklist)

The serverless **Company/financials** segment runs today on Firebase + Supabase
(both provisioned). Running the **full platform** (products + Eka Brain) also
requires, and these must be supplied before that phase:

- **AI-provider key** (`OPENROUTER_API_KEY` or `ANTHROPIC_API_KEY`) — Eka Brain
  and every agent are inert without one.
- **Backend compute host** (`BACKEND_SSH_*`) — to run the FastAPI backend + the
  platform services.
- **MongoDB** (`MONGO_URL`) and **Redis** (`REDIS_URL`).
- **Firebase Admin service account** (`FIREBASE_SERVICE_ACCOUNT_JSON`) — backend
  login verification.
- **Valid AWS credentials** — Route 53 DNS for `api.kailash-ai.in` (current
  session creds are invalid).

## 11. Success metrics

- Products consume Kailash/Eka Brain APIs rather than bespoke AI code.
- Green single pipeline: commit → staging → production, health-verified.
- Statutory financials reconcile against the CA/Tally books with zero silent
  drops (every ingestion error queued, not lost).
- Dashboard telemetry isolates any failing layer to the exact FE/API/BE stage.

## 12. Out of scope

- Selling Kailash itself as a standalone product to third parties.
- Any capability that bypasses the unified backend / Eka Brain contract.
- Ad-hoc files or folders outside the locked repo structure (RULES.md).

## 13. References

- Business requirements: [`BRD.md`](./BRD.md)
- Technical requirements & architecture: [`TRD.md`](./TRD.md)
- Platform architecture: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
- Project rules (read first): [`../../RULES.md`](../../RULES.md)
