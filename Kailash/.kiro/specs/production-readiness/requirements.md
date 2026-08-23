# Requirements Document

## Introduction

The Kailash monorepo ships a React 19 SPA to Firebase Hosting (project `kailash-29111`) and a FastAPI backend to a Vultr VPS running a 15-container Docker Compose stack behind Nginx and Let's Encrypt. Configuration for both targets is present in the repository, and the backend test suite passes (37 tests against containerized Postgres).

Two premises in the original text were wrong and are corrected here, because checks written against them would enforce the wrong values:

- The frontend targeted `kailash-38268`, which serves a stale "AEGIS HUB" build on no live domain. `kailash-ai.com` — where `kailash-ai.in` redirects — is served by `kailash-29111`, the only Firebase project the operator account can see. All four config sites now name `kailash-29111`.
- `api.kailash-ai.in` has no DNS record (`nslookup` → non-existent domain). The backend hostname baked into `frontend/.env.production` does not resolve, so the deployed SPA has no reachable API. Requirement 2 must verify the backend origin resolves before asserting anything about its content.

Production readiness is not established. Fourteen of the fifteen containers in the `kailash-ai` compose profile report Docker health state `unhealthy`. No staging environment exists, so every merge to `main` reaches production directly. The live status of both production domains has never been confirmed against the current build. Default database and cache credentials are embedded as compose fallback values. Nine per-service Dockerfiles reference pre-consolidation paths and cannot build. No rollback procedure is documented for either deployment target.

This specification defines what must be true for the platform to be considered production ready. It covers diagnosis and remediation of container health, verification that production actually serves the current build, prevention of the configuration-drift class of defect, credential handling, removal of dead build files, rollback capability for both targets, cleanup of untracked containers on the Docker host, introduction of a staging environment, and repository-state integrity at deploy time.

A Firebase project identifier mismatch in `frontend/.firebaserc` has already been corrected. Requirement 3 addresses prevention of that class of defect rather than the individual instance.

## Glossary

- **Kailash_Platform**: The complete deployed system, comprising the Frontend_App and the Compose_Stack.
- **Frontend_App**: The React 19 single-page application built from `frontend/` via CRACO and hosted on Firebase Hosting project `kailash-29111`.
- **Compose_Stack**: The 15 containers started by the `kailash-ai` profile of `docker-compose.yml`, all bound to `127.0.0.1`.
- **Backend_Service**: The FastAPI container named `kailash-backend`, listening on port 8000.
- **Platform_Services**: The nine containers `document-ai` (8101), `forecasting` (8102), `anomaly` (8103), `rag` (8104), `vision-gateway` (8105), `speech` (8106), `model-registry` (8107), `knowledge-graph` (8108), and `automobile-llm` (8109).
- **Data_Services**: The containers `kailash-postgres`, `kailash-redis`, and `kailash-mongo`.
- **Health_Check_Definition**: The `healthcheck` block declared for a container in `docker-compose.yml`, including its test command, interval, timeout, retries, and start period.
- **Health_Path**: The HTTP path a service exposes for liveness, as declared in that service's Health_Check_Definition.
- **Diagnosis_Record**: A written record in the repository capturing observed evidence for each unhealthy container.
- **CI_Pipeline**: The GitHub Actions workflow `.github/workflows/ci.yml` and its six jobs: lint, shared, services (nine-way matrix), backend, frontend, and compose-build.
- **Frontend_Deploy_Workflow**: The GitHub Actions workflow `.github/workflows/deploy-frontend.yml`.
- **Backend_Deploy_Workflow**: The GitHub Actions workflow `.github/workflows/deploy-backend.yml`.
- **Config_Drift_Check**: An automated check that compares a configuration value across every file that declares it and reports disagreement.
- **Secret_Scan**: An automated check that detects literal credential values in files tracked by git.
- **Deployment_Verification_Check**: An automated check that issues HTTP requests to production endpoints and compares observed responses against expected values.
- **Rollback_Procedure**: The documented sequence of commands that restores a previously deployed version of the Frontend_App or the Backend_Service.
- **Staging_Environment**: A deployment of the Kailash_Platform on hostnames distinct from `kailash-ai.in` and `api.kailash-ai.in`, used to validate a build before production release.
- **Production_Environment**: The deployment serving `kailash-ai.in`, `www.kailash-ai.in`, and `api.kailash-ai.in`.
- **Docker_Host**: The machine running the Docker daemon that hosts the Compose_Stack.
- **Orphaned_Container**: A container running on the Docker_Host that belongs to no compose file tracked in the repository.
- **Cleanup_Record**: A written record in the repository classifying each Orphaned_Container as retained or removed.
- **Working_Tree**: The state of the local git checkout, as reported by `git status --porcelain`.
- **Deployment_Critical_Path**: Any of `deploy/`, `.github/workflows/`, `frontend/.firebaserc`, `frontend/.env.production`, and `docker-compose.yml`.
- **Operator**: The person authorizing a deployment, credential rotation, or container removal.

