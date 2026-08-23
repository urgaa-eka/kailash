"""Go4Garage FY dashboard — one self-contained HTML page, organised by the model.

Renders entity, the five financial years, the ten departments, the sales and
vendor-settlement views (with the confirmed Net Payable formula), the GST cockpit
across three GSTINs, treasury, direct tax, and the internal-audit registry of
defects and open decisions. Every figure is routed through a data provider; when
none is connected the page shows "awaiting source" rather than a made-up number.

Design: the "Eames" identity — warm paper ground, espresso rail, burnished-gold
data-viz — carrying the GO4GARAGE brand colours (navy #0A3D62 primary, amber
#FFC312 secondary) that also key the frontend theme, so this page and the React
dashboard read as one product. Charts are hand-drawn SVG (no dependency).

`render_fy` serves one FY from the backend (dropdown navigates by ?fy=).
`render_static` bakes all five FYs into a single self-contained page with a
client-side switcher — for publishing as a standalone artifact, no server.
"""
from __future__ import annotations

import html as _html
from datetime import date

from . import defects as _defects
from . import model as _model
from .logic import COMMISSION_RATE, TDS_RATE
from .provider import FinancialDataProvider, FYFinancials

_AWAIT = "<span class='await'>awaiting source</span>"

_AUDIT_CLS = {"AUDITED_SIGNED": "ok", "AUDITED_QUALIFIED": "warn",
             "UNAUDITED": "warn", "NONE": "bad"}
_SEV_CLS = {"material": "bad", "major": "warn", "minor": "ok"}
_STATUS_CLS = {"open": "bad", "mitigated": "warn", "fixed": "ok", "withdrawn": "ok"}


def _esc(s) -> str:
    return _html.escape(str(s))


def _fnum(v):
    """Best-effort float for arithmetic/plotting; None stays None."""
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _money(v) -> str:
    """Indian ₹ with Cr/L scaling; None -> awaiting-source marker."""
    if v is None:
        return _AWAIT
    n = _fnum(v)
    if n is None:
        return _esc(v)
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1e7:
        return f"{sign}₹{n / 1e7:,.2f} Cr"
    if n >= 1e5:
        return f"{sign}₹{n / 1e5:,.2f} L"
    return f"{sign}₹{n:,.2f}"


def _compact(v) -> str:
    """Very short ₹ label for chart annotations."""
    n = _fnum(v)
    if n is None:
        return "—"
    sign = "-" if n < 0 else ""
    a = abs(n)
    if a >= 1e7:
        return f"{sign}₹{a / 1e7:.2f}Cr"
    if a >= 1e5:
        return f"{sign}₹{a / 1e5:.1f}L"
    if a >= 1e3:
        return f"{sign}₹{a / 1e3:.0f}k"
    return f"{sign}₹{a:.0f}"


def _int(v) -> str:
    return _AWAIT if v is None else f"{int(v):,}"


def _text(v) -> str:
    return _AWAIT if v in (None, "") else _esc(v)


# --------------------------------------------------------------------------
# SVG charts (hand-drawn, theme-aware via CSS classes) — no dependency
# --------------------------------------------------------------------------

def _summaries(provider: FinancialDataProvider) -> list[dict]:
    """Compact per-FY figures for the five-year trend (one pass over the model)."""
    out = []
    for m in _model.FINANCIAL_YEARS:
        f = provider.fy_financials(m.fy)
        out.append({
            "fy": m.fy,
            "revenue": _fnum(f.revenue),
            "pat": _fnum(f.pat),
            "net_payable": _fnum(f.purchase.net_payable),
            "sales": _fnum(f.sales.total_sales),
        })
    return out


