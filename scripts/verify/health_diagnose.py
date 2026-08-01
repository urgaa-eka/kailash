"""Container health diagnosis: capture the evidence, then classify it.

The module has two halves and the seam between them is the point.

The **collector** (everything above the `Phase A classifier` banner) shells out
to Docker and writes what it saw, verbatim, to
`docs/records/container-health-evidence.json`. It decides nothing.

The **classifier** (everything below that banner) is a pure function from that
captured JSON to `list[Finding]` plus Diagnosis_Record entries. It calls no
subprocess, reads no clock and touches no filesystem, which is what lets all
fourteen failure shapes be exercised from `tests/verify/fixtures/inspect_*.json`
with no daemon, no stack and no timing luck -- and what lets
`--from-evidence` regenerate the record on a runner with no Docker socket.

Three collection decisions carry weight.

**The effective probe is read from `.Config.Healthcheck`, never from
`docker-compose.yml`.** Nine of the fifteen containers -- the Platform_Services
-- are probed by a `HEALTHCHECK` baked into the image by
`backend/services/Dockerfile.service`; the `x-platform-service` compose anchor
declares no `healthcheck` at all. Reading the compose file would therefore have
investigated the wrong probe for nine containers. Compose is consulted for
exactly one thing: whether a service *declares* a probe, which is what
distinguishes `probe_source: compose` from `probe_source: image`.

**The roster is the declared set, not the running set.** Container names come
from the `container_name` keys in `docker-compose.yml`, so a container that is
absent from the daemon is captured as absent rather than silently dropped from
the count. A roster read from `docker ps` would shrink to fit reality and hide
the interesting case.

**`.State.Health.Log` is preserved whole.** Every attempt keeps its `Start`,
`End`, `ExitCode` and `Output`. `End - Start` per attempt is the measurement
task 4.3 needs for the start-period rule, so this module computes
`duration_seconds` alongside the verbatim timestamps and stops there.

Nothing here raises on bad input. A malformed or truncated `docker inspect`
capture is written to the evidence file as the raw string it was, with a
`capture-unparsed` finding naming it. An unreachable daemon is
`Exit.UNAVAILABLE`, classifying nothing and writing nothing -- absence of
findings from a capture that never happened means nothing at all.

Usage:

    python -m scripts.verify.health_diagnose \
        --emit-record docs/records/container-health-diagnosis.md
    python -m scripts.verify.health_diagnose \
        --from-evidence docs/records/container-health-evidence.json \
        --emit-record docs/records/container-health-diagnosis.md
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .common import (
    Finding,
    Report,
    Unavailable,
    Usage,
    base_parser,
    resolve_root,
    run,
)

EVIDENCE_PATH = "docs/records/container-health-evidence.json"

# The image used for the H9 clock-skew reading. Small, and its BusyBox `date`
# accepts `+%s`, which removes a timestamp-format parsing step from a
# measurement whose whole value is arithmetic.
CLOCK_IMAGE = "alpine"


# --------------------------------------------------------------------------
# The four Phase A captures
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Capture:
    key: str
    fmt: str


CAPTURES: tuple[Capture, ...] = (
    Capture("health", "{{json .State.Health}}"),
    Capture("effective", "{{json .Config.Healthcheck}}"),
    Capture("state", "{{json .State}}"),
    Capture("restarts", "{{.RestartCount}}"),
)


def inspect_argv(name: str, fmt: str) -> list[str]:
    return ["docker", "inspect", "--format", fmt, name]


HOST_VERSION_ARGV = ["docker", "version", "--format", "{{json .}}"]
HOST_INFO_ARGV = ["docker", "info", "--format", "{{json .}}"]
ROSTER_ARGV = ["docker", "ps", "-a", "--no-trunc",
               "--format", "{{.Names}}\t{{.Image}}\t{{.ID}}\t{{.Status}}"]
CLOCK_IMAGE_ARGV = ["docker", "image", "inspect", CLOCK_IMAGE, "--format", "{{.Id}}"]
CLOCK_PULL_ARGV = ["docker", "pull", CLOCK_IMAGE]
CLOCK_ARGV = ["docker", "run", "--rm", CLOCK_IMAGE, "date", "-u", "+%s"]


# --------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------

Executor = Callable[..., subprocess.CompletedProcess]


def default_execute(argv: Sequence[str], **kwargs) -> subprocess.CompletedProcess:
    """`subprocess.run` with the settings every capture here wants.

    `check=False` throughout: a non-zero `docker inspect` is evidence about the
    container, not an error in the collector, and raising on it would lose the
    stderr that says which container is missing.
    """
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("timeout", 60)
    return subprocess.run(list(argv), check=False, **kwargs)  # noqa: S603


def _run(execute: Executor, argv: Sequence[str], **kwargs) -> dict:
    """One command, reduced to a recordable result. Never raises."""
    try:
        proc = execute(list(argv), **kwargs)
    except FileNotFoundError as exc:
        raise Unavailable("docker is not installed or not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        return {"argv": list(argv), "exit_code": None, "stdout": "",
                "stderr": f"timeout after {exc.timeout}s"}
    except OSError as exc:  # pragma: no cover - platform-specific spawn failures
        return {"argv": list(argv), "exit_code": None, "stdout": "",
                "stderr": f"{type(exc).__name__}: {exc}"}
    return {
        "argv": list(argv),
        "exit_code": proc.returncode,
        "stdout": proc.stdout or "",
        "stderr": proc.stderr or "",
    }


def require_daemon(execute: Executor) -> dict:
    """`docker version`, or `Unavailable`.

    Every later capture is meaningless without this, so it is the one place
    that converts a missing prerequisite into exit 2.
    """
    result = _run(execute, HOST_VERSION_ARGV)
    if result["exit_code"] != 0:
        detail = (result["stderr"] or result["stdout"]).strip().splitlines()
        raise Unavailable(
            "docker daemon unreachable: "
            + (detail[0] if detail else f"docker version exited {result['exit_code']}")
        )
    return result


# --------------------------------------------------------------------------
# Parsing helpers -- tolerant by design
# --------------------------------------------------------------------------

_DOCKER_TS = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})[T ](?P<clock>\d{2}:\d{2}:\d{2})"
    r"(?:\.(?P<frac>\d+))?(?P<tz>[Zz]|[+-]\d{2}:?\d{2})?$"
)


def parse_docker_time(value: object) -> datetime | None:
    """Docker's nanosecond timestamps, which `fromisoformat` rejects.

    `2026-01-05T10:00:00.412000000Z` carries nine fractional digits; the stdlib
    parser accepts three or six. Truncating rather than refusing keeps the
    duration measurement available, and the verbatim string is preserved
    separately either way.
    """
    if not isinstance(value, str) or not value.strip():
        return None
    m = _DOCKER_TS.match(value.strip())
    if not m:
        return None
    frac = (m.group("frac") or "")[:6].ljust(6, "0")
    tz = m.group("tz") or "Z"
    tz = "+00:00" if tz in ("Z", "z") else tz
    if len(tz) == 5:  # +0530 -> +05:30
        tz = f"{tz[:3]}:{tz[3:]}"
    try:
        return datetime.fromisoformat(f"{m['date']}T{m['clock']}.{frac}{tz}")
    except ValueError:  # pragma: no cover - regex already constrains the shape
        return None


def parse_json_capture(raw: str) -> tuple[object, str | None]:
    """(value, parse_error). A truncated capture yields (None, message)."""
    text = (raw or "").strip()
    if not text or text in ("null", "<no value>"):
        return None, None
    try:
        return json.loads(text), None
    except (json.JSONDecodeError, ValueError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def _ns_to_seconds(value: object) -> float | None:
    """Docker reports healthcheck durations in nanoseconds."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return value / 1_000_000_000


def probe_log(health: object) -> list[dict]:
    """`.State.Health.Log` with each attempt's duration added.

    Start, End, ExitCode and Output are carried through unmodified. The added
    `duration_seconds` is `End - Start`, which is the measurement task 4.3's
    start-period rule consumes; a probe still in flight has a zero-value `End`
    and yields `None` rather than a negative number.
    """
    if not isinstance(health, dict):
        return []
    entries = health.get("Log")
    if not isinstance(entries, list):
        return []
    out: list[dict] = []
    for entry in entries:
        if not isinstance(entry, dict):
            out.append({"raw": entry})
            continue
        start, end = parse_docker_time(entry.get("Start")), parse_docker_time(entry.get("End"))
        duration = None
        if start and end and end >= start:
            duration = (end - start).total_seconds()
        out.append({
            "start": entry.get("Start"),
            "end": entry.get("End"),
            "exit_code": entry.get("ExitCode"),
            "output": entry.get("Output"),
            "duration_seconds": duration,
        })
    return out


