"""Tests for backend.shared platform library."""
from __future__ import annotations

import pytest
from fastapi import APIRouter, Depends, FastAPI
from fastapi.testclient import TestClient

from backend.shared.app import build_app
from backend.shared.auth import require_internal_token
from backend.shared.config import BaseServiceSettings
from backend.shared.errors import NotFoundError, ValidationError


def _make_app(routers=None) -> FastAPI:
    settings = BaseServiceSettings(
        service_name="test-svc",
        version="9.9.9",
        env="test",
    )
    return build_app(settings, routers=routers or [])


def test_health_and_root():
    client = TestClient(_make_app())

    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "test-svc"
    assert body["version"] == "9.9.9"
    assert "uptime_s" in body

    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "test-svc"
    assert body["env"] == "test"


def test_metrics_endpoint():
    client = TestClient(_make_app())
    client.get("/health")  # generate at least one sample
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers["content-type"]
    assert "http_requests_total" in r.text


def test_request_id_propagation():
    client = TestClient(_make_app())
    r = client.get("/health", headers={"x-request-id": "abc-123"})
    assert r.headers.get("x-request-id") == "abc-123"

    r = client.get("/health")
    assert r.headers.get("x-request-id")


def test_platform_errors_mapped():
    router = APIRouter()

    @router.get("/boom-404")
    def boom_404():
        raise NotFoundError("nope")

    @router.get("/boom-422")
    def boom_422():
        raise ValidationError("bad", hint="fix me")

    client = TestClient(_make_app(routers=[lambda a: a.include_router(router)]))

    r = client.get("/boom-404")
    assert r.status_code == 404
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "not_found"

    r = client.get("/boom-422")
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["hint"] == "fix me"


def test_internal_token_guard(monkeypatch):
    monkeypatch.setenv("PLATFORM_INTERNAL_TOKEN", "s3cret")

    router = APIRouter()

    @router.get("/secret", dependencies=[Depends(require_internal_token)])
    def secret():
        return {"ok": True}

    client = TestClient(_make_app(routers=[lambda a: a.include_router(router)]))

    assert client.get("/secret").status_code == 401
    assert client.get("/secret", headers={"x-platform-token": "wrong"}).status_code == 401
    assert client.get("/secret", headers={"x-platform-token": "s3cret"}).status_code == 200
