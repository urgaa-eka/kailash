"""Response envelope and shared data models."""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    hint: str | None = None


class ApiResponse(BaseModel, Generic[T]):
    ok: bool = True
    data: T | None = None
    error: ErrorDetail | None = None
    request_id: str | None = None


class HealthResponse(BaseModel):
    service: str
    status: str = "ok"
    version: str
    uptime_s: float = 0.0


class PageInfo(BaseModel):
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=500, default=50)
    total: int = 0
