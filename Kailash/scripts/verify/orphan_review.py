"""Orphan review: every container on the Docker host is accounted for, or named.

The accountability model (design Component 7) is label-based, never name-based.
A container is accounted for when either:

* its `com.docker.compose.project.config_files` label resolves to a compose
  file tracked in this repository -- ownership proven by what started it, not
  by what it is called, because a container named `kailash-backend` started by
  hand from an unrelated compose file is not the stack's backend; or
* its name appears in `scripts/verify/data/retained_containers.json`, the one
  source of truth for reviewed dispositions. `docs/records/docker-host-cleanup.md`
  is *generated* from that file by `--emit-record`: a hand-written record plus
  a machine-read list is two sources that will disagree.

Anything else is a finding, printed with name and image (Requirement 7.6):
`removal-pending` when the file records an explicit `remove` disposition
awaiting operator execution (task 13.4), `unaccounted-container` when it
records nothing. Both exit 1 -- the review goes green only when `docker ps`
lists nothing but the compose stack and the reviewed retained set (7.4).

The module splits collector from classifier, as `health_diagnose.py` does. The
**collector** shells out to Docker -- `docker version`, `docker ps` and
per-container `docker inspect`, all read-only -- and writes what it saw to
`docs/records/orphan-review-evidence.json`. It captures labels, ports, state,
created, image and command, and deliberately **never `.Config.Env`**: the
stack's environment carries credential values, and an evidence file that
embedded them could never be committed. The **classifier** is a pure function
from that evidence plus the parsed retained list to findings and per-container
assessments, so every disposition shape is testable from synthetic container
lists with no daemon.

Retained entries are validated against the shape formalised in
`scripts/verify/data/retained_containers.schema.json`. A malformed entry is a
finding and the entry is dropped, so the container it names reappears as
unaccounted rather than being silently skipped. Every retained entry must
carry a non-empty `owner` (7.2), and whenever the container publishes a port,
the port and its bind address must be recorded (7.5) -- that field is what
makes "what is listening on this box" answerable.

The removal path (`--execute-removals NAME... --yes`) is the confirmation gate
of Requirement 7.3 / Property 15. `docker rm` is issued only when all of these
hold, and any refusal is `Exit.USAGE` with no command issued:

* `--yes` is present -- but `--yes` alone is insufficient;
* the run names the containers it intends to remove, and the named set equals,
  as a set, the observed containers carrying a recorded `remove` disposition.
  So a stale `--yes` cannot remove something added since, a retained or
  undispositioned container can never reach a `docker rm` argv, and a recorded
  candidate cannot be quietly skipped;
* the review ran against the live daemon: `--from-evidence` cannot confirm a
  removal, because the artifact may be older than the host.

Exit codes follow `common.py`: 0 everything accounted, 1 findings (unaccounted
containers, pending removals, invalid retained entries), 2 daemon or git
unavailable, 3 usage -- including every refused removal.

Usage:

    python -m scripts.verify.orphan_review \
        --emit-record docs/records/docker-host-cleanup.md
    python -m scripts.verify.orphan_review \
        --from-evidence docs/records/orphan-review-evidence.json
    python -m scripts.verify.orphan_review --execute-removals NAME [NAME ...] --yes
"""
from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Iterable, Sequence
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
    tracked_files,
)
from .health_diagnose import (
    Executor,
    default_execute,
    parse_json_capture,
    require_daemon,
)

RETAINED_PATH = "scripts/verify/data/retained_containers.json"
SCHEMA_PATH = "scripts/verify/data/retained_containers.schema.json"
EVIDENCE_PATH = "docs/records/orphan-review-evidence.json"
RECORD_PATH = "docs/records/docker-host-cleanup.md"

CONFIG_FILES_LABEL = "com.docker.compose.project.config_files"
PROJECT_LABEL = "com.docker.compose.project"
SERVICE_LABEL = "com.docker.compose.service"

# Dispositions an observed container can end the review with.
COMPOSE_OWNED = "compose-owned"
RETAINED = "retained"
REMOVE_PROPOSED = "remove-proposed"
UNACCOUNTED = "unaccounted"
ABSENT = "absent"  # vanished between `docker ps` and `docker inspect`

