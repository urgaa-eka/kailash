# Record: what path does the backend serve its health route on?

- **Date:** 2026-08-01
- **Repository state:** `9340f44`. Under Deployment_Critical_Path the working tree
  carries the uncommitted task-3.2 edits to `deploy/host/deploy.sh` and
  `.github/workflows/deploy-backend.yml`, and nothing else
- **Spec task:** production-readiness 3.3
- **Requirements:** 1.3, 2.3
- **Hypothesis under test:** H5 — "`backend` serves its health route at a path
  other than `/api/health`, so `curl -f` gets a 404"
- **Evidence type:** **container.** Every observation below came from the running
  `kailash-backend` container — from inside it via `docker exec`, and from the
  host against its published port. None of it is in-process `TestClient`
  evidence, which by construction cannot see a wrong-image or stale-build
  difference
- **Read by:** task 4.8 (adds the route only if it is not served), task 4.7
  (probe corrections)

## Verdict

**H5 is refuted.** The running backend serves `/api/health` and it returns HTTP
200. The compose probe's path is correct, `curl` is present in the image, and
the container reports `healthy` with a failing streak of 0.

Task 4.8 therefore makes **no source change**. Task 4.7 has no path-alignment
remedy to apply to `backend`.

## Two premises in the spec that the evidence corrects

1. **"No literal `/api/health` route exists anywhere in `backend/**/*.py`."**
   Stated in task 3.3, in the design's H5 row, and in the design's open question
   1. It is wrong. `backend/app/main.py` declares the literal decorators, and a
   plain grep for `/api/health` across `**/*.py` finds them at lines 299 and 300
   along with three other occurrences in the same file. Why the original grep
   missed them is not established here; the current result is reproducible.
2. **`curl -s localhost:8000/openapi.json` reads the path list.** It does not.
   The main app sets `openapi_url="/api/openapi.json"`, so `/openapi.json`
   returns 404 and the prescribed command prints `{"detail":"Not Found"}` while
   exiting 0 — no schema, no error signal. Taken at face value that reads as
   "the app publishes no paths", which would have *appeared* to confirm H5. The
   schema is at `/api/openapi.json`. Both were run; both results are recorded
   below.

## Source registration sites

Both of the two health mounts exist, and they serve different consumers. This is
not a duplicate to be reconciled.

| Site | Path(s) | Methods | Consumer |
| --- | --- | --- | --- |
| `backend/app/main.py:299-303` | `/api/health`, `/health` | GET, HEAD each | the main app, container `kailash-backend` |
| `backend/shared/app.py:99` | `/health` | GET | the ten `build_app()` services |
| `backend/app/api/simple_health.py:11-12` | `/health/simple` | GET, HEAD | main app, router mounted with no prefix at `main.py:296` |
| `backend/app/api/system_health.py:19` | `/api/system/health/detailed` | GET | main app, router mounted with no prefix at `main.py:295` |

`backend/app/main.py` does not use `build_app()`. It constructs `FastAPI(...)`
directly at line 212 with `docs_url="/api/docs"`, `redoc_url="/api/redoc"` and
`openapi_url="/api/openapi.json"`, then stacks four decorators on one handler:

```python
# backend/app/main.py:298-303
# Health check endpoint
@app.get("/api/health")
@app.head("/api/health")
@app.get("/health")
@app.head("/health")
async def health_check():
```

`build_app()` mounts only `/health`:

```python
# backend/shared/app.py:99
@app.get("/health", response_model=HealthResponse, tags=["platform"])
```

Its consumers are all ten service modules under `backend/services/*/app/main.py`
— the nine Platform_Services plus `company` — each of which is exactly
`app = build_app(settings, routers=[register])`, verified by grep across all ten:
`anomaly`, `automobile-llm`, `company`, `document-ai`, `forecasting`,
`knowledge-graph`, `model-registry`, `rag`, `speech`, `vision-gateway`.

The main app's `/health` alias is what keeps the two consistent from a caller's
point of view, but it is served by `health_check()` in `main.py`, not by
`build_app()`.

