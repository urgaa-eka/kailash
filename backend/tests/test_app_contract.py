"""Contract tests for the backend app that need no external service.

These exist because of how the department integration suite failed. Its login
fixture posted `kailash_code`, the endpoint had moved to `login_id`, and the
resulting 422 was converted into a skip. Eleven tests reported "skipped", the
step exited 0, and nothing recorded that the suite had stopped testing anything.

Every assertion here runs against the real app in-process with no MongoDB, no
network and no mocks, so `pytest tests -q` reports genuine passes rather than
only skips. That is what makes the un-masked `backend` CI job able to fail:
without it, the step's exit code is independent of whether the app works.
"""
import pytest
from app.main import app
from fastapi.testclient import TestClient

# Deliberately not a context manager. Entering the lifespan would try to reach
# MongoDB and burn every startup timeout before giving up, and none of the
# assertions below touch the database.
client = TestClient(app)


def test_api_health_returns_200():
    """`/api/health` is the path both deploy scripts and the compose probe use."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_alias_returns_200():
    """`/health` is the path `build_app()` mounts for the platform services."""
    assert client.get("/health").status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        "/api/auth/login",
        "/api/departments/",
        "/api/departments/{department_id}",
        "/api/departments/{department_id}/summary",
    ],
)
def test_expected_routes_are_mounted(path: str):
    """The routes the department integration suite exercises actually exist.

    A skipping integration suite cannot notice a route being renamed or a router
    failing to mount. This can.
    """
    assert path in app.openapi()["paths"]


def test_login_request_schema_requires_login_id():
    """Pin the login request contract.

    This is the regression guard for the drift that silenced the agent suite: the
    field is `login_id`, and `password` is optional.
    """
    schema = app.openapi()["components"]["schemas"]["UserLogin"]
    assert schema["required"] == ["login_id"]
    assert set(schema["properties"]) == {"login_id", "password"}


def test_login_rejects_legacy_kailash_code_payload():
    """The pre-rename request shape must be a 422, not a silent pass.

    Asserted from the caller's side so the contract is pinned by observed
    behaviour and not only by the generated schema.
    """
    response = client.post(
        "/api/auth/login",
        json={"kailash_code": "not-the-field-name", "password": "irrelevant"},
    )
    assert response.status_code == 422
    missing = [
        error["loc"]
        for error in response.json()["detail"]
        if error["type"] == "missing"
    ]
    assert ["body", "login_id"] in missing
