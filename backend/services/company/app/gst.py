"""GST engine (L2) — pure functions of the ledger + masters.

Builds GSTR-1 (sectioned per templates/gstr1_section_mapping.csv rules),
GSTR-3B summary (liability from sales, ITC from the register) as versioned
artefacts in co_gstr1 / co_gstr3b_summary. Never mutates L1.
"""
from __future__ import annotations

import json
from decimal import Decimal

import psycopg

from backend.shared import NotFoundError

from . import events
from .posting import as_money

B2CL_THRESHOLD = Decimal("100000")  # inter-state unregistered, invoice > 1 lakh


def _gstin_row(conn: psycopg.Connection, gstin: str) -> dict:
    row = conn.execute(
        "SELECT * FROM co_gstin WHERE gstin = %s", (gstin,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"GSTIN {gstin} not registered")
    return row


def classify_section(inv: dict, supplier_state: str) -> str:
    """GSTR-1 section per templates/gstr1_section_mapping.csv."""
    st = inv["supply_type"]
    if st == "EXPORT":
        return "EXP"
    if st == "SEZ":
        return "SEZ"
    if st in ("NIL", "EXEMPT"):
        return "NIL"
    if inv["counterparty_gstin"]:
        return "B2B"
    inter_state = inv["place_of_supply"] != supplier_state
    if inter_state and Decimal(str(inv["total_value"])) > B2CL_THRESHOLD:
        return "B2CL"
    return "B2CS"


def generate_gstr1(conn: psycopg.Connection, gstin: str, period: str) -> dict:
    g = _gstin_row(conn, gstin)
    invoices = conn.execute(
        """
        SELECT * FROM co_v_gstr1_feed
        WHERE gstin_id = %s AND gst_period = %s
        ORDER BY invoice_date, invoice_no
        """,
        (g["gstin_id"], period),
    ).fetchall()

    sections: dict[str, list] = {k: [] for k in ("B2B", "B2CL", "B2CS", "EXP", "SEZ", "NIL")}
    for inv in invoices:
        sec = classify_section(inv, g["state_code"])
        sections[sec].append(inv)

    def _inv_json(inv: dict) -> dict:
        return {
            "inum": inv["invoice_no"],
            "idt": inv["invoice_date"].strftime("%d-%m-%Y"),
            "val": str(as_money(inv["total_value"])),
            "pos": inv["place_of_supply"],
            "txval": str(as_money(inv["taxable_value"])),
            "camt": str(as_money(inv["cgst"])),
            "samt": str(as_money(inv["sgst"])),
            "iamt": str(as_money(inv["igst"])),
            "csamt": str(as_money(inv["cess"])),
        }

    # B2B: grouped by counterparty GSTIN (GSTN offline-tool shape).
    b2b = []
    by_ctin: dict[str, list] = {}
    for inv in sections["B2B"]:
        by_ctin.setdefault(inv["counterparty_gstin"].strip(), []).append(inv)
    for ctin, invs in sorted(by_ctin.items()):
        b2b.append({"ctin": ctin, "inv": [_inv_json(i) for i in invs]})

    # B2CS: aggregated rate-less summary by place-of-supply.
    b2cs_agg: dict[str, dict] = {}
    for inv in sections["B2CS"]:
        a = b2cs_agg.setdefault(inv["place_of_supply"], {
            "pos": inv["place_of_supply"], "txval": Decimal("0"),
            "camt": Decimal("0"), "samt": Decimal("0"),
            "iamt": Decimal("0"), "csamt": Decimal("0"),
        })
        a["txval"] += Decimal(str(inv["taxable_value"]))
        a["camt"] += Decimal(str(inv["cgst"]))
        a["samt"] += Decimal(str(inv["sgst"]))
        a["iamt"] += Decimal(str(inv["igst"]))
        a["csamt"] += Decimal(str(inv["cess"]))
    b2cs = [
        {k: (str(as_money(v)) if isinstance(v, Decimal) else v) for k, v in a.items()}
        for a in b2cs_agg.values()
    ]

    # HSN summary from invoice lines in the period.
    hsn_rows = conn.execute(
        """
        SELECT sl.hsn_sac,
               SUM(sl.qty)           AS qty,
               SUM(sl.taxable_value) AS txval,
               SUM(sl.taxable_value * tr.total_rate / 100.0) AS tax
        FROM co_sales_line sl
        JOIN co_sales_invoice si ON si.invoice_id = sl.invoice_id
        LEFT JOIN co_tax_rate tr ON tr.tax_rate_id = sl.tax_rate_id
        WHERE si.gstin_id = %s AND to_char(si.invoice_date,'MMYYYY') = %s
        GROUP BY sl.hsn_sac ORDER BY sl.hsn_sac
        """,
        (g["gstin_id"], period),
    ).fetchall()
    hsn = [
        {
            "hsn_sc": r["hsn_sac"],
            "qty": str(r["qty"] or 0),
            "txval": str(as_money(r["txval"])),
            "tax": str(as_money(r["tax"] or 0)),
        }
        for r in hsn_rows
    ]

    # Documents issued: invoice number range for the period.
    docs = conn.execute(
        """
        SELECT COUNT(*) AS cnt, MIN(invoice_no) AS from_no, MAX(invoice_no) AS to_no
        FROM co_sales_invoice
        WHERE gstin_id = %s AND to_char(invoice_date,'MMYYYY') = %s
        """,
        (g["gstin_id"], period),
    ).fetchone()

    payload = {
        "gstin": gstin,
        "fp": period,
        "b2b": b2b,
        "b2cl": [_inv_json(i) for i in sections["B2CL"]],
        "b2cs": b2cs,
        "exp": [_inv_json(i) for i in sections["EXP"]],
        "sez": [_inv_json(i) for i in sections["SEZ"]],
        "nil": [_inv_json(i) for i in sections["NIL"]],
        "hsn": {"data": hsn},
        "doc_issue": {
            "docs": [{
                "num": 1, "count": docs["cnt"],
                "from": docs["from_no"], "to": docs["to_no"],
            }] if docs["cnt"] else [],
        },
        "totals": {
            "invoices": len(invoices),
            "taxable_value": str(as_money(sum(
                (Decimal(str(i["taxable_value"])) for i in invoices), Decimal("0")))),
            "tax": str(as_money(sum(
                (Decimal(str(i["cgst"])) + Decimal(str(i["sgst"]))
                 + Decimal(str(i["igst"])) + Decimal(str(i["cess"]))
                 for i in invoices), Decimal("0")))),
        },
    }

    conn.execute(
        """
        INSERT INTO co_gstr1 (gstin_id, gst_period, status, payload)
        VALUES (%s, %s, 'draft', %s::jsonb)
        ON CONFLICT (gstin_id, gst_period)
        DO UPDATE SET payload = EXCLUDED.payload, generated_at = now()
        """,
        (g["gstin_id"], period, json.dumps(payload)),
    )
    events.return_generated("GSTR-1", gstin, period, {
        "invoices": payload["totals"]["invoices"],
        "taxable_value": payload["totals"]["taxable_value"],
    })
    return payload


def generate_gstr3b(conn: psycopg.Connection, gstin: str, period: str) -> dict:
    g = _gstin_row(conn, gstin)
    outward = conn.execute(
        """
        SELECT COALESCE(SUM(taxable_value),0) AS taxable,
               COALESCE(SUM(cgst+sgst+igst+cess),0) AS tax
        FROM co_sales_invoice
        WHERE gstin_id = %s AND to_char(invoice_date,'MMYYYY') = %s
        """,
        (g["gstin_id"], period),
    ).fetchone()
    itc = conn.execute(
        """
        SELECT COALESCE(SUM(itc_amount),0) AS itc
        FROM co_itc_register
        WHERE gstin_id = %s AND gst_period = %s AND status = 'eligible'
        """,
        (g["gstin_id"], period),
    ).fetchone()

    outward_taxable = as_money(outward["taxable"])
    output_tax = as_money(outward["tax"])
    itc_available = as_money(itc["itc"])
    net_payable = as_money(max(output_tax - itc_available, Decimal("0")))

    conn.execute(
        """
        INSERT INTO co_gstr3b_summary
            (gstin_id, gst_period, outward_taxable, output_tax, itc_available, net_payable)
        VALUES (%s,%s,%s,%s,%s,%s)
        ON CONFLICT (gstin_id, gst_period)
        DO UPDATE SET outward_taxable = EXCLUDED.outward_taxable,
                      output_tax      = EXCLUDED.output_tax,
                      itc_available   = EXCLUDED.itc_available,
                      net_payable     = EXCLUDED.net_payable
        """,
        (g["gstin_id"], period, outward_taxable, output_tax, itc_available, net_payable),
    )
    result = {
        "gstin": gstin, "period": period,
        "outward_taxable": str(outward_taxable),
        "output_tax": str(output_tax),
        "itc_available": str(itc_available),
        "net_payable": str(net_payable),
    }
    events.return_generated("GSTR-3B", gstin, period, {
        "output_tax": result["output_tax"], "net_payable": result["net_payable"],
    })
    return result


def get_gstr1(conn: psycopg.Connection, gstin: str, period: str) -> dict:
    g = _gstin_row(conn, gstin)
    row = conn.execute(
        "SELECT status, generated_at, payload FROM co_gstr1 WHERE gstin_id = %s AND gst_period = %s",
        (g["gstin_id"], period),
    ).fetchone()
    if row is None:
        raise NotFoundError(f"GSTR-1 for {gstin} {period} not generated yet")
    return {
        "status": row["status"],
        "generated_at": row["generated_at"].isoformat(),
        "payload": row["payload"],
    }
