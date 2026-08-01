"""Rollback preconditions: membership is exact, absence prints the identifier.

The collector/classifier seam in `scripts/verify/rollback.py` is what these
tests exercise: available-set fixtures with present, absent and near-miss
identifiers drive the pure classifier (Property 13), the recording fake
executor proves the CLI consults exactly the two rollback surfaces and
mutates nothing, and the tag-derivation helpers round-trip a SHA in full,
short and mixed-case forms (Property 12).

The runbook assertions at the bottom pin `docs/runbooks/rollback.md` to the
two command forms Requirement 6.1 names, each executable without modification
apart from a single substitutable token.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scripts.verify import rollback as rb
from scripts.verify.common import Exit, Usage

FULL_SHA = "0f5a3c1d9e8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f"

# Written out rather than derived from the module, so a change to either
# command has to be made twice -- once in the collector, once here as a
# deliberate act.
FIREBASE_CMD = "firebase hosting:releases:list --project kailash-29111 --json"
DOCKER_CMD = "docker image ls kailash-backend --format {{.Tag}}"

FIREBASE_RELEASES_JSON = json.dumps({
    "status": "success",
    "result": [
        {
            "name": "sites/kailash-29111/releases/1750000000000000",
            "type": "DEPLOY",
            "version": {
                "name": "sites/kailash-29111/versions/abc123XY",
                "status": "FINALIZED",
            },
        },
        {
            "name": "sites/kailash-29111/releases/1749990000000000",
            "version": {"name": "sites/kailash-29111/versions/def456ZW"},
        },
    ],
})


def _set(surface: str, *members: str) -> rb.AvailableSet:
    return rb.AvailableSet(surface, frozenset(members))


def _down(surface: str, reason: str = "cannot connect") -> rb.AvailableSet:
    return rb.AvailableSet(surface, None, reason)


# --------------------------------------------------------------------------
# Tag derivation (task 10.1, Property 12)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("sha", [
    FULL_SHA,                     # full
    "0f5a3c1",                    # short
    "0F5A3C1D9E8B",               # mixed/upper case
])
def test_tag_derivation_round_trips(sha):
    tag = rb.image_tag_for_commit(sha)
    assert tag == f"kailash-backend:{sha.lower()}"
    assert rb.commit_for_image_tag(tag) == sha.lower()


@given(sha=st.text(alphabet="0123456789abcdefABCDEF", min_size=7, max_size=40))
def test_tag_derivation_round_trip_property(sha):
    tag = rb.image_tag_for_commit(sha)
    assert rb.commit_for_image_tag(tag) == sha.lower()
    # The inverse is a true inverse on derived tags.
    assert rb.image_tag_for_commit(rb.commit_for_image_tag(tag)) == tag


@pytest.mark.parametrize("bad", ["", "latest", "g1234567", "0f5a", "0" * 41])
def test_non_sha_input_is_rejected(bad):
    with pytest.raises(ValueError):
        rb.image_tag_for_commit(bad)


@pytest.mark.parametrize("bad", [
    "kailash-backend:latest",     # tag but not a commit tag
    f"other-image:{FULL_SHA}",    # right shape, wrong repository
    FULL_SHA,                     # bare SHA is not a tag
    "kailash-backend:",
])
def test_non_commit_tag_is_rejected(bad):
    with pytest.raises(ValueError):
        rb.commit_for_image_tag(bad)


# --------------------------------------------------------------------------
# Parsers -- pure
# --------------------------------------------------------------------------

def test_firebase_release_ids_from_a_cli_listing():
    assert rb.firebase_release_ids(FIREBASE_RELEASES_JSON) == {"abc123XY", "def456ZW"}


def test_firebase_release_ids_empty_history_is_an_empty_set():
    assert rb.firebase_release_ids('{"status": "success", "result": []}') == set()


def test_firebase_garbage_raises_rather_than_reading_as_no_releases():
    with pytest.raises(ValueError):
        rb.firebase_release_ids("Error: not logged in")


def test_docker_tags_drop_blank_and_none_lines():
    assert rb.docker_image_tags(f"latest\n<none>\n\n{FULL_SHA}\n") == {
        "latest", FULL_SHA}


# --------------------------------------------------------------------------
# Classifier -- available-set fixtures (Property 13)
# --------------------------------------------------------------------------

def test_present_docker_tag_is_ok():
    report = rb.classify(FULL_SHA, (
        _set(rb.FIREBASE_SURFACE, "abc123XY"),
        _set(rb.DOCKER_SURFACE, "latest", FULL_SHA),
    ))
    assert report.exit_code() == Exit.OK
    assert not report.findings


def test_present_firebase_version_is_ok():
    report = rb.classify("abc123XY", (
        _set(rb.FIREBASE_SURFACE, "abc123XY", "def456ZW"),
        _set(rb.DOCKER_SURFACE, "latest"),
    ))
    assert report.exit_code() == Exit.OK


def test_absent_target_fails_and_prints_the_identifier():
    report = rb.classify("feedface", (
        _set(rb.FIREBASE_SURFACE, "abc123XY"),
        _set(rb.DOCKER_SURFACE, "latest", FULL_SHA),
    ))
    assert report.exit_code() == Exit.FAILED
    [finding] = report.findings
    assert finding.rule == "rollback-target-absent"
    assert finding.path == "feedface"
    assert "feedface" in report.render()


def test_short_sha_of_an_available_tag_is_a_near_miss_not_a_match():
    """Docker resolves tags by exact string; a prefix must not pass."""
    report = rb.classify(FULL_SHA[:12], (
        _set(rb.FIREBASE_SURFACE),
        _set(rb.DOCKER_SURFACE, FULL_SHA),
    ))
    assert report.exit_code() == Exit.FAILED
    [finding] = report.findings
    assert FULL_SHA in finding.message


def test_case_variant_is_a_near_miss_not_a_match():
    report = rb.classify("abc123xy", (
        _set(rb.FIREBASE_SURFACE, "abc123XY"),
        _set(rb.DOCKER_SURFACE),
    ))
    assert report.exit_code() == Exit.FAILED
    [finding] = report.findings
    assert "abc123XY" in finding.message


def test_unreachable_surface_with_absence_elsewhere_is_unavailable():
    """Absence is unproven while a surface is unreadable; that must not read
    as the target being gone, nor as it being fine."""
    report = rb.classify(FULL_SHA, (
        _set(rb.FIREBASE_SURFACE, "abc123XY"),
        _down(rb.DOCKER_SURFACE),
    ))
    assert report.exit_code() == Exit.UNAVAILABLE
    assert not report.findings
    assert FULL_SHA in report.render()


def test_unreachable_surface_cannot_unprove_a_membership():
    report = rb.classify("abc123XY", (
        _set(rb.FIREBASE_SURFACE, "abc123XY"),
        _down(rb.DOCKER_SURFACE),
    ))
    assert report.exit_code() == Exit.OK


def test_docker_match_without_a_compose_file_fails():
    report = rb.classify(FULL_SHA, (
        _set(rb.FIREBASE_SURFACE),
        _set(rb.DOCKER_SURFACE, FULL_SHA),
    ), compose_present=False)
    assert report.exit_code() == Exit.FAILED
    [finding] = report.findings
    assert finding.rule == "compose-file-missing"


def test_firebase_match_needs_no_compose_file():
    report = rb.classify("abc123XY", (
        _set(rb.FIREBASE_SURFACE, "abc123XY"),
        _set(rb.DOCKER_SURFACE),
    ), compose_present=False)
    assert report.exit_code() == Exit.OK


_IDENT = st.text(
    alphabet="0123456789abcdefABCDEFxyzXYZ_-", min_size=1, max_size=12)


@given(members=st.lists(st.tuples(_IDENT, st.booleans()), max_size=8),
       target=_IDENT)
def test_membership_property(members, target):
    """Exit 0 iff the target is a member of the union of the available sets,
    and the requested identifier appears in the output whenever it is not."""
    firebase = frozenset(m for m, on_firebase in members if on_firebase)
    docker = frozenset(m for m, on_firebase in members if not on_firebase)
    report = rb.classify(target, (
        rb.AvailableSet(rb.FIREBASE_SURFACE, firebase),
        rb.AvailableSet(rb.DOCKER_SURFACE, docker),
    ))
    if target in firebase | docker:
        assert report.exit_code() == Exit.OK
    else:
        assert report.exit_code() == Exit.FAILED
        assert target in report.render()


# --------------------------------------------------------------------------
# CLI -- collectors through the fake executor
# --------------------------------------------------------------------------

def _args(root, execute, target, env="production"):
    return argparse.Namespace(root=root, json=False, emit_record=None,
                              target=target, env=env, check=True,
                              execute=execute)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "docker-compose.yml").write_text("services: {}\n",
                                                 encoding="utf-8")
    return tmp_path


def test_cli_consults_exactly_the_two_surfaces_and_mutates_nothing(
        repo, fake_executor):
    fake_executor.script(FIREBASE_CMD, 0, FIREBASE_RELEASES_JSON)
    fake_executor.script(DOCKER_CMD, 0, f"latest\n{FULL_SHA}\n")

    report = rb.build_report(_args(repo, fake_executor, FULL_SHA))

    assert report.exit_code() == Exit.OK
    assert fake_executor.commands() == [FIREBASE_CMD, DOCKER_CMD]
    # A checker, not an automation wrapper: nothing here may act on the target.
    for mutation in ("hosting:clone", "docker tag", "docker rmi",
                     "up -d", "docker pull"):
        fake_executor.assert_never(mutation)


def test_cli_absent_target_fails_with_the_identifier(repo, fake_executor):
    fake_executor.script(FIREBASE_CMD, 0, FIREBASE_RELEASES_JSON)
    fake_executor.script(DOCKER_CMD, 0, "latest\n")

    report = rb.build_report(_args(repo, fake_executor, "feedface"))

    assert report.exit_code() == Exit.FAILED
    assert "feedface" in report.render()


def test_cli_firebase_failure_downgrades_absence_to_unavailable(
        repo, fake_executor):
    fake_executor.script(FIREBASE_CMD, 1, "", "Error: not logged in")
    fake_executor.script(DOCKER_CMD, 0, "latest\n")

    report = rb.build_report(_args(repo, fake_executor, "abc123XY"))

    assert report.exit_code() == Exit.UNAVAILABLE
    assert "not logged in" in report.render()


def test_cli_unparseable_firebase_output_is_unavailable_not_absent(
        repo, fake_executor):
    fake_executor.script(FIREBASE_CMD, 0, "<html>proxy error</html>")
    fake_executor.script(DOCKER_CMD, 0, "latest\n")

    report = rb.build_report(_args(repo, fake_executor, "abc123XY"))

    assert report.exit_code() == Exit.UNAVAILABLE


def test_blank_target_is_usage(repo, fake_executor):
    with pytest.raises(Usage):
        rb.build_report(_args(repo, fake_executor, "   "))
    assert fake_executor.commands() == []


def test_check_flag_is_mandatory():
    """The flag is the operator's statement of intent; there is no other mode,
    and argparse refusing early means no subprocess ever runs."""
    assert rb.main(["--target", "x", "--env", "production"]) == int(Exit.USAGE)


def test_target_and_env_are_mandatory():
    assert rb.main(["--check"]) == int(Exit.USAGE)
    assert rb.main(["--target", "x", "--check"]) == int(Exit.USAGE)
    assert rb.main(["--target", "x", "--env", "nonesuch", "--check"]) \
        == int(Exit.USAGE)


# --------------------------------------------------------------------------
# The runbook (task 10.3, Requirement 6.1)
# --------------------------------------------------------------------------

RUNBOOK = Path(__file__).resolve().parents[2] / "docs" / "runbooks" / "rollback.md"

# A substitutable token: <VERSION_ID>, <COMMIT_SHA>, <target-release-manifest>.
TOKEN_RX = re.compile(r"<[^<>\s]+>")


@pytest.fixture(scope="module")
def runbook() -> str:
    return RUNBOOK.read_text(encoding="utf-8")


def _fenced_commands(text: str) -> list[str]:
    lines = []
    for block in re.findall(r"```(?:bash)?\n(.*?)```", text, re.S):
        for line in block.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    return lines


def test_runbook_contains_both_rollback_command_forms(runbook):
    assert ("firebase hosting:clone kailash-29111:live@<VERSION_ID> "
            "kailash-29111:live") in runbook
    assert ("BACKEND_IMAGE_TAG=<COMMIT_SHA> docker compose "
            "-f docker-compose.yml up -d --no-build backend") in runbook


def test_runbook_finds_targets_checks_preconditions_and_verifies(runbook):
    assert "firebase hosting:releases:list --project kailash-29111" in runbook
    assert ("python -m scripts.verify.rollback --target <VERSION_ID> "
            "--env production --check") in runbook
    assert ("python -m scripts.verify.rollback --target <COMMIT_SHA> "
            "--env production --check") in runbook
    assert ("python -m scripts.verify.deployment_check --env production "
            "--manifest <target-release-manifest>") in runbook


def test_every_runbook_command_needs_at_most_one_substitution(runbook):
    """Requirement 6.1: executable without modification apart from a version
    identifier -- so no command line may demand two different substitutions."""
    commands = _fenced_commands(runbook)
    assert commands, "no fenced commands found in the runbook"
    for line in commands:
        tokens = set(TOKEN_RX.findall(line))
        assert len(tokens) <= 1, (line, tokens)


def test_the_two_rollback_commands_take_exactly_one_token(runbook):
    for fragment in ("hosting:clone", "BACKEND_IMAGE_TAG="):
        [line] = [c for c in _fenced_commands(runbook) if fragment in c]
        assert len(set(TOKEN_RX.findall(line))) == 1, line


def test_runbook_states_retention_and_its_pending_basis(runbook):
    """Task 10.4 sizes retention from the task 4.5 disk-headroom record, which
    does not exist yet; the runbook must say what the default is and why."""
    assert "RETAINED_IMAGE_TAGS" in runbook
    assert "4.5" in runbook
    assert "**3**" in runbook


def test_runbook_names_the_compose_image_key_dependency(runbook):
    """The backend command only selects a tag once task 10.5 (operator-gated)
    adds the image: key; a runbook silent on that would send an operator
    mid-incident down a command that rebuilds instead of rolling back."""
    assert "10.5" in runbook
    assert "image: kailash-backend:${BACKEND_IMAGE_TAG:-latest}" in runbook
