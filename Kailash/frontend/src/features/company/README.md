# Feature: company (financials)

The Company data-core segment's UI — the Go4Garage FY financial-controller
dashboard. **Live today**, serverless: reads figures directly from Supabase
(Auth + RLS), no application backend.

- `Go4GarageFinancials.jsx` / `.css` — the dashboard (self-gated via Supabase Auth).
- `go4garageApi.js` — Supabase reads for overview + per-FY payloads; client-side CSV export.
- `supabaseClient.js` — the `@supabase/supabase-js` client (publishable anon key; RLS is the boundary).

Routes (`@/App.js`): `/financials`, `/dashboard/financials`.
Backend counterpart (segment source-of-record): `backend/features/company/` (the
statutory ledger; not required by this serverless surface).
