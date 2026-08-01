"""Rollback precondition check: does the requested target actually exist?

`rollback.py --target <id> --env <env> --check` resolves the identifier
against the two rollback surfaces this stack has -- Firebase Hosting release
history for the frontend, local `kailash-backend` image tags for the backend
-- and exits non-zero printing the requested identifier when it is absent
(Requirement 6.8).

Deliberately a *checker*, not an automation wrapper. Requirement 6.1 wants
documented commands an operator runs, and an operator mid-incident should
execute commands they can read rather than trust a script to orchestrate a
rollback. This script answers "does this target exist" -- the question that is
tedious and error-prone to answer by hand -- and stops there. It never issues
`hosting:clone`, `docker tag`, `docker rmi` or `compose up`.

The collector/classifier split is the testable seam: `collect_firebase()` and
`collect_docker()` shell out and reduce what they saw to an `AvailableSet`;
`classify()` is a pure function from the target plus those sets to a Report,
so membership, near-miss and unavailability behaviour are all exercised
without Firebase or a Docker daemon.

Exit codes follow scripts/verify/common.py:
    0  the target is a member of an available set
    1  every surface was consulted and none contains the target
    2  a surface could not be consulted and no consulted surface contains the
       target -- absence is unproven, which must not read as proof either way
    3  usage

Membership is exact string equality. Docker resolves tags by exact string, so
a short-SHA prefix of an available tag would not run that image, and the check
must not say it would; a near miss is reported as a hint, never as a match.

This module also owns the image-tag derivation helpers (task 10.1): the tag a
deploy writes is `kailash-backend:<sha>`, and `commit_for_image_tag()` is the
inverse, so a tag parses back to the SHA it came from (Property 12).

Usage:

    python -m scripts.verify.rollback --target <VERSION_ID> --env production --check
    python -m scripts.verify.rollback --target <COMMIT_SHA> --env production --check
"""
from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass

from .common import Finding, Report, Usage, base_parser, resolve_root, run

# The Firebase project that serves production Hosting. kailash-29111 by the
# same sources config_drift.py pins (frontend/.firebaserc and the deploy
# workflow); the spec text still says kailash-38268, which is the drift value
# the firebase-app-identity rule exists to catch.
FIREBASE_PROJECTS = {
    "production": "kailash-29111",
    # Staging hosting is planned as a second site in the same project
    # (staging.kailash-ai.com), so its release history lives there too until a
    # dedicated staging project exists.
    "staging": "kailash-29111",
}

IMAGE_REPOSITORY = "kailash-backend"

FIREBASE_SURFACE = "firebase-hosting-releases"
DOCKER_SURFACE = "docker-image-tags"


# --------------------------------------------------------------------------
# Image-tag derivation (task 10.1, Property 12)
# --------------------------------------------------------------------------

# Full or abbreviated git object name. Case-insensitive on input because
# operators paste SHAs from tools that uppercase them; the derived tag is
# always lowercase, both because git prints lowercase and because Docker
# rejects uppercase tag characters coming from some registries.
_SHA_RX = re.compile(r"^[0-9a-fA-F]{7,40}$")


def image_tag_for_commit(sha: str) -> str:
    """The image tag a deploy writes for `sha`: `kailash-backend:<sha>`."""
    s = sha.strip()
    if not _SHA_RX.match(s):
        raise ValueError(f"not a git commit SHA: {sha!r}")
    return f"{IMAGE_REPOSITORY}:{s.lower()}"


def commit_for_image_tag(tag: str) -> str:
    """The inverse of `image_tag_for_commit`: the SHA a deploy tag came from."""
    repository, _, sha = tag.partition(":")
    if repository != IMAGE_REPOSITORY or not _SHA_RX.match(sha):
        raise ValueError(f"not a {IMAGE_REPOSITORY} commit tag: {tag!r}")
    return sha.lower()


# --------------------------------------------------------------------------
# Collectors
# --------------------------------------------------------------------------

