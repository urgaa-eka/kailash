"""Knowledge Graph service — in-process graph with Cypher-ish path queries.

The production target is Neo4j + Cypher. For dev/tests we provide a
single-process adapter that stores nodes and edges and supports 1..N-hop
neighbour queries. Swap implementations by setting ``KG_BACKEND=neo4j``
and providing ``NEO4J_URI``, ``NEO4J_USER``, ``NEO4J_PASSWORD``.
"""
from __future__ import annotations

import threading
from collections import defaultdict, deque
from typing import Any

from backend.shared import NotFoundError, ValidationError


class InMemoryGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: dict[tuple[str, str, str], dict[str, Any]] = {}
        self._adj: dict[str, list[tuple[str, str]]] = defaultdict(list)  # src -> [(rel, dst)]
        self._lock = threading.Lock()

    def upsert_node(self, node_id: str, labels: list[str], props: dict[str, Any]) -> dict[str, Any]:
        if not node_id:
            raise ValidationError("node_id required")
        with self._lock:
            self._nodes[node_id] = {"id": node_id, "labels": labels, "props": props}
            return self._nodes[node_id]

    def upsert_edge(self, src: str, rel: str, dst: str, props: dict[str, Any]) -> dict[str, Any]:
        if src not in self._nodes or dst not in self._nodes:
            raise NotFoundError("src/dst must exist as nodes")
        key = (src, rel, dst)
        with self._lock:
            self._edges[key] = {"src": src, "rel": rel, "dst": dst, "props": props}
            self._adj[src].append((rel, dst))
        return self._edges[key]

    def neighbours(self, node_id: str, depth: int = 1, rel: str | None = None) -> dict[str, Any]:
        if node_id not in self._nodes:
            raise NotFoundError(f"node not found: {node_id}")
        if depth < 1 or depth > 5:
            raise ValidationError("depth must be 1..5")
        seen: set[str] = {node_id}
        frontier = deque([(node_id, 0)])
        nodes_out: list[dict[str, Any]] = []
        edges_out: list[dict[str, Any]] = []
        while frontier:
            nid, d = frontier.popleft()
            if d >= depth:
                continue
            for r, nxt in self._adj.get(nid, []):
                if rel and r != rel:
                    continue
                edges_out.append({"src": nid, "rel": r, "dst": nxt})
                if nxt not in seen:
                    seen.add(nxt)
                    nodes_out.append(self._nodes[nxt])
                    frontier.append((nxt, d + 1))
        return {"root": self._nodes[node_id], "nodes": nodes_out, "edges": edges_out}

    def stats(self) -> dict[str, int]:
        return {"nodes": len(self._nodes), "edges": len(self._edges)}


GRAPH = InMemoryGraph()
