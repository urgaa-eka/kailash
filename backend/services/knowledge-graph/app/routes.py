from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

from backend.shared import ApiResponse, require_internal_token

from .service import GRAPH


class NodeIn(BaseModel):
    id: str
    labels: list[str] = Field(default_factory=list)
    props: dict[str, Any] = Field(default_factory=dict)


class EdgeIn(BaseModel):
    src: str
    rel: str
    dst: str
    props: dict[str, Any] = Field(default_factory=dict)


def register(app: FastAPI) -> None:
    @app.post(
        "/nodes",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["knowledge-graph"],
    )
    async def upsert_node(n: NodeIn):
        return ApiResponse(data=GRAPH.upsert_node(n.id, n.labels, n.props))

    @app.post(
        "/edges",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["knowledge-graph"],
    )
    async def upsert_edge(e: EdgeIn):
        return ApiResponse(data=GRAPH.upsert_edge(e.src, e.rel, e.dst, e.props))

    @app.get(
        "/neighbours/{node_id}",
        response_model=ApiResponse,
        tags=["knowledge-graph"],
    )
    async def neighbours(node_id: str, depth: int = 1, rel: str | None = None):
        return ApiResponse(data=GRAPH.neighbours(node_id, depth=depth, rel=rel))

    @app.get("/stats", response_model=ApiResponse, tags=["knowledge-graph"])
    async def stats():
        return ApiResponse(data=GRAPH.stats())
