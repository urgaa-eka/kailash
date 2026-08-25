# Kailash — "Company" Segment

## Technical Specification: Master Operational Ledger & Statutory Financial Data Architecture

| Field | Value |
|---|---|
| **Project** | Kailash (Center Lake data core) |
| **Segment** | Company (1 of 4: Product · Sprint · **Company** · Goal) |
| **Document type** | Technical Requirement / Architecture Specification (TRD-grade) |
| **Owner** | Eka / Go4Garage engineering |
| **Status** | v1.1 — Baseline built (schema hardened C1–C4/N1–N7; working service at `backend/services/company/`) |
| **Design lock (per stakeholder)** | Kailash Company segment is the **full double-entry system-of-record**; it **migrates from and continuously reconciles against the CA's Tally books** |
| **Jurisdiction** | India — Companies Act 2013, CGST/SGST/IGST Acts, Income-tax Act, "GST 2.0" rate regime (eff. 22-Sep-2025) |
| **Reporting currency / calendar** | INR · Financial Year = 1 Apr → 31 Mar |
| **Related docs** | `BRD_kailash_ai.md`, `TRD_kailash_ai.md`, `ARCHITECTURE.md`, `EKA_BRAIN_E2E_MASTER_PLAN.md` |

---

## 1. Purpose & Scope

### 1.1 What the Company segment is

The Company segment is the **master operational ledger and foundational corporate-administrative database** of the organisation. It is the single, authoritative store for every financial and statutory fact the company generates from **Day 1** of incorporation onward. Where the *Product* segment tracks what the company builds, the *Sprint* segment tracks how fast it builds, and the *Goal* segment tracks where it is going, the **Company segment is the financial and legal source of truth** — the ledger against which auditors, the CA, the board, and future investors will test the company.

### 1.2 The end-state deliverable (the "visible result")

The concrete target — the thing a user sees after all data is loaded — is a **complete, financial-year-wise view of the company's finances at Indian statutory standard**, produced end-to-end from primary records, including:

- **Sales / outward supply** register and turnover, reconciled to GST and to books.
- **Purchase / inward supply** register with eligible Input Tax Credit (ITC).
- **GST returns** — `GSTR-1`, `GSTR-3B`, `GSTR-2B` (ITC), `GSTR-9`/`9C` — generated from the ledger, not re-keyed.
- **Statutory financial statements** — Balance Sheet, Statement of Profit & Loss, Cash-Flow, Notes — in **Schedule III (Companies Act 2013)** format, per FY.
- **Direct-tax artefacts** — TDS ledgers/returns, advance-tax schedule, tax-audit (3CD) data, ITR-6 feed.
- **ROC / MCA compliance** — AOC-4, MGT-7/7A, DPT-3, MSME-1, DIR-3 KYC, ADT-1 status and the data behind each form.
- **Reconciliation dashboard** — internal (Kailash-computed) figures cross-checked against the CA's audited/Tally figures, with every variance flagged.

"End-to-end" here means **primary document → journal → sub-ledger → statutory computation → filed-return/financial-statement → reconciliation**, with no manual re-entry between stages and a full audit trail at every hop.

### 1.3 Position within Kailash and the Center Lake philosophy

Under the **Center Lake** architecture, **Eka Brain is the "mind"** (decisioning, the 85-agent fleet) and **Kailash is the "heart"** (the data-pumping core). All organisational data routes **into Kailash first**; Kailash then dictates how, where, and to which agent/interface data is distributed. The Company segment is the chamber of that heart which handles **money and legal identity**. It therefore has the strictest integrity, immutability, and access-control requirements of any segment, and it is the segment most directly exposed to external regulators (GSTN, Income-tax Dept., MCA) and to investors during the second funding round.

### 1.4 In scope / out of scope

**In scope:** company master & Day-1 records; chart of accounts; double-entry journal; AR/AP/bank/tax sub-ledgers; sales, purchase, expense, payroll, fixed-asset and banking transaction capture; GST/TDS/income-tax/ROC compliance engines; Schedule III financial-statement builder; the CA-vs-internal reconciliation engine; the employee financial dashboard; and the statutory document vault.

**Out of scope (owned by other segments / systems):** product BRD/TRD content (*Product* segment); sprint HTML and delivery tracking (*Sprint* segment); strategic planning (*Goal* segment); the ML training lifecycle of the 85 agents (Eka Brain). The Company segment **exposes** clean financial facts to those systems; it does not host their logic.

---

## 2. Design Principles