def _trend_chart(summaries: list[dict]) -> str:
    """Five-year revenue bars (burnished gold) with a profit/(loss) chip per year.

    Revenue and profit differ by orders of magnitude (thin margins are the story),
    so profit is annotated as a signed chip rather than crushed onto one axis.
    """
    revs = [s["revenue"] for s in summaries]
    have = [r for r in revs if r is not None]
    if not have:
        return "<p class='await'>five-year trend loads once an audited/live source is connected</p>"
    vmax = max(have) or 1.0
    n = len(summaries)
    W, H = 720, 260
    padL, padR, padT, padB = 54, 16, 26, 58
    plotW, plotH = W - padL - padR, H - padT - padB
    slot = plotW / n
    bw = min(64, slot * 0.5)

    # horizontal gridlines at 0/¼/½/¾/max
    grid = []
    for i in range(5):
        gv = vmax * i / 4
        gy = padT + plotH - (gv / vmax) * plotH
        grid.append(f"<line class='grid' x1='{padL}' y1='{gy:.1f}' x2='{W - padR}' y2='{gy:.1f}'/>")
        grid.append(f"<text class='axis' x='{padL - 8}' y='{gy + 3:.1f}' text-anchor='end'>{_compact(gv)}</text>")

    bars, labels, chips = [], [], []
    for i, s in enumerate(summaries):
        cx = padL + slot * i + slot / 2
        r = s["revenue"]
        if r is not None and r > 0:
            bh = (r / vmax) * plotH
            by = padT + plotH - bh
            bars.append(f"<rect class='bar-rev' x='{cx - bw / 2:.1f}' y='{by:.1f}' "
                        f"width='{bw:.1f}' height='{bh:.1f}' rx='3'/>")
            bars.append(f"<text class='bar-val' x='{cx:.1f}' y='{by - 6:.1f}' "
                        f"text-anchor='middle'>{_compact(r)}</text>")
        else:
            bars.append(f"<text class='await-sm' x='{cx:.1f}' y='{padT + plotH - 6:.1f}' "
                        f"text-anchor='middle'>no audit</text>")
        labels.append(f"<text class='axis fy' x='{cx:.1f}' y='{H - padB + 20:.1f}' "
                      f"text-anchor='middle'>{_esc(s['fy'])}</text>")
        pat = s["pat"]
        if pat is not None:
            cls = "chip-pos" if pat >= 0 else "chip-neg"
            chips.append(f"<text class='{cls}' x='{cx:.1f}' y='{H - padB + 38:.1f}' "
                         f"text-anchor='middle'>{_compact(pat)}</text>")
        else:
            chips.append(f"<text class='axis-dim' x='{cx:.1f}' y='{H - padB + 38:.1f}' "
                         f"text-anchor='middle'>PAT —</text>")

    return f"""<div class="chart-wrap">
  <svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Five-year revenue and profit trend" preserveAspectRatio="xMinYMin meet">
    {''.join(grid)}{''.join(bars)}{''.join(labels)}{''.join(chips)}
  </svg>
  <div class="chart-legend"><span><i class="sw sw-rev"></i>Revenue (bars)</span>
    <span><i class="sw sw-pat"></i>Profit / (loss) after tax — per year</span></div>
</div>"""


def _waterfall(p) -> str:
    """The Net Payable waterfall: Approved − Commission − TDS − IGST = Net Payable
    (and, once treasury is connected, − Paid = Outstanding). Ties by construction."""
    approved = _fnum(p.approved)
    if not approved or approved <= 0:
        return "<p class='await'>waterfall loads once the vendor register is connected</p>"
    comm = _fnum(p.commission) or 0.0
    tds = _fnum(p.tds) or 0.0
    igst = _fnum(p.igst_deducted) or 0.0
    net = _fnum(p.net_payable)
    if net is None:
        net = approved - comm - tds - igst

    steps = [("Approved", "base", approved),
             (f"−Commission {COMMISSION_RATE:.0%}", "minus", comm),
             (f"−TDS {TDS_RATE:.1%}", "minus", tds)]
    if igst > 0:
        steps.append(("−IGST", "minus", igst))
    steps.append(("Net Payable", "total", net))
    paid = _fnum(p.paid)
    out = _fnum(p.outstanding)
    if paid:
        steps.append(("−Paid", "minus", paid))
    if out is not None:
        steps.append(("Outstanding", "total", out))

    n = len(steps)
    W, H = 720, 280
    padL, padR, padT, padB = 54, 16, 20, 54
    plotW, plotH = W - padL - padR, H - padT - padB
    slot = plotW / n
    bw = min(74, slot * 0.62)
    vmax = approved * 1.06

    def y(v):
        return padT + plotH - (v / vmax) * plotH

    grid = []
    for i in range(4):
        gv = vmax * i / 3
        gy = y(gv)
        grid.append(f"<line class='grid' x1='{padL}' y1='{gy:.1f}' x2='{W - padR}' y2='{gy:.1f}'/>")
        grid.append(f"<text class='axis' x='{padL - 8}' y='{gy + 3:.1f}' text-anchor='end'>{_compact(gv)}</text>")

    bars, labels, conns = [], [], []
    running = approved
    prev_x2 = None
    for i, (label, kind, val) in enumerate(steps):
        cx = padL + slot * i + slot / 2
        x1 = cx - bw / 2
        if kind == "base":
            top, bot = val, 0.0
            running = val
            cls = "bar-base"
        elif kind == "minus":
            top, bot = running, running - val
            running = running - val
            cls = "bar-minus"
        else:  # total
            top, bot = val, 0.0
            running = val
            cls = "bar-total"
        yt, yb = y(top), y(bot)
        h = max(1.6, yb - yt)
        bars.append(f"<rect class='{cls}' x='{x1:.1f}' y='{yt:.1f}' width='{bw:.1f}' "
                    f"height='{h:.1f}' rx='3'/>")
        vlabel = f"−{_compact(val)}" if kind == "minus" else _compact(val)
        bars.append(f"<text class='bar-val' x='{cx:.1f}' y='{yt - 6:.1f}' text-anchor='middle'>{vlabel}</text>")
        labels.append(f"<text class='axis wf' x='{cx:.1f}' y='{H - padB + 18:.1f}' "
                      f"text-anchor='middle'>{_esc(label)}</text>")
        if prev_x2 is not None:
            conns.append(f"<line class='wf-conn' x1='{prev_x2:.1f}' y1='{y(top if kind=='minus' else running):.1f}' "
                         f"x2='{x1:.1f}' y2='{y(top if kind=='minus' else running):.1f}'/>")
        prev_x2 = cx + bw / 2

    return f"""<div class="chart-wrap">
  <svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Net Payable waterfall" preserveAspectRatio="xMinYMin meet">
    {''.join(grid)}{''.join(conns)}{''.join(bars)}{''.join(labels)}
  </svg>
  <div class="chart-legend"><span><i class="sw sw-rev"></i>Vendor-facing / net</span>
    <span><i class="sw sw-minus"></i>Statutory &amp; commission deductions</span>
    <span><i class="sw sw-navy"></i>Net Payable</span></div>
</div>"""


