# services/company

The **Company segment** — Kailash's master operational ledger and statutory
financial core. A full **double-entry system-of-record** (PostgreSQL) that
migrates from and reconciles against the CA's Tally books, and produces
FY-wise financials at Indian statutory standard end-to-end:
primary document → journal → sub-ledger → GSTR-1/3B → Schedule III
statements → reconciliation.

Design spec: [`company-segment/Company_Segment_Technical_Specification.md`](../../../company-segment/Company_Segment_Technical_Specification.md)
· Schema/DDL + seed templates: [`company-segment/`](../../../company-segment/)
· AWS deployment architecture: [`company-segment/docs/aws/`](../../../company-segment/docs/aws/)
(Aurora Serverless v2, Lambda engines, Step Functions, EventBridge — this
service's code is the application layer that maps onto that stack)

## Architecture (5 layers)

| Layer | What | Where |
|---|---|---|
| L0 | Ingestion contracts, dedup, error queue | `/ingest/*`, `co_ingest_error` |
| L1 | Immutable double-entry ledger (system of record) | `co_journal`, `co_journal_line` |
| L2 | GST/TDS engines, Schedule III statement builder | `/gst/*`, `/reports/*` |
| L3 | Reconciliation: internal ⟷ CA/Tally/GSTN | `/recon/*` |
| L4 | Read-only projections + HTML dashboard | `/dashboard`, `co_v_*` views |

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/admin/init` | Apply schema + seed masters (COA, GST 2.0 rates, parties, recon points, fiscal calendar). Idempotent. |
| `POST` | `/admin/company` | Register legal entity + GSTIN (Day-1 identity). |
| `POST` | `/admin/bank-account` | Register a bank account for BRS. |
| `POST` | `/ingest/sales` | Sales invoice (per `sales_invoice.contract.json`) → posted journal. |
| `POST` | `/ingest/purchase` | Purchase bill → posted journal + ITC register. |
| `POST` | `/ingest/bank` | Bank statement lines (idempotent by `source_hash`). |
| `GET`  | `/ingest/errors` | The error queue — nothing silently drops. |
| `POST` | `/journal` | Manual draft journal (by account codes). |
| `POST` | `/journal/{fy}/{id}/post` | Maker-checker post (DB enforces Σdr=Σcr, maker≠checker). |
| `POST` | `/journal/{fy}/{id}/reverse` | Correction by reversal — posted entries are never edited. |
| `POST` | `/migration/opening-balance` | Tally cut-over opening journal (`origin=TALLY_MIGRATION`). |
| `POST` | `/gst/gstr1/generate` | Build GSTR-1 (B2B/B2CL/B2CS/EXP/SEZ + HSN + docs) as versioned JSONB. |
| `POST` | `/gst/gstr3b/generate` | GSTR-3B summary: liability from sales, ITC from register. |
| `POST` | `/tds/entry` | TDS deduction capture (feeds 24Q/26Q/27Q). |
| `GET`  | `/reports/trial-balance` | Per-FY trial balance (+ balanced flag). |
| `GET`  | `/reports/schedule-iii` | P&L + Balance Sheet + accounting-equation probe. |
| `POST` | `/reports/financials/snapshot` | Version statements into `co_financial_statement_line`. |
| `POST` | `/recon/run` | Run the 10 control points; externals from CA/portal, cross-checks computed. |
| `GET`  | `/recon/variances` | Open variances (RAG matrix source). |
| `PATCH`| `/recon/variance/{id}` | Resolution workflow (open→investigating→resolved/accepted). |
| `GET`  | `/compliance/calendar` | GST/TDS/IT/ROC due dates with status. |
| `GET`  | `/dashboard` | Self-contained HTML FY dashboard (L4). |

Mutating endpoints require `X-Platform-Token`; reads are open (standard
platform convention).

## Running

**Containerized (compose profile `kailash-ai`)** — Postgres + this service:

```bash
docker compose --profile kailash-ai up -d --build company   # from repo root
curl -X POST localhost:8110/admin/init
```

**Bare-metal dev:**

```bash
# 1. Postgres (published on loopback by docker-compose.override.yml)
docker compose up -d postgres

# 2. Service
pip install -r requirements.txt
PYTHONPATH=../../.. uvicorn app.main:app --port 8110   # from this directory

# 3. Bootstrap
curl -X POST localhost:8110/admin/init
```

Config via env (see `.env.example`): `COMPANY_DB_URL`,
`COMPANY_SCAFFOLD_DIR`, `PLATFORM_INTERNAL_TOKEN`.

## Ledger invariants (DB-enforced, adversarially tested)

- Σdebit = Σcredit per journal, checked at post time; journals can never be
  INSERTed as `posted`.
- Posted journals and their lines are immutable; corrections are reversals
  (`posted` → only `reversed`; `reversed` is terminal).
- Maker ≠ checker required to post.
- `source_hash` dedup at DB level (per FY) + API level (global).
- `co_audit_log` is trigger-enforced append-only.
- GST rate splits must satisfy `cgst+sgst = total = igst`.
- FY-partitioned ledger with a DEFAULT partition for historical
  (Tally-migration) years.

`tests/test_invariants.py` attacks each one with raw SQL and asserts the
database rejects it. `tests/test_routes.py` is the end-to-end journey
(init → opening balance → sales/purchase → GSTR-1/3B → reconciliation →
dashboard). Tests run against a throwaway `kailash_company_test` database
and skip cleanly when Postgres is absent; CI runs them against a
`postgres:16` service container.

## Deferred (post-baseline, per spec §11/§14)

- Row-level security policies per GSTIN/cost-center (service currently
  connects as a single role; RBAC happens at the API gateway layer).
- pgcrypto column encryption for PAN/Aadhaar/bank/salary PII.
- Payroll + fixed-asset depreciation engines, GSTR-9/9C, cash-flow
  statement, Tally XML auto-import (schema + tables are in place).
