# KAILASH AEGIS HUB — Deployment Guide

## Architecture

```
┌─────────────────────┐       HTTPS        ┌──────────────────────────────┐
│   Firebase Hosting   │ ───────────────► │      managed host                │
│   (Frontend React)   │   API calls      │  ┌──────────────────────┐    │
│                      │                   │  │  Nginx (SSL/proxy)   │    │
│  kailash-ai.in       │                   │  └──────────┬───────────┘    │
│  kailash-aegis.      │                   │             │                │
│    web.app           │                   │  ┌──────────▼───────────┐    │
└─────────────────────┘                   │  │  FastAPI Backend     │    │
                                           │  │  (Docker :8000)     │    │
                                           │  └──────────┬───────────┘    │
                                           │             │                │
                                           │  ┌──────────▼───────────┐    │
                                           │  │ MongoDB │ Postgres  │    │
                                           │  │ Redis                │    │
                                           │  └──────────────────────┘    │
                                           │  api.kailash-ai.in          │
                                           └──────────────────────────────┘
```

---

## 0. Hard precondition — compose credentials

`docker-compose.yml` declares three credentials with `${VAR:?...}`, which has no
default. **Every** compose subcommand — `up`, `build`, `config`, `ps` — aborts
during configuration parsing, before any container is created, if any of them is
unset or empty:

| Variable | Used by |
|---|---|
| `POSTGRES_PASSWORD` | `postgres`, `backend` (`POSTGRES_URL`), `company` (`COMPANY_DB_URL`) |
| `REDIS_PASSWORD` | `redis` server command and healthcheck, `backend` (`REDIS_URL`) |
| `PLATFORM_INTERNAL_TOKEN` | every platform service, and `company` |

This is a deliberate trade. These previously carried `${VAR:-<literal>}`
defaults, so a deploy with nothing configured came up on a password published in
this repository, and `PLATFORM_INTERNAL_TOKEN` defaulted to empty — which
`require_internal_token` treats as matching a caller that sends no header at all.
The failure now moves from *silently deploying with a known-bad credential* to a
loud abort at parse time.

Compose reads these from the environment or from a `.env` file **in the same
directory as `docker-compose.yml`** — on the VPS that is `/opt/kailash/.env`, not
`backend/.env`, which compose never consults for interpolation. Create it before
the first deploy that includes this change:

```bash
# On the VPS, in /opt/kailash
umask 077
cat > .env <<'EOF'
POSTGRES_PASSWORD=<generated>
REDIS_PASSWORD=<generated>
PLATFORM_INTERNAL_TOKEN=<generated>
EOF
```

`.env` is gitignored, and `deploy.sh`'s `git clean -fd` has no `-x`, so it is not
removed by a deploy. Rotating these values requires recreating the Postgres and
Redis volumes or issuing `ALTER USER` / `CONFIG SET requirepass` — changing the
variable alone does not change an already-initialised database's password.

### When `ENV=production`

The backend additionally refuses to start if either of these still holds its
development default (TRD NFR-Sec4 / TR-2, enforced in `app/core/config.py`):

