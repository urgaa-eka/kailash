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
