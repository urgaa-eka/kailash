"""Tests for the Go4Garage FY dashboard renderer and route."""
from __future__ import annotations

from decimal import Decimal

from app.go4garage import model, render_fy
from app.go4garage.provider import (
    FYFinancials,
    NullProvider,
    PurchaseSummary,
    SalesSummary,
)


class _PopulatedProvider:
    """A provider that supplies a couple of numbers, to prove values render."""

    def name(self):
        return "test"

    def source_label(self):
        return "test source"

    def connected(self):
        return True

    def fy_financials(self, fy):
        return FYFinancials(
            fy=fy,
            sales=SalesSummary(invoices=1363, total_sales=Decimal("29604776.60")),
            purchase=PurchaseSummary(approved=Decimal("19820967.43"),
                                     net_payable=Decimal("16865684.42")),
        )


def test_renders_structure_with_null_provider():
    html = render_fy(NullProvider(), "2023-24")
    assert html.startswith("<!DOCTYPE html>")
    # Entity + every department + the audit gate render even with no data.
    assert model.ENTITY["cin"] in html
    assert "Net Payable" in html
    assert "Internal Audit" in html
    assert "Open decisions" in html
    # No source connected -> awaiting-source markers, no fabricated numbers.
    assert "awaiting source" in html
    assert "not connected" in html


def test_all_five_years_selectable():
    html = render_fy(NullProvider(), "2024-25")
    for m in model.FINANCIAL_YEARS:
        assert m.fy in html


def test_invalid_fy_falls_back_to_latest():
    html = render_fy(NullProvider(), "1999-00")
    assert "FY 2025-26" in html or "2025-26" in html


def test_populated_provider_shows_numbers():
    html = render_fy(_PopulatedProvider(), "2023-24")
    assert "connected" in html
    assert "1,363" in html               # sales invoices
    assert "Cr" in html                  # ₹ scaled figure rendered


def test_route_serves_dashboard(client):
    r = client.get("/dashboard/fy")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert model.ENTITY["name"] in r.text

    r2 = client.get("/dashboard/fy", params={"fy": "2024-25"})
    assert r2.status_code == 200
