"""Ingestion pipelines — typed contracts -> validated -> posted journals.

Universal rules (ingestion/README.md): schema-validate -> dedup by
source_hash -> resolve masters -> compute tax (effective-dated, place-of-
supply aware) -> draft journal -> maker-checker post. Failures land in
co_ingest_error; nothing silently drops.
"""
from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import psycopg

from backend.shared import ValidationError

from . import cloud
from .db import account_by_code, audit, effective_tax_rate, fy_for
from .posting import as_money, create_and_post
from .settings import settings

# Default control accounts from templates/chart_of_accounts.csv.
ACC_AR = "5010"          # Trade Receivables
ACC_AP = "3010"          # Trade Payables
ACC_SALES_GOODS = "6010"
ACC_SALES_SERVICES = "6020"
ACC_PURCHASES = "7010"
ACC_OUT_CGST, ACC_OUT_SGST, ACC_OUT_IGST, ACC_OUT_CESS = "3030", "3031", "3032", "3033"
ACC_IN_CGST, ACC_IN_SGST, ACC_IN_IGST = "5040", "5041", "5042"


def _fail(conn: psycopg.Connection, source: str, payload: dict, reason: str):
    # The error row must survive while every partial write of the failed
    # ingest rolls back — so it goes through its own short connection.
    with psycopg.connect(
        settings.company_db_url, options="-c search_path=company,public"
    ) as err_conn:
        err_conn.execute(
            "INSERT INTO co_ingest_error (source, payload, reason_code) VALUES (%s, %s::jsonb, %s)",
            (source, json.dumps(payload, default=str), reason),
        )
        err_conn.commit()
    raise ValidationError(reason)


def _resolve_gstin(conn: psycopg.Connection, gstin: str) -> dict:
    row = conn.execute(
        "SELECT * FROM co_gstin WHERE gstin = %s AND active", (gstin,)
    ).fetchone()
    return row


