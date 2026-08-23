# Rollback_Procedure

How to roll production back to a previously deployed version, within the
10-minute bound of Requirement 6.3. Two independent targets: the frontend on
Firebase Hosting, the backend on the Vultr VPS. Each command below is
executable without modification apart from a single substitutable token —
`<VERSION_ID>` for the frontend, `<COMMIT_SHA>` for the backend.

The Firebase project is `kailash-29111`, the project the deploy sources pin
(`frontend/.firebaserc`, `deploy-frontend.yml`; enforced by
`scripts/verify/config_drift.py`). Do not substitute another project id: the
historical drift value `kailash-38268` still appears in older planning text
and rolls back nothing that users see.

## 0. Precondition — verify the target exists

Before either rollback, confirm the identifier you are about to substitute
actually exists (Requirement 6.8). The check exits 0 when the target is
present, 1 (printing the identifier) when it is absent, 2 when a surface
could not be consulted:

```bash
python -m scripts.verify.rollback --target <VERSION_ID> --env production --check
```

For a backend target, pass the commit SHA instead:

```bash
python -m scripts.verify.rollback --target <COMMIT_SHA> --env production --check
```

Do not proceed on a non-zero exit. Exit 1 means the target does not exist to
roll back to; the output includes a near-miss hint when an available
identifier differs only by case or truncation. Exit 2 means the check could
not see one of the surfaces (no Firebase CLI login, no Docker daemon) —
resolve that first rather than guessing.

## 1. Frontend — Firebase Hosting

Hosting keeps release history, so a rollback is a pointer switch, not a
rebuild. Find the target version, newest first:

```bash
firebase hosting:releases:list --project kailash-29111
```

Roll live back to it:

```bash
firebase hosting:clone kailash-29111:live@<VERSION_ID> kailash-29111:live
```

Propagation is seconds to a couple of minutes, comfortably inside the
10-minute bound (Requirement 6.3).

## 2. Backend — Vultr VPS

Every deploy tags the backend image with the commit it was built from
(`kailash-backend:<full 40-hex sha>`), in `deploy/vultr/deploy.sh` and the
`deploy-backend.yml` SSH step. On the VPS (`/opt/kailash`), start the tagged
image without rebuilding:

```bash
BACKEND_IMAGE_TAG=<COMMIT_SHA> docker compose -f docker-compose.yml up -d --no-build backend
```

Use the full 40-character SHA: Docker resolves tags by exact string, so a
short SHA does not select the image a deploy tagged.

> **Dependency (task 10.5, operator-gated, not yet applied):** this command
> selects the tagged image only once the `backend` service in
> `docker-compose.yml` carries `image: kailash-backend:${BACKEND_IMAGE_TAG:-latest}`
> alongside its `build:` block. `docker-compose.yml` is a
> Deployment_Critical_Path, so that edit requires the Requirement 9.4
> confirmation gate. Until it lands, the backend has tagged images to roll
> back to but no compose key to run them with, and a backend rollback means
> re-deploying the target commit via `deploy/vultr/deploy.sh` with the branch
> reset to it.

### Image retention

Deploys retain the **3** most recent commit-tagged backend images (including
the one just deployed); older commit tags are pruned. Three is a conservative
default chosen because the task 4.5 disk-headroom record that is supposed to
size this number does not exist yet — the design proposed 10. When that
record lands, revisit `RETAINED_IMAGE_TAGS` in `deploy/vultr/deploy.sh` and
the matching prune in `.github/workflows/deploy-backend.yml`. A target older
than the retention window fails the precondition check and cannot be rolled
back to without a rebuild.

## 3. Verify after rollback

Confirm production actually serves the target release (Requirement 6.2):

```bash
python -m scripts.verify.deployment_check --env production --manifest <target-release-manifest>
```

`--manifest` takes the `asset-manifest.json` from the build of the release
you rolled back to; omit it only if the rollback was backend-only.

For a backend rollback, additionally confirm the running commit — the health
body reports it (Requirement 6.6):

```bash
curl -s https://api.kailash-ai.in/api/health
```

The `commit` field must equal the `<COMMIT_SHA>` you substituted. `unknown`
means the container was started without the deploy pipeline exporting
`GIT_COMMIT` — treat that as a failed rollback and investigate before
declaring the incident over.
