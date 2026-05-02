"""RAG service — embeddings + cosine-similarity search.

In-memory store by default (fine for dev, small datasets, CI). Switch to
pgvector / Pinecone / Qdrant by implementing the ``VectorStore`` protocol
in ``store.py`` and configuring ``RAG_BACKEND``.

Embeddings are produced via OpenRouter (OpenAI-compatible ``/embeddings``)
when ``OPENROUTER_API_KEY`` is set. Otherwise a deterministic hash
embedding is used so tests and offline dev still pass.
"""
from __future__ import annotations

import hashlib
import os
import threading
from dataclasses import dataclass, field
from typing import Iterable

import httpx
import numpy as np

from backend.shared import UpstreamError, ValidationError, get_logger

log = get_logger("rag")

EMBED_DIM = 384


def _hash_embed(text: str, dim: int = EMBED_DIM) -> list[float]:
    """Deterministic embedding — not semantic, but stable for tests."""
    if not text:
        raise ValidationError("empty text")
    # SHA-256 produces 32 bytes per block; chain blocks until we have enough.
    needed = dim * 2  # uint16 → 2 bytes per value
    buf = b""
    counter = 0
    base = text.encode("utf-8")
    while len(buf) < needed:
        buf += hashlib.sha256(base + counter.to_bytes(4, "big")).digest()
        counter += 1
    arr = np.frombuffer(buf[:needed], dtype=np.uint16).astype(np.float32)
    arr = arr / (np.linalg.norm(arr) or 1.0)
    return arr[:dim].tolist()


async def embed_batch(texts: list[str]) -> list[list[float]]:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = os.environ.get("RAG_EMBED_MODEL", "openai/text-embedding-3-small")
    base = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key:
        return [_hash_embed(t) for t in texts]

    url = f"{base.rstrip('/')}/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "input": texts}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
        return [item["embedding"] for item in data["data"]]
    except Exception as e:
        log.warning("embed_fallback", extra={"event": "embed_fallback"})
        raise UpstreamError(f"embedding provider failed: {e}")


@dataclass
class Doc:
    id: str
    text: str
    metadata: dict
    vector: list[float] = field(default_factory=list)


class InMemoryStore:
    def __init__(self) -> None:
        self._docs: dict[str, Doc] = {}
        self._lock = threading.Lock()

    def upsert(self, docs: Iterable[Doc]) -> int:
        with self._lock:
            for d in docs:
                self._docs[d.id] = d
            return len(self._docs)

    def search(self, query_vec: list[float], k: int = 5) -> list[dict]:
        if not self._docs:
            return []
        q = np.asarray(query_vec, dtype=np.float32)
        q = q / (np.linalg.norm(q) or 1.0)
        scored: list[tuple[float, Doc]] = []
        for d in self._docs.values():
            v = np.asarray(d.vector, dtype=np.float32)
            v = v / (np.linalg.norm(v) or 1.0)
            score = float(np.dot(q, v))
            scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"id": d.id, "score": s, "text": d.text, "metadata": d.metadata}
            for s, d in scored[:k]
        ]

    def count(self) -> int:
        return len(self._docs)


STORE = InMemoryStore()