# --------------------------------------------------------------------------
# FY-independent fragments (identical for every year)
# --------------------------------------------------------------------------

def _gstins() -> str:
    return " · ".join(f"{_esc(g['gstin'])} ({_esc(g['state'])})" for g in _model.GSTINS)


def _years_rows() -> str:
    return "".join(
        f"<tr><td>{_esc(m.fy)}</td>"
        f"<td><span class='pill {_AUDIT_CLS.get(m.audit_status,'')}'>"
        f"{_esc(m.audit_status.replace('_',' ').title())}</span></td>"
        f"<td>{_esc(m.posture)}</td><td class='dim'>{_esc(m.note)}</td></tr>"
        for m in _model.FINANCIAL_YEARS)


def _departments_rows() -> str:
    out = []
    for d in _model.DEPARTMENTS:
        veto = " · <span class='pill warn'>veto</span>" if d.cross_cutting else ""
        out.append(
            f"<tr><td class='num'>{d.num}</td><td>{_esc(d.name)}{veto}</td>"
            f"<td class='dim'>{_esc(d.owns)}</td>"
            f"<td class='dim'>{_esc(d.source_of_truth)}</td></tr>")
    return "".join(out)


def _defects_rows() -> str:
    return "".join(
        f"<tr><td>{_esc(d.id)}</td><td class='num'>{d.dept}</td>"
        f"<td>{_esc(d.title)}</td><td class='dim'>{_esc(d.guard)}</td>"
        f"<td><span class='pill {_SEV_CLS.get(d.severity,'')}'>{_esc(d.severity)}</span></td>"
        f"<td><span class='pill {_STATUS_CLS.get(d.status,'')}'>{_esc(d.status)}</span></td></tr>"
        for d in _defects.DEFECTS)


def _decisions_rows() -> str:
    return "".join(
        f"<tr><td>{_esc(q.id)}</td><td class='num'>{q.dept}</td>"
        f"<td>{_esc(q.question)}</td><td>{_esc(q.owner)}</td></tr>"
        for q in _defects.OPEN_DECISIONS)


def _banner() -> str:
    return (
        "<div class='banner'><b>Two approval layers, never joined.</b> Client "
        "approval drives sales only and is confidential to vendors; vendor approval "
        "drives purchases only. There is no per-job spread — margin is a P&amp;L-level "
        "figure (sales − net purchase cost). Related parties: "
        f"{_esc(_model.RELATED_PARTY_NOTE)}</div>")


def _reference_cards(summaries: list[dict]) -> str:
    return f"""
<section class="card" id="trend"><div class="card-h"><h2>Five-year trend</h2>
  <span class="card-note">revenue audited where available; profit annotated per year</span></div>
  {_trend_chart(summaries)}
  <table class="mt"><tr><th>FY</th><th>Audit status</th><th>Posture</th><th>Note</th></tr>{_years_rows()}</table>
  <p class="dim mt-s">Closed years (≤ {_esc(_model.CLOSED_YEAR_CUTOFF)}) are carried by
    summary journals in Zoho org {_esc(_model.ZOHO['target_org'])}; never post transaction-level detail into them.</p>
</section>
<section class="card" id="departments"><div class="card-h"><h2>The ten departments</h2>
  <span class="card-note">the organising spine of the controller model</span></div>
  <table><tr><th class="num">#</th><th>Department</th><th>Owns</th><th>Source of truth</th></tr>{_departments_rows()}</table>
</section>
<section class="card" id="audit"><div class="card-h"><h2>Internal Audit — known defects (the veto gate)</h2>
  <span class="card-note">Dept 10 vetoes any figure that has not cleared its guard</span></div>
  <table><tr><th>ID</th><th class="num">Dept</th><th>Defect</th><th>Guard</th><th>Severity</th><th>Status</th></tr>
  {_defects_rows()}</table>
</section>
<section class="card" id="decisions"><div class="card-h"><h2>Open decisions — escalate, never resolve alone</h2>
  <span class="card-note">owner / CA sign-off required</span></div>
  <table><tr><th>ID</th><th class="num">Dept</th><th>Decision</th><th>Owner</th></tr>{_decisions_rows()}</table>
</section>"""


