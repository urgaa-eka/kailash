"""Go4Garage dashboard store — the database layer behind the FY dashboard.

A small, dedicated set of `g4g_*` tables (in the same PostgreSQL database as the
company ledger, so it works against local Postgres or Supabase alike) holding the
per-FY figures the dashboard displays. Seeded from the confirmed Knowledge-Pack
figures so the dashboard is populated on day one, then editable via the ingest
endpoints — this is where Go4Garage's real data lives and is worked on.

`read_fy` returns the same `FYFinancials` the other providers do, so the renderer
and the confirmed logic are unchanged; only the numbers' origin moves to the DB.
"""
from __future__ import annotations

from decimal import Decimal

from . import kp_data
from . import model as _model
from .provider import (
    BankLine,
    FYFinancials,
    GstLine,
    PurchaseSummary,
    SalesSummary,
    TaxSummary,
)

# Tables land in the `company` schema (first on the connection search_path).
SCHEMA = """
CREATE TABLE IF NOT EXISTS g4g_fy (
    fy           text PRIMARY KEY,
    audit_status text,
    posture      text,
    note         text,
    revenue      numeric,
    pat          numeric,
    updated_at   timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS g4g_purchase_fy (
    fy                   text PRIMARY KEY REFERENCES g4g_fy(fy) ON DELETE CASCADE,
    rows                 integer,
    approved             numeric,
    commission           numeric,
    tds                  numeric,
    net_payable          numeric,
    paid                 numeric,
    outstanding          numeric,
    zero_commission_rows integer
);
CREATE TABLE IF NOT EXISTS g4g_sales_fy (
    fy          text PRIMARY KEY REFERENCES g4g_fy(fy) ON DELETE CASCADE,
    invoices    integer,
    total_sales numeric,
    receivable  numeric
);
CREATE TABLE IF NOT EXISTS g4g_tax_fy (
    fy         text PRIMARY KEY REFERENCES g4g_fy(fy) ON DELETE CASCADE,
    tds_26as   numeric,
    itr_status text
);
CREATE TABLE IF NOT EXISTS g4g_bank_fy (
    id            bigserial PRIMARY KEY,
    fy            text NOT NULL REFERENCES g4g_fy(fy) ON DELETE CASCADE,
    bank          text NOT NULL,
    debit         numeric,
    credit        numeric,
    excluded_rows integer
);
CREATE TABLE IF NOT EXISTS g4g_gst_fy (
    id                 bigserial PRIMARY KEY,
    fy                 text NOT NULL REFERENCES g4g_fy(fy) ON DELETE CASCADE,
    gstin              text NOT NULL,
    r1_taxable         numeric,
    output_tax         numeric,
    itc_2b             numeric,
    r3b_filed          boolean,
    vendor_3b_defaults integer
);
CREATE TABLE IF NOT EXISTS g4g_flag (
    id   bigserial PRIMARY KEY,
    fy   text NOT NULL REFERENCES g4g_fy(fy) ON DELETE CASCADE,
    body text NOT NULL
);
"""


def init_schema(conn) -> None:
    conn.execute(SCHEMA)


def _d(v):
    return None if v in (None, "") else Decimal(str(v))


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------

def upsert_fy(conn, fy: str, data: dict) -> None:
    """Idempotent upsert of one FY's figures from a plain dict.

    `data` keys (all optional): audit_status, posture, note, revenue, pat,
    purchase{rows,approved,commission,tds,net_payable,paid,outstanding,
    zero_commission_rows}, sales{invoices,total_sales,receivable},
    tax{tds_26as,itr_status}, bank[{bank,debit,credit,excluded_rows}],
    gst[{gstin,r1_taxable,output_tax,itc_2b,r3b_filed,vendor_3b_defaults}],
    flags[str].
    """
    conn.execute(
        """
        INSERT INTO g4g_fy (fy, audit_status, posture, note, revenue, pat)
        VALUES (%s,%s,%s,%s,%s,%s)
        ON CONFLICT (fy) DO UPDATE SET
            audit_status=EXCLUDED.audit_status, posture=EXCLUDED.posture,
            note=EXCLUDED.note, revenue=EXCLUDED.revenue, pat=EXCLUDED.pat,
            updated_at=now()
        """,
        (fy, data.get("audit_status"), data.get("posture"), data.get("note"),
         _d(data.get("revenue")), _d(data.get("pat"))),
    )

    p = data.get("purchase")
    if p is not None:
        conn.execute(
            """
            INSERT INTO g4g_purchase_fy (fy, rows, approved, commission, tds,
                net_payable, paid, outstanding, zero_commission_rows)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (fy) DO UPDATE SET
                rows=EXCLUDED.rows, approved=EXCLUDED.approved,
                commission=EXCLUDED.commission, tds=EXCLUDED.tds,
                net_payable=EXCLUDED.net_payable, paid=EXCLUDED.paid,
                outstanding=EXCLUDED.outstanding,
                zero_commission_rows=EXCLUDED.zero_commission_rows
            """,
            (fy, p.get("rows"), _d(p.get("approved")), _d(p.get("commission")),
             _d(p.get("tds")), _d(p.get("net_payable")), _d(p.get("paid")),
             _d(p.get("outstanding")), p.get("zero_commission_rows")),
        )

    s = data.get("sales")
    if s is not None:
        conn.execute(
            """
            INSERT INTO g4g_sales_fy (fy, invoices, total_sales, receivable)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (fy) DO UPDATE SET
                invoices=EXCLUDED.invoices, total_sales=EXCLUDED.total_sales,
                receivable=EXCLUDED.receivable
            """,
            (fy, s.get("invoices"), _d(s.get("total_sales")), _d(s.get("receivable"))),
        )

    t = data.get("tax")
    if t is not None:
        conn.execute(
            """
            INSERT INTO g4g_tax_fy (fy, tds_26as, itr_status)
            VALUES (%s,%s,%s)
            ON CONFLICT (fy) DO UPDATE SET
                tds_26as=EXCLUDED.tds_26as, itr_status=EXCLUDED.itr_status
            """,
            (fy, _d(t.get("tds_26as")), t.get("itr_status")),
        )

    # Multi-row sets: replace wholesale so an edit is authoritative.
    if data.get("bank") is not None:
        conn.execute("DELETE FROM g4g_bank_fy WHERE fy=%s", (fy,))
        for b in data["bank"]:
            conn.execute(
                "INSERT INTO g4g_bank_fy (fy, bank, debit, credit, excluded_rows)"
                " VALUES (%s,%s,%s,%s,%s)",
                (fy, b.get("bank"), _d(b.get("debit")), _d(b.get("credit")),
                 b.get("excluded_rows")),
            )
    if data.get("gst") is not None:
        conn.execute("DELETE FROM g4g_gst_fy WHERE fy=%s", (fy,))
        for g in data["gst"]:
            conn.execute(
                "INSERT INTO g4g_gst_fy (fy, gstin, r1_taxable, output_tax, itc_2b,"
                " r3b_filed, vendor_3b_defaults) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (fy, g.get("gstin"), _d(g.get("r1_taxable")), _d(g.get("output_tax")),
                 _d(g.get("itc_2b")), g.get("r3b_filed"), g.get("vendor_3b_defaults")),
            )
    if data.get("flags") is not None:
        conn.execute("DELETE FROM g4g_flag WHERE fy=%s", (fy,))
        for body in data["flags"]:
            conn.execute("INSERT INTO g4g_flag (fy, body) VALUES (%s,%s)", (fy, body))


