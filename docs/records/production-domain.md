# Production domain topology — observed, decided, and what remains

Task 9.4 ran `python -m scripts.verify.deployment_check --env production`
against the live endpoints on 2026-08-01. This record is its outcome: the
observations, the domain decision they force, and the operator actions that
are the only path to a working product.

## What is live (all observed 2026-08-01)

| Host | DNS | Observed |
|---|---|---|
| `kailash-ai.com` | 199.36.158.100 (Firebase Hosting) | **200, `text/html`** — serves the SPA |
| `www.kailash-ai.com` | resolves | 301 → `https://kailash-ai.com/` |
| `kailash-ai.in` | resolves | 301 → `https://kailash-ai.com/`, cert valid 78 days |
| `www.kailash-ai.in` | resolves | 301 → `https://kailash-ai.com/`, cert valid 78 days |
| `api.kailash-ai.in` | **does not resolve** | — |
| `api.kailash-ai.com` | **does not resolve** | — |

## The defect that matters

The shipped bundle calls `https://api.kailash-ai.in`
(`frontend/.env.production`, `REACT_APP_BACKEND_URL`). That hostname has no
DNS record. **The production site loads and then every API call fails name
resolution** — the product cannot work for any user, independent of anything
on the VPS.

## The domain decision

The original spec assumed `kailash-ai.in` was the web domain. The live
deployment says otherwise: both `.in` hosts carry deliberate, human-configured
301s to `kailash-ai.com`, which serves the SPA from Firebase Hosting. The
verification suite now follows the evidence:

- **Web (canonical): `kailash-ai.com`** — expected 200 `text/html`.
- **Web (legacy): `kailash-ai.in`, `www.kailash-ai.in`** — expected to
  *redirect only* (301/308). A 200 from either would mean split-brain hosting.
- **API: `api.kailash-ai.in`** — because that is the URL baked into the
  shipped bundle. Creating this one DNS record makes the existing deployed
  frontend work without a rebuild; moving the API to `.com` instead would
  require a frontend rebuild and redeploy for zero functional gain.

Encoded in `scripts/verify/deployment_check.py` (`ENVIRONMENTS`,
`LEGACY_REDIRECTS`) and pinned by `tests/verify/test_deployment_check.py`.
If the operator intends differently, change this record and the table
together.

## Operator actions required (nothing else unblocks the product)

1. **Create DNS record `api.kailash-ai.in` → VPS public IP** at the `.in`
   registrar/DNS provider.
2. **Terminate TLS for `api.kailash-ai.in` on the VPS** (the deploy stack
   must obtain a certificate for that hostname and route 443 →
   `backend:8000`).
3. **Set `ALLOWED_ORIGINS` on the VPS to include `https://kailash-ai.com`**
   (and `https://www.kailash-ai.com`). The backend's CORS allowlist predates
   the `.com` cutover; without this, browsers block every API response even
   after DNS resolves. `backend/.env.example` now shows the full set.
4. After 1–3: `python -m scripts.verify.deployment_check --env production`
   must exit 0. Until then it reports `api.kailash-ai.in` UNAVAILABLE, which
   is accurate.

## Certificate margin

`kailash-ai.in` and `www.kailash-ai.in`: 78 days remaining (well above the
14-day floor). The `.com` certificates are managed by Firebase Hosting and
renew automatically.
