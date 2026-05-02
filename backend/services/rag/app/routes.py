from __future__ import annotations

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

from backend.shared import ApiResponse, require_internal_token

from .service import Doc, STORE, embed_batch


class UpsertDoc(BaseModel):
    id: str
    text: str
    metadata: dict = Field(default_factory=dict)


class UpsertRequest(BaseModel):
    docs: list[UpsertDoc]


class SearchRequest(BaseModel):
    query: str
    k: int = Field(default=5, ge=1, le=50)


def register(app: FastAPI) -> None:
    @app.post(
        "/upsert",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["rag"],
    )
    async def upsert(req: UpsertRequest):
        vectors = await embed_batch([d.text for d in req.docs])
        docs = [Doc(id=d.id, text=d.text, metadata=d.metadata, vector=v) for d, v in zip(req.docs, vectors)]
        total = STORE.upsert(docs)
        return ApiResponse(data={"upserted": len(docs), "total": total})

    @app.post(
        "/search",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["rag"],
    )
    async def search(req: SearchRequest):
        qvec = (await embed_batch([req.query]))[0]
        hits = STORE.search(qvec, k=req.k)
        return ApiResponse(data={"hits": hits, "count": len(hits)})

    @app.get("/stats", response_model=ApiResponse, tags=["rag"])
    async def stats():
        return ApiResponse(data={"documents": STORE.count()})
