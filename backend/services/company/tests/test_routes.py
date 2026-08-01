"""End-to-end journey: init -> company -> opening balance -> sales/purchase
ingestion -> ledger reports -> GSTR-1/3B -> reconciliation -> dashboard.

Runs against a throwaway Postgres database (see conftest). Order matters
within this module; state accumulates deliberately (it IS the e2e test).
"""
from __future__ import annotations

FY = "2025-26"
CO_GSTIN = "27AAICG1234F1Z5"      # Maharashtra (27)
ACME_GSTIN = "27AABCA1234A1Z5"    # seeded B2B customer, intra-state
PERIOD = "102025"                  # Oct 2025 (post GST 2.0 cutover)


def test_company_setup(db):
    r = db.post("/admin/company", json={
        "legal_name": "Go4Garage Test Pvt Ltd",
        "cin": "U74999MH2024PTC000001",
        "pan": "AAICG1234F",
        "incorporation_dt": "2024-06-01",
        "gstin": CO_GSTIN,
    })
    assert r.status_code == 200, r.text
    assert r.json()["data"]["gstin_id"] >= 1


def test_opening_balance(db):
    r = db.post("/migration/opening-balance", json={
        "gstin": CO_GSTIN, "as_of": "2025-04-01",
        "maker": "migration", "checker": "ca-verified",
        "lines": [
            {"account_code": "5030", "debit": 1000000},
            {"account_code": "1010", "credit": 1000000},
        ],
    })
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "posted"


def test_ingest_sales_b2b_intra(db):
    r = db.post("/ingest/sales", json={
        "source_hash": "sale-001",
        "gstin": CO_GSTIN,
        "invoice_no": "G4G/25-26/001",
        "invoice_date": "2025-10-05",
        "party": {"name": "SAMPLE - Acme Retail Pvt Ltd", "gstin": ACME_GSTIN,
                  "state_code": "27"},
        "supply_type": "B2B",
        "place_of_supply": "27",
        "lines": [
            {"hsn_sac": "998313", "taxable_value": 100000, "gst_rate": 18},
        ],
    })
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    # intra-state 18% -> CGST 9000 + SGST 9000
    assert d["cgst"] == "9000.00" and d["sgst"] == "9000.00" and d["igst"] == "0.00"
    assert d["total_value"] == "118000.00"
    assert d["voucher_no"].startswith("INV/2025-26/")


def test_ingest_sales_idempotent(db):
    r = db.post("/ingest/sales", json={
        "source_hash": "sale-001",
        "gstin": CO_GSTIN,
        "invoice_no": "G4G/25-26/001",
        "invoice_date": "2025-10-05",
        "party": {"name": "SAMPLE - Acme Retail Pvt Ltd", "gstin": ACME_GSTIN},
        "supply_type": "B2B",
        "place_of_supply": "27",
        "lines": [{"hsn_sac": "998313", "taxable_value": 100000, "gst_rate": 18}],
    })
    assert r.status_code == 200
    assert r.json()["data"]["deduped"] is True


def test_ingest_sales_b2cl_inter(db):
    r = db.post("/ingest/sales", json={
        "source_hash": "sale-002",
        "gstin": CO_GSTIN,
        "invoice_no": "G4G/25-26/002",
        "invoice_date": "2025-10-12",
        "party": {"name": "Retail Walk-in Bangalore", "state_code": "29"},
        "supply_type": "B2CL",
        "place_of_supply": "29",
        "lines": [{"hsn_sac": "8703", "taxable_value": 200000, "gst_rate": 18}],
    })
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    # inter-state -> IGST only
    assert d["igst"] == "36000.00" and d["cgst"] == "0.00"


def test_ingest_sales_bad_totals_rejected(db):
    r = db.post("/ingest/sales", json={
        "source_hash": "sale-bad-totals",
        "gstin": CO_GSTIN,
        "invoice_no": "G4G/25-26/BAD",
        "invoice_date": "2025-10-13",
        "party": {"name": "SAMPLE - Acme Retail Pvt Ltd", "gstin": ACME_GSTIN},
        "supply_type": "B2B",
        "place_of_supply": "27",
        "lines": [{"hsn_sac": "998313", "taxable_value": 1000, "gst_rate": 18}],
        "totals": {"total_value": 99999},
    })
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
    # and it landed in the error queue
    q = db.get("/ingest/errors")
    assert any("declared total_value" in e["reason_code"]
               for e in q.json()["data"]["errors"])


