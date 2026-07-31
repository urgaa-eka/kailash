# Company Segment — Data Dictionary (summary)

All tables use the `co_` prefix inside the `company` PostgreSQL schema. Surrogate PKs are IDENTITY
columns; natural keys (GSTIN, PAN, invoice-no) carry UNIQUE constraints.

## Masters
| Table | Grain | Key columns |
|---|---|---|
| `co_company` | one legal entity | cin, pan, tan, incorporation_dt, authorised/paidup capital |
| `co_gstin` | one GST registration (per state) | gstin, state_code, einvoice_applicable |
| `co_fiscal_calendar` | one date | fy, quarter, month_no, gst_period |
| `co_account` | one COA node | account_type, normal_balance, schedule_iii_group, tax_nature |
| `co_party` | one customer/vendor | gstin, pan, state_code, is_msme, tds_applicable |
| `co_item` | one good/service | hsn_sac, uqc, default_tax_rate_id |
| `co_tax_rate` | one GST slab (effective-dated) | total_rate, cgst/sgst/igst/cess, effective_from |
| `co_cost_center` | one department/project | parent_id |
| `co_employee` | one employee | pan, uan, esi_no, ctc_annual |
| `co_bank_account` | one bank account | ifsc, ledger_account_id |
| `co_document_series` | one numbering series | gstin_id, voucher_type, fy, last_number |

## Ledger core (system of record)
| Table | Grain | Notes |
|---|---|---|
| `co_journal` | one voucher header | FY-partitioned; status draft/posted/reversed; immutable once posted |
| `co_journal_line` | one posting | exactly one of debit/credit > 0; `Σdebit = Σcredit` per journal |

## Transaction capture
`co_sales_invoice`/`co_sales_line`, `co_purchase_bill`/`co_purchase_line`, `co_bank_txn`,
`co_payroll_run`/`co_payslip`, `co_fixed_asset`. Each generates a balanced journal and links via
`journal_id`.

## Compliance / output
`co_gstr1` (+JSONB payload), `co_gstr3b_summary`, `co_itc_register`, `co_tds_ledger`,
`co_financial_statement_line` (versioned Schedule III lines), `co_roc_filing`, `co_statutory_register`.

## Reconciliation
`co_recon_control_point` (definition + tolerance) → `co_recon_run` (internal vs external values) →
`co_recon_variance` (amount, %, severity, status, resolution).

## Governance
`co_audit_log` (append-only), `co_ingest_error` (error queue), `co_map_tally` (Tally→Kailash mapping).

## Key views (L4)
| View | Produces |
|---|---|
| `co_v_trial_balance` | debit/credit/net per account per FY |
| `co_v_schedule_iii` | P&L + Balance Sheet rolled up by Schedule III group |
| `co_v_gstr1_feed` | outward-supply rows shaped for GSTR-1 |
| `co_v_open_variances` | unresolved reconciliation items (RAG matrix source) |
