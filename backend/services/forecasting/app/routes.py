from __future__ import annotations

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

from backend.shared import ApiResponse, require_internal_token

from .service import forecast


class ForecastRequest(BaseModel):
    series: list[float] = Field(..., description="Historical observations, oldest→newest.")
    horizon: int = Field(..., ge=1, le=365)
    season: int = Field(default=0, ge=0, le=52, description="0 = non-seasonal.")


def register(app: FastAPI) -> None:
    @app.post(
        "/forecast",
        response_model=ApiResponse,
        dependencies=[Depends(require_internal_token)],
        tags=["forecasting"],
    )
    async def forecast_route(req: ForecastRequest):
        res = forecast(req.series, req.horizon, season=req.season)
        return ApiResponse(data=res.__dict__)