def test_ingest_purchase_inter_itc(db):
    r = db.post("/ingest/purchase", json={
        "source_hash": "pur-001",
        "gstin": CO_GSTIN,
        "bill_no": "CH/1042",
        "bill_date": "2025-10-08",
        "vendor": {"name": "SAMPLE - CloudHost India LLP",
                   "gstin": "29AABFC5678B1Z2", "state_code": "29"},
        "place_of_supply": "27",
        "lines": [{"hsn_sac": "998315", "taxable_value": 50000, "gst_rate": 18}],
    })
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["itc_amount"] == "9000.00"
    assert d["total_value"] == "59000.00"


def test_trial_balance_balanced(db):
    r = db.get(f"/reports/trial-balance?fy={FY}")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["balanced"] is True
    revenue = [a for a in d["accounts"] if a["account_code"] == "6020"]
    assert revenue, "service sales account should have postings"


def test_schedule_iii_equation_holds(db):
    r = db.get(f"/reports/schedule-iii?fy={FY}")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["equation"]["holds"] is True
    # revenue 100000 (services) + 200000 (goods); purchases 50000 -> profit 250000
    assert d["profit_after_adjustments"] == "250000.00"


def test_gstr1_sections(db):
    r = db.post(f"/gst/gstr1/generate?gstin={CO_GSTIN}&period={PERIOD}")
    assert r.status_code == 200, r.text
    p = r.json()["data"]
    assert len(p["b2b"]) == 1 and p["b2b"][0]["ctin"] == ACME_GSTIN
    assert len(p["b2b"][0]["inv"]) == 1
    assert len(p["b2cl"]) == 1          # inter-state unregistered > 1 lakh
    assert p["totals"]["taxable_value"] == "300000.00"
    assert p["totals"]["tax"] == "54000.00"
    assert p["hsn"]["data"], "HSN summary must be present"
    assert p["doc_issue"]["docs"][0]["count"] == 2

    g = db.get(f"/gst/gstr1?gstin={CO_GSTIN}&period={PERIOD}")
    assert g.status_code == 200
    assert g.json()["data"]["status"] == "draft"


def test_gstr3b_summary(db):
    r = db.post(f"/gst/gstr3b/generate?gstin={CO_GSTIN}&period={PERIOD}")
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    assert d["outward_taxable"] == "300000.00"
    assert d["output_tax"] == "54000.00"
    assert d["itc_available"] == "9000.00"
    assert d["net_payable"] == "45000.00"


def test_reconciliation_run(db):
    r = db.post("/recon/run", json={
        "fy": FY,
        "externals": {
            "FY_SALES": 300000,        # matches books exactly
            "NET_PROFIT": 999999,      # deliberately wrong -> material variance
        },
    })
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    by_code = {x["code"]: x for x in d["results"]}
    assert by_code["FY_SALES"]["severity"] == "matched"
    assert by_code["NET_PROFIT"]["severity"] == "material"
    assert by_code["NET_PROFIT"]["status"] == "open"
    # cross-internal checks ran without externals being provided
    assert by_code["GSTR1_VS_3B"]["severity"] == "matched"
    assert by_code["BOOKS_VS_GST_TURNOVER"]["severity"] == "matched"


def test_variance_workflow(db, raw_conn):
    v = db.get("/recon/variances").json()["data"]["variances"]
    net_profit = [x for x in v if x["code"] == "NET_PROFIT"]
    assert net_profit, "open NET_PROFIT variance expected"
    vid = raw_conn.execute(
        """
        SELECT v.variance_id FROM co_recon_variance v
        JOIN co_recon_run r ON r.run_id = v.run_id
        JOIN co_recon_control_point cp ON cp.cp_id = r.cp_id
        WHERE cp.code = 'NET_PROFIT' AND v.status = 'open'
        ORDER BY v.variance_id DESC LIMIT 1
        """
    ).fetchone()["variance_id"]
    r = db.patch(f"/recon/variance/{vid}", json={
        "status": "accepted", "owner": "eka",
        "root_cause": "test external figure was synthetic",
        "note": "accepted-with-note",
    })
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "accepted"


