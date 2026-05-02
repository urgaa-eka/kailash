"""Shared auth dependency — validates X-Platform-Token header."""
from __future__ import annotations

import os
from fastapi import Header, HTTPException, status


def require_internal_token(
    x_platform_token: str | None = Header(default=None, alias="X-Platform-Token"),
) -> None:
    """Validate internal platform token from env.
    
    - Dev/test: if PLATFORM_INTERNAL_TOKEN unset, allow all (no-op dep)
    - Prod: if PLATFORM_INTERNAL_TOKEN unset, raise 500 (fail-closed)
    """
    expected = os.environ.get("PLATFORM_INTERNAL_TOKEN")
    env_mode = os.environ.get("ENV", "dev").lower()
    
    # Fail-closed in production if token not configured
    if not expected and env_mode not in ("dev", "test"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Platform auth misconfigured: PLATFORM_INTERNAL_TOKEN not set",
        )
    
    # Allow if no token configured (dev/test mode)
    if not expected:
        return
    
    # Validate token
    if not x_platform_token or x_platform_token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing X-Platform-Token",
        )