# --------------------------------------------------------------------------
# Per-FY fragments
# --------------------------------------------------------------------------

def _kpi_html(fin: FYFinancials) -> str:
    p, s, t = fin.purchase, fin.sales, fin.tax
    kpis = [
        ("Revenue (FY)", _money(fin.revenue), "audited / live turnover"),
        ("Profit / (Loss)", _money(fin.pat), "after tax"),
        ("Sales invoices", _int(s.invoices), "date-derived, outward"),
        ("Net Payable — vendors", _money(p.net_payable), "after commission, TDS, IGST"),
        ("Outstanding to vendors", _money(p.outstanding), "recomputed, ₹1 floor"),
        ("TDS credited (26AS)", _money(t.tds_26as), "annual information statement"),
    ]
    return "".join(
        f"<div class='kpi'><div class='kpi-label'>{_esc(k)}</div>"
        f"<div class='kpi-value'>{v}</div><div class='kpi-sub'>{_esc(sub)}</div></div>"
        for k, v, sub in kpis)


def _flags_html(fin: FYFinancials, fy: str) -> str:
    if not fin.flags:
        return ""
    items = "".join(f"<li>{_esc(f)}</li>" for f in fin.flags)
    return (f"<section class='card flags-card'><div class='card-h'><h2>Flagged for FY {_esc(fy)}</h2>"
            "<span class='card-note'>contradictions &amp; caveats — surfaced, not resolved</span></div>"
            f"<ul class='flags'>{items}</ul></section>")


def _vendor_rows(p) -> str:
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


def _gst_rows(fin: FYFinancials) -> str:
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


def _bank_rows(fin: FYFinancials) -> str:
    if not fin.bank:
        return "<tr><td colspan='4' class='empty'>Bank rows load after the treasury source is connected</td></tr>"
    return "".join(
        f"<tr><td>{_esc(b.bank)}</td><td class='num'>{_money(b.debit)}</td>"
        f"<td class='num'>{_money(b.credit)}</td>"
        f"<td class='num'>{_int(b.excluded_rows)}</td></tr>"
        for b in fin.bank)


def _fy_panel(fin: FYFinancials, fy: str) -> str:
    """Everything that changes per FY: KPIs, flags, and the department cards."""
    p, s, t = fin.purchase, fin.sales, fin.tax
    return f"""
<section class="kpis" data-sec="overview">{_kpi_html(fin)}</section>
{_flags_html(fin, fy)}
<section class="card" data-sec="vendor"><div class="card-h"><h2>Vendor / Workshop Settlement — Net Payable</h2>
  <span class="card-note">Dept 2 · the confirmed formula, tying to the register</span></div>
  {_waterfall(p)}
  <table class="mt"><tr><th>Line</th><th class="num">FY {_esc(fy)}</th></tr>{_vendor_rows(p)}</table>
  <p class="dim mt-s">Rows: {_int(p.rows)} · zero-commission rows (Q3): {_int(p.zero_commission_rows)}</p>
</section>
<div class="grid2">
  <section class="card" data-sec="sales"><div class="card-h"><h2>Sales / Client Billing</h2>
    <span class="card-note">Dept 1 · outward</span></div>
    <table>
      <tr><td>Invoices</td><td class="num">{_int(s.invoices)}</td></tr>
      <tr><td>Total sales (from Date, not the FY column)</td><td class="num">{_money(s.total_sales)}</td></tr>
      <tr><td>Receivable</td><td class="num">{_money(s.receivable)}</td></tr>
    </table>
    <p class="dim mt-s">FY is derived from the invoice Date — the ledger's
      <code>Financial Year</code> column is the invoice prefix and misallocates ₹2.96 Cr.</p>
  </section>
  <section class="card" data-sec="tax"><div class="card-h"><h2>Direct Tax / TDS</h2>
    <span class="card-note">Dept 5</span></div>
    <table>
      <tr><td>TDS credited (26AS)</td><td class="num">{_money(t.tds_26as)}</td></tr>
      <tr><td>ITR status</td><td class="num">{_text(t.itr_status)}</td></tr>
    </table>
    <p class="dim mt-s">2% deduction → 26Q → challans → 26AS → ITR. No ITR filed for AY2024-25 / AY2025-26.</p>
  </section>
</div>
<section class="card" data-sec="gst"><div class="card-h"><h2>GST Cockpit — three GSTINs (R1 / 2B / 3B)</h2>
  <span class="card-note">Dept 4 · deduction triggers on 3B discharge, never 2B presence</span></div>
  <table><tr><th>GSTIN</th><th class="num">R1 taxable</th><th class="num">Output tax</th>
  <th class="num">ITC (2B)</th><th>3B filed</th><th class="num">Vendor 3B defaults</th></tr>
  {_gst_rows(fin)}</table>
  <p class="dim mt-s">2B proves declaration, 3B proves discharge. Hold back the GST component until the vendor's 3B is confirmed filed.</p>
</section>
<section class="card" data-sec="treasury"><div class="card-h"><h2>Treasury / Banking</h2>
  <span class="card-note">Dept 3 · company funds vs director-personal, kept separate</span></div>
  <table><tr><th>Bank</th><th class="num">Debit</th><th class="num">Credit</th>
  <th class="num">Excluded (re-dated)</th></tr>{_bank_rows(fin)}</table>
  <p class="dim mt-s">Skip <code>TOTAL</code> rows; the FY25-26 ICICI re-dated block is quarantined (D6).</p>
</section>"""


