"""Known defects (D1–D17) and open decisions (Q1–Q10) — the internal-audit gate.

Structured qualitatively: each entry names the defect/decision, the department it
sits in, and the guard or rule that neutralises it. The specific rupee exposures
live in the source data (quantified at run time), not in this file — this is the
*rule*, not the *number*.

Department 10 (Internal Audit) uses this registry to veto any figure that has not
cleared its guard (KP §1.8, §4).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Defect:
    id: str
    dept: int
    title: str
    guard: str          # what to do so the defect cannot propagate
    severity: str       # material | major | minor
    status: str = "open"   # open | mitigated | fixed | withdrawn


# The confirmed defects (KP §4.1). Amounts are deliberately omitted; the guard is
# the load-bearing part.
DEFECTS = [
    Defect("D1", 2, "Zoho over-deducts commission & TDS by exactly 1.18×",
           "Trust the purchase register, not Zoho, for any vendor balance; recompute at 15% / 2%",
           "material"),
    Defect("D2", 7, "Workshop Summary `Outstanding` column is unreliable (95/133 wrong)",
           "Never read Outstanding; recompute Total Payable − Paid (₹1 floor)", "material"),
    Defect("D3", 7, "A set of workshops are overpaid",
           "Recompute overpayment; do not chase recovery until `Paid` is bank-reconciled", "major"),
    Defect("D4", 3, "Zoho vendor payments are transcribed bank narrations, not independent",
           "Treat register `Paid` classes (RECONCILED/PARTIAL/CONTRADICTED/NO_TRACE) as the evidence", "material"),
    Defect("D5", 3, "A broken all-tokens matcher discarded 35% of confirmed payments",
           "Withdrawn — do not apply; it destroys exactly-reconciling records", "major", "withdrawn"),
    Defect("D6", 3, "ICICI 'FY2025-26' section is FY2023-24 re-dated +2 years",
           "Never import/cite it; gate every import on the bank-verify step", "material"),
    Defect("D7", 6, "Bills posted on several mutually inconsistent bases",
           "Reconcile the posting basis before trusting ITC / GSTR-2B", "material"),
    Defect("D8", 2, "Register internally inconsistent (Taxable+IGST ≠ Approved on some rows)",
           "Treat Approved as primary; re-derive tax; reconcile before use", "major"),
    Defect("D9", 7, "'Star Motors' is not 'StarCars' — unrelated workshops",
           "Match workshops by CODE, never by name substring", "material"),
    Defect("D10", 2, "Star Motors GST flags contradict each other",
           "Open question Q2; do not auto-deduct IGST until resolved", "minor", "open"),
    Defect("D11", 6, "Item-level tax_id silently dropped in the India edition",
           "Fixed via item_tax_preferences (2026-08-03)", "major", "fixed"),
    Defect("D12", 1, "Customers had blank gst_no; place_of_contact defaulted to UP",
           "Set place_of_contact and let Zoho re-derive tax; add missing customer GSTINs", "major", "mitigated"),
    Defect("D13", 6, "Duplicate / near-duplicate ledgers in the chart of accounts",
           "Map opening balances to canonical ledgers; avoid the duplicate parents", "major"),
    Defect("D14", 6, "Duplicate 26AS invoices (H-FY* voided)",
           "Canonical series is H23-*..H25-*; never re-post HIST-*/H-FY*", "minor", "fixed"),
    Defect("D15", 8, "Register header CIN conflicts with MCA/Zoho",
           "Use U34300UP2021PTC145107; purge the register-header CIN", "major", "mitigated"),
    Defect("D16", 2, "Smaller register gaps (blank workshop / zero-approved rows)",
           "Nil-value jobs are correct, not gaps; nothing to post", "minor"),
    Defect("D17", 6, "Vyapar txn_type labels are inference, not documentation",
           "Do not post on inferred type; concatenate prefix||ref to match invoice numbers", "minor"),
]


@dataclass(frozen=True)
class OpenDecision:
    id: str
    dept: int
    question: str
    owner: str          # who must decide — owner or CA


# The ten open decisions (KP §4 / AGENT-INSTRUCTION §9). Escalate, never resolve
# alone. Exposure amounts are held in the source data.
OPEN_DECISIONS = [
    OpenDecision("Q1", 2, "Authoritative base for commission & TDS — Approved Amt or Taxable × 1.18?", "CA"),
    OpenDecision("Q2", 7, "Is Star Motors GST-registered? Flags contradict (No.=Not Found, Status=Available)", "owner"),
    OpenDecision("Q3", 2, "537 rows carry zero commission — genuine 0% terms or a missing rule?", "owner"),
    OpenDecision("Q4", 3, "Classification of the uncategorised bank lines", "owner"),
    OpenDecision("Q5", 3, "Slice account — company or Vivek Raj personally?", "owner"),
    OpenDecision("Q6", 3, "Cash at Bank ₹470 — ICICI or YES, or split?", "CA"),
    OpenDecision("Q7", 6, "Opening-balance sign-off", "CA"),
    OpenDecision("Q8", 6, "Historical expense drafts still holding REPLACE_WITH_* placeholders", "owner"),
    OpenDecision("Q9", 7, "Recovery outreach on apparently-overpaid workshops", "owner"),
    OpenDecision("Q10", 1, "Are the aggregate historical invoices the right treatment at all?", "CA"),
]