1. **System of Record, not a mirror.** Kailash holds the authoritative double-entry ledger. Tally is treated as a **migration source and a reconciliation counterparty**, never as the master. Once cut-over is complete, a transaction is "real" when it is posted in Kailash.
2. **Everything is double-entry.** No financial fact enters the core without balanced debit/credit postings. `Σ debits = Σ credits` is a hard database invariant, enforced per journal voucher.
3. **Append-only / immutable ledger.** Posted vouchers are never updated or deleted. Corrections are made by **reversal + re-posting**, preserving a legally defensible audit trail (Companies Act §128 requires books to be maintainable and inspectable; tampering is disqualifying at diligence).
4. **Design backwards from the statutory output.** The schema is shaped so that `GSTR-1` sections, Schedule III line items, and ROC form fields are *derivable by query*, not assembled by hand. Every master carries the tags (HSN/SAC, place-of-supply, Schedule III grouping, TDS section) that the outputs need.
5. **FY-partitioned, multi-GSTIN aware.** All facts are stamped with the Indian FY (Apr–Mar) and the relevant GSTIN/state, because GST is state-wise and every statutory report is FY-scoped.
6. **Reconciliation is a first-class citizen.** The internal-vs-CA cross-check is not a report bolted on at the end; it is a modelled subsystem with control points, tolerances, variance records and a resolution workflow.
7. **Center Lake routing.** Ingress and egress are contract-based. Data lands in Kailash, is validated, canonicalised, posted, and only then published to Eka Brain agents and other segments.
8. **Audit-first security.** Maker-checker on postings, row-level access by role and GSTIN, PII isolation for PAN/Aadhaar/bank data, and statutory retention windows (8 years, Companies Act §128(5)).

---

## 3. Logical Architecture

The segment is a five-layer pipeline. Data only ever flows "up" the layers within the core; nothing writes to L1 (the ledger) except the posting engine.

```
                          ┌───────────────────────────────────────────────┐
   External regulators →  │  L4  PRESENTATION / EXPORT                     │
   GSTN · MCA · IT Dept   │  FY financial dashboard · statutory registers  │
   Investors · Board      │  GSTR-1 JSON · Schedule-III stmts · ROC feeds  │
                          │  employee analytics · compliance calendar      │
                          └───────────────▲───────────────────────────────┘
                                          │  (read-only projections / views)
                          ┌───────────────┴───────────────────────────────┐
                          │  L3  RECONCILIATION                            │
   CA / Tally figures  →  │  control points · variance engine · resolution │
                          │  (internal Kailash  ⟷  CA-audited / Tally)     │
                          └───────────────▲───────────────────────────────┘
                                          │
                          ┌───────────────┴───────────────────────────────┐
                          │  L2  COMPUTATION & COMPLIANCE  (Gold)          │
                          │  GST engine · TDS engine · income-tax engine   │
                          │  ROC/MCA engine · Schedule-III stmt builder    │
                          └───────────────▲───────────────────────────────┘
                                          │  (derives from, never mutates, L1)
                          ┌───────────────┴───────────────────────────────┐
                          │  L1  CORE LEDGER  (Silver) — SYSTEM OF RECORD  │
                          │  double-entry journal · AR/AP/Bank/Tax ledgers │
                          │  chart of accounts · immutable, FY-partitioned │
                          └───────────────▲───────────────────────────────┘
                                          │  (posting engine; validated, idempotent)
                          ┌───────────────┴───────────────────────────────┐
                          │  L0  SOURCE / INGESTION  (Bronze)              │
   Day-1 docs · Tally  →  │  staging · schema-validate · dedup · map · FX  │
   invoices · bank · HR   │  error queue · document vault (object store)   │
                          └───────────────────────────────────────────────┘
```

**Storage split.** L0 document vault and generated statutory files (GSTR-1 JSON, PDF statements) live in an **object store**; L1–L3 structured facts live in **PostgreSQL** (the Kailash-Ai repo already carries a `database/` module); L4 is served as SQL **views/materialised views** plus the existing HTML dashboard style used across `eka-brain/`.

---

## 4. Data Model

The model has four rings: **Masters** (dimensions), **Ledger** (the double-entry core), **Compliance** (statutory outputs), and **Reconciliation**. Full DDL ships in the scaffold (`schema/company_segment_schema.sql`); this section explains the design intent. Table names below use the `co_` prefix (Company segment) to keep the namespace clean inside the shared Kailash database.

### 4.1 Master data (dimensions)

| Table | Holds | Key statutory tags it must carry |
|---|---|---|
| `co_company` | Legal entity/entities — CIN, PAN, TAN, incorporation date, registered office, authorised & paid-up capital, class of company | Drives ROC filing set; "Day-1" identity |
| `co_gstin` | One row per GST registration (state-wise) under the company | GSTIN, state code, registration type, e-invoice applicability |
| `co_fiscal_calendar` | Date → FY, quarter, month, GST period | Indian FY (Apr–Mar); every fact joins here |
| `co_account` | **Chart of Accounts** — code, name, account_type, parent (tree) | Schedule III grouping, normal balance (Dr/Cr), GST/TDS nature flags |
| `co_party` | Customers & vendors | GSTIN, PAN, party type, state (place-of-supply), MSME/Udyam status (drives MSME-1), TDS applicability |
| `co_item` | Goods & services sold/purchased | HSN (goods) / SAC (services), UQC (unit), default GST rate slab |
| `co_tax_rate` | GST rate master under **GST 2.0** | Slab (0/5/18/40 + niche 3/0.25/12/28), CGST/SGST/IGST split, cess, effective-dated |
| `co_cost_center` | Department / project dimension | Employee-dashboard analytics; segment reporting |
| `co_employee` | Payroll subjects | PAN, PF/ESI/UAN, salary structure (feeds 24Q, Form 16) |
| `co_bank_account` | Company bank accounts | For bank sub-ledger & statement reconciliation |
| `co_document_series` | Invoice/voucher numbering series | GST-compliant, gap-free, per-GSTIN, per-FY |