_STYLE = """
  :root {
    --cream:#F5EEDF; --cream-2:#FBF6EC; --paper:#FFFDF9;
    --espresso:#1C1509; --espresso-2:#2A2012; --espresso-3:#372B18;
    --ink:#241B10; --ink-2:#4A3D28; --dim:#8A7A5C; --line:#E7DDC7; --line-2:#EFE7D6;
    --navy:#0A3D62; --navy-2:#0E4E7D; --navy-soft:rgba(10,61,98,.10);
    --amber:#FFC312; --gold-1:#E7B24A; --gold-2:#B4772C;
    --ok:#2E7D46; --ok-bg:#E4EFE2; --warn:#9A5B12; --warn-bg:#F6E9CF;
    --bad:#A5372B; --bad-bg:#F3DED9; --rail-w:250px;
  }
  * { box-sizing:border-box; margin:0; }
  html { scroll-behavior:smooth; }
  body { background:var(--cream); color:var(--ink);
         font:14.5px/1.6 'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
         -webkit-font-smoothing:antialiased; display:flex; min-height:100vh; }
  .serif { font-family:'Fraunces','Georgia','Times New Roman',serif; }
  .num, .kpi-value, tr.tot td, .mono, .bar-val, .axis, .chip-pos, .chip-neg {
    font-variant-numeric:tabular-nums lining-nums; }

  /* ---- rail ---- */
  .rail { width:var(--rail-w); flex:0 0 var(--rail-w); background:var(--espresso);
          color:#EFE6D2; position:sticky; top:0; align-self:flex-start; height:100vh;
          display:flex; flex-direction:column; padding:22px 0; overflow-y:auto; }
  .brand { display:flex; align-items:center; gap:11px; padding:0 22px 20px;
           border-bottom:1px solid rgba(255,255,255,.08); }
  .brand .mark { width:26px; height:26px; flex:0 0 26px; transform:rotate(45deg);
                 background:linear-gradient(150deg,var(--amber),var(--gold-2));
                 border-radius:6px; box-shadow:0 0 0 4px rgba(255,195,18,.12); }
  .brand .wm { display:block; font-family:'Fraunces',serif; font-weight:700; font-size:18px;
               letter-spacing:.01em; color:#FBF6EC; line-height:1.05; }
  .brand .wm b { color:var(--amber); font-weight:700; }
  .brand .subwm { display:block; font-size:10px; letter-spacing:.14em; text-transform:uppercase;
                  color:#A99B7C; margin-top:3px; }
  .nav { padding:14px 12px; display:flex; flex-direction:column; gap:2px; }
  .nav .grp { font-size:10px; letter-spacing:.16em; text-transform:uppercase;
              color:#8C7D5E; padding:14px 12px 6px; }
  .nav a { display:flex; align-items:center; gap:10px; color:#D9CEB4; text-decoration:none;
           padding:8px 12px; border-radius:8px; font-size:13.5px; cursor:pointer;
           border-left:3px solid transparent; transition:background .12s,color .12s; }
  .nav a:hover { background:var(--espresso-2); color:#FBF6EC; }
  .nav a.on { background:var(--espresso-2); color:#FBF6EC; border-left-color:var(--amber); }
  .nav a .dot { width:6px; height:6px; border-radius:50%; background:#6E6045; flex:0 0 6px; }
  .nav a:hover .dot, .nav a.on .dot { background:var(--amber); }
  .rail-foot { margin-top:auto; padding:14px 22px 4px; border-top:1px solid rgba(255,255,255,.08);
               font-size:11.5px; color:#A99B7C; }
  .rail-foot .src { margin-top:6px; color:#8C7D5E; line-height:1.45; }

  /* ---- fy picker (rail) ---- */
  .fybox { padding:6px 18px 12px; }
  .fybox label { font-size:10px; letter-spacing:.14em; text-transform:uppercase;
                 color:#8C7D5E; display:block; margin-bottom:6px; }
  .fybox select { width:100%; background:var(--espresso-2); color:#FBF6EC;
                  border:1px solid rgba(255,255,255,.14); border-radius:8px;
                  padding:8px 10px; font-size:13px; font-family:inherit; }

  /* ---- content ---- */
  .content { flex:1 1 auto; min-width:0; padding:26px 30px 60px; max-width:1180px; }
  .topbar { display:flex; justify-content:space-between; align-items:flex-start;
            gap:16px; flex-wrap:wrap; margin-bottom:14px; }
  h1 { font-family:'Fraunces',serif; font-size:27px; font-weight:600;
       letter-spacing:-.01em; color:var(--navy); line-height:1.12; }
  h1 .accent { color:var(--gold-2); }
  .meta { color:var(--ink-2); font-size:12.5px; margin-top:7px; max-width:70ch; }
  .meta b { color:var(--ink); font-weight:600; }
  .statusline { text-align:right; font-size:12px; color:var(--dim); }
  .statusline .gen { margin-top:6px; }

  h2 { font-family:'Fraunces',serif; font-size:17px; font-weight:600; color:var(--ink);
       letter-spacing:-.005em; }
  .card-h { display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; margin-bottom:12px; }
  .card-note { font-size:11.5px; letter-spacing:.02em; color:var(--dim); }

  .banner { background:linear-gradient(180deg,#FBF6EC,#F6EEDD); border:1px solid var(--line);
            border-left:4px solid var(--navy); color:var(--ink-2); border-radius:12px;
            padding:13px 16px; margin-bottom:22px; font-size:12.5px; line-height:1.55; }
  .banner b { color:var(--navy); }

  .kpis { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
          gap:14px; margin-bottom:22px; }
  .kpi { background:var(--paper); border:1px solid var(--line); border-radius:13px;
         padding:16px 17px; position:relative; overflow:hidden;
         box-shadow:0 1px 2px rgba(28,21,9,.04); }
  .kpi::before { content:""; position:absolute; left:0; top:0; bottom:0; width:3px;
                 background:linear-gradient(180deg,var(--amber),var(--gold-2)); }
  .kpi:nth-child(4n+1)::before { background:linear-gradient(180deg,var(--navy),var(--navy-2)); }
  .kpi-label { color:var(--dim); font-size:11px; letter-spacing:.06em;
               text-transform:uppercase; font-weight:600; }
  .kpi-value { font-family:'Fraunces',serif; font-size:25px; font-weight:600;
               color:var(--ink); margin-top:8px; letter-spacing:-.01em; line-height:1.1; }
  .kpi-sub { color:var(--dim); font-size:11px; margin-top:5px; }

  .card { background:var(--paper); border:1px solid var(--line); border-radius:14px;
          padding:20px 22px; margin-bottom:22px; overflow-x:auto;
          box-shadow:0 1px 2px rgba(28,21,9,.04); }
  .flags-card { border-left:4px solid var(--warn); background:linear-gradient(180deg,#FBF6EC,var(--paper)); }

  table { border-collapse:collapse; width:100%; }
  .mt { margin-top:14px; } .mt-s { margin-top:10px; }
  th,td { text-align:left; padding:8px 11px; border-bottom:1px solid var(--line-2);
          white-space:nowrap; vertical-align:top; font-size:13px; }
  th { color:var(--dim); font-weight:600; font-size:10.5px; letter-spacing:.07em;
       text-transform:uppercase; border-bottom:1.5px solid var(--line); }
  td.dim,.dim { color:var(--ink-2); white-space:normal; }
  .num { text-align:right; font-variant-numeric:tabular-nums; }
  .empty { color:var(--dim); text-align:center; font-style:italic; }
  tr.sub td:first-child { padding-left:24px; color:var(--ink-2); }
  tr.tot td { font-weight:700; color:var(--ink); border-top:1.5px solid var(--gold-2);
              border-bottom:none; background:rgba(255,195,18,.06); }
  code { font-family:'IBM Plex Mono',ui-monospace,monospace; font-size:12px;
         background:var(--cream); padding:1px 5px; border-radius:5px; color:var(--ink-2); }
  .await { color:var(--dim); font-style:italic; font-size:12.5px; }

  .flags { margin:0; padding-left:18px; }
  .flags li { margin:7px 0; color:var(--ink-2); white-space:normal; line-height:1.5; }
  .flags li::marker { color:var(--warn); }

  .pill { padding:2px 9px; border-radius:99px; font-size:11px; font-weight:600;
          letter-spacing:.02em; white-space:nowrap; display:inline-block; }
  .pill.ok { background:var(--ok-bg); color:var(--ok); }
  .pill.warn { background:var(--warn-bg); color:var(--warn); }
  .pill.bad { background:var(--bad-bg); color:var(--bad); }
  .pill.brand { background:var(--navy-soft); color:var(--navy); }

  .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:22px; }

  /* ---- charts ---- */
  .chart-wrap { width:100%; }
  .chart { width:100%; height:auto; display:block; }
  .chart .grid { stroke:var(--line); stroke-width:1; }
  .chart .axis { fill:var(--dim); font-size:11px; }
  .chart .axis.fy { fill:var(--ink); font-weight:600; font-size:12px; }
  .chart .axis.wf { fill:var(--ink-2); font-size:10.5px; }
  .chart .axis-dim { fill:var(--dim); font-size:10.5px; }
  .chart .await-sm { fill:var(--dim); font-size:10.5px; font-style:italic; }
  .chart .bar-val { fill:var(--ink); font-size:11px; font-weight:600; }
  .chart .bar-rev { fill:url(#gold); }
  .chart .bar-base { fill:url(#gold); }
  .chart .bar-minus { fill:#D9BFA0; }
  .chart .bar-total { fill:var(--navy); }
  .chart .wf-conn { stroke:#C9B892; stroke-width:1; stroke-dasharray:3 3; }
  .chart .chip-pos { fill:var(--navy); font-size:11px; font-weight:700; }
  .chart .chip-neg { fill:var(--bad); font-size:11px; font-weight:700; }
  .chart-legend { display:flex; gap:18px; flex-wrap:wrap; margin-top:10px;
                  font-size:11.5px; color:var(--ink-2); }
  .chart-legend .sw { width:11px; height:11px; border-radius:3px; display:inline-block;
                      margin-right:6px; vertical-align:-1px; }
  .sw-rev { background:linear-gradient(180deg,var(--gold-1),var(--gold-2)); }
  .sw-pat { background:var(--navy); border-radius:50%!important; }
  .sw-minus { background:#D9BFA0; }
  .sw-navy { background:var(--navy); }

  .fy-panel.hidden { display:none; }

  @media (max-width:1000px) {
    body { display:block; }
    .rail { width:auto; height:auto; position:static; flex-direction:column; }
    .nav { flex-flow:row wrap; }
    .nav .grp { width:100%; padding:8px 12px 2px; }
    .rail-foot { margin-top:12px; }
    .content { padding:22px 18px 48px; max-width:none; }
    .grid2 { grid-template-columns:1fr; }
  }
"""


