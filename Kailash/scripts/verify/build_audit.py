"""Assert every build definition can actually be built, without building it.

The defect class is a `COPY` whose source is not in the build context. Nine
`backend/services/<service>/Dockerfile` files copy from `platform/` and
`services/<service>/`, neither of which has existed since the consolidation;
no compose service references them, so nothing fails until someone builds one
by hand and loses an afternoon. Meanwhile the file that *is* built,
`backend/services/Dockerfile.service`, copies
`backend/services/${SERVICE}/requirements.txt` -- a path that only exists for
the nine known `SERVICE` values. A real `docker build` proves one value in
minutes; this audit proves all nine in milliseconds, which is why it is a
static check with no daemon and runs on every push.

Three rules:

  unresolved-copy-source  a `COPY`/`ADD` source in a compose-referenced build
                          file does not resolve inside that service's declared
                          context after ARG substitution. One finding per
                          referencing service, so a templated path failing for
                          one `SERVICE` value names that value.
  dead-build-file         a tracked build file that no compose service
                          references and whose sources resolve from neither
                          the repo root nor the file's own directory. A
                          reintroduced dead Dockerfile fails CI here.
  compose-unparseable     docker-compose.yml does not parse, so referenced-ness
                          is undecidable. That is a defect in the build
                          definitions, not an environment problem.

An unreferenced build file whose sources all resolve is a note, not a finding:
the design (5.3) makes the finding conditional on *both* unreferenced and
unresolvable, and a buildable-but-unwired file is a review question rather
than a broken definition.

Sources behind `--from=` are skipped -- they resolve in an earlier stage or
image, not the context. Glob sources resolve when at least one match exists.
"""
from __future__ import annotations

import glob as globmod
import json
import posixpath
import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import yaml

from .common import (
    Corpus,
    Finding,
    Report,
    base_parser,
    load_corpus,
    resolve_root,
    run,
)

COMPOSE_FILE = "docker-compose.yml"

# Sources a filesystem check cannot see: remote ADD sources and heredocs.
REMOTE_PREFIXES = ("http://", "https://", "ssh://", "git://", "ftp://", "git@")

# `${NAME}`, `${NAME:-default}`, `${NAME:+alternate}` and bare `$NAME`.
VAR_RX = re.compile(r"\$\{(\w+)(?::([-+])([^}]*))?\}|\$(\w+)")


# --------------------------------------------------------------------------
# Dockerfile parsing
# --------------------------------------------------------------------------

def instructions(text: str) -> list[tuple[int, str]]:
    """(first physical line, logical line) for every instruction.

    `\\r` is stripped per line: this repository is checked out CRLF on the
    Windows developer host and LF in CI, and a trailing `\\r` would defeat the
    continuation test below. Comment lines are legal *inside* a continuation
    and are skipped without ending it, as docker does.
    """
    out: list[tuple[int, str]] = []
    pending: str | None = None
    start = 0
    for lineno, raw in enumerate(text.split("\n"), 1):
        stripped = raw.rstrip("\r").strip()
        if not stripped or stripped.startswith("#"):
            continue
        if pending is None:
            start = lineno
            if stripped.endswith("\\"):
                pending = stripped[:-1] + " "
            else:
                out.append((lineno, stripped))
        elif stripped.endswith("\\"):
            pending += stripped[:-1] + " "
        else:
            out.append((start, pending + stripped))
            pending = None
    if pending is not None:
        out.append((start, pending.rstrip()))
    return out


def arg_defaults(text: str) -> dict[str, str]:
    """Every `ARG NAME=default` in the file. A default-less ARG stays absent:
    at build time it is empty unless supplied, and a path built from an empty
    fragment is not a path anyone intended."""
    defaults: dict[str, str] = {}
    for _, logical in instructions(text):
        m = re.match(r"(\w+)\s+(.*)", logical)
        if not m or m.group(1).upper() != "ARG":
            continue
        for token in _split_operands(m.group(2)):
            name, eq, value = token.partition("=")
            if eq:
                defaults[name] = value.strip().strip("\"'")
    return defaults


@dataclass(frozen=True)
class CopyDirective:
    line: int
    instruction: str            # COPY or ADD
    sources: tuple[str, ...]
    from_stage: str | None


def _split_operands(rest: str) -> list[str]:
    """JSON-array form or shell form; the last operand is the destination."""
    rest = rest.strip()
    if rest.startswith("["):
        try:
            parsed = json.loads(rest)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [str(p) for p in parsed]
    try:
        return shlex.split(rest, posix=True)
    except ValueError:
        return rest.split()


