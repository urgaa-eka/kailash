# Go4Garage FY Dashboard — Launch Runbook

The financial-controller FY dashboard for GO4GARAGE PRIVATE LIMITED. It renders
the ten-department model, the Net Payable waterfall, the GST cockpit across three
GSTINs, treasury, direct tax, and the internal-audit registry of defects and open
decisions — on the confirmed figures from the Agent Knowledge Pack, with the
Pack's contradictions surfaced (never silently resolved).

There are two ways to have it in use. Path A needs no infrastructure and is live
today; Path B is the in-product route once the backend is deployed.

## Path A — Instant, no infrastructure (live today)

A standalone, self-contained page (all five FYs, client-side switcher) is
published as a **private** Claude artifact. Only you can see it until you share
it from the page's share menu.

- Regenerate any time from the code:
  ```bash
  cd Kailash/backend/services/company
  PYTHONPATH=. python3 -c "from app.go4garage import render_static, KnowledgePackProvider; \
    open('g4g.html','w').write(render_static(KnowledgePackProvider()))"
  ```
  `g4g.html` is a complete page you can open in any browser or host anywhere
  static (Firebase Hosting, S3, etc.).

## Path B — In the company backend (production)

The dashboard ships as routes on the company service:

| Route | What |
| --- | --- |
| `GET /dashboard/fy?fy=2023-24` | One FY, server-rendered |
| `GET /dashboard/fy/all` | All five FYs in one page (client-side switcher) |
| `GET /dashboard` | The existing Kailash ledger dashboard (unchanged) |

**Data source** is chosen by one environment variable:

```bash
G4G_PROVIDER=knowledge-pack   # default — the confirmed Knowledge-Pack figures
G4G_PROVIDER=null             # structure only, every figure "awaiting source"
```

Bring the whole stack up locally (from `Kailash/`):

```bash
docker compose --profile kailash-ai up -d --build company postgres
# then open http://localhost:8110/dashboard/fy/all
```

### Deploying to production

1. **Merge PR #11** into `main` (the `Kailash/` restructure + this dashboard).
2. Deploy the company service the usual way (`deploy/vultr/deploy.sh` brings up
   the `company` service; or host it wherever the backend runs).
3. Put it behind the reverse proxy / a route on the app so staff can reach
   `/dashboard/fy/all`.
4. Leave `G4G_PROVIDER=knowledge-pack` for now — it is the richest source until a
   live one is populated.

## Working on your data — the built-in database (recommended)

The dashboard has its own store (`g4g_*` tables) in the same PostgreSQL database
as the ledger — so it works against local Postgres or the **Supabase** Postgres
you point `COMPANY_DB_URL` at. This is where your real figures live and are
edited.

**One-time set-up** (creates the tables and seeds them from the confirmed
figures, so nothing starts blank — idempotent):

```bash
curl -X POST http://<host>:8110/go4garage/admin/init \
     -H "X-Platform-Token: $PLATFORM_INTERNAL_TOKEN"
# -> { "schema": "applied", "years_seeded": 5 }
```

**Serve the dashboard from the database** — set one env var and restart:

```bash
G4G_PROVIDER=db      # was knowledge-pack; now reads live from g4g_* tables
```

**Edit / load a year's figures** (partial payloads allowed; the dashboard
reflects it immediately):

```bash
curl -X POST http://<host>:8110/go4garage/fy/2024-25 \
     -H "X-Platform-Token: $PLATFORM_INTERNAL_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"sales": {"invoices": 142, "total_sales": "7151744.25"},
          "purchase": {"approved": "110753.00", "net_payable": "108537.94"}}'
```

Accepted keys per FY: `audit_status, posture, note, revenue, pat`,
`purchase{rows,approved,commission,tds,net_payable,paid,outstanding,zero_commission_rows}`,
`sales{invoices,total_sales,receivable}`, `tax{tds_26as,itr_status}`,
`bank[{bank,debit,credit,excluded_rows}]`,
`gst[{gstin,r1_taxable,output_tax,itc_2b,r3b_filed,vendor_3b_defaults}]`,
`flags[...]`. The Net Payable IGST line is derived so the waterfall always ties.

## Other live sources (optional)

The dashboard reads through a `FinancialDataProvider`
(`app/go4garage/provider.py`). Beyond `db`, you can add:

- **Zoho Books** — read org `60083342031`. Note: today that org is a near-empty
  rebuild (six summary journals for the closed years; the open years are still to
  be built), so it currently holds *less* than the seeded database.

Register any new provider in the `_g4g_providers` map in `app/routes.py`. The
rendering and the confirmed logic (`app/go4garage/logic.py`) never change — only
the numbers' origin.

## What is deliberately *not* wired

- **No writes.** The dashboard is read-only. Nothing here posts to Zoho; the
  Knowledge Pack mandates advisory mode.
- **No private values in the repo beyond the confirmed figures** the dashboard
  displays (`app/go4garage/kp_data.py`). The raw Knowledge-Pack narrative is not
  committed.
