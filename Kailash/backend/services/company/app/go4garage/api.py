"""JSON serialisation of the FY dashboard — the frontend / Zoho-mapping seam.

Emits the **same key shape the store accepts** (see `store.upsert_fy`), so a figure
the dashboard shows maps 1:1 onto what you would POST to `/go4garage/fy/{fy}` and,
from there, into Zoho Books. Money is emitted as strings to preserve exact Decimal
precision (the frontend parses to numbers only for display); counts stay ints;
`None` means "not yet sourced" and the frontend renders "awaiting source".

Two endpoints consume this (see routes.py):
  GET /go4garage/api/overview   — entity, model, departments, defects, decisions,
                                  the five-year trend, provider status, rates.
  GET /go4garage/api/fy/{fy}    — one year's full FYFinancials in store shape.
"""
from __future__ import annotations

from . import defects as _defects
from . import kp_data as _kp
from . import model as _model
from .logic import COMMISSION_RATE, TDS_RATE
from .provider import FinancialDataProvider, FYFinancials


def _s(v):
    """Decimal/number -> str (exact); None stays None. Never fabricate a value."""
    return None if v is None else str(v)


def _fy_meta(fy: str):
    return next((m for m in _model.FINANCIAL_YEARS if m.fy == fy), None)


def fy_payload(fin: FYFinancials) -> dict:
    """One financial year, in the store's accepted key shape (Zoho-mappable)."""
    p, s, t = fin.purchase, fin.sales, fin.tax
    meta = _fy_meta(fin.fy)
    return {
        "fy": fin.fy,
        "audit_status": meta.audit_status if meta else None,
        "posture": meta.posture if meta else None,
        "note": meta.note if meta else None,
        "revenue": _s(fin.revenue),
        "pat": _s(fin.pat),
        "flags": list(fin.flags),
        "sales": {
            "invoices": s.invoices,
            "total_sales": _s(s.total_sales),
            "receivable": _s(s.receivable),
        },
        "purchase": {
            "rows": p.rows,
            "approved": _s(p.approved),
            "commission": _s(p.commission),
            "tds": _s(p.tds),
            "igst_deducted": _s(p.igst_deducted),
            "net_payable": _s(p.net_payable),
            "paid": _s(p.paid),
            "outstanding": _s(p.outstanding),
            "zero_commission_rows": p.zero_commission_rows,
        },
        "gst": [
            {
                "gstin": g.gstin,
                "r1_taxable": _s(g.r1_taxable),
                "output_tax": _s(g.output_tax),
                "itc_2b": _s(g.itc_2b),
                "r3b_filed": g.r3b_filed,
                "vendor_3b_defaults": g.vendor_3b_defaults,
            }
            for g in fin.gst
        ],
        "bank": [
            {
                "bank": b.bank,
                "debit": _s(b.debit),
                "credit": _s(b.credit),
                "excluded_rows": b.excluded_rows,
            }
            for b in fin.bank
        ],
        "tax": {"tds_26as": _s(t.tds_26as), "itr_status": t.itr_status},
    }


def _trend(provider: FinancialDataProvider) -> list[dict]:
    """Compact per-FY series for the five-year chart (one pass over the model)."""
    out = []
    for m in _model.FINANCIAL_YEARS:
        f = provider.fy_financials(m.fy)
        out.append({
            "fy": m.fy,
            "audit_status": m.audit_status,
            "posture": m.posture,
            "revenue": _s(f.revenue),
            "pat": _s(f.pat),
            "net_payable": _s(f.purchase.net_payable),
            "total_sales": _s(f.sales.total_sales),
            "invoices": f.sales.invoices,
        })
    return out


# Flat, one-row-per-FY export in the store's column shape — for column-mapping
# into Zoho's importer or re-loading the store. Money as exact strings; blank
# means "not yet sourced".
EXPORT_FIELDS = [
    "fy", "audit_status", "posture",
    "revenue", "pat",
    "sales_invoices", "sales_total_sales", "sales_receivable",
    "purchase_rows", "purchase_approved", "purchase_commission", "purchase_tds",
    "purchase_igst_deducted", "purchase_net_payable", "purchase_paid",
    "purchase_outstanding", "purchase_zero_commission_rows",
    "tax_tds_26as", "tax_itr_status",
]


def export_rows(provider: FinancialDataProvider) -> list[dict]:
    """One flat dict per FY, keyed by EXPORT_FIELDS (Zoho-mappable / store-shape)."""
    rows = []
    for m in _model.FINANCIAL_YEARS:
        fin = provider.fy_financials(m.fy)
        p, s, t = fin.purchase, fin.sales, fin.tax
        rows.append({
            "fy": m.fy, "audit_status": m.audit_status, "posture": m.posture,
            "revenue": _s(fin.revenue), "pat": _s(fin.pat),
            "sales_invoices": s.invoices, "sales_total_sales": _s(s.total_sales),
            "sales_receivable": _s(s.receivable),
            "purchase_rows": p.rows, "purchase_approved": _s(p.approved),
            "purchase_commission": _s(p.commission), "purchase_tds": _s(p.tds),
            "purchase_igst_deducted": _s(p.igst_deducted),
            "purchase_net_payable": _s(p.net_payable), "purchase_paid": _s(p.paid),
            "purchase_outstanding": _s(p.outstanding),
            "purchase_zero_commission_rows": p.zero_commission_rows,
            "tax_tds_26as": _s(t.tds_26as), "tax_itr_status": t.itr_status,
        })
    return rows


def export_csv(provider: FinancialDataProvider) -> str:
    """The five-year flat export as CSV text (RFC 4180). Blank = not yet sourced."""
    import csv
    import io

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=EXPORT_FIELDS, extrasaction="ignore")
    w.writeheader()
    for r in export_rows(provider):
        w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in EXPORT_FIELDS})
    return buf.getvalue()


def overview_payload(provider: FinancialDataProvider) -> dict:
    """Everything FY-independent: entity, model spine, governance, trend, status."""
    return {
        "entity": dict(_model.ENTITY),
        "gstins": [dict(g) for g in _model.GSTINS],
        "directors": [dict(d) for d in _model.DIRECTORS],
        "related_party_note": _model.RELATED_PARTY_NOTE,
        "financial_years": [
            {"fy": m.fy, "audit_status": m.audit_status, "posture": m.posture, "note": m.note}
            for m in _model.FINANCIAL_YEARS
        ],
        "closed_year_cutoff": _model.CLOSED_YEAR_CUTOFF,
        "zoho": dict(_model.ZOHO),
        "departments": [
            {
                "num": d.num, "name": d.name, "owns": d.owns,
                "source_of_truth": d.source_of_truth,
                "standing_defect": d.standing_defect, "cross_cutting": d.cross_cutting,
            }
            for d in _model.DEPARTMENTS
        ],
        "defects": [
            {"id": d.id, "dept": d.dept, "title": d.title, "guard": d.guard,
             "severity": d.severity, "status": d.status}
            for d in _defects.DEFECTS
        ],
        "decisions": [
            {"id": q.id, "dept": q.dept, "question": q.question, "owner": q.owner}
            for q in _defects.OPEN_DECISIONS
        ],
        "rates": {"commission": str(COMMISSION_RATE), "tds": str(TDS_RATE)},
        "provider": {
            "name": provider.name(),
            "connected": provider.connected(),
            "source_label": provider.source_label(),
        },
        "trend": _trend(provider),
        "reference_totals": {
            "purchase_approved": _kp.PURCHASE_APPROVED_TOTAL,
            "sales_date_derived": _kp.SALES_DATE_DERIVED_TOTAL,
        },
    }
