# Implementation Plan: Production Readiness

## Overview

The plan builds the `scripts/verify/` package and its test harness first, because every gate in this design is a Python check and a check that cannot be tested cannot be trusted. It then un-masks the three CI jobs that currently cannot fail, because until they can fail no gate designed here means anything. Only after that does it touch the deployment topology.

Three sequencing rules are load-bearing and are reflected in the task order and in the dependency graph:

1. **Requirement 1 gates Requirement 8.** The staging backend recommendation (Option D, second compose project on the same host) is conditional on the health diagnosis. Task 4.5 produces the H1 verdict; task 12.1 reads it and either confirms Option D or flips to Option C. No staging infrastructure task runs before 12.1.
2. **Un-masking CI comes early and is expected to go red.** Tasks 2.2, 2.3 and 2.4 each remove one `|| true` and each owns fixing whatever real failure surfaces. They are deliberately separate tasks touching one job each, so a red build is attributable to a single change.
3. **`common.py` and the test harness precede every check.** Tasks 1.1 and 1.2 come first so each check is testable from its first commit, and task 1.3 lands the `verify-scripts` job before any check is wired as a gate.

Three questions are open and must be answered by observation, not assumption. Tasks 3.2 (whether production is intended to run the profiled services), 3.3 (the backend health path) and 13.3 (ownership of the `mcp-tunnel-*` containers) resolve them. Downstream tasks are written to consume the answer rather than presume one.

### Task markers

| Marker | Meaning for the orchestrator |
| --- | --- |
| `[live-docker]` | Requires a reachable Docker daemon and the running stack. Do not dispatch on a runner without one. |
| `[live-network]` | Issues requests to real production or staging hostnames. |
| `[operator]` | Requires explicit operator confirmation before the action is taken. Never auto-execute. |
| `[destructive]` | Issues an irreversible command. Always paired with `[operator]`. |
| `*` | Design-flagged extension beyond the letter of the requirements. Droppable. |

---

## Tasks

- [ ] 1. Verification foundation: shared contract, test harness, CI job

  - [ ] 1.1 Create the `scripts/verify` package and shared contract
    - Create `scripts/verify/__init__.py` and `scripts/verify/common.py` with `Exit(IntEnum)` (`OK=0`, `FAILED=1`, `UNAVAILABLE=2`, `USAGE=3`), a frozen `Finding` dataclass (`rule`, `path`, `line`, `observed`, `expected`, `message`), and `Report` with `findings`, `suppressions`, `unavailable` and `exit_code()`
    - Implement the single output renderer producing `FAIL <rule> <path>:<line> observed=<v> expected=<v>`; this one format discharges every printing obligation in the spec
    - Implement `git ls-files -z` corpus enumeration under `--root`, UTF-8 skip-and-count, and the shared argparse surface `[--root PATH] [--json] [--emit-record PATH]` with `--root` defaulting to the git top level
    - Implement the guarantee that no check raises: wrap main in a handler mapping a missing prerequisite to `Exit.UNAVAILABLE` and a bad invocation to `Exit.USAGE`, so an unhandled traceback can never be mistaken for a check that was never wired up
    - Create `requirements-dev.txt` pinning `pytest==8.4.2` and `hypothesis`
    - Write `tests/verify/test_common.py`: exit-code precedence (unavailable outranks findings), renderer output for each `Finding` field combination, `--root` resolution, non-UTF-8 skip counting
    - _Requirements: 2.7, 3.7, 4.7, 5.5, 6.8, 7.6_

  - [ ] 1.2 Build the test harness the checks are tested through
    - Create `tests/verify/conftest.py` with the `tmp_repo` fixture: `git init` in `tmp_path`, helpers to write synthetic `frontend/.firebaserc`, `frontend/.env.production`, `.github/workflows/*.yml`, `backend/.env.example`, `docker-compose.yml` and arbitrary tracked files, then `git add`
    - Add the recording fake executor: captures `(args, kwargs)` per call, returns a scripted exit code, stdout and stderr, and asserts on calls not made. This is how "no `docker rm` without confirmation" is verified with no daemon
    - Add a `local_http_server` fixture on an ephemeral port returning scripted status, `Content-Type` and HTML body
    - Register `docker` and `network` markers with autouse skip when the prerequisite is absent, so the unit suite runs anywhere
    - Create `tests/verify/fixtures/` with `inspect_*.json` placeholders and `workflows/` for synthetic graphs
    - _Requirements: 3.5, 7.3, 9.1_

  - [ ] 1.3 Add the `verify-scripts` job to `ci.yml`
    - New job running `pip install -r requirements-dev.txt` then `pytest -q tests/verify -m "not docker and not network"` on push and pull request
    - This job must exist before any check is wired as a gate: a check whose own tests fail must not be trusted to gate a deployment
    - Do not add `needs:` edges from other jobs yet — tasks 5.4, 6.2 and 12.9 add them as those checks land
    - _Requirements: 3.4, 4.4, 8.8_

- [ ] 2. Toolchain prerequisite and CI failure un-masking

  - [ ] 2.1 Make yarn available locally without changing the lockfile
    - Run `corepack enable` then `corepack prepare yarn@1.22.22 --activate`, matching the `packageManager` field, `frontend/yarn.lock`, `frontend/Dockerfile` and `deploy-frontend.yml`
    - Add both commands to `CONTRIBUTING.md` as a prerequisite for any frontend command
    - Do not regenerate the lockfile or migrate to npm: the lockfile determines what production runs, and regenerating it to fix a `PATH` problem changes the deployed artifact to solve a workstation issue
    - Verify by running `yarn --version` and `yarn install --frozen-lockfile` in `frontend/`
    - _Requirements: 2.4_

  - [ ] 2.2 Un-mask the `ci.yml` backend job and fix what surfaces
    - Remove the `|| true` from the `Backend smoke tests` step in the `backend` job so `pytest ../tests/backend -q` can fail the job
    - **Expect this to go red.** Fixing the real test failures that surface is this task's work, not a surprise to escalate. Run the suite locally first, fix the failures in `tests/backend/` or in the code under test, and only then push
    - Change nothing else in `ci.yml`, so a red build is attributable to this one edit
    - _Requirements: 8.8_
    - _Property: 9_

  - [ ] 2.3 Un-mask the `ci.yml` frontend job and fix what surfaces
    - Remove the `|| true` from `yarn build` in the `frontend` job
    - Reproduce locally with the yarn from task 2.1 before pushing, then fix the real build failures. Note that `CI: false` is set in `deploy-frontend.yml` but not in `ci.yml`, so CRA treats warnings as errors in CI and not in the deploy build. Resolve that difference explicitly rather than by re-masking
    - Leave the Node version alone; task 5.5 owns the pin
    - _Requirements: 8.8_
    - _Property: 9_

  - [ ] 2.4 Un-mask the `deploy-backend.yml` test job and fix what surfaces
    - Remove the `|| true` from the `Run tests` step in the `test` job
    - Confirm the `deploy` job's `needs: test` now actually blocks: a failing test must skip the deploy job
    - _Requirements: 8.8_
    - _Property: 9_

  - [ ] 2.5 Checkpoint - all three gating jobs can fail, and pass
    - Ensure all tests pass, ask the user if questions arise.