def _resolve_or_create_party(
    conn: psycopg.Connection, party: dict, party_type: str, actor: str
) -> dict:
    """Match by GSTIN first, then exact name; create with an audit entry
    otherwise (the audit trail is the review queue for auto-created
    masters — see ingestion/README.md)."""
    row = None
    if party.get("gstin"):
        row = conn.execute(
            "SELECT * FROM co_party WHERE gstin = %s", (party["gstin"],)
        ).fetchone()
    if row is None:
        row = conn.execute(
            "SELECT * FROM co_party WHERE party_name = %s", (party["name"],)
        ).fetchone()
    if row is not None:
        return row
    ledger_code = ACC_AR if party_type == "CUSTOMER" else ACC_AP
    ledger = account_by_code(conn, ledger_code)
    row = conn.execute(
        """
        INSERT INTO co_party (party_name, party_type, gstin, pan, state_code,
                              ledger_account_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            party["name"], party_type, party.get("gstin"), party.get("pan"),
            party.get("state_code"), ledger["account_id"],
        ),
    ).fetchone()
    audit(conn, actor, "party_autocreated", "co_party", str(row["party_id"]),
          after={"name": party["name"], "gstin": party.get("gstin")})
    return row


def _compute_line_tax(
    conn: psycopg.Connection,
    line: dict,
    doc_date: date,
    intra_state: bool,
    source: str,
    payload: dict,
) -> dict:
    """Effective-dated rate lookup + CGST/SGST vs IGST split."""
    gst_rate = Decimal(str(line["gst_rate"]))
    taxable = as_money(line["taxable_value"])
    rate_row = effective_tax_rate(conn, gst_rate, doc_date)
    if rate_row is None:
        _fail(conn, source, payload,
              f"no tax rate {gst_rate}% effective on {doc_date}")
    tax = taxable * gst_rate / 100
    cess = taxable * Decimal(str(rate_row["cess_rate"])) / 100
    out = {
        "taxable": taxable,
        "tax_rate_id": rate_row["tax_rate_id"],
        "cess": as_money(cess),
        "cgst": Decimal("0.00"), "sgst": Decimal("0.00"), "igst": Decimal("0.00"),
    }
    if intra_state:
        out["cgst"] = as_money(tax / 2)
        out["sgst"] = as_money(tax / 2)
    else:
        out["igst"] = as_money(tax)
    return out


# ---------------------------------------------------------------------------
# Sales (sales_invoice.contract.json)
# ---------------------------------------------------------------------------

def ingest_sales_invoice(conn: psycopg.Connection, payload: dict) -> dict:
    src = "SALES"
    # Idempotency (source_hash is UNIQUE on co_sales_invoice).
    existing = conn.execute(
        "SELECT invoice_id, invoice_no, journal_id, journal_fy FROM co_sales_invoice WHERE source_hash = %s",
        (payload["source_hash"],),
    ).fetchone()
    if existing:
        return {**existing, "deduped": True}

    gstin = _resolve_gstin(conn, payload["gstin"])
    if gstin is None:
        _fail(conn, src, payload, f"unknown supplier GSTIN {payload['gstin']}")

    party = _resolve_or_create_party(
        conn, payload["party"], "CUSTOMER", settings.ingest_maker
    )
    inv_date = date.fromisoformat(str(payload["invoice_date"]))
    pos = payload["place_of_supply"]
    intra = gstin["state_code"] == pos

    totals = {"taxable": Decimal("0.00"), "cgst": Decimal("0.00"),
              "sgst": Decimal("0.00"), "igst": Decimal("0.00"),
              "cess": Decimal("0.00")}
    computed_lines = []
    for ln in payload["lines"]:
        t = _compute_line_tax(conn, ln, inv_date, intra, src, payload)
        computed_lines.append({**ln, **t})
        for k in ("taxable", "cgst", "sgst", "igst", "cess"):
            totals[k] += t[k]
    total_value = sum(totals.values())

    # If the caller supplied totals, recompute and assert (contract: totals
    # are "recomputed and asserted by the engine").
    if payload.get("totals"):
        declared = payload["totals"]
        for key, ours in (("taxable_value", totals["taxable"]),
                          ("cgst", totals["cgst"]), ("sgst", totals["sgst"]),
                          ("igst", totals["igst"]),
                          ("total_value", total_value)):
            if (key in declared and declared[key] is not None
                    and abs(as_money(declared[key]) - as_money(ours)) > Decimal("0.01")):
                _fail(conn, src, payload,
                      f"declared {key}={declared[key]} != computed {ours}")

    inv = conn.execute(
        """
        INSERT INTO co_sales_invoice
            (gstin_id, invoice_no, invoice_date, party_id, supply_type,
             place_of_supply, taxable_value, cgst, sgst, igst, cess,
             total_value, irn, ewb_no, source_hash)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING invoice_id, invoice_no
        """,
        (
            gstin["gstin_id"], payload["invoice_no"], inv_date,
            party["party_id"], payload["supply_type"], pos,
            totals["taxable"], totals["cgst"], totals["sgst"], totals["igst"],
            totals["cess"], as_money(total_value),
            payload.get("irn"), payload.get("ewb_no"), payload["source_hash"],
        ),
    ).fetchone()
    for ln in computed_lines:
        conn.execute(
            """
            INSERT INTO co_sales_line (invoice_id, hsn_sac, qty, rate,
                                       taxable_value, tax_rate_id)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (inv["invoice_id"], ln["hsn_sac"], ln.get("qty"), ln.get("rate"),
             ln["taxable"], ln["tax_rate_id"]),
        )

    # Journal: Dr Debtor (total) / Cr Sales (taxable) / Cr Output GST.
    ar_account_id = party["ledger_account_id"] or account_by_code(conn, ACC_AR)["account_id"]
    jlines = [{
        "account_id": ar_account_id, "debit": as_money(total_value),
        "party_id": party["party_id"], "place_of_supply": pos,
    }]
    for ln in computed_lines:
        sales_code = ACC_SALES_SERVICES if str(ln["hsn_sac"]).startswith("99") else ACC_SALES_GOODS
        jlines.append({
            "account_id": account_by_code(conn, sales_code)["account_id"],
            "credit": ln["taxable"], "hsn_sac": ln["hsn_sac"],
            "tax_rate_id": ln["tax_rate_id"], "place_of_supply": pos,
        })
    for code, amt in ((ACC_OUT_CGST, totals["cgst"]), (ACC_OUT_SGST, totals["sgst"]),
                      (ACC_OUT_IGST, totals["igst"]), (ACC_OUT_CESS, totals["cess"])):
        if amt:
            jlines.append({"account_id": account_by_code(conn, code)["account_id"],
                           "credit": amt, "place_of_supply": pos})

    j = create_and_post(
        conn,
        voucher_type="SALES",
        voucher_date=inv_date,
        gstin_id=gstin["gstin_id"],
        lines=jlines,
        narration=f"Sales invoice {payload['invoice_no']} to {party['party_name']}",
        source_ref=f"sales_invoice:{inv['invoice_id']}",
        source_hash=payload["source_hash"],
        maker=settings.ingest_maker,
        checker=settings.ingest_checker,
    )
    conn.execute(
        "UPDATE co_sales_invoice SET journal_id = %s, journal_fy = %s WHERE invoice_id = %s",
        (j["journal_id"], j["fy"], inv["invoice_id"]),
    )
    cloud.record_hash(payload["source_hash"], f"sales_invoice:{inv['invoice_id']}")
    cloud.vault_put(j["fy"], "Sales", payload["source_hash"], payload)
    return {
        "invoice_id": inv["invoice_id"], "invoice_no": inv["invoice_no"],
        "journal_id": j["journal_id"], "journal_fy": j["fy"],
        "voucher_no": j["voucher_no"],
        "taxable_value": str(totals["taxable"]),
        "cgst": str(totals["cgst"]), "sgst": str(totals["sgst"]),
        "igst": str(totals["igst"]), "cess": str(totals["cess"]),
        "total_value": str(as_money(total_value)), "deduped": False,
    }


