"""FastAPI app factory — every service uses build_app() for consistent wiring.

Wires: CORS, request-id middleware, platform error handler, /health + /
routes, Prometheus-style metrics at /metrics.
"""
from __future__ import annotations

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from .config import BaseServiceSettings
from .errors import PlatformError
from .logging import configure_logging, get_logger
from .schemas import ApiResponse, ErrorDetail, HealthResponse


_started_at = time.time()


def _metrics_text(counters: dict[str, int], histograms: dict[str, list[float]]) -> str:
    lines: list[str] = []
    for name, v in counters.items():
        lines.append(f"# TYPE {name} counter")
        lines.append(f"{name} {v}")
    for name, vs in histograms.items():
        if not vs:
            continue
        lines.append(f"# TYPE {name} summary")
        lines.append(f"{name}_count {len(vs)}")
        lines.append(f"{name}_sum {sum(vs):.6f}")
    return "\n".join(lines) + "\n"


def build_app(
    settings: BaseServiceSettings,
    *,
    title: str | None = None,
    routers: list[Callable[[FastAPI], None]] | None = None,
) -> FastAPI:
    configure_logging(settings.log_level, settings.log_json, settings.service_name)
    log = get_logger(settings.service_name)

    app = FastAPI(
        title=title or f"KAILASH-AI · {settings.service_name}",
        version=settings.version,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    counters: dict[str, int] = {"http_requests_total": 0, "http_errors_total": 0}
    histograms: dict[str, list[float]] = {"http_request_duration_seconds": []}

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        req_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        request.state.request_id = req_id
        t0 = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            counters["http_errors_total"] += 1
            raise
        dt = time.perf_counter() - t0
        counters["http_requests_total"] += 1
        histograms["http_request_duration_seconds"].append(dt)
        if response.status_code >= 500:
            counters["http_errors_total"] += 1
        response.headers["x-request-id"] = req_id
        log.info(
            "request",
            extra={
                "request_id": req_id,
                "route": request.url.path,
                "latency_ms": round(dt * 1000, 2),
                "event": "http",
            },
        )
        return response

    @app.exception_handler(PlatformError)
    async def _handle_platform_error(request: Request, exc: PlatformError):
        req_id = getattr(request.state, "request_id", None)
        payload = ApiResponse(
            ok=False,
            error=ErrorDetail(code=exc.code, message=exc.message, hint=exc.hint),
            request_id=req_id,
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.get("/health", response_model=HealthResponse, tags=["platform"])
    async def health() -> HealthResponse:
        return HealthResponse(
            service=settings.service_name,
            version=settings.version,
            uptime_s=round(time.time() - _started_at, 2),
        )

    @app.get("/", tags=["platform"])
    async def root():
        return {
            "service": settings.service_name,
            "version": settings.version,
            "env": settings.env,
        }

    @app.get("/metrics", tags=["platform"], response_class=PlainTextResponse)
    async def metrics():
        return _metrics_text(counters, histograms)

    for wire in routers or []:
        wire(app)

    log.info("service_start", extra={"event": "startup", "service": settings.service_name})
    return app
