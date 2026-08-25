"""Find credentials committed to the repository.

Operates over the `git ls-files` corpus. Untracked files are out of scope by
definition -- the requirement is "every file tracked by git", and a scanner
that also walked the working tree would report on virtualenvs and build output
until nobody read its output.

Four detectors, deliberately overlapping:

1. Denylist  -- exact literals known to have leaked. Applies to every file,
                lockfiles included.
2. Structured -- shapes that are unambiguously credentials (private key
                headers, provider key formats).
3. Assignment -- a credential-shaped key assigned a value that is neither a
                placeholder nor an environment reference.
4. Compose   -- a strict-required compose variable given a `:-` default, so a
                reverted `${VAR:?}` is caught by the same job that enforced it.
"""
from __future__ import annotations

import re
from pathlib import Path

from .common import (
    Corpus,
    Finding,
    Report,
    Suppression,
    base_parser,
    load_corpus,
    resolve_root,
    run,
    suppression_on,
)

DATA_DIR = Path(__file__).parent / "data"

# Variables docker-compose.yml must declare with `:?`, never `:-`.
STRICT_COMPOSE_VARS = ("POSTGRES_PASSWORD", "REDIS_PASSWORD", "PLATFORM_INTERNAL_TOKEN")

STRUCTURED = (
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("google-api-key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("slack-token", re.compile(r"xox[baprs]-")),
    ("gcp-service-account", re.compile(r'"type"\s*:\s*"service_account"')),
)

# The prefix is optional on purpose: a mandatory leading character means the
# bare names -- API_KEY, SECRET, TOKEN -- can never match, which is most of
# what this detector exists to catch.
ASSIGNMENT = re.compile(
    r"""(?P<key>[A-Za-z0-9_]*(?:PASSWORD|SECRET|TOKEN|API_?KEY|PRIVATE_KEY|CREDENTIAL)[A-Za-z0-9_]*)
        \s*[:=]\s*
        (?P<quote>["']?)(?P<value>[^"'\s,;)}]{8,})(?P=quote)""",
    re.X | re.I,
)

# An environment reference is not a secret, it is the absence of one.
ENV_REFERENCE = re.compile(
    r"""^\$\{|^\$[A-Z_]|os\.environ|os\.getenv|process\.env|
        secrets\.|vars\.|getenv\(|System\.getenv""",
    re.X | re.I,
)

# Prefix forms, not exact matches: a real .env.example says
# `change-me-to-a-long-random-string` and `sk-ant-your-anthropic-key-here`,
# neither of which equals its own stem.
PLACEHOLDER = re.compile(
    r"""^(|change[-_]?me.*|replace[-_]?me.*|<[^>]*>|.*\byour[-_].*|xxx.*|\*{3,}|
        .*\bplaceholder\b.*|generated|none|null|todo|example.*|dummy.*|
        .*[-_](here|goes[-_]here)$)$""",
    re.X | re.I,
)

# `${VAR:?msg}` and `${VAR:-default}` put a credential-shaped name and a
# colon next to each other, which the assignment detector would otherwise
# read as `VAR: ?msg`. The expansion is the opposite of a hardcoded secret.
IN_EXPANSION = re.compile(r"\$\{[^}]*$")

LOCKFILE_NAMES = {
    "yarn.lock", "package-lock.json", "pnpm-lock.yaml", "bun.lockb",
    "poetry.lock", "Pipfile.lock", "Cargo.lock", "composer.lock", "go.sum",
}

CONFIG_SUFFIXES = (".yml", ".yaml", ".ini", ".cfg", ".toml", ".properties", ".conf")


def _is_lockfile(rel: str) -> bool:
    return Path(rel).name in LOCKFILE_NAMES


def _is_config_format(rel: str) -> bool:
    """Formats where an unquoted value is a literal rather than an expression."""
    name = Path(rel).name
    return name.startswith(".env") or ".env" in name or rel.endswith(CONFIG_SUFFIXES)


def _load_denylist() -> list[str]:
    path = DATA_DIR / "denylist.txt"
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return []
    return [ln.strip() for ln in raw.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


_suppressed = suppression_on


def _is_placeholder_exempt(rel: str, value: str) -> bool:
    """Both conditions, never either alone.

    A real credential in a `.env.example` is still a finding, and a placeholder
    outside one is still reported -- which is how "no other path is exempt"
    becomes something the tests can demonstrate rather than something the
    prose asserts.
    """
    return rel.endswith(".env.example") and bool(PLACEHOLDER.match(value.strip()))


def scan_file(rel: str, text: str, denylist: list[str], report: Report) -> None:
    lines = text.splitlines()
    lockfile = _is_lockfile(rel)

    for idx, line in enumerate(lines):
        lineno = idx + 1

        # Detector 1 -- denylist. Never exempted, not even in lockfiles.
        for literal in denylist:
            if literal in line:
                reason = _suppressed(lines, idx)
                if reason:
                    report.suppressions.append(
                        Suppression("denylist", rel, lineno, reason))
                else:
                    report.add(Finding(
                        rule="denylist", path=rel, line=lineno,
                        observed=f"{literal[:4]}...({len(literal)} chars)",
                        expected="<absent>",
                        message="known-leaked literal",
                    ))

        if lockfile:
            continue  # integrity hashes trip 2 and 3; the denylist already ran

        # Detector 2 -- structured shapes.
        for name, rx in STRUCTURED:
            if rx.search(line):
                reason = _suppressed(lines, idx)
                if reason:
                    report.suppressions.append(Suppression(name, rel, lineno, reason))
                else:
                    report.add(Finding(
                        rule=name, path=rel, line=lineno,
                        observed="<matched>", expected="<absent>",
                    ))

        # Detector 3 -- credential-shaped assignment.
        for m in ASSIGNMENT.finditer(line):
            value = m.group("value")
            # An unquoted value in source code is an expression, not a secret:
            # `access_token = create_access_token(...)` and
            # `hashed_password=get_password_hash(user.password)` are the shape
            # of every auth module ever written. Config formats have no
            # expressions, so unquoted values there are still literals.
            if not m.group("quote") and not _is_config_format(rel):
                continue
            if IN_EXPANSION.search(line[:m.start("key")]):
                continue
            if ENV_REFERENCE.search(value) or ENV_REFERENCE.search(line[m.start("value"):]):
                continue
            if PLACEHOLDER.match(value.strip()):
                if _is_placeholder_exempt(rel, value):
                    continue
                # Reported, not failed. The security property is the other
                # direction -- a real credential in a .env.example IS a
                # finding, and that is enforced above. A placeholder outside
                # one is almost always documentation showing a reader what to
                # type; failing on those makes the check unusable in any repo
                # that has docs, and an unusable check gets weakened.
                report.notes.append(
                    f"placeholder outside *.env.example: {rel}:{lineno} "
                    f"{m.group('key')}={value}")
                continue
            reason = _suppressed(lines, idx)
            if reason:
                report.suppressions.append(Suppression("assignment", rel, lineno, reason))
            else:
                report.add(Finding(
                    rule="assignment", path=rel, line=lineno,
                    observed=f"{m.group('key')}=<{len(value)} chars>",
                    expected="an environment reference or a placeholder",
                ))


def scan_compose_strictness(corpus: Corpus, report: Report) -> None:
    rel = "docker-compose.yml"
    text = corpus.read(rel)
    if text is None:
        return
    for idx, line in enumerate(text.splitlines(), 1):
        for var in STRICT_COMPOSE_VARS:
            if re.search(rf"\$\{{{var}:-", line):
                report.add(Finding(
                    rule="compose-strictness", path=rel, line=idx,
                    observed=f"${{{var}:-...}}", expected=f"${{{var}:?...}}",
                    message="a default here deploys on whatever literal follows it",
                ))


def build_report(args) -> Report:
    root = resolve_root(args.root)
    corpus = load_corpus(root)
    report = Report()
    denylist = _load_denylist()
    if not denylist:
        report.notes.append("denylist is empty; detector 1 did nothing")

    for rel, text in corpus.texts():
        # The denylist file is a list of the literals. Scanning it for them is
        # a tautology, and suppressing every line would leave the file unable
        # to grow without editing two things.
        if rel == "scripts/verify/data/denylist.txt":
            continue
        scan_file(rel, text, denylist, report)

    scan_compose_strictness(corpus, report)

    if corpus.skipped_binary:
        report.notes.append(f"{corpus.skipped_binary} non-UTF-8 file(s) skipped")
    return report


def main(argv=None) -> int:
    parser = base_parser("Scan every tracked file for committed credentials.")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