| Variable | Rejected value | Why |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key-change-in-production` | It is published in this repository. Anyone who can read the source can forge a JWT for any account, including the admin — no password needed. |  <!-- secret-scan: allow documents the credential incident being remediated -->
| `CORS_ORIGINS` | `*` | Any origin may call the API with credentials. |

The check runs at import, so the process exits before serving a request rather
than serving one signed with a public key. `ENV` defaults to `dev`, where both
defaults remain allowed.

### Creating the file

```bash
bash deploy/host/bootstrap-env.sh          # defaults to /opt/kailash
cd /opt/kailash && docker compose config --quiet && echo OK
```

Generates all four values from `/dev/urandom`, writes mode 0600, and refuses
to overwrite an existing file. That refusal matters: regenerating credentials
while the Postgres and Redis volumes still hold the old ones produces a stack
that cannot authenticate against its own databases.

### Rotating on a stack that is already running

```bash
bash deploy/host/rotate-credentials.sh
```

`POSTGRES_PASSWORD` and the Redis `requirepass` are read **only when the
volume is first initialised**. Editing `.env` and restarting changes the
password the *clients present*, not the one the database *accepts* — so the
stack comes up unable to log in to its own datastores, and the symptom points
at the application rather than at the rotation.

The script does it in the order that works: `ALTER USER` inside the running
Postgres and `CONFIG SET requirepass` inside the running Redis first, `.env`
second, restart third. It backs up the previous file and tells you to delete
the backup once the stack is healthy.

Rotating `SECRET_KEY` invalidates every issued JWT and forces everyone to sign
in again. That is the point — tokens signed with the old key stop being
forgeable.

### Bootstrapping the first admin

`app/core/seeder.py` creates an admin **only** into a database with no users at
all, and **only** when `ADMIN_SEED_PASSWORD` is set. There is no default and no
"recreate if missing" branch, so a deleted admin stays deleted. To bootstrap:
set `ADMIN_SEED_PASSWORD`, start once, sign in, change the password, then unset
the variable. `database/seed_data.py` requires `SEED_ADMIN_PASSWORD` in the same
way and exits if it is unset.

---

## 0b. Going live — the actual blocking order

As of this writing the site at `kailash-ai.com` is a static SPA on Firebase
project `kailash-29111` with **no backend anywhere**:

```
api.kailash-ai.in       NXDOMAIN
api.kailash-ai.com      NXDOMAIN
backend.kailash-ai.com  NXDOMAIN
```

`kailash-ai.com/api/health` answers 200, but with `Content-Type: text/html`
and the SPA index — that is `firebase.json`'s catch-all rewrite, not an API.

The deployed build's login therefore cannot work, and neither can this
repository's, because both point at a hostname with no DNS record. Deploying
the frontend before the backend exists produces a site that loads and cannot
authenticate anyone.

Do it in this order:

| # | Step | Blocked on |
|---|---|---|
| 1 | `bash deploy/host/bootstrap-env.sh` on the VPS | nothing |
| 2 | Confirm `git remote -v` in `/opt/kailash` is `urgaa-eka/kailash` | nothing |
| 3 | Bring the stack up, confirm `curl -sf localhost:8000/api/health` | 1, 2 |
| 4 | Point an `A` record at the VPS for the API hostname | 3 |
| 5 | Set `REACT_APP_BACKEND_URL` in `frontend/.env.production` to it | 4 |
| 6 | Rebuild and deploy the frontend | 5 |
| 7 | `python -m scripts.verify.deployment_check --env production` | 6 |

Step 4 is the only one that is not in this repository, and everything after it
depends on it. Step 7 currently reports the two known defects — the `.in`
domain 301ing to `.com`, and the missing API record — and will go green when
they are fixed.

---

## 1. Frontend → Firebase Hosting

### Prerequisites
- Node.js 18+ and Yarn
- Firebase CLI: `npm install -g firebase-tools`
- Firebase project: `kailash-aegis`

### Setup (One-Time)
```bash
cd apps/frontend
firebase login
firebase use kailash-38268
```

### Manual Deploy
```bash
cd apps/frontend
yarn install
yarn build              # uses .env.production automatically
firebase deploy --only hosting
```

### CI/CD (Automatic)
Pushes to `main` that modify `apps/frontend/` trigger the `deploy-frontend.yml` workflow.

**Required GitHub Secrets:** none for Firebase. Both deploy jobs authenticate
with `google-github-actions/auth@v2` via Workload Identity Federation (pool
`github-actions`, provider `github`, project `794735482892`). Do not create
or upload a service-account key: org policy
(`iam.disableServiceAccountKeyCreation` / `iam.disableServiceAccountKeyUpload`)
blocks both.

### Environment Files
| File | Usage |
|------|-------|
| `.env.development` | `yarn start` (local dev) |
| `.env.staging` | Staging builds |
| `.env.production` | `yarn build` (production) |

### URLs
- Production: `https://kailash-ai.in` or `https://kailash-38268.web.app`
- Firebase Console: `https://console.firebase.google.com/project/kailash-38268`

---

## 2. Backend → managed host

### Prerequisites
- managed host (Ubuntu 22.04/24.04, minimum 2GB RAM)
- Domain DNS: `api.kailash-ai.in` → managed host IP

### Initial VPS Setup (One-Time)
```bash
# SSH into your managed host, then:
curl -fsSL https://raw.githubusercontent.com/urgaa-eka/kailash/main/deploy/host/setup-vps.sh | bash
```

This installs: Docker, Nginx, Certbot, UFW firewall, fail2ban, 2GB swap.

### First Deployment
```bash
# On the VPS:
cd /opt/kailash
git clone https://github.com/urgaa-eka/kailash.git .
cp apps/backend/.env.example apps/backend/.env
nano apps/backend/.env  # Fill in production secrets
bash deploy/host/deploy.sh
```

### Subsequent Deployments
```bash
# On the VPS:
cd /opt/kailash
bash deploy/host/deploy.sh
```