# ---------------------------------------------------------------------------
# Purchase (mirror of sales; ITC side)
# ---------------------------------------------------------------------------

def ingest_purchase_bill(conn: psycopg.Connection, payload: dict) -> dict:
    src = "PURCHASE"
    existing = conn.execute(
        "SELECT bill_id, bill_no, journal_id, journal_fy FROM co_purchase_bill WHERE source_hash = %s",
        (payload["source_hash"],),
    ).fetchone()
    if existing:
        return {**existing, "deduped": True}

    gstin = _resolve_gstin(conn, payload["gstin"])
    if gstin is None:
        _fail(conn, src, payload, f"unknown recipient GSTIN {payload['gstin']}")

    vendor = _resolve_or_create_party(
        conn, payload["vendor"], "VENDOR", settings.ingest_maker
    )
    bill_date = date.fromisoformat(str(payload["bill_date"]))
    pos = payload.get("place_of_supply") or gstin["state_code"]
    intra = (vendor["state_code"] or pos) == gstin["state_code"]
    itc_eligible = bool(payload.get("itc_eligible", True))

    totals = {"taxable": Decimal("0.00"), "cgst": Decimal("0.00"),
              "sgst": Decimal("0.00"), "igst": Decimal("0.00"),
              "cess": Decimal("0.00")}
    computed_lines = []
    for ln in payload["lines"]:
        t = _compute_line_tax(conn, ln, bill_date, intra, src, payload)
        computed_lines.append({**ln, **t})
        for k in ("taxable", "cgst", "sgst", "igst", "cess"):
            totals[k] += t[k]
    total_value = sum(totals.values())
    tax_total = totals["cgst"] + totals["sgst"] + totals["igst"] + totals["cess"]

    bill = conn.execute(
        """
        INSERT INTO co_purchase_bill
            (gstin_id, vendor_id, bill_no, bill_date, place_of_supply,
             taxable_value, cgst, sgst, igst, cess, total_value,
             itc_eligible, source_hash)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING bill_id, bill_no
        """,
        (
            gstin["gstin_id"], vendor["party_id"], payload["bill_no"], bill_date,
            pos, totals["taxable"], totals["cgst"], totals["sgst"],
            totals["igst"], totals["cess"], as_money(total_value),
            itc_eligible, payload["source_hash"],
        ),
    ).fetchone()
    for ln in computed_lines:
        conn.execute(
            """
            INSERT INTO co_purchase_line (bill_id, hsn_sac, taxable_value, tax_rate_id)
            VALUES (%s,%s,%s,%s)
            """,
            (bill["bill_id"], ln.get("hsn_sac"), ln["taxable"], ln["tax_rate_id"]),
        )

    # Journal: Dr Purchases (taxable [+tax if ITC-ineligible]) /
    #          Dr Input GST (if eligible) / Cr Creditor (total).
    purchase_debit = totals["taxable"] + (Decimal("0") if itc_eligible else tax_total)
    jlines = [{
        "account_id": account_by_code(conn, ACC_PURCHASES)["account_id"],
        "debit": as_money(purchase_debit),
    }]
    if itc_eligible:
        for code, amt in ((ACC_IN_CGST, totals["cgst"]), (ACC_IN_SGST, totals["sgst"]),
                          (ACC_IN_IGST, totals["igst"])):
            if amt:
                jlines.append({"account_id": account_by_code(conn, code)["account_id"],
                               "debit": amt})
        if totals["cess"]:
            jlines.append({"account_id": account_by_code(conn, ACC_IN_IGST)["account_id"],
                           "debit": totals["cess"]})
    ap_account_id = vendor["ledger_account_id"] or account_by_code(conn, ACC_AP)["account_id"]
    jlines.append({"account_id": ap_account_id, "credit": as_money(total_value),
                   "party_id": vendor["party_id"]})

    j = create_and_post(
        conn,
        voucher_type="PURCHASE",
        voucher_date=bill_date,
        gstin_id=gstin["gstin_id"],
        lines=jlines,
        narration=f"Purchase bill {payload['bill_no']} from {vendor['party_name']}",
        source_ref=f"purchase_bill:{bill['bill_id']}",
        source_hash=payload["source_hash"],
        maker=settings.ingest_maker,
        checker=settings.ingest_checker,
    )
    conn.execute(
        "UPDATE co_purchase_bill SET journal_id = %s, journal_fy = %s WHERE bill_id = %s",
        (j["journal_id"], j["fy"], bill["bill_id"]),
    )

    # ITC register entry for the bill's period (eligible amounts only).
    if itc_eligible and tax_total:
        conn.execute(
            """
            INSERT INTO co_itc_register (gstin_id, gst_period, bill_id, itc_amount, status)
            VALUES (%s, %s, %s, %s, 'eligible')
            ON CONFLICT (gstin_id, gst_period, bill_id) DO NOTHING
            """,
            (gstin["gstin_id"], f"{bill_date.month:02d}{bill_date.year}",
             bill["bill_id"], as_money(tax_total)),
        )

    cloud.record_hash(payload["source_hash"], f"purchase_bill:{bill['bill_id']}")
    cloud.vault_put(j["fy"], "Purchase", payload["source_hash"], payload)
    return {
        "bill_id": bill["bill_id"], "bill_no": bill["bill_no"],
        "journal_id": j["journal_id"], "journal_fy": j["fy"],
        "voucher_no": j["voucher_no"],
        "taxable_value": str(totals["taxable"]),
        "itc_amount": str(as_money(tax_total)) if itc_eligible else "0.00",
        "total_value": str(as_money(total_value)), "deduped": False,
    }