- [ ] 3. Reconcile repository state and resolve the open questions

  - [ ] 3.1 Reconcile uncommitted Deployment_Critical_Path changes `[operator]`
    - The working tree currently carries uncommitted modifications under `.github/workflows/ci.yml`, `deploy/vultr/deploy.sh`, `deploy/vultr/setup-vps.sh`, `docker-compose.yml` and `frontend/.firebaserc`, plus untracked `backend/services/Dockerfile.service`, `docker-compose.override.yml`, `database/postgres_init.sql` and `docs/guides/docker-and-mcp.md`
    - Present a per-path diff summary and obtain explicit operator confirmation for each critical path before committing. `frontend/.firebaserc` is already corrected from `kailash-15365` to `kailash-38268` — commit it, do not re-fix it
    - `backend/services/Dockerfile.service` being untracked is blocking: `git ls-files` cannot see it, a CI checkout will not have it, and `deploy.sh`'s `git clean -fd` would delete it on the VPS. It must be tracked before any Requirement 5 work begins
    - Leave nothing modified under a critical path when this task completes, so `repo_state.py` has a clean baseline from its first run
    - _Requirements: 9.1, 9.4_

  - [ ] 3.2 Resolve whether production is intended to run the profiled services `[operator]`
    - Establish the fact first: neither `deploy/vultr/deploy.sh` nor `deploy-backend.yml` passes `--profile kailash-ai`, so the nine Platform_Services, `company` and `frontend` are not started by a deploy today. Confirm by reading both files, and by `docker compose -f docker-compose.yml ps` on the VPS if it is reachable
    - Ask the operator to decide between (a) production runs all 15 containers and both deploy paths gain `--profile kailash-ai`, and (b) production runs the unprofiled subset by design, and Requirement 8.2's "same 15 containers" means the compose profile's declared set rather than the production runtime set
    - Record the question, the evidence, the decision and its date in `docs/records/profiled-services-scope.md`
    - Do not pick an interpretation silently. Tasks 8.3 and 12.3 read this record for their service scope
    - _Requirements: 8.2, 5.1_

  - [ ] 3.3 Resolve the backend health path by observation `[live-docker]`
    - `backend/shared/app.py` mounts `/health` via `build_app()`, and no literal `/api/health` route exists anywhere in `backend/**/*.py`. The served path must be read from the running app, not inferred
    - Run `docker exec kailash-backend curl -s localhost:8000/openapi.json` and record the full path list. If the container is not reachable, start it and retry; if `curl` is absent from the image, use a `python -c urllib` equivalent
    - Record the observed paths and the verdict on hypothesis H5 in `docs/records/backend-health-path.md`
    - Change no route in this task. Task 4.8 acts on the answer, and only if the answer is that `/api/health` is not served
    - _Requirements: 1.3, 2.3_