def test_manual_journal_post_and_reverse(db):
    r = db.post("/journal", json={
        "gstin": CO_GSTIN, "voucher_date": "2025-11-01",
        "narration": "Cloud hosting paid", "maker": "alice",
        "lines": [
            {"account_code": "7440", "debit": 5000},
            {"account_code": "5030", "credit": 5000},
        ],
    })
    assert r.status_code == 200, r.text
    j = r.json()["data"]
    assert j["status"] == "draft"

    p = db.post(f"/journal/{j['fy']}/{j['journal_id']}/post",
                json={"checker": "bob"})
    assert p.status_code == 200, p.text
    assert p.json()["data"]["status"] == "posted"

    before = db.get(f"/reports/schedule-iii?fy={FY}").json()["data"]

    rev = db.post(f"/journal/{j['fy']}/{j['journal_id']}/reverse",
                  json={"maker": "alice", "checker": "bob"})
    assert rev.status_code == 200, rev.text

    after = db.get(f"/reports/schedule-iii?fy={FY}").json()["data"]
    # reversal restores profit to the pre-journal figure
    assert float(after["profit_after_adjustments"]) == \
        float(before["profit_after_adjustments"]) + 5000
    assert after["equation"]["holds"] is True


def test_maker_checker_rejected(db):
    r = db.post("/journal", json={
        "gstin": CO_GSTIN, "voucher_date": "2025-11-02",
        "maker": "alice",
        "lines": [
            {"account_code": "7440", "debit": 100},
            {"account_code": "5030", "credit": 100},
        ],
    })
    j = r.json()["data"]
    p = db.post(f"/journal/{j['fy']}/{j['journal_id']}/post",
                json={"checker": "alice"})
    assert p.status_code == 422
    assert "distinct checker" in p.json()["error"]["message"]


def test_unbalanced_journal_rejected_at_post(db):
    r = db.post("/journal", json={
        "gstin": CO_GSTIN, "voucher_date": "2025-11-03",
        "maker": "alice",
        "lines": [
            {"account_code": "7440", "debit": 100},
            {"account_code": "5030", "credit": 99},
        ],
    })
    j = r.json()["data"]
    p = db.post(f"/journal/{j['fy']}/{j['journal_id']}/post",
                json={"checker": "bob"})
    assert p.status_code == 422
    assert "unbalanced" in p.json()["error"]["message"]


def test_bank_statement_import_idempotent(db):
    acc = db.post("/admin/bank-account", json={
        "bank_name": "HDFC", "account_no": "50200012345678",
        "ifsc": "HDFC0000001",
    })
    assert acc.status_code == 200, acc.text
    bid = acc.json()["data"]["bank_account_id"]
    r = db.post("/ingest/bank", json={
        "bank_account_id": bid,
        "txns": [
            {"source_hash": "bank-1", "txn_date": "2025-10-06",
             "credit": 118000, "description": "NEFT ACME",
             "running_balance": 1118000},
            {"source_hash": "bank-1", "txn_date": "2025-10-06",
             "credit": 118000, "description": "duplicate import"},
        ],
    })
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["imported"] == 1 and d["deduped"] == 1


def test_compliance_calendar(db):
    r = db.get("/compliance/calendar")
    assert r.status_code == 200
    cal = r.json()["data"]["calendar"]
    assert any(c["form"] == "GSTR-3B" for c in cal)
    assert all(c["status"] in
               ("upcoming", "due_soon", "overdue", "unscheduled") for c in cal)


def test_financial_snapshot_versioned(db):
    v1 = db.post(f"/reports/financials/snapshot?fy={FY}").json()["data"]
    v2 = db.post(f"/reports/financials/snapshot?fy={FY}").json()["data"]
    assert v2["version"] == v1["version"] + 1


def test_dashboard_renders(db):
    r = db.get(f"/dashboard?fy={FY}")
    assert r.status_code == 200
    assert "Trial Balance" in r.text
    assert "Reconciliation Matrix" in r.text
    assert "Compliance Calendar" in r.text