Executor = Callable[..., subprocess.CompletedProcess]


def default_execute(argv: Sequence[str], **kwargs) -> subprocess.CompletedProcess:
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("timeout", 60)
    return subprocess.run(list(argv), check=False, **kwargs)  # noqa: S603


@dataclass(frozen=True)
class AvailableSet:
    """What one rollback surface currently offers.

    `members` is None when the surface could not be consulted at all, which is
    a different fact from "consulted and empty": the first can prove nothing,
    the second proves absence.
    """

    surface: str
    members: frozenset[str] | None = None
    unavailable_reason: str | None = None


def firebase_releases_argv(project: str) -> list[str]:
    return ["firebase", "hosting:releases:list", "--project", project, "--json"]


DOCKER_TAGS_ARGV = ["docker", "image", "ls", IMAGE_REPOSITORY, "--format", "{{.Tag}}"]


def _first_line(text: str) -> str:
    for line in (text or "").splitlines():
        if line.strip():
            return line.strip()
    return ""


def _walk_strings(node: object) -> Iterator[str]:
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _walk_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_strings(value)


# A version resource name: `sites/<site>/versions/<VERSION_ID>`. The version
# id is what `firebase hosting:clone <project>:live@<VERSION_ID>` takes, so it
# is the identifier this check resolves -- release names are not clonable.
_VERSION_PATH_RX = re.compile(r"(?:^|/)versions/([A-Za-z0-9_-]+)$")


def firebase_release_ids(payload: str) -> set[str]:
    """Version ids from `firebase hosting:releases:list --json` output.

    Walks every string in the parsed JSON rather than assuming a shape: the
    CLI has moved fields between `result`, `releases` and `version` across
    versions, but the version resource name format is the stable part.
    Raises ValueError on unparseable payloads -- garbage must surface as
    UNAVAILABLE upstream, never as "no releases exist".
    """
    data = json.loads(payload)
    return {
        m.group(1)
        for s in _walk_strings(data)
        if (m := _VERSION_PATH_RX.search(s))
    }


def docker_image_tags(stdout: str) -> set[str]:
    """Tags from `docker image ls kailash-backend --format {{.Tag}}` output."""
    return {
        line.strip()
        for line in stdout.splitlines()
        if line.strip() and line.strip() != "<none>"
    }


def collect_firebase(execute: Executor, project: str) -> AvailableSet:
    try:
        proc = execute(firebase_releases_argv(project))
    except FileNotFoundError:
        return AvailableSet(FIREBASE_SURFACE, None,
                            "firebase CLI is not installed or not on PATH")
    except subprocess.TimeoutExpired as exc:
        return AvailableSet(FIREBASE_SURFACE, None,
                            f"firebase CLI timed out after {exc.timeout}s")
    if proc.returncode != 0:
        reason = _first_line(proc.stderr) or f"firebase exited {proc.returncode}"
        return AvailableSet(FIREBASE_SURFACE, None, reason)
    try:
        ids = firebase_release_ids(proc.stdout)
    except ValueError as exc:
        return AvailableSet(FIREBASE_SURFACE, None,
                            f"unparseable release listing: {exc}")
    return AvailableSet(FIREBASE_SURFACE, frozenset(ids))


def collect_docker(execute: Executor) -> AvailableSet:
    try:
        proc = execute(DOCKER_TAGS_ARGV)
    except FileNotFoundError:
        return AvailableSet(DOCKER_SURFACE, None,
                            "docker is not installed or not on PATH")
    except subprocess.TimeoutExpired as exc:
        return AvailableSet(DOCKER_SURFACE, None,
                            f"docker timed out after {exc.timeout}s")
    if proc.returncode != 0:
        reason = _first_line(proc.stderr) or f"docker exited {proc.returncode}"
        return AvailableSet(DOCKER_SURFACE, None, reason)
    return AvailableSet(DOCKER_SURFACE, frozenset(docker_image_tags(proc.stdout)))


# --------------------------------------------------------------------------
# Classifier -- pure
# --------------------------------------------------------------------------

