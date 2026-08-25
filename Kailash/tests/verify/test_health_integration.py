"""Live-stack health integration tests (task 4.9). All `@pytest.mark.docker`.

These are the requirements of epic 4 asserted against the actual running
stack rather than fixtures: every probe executable exists where its probe
runs (1.2), every Platform_Service answers its Health_Path on its bound
loopback port (1.4), the backend answers `/api/health` (1.3), and the healthy
set is the full roster (1.5). CI excludes the `docker` marker; these run on a
host with the stack up.
"""
from __future__ import annotations

import json
import shlex
import subprocess
import urllib.request
from pathlib import Path

import pytest

pytestmark = pytest.mark.docker

ROOT = Path(__file__).resolve().parents[2]

PLATFORM_PORTS = range(8101, 8110)  # the nine Platform_Services


def _docker(*args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(["docker", *args], capture_output=True, text=True,
                          check=False, timeout=timeout)


def _roster() -> list[str]:
    """Container names declared in docker-compose.yml, the authoritative set."""
    import yaml
    doc = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    return sorted(
        svc["container_name"] for svc in doc["services"].values()
        if isinstance(svc, dict) and svc.get("container_name")
    )


def _probe_executable(name: str) -> str | None:
    """First argv element of the container's effective probe, if any."""
    out = _docker("inspect", "--format", "{{json .Config.Healthcheck}}", name)
    if out.returncode != 0:
        return None
    test = (json.loads(out.stdout.strip() or "null") or {}).get("Test") or []
    if not test or test == ["NONE"]:
        return None
    if test[0] == "CMD":
        return test[1] if len(test) > 1 else None
    if test[0] == "CMD-SHELL":
        parts = shlex.split(test[1]) if len(test) > 1 else []
        return parts[0] if parts else None
    return test[0]


def test_every_probe_executable_resolves_inside_its_container():
    """Requirement 1.2, live: `which <exe>` exits 0 in all 15 containers."""
    missing: list[str] = []
    for name in _roster():
        exe = _probe_executable(name)
        if exe is None:
            missing.append(f"{name}: no probe declared")
            continue
        result = _docker("exec", name, "which", exe)
        if result.returncode != 0:
            missing.append(f"{name}: which {exe} -> {result.returncode}")
    assert not missing, missing


@pytest.mark.parametrize("port", PLATFORM_PORTS)
def test_platform_service_health_paths_answer_200(port):
    """Requirement 1.4: each Platform_Service's /health on 127.0.0.1."""
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=15) as r:
        assert r.status == 200


def test_backend_api_health_answers_200():
    """Requirement 1.3."""
    with urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=15) as r:
        assert r.status == 200


def test_the_full_roster_reports_healthy():
    """Requirement 1.5: `docker ps --filter health=healthy` lists every
    declared container. The 180-second convergence bound applies to a fresh
    `up`; on an already-converged stack the assertion is immediate."""
    out = _docker("ps", "--filter", "health=healthy", "--format", "{{.Names}}")
    healthy = {line.strip() for line in out.stdout.splitlines() if line.strip()}
    missing = [name for name in _roster() if name not in healthy]
    assert not missing, f"not reporting healthy: {missing}"