**Normal-balance rule.** Every `co_account` row declares its `normal_balance` (`D` or `C`) and its `schedule_iii_group`. This single design choice is what lets the statement builder (L2) roll a raw trial balance up into a Schedule III Balance Sheet and P&L automatically.

### 4.2 The double-entry core (the ledger)

Two tables carry the entire system of record:

- **`co_journal`** — the voucher header: `journal_id`, `voucher_type` (Sales/Purchase/Payment/Receipt/Contra/Journal/CreditNote/DebitNote), `voucher_no` (from `co_document_series`), `voucher_date`, `fy`, `gstin_id`, `narration`, `source_ref` (link back to the originating document in L0), `status` (`draft`→`posted`→`reversed`), maker/checker, timestamps.
- **`co_journal_line`** — the postings: `journal_id`, `line_no`, `account_id`, `debit`, `credit`, `party_id?`, `item_id?`, `cost_center_id?`, `tax_code?`, `hsn_sac?`, `place_of_supply?`. Exactly one of `debit`/`credit` is non-zero per line.

**The hard invariant** — enforced by a deferrable constraint / posting-time trigger:

```
For every journal_id:  Σ(debit) = Σ(credit)   AND   Σ(debit) > 0
Once status = 'posted': rows are immutable (no UPDATE/DELETE).
Correction path: post a reversing journal (source_ref → original), then re-post correctly.
```

Everything else in accounting is a **projection of these two tables**. Sub-ledgers are not separate books; they are the journal filtered by account nature:

| Sub-ledger | Definition (a view over `co_journal_line`) |
|---|---|
| **Accounts Receivable (AR)** | lines where `account.type = 'AR'`, grouped by `party_id` → who owes us |
| **Accounts Payable (AP)** | lines where `account.type = 'AP'`, grouped by `party_id` → whom we owe |
| **Bank / Cash** | lines where `account.type IN ('BANK','CASH')` → feeds statement reconciliation |
| **Tax** | lines where `account.nature IN ('GST_OUT','GST_IN','TDS')` → feeds the GST/TDS engines |

### 4.3 Transaction capture tables (business documents)

These tables hold the *business meaning* of a document and are the source that generates the journal. They keep GST-grade detail the bare journal does not need:

| Table (+ line table) | Generates | Notes |
|---|---|---|
| `co_sales_invoice` / `co_sales_line` | Dr Debtor, Cr Sales, Cr Output GST | invoice type (B2B/B2CL/B2CS/EXP/SEZ), place-of-supply, IRN/QR if e-invoiced |
| `co_purchase_bill` / `co_purchase_line` | Dr Purchase/Expense, Dr Input GST, Cr Creditor | ITC eligibility flag, vendor GSTIN, GSTR-2B match key |
| `co_credit_note` / `co_debit_note` | reversals of the above | flows to GSTR-1 CDNR / amendments |
| `co_receipt` / `co_payment` | Dr/Cr Bank ↔ Party | TDS deduction lines where applicable |
| `co_expense` | Dr Expense, Cr Bank/Creditor | cost-center tagged; TDS section tagged |
| `co_payroll_run` / `co_payslip` | Dr Salary, Cr Bank/PF/ESI/TDS payable | feeds 24Q & Form 16 |
| `co_fixed_asset` / `co_depreciation_schedule` | Dr Asset; periodic Dr Depreciation, Cr Accum. Dep. | Companies Act Sch II useful-life + Income-tax WDV block (dual) |

### 4.4 Compliance / output tables

Materialised outputs so a filed return is a stored, versioned artefact — not a transient query:

| Table | Purpose |
|---|---|
| `co_gstr1` + section tables (`_b2b`, `_b2cl`, `_b2cs`, `_exp`, `_cdnr`, `_hsn`, `_docs`) | Outward-supply return, GSTN-schema shaped |
| `co_gstr3b_summary` | Auto-populated summary liability & ITC per period |
| `co_itc_register` | GSTR-2B-matched inward credit, eligible/ineligible/deferred |
| `co_tds_ledger` | Deduction-level TDS by section (194C/194J/192…), feeds 24Q/26Q/27Q |
| `co_financial_statement_line` | Versioned trial-balance → P&L → BS → Cash-Flow lines, per FY |
| `co_roc_filing` | One row per ROC form instance with status, due date, SRN |
| `co_statutory_register` | Members, directors, charges, related-party, etc. |

