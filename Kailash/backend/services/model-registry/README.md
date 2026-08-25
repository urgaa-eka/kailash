# services/model-registry

Lightweight SQLite-backed model registry (MLflow-shape API).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/models` | Register `{name, version, stage, metrics, tags, artifact_uri}`. |
| `GET`  | `/models?name=foo` | List versions. |
| `GET`  | `/models/{name}/{version}` | Fetch one. |
| `POST` | `/models/{name}/{version}/promote` | `{ stage }` — dev/staging/prod/archived. |

Set `MODEL_REGISTRY_DB` for a persistent path (defaults to `/tmp`). Mirror
this API onto a real MLflow server in production.
