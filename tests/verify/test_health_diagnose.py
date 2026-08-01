"""Phase A collector tests: the commands issued, and what survives bad output.

Two things are worth asserting about a collector, and they are the two the task
names. First, the *exact* commands: the whole point of reading the effective
probe from `.Config.Healthcheck` is lost if the collector quietly reads
something else, and only the recorded argv proves which it read. Second, that
malformed output is preserved rather than raised: a truncated capture is real
evidence about a real container, and a collector that raises on it loses both
the container and every container after it.

Nothing here needs a daemon. The fake executor from the harness scripts every
command by its exact text, and the captured shapes come from
`tests/verify/fixtures/inspect_*.json`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from scripts.verify import health_diagnose as hd
from scripts.verify.common import Exit, Unavailable

from .conftest import load_fixture, read_fixture

# Written out rather than derived from the module, so a change to the format
# strings has to be made twice -- once in the collector, once here as a
# deliberate act. A test that builds its expectation from the code under test
# asserts only that the code equals itself.
FORMATS = {
    "health": "{{json .State.Health}}",
    "effective": "{{json .Config.Healthcheck}}",
    "state": "{{json .State}}",
    "restarts": "{{.RestartCount}}",
}

VERSION_JSON = json.dumps({
    "Client": {"Version": "29.6.2"},
    "Server": {"Version": "29.6.2", "Os": "linux", "Arch": "amd64"},
})
INFO_JSON = json.dumps({
    "MemTotal": 8261832704, "NCPU": 8, "ContainersRunning": 15,
    "KernelVersion": "6.6.114.1-microsoft-standard-WSL2",
})

COMPOSE = """
services:
  frontend:
    container_name: kailash-frontend
  forecasting:
    container_name: kailash-forecasting
  postgres:
    container_name: kailash-postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kailash"]