def _nav(*, static: bool) -> str:
    groups = [
        ("Overview", [("Snapshot", "overview", "on"), ("Five-year trend", "#trend", "")]),
        ("Ledgers", [("Vendor settlement", "vendor", ""), ("Sales & billing", "sales", ""),
                     ("GST cockpit", "gst", ""), ("Treasury", "treasury", ""),
                     ("Direct tax", "tax", "")]),
        ("Governance", [("Departments", "#departments", ""), ("Internal audit", "#audit", ""),
                        ("Open decisions", "#decisions", "")]),
    ]
    out = []
    for title, items in groups:
        out.append(f"<div class='grp'>{title}</div>")
        for label, target, on in items:
            out.append(f"<a class='{on}' onclick=\"goto('{target}',this)\">"
                       f"<span class='dot'></span>{label}</a>")
    return "".join(out)


def _rail(*, fy_select: str, conn_pill: str, source_label: str) -> str:
    return f"""<aside class="rail">
  <div class="brand">
    <span class="mark"></span>
    <span><span class="wm">GO4<b>GARAGE</b></span><span class="subwm">Financial Controller</span></span>
  </div>
  <div class="fybox"><label>Financial year</label>{fy_select}</div>
  <nav class="nav">{_nav(static=True)}</nav>
  <div class="rail-foot">{conn_pill}<div class="src">{_esc(source_label)}</div></div>
</aside>"""