- [ ] 4. Requirement 1 - container health diagnosis and remediation

  - [ ] 4.1 Build the Phase A evidence collector `[live-docker]`
    - Create `scripts/verify/health_diagnose.py` with the collector half only: for each of the 15 containers run the four `docker inspect` captures (`.State.Health`, `.Config.Healthcheck`, `.State`, `.RestartCount`) and write them verbatim to `docs/records/container-health-evidence.json` in the schema from the design's Data Models section
    - Read the effective probe from `.Config.Healthcheck`, not from `docker-compose.yml`: nine of the fourteen probes are baked into the image by `backend/services/Dockerfile.service`, so reading the compose file would investigate the wrong probe for nine containers
    - Capture host facts: `docker info` memory ceiling, `docker version`, and clock skew from `docker run --rm alpine date` against host time
    - Preserve `.State.Health.Log` in full including `Start`, `End`, `ExitCode` and `Output`. `End - Start` per attempt is the measurement task 4.3 needs
    - An unreachable daemon is `Exit.UNAVAILABLE`, classifying nothing
    - Test the collector with the fake executor from 1.2: assert the exact commands issued, and that malformed inspect output is preserved rather than raised
    - _Requirements: 1.1_

  - [ ] 4.2 Build the pure classifier, attribution, and Diagnosis_Record emission
    - Add the classifier to `health_diagnose.py` as a pure function from the captured JSON to `list[Finding]` plus record entries, with no subprocess calls. This separation is what makes all fourteen failure shapes testable from fixture JSON
    - Implement the design's decision tree: `which` non-zero, replay-succeeds-probe-fails, replay-succeeds-host-saturated, 200-on-a-different-path, non-200-on-the-probed-path, connection-refused, rendered-string-differs-from-intent
    - Implement executable extraction from `CMD`, `CMD-SHELL` and bare-string test forms, stable under surrounding whitespace, quoting and `${...}` references
    - Emit `docs/records/container-health-diagnosis.md` via `--emit-record` in the per-container section format from the design. `Attribution` must never be empty for a non-healthy container
    - Write `tests/verify/test_health_diagnose.py` fed `tests/verify/fixtures/inspect_*.json` covering: 200-but-unhealthy, executable absent, replay-succeeds-probe-fails, connection refused, an `HTTPError` traceback in `Output`, no healthcheck declared (`frontend`), and truncated or malformed inspect JSON
    - Add the property test asserting exactly one entry per non-healthy container, each carrying name, effective test, probe exit code, probe output and a non-empty attribution
    - _Requirements: 1.1, 1.2, 1.7, 1.8_
    - _Property: 1, 3_

  - [ ] 4.3 Implement the start-period rule
    - Add the rule comparing each container's declared `start_period` against its measured time to first successful probe, derived from the `probe_log` durations and first-success timestamp in the evidence JSON
    - Absent `start_period` is zero, not "skip": `postgres` and `redis` declare none today, and treating absence as a pass would hide exactly the case Requirement 1.6 covers
    - Property test over generated pairs of declared and measured values, including equality at the boundary
    - _Requirements: 1.6_
    - _Property: 2_

  - [ ] 4.4 Run Phase C replay and Phase D executable evidence `[live-docker]`
    - Extend the collector: for each failing container, extract `.Config.Healthcheck.Test`, replay it via `docker exec`, and record exit code, stdout, stderr and wall time. A failing `docker exec` is recorded verbatim as evidence, never raised
    - The replay is the decisive step because it separates three outcomes that `unhealthy` alone conflates: the service is fine and the probe invocation is at fault, the service is not listening, or the service is listening and rejecting the probed path
    - For all 15 containers including the passing ones, run `docker exec <c> which <exe>` and record exit code and output. Requirement 1.2 is a claim about all fifteen, so the evidence must cover all fifteen
    - Confirm `which wget` inside the `frontend` container, since task 4.6's probe depends on BusyBox `wget` being present in `nginx:alpine`
    - Regenerate the evidence JSON and the Diagnosis_Record
    - _Requirements: 1.1, 1.2, 1.7, 1.8_
    - _Property: 1, 3_

  - [ ] 4.5 Run Phase B uniform-cause probes and record the H1 verdict `[live-docker]`
    - Add the Phase B mode to `health_diagnose.py`: run once for the host rather than per container
    - H1 (host resource saturation): `docker stats --no-stream`, the `docker info` memory ceiling, and the measured wall time of each probe against its declared timeout. H9 (clock skew): compare container date to host date. H2: `docker compose --profile kailash-ai config`, read the rendered `redis` `test` string, then replay it inside the container
    - Fourteen probes failing across five heterogeneous mechanisms points at a common cause before fourteen independent ones. If H1 confirms, stop, record it, remediate the host, and re-run Phase A before editing any probe definition — that path costs five probes where the per-container path costs fourteen investigations
    - **This task produces the verdict that gates Requirement 8.** Write the H1 conclusion explicitly and unambiguously into `docs/records/container-health-diagnosis.md` under a `## Host resource assessment` heading, including available memory, CPU headroom and free disk. Task 12.1 reads it and cannot proceed until it exists
    - Record disk headroom as the input to the backend image tag retention depth in task 10.4
    - _Requirements: 1.1, 1.8_

  - [ ] 4.6 Give the `frontend` container a health probe `[live-docker]`
    - Add a `healthcheck` block to the `frontend` service in `docker-compose.yml` using the BusyBox `wget` form confirmed by task 4.4: `["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]`, interval 30s, timeout 5s, retries 3, start period 10s
    - `frontend` is not healthier than the others today: it is the only container with no probe at all, so it reports no health state and `docker ps --filter health=healthy` can list at most 14 names. Requirement 1.5 is unsatisfiable without this
    - Prefer the HTTP probe over `nginx -t`, which validates configuration syntax without proving the server answers requests
    - Verify with `docker compose --profile kailash-ai up -d frontend` and `docker inspect --format '{{.State.Health.Status}}'`
    - _Requirements: 1.2, 1.5_

  - [ ] 4.7 Apply the probe corrections the diagnosis attributes `[live-docker]`
    - For each container whose attribution names a failing element of its Health_Check_Definition, apply the corresponding remedy in `docker-compose.yml`, and in `backend/services/Dockerfile.service` for the nine image-level probes
    - Remedies come from the decision tree, not from guesswork: raise `timeout` to three times measured, add `start_period` at or above the measured first-success time, replace an absent executable, correct a compose interpolation, align a probe to the served path
    - Add `start_period` to `postgres` and `redis`, which declare none
    - For any container still unhealthy after correction, the Diagnosis_Record must name it and state the blocking condition rather than leaving it as "unhealthy"
    - Re-run `health_diagnose.py` and confirm the task 4.3 start-period rule now passes for every container
    - _Requirements: 1.2, 1.6, 1.7, 1.8_
    - _Property: 2, 3_

  - [ ] 4.8 Ensure `/api/health` is served, per the task 3.3 finding
    - Read `docs/records/backend-health-path.md`. If `/api/health` is already served, make no source change and record that in the task outcome
    - If it is not served, add the route rather than retargeting the probe: Requirements 2.3, 4.6 and 6.6, both deploy scripts, and the compose `backend` probe all already depend on that exact path, making it the more entrenched of the two
    - Add the route so it does not disturb the `/health` mount `build_app()` already provides to all ten services
    - Add a test asserting HTTP 200 from `/api/health` on the backend app via `TestClient`
    - _Requirements: 1.3, 2.3_

  - [ ] 4.9 Add the live-stack health integration tests `[live-docker]`
    - Create `tests/verify/test_health_integration.py` marked `@pytest.mark.docker`
    - Assert `docker exec <c> which <exe>` exits 0 for all 15 containers (1.2)
    - Assert HTTP 200 from each of the nine Platform_Services' Health_Path on its bound port on `127.0.0.1`, ports 8101 through 8109 (1.4)
    - Assert HTTP 200 from `http://127.0.0.1:8000/api/health` (1.3)
    - Assert that 180 seconds after `docker compose --profile kailash-ai up -d` returns, `docker ps --filter health=healthy --format '{{.Names}}'` lists 15 names (1.5)
    - _Requirements: 1.2, 1.3, 1.4, 1.5_

  - [ ] 4.10 Checkpoint - diagnosis recorded, H1 verdict written, stack healthy
    - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Requirement 3 - configuration drift check

  - [ ] 5.1 Implement `config_drift.py` with the project-id and repo-slug rules
    - Create `scripts/verify/config_drift.py` with the `DriftRule` and `Source` dataclasses from the design (`rule_id`, `sources`, `expected`, `required_sources`)
    - Rule `firebase-project-id`: extract `.projects.default` from `frontend/.firebaserc` (JSON), the `*FIREBASE_PROJECT_ID*` key from `frontend/.env.production` (dotenv), `projectId` under the hosting-deploy step in `.github/workflows/deploy-frontend.yml` (YAML), and `FIREBASE_PROJECT_ID` from `backend/.env.example`. Exit 0 only when all four are present and identical. A missing declaration is a finding, not a skip: skipping absent values would let the check pass by deleting a line, certifying agreement among three files while the fourth targets nothing
    - Rule `github-repo-slug`: scan every tracked file for `(?:github\.com[:/])(?P<owner>[\w.-]+)/(?P<name>kailash)(?:\.git)?\b` plus the bare `owner/kailash` form; every match must equal `urgaa-eka/kailash`. Declare `deploy/vultr/deploy.sh` a required source that must yield at least one match, because that script runs `git reset --hard`, `git clean -fd` and `git clone` against whatever it resolves, and a vacuous pass there is the most dangerous outcome in the whole check
    - Print every participating path together with the value found in it on any disagreement
    - Write `tests/verify/test_config_drift.py` using `tmp_repo`: per rule, one fixture that must exit 0 and one that must exit 1 with the path and value asserted in stdout, plus the missing-declaration and vacuous-required-source cases
    - Add the property test over four-element value assignments including `None`, asserting exit 0 iff all values are present and identical, and that every path and value appears in the rendered output
    - _Requirements: 3.1, 3.2, 3.7_
    - _Property: 7_

  - [ ] 5.2 Implement the `firebase-app-identity` rule
    - Create `scripts/verify/data/project_map.json` containing `{"kailash-38268": "172604807567"}` as the reviewed record of the one-time console lookup. Adding an environment then means adding a line and a reviewer noticing
    - Add the rule to `config_drift.py`: `appId.split(":")[1]` in `frontend/src/lib/firebase.js` must equal `messagingSenderId` in the same file, and must equal `project_map.json[project_id]`
    - Do not attempt to derive the project number from the project id: `kailash-38268` and `172604807567` are unrelated strings and no string operation maps one to the other
    - Test the passing case, a partial copy-paste where `appId` and `messagingSenderId` disagree, an id absent from the map, and a malformed `appId`
    - Add the property test over generated `appId`, `messagingSenderId` and project-number triples
    - _Requirements: 3.3_
    - _Property: 8_

  - [ ] 5.3 Assert the drift check exits 0 against the real repository
    - Add `tests/verify/test_config_drift.py::test_passes_on_real_repository` running the check with `--root` set to the repository root and asserting `Exit.OK`
    - If it fails, the finding is a real defect: fix the disagreeing file, do not relax the rule
    - _Requirements: 3.5_
    - _Property: 7_

  - [ ] 5.4 Add the `config-drift` job to `ci.yml`
    - New job running `python -m scripts.verify.config_drift` on pull request to `main` and on push to `main`, with `needs: verify-scripts`
    - _Requirements: 3.4_

  - [ ]* 5.5 Add the `node-version` rule and pin CI's frontend Node to 20
    - Design-flagged extension beyond the letter of Requirement 3, droppable without touching rules 3.1 through 3.3
    - Live instance of the same defect class: `ci.yml`'s frontend job pins Node 18, `deploy-frontend.yml` pins 20, `frontend/Dockerfile` uses `node:20-alpine`. CI is validating a build on a runtime no deployment uses
    - Change `ci.yml`'s frontend `node-version` to `"20"`, then add the rule requiring the CI frontend job and the deploy workflow to agree, with the deployed version authoritative
    - Test the agreeing and disagreeing cases against synthetic workflow files
    - _Requirements: 3.4_

