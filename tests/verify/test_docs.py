"""The build-mechanism documentation cannot silently drift from the mechanism.

Task 8.4: `docs/guides/docker-and-mcp.md` once described the nine per-service
Dockerfiles as the build path and a published Redis default as the way in.
Both statements were false about the repository they sat in. These assertions
pin the corrected description to the mechanism CI actually executes, so the
next drift fails a test instead of misleading the next operator.
"""
from __future__ import annotations

from pathlib import Path

import pytest

DOC = Path(__file__).resolve().parents[2] / "docs" / "guides" / "docker-and-mcp.md"


@pytest.fixture(scope="module")
def doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_documents_the_generic_build_file_and_its_arguments(doc):
    assert "backend/services/Dockerfile.service" in doc
    assert "SERVICE" in doc and "PORT" in doc
    assert "x-platform-service" in doc


def test_states_the_per_service_dockerfiles_were_removed_and_why(doc):
    assert "removed" in doc
    assert "drift" in doc
    # The audit is what makes the removal stick.
    assert "build_audit" in doc


def test_does_not_present_a_credential_default(doc):
    """Compose credentials are strictly required (`:?`); a doc that offers a
    default teaches operators to expect one."""
    assert "required, no default" in doc
    # secret-scan: allow negative assertion; the literal must be named to be asserted absent
    assert "kailash_redis_2026" not in doc
    assert "${VAR:?}" in doc
