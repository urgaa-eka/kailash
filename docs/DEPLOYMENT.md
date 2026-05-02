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
curl -fsSL https://raw.githubusercontent.com/flywithvvk/kailash/main/deploy/vultr/setup-vps.sh | bash
```

This installs: Docker, Nginx, Certbot, UFW firewall, fail2ban, 2GB swap.

### First Deployment
```bash
# On the VPS:
cd /opt/kailash
git clone https://github.com/flywithvvk/kailash.git .
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

Go to: `https://github.com/flywithvvk/kailash/settings/secrets/actions`

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