## Requirements

### Requirement 1: Container Health Accuracy

**User Story:** As an operator, I want every container in the compose profile to report an accurate Docker health state, so that orchestration and monitoring reflect real service availability rather than a broken probe.

#### Acceptance Criteria

1. WHEN the health investigation completes, THE Diagnosis_Record SHALL contain, for each of the 14 containers currently reporting `unhealthy`, the container name, the exact health check test command, the observed exit code from `docker inspect --format '{{json .State.Health}}'`, and the observed command output.
2. THE Health_Check_Definition of each of the 15 containers in the Compose_Stack SHALL invoke an executable present in that container's image, verified by `docker exec <container> which <executable>` exiting with code 0.
3. WHEN a GET request is issued to `http://127.0.0.1:8000/api/health`, THE Backend_Service SHALL return HTTP status 200.
4. WHEN a GET request is issued to the Health_Path of each of the nine Platform_Services on its bound port on `127.0.0.1`, THE addressed service SHALL return HTTP status 200.
5. WHEN `docker compose --profile kailash-ai up -d` returns and 180 seconds elapse, THE Compose_Stack SHALL report Docker health state `healthy` for all 15 containers, verified by `docker ps --filter health=healthy --format '{{.Names}}'` listing 15 names.
6. WHILE a container reports Docker health state `starting`, THE Health_Check_Definition SHALL permit a start period of at least the container's measured time to first successful probe.
7. IF a container's Health_Path returns HTTP status 200 while the container reports `unhealthy`, THEN THE Diagnosis_Record SHALL identify the failing element of that container's Health_Check_Definition.
8. IF a container reports `unhealthy` after the Health_Check_Definition is corrected, THEN THE Diagnosis_Record SHALL name the container and state the blocking condition that prevents a healthy state.

### Requirement 2: Live Production Verification

**User Story:** As an operator, I want automated confirmation that production serves the current build, so that a green deployment pipeline is evidence of a working site rather than an assumption.

#### Acceptance Criteria

1. WHEN the Deployment_Verification_Check issues a GET request to `https://kailash-ai.in/`, THE Production_Environment SHALL return HTTP status 200 with a `Content-Type` header containing `text/html`.
2. WHEN the Deployment_Verification_Check issues a GET request to `https://www.kailash-ai.in/`, THE Production_Environment SHALL return HTTP status 200, 301, or 308.
3. WHEN the Deployment_Verification_Check issues a GET request to `https://api.kailash-ai.in/api/health`, THE Backend_Service SHALL return HTTP status 200.
4. THE hashed asset filenames referenced by the HTML served at `https://kailash-ai.in/` SHALL match the filenames in the `build/` directory produced by the most recent successful Frontend_Deploy_Workflow run.
5. THE TLS certificates presented by `kailash-ai.in`, `www.kailash-ai.in`, and `api.kailash-ai.in` SHALL each have a `notAfter` value at least 14 days later than the time of verification.
6. WHEN the Frontend_Deploy_Workflow completes and WHEN the Backend_Deploy_Workflow completes, THE CI_Pipeline SHALL run the Deployment_Verification_Check and record the exit code in the workflow run.
7. IF any request in the Deployment_Verification_Check returns a status outside the values specified in criteria 1 through 3, THEN THE Deployment_Verification_Check SHALL exit with a non-zero code and print the requested URL and the observed status code.

### Requirement 3: Configuration Drift Prevention

**User Story:** As a developer, I want configuration values that appear in multiple files to be checked for agreement automatically, so that a deploy never targets the wrong project or repository because one file was missed.

#### Acceptance Criteria

1. THE Config_Drift_Check SHALL compare the Firebase project identifier declared in `frontend/.firebaserc`, `frontend/.env.production`, `.github/workflows/deploy-frontend.yml`, and `backend/.env.example` and SHALL exit with code 0 only when all four values are identical.
2. THE Config_Drift_Check SHALL compare the GitHub repository slug declared in `deploy/vultr/deploy.sh` and in every other tracked file that references a `flywithvvk` or `urgaa-eka` repository path, and SHALL exit with code 0 only when all values equal `urgaa-eka/kailash`.
3. THE Config_Drift_Check SHALL confirm that the Firebase `appId` in `frontend/src/lib/firebase.js` carries the numeric project prefix matching the Firebase project identifier from criterion 1.
4. WHEN a pull request targets `main` and WHEN a commit is pushed to `main`, THE CI_Pipeline SHALL run the Config_Drift_Check as a required job.
5. WHEN the Config_Drift_Check runs against the current `main` branch, THE Config_Drift_Check SHALL exit with code 0.
6. IF the Config_Drift_Check exits with a non-zero code, THEN THE Frontend_Deploy_Workflow and THE Backend_Deploy_Workflow SHALL each terminate with a non-zero exit code before invoking any deployment command.
7. IF the Config_Drift_Check detects disagreement, THEN THE Config_Drift_Check SHALL print each file path together with the value found in that file.

