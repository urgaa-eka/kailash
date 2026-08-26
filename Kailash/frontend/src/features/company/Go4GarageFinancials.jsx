import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getOverview, getFy, fetchExportCsv,
  getSession, onAuthChange, signIn, signOut,
} from './go4garageApi';
import { supabaseConfigured } from './supabaseClient';
import './Go4GarageFinancials.css';

/* =========================================================================
   Go4Garage Financial Controller — enterprise FY financial dashboard.
   Automobile-focused, "Eames" identity, GO4GARAGE brand colours. Consumes the
   company JSON API, whose payloads carry the store's key shape, so anything
   shown here maps 1:1 into the store and onward to Zoho Books.
   ========================================================================= */

// ---- formatting (mirrors app/go4garage/dashboard.py) ----------------------
const numOf = (v) => {
  if (v === null || v === undefined || v === '') return null;
  const n = Number(v);
  return Number.isNaN(n) ? null : n;
};
const inr = (x, d = 2) =>
  x.toLocaleString('en-IN', { minimumFractionDigits: d, maximumFractionDigits: d });

function money(v) {
  const n = numOf(v);
  if (n === null) return null;
  const sign = n < 0 ? '-' : '';
  const a = Math.abs(n);
  if (a >= 1e7) return `${sign}₹${inr(a / 1e7)} Cr`;
  if (a >= 1e5) return `${sign}₹${inr(a / 1e5)} L`;
  return `${sign}₹${inr(a)}`;
}
function compact(v) {
  const n = numOf(v);
  if (n === null) return '—';
  const sign = n < 0 ? '-' : '';
  const a = Math.abs(n);
  if (a >= 1e7) return `${sign}₹${inr(a / 1e7)}Cr`;
  if (a >= 1e5) return `${sign}₹${inr(a / 1e5, 1)}L`;
  if (a >= 1e3) return `${sign}₹${inr(a / 1e3, 0)}k`;
  return `${sign}₹${inr(a, 0)}`;
}
const intFmt = (v) =>
  v === null || v === undefined ? null : Number(v).toLocaleString('en-IN');

const Await = () => <span className="await">awaiting source</span>;
const Money = ({ v }) => { const s = money(v); return s === null ? <Await /> : <>{s}</>; };
const Int = ({ v }) => { const s = intFmt(v); return s === null ? <Await /> : <>{s}</>; };
const Text = ({ v }) => (v === null || v === undefined || v === '' ? <Await /> : <>{v}</>);

const AUDIT_CLS = { AUDITED_SIGNED: 'ok', AUDITED_QUALIFIED: 'warn', UNAUDITED: 'warn', NONE: 'bad' };
const SEV_CLS = { material: 'bad', major: 'warn', minor: 'ok' };
const STATUS_CLS = { open: 'bad', mitigated: 'warn', fixed: 'ok', withdrawn: 'ok' };
const titleCase = (s) => (s || '').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

const Pill = ({ kind, children }) => <span className={`pill ${kind || ''}`}>{children}</span>;

