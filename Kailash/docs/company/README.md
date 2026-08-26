# Segment: Company

Master operational ledger and corporate system-of-record: Day-1 records,
statutory financials (GSTR-1/3B, Schedule III, TDS/ROC), and the CA-vs-internal
reconciliation. This is the segment that is **live today** (the Go4Garage FY
dashboard on Firebase + Supabase).

- Technical spec: [`../TRD.md`](../TRD.md) → "Company Segment" sections.
- Go-live / launch: [`GO-LIVE.md`](./GO-LIVE.md), [`LAUNCH.md`](./LAUNCH.md).
- Backend service: `backend/services/company/`; frontend: `frontend/src/features/company/`.
