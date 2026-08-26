# Kailash — Go-Live Runbook (Firebase + managed data + managed host)

The single, copy-paste checklist to take Kailash (the 14-service platform + the
Go4Garage FY dashboard) from the CI-green branch to production.

**Topology at launch** (public domains do **not** change):

```
kailash-ai.in ────────► Firebase Hosting  (project kailash-29111, SPA)   [unchanged]
api.kailash-ai.in ────► managed host       (docker compose over SSH)      [replaces Vultr]
                          ├─ Postgres → Supabase      (COMPANY_DB_URL, POSTGRES_URL)
                          ├─ MongoDB  → MongoDB Atlas  (MONGO_URL)
                          └─ Redis    → managed Redis  (REDIS_URL)
```

The repo is **already wired for this**: each data store is repointed by one env
var (`docker-compose.yml` reads `${VAR:-<local default>}` for all three), and the
backend deploy is provider-neutral (`deploy/host/deploy.sh`, `BACKEND_SSH_*`
secrets). Nothing in the repo needs to change to go live — this runbook is the
operator side.

> **Secrets never live in the repo.** Every value below is a placeholder. Set
> real values only on the host `.env` and in GitHub environment secrets.

---

## 0. Prerequisites

- PR #11 (`claude/init-x0katl`) merged to `main` — or deploy from that branch.
- A managed Linux host with Docker + Docker Compose, reachable over SSH.
- Accounts: Supabase, MongoDB Atlas (or equivalent), a managed Redis (Upstash /
  Redis Cloud / equivalent), and DNS control for `kailash-ai.in`.

---

## 1. Managed data services

### 1a. Supabase Postgres (project `xwlpuehfhaupkfyuibtz`, or your own)

1. In the project, open **SQL editor** and run the extension bootstrap that used
   to run as container-init (from `Kailash/database/postgres_init.sql`, idempotent):

   ```sql
   CREATE EXTENSION IF NOT EXISTS pgcrypto;
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```

2. Take the **session-pooler** connection string — **port 5432**, TLS required.
   Use the session pooler, *not* the transaction pooler (`:6543`): the transaction
   pooler disables prepared statements, and asyncpg then needs
   `statement_cache_size=0`. This one string feeds two env vars:

   ```
   COMPANY_DB_URL=postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
   POSTGRES_URL=postgresql+asyncpg://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
   ```
   (Same host/credentials; `COMPANY_DB_URL` is psycopg-style, `POSTGRES_URL` is
   the asyncpg driver form the backend uses.)

The `g4g_*` tables themselves are **not** created here — they are created and
seeded by the app in step 6 (`/go4garage/admin/init`), which writes into the
`company` schema.

### 1b. MongoDB Atlas

1. Create a free/shared cluster; get the SRV connection string → `MONGO_URL`:
   ```
   MONGO_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/kailash
   ```
2. Apply the collection + index bootstrap from `Kailash/database/mongodb_init.js`
   (10 collections with their indexes) against the cluster, e.g.:
   ```bash
   mongosh "<MONGO_URL>" Kailash/database/mongodb_init.js
   ```

### 1c. Managed Redis (Upstash / Redis Cloud / equivalent)

- Take the TLS URL (with password) → `REDIS_URL`:
  ```
  REDIS_URL=rediss://:<password>@<host>:<port>/0
  ```
- Note: if you keep the local `redis` container instead of a managed one, its
  password site in `docker-compose.yml` still requires `REDIS_PASSWORD` at
  parse-time — set one, or drop `redis` from the started service list.

---

## 2. The host `.env`

Put this on the managed host (never commit it). Placeholders only:

```bash
# ---- Data layer (managed) ----
COMPANY_DB_URL=postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
POSTGRES_URL=postgresql+asyncpg://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
MONGO_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/kailash
REDIS_URL=rediss://:<password>@<host>:<port>/0
DATABASE_NAME=kailash

# ---- Go4Garage dashboard source ----
G4G_PROVIDER=db                 # serve the FY dashboard live from Supabase (after step 6)

# ---- Security / internal ----
SECRET_KEY=<long-random-string>
PLATFORM_INTERNAL_TOKEN=<long-random-string>

# Kept for compose parse-time even when the managed URLs override them
# (the local container password sites use these; see docker-compose.yml notes):
POSTGRES_PASSWORD=<long-random-string>
REDIS_PASSWORD=<long-random-string>

# ---- CORS / domains ----
ALLOWED_ORIGINS=https://kailash-ai.in,https://www.kailash-ai.in,https://kailash-ai.com,https://www.kailash-ai.com,https://kailash-29111.web.app,https://kailash-29111.firebaseapp.com,https://kailash-29111--staging.web.app
BACKEND_URL=https://api.kailash-ai.in
FRONTEND_URL=https://kailash-ai.in

# ---- Auth (Firebase Admin SDK — verifies logins for the /financials page) ----
FIREBASE_SERVICE_ACCOUNT_JSON=<inline service-account JSON>
FIREBASE_PROJECT_ID=kailash-29111

# ---- AI provider (choose one) ----
OPENROUTER_API_KEY=<openrouter-key>
# ANTHROPIC_API_KEY=<anthropic-key>
```

