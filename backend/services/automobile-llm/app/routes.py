from __future__ import annotations

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

from backend.shared import ApiResponse, require_internal_token

from .service import DEFAULT_MODEL, chat


class Message(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    model: str | None = None
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)


def register(app: FastAPI) -> None:
    @app.get("/model", response_model=ApiResponse, tags=["automobile-llm"])
    async def model():
        import os
        return ApiResponse(data={"default": DEFAULT_MODEL, "active": os.environ.get("AUTOMOBILE_LLM_MODEL", DEFAULT_MODEL)})

    @app.post(
        "/chat",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["automobile-llm"],
    )
    async def chat_route(req: ChatRequest):
        result = await chat(
            [m.model_dump() for m in req.messages],
            model=req.model,
            temperature=req.temperature,
        )
        return ApiResponse(data=result)