### 4.5 Reconciliation tables

| Table | Purpose |
|---|---|
| `co_recon_control_point` | Definition of each thing that must match (e.g. "FY sales", "output tax", "ITC", "net profit", "GSTR-1 vs 3B") with its tolerance |
| `co_recon_run` | An execution of the reconciliation for a period, capturing internal value, CA/Tally value, source refs |
| `co_recon_variance` | Each mismatch: amount, %, severity, owner, root cause, status (`open`→`resolved`/`accepted`), notes |

### 4.6 Keys, partitioning, integrity

- **Surrogate PKs** (BIGINT/UUID) everywhere; natural keys (GSTIN, PAN, invoice-no) carry **unique constraints** but are not PKs.
- **Partition** `co_journal` / `co_journal_line` by `fy` (declarative range partitioning) — statutory reports are always FY-bounded, and old FYs become read-only/archival.
- **Immutability** enforced by trigger: `BEFORE UPDATE/DELETE ON co_journal WHERE status='posted' → RAISE`.
- **Referential integrity**: every posting line FKs to a valid `co_account`; every GST line FKs to a valid `co_tax_rate` effective on the voucher date.
- **Idempotency**: ingestion carries a `source_hash`; re-ingesting the same document is a no-op, preventing double-posting.

---

## 5. Chart of Accounts (COA) Design

The COA is the spine that makes automated statutory output possible. It is a **tree** (`co_account.parent_id`) with four to five levels: `Nature → Group → Ledger → Sub-ledger`. Every leaf declares:

- **`account_type`** — one of `ASSET`, `LIABILITY`, `EQUITY`, `INCOME`, `EXPENSE`, plus operational subtypes `AR`, `AP`, `BANK`, `CASH`, `GST_OUT`, `GST_IN`, `TDS_PAYABLE`, `TDS_RECEIVABLE`.
- **`normal_balance`** — `D` or `C`.
- **`schedule_iii_group`** — the exact Schedule III line the ledger rolls into (e.g. *Revenue from Operations*, *Trade Receivables*, *Short-term Borrowings*, *Other Expenses*).
- **`tax_nature`** — optional GST/TDS tag so the compliance engines can find the right accounts without hard-coded IDs.

Because each leaf knows its Schedule III home and its normal balance, the statement builder needs no manual mapping table at period-end: it sums the trial balance by `schedule_iii_group` and signs it by `normal_balance`. A **starter COA** (Indian private-company, Schedule III aligned, GST/TDS tagged) ships as `templates/chart_of_accounts.csv` — it is the single most important file to review before build, because it locks the shape of every downstream report.

---

## 6. Ingestion & Migration

### 6.1 Tally migration (cut-over + history)

The CA keeps the books in **Tally**, so Tally is the migration source and, post-cut-over, a reconciliation counterparty. Tally exposes data as **XML** (Export → Day Book / Trial Balance / Ledgers / Stock Summary) and via ODBC. The migration pipeline:

1. **Extract** Tally masters (ledgers, groups, stock items, parties) and vouchers as XML for the migration window.
2. **Stage** raw XML into `co_stg_tally_*` tables (untouched, hashed).
3. **Map** Tally ledgers → `co_account`, Tally parties → `co_party`, Tally stock items → `co_item`. This mapping table (`co_map_tally`) is reviewed once with the CA and then reused.
4. **Opening balances** as of the cut-over date are posted as a single dated **opening journal** (Dr assets / Cr liabilities & equity, balanced).
5. **Historical vouchers** (optional, for prior FYs) are posted as reversible journals tagged `origin='TALLY_MIGRATION'` so they are visibly distinguishable from natively-captured Kailash transactions.
6. **Parallel run**: for the first 1–2 GST periods, both systems run; the reconciliation engine (L3) proves Kailash reproduces Tally to the rupee before Tally is retired as the book of record.

### 6.2 Ongoing source-document pipelines

| Source | Path into Kailash | Journal produced |
|---|---|---|
| **Sales** | GSTSAAS / e-invoice IRP (IRN+QR) or manual `co_sales_invoice` | Dr Debtor · Cr Sales · Cr Output CGST/SGST/IGST |
| **Purchase** | vendor bill capture → GSTR-2B match | Dr Purchase/Expense · Dr Input GST (if eligible) · Cr Creditor |
| **Bank** | statement import (CSV / MT940 / ISO 20022) | Dr/Cr Bank ↔ contra; flagged for reconciliation |
| **Payroll** | `co_payroll_run` (monthly) | Dr Salary · Cr Bank/PF/ESI/TDS-payable |
| **Expenses** | employee/vendor expense capture | Dr Expense · Cr Bank/Creditor (TDS-tagged) |

