# Runbook: staging

- **Spec task:** production-readiness 12.8
- **Requirements:** 4.6, 8.1, 8.2, 8.3
- **Read with:** `docs/records/profiled-services-scope.md` (the service set),
  `docs/records/container-health-diagnosis.md` (`## Host resource assessment`,
  the H1 verdict that permits same-host staging),
  `docs/records/staging-topology-decision.md` (task 12.1's operator
  confirmation — if that file does not exist yet, obtain the confirmation
  before the first staging deploy)

## Topology

Staging is **Option D**: a second compose project, `kailash-staging`, on the
same VPS as production. The H1 verdict (refuted: memory 41%, CPU 3%, 915 GiB
free disk) makes the host viable for both stacks; the overlay's
`deploy.resources.limits` are the explicit mitigation for the contention risk.
The frontend is a named Firebase Hosting channel (`staging`) on the same
project production uses, `kailash-29111` — **Option A**, chosen because
Requirement 8.1 asks only for a distinct hostname and a named channel provides
one at zero infrastructure cost.

| | Production | Staging |
|---|---|---|
| Web (canonical) | `kailash-ai.com` | `staging.kailash-ai.com` |
| Web (www) | `www.kailash-ai.com` | `www.staging.kailash-ai.com` |
| API | `api.kailash-ai.in` | `staging-api.kailash-ai.in` |
| Firebase serving | live channel | named channel `staging` (`https://kailash-29111--staging.web.app`) |
| Compose project | default (`/opt/kailash`) | `-p kailash-staging`, same checkout |
| Backend port (loopback) | `127.0.0.1:8000` | `127.0.0.1:9000` |
| Platform services | `127.0.0.1:8101-8109` | `127.0.0.1:9101-9109` |
| Company ledger | `127.0.0.1:8110` | `127.0.0.1:9110` |

These hostnames are pinned by the `ENVIRONMENTS` table in
`scripts/verify/deployment_check.py`, which is what `--env staging` probes and
what the isolation rule in `scripts/verify/workflow_gate.py` reads. That table
is the single source; do not restate hostnames anywhere a check cannot see.

Both environments run the same 14 services — the `kailash-ai` profile's 15
minus `frontend` — per `docs/records/profiled-services-scope.md`. The
`workflow_gate.py` service-parity rule holds the overlay to the base compose
file's full service set, so adding a service to `docker-compose.yml` without
updating `deploy/staging/docker-compose.staging.yml` fails CI instead of
colliding with production at `up` time.

## The credential model (Requirement 8.3)

Staging credentials exist under names **disjoint** from production's. The
names are declared in the workflows (the `deploy-staging` jobs) and verified
disjoint by `workflow_gate.py`; the values live only in the GitHub `staging`
environment and on the VPS. Never write a value into a tracked file.

| Production name | Staging name |
|---|---|
| `POSTGRES_PASSWORD` | `STAGING_POSTGRES_PASSWORD` |
| `REDIS_PASSWORD` | `STAGING_REDIS_PASSWORD` |
| `PLATFORM_INTERNAL_TOKEN` | `STAGING_PLATFORM_INTERNAL_TOKEN` |
| `VULTR_HOST` / `VULTR_USER` / `VULTR_SSH_KEY` / `VULTR_SSH_PORT` | `STAGING_VULTR_HOST` / `STAGING_VULTR_USER` / `STAGING_VULTR_SSH_KEY` / `STAGING_VULTR_SSH_PORT` (same host under Option D — distinct declaration, so flipping to Option C later is a secret-value change, not a workflow change) |
| `FIREBASE_SERVICE_ACCOUNT` | `STAGING_FIREBASE_SERVICE_ACCOUNT` |

GitHub Environments `staging` and `production` carry their respective sets, so
`production` can additionally require a reviewer. Creating the environments
and populating the secrets is operator console work (task 12.4 declares the
names; it cannot create the values).