def copy_directives(text: str) -> list[CopyDirective]:
    out: list[CopyDirective] = []
    for lineno, logical in instructions(text):
        m = re.match(r"(\w+)\s+(.*)", logical)
        if not m or m.group(1).upper() not in ("COPY", "ADD"):
            continue
        rest = m.group(2).strip()
        from_stage = None
        while rest.startswith("--"):
            flag, _, rest = rest.partition(" ")
            rest = rest.strip()
            if flag.startswith("--from="):
                from_stage = flag[len("--from="):]
        operands = _split_operands(rest)
        if len(operands) < 2:
            continue  # malformed; docker itself rejects it, nothing to resolve
        out.append(CopyDirective(
            line=lineno, instruction=m.group(1).upper(),
            sources=tuple(operands[:-1]), from_stage=from_stage))
    return out


def substitute(value: str, args: dict[str, str]) -> tuple[str, frozenset[str]]:
    """ARG substitution, returning the names that had no value to substitute."""
    unset: set[str] = set()

    def repl(m: re.Match) -> str:
        name = m.group(1) or m.group(4)
        op, alt = m.group(2), m.group(3) or ""
        if name in args:
            current = args[name]
            if op == "+":
                return alt if current else ""
            if op == "-" and not current:
                return alt
            return current
        if op == "-":
            return alt
        if op == "+":
            return ""
        unset.add(name)
        return ""

    return VAR_RX.sub(repl, value), frozenset(unset)


# --------------------------------------------------------------------------
# Resolution
# --------------------------------------------------------------------------

def source_resolves(context: Path, source: str) -> bool:
    """Does `source` name something inside `context` on disk?

    A leading `/` is context-relative, as docker treats it. A glob resolves
    when at least one match exists -- an empty glob COPY fails the real build
    exactly like a missing literal path does.
    """
    src = source.strip().lstrip("/")
    if not src:
        return False
    norm = posixpath.normpath(src)
    if norm.startswith(".."):
        return False  # docker forbids escaping the context outright
    if any(ch in norm for ch in "*?["):
        return bool(globmod.glob(str(context / norm), recursive=True))
    return (context / norm).exists()


@dataclass(frozen=True)
class MissingSource:
    line: int
    instruction: str
    raw: str                 # as written in the build file
    resolved: str            # after ARG substitution
    unset: frozenset[str]    # ARG names with no value

    @property
    def reason(self) -> str:
        if self.unset:
            return "build arg(s) with no value: " + ",".join(sorted(self.unset))
        if posixpath.normpath(self.resolved.lstrip("/") or ".").startswith(".."):
            return "escapes the build context"
        return "not found in the build context"


def missing_sources(text: str, context: Path,
                    args: dict[str, str]) -> list[MissingSource]:
    """Every COPY/ADD source that does not resolve inside `context`.

    `args` are the compose-declared build args; they override the file's own
    ARG defaults, exactly as `docker build --build-arg` does.
    """
    effective = {**arg_defaults(text), **args}
    out: list[MissingSource] = []
    for directive in copy_directives(text):
        if directive.from_stage is not None:
            continue  # resolves in an earlier stage or image, not the context
        for raw in directive.sources:
            if raw.startswith(REMOTE_PREFIXES) or raw.startswith("<<"):
                continue
            resolved, unset = substitute(raw, effective)
            if not unset and source_resolves(context, resolved):
                continue
            out.append(MissingSource(
                line=directive.line, instruction=directive.instruction,
                raw=raw, resolved=resolved, unset=unset))
    return out


# --------------------------------------------------------------------------
# Compose references
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class ComposeRef:
    """One compose service that builds a given file."""

    service: str
    context: str                               # repo-relative, "." for the root
    args: dict[str, str] = field(default_factory=dict)
    passthrough: frozenset[str] = frozenset()  # declared, value from build env


def _norm(rel: str) -> str:
    return posixpath.normpath(rel.replace("\\", "/"))


def _build_args(spec: object) -> tuple[dict[str, str], frozenset[str]]:
    """Both compose spellings: a mapping, or a list of `KEY=value` / `KEY`.

    A bare `KEY` takes its value from the build environment, which a static
    check cannot know; those names are returned separately so a source that
    needs one is skipped with a note rather than reported as broken.
    """
    args: dict[str, str] = {}
    passthrough: set[str] = set()
    if isinstance(spec, dict):
        for key, value in spec.items():
            if value is None:
                passthrough.add(str(key))
            else:
                args[str(key)] = str(value)
    elif isinstance(spec, list):
        for item in spec:
            name, eq, value = str(item).partition("=")
            if eq:
                args[name] = value
            else:
                passthrough.add(name)
    return args, frozenset(passthrough)


