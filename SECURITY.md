# Security Policy

## Supported Versions

Only the `main` branch is actively supported. Security fixes are not
backported to older tags.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security reports.**

Email `security@kailash-ai.in` with:

- A description of the issue and its impact.
- Steps to reproduce (PoC, affected endpoints, request/response samples).
- Your disclosure timeline expectations.

We will acknowledge receipt within 72 hours and provide a remediation
timeline within 7 days.

## Secrets Handling

1. **Never commit secrets.** `.env`, service credentials, provider API
   keys, signing material, and production configuration are all
   `.gitignore`-d.
2. Each service ships a committed `.env.example` documenting variable
   names only.
3. GitHub push protection is enabled upstream; commits that include a
   detected secret are rejected.

### If a secret is accidentally committed

1. **Rotate the credential at the provider first** (OpenRouter,
   Anthropic, Mongo, etc.). Assume it is compromised.
2. Remove the secret from the working tree and commit the fix.
3. Scrub history with `git filter-repo` or BFG if the leak reached the
   remote.
4. Force-push the cleaned history; notify all collaborators to re-clone.
5. Open a private post-mortem issue referencing the rotation IDs.

## Authentication Model

- **Internal token** — platform services are guarded by
  `require_internal_token`, which checks `X-Platform-Token` against
  `PLATFORM_INTERNAL_TOKEN`. No-op in dev mode.
- **Producer-to-platform** — consumers must hold the internal token; it
  should be provisioned per deployment and rotated on any suspected
  exposure.
- **End-user auth** — handled inside the main application (three-factor auth
  + JWT). Platform services never see end-user credentials.

## Transport

Production deployments must terminate TLS at the gateway or upstream
load balancer. Intra-cluster traffic should use a private network / VPC
/ service mesh; the internal token is a defence-in-depth layer, not a
substitute for network isolation.

## Dependency Hygiene

- All Python dependencies are pinned in each service's `requirements.txt`.
- CI runs `ruff` and the full test matrix on every push and PR.
- Dependabot / Renovate is recommended for periodic upgrades (not yet
  enabled in this repo).