## Observation from the running container

Container: `kailash-backend`, started `2026-07-31T15:27:17Z`, status
`Up 21 hours (healthy)`.

### Direct probes

```console
$ docker exec kailash-backend curl -s -o /dev/null -w '%{http_code}' localhost:8000/openapi.json
404
$ docker exec kailash-backend curl -s -o /dev/null -w '%{http_code}' localhost:8000/api/openapi.json
200
$ docker exec kailash-backend curl -s -o /dev/null -w '%{http_code}' localhost:8000/api/health
200
$ docker exec kailash-backend curl -s -o /dev/null -w '%{http_code}' localhost:8000/health
200
```

`/api/health` → **200**. That one line refutes H5.

### Host-side probe, matching Requirement 1.3's wording exactly

Requirement 1.3 names `http://127.0.0.1:8000/api/health`, from the host rather
than from inside the container, so it was issued that way too:

```console
PS> (Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing).StatusCode
200
PS> (Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing).Content
{"status":"healthy","app":"Kailash","database":"connected",
 "timestamp":"2026-08-01T12:37:06.539241","version":"2.0.0",
 "company":"Go4Garage","product":"Kailash","domain":"kailash-ai.in",
 "departments":20,"sub_agents":64}
```

Requirement 1.3 holds as observed at this date. Task 4.9 still owns asserting it
as a repeatable test; this is a single manual reading, not a gate.

Two details in that body are worth carrying forward, neither of them this task's
business. `"database":"connected"` means the handler's MongoDB ping succeeded, so
the 200 here is not the always-200 degraded branch — the route returns 200 either
way, by design, for exactly the k8s-probe reason its docstring gives.
`"version":"2.0.0"` carries no commit identifier, which is what Requirement 6.6
will need when it asks the health response to report the deployed commit SHA.

### Path list from the running app's OpenAPI schema

Fetched inside the container from `http://localhost:8000/api/openapi.json`
(77 420 bytes). **Total paths: 99.** Every path whose name contains `health`,
which is the relevant subset:

| Path | Methods |
| --- | --- |
| `/api/analytics/department-health` | get |
| `/api/automobile/health` | get |
| `/api/departments/{department_id}/health` | get |
| **`/api/health`** | **get, head** |
| `/api/system/health/detailed` | get |
| `/health` | get, head |
| `/health/simple` | get, head |

The full 99-path list is not reproduced here; it is the main app's entire route
surface across every mounted router, and one call to the command above
regenerates it. The four registration sites in the table above account for all
four liveness paths in that subset; the remaining three health-named paths are
domain routes (department health scores, automobile subsystem status), not
liveness endpoints.

### The route is in the image, not only in the working tree

```console
$ docker exec kailash-backend grep -n api/health /app/backend/app/main.py
241:    if request.url.path in ["/api/health", "/health", "/"]:
284:@app.get("/api/health")
285:@app.head("/api/health")
376:        "health": "/api/health",
```

The line numbers differ from the working tree's 256/299/300/391 because the
image was built from an earlier commit. The route predates the current
working-tree state, so the finding is not an artefact of recent local edits.

## Is `curl` in the image?

**Yes.** This is recorded separately because it is a live candidate for the
container-health problem in its own right: the compose probe is
`curl -f http://localhost:8000/api/health`, and an absent `curl` would fail the
probe no matter how correct the path is.

```console
$ docker exec kailash-backend which curl
/usr/bin/curl          # exit 0
$ docker exec kailash-backend which wget
                       # exit 1 — absent
$ docker exec kailash-backend which python
/usr/local/bin/python  # exit 0
```