- [ ] 6. Requirement 4 - credential handling and secret scan

  - [ ] 6.1 Implement `secret_scan.py`
    - Create `scripts/verify/secret_scan.py` operating over the `git ls-files -z` corpus from `common.py`. Untracked files are out of scope by definition: 4.3 says "every file tracked by git"
    - Detector 1, denylist: literals from `scripts/verify/data/denylist.txt`, seeded with `kailash_prod_2026` and `kailash_redis_2026`, applied to every file including lockfiles. Rotation never adds the new value here — a denylist of live credentials would itself be the leak
    - Detector 2, structured patterns: `-----BEGIN [A-Z ]*PRIVATE KEY-----`, `AIza[0-9A-Za-z_\-]{35}`, `gh[pousr]_[A-Za-z0-9]{36,}`, `AKIA[0-9A-Z]{16}`, `xox[baprs]-`, and `"type"\s*:\s*"service_account"`
    - Detector 3, assignment heuristic: a key matching `(PASSWORD|SECRET|TOKEN|API_?KEY|PRIVATE_KEY|CREDENTIAL)` assigned a value that is not a placeholder, not an environment reference (`${...}`, `os.environ`, `secrets.`, `vars.`), and at least 8 characters
    - Detector 4, compose strictness: any strict-required compose variable declared with a `:-` default is a finding, so a reverted default is caught by the same job as task 6.3's edit
    - The placeholder exemption requires both conditions: the path matches `*.env.example` **and** the value matches the placeholder grammar (`""`, `changeme`, `CHANGE_ME`, `REPLACE_ME`, `<...>`, `your-*`, `xxx*`, `***`). A real credential in `.env.example` is still a finding, and a placeholder anywhere else is still reported, which is how 4.5's "no other path" is verified
    - Suppression via `# secret-scan: allow <reason>` on the same or preceding line, counted and printed even on success, so a growing suppression list is visible rather than a silent path to green
    - Exempt lockfiles from detectors 2 and 3, since integrity hashes trip entropy heuristics, but never from the denylist
    - Write `tests/verify/test_secret_scan.py`: corpora seeded with each detector's pattern at known line numbers asserting the exact reported line, near-miss corpora (a password-shaped variable assigned `${VAR}`) that must not fire, and the full placeholder matrix over path times value
    - Add the property test over generated credential-shaped strings and their placeholder near-misses
    - _Requirements: 4.1, 4.3, 4.5, 4.7_
    - _Property: 10_

  - [ ] 6.2 Add the `secret-scan` job to `ci.yml`
    - New job running `python -m scripts.verify.secret_scan` on pull request to `main` and on push to `main`, with `needs: verify-scripts`
    - _Requirements: 4.4_

  - [ ] 6.3 Make credentials strictly required in compose
    - Replace `${VAR:-default}` with `${VAR:?VAR must be set}` for `POSTGRES_PASSWORD` and `REDIS_PASSWORD` at all four occurrence sites in `docker-compose.yml`: `postgres.environment`, `redis.command`, `backend.environment` (`REDIS_URL`, `POSTGRES_URL`) and `company.environment` (`COMPANY_DB_URL`). Confirm the literals `kailash_prod_2026` and `kailash_redis_2026` no longer appear in the file
    - `:?` aborts during configuration parsing, before any container is created, which is exactly what 4.2 requires and is stronger than a runtime guard that needs a container to exist first
    - Apply `:?` to `PLATFORM_INTERNAL_TOKEN` in the same edit: it currently defaults to empty, and `require_internal_token` comparing an empty expected token against an absent header is an authentication bypass waiting for a caller who omits the header
    - `:?` makes every compose subcommand require the variables, including `config`, `build` and `ps`. In the same task add `POSTGRES_PASSWORD`, `REDIS_PASSWORD` and `PLATFORM_INTERNAL_TOKEN` throwaway values to the `compose-build` job's `env:` block in `ci.yml`, so CI does not break between this task and task 8.3
    - State the three variables as a hard precondition in `docs/DEPLOYMENT.md`. This is a deliberate trade: the failure moves from silently deploying with a published default password to a loud failure at parse time
    - This edits `docker-compose.yml`, a Deployment_Critical_Path, so the task 7.3 confirmation gate applies to the commit
    - _Requirements: 4.1, 4.2_
    - _Property: 10_

  - [ ] 6.4 Add the unset-credential integration test `[live-docker]`
    - Add a `@pytest.mark.docker` test asserting that `docker compose --profile kailash-ai config` and `up -d` with `POSTGRES_PASSWORD` unset or empty exit non-zero
    - Assert no Data_Services container was created, by comparing `docker ps -a` container names before and after
    - _Requirements: 4.2_

- [ ] 7. Requirement 9 - repository state integrity

  - [ ] 7.1 Implement `repo_state.py`
    - Create `scripts/verify/repo_state.py` with `CRITICAL_PATHS = ("deploy/", ".github/workflows/", "frontend/.firebaserc", "frontend/.env.production", "docker-compose.yml")`
    - Run `git status --porcelain -- <path>` per path; any output is a finding naming the modified path. Handle rename entries (`R  old -> new`, both sides checked) and quoted paths containing spaces
    - Prefix matching must be path-segment aware: `deploy/` must not match a hypothetical `deployment-notes.md`
    - Implement the git remote URL normaliser mapping `git@github.com:urgaa-eka/kailash.git`, `https://github.com/urgaa-eka/kailash.git` and `https://github.com/urgaa-eka/kailash` to the same `urgaa-eka/kailash` slug, and assert `deploy/vultr/deploy.sh` carries that exact slug
    - Write `tests/verify/test_repo_state.py` over synthetic `git status --porcelain` outputs: renames, quoted paths with spaces, staged versus unstaged, and the `deployment-notes.md` prefix collision
    - Add the property tests for working-tree cleanliness and for URL normalisation across all forms. The normaliser is worth a property test because one that silently returns the unmodified URL makes task 7.2's guard reject every valid checkout, turning a safety feature into an outage
    - _Requirements: 9.1, 9.2, 9.6_
    - _Property: 17, 18_

  - [ ] 7.2 Add the destructive-operation guard to `deploy.sh`
    - Add `assert_expected_checkout()` to `deploy/vultr/deploy.sh` and call it before each of `git reset --hard`, `git clean -fd` and `git clone`. It must exit non-zero when the target directory is not a git work tree and when the normalised origin slug is not `urgaa-eka/kailash`
    - `git clean -fd` in the wrong directory destroys untracked files with no recovery, which is why the guard precedes the operation rather than reporting after it
    - Add the clone-path guard: assert `$APP_DIR` is absent or empty before `git clone`. Today a non-empty `$APP_DIR` without `.git` makes the clone fail after `install_prerequisites` has already run
    - Add the load-bearing repo-state placement: invoke `repo_state.py` inside `deploy.sh` after `git reset --hard`, where a reported modification means somebody edited files on the production server. Terminate the deploy non-zero, printing each modified path
    - Test the guard with a shell test or a Python wrapper over the fake executor: valid checkout passes; wrong slug, non-work-tree, and non-empty clone target each exit non-zero
    - _Requirements: 9.1, 9.2, 9.3, 9.6_
    - _Property: 17, 18_

  - [ ] 7.3 Add the critical-path commit confirmation hook
    - Add a `pre-commit` hook that fails when staged paths intersect `CRITICAL_PATHS`, with a message instructing the operator to re-run with `CONFIRM_CRITICAL_PATH=1` in the environment. Wire it through the existing `.pre-commit-config.yaml`
    - Use an environment token rather than an interactive prompt: pre-commit hooks have no reliable TTY, from an IDE's git integration a prompt hangs or silently fails, and a safety gate that hangs gets disabled. Setting a variable is a deliberate, auditable act with the same intent and none of the fragility
    - State plainly in the failure message that `--no-verify` bypasses the hook and that the unbypassable enforcement is the CI `preflight` job plus branch protection. The hook exists to catch the accidental case, which is the common one
    - Test with the recording executor that no commit is created for a staged critical path without the token, and that the commit proceeds with it
    - _Requirements: 9.4_
    - _Property: 15_

