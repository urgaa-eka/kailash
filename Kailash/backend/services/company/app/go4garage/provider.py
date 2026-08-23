"""Financial data provider — the seam between logic and live data.

The FY dashboard renders its whole structure from `model`/`defects` and computes
every number through `logic`. The actual figures come from a provider that this
module defines as a Protocol. Ship the structure now; connect a real provider
(Zoho Books org 60083342031, Supabase Postgres, or the Kailash ledger) after
deployment. Until then `NullProvider` returns Nones and the dashboard shows
"awaiting source" — no fabricated values.

All money fields are Optional[Decimal]; None means "not yet sourced".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol, runtime_checkable

Money = Decimal | None


@dataclass(frozen=True)
class SalesSummary:
    invoices: int | None = None
    total_sales: Money = None
    receivable: Money = None


@dataclass(frozen=True)
class PurchaseSummary:
    rows: int | None = None
    approved: Money = None
    commission: Money = None
    tds: Money = None
    igst_deducted: Money = None
    net_payable: Money = None
    paid: Money = None
    outstanding: Money = None
    zero_commission_rows: int | None = None   # open decision Q3


@dataclass(frozen=True)
class GstLine:
    gstin: str
    r1_taxable: Money = None
    output_tax: Money = None
    itc_2b: Money = None
    r3b_filed: bool | None = None
    vendor_3b_defaults: int | None = None      # the 3B-not-2B holdback signal


@dataclass(frozen=True)
class BankLine:
    bank: str
    debit: Money = None
    credit: Money = None
    excluded_rows: int | None = None           # re-dated quarantine (D6)


@dataclass(frozen=True)
class TaxSummary:
    tds_26as: Money = None
    itr_status: str | None = None              # FILED / NOT_FILED / REFUNDABLE / —


@dataclass(frozen=True)
class FYFinancials:
    fy: str
    sales: SalesSummary = field(default_factory=SalesSummary)
    purchase: PurchaseSummary = field(default_factory=PurchaseSummary)
    gst: list[GstLine] = field(default_factory=list)
    bank: list[BankLine] = field(default_factory=list)
    tax: TaxSummary = field(default_factory=TaxSummary)
    revenue: Money = None            # audited/live revenue for the year
    pat: Money = None                # profit / (loss) after tax
    flags: list[str] = field(default_factory=list)   # flagged contradictions / caveats


@runtime_checkable
class FinancialDataProvider(Protocol):
    """What the dashboard needs. Implement against Zoho / Supabase / the ledger."""

    def name(self) -> str: ...
    def source_label(self) -> str: ...
    def connected(self) -> bool: ...
    def fy_financials(self, fy: str) -> FYFinancials: ...


class NullProvider:
    """The default until a real source is connected. Renders structure, not numbers."""

    def name(self) -> str:
        return "null"

    def source_label(self) -> str:
        return "no data source connected — values load after deployment"

    def connected(self) -> bool:
        return False

    def fy_financials(self, fy: str) -> FYFinancials:
        return FYFinancials(fy=fy)


def _d(v) -> Money:
    """String/number -> Decimal; None stays None (never fabricate a value)."""
    return None if v is None else Decimal(str(v))


class KnowledgePackProvider:
    """Serves the confirmed Go4Garage figures recorded in kp_data.

    Uses the confirmed register/sales/bank/26AS figures. The IGST-deducted line
    of the Net Payable waterfall is COMPUTED (Approved − Commission − TDS − Net
    Payable) so the waterfall ties to the recorded Net Payable exactly, rather
    than shown from the register's gross IGST column (which includes IGST that
    was reclaimed as ITC, not deducted).
    """

    def name(self) -> str:
        return "knowledge-pack"

    def source_label(self) -> str:
        return "Go4Garage Agent Knowledge Pack — confirmed figures (contradictions flagged, not resolved)"

    def connected(self) -> bool:
        return True

    def fy_financials(self, fy: str) -> FYFinancials:
        from . import kp_data
        row = kp_data.KP_FY.get(fy)
        if row is None:
            return FYFinancials(fy=fy)

        pr = row.get("purchase")
        if pr:
            approved = _d(pr["approved"])
            comm, tds_ = _d(pr["commission"]), _d(pr["tds"])
            net = _d(pr["net_payable"])
            # The deduction that actually reduces the payable ties the waterfall.
            igst_deducted = approved - comm - tds_ - net
            purchase = PurchaseSummary(
                rows=pr.get("rows"), approved=approved, commission=comm, tds=tds_,
                igst_deducted=igst_deducted, net_payable=net,
                zero_commission_rows=pr.get("zero_commission_rows"))
        else:
            purchase = PurchaseSummary()

        sr = row.get("sales") or {}
        sales = SalesSummary(invoices=sr.get("invoices"),
                             total_sales=_d(sr.get("total_sales")),
                             receivable=_d(sr.get("receivable")))

        gst = []
        g = row.get("gst")
        if g:
            gst = [GstLine(gstin=g["gstin"], r1_taxable=_d(g.get("r1_taxable")),
                           output_tax=_d(g.get("output_tax")), itc_2b=_d(g.get("itc_2b")))]

        bank = [BankLine(bank=b["bank"], debit=_d(b.get("debit")),
                         credit=_d(b.get("credit")), excluded_rows=b.get("excluded_rows"))
                for b in (row.get("bank") or [])]

        tx = row.get("tax") or {}
        tax = TaxSummary(tds_26as=_d(tx.get("tds_26as")), itr_status=tx.get("itr_status"))

        audited = row.get("audited") or {}
        return FYFinancials(
            fy=fy, sales=sales, purchase=purchase, gst=gst, bank=bank, tax=tax,
            revenue=_d(audited.get("revenue")), pat=_d(audited.get("pat")),
            flags=list(row.get("flags") or []))
