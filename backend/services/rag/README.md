# services/rag

Embeddings + shared vector store.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/upsert` | `{ docs: [{id, text, metadata}] }` — index documents. |
| `POST` | `/search` | `{ query, k }` — top-k cosine-similarity hits. |
| `GET`  | `/stats`  | Total indexed documents. |

Embeddings go through OpenRouter (`OPENROUTER_API_KEY`, model configurable
via `RAG_EMBED_MODEL`). Falls back to a deterministic hash embedding when
no key is set (useful for CI / offline).

Default store is in-process. Set `RAG_BACKEND=pgvector|pinecone|qdrant`
and implement the adapter to scale out.
