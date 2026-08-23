"""Confirmed per-FY figures from the Go4Garage Agent Knowledge Pack.

These are Go4Garage's own financial figures, committed with the owner's
authorisation to populate the FY dashboard. Only the Knowledge Pack's
**confirmed** numbers are recorded here — those recomputed from source and tied
to a grand total. Where the Pack flags contradictory values for the same fact,
the flag is carried in `flags` and the dashboard surfaces it; the number is never
silently picked (evidence standard, AGENT-INSTRUCTION §7).

Two grand totals verify the transcription (see test_go4garage_kp_data):
  Σ purchase Approved = ₹2,77,90,802.65  (KP §3.2)
  Σ sales (date-derived) = ₹4,83,53,442.80  (KP §3.5)

Section references (KP §): 2.2 audited, 2.3 26AS, 2.4 ITR, 2.5 GST register,
3.2 purchase register, 3.5 date-derived sales, 3.8 bank. All rupee figures are
strings, parsed to Decimal by the provider.
"""
from __future__ import annotations

# Per-FY confirmed figures. `None` means "not in the archive for this year"; an
# empty list means "no rows". AY maps to FY as AY − 1 (26AS/ITR).
KP_FY: dict[str, dict] = {
    "2021-22": {
        "audited": {"revenue": "2046920", "pat": "-2259570"},
        "purchase": None,                      # register starts FY22-23 (§3.2)
        "sales": {"invoices": None, "total_sales": None},   # no invoice PDFs (§2.6)
        "bank": [],                            # no bank data on any bank (§3.8)
        "gst": None,                           # no GST register (§2.5)
        "tax": {"tds_26as": "0", "itr_status": "FILED · 139(4) belated"},
        "flags": [
            "FY21-22 loss stated three ways (−22,59,570 / −22,59,586 / 22,59,580) — "
            "OCR/read uncertainty, not a booked difference (KP §2.8#1)",
            "Revenue ₹20,46,920 exceeds filed GSTR-3B turnover ₹16,62,364 by ₹3,84,556 (KP §2.9)",
        ],
    },
    "2022-23": {
        "audited": {"revenue": "11691180", "pat": "340235"},
        "purchase": {"rows": 581, "approved": "7859082.22", "commission": "1178862.33",
                     "tds": "157181.64", "igst": "1411070.81", "net_payable": "6302667.52"},
        "sales": {"invoices": 556, "total_sales": "9527680.95"},
        "bank": [{"bank": "ICICI", "debit": "9020073.89", "credit": "9296179.60"},
                 {"bank": "AU", "debit": "2974789.25", "credit": "3005719.00"}],
        "gst": {"gstin": "09AAICG9768N1ZI", "r1_taxable": "8352628.21",
                "output_tax": "1801030.18"},   # register aggregate (§2.5); per-GSTIN split needs portal data
        "tax": {"tds_26as": "137398.02", "itr_status": "FILED · 139(1) · refundable ₹17,850"},
        "flags": [
            "Revenue stated four ways: audited 1,16,91,180 → restated 81,63,000 → "
            "GST-register taxable 83,52,628.21 → 26AS credited 68,69,855.57 (KP §2.8#3)",
            "Six months of sales invoices missing (PDFs begin 04-10-2022) (KP §2.9)",
        ],
    },
    "2023-24": {
        "audited": {"revenue": "25238000", "pat": "826420.01"},
        "purchase": {"rows": 1408, "approved": "19820967.43", "commission": "1662424.09",
                     "tds": "396419.35", "igst": "3415060.24", "net_payable": "16865684.42"},
        "sales": {"invoices": 1363, "total_sales": "29604776.60"},
        "bank": [{"bank": "ICICI", "debit": "33917702.04", "credit": "33833386.32"}],
        "gst": {"gstin": "09AAICG9768N1ZI", "r1_taxable": "24491723.08",
                "output_tax": "5387856.66"},
        "tax": {"tds_26as": "469555.00", "itr_status": "NOT FILED (AY2024-25)"},
        "flags": [
            "Audit opinion is QUALIFIED; GST ₹20,99,000 and TDS ₹2,83,000 undischarged (KP §2.9)",
            "FY23-24 change of ownership with no transfer disclosed; shareholding totals 100.02% (KP §2.8#9)",
        ],
    },
    "2024-25": {
        "audited": None,                       # no financial statements (§2.1)
        "purchase": {"rows": 136, "approved": "110753.00", "commission": "0",
                     "tds": "2215.06", "igst": "0", "net_payable": "108537.94"},
        "sales": {"invoices": 91, "total_sales": "8021661.25"},
        "bank": [{"bank": "ICICI", "debit": "1602875.61", "credit": None},
                 {"bank": "YES", "debit": "1587585", "credit": None}],
        "gst": {"gstin": "09AAICG9768N1ZI", "r1_taxable": "5612348.22",
                "output_tax": "1379921.21"},
        "tax": {"tds_26as": "588272.19", "itr_status": "NOT FILED (AY2025-26)"},
        "flags": [
            "Date-derived sales 91 inv / 80,21,661.25 vs compiled workbook 137 inv / "
            "71,51,744.25 — date-derived is authoritative (KP §2.8#10)",
            "Invoice PDFs stop 14-10-2024; Nov'24–Mar'25 sales have no document support (KP §2.9)",
        ],
    },
    "2025-26": {
        "audited": None,
        "purchase": None,                      # register does not reach FY25-26
        "sales": {"invoices": 1, "total_sales": "1199324.00"},
        "bank": [{"bank": "ICICI", "debit": "10723043.00", "credit": None, "excluded_rows": 695},
                 {"bank": "Slice", "debit": None, "credit": None, "excluded_rows": 913}],
        "gst": None,
        "tax": {"tds_26as": "0", "itr_status": "NOT FILED"},
        "flags": [
            "ICICI 'FY25-26' block: 695/718 rows are FY23-24 re-dated +2yr, ₹2.13 Cr phantom — "
            "quarantined, never cited as bank evidence (KP §3.8, D6)",
            "All 913 Slice rows ruled personal (director), excluded from company bank (KP §3.8)",
            "No audit, no ITR; reconstruct from Zoho + bank sourced elsewhere (KP §2.9)",
        ],
    },
}

# The grand totals the sums must tie to (KP §3.2 / §3.5) — the transcription check.
PURCHASE_APPROVED_TOTAL = "27790802.65"
SALES_DATE_DERIVED_TOTAL = "48353442.80"
