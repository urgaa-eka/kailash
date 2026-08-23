"""Go4Garage FY dashboard — one self-contained HTML page, organised by the model.

Renders entity, the five financial years, the ten departments, the sales and
vendor-settlement views (with the confirmed Net Payable formula), the GST cockpit
across three GSTINs, treasury, direct tax, and the internal-audit registry of
defects and open decisions. Every figure is routed through a data provider; when
none is connected the page shows "awaiting source" rather than a made-up number.
"""
from __future__ import annotations

import html as _html
from datetime import date

from . import defects as _defects
from . import model as _model
from .logic import COMMISSION_RATE, TDS_RATE
from .provider import FinancialDataProvider, FYFinancials

_AWAIT = "<span class='await'>awaiting source</span>"


def _esc(s) -> str:
    return _html.escape(str(s))


def _money(v) -> str:
    """Indian ₹ with Cr/L scaling; None -> awaiting-source marker."""
    if v is None:
        return _AWAIT
    try:
        n = float(v)
    except (TypeError, ValueError):
        return _esc(v)
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1e7:
        return f"{sign}₹{n / 1e7:,.2f} Cr"
    if n >= 1e5:
        return f"{sign}₹{n / 1e5:,.2f} L"
    return f"{sign}₹{n:,.2f}"


def _int(v) -> str:
    return _AWAIT if v is None else f"{int(v):,}"


def _text(v) -> str:
    return _AWAIT if v in (None, "") else _esc(v)


_AUDIT_CLS = {"AUDITED_SIGNED": "ok", "AUDITED_QUALIFIED": "warn",
             "UNAUDITED": "warn", "NONE": "bad"}
_SEV_CLS = {"material": "bad", "major": "warn", "minor": "ok"}
_STATUS_CLS = {"open": "bad", "mitigated": "warn", "fixed": "ok",
               "withdrawn": "ok"}


def render_fy(provider: FinancialDataProvider, fy: str, *, today: date | None = None) -> str:
    today = today or date.today()
    fys = [m.fy for m in _model.FINANCIAL_YEARS]
    if fy not in fys:
        fy = fys[-1]
    fin: FYFinancials = provider.fy_financials(fy)
    p, s, t = fin.purchase, fin.sales, fin.tax

    connected = provider.connected()
    conn_pill = ("<span class='pill ok'>connected</span>" if connected
                 else "<span class='pill warn'>not connected</span>")

    # --- KPIs (all provider-fed; None renders as awaiting-source) ---
    kpis = [
        ("Revenue (FY)", _money(fin.revenue)),
        ("Profit / (Loss)", _money(fin.pat)),
        ("Sales invoices", _int(s.invoices)),
        ("Net Payable (vendors)", _money(p.net_payable)),
        ("Outstanding to vendors", _money(p.outstanding)),
        ("TDS credited (26AS)", _money(t.tds_26as)),
    ]

    def fy_options() -> str:
        return "".join(
            f"<option value='{_esc(m.fy)}'{' selected' if m.fy == fy else ''}>"
            f"{_esc(m.fy)} · {_esc(m.audit_status.replace('_', ' ').title())}</option>"
            for m in _model.FINANCIAL_YEARS)

    def gstins() -> str:
        return " · ".join(f"{_esc(g['gstin'])} ({_esc(g['state'])})" for g in _model.GSTINS)

    def years_row() -> str:
        return "".join(
            f"<tr><td>{_esc(m.fy)}</td>"
            f"<td><span class='pill {_AUDIT_CLS.get(m.audit_status,'')}'>"
            f"{_esc(m.audit_status.replace('_',' ').title())}</span></td>"
            f"<td>{_esc(m.posture)}</td><td class='dim'>{_esc(m.note)}</td></tr>"
            for m in _model.FINANCIAL_YEARS)

    def departments_row() -> str:
        out = []
        for d in _model.DEPARTMENTS:
            veto = " · <span class='pill warn'>veto</span>" if d.cross_cutting else ""
            out.append(
                f"<tr><td class='num'>{d.num}</td><td>{_esc(d.name)}{veto}</td>"
                f"<td class='dim'>{_esc(d.owns)}</td>"
                f"<td class='dim'>{_esc(d.source_of_truth)}</td></tr>")
        return "".join(out)

    def vendor_rows() -> str:
        # The Net Payable identity, laid out as a waterfall.
        rows = [
            ("Vendor-facing approved", _money(p.approved), ""),
            (f"less Commission ({COMMISSION_RATE:.0%})", _money(p.commission), "sub"),
            (f"less TDS ({TDS_RATE:.1%})", _money(p.tds), "sub"),
            ("less IGST (only when GST 'Not Available')", _money(p.igst_deducted), "sub"),
            ("= Net Payable", _money(p.net_payable), "tot"),
            ("less Paid", _money(p.paid), "sub"),
            ("= Outstanding (recomputed, ₹1 floor)", _money(p.outstanding), "tot"),
        ]
        return "".join(
            f"<tr class='{cls}'><td>{label}</td><td class='num'>{val}</td></tr>"
            for label, val, cls in rows)

    def gst_rows() -> str:
        if not fin.gst:
            return ("<tr><td colspan='6' class='empty'>Three GSTINs configured; "
                    "R1/2B/3B load after the GST source is connected</td></tr>")
        out = []
        for g in fin.gst:
            filed = ("—" if g.r3b_filed is None
                     else ("<span class='pill ok'>filed</span>" if g.r3b_filed
                           else "<span class='pill bad'>not filed</span>"))
            out.append(
                f"<tr><td>{_esc(g.gstin)}</td>"
                f"<td class='num'>{_money(g.r1_taxable)}</td>"
                f"<td class='num'>{_money(g.output_tax)}</td>"
                f"<td class='num'>{_money(g.itc_2b)}</td>"
                f"<td>{filed}</td><td class='num'>{_int(g.vendor_3b_defaults)}</td></tr>")
        return "".join(out)

    def bank_rows() -> str:
        if not fin.bank:
            return "<tr><td colspan='4' class='empty'>Bank rows load after the treasury source is connected</td></tr>"
        return "".join(
            f"<tr><td>{_esc(b.bank)}</td><td class='num'>{_money(b.debit)}</td>"
            f"<td class='num'>{_money(b.credit)}</td>"
            f"<td class='num'>{_int(b.excluded_rows)}</td></tr>"
            for b in fin.bank)

    def defects_rows() -> str:
        return "".join(
            f"<tr><td>{_esc(d.id)}</td><td class='num'>{d.dept}</td>"
            f"<td>{_esc(d.title)}</td><td class='dim'>{_esc(d.guard)}</td>"
            f"<td><span class='pill {_SEV_CLS.get(d.severity,'')}'>{_esc(d.severity)}</span></td>"
            f"<td><span class='pill {_STATUS_CLS.get(d.status,'')}'>{_esc(d.status)}</span></td></tr>"
            for d in _defects.DEFECTS)

    def decisions_rows() -> str:
        return "".join(
            f"<tr><td>{_esc(q.id)}</td><td class='num'>{q.dept}</td>"
            f"<td>{_esc(q.question)}</td><td>{_esc(q.owner)}</td></tr>"
            for q in _defects.OPEN_DECISIONS)

    flags_html = ""
    if fin.flags:
        items = "".join(f"<li>{_esc(f)}</li>" for f in fin.flags)
        flags_html = (f"<div class='card'><h2>Flagged for FY {_esc(fy)} — "
                      "contradictions &amp; caveats (surfaced, not resolved)</h2>"
                      f"<ul class='flags'>{items}</ul></div>")

    kpi_html = "".join(
        f"<div class='kpi'><div class='kpi-label'>{_esc(k)}</div>"
        f"<div class='kpi-value'>{v}</div></div>" for k, v in kpis)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Go4Garage · Financial Controller · FY {_esc(fy)}</title>