Each pipeline enforces an **ingestion contract**: JSON schema validation → dedup by `source_hash` → master resolution (create-or-map party/item) → tax computation → **draft** journal → maker-checker → **post**. Anything that fails validation lands in an **error queue** (`co_ingest_error`) with a reason code; nothing silently drops.

### 6.3 Day-1 corporate records (static reference)

Incorporation certificate, MOA/AOA, PAN, TAN, GST certificates, PF/ESI, Udyam/MSME, Startup-India, share certificates, board resolutions and statutory registers are **documents**, not transactions. They load into the **document vault** (object store) with metadata rows in `co_company`, `co_gstin`, and `co_statutory_register`. These populate the identity fields every ROC form and every GST return header depends on — hence "Day-1": without them the compliance engines cannot even address a filing.

---

## 7. Compliance Engines (L2)

All engines are **pure functions of the ledger + masters for a given (FY, period, GSTIN)**. They never mutate L1; they read it and emit versioned artefacts into the L2 compliance tables. Compliance rules below are current as of the dates in **Appendix A** and are held in **effective-dated config**, never hard-coded, so a rate or due-date change is a data change.

### 7.1 GST engine

**Rate regime — "GST 2.0" (effective 22-Sep-2025).** `co_tax_rate` is effective-dated so pre- and post-reform invoices compute correctly. Current slabs:

| Slab | Applies to (indicative) |
|---|---|
| **0% (Nil)** | fresh/unprocessed food, ~33 life-saving drugs, education materials, individual life & health insurance |
| **5%** | daily essentials, agri goods, medical equipment, many processed foods |
| **18%** | electronics, appliances, most manufactured goods, cement, **most services** |
| **40%** | sin/luxury — sugary/aerated drinks, tobacco, high-cc motorcycles (>350cc), premium vehicles, yachts, betting/gambling |
| Niche | 3% (jewellery/precious metal), 0.25% (rough diamonds), 12% (specified bricks/tiles), 28% (transitional pan-masala/tobacco pending notification) |

The old **12% and 28%** slabs are consolidated into 5/18/40. **Place-of-supply logic** decides CGST+SGST (intra-state) vs IGST (inter-state); the engine derives this from supplier GSTIN state vs `place_of_supply`.

**Returns generated:**

| Return | What the engine builds | Cadence / due date |
|---|---|---|
| **GSTR-1** | outward supplies, split into B2B, B2CL, B2CS, EXP, SEZ, CDNR, HSN-summary, docs-issued | monthly by **11th**; QRMP (turnover ≤ ₹5 cr) quarterly by **13th** |
| **IFF** | optional upload of B2B invoices for months 1–2 of a QRMP quarter | **13th** of following month |
| **GSTR-1A** | amendment/rectification of a filed GSTR-1 **before** GSTR-3B of that period | same period, pre-3B |
| **GSTR-3B** | summary liability & ITC, **auto-populated** from GSTR-1 (liability) and GSTR-2B (ITC); filed **sequentially** after GSTR-1 | monthly by **20th**; QRMP quarterly by **22nd/24th** (state-grouped) |
| **GSTR-2B** | static, auto-drafted ITC statement consumed for purchase matching | generated ~**14th** |
| **GSTR-9 / 9C** | annual return / self-certified reconciliation statement | **31 Dec** of next FY; 9 optional if turnover ≤ ₹2 cr, 9C required if turnover > ₹5 cr |

**Additional rules the engine encodes:** **e-invoicing** is mandatory for B2B/export where aggregate turnover > **₹5 cr** (IRN + signed QR from the IRP) — Kailash stores the IRN on `co_sales_invoice`; **e-way bills** for goods movement > ₹50,000; the **3-year time bar** (returns cannot be filed after 3 years past due date) is surfaced as a hard alert on the compliance calendar; and the trend toward **hard-locked, non-editable auto-populated GSTR-3B liability** means the engine must make GSTR-1 correct *first* (via GSTR-1A) rather than adjust in 3B.

### 7.2 TDS engine

Reads payment/expense/payroll lines tagged with a TDS section (192 salary, 194C contractors, 194J professional, 194I rent, 194Q goods, etc.), computes deduction at the section rate, and posts `Cr TDS payable`. It produces:

- **Monthly deposit** obligation — due **7th** of the following month (April deposits for March: **30 Apr**).
- **Quarterly returns** — **24Q** (salary), **26Q** (non-salary resident), **27Q** (non-resident): due **31 Jul / 31 Oct / 31 Jan / 31 May** for Q1–Q4.
- **Certificates** — **Form 16** (annual salary) by **15 Jun**; **Form 16A** (quarterly, non-salary) within 15 days of the return due date.

### 7.3 Income-tax engine