"""


def inspect_cmd(name: str, key: str) -> str:
    return f"docker inspect --format {FORMATS[key]} {name}"


def script_host(fake, *, roster: str = "") -> None:
    fake.script("docker version --format {{json .}}", 0, VERSION_JSON)
    fake.script("docker info --format {{json .}}", 0, INFO_JSON)
    fake.script(
        "docker ps -a --no-trunc --format {{.Names}}\t{{.Image}}\t{{.ID}}\t{{.Status}}",
        0, roster)
    fake.script("docker image inspect alpine --format {{.Id}}", 0, "sha256:deadbeef\n")
    fake.script("docker run --rm alpine date -u +%s", 0, "1767607200\n")


def script_capture(fake, fixture: dict, *, name: str | None = None) -> None:
    """Script the four captures for one container from a fixture."""
    name = name or fixture["name"]
    for key in ("health", "effective", "state"):
        fake.script(inspect_cmd(name, key), 0, json.dumps(fixture.get(key)))
    fake.script(inspect_cmd(name, "restarts"), 0, f"{fixture.get('restarts', 0)}\n")


def script_all(fake, fixtures: dict[str, dict]) -> None:
    """`{container_name: fixture}`, plus a roster line per container."""
    roster = "\n".join(
        f"{n}\timage-for-{n}\tcid-{n}\tUp 24 hours" for n in fixtures
    )
    script_host(fake, roster=roster)
    for name, fixture in fixtures.items():
        script_capture(fake, fixture, name=name)


def fake_clock():
    """Monotonic host clock, one second per read, starting at a known epoch."""
    state = {"t": 1767607200.0}

    def read() -> float:
        state["t"] += 1.0
        return state["t"]

    return read


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "docker-compose.yml").write_text(COMPOSE, encoding="utf-8")
    return tmp_path


# --------------------------------------------------------------------------
# The commands issued
# --------------------------------------------------------------------------

def test_issues_exactly_the_four_captures_for_every_declared_container(repo, fake_executor):
    script_all(fake_executor, {
        "kailash-frontend": load_fixture("inspect_no_healthcheck.json"),
        "kailash-forecasting": load_fixture("inspect_replay_succeeds.json"),
        "kailash-postgres": load_fixture("inspect_healthy.json"),
    })

    hd.collect(repo, fake_executor, clock=fake_clock())

    issued = fake_executor.commands()
    for name in ("kailash-frontend", "kailash-forecasting", "kailash-postgres"):
        assert [c for c in issued if f" {name}" in c] == [
            inspect_cmd(name, "health"),
            inspect_cmd(name, "effective"),
            inspect_cmd(name, "state"),
            inspect_cmd(name, "restarts"),
        ]
    assert len([c for c in issued if c.startswith("docker inspect --format")]) == 12


def test_reads_the_probe_from_config_healthcheck_and_never_from_compose(repo, fake_executor):
    """Nine of fifteen probes are baked into the image, so compose is the wrong
    file to read a probe from. The collector must not consult it for one."""
    script_all(fake_executor, {
        "kailash-frontend": load_fixture("inspect_no_healthcheck.json"),
        "kailash-forecasting": load_fixture("inspect_replay_succeeds.json"),
        "kailash-postgres": load_fixture("inspect_healthy.json"),
    })

    evidence = hd.collect(repo, fake_executor, clock=fake_clock())
    by_name = {c["name"]: c for c in evidence["containers"]}

    # The image-level probe: compose declares no healthcheck for `forecasting`,
    # yet the effective test is present, so its source is the image.
    forecasting = by_name["kailash-forecasting"]
    assert forecasting["compose_declares_healthcheck"] is False
    assert forecasting["probe_source"] == "image"
    assert forecasting["effective_test"] == \
        load_fixture("inspect_replay_succeeds.json")["effective"]["Test"]

    assert by_name["kailash-postgres"]["probe_source"] == "compose"
    assert by_name["kailash-frontend"]["probe_source"] == "none"

    fake_executor.assert_never("docker compose")
    fake_executor.assert_never("config --format")


def test_host_facts_come_from_version_info_and_a_container_clock(repo, fake_executor):
    script_all(fake_executor, {"kailash-postgres": load_fixture("inspect_healthy.json")})

    host = hd.collect(repo, fake_executor, clock=fake_clock())["host"]

    assert host["docker_version"] == "29.6.2"
    assert host["mem_total_bytes"] == 8261832704
    assert host["ncpu"] == 8
    # Host reads bracket the container run at 1767607201 and 1767607202, so the
    # midpoint is 1767607201.5 and the container's 1767607200 is 1.5s behind.
    assert host["clock_skew_seconds"] == pytest.approx(-1.5)
    assert host["clock"]["host_window_seconds"] == pytest.approx(1.0)
    assert host["clock"]["pulled"] is False
    assert "docker pull alpine" not in fake_executor.commands()


def test_clock_image_is_pulled_before_the_timed_window(repo, fake_executor):
    """A pull inside the measurement would add its download time to the host
    midpoint and turn the skew figure into a measurement of network speed."""
    script_all(fake_executor, {"kailash-postgres": load_fixture("inspect_healthy.json")})
    fake_executor.script("docker image inspect alpine --format {{.Id}}", 1, "",
                         "Error: No such image: alpine")

    host = hd.collect(repo, fake_executor, clock=fake_clock())["host"]

    issued = fake_executor.commands()
    assert issued.index("docker pull alpine") < issued.index("docker run --rm alpine date -u +%s")
    assert host["clock"]["pulled"] is True


# --------------------------------------------------------------------------
# Bad output is preserved, not raised
# --------------------------------------------------------------------------

def test_truncated_capture_is_preserved_rather_than_raised(repo, fake_executor):
    truncated = read_fixture("inspect_truncated.json")
    script_all(fake_executor, {"kailash-postgres": load_fixture("inspect_healthy.json")})
    fake_executor.script(inspect_cmd("kailash-forecasting", "health"), 0, truncated)
    fake_executor.script(inspect_cmd("kailash-forecasting", "effective"), 0, "null")
    fake_executor.script(inspect_cmd("kailash-forecasting", "state"), 0, '{"Status":"running"}')
    fake_executor.script(inspect_cmd("kailash-forecasting", "restarts"), 0, "0")

    evidence = hd.collect(repo, fake_executor, clock=fake_clock())
    forecasting = next(c for c in evidence["containers"] if c["name"] == "kailash-forecasting")

    # Verbatim: the bytes docker printed, not a normalised or repaired form.
    assert forecasting["raw"]["health"]["stdout"] == truncated
    assert "health" in forecasting["parse_errors"]
    assert forecasting["health_status"] is None
    # And the containers after it were still captured.
    assert {c["name"] for c in evidence["containers"]} == {
        "kailash-frontend", "kailash-forecasting", "kailash-postgres"}

    findings = hd.capture_findings(evidence)
    assert any(f.rule == "capture-unparsed" and f.path == "kailash-forecasting:health"
               for f in findings)


def test_non_integer_restart_count_is_recorded_not_raised(repo, fake_executor):
    script_all(fake_executor, {"kailash-postgres": load_fixture("inspect_healthy.json")})
    fake_executor.script(inspect_cmd("kailash-postgres", "restarts"), 0, "<no value>\n")

    evidence = hd.collect(repo, fake_executor, clock=fake_clock())
    postgres = next(c for c in evidence["containers"] if c["name"] == "kailash-postgres")

    assert postgres["restart_count"] is None
    assert "restarts" in postgres["parse_errors"]


def test_absent_container_is_evidence_not_an_error(repo, fake_executor):
    script_all(fake_executor, {"kailash-postgres": load_fixture("inspect_healthy.json")})
    for key in FORMATS:
        fake_executor.script(inspect_cmd("kailash-forecasting", key), 1, "",
                             "Error response from daemon: No such container: kailash-forecasting")

    evidence = hd.collect(repo, fake_executor, clock=fake_clock())
    forecasting = next(c for c in evidence["containers"] if c["name"] == "kailash-forecasting")

    assert forecasting["present"] is False
    assert forecasting["capture_failed"] == ["health", "effective", "state", "restarts"]
    findings = hd.capture_findings(evidence)
    assert [f.rule for f in findings if f.path == "kailash-forecasting"] == ["container-absent"]


# --------------------------------------------------------------------------
# The probe log, which is what task 4.3 measures from
# --------------------------------------------------------------------------

def test_probe_log_is_preserved_in_full_with_per_attempt_duration(repo, fake_executor):
    fixture = load_fixture("inspect_executable_absent.json")
    script_all(fake_executor, {"kailash-postgres": fixture})

    evidence = hd.collect(repo, fake_executor, clock=fake_clock())
    entry = next(c for c in evidence["containers"]
                 if c["name"] == "kailash-postgres")["probe_log"][0]
    original = fixture["health"]["Log"][0]

    assert entry["start"] == original["Start"]
    assert entry["end"] == original["End"]
    assert entry["exit_code"] == original["ExitCode"]
    assert entry["output"] == original["Output"]
    # 10:00:00.100 -> 10:00:00.180, nine fractional digits, which the stdlib
    # ISO parser rejects outright.
    assert entry["duration_seconds"] == pytest.approx(0.08)


def test_declared_start_period_absent_is_zero_not_missing(repo, fake_executor):
    """postgres and redis declare no start period today, and treating absence
    as "skip" would hide exactly the case Requirement 1.6 covers."""
    fixture = load_fixture("inspect_healthy.json")
    assert "StartPeriod" not in fixture["effective"]
    script_all(fake_executor, {"kailash-postgres": fixture})

    evidence = hd.collect(repo, fake_executor, clock=fake_clock())
    postgres = next(c for c in evidence["containers"] if c["name"] == "kailash-postgres")

    assert postgres["declared_start_period_seconds"] == 0
    assert postgres["declared_timeout_seconds"] == pytest.approx(10.0)
    assert postgres["declared_interval_seconds"] == pytest.approx(30.0)


def test_in_flight_probe_yields_no_duration_rather_than_a_negative_one(repo, fake_executor):
    script_all(fake_executor, {"kailash-postgres": load_fixture("inspect_healthy.json")})
    fake_executor.script(inspect_cmd("kailash-postgres", "health"), 0, json.dumps({
        "Status": "starting", "FailingStreak": 0,
        "Log": [{"Start": "2026-01-05T10:00:00.000000000Z",
                 "End": "0001-01-01T00:00:00Z", "ExitCode": 0, "Output": ""}],
    }))

    evidence = hd.collect(repo, fake_executor, clock=fake_clock())
    entry = next(c for c in evidence["containers"]
                 if c["name"] == "kailash-postgres")["probe_log"][0]

    assert entry["duration_seconds"] is None
    assert entry["end"] == "0001-01-01T00:00:00Z"


# --------------------------------------------------------------------------
# An unreachable daemon classifies nothing
# --------------------------------------------------------------------------

def test_unreachable_daemon_is_unavailable_and_inspects_nothing(repo, fake_executor):
    fake_executor.script("docker version --format {{json .}}", 1, "",
                         "Cannot connect to the Docker daemon at unix:///var/run/docker.sock.")

    with pytest.raises(Unavailable):
        hd.collect(repo, fake_executor, clock=fake_clock())

    fake_executor.assert_never("docker inspect")
    fake_executor.assert_never("docker ps")


def test_daemon_failure_exits_unavailable_and_writes_no_evidence(repo, fake_executor):
    fake_executor.script("docker version --format {{json .}}", 1, "", "Cannot connect")
    evidence_path = repo / "docs" / "records" / "container-health-evidence.json"

    args = argparse.Namespace(root=repo, json=False, emit_record=None,
                              evidence=evidence_path, execute=fake_executor)
    with pytest.raises(Unavailable):
        hd.build_report(args)

    assert not evidence_path.exists()


# --------------------------------------------------------------------------
# The evidence file
# --------------------------------------------------------------------------

def test_writes_the_evidence_file_in_the_designed_schema(repo, fake_executor):
    script_all(fake_executor, {
        "kailash-frontend": load_fixture("inspect_no_healthcheck.json"),
        "kailash-forecasting": load_fixture("inspect_http_error_traceback.json"),
        "kailash-postgres": load_fixture("inspect_healthy.json"),
    })
    evidence_path = repo / "docs" / "records" / "container-health-evidence.json"

    args = argparse.Namespace(root=repo, json=False, emit_record=None,
                              evidence=evidence_path, execute=fake_executor)
    report = hd.build_report(args)

    written = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert set(written) >= {"captured_at", "host", "containers", "summary"}
    assert set(written["host"]) >= {"docker_version", "mem_total_bytes", "clock_skew_seconds"}
    for container in written["containers"]:
        assert set(container) >= {
            "name", "health_status", "failing_streak", "restart_count", "probe_source",
            "effective_test", "executable", "probe_log", "replay",
            "measured_first_success_seconds", "declared_start_period_seconds", "attribution",
        }
        # The fields later phases fill are present and null, so a reader can
        # tell "not collected yet" from "no such concept".
        assert container["executable"] is None
        assert container["replay"] is None
        assert container["attribution"] is None

    # The capture succeeded, but the check still fails: the classifier runs on
    # every invocation, and this trio contains a container with no probe and a
    # container whose service rejects its probe.
    assert report.exit_code() == Exit.FAILED
    assert {(f.rule, f.path) for f in report.findings} == {
        ("probe-absent", "kailash-frontend"),
        ("service-rejects-probe", "kailash-forecasting"),
    }
    assert written["summary"]["probe_source_counts"] == {"compose": 1, "image": 1, "none": 1}
    assert written["summary"]["without_probe"] == ["kailash-frontend"]


def test_a_credential_literal_in_the_capture_is_flagged_without_being_echoed(repo, fake_executor):
    """`redis`'s compose probe renders `${REDIS_PASSWORD:-<fallback>}`, so the
    effective probe carries the fallback verbatim. Capturing it is correct;
    committing it silently is not."""
    literal = "not-a-real-password-fixture"
    (repo / "scripts" / "verify" / "data").mkdir(parents=True)
    (repo / "scripts" / "verify" / "data" / "denylist.txt").write_text(
        f"# fixture\n{literal}\n", encoding="utf-8")
    script_all(fake_executor, {"kailash-postgres": load_fixture("inspect_healthy.json")})
    fake_executor.script(inspect_cmd("kailash-postgres", "effective"), 0, json.dumps(
        {"Test": ["CMD", "redis-cli", "-a", literal, "ping"], "Interval": 30000000000}))

    args = argparse.Namespace(root=repo, json=False, emit_record=None,
                              evidence=repo / "evidence.json", execute=fake_executor)
    report = hd.build_report(args)

    flagged = [n for n in report.notes if "denylist.txt" in n]
    assert flagged, report.notes
    assert "kailash-postgres" in flagged[0]
    assert literal not in flagged[0]
    # Verbatim in the artefact, all the same: redacting would destroy the
    # evidence that the fallback is what the runtime probe actually uses.
    assert literal in (repo / "evidence.json").read_text(encoding="utf-8")


def test_missing_compose_file_is_unavailable(tmp_path, fake_executor):
    script_host(fake_executor)
    with pytest.raises(Unavailable):
        hd.collect(tmp_path, fake_executor, clock=fake_clock())
