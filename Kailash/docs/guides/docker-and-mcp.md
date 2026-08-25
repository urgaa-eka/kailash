# Local stack: Docker profile + MCP gateway

Two things live here: the **`kailash-ai` Compose profile** (runs the whole
platform locally) and the **`kailash-ai` Docker MCP profile** (exposes the
running stack to AI clients as MCP tools). They share a name; they are
separate systems.

## 1. Compose profile — the full stack

```bash
docker compose --profile kailash-ai up -d --build
```

Brings up 15 containers. `POSTGRES_PASSWORD`, `REDIS_PASSWORD` and
`PLATFORM_INTERNAL_TOKEN` must be set in the environment first: compose
declares them `${VAR:?}` (required, no default), so every subcommand —
`up`, `build`, `config`, `ps` — refuses to parse without them.

| Service | Port (loopback) | Notes |
|---|---|---|
| `frontend` | 3000 | React SPA on nginx; proxies `/api/` → backend |
| `backend` | 8000 | Main FastAPI app (departments, GANESHA, guardians) |
| `company` | 8110 | Company-segment statutory ledger (`/dashboard`) |
| `document-ai` … `automobile-llm` | 8101–8109 | The 9 platform/ML services |
| `mongo` · `postgres` · `redis` | 27017 · 5432 · 6379 | Datastores |

Everything binds to `127.0.0.1` only. The profile is inert for a plain
`docker compose up -d`, so production deploys are unaffected.

**Datastore bootstrap** (fresh volumes only): Postgres enables `pgcrypto`
and `uuid-ossp` via `database/postgres_init.sql`; Mongo creates
collections and indexes via `database/mongodb_init.js`. On an existing
volume, apply them manually:

```bash
docker exec -i kailash-postgres psql -U kailash -d kailash \
  -c 'CREATE EXTENSION IF NOT EXISTS pgcrypto; CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
```

**Redis requires a password** (`REDIS_PASSWORD` — required, no default;
the published default it once shipped with was rotated out and is
denylisted). Connect with
`docker exec kailash-redis redis-cli -a "$REDIS_PASSWORD" ping`.

**Images.** The 9 platform services build from **one generic build file,
`backend/services/Dockerfile.service`** — this is the mechanism the CI
pipeline actually executes, not a per-service Dockerfile. Each service in
`docker-compose.yml` extends the `x-platform-service` YAML anchor and
passes two build args, `SERVICE` and `PORT`; the Dockerfile copies
`backend/services/${SERVICE}/` and bakes in a `HEALTHCHECK` probing
`http://localhost:${PORT}/health`. The nine per-service
`backend/services/<service>/Dockerfile` files were **removed**: they
copied from pre-consolidation paths (`platform/`, `services/<service>/`)
that no longer exist, no compose service referenced them, and two
definitions of the same image is drift by construction.
`scripts/verify/build_audit.py` fails CI if one is reintroduced.
`backend/services/company/Dockerfile` remains — it uses current paths and
compose references it.

## 2. Docker MCP profile — the stack as AI tools

Docker Desktop's MCP Toolkit (`docker mcp`) runs each MCP server as a
container and multiplexes them through one gateway.

```bash
# Profile with three servers pointed at this stack
docker mcp profile create --name kailash-ai \
  --server "catalog://mcp/docker-mcp-catalog/mongodb+redis+fetch"

# Connection details (config = plain values, secrets = credentials)
docker mcp profile config kailash_ai --set redis.host=host.docker.internal --set redis.port=6379
docker mcp secret set "mongodb.connection_string=mongodb://host.docker.internal:27017/kailash"
docker mcp secret set "redis.password=<your REDIS_PASSWORD>"

# Connect a client (writes the gateway entry into the client's config)
docker mcp client connect --global --profile kailash_ai claude-code

# Run the gateway
docker mcp gateway run --profile kailash_ai                       # stdio (what clients use)
docker mcp gateway run --profile kailash_ai --transport streaming --port 8812   # HTTP, for probing
```

### Sharing the profile

The profile is published as an OCI artifact, so another machine can adopt
the same server set without re-creating it:

```bash
docker mcp profile pull docker.io/ekadhi/kailash_ai:latest
docker mcp profile push kailash_ai docker.io/ekadhi/kailash_ai:latest   # after changes
```

Only server definitions and non-sensitive config travel with it —
`export`/`push` record secrets by *name* against the local
`docker-desktop-store` provider, never their values. Each machine must set
its own:

```bash
docker mcp secret set "mongodb.connection_string=mongodb://host.docker.internal:27017/kailash"
docker mcp secret set "redis.password=<your REDIS_PASSWORD>"
```

What each server gives you against the running stack: **mongodb** queries
the app database, **redis** inspects the cache/broker, **fetch** reaches
any service endpoint (use `host.docker.internal`, e.g.
`http://host.docker.internal:8110/health`).

### Notes from setting this up

- Containers reach host-published ports via `host.docker.internal`, never
  `localhost`.
- `--port` requires `--transport streaming`; the default stdio transport
  rejects it.
- `--profile` is mutually exclusive with `--servers`, `--config`,
  `--secrets` and friends — put connection details in the profile.
- The streaming gateway prints a Bearer token at startup and requires it
  on every request (or pass `--allow-unauthenticated`).
- `--long-lived` keeps server containers running between calls. Without
  it they are per-call; either way, orphans can accumulate — clean with
  `docker ps -q --filter label=docker-mcp=true | xargs -r docker rm -f`.
- Server config keys are typed: what the catalog lists under `secrets:`
  must be set with `docker mcp secret set`, and what it lists under `env:`
  with `docker mcp profile config --set`. Getting this backwards makes the
  server container start and then fail to connect.
- Cold start pulls server images and can take several minutes.