- [ ] 8. Requirement 5 - buildable build definitions

  - [ ] 8.1 Implement `build_audit.py`
    - Create `scripts/verify/build_audit.py`, static with no daemon so it runs on every push
    - Enumerate tracked `Dockerfile*` under `backend/` and the repository root; for each, find the compose service referencing it and take that service's `context` and `args`
    - Parse `COPY` and `ADD` source operands, substituting declared `ARG` values, and assert each source resolves inside the declared context. Report the build file together with the missing path
    - Check all nine `SERVICE` values against `backend/services/Dockerfile.service`. Argument substitution is why this is worth writing rather than relying on the real build: `COPY backend/services/${SERVICE}/requirements.txt` only resolves for the nine known values, and the audit checks all nine in milliseconds where nine real builds take minutes
    - A tracked build file that no compose service references and whose paths do not resolve is a finding, so a reintroduced dead Dockerfile fails CI
    - Write `tests/verify/test_build_audit.py` over synthetic contexts and argument-templated `COPY` paths, including a deliberately reintroduced `COPY platform /opt/platform` asserted to be reported with its build file
    - Add the property test over generated build-context and source-path pairs
    - _Requirements: 5.2, 5.3, 5.5_
    - _Property: 11_

  - [ ] 8.2 Remove the nine dead per-service Dockerfiles
    - Delete `backend/services/<service>/Dockerfile` for `document-ai`, `forecasting`, `anomaly`, `rag`, `vision-gateway`, `speech`, `model-registry`, `knowledge-graph` and `automobile-llm`. They copy from `platform/` and `services/<service>/`, neither of which exists post-consolidation, and no compose service references them
    - Remove rather than update: Requirement 5.3 permits either, but two definitions of the same image is drift by construction, the exact class Requirement 3 exists to eliminate. `Dockerfile.service` is the single definition
    - Keep `backend/services/company/Dockerfile`, which uses current paths (`/srv`, `backend.services.company.app.main`) and is referenced by compose
    - Confirm `build_audit.py` reports no findings afterwards
    - _Requirements: 5.3_
    - _Property: 11_

  - [ ] 8.3 Fix the `compose-build` job to build what it claims to build
    - Add `--profile kailash-ai` to the `docker compose build` invocation in `ci.yml`'s `compose-build` job. Without it the profile-gated services are inert, so the nine Platform_Services, `company` and `frontend` are not built in CI today, and 5.1 and 5.4 are unverified rather than satisfied
    - Add `python -m scripts.verify.build_audit` as a step before the build: it fails in seconds on a path error that would otherwise surface minutes into a layer build
    - Read `docs/records/profiled-services-scope.md` from task 3.2 and confirm the built service set matches the recorded decision
    - Confirm the throwaway credential `env:` block added by task 6.3 is present, since `:?` makes `build` require the variables
    - _Requirements: 5.1, 5.4_

  - [ ] 8.4 Correct `docs/guides/docker-and-mcp.md` to describe the real build mechanism
    - Describe `backend/services/Dockerfile.service` with the `SERVICE` and `PORT` build arguments and the `x-platform-service` YAML anchor as the mechanism the CI pipeline actually executes for the nine Platform_Services
    - State that the per-service Dockerfiles were removed, and why
    - Add a test asserting the document contains the required content, so the description cannot silently drift from the mechanism
    - _Requirements: 5.6_

  - [ ] 8.5 Checkpoint - every tracked build file builds, drift and secret gates are live
    - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Requirement 2 - deployment verification check

  - [ ] 9.1 Implement `deployment_check.py` status and content-type rules
    - Create `scripts/verify/deployment_check.py` with `--env {production|staging}`, the frozen `Endpoint` dataclass (`url`, `allowed_statuses`, `content_type`, `check_certificate`), and the two-entry `ENVIRONMENTS` table from the design. One check with two environment tables is how 8.6 is satisfied by construction rather than by a parallel implementation that can drift
    - Production: `https://kailash-ai.in/` expecting 200 with `Content-Type` containing `text/html`; `https://www.kailash-ai.in/` expecting 200, 301 or 308; `https://api.kailash-ai.in/api/health` expecting 200. Staging: the same allowed sets against `staging.kailash-ai.in`, `www.staging.kailash-ai.in` and `staging-api.kailash-ai.in`
    - Do not follow redirects: following them would let a 301 to an unrelated host pass as 200
    - Report every out-of-set status with its URL and observed code, and exit 1
    - Classify DNS and connection failures as `Exit.UNAVAILABLE`, not `FAILED`. A green pipeline that went red because the runner lost egress is a different event from production being down, and conflating them trains people to ignore the check
    - Test with the `local_http_server` fixture over scripted statuses and content types. Add the property test asserting exit 0 iff every observed status is in the allowed set and every content-type expectation is met, that each offending URL and status is printed, and that corresponding staging and production endpoints carry identical allowed sets
    - _Requirements: 2.1, 2.2, 2.3, 2.7, 8.6_
    - _Property: 4_

  - [ ] 9.2 Implement the asset-manifest containment rule
    - Parse the served HTML for `src` and `href` values matching the CRA hashed pattern `\.[0-9a-f]{8,}\.(js|css)`, and require that set to be contained in `asset-manifest.json` from the deploying build
    - Containment, not equality: the manifest legitimately lists assets the entry HTML does not reference, such as lazy chunks and source maps, so requiring equality would fail on every code-split build
    - Take the manifest from the build artifact in the same CI run, or from `--manifest` when run by hand
    - Test with scripted HTML bodies and synthetic manifests, including a served asset absent from the manifest and a manifest superset. Add the containment property test
    - _Requirements: 2.4_
    - _Property: 5_

  - [ ] 9.3 Implement the certificate margin rule
    - Read `notAfter` from `ssl.SSLSocket.getpeercert()` per hostname, parse it, and compare against now plus 14 days for `kailash-ai.in`, `www.kailash-ai.in` and `api.kailash-ai.in`
    - Report days remaining rather than a bare pass or fail, so the output is useful before it is failing
    - Test against synthesised `notAfter` values straddling the boundary, never against live certificates. Add the property test over generated expiry and verification timestamps
    - _Requirements: 2.5_
    - _Property: 6_

  - [ ] 9.4 Run the check against live production `[live-network]`
    - Invoke `python -m scripts.verify.deployment_check --env production` against the real endpoints and record the outcome
    - This is the first confirmation that production actually serves the current build. Treat any finding as a real defect to report, not as a check to relax
    - Keep this a marked smoke invocation, never a unit test
    - _Requirements: 2.1, 2.2, 2.3, 2.5_
    - _Property: 4, 6_