# ---------------------------------------------------------------------------
# Bank statement import (BRS source)
# ---------------------------------------------------------------------------

def ingest_bank_statement(
    conn: psycopg.Connection, bank_account_id: int, txns: list[dict]
) -> dict:
    acc = conn.execute(
        "SELECT * FROM co_bank_account WHERE bank_account_id = %s",
        (bank_account_id,),
    ).fetchone()
    if acc is None:
        raise ValidationError(f"bank account {bank_account_id} not found")
    imported, skipped = 0, 0
    for t in txns:
        cur = conn.execute(
            """
            INSERT INTO co_bank_txn
                (bank_account_id, txn_date, value_date, description,
                 debit, credit, running_balance, source_hash)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (source_hash) DO NOTHING
            """,
            (
                bank_account_id, t["txn_date"], t.get("value_date"),
                t.get("description"), t.get("debit", 0), t.get("credit", 0),
                t.get("running_balance"), t["source_hash"],
            ),
        )
        if cur.rowcount:
            imported += 1
        else:
            skipped += 1
    return {"imported": imported, "deduped": skipped}


# ---------------------------------------------------------------------------
# Opening balance (Tally migration cut-over)
# ---------------------------------------------------------------------------

def post_opening_balance(
    conn: psycopg.Connection,
    *,
    gstin: str,
    as_of: date,
    lines: list[dict],
    maker: str,
    checker: str,
) -> dict:
    g = _resolve_gstin(conn, gstin)
    if g is None:
        raise ValidationError(f"unknown GSTIN {gstin}")
    jlines = []
    for ln in lines:
        acc = account_by_code(conn, ln["account_code"])
        jlines.append({
            "account_id": acc["account_id"],
            "debit": as_money(ln.get("debit", 0)),
            "credit": as_money(ln.get("credit", 0)),
        })
    j = create_and_post(
        conn,
        voucher_type="OPENING",
        voucher_date=as_of,
        gstin_id=g["gstin_id"],
        lines=jlines,
        narration=f"Opening balances as of {as_of} (Tally cut-over)",
        source_ref="tally:opening_balance",
        source_hash=f"opening:{gstin}:{as_of}",
        origin="TALLY_MIGRATION",
        maker=maker,
        checker=checker,
        fy=fy_for(as_of),
    )
    return j
