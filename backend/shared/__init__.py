"""Kailash backend shared library.

Re-exports the public surface that every service should use so the contract
stays uniform across the fleet.
"""
from .schemas import ApiResponse, ErrorDetail, HealthResponse, PageInfo
from .auth import require_internal_token
from .config import BaseServiceSettings
from .logging import configure_logging, get_logger
from .errors import PlatformError, NotFoundError, ValidationError, UpstreamError
from .app import build_app

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