- [ ] 10. Requirement 6 - rollback mechanics

  - [ ] 10.1 Report the deployed commit in the health response
    - Add `GIT_COMMIT` as a build `ARG` and `ENV` in the root `Dockerfile`
    - Add an optional `commit` field to `HealthResponse` in `backend/shared/schemas.py` and populate it from `os.environ.get("GIT_COMMIT", "unknown")` in the `/health` handler in `backend/shared/app.py`
    - This is the one additive application change in the design. It exists because Requirement 6.6 needs the health body to identify what is actually running, the single most useful fact during an incident. Change no route logic, no UI, no data model
    - Add the image-tag derivation helper and its inverse, so a tag parses back to the SHA it came from
    - Test via `TestClient` that the field is present and reflects the environment variable, that `unknown` is returned when unset, and add the property test that a SHA round-trips through tag derivation and back, in full, short and mixed-case forms
    - _Requirements: 6.4, 6.6_
    - _Property: 12_

  - [ ] 10.2 Implement the `rollback.py` precondition check
    - Create `scripts/verify/rollback.py` with `--target <id> --env <env> --check`, resolving the identifier against Firebase Hosting release history and local Docker image tags, exiting non-zero and printing the requested identifier when absent
    - Keep it a checker, not an automation wrapper. Requirement 6.1 wants documented commands an operator runs, and an operator mid-incident should execute commands they can read rather than trust a script to orchestrate a rollback. The script answers "does this target exist", the question that is tedious and error-prone by hand, and stops there
    - Split collector from classifier so available-set resolution is testable without Firebase or Docker
    - Test over available-set fixtures with present, absent and near-miss identifiers. Add the membership property test
    - _Requirements: 6.8_
    - _Property: 13_

  - [ ] 10.3 Write the Rollback_Procedure runbook
    - Create `docs/runbooks/rollback.md` with the exact commands for both targets, each executable without modification apart from a version identifier
    - Frontend: `firebase hosting:releases:list --project kailash-38268` to find the target, then `firebase hosting:clone kailash-38268:live@<VERSION_ID> kailash-38268:live`. One substitutable token, and propagation is seconds to a couple of minutes, comfortably inside the 10-minute bound
    - Backend: `BACKEND_IMAGE_TAG=<COMMIT_SHA> docker compose -f docker-compose.yml up -d --no-build backend`
    - Include the `rollback.py --check` precondition invocation before each, and the `deployment_check.py --env production --manifest <target-release-manifest>` verification after
    - Add a test asserting the runbook contains both command forms and the single-token substitution property
    - _Requirements: 6.1, 6.2, 6.5_

  - [ ] 10.4 Tag deployed backend images by commit SHA
    - In `deploy-backend.yml`, pass `GIT_COMMIT: ${{ github.sha }}` as a build argument and tag the built image `kailash-backend:<sha>` in addition to `:latest`
    - Prune to the most recent tags, with the retention depth set from the disk headroom recorded by task 4.5 rather than an arbitrary number. The design proposes 10 as a starting point
    - Write `github.sha` to `$GITHUB_STEP_SUMMARY` so the deployed commit appears in the workflow run output
    - Verify the tag exists on the host with `docker image inspect kailash-backend:<sha>`
    - _Requirements: 6.4, 9.5_
    - _Property: 12_

  - [ ] 10.5 Make a prior image tag runnable without a rebuild `[operator]`
    - Add an `image: kailash-backend:${BACKEND_IMAGE_TAG:-latest}` key alongside the existing `build:` block for the `backend` service in `docker-compose.yml`, and pass `GIT_COMMIT: ${GIT_COMMIT:-unknown}` as a build arg
    - Today `deploy.sh` rebuilds from git HEAD, so there is nothing to roll back to, only something to rebuild. This key is what makes a prior tag runnable
    - This edits `docker-compose.yml`, a Deployment_Critical_Path, so the Requirement 9.4 confirmation gate from task 7.3 applies to the commit
    - Verify `BACKEND_IMAGE_TAG=<sha> docker compose -f docker-compose.yml up -d --no-build backend` starts the tagged image and that `/api/health` reports that SHA
    - _Requirements: 6.5, 6.6, 9.4_
    - _Property: 12_

- [ ] 11. Workflow topology - gates and CI linkage

  - [ ] 11.1 Implement `workflow_gate.py`
    - Create `scripts/verify/workflow_gate.py` parsing `.github/workflows/*.yml` into a job graph and asserting, by reachability rather than by review habit: every job containing a deployment command (`firebase ... deploy`, `hosting:clone`, `action-hosting-deploy`, `ssh-action`, `docker compose ... up`) has `preflight`, `ci-gate`, `deploy-staging` and `verify-staging` as transitive `needs`; every production deployment job is preceded by its staging counterpart; no job in the gating set contains a step masking a non-zero exit (`|| true`, `continue-on-error: true`, a trailing `exit 0`); and a verification job follows each deployment job
    - No network, pure graph reachability over parsed YAML
    - Write `tests/verify/test_workflow_gate.py` over synthetic graphs in `tests/verify/fixtures/workflows/`: a missing `needs` edge, a masked gating job, production ordered before staging, a deploy job with no verification successor, plus cycles and orphan jobs
    - Add the property test over generated workflow graphs. Do not assert against the real workflow files yet — task 12.9 does that once the staging jobs exist
    - _Requirements: 2.6, 3.4, 3.6, 4.4, 8.4, 8.5, 8.7, 8.8_
    - _Property: 9_

  - [ ] 11.2 Make `ci.yml` callable as a gate
    - Add `workflow_call` to `ci.yml`'s triggers alongside `push` and `pull_request`. Today `ci.yml` and the deploy workflows are independent, separately triggered workflows, so a deploy does not wait for CI
    - Change no job bodies in this task
    - _Requirements: 8.8_
    - _Property: 9_

  - [ ] 11.3 Add `preflight`, `ci-gate` and `verify-production` to `deploy-frontend.yml`
    - Add a `preflight` job running `config_drift.py`, `secret_scan.py` and `repo_state.py`
    - Add a `ci-gate` job with `uses: ./.github/workflows/ci.yml` and `needs: preflight`, which transitively pulls in `verify-scripts`
    - Add a `verify-production` job running `deployment_check.py --env production` with `needs` on the deploy job, taking `asset-manifest.json` from the build artifact in the same run. Its exit code is the job's exit code, which is what recording the exit code in the workflow run means in Actions terms
    - Make the existing `build-and-deploy` job `needs: [preflight, ci-gate]`, and write `github.sha` to `$GITHUB_STEP_SUMMARY`
    - Leave the staging edges to task 12.6
    - _Requirements: 2.6, 3.6, 9.5_
    - _Property: 9_

  - [ ] 11.4 Add `preflight`, `ci-gate` and `verify-production` to `deploy-backend.yml`
    - The same three jobs as 11.3, with `verify-production` running `deployment_check.py --env production`
    - Make the existing `deploy` job `needs: [preflight, ci-gate, test]`, and write `github.sha` to `$GITHUB_STEP_SUMMARY`
    - Leave the staging edges to task 12.6
    - _Requirements: 2.6, 3.6, 9.5_
    - _Property: 9_

