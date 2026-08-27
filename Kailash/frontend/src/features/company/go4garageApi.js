/**
 * Go4Garage Financial Controller — data service (serverless).
 *
 * Reads the FY dashboard straight from Supabase Postgres (table
 * public.g4g_dashboard, one JSON payload per key: "overview" and "fy:<FY>"),
 * gated by Supabase Auth + Row-Level Security. No application server.
 *
 * The payloads carry the same key shape the store/Zoho mapping used, so a figure
 * shown here still maps 1:1 onto the export columns below.
 */
import { supabase } from './supabaseClient';

// ---- auth -----------------------------------------------------------------
export async function getSession() {
  const { data } = await supabase.auth.getSession();
  return data.session || null;
}

export function onAuthChange(cb) {
  const { data } = supabase.auth.onAuthStateChange((_event, session) => cb(session));
  return () => data.subscription.unsubscribe();
}

export async function signIn(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data.session;
}

export async function signOut() {
  await supabase.auth.signOut();
}

export async function updatePassword(newPassword) {
  const { error } = await supabase.auth.updateUser({ password: newPassword });
  if (error) throw error;
}

// ---- data (RLS returns rows only to the authorised, signed-in owner) -------
async function readPayload(key) {
  const { data, error } = await supabase
    .from('g4g_dashboard')
    .select('payload')
    .eq('key', key)
    .maybeSingle();
  if (error) throw error;
  if (!data) {
    // Signed in but no row visible => not authorised for these figures, or the
    // data has not been seeded. Surface a clear, non-technical message.
    throw new Error('Not authorised to view these figures, or no data has been loaded yet.');
  }
  return data.payload;
}

/** FY-independent: entity, model spine, departments, defects, decisions, trend. */
export async function getOverview() {
  return readPayload('overview');
}

/** One financial year in store shape (money as exact strings; null = awaiting). */
export async function getFy(fy) {
  return readPayload(`fy:${fy}`);
}

// ---- invoices -------------------------------------------------------------
// public.g4g_invoices carries one row per sales invoice, reconciled against the
// sales ledger. status: MATCHED | PDF_ONLY (no ledger entry) | LEDGER_ONLY (no PDF).
// Same RLS gate as the figures — an unauthorised read returns an empty list.

/** One page of invoices. `fy` / `status` / `q` are all optional filters. */
export async function getInvoices({ fy, status, q, limit = 100, offset = 0 } = {}) {
  let sel = supabase
    .from('g4g_invoices')
    .select('ref,fy,inv_date,party,amount,status,direction,file_name,storage_path,bytes', { count: 'exact' })
    .order('inv_date', { ascending: false })
    .range(offset, offset + limit - 1);
  if (fy) sel = sel.eq('fy', fy);
  if (status) sel = sel.eq('status', status);
  if (q) sel = sel.or(`ref.ilike.%${q}%,party.ilike.%${q}%`);
  const { data, error, count } = await sel;
  if (error) throw error;
  return { rows: data || [], total: count ?? 0 };
}

/** Per-FY counts and totals for the summary strip. */
export async function getInvoiceSummary() {
  const { data, error } = await supabase
    .from('g4g_invoices')
    .select('fy,status,amount');
  if (error) throw error;
  const acc = {};
  for (const r of data || []) {
    const a = (acc[r.fy] ??= { fy: r.fy, count: 0, amount: 0, matched: 0, pdf_only: 0, ledger_only: 0 });
    a.count += 1;
    a.amount += Number(r.amount || 0);
    if (r.status === 'MATCHED') a.matched += 1;
    else if (r.status === 'PDF_ONLY') a.pdf_only += 1;
    else a.ledger_only += 1;
  }
  return Object.values(acc).sort((x, y) => x.fy.localeCompare(y.fy));
}

/**
 * Short-lived signed URL for one invoice PDF. The bucket is private, so this is
 * the only way to hand the browser a downloadable link.
 */
export async function getInvoiceDownloadUrl(storagePath, fileName) {
  const { data, error } = await supabase.storage
    .from('invoices')
    .createSignedUrl(storagePath, 120, { download: fileName || true });
  if (error) throw error;
  return data.signedUrl;
}

/** Audit blockers and contradictions, rendered on the Issues board. */
export async function getIssues() {
  return readPayload('issues');
}

// ---- client-side CSV export (no server) -----------------------------------
// Column order mirrors the former api.EXPORT_FIELDS so a file taken out here is
// identical to the old server export — Zoho-mappable / store-shape.
const EXPORT_FIELDS = [
  'fy', 'audit_status', 'posture',
  'revenue', 'pat',
  'sales_invoices', 'sales_total_sales', 'sales_receivable',
  'purchase_rows', 'purchase_approved', 'purchase_commission', 'purchase_tds',
  'purchase_igst_deducted', 'purchase_net_payable', 'purchase_paid',
  'purchase_outstanding', 'purchase_zero_commission_rows',
  'tax_tds_26as', 'tax_itr_status',
];

const flat = (p) => ({
  fy: p.fy, audit_status: p.audit_status, posture: p.posture,
  revenue: p.revenue, pat: p.pat,
  sales_invoices: p.sales?.invoices, sales_total_sales: p.sales?.total_sales,
  sales_receivable: p.sales?.receivable,
  purchase_rows: p.purchase?.rows, purchase_approved: p.purchase?.approved,
  purchase_commission: p.purchase?.commission, purchase_tds: p.purchase?.tds,
  purchase_igst_deducted: p.purchase?.igst_deducted,
  purchase_net_payable: p.purchase?.net_payable, purchase_paid: p.purchase?.paid,
  purchase_outstanding: p.purchase?.outstanding,
  purchase_zero_commission_rows: p.purchase?.zero_commission_rows,
  tax_tds_26as: p.tax?.tds_26as, tax_itr_status: p.tax?.itr_status,
});

// RFC 4180: quote a field only when it contains a comma, quote or newline.
const csvCell = (v) => {
  if (v === null || v === undefined) return '';
  const s = String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

/** All FYs as flat CSV text (store column shape) — built entirely client-side. */
export async function fetchExportCsv() {
  const { data, error } = await supabase
    .from('g4g_dashboard')
    .select('key,payload')
    .like('key', 'fy:%');
  if (error) throw error;
  const rows = (data || [])
    .map((r) => flat(r.payload))
    .sort((a, b) => String(a.fy).localeCompare(String(b.fy)));
  const lines = [EXPORT_FIELDS.join(',')];
  for (const r of rows) lines.push(EXPORT_FIELDS.map((k) => csvCell(r[k])).join(','));
  return `${lines.join('\r\n')}\r\n`;
}

const go4garageApi = {
  getSession, onAuthChange, signIn, signOut, updatePassword,
  getOverview, getFy, fetchExportCsv,
  getInvoices, getInvoiceSummary, getInvoiceDownloadUrl, getIssues,
};
export default go4garageApi;