# --------------------------------------------------------------------------
# Roster and probe provenance, from docker-compose.yml
# --------------------------------------------------------------------------

def compose_services(root: Path) -> list[dict]:
    """`(service, container_name, declares_healthcheck)` in compose file order.

    Compose is read for the roster and for probe *provenance* only. The probe
    itself is always read from `.Config.Healthcheck`, because nine of these
    containers carry an image-level probe that compose never mentions.
    """
    path = root / "docker-compose.yml"
    if not path.is_file():
        raise Unavailable(f"{path} is absent; the container roster is declared there")
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - pyyaml is a pinned dev dep
        raise Unavailable("pyyaml is not installed") from exc
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise Unavailable(f"docker-compose.yml does not parse: {exc}") from exc
    services = (doc or {}).get("services") or {}
    if not isinstance(services, dict):
        raise Unavailable("docker-compose.yml declares no services mapping")
    out = []
    for service, body in services.items():
        body = body if isinstance(body, dict) else {}
        out.append({
            "service": service,
            "name": body.get("container_name") or service,
            "compose_declares_healthcheck": "healthcheck" in body,
        })
    return out


def probe_source(*, effective_present: bool, compose_declares: bool) -> str:
    """Where the probe the runtime actually uses came from.

    Order matters: a container with no effective probe has no source no matter
    what compose says, and a container with an effective probe that compose
    never declared got it from its image.
    """
    if not effective_present:
        return "none"
    return "compose" if compose_declares else "image"


# --------------------------------------------------------------------------
# Host facts
# --------------------------------------------------------------------------

def collect_clock(execute: Executor, *, clock: Callable[[], float] = time.time) -> dict:
    """H9's reading: container clock minus host clock.

    The image presence check comes first and any pull is deliberately outside
    the timed window. A pull inside it would add tens of seconds to the host
    midpoint and turn the skew figure into a measurement of download speed.

    `host_window_seconds` is reported because it bounds the reading: with
    one-second container granularity and container start overhead, a skew
    smaller than the window is not distinguishable from zero.
    """
    out: dict = {"image": CLOCK_IMAGE, "pulled": False}
    present = _run(execute, CLOCK_IMAGE_ARGV)
    out["image_inspect"] = present
    if present["exit_code"] != 0:
        out["pull"] = _run(execute, CLOCK_PULL_ARGV, timeout=300)
        out["pulled"] = out["pull"]["exit_code"] == 0

    before = clock()
    result = _run(execute, CLOCK_ARGV, timeout=120)
    after = clock()
    out["run"] = result
    out["host_before_epoch"] = before
    out["host_after_epoch"] = after
    out["host_window_seconds"] = after - before
    out["container_raw"] = result["stdout"].strip()

    if result["exit_code"] != 0:
        out["error"] = (result["stderr"] or "").strip() or f"exited {result['exit_code']}"
        out["skew_seconds"] = None
        return out
    try:
        container_epoch = float(out["container_raw"].splitlines()[-1])
    except (ValueError, IndexError):
        out["error"] = f"unparseable container time: {out['container_raw']!r}"
        out["skew_seconds"] = None
        return out
    out["container_epoch"] = container_epoch
    out["skew_seconds"] = container_epoch - (before + after) / 2
    return out