The overlay re-pins every compose credential site to the `STAGING_*` names
with the same `${VAR:?}` strictness as production, so an unset staging
credential aborts at config-parse time rather than deploying on a default.
The base file's own `${POSTGRES_PASSWORD:?}` sites still interpolate, which is
why the CI script (and `.env.staging`, below) also export the unprefixed names
— pointed at the staging values, never production's.

Known, accepted coupling: the staging backend reads the same `backend/.env`
as production for non-compose configuration (`SECRET_KEY`, API keys). The
compose credential set is fully split; splitting `backend/.env` is a follow-up
if staging ever needs divergent application config.

## Deploying to staging

**CI (normal path).** Push to `main`. In both deploy workflows the order is:

```
preflight ─┬─► deploy-staging ─► verify-staging ─┐
ci-gate  ──┤                                     ├─► production deploy ─► verify-production
(test)   ──┘                                     │
        └────────────────────────────────────────┘
```

`deploy-staging` brings up the `kailash-staging` project (backend) and the
`staging` channel (frontend); `verify-staging` runs
`python -m scripts.verify.deployment_check --env staging` and its exit code is
the job's exit code. GitHub Actions skips any job whose `needs` failed, so a
red staging verification makes the production deploy **skipped**, not
attempted — that is Requirements 8.7/8.8 held by the graph, and
`workflow_gate.py --require-staging` (run by ci.yml) asserts the edges exist.

**Manual (VPS).** From `/opt/kailash`, with
`deploy/staging/.env.staging` in place (copy
`deploy/staging/.env.staging.example` and fill it — `umask 077` first):

```bash
docker compose -p kailash-staging \
  -f docker-compose.yml -f deploy/staging/docker-compose.staging.yml \
  --profile kailash-ai --env-file deploy/staging/.env.staging \
  up -d --build backend mongo postgres redis company \
  document-ai forecasting anomaly rag vision-gateway \
  speech model-registry knowledge-graph automobile-llm
curl -sf http://127.0.0.1:9000/api/health
```

**Manual (frontend).** `cd frontend && yarn firebase:preview` deploys the
build to the named `staging` channel with a 30-day expiry.

Verify either path with:

```bash
python -m scripts.verify.deployment_check --env staging
```

## Promotion to production

There is no separate promotion command. Production is deployed by the same
workflow run, from the same commit, **only after** `verify-staging` is green —
the production jobs' `needs` edges are the promotion gate. To promote a fix,
merge it to `main` and let the graph run. To halt a promotion, let
`verify-staging` fail (or cancel the run); the production jobs are skipped.

Consequence worth stating plainly: while staging is red — including while its
DNS, certificates or credentials are not yet provisioned — **production
deploys do not run.** That is the requirement working as designed, and it
makes the operator prerequisites below blocking, not cosmetic.

## Credential rotation (staging)

The ordering constraint is the whole procedure: Postgres reads
`POSTGRES_PASSWORD` **only when the volume is first initialised**. Changing
the compose value first leaves the database accepting the old password while
every client presents the new one, and the symptom points at the application.

Sequence, in order:

1. **Generate** the new value (`openssl rand -hex 32`).
2. **`ALTER ROLE`** inside the running staging database, before any compose
   value changes:
   `docker exec -it kailash-staging-postgres psql -U kailash -c "ALTER ROLE kailash WITH PASSWORD '<new>';"`
   (For Redis: `docker exec kailash-staging-redis redis-cli -a '<old>' CONFIG SET requirepass '<new>'`.)
3. **Store** the new value in the GitHub `staging` environment secret
   (`STAGING_POSTGRES_PASSWORD` / `STAGING_REDIS_PASSWORD`).
4. **Update the VPS** `deploy/staging/.env.staging`.
5. **Restart the affected services** so clients present the new value:
   `docker compose -p kailash-staging -f docker-compose.yml -f deploy/staging/docker-compose.staging.yml --env-file deploy/staging/.env.staging up -d backend company postgres redis`
