# Company Segment — Folder & Storage Layout

Two mirrored structures: the **repo module** (code/schema/config) and the **document vault**
(the object-store side that holds primary documents and generated statutory files, FY-partitioned).

## A. Repo module (commit into Kailash-Ai)

```
company-segment/
├── schema/            PostgreSQL DDL (masters → ledger → compliance → recon → views)
├── templates/         Seed CSVs (COA, GST rates, parties, GSTR-1 map, recon points)
├── compliance/        Effective-dated calendar (GST/TDS/income-tax/ROC)
├── ingestion/         Source contracts (Tally, sales, purchase, bank, payroll) + JSON schemas
└── docs/              This file + data dictionary
```

## B. Document vault (object store, FY-partitioned)

```
Company/
├── 00_Foundation/                 # DAY-1 corporate identity (static reference)
│   ├── Incorporation/             #   Certificate of Incorporation, CIN, MOA, AOA
│   ├── Registrations/             #   PAN, TAN, GST certs, PF, ESI, Udyam/MSME, Startup-India
│   ├── Statutory_Registers/       #   members, directors, charges, related-party
│   └── Bank_KYC/                  #   bank account opening / KYC
├── 01_Masters/                    # exports of live masters (COA, parties, items, rates)
├── 02_Ledger/
│   └── FY2025-26/                 #   journal exports, trial-balance snapshots
├── 03_Source_Docs/
│   └── FY2025-26/
│       ├── Sales/                 #   tax invoices, e-invoice IRN payloads
│       ├── Purchase/              #   vendor bills, GSTR-2B extracts
│       ├── Bank/                  #   statements (CSV/MT940/ISO 20022)
│       ├── Payroll/               #   payroll runs, payslips
│       └── Expenses/              #   expense vouchers, receipts
├── 04_GST/
│   └── FY2025-26/{GSTR1,GSTR3B,GSTR2B,GSTR9}   # generated returns (JSON + filed proofs)
├── 05_Income_Tax/                 # TDS challans/returns, advance tax, 3CD, ITR-6
├── 06_ROC_MCA/                    # AOC-4, MGT-7, DPT-3, MSME-1, DIR-3 KYC, resolutions
├── 07_Financials/
│   └── FY2025-26/                 #   Schedule III BS, P&L, cash-flow, notes (PDF/XLSX)
├── 08_Reconciliation/             # CA-vs-internal control sheets & sign-offs
└── 09_Dashboards/                 # generated HTML/PDF dashboard snapshots
```

**Why "Day-1" (`00_Foundation`) is separate:** these are documents, not transactions. They
populate the identity fields (`co_company`, `co_gstin`, `co_statutory_register`) that every GST
return header and every ROC form depends on — the compliance engines cannot address a filing
without them.

**FY partitioning everywhere:** because every Indian statutory report (GST period, Schedule III
statement, ROC form, ITR) is financial-year scoped, both the ledger partitions and the vault
folders are cut by FY, so a closed year becomes a clean, read-only archive.