def parse_roster(stdout: str) -> dict[str, dict]:
    """`docker ps` lines keyed by container name.

    Image identity is captured here rather than through a fifth `docker
    inspect` because it changes how any other observation reads: the running
    `kailash-backend` is one build behind its `latest` tag (recorded in
    `docs/records/backend-health-path.md`), so "the container does X" is a
    statement about the image it is running, not about the working tree.
    """
    roster: dict[str, dict] = {}
    for line in (stdout or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 4 or not parts[0].strip():
            continue
        name, image, cid, status = (p.strip() for p in parts[:4])
        roster[name] = {"image": image, "container_id": cid, "status": status}
    return roster


def collect_host(execute: Executor, *, clock: Callable[[], float] = time.time) -> dict:
    """`docker version`, `docker info`'s memory ceiling, the roster, and skew."""
    version = require_daemon(execute)
    info = _run(execute, HOST_INFO_ARGV)
    roster_result = _run(execute, ROSTER_ARGV)

    version_doc, version_error = parse_json_capture(version["stdout"])
    info_doc, info_error = parse_json_capture(info["stdout"])
    clock_facts = collect_clock(execute, clock=clock)

    version_map = version_doc if isinstance(version_doc, dict) else {}
    server = version_map.get("Server") if isinstance(version_map.get("Server"), dict) else {}
    client = version_map.get("Client") if isinstance(version_map.get("Client"), dict) else {}
    info_map = info_doc if isinstance(info_doc, dict) else {}

    return {
        "docker_version": server.get("Version") or client.get("Version"),
        "docker_client_version": client.get("Version"),
        "docker_os_arch": f"{server.get('Os')}/{server.get('Arch')}" if server else None,
        "kernel_version": info_map.get("KernelVersion"),
        "mem_total_bytes": info_map.get("MemTotal"),
        "ncpu": info_map.get("NCPU"),
        "containers_running": info_map.get("ContainersRunning"),
        "clock_skew_seconds": clock_facts.get("skew_seconds"),
        "clock": clock_facts,
        "roster": parse_roster(roster_result["stdout"]),
        "raw": {
            "version": version,
            "info": info,
            "roster": roster_result,
        },
        "parse_errors": {k: v for k, v in
                         (("version", version_error), ("info", info_error)) if v},
    }


# --------------------------------------------------------------------------
# Per-container capture
# --------------------------------------------------------------------------

def collect_container(execute: Executor, entry: dict, roster: dict[str, dict]) -> dict:
    """The four captures for one container, plus what reads straight off them.

    Every field the design's schema fills in a later phase -- `executable`
    (task 4.4 Phase D), `replay` (task 4.4 Phase C),
    `measured_first_success_seconds` (task 4.3) and `attribution` (task 4.2) --
    is present and null. Present-and-null says "not yet collected"; absent
    would say "no such concept", and a later reader cannot tell those apart.
    """
    name = entry["name"]
    raw: dict[str, dict] = {}
    for capture in CAPTURES:
        raw[capture.key] = _run(execute, inspect_argv(name, capture.fmt))

    parse_errors: dict[str, str] = {}
    parsed: dict[str, object] = {}
    for key in ("health", "effective", "state"):
        value, error = parse_json_capture(raw[key]["stdout"])
        parsed[key] = value
        if error:
            parse_errors[key] = error

    restart_count: int | None = None
    restarts_text = raw["restarts"]["stdout"].strip()
    if restarts_text:
        try:
            restart_count = int(restarts_text)
        except ValueError:
            parse_errors["restarts"] = f"not an integer: {restarts_text!r}"

    # A capture that did not exit 0 produced no evidence. Recorded as such
    # rather than left to look like "this container has no health state",
    # which is what an empty stdout would otherwise read as.
    failed = [c.key for c in CAPTURES if raw[c.key]["exit_code"] != 0]
    absent = len(failed) == len(CAPTURES)
    health = parsed["health"] if isinstance(parsed["health"], dict) else None
    effective = parsed["effective"] if isinstance(parsed["effective"], dict) else None
    state = parsed["state"] if isinstance(parsed["state"], dict) else None

    return {
        "name": name,
        "service": entry["service"],
        "present": not absent,
        "image": roster.get(name, {}).get("image"),
        "container_id": roster.get(name, {}).get("container_id"),
        "ps_status": roster.get(name, {}).get("status"),
        "health_status": (health or {}).get("Status"),
        "failing_streak": (health or {}).get("FailingStreak"),
        "restart_count": restart_count,
        "state_status": (state or {}).get("Status"),
        "started_at": (state or {}).get("StartedAt"),
        "probe_source": probe_source(
            effective_present=effective is not None,
            compose_declares=entry["compose_declares_healthcheck"],
        ),
        "compose_declares_healthcheck": entry["compose_declares_healthcheck"],
        "effective_test": (effective or {}).get("Test"),
        "declared_interval_seconds": _ns_to_seconds((effective or {}).get("Interval")),
        "declared_timeout_seconds": _ns_to_seconds((effective or {}).get("Timeout")),
        "declared_start_period_seconds": _ns_to_seconds((effective or {}).get("StartPeriod")) or 0,
        "declared_retries": (effective or {}).get("Retries"),
        "probe_log": probe_log(health),
        # Filled by later phases; see the docstring.
        "executable": None,
        "replay": None,
        "measured_first_success_seconds": None,
        "attribution": None,
        "raw": dict(raw),
        "capture_failed": failed,
        "parse_errors": parse_errors,
    }


def summarise(containers: list[dict]) -> dict:
    """Counts by observed health state. Arithmetic, not diagnosis."""
    by_status: dict[str, int] = {}
    for c in containers:
        key = c["health_status"] or ("absent" if not c["present"] else "no-health-state")
        by_status[key] = by_status.get(key, 0) + 1
    return {
        "containers": len(containers),
        "by_health_status": dict(sorted(by_status.items())),
        "without_probe": sorted(c["name"] for c in containers if c["probe_source"] == "none"),
        "probe_source_counts": {
            source: sum(1 for c in containers if c["probe_source"] == source)
            for source in ("compose", "image", "none")
        },
    }


def collect(root: Path, execute: Executor, *,
            clock: Callable[[], float] = time.time) -> dict:
    """Phase A end to end. Raises only `Unavailable`."""
    entries = compose_services(root)
    host = collect_host(execute, clock=clock)
    containers = [collect_container(execute, entry, host["roster"]) for entry in entries]
    return {
        "captured_at": datetime.now(UTC).isoformat(),
        "phase": "A",
        "generated_by": "scripts/verify/health_diagnose.py",
        "host": host,
        "containers": containers,
        "summary": summarise(containers),
    }


def write_evidence(evidence: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


# --------------------------------------------------------------------------
# Report -- capture integrity only. Health classification is task 4.2.
# --------------------------------------------------------------------------

def load_denylist(root: Path) -> list[str]:
    """The secret-scan denylist literals, if the data file is present."""
    path = root / "scripts" / "verify" / "data" / "denylist.txt"
    if not path.is_file():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")]


def denylisted_captures(evidence: dict, denylist: list[str]) -> list[str]:
    """Containers whose verbatim capture carries a denylisted credential literal.

    This is a real collision, not a hypothetical one: `redis`'s compose probe
    reads `${REDIS_PASSWORD:-<fallback>}`, so the *rendered* probe that
    `.Config.Healthcheck` reports contains whatever the fallback was. Capturing
    verbatim is the requirement, and the literal is therefore in the evidence
    file by construction.

    Reported as a note rather than a finding, and without echoing the literal.
    The capture itself is correct; what it means is that committing the evidence
    file puts a denylisted string into a tracked file, which the secret scan
    will fail. Somebody has to decide that, so it is said out loud here instead
    of being discovered in CI.
    """
    if not denylist:
        return []
    hits = []
    for container in evidence["containers"]:
        blob = json.dumps(container, ensure_ascii=False)
        if any(literal in blob for literal in denylist):
            hits.append(container["name"])
    return sorted(hits)


def _first_stderr(container: dict) -> str:
    for capture in CAPTURES:
        text = (container["raw"][capture.key].get("stderr") or "").strip()
        if text:
            return text.splitlines()[0]
    return ""


def capture_findings(evidence: dict) -> list[Finding]:
    """What went wrong *with the capture*, not with any container's health.

    A truncated inspect capture is preserved in the evidence file and reported
    here, because a collector that returned OK on output it could not read
    would hand task 4.2 a file that silently omits a container.
    """
    findings: list[Finding] = []
    for container in evidence["containers"]:
        name = container["name"]
        failed = container.get("capture_failed") or []
        if not container["present"]:
            findings.append(Finding(
                rule="container-absent", path=name,
                observed="no such container", expected="present on the daemon",
                message=_first_stderr(container) or "docker inspect failed",
            ))
        elif failed:
            findings.append(Finding(
                rule="capture-failed", path=f"{name}:{','.join(failed)}",
                observed="docker inspect did not exit 0",
                expected="all four captures",
                message=_first_stderr(container) or "raw output preserved",
            ))
        for key, error in sorted(container["parse_errors"].items()):
            findings.append(Finding(
                rule="capture-unparsed", path=f"{name}:{key}",
                observed=error, expected="parseable capture",
                message="raw output preserved in the evidence file",
            ))
    for key, error in sorted(evidence["host"].get("parse_errors", {}).items()):
        findings.append(Finding(
            rule="capture-unparsed", path=f"host:{key}",
            observed=error, expected="parseable capture",
        ))
    return findings


def build_report(args) -> Report:
    root = resolve_root(args.root)
    # Injectable so the CLI path is testable with the recording fake executor;
    # the real invocation never sets it.
    execute = getattr(args, "execute", None) or default_execute
    report = Report()

    source = getattr(args, "from_evidence", None)
    if source:
        # The classifier is pure, so reclassifying a committed capture needs no
        # daemon. This is how the record is regenerated in CI, and how a
        # reviewer checks the narrative against the evidence it came from.
        evidence = read_evidence(Path(source))
        evidence_path = Path(source)
        annotate_first_success(evidence)
        report.notes.append(f"classified {evidence_path} without contacting Docker")
    else:
        evidence = collect(root, execute)
        evidence_path = Path(args.evidence) if args.evidence else root / EVIDENCE_PATH
        annotate_first_success(evidence)
        write_evidence(evidence, evidence_path)
        report.notes.append(f"evidence written to {evidence_path}")

    for finding in capture_findings(evidence):
        report.add(finding)

    findings, entries = classify(evidence)
    for finding in findings:
        report.add(finding)

    for finding in start_period_findings(evidence):
        report.add(finding)

    denylist = load_denylist(root)
    record = getattr(args, "emit_record", None)
    if record is not None and Path(record).suffix.lower() in (".md", ".markdown"):
        # The Diagnosis_Record is a narrative document, not a JSON dump, so this
        # check writes it itself and clears the flag the shared runner uses --
        # otherwise `common.run` would overwrite the markdown with the JSON
        # report at the same path. A `.json` destination is left to the runner.
        write_record(render_record(evidence, entries, denylist=denylist), Path(record))
        args.emit_record = None
        report.notes.append(f"diagnosis record written to {record}")

    undetermined = [e.name for e in entries if not e.determined]
    if entries:
        report.notes.append(
            f"{len(entries)} container(s) not reporting healthy, each attributed: "
            + ", ".join(f"{e.name}={e.attribution_rule}" for e in entries))
    if undetermined:
        report.notes.append(
            "attribution is provisional for " + ", ".join(undetermined)
            + ": the evidence in hand does not discriminate between a failing "
              "invocation and a failing service, which Phase C replay and Phase D "
              "`which` (task 4.4) resolve")

    summary = evidence["summary"]
    report.notes.append(
        f"{summary['containers']} containers captured: "
        + ", ".join(f"{k}={v}" for k, v in summary["by_health_status"].items())
    )
    report.notes.append(
        "probe source: "
        + ", ".join(f"{k}={v}" for k, v in summary["probe_source_counts"].items())
    )
    if summary["without_probe"]:
        report.notes.append(
            "no probe declared, so no health state can be reported: "
            + ", ".join(summary["without_probe"])
        )
    exposed = denylisted_captures(evidence, denylist)
    if exposed:
        report.notes.append(
            "the verbatim capture for " + ", ".join(exposed)
            + " contains a literal from scripts/verify/data/denylist.txt "
              "(a compose fallback rendered into the effective probe); "
              f"{evidence_path.name} cannot be committed until the fallback is "
              "removed or the file carries a reviewed suppression"
        )

    clock = evidence["host"]["clock"]
    if clock.get("skew_seconds") is None:
        report.unavailable.append(
            f"clock skew not measured: {clock.get('error', 'unknown reason')}")
    else:
        report.notes.append(
            f"clock skew {clock['skew_seconds']:+.2f}s "
            f"(host measurement window {clock['host_window_seconds']:.2f}s)"
        )
    return report


def main(argv=None) -> int:
    parser = base_parser(
        "Capture Phase A container health evidence and classify it. The collector "
        "shells out to Docker; the classifier is a pure function of what it "
        "captured, so `--from-evidence` reclassifies with no daemon at all."
    )
    parser.add_argument("--evidence", type=Path, default=None,
                        help=f"evidence output path (default: <root>/{EVIDENCE_PATH})")
    parser.add_argument("--from-evidence", type=Path, default=None,
                        help="classify a previously captured evidence file instead "
                             "of contacting Docker")
    return run(build_report, argv, parser)

# ==========================================================================
# Phase A classifier -- a pure function of the captured JSON
# ==========================================================================
#
# Nothing below this line calls a subprocess, reads a clock, touches the
# filesystem or contacts Docker. Its whole input is the evidence dict the
# collector above produced, which is why all fourteen failure shapes are
# reachable from `tests/verify/fixtures/inspect_*.json` with no daemon, no
# stack and no timing luck.
#
# Two properties of the live data shape this code, and both are worth stating
# because they cut against the premise the spec was written under:
#
#   * The capture of 2026-08-01 reports **14 healthy** containers and one --
#     `kailash-frontend` -- with no health state at all, because it declares no
#     `HEALTHCHECK`. The spec's premise was 14 `unhealthy`. The classifier is
#     therefore written to be correct in both worlds: fed the fixtures it
#     attributes every failure shape, and fed today's evidence it legitimately
#     produces one entry. A classifier tuned to make today's data look
#     interesting would be a classifier that invents findings.
#
#   * `executable` and `replay` are null in today's evidence: Phase C and
#     Phase D are task 4.4. Every branch here treats null as "not yet
#     collected", attributes what the recorded probe output alone can carry,
#     and names the missing evidence rather than assuming it. An attribution
#     that says "not yet discriminated, because the replay has not run" is
#     honest; one that guesses is not.

DIAGNOSIS_PATH = "docs/records/container-health-diagnosis.md"

REDACTED = "<redacted:denylisted-literal>"

# `sh -c "<string>"` is `CMD-SHELL` written out longhand, so both forms are
# unwrapped to the command the shell runs. The design's own record example
# extracts `python` from a `CMD-SHELL` probe rather than `/bin/sh`, which fixes
# the meaning of "the executable the runtime will invoke" for Property 3: the
# shell is transparent, and `which python` is the check Requirement 1.2 wants.
SHELL_EXECUTABLES = frozenset({"sh", "bash", "ash", "dash", "zsh", "ksh"})

# `FOO=bar curl ...` invokes curl; `exec curl ...` invokes curl. Neither prefix
# is an executable, so both are skipped when reading the leading word.
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_TRANSPARENT = frozenset({"exec"})

# Word-splitting operators. `(` and `)` are deliberately *not* here: no probe in
# this stack uses a subshell, and treating them as delimiters would split
# `db.adminCommand('ping')` into three words for no gain.
_OPERATORS = "|&;<>\n"

_SHELL_C_FLAGS = frozenset({"-c", "-lc", "-ec", "-cu", "-uc"})


# --------------------------------------------------------------------------
# Probe form parsing and executable extraction (Property 3)
# --------------------------------------------------------------------------

def _strip_quotes(token: str) -> str:
    """`"curl"` and `'curl'` and ` curl ` are all `curl`.

    Property 3 requires extraction to be unchanged by surrounding whitespace
    and quoting, and this is the whole of that guarantee for a single word.
    """
    text = token.strip()
    while len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1].strip()
    return text


def shell_words(text: str) -> list[str]:
    """Split a shell command string into words the way the shell would.

    Hand-written rather than `shlex.split` for one reason: `${...}` must be
    atomic. A probe carrying `redis-cli -a "${REDIS_PASSWORD:-a b}" ping` has a
    reference whose *default* may contain a space, and a splitter that broke
    inside the reference would shift every later word. Property 3 requires the
    extraction to be unchanged by environment references, so the reference is
    consumed whole, braces and all.

    Quotes are removed, backslash escapes are honoured outside single quotes,
    and unquoted `|`, `&`, `;`, `<`, `>` end a word -- which is how
    `python -c "..." || exit 1` yields `python` as its first word rather than
    the whole line.
    """
    words: list[str] = []
    token: list[str] = []
    had_quote = False          # `""` is a real, empty word
    single = double = False
    depth = 0                  # inside ${...}
    i, n = 0, len(text or "")
    while i < n:
        ch = text[i]
        if depth:
            token.append(ch)
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            i += 1
            continue
        if ch == "\\" and not single:
            if i + 1 < n:
                token.append(text[i + 1])
                had_quote = True
                i += 2
                continue
            i += 1
            continue
        if ch == "'" and not double:
            single = not single
            had_quote = True
            i += 1
            continue
        if ch == '"' and not single:
            double = not double
            had_quote = True
            i += 1
            continue
        if not single and not double and text[i:i + 2] == "${":
            token.append("${")
            depth = 1
            i += 2
            continue
        if not single and not double and (ch.isspace() or ch in _OPERATORS):
            if token or had_quote:
                words.append("".join(token))
                token, had_quote = [], False
            i += 1
            continue
        token.append(ch)
        i += 1
    if token or had_quote:
        words.append("".join(token))
    return words


def _executable_from_words(words: Sequence[object], *, depth: int = 0) -> str | None:
    """The first word that is actually a command, shells unwrapped once."""
    for index, raw in enumerate(words):
        token = _strip_quotes(str(raw))
        if not token or _ASSIGNMENT.match(token) or token in _TRANSPARENT:
            continue
        if depth < 2 and token.rsplit("/", 1)[-1] in SHELL_EXECUTABLES:
            rest = [_strip_quotes(str(w)) for w in words[index + 1:]]
            for pos, word in enumerate(rest):
                if word in _SHELL_C_FLAGS and pos + 1 < len(rest):
                    inner = _executable_from_words(
                        shell_words(rest[pos + 1]), depth=depth + 1)
                    return inner or token
            return token
        return token
    return None


@dataclass(frozen=True)
class Probe:
    """A `.Config.Healthcheck.Test` value, read.

    `form` is the declared form; `command` is the command text as the runtime
    runs it, which is what the record quotes and what URLs are read from.
    """

    form: str                       # CMD | CMD-SHELL | SHELL | NONE | ABSENT | UNKNOWN
    executable: str | None
    words: tuple[str, ...]
    command: str

    @property
    def declared(self) -> bool:
        return self.form not in ("ABSENT", "NONE")


def parse_probe(test: object) -> Probe:
    """Every test form Docker and compose accept, reduced to one shape.

    `["CMD", ...]` is an argv the runtime execs directly. `["CMD-SHELL", s]`
    and a bare string `s` are both `/bin/sh -c s`, so the executable is the
    leading word of `s`. `["NONE"]` disables an inherited probe, which is not
    the same thing as never having declared one -- hence two form names.
    """
    if test is None:
        return Probe("ABSENT", None, (), "")
    if isinstance(test, str):
        text = test.strip()
        if not text:
            return Probe("ABSENT", None, (), "")
        words = shell_words(text)
        return Probe("SHELL", _executable_from_words(words), tuple(words), text)
    if isinstance(test, list | tuple):
        items = [str(x) for x in test if x is not None]
        if not items:
            return Probe("ABSENT", None, (), "")
        head = _strip_quotes(items[0]).upper()
        if head == "NONE":
            return Probe("NONE", None, (), "NONE")
        if head == "CMD-SHELL":
            # Docker writes exactly one element after the form, but joining is
            # what a hand-written multi-element form means anyway.
            joined = " ".join(items[1:]).strip()
            words = shell_words(joined)
            return Probe("CMD-SHELL", _executable_from_words(words),
                         tuple(words), joined)
        argv = items[1:] if head == "CMD" else items
        form = "CMD" if head == "CMD" else "UNKNOWN"
        cleaned = tuple(_strip_quotes(a) for a in argv)
        return Probe(form, _executable_from_words(argv), cleaned, " ".join(argv))
    return Probe("UNKNOWN", None, (), str(test))


def extract_executable(test: object) -> str | None:
    """The executable a health check test invokes. Property 3's function."""
    return parse_probe(test).executable


def rendered_test(test: object) -> str:
    """The probe as one readable line, with its form kept.

    The form is part of the evidence: `CMD curl -f url` and
    `CMD-SHELL curl -f url` fail differently, because only the second one has a
    shell to interpret `||` and only the first survives a missing `/bin/sh`.
    """
    probe = parse_probe(test)
    if probe.form in ("ABSENT",):
        return "none declared"
    if probe.form == "NONE":
        return "NONE (an inherited probe, explicitly disabled)"
    if probe.form in ("CMD", "CMD-SHELL"):
        return f"{probe.form} {probe.command}".strip()
    return probe.command


# --------------------------------------------------------------------------
# URLs inside a probe -- the path element of the definition
# --------------------------------------------------------------------------

def _scan_url(text: str, start: int) -> str:
    """Read a URL from `start`, treating `{...}`/`[...]` as atomic.

    The nine image-level probes embed the port as an f-string expression:
    `http://localhost:{os.environ["PORT"]}/health`. A URL regex that stopped at
    the first quote would return `http://localhost:{os.environ[` and lose the
    `/health` path -- which is the one element of that definition Requirement
    1.7 turns on. Bracket depth is tracked so the quotes inside the expression
    do not terminate the URL.
    """
    depth = 0
    i = start
    while i < len(text):
        ch = text[i]
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            if depth == 0:
                break
            depth -= 1
        elif depth == 0 and (ch.isspace() or ch in "\"'`\\|&;,>"):
            break
        i += 1
    return text[start:i]


def probe_urls(test: object) -> list[str]:
    """Every URL the probe addresses, in order."""
    command = parse_probe(test).command
    urls: list[str] = []
    for match in re.finditer(r"https?://", command):
        url = _scan_url(command, match.start())
        if url:
            urls.append(url)
    return urls


def url_path(url: str) -> str:
    """The path of a URL, with `{...}` expressions ignored while finding it."""
    if not url:
        return ""
    rest = url.split("://", 1)[1] if "://" in url else url
    depth = 0
    for i, ch in enumerate(rest):
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth = max(0, depth - 1)
        elif ch == "/" and depth == 0:
            path = rest[i:]
            return path.split("?", 1)[0].split("#", 1)[0]
    return "/"


def probe_path(test: object) -> str | None:
    """The path the probe asks for, or None when the probe is not HTTP."""
    urls = probe_urls(test)
    return url_path(urls[0]) if urls else None


# --------------------------------------------------------------------------
# Reading signals out of recorded output
# --------------------------------------------------------------------------

# Connection refused, in the words each probe mechanism actually uses.
REFUSED_SIGNALS = (
    "connection refused", "connectionrefusederror", "errno 111",
    "errno 61", "curl: (7)", "failed to connect", "could not connect",
    "couldn't connect to server", "connection reset by peer",
    "no route to host", "econnrefused",
)

# An executable the image does not have, in the words the runtime uses.
MISSING_EXECUTABLE_SIGNALS = (
    "executable file not found", "command not found", "not found in $path",
    "no such file or directory", "unable to start container process",
)

TIMEOUT_SIGNALS = ("exceeded timeout", "context deadline exceeded", "timed out")

# `urllib.error.HTTPError: HTTP Error 503: Service Unavailable`, and
# `curl: (22) The requested URL returned error: 404`. Both are the diagnosis
# rather than a symptom of one: `urllib.request.urlopen` raises on any non-2xx,
# so a platform-service probe never reaches its `sys.exit(1)` branch and the
# exception class in `Output` is what says which failure it was.
_HTTP_STATUS = re.compile(
    r"(?:HTTP\s*Error|returned\s+error:|HTTP/\d(?:\.\d)?|status(?:\s+code)?\s*[:=]?)"
    r"\s*(\d{3})", re.IGNORECASE)

_EXCEPTION_CLASS = re.compile(r"^\s*([A-Za-z_][\w.]*(?:Error|Exception|Timeout))\b",
                              re.MULTILINE)


def _has(text: str, signals: Sequence[str]) -> bool:
    low = (text or "").lower()
    return any(signal in low for signal in signals)


def http_status_in(text: str) -> int | None:
    """The HTTP status a recorded output reports, if it reports one."""
    for match in _HTTP_STATUS.finditer(text or ""):
        code = int(match.group(1))
        if 100 <= code <= 599:
            return code
    if "curl: (22)" in (text or ""):
        return 400  # curl -f without a parseable code: some 4xx/5xx happened
    return None


def exception_class_in(text: str) -> str | None:
    """The exception class named in a traceback, which for the nine
    image-level probes **is** the diagnosis."""
    classes = _EXCEPTION_CLASS.findall(text or "")
    return classes[-1] if classes else None


def first_line(text: str, limit: int = 220) -> str:
    """The first non-blank line of an output, shortened for a FAIL line."""
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped:
            return stripped if len(stripped) <= limit else stripped[:limit] + "..."
    return ""


# --------------------------------------------------------------------------
# Evidence accessors
# --------------------------------------------------------------------------

def evidence_attempt(container: dict) -> dict | None:
    """The probe attempt the record quotes.

    The most recent *failing* attempt when there is one, else the most recent
    attempt. Requirement 1.1 asks for the observed exit code and output of a
    container reporting `unhealthy`, and on a container that has since had one
    success the last entry in the log would be a success -- evidence of the
    wrong thing.
    """
    log = container.get("probe_log") or []
    entries = [e for e in log if isinstance(e, dict)]
    if not entries:
        return None
    failing = [e for e in entries if e.get("exit_code") not in (0, None)]
    return failing[-1] if failing else entries[-1]


def slowest_attempt_seconds(container: dict) -> float | None:
    durations = [e.get("duration_seconds") for e in (container.get("probe_log") or [])
                 if isinstance(e, dict) and isinstance(e.get("duration_seconds"), int | float)]
    return max(durations) if durations else None


def _replay(container: dict) -> dict | None:
    replay = container.get("replay")
    return replay if isinstance(replay, dict) else None


def replay_ok(container: dict) -> bool:
    replay = _replay(container)
    return bool(replay) and replay.get("exit_code") == 0


def replay_path(container: dict) -> str | None:
    """The path the replay actually asked for, when it recorded one.

    Phase C records the command it replayed. When that command addresses a
    different path than the probe does and it succeeded, the two facts together
    are the 200-on-a-different-path finding -- neither one alone is.
    """
    replay = _replay(container)
    if not replay:
        return None
    replayed = replay.get("replayed") or replay.get("command") or replay.get("argv")
    if isinstance(replayed, list | tuple):
        text = " ".join(str(x) for x in replayed)
    elif isinstance(replayed, str):
        text = replayed
    else:
        return None
    for match in re.finditer(r"https?://", text):
        return url_path(_scan_url(text, match.start()))
    return None


def executable_evidence(container: dict) -> dict | None:
    """Phase D's `which` result, or None when it has not been collected."""
    exe = container.get("executable")
    return exe if isinstance(exe, dict) else None


def host_saturation(host: dict) -> tuple[bool | None, str]:
    """H1's verdict, when Phase B has recorded one.

    Returns `(None, reason)` while it has not been measured. `None` is not
    `False`: a classifier that read "not measured" as "not saturated" would
    attribute a host-wide failure to fourteen separate probe definitions, which
    is the fourteen-investigations path the design exists to avoid.
    """
    saturation = (host or {}).get("saturation")
    if isinstance(saturation, dict) and "confirmed" in saturation:
        detail = str(saturation.get("detail") or "").strip()
        return bool(saturation["confirmed"]), detail
    return None, "host saturation is not measured in this capture (Phase B, task 4.5)"


def probe_declared_in(container: dict) -> str:
    source = container.get("probe_source")
    if source == "image":
        # The only image-level probe in this repository. Nine containers share
        # it, and it is invisible in docker-compose.yml.
        return "image (backend/services/Dockerfile.service)"
    if source == "compose":
        return "docker-compose.yml"
    return "nowhere -- no probe is declared"


# --------------------------------------------------------------------------
# Rendered-probe-versus-intent
# --------------------------------------------------------------------------

_CREDENTIAL_FLAGS = frozenset({"-a", "--pass", "--password", "--requirepass"})


def interpolation_defect(container: dict, probe: Probe) -> str | None:
    """Whether the probe the runtime runs is the probe somebody declared.

    Three shapes, in decreasing order of certainty:

    1. `intent_test` is recorded (Phase B reads it from `docker compose
       --profile kailash-ai config`) and the rendered probe differs from it.
       `redis` is the live instance: compose declares
       `redis-cli -a "${REDIS_PASSWORD:-...}" ping` and the effective probe
       carries the rendered fallback, so what runs is not what was written.
    2. The rendered probe still carries an unexpanded `${...}`, which means the
       interpolation never happened and the probe is asking for a literal
       dollar-brace string.
    3. A credential flag rendered to an empty value, which is the H2 shape:
       the variable was unset in the shell that ran compose and the fallback
       was empty, so the probe authenticates with no password at all.
    """
    rendered = probe.command
    intent = container.get("intent_test")
    if intent is not None:
        intent_command = parse_probe(intent).command
        if " ".join(rendered.split()) != " ".join(intent_command.split()):
            if "${" in intent_command:
                return ("compose interpolation: the declared probe is "
                        f"{intent_command!r} and the probe the runtime runs is a "
                        "rendered form of it, so the value it uses comes from the "
                        "fallback rather than from the declaration")
            return (f"the running probe is not the declared one: declared "
                    f"{intent_command!r}, running {rendered!r}")
    if "${" in rendered:
        return ("the rendered probe still carries an unexpanded reference "
                f"({rendered!r}), so compose interpolation did not happen and the "
                "probe is asking for a literal dollar-brace string")
    words = list(probe.words)
    for index, word in enumerate(words[:-1]):
        if word in _CREDENTIAL_FLAGS and not str(words[index + 1]).strip():
            return (f"the {word} argument rendered to an empty value, so the probe "
                    "authenticates with no credential; the variable was unset "
                    "where compose ran and the fallback was empty")
    return None


# --------------------------------------------------------------------------
# The decision tree
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Attribution:
    """The failing element of the definition, or the blocking condition.

    `element` is never empty. That is Property 1, and it is enforced by
    construction: the tree's last branch attributes the evidence that *is*
    present and names the evidence that is not, rather than falling through to
    an empty string.
    """

    rule: str
    element: str
    remedy: str
    criterion: str
    determined: bool = True


def attribute(container: dict, host: dict | None = None) -> Attribution:
    """Classify one non-healthy container. Pure.

    Branch order is not the design table's row order, and the two places it
    differs are deliberate:

    * `probe-path-mismatch` is tested before the connection and status
      branches, because a successful replay against a different path explains a
      404 on the probed path, and the general "replay succeeded" branch would
      otherwise swallow it as a timeout.
    * `host-saturated` is tested before `probe-invocation`. Both require a
      successful replay; saturation is the strict refinement, and testing the
      general case first would attribute a host-wide cause to a probe
      definition.
    """
    host = host or {}
    probe = parse_probe(container.get("effective_test"))
    attempt = evidence_attempt(container) or {}
    exit_code = attempt.get("exit_code")
    output = attempt.get("output") or ""
    replay = _replay(container)
    replay_text = ""
    if replay:
        replay_text = f"{replay.get('stdout') or ''}\n{replay.get('stderr') or ''}"
    exe = executable_evidence(container)

    # ---- the capture itself, before anything is read out of it -------------
    if not container.get("present", True):
        return Attribution(
            "container-absent",
            "the container is not on the daemon, so it has no health state to "
            "report; nothing about its probe definition can be concluded from "
            "this capture",
            "start the container with `docker compose --profile kailash-ai up -d` "
            "and re-run the capture",
            "1.1",
            determined=False,
        )
    unparsed = sorted(container.get("parse_errors") or {})
    if unparsed:
        return Attribution(
            "evidence-incomplete",
            "the " + ", ".join(unparsed) + " capture did not parse, so the probe "
            "outcome cannot be read; the raw output is preserved verbatim in the "
            "evidence file",
            "re-run the capture; if it truncates again, capture that container's "
            "inspect output to a file and attach it",
            "1.1",
            determined=False,
        )

    # ---- no probe at all --------------------------------------------------
    if not probe.declared:
        disabled = probe.form == "NONE"
        return Attribution(
            "probe-absent",
            ("the probe inherited from the image is explicitly disabled with "
             "`NONE`, so no health state is reported"
             if disabled else
             "no health check is declared, in compose or in the image, so the "
             "container reports no health state at all -- it is not failing a "
             "probe, it has none to fail, and `docker ps --filter health=healthy` "
             "can therefore never list it"),
            "add a healthcheck block to this service (task 4.6 adds the BusyBox "
            "wget probe for `frontend`)",
            "1.5",
        )

    # ---- 1.2: an executable the image does not have ------------------------
    if exe is not None and (exe.get("present") is False
                            or (exe.get("which_exit_code") not in (0, None))):
        name = exe.get("name") or probe.executable or "the probe executable"
        return Attribution(
            "probe-executable-absent",
            f"the probe invokes `{name}`, which the image does not have: "
            f"`which {name}` exited {exe.get('which_exit_code')}",
            f"replace `{name}` with an executable the image ships",
            "1.2",
        )
    if exit_code == 127 or _has(output, MISSING_EXECUTABLE_SIGNALS):
        name = probe.executable or "the probe executable"
        return Attribution(
            "probe-executable-absent",
            f"the probe invokes `{name}` and the runtime could not start it "
            f"(exit {exit_code}: {first_line(output)!r})",
            f"replace `{name}` with an executable the image ships, and confirm "
            f"with `docker exec {container.get('name')} which <executable>`",
            "1.2",
        )

    probed = probe_path(container.get("effective_test"))
    replayed = replay_path(container)
    status = http_status_in(output) or http_status_in(replay_text)

    # ---- 1.7: 200 on a different path than the one probed -----------------
    if replay_ok(container) and ((replayed and probed and replayed != probed)
                                 or status == 404):
        served = replayed or "a path the probe does not ask for"
        return Attribution(
            "probe-path-mismatch",
            f"the path element of the definition: the service answers on `{served}` "
            f"while the probe asks for `{probed}`, so the container is healthy and "
            "the probe is wrong about where to look",
            f"align the probe to `{served}`, or add the `{probed}` route -- "
            "`/api/health` is the more entrenched of the two, since Requirements "
            "2.3, 4.6 and 6.6 and both deploy scripts already depend on it",
            "1.7",
        )

    # ---- 1.8: the service is not listening --------------------------------
    if _has(output, REFUSED_SIGNALS) or _has(replay_text, REFUSED_SIGNALS):
        detail = first_line(output) or first_line(replay_text)
        return Attribution(
            "service-not-listening",
            "blocking condition: the probe is refused at the transport, so the "
            f"service is not listening on the probed address ({detail!r}). The "
            "definition is not at fault",
            "an application startup defect: read the container logs and fix the "
            "service; do not widen the probe",
            "1.8",
        )

    # ---- 1.8: the service is listening and rejecting the probed path ------
    if status is not None and status >= 400:
        exception = exception_class_in(output) or exception_class_in(replay_text)
        via = f" via {exception}" if exception else ""
        hint = (" A 404 means the path may be wrong, but no replay has succeeded "
                "elsewhere to prove it." if status == 404 else "")
        return Attribution(
            "service-rejects-probe",
            f"blocking condition: the service answers the probed path `{probed}` "
            f"with HTTP {status}{via}, so it is listening and rejecting the "
            f"request.{hint}",
            "an application defect: fix what the service reports at its health "
            "path. Note that `urllib.request.urlopen` raises on any non-2xx, so "
            "this probe exits through a traceback rather than its `sys.exit(1)` "
            "branch",
            "1.8",
        )

    # ---- 1.7: the probe that runs is not the probe declared ---------------
    interpolation = interpolation_defect(container, probe)
    if interpolation:
        return Attribution(
            "probe-interpolation",
            f"the definition's rendered form: {interpolation}",
            "correct the reference in docker-compose.yml so the probe the runtime "
            "runs is the probe that was declared",
            "1.7",
        )

    measured = (replay or {}).get("duration_seconds")
    slowest = slowest_attempt_seconds(container)
    timeout = container.get("declared_timeout_seconds")
    start_period = container.get("declared_start_period_seconds")
    first_success = container.get("measured_first_success_seconds")

    # ---- 1.8: environmental, and therefore not fourteen probe bugs --------
    saturated, saturation_detail = host_saturation(host)
    if replay_ok(container) and saturated:
        return Attribution(
            "host-saturated",
            "blocking condition: the replay succeeds while the recorded probe "
            f"fails, and the host is saturated ({saturation_detail}). A uniform "
            "failure across heterogeneous probes is one environmental cause, not "
            "one bug per probe",
            "remediate the host, then re-run Phase A before editing any probe "
            "definition",
            "1.8",
        )

    # ---- 1.6/1.7: the invocation, not the service -------------------------
    if replay_ok(container):
        parts = [
            "the probe invocation, not the service: replaying the same test "
            f"exited 0{f' in {measured:.2f}s' if isinstance(measured, int | float) else ''} "
            "while the recorded attempt failed"
        ]
        if isinstance(slowest, int | float) and isinstance(timeout, int | float) \
                and slowest >= timeout:
            parts.append(f"the slowest recorded attempt took {slowest:.2f}s against "
                         f"a declared timeout of {timeout:.0f}s")
        elif _has(output, TIMEOUT_SIGNALS):
            parts.append(f"the recorded attempt reports {first_line(output)!r}")
        if not start_period:
            parts.append("no start period is declared, so a slow first boot is "
                         "counted as a failure from the first interval")
        remedy = []
        if isinstance(measured, int | float):
            remedy.append(f"raise timeout to at least 3x measured ({measured * 3:.1f}s; "
                          f"declared {timeout}s)")
        else:
            remedy.append("raise timeout to at least 3x the measured replay time")
        if isinstance(first_success, int | float):
            remedy.append(f"add start_period >= the measured first success "
                          f"({first_success:.0f}s; declared {start_period or 0}s)")
        else:
            remedy.append("add a start_period at or above the measured time to first "
                          "successful probe")
        return Attribution("probe-invocation", "; ".join(parts), ", ".join(remedy),
                           "1.6")

    # ---- still starting ---------------------------------------------------
    if (container.get("health_status") or "").lower() == "starting":
        return Attribution(
            "probe-starting",
            "the container is still starting and no probe has succeeded yet"
            + (f"; the last attempt exited {exit_code}" if exit_code is not None else ""),
            f"re-capture after the declared start period ({start_period or 0}s) has "
            "elapsed; if it never clears, the start period is the element to raise",
            "1.6",
            determined=False,
        )

    # ---- the honest fallback ----------------------------------------------
    known = [f"the probe is `{rendered_test(container.get('effective_test'))}`"]
    if exit_code is not None:
        known.append(f"the recorded attempt exited {exit_code}")
    if output.strip():
        known.append(f"its output was {first_line(output)!r}")
    if isinstance(slowest, int | float) and isinstance(timeout, int | float):
        known.append(f"the slowest attempt took {slowest:.2f}s against a declared "
                     f"timeout of {timeout:.0f}s")
    missing = []
    if replay is None:
        missing.append("the probe has not been replayed (Phase C, task 4.4), so a "
                       "failing invocation cannot be separated from a failing service")
    if exe is None:
        missing.append(f"`which {probe.executable or '<executable>'}` has not been run "
                       "(Phase D, task 4.4), so an absent executable is not ruled out")
    if saturated is None:
        missing.append(saturation_detail)
    return Attribution(
        "probe-undetermined",
        "not yet discriminated. What the capture shows: " + "; ".join(known)
        + (". What it cannot yet show: " + "; ".join(missing) if missing else ""),
        "run Phase C replay and Phase D `which` for this container (task 4.4), "
        "then re-classify",
        "1.8",
        determined=False,
    )


# --------------------------------------------------------------------------
# Record entries
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Entry:
    """One Diagnosis_Record entry. Exactly one per non-healthy container.

    Every field Requirement 1.1 names is present whether or not the evidence
    for it was collected, with an explicit null rather than a missing key: a
    reader must be able to tell "no probe ran" from "the field does not exist".
    """

    name: str
    service: str
    present: bool
    health_status: str | None
    failing_streak: int | None
    restart_count: int | None
    probe_source: str
    probe_declared_in: str
    effective_test: object
    rendered_test: str
    executable_name: str | None
    executable: dict | None
    probe_exit_code: int | None
    probe_output: str
    probe_duration_seconds: float | None
    slowest_probe_seconds: float | None
    declared_interval_seconds: float | None
    declared_timeout_seconds: float | None
    declared_start_period_seconds: float | None
    declared_retries: int | None
    measured_first_success_seconds: float | None
    replay: dict | None
    attribution: str
    attribution_rule: str
    remedy: str
    criterion: str
    determined: bool

    @property
    def health_state(self) -> str:
        if not self.present:
            return "absent from the daemon"
        if not self.health_status:
            return "no health state reported"
        streak = self.failing_streak
        return (f"{self.health_status} (failing streak {streak})"
                if streak is not None else str(self.health_status))


def diagnose(container: dict, host: dict | None = None) -> Entry:
    """One container's record entry. Pure."""
    attribution = attribute(container, host)
    attempt = evidence_attempt(container) or {}
    exe = executable_evidence(container)
    return Entry(
        name=container.get("name") or "<unnamed>",
        service=container.get("service") or "",
        present=bool(container.get("present", True)),
        health_status=container.get("health_status"),
        failing_streak=container.get("failing_streak"),
        restart_count=container.get("restart_count"),
        probe_source=container.get("probe_source") or "none",
        probe_declared_in=probe_declared_in(container),
        effective_test=container.get("effective_test"),
        rendered_test=rendered_test(container.get("effective_test")),
        executable_name=(exe or {}).get("name") or extract_executable(
            container.get("effective_test")),
        executable=exe,
        probe_exit_code=attempt.get("exit_code"),
        probe_output=attempt.get("output") or "",
        probe_duration_seconds=attempt.get("duration_seconds"),
        slowest_probe_seconds=slowest_attempt_seconds(container),
        declared_interval_seconds=container.get("declared_interval_seconds"),
        declared_timeout_seconds=container.get("declared_timeout_seconds"),
        declared_start_period_seconds=container.get("declared_start_period_seconds"),
        declared_retries=container.get("declared_retries"),
        measured_first_success_seconds=container.get("measured_first_success_seconds"),
        replay=_replay(container),
        attribution=attribution.element,
        attribution_rule=attribution.rule,
        remedy=attribution.remedy,
        criterion=attribution.criterion,
        determined=attribution.determined,
    )


# --------------------------------------------------------------------------
# The start-period rule (task 4.3, Requirement 1.6, Property 2)
# --------------------------------------------------------------------------

def measured_first_success(container: dict) -> float | None:
    """Seconds from container start to its first observed successful probe.

    Docker retains only the last five probe attempts, so the earliest log
    entry is not necessarily the container's first probe. The measurement is
    trusted only when the window demonstrably reaches back to startup: the
    earliest retained attempt must have begun within the declared start period
    plus two probe intervals of `StartedAt`. A five-hour-old container whose
    window holds five recent successes has an unobservable first success, and
    a rule that guessed from it would fail every long-running healthy
    container with a finding about its boot.
    """
    started = parse_docker_time(container.get("started_at"))
    if started is None:
        return None
    attempts: list[tuple[datetime, datetime | None, object]] = []
    for entry in container.get("probe_log") or []:
        if not isinstance(entry, dict):
            continue
        t_start = parse_docker_time(entry.get("start"))
        if t_start is None:
            continue
        attempts.append((t_start, parse_docker_time(entry.get("end")), entry.get("exit_code")))
    if not attempts:
        return None
    attempts.sort(key=lambda a: a[0])

    interval = container.get("declared_interval_seconds") or 30.0
    declared = container.get("declared_start_period_seconds") or 0.0
    if (attempts[0][0] - started).total_seconds() > declared + 2 * interval:
        return None

    success = next((a for a in attempts if a[2] == 0), None)
    if success is None:
        return None
    when = success[1] or success[0]
    seconds = (when - started).total_seconds()
    return seconds if seconds >= 0 else None


def annotate_first_success(evidence: dict) -> None:
    """Fill `measured_first_success_seconds` where it is derivable.

    Idempotent: a value already present (a committed capture re-classified via
    `--from-evidence`) is left alone.
    """
    for container in evidence.get("containers") or []:
        if (isinstance(container, dict)
                and container.get("measured_first_success_seconds") is None):
            container["measured_first_success_seconds"] = measured_first_success(container)


def start_period_findings(evidence: dict) -> list[Finding]:
    """Declared start period must cover the measured startup, per container.

    Evaluated for every container with a measurement, healthy ones included: a
    healthy container whose first success landed after its declared start
    period boots straight into a failing streak on any restart that is
    marginally slower than this one was. An absent start period is zero, not a
    skip -- `postgres` and `redis` declare none today, which is exactly the
    case Requirement 1.6 covers (hypothesis H4).
    """
    findings: list[Finding] = []
    for container in evidence.get("containers") or []:
        if not isinstance(container, dict):
            continue
        measured = container.get("measured_first_success_seconds")
        if not isinstance(measured, int | float):
            continue
        declared = container.get("declared_start_period_seconds") or 0.0
        if declared < measured:
            findings.append(Finding(
                rule="start-period",
                path=container.get("name") or "<unnamed>",
                observed=f"start_period {declared:g}s, first success at {measured:.1f}s",
                expected=f"start_period >= {measured:.1f}s",
                message="a restart marginally slower than this boot marks the "
                        "container unhealthy before it finishes starting",
            ))
    return findings


def is_healthy(container: dict) -> bool:
    return (container.get("health_status") or "").lower() == "healthy"


def classify(evidence: dict) -> tuple[list[Finding], list[Entry]]:
    """The classifier. Captured JSON in, findings and record entries out.

    Exactly one entry per container not reporting `healthy` -- Property 1 --
    and one finding per entry, whose rule names the attributed cause so the
    FAIL line carries the diagnosis rather than repeating "unhealthy".

    The one exception is a container absent from the daemon: `capture_findings`
    already reports that as `container-absent`, and two findings for one fact
    would double-count. The record entry is still produced, because Property 1
    is a statement about the record.
    """
    host = evidence.get("host") or {}
    containers = [c for c in (evidence.get("containers") or []) if isinstance(c, dict)]
    findings: list[Finding] = []
    entries: list[Entry] = []
    for container in containers:
        if is_healthy(container):
            continue
        entry = diagnose(container, host)
        entries.append(entry)
        if entry.attribution_rule == "container-absent":
            continue
        findings.append(Finding(
            rule=entry.attribution_rule,
            path=entry.name,
            observed=entry.health_status or "no health state",
            expected="healthy",
            message=entry.attribution,
        ))
    return findings, entries


# --------------------------------------------------------------------------
# The Diagnosis_Record
# --------------------------------------------------------------------------

def redact(text: str, denylist: Sequence[str] = ()) -> str:
    """Replace denylisted credential literals in narrative text.

    The evidence JSON keeps the probe verbatim, because a rendered credential
    is evidence about what the runtime actually invokes. The narrative record
    is a different artefact with a different obligation: it is a tracked file,
    and Requirement 4.3 says no tracked file carries a literal credential.
    `redis`'s effective probe carries the rendered `${REDIS_PASSWORD:-...}`
    fallback, so this is a live collision rather than a hypothetical one. The
    record says where the verbatim string is.
    """
    out = text or ""
    for literal in denylist:
        if literal and literal in out:
            out = out.replace(literal, REDACTED)
    return out


def _cell(value: object) -> str:
    """A table cell: pipes escaped, newlines flattened."""
    text = "-" if value is None or value == "" else str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _seconds(value: object) -> str:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return "-"
    return f"{value:.2f}s" if value < 10 else f"{value:.0f}s"


def _verbatim(label: str, text: str, denylist: Sequence[str]) -> list[str]:
    """A bullet whose value may be a traceback.

    A multi-line output on a bullet line stops being readable and stops being
    markdown, so it moves into a fenced block under the same label. The label
    is identical either way, which is what makes the record greppable.
    """
    clean = redact(text or "", denylist)
    if not clean.strip():
        return [f"- {label}: none recorded"]
    lines = clean.rstrip("\n").splitlines()
    if len(lines) == 1 and len(lines[0]) <= 160:
        return [f"- {label}: `{lines[0]}`"]
    return [f"- {label}:", "", "  ```", *[f"  {line}" for line in lines], "  ```", ""]


def render_record(evidence: dict, entries: Sequence[Entry], *,
                  denylist: Sequence[str] = ()) -> str:
    """The Diagnosis_Record, in the design's per-container section format.

    One `###` section per non-healthy container and no section for a healthy
    one, which is what makes "exactly one entry per non-healthy container"
    checkable by reading the record rather than by trusting the generator.
    Healthy containers still appear, as a table: a record that omitted them
    would not show that 14 of 15 probes pass, which is the single most
    important fact about this capture.
    """
    containers = [c for c in (evidence.get("containers") or []) if isinstance(c, dict)]
    healthy = [c for c in containers if is_healthy(c)]
    host = evidence.get("host") or {}
    captured_at = evidence.get("captured_at") or "unknown"

    out: list[str] = [
        "# Container Health Diagnosis",
        "",
        "Diagnosis_Record for Requirement 1. Generated by "
        "`python -m scripts.verify.health_diagnose --emit-record "
        f"{DIAGNOSIS_PATH}`; regenerate it rather than editing it.",
        "",
        f"- Evidence: `{EVIDENCE_PATH}`, captured {captured_at}",
        f"- Containers declared by the `kailash-ai` profile: {len(containers)}",
        f"- Reporting `healthy`: {len(healthy)}",
        f"- Not reporting `healthy`: {len(entries)}",
        "",
    ]

    if len(containers) and not entries:
        out += ["Every declared container reports `healthy`. No attribution is "
                "required, and none is invented.", ""]

    if entries:
        out += [
            "## Containers not reporting healthy",
            "",
            "| Container | Service | Health state | Probe declared in | Attributed to | Criterion |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for e in entries:
            out.append(
                f"| `{_cell(e.name)}` | {_cell(e.service)} | {_cell(e.health_state)} "
                f"| {_cell(e.probe_declared_in)} | `{_cell(e.attribution_rule)}` "
                f"| {_cell(e.criterion)} |")
        out.append("")

    if healthy:
        out += [
            "## Containers reporting healthy",
            "",
            "Recorded because Requirement 1.2 is a claim about all fifteen "
            "containers, and because a probe that passes today with no headroom "
            "against its timeout is next week's finding.",
            "",
            "| Container | Effective test | Executable | Last exit | Slowest attempt | Declared timeout | Start period |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for c in healthy:
            attempt = evidence_attempt(c) or {}
            out.append(
                f"| `{_cell(c.get('name'))}` "
                f"| `{_cell(redact(rendered_test(c.get('effective_test')), denylist))}` "
                f"| {_cell(extract_executable(c.get('effective_test')))} "
                f"| {_cell(attempt.get('exit_code'))} "
                f"| {_seconds(slowest_attempt_seconds(c))} "
                f"| {_seconds(c.get('declared_timeout_seconds'))} "
                f"| {_seconds(c.get('declared_start_period_seconds'))} |")
        out.append("")

    if entries:
        out += ["## Diagnosis", ""]
        for e in entries:
            out += [f"### {e.name}", ""]
            out.append(f"- Health state: {e.health_state}")
            out.append(f"- Probe declared in: {e.probe_declared_in}")
            out.append(f"- Effective test: "
                       f"`{redact(e.rendered_test, denylist)}`")
            if e.executable:
                exe = e.executable
                verdict = "present" if exe.get("present") else "absent"
                out.append(
                    f"- Executable: {exe.get('name')} -- {verdict} "
                    f"(`which {exe.get('name')}` -> "
                    f"{_cell(first_line(str(exe.get('which_output') or '')) or 'no output')}, "
                    f"exit {exe.get('which_exit_code')})")
            elif e.executable_name:
                out.append(f"- Executable: {e.executable_name} -- `which` not yet run "
                           "(Phase D, task 4.4)")
            else:
                out.append("- Executable: none -- there is no probe to extract one from")
            out.append(f"- Last probe exit code: {_cell(e.probe_exit_code)}")
            out += _verbatim("Last probe output", e.probe_output, denylist)
            if e.replay:
                duration = e.replay.get("duration_seconds")
                shown = f" in {duration:.2f}s" if isinstance(duration, int | float) else ""
                detail = (str(e.replay.get("stderr") or "")
                          or str(e.replay.get("stdout") or ""))
                out.append(f"- Manual replay: exit {_cell(e.replay.get('exit_code'))}"
                           f"{shown} -- "
                           f"{redact(first_line(detail) or 'no output', denylist)}")
            else:
                out.append("- Manual replay: not run (Phase C, task 4.4)")
            out.append(
                f"- Declared: interval {_seconds(e.declared_interval_seconds)}, "
                f"timeout {_seconds(e.declared_timeout_seconds)}, "
                f"start period {_seconds(e.declared_start_period_seconds)}, "
                f"retries {_cell(e.declared_retries)}")
            if e.measured_first_success_seconds is not None:
                out.append("- Measured time to first successful probe: "
                           f"{_seconds(e.measured_first_success_seconds)}")
            out.append(f"- Attribution: {redact(e.attribution, denylist)}")
            out.append(f"- Remedy: {e.remedy} (Requirement {e.criterion})")
            out.append("")

    saturated, detail = host_saturation(host)
    out += [
        "## Host resource assessment",
        "",
        f"- Memory ceiling: {_cell(host.get('mem_total_bytes'))} bytes",
        f"- CPUs: {_cell(host.get('ncpu'))}",
        f"- Containers running: {_cell(host.get('containers_running'))}",
        f"- Docker: {_cell(host.get('docker_version'))} "
        f"({_cell(host.get('docker_os_arch'))})",
        f"- Clock skew, container minus host: "
        f"{_cell(host.get('clock_skew_seconds'))}s",
        "",
    ]
    if saturated is None:
        out += [
            f"H1 verdict: **not yet assessed**. {detail}. Task 4.5 runs the Phase B "
            "uniform-cause probes and writes the verdict here; task 12.1 reads it "
            "and cannot proceed until it exists.",
            "",
        ]
    else:
        out += [f"H1 verdict: **{'confirmed' if saturated else 'refuted'}**. {detail}",
                ""]

    if denylist:
        out += [
            "---",
            "",
            f"`{REDACTED}` marks a credential literal from "
            "`scripts/verify/data/denylist.txt` that a compose fallback rendered "
            f"into the live probe. The verbatim string is in `{EVIDENCE_PATH}`; it "
            "is redacted here because this record is a tracked file and "
            "Requirement 4.3 says no tracked file carries a literal credential.",
            "",
        ]
    return "\n".join(out)


def write_record(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def read_evidence(path: Path) -> dict:
    """A previously captured evidence file, for classifying without a daemon."""
    if not path.is_file():
        raise Usage(f"--from-evidence {path} does not exist")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        raise Usage(f"--from-evidence {path} does not parse: {exc}") from exc
    if not isinstance(loaded, dict) or "containers" not in loaded:
        raise Usage(f"--from-evidence {path} is not a Phase A evidence file")
    return loaded


if __name__ == "__main__":
    raise SystemExit(main())
