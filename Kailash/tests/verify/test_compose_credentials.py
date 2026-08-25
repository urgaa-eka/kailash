"""Unset credentials must abort compose before any container exists (task 6.4).

`${VAR:?}` fails during configuration parsing, which is the property being
bought: the failure happens before `up` creates anything, so a deploy with a
missing password cannot leave a half-started stack behind. These tests run
compose against the real docker-compose.yml with the credential deliberately
unset or empty, and compare the daemon's container set before and after `up`
to prove nothing was created.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _compose(args: list[str], **env_overrides) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    # Only the variable under test is missing; the others hold throwaway
    # values so the failure is attributable to that one variable.
    env["REDIS_PASSWORD"] = "test-only-placeholder"
    env["PLATFORM_INTERNAL_TOKEN"] = "test-only-placeholder"
    env.pop("POSTGRES_PASSWORD", None)
    for key, value in env_overrides.items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    return subprocess.run(
        ["docker", "compose", "-f", "docker-compose.yml",
         "--profile", "kailash-ai", *args],
        cwd=ROOT, env=env, capture_output=True, text=True, check=False,
        timeout=120,
    )


def _container_names() -> set[str]:
    out = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}"],
                         capture_output=True, text=True, check=False, timeout=60)
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


@pytest.mark.docker
@pytest.mark.parametrize("value", [None, ""], ids=["unset", "empty"])
def test_config_refuses_without_postgres_password(value):
    result = _compose(["config", "--quiet"], POSTGRES_PASSWORD=value)
    assert result.returncode != 0
    assert "POSTGRES_PASSWORD" in result.stderr


@pytest.mark.docker
@pytest.mark.parametrize("value", [None, ""], ids=["unset", "empty"])
def test_up_refuses_and_creates_no_container(value):
    before = _container_names()
    result = _compose(["up", "-d", "--no-build"], POSTGRES_PASSWORD=value)
    after = _container_names()

    assert result.returncode != 0
    assert "POSTGRES_PASSWORD" in result.stderr
    assert after == before