### Requirement 4: Credential and Secret Handling

**User Story:** As a security reviewer, I want production credentials supplied exclusively from outside the repository, so that no default or committed value can reach a live environment.

#### Acceptance Criteria

1. THE file `docker-compose.yml` SHALL declare `POSTGRES_PASSWORD` and `REDIS_PASSWORD` as environment references without fallback values, verified by the strings `kailash_prod_2026` and `kailash_redis_2026` being absent from the file.  <!-- secret-scan: allow documents the credential incident being remediated -->
2. WHEN the Compose_Stack starts with `POSTGRES_PASSWORD` or `REDIS_PASSWORD` unset or empty, THE Compose_Stack SHALL exit with a non-zero code before any Data_Services container accepts a network connection.
3. THE Secret_Scan SHALL inspect every file tracked by git and SHALL exit with code 0 only when no file contains a literal credential value.
4. WHEN a pull request targets `main` and WHEN a commit is pushed to `main`, THE CI_Pipeline SHALL run the Secret_Scan as a required job.
5. THE tracked files containing credential placeholders SHALL be limited to files matching the pattern `*.env.example`, verified by the Secret_Scan reporting no other path.
6. WHEN the Production_Environment Postgres and Redis credentials are rotated to values distinct from the previous compose fallback values, THE Backend_Service SHALL return HTTP status 200 for a GET request to `https://api.kailash-ai.in/api/health`.
7. IF the Secret_Scan detects a literal credential value in a tracked file, THEN THE CI_Pipeline SHALL exit with a non-zero code and print the file path and line number.

### Requirement 5: Buildable Build Definitions

**User Story:** As a developer, I want every Dockerfile in the repository to build, so that no engineer wastes time on a file that describes a directory layout the project abandoned.

#### Acceptance Criteria

1. WHEN `docker compose --profile kailash-ai build` runs from the repository root, THE Compose_Stack SHALL build all nine Platform_Services from `backend/services/Dockerfile.service` using the `SERVICE` and `PORT` build arguments and SHALL exit with code 0.
2. THE repository SHALL contain, for every Dockerfile under `backend/services/`, a build that exits with code 0 when invoked with the build arguments declared for that file in `docker-compose.yml`.
3. THE per-service Dockerfiles that reference the pre-consolidation paths `platform/` and `services/` SHALL be removed from the repository or updated to build against the current directory layout.
4. WHEN the CI_Pipeline `compose-build` job runs, THE CI_Pipeline SHALL build every Dockerfile tracked under `backend/` and SHALL exit with code 0.
5. IF a tracked build file references a path absent from the repository, THEN THE CI_Pipeline SHALL exit with a non-zero code and print the build file path and the missing path.
6. THE file `docs/guides/docker-and-mcp.md` SHALL describe the build mechanism that the CI_Pipeline actually executes for the nine Platform_Services.

### Requirement 6: Rollback Capability

**User Story:** As an operator, I want a documented and rehearsed rollback for both deployment targets, so that a bad release is recoverable within minutes without rebuilding from source.

#### Acceptance Criteria

1. THE Rollback_Procedure SHALL be documented in the repository with the exact commands for the Frontend_App and for the Backend_Service, each command written so it can be executed without modification apart from a version identifier.
2. WHERE the Frontend_App is hosted on Firebase Hosting, THE Rollback_Procedure SHALL restore a prior release using a Firebase Hosting release rollback identified by release version.
3. WHEN a frontend rollback is initiated, THE Production_Environment SHALL serve the hashed asset filenames of the target release at `https://kailash-ai.in/` within 10 minutes.
4. THE Backend_Deploy_Workflow SHALL tag each deployed backend image with the deployed commit SHA, verified by `docker image inspect` reporting that tag on the Docker_Host.
5. WHERE the Backend_Service is deployed from a git reference by `deploy/vultr/deploy.sh`, THE Rollback_Procedure SHALL redeploy a named prior commit SHA or image tag.
6. WHEN a backend rollback to a named target completes, THE Backend_Service SHALL return HTTP status 200 for a GET request to `https://api.kailash-ai.in/api/health` and SHALL report the target commit SHA in the health response body.
7. WHEN a rollback rehearsal is performed for each target, THE Rollback_Procedure SHALL complete within 15 minutes measured from initiation to the health verification in criteria 3 and 6 returning success.
8. IF a rollback target version is unavailable on the Docker_Host or in Firebase Hosting release history, THEN THE Rollback_Procedure SHALL exit with a non-zero code and print the requested version identifier.