### CI/CD (Automatic)
Pushes to `main` that modify `apps/backend/` trigger the `deploy-backend.yml` workflow.

**Required GitHub Secrets:**
| Secret | Description |
|--------|-------------|
| `BACKEND_SSH_HOST` | VPS IP address |
| `BACKEND_SSH_USER` | SSH username (usually `root`) |
| `BACKEND_SSH_KEY` | SSH private key for the VPS |
| `BACKEND_SSH_PORT` | SSH port (default: 22) |

### Container Management
```bash
# View running containers
docker compose -f deploy/docker/docker-compose.prod.yml ps

# View logs
docker compose -f deploy/docker/docker-compose.prod.yml logs -f backend

# Restart backend only
docker compose -f deploy/docker/docker-compose.prod.yml restart backend

# Full rebuild
docker compose -f deploy/docker/docker-compose.prod.yml up -d --build
```

### URLs
- API: `https://api.kailash-ai.in`
- API Docs: `https://api.kailash-ai.in/api/docs`
- Health: `https://api.kailash-ai.in/api/health`

---

## 3. DNS Configuration

| Record | Type | Value |
|--------|------|-------|
| `kailash-ai.in` | A / CNAME | Firebase Hosting (follow Firebase custom domain setup) |
| `www.kailash-ai.in` | CNAME | `kailash-ai.in` |
| `api.kailash-ai.in` | A | `<managed host IP>` |

---

## 4. GitHub Secrets Checklist

Go to: `https://github.com/urgaa-eka/kailash/settings/secrets/actions`

| Secret | For |
|--------|-----|
| `BACKEND_SSH_HOST` | Backend deploy |
| `BACKEND_SSH_USER` | Backend deploy |
| `BACKEND_SSH_KEY` | Backend deploy |

Frontend deploys need no secret: Workload Identity Federation covers both the
production and staging Firebase jobs (see §CI/CD above).

### Staging (Requirement 8.3 — names only, values never in this repository)

The staging credential set exists under names **disjoint** from production's;
`scripts/verify/workflow_gate.py` verifies the disjointness from the workflow
declarations. Carry these in the GitHub Environment `staging` (and the
production set in the Environment `production`, which can additionally
require a reviewer):

| Secret | For |
|--------|-----|
| `STAGING_BACKEND_SSH_HOST` | Backend staging deploy (same VPS under Option D; distinct declaration) |
| `STAGING_BACKEND_SSH_USER` | Backend staging deploy |
| `STAGING_BACKEND_SSH_KEY` | Backend staging deploy |
| `STAGING_BACKEND_SSH_PORT` | Backend staging deploy (optional; defaults to 22) |
| `STAGING_POSTGRES_PASSWORD` | Staging compose credentials (`deploy/staging/docker-compose.staging.yml`) |
| `STAGING_REDIS_PASSWORD` | Staging compose credentials |
| `STAGING_PLATFORM_INTERNAL_TOKEN` | Staging compose credentials |

Operational detail: `docs/runbooks/staging.md`.

---

## 5. Backend Environment Variables

Edit `/opt/kailash/apps/backend/.env` on the managed host:

```env
# Required
MONGO_URL=mongodb://localhost:27017      # or MongoDB Atlas URL
DATABASE_NAME=kailash_aegis
SECRET_KEY=<generate-a-long-random-string>
OPENROUTER_API_KEY=sk-or-v1-your-key

# Recommended
FRONTEND_URL=https://kailash-ai.in
BACKEND_URL=https://api.kailash-ai.in
ALLOWED_ORIGINS=https://kailash-ai.in,https://www.kailash-ai.in,https://kailash-38268.web.app,https://kailash-38268.firebaseapp.com

# Firebase Admin (optional — for server-side Firebase features)
FIREBASE_PROJECT_ID=kailash-38268
FIREBASE_STORAGE_BUCKET=kailash-38268.firebasestorage.app
# FIREBASE_SERVICE_ACCOUNT_PATH=/opt/kailash/serviceAccountKey.json
```

---

## 6. Monitoring & Maintenance

### Health Check
```bash
curl https://api.kailash-ai.in/api/health
```

### SSL Certificate (Auto-Renewed)
```bash
certbot certificates                    # Check status
certbot renew --dry-run                 # Test renewal
# Cron auto-renews at 3 AM daily
```

### Backup MongoDB
```bash
docker exec kailash-mongo mongodump --out /data/backup/$(date +%Y%m%d)
docker cp kailash-mongo:/data/backup ./backups/
```

### Update
```bash
cd /opt/kailash && bash deploy/host/deploy.sh
```