# The entry shapes, mirrored in retained_containers.schema.json. A test holds
# the two in agreement, so the schema file cannot drift from what this module
# enforces.
REQUIRED_RETAINED_KEYS = ("name", "image", "owner", "published_ports",
                          "justification", "reviewed")
REQUIRED_REMOVAL_KEYS = ("name", "image", "reason", "reviewed")
REQUIRED_PORT_KEYS = ("host_ip", "host_port", "container_port")

_REVIEWED = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# --------------------------------------------------------------------------
# Collector -- read-only by construction
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Capture:
    key: str
    fmt: str


# Deliberately absent: `{{json .Config}}` and `{{json .Config.Env}}`. The
# compose stack's environment carries credential values, so the evidence file
# would embed denylisted literals and could never be committed.
CAPTURES: tuple[Capture, ...] = (
    Capture("labels", "{{json .Config.Labels}}"),
    Capture("ports", "{{json .NetworkSettings.Ports}}"),
    Capture("state", "{{json .State}}"),
    Capture("created", "{{.Created}}"),
    Capture("image", "{{.Config.Image}}"),
    Capture("entrypoint", "{{json .Config.Entrypoint}}"),
    Capture("cmd", "{{json .Config.Cmd}}"),
)

PS_ARGV = ["docker", "ps", "-a", "--no-trunc",
           "--format", "{{.Names}}\t{{.Image}}\t{{.ID}}\t{{.Status}}"]


def inspect_argv(name: str, fmt: str) -> list[str]:
    return ["docker", "inspect", "--format", fmt, name]


def _run(execute: Executor, argv: Sequence[str], **kwargs) -> dict:
    """One command, reduced to a recordable result. Never raises on failure."""
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
    return {"argv": list(argv), "exit_code": proc.returncode,
            "stdout": proc.stdout or "", "stderr": proc.stderr or ""}