def near_misses(target: str, available: Iterable[str]) -> list[str]:
    """Identifiers the operator plausibly meant.

    Case-insensitive equality, or a prefix relation of at least four
    characters, either way round. These are hints only: membership stays
    exact, because `docker compose` resolves a tag by exact string and a
    check that blessed a prefix would bless a command that fails.
    """
    t = target.lower()
    hits = set()
    for candidate in available:
        if candidate == target:
            continue
        c = candidate.lower()
        if c == t or (len(t) >= 4 and c.startswith(t)) or (len(c) >= 4 and t.startswith(c)):
            hits.add(candidate)
    return sorted(hits)


def classify(target: str, sets: Sequence[AvailableSet], *,
             compose_present: bool = True) -> Report:
    """Membership of `target` in the union of the available sets.

    Exit semantics (Property 13): with every surface consulted, OK if and only
    if the target is a member, and the requested identifier is printed
    whenever it is not. An unconsulted surface downgrades absence to
    UNAVAILABLE -- an unproven absence must not read as a proven one -- but
    cannot downgrade a proven membership.
    """
    report = Report()
    matched = [s for s in sets if s.members is not None and target in s.members]
    consulted = [s for s in sets if s.members is not None]
    unreachable = [s for s in sets if s.members is None]

    if matched:
        for s in matched:
            report.notes.append(f"target {target} found in {s.surface}")
        for s in unreachable:
            # Membership is already proven; an unreachable second surface
            # cannot unprove it, so this is a note rather than UNAVAILABLE.
            report.notes.append(f"{s.surface} not consulted: {s.unavailable_reason}")
        if not compose_present and any(s.surface == DOCKER_SURFACE for s in matched):
            report.add(Finding(
                rule="compose-file-missing", path="docker-compose.yml",
                observed="absent", expected="present at the repository root",
                message="the backend rollback command runs "
                        "docker compose -f docker-compose.yml (Requirement 6.5)",
            ))
        return report

    if unreachable:
        for s in unreachable:
            report.unavailable.append(
                f"{s.surface} unreachable while resolving {target}: "
                f"{s.unavailable_reason}")
        for s in consulted:
            report.notes.append(
                f"target {target} not in {s.surface} "
                f"({len(s.members or ())} identifier(s) available)")
        return report

    candidates = sorted(set().union(*(s.members or frozenset() for s in consulted))) \
        if consulted else []
    hints = near_misses(target, candidates)
    report.add(Finding(
        rule="rollback-target-absent",
        path=target,  # Requirement 6.8: print the requested identifier
        observed="absent from every rollback surface",
        expected="a Firebase Hosting version id or a "
                 f"{IMAGE_REPOSITORY} image tag",
        message=("near miss: " + ", ".join(hints)) if hints else
                f"{len(candidates)} identifier(s) available across "
                f"{len(consulted)} surface(s)",
    ))
    return report


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_report(args) -> Report:
    root = resolve_root(args.root)
    # Injectable so the CLI path is testable with the recording fake executor;
    # the real invocation never sets it.
    execute = getattr(args, "execute", None) or default_execute
    target = (args.target or "").strip()
    if not target:
        raise Usage("--target must name a Firebase version id or an image tag")
    project = FIREBASE_PROJECTS[args.env]
    sets = (collect_firebase(execute, project), collect_docker(execute))
    return classify(target, sets,
                    compose_present=(root / "docker-compose.yml").is_file())


def main(argv=None) -> int:
    parser = base_parser("Verify a rollback target exists before it is attempted.")
    parser.add_argument("--target", required=True,
                        help="Firebase Hosting version id, or a kailash-backend "
                             "image tag (the deployed commit SHA)")
    parser.add_argument("--env", required=True, choices=sorted(FIREBASE_PROJECTS))
    parser.add_argument("--check", action="store_true", required=True,
                        help="the only mode: this is a checker, not an "
                             "automation wrapper (Requirement 6.1)")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