See `Kailash/backend/.env.example` and
`Kailash/backend/services/company/.env.example` for the full annotated templates.

---

## 3. GitHub environment secrets (for the deploy pipeline)

The backend deploy (`.github/workflows/deploy-backend.yml`) is keyed to
**disjoint** staging vs production secret names (the `workflow_gate` enforces
disjointness). Set these on the `production` and `staging` GitHub **Environments**:

| Production env | Staging env | Value |
| --- | --- | --- |
| `BACKEND_SSH_HOST` | `STAGING_BACKEND_SSH_HOST` | host IP / DNS |
| `BACKEND_SSH_USER` | `STAGING_BACKEND_SSH_USER` | deploy user |
| `BACKEND_SSH_KEY`  | `STAGING_BACKEND_SSH_KEY`  | private SSH key |
| `BACKEND_SSH_PORT` | `STAGING_BACKEND_SSH_PORT` | SSH port (optional) |
| `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `PLATFORM_INTERNAL_TOKEN` | `STAGING_*` of each | as on the host |

- **Frontend** deploys keylessly via **Workload Identity Federation**
  (`github-actions-deploy@`, `roles/firebasehosting.admin`) — no key secret to set.
- Confirm the repo/environment var **`vars.BACKEND_URL = https://api.kailash-ai.in`**
  (the SPA build reads it; it also defaults to that value).

---

## 4. DNS + TLS

- `kailash-ai.in` (+ `www`) → **Firebase Hosting**: add the custom domain in the
  Firebase console and create the A/AAAA + TXT records it shows. Firebase issues
  the TLS cert.
- `api.kailash-ai.in` → the **managed host** IP (A record). Terminate TLS at the
  host (the `deploy/host/nginx-api.conf` reverse-proxy pattern, or host-managed
  TLS).
- Add the staging hostnames the pipeline already declares, the same way.

---

## 5. Deploy

Merge PR #11 (or push `claude/init-x0katl`). The two pipelines run:

- **Backend** — `preflight → ci-gate → test → deploy-staging → verify-staging →
  deploy → verify-production`. Production is gated behind a green staging
  (`deployment_check.py`).
- **Frontend** — Firebase staging channel → verify → live → verify.

The backend deploy runs `deploy/host/deploy.sh` over SSH: it checks out the
expected repo, then `docker compose up -d` for the stack. Bring up the full
profile (platform + company + frontend-nginx) with `--profile kailash-ai`.

---

## 6. Post-deploy data bootstrap (Go4Garage dashboard)

Create + seed the `g4g_*` tables in Supabase's `company` schema (idempotent,
5 FYs). The company service listens on `:8110`; the endpoint is guarded by the
`X-Platform-Token` header:

```bash
curl -X POST https://api.kailash-ai.in/go4garage/admin/init \
     -H "X-Platform-Token: <PLATFORM_INTERNAL_TOKEN>"
# -> { "ok": true, "data": { "schema": "applied", "years_seeded": 5 } }
```

With `G4G_PROVIDER=db` (step 2), the dashboard now serves live from Supabase.
Load or edit a year with `POST /go4garage/fy/{fy}` (same token header) — see
`docs/company/LAUNCH.md` for the accepted keys.

---

## 7. Smoke test

| Check | URL / action | Expect |
| --- | --- | --- |
| Frontend up | `https://kailash-ai.in/` | SPA loads |
| FY dashboard | `https://kailash-ai.in/financials` | login → KPIs, waterfall, GST, trend |
| Server-rendered FY | `https://api.kailash-ai.in/dashboard/fy/all` | all five FYs, switcher |
| Backend health | `https://api.kailash-ai.in/api/health` | `ok`, reports `GIT_COMMIT` |
| JSON API | `https://api.kailash-ai.in/go4garage/api/overview` | entity + model + trend JSON |
| Login | sign in on `/financials` | token accepted (Firebase Admin SDK) |

If a call fails CORS, the failing origin is missing from `ALLOWED_ORIGINS`
(step 2) — add it and restart. Production refuses to start on `ALLOWED_ORIGINS=*`.

---

## What is deliberately *not* automated

- **No secrets in the repo** — all real values are set on the host `.env` and in
  GitHub environment secrets.
- **No writes to Zoho** — the dashboard is read-only/advisory.
- **Account, DNS, and secret provisioning stay with the operator** — this runbook
  is the map, not an agent that holds your credentials.
