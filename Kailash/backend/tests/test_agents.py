"""
Agent Test Suite - Validates all 36 agents across departments

Every endpoint exercised here sits behind `get_current_active_user` and reads
MongoDB, so this file is an integration suite: it needs a reachable MongoDB and
an account to log in as. Both come from the environment
(`KAILASH_TEST_LOGIN_ID`, `KAILASH_TEST_PASSWORD`), and the fixtures skip when
they are absent, because an absent backing store is a different event from a
broken application.

What is deliberately *not* skipped is a contract break. HTTP 422 from
`/api/auth/login` means the request body no longer matches `UserLogin`, and 401
means the credentials were rejected. Both are real defects and both fail the
suite. A fixture that turns every non-200 into a skip cannot fail the CI job it
is supposed to gate, which is the same masking as a trailing `|| true`, one
layer further down.
"""
import os
from collections.abc import Iterator

import pytest
from app.main import app
from fastapi.testclient import TestClient

# Statuses the login endpoint returns when its dependencies, not its contract,
# are the problem: `get_db()` raising, or a Mongo server-selection timeout, both
# surface as 500 via the handler's except branch; 503 is the explicit
# Atlas-permission signal.
_BACKING_STORE_STATUSES = (500, 502, 503, 504)


@pytest.fixture(scope="module")
def integration_credentials() -> tuple[str, str | None]:
    """The account this suite authenticates as, or a skip.

    Checked before the client is built so the absent-prerequisite case costs
    nothing: entering the app lifespan against an unreachable MongoDB burns
    every startup timeout before it gives up.
    """
    login_id = os.environ.get("KAILASH_TEST_LOGIN_ID")
    if not login_id:
        pytest.skip(
            "KAILASH_TEST_LOGIN_ID is unset, so there is no account to "
            "authenticate as. Set it and KAILASH_TEST_PASSWORD, with a "
            "reachable MONGO_URL, to run the department integration tests."
        )
    return login_id, os.environ.get("KAILASH_TEST_PASSWORD")


@pytest.fixture(scope="module")
def client(integration_credentials: tuple[str, str | None]) -> Iterator[TestClient]:
    """A client that has actually run the app's startup.

    `TestClient(app)` on its own never enters the lifespan, so
    `MongoD.connect_db()` never runs and every database-backed route answers 500
    whether or not MongoDB is reachable. Entering the context manager is what
    makes these tests capable of passing at all.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def auth_token(
    client: TestClient, integration_credentials: tuple[str, str | None]
) -> str:
    """Authenticate against the real login endpoint and return the token."""
    login_id, password = integration_credentials

    # `UserLogin` declares `login_id` and an optional `password`. Sending
    # `kailash_code` instead is a 422, not a login failure.
    payload: dict[str, str] = {"login_id": login_id}
    if password:
        payload["password"] = password

    response = client.post("/api/auth/login", json=payload)

    if response.status_code in _BACKING_STORE_STATUSES:
        pytest.skip(
            f"/api/auth/login returned {response.status_code}, which this app "
            f"uses for database faults rather than credential rejection: "
            f"{response.text}"
        )

    if response.status_code == 422:
        pytest.fail(
            "/api/auth/login rejected the request body, so the login contract "
            f"and this suite disagree: {response.text}"
        )

    if response.status_code == 401:
        pytest.fail(
            "/api/auth/login rejected KAILASH_TEST_LOGIN_ID and "
            f"KAILASH_TEST_PASSWORD: {response.text}"
        )

    assert response.status_code == 200, (
        f"unexpected status from /api/auth/login: {response.status_code} "
        f"{response.text}"
    )

    data = response.json()
    assert "access_token" in data, f"no access token in login response: {data}"
    return data["access_token"]


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {auth_token}"}


class TestDepartmentEndpoints:
    """Test department API endpoints"""

    def test_list_departments(self, client: TestClient, auth_headers: dict[str, str]):
        """Test listing all departments"""
        response = client.get("/api/departments", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 20

    def test_get_ganesha(self, client: TestClient, auth_headers: dict[str, str]):
        """Test GANESHA department"""
        response = client.get("/api/departments/ganesha", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "GANESHA"

    def test_get_vishwakarma(self, client: TestClient, auth_headers: dict[str, str]):
        """Test VISHWAKARMA department"""
        response = client.get("/api/departments/vishwakarma", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "VISHWAKARMA"


class TestProductAgents:
    """Test product-specific agents"""

    def test_urgaa_agent(self, client: TestClient, auth_headers: dict[str, str]):
        """Test SURYA (URGAA) agent"""
        response = client.get("/api/departments/surya/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["department"] == "SURYA"
        assert "sub_agents" in data

    def test_gstsaas_agent(self, client: TestClient, auth_headers: dict[str, str]):
        """Test TVASHTA (GSTSAAS) agent"""
        response = client.get("/api/departments/tvashta/summary", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["department"] == "TVASHTA"

    def test_ignition_agent(self, client: TestClient, auth_headers: dict[str, str]):
        """Test KARTIKEYA (IGNITION) agent"""
        response = client.get("/api/departments/kartikeya/summary", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["department"] == "KARTIKEYA"


class TestInternalAgents:
    """Test internal department agents"""

    def test_lakshmi_cfo(self, client: TestClient, auth_headers: dict[str, str]):
        """Test LAKSHMI (CFO) agent"""
        response = client.get("/api/departments/lakshmi", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "LAKSHMI"

    def test_kubera_sales(self, client: TestClient, auth_headers: dict[str, str]):
        """Test KUBERA (Sales) agent"""
        response = client.get("/api/departments/kubera", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "KUBERA"

    def test_kamadeva_marketing(self, client: TestClient, auth_headers: dict[str, str]):
        """Test KAMADEVA (Marketing) agent"""
        response = client.get("/api/departments/kamadeva", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "KAMADEVA"


class TestRoutingValidation:
    """Test task routing logic

    Both tests below are placeholders that assert nothing. They are left as
    written rather than deleted, but they are not coverage: whoever owns the
    routing logic should either implement or remove them.
    """

    def test_route_to_department(self, client: TestClient, auth_headers: dict[str, str]):
        """Test routing task to specific department"""
        # This would test the actual routing logic
        # Placeholder for now
        assert True

    def test_priority_assignment(self, client: TestClient, auth_headers: dict[str, str]):
        """Test priority assignment logic"""
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
