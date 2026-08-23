"""Go4Garage structural model — public facts, FYs, departments, rebuild shape.

Everything here is either a public registry fact (CIN, GSTIN, DIN — all on the
MCA / GST portals) or a structural constant from the Agent Knowledge Pack (which
FYs exist, their audit status, the ten departments, the Zoho rebuild shape).

It carries **no private financial values**: no revenue, no PAT, no balances, no
journal amounts. Those are supplied by a data provider after deployment (see
provider.py). Audit *status* is structural; audit *figures* are not committed.
"""
from __future__ import annotations

from dataclasses import dataclass

# --------------------------------------------------------------------------
# The entity — public registry identifiers (KP §1.1)
# --------------------------------------------------------------------------

ENTITY = {
    "name": "GO4GARAGE PRIVATE LIMITED",
    "cin": "U34300UP2021PTC145107",          # resolved; the register-header U74900… is purged (KP §1.1, D15)
    "pan": "AAICG9768N",
    "tan": "MRTG10143A",
    "incorporated": "2021-04-14",
    "registered_office": "Block B RN-75, Sector 62 Noida, Gautam Buddha Nagar, UP 201301",
    "class": "Private, limited by shares, non-government",
    "roc": "ROC Kanpur",
    "msme_udyam": "UDYAM-HR-05-0114512",
    "dpiit": "DIPP203673",
}

# Three GST registrations (KP §1.1). All public.
GSTINS = [
    {"gstin": "09AAICG9768N1ZI", "state": "Uttar Pradesh", "role": "Head office"},
    {"gstin": "06AAICG9768N1ZO", "state": "Haryana", "role": "Branch"},
    {"gstin": "10AAICG9768N1ZZ", "state": "Bihar", "role": "Branch (suspended)"},
]

# Directors — public (MCA). The mother/son relationship makes every transaction
# with them a related-party transaction (KP §1.1).
DIRECTORS = [
    {"name": "VIVEK RAJ", "din": "10247670", "appointed": "2023-07-21"},
    {"name": "SAPNA GUPTA", "din": "10166695", "appointed": "2023-05-12"},
]
RELATED_PARTY_NOTE = ("Vivek Raj and Sapna Gupta are son and mother; treat every "
                      "transaction with either as related-party (AS 18 / Ind AS 24 / s.188).")


# --------------------------------------------------------------------------
# The five financial years and their audit status (KP §2.1) — status only
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class FinancialYearMeta:
    fy: str
    audit_status: str          # AUDITED_SIGNED | AUDITED_QUALIFIED | UNAUDITED | NONE
    posture: str               # CLOSED (journalised) | OPEN (build in detail)
    note: str = ""


FINANCIAL_YEARS = [
    FinancialYearMeta("2021-22", "AUDITED_SIGNED", "CLOSED", "Auditor Avdhesh; PDF is a pure scan"),
    FinancialYearMeta("2022-23", "AUDITED_SIGNED", "CLOSED", "P C Modi & Co; six months of invoices missing"),
    FinancialYearMeta("2023-24", "AUDITED_QUALIFIED", "CLOSED", "Agarwal Singh & Madhur; qualified opinion"),
    FinancialYearMeta("2024-25", "UNAUDITED", "OPEN", "No financial statements; build in transaction detail"),
    FinancialYearMeta("2025-26", "NONE", "OPEN", "No evidence beyond a nil 26AS; source from Zoho + bank"),
]

# The audited-close cutoff. NEVER post a transaction-level document dated on or
# before this into the target org — the closed years are carried by summary
# journals and a detail posting double-counts (KP §5, AGENT-INSTRUCTION §5).
CLOSED_YEAR_CUTOFF = "2024-03-31"


# --------------------------------------------------------------------------
# The Zoho position (KP §5) — structural only, no amounts
# --------------------------------------------------------------------------

ZOHO = {
    # The target org. The older 60081359225 is ABANDONED (locked out) and every
    # account ID in historical reports/scripts is a dead old-org ID — always read
    # IDs live before posting.
    "target_org": "60083342031",
    "abandoned_org": "60081359225",
    "id_namespace_target": "4104093…",
    "id_namespace_abandoned": "4031016…",
}

# The six summary journals that already close the three audited years in the
# target org (labels only — amounts come from the live org, never committed here).
CLOSED_YEAR_JOURNALS = [
    "G4G-OB-2021", "G4G-FY2122", "G4G-FY2223-RECLASS",
    "G4G-FY2223", "G4G-FY2324", "G4G-SUBLEDGER-2024",
]


# --------------------------------------------------------------------------
# The ten departments (KP §1.8) — the organising structure of the dashboard
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Department:
    num: int
    name: str
    owns: str
    source_of_truth: str
    standing_defect: str = ""
    cross_cutting: bool = False


DEPARTMENTS = [
    Department(1, "Sales / Client Billing",
               "Client approval → invoice → outward GSTR-1 → receivable → collection",
               "Go4Garage_Sales_Ledger_FINAL.xlsx",
               "Income-account mapping undefined; FY column is the invoice prefix, not the date"),
    Department(2, "Vendor / Workshop Settlement",
               "Vendor approval (a ceiling) → vendor bill → two gates → Net Payable",
               "Go4Garage_Purchase_Register_v4.xlsx",
               "537 rows carry zero commission with no rule; 58 malformed GSTINs"),
    Department(3, "Treasury / Banking & Reconciliation",
               "Pay vendors → match bank → company vs director-personal funds",
               "bank-statement-verified.json",
               "All three ICICI statements are credit-filtered; FY21-22 has no bank data"),
    Department(4, "GST / Indirect Tax",
               "3 GSTINs × R1/2B/3B, ITC, vendor-3B-default holdback",
               "gst-portal extracts",
               "UP over-claimed ITC; all three GSTINs non-filing since Mar'25; Bihar suspended"),
    Department(5, "Direct Tax / TDS",
               "2% deduction → 26Q → challans → 26AS → company ITR",
               "Form 26AS + ITR acknowledgements",
               "No ITR filed for AY2024-25 or AY2025-26"),
    Department(6, "Accounting / Controller (Books)",
               "Chart of accounts, journals, provisions, per-FY close, all Zoho posting",
               "Audited financials + Zoho org 60083342031",
               "Target org is a near-empty rebuild; closed years are journals, not detail"),
    Department(7, "Master Data & Vendor Governance",
               "133 workshops, codes, GSTIN validity, payee identity",
               "Workshop Summary",
               "Identity is by code, never name substring (Star Motors ≠ StarCars)"),
    Department(8, "Statutory / Secretarial (MCA-ROC)",
               "Audit, ROC, share capital, directors, registered office",
               "COI + MCA master data",
               "FY23-24 change of ownership undisclosed; shareholding totals 100.02%"),
    Department(9, "Legal & Disputes",
               "ZoomCar NCLT/NeSL claim, vendor over-billing, set-off",
               "The 709-page litigation bundle",
               "The company's own two filings differ by ₹13.19 lakh and 13 months"),
    Department(10, "Internal Audit",
               "Verifies every other department's claim before it posts",
               "— (cross-cutting)",
               "Has a veto; caught the bank re-dating",
               cross_cutting=True),
]
