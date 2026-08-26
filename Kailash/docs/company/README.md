# Segment: Company

Master operational ledger and corporate system-of-record: Day-1 records,
statutory financials (GSTR-1/3B, Schedule III, TDS/ROC), and the CA-vs-internal
reconciliation. This is the segment that is **live today** (the Go4Garage FY
dashboard on Firebase + Supabase).

- Technical spec: [`../TRD.md`](../TRD.md) → "Company Segment" sections.
- Go-live / launch: [`../fy-dashboard/`](../fy-dashboard/).
- Backend feature: `backend/features/company/`; frontend: `frontend/src/features/company/`.