- [ ] 12. Requirement 8 - staging environment and promotion gate

  - [ ] 12.1 Confirm or flip the backend staging option from the H1 verdict `[operator]`
    - Read the `## Host resource assessment` section of `docs/records/container-health-diagnosis.md` written by task 4.5 before doing anything else in this epic
    - If H1 is refuted and the host has headroom, confirm **Option D**: a second compose project on the same host, `docker compose -p kailash-staging --profile kailash-ai --env-file .env.staging up -d`, with a port offset and hard resource ceilings
    - If H1 is confirmed and the host is resource-saturated, **flip to Option C**: a second VPS. Adding a second full stack to a host that cannot sustain one is the wrong move. This is a real dependency, not a preference
    - Record the verdict read, the option chosen and the reasoning in `docs/records/staging-topology-decision.md`, and obtain operator confirmation for the choice, since Option C carries provisioning cost
    - Tasks 12.3 and 12.5 read this record. Do not start them before it exists
    - _Requirements: 8.1, 8.2_

  - [ ] 12.2 Configure the named Firebase staging channel
    - Configure a named `staging` channel on Firebase project `kailash-38268`, giving the stable hostname `https://kailash-38268--staging.web.app`. Named channels keep a fixed URL; only unnamed ones get hash suffixes
    - Set channel expiry to 30 days and refresh it on every staging deploy, so an abandoned staging URL expires rather than silently serving an ancient build. Task 12.8 records the expiry decision for operator sign-off
    - Wire the deploy command through the existing `firebase:preview` script in `frontend/package.json`, adjusting `frontend/firebase.json` only if the channel requires it
    - Option A over a second Firebase project: Requirement 8.1 asks only for a distinct hostname, and a named channel provides one at zero infrastructure cost. A second project would make the Firebase project identifier stop being a single global value and double the configuration surface, which is the defect class this spec exists to close
    - Leave the workflow job wiring to task 12.6
    - _Requirements: 8.1_
    - _Property: 16_

  - [ ] 12.3 Create the staging compose overlay
    - Create `deploy/staging/docker-compose.staging.yml` as an overlay applied on top of `docker-compose.yml`, so the service set stays identical and only ports and limits differ
    - Offset every published port by +1000 bound to `127.0.0.1` (backend `127.0.0.1:9000:8000`, Platform_Services 9101 through 9109, `company` 9110), and declare `deploy.resources.limits` for cpus and memory per service. The resource-contention risk of Option D is mitigated explicitly, not hoped away
    - Read `docs/records/profiled-services-scope.md` from task 3.2 for the service set. Requirement 8.2's "same 15 containers" resolves against the recorded decision, not against an assumption
    - If task 12.1 selected Option C, produce the second-VPS equivalent instead: the same overlay without port offsets, plus the host provisioning steps under `deploy/staging/`
    - Compose namespaces volumes by project, so `kailash-staging_postgres_data` is created fresh. Note in the overlay header that staging is therefore the only environment that exercises the `docker-entrypoint-initdb.d` first-boot path in `database/postgres_init.sql` and `database/mongodb_init.js`, and that any schema, index or extension applied to production by hand and never added to those scripts will be absent from staging. That divergence is a defect for the init scripts to absorb, and surfacing it on an ordinary Tuesday rather than during disaster recovery is a benefit of this design
    - Staging receives no copy of production data
    - Verify with `docker compose -p kailash-staging -f docker-compose.yml -f deploy/staging/docker-compose.staging.yml --profile kailash-ai config`
    - _Requirements: 8.1, 8.2_
    - _Property: 16_

  - [ ] 12.4 Declare the staging credential set under distinct secret names
    - Create `deploy/staging/.env.staging.example` and declare the `STAGING_*` secret names in the workflows: `STAGING_POSTGRES_PASSWORD`, `STAGING_REDIS_PASSWORD`, `STAGING_PLATFORM_INTERNAL_TOKEN`, `STAGING_VULTR_HOST`, `STAGING_VULTR_USER`, `STAGING_VULTR_SSH_KEY`, `STAGING_FIREBASE_SERVICE_ACCOUNT`
    - The production and staging secret-name sets must be disjoint, which is exactly the verification Requirement 8.3 specifies: readable from the workflow `env:` blocks
    - Create GitHub Environments `staging` and `production` carrying their respective secrets, so the production environment can additionally require a reviewer
    - `.env.staging.example` must satisfy the task 6.1 placeholder grammar, since `*.env.example` is the only exempt path pattern
    - _Requirements: 8.3_
    - _Property: 16_

  - [ ] 12.5 Route the staging hostnames `[operator]` `[live-network]`
    - Add `deploy/vultr/nginx-staging.conf` routing `staging-api.kailash-ai.in` to the offset backend port, modelled on the existing `nginx-api.conf`
    - Extend `deploy/vultr/setup-vps.sh` with the certbot invocation for the staging hostname, leaving the production certificate lifecycle untouched
    - Requires the operator to add the DNS A record and to run certbot on the host. Do not attempt certificate issuance from CI
    - If task 12.1 selected Option C, apply the same routing on the second VPS instead
    - _Requirements: 8.1_
    - _Property: 16_

  - [ ] 12.6 Add `deploy-staging` and `verify-staging` to both deploy workflows
    - In `deploy-frontend.yml`: a `deploy-staging` job deploying to the named channel with `STAGING_FIREBASE_SERVICE_ACCOUNT`, then `verify-staging` running `deployment_check.py --env staging`, then make `build-and-deploy` (production) `needs: [preflight, ci-gate, deploy-staging, verify-staging]`
    - In `deploy-backend.yml`: a `deploy-staging` job bringing up the `kailash-staging` compose project with the overlay and the `STAGING_VULTR_*` secrets, then `verify-staging`, then make `deploy` (production) `needs: [preflight, ci-gate, test, deploy-staging, verify-staging]`
    - Satisfy 8.7 and 8.8 through the dependency graph rather than through in-job conditionals: Actions skips a job whose `needs` failed, so a failure anywhere upstream terminates the run before any deployment command executes, and that holds for the next job someone adds
    - Confirm that a deliberately failing `verify-staging` skips the production job
    - _Requirements: 8.4, 8.5, 8.6, 8.7, 8.8_
    - _Property: 9_

  - [ ] 12.7 Add the staging isolation rule to `workflow_gate.py`
    - Assert that the staging and production hostname sets are disjoint under normalisation, that their credential secret-name sets are disjoint, and that their compose service-name sets are identical
    - Extract hostnames from the `ENVIRONMENTS` table in `deployment_check.py` and secret names from the parsed workflow `env:` blocks, so the rule reads the same declarations Requirement 8.3 names as the verification source
    - Test over synthetic pairs including an overlapping hostname, a shared secret name, and a service present in one set only. Add the property test
    - _Requirements: 8.1, 8.2, 8.3_
    - _Property: 16_

  - [ ] 12.8 Write the staging runbook
    - Create `docs/runbooks/staging.md` covering deploying to staging, the promotion path to production, the `STAGING_*` credential model, and the fresh-volume init-script behaviour with the expected early divergence finding
    - Document the credential rotation procedure with its ordering constraint stated explicitly: Postgres password rotation requires `ALTER ROLE` inside the running database before the compose value changes, or the backend cannot reconnect. Sequence: generate, `ALTER ROLE`, store in the GitHub environment secret, update the VPS `.env`, `docker compose up -d` the affected services, verify `/api/health`
    - Record the accepted limitation of Option A: staging and production share the Firebase project, so Auth configuration and Firestore rule changes are not validated by staging. Note the revisit trigger
    - Record the 30-day channel expiry decision for operator sign-off, and note that expiry becomes a surprise if a staging URL is shared externally
    - Note that `docker-compose.override.yml` is auto-merged locally but not in production, because `deploy.sh` and `deploy-backend.yml` both pass `-f docker-compose.yml` explicitly. Local and production stacks therefore differ in published ports, and that is correct as it stands — say so, so nobody "fixes" it by removing the `-f`
    - _Requirements: 4.6, 8.1, 8.2, 8.3_

  - [ ] 12.9 Enforce the workflow graph in CI
    - Add `python -m scripts.verify.workflow_gate` to the `config-drift` job in `ci.yml`
    - Add `tests/verify/test_workflow_gate.py::test_real_workflows_are_gated` asserting against the actual `.github/workflows/*.yml` files, now that the staging jobs exist. This is what makes Requirement 8.8 a checked property instead of a review habit
    - Confirm no job in the gating set masks a non-zero exit, which closes the loop on tasks 2.2, 2.3 and 2.4
    - _Requirements: 2.6, 3.4, 3.6, 4.4, 8.4, 8.5, 8.7, 8.8_
    - _Property: 9_

  - [ ] 12.10 Checkpoint - production is reachable only through staging
    - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Requirement 7 - Docker host cleanup

  - [ ] 13.1 Implement `orphan_review.py` and the retained-container schema
    - Create `scripts/verify/orphan_review.py`. A container is accounted for when its `com.docker.compose.project.config_files` label resolves to a compose file tracked in this repository, or its name appears in `scripts/verify/data/retained_containers.json`. Anything else exits 1, printing name and image
    - Use label-based ownership, not name matching: names are cosmetic, and a container named `kailash-backend` started by hand from an unrelated compose file is not the stack's backend
    - Create `scripts/verify/data/retained_containers.json` with the schema from the design (`name`, `image`, `owner`, `published_ports`, `justification`, `reviewed`) and a JSON Schema alongside it, so a malformed entry fails the check rather than being silently ignored. A retained entry that fails to parse would otherwise reappear as an unaccounted container or, worse, be skipped
    - Generate `docs/records/docker-host-cleanup.md` from that file via `--emit-record`. One source, one derived document: a hand-written record plus a machine-read list is two sources that will disagree
    - Require a non-empty `owner` on every retained entry, and a published port with bind address whenever that container publishes one. That field is what makes "what is listening on this box" answerable
    - Split collector from classifier so classification is testable from container-list fixtures with no daemon
    - Write `tests/verify/test_orphan_review.py` over container-list fixtures, and add the accountability property test
    - _Requirements: 7.1, 7.2, 7.4, 7.5, 7.6_
    - _Property: 14_

  - [ ] 13.2 Implement the removal confirmation gate
    - Implement `remove(candidates, *, confirmed, execute)` returning an empty list and issuing no command when `confirmed` is false, with `execute` injected
    - Confirmation is per-run and explicit: `--yes` alone is insufficient, the run must also name the containers it intends to remove, so a stale `--yes` cannot remove something added since
    - Test with the recording executor: zero `docker rm` calls without confirmation, exactly the named containers with it, and no call when the named set does not match the observed candidate set. This is how the guarantee is verified without a daemon and without removing anything
    - Add the property test that no destructive command is issued without explicit confirmation for that specific set
    - _Requirements: 7.3_
    - _Property: 15_

  - [ ] 13.3 Classify the six named containers from evidence `[live-docker]`
    - For `mcp-tunnel-cloudflared-1`, `mcp-tunnel-mcp-proxy-1`, `log-reader`, `nervous_dhawan`, `interesting_northcutt` and `gifted_leavitt`, collect labels, image, `Created`, `Command` and published ports, and search the repository documentation for a claim of ownership
    - Resolve `mcp-tunnel-*` ownership from labels and `docs/guides/docker-and-mcp.md`, not from the name. The name plausibly points at the documented Docker MCP tunnel, but "plausibly" is not evidence
    - `nervous_dhawan`, `interesting_northcutt` and `gifted_leavitt` carry Docker-generated names that suggest ad-hoc `docker run`, but "suggests" is not evidence and `docker rm` is not reversible. Classify each from what the labels actually say
    - Populate `retained_containers.json` for every container classified as retained, with its owner, published ports and bind addresses, then regenerate the Cleanup_Record
    - Produce the removal candidate list without executing anything
    - _Requirements: 7.1, 7.2, 7.5_
    - _Property: 14_

  - [ ] 13.4 Execute the confirmed removals `[operator]` `[destructive]`
    - Present the candidate list with each container's image, created time, command and published ports, and obtain explicit operator confirmation naming the specific containers. `docker rm` is irreversible; do not auto-execute
    - Run the removal only for the confirmed set, then regenerate `docs/records/docker-host-cleanup.md`
    - Verify `docker ps --format '{{.Names}}'` lists only the 15 Compose_Stack names plus the names recorded as retained
    - _Requirements: 7.3, 7.4_
    - _Property: 15_

