"""Kailash backend shared library.

Re-exports the public surface that every service should use so the contract
stays uniform across the fleet.
"""
from .app import build_app
from .auth import require_internal_token
from .config import BaseServiceSettings
from .errors import NotFoundError, PlatformError, UpstreamError, ValidationError
from .logging import configure_logging, get_logger
from .schemas import ApiResponse, ErrorDetail, HealthResponse, PageInfo

__all__ = [
    "ApiResponse",
    "ErrorDetail",
    "HealthResponse",
    "PageInfo",
    "require_internal_token",
    "BaseServiceSettings",
    "configure_logging",
    "get_logger",
    "PlatformError",
    "NotFoundError",
    "ValidationError",
    "UpstreamError",
    "build_app",
]

__version__ = "0.1.0"
