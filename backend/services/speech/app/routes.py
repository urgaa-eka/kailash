from __future__ import annotations

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

from backend.shared import ApiResponse, require_internal_token

from .service import SUPPORTED_LANGS, synthesize, transcribe


class ASRRequest(BaseModel):
    audio_b64: str
    lang: str = Field(default="hi")


class TTSRequest(BaseModel):
    text: str
    lang: str = Field(default="hi")
    voice: str = Field(default="default")


def register(app: FastAPI) -> None:
    @app.get("/languages", response_model=ApiResponse, tags=["speech"])
    async def languages():
        return ApiResponse(data={"supported": SUPPORTED_LANGS})

    @app.post(
        "/asr",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["speech"],
    )
    async def asr(req: ASRRequest):
        return ApiResponse(data=transcribe(req.audio_b64, req.lang))

    @app.post(
        "/tts",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["speech"],
    )
    async def tts(req: TTSRequest):
        return ApiResponse(data=synthesize(req.text, req.lang, req.voice))
