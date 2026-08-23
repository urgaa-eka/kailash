"""Verify the transcribed Knowledge-Pack figures against the Pack's grand totals.

These tie-outs are the transcription check: if a figure was mistyped, a total
stops matching. The Net Payable waterfall must also tie for every year with a
purchase register.
"""
from __future__ import annotations

from decimal import Decimal

from app.go4garage import kp_data
from app.go4garage.provider import KnowledgePackProvider


def test_purchase_approved_ties_to_grand_total():
    total = sum(
        (Decimal(r["purchase"]["approved"]) for r in kp_data.KP_FY.values()
         if r.get("purchase")),
        Decimal("0"),
    )
    assert total == Decimal(kp_data.PURCHASE_APPROVED_TOTAL)   # ₹2,77,90,802.65 (KP §3.2)


def test_sales_date_derived_ties_to_grand_total():
    total = sum(
        (Decimal(r["sales"]["total_sales"]) for r in kp_data.KP_FY.values()
         if (r.get("sales") or {}).get("total_sales")),
        Decimal("0"),
    )
    assert total == Decimal(kp_data.SALES_DATE_DERIVED_TOTAL)  # ₹4,83,53,442.80 (KP §3.5)


def test_net_payable_waterfall_ties_every_year():
    prov = KnowledgePackProvider()
    for fy, row in kp_data.KP_FY.items():
        if not row.get("purchase"):
            continue
        p = prov.fy_financials(fy).purchase
        # Approved − Commission − TDS − IGST(deducted) == Net Payable, exactly.
        assert (p.approved - p.commission - p.tds - p.igst_deducted) == p.net_payable, fy


def test_provider_populates_real_figures():
    fin = KnowledgePackProvider().fy_financials("2023-24")
    assert fin.purchase.net_payable == Decimal("16865684.42")
    assert fin.revenue == Decimal("25238000")
    assert fin.sales.invoices == 1363
    assert fin.flags                     # FY23-24 carries qualified-audit / ownership flags


def test_provider_is_connected():
    prov = KnowledgePackProvider()
    assert prov.connected() is True
    assert "Knowledge Pack" in prov.source_label()


def test_unknown_year_is_empty_not_an_error():
    fin = KnowledgePackProvider().fy_financials("1990-91")
    assert fin.purchase.net_payable is None
