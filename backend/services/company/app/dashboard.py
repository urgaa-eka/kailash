"""L4 FY financial dashboard — one self-contained HTML page, rendered from
read-only projections (co_v_* views + compliance artefacts)."""
from __future__ import annotations

import html as _html
from datetime import date

import psycopg

from . import compliance, recon, reports


def _fmt(v) -> str:
    try:
        n = float(v)
    except (TypeError, ValueError):
        return str(v)
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1e7:
        return f"{sign}₹{n / 1e7:,.2f} Cr"
    if n >= 1e5:
        return f"{sign}₹{n / 1e5:,.2f} L"
    return f"{sign}₹{n:,.2f}"


def _esc(s) -> str:
    return _html.escape(str(s))


def render(conn: psycopg.Connection, fy: str) -> str:
    tb = reports.trial_balance(conn, fy)
    s3 = reports.schedule_iii(conn, fy)
    variances = recon.open_variances(conn)
    calendar = [c for c in compliance.load_calendar() if c["status"] != "unscheduled"]
    fys = [r["fy"] for r in conn.execute(
        "SELECT DISTINCT fy FROM co_journal ORDER BY fy"
    ).fetchall()]
    gst = conn.execute(
        """
        SELECT g.gstin, s.gst_period, s.outward_taxable, s.output_tax,
               s.itc_available, s.net_payable
        FROM co_gstr3b_summary s JOIN co_gstin g ON g.gstin_id = s.gstin_id
        ORDER BY s.gst_period
        """
    ).fetchall()

    eq = s3["equation"]
    revenue = next((r["amount"] for r in s3["profit_and_loss"]
                    if r["schedule_iii_group"] == "Revenue from Operations"), "0")

    kpis = [
        ("Revenue (FY)", _fmt(revenue)),
        ("Profit / (Loss)", _fmt(eq["profit"])),
        ("Assets", _fmt(eq["assets"])),
        ("Equity + Liabilities", _fmt(float(eq["equity"]) + float(eq["liabilities"]))),
        ("Books balanced", "YES" if tb["balanced"] else "NO — INVESTIGATE"),
        ("Equation holds", "YES" if eq["holds"] else "NO — INVESTIGATE"),
    ]

    def rows_tb() -> str:
        out = []
        for a in tb["accounts"]:
            out.append(
                f"<tr><td>{_esc(a['account_code'])}</td><td>{_esc(a['account_name'])}</td>"
                f"<td>{_esc(a['schedule_iii_group'])}</td>"
                f"<td class='num'>{_fmt(a['total_debit'])}</td>"
                f"<td class='num'>{_fmt(a['total_credit'])}</td>"
                f"<td class='num'>{_fmt(a['net_movement'])}</td></tr>"
            )
        return "".join(out) or "<tr><td colspan='6' class='empty'>No postings this FY</td></tr>"

    def rows_s3(items) -> str:
        return "".join(
            f"<tr><td>{_esc(r['schedule_iii_group'])}</td>"
            f"<td class='num'>{_fmt(r['amount'])}</td></tr>"
            for r in items
        ) or "<tr><td colspan='2' class='empty'>—</td></tr>"

    def rows_gst() -> str:
        return "".join(
            f"<tr><td>{_esc(g['gstin'])}</td><td>{_esc(g['gst_period'])}</td>"
            f"<td class='num'>{_fmt(g['outward_taxable'])}</td>"
            f"<td class='num'>{_fmt(g['output_tax'])}</td>"
            f"<td class='num'>{_fmt(g['itc_available'])}</td>"
            f"<td class='num'>{_fmt(g['net_payable'])}</td></tr>"
            for g in gst
        ) or "<tr><td colspan='6' class='empty'>No GSTR-3B generated yet</td></tr>"

    def rows_recon() -> str:
        sev_cls = {"matched": "ok", "minor": "warn", "material": "bad"}
        return "".join(
            f"<tr><td>{_esc(v['code'])}</td><td>{_esc(v['period_label'])}</td>"
            f"<td class='num'>{_fmt(v['value_internal'])}</td>"
            f"<td class='num'>{_fmt(v['value_external'])}</td>"
            f"<td class='num'>{_fmt(v['variance_amt'])}</td>"
            f"<td><span class='pill {sev_cls.get(v['severity'], '')}'>"
            f"{_esc(v['severity'])}</span></td>"
            f"<td>{_esc(v['status'])}</td></tr>"
            for v in variances
        ) or "<tr><td colspan='7' class='empty ok-text'>All control points reconciled ✓</td></tr>"

    def rows_cal() -> str:
        st_cls = {"overdue": "bad", "due_soon": "warn", "upcoming": "ok"}
        return "".join(
            f"<tr><td>{_esc(c['area'])}</td><td>{_esc(c['form'])}</td>"
            f"<td>{_esc(c['covers'])}</td><td>{_esc(c['due_date'] or '—')}</td>"
            f"<td><span class='pill {st_cls.get(c['status'], '')}'>"
            f"{_esc(c['status'])}</span></td></tr>"
            for c in calendar
        )

    fy_options = "".join(
        f"<option value='{_esc(f)}'{' selected' if f == fy else ''}>{_esc(f)}</option>"
        for f in (fys or [fy])
    )
    kpi_html = "".join(
        f"<div class='kpi'><div class='kpi-label'>{_esc(k)}</div>"
        f"<div class='kpi-value'>{_esc(v)}</div></div>"
        for k, v in kpis
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kailash · Company Segment · FY {_esc(fy)}</title>
<style>
  :root {{ --bg:#0e1420; --card:#161f2e; --ink:#e8edf5; --dim:#8b98ab;
           --ok:#22c55e; --warn:#f59e0b; --bad:#ef4444; --accent:#38bdf8; }}
  * {{ box-sizing:border-box; margin:0; }}
  body {{ background:var(--bg); color:var(--ink);
          font:14px/1.5 -apple-system,'Segoe UI',Roboto,sans-serif; padding:24px; }}
  h1 {{ font-size:20px; }} h2 {{ font-size:15px; margin-bottom:10px; color:var(--accent); }}
  .sub {{ color:var(--dim); margin:4px 0 20px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr));
           gap:12px; margin-bottom:20px; }}
  .kpi {{ background:var(--card); border-radius:10px; padding:14px 16px; }}
  .kpi-label {{ color:var(--dim); font-size:12px; }}
  .kpi-value {{ font-size:18px; font-weight:600; margin-top:4px; }}
  .card {{ background:var(--card); border-radius:10px; padding:16px; margin-bottom:20px;
           overflow-x:auto; }}
  table {{ border-collapse:collapse; width:100%; }}
  th,td {{ text-align:left; padding:6px 10px; border-bottom:1px solid #22304a;
           white-space:nowrap; }}
  th {{ color:var(--dim); font-weight:500; font-size:12px; }}
  .num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  .empty {{ color:var(--dim); text-align:center; }}
  .ok-text {{ color:var(--ok); }}
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
<h1>Kailash · Company Segment — Master Operational Ledger</h1>
<p class="sub">Financial year
  <select onchange="location.href='/dashboard?fy='+this.value">{fy_options}</select>
  · generated {date.today().isoformat()} · L4 read-only projection of the posted ledger</p>

<div class="kpis">{kpi_html}</div>

<div class="grid2">
  <div class="card"><h2>Statement of Profit &amp; Loss (Schedule III)</h2>
    <table><tr><th>Line</th><th class="num">Amount</th></tr>{rows_s3(s3["profit_and_loss"])}</table>
  </div>
  <div class="card"><h2>Balance Sheet (Schedule III)</h2>
    <table><tr><th>Line</th><th class="num">Amount</th></tr>{rows_s3(s3["balance_sheet"])}</table>
  </div>
</div>

<div class="card"><h2>GST Cockpit — GSTR-3B summaries</h2>
  <table><tr><th>GSTIN</th><th>Period</th><th class="num">Outward taxable</th>
  <th class="num">Output tax</th><th class="num">ITC</th><th class="num">Net payable</th></tr>
  {rows_gst()}</table>
</div>

<div class="card"><h2>Reconciliation Matrix — internal ⟷ CA/Tally (open items)</h2>
  <table><tr><th>Control point</th><th>Period</th><th class="num">Internal</th>
  <th class="num">External</th><th class="num">Variance</th><th>Severity</th><th>Status</th></tr>
  {rows_recon()}</table>
</div>

<div class="card"><h2>Compliance Calendar</h2>
  <table><tr><th>Area</th><th>Form</th><th>Covers</th><th>Due</th><th>Status</th></tr>
  {rows_cal()}</table>
</div>

<div class="card"><h2>Trial Balance</h2>
  <table><tr><th>Code</th><th>Account</th><th>Schedule III group</th>
  <th class="num">Debit</th><th class="num">Credit</th><th class="num">Net</th></tr>
  {rows_tb()}
  <tr><th></th><th>TOTAL</th><th></th>
  <th class="num">{_fmt(tb["total_debit"])}</th>
  <th class="num">{_fmt(tb["total_credit"])}</th><th></th></tr></table>
</div>

</body></html>"""