def parse_ps(stdout: str) -> list[dict]:
    """`docker ps -a` lines, in daemon order."""
    out = []
    for line in (stdout or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 4 or not parts[0].strip():
            continue
        name, image, cid, status = (p.strip() for p in parts[:4])
        out.append({"name": name, "image": image, "container_id": cid, "status": status})
    return out


def tracked_compose_files(root: Path) -> list[str]:
    """Absolute paths of every compose file git tracks in this repository.

    The accountability rule compares these against the
    `com.docker.compose.project.config_files` label, which records the
    absolute path compose was invoked with -- so the tracked set is
    materialised as absolute paths too.
    """
    out = []
    for rel in tracked_files(root):
        base = rel.rsplit("/", 1)[-1].casefold()
        if "compose" in base and base.endswith((".yml", ".yaml")):
            out.append(str(root / rel))
    return out


def parse_published_ports(ports: object) -> list[dict]:
    """Only the published bindings out of `.NetworkSettings.Ports`.

    The raw shape is `{"80/tcp": [{"HostIp": "127.0.0.1", "HostPort":
    "3000"}], "5432/tcp": null}`; a null value is an exposed-but-unpublished
    port, which is not listening on the host and therefore not evidence 7.5
    asks for.
    """
    if not isinstance(ports, dict):
        return []
    out = []
    for container_port, bindings in sorted(ports.items()):
        if not isinstance(bindings, list):
            continue
        for binding in bindings:
            if isinstance(binding, dict):
                out.append({
                    "host_ip": str(binding.get("HostIp") or ""),
                    "host_port": str(binding.get("HostPort") or ""),
                    "container_port": str(container_port),
                })
    return out


def render_command(entrypoint: object, cmd: object) -> str:
    """Entrypoint and cmd as the one line `docker ps` calls Command."""
    parts: list[str] = []
    for chunk in (entrypoint, cmd):
        if isinstance(chunk, list):
            parts.extend(str(x) for x in chunk)
        elif isinstance(chunk, str) and chunk.strip():
            parts.append(chunk.strip())
    return " ".join(parts)


def collect_container(execute: Executor, entry: dict) -> dict:
    """The seven captures for one container, plus what reads straight off them."""
    name = entry["name"]
    raw = {c.key: _run(execute, inspect_argv(name, c.fmt)) for c in CAPTURES}

    parsed: dict[str, object] = {}
    parse_errors: dict[str, str] = {}
    for key in ("labels", "ports", "state", "entrypoint", "cmd"):
        value, error = parse_json_capture(raw[key]["stdout"])
        parsed[key] = value
        if error:
            parse_errors[key] = error

    failed = [c.key for c in CAPTURES if raw[c.key]["exit_code"] != 0]
    labels = parsed["labels"] if isinstance(parsed["labels"], dict) else {}
    state = parsed["state"] if isinstance(parsed["state"], dict) else {}
    config_image = raw["image"]["stdout"].strip()

    return {
        "name": name,
        "image": config_image or entry.get("image") or "",
        "container_id": entry.get("container_id"),
        "ps_status": entry.get("status"),
        "created": raw["created"]["stdout"].strip(),
        "state_status": state.get("Status"),
        "started_at": state.get("StartedAt"),
        "labels": labels,
        "compose_project": str(labels.get(PROJECT_LABEL) or ""),
        "compose_service": str(labels.get(SERVICE_LABEL) or ""),
        "compose_config_files": str(labels.get(CONFIG_FILES_LABEL) or ""),
        "published_ports": parse_published_ports(parsed["ports"]),
        "command": render_command(parsed["entrypoint"], parsed["cmd"]),
        "present": len(failed) < len(CAPTURES),
        "capture_failed": failed,
        "parse_errors": parse_errors,
        "raw": raw,
    }


def collect(root: Path, execute: Executor) -> dict:
    """The whole capture. Raises only `Unavailable`.

    Every argv issued here is `docker version`, `docker ps` or `docker
    inspect`. Removal lives behind `remove()` and its gate, and the tests hold
    the two apart with the recording executor.
    """
    require_daemon(execute)
    ps = _run(execute, PS_ARGV)
    if ps["exit_code"] != 0:
        detail = (ps["stderr"] or "").strip().splitlines()
        raise Unavailable("docker ps failed: " + (detail[0] if detail else "no detail"))
    entries = parse_ps(ps["stdout"])
    return {
        "captured_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/verify/orphan_review.py",
        "compose_files": tracked_compose_files(root),
        "containers": [collect_container(execute, entry) for entry in entries],
    }


def write_evidence(evidence: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


# ==========================================================================
# Classifier -- a pure function of the evidence and the retained list
# ==========================================================================
#
# Nothing below this line calls a subprocess or contacts Docker, except the
# explicitly gated `remove()` at the very bottom, which receives its executor
# and issues nothing unless `confirmed` is true.

def normalize_path(path: object) -> str:
    """A path as a comparison key: slashes unified, case folded, quotes shed.

    Pure string work, no filesystem: the classifier compares a path Docker
    recorded on the host against paths git listed, and on Windows the same
    file arrives spelled `C:\\...` from one and `C:/...` from the other.
    """
    text = str(path or "").strip().strip('"').strip("'").replace("\\", "/")
    while "//" in text:
        text = text.replace("//", "/")
    return text.rstrip("/").casefold()


def label_config_files(value: object) -> list[str]:
    """The config-files label, split. Compose joins multiple files with commas."""
    return [p.strip() for p in str(value or "").split(",") if p.strip()]


@dataclass(frozen=True)
class RetainedDoc:
    """The parsed retained list: valid entries by name, plus what was wrong."""

    retained: dict[str, dict]
    removals: dict[str, dict]
    findings: tuple[Finding, ...]


def _entry_defects(entry: object, required: tuple[str, ...]) -> list[str]:
    """Everything wrong with one entry, in schema terms."""
    if not isinstance(entry, dict):
        return [f"entry is {type(entry).__name__}, not an object"]
    defects = []
    for key in required:
        value = entry.get(key)
        if key == "published_ports":
            if not isinstance(value, list):
                defects.append("published_ports is missing or not a list")
                continue
            for index, port in enumerate(value):
                if not isinstance(port, dict) or set(port) != set(REQUIRED_PORT_KEYS) or any(
                        not str(port.get(k) or "").strip() for k in REQUIRED_PORT_KEYS):
                    defects.append(
                        f"published_ports[{index}] must carry exactly "
                        + ", ".join(REQUIRED_PORT_KEYS))
            continue
        if not isinstance(value, str) or not value.strip():
            defects.append(f"{key} is missing or empty")
        elif key == "reviewed" and not _REVIEWED.match(value.strip()):
            defects.append(f"reviewed is {value!r}, not YYYY-MM-DD")
    unknown = sorted(set(entry) - set(required))
    if unknown:
        defects.append("unknown key(s): " + ", ".join(unknown))
    return defects


def read_retained_doc(raw: object, source: str = RETAINED_PATH) -> RetainedDoc:
    """Validate and index the retained list. Pure.

    An invalid entry is a finding and is dropped, so the container it names
    reappears as unaccounted -- the design's stated failure mode. Silently
    keeping it would retain a container on the strength of an entry nobody
    can read; silently skipping the defect would hide the entry entirely.
    """
    findings: list[Finding] = []
    if not isinstance(raw, dict):
        findings.append(Finding(
            "retained-list-invalid", path=source,
            observed=type(raw).__name__,
            expected="a JSON object with a `retained` list",
            message="every container it might have retained reports as unaccounted"))
        return RetainedDoc({}, {}, tuple(findings))

    unknown = sorted(set(raw) - {"retained", "proposed_removals"})
    if unknown:
        findings.append(Finding(
            "retained-list-invalid", path=source,
            observed=unknown, expected="only `retained` and `proposed_removals`",
            message="unknown keys are refused rather than skipped; see "
                    + SCHEMA_PATH))

    retained: dict[str, dict] = {}
    removals: dict[str, dict] = {}
    for key, required, target in (("retained", REQUIRED_RETAINED_KEYS, retained),
                                  ("proposed_removals", REQUIRED_REMOVAL_KEYS, removals)):
        entries = raw.get(key, [])
        if not isinstance(entries, list):
            findings.append(Finding(
                "retained-list-invalid", path=source,
                observed=f"`{key}` is {type(entries).__name__}",
                expected=f"`{key}` is a list"))
            continue
        for index, entry in enumerate(entries):
            defects = _entry_defects(entry, required)
            name = entry.get("name") if isinstance(entry, dict) else None
            label = name if isinstance(name, str) and name.strip() else f"{key}[{index}]"
            if isinstance(name, str) and name.strip() and name in target:
                defects.append("duplicate name")
            if defects:
                findings.append(Finding(
                    "retained-entry-invalid", path=f"{source}:{label}",
                    observed="; ".join(defects),
                    expected="an entry matching " + SCHEMA_PATH,
                    message="the entry is ignored, so the container it names "
                            "reappears as unaccounted"))
                continue
            target[entry["name"]] = entry

    for name in sorted(set(retained) & set(removals)):
        findings.append(Finding(
            "disposition-conflict", path=f"{source}:{name}",
            observed="retained and proposed for removal",
            expected="exactly one disposition per container",
            message="neither disposition is honoured until the conflict is resolved"))
        retained.pop(name)
        removals.pop(name)

    return RetainedDoc(retained, removals, tuple(findings))


def load_retained(path: Path) -> tuple[RetainedDoc, list[str]]:
    """The retained list and its defects. A missing file retains nothing."""
    if not path.is_file():
        return RetainedDoc({}, {}, ()), [f"{path} is absent; nothing is retained"]
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        finding = Finding(
            "retained-list-unparseable", path=str(path),
            observed=f"{type(exc).__name__}: {exc}",
            expected="valid JSON matching " + SCHEMA_PATH,
            message="every entry in it is ignored, so its containers reappear "
                    "as unaccounted")
        return RetainedDoc({}, {}, (finding,)), []
    return read_retained_doc(raw, source=str(path)), []


@dataclass(frozen=True)
class Assessment:
    """One observed container, dispositioned."""

    name: str
    image: str
    disposition: str
    owner: str = ""
    reason: str = ""


def _retained_checks(container: dict, entry: dict) -> list[Finding]:
    """A valid retained entry, held against what the daemon actually shows."""
    name = str(container.get("name") or "")
    findings: list[Finding] = []

    observed_image = str(container.get("image") or "")
    if observed_image and observed_image != str(entry.get("image")):
        findings.append(Finding(
            "retained-image-mismatch", path=name,
            observed=observed_image, expected=str(entry.get("image")),
            message="the retention was reviewed for a different image; re-review "
                    "the entry"))

    recorded = {(str(p.get("host_ip")), str(p.get("host_port")), str(p.get("container_port")))
                for p in entry.get("published_ports") or []}
    for port in container.get("published_ports") or []:
        key = (str(port.get("host_ip")), str(port.get("host_port")),
               str(port.get("container_port")))
        if key not in recorded:
            findings.append(Finding(
                "retained-port-unrecorded", path=name,
                observed=f"{key[0]}:{key[1]} -> {key[2]}",
                expected=f"the port and bind address recorded in {RETAINED_PATH}",
                message="a retained container's published ports are what make "
                        "'what is listening on this box' answerable (7.5)"))
    return findings


def classify(evidence: dict, doc: RetainedDoc) -> tuple[list[Finding], list[Assessment], list[str]]:
    """Every observed container, dispositioned from evidence. Pure."""
    findings = list(doc.findings)
    assessments: list[Assessment] = []
    notes: list[str] = []
    tracked = {normalize_path(p) for p in evidence.get("compose_files") or []}
    observed: set[str] = set()

    for container in evidence.get("containers") or []:
        name = str(container.get("name") or "")
        image = str(container.get("image") or "")
        observed.add(name)

        for key, error in sorted((container.get("parse_errors") or {}).items()):
            findings.append(Finding(
                "capture-unparsed", path=f"{name}:{key}",
                observed=error, expected="parseable capture",
                message="raw output preserved in the evidence file"))

        if not container.get("present", True):
            # Gone between `docker ps` and `docker inspect` -- the per-call MCP
            # servers do exactly this. Nothing is on the host to account for.
            assessments.append(Assessment(name, image, ABSENT))
            notes.append(f"{name} vanished between docker ps and docker inspect; "
                         "nothing remains to account for")
            continue

        config_files = label_config_files(container.get("compose_config_files"))
        owned = [p for p in config_files if normalize_path(p) in tracked]
        if owned:
            assessments.append(Assessment(name, image, COMPOSE_OWNED, owner=owned[0]))
            continue

        if name in doc.retained:
            entry = doc.retained[name]
            findings.extend(_retained_checks(container, entry))
            assessments.append(Assessment(name, image, RETAINED,
                                          owner=str(entry.get("owner") or "")))
            continue

        if name in doc.removals:
            entry = doc.removals[name]
            findings.append(Finding(
                "removal-pending", path=name, observed=image,
                expected="removed after explicit operator confirmation (task 13.4)",
                message=str(entry.get("reason") or "")))
            assessments.append(Assessment(name, image, REMOVE_PROPOSED,
                                          reason=str(entry.get("reason") or "")))
            continue

        findings.append(Finding(
            "unaccounted-container", path=name, observed=image,
            expected=f"a reviewed disposition in {RETAINED_PATH}",
            message="started by no compose file tracked in this repository, "
                    "and not retained"))
        assessments.append(Assessment(name, image, UNACCOUNTED))

    for name in sorted(set(doc.retained) - observed):
        notes.append(f"retained entry `{name}` matches no observed container")
    for name in sorted(set(doc.removals) - observed):
        notes.append(f"proposed removal `{name}` matches no observed container "
                     "(already removed?)")

    return findings, assessments, notes


# --------------------------------------------------------------------------
# The confirmation gate (Requirement 7.3, Property 15)
# --------------------------------------------------------------------------

def removal_gate(named: Iterable[str], candidates: Iterable[str],
                 *, confirmed: bool) -> tuple[bool, str]:
    """Whether this run may remove anything, and why not.

    Confirmation is per-run and per-set: `--yes` alone is insufficient, and
    the named set must equal -- as a set -- the observed containers carrying a
    recorded `remove` disposition. Naming extra containers (retained,
    undispositioned, or absent) refuses the whole run; naming fewer than the
    recorded candidates refuses too, so a candidate cannot be quietly skipped
    and later mistaken for reviewed-and-kept.
    """
    named_set, candidate_set = set(named), set(candidates)
    if not confirmed:
        return False, ("removal refused: --yes is absent, so no confirmation "
                       "was given for this set")
    if not named_set:
        return False, "removal refused: no containers were named"
    if named_set != candidate_set:
        detail = []
        extra = sorted(named_set - candidate_set)
        missing = sorted(candidate_set - named_set)
        if extra:
            detail.append("named without a recorded, observed `remove` "
                          "disposition: " + ", ".join(extra))
        if missing:
            detail.append("recorded candidates left unnamed: " + ", ".join(missing))
        return False, ("removal refused: the named set must equal the observed "
                       "remove-dispositioned set -- " + "; ".join(detail))
    return True, ""


def remove(candidates: Sequence[str], *, confirmed: bool, execute: Executor) -> list:
    """The design's gate, verbatim: no confirmation, no command, empty list.

    `execute` is injected, which is how the tests prove `docker rm` is never
    issued without confirmation -- the recording executor sees every call, and
    the assertion needs no daemon and removes nothing.
    """
    if not confirmed:
        return []
    return [execute("docker", "rm", "-f", c) for c in candidates]


# --------------------------------------------------------------------------
# The generated Cleanup_Record
# --------------------------------------------------------------------------

def _port_cell(ports: list) -> str:
    if not ports:
        return "none"
    return "; ".join(f"{p['host_ip']}:{p['host_port']} -> {p['container_port']}"
                     for p in ports)


def render_record(doc: RetainedDoc, assessments: Sequence[Assessment],
                  *, captured_at: str = "") -> str:
    """`docs/records/docker-host-cleanup.md`, generated. One source, one
    derived document."""
    by_disposition: dict[str, list[Assessment]] = {}
    for a in assessments:
        by_disposition.setdefault(a.disposition, []).append(a)

    lines = [
        "# Docker host cleanup record",
        "",
        "Generated by `python -m scripts.verify.orphan_review --emit-record "
        + RECORD_PATH + "`",
        f"from `{RETAINED_PATH}` (the single source of truth for dispositions)"
        + (f" and the capture of {captured_at}." if captured_at else "."),
        "Do not edit by hand: edit the JSON and regenerate, or this record and",
        "the machine-read list become two sources that disagree.",
        "",
        "## Retained containers",
    ]
    if not doc.retained:
        lines += ["", "None recorded."]
    for name, entry in sorted(doc.retained.items()):
        lines += [
            "",
            f"### {name}",
            "",
            f"- image: `{entry['image']}`",
            f"- owner: {entry['owner']}",
            f"- published ports: {_port_cell(entry['published_ports'])}",
            f"- reviewed: {entry['reviewed']}",
            f"- justification: {entry['justification']}",
        ]

    lines += ["", "## Proposed removals (operator confirmation required -- task 13.4)", ""]
    if not doc.removals:
        lines += ["None recorded."]
    else:
        lines += [
            "`docker rm` is irreversible; nothing below is executed by the review. "
            "The gate is `python -m scripts.verify.orphan_review "
            "--execute-removals <names> --yes`, and the named set must equal "
            "this list.",
        ]
        for name, entry in sorted(doc.removals.items()):
            lines += [
                "",
                f"### {name}",
                "",
                f"- image: `{entry['image']}`",
                f"- reviewed: {entry['reviewed']}",
                f"- reason: {entry['reason']}",
            ]

    unaccounted = sorted(by_disposition.get(UNACCOUNTED) or [], key=lambda a: a.name)
    lines += ["", "## Observed and unaccounted", ""]
    if unaccounted:
        lines += [f"Each needs a reviewed disposition in `{RETAINED_PATH}`:", ""]
        lines += [f"- `{a.name}` -- image `{a.image}`" for a in unaccounted]
    else:
        lines += ["None at capture time."]

    owned = sorted(by_disposition.get(COMPOSE_OWNED) or [], key=lambda a: a.name)
    lines += [
        "",
        "## Compose-owned (accounted by label)",
        "",
        f"{len(owned)} container(s) whose `{CONFIG_FILES_LABEL}` label resolves "
        "to a compose file tracked in this repository:",
        "",
    ]
    lines += [f"- `{a.name}`" for a in owned]
    return "\n".join(lines) + "\n"


def write_record(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_report(args) -> Report:
    root = resolve_root(args.root)
    # Injectable so the whole CLI path is testable with the recording fake
    # executor; the real invocation never sets it.
    execute = getattr(args, "execute", None) or default_execute
    report = Report()

    removals_named = list(getattr(args, "execute_removals", None) or [])
    if getattr(args, "yes", False) and not removals_named:
        raise Usage("--yes without --execute-removals confirms nothing; name the "
                    "containers to remove")
    if removals_named and getattr(args, "from_evidence", None):
        raise Usage("removals require a live daemon; --from-evidence classifies "
                    "a recorded capture that may be older than the host")

    retained_file = Path(getattr(args, "retained", None) or root / RETAINED_PATH)
    doc, load_notes = load_retained(retained_file)
    report.notes.extend(load_notes)

    source = getattr(args, "from_evidence", None)
    if source:
        try:
            evidence = json.loads(Path(source).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise Usage(f"--from-evidence {source} does not parse: {exc}") from exc
        if not isinstance(evidence, dict) or "containers" not in evidence:
            raise Usage(f"--from-evidence {source} is not an orphan-review "
                        "evidence file")
        report.notes.append(f"classified {source} without contacting Docker")
    else:
        evidence = collect(root, execute)
        evidence_path = Path(getattr(args, "evidence", None) or root / EVIDENCE_PATH)
        write_evidence(evidence, evidence_path)
        report.notes.append(f"evidence written to {evidence_path}")

    findings, assessments, notes = classify(evidence, doc)
    report.notes.extend(notes)

    if removals_named:
        candidates = sorted(a.name for a in assessments
                            if a.disposition == REMOVE_PROPOSED)
        ok, reason = removal_gate(removals_named, candidates,
                                  confirmed=bool(getattr(args, "yes", False)))
        if not ok:
            raise Usage(reason)  # Exit.USAGE; no command was issued
        removed: set[str] = set()
        for name, proc in zip(candidates, remove(candidates, confirmed=True,
                                                 execute=execute), strict=True):
            if getattr(proc, "returncode", 1) == 0:
                removed.add(name)
                report.notes.append(f"removed {name} (operator-confirmed)")
            else:
                stderr = (getattr(proc, "stderr", "") or "").strip()
                findings.append(Finding(
                    "removal-failed", path=name,
                    observed=f"docker rm -f exited {proc.returncode}",
                    expected="removal of the confirmed candidate",
                    message=stderr.splitlines()[0] if stderr else ""))
        findings = [f for f in findings
                    if not (f.rule == "removal-pending" and f.path in removed)]

    for finding in findings:
        report.add(finding)

    counts = {d: sum(1 for a in assessments if a.disposition == d)
              for d in (COMPOSE_OWNED, RETAINED, REMOVE_PROPOSED, UNACCOUNTED, ABSENT)}
    report.notes.append(f"{len(assessments)} container(s) observed: "
                        + ", ".join(f"{k}={v}" for k, v in counts.items()))

    record = getattr(args, "emit_record", None)
    if record is not None and Path(record).suffix.lower() in (".md", ".markdown"):
        # The Cleanup_Record is a markdown document, so this check writes it
        # itself and clears the flag the shared runner uses -- otherwise
        # `common.run` would overwrite the markdown with the JSON report.
        write_record(render_record(doc, assessments,
                                   captured_at=str(evidence.get("captured_at") or "")),
                     Path(record))
        args.emit_record = None
        report.notes.append(f"cleanup record written to {record}")

    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = base_parser(
        "Review every container on the Docker host for accountability: owned by "
        "a tracked compose file (by label, not by name), retained by review, or "
        "a finding. The removal path is gated on --yes plus naming exactly the "
        "remove-dispositioned set; refusal is exit 3 with nothing issued."
    )
    parser.add_argument("--retained", type=Path, default=None,
                        help=f"retained-containers file (default: <root>/{RETAINED_PATH})")
    parser.add_argument("--evidence", type=Path, default=None,
                        help=f"evidence output path (default: <root>/{EVIDENCE_PATH})")
    parser.add_argument("--from-evidence", type=Path, default=None,
                        help="classify a previously captured evidence file instead "
                             "of contacting Docker")
    parser.add_argument("--execute-removals", nargs="+", metavar="NAME", default=None,
                        help="remove exactly these containers; refused unless each "
                             "carries a recorded `remove` disposition and --yes is "
                             "present")
    parser.add_argument("--yes", action="store_true",
                        help="per-run confirmation; insufficient without "
                             "--execute-removals naming the set")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