- [ ] 14. Operator-gated production actions

  - [ ] 14.1 Rotate the Postgres and Redis credentials `[operator]` `[live-network]`
    - Rehearse on staging first, following the ordering in `docs/runbooks/staging.md`. Rehearsing on staging is a concrete reason staging exists
    - Rotate to values distinct from the previous compose fallbacks `kailash_prod_2026` and `kailash_redis_2026`, then confirm HTTP 200 from `https://api.kailash-ai.in/api/health`
    - Do not add the new values to `data/denylist.txt`: a denylist of live credentials would itself be the leak
    - Confirm the secret scan still exits 0 and that the rotated values appear in no tracked file
    - _Requirements: 4.6_
    - _Property: 10_

  - [ ] 14.2 Rehearse and time the rollback for both targets `[operator]` `[live-network]`
    - Rehearse against staging, not production. Rehearsing on production would mean deliberately serving a stale release to users to prove we can serve a stale release
    - Frontend: run `rollback.py --check`, then `firebase hosting:clone`, then verify the target release's hashed asset filenames are served within 10 minutes via `deployment_check.py --manifest <target-release-manifest>`
    - Backend: run `rollback.py --check`, then `BACKEND_IMAGE_TAG=<sha> docker compose up -d --no-build backend`, then verify HTTP 200 from `/api/health` with the target commit SHA in the response body
    - Measure each rehearsal from initiation to successful health verification and confirm both complete within 15 minutes
    - Record the commands run, the timings and any deviation from the runbook in `docs/records/rollback-rehearsal.md`, and correct the runbook wherever the rehearsal diverged from it
    - _Requirements: 6.2, 6.3, 6.5, 6.6, 6.7_
    - _Property: 12, 13_

  - [ ] 14.3 Final checkpoint - every gate is live and every record is generated
    - Ensure all tests pass, ask the user if questions arise.

---

## Notes

- Every leaf task cites the requirement clauses it satisfies and, where it implements one, the design property it establishes.
- Test work lives in the same task as the code it tests, per the design's Testing Strategy. There is no trailing "write the tests" task, because a check landing untested is a check producing confident green output before anyone has reason to believe it.
- Task order encodes the two hard dependencies: 4.5 before 12.1 before any staging infrastructure, and 1.1 through 1.3 before any check is wired as a gate.
- Tasks 2.2, 2.3 and 2.4 are each expected to turn CI red. Fixing what surfaces is the task's own work.
- Marked tasks (`[live-docker]`, `[live-network]`, `[operator]`, `[destructive]`) must not be dispatched to an environment that cannot satisfy the prerequisite, and the operator-gated ones must never be auto-executed.
- Task 5.5 is the only optional task. It is a design-flagged extension beyond the letter of Requirement 3 and can be dropped without affecting requirement coverage.
- The Kailash Console UI page is a blocked external dependency recorded in requirements.md with no requirements attached, so no task covers it.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["3.1"] },
    { "id": 1, "tasks": ["1.1", "2.1", "2.2", "3.2"] },
    { "id": 2, "tasks": ["1.2", "2.3", "3.3"] },
    { "id": 3, "tasks": ["1.3", "4.1"] },
    { "id": 4, "tasks": ["2.4", "4.2", "5.1", "7.1"] },
    { "id": 5, "tasks": ["4.3", "5.2", "6.1", "7.2", "8.1", "9.1"] },
    { "id": 6, "tasks": ["4.4", "5.3", "7.3", "8.2", "9.2", "10.1", "11.1", "11.2"] },
    { "id": 7, "tasks": ["4.5", "4.6", "5.4", "9.3", "10.2"] },
    { "id": 8, "tasks": ["4.7", "6.2", "8.4", "9.4", "10.3", "12.1"] },
    { "id": 9, "tasks": ["6.3", "11.3", "12.2", "13.1"] },
    { "id": 10, "tasks": ["4.8", "8.3", "11.4", "12.3", "13.2"] },
    { "id": 11, "tasks": ["4.9", "6.4", "10.4", "12.4", "12.5", "13.3"] },
    { "id": 12, "tasks": ["5.5", "10.5", "12.6", "12.7", "13.4"] },
    { "id": 13, "tasks": ["12.8", "12.9"] },
    { "id": 14, "tasks": ["14.1", "14.2"] }
  ]
}
```
