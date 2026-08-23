"""Tests for the confirmed Go4Garage financial logic and guards."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from app.go4garage import logic


class TestNetPayable:
    def test_igst_not_deducted_when_gst_available(self):
        # Net = Approved − Commission − TDS  (IGST stays, reclaimed as ITC)
        net = logic.net_payable(10000, 1500, 200, 900, "Available")
        assert net == Decimal("8300")

    def test_igst_deducted_when_not_available(self):
        net = logic.net_payable(10000, 1500, 200, 900, "Not Available")
        assert net == Decimal("7400")

    def test_igst_flag_is_case_and_space_insensitive(self):
        assert logic.igst_is_deducted("  not available ") is True
        assert logic.igst_is_deducted("Available") is False
        assert logic.igst_is_deducted(None) is False

    def test_confirmed_rates(self):
        assert logic.commission(10000) == Decimal("1500.00")
        assert logic.tds(10000) == Decimal("200.00")

    def test_recompute_at_confirmed_rates(self):
        # GST Available branch, so IGST is not subtracted.
        assert logic.net_payable_at_confirmed_rates(10000, 900, "Available") == Decimal("8300.00")

    def test_the_layers_never_join(self):
        with pytest.raises(NotImplementedError):
            logic.assert_layers_separate()


class TestFinancialYear:
    @pytest.mark.parametrize("d,fy", [
        (date(2022, 4, 10), "2022-23"),   # THE trap: Apr 2022 is FY22-23, not FY21-22
        (date(2022, 10, 4), "2022-23"),
        (date(2022, 1, 15), "2021-22"),
        (date(2024, 3, 31), "2023-24"),   # last day of a closed year
        (date(2024, 4, 1), "2024-25"),    # first day of the next
        (date(2026, 1, 16), "2025-26"),
    ])
    def test_derived_from_date(self, d, fy):
        assert logic.financial_year(d) == fy


class TestGates:
    def test_reference_gate(self):
        refs = {"G4G/23-24/10", "G4G/23-24/11"}
        assert logic.gate_reference_in_sales("G4G/23-24/10", refs) is True
        assert logic.gate_reference_in_sales("G4G/23-24/99", refs) is False

    def test_approval_gate_is_inclusive(self):
        assert logic.gate_within_approval(100, 100) is True
        assert logic.gate_within_approval(101, 100) is False

    def test_full_verdict(self):
        refs = {"G4G/23-24/10"}
        assert logic.validate_vendor_bill("G4G/23-24/10", 90, 100, refs).accepted is True
        assert logic.validate_vendor_bill("G4G/23-24/99", 90, 100, refs).accepted is False
        v = logic.validate_vendor_bill("G4G/23-24/10", 110, 100, refs)
        assert v.accepted is False and "above" in v.reason


class TestGuards:
    def test_outstanding_recomputed_with_floor(self):
        assert logic.recompute_outstanding(1000, 400) == Decimal("600")
        # sub-rupee artifact collapses to zero
        assert logic.recompute_outstanding(Decimal("100.18"), Decimal("100.00")) == Decimal("0")

    def test_overpaid(self):
        assert logic.is_overpaid(100, 500) is True
        assert logic.is_overpaid(100, Decimal("100.50")) is False   # within ₹1 floor

    def test_total_row_skipped(self):
        assert logic.is_total_row("TOTAL") is True
        assert logic.is_total_row(" total ") is True
        assert logic.is_total_row("Sales") is False

    def test_dedup_key_collapses_repeats(self):
        rows = [
            {"state": "UP", "gstin": "x", "period": "Apr", "counterparty_gstin": "y",
             "invoice_no": "1", "invoice_date": "2023-04-01"},
            {"state": "UP", "gstin": "x", "period": "Apr", "counterparty_gstin": "y",
             "invoice_no": "1", "invoice_date": "2023-04-01"},   # split-row duplicate
        ]
        assert len({logic.dedup_key(r) for r in rows}) == 1


class TestGstin:
    def test_malformed_position_13(self):
        # a capital I where position 13 must be a digit
        assert logic.gstin_is_malformed("36AXNPS4900RIZM") is True

    def test_well_formed_is_not_malformed(self):
        assert logic.gstin_is_malformed("09AAICG9768N1ZI") is False   # UP HO, digit at pos 13

    def test_absent_markers_are_not_malformed(self):
        for absent in ("", "Not Available", "Not Found", "AMBIGUOUS", None):
            assert logic.gstin_is_present(absent) is False
            assert logic.gstin_is_malformed(absent) is False


class TestIdentity:
    @pytest.mark.parametrize("name", [
        "Vivek Raj", "VIVEK GUPTA", "Vivek Raj Alias Vivek Gupta",
        "Vivek Raj Alias Vevek Gupta", "Sapna Gupta", "Mr VIVEK RAJ",
    ])
    def test_related_parties(self, name):
        assert logic.is_related_party(name) is True

    def test_unrelated_party(self):
        assert logic.is_related_party("Zoomcar India") is False

    def test_workshop_identity_is_exact_never_substring(self):
        assert logic.same_workshop("Star Motors", "star motors") is True
        assert logic.same_workshop("Star Motors", "StarCars") is False
        assert logic.same_workshop("KM Motors", "KMAuto") is False
