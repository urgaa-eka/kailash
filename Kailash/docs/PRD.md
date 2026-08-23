# Kailash — Product Requirements Document (PRD)

> **Single source of truth.** This is the one and only PRD for the entire
> Kailash project. Do not create separate or duplicate PRD files — edit this
> one. Business context lives in [`BRD.md`](./BRD.md); technical design lives in
> [`TRD.md`](./TRD.md).

## 1. Vision

Kailash is the shared AI engine for Go4Garage's EV ecosystem in India. It is
**not** a product sold to customers — it is one unified backend that powers
every consumer product (URGAA, GSTSAAS, Ignition, ARJUN) and the internal
Kailash operations dashboard. One platform, one set of AI capabilities, many
surfaces.

## 2. Target users

| User | Surface | Primary need |
| --- | --- | --- |
| EV charging operators & partners | URGAA | Certificates, SLA tracking, uptime forecasting |
| Businesses filing GST | GSTSAAS | Invoice OCR, fraud detection, voice assistance |
| Charger owners / installers | Ignition | Charger trust scoring, RC verification |
| Field agents | ARJUN | ID-proof verification, Indic speech |
| Internal operators / leadership | Kailash Dashboard | Cross-product ops cockpit, KPIs |

## 3. Product goals

1. **One backend, many products.** Every consumer product calls the same
   Kailash API rather than reimplementing AI capabilities.
2. **Domain moat.** Build an automobile-domain LLM that competitors cannot
   trivially replicate (see the roadmap in `../README.md` and `TRD.md`).
3. **Statutory-grade finance.** The Company segment is an auditable
   double-entry system-of-record producing Indian statutory financials
   (GSTR-1/3B, Schedule III) end-to-end.
4. **India-first.** Indic locales for speech, GST/HSN/regulatory knowledge, and
   rupee-native financial workflows.

## 4. Functional scope

- **AI departments & guardians** — deity-themed AI departments orchestrated by
  GANESHA, with SHIV (security/auto-rectification) and PARVATI (workload)
  guardians. Auth, RBAC, and per-department knowledge bases.
- **Platform services** — document-ai, forecasting, anomaly, rag,
  vision-gateway, speech, model-registry, knowledge-graph, automobile-llm — each
  an independent internal microservice behind an internal-token contract.
- **Company segment** — statutory ledger, GST/TDS engines, reconciliation, and
  an FY dashboard.
- **Frontend** — React 19 operations UI and product surfaces.

## 5. Non-functional requirements

- **Security** — internal-token auth between services; JWT + RBAC for the main
  app; no secrets in the repo (env vars / secret store only).
- **Observability** — every service exposes `/health`, `/metrics`, and
  structured JSON logs with a request id.
- **Deployability** — a single, gated CI/CD pipeline; the deploy is safe to run
  from any clean checkout (enforced by the `scripts/verify/` gates).
- **Reliability** — staging must precede production; every deploy is verified
  against a health endpoint before it is considered done.

## 6. Success metrics

- Consumer products consume Kailash APIs rather than bespoke AI code.
- Green, single pipeline from commit → staging → production with automated
  verification.
- Statutory financials reconcile against the CA/Tally books with zero silent
  drops (every ingestion error is queued, not lost).

## 7. Out of scope

- Selling Kailash as a standalone product to third parties.
- Any capability that bypasses the unified backend contract.

## 8. References

- Business requirements: [`BRD.md`](./BRD.md)
- Technical requirements & architecture: [`TRD.md`](./TRD.md)
- Platform architecture: [`../ARCHITECTURE.md`](../ARCHITECTURE.md),
  [`architecture/`](./architecture/)
- Project rules (read first): [`../../RULES.md`](../../RULES.md)
