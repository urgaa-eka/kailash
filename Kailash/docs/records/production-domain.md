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

Encoded in `scripts/verify/deployment_check.py` (`ENVIRONMENTS`) and pinned by
`tests/verify/test_deployment_check.py`. If the operator intends differently,
change this record and the table together. **Superseded in part by the
addendum below**, which records the operator's decision that both domains are
production.

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

## Addendum — operator decision, 2026-08-02: both domains are production

The operator owns **both** `kailash-ai.in` and `kailash-ai.com` and both are to
be synced to serve the same site. That supersedes the "canonical `.com`,
legacy `.in`" reading above. Neither domain is a redirect to the other; both
are production entry points.

What changed in the repository:

- `scripts/verify/deployment_check.py` — the production table now verifies
  **five** hosts: `kailash-ai.in` and `kailash-ai.com` (200 `text/html`, asset
  manifest containment, certificate margin), `www.kailash-ai.in` and
  `www.kailash-ai.com` (200/301/308, certificate margin), and
  `api.kailash-ai.in/api/health` (200, certificate margin). `LEGACY_REDIRECTS`
  is gone: a `.in` apex that only redirects is now a finding, because half the
  operator's traffic would be reaching a host that serves nothing itself.
- The API host stays `.in` alone. `api.kailash-ai.com` has never resolved and
  no tracked file references it, so verifying it would assert an intention
  nothing declares.
- `REACT_APP_DOMAIN` remains `kailash-ai.in`, now pinned by the
  `production-domain` rule in `scripts/verify/config_drift.py`
  (`EXPECTED_PRODUCTION_DOMAIN`). It is the app's own idea of its identity,
  not a routing rule — the other domain works either way.
- `backend/.env.example` and `deploy/host/bootstrap-env.sh` now list every
  origin the SPA can be served from: both apexes, both `www` forms, both
  Firebase default hosts, and the named staging channel
  `kailash-29111--staging.web.app`.

### Live state on 2026-08-02, and what it still needs

`python -m scripts.verify.deployment_check --env production` from the developer
workstation:

| Host | Observed | Verdict |
|---|---|---|
| `kailash-ai.com` | 200 `text/html`, cert 77 days | passes |
| `www.kailash-ai.com` | in allowed set, cert 77 days | passes |
| `www.kailash-ai.in` | in allowed set, cert 77 days | passes |
| `kailash-ai.in` | **301, `text/plain`**, cert 77 days | **FAIL** — the sync is not in effect yet |
| `api.kailash-ai.in` | does not resolve | UNAVAILABLE (unchanged) |

The `.in` apex is still a redirect. Making it serve the site is operator work
in the Firebase console: attach `kailash-ai.in` as a custom domain on
`kailash-29111` (Hosting → Add custom domain) and remove the registrar-level
301, after which Firebase provisions the certificate itself. Until then the
production check reports that host as a finding, which is accurate.

### Certbot coverage

TLS on the VPS is issued by `deploy/host/deploy.sh` for `api.kailash-ai.in`
only, and no additional **production** hostname needs certbot: the four web
hosts are terminated by Firebase Hosting. One staging gap remains and is not
addressed here — `staging-api.kailash-ai.in`, which the staging table verifies,
has no certbot invocation in `deploy/host/deploy.sh` or `nginx-api.conf`.
Issuing it is operator work on the VPS (spec task 12.5).

## Certificate margin

`kailash-ai.in` and `www.kailash-ai.in`: 78 days remaining (well above the
14-day floor). The `.com` certificates are managed by Firebase Hosting and
renew automatically.

## Addendum — 2026-08-03: DNS created, VPS provisioning underway

- **`api.kailash-ai.in` → `140.82.62.136` exists** (Route 53 zone
  `Z09657811Z81KA47PHRNW`, TTL 300), verified against the authoritative
  nameserver and propagated to public resolvers. Operator action 1 above is
  discharged. `staging-api.kailash-ai.in` points at the same VPS (Option D).
- The VPS (`140.82.62.136`, fresh Ubuntu 22.04) is being provisioned from
  `deploy/host/setup-vps.sh` + `bootstrap-env.sh` + `deploy.sh`. Until that
  completes, the API hostnames resolve but nothing answers on 443 — the check
  correctly reports them unreachable.
- `kailash-ai.in` was attached as a custom domain on `kailash-29111` in the
  Firebase console on 2026-08-03. As of the last probe it still serves the
  301 — Firebase keeps the old redirect config live until the new domain
  finishes provisioning. If it still redirects after provisioning settles,
  the redirect-type domain entry must be removed explicitly in
  Hosting → custom domains.
- The stray literal-`@` record (`\100.kailash-ai.in A 172.66.2.113`) predates
  this effort, recurs in unrelated zones (`urgaa.in`, `gstsaas.in`), and
  points at a bulk-import mistake — harmless, but worth deleting when someone
  is next in the zone.