<style>
  :root {{ --bg:#0e1420; --card:#161f2e; --ink:#e8edf5; --dim:#8b98ab;
           --ok:#22c55e; --warn:#f59e0b; --bad:#ef4444; --accent:#38bdf8; }}
  * {{ box-sizing:border-box; margin:0; }}
  body {{ background:var(--bg); color:var(--ink);
          font:14px/1.5 -apple-system,'Segoe UI',Roboto,sans-serif; padding:24px; }}
  h1 {{ font-size:20px; }} h2 {{ font-size:15px; margin-bottom:10px; color:var(--accent); }}
  .sub {{ color:var(--dim); margin:4px 0 16px; }}
  .banner {{ background:#3b2405; border:1px solid #f59e0b44; color:#fcd34d;
             border-radius:10px; padding:10px 14px; margin-bottom:20px; font-size:13px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
           gap:12px; margin-bottom:20px; }}
  .kpi {{ background:var(--card); border-radius:10px; padding:14px 16px; }}
  .kpi-label {{ color:var(--dim); font-size:12px; }}
  .kpi-value {{ font-size:17px; font-weight:600; margin-top:4px; }}
  .card {{ background:var(--card); border-radius:10px; padding:16px; margin-bottom:20px;
           overflow-x:auto; }}
  table {{ border-collapse:collapse; width:100%; }}
  th,td {{ text-align:left; padding:6px 10px; border-bottom:1px solid #22304a;
           white-space:nowrap; vertical-align:top; }}
  th {{ color:var(--dim); font-weight:500; font-size:12px; }}
  td.dim,.dim {{ color:var(--dim); white-space:normal; }}
  .num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  .empty {{ color:var(--dim); text-align:center; }}
  tr.sub td:first-child {{ padding-left:22px; color:var(--dim); }}
  tr.tot td {{ font-weight:600; border-top:1px solid #2a3b58; }}
  .await {{ color:var(--dim); font-style:italic; font-size:12px; }}
  .flags {{ margin:0; padding-left:18px; }}
  .flags li {{ margin:4px 0; color:var(--warn); white-space:normal; }}
  .pill {{ padding:2px 8px; border-radius:99px; font-size:12px; }}
  .pill.ok {{ background:#052e16; color:var(--ok); }}
  .pill.warn {{ background:#3b2405; color:var(--warn); }}
  .pill.bad {{ background:#450a0a; color:var(--bad); }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
  @media (max-width:900px) {{ .grid2 {{ grid-template-columns:1fr; }} }}
  select {{ background:var(--card); color:var(--ink); border:1px solid #2a3b58;
            border-radius:6px; padding:4px 8px; }}
</style>
</head>
<body>
<h1>{_esc(_model.ENTITY['name'])} — Financial Controller</h1>
<p class="sub">
  CIN {_esc(_model.ENTITY['cin'])} · PAN {_esc(_model.ENTITY['pan'])} · GSTINs: {gstins()}<br>
  Financial year
  <select onchange="location.href='?fy='+this.value">{fy_options()}</select>
  · {conn_pill} <span class="dim">{_esc(provider.source_label())}</span>
  · generated {today.isoformat()}
</p>

<div class="banner">
  <b>Two approval layers, never joined.</b> Client approval drives sales only and
  is confidential to vendors; vendor approval drives purchases only. There is no
  per-job spread — margin is a P&amp;L-level figure (sales − net purchase cost).
  Related parties: {_esc(_model.RELATED_PARTY_NOTE)}
</div>

<div class="kpis">{kpi_html}</div>

{flags_html}

<div class="grid2">
  <div class="card"><h2>Dept 2 · Vendor / Workshop Settlement — Net Payable</h2>
    <table><tr><th>Line</th><th class="num">FY {_esc(fy)}</th></tr>{vendor_rows()}</table>
    <p class="dim" style="margin-top:8px">Rows: {_int(p.rows)} · zero-commission rows (Q3): {_int(p.zero_commission_rows)}</p>
  </div>
  <div class="card"><h2>Dept 1 · Sales / Client Billing</h2>
    <table>
      <tr><td>Invoices</td><td class="num">{_int(s.invoices)}</td></tr>
      <tr><td>Total sales (from Date, not the FY column)</td><td class="num">{_money(s.total_sales)}</td></tr>
      <tr><td>Receivable</td><td class="num">{_money(s.receivable)}</td></tr>
    </table>
    <p class="dim" style="margin-top:8px">FY is derived from the invoice Date — the
      ledger's <code>Financial Year</code> column is the invoice prefix and misallocates ₹2.96 Cr.</p>
  </div>
</div>

<div class="card"><h2>Dept 4 · GST Cockpit — three GSTINs (R1 / 2B / 3B)</h2>
  <table><tr><th>GSTIN</th><th class="num">R1 taxable</th><th class="num">Output tax</th>
  <th class="num">ITC (2B)</th><th>3B filed</th><th class="num">Vendor 3B defaults</th></tr>
  {gst_rows()}</table>
  <p class="dim" style="margin-top:8px">Deduction trigger is GSTR-<b>3B</b>, never 2B presence:
    2B proves declaration, 3B proves discharge. Hold back the GST component until the vendor's 3B is confirmed filed.</p>
</div>

<div class="grid2">
  <div class="card"><h2>Dept 3 · Treasury / Banking</h2>
    <table><tr><th>Bank</th><th class="num">Debit</th><th class="num">Credit</th>
    <th class="num">Excluded (re-dated)</th></tr>{bank_rows()}</table>
    <p class="dim" style="margin-top:8px">Skip <code>TOTAL</code> rows; the FY25-26 ICICI re-dated
      block is quarantined (D6). Company funds vs director-personal are kept separate.</p>
  </div>
  <div class="card"><h2>Dept 5 · Direct Tax / TDS</h2>
    <table>
      <tr><td>TDS credited (26AS)</td><td class="num">{_money(t.tds_26as)}</td></tr>
      <tr><td>ITR status</td><td class="num">{_text(t.itr_status)}</td></tr>
    </table>
    <p class="dim" style="margin-top:8px">2% deduction → 26Q → challans → 26AS → ITR. No ITR filed for AY2024-25 / AY2025-26.</p>
  </div>
</div>

<div class="card"><h2>The five financial years</h2>
  <table><tr><th>FY</th><th>Audit status</th><th>Posture</th><th>Note</th></tr>{years_row()}</table>
  <p class="dim" style="margin-top:8px">Closed years (≤ {_esc(_model.CLOSED_YEAR_CUTOFF)}) are carried by
    summary journals in Zoho org {_esc(_model.ZOHO['target_org'])}; never post transaction-level detail into them.</p>
</div>

<div class="card"><h2>The ten departments</h2>
  <table><tr><th class="num">#</th><th>Department</th><th>Owns</th><th>Source of truth</th></tr>{departments_row()}</table>
</div>

<div class="card"><h2>Dept 10 · Internal Audit — known defects (the veto gate)</h2>
  <table><tr><th>ID</th><th class="num">Dept</th><th>Defect</th><th>Guard</th><th>Severity</th><th>Status</th></tr>
  {defects_rows()}</table>
</div>

<div class="card"><h2>Open decisions — escalate, never resolve alone</h2>
  <table><tr><th>ID</th><th class="num">Dept</th><th>Decision</th><th>Owner</th></tr>{decisions_rows()}</table>
</div>

</body></html>"""