def seed_from_kp(conn) -> int:
    """Seed every FY from the confirmed Knowledge-Pack figures. Idempotent."""
    meta = {m.fy: m for m in _model.FINANCIAL_YEARS}
    for fy, row in kp_data.KP_FY.items():
        m = meta.get(fy)
        audited = row.get("audited") or {}
        gst = row.get("gst")
        upsert_fy(conn, fy, {
            "audit_status": m.audit_status if m else None,
            "posture": m.posture if m else None,
            "note": m.note if m else None,
            "revenue": audited.get("revenue"),
            "pat": audited.get("pat"),
            "purchase": row.get("purchase"),
            "sales": row.get("sales"),
            "tax": row.get("tax"),
            "bank": row.get("bank") or [],
            "gst": [gst] if gst else [],
            "flags": row.get("flags") or [],
        })
    return len(kp_data.KP_FY)


# ---------------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------------

def read_fy(conn, fy: str) -> FYFinancials:
    head = conn.execute("SELECT * FROM g4g_fy WHERE fy=%s", (fy,)).fetchone()
    if head is None:
        return FYFinancials(fy=fy)

    pr = conn.execute("SELECT * FROM g4g_purchase_fy WHERE fy=%s", (fy,)).fetchone()
    if pr:
        approved, comm = pr["approved"] or Decimal(0), pr["commission"] or Decimal(0)
        tds_, net = pr["tds"] or Decimal(0), pr["net_payable"]
        igst = (approved - comm - tds_ - net) if net is not None else None
        purchase = PurchaseSummary(
            rows=pr["rows"], approved=pr["approved"], commission=pr["commission"],
            tds=pr["tds"], igst_deducted=igst, net_payable=pr["net_payable"],
            paid=pr["paid"], outstanding=pr["outstanding"],
            zero_commission_rows=pr["zero_commission_rows"])
    else:
        purchase = PurchaseSummary()

    sr = conn.execute("SELECT * FROM g4g_sales_fy WHERE fy=%s", (fy,)).fetchone() or {}
    sales = SalesSummary(invoices=sr.get("invoices"),
                         total_sales=sr.get("total_sales"),
                         receivable=sr.get("receivable"))

    tr = conn.execute("SELECT * FROM g4g_tax_fy WHERE fy=%s", (fy,)).fetchone() or {}
    tax = TaxSummary(tds_26as=tr.get("tds_26as"), itr_status=tr.get("itr_status"))

    gst = [GstLine(gstin=g["gstin"], r1_taxable=g["r1_taxable"],
                   output_tax=g["output_tax"], itc_2b=g["itc_2b"],
                   r3b_filed=g["r3b_filed"], vendor_3b_defaults=g["vendor_3b_defaults"])
           for g in conn.execute(
               "SELECT * FROM g4g_gst_fy WHERE fy=%s ORDER BY id", (fy,)).fetchall()]

    bank = [BankLine(bank=b["bank"], debit=b["debit"], credit=b["credit"],
                     excluded_rows=b["excluded_rows"])
            for b in conn.execute(
                "SELECT * FROM g4g_bank_fy WHERE fy=%s ORDER BY id", (fy,)).fetchall()]

    flags = [r["body"] for r in conn.execute(
        "SELECT body FROM g4g_flag WHERE fy=%s ORDER BY id", (fy,)).fetchall()]

    return FYFinancials(fy=fy, sales=sales, purchase=purchase, gst=gst, bank=bank,
                        tax=tax, revenue=head["revenue"], pat=head["pat"], flags=flags)