def parse_compose(text: str, report: Report) -> dict[str, list[ComposeRef]]:
    """Build-file repo path -> the compose services that build it.

    Parsed with yaml.safe_load, as workflow_gate.py already does for the
    workflow files: the real compose uses anchors and `<<:` merge keys, which
    a line regex cannot follow honestly.
    """
    try:
        doc = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        report.add(Finding(
            rule="compose-unparseable", path=COMPOSE_FILE,
            observed=f"{type(exc).__name__}",
            expected="parseable YAML",
            message="referenced-ness of every build file is undecidable",
        ))
        return {}

    refs: dict[str, list[ComposeRef]] = {}
    services = doc.get("services") if isinstance(doc, dict) else None
    if not isinstance(services, dict):
        return refs

    for name, spec in services.items():
        if not isinstance(spec, dict):
            continue
        build = spec.get("build")
        if isinstance(build, str):
            context, dockerfile, args, passthrough = build, "Dockerfile", {}, frozenset()
        elif isinstance(build, dict):
            context = str(build.get("context", "."))
            dockerfile = str(build.get("dockerfile", "Dockerfile"))
            args, passthrough = _build_args(build.get("args"))
        else:
            continue
        context = _norm(context)
        target = _norm(posixpath.join(context, dockerfile.replace("\\", "/")))
        if target.startswith(".."):
            continue  # points outside the repository; not ours to audit
        refs.setdefault(target, []).append(ComposeRef(
            service=str(name), context=context,
            args=args, passthrough=passthrough))
    return refs


# --------------------------------------------------------------------------
# The check
# --------------------------------------------------------------------------

def in_scope(rel: str) -> bool:
    """Tracked `Dockerfile*` at the repository root or under `backend/`."""
    name = PurePosixPath(rel).name
    if not name.startswith("Dockerfile"):
        return False
    return "/" not in rel or rel.startswith("backend/")


def enumerate_build_files(files: list[str]) -> list[str]:
    return [rel for rel in files if in_scope(rel)]


def _fmt_args(ref: ComposeRef) -> str:
    if not ref.args:
        return ""
    return " (" + ", ".join(f"{k}={v}" for k, v in sorted(ref.args.items())) + ")"


def _audit_referenced(rel: str, text: str, refs: list[ComposeRef],
                      root: Path, report: Report) -> None:
    for ref in refs:
        context_dir = root / Path(ref.context)
        for miss in missing_sources(text, context_dir, ref.args):
            if miss.unset and miss.unset <= ref.passthrough:
                report.notes.append(
                    f"{rel}:{miss.line} source {miss.raw!r} depends on build-time "
                    f"env arg(s) {','.join(sorted(miss.unset))}; not statically checkable")
                continue
            report.add(Finding(
                rule="unresolved-copy-source", path=rel, line=miss.line,
                observed=miss.resolved or miss.raw,
                expected=f"a path inside build context '{ref.context}'",
                message=f"compose service '{ref.service}'{_fmt_args(ref)}: {miss.reason}",
            ))


def _audit_unreferenced(rel: str, text: str, root: Path, report: Report) -> None:
    """Dead iff its sources resolve from neither plausible context.

    The repo root is what every current build file documents as its context;
    the file's own directory is the other context a `docker build .` from that
    directory would use. Failing under both is not a wiring gap, it is a build
    definition that cannot build -- the nine dead per-service Dockerfiles.
    """
    parent = str(PurePosixPath(rel).parent)
    candidates = ["."] if parent == "." else [".", parent]
    attempts = {c: missing_sources(text, root / Path(c), {}) for c in candidates}
    best = min(attempts, key=lambda c: len(attempts[c]))
    if not attempts[best]:
        report.notes.append(
            f"unreferenced build file {rel}: sources resolve from context "
            f"'{best}' but no compose service builds it")
        return
    for miss in attempts[best]:
        report.add(Finding(
            rule="dead-build-file", path=rel, line=miss.line,
            observed=miss.resolved or miss.raw,
            expected="a compose reference or resolving sources",
            message="no compose service references this build file and this "
                    f"source resolves from neither the repo root nor "
                    f"{parent + '/' if parent != '.' else 'its directory'}: "
                    f"{miss.reason}",
        ))


def audit(corpus: Corpus, report: Report) -> None:
    compose_text = corpus.read(COMPOSE_FILE)
    if compose_text is None:
        refmap: dict[str, list[ComposeRef]] = {}
        report.notes.append(
            f"{COMPOSE_FILE} not found; every build file is treated as unreferenced")
    else:
        refmap = parse_compose(compose_text, report)

    for rel in enumerate_build_files(corpus.files):
        text = corpus.read(rel)
        if text is None:
            report.notes.append(f"build file {rel} is unreadable as UTF-8; skipped")
            continue
        refs = refmap.get(rel, [])
        if refs:
            _audit_referenced(rel, text, refs, corpus.root, report)
        else:
            _audit_unreferenced(rel, text, corpus.root, report)


def build_report(args) -> Report:
    root = resolve_root(args.root)
    corpus = load_corpus(root)
    report = Report()
    audit(corpus, report)
    return report


def main(argv=None) -> int:
    parser = base_parser(
        "Statically verify every COPY/ADD source resolves in its build context.")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