def _shell(title: str, rail: str, topbar: str, body: str, script: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap">
<style>{_STYLE}</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <linearGradient id="gold" x1="0" x2="0" y1="0" y2="1">
    <stop offset="0" stop-color="#E7B24A"/><stop offset="1" stop-color="#B4772C"/></linearGradient>
</defs></svg>
{rail}
<main class="content">
{topbar}
{_banner()}
{body}
</main>
<script>
function goto(target, el){{
  var t;
  if (target.charAt(0) === '#') {{ t = document.querySelector(target); }}
  else {{
    var vis = document.querySelector('.fy-panel:not(.hidden)') || document;
    t = vis.querySelector('[data-sec="'+target+'"]');
  }}
  if (t) t.scrollIntoView({{behavior:'smooth', block:'start'}});
  if (el) {{ document.querySelectorAll('.nav a').forEach(function(a){{a.classList.remove('on');}}); el.classList.add('on'); }}
}}
{script}
</body></html>"""


def _topbar(*, fy: str, conn_pill: str, source_label: str, today: date) -> str:
    return f"""<div class="topbar">
  <div>
    <h1>{_esc(_model.ENTITY['name'])} <span class="accent">·</span> Financial Controller</h1>
    <p class="meta"><b>CIN</b> {_esc(_model.ENTITY['cin'])} · <b>PAN</b> {_esc(_model.ENTITY['pan'])} ·
      <b>GSTINs</b> {_gstins()}</p>
  </div>
  <div class="statusline">{conn_pill}<div class="gen"><span id="fylabel">FY {_esc(fy)}</span> ·
      generated {today.isoformat()}</div>
    <div class="gen dim" style="max-width:26ch">{_esc(source_label)}</div></div>
</div>"""


def render_fy(provider: FinancialDataProvider, fy: str, *, today: date | None = None) -> str:
    """One FY, served by the backend; the dropdown navigates by ?fy=."""
    today = today or date.today()
    fys = [m.fy for m in _model.FINANCIAL_YEARS]
    if fy not in fys:
        fy = fys[-1]
    fin = provider.fy_financials(fy)
    summaries = _summaries(provider)

    conn_pill = ("<span class='pill ok'>connected</span>" if provider.connected()
                 else "<span class='pill warn'>not connected</span>")
    options = "".join(
        f"<option value='{_esc(m.fy)}'{' selected' if m.fy == fy else ''}>"
        f"{_esc(m.fy)} · {_esc(m.audit_status.replace('_', ' ').title())}</option>"
        for m in _model.FINANCIAL_YEARS)
    fy_select = f"<select onchange=\"location.href='?fy='+this.value\">{options}</select>"

    rail = _rail(fy_select=fy_select, conn_pill=conn_pill, source_label=provider.source_label())
    topbar = _topbar(fy=fy, conn_pill=conn_pill, source_label=provider.source_label(), today=today)
    body = (f"<div class='fy-panel' data-fy='{_esc(fy)}'>{_fy_panel(fin, fy)}</div>"
            + _reference_cards(summaries))
    return _shell(f"Go4Garage · Financial Controller · FY {fy}", rail, topbar, body)


def render_static(provider: FinancialDataProvider, *, today: date | None = None,
                  default_fy: str = "2023-24") -> str:
    """All five FYs baked into one self-contained page, switched client-side.

    No backend needed — suitable for publishing as a standalone artifact.
    """
    today = today or date.today()
    fys = [m.fy for m in _model.FINANCIAL_YEARS]
    if default_fy not in fys:
        default_fy = fys[-1]
    summaries = _summaries(provider)

    conn_pill = ("<span class='pill ok'>connected</span>" if provider.connected()
                 else "<span class='pill warn'>not connected</span>")
    options = "".join(
        f"<option value='{_esc(m.fy)}'{' selected' if m.fy == default_fy else ''}>"
        f"{_esc(m.fy)} · {_esc(m.audit_status.replace('_', ' ').title())}</option>"
        for m in _model.FINANCIAL_YEARS)
    fy_select = f"<select id='fysel' onchange='showFy(this.value)'>{options}</select>"

    rail = _rail(fy_select=fy_select, conn_pill=conn_pill, source_label=provider.source_label())
    topbar = _topbar(fy=default_fy, conn_pill=conn_pill, source_label=provider.source_label(), today=today)

    panels = "".join(
        f"<div class='fy-panel{'' if fy == default_fy else ' hidden'}' data-fy='{_esc(fy)}'>"
        f"{_fy_panel(provider.fy_financials(fy), fy)}</div>"
        for fy in fys)
    body = panels + _reference_cards(summaries)
    script = """
function showFy(fy){
  document.querySelectorAll('.fy-panel').forEach(function(p){
    p.classList.toggle('hidden', p.dataset.fy !== fy);
  });
  var l = document.getElementById('fylabel');
  if (l) l.textContent = 'FY ' + fy;
}
document.addEventListener('DOMContentLoaded', function(){
  showFy(document.getElementById('fysel').value);
});
"""
    return _shell("Go4Garage · Financial Controller", rail, topbar, body, script)
