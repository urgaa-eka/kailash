"""Go4Garage financial logic — the confirmed formulas and the guards.

Pure functions, no I/O. This module encodes the rules the Agent Knowledge Pack
confirmed against source (Net Payable, the two approval-layer gates, FY-from-date,
the deduplication key, the "never trust this column" guards). It holds **no
financial values** — every rupee figure comes from a data provider at run time,
supplied after deployment. What lives here is the *logic*, which is testable in
isolation and must never drift.

Section references are to the Go4Garage Agent Knowledge Pack.
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

# Confirmed commercial rates (KP §1.5 / §3.3). These are the *logic*, verified to
# the paisa across the register — not values to fill in:
#   Commission 15.00% flat (or a genuine 0% — open decision Q3), TDS 2.000% flat.
# Never reverse-engineer the commission rate from ledger ratios (KP §1.9): it was
# 12% originally, later 15%.
COMMISSION_RATE = Decimal("0.15")
TDS_RATE = Decimal("0.02")

# The one GST-status string that switches IGST from "claimed as ITC" to "deducted
# from the vendor" (KP §1.5). Compared case-insensitively, trimmed.
GST_STATUS_NOT_AVAILABLE = "not available"


def _dec(v) -> Decimal:
    """Money as Decimal. None/blank -> 0. Never float-parse a rupee figure."""
    if v is None or v == "":
        return Decimal("0")
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


# --------------------------------------------------------------------------
# The Net Payable formula (KP §1.5, §3.3) — confirmed on 2,125 of 2,125 rows
# --------------------------------------------------------------------------

def commission(approved, rate: Decimal = COMMISSION_RATE) -> Decimal:
    """Commission on the VENDOR-FACING approved amount (never the client figure)."""
    return _dec(approved) * rate


def tds(approved, rate: Decimal = TDS_RATE) -> Decimal:
    """TDS on the vendor-facing approved amount. A deduction, not a supply — no GST."""
    return _dec(approved) * rate


def igst_is_deducted(gst_status: str | None) -> bool:
    """IGST is deducted from the vendor ONLY when GST Status = "Not Available".

    Otherwise the vendor charged GST that Go4Garage reclaims as ITC, so it is not
    withheld. This single condition decides which Net Payable variant applies.
    """
    return (gst_status or "").strip().lower() == GST_STATUS_NOT_AVAILABLE


def net_payable(approved, commission_amt, tds_amt, igst, gst_status: str | None) -> Decimal:
    """Net Payable = Approved − Commission − TDS − IGST(only if GST "Not Available").

    Commission and TDS are always deducted; IGST is deducted only on the
    Not-Available branch (KP §3.3). Amounts are passed in rather than recomputed
    so a caller can feed the register's own figures and reconcile against this.
    """
    net = _dec(approved) - _dec(commission_amt) - _dec(tds_amt)
    if igst_is_deducted(gst_status):
        net -= _dec(igst)
    return net


def net_payable_at_confirmed_rates(approved, igst, gst_status: str | None) -> Decimal:
    """Net Payable recomputed from the approved amount at the confirmed rates.

    Uses COMMISSION_RATE and TDS_RATE. Handy for a "what the register *should*
    say" check against defect D1 (Zoho over-deducts by exactly 1.18×).
    """
    return net_payable(approved, commission(approved), tds(approved), igst, gst_status)


# --------------------------------------------------------------------------
# The two approval layers must never meet (KP §1.3)
# --------------------------------------------------------------------------

def assert_layers_separate() -> None:
    """A structural reminder: there is NO function that joins the client approval
    to the vendor approval, because no such relationship exists. Margin is a
    P&L-level emergent figure (sales − net purchase cost), never a per-job spread.
    Any code that needs a per-job margin is wrong by construction (KP §1.3, §3.6).
    """
    raise NotImplementedError(
        "client approval and vendor approval are independent tracks; there is no "
        "per-job spread to compute (KP §1.3)")


# --------------------------------------------------------------------------
# The two validation gates on an incoming vendor bill (KP §1.4)
# --------------------------------------------------------------------------

def gate_reference_in_sales(g4g_ref: str, sales_refs: Iterable[str]) -> bool:
    """Gate 1: the G4G reference must exist in the sales ledger.

    If it does not, the job was never billed to a client — leakage or a fake
    vendor invoice. The sales ledger has no duplicate references, so this is a
    hard check.
    """
    return g4g_ref in set(sales_refs)


def gate_within_approval(billed, approval) -> bool:
    """Gate 2: the billed amount must be within the approval shared with that
    vendor. Anything above is invalid unless the vendor produces the Go4Garage
    approval PDF (which this gate cannot see, so excess fails here by default).
    """
    return _dec(billed) <= _dec(approval)


@dataclass(frozen=True)
class BillVerdict:
    accepted: bool
    reason: str


def validate_vendor_bill(g4g_ref: str, billed, approval, sales_refs: Iterable[str]) -> BillVerdict:
    """Both gates, in order. Reason names the first gate that failed."""
    if not gate_reference_in_sales(g4g_ref, sales_refs):
        return BillVerdict(False, "reference absent from sales ledger — leakage or fake invoice")
    if not gate_within_approval(billed, approval):
        return BillVerdict(False, "billed above the shared approval — needs the approval PDF")
    return BillVerdict(True, "within approval and referenced in sales")


# --------------------------------------------------------------------------
# Financial-year derivation — THE highest-value trap (KP §3.5)
# --------------------------------------------------------------------------

def financial_year(d: date) -> str:
    """Indian FY (April–March) from a DATE, formatted `YYYY-YY`.

    The sales ledger's `Financial Year` column is the invoice-number prefix, not
    the date, and misallocates ₹2.96 Cr across 1,358 rows. FY is ALWAYS derived
    from the date, never read from that column (KP §3.5).
    """
    start = d.year if d.month >= 4 else d.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


# --------------------------------------------------------------------------
# "Never trust this column" guards (KP §3.7, §3.8, §3.9)
# --------------------------------------------------------------------------

def recompute_outstanding(total_payable, paid, floor: Decimal = Decimal("1")) -> Decimal:
    """Outstanding = Total Payable − Paid, recomputed — never read.

    The Workshop Summary `Outstanding` column is wrong on 95 of 133 rows. A ₹1
    floor suppresses sub-rupee artifacts (the 18-paise overpayment that turns 47
    genuine overpayments into a spurious 48) (KP §3.7, D2/D3).
    """
    out = _dec(total_payable) - _dec(paid)
    return Decimal("0") if abs(out) < floor else out


def is_overpaid(total_payable, paid, floor: Decimal = Decimal("1")) -> bool:
    """Paid exceeds payable beyond the ₹1 floor. Do not act on it until the
    `Paid` figure is bank-reconciled (KP §6 rule 17 / D3)."""
    return _dec(paid) - _dec(total_payable) > floor


def is_total_row(description: str | None) -> bool:
    """A combined bank statement carries a `TOTAL` row inside each bank's data
    range; a naive sum double-counts. Skip every row whose Description is TOTAL
    (KP §3.8)."""
    return (description or "").strip().upper() == "TOTAL"


def dedup_key(row: dict) -> tuple:
    """The GST-invoice identity for de-duplication (KP defect on §2.5 / §4).

    A naive sum of a GST workbook's `Invoice Value` overstates by ₹5.10 Cr
    because split rows repeat. Deduplicate on this 6-tuple before summing.
    """
    return (
        (row.get("state") or "").strip(),
        (row.get("gstin") or "").strip(),
        (row.get("period") or "").strip(),
        (row.get("counterparty_gstin") or "").strip(),
        (row.get("invoice_no") or "").strip(),
        (row.get("invoice_date") or "").strip(),
    )


# --------------------------------------------------------------------------
# GSTIN validity — 58 register GSTINs will fail Zoho (KP §3.4)
# --------------------------------------------------------------------------

_ABSENT_GSTIN = {"", "not available", "not found", "ambiguous"}


def gstin_is_present(gstin: str | None) -> bool:
    return (gstin or "").strip().lower() not in _ABSENT_GSTIN


def gstin_is_malformed(gstin: str | None) -> bool:
    """True for a present-but-invalid GSTIN.

    Position 13 (1-indexed) must be a digit (the registration count); the known
    defect is a capital `I` there, e.g. `36AXNPS4900RIZM`. A 15-char GSTIN whose
    13th character is not a digit is malformed and will fail Zoho validation
    (KP §3.4). Absent markers ("Not Available"/"Not Found"/blank) are not
    malformed — they are simply absent.
    """
    g = (gstin or "").strip()
    if not gstin_is_present(g):
        return False
    return not (len(g) == 15 and g[12].isdigit())


# --------------------------------------------------------------------------
# Related parties (KP §1.1) and vendor-name identity (KP §3.4 / D9)
# --------------------------------------------------------------------------

_RELATED_PARTY_KEYS = {"vivek raj", "vivek gupta", "vevek gupta", "sapna gupta"}


def is_related_party(name: str | None) -> bool:
    """Vivek Raj and Sapna Gupta (mother and son) and their name variants.

    Every transaction between them and the company is a related-party
    transaction under AS 18 / Ind AS 24 / s.188 (KP §1.1).
    """
    n = re.sub(r"\balias\b", " ", (name or "").strip().lower())
    n = re.sub(r"[^a-z\s]", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    if n in _RELATED_PARTY_KEYS:
        return True
    # "Vivek Raj Alias Vivek Gupta" -> tokens contain a known full name.
    return any(key in f" {n} " for key in (" vivek raj ", " vivek gupta ", " sapna gupta "))


def same_workshop(a: str | None, b: str | None) -> bool:
    """Workshop identity is by CODE, never by name substring. Star Motors ≠
    StarCars; "KM Motors" is a KMAuto duplicate (KP §3.4 / D9). This helper only
    affirms an EXACT normalised match and never substring-matches — a name
    matcher's silence is never evidence of absence.
    """
    def norm(s):
        return re.sub(r"\s+", " ", (s or "").strip().lower())
    return norm(a) == norm(b) and norm(a) != ""
