# Record: does production run the profile-gated services?

- **Date:** 2026-08-01
- **Repository state:** `9340f44`, working tree clean under every Deployment_Critical_Path
- **Spec task:** production-readiness 3.2
- **Requirements:** 8.2, 5.1
- **Read by:** tasks 8.3 (CI build scope) and 12.3 (staging service set)

## The question

`docker-compose.yml` declares fifteen services. Eleven of them are gated behind
`profiles: ["kailash-ai"]`. Neither deploy path enabled that profile, so a
production deploy started four containers, not fifteen.

Requirement 8.2 says the Staging_Environment runs "the same 15 containers
declared by the `kailash-ai` compose profile". That sentence has two readings
and the requirements do not settle which one holds:

- **(a)** Production is meant to run all fifteen, and both deploy paths are
  missing the profile flag. The omission is a defect.
- **(b)** Production runs the unprofiled subset by design, and "the same 15
  containers" describes the profile's declared set rather than the production
  runtime set. The omission is intentional.

Picking a reading silently would have set the service scope for CI builds and
for the entire staging environment on an assumption.

## Evidence

### Neither deploy path enables the profile

`deploy_containers()` in `deploy/host/deploy.sh`, before this task:

```bash
docker compose -f "$COMPOSE_FILE" pull --ignore-buildable 2>/dev/null || true
docker compose -f "$COMPOSE_FILE" up -d --build --remove-orphans
```

The SSH script block in `.github/workflows/deploy-backend.yml`, before this task:

```bash
docker compose -f docker-compose.yml up -d --build --remove-orphans
```

Neither carries `--profile kailash-ai`, and neither names services explicitly.

### Compose treats profile-gated services as inert without the flag

Verified by running the resolver against the real file, with throwaway
credentials to satisfy the `:?` guards:

```console
$ docker compose -f docker-compose.yml config --services
backend
mongo
postgres
redis
```

Four services. The other eleven are not merely unstarted, they are absent from
the resolved model, so `up`, `build`, `pull` and `ps` all act as if they do not
exist.

The eleven gated services, and where the gate is declared:

| Service | Container | Gate |
| --- | --- | --- |
| `frontend` | `kailash-frontend` | own `profiles: ["kailash-ai"]` |
| `company` | `kailash-company` | own `profiles: ["kailash-ai"]` |
| `document-ai` | `kailash-document-ai` | `x-platform-service` anchor |
| `forecasting` | `kailash-forecasting` | `x-platform-service` anchor |
| `anomaly` | `kailash-anomaly` | `x-platform-service` anchor |
| `rag` | `kailash-rag` | `x-platform-service` anchor |
| `vision-gateway` | `kailash-vision-gateway` | `x-platform-service` anchor |
| `speech` | `kailash-speech` | `x-platform-service` anchor |
| `model-registry` | `kailash-model-registry` | `x-platform-service` anchor |
| `knowledge-graph` | `kailash-knowledge-graph` | `x-platform-service` anchor |
| `automobile-llm` | `kailash-automobile-llm` | `x-platform-service` anchor |

The nine platform services inherit the gate from the YAML anchor rather than
declaring it, which is why the omission is easy to miss when reading either
deploy script against the compose file.

### Consequence, as it stood

Production ran `backend`, `mongo`, `postgres` and `redis`. Every request the
backend makes to a platform service on ports 8101 through 8109, and every
request to the company ledger on 8110, had nothing listening. "Deploy the
backend" meant deploying the backend and none of the services it talks to.

### VPS runtime evidence: not obtained

`docker compose -f docker-compose.yml ps` on the VPS was not run.
`api.kailash-ai.in` does not resolve from this workstation (`nslookup` →
non-existent domain), and `BACKEND_SSH_HOST`, `BACKEND_SSH_USER` and `BACKEND_SSH_KEY` are
GitHub Actions secrets not available locally. The static evidence is decisive
on its own: the resolver output above shows the deployed command could only
ever have created four containers.

## Decision

**Reading (a). Production runs the full `kailash-ai` service set, and both
deploy paths gain `--profile kailash-ai`.**

The Operator asked for "proper deployment for real use with all features". A
backend deployed without the nine platform services and the company ledger is
not the platform with all features, so reading (b) is ruled out by the stated
intent, not by inference.

### The decided set

Requirement 8.2's "same 15 containers" resolves to the profile's fifteen
declared services. Production runs **fourteen of them**; `frontend` is excluded,
for the reason in the next section.

Production and staging service set — 14 containers:

```
backend  mongo  postgres  redis
company
document-ai  forecasting  anomaly  rag  vision-gateway
speech  model-registry  knowledge-graph  automobile-llm
```

Excluded from the production and staging runtime: `frontend`.

Downstream tasks should read this list, not the raw profile membership:

- **Task 8.3** (`compose-build` in `ci.yml`): build scope is a different
  question from runtime scope, and the exclusion below does not carry over. CI
  builds all fifteen, `frontend` included — that task names `frontend` among the
  images not built today, and a tracked build file that CI never exercises is
  the defect Requirement 5 exists to close. `--profile kailash-ai` on
  `docker compose build` with no service names gives exactly that; do not copy
  the fourteen-name list into the build job.
