"""Shared contract for every verification check.

One exit-code enum, one Finding shape, one renderer. Checks import from here
rather than defining their own conventions, so a caller can treat them
uniformly and a reader learns the output format once.

Exit codes:
    0  OK           nothing wrong
    1  FAILED       the check ran and found something
    2  UNAVAILABLE  the check could not run (no network, no docker, no git)
    3  USAGE        the check was invoked wrongly

UNAVAILABLE is deliberately distinct from FAILED. A pipeline that went red
because the runner lost egress is a different event from production being
down, and conflating them trains people to ignore the check.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable, Iterable, Sequence
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from pathlib import Path


class Exit(IntEnum):
    OK = 0
    FAILED = 1
    UNAVAILABLE = 2
    USAGE = 3


class Unavailable(Exception):
    """A prerequisite the check needs is absent. Maps to Exit.UNAVAILABLE."""


class Usage(Exception):
    """The check was invoked wrongly. Maps to Exit.USAGE."""


@dataclass(frozen=True)
class Finding:
    """One thing wrong, at one place."""

    rule: str
    path: str = ""
    line: int | None = None
    observed: object = None
    expected: object = None
    message: str = ""

    def render(self) -> str:
        """The single output format. Every printing obligation goes through here."""
        parts = [f"FAIL {self.rule}"]
        if self.path:
            parts.append(f"{self.path}:{self.line}" if self.line is not None else self.path)
        if self.observed is not None:
            parts.append(f"observed={_fmt(self.observed)}")
        if self.expected is not None:
            parts.append(f"expected={_fmt(self.expected)}")
        if self.message:
            parts.append(f"-- {self.message}")
        return " ".join(parts)


def _fmt(value: object) -> str:
    if isinstance(value, list | tuple | set):
        return ",".join(sorted(str(v) for v in value))
    return str(value)


@dataclass(frozen=True)
class Suppression:
    """An in-repository opt-out, counted and printed even on success.

    A suppression list that grows silently is a path to green that nobody
    reviews, so these are surfaced whether or not the check found anything.
    """

    rule: str
    path: str
    line: int
    reason: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    suppressions: list[Suppression] = field(default_factory=list)
    unavailable: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def exit_code(self) -> Exit:
        """Unavailable outranks findings.

        If the check could not run parts of itself, the absence of findings
        from those parts means nothing, so it must not report OK.
        """
        if self.unavailable:
            return Exit.UNAVAILABLE
        return Exit.FAILED if self.findings else Exit.OK

    def render(self) -> str:
        lines = [f.render() for f in self.findings]
        for reason in self.unavailable:
            lines.append(f"UNAVAILABLE {reason}")
        for note in self.notes:
            lines.append(f"note: {note}")
        for s in self.suppressions:
            lines.append(f"suppressed {s.rule} {s.path}:{s.line} -- {s.reason}")
        if self.suppressions:
            lines.append(f"{len(self.suppressions)} suppression(s) in force")
        if not self.findings and not self.unavailable:
            lines.append("OK")
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps(
            {
                "exit_code": int(self.exit_code()),
                "findings": [asdict(f) for f in self.findings],
                "suppressions": [asdict(s) for s in self.suppressions],
                "unavailable": self.unavailable,
                "notes": self.notes,
            },
            indent=2,
            default=str,
        )


# --------------------------------------------------------------------------
# Corpus
# --------------------------------------------------------------------------

def git_top_level(start: Path | None = None) -> Path:
    """The git work-tree root containing `start`, or raise Unavailable."""
    cwd = Path(start) if start else Path.cwd()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd, capture_output=True, text=True, check=False,
        )
    except FileNotFoundError as exc:
        raise Unavailable("git is not installed") from exc
    if out.returncode != 0:
        raise Unavailable(f"{cwd} is not inside a git work tree")
    return Path(out.stdout.strip())


def tracked_files(root: Path) -> list[str]:
    """Repo-relative paths of every file tracked by git, in sorted order.

    `-z` because paths may contain spaces or quotes, which git otherwise
    escapes into a form that does not round-trip.
    """
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root, capture_output=True, check=False,
        )
    except FileNotFoundError as exc:
        raise Unavailable("git is not installed") from exc
    if out.returncode != 0:
        raise Unavailable(f"git ls-files failed in {root}")
    names = out.stdout.decode("utf-8", errors="replace").split("\0")
    return sorted(n for n in names if n)


@dataclass
class Corpus:
    """Tracked text files, with undecodable ones counted rather than crashed on."""

    root: Path
    files: list[str]
    skipped_binary: int = 0
    skipped_names: list[str] = field(default_factory=list)

    def read(self, rel: str) -> str | None:
        """UTF-8 text of a tracked file, or None if it does not decode."""
        p = self.root / rel
        try:
            data = p.read_bytes()
        except (OSError, IsADirectoryError):
            return None
        if b"\0" in data[:8192]:
            return None
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return None

    def texts(self) -> Iterable[tuple[str, str]]:
        """(relpath, text) for every tracked file that decodes as UTF-8."""
        for rel in self.files:
            text = self.read(rel)
            if text is None:
                self.skipped_binary += 1
                self.skipped_names.append(rel)
                continue
            yield rel, text


def load_corpus(root: Path) -> Corpus:
    return Corpus(root=root, files=tracked_files(root))


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

# Any comment syntax: `#`, `//`, `<!-- -->`. Markdown needs the last one.
# Shared, because every check that scans the corpus eventually scans its own
# source and tests -- the negative fixtures are, by construction, the thing
# being looked for.
# `verify: allow` is the general form; `secret-scan: allow` is the original
# spelling and stays accepted, since 40-odd markers already use it.
SUPPRESSION = re.compile(
    r"(?:secret-scan|verify):\s*allow(?:\s+(?P<reason>[^\n>*]*))?")


def suppression_on(lines: list[str], idx: int) -> str | None:
    """A `secret-scan: allow <reason>` on this line or the one above it."""
    for probe in (idx, idx - 1):
        if 0 <= probe < len(lines):
            m = SUPPRESSION.search(lines[probe])
            if m:
                return (m.group("reason") or "").strip() or "no reason given"
    return None


def base_parser(description: str) -> argparse.ArgumentParser:
    """The argument surface every check shares."""
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--root", type=Path, default=None,
                   help="repository root (default: git top level)")
    p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    p.add_argument("--emit-record", type=Path, default=None,
                   help="also write the JSON record to this path")
    return p


def resolve_root(value: Path | None) -> Path:
    if value is None:
        return git_top_level()
    root = Path(value).resolve()
    if not root.is_dir():
        raise Usage(f"--root {value} is not a directory")
    return root


def run(check: Callable[[argparse.Namespace], Report],
        argv: Sequence[str] | None,
        parser: argparse.ArgumentParser) -> int:
    """Invoke `check`, guaranteeing it never escapes as a traceback.

    An unhandled traceback exits 1 by default, which is indistinguishable from
    a check that ran and found something. That ambiguity is exactly what makes
    a broken check look like a working gate, so every path is mapped here.
    """
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse already printed the reason
        return int(Exit.USAGE) if exc.code not in (0, None) else int(Exit.OK)

    try:
        report = check(args)
    except Usage as exc:
        print(f"USAGE {exc}", file=sys.stderr)
        return int(Exit.USAGE)
    except Unavailable as exc:
        print(f"UNAVAILABLE {exc}", file=sys.stderr)
        return int(Exit.UNAVAILABLE)
    except Exception as exc:  # noqa: BLE001 - the whole point is to catch everything
        print(f"UNAVAILABLE unexpected error in check: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return int(Exit.UNAVAILABLE)

    text = report.to_json() if getattr(args, "json", False) else report.render()
    print(text)
    if getattr(args, "emit_record", None):
        args.emit_record.parent.mkdir(parents=True, exist_ok=True)
        args.emit_record.write_text(report.to_json(), encoding="utf-8")
    return int(report.exit_code())
