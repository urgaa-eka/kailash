from __future__ import annotations

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

from backend.shared import ApiResponse, require_internal_token

from .service import MODELS, build_messages, call_openrouter, choose


class InferRequest(BaseModel):
    prompt: str = ""
    image_url: str | None = None
    tier: str | None = Field(default=None, description="fast | balanced | long (auto if None)")


def register(app: FastAPI) -> None:
    @app.get("/models", response_model=ApiResponse, tags=["vision-gateway"])
    async def models():
        return ApiResponse(data={"tiers": MODELS})

    @app.post(
        "/route",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["vision-gateway"],
    )
    async def route(req: InferRequest):
        decision = choose(req.tier, req.prompt)
        return ApiResponse(data=decision.__dict__)

    @app.post(
        "/infer",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["vision-gateway"],
    )
    async def infer(req: InferRequest):
        decision = choose(req.tier, req.prompt)
        messages = build_messages(req.prompt, req.image_url)
        result = await call_openrouter(decision.model, messages)
        return ApiResponse(data={"route": decision.__dict__, "result": result})