### Requirement 7: Docker Host Cleanup

**User Story:** As an operator, I want the Docker host to run only containers the project accounts for, so that resource use and open ports are explainable and no unknown process shares the machine with production.

#### Acceptance Criteria

1. WHEN the orphan review completes, THE Cleanup_Record SHALL classify each of `mcp-tunnel-cloudflared-1`, `mcp-tunnel-mcp-proxy-1`, `log-reader`, `nervous_dhawan`, `interesting_northcutt`, and `gifted_leavitt` as retained or removed.
2. WHERE a container is classified as retained, THE Cleanup_Record SHALL name the compose file or documentation entry that owns that container.
3. WHEN a container is proposed for removal, THE Cleanup_Procedure SHALL obtain explicit Operator confirmation before executing `docker rm`.
4. WHEN the Cleanup_Procedure completes, `docker ps --format '{{.Names}}'` SHALL list only the 15 Compose_Stack container names and the container names recorded as retained in the Cleanup_Record.
5. WHERE a retained container publishes a port, THE Cleanup_Record SHALL state the published port and the bind address for that container.
6. IF a container appears on the Docker_Host that the Cleanup_Record does not classify, THEN THE orphan review SHALL exit with a non-zero code and print the container name and image.

### Requirement 8: Staging Environment and Promotion Gate

**User Story:** As a developer, I want changes validated on a staging deployment before production release, so that production is never the first environment to run a new build.

#### Acceptance Criteria

1. THE Staging_Environment SHALL serve the Frontend_App and the Backend_Service on hostnames distinct from `kailash-ai.in`, `www.kailash-ai.in`, and `api.kailash-ai.in`.
2. THE Staging_Environment SHALL run the same 15 containers declared by the `kailash-ai` compose profile.
3. THE Staging_Environment SHALL read database and cache credentials from secret names distinct from the secret names used by the Production_Environment, verified by inspecting the workflow environment declarations.
4. WHEN a commit is pushed to `main`, THE CI_Pipeline SHALL deploy to the Staging_Environment before deploying to the Production_Environment.
5. THE production deployment jobs SHALL declare the staging deployment job and the Deployment_Verification_Check against the Staging_Environment as prerequisites, verified by the `needs` keys in `.github/workflows/deploy-frontend.yml` and `.github/workflows/deploy-backend.yml`.
6. WHEN the Deployment_Verification_Check runs against the Staging_Environment, THE Staging_Environment SHALL satisfy the response criteria of Requirement 2 for the staging hostnames.
7. IF the Deployment_Verification_Check against the Staging_Environment exits with a non-zero code, THEN THE production deployment jobs SHALL terminate before invoking any deployment command.
8. IF any of the six CI_Pipeline jobs exits with a non-zero code, THEN THE Frontend_Deploy_Workflow and THE Backend_Deploy_Workflow SHALL each terminate before invoking any deployment command.

### Requirement 9: Repository State Integrity at Deploy Time

**User Story:** As an operator, I want deployment blocked while deployment-critical files carry uncommitted changes, so that the code running in production matches a reviewed commit and destructive remote commands act on the intended repository.

#### Acceptance Criteria

1. WHEN a deployment is initiated, THE Working_Tree SHALL report no modifications under any Deployment_Critical_Path, verified by `git status --porcelain -- <path>` producing empty output for each path.
2. THE repository reference in `deploy/vultr/deploy.sh` SHALL equal `urgaa-eka/kailash`, verified by exact string match.
3. WHEN `deploy/vultr/deploy.sh` executes `git reset --hard`, `git clean -fd`, or `git clone`, THE script SHALL first confirm that the target directory is the expected repository checkout and SHALL exit with a non-zero code when the confirmation fails.
4. WHEN a change to a Deployment_Critical_Path is staged for commit, THE Operator SHALL confirm the change explicitly before the commit is created.
5. WHEN a deployment workflow starts, THE deployment workflow SHALL record the deployed commit SHA in the workflow run output.
6. IF `git status --porcelain` reports a modification under a Deployment_Critical_Path at deployment time, THEN THE deployment SHALL terminate with a non-zero exit code and print each modified path.

## Blocked External Dependencies

The following item is recorded so it is not lost. It is outside the scope of this specification and carries no requirements.

- **Kailash Console UI page** (`Kailash Console.dc.html`): The design source lives in an external Claude Design project that requires authentication unavailable from this environment. Neither the design source, nor `support.js`, nor `kailash-ai-logo-dark.png` exists anywhere in this repository. Work on this page is blocked pending access to the external design project or a decision to rebuild the page from a new design.
