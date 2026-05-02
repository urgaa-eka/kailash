from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

from backend.shared import ApiResponse, require_internal_token

from .service import get_model, list_models, promote, register_model


class RegisterRequest(BaseModel):
    name: str
    version: str
    stage: str = "dev"
    metrics: dict[str, Any] = Field(default_factory=dict)
    tags: dict[str, Any] = Field(default_factory=dict)
    artifact_uri: str | None = None


class PromoteRequest(BaseModel):
    stage: str


def register(app: FastAPI) -> None:
    @app.post(
        "/models",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["model-registry"],
    )
    async def create(req: RegisterRequest):
        return ApiResponse(data=register_model(
            req.name, req.version, req.metrics, req.tags, req.artifact_uri, req.stage,
        ))

    @app.get("/models", response_model=ApiResponse, tags=["model-registry"])
    async def list_(name: str | None = None):
        return ApiResponse(data={"models": list_models(name)})

    @app.get("/models/{name}/{version}", response_model=ApiResponse, tags=["model-registry"])
    async def get_(name: str, version: str):
        return ApiResponse(data=get_model(name, version))

    @app.post(
        "/models/{name}/{version}/promote",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["model-registry"],
    )
    async def promote_(name: str, version: str, req: PromoteRequest):
        return ApiResponse(data=promote(name, version, req.stage))
