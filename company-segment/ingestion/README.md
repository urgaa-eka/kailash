# Ingestion Contracts

Every source posts through a **typed contract**, never directly to the ledger. The posting engine
mediates: `validate schema → dedup by source_hash → resolve masters → compute tax → draft journal →
maker-checker → post`. Failures land in `co_ingest_error` with a reason code.

## Sources

| Source | Contract | Produces (journal) |
|---|---|---|
| **Tally** (migration) | XML export → `co_stg_tally_*` → `co_map_tally` | opening-balance + historical journals (`origin=TALLY_MIGRATION`) |
| **Sales** | `sales_invoice.contract.json` | Dr Debtor · Cr Sales · Cr Output CGST/SGST/IGST |
| **Purchase** | `purchase_bill.contract.json` (model on sales) | Dr Purchase/Expense · Dr Input GST (if eligible) · Cr Creditor |
| **Bank** | `bank_statement.contract.json` | Dr/Cr Bank ↔ contra; flagged for BRS |
| **Payroll** | `payroll_run.contract.json` | Dr Salary · Cr Bank/PF/ESI/TDS-payable |

## Universal rules

- **`source_hash`** (SHA-256 of the canonical document) is mandatory and UNIQUE — re-ingesting the
  same document is a no-op (idempotent).
- **Master resolution**: parties/items are matched by GSTIN/HSN or created via a review queue; never
  auto-created silently for GST-bearing documents.
- **Tax computation** uses `co_tax_rate` effective on the document date (so pre/post GST-2.0 invoices
  compute correctly).
- **Place-of-supply** decides CGST+SGST vs IGST (supplier GSTIN state vs place_of_supply).
- Nothing posts unbalanced — the DB rejects it at post time.

See `sales_invoice.contract.json` for the canonical example; the other contracts follow the same shape.