- **Task 12.3** (staging overlay): the fourteen above, with the port offsets it
  specifies. `frontend` is excluded there too; staging's SPA is the Firebase
  named channel from task 12.2, matching production's topology.

## Excluding the frontend container, and why

Enabling the profile would also start `kailash-frontend`, an `nginx:alpine`
container publishing `127.0.0.1:3000:80` and serving a CRA build. That is wrong
for production: Firebase Hosting serves the SPA at `kailash-ai.in`, and the
container exists so the stack can be run end-to-end locally without Firebase.
Running it on the VPS would add a second, divergent copy of the frontend that
nothing routes to.

**Mechanism chosen: name the fourteen services explicitly on the `up` command,
alongside `--profile kailash-ai`.**

Rejected alternatives:

- **`--scale frontend=0`.** `up --build` builds every *selected* service, and
  scale 0 still selects it, so the VPS would run a full `yarn install` plus CRA
  build on every deploy to produce an image that never starts. On a host whose
  headroom is in question (see below) that is a real cost for no benefit. The
  flag also expresses "never run this" as a container count, and compose's
  `--scale` handling is entangled with `container_name` — it rejects counts above
  one for a service that sets one, which `frontend` does — so it is a poorer fit
  for standing policy than a service list an operator can read.
- **Moving `frontend` to its own profile** (for example `profiles: ["local-ui"]`),
  after which `--profile kailash-ai` alone would yield exactly the fourteen and
  the drift risk below would disappear. This is the cleaner fix and is
  recommended as a follow-up. It is not done here because this task must not
  modify `docker-compose.yml`, a Deployment_Critical_Path with its own
  confirmation gate.

Verified with a dry run against the real compose file: the fourteen named
services are planned for creation, `kailash-frontend` appears in no line of the
output, and `--remove-orphans` plans no removal of it either — an explicitly
named subset does not make the unnamed services orphans.

**Known cost of explicit naming:** a service added to `docker-compose.yml` is
not deployed until the list is updated in both deploy paths. Two places now
carry the list: `PROD_SERVICES` in `deploy/host/deploy.sh` and `PROD_SERVICES`
in the SSH script block of `.github/workflows/deploy-backend.yml`. Both carry a
comment pointing at this record and at each other. Collapsing them to one
source is what the `local-ui` profile follow-up would achieve.

## Edits made under this decision

`deploy/host/deploy.sh`:

- Added `COMPOSE_PROFILE="kailash-ai"` and the `PROD_SERVICES` array.
- `deploy_containers()` now passes `--profile "$COMPOSE_PROFILE"` and
  `"${PROD_SERVICES[@]}"` to both `pull` and `up -d --build --remove-orphans`.
- Added a `ps` call with the profile, so the deploy log shows what is running.

`.github/workflows/deploy-backend.yml`, in the `deploy` job's SSH script:

- Added the `PROD_SERVICES` shell variable with the same fourteen names.
- The `up -d --build --remove-orphans` line now passes `--profile kailash-ai`
  and `$PROD_SERVICES`.
- The closing `docker compose ps` now passes `--profile kailash-ai`. Without it
  `ps` filters by active profile and reports four containers out of fourteen,
  which would make a correct deploy look like a broken one in the run log.

Not changed: `docker-compose.yml`, and the `compose-build` job in `ci.yml`
(task 8.3 owns that, and eleven images are still unbuilt in CI until it lands).

## Resource implication — flagged, not resolved

This takes the VPS from **4 running containers to 14**. All ten additions are
Python services — the nine platform services plus the company ledger — each with
its own interpreter and dependency set, and several of them ML-adjacent. The
requirements already record fourteen of the fifteen containers as reporting
Docker health state `unhealthy`, and H1 — host resource saturation making every
probe exceed its timeout at once — is the leading hypothesis in the design's
Requirement 1 analysis.

If H1 is confirmed, this deploy change increases load on a host that is already
the suspected cause of the health failures. That does not make the decision
wrong; the platform is supposed to run these services. It makes the ordering
matter.

- **Task 4.5** measures host headroom and writes the H1 verdict under
  `## Host resource assessment` in `docs/records/container-health-diagnosis.md`.
- **Task 12.1** reads that verdict and either confirms Option D (a second
  compose project on the same host for staging) or flips to Option C (a second
  VPS). Adding a second full stack to a host that cannot sustain one is the
  wrong move, so that dependency is real.

Sizing the VPS is out of scope for this task and is deliberately not attempted
here. Treat the first deploy after this change as the moment to watch memory and
CPU, and note that a staging deployment on the same host would put a further 14
containers alongside these.

## `docker-compose.override.yml` stays local-only

Both deploy paths pass `-f docker-compose.yml` explicitly, which suppresses the
automatic merge of `docker-compose.override.yml`. The override publishes
Postgres, Mongo and Redis on `127.0.0.1` for local development and for the
company-segment tests that reach the ledger DB from the host.

That divergence is correct and should not be "fixed". Adding the override to the
deploy paths, or dropping the explicit `-f`, would publish three database ports
on the production host — even bound to loopback, that widens the surface for no
production purpose. Local and production stacks therefore differ in published
ports by design. The same note belongs in the staging runbook (task 12.8), which
already carries it as a requirement.
