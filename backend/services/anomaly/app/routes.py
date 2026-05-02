from __future__ import annotations

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

from backend.shared import ApiResponse, require_internal_token

from .service import detect


class DetectRequest(BaseModel):
    points: list[list[float]] = Field(..., description="Matrix of samples (rows) × features (cols).")
    contamination: float = Field(default=0.05, gt=0.0, lt=0.5)


def register(app: FastAPI) -> None:
    @app.post(
        "/detect",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["anomaly"],
    )
    async def detect_route(req: DetectRequest):
        res = detect(req.points, req.contamination)
        return ApiResponse(data=res.__dict__)