// ---- client-side file download (works in the deployed app, not a sandbox) --
function downloadBlob(filename, text, mime = 'text/plain') {
  const blob = new Blob([text], { type: `${mime};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ---- Net Payable waterfall (SVG) ------------------------------------------
function Waterfall({ purchase, rates }) {
  const approved = numOf(purchase.approved);
  if (!approved || approved <= 0)
    return <p className="await">waterfall loads once the vendor register is connected</p>;
  const comm = numOf(purchase.commission) || 0;
  const tds = numOf(purchase.tds) || 0;
  const igst = numOf(purchase.igst_deducted) || 0;
  const net = numOf(purchase.net_payable) ?? approved - comm - tds - igst;
  const commPct = Math.round((numOf(rates?.commission) ?? 0.15) * 100);
  const tdsPct = ((numOf(rates?.tds) ?? 0.02) * 100).toFixed(1);

  const steps = [
    ['Approved', 'base', approved],
    [`−Commission ${commPct}%`, 'minus', comm],
    [`−TDS ${tdsPct}%`, 'minus', tds],
  ];
  if (igst > 0) steps.push(['−IGST', 'minus', igst]);
  steps.push(['Net Payable', 'total', net]);
  const paid = numOf(purchase.paid);
  const out = numOf(purchase.outstanding);
  if (paid) steps.push(['−Paid', 'minus', paid]);
  if (out !== null) steps.push(['Outstanding', 'total', out]);

  const W = 720, H = 280, padL = 54, padR = 16, padT = 20, padB = 54;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  const slot = plotW / steps.length, bw = Math.min(74, slot * 0.62), vmax = approved * 1.06;
  const y = (v) => padT + plotH - (v / vmax) * plotH;

  const grid = [];
  for (let i = 0; i < 4; i++) {
    const gv = (vmax * i) / 3, gy = y(gv);
    grid.push(<line key={`g${i}`} className="grid" x1={padL} y1={gy} x2={W - padR} y2={gy} />);
    grid.push(<text key={`gt${i}`} className="axis" x={padL - 8} y={gy + 3} textAnchor="end">{compact(gv)}</text>);
  }

  const bars = [], labels = [], conns = [];
  let running = approved, prevX2 = null;
  steps.forEach(([label, kind, val], i) => {
    const cx = padL + slot * i + slot / 2, x1 = cx - bw / 2;
    let top, bot, cls;
    if (kind === 'base') { top = val; bot = 0; running = val; cls = 'bar-base'; }
    else if (kind === 'minus') { top = running; bot = running - val; running -= val; cls = 'bar-minus'; }
    else { top = val; bot = 0; running = val; cls = 'bar-total'; }
    const yt = y(top), yb = y(bot), h = Math.max(1.6, yb - yt);
    bars.push(<rect key={`b${i}`} className={cls} x={x1} y={yt} width={bw} height={h} rx="3" />);
    const vlabel = kind === 'minus' ? `−${compact(val)}` : compact(val);
    bars.push(<text key={`bv${i}`} className="bar-val" x={cx} y={yt - 6} textAnchor="middle">{vlabel}</text>);
    labels.push(<text key={`l${i}`} className="axis wf" x={cx} y={H - padB + 18} textAnchor="middle">{label}</text>);
    if (prevX2 !== null) {
      const ly = y(kind === 'minus' ? top : running);
      conns.push(<line key={`c${i}`} className="wf-conn" x1={prevX2} y1={ly} x2={x1} y2={ly} />);
    }
    prevX2 = cx + bw / 2;
  });

  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${W} ${H}`} className="chart" role="img" aria-label="Net Payable waterfall" preserveAspectRatio="xMinYMin meet">
        {grid}{conns}{bars}{labels}
      </svg>
      <div className="chart-legend">
        <span><i className="sw sw-rev" />Vendor-facing / net</span>
        <span><i className="sw sw-minus" />Statutory &amp; commission deductions</span>
        <span><i className="sw sw-navy" />Net Payable</span>
      </div>
    </div>
  );
}

