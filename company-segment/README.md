# Kailash — Company Segment (buildable scaffold)

This module is the **master operational ledger and statutory-financial core** of Kailash.
It is designed as a **full double-entry system-of-record** that migrates from, and continuously
reconciles against, the CA's **Tally** books, and produces **FY-wise financials at Indian
statutory standard** (sales, purchase, GSTR-1/3B/9, TDS, ROC, Schedule III statements) end-to-end.

The full design rationale is in **`../Company_Segment_Technical_Specification.md`**. This folder
is the code-side starting point you can commit into the `Kailash-Ai` repo.

## Contents

```
company-segment/
├── schema/
│   └── company_segment_schema.sql     # PostgreSQL DDL: masters -> ledger -> compliance -> recon -> views
├── templates/
│   ├── chart_of_accounts.csv          # Schedule III-aligned COA, GST/TDS tagged  <-- REVIEW FIRST
│   ├── hsn_gst_rate_master.csv        # GST 2.0 rate slabs (eff. 22-Sep-2025)
│   ├── party_master.csv               # sample customers/vendors (GSTIN/PAN/MSME/TDS)
│   ├── gstr1_section_mapping.csv      # supply type -> GSTR-1 section rules
│   └── reconciliation_control_points.csv  # the 10 CA-vs-internal control points
├── compliance/
│   └── compliance_calendar.csv        # GST/TDS/income-tax/ROC due dates (FY 2025-26)
├── ingestion/
│   ├── README.md                      # ingestion contracts (Tally, sales, purchase, bank, payroll)
│   └── sales_invoice.contract.json    # example JSON schema for the sales pipeline
└── docs/
    ├── FOLDER_STRUCTURE.md            # repo module + document-vault layout
    ├── DATA_DICTIONARY.md             # table-by-table reference
    └── aws/                           # AWS deployment architecture
        ├── Company_Segment_Backend_Architecture_AWS.md
        ├── architecture.{mmd,png,svg} # L0-L4 on the Go4Garage AWS stack
        └── dataflow.{mmd,png,svg}     # end-to-end sequence (capture->file->reconcile)
```

## Build order (matches the 3-day baseline plan in the spec, §14)

1. **Create the schema.** `psql "$DATABASE_URL" -f schema/company_segment_schema.sql`
   (creates the `company` schema; `co_journal*` partitions for FY 2025-26 and 2026-27 are included).
2. **Load masters.** Import `templates/hsn_gst_rate_master.csv` → `co_tax_rate`,
   `templates/chart_of_accounts.csv` → `co_account` (resolve `parent_code`→`parent_id`),
   then `party_master.csv` → `co_party`. **Review the COA with the CA before loading — it fixes
   the shape of every downstream report.**
3. **Seed reconciliation + calendar.** `reconciliation_control_points.csv` → `co_recon_control_point`;
   `compliance/compliance_calendar.csv` drives the compliance-calendar view.
4. **Tally migration.** Build the `co_map_tally` mapping once with the CA; post the opening-balance
   journal as of cut-over; verify `co_v_trial_balance` ties to Tally to the rupee (control point
   `CLOSING_BALANCES`).
5. **Go live.** Capture sales/purchase → journals; generate GSTR-1/3B for one live period; light up
   the FY dashboard and reconciliation matrix.

## Implementation

The working service lives at **`backend/services/company/`** (FastAPI on the
platform `build_app()` factory): ingestion APIs, posting engine, GST engine,
reconciliation runner, and the L4 HTML dashboard. Its test suite includes
adversarial SQL tests that prove each invariant below is rejected by the
database itself.

## Non-negotiable invariants (enforced in the schema, v1.1 hardened)

- Every posted voucher balances: `Σ debit = Σ credit`, checked at post time
  on both the UPDATE and INSERT paths — a journal can never be born
  `posted` (`trg_assert_balanced`, `trg_assert_balanced_ins`).
- Posted vouchers **and their lines** are immutable — corrections are
  reversals, never edits (`trg_block_posted`, `trg_block_posted_lines`).
- No un-posting: `posted` may only become `reversed`; `reversed` is
  terminal. Reporting views include both (a reversal pair nets to zero —
  neither side ever disappears from the books).
- Maker ≠ checker enforced at post time in the database.
- Ingestion is idempotent via `source_hash` — UNIQUE at the DB level
  (per FY, partition-key-complete) plus global cross-FY dedup in the API.
- `co_audit_log` is trigger-enforced append-only.
- GST rate splits satisfy `CHECK (cgst+sgst = total AND igst = total)`.
- Ledger is FY-partitioned with a DEFAULT partition, so historical-FY
  Tally-migration vouchers land instead of erroring.
- Business-document → journal links carry composite `(journal_id, fy)`
  FOREIGN KEYs — the audit trail is referentially enforced.

**Deferred to post-baseline** (per spec §11): row-level security policies
per GSTIN/cost-center and pgcrypto column encryption for PII — the service
currently connects as a single role and PII columns are plaintext.

## Requirements

PostgreSQL 14+ (uses IDENTITY columns, declarative LIST partitioning, JSONB, plpgsql triggers).
