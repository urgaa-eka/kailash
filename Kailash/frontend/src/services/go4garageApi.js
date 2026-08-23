/**
 * Go4Garage Financial Controller — API service.
 *
 * Reads the FY financial dashboard from the company service. The payloads carry
 * the same key shape the store accepts (POST /go4garage/fy/{fy}), so every figure
 * shown here maps 1:1 into the store and onward to Zoho Books.
 *
 * Base URL: REACT_APP_COMPANY_API_URL (the company service, e.g. :8110) if set,
 * otherwise the main backend URL, otherwise same-origin.
 */
import axios from 'axios';

const BASE =
  process.env.REACT_APP_COMPANY_API_URL ||
  process.env.REACT_APP_BACKEND_URL ||
  '';

const client = axios.create({ baseURL: BASE, timeout: 20000 });

// Company responses are ApiResponse envelopes: { ok, data, error, request_id }.
const unwrap = (res) => (res && res.data && 'data' in res.data ? res.data.data : res.data);

/** FY-independent: entity, model spine, departments, defects, decisions, trend. */
export async function getOverview() {
  return unwrap(await client.get('/go4garage/api/overview'));
}

/** One financial year in store shape (money as exact strings; null = awaiting). */
export async function getFy(fy) {
  return unwrap(await client.get(`/go4garage/api/fy/${encodeURIComponent(fy)}`));
}

/** All five FYs as flat CSV text (store column shape) — for Zoho column-mapping. */
export async function fetchExportCsv() {
  const res = await client.get('/go4garage/api/export.csv', { responseType: 'text' });
  return res.data;
}

const go4garageApi = { getOverview, getFy, fetchExportCsv };
export default go4garageApi;
