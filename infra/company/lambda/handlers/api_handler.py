"""API Lambda — the full company-segment FastAPI surface behind API Gateway.

Mangum adapts API Gateway (REST, payload v1) events to ASGI, so every
endpoint of backend/services/company runs unchanged on Lambda.
"""
from __future__ import annotations

from handlers.common import resolve_db_url

resolve_db_url()

from mangum import Mangum  # noqa: E402

from backend.services.company.app.main import app  # noqa: E402

handler = Mangum(app, lifespan="off")
