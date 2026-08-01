"""Assert the repository is in a state it is safe to deploy from.

Two properties:

1. No uncommitted modification under a Deployment_Critical_Path. `deploy.sh`
   runs `git reset --hard` and `git clean -fd` on the target host, so anything
   uncommitted there is deleted with nothing to recover from.
2. `deploy/vultr/deploy.sh` names this repository. It resolves that URL and
   hard-resets against it; a wrong slug means resetting production to someone
   else's code. That exact defect was live until recently -- the script said
   `flywithvvk/kailash` while origin was `urgaa-eka/kailash`.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .common import (
    Finding,
    Report,
    Unavailable,
    base_parser,
    resolve_root,
    run,
)

CRITICAL_PATHS = (
    "deploy/",
    ".github/workflows/",
    "frontend/.firebaserc",
    "frontend/.env.production",
    "docker-compose.yml",
)

EXPECTED_SLUG = "urgaa-eka/kailash"

# Every URL form git accepts for the same repository.
_SLUG_RX = re.compile(
    r"""^(?:
          git@[\w.-]+:                    # git@github.com:owner/name
        | ssh://git@[\w.-]+(?::\d+)?/     # ssh://git@github.com/owner/name
        | https?://(?:[^@/]+@)?[\w.-]+/   # https://[user@]github.com/owner/name
        | [\w.-]+@[\w.-]+:                # scp-like
        )?
        (?P<owner>[\w.-]+)/(?P<name>[\w.-]+?)(?:\.git)?/?$""",
    re.X,
)


def normalise_remote(url: str) -> str | None:
    """Reduce any remote URL form to `owner/name`.

    Property-tested because the failure mode is asymmetric: a normaliser that
    silently returns the URL unchanged makes the deploy guard reject every
    valid checkout, turning a safety feature into an outage.
    """
    if not url or not url.strip():
        return None
    m = _SLUG_RX.match(url.strip())
    if not m:
        return None
    return f"{m.group('owner')}/{m.group('name')}"


def _under_critical_path(path: str) -> str | None:
    """Segment-aware prefix match.

    `deploy/` must not match `deployment-notes.md`, which a plain startswith
    would.
    """
    # Strip one leading "./" only. `lstrip("./")` would eat the dot from
    # ".github/workflows/", silently exempting every workflow file.
    p = path.replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    for crit in CRITICAL_PATHS:
        if crit.endswith("/"):
            if p == crit.rstrip("/") or p.startswith(crit):
                return crit
        elif p == crit:
            return crit
    return None


def _unquote(path: str) -> str:
    """git quotes paths containing spaces or specials with C-style escaping."""
    path = path.strip()
    if path.startswith('"') and path.endswith('"'):
        body = path[1:-1]
        return body.encode().decode("unicode_escape")
    return path


def parse_porcelain(output: str) -> list[tuple[str, str]]:
    """(status, path) for every entry, with both sides of a rename returned."""
    entries: list[tuple[str, str]] = []
    for raw in output.splitlines():
        if not raw.strip():
            continue
        status, _, rest = raw[:2], raw[2:3], raw[3:]
        if " -> " in rest:  # rename or copy: R  old -> new
            old, new = rest.split(" -> ", 1)
            entries.append((status, _unquote(old)))
            entries.append((status, _unquote(new)))
        else:
            entries.append((status, _unquote(rest)))
    return entries


def _git(root: Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=root,
                             capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise Unavailable("git is not installed") from exc
    if out.returncode != 0:
        raise Unavailable(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def check_critical_paths_clean(root: Path, report: Report) -> None:
    output = _git(root, "status", "--porcelain")
    for status, path in parse_porcelain(output):
        crit = _under_critical_path(path)
        if crit:
            report.add(Finding(
                rule="critical-path-dirty", path=path,
                observed=f"status={status.strip() or '??'}",
                expected="committed",
                message=f"under {crit}; deploy.sh runs git clean -fd on the target",
            ))


def check_deploy_script_slug(root: Path, report: Report) -> None:
    rel = "deploy/vultr/deploy.sh"
    script = root / rel
    if not script.is_file():
        report.add(Finding(rule="deploy-slug", path=rel, observed="<absent>",
                           expected=EXPECTED_SLUG,
                           message="the deploy script is a required source"))
        return

    text = script.read_text(encoding="utf-8", errors="replace")
    found: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r"""["']?(?P<url>(?:https?://|git@|ssh://)[^"'\s]+)["']?""", line):
            url = m.group("url")
            # Only repository URLs. This script also names API endpoints such
            # as https://api.kailash-ai.in/api/docs, which normalise to a
            # perfectly well-formed "api/docs" and are not remotes.
            if "github.com" not in url and not url.endswith(".git"):
                continue
            slug = normalise_remote(url)
            if slug:
                found.append((lineno, slug))

    if not found:
        report.add(Finding(rule="deploy-slug", path=rel, observed="<no match>",
                           expected=EXPECTED_SLUG,
                           message="required source yielded no repository URL"))
        return

    for lineno, slug in found:
        if slug != EXPECTED_SLUG:
            report.add(Finding(rule="deploy-slug", path=rel, line=lineno,
                               observed=slug, expected=EXPECTED_SLUG))


def build_report(args) -> Report:
    root = resolve_root(args.root)
    report = Report()
    check_critical_paths_clean(root, report)
    check_deploy_script_slug(root, report)
    return report


def main(argv=None) -> int:
    parser = base_parser("Assert the repository is safe to deploy from.")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