- **Advance tax** schedule for companies: **15%/45%/75%/100%** cumulative by **15 Jun / 15 Sep / 15 Dec / 15 Mar**.
- **Tax-audit test** (§44AB): turnover > **₹1 cr** (or > **₹10 cr** where ≥95% of receipts **and** payments are non-cash). Where triggered, the engine assembles the **3CD** data set.
- **Return**: **ITR-6** for the company; due **31 Oct** (audited) / **30 Nov** (transfer-pricing / Form 3CEB). Tax-audit report (3CA/3CB-3CD) due **30 Sep**.

### 7.4 ROC / MCA engine

Event-driven + annual calendar keyed off incorporation date and AGM date. For FY 2025-26 (AGM by 30-Sep-2026):

| Form | Purpose | Due |
|---|---|---|
| **ADT-1** | auditor appointment/ratification | within 15 days of AGM |
| **AOC-4** | file audited financial statements | within 30 days of AGM (~29-Oct-2026) |
| **MGT-7 / 7A** | annual return (7A for small co./OPC) | within 60 days of AGM (~28-Nov-2026) |
| **DPT-3** | return of deposits & outstanding loans | **30-Jun-2026** |
| **DIR-3 KYC** | director KYC for active DINs | **30-Sep-2026** |
| **MSME-1** | half-yearly dues to MSME suppliers outstanding > 45 days | **30-Apr** (Oct–Mar) & **31-Oct** (Apr–Sep) |
| Board meetings | min. 4/year, gap ≤ 120 days (2/year for small co./OPC) | rolling |

Each maps to a `co_roc_filing` row with computed due date, status, and SRN once filed; the data behind AOC-4 comes straight from the Schedule III statements (§7.5), so financial statements and the ROC filing can never diverge.

### 7.5 Financial-statement builder

Rolls the posted ledger into **Schedule III (Division I/II)** statements per FY:

1. **Trial balance** — sum debits/credits per `co_account` for the FY (opening + movement = closing).
2. **P&L** — income and expense leaves grouped by `schedule_iii_group`; derives Revenue from Operations, Other Income, expenses, EBITDA, PBT, tax, PAT.
3. **Balance Sheet** — asset/liability/equity leaves grouped and signed; Equity & Liabilities = Assets is asserted (a failure here means an unbalanced journal slipped through — impossible if §4.2's invariant held, so this doubles as an integrity probe).
4. **Cash-flow** (indirect) and **Notes** (schedules by group).

Output is versioned into `co_financial_statement_line` (so "the FY24-25 balance sheet as the CA signed it" is reproducible), and rendered to the L4 dashboard and to PDF/Excel.

---

## 8. Reconciliation Engine — Internal ⟷ CA/Tally (L3)

This is the subsystem that satisfies the core requirement: *systematically synchronise the independent figures computed by internal staff (via the Kailash dashboards) with the official, audited figures from the CA, and instantly flag every variance.* It is modelled, not manual.

### 8.1 Control points

A **control point** is one quantity that must agree across two independent sources, with a tolerance. The starter set (`templates/reconciliation_control_points.csv`):

| # | Control point | Source A (internal) | Source B (external / cross) | Typical tolerance |
|---|---|---|---|---|
| 1 | FY **sales / turnover** | Kailash sales ledger | CA/Tally P&L revenue | ₹0 (exact) |
| 2 | FY **purchases** | Kailash purchase ledger | CA/Tally | ₹0 |
| 3 | **Output GST** liability | Kailash GST engine | GSTR-3B filed | ₹1 rounding |
| 4 | **GSTR-1 vs GSTR-3B** | GSTR-1 taxable value | GSTR-3B outward | ₹0 |
| 5 | **ITC claimed** | Kailash ITC register | GSTR-2B | flag unmatched |
| 6 | **Books turnover vs GST turnover** | Schedule III revenue | Σ GSTR-1 (annual) | reconciling items only |
| 7 | **Net profit (PAT)** | Kailash P&L | CA audited P&L | ₹0 after adjustments |
| 8 | **Closing balances** (key ledgers: bank, debtors, creditors) | Kailash | Tally trial balance | ₹0 |
| 9 | **TDS deducted** | Kailash TDS ledger | Form 26AS / AIS | ₹0 |
| 10 | **Bank balance** | Kailash bank sub-ledger | bank statement | ₹0 (BRS) |

### 8.2 Variance engine & workflow

For each control point and period the engine computes `variance = A − B`, `variance_% = variance / B`, assigns **severity** by tolerance band (`matched` / `minor` / `material`), and writes a `co_recon_variance` row. Material variances open a **resolution task** with an owner, a root-cause field, and a status (`open → investigating → resolved / accepted-with-note`). Nothing is auto-erased — "eliminating" a variance means either correcting the ledger (reversal + re-post) or recording an accepted reconciling item with an audit note. The L4 dashboard shows a **red/amber/green reconciliation matrix** (control point × period) so an unresolved mismatch is visible at a glance and cannot be filed over.

### 8.3 Why this is the trust anchor for the funding round

At diligence, an investor's or acquirer's accountants run exactly these cross-checks. Because Kailash computes independently and then proves agreement with the CA's audited books to the rupee, the company walks into the second round with a **pre-reconciled, defensible** financial position rather than a spreadsheet assembled the night before.

---

## 9. Reporting & Presentation Layer (L4)

L4 is read-only projections over L1–L3 — SQL views and materialised views, surfaced in the same self-contained HTML dashboard idiom already used across `eka-brain/` (e.g. `go4garage-command-center-v3.html`). Core surfaces:

- **FY Financial Dashboard** (the headline "visible result"): a financial-year selector driving Balance Sheet, P&L, Cash-Flow, key ratios, sales/purchase trend, GST liability vs ITC, and cash position — all for the chosen FY, drill-down to voucher.
- **GST cockpit**: return-by-return status (GSTR-1 / 3B / 2B / 9), liability, ITC, and the GSTR-1↔3B↔books reconciliation.
- **Compliance calendar**: every GST/TDS/income-tax/ROC due date with status (upcoming/filed/overdue) and the 3-year time-bar alerts.
- **Statutory registers**: members, directors, charges — rendered from `co_statutory_register`.
- **Reconciliation matrix**: the RAG grid from §8.2.
- **Employee analytics dashboard**: cost-center spend, budget vs actual, payroll summaries — the "internal employee dashboard analytics" input, now scoped by role.

**Export formats:** GSTR-1 **JSON** to the GSTN offline-tool schema; Schedule III statements to **PDF/XLSX**; ROC form data sets; and a full **trial-balance/CSV** for the CA. Exports are generated files stored in the object vault and versioned.

---

## 10. Integration — Center Lake Ingress/Egress

The Company segment is a Center Lake node: data enters, is made authoritative, and is then published.

- **Ingress contracts**: every source (GSTSAAS e-invoices, bank feeds, Tally, payroll) posts to a **typed ingestion API** with a JSON schema and `source_hash`. No source writes to L1 directly — the posting engine mediates.
- **Egress / publication**: clean financial facts are published as **read APIs and change events** for (a) other Kailash segments and (b) **Eka Brain** and its 85-agent fleet. The **`finance_lora`** model already present in `eka-brain/models/` is a natural consumer — it should read *published* Company-segment facts (turnover, runway, ITC position), never the raw ledger.
- **Direction of truth**: per the Center Lake rule, data routes **into Kailash first**; Kailash decides distribution. That means the employee dashboards and any agent read **projections**, keeping the ledger single-writer and tamper-evident.
- **Future phase**: as Eka Brain moves training in-house, the same egress contract lets an agent request a period's facts without bespoke plumbing.

---

## 11. Security, Access Control, Audit & Retention

- **RBAC + maker-checker**: roles `owner`, `accountant`, `ca_readonly`, `employee_dashboard`, `auditor`. Posting requires maker≠checker. The **CA gets read + reconciliation** access, not write.
- **Row-level scoping** by GSTIN / cost-center so an employee dashboard sees only its department.
- **Immutability & audit log**: append-only ledger; every state change (draft/post/reverse, master edit, config change) is written to an immutable `co_audit_log` (who/what/when/before/after).
- **PII isolation**: PAN, Aadhaar, bank and salary data are column-encrypted and access-gated separately from the general ledger.
- **Retention** (design to the longest applicable): books & records **8 years** (Companies Act §128(5)); GST records **72 months**; income-tax records **6+ years**. Statutory documents in the vault are WORM-tagged.
- **Backups / DR**: point-in-time recovery on the ledger DB; the object vault is versioned and replicated.

---

## 12. Technology & Repo Mapping

The segment slots into the existing Kailash-Ai stack rather than introducing new infrastructure:

- **Ledger & compliance store**: PostgreSQL (declarative FY partitioning, deferrable constraints, row-level security) — extends the repo's `database/` module.
- **Object vault**: the existing storage bucket (Firebase Storage / S3-compatible) for Day-1 documents and generated statutory files.
- **Services**: `backend/` hosts the ingestion API, posting engine, compliance engines, and reconciliation runner (jobs/cron for period-end builds).
- **UI**: `frontend/` (or a self-contained HTML surface consistent with `launch-control/`) for the L4 dashboards.
- **Config**: effective-dated rate/due-date tables seeded from `compliance/compliance_calendar.csv` and `templates/hsn_gst_rate_master.csv`.

Suggested placement in the repo: a new `company-segment/` module (schema, ingestion, engines, exports) — exactly the scaffold shipped with this spec.

---

## 13. Storage / Folder Layout

The document vault and repo module mirror the data model. Full tree in `docs/FOLDER_STRUCTURE.md`; summary:

```
company-segment/
├── schema/            # PostgreSQL DDL (masters → ledger → compliance → recon → views)
├── templates/         # seed CSVs: COA, party, HSN/GST rates, GSTR-1 map, recon points
├── compliance/        # effective-dated calendar (GST/TDS/IT/ROC)
├── ingestion/         # source contracts (Tally, sales, purchase, bank, payroll)
└── docs/              # folder-structure & data-dictionary

Document vault (object store), FY-partitioned:
Company/
├── 00_Foundation/        # Day-1: incorporation, MOA/AOA, PAN, TAN, GST/PF/ESI certs, Udyam
├── 01_Masters/           # COA, parties, items, HSN, tax rates (exports of live masters)
├── 02_Ledger/FY2025-26/  # journal exports, trial balance snapshots
├── 03_Source_Docs/FY2025-26/{Sales,Purchase,Bank,Payroll,Expenses}
├── 04_GST/FY2025-26/{GSTR1,GSTR3B,GSTR2B,GSTR9}
├── 05_Income_Tax/        # TDS, advance tax, 3CD, ITR-6
├── 06_ROC_MCA/           # AOC-4, MGT-7, DPT-3, MSME-1, resolutions, registers
├── 07_Financials/FY2025-26/  # Schedule III BS, P&L, cash-flow, notes
├── 08_Reconciliation/    # CA-vs-internal control sheets & sign-offs
└── 09_Dashboards/        # generated HTML/PDF snapshots
```

---

## 14. Phased Rollout (mapped to the 3-day baseline deadline)

The goal for the baseline is a **coded, deployed skeleton with real masters and a working end-to-end slice**, not every engine finished — enough to be the "definitive, unalterable baseline" the funding round needs.

| Phase | Deliverable | Depends on |
|---|---|---|
| **P0 — Scaffold (Day 1 am)** | commit `company-segment/` module; create schema in Postgres; load COA, GST-rate, party templates | scaffold shipped here |
| **P1 — Masters + migration (Day 1 pm)** | Tally master mapping; post opening-balance journal; verify trial balance ties to Tally | P0 |
| **P2 — Transactions + GST (Day 2)** | sales/purchase capture → journal; GSTR-1 + GSTR-3B build for one live period; e-invoice IRN capture | P1 |
| **P3 — Reconciliation + reporting (Day 3)** | reconciliation control points 1–8 running; FY dashboard + compliance calendar live; Schedule III draft statements | P2 |
| **Post-baseline** | TDS/ROC engines, GSTR-9/9C, cash-flow, full document vault, agent egress to Eka Brain | baseline |

The **critical path** is P0→P1: nothing computes until the COA is locked and opening balances tie to Tally. Prioritise `templates/chart_of_accounts.csv` review with the CA on Day 1.

---

## Appendix A — Verified Compliance Reference (as of Jul 2026)

| Area | Key figures used in this spec |
|---|---|
| **GST slabs (GST 2.0, eff. 22-Sep-2025)** | 0 / 5 / 18 / 40 %; niche 3 / 0.25 / 12 / 28 %; 12 % & 28 % consolidated |
| **GSTR-1** | monthly 11th; QRMP (≤ ₹5 cr) quarterly 13th; IFF 13th; GSTR-1A pre-3B |
| **GSTR-3B** | monthly 20th; QRMP 22nd/24th; auto-populated, sequential, trend to hard-lock |
| **GSTR-9 / 9C** | 31 Dec; 9 optional ≤ ₹2 cr; 9C required > ₹5 cr |
| **E-invoicing** | mandatory > ₹5 cr aggregate turnover (IRN+QR) |
| **Return time-bar** | no filing after 3 years past due date |
| **TDS** | deposit 7th (Mar→30 Apr); returns 24Q/26Q/27Q due 31 Jul/31 Oct/31 Jan/31 May; Form 16 by 15 Jun |
| **Advance tax** | 15/45/75/100 % by 15 Jun/15 Sep/15 Dec/15 Mar |
| **Tax audit (44AB)** | > ₹1 cr (or > ₹10 cr if ≥95 % digital); report 30 Sep; ITR-6 31 Oct / 30 Nov (TP) |
| **ROC (FY25-26, AGM ≤ 30-Sep-26)** | ADT-1 +15d; AOC-4 +30d; MGT-7 +60d; DPT-3 30 Jun; DIR-3 KYC 30 Sep; MSME-1 30 Apr & 31 Oct |

*Rates and dates are held in effective-dated config, not code; verify against the GSTN/MCA/Income-tax portals at each period-end.*

## Appendix B — Glossary

**AR/AP** accounts receivable/payable · **COA** chart of accounts · **CDNR** credit/debit notes (registered) · **HSN/SAC** goods/services tax codes · **ITC** input tax credit · **IRN** invoice reference number (e-invoice) · **QRMP** quarterly return, monthly payment · **Schedule III** Companies Act statement format · **SoR** system of record · **SRN** MCA service request number · **UQC** unit quantity code.

---

*End of specification. Scaffold (schema + templates + calendar) accompanies this document under `company-segment/`.*