// ---- five-year revenue trend (SVG) ----------------------------------------
function TrendChart({ trend }) {
  const revs = trend.map((s) => numOf(s.revenue));
  const have = revs.filter((r) => r !== null);
  if (!have.length)
    return <p className="await">five-year trend loads once an audited/live source is connected</p>;
  const vmax = Math.max(...have) || 1;
  const n = trend.length;
  const W = 720, H = 260, padL = 54, padR = 16, padT = 26, padB = 58;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  const slot = plotW / n, bw = Math.min(64, slot * 0.5);

  const grid = [];
  for (let i = 0; i < 5; i++) {
    const gv = (vmax * i) / 4, gy = padT + plotH - (gv / vmax) * plotH;
    grid.push(<line key={`g${i}`} className="grid" x1={padL} y1={gy} x2={W - padR} y2={gy} />);
    grid.push(<text key={`gt${i}`} className="axis" x={padL - 8} y={gy + 3} textAnchor="end">{compact(gv)}</text>);
  }

  const bars = [], labels = [], chips = [];
  trend.forEach((s, i) => {
    const cx = padL + slot * i + slot / 2, r = numOf(s.revenue);
    if (r !== null && r > 0) {
      const bh = (r / vmax) * plotH, by = padT + plotH - bh;
      bars.push(<rect key={`b${i}`} className="bar-rev" x={cx - bw / 2} y={by} width={bw} height={bh} rx="3" />);
      bars.push(<text key={`bv${i}`} className="bar-val" x={cx} y={by - 6} textAnchor="middle">{compact(r)}</text>);
    } else {
      bars.push(<text key={`na${i}`} className="await-sm" x={cx} y={padT + plotH - 6} textAnchor="middle">no audit</text>);
    }
    labels.push(<text key={`l${i}`} className="axis fy" x={cx} y={H - padB + 20} textAnchor="middle">{s.fy}</text>);
    const pat = numOf(s.pat);
    if (pat !== null)
      chips.push(<text key={`p${i}`} className={pat >= 0 ? 'chip-pos' : 'chip-neg'} x={cx} y={H - padB + 38} textAnchor="middle">{compact(pat)}</text>);
    else
      chips.push(<text key={`p${i}`} className="axis-dim" x={cx} y={H - padB + 38} textAnchor="middle">PAT —</text>);
  });

  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${W} ${H}`} className="chart" role="img" aria-label="Five-year revenue and profit trend" preserveAspectRatio="xMinYMin meet">
        {grid}{bars}{labels}{chips}
      </svg>
      <div className="chart-legend">
        <span><i className="sw sw-rev" />Revenue (bars)</span>
        <span><i className="sw sw-pat" />Profit / (loss) after tax — per year</span>
      </div>
    </div>
  );
}

// ---- nav spine ------------------------------------------------------------
const NAV = [
  ['Overview', [['Snapshot', 'overview'], ['Five-year trend', 'trend']]],
  ['Ledgers', [['Vendor settlement', 'vendor'], ['Sales & billing', 'sales'],
    ['GST cockpit', 'gst'], ['Treasury', 'treasury'], ['Direct tax', 'tax']]],
  ['Governance', [['Departments', 'departments'], ['Internal audit', 'audit'],
    ['Open decisions', 'decisions']]],
];

// ---- page -----------------------------------------------------------------
// Supabase Auth gate — the confidential figures load only after sign-in (RLS).
function LoginGate({ onSignedIn }) {
  const [email, setEmail] = useState('');
  const [pw, setPw] = useState('');
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setErr(null);
    try {
      const session = await signIn(email.trim(), pw);
      onSignedIn(session);
    } catch {
      setErr('Sign-in failed — check your email and password.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="g4g">
      <div className="auth-wrap">
        <form className="auth-card" onSubmit={submit}>
          <div className="auth-brand">GO4GARAGE</div>
          <h1 className="auth-title">Financial Controller</h1>
          <p className="auth-sub">Sign in to view the confidential FY dashboard.</p>
          <label className="auth-label">Email
            <input className="auth-input" type="email" autoComplete="username" value={email}
              onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label className="auth-label">Password
            <input className="auth-input" type="password" autoComplete="current-password" value={pw}
              onChange={(e) => setPw(e.target.value)} required />
          </label>
          {err && <div className="auth-err">{err}</div>}
          <button className="auth-btn" type="submit" disabled={busy}>
            {busy ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function Go4GarageFinancials() {
  const navigate = useNavigate();
  const [session, setSession] = useState(undefined); // undefined=checking, null=out, obj=in
  const [overview, setOverview] = useState(null);
  const [fy, setFy] = useState(null);
  const [fyData, setFyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fyLoading, setFyLoading] = useState(false);
  const [error, setError] = useState(null);
  const [active, setActive] = useState('overview');
  const [exporting, setExporting] = useState(false);

  // Track the Supabase session (and react to sign-in / sign-out / refresh).
  useEffect(() => {
    getSession().then(setSession);
    return onAuthChange(setSession);
  }, []);

  const doSignOut = async () => {
    await signOut();
    setSession(null);
    setOverview(null);
    setFyData(null);
  };

  const pickDefaultFy = (years) => {
    const has = years.find((y) => y.fy === '2023-24');
    return has ? '2023-24' : years[years.length - 1]?.fy;
  };

  const loadFy = useCallback(async (year) => {
    setFyLoading(true);
    try {
      const d = await getFy(year);
      setFyData(d);
      setFy(year);
      setError(null);
    } catch (e) {
      setError('Could not load the figures for this year.');
    } finally {
      setFyLoading(false);
    }
  }, []);

  const boot = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const ov = await getOverview();
      setOverview(ov);
      const def = pickDefaultFy(ov.financial_years || []);
      await loadFy(def);
    } catch (e) {
      setError('The financial service is unreachable. Check the connection and retry.');
    } finally {
      setLoading(false);
    }
  }, [loadFy]);

  useEffect(() => { if (session) boot(); }, [session, boot]);

  const goto = (id) => {
    setActive(id);
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  // The store-ready payload for this FY — re-importable via POST /go4garage/fy/{fy}.
  const exportFyJson = () => {
    if (!fyData) return;
    downloadBlob(`go4garage_${fy}.json`, JSON.stringify(fyData, null, 2), 'application/json');
  };

  // All five FYs as one flat CSV (store column shape) for Zoho column-mapping.
  const exportAllCsv = async () => {
    setExporting(true);
    try {
      const csv = await fetchExportCsv();
      downloadBlob('go4garage_fy_export.csv', csv, 'text/csv');
    } catch (e) {
      setError('Could not download the export. Check the connection and retry.');
    } finally {
      setExporting(false);
    }
  };

  const connPill = useMemo(() => {
    const p = overview?.provider;
    if (!p) return null;
    return <Pill kind={p.connected ? 'ok' : 'warn'}>{p.connected ? 'connected' : 'not connected'}</Pill>;
  }, [overview]);

  if (!supabaseConfigured)
    return (
      <div className="g4g"><div className="state">
        <h2>Not configured</h2>
        <p>Supabase is not configured for this build (REACT_APP_SUPABASE_URL / _ANON_KEY).</p>
      </div></div>
    );

  if (session === undefined)
    return (
      <div className="g4g"><div className="state"><div className="spinner" />
        <div>Checking your session…</div></div></div>
    );

  if (session === null) return <LoginGate onSignedIn={setSession} />;

  if (loading)
    return (
      <div className="g4g"><div className="state"><div className="spinner" />
        <div>Loading GO4GARAGE financials…</div></div></div>
    );

  if (error && !overview)
    return (
      <div className="g4g"><div className="state">
        <h2>Financials unavailable</h2><p>{error}</p>
        <button className="retry" onClick={boot}>Retry</button>
      </div></div>
    );

  const ent = overview.entity || {};
  const gstinLabel = (overview.gstins || []).map((g) => `${g.gstin} (${g.state})`).join(' · ');
  const d = fyData || {};
  const p = d.purchase || {};
  const s = d.sales || {};
  const t = d.tax || {};

  return (
    <div className="g4g">
      <button className="signout" onClick={doSignOut} title="Sign out">Sign out</button>
      {/* one shared gold gradient for every chart */}
      <svg width="0" height="0" style={{ position: 'absolute' }} aria-hidden="true">
        <defs>
          <linearGradient id="g4gGold" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stopColor="#E7B24A" /><stop offset="1" stopColor="#B4772C" />
          </linearGradient>
        </defs>
      </svg>

      <aside className="rail">
        <div className="brand" role="button" tabIndex={0}
          onClick={() => navigate('/kailash')} onKeyDown={(e) => e.key === 'Enter' && navigate('/kailash')}>
          <span className="mark" />
          <span><span className="wm">GO4<b>GARAGE</b></span>
            <span className="subwm">Financial Controller</span></span>
        </div>

        <div className="fybox">
          <label>Financial year</label>
          <div className="fybtns">
            {(overview.financial_years || []).map((y) => (
              <button key={y.fy} className={`fybtn ${y.fy === fy ? 'on' : ''}`}
                disabled={fyLoading} onClick={() => loadFy(y.fy)} title={titleCase(y.audit_status)}>
                {y.fy}
              </button>
            ))}
          </div>
        </div>

        <div className="fybox export-box">
          <label>Export · maps to store / Zoho</label>
          <div className="fybtns">
            <button className="fybtn" onClick={exportFyJson} disabled={!fyData}
              title={`Download FY ${fy} in the store's shape (re-importable via POST /go4garage/fy/${fy})`}>
              This year · JSON
            </button>
            <button className="fybtn" onClick={exportAllCsv} disabled={exporting}
              title="Download all five FYs as one flat CSV — column-map into Zoho's importer">
              {exporting ? 'Preparing…' : 'All years · CSV'}
            </button>
          </div>
        </div>

        <nav className="nav">
          {NAV.map(([grp, items]) => (
            <React.Fragment key={grp}>
              <div className="grp">{grp}</div>
              {items.map(([label, id]) => (
                <button key={id} className={active === id ? 'on' : ''} onClick={() => goto(id)}>
                  <span className="dot" />{label}
                </button>
              ))}
            </React.Fragment>
          ))}
        </nav>

        <div className="rail-foot">
          {connPill}
          <div className="src">{overview.provider?.source_label}</div>
        </div>
      </aside>

      <main className="content">
        <div className="inner">
          <div className="topbar">
            <div>
              <h1>{ent.name} <span className="accent">·</span> Financial Controller</h1>
              <p className="meta"><b>CIN</b> {ent.cin} · <b>PAN</b> {ent.pan} · <b>GSTINs</b> {gstinLabel}</p>
            </div>
            <div className="statusline">
              {connPill}
              <div className="gen">FY {fy}{fyLoading ? ' · loading…' : ''}</div>
            </div>
          </div>

          <div className="banner">
            <b>Two approval layers, never joined.</b> Client approval drives sales only and is
            confidential to vendors; vendor approval drives purchases only. There is no per-job
            spread — margin is a P&amp;L-level figure (sales − net purchase cost).
            {overview.related_party_note ? ` Related parties: ${overview.related_party_note}` : ''}
          </div>

          {/* KPIs */}
          <section className="kpis" id="overview">
            {[
              ['Revenue (FY)', <Money v={d.revenue} />, 'audited / live turnover', true],
              ['Profit / (Loss)', <Money v={d.pat} />, 'after tax', false],
              ['Sales invoices', <Int v={s.invoices} />, 'date-derived, outward', false],
              ['Net Payable — vendors', <Money v={p.net_payable} />, 'after commission, TDS, IGST', false],
              ['Outstanding to vendors', <Money v={p.outstanding} />, 'recomputed, ₹1 floor', true],
              ['TDS credited (26AS)', <Money v={t.tds_26as} />, 'annual information statement', false],
            ].map(([label, value, sub, brand], i) => (
              <div className={`kpi ${brand ? 'kpi-navy' : ''}`} key={i}>
                <div className="kpi-label">{label}</div>
                <div className="kpi-value">{value}</div>
                <div className="kpi-sub">{sub}</div>
              </div>
            ))}
          </section>

          {/* flags */}
          {(d.flags || []).length > 0 && (
            <section className="card flags-card">
              <div className="card-h"><h2>Flagged for FY {fy}</h2>
                <span className="card-note">contradictions &amp; caveats — surfaced, not resolved</span></div>
              <ul className="flags">{d.flags.map((f, i) => <li key={i}>{f}</li>)}</ul>
            </section>
          )}

          {/* vendor settlement + waterfall */}
          <section className="card scroll" id="vendor">
            <div className="card-h"><h2>Vendor / Workshop Settlement — Net Payable</h2>
              <span className="card-note">Dept 2 · the confirmed formula, tying to the register</span></div>
            <Waterfall purchase={p} rates={overview.rates} />
            <table className="mt">
              <tbody>
                <tr><th>Line</th><th className="num">FY {fy}</th></tr>
                <tr><td>Vendor-facing approved</td><td className="num"><Money v={p.approved} /></td></tr>
                <tr className="sub"><td>less Commission ({Math.round((numOf(overview.rates?.commission) ?? 0.15) * 100)}%)</td><td className="num"><Money v={p.commission} /></td></tr>
                <tr className="sub"><td>less TDS ({((numOf(overview.rates?.tds) ?? 0.02) * 100).toFixed(1)}%)</td><td className="num"><Money v={p.tds} /></td></tr>
                <tr className="sub"><td>less IGST (only when GST 'Not Available')</td><td className="num"><Money v={p.igst_deducted} /></td></tr>
                <tr className="tot"><td>= Net Payable</td><td className="num"><Money v={p.net_payable} /></td></tr>
                <tr className="sub"><td>less Paid</td><td className="num"><Money v={p.paid} /></td></tr>
                <tr className="tot"><td>= Outstanding (recomputed, ₹1 floor)</td><td className="num"><Money v={p.outstanding} /></td></tr>
              </tbody>
            </table>
            <p className="dim mt-s">Rows: <Int v={p.rows} /> · zero-commission rows (Q3): <Int v={p.zero_commission_rows} /></p>
          </section>

          <div className="grid2">
            <section className="card scroll" id="sales">
              <div className="card-h"><h2>Sales / Client Billing</h2><span className="card-note">Dept 1 · outward</span></div>
              <table><tbody>
                <tr><td>Invoices</td><td className="num"><Int v={s.invoices} /></td></tr>
                <tr><td>Total sales (from Date, not the FY column)</td><td className="num"><Money v={s.total_sales} /></td></tr>
                <tr><td>Receivable</td><td className="num"><Money v={s.receivable} /></td></tr>
              </tbody></table>
              <p className="dim mt-s">FY is derived from the invoice Date — the ledger's <code>Financial Year</code> column is the invoice prefix and misallocates ₹2.96 Cr.</p>
            </section>

            <section className="card scroll" id="tax">
              <div className="card-h"><h2>Direct Tax / TDS</h2><span className="card-note">Dept 5</span></div>
              <table><tbody>
                <tr><td>TDS credited (26AS)</td><td className="num"><Money v={t.tds_26as} /></td></tr>
                <tr><td>ITR status</td><td className="num"><Text v={t.itr_status} /></td></tr>
              </tbody></table>
              <p className="dim mt-s">2% deduction → 26Q → challans → 26AS → ITR. No ITR filed for AY2024-25 / AY2025-26.</p>
            </section>
          </div>

          {/* GST cockpit */}
          <section className="card scroll" id="gst">
            <div className="card-h"><h2>GST Cockpit — three GSTINs (R1 / 2B / 3B)</h2>
              <span className="card-note">Dept 4 · deduction triggers on 3B discharge, never 2B presence</span></div>
            <table>
              <tbody>
                <tr><th>GSTIN</th><th className="num">R1 taxable</th><th className="num">Output tax</th>
                  <th className="num">ITC (2B)</th><th>3B filed</th><th className="num">Vendor 3B defaults</th></tr>
                {(d.gst || []).length === 0 ? (
                  <tr><td colSpan="6" className="empty">Three GSTINs configured; R1/2B/3B load after the GST source is connected</td></tr>
                ) : d.gst.map((g, i) => (
                  <tr key={i}>
                    <td>{g.gstin}</td>
                    <td className="num"><Money v={g.r1_taxable} /></td>
                    <td className="num"><Money v={g.output_tax} /></td>
                    <td className="num"><Money v={g.itc_2b} /></td>
                    <td>{g.r3b_filed === null || g.r3b_filed === undefined ? '—' : (g.r3b_filed ? <Pill kind="ok">filed</Pill> : <Pill kind="bad">not filed</Pill>)}</td>
                    <td className="num"><Int v={g.vendor_3b_defaults} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="dim mt-s">2B proves declaration, 3B proves discharge. Hold back the GST component until the vendor's 3B is confirmed filed.</p>
          </section>

          {/* treasury */}
          <section className="card scroll" id="treasury">
            <div className="card-h"><h2>Treasury / Banking</h2>
              <span className="card-note">Dept 3 · company funds vs director-personal, kept separate</span></div>
            <table>
              <tbody>
                <tr><th>Bank</th><th className="num">Debit</th><th className="num">Credit</th><th className="num">Excluded (re-dated)</th></tr>
                {(d.bank || []).length === 0 ? (
                  <tr><td colSpan="4" className="empty">Bank rows load after the treasury source is connected</td></tr>
                ) : d.bank.map((b, i) => (
                  <tr key={i}>
                    <td>{b.bank}</td>
                    <td className="num"><Money v={b.debit} /></td>
                    <td className="num"><Money v={b.credit} /></td>
                    <td className="num"><Int v={b.excluded_rows} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="dim mt-s">Skip <code>TOTAL</code> rows; the FY25-26 ICICI re-dated block is quarantined (D6).</p>
          </section>

          {/* five-year trend */}
          <section className="card scroll" id="trend">
            <div className="card-h"><h2>Five-year trend</h2>
              <span className="card-note">revenue audited where available; profit annotated per year</span></div>
            <TrendChart trend={overview.trend || []} />
            <table className="mt">
              <tbody>
                <tr><th>FY</th><th>Audit status</th><th>Posture</th><th>Note</th></tr>
                {(overview.financial_years || []).map((y) => (
                  <tr key={y.fy}>
                    <td>{y.fy}</td>
                    <td><Pill kind={AUDIT_CLS[y.audit_status]}>{titleCase(y.audit_status)}</Pill></td>
                    <td>{y.posture}</td>
                    <td className="dim">{y.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="dim mt-s">Closed years (≤ {overview.closed_year_cutoff}) are carried by summary journals in Zoho org {overview.zoho?.target_org}; never post transaction-level detail into them.</p>
          </section>

          {/* departments */}
          <section className="card scroll" id="departments">
            <div className="card-h"><h2>The ten departments</h2>
              <span className="card-note">the organising spine of the controller model</span></div>
            <table>
              <tbody>
                <tr><th className="num">#</th><th>Department</th><th>Owns</th><th>Source of truth</th></tr>
                {(overview.departments || []).map((dep) => (
                  <tr key={dep.num}>
                    <td className="num">{dep.num}</td>
                    <td>{dep.name}{dep.cross_cutting ? <> · <Pill kind="warn">veto</Pill></> : null}</td>
                    <td className="dim">{dep.owns}</td>
                    <td className="dim">{dep.source_of_truth}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          {/* internal audit */}
          <section className="card scroll" id="audit">
            <div className="card-h"><h2>Internal Audit — known defects (the veto gate)</h2>
              <span className="card-note">Dept 10 vetoes any figure that has not cleared its guard</span></div>
            <table>
              <tbody>
                <tr><th>ID</th><th className="num">Dept</th><th>Defect</th><th>Guard</th><th>Severity</th><th>Status</th></tr>
                {(overview.defects || []).map((df) => (
                  <tr key={df.id}>
                    <td>{df.id}</td><td className="num">{df.dept}</td>
                    <td>{df.title}</td><td className="dim">{df.guard}</td>
                    <td><Pill kind={SEV_CLS[df.severity]}>{df.severity}</Pill></td>
                    <td><Pill kind={STATUS_CLS[df.status]}>{df.status}</Pill></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          {/* open decisions */}
          <section className="card scroll" id="decisions">
            <div className="card-h"><h2>Open decisions — escalate, never resolve alone</h2>
              <span className="card-note">owner / CA sign-off required</span></div>
            <table>
              <tbody>
                <tr><th>ID</th><th className="num">Dept</th><th>Decision</th><th>Owner</th></tr>
                {(overview.decisions || []).map((q) => (
                  <tr key={q.id}>
                    <td>{q.id}</td><td className="num">{q.dept}</td>
                    <td>{q.question}</td><td>{q.owner}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      </main>
    </div>
  );
}
