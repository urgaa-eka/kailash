# services/knowledge-graph

Regulations, parts, HSN codes, workflows, certifications — as a graph.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/nodes` | Upsert `{id, labels, props}`. |
| `POST` | `/edges` | Upsert `{src, rel, dst, props}`. |
| `GET`  | `/neighbours/{id}?depth=N&rel=X` | BFS out to N hops. |
| `GET`  | `/stats` | Node/edge counts. |

Default storage is in-process. Set `KG_BACKEND=neo4j` + `NEO4J_URI/USER/PASSWORD`
and wire the adapter to go to a real Neo4j cluster.