Requirement 1.2 is satisfied for `kailash-backend`: the probe's executable is
present, verified by `which` exiting 0. Note for task 4.7 — `wget` is **not** in
this image, so a probe rewritten to `wget` would break a currently working
probe. (`nginx:alpine` in `kailash-frontend` is the container where `wget` is
the right choice; that is task 4.6's scope, and this record does not test it.)

### Effective probe and current state

```console
$ docker inspect --format '{{json .Config.Healthcheck}}' kailash-backend
{"Test":["CMD","curl","-f","http://localhost:8000/api/health"],
 "Interval":30000000000,"Timeout":10000000000,"StartPeriod":40000000000,"Retries":3}

$ docker inspect --format '{{.State.Health.Status}} {{.State.Health.FailingStreak}}' kailash-backend
healthy 0
```

The effective probe matches the declaration at `docker-compose.yml:196` exactly,
so for this container there is no compose-interpolation gap between declared and
effective probe.

## Reasoning behind the verdict

H5 predicted a 404 on the probed path. The probed path returns 200, from the
image the container is actually running, and Docker's own probe — the same
command, on the same interval — reports `healthy` with a failing streak of 0.
Three independent readings agree. There is no version of H5 that survives them.

The hypothesis was reasonable when written: `build_app()` genuinely does mount
`/health` and not `/api/health`, and if the main app had been built through the
factory like the other ten services, H5 would have been correct. It is not; it
predates the shared factory and declares its own routes.

## Evidence limits

- **In-process cross-check not obtained on this workstation.** `pytest
  backend/tests/test_app_contract.py` fails at collection with
  `ModuleNotFoundError: No module named 'jose'` — `python-jose` is not installed
  in the host interpreter. It is not worth installing: container evidence is the
  stronger of the two for this question, because a container-level difference
  (wrong image, stale build) is invisible to an in-process run.
- **The contract test is not in the running image.** `test_app_contract.py`, added
  by task 2.2, is absent from the image's `/app/backend/tests` because the image
  predates it. That does not weaken the finding; it sharpens it. The older image
  already serves the route.
- **The running container is one build behind the tag.** It runs image
  `sha256:c3e6115…`, while `kailash-ai-backend:latest` now resolves to
  `sha256:e7f7a7f…` built 2026-08-01 10:37 IST. Both serve `/api/health` — the
  working tree declares it and the running image declares it — so the drift does
  not affect this verdict. Recorded because the running stack is not the newest
  build, which matters for any later observation taken from these containers.

## Collateral observation: the "14 unhealthy" premise is stale

Not this task's subject, and **not acted on here**. Recorded because tasks 4.1
through 4.7 are scoped around fourteen unhealthy containers, and as observed at
this date the count is the mirror image of that:

```console
$ docker ps -a --filter name=kailash- --format '{{.Names}} | {{.Status}}'
kailash-anomaly          | Up 24 hours (healthy)
kailash-automobile-llm   | Up 24 hours (healthy)
kailash-backend          | Up 21 hours (healthy)
kailash-company          | Up 23 hours (healthy)
kailash-document-ai      | Up 24 hours (healthy)
kailash-forecasting      | Up 24 hours (healthy)
kailash-frontend         | Up 22 hours
kailash-knowledge-graph  | Up 24 hours (healthy)
kailash-model-registry   | Up 24 hours (healthy)
kailash-mongo            | Up 21 hours (healthy)
kailash-postgres         | Up 24 hours (healthy)
kailash-rag              | Up 24 hours (healthy)
kailash-redis            | Up 23 hours (healthy)
kailash-speech           | Up 24 hours (healthy)
kailash-vision-gateway   | Up 24 hours (healthy)
```

Fourteen report `healthy`. `kailash-frontend` reports no health state at all,
which is consistent with the design's finding that it declares no `HEALTHCHECK`.
Requirement 1.5 therefore still fails, but for the one reason task 4.6 already
owns — a missing probe, not fourteen broken ones.

Task 4.1 should capture Phase A evidence before assuming the fourteen-unhealthy
starting point, and should record what changed between the requirements snapshot
and now. This observation is a `docker ps` status column, not a diagnosis; it
does not establish *why* the earlier state differed.

## What this record does not do

No route was added, moved or renamed. `backend/app/main.py`,
`backend/shared/app.py`, every router, and `docker-compose.yml` are unmodified by
task 3.3. Task 4.7 owns probe corrections; task 4.8 reads this record and, on
this verdict, makes no source change.
