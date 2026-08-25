"""Typed platform exceptions; FastAPI handler maps them to ApiResponse."""
from __future__ import annotations


class PlatformError(Exception):
    code: str = "platform_error"
    status_code: int = 500

    def __init__(self, message: str, *, hint: str | None = None, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.hint = hint
        if code:
            self.code = code


class NotFoundError(PlatformError):
    code = "not_found"
    status_code = 404


class ValidationError(PlatformError):
    code = "validation_error"
    status_code = 422


class UpstreamError(PlatformError):
    code = "upstream_error"
    status_code = 502
