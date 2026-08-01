# KAILASH AEGIS HUB — Deployment Guide

## Architecture

```
┌─────────────────────┐       HTTPS        ┌──────────────────────────────┐
│   Firebase Hosting   │ ───────────────► │      Vultr VPS                │
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

**Required GitHub Secrets:**
| Secret | Description |
|--------|-------------|
| `FIREBASE_SERVICE_ACCOUNT` | Firebase service account JSON (from Firebase Console → Project Settings → Service Accounts) |

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

## 2. Backend → Vultr VPS

### Prerequisites
- Vultr VPS (Ubuntu 22.04/24.04, minimum 2GB RAM)
- Domain DNS: `api.kailash-ai.in` → Vultr VPS IP

### Initial VPS Setup (One-Time)
```bash
# SSH into your Vultr VPS, then:
curl -fsSL https://raw.githubusercontent.com/urgaa-eka/kailash/main/deploy/vultr/setup-vps.sh | bash
```

This installs: Docker, Nginx, Certbot, UFW firewall, fail2ban, 2GB swap.

### First Deployment
```bash
# On the VPS:
cd /opt/kailash
git clone https://github.com/urgaa-eka/kailash.git .
cp apps/backend/.env.example apps/backend/.env
nano apps/backend/.env  # Fill in production secrets
bash deploy/vultr/deploy.sh
```

### Subsequent Deployments
```bash
# On the VPS:
cd /opt/kailash
bash deploy/vultr/deploy.sh
```

### CI/CD (Automatic)
Pushes to `main` that modify `apps/backend/` trigger the `deploy-backend.yml` workflow.

**Required GitHub Secrets:**
| Secret | Description |
|--------|-------------|
| `VULTR_HOST` | VPS IP address |
| `VULTR_USER` | SSH username (usually `root`) |
| `VULTR_SSH_KEY` | SSH private key for the VPS |
| `VULTR_SSH_PORT` | SSH port (default: 22) |

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
| `api.kailash-ai.in` | A | `<Vultr VPS IP>` |

---

## 4. GitHub Secrets Checklist

Go to: `https://github.com/urgaa-eka/kailash/settings/secrets/actions`

| Secret | For |
|--------|-----|
| `FIREBASE_SERVICE_ACCOUNT` | Frontend deploy |
| `VULTR_HOST` | Backend deploy |
| `VULTR_USER` | Backend deploy |
| `VULTR_SSH_KEY` | Backend deploy |

---

## 5. Backend Environment Variables

Edit `/opt/kailash/apps/backend/.env` on the Vultr VPS:

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
cd /opt/kailash && bash deploy/vultr/deploy.sh
```