6. **Verify:** `curl -sf http://127.0.0.1:9000/api/health` and
   `python -m scripts.verify.deployment_check --env staging`.

`deploy/vultr/rotate-credentials.sh` implements this ordering for production;
it operates on `/opt/kailash/.env` and the production containers, so do not
point it at staging without adapting both.

## Fresh volumes and the init scripts (Requirement 4.6)

Compose namespaces volumes by project, so `kailash-staging_postgres_data` and
`kailash-staging_mongo_data` are created fresh on first `up`. Staging is
therefore the **only** environment that exercises the
`docker-entrypoint-initdb.d` first-boot path in `database/postgres_init.sql`
and `database/mongodb_init.js`.

**Expect an early divergence finding.** Any schema, index or extension applied
to production by hand and never added to those scripts will be absent from
staging. That gap is a defect for the init scripts to absorb — fix the script,
not the staging database — and surfacing it on an ordinary Tuesday rather than
during disaster recovery is a benefit of this design, not a problem with it.

Staging receives **no copy of production data**. Seeding, if ever wanted, is a
separate decision with its own privacy consequences.

## Accepted limitation of Option A (shared Firebase project)

Staging and production share Firebase project `kailash-29111`. Firebase Auth
configuration and Firestore security rules are project-scoped, so **staging
does not validate changes to them** — a rules change goes from review to
production without a staging pass.

**Revisit trigger:** the first time an Auth-configuration or security-rules
change causes (or plausibly nearly causes) a production incident, or when such
changes become routine, move staging to its own Firebase project and update
`scripts/verify/data/project_map.json`, `frontend/.firebaserc` and the
`STAGING_FIREBASE_SERVICE_ACCOUNT` secret together.

## Channel expiry: 30 days — operator sign-off required

The `staging` channel is deployed with `expires: 30d`, and every staging
deploy refreshes the window, so an abandoned staging URL expires rather than
silently serving an ancient build. Two consequences the operator is signing
up for:

- More than 30 days without a staging deploy means the staging URL goes dark
  until the next deploy. That is the designed behaviour.
- If the staging URL is ever **shared externally**, expiry becomes a surprise
  to whoever holds the link. Do not share it as if it were stable; if a
  stable external preview is ever needed, that is a different channel with a
  deliberate expiry, not an extension of this one.

- [ ] Operator sign-off on the 30-day expiry: _____________

## Operator prerequisites (blocking, one-time)

- **Task 12.1** — confirm Option D in
  `docs/records/staging-topology-decision.md` (the H1 verdict recommends it;
  the confirmation is the operator's).
- **Task 12.5** — DNS A record for `staging-api.kailash-ai.in`, the
  `nginx-staging.conf` route to `127.0.0.1:9000`, and certbot on the host.
  Additionally, the web hostnames `staging.kailash-ai.com` /
  `www.staging.kailash-ai.com` must be attached in the Firebase console —
  named channels only mint `*.web.app` URLs, so the custom staging domain is
  console + DNS work.
- GitHub Environments `staging` and `production`, with the secret names from
  the table above (values never in this repository).
- `deploy/staging/.env.staging` on the VPS, from the example file, mode 0600.

## `docker-compose.override.yml` stays local-only — do not "fix" this

`docker-compose.override.yml` is auto-merged by a bare `docker compose up`
locally, but **not** in production or staging: `deploy/vultr/deploy.sh`, the
`deploy` job and the `deploy-staging` job all pass `-f docker-compose.yml`
explicitly (staging adds `-f deploy/staging/docker-compose.staging.yml`),
which suppresses the automatic merge. The override publishes the database
ports on loopback for local development; local and deployed stacks therefore
differ in published ports, **and that is correct as it stands**. Removing the
explicit `-f`, or adding the override to a deploy path, would publish three
database ports on the VPS for no production purpose.
