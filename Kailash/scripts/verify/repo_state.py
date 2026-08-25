"""Assert the repository is in a state it is safe to deploy from.

Two properties:

1. No uncommitted modification under a Deployment_Critical_Path. `deploy.sh`
   runs `git reset --hard` and `git clean -fd` on the target host, so anything
   uncommitted there is deleted with nothing to recover from.
2. `deploy/host/deploy.sh` names this repository. It resolves that URL and
   hard-resets against it; a wrong slug means resetting production to someone
   else's code. That exact defect was live until recently -- the script said
   `flywithvvk/kailash` while origin was `urgaa-eka/kailash`.  # secret-scan: allow documents the slug defect this rule detects
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

# Every URL form git accepts for the same repository. Deliberately as
# permissive as the `case` statement in normalise_remote() in
# deploy/host/deploy.sh, which the parity test in tests/verify/test_repo_state.py
# holds this to: any scheme, optional userinfo, optional port, and the two
# scp-like forms with and without a user.
_SLUG_RX = re.compile(
    r"""^(?:
          [A-Za-z][A-Za-z0-9+.\-]*://     # scheme://  (https, ssh, git, file)
            (?:[^@/]+@)?                  #   [user[:pass]@]
            [\w.\-]*(?::\d+)?/            #   host[:port]/   (host may be empty)
        | [\w.\-]+@[\w.\-]+:              # user@host:owner/name  (scp-like)
        | [\w.\-]+:                       # host:owner/name       (scp-like)
        )?
        (?P<owner>[\w.\-]+)/(?P<name>[\w.\-]+?)(?:\.git)?/?$""",
    re.X,
)


def normalise_remote(url: str) -> str | None:
    """Reduce any remote URL form to `owner/name`.

    Property-tested because the failure mode is asymmetric: a normaliser that
    silently returns the URL unchanged makes the deploy guard reject every
    valid checkout, turning a safety feature into an outage.

    Kept in step with the bash `normalise_remote()` in `deploy/host/deploy.sh`,
    which guards `git reset --hard` and `git clean -fd` on the production host.
    The two must agree, and where they cannot -- input that is not a two-segment
    repository path at all -- both must still refuse: bash echoes the input
    unchanged, which never equals the expected slug, and this returns None.
    """
    if not url or not url.strip():
        return None
    m = _SLUG_RX.match(url.strip())
    if not m:
        return None
    return f"{m.group('owner')}/{m.group('name')}"


# Any remote-shaped string in a file: any scheme, or the scp-like
# `[user@]host.tld:owner/name`. Extraction has to be at least as broad as the
# normaliser, or a valid URL in an unusual form reads as "no repository URL
# found" and fails the gate on a correct script.
_URL_IN_TEXT = re.compile(
    r"""["']?(?P<url>
          (?: [A-Za-z][A-Za-z0-9+.\-]*://          # scheme://
            | (?:[\w.\-]+@)?[\w\-]+(?:\.[\w\-]+)+: # [user@]host.tld:
          )
          [^"'\s]+ )["']?""",
    re.X,
)


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
    if not (len(path) >= 2 and path.startswith('"') and path.endswith('"')):
        return path
    body = path[1:-1]
    # git escapes non-ASCII bytes octally, one escape per *byte*. Decoding the
    # escapes straight to text would turn "\303\251" into two Latin-1
    # characters instead of "é", so the escapes are resolved to bytes first and
    # only then decoded as UTF-8.
    try:
        return (body.encode("latin-1", "backslashreplace")
                    .decode("unicode_escape")
                    .encode("latin-1")
                    .decode("utf-8"))
    except (UnicodeDecodeError, UnicodeEncodeError):
        try:
            return body.encode("utf-8", "surrogateescape").decode("unicode_escape")
        except (UnicodeDecodeError, UnicodeEncodeError):
            return body


def _split_rename(rest: str) -> tuple[str, str] | None:
    """Split `old -> new`, honouring quotes around either side.

    Quote-aware because git quotes each side independently, and a filename may
    itself contain ` -> `. Splitting on the first occurrence would then report
    two paths that do not exist and miss the one that does.
    """
    if rest.startswith('"'):
        end = 1
        while end < len(rest):
            if rest[end] == "\\":
                end += 2
                continue
            if rest[end] == '"':
                break
            end += 1
        head, sep, tail = rest[:end + 1], rest[end + 1:end + 5], rest[end + 5:]
        if sep == " -> ":
            return head, tail
        return None
    if " -> " in rest:
        old, new = rest.split(" -> ", 1)
        return old, new
    return None


def parse_porcelain(output: str) -> list[tuple[str, str]]:
    """(status, path) for every entry, with both sides of a rename returned."""
    entries: list[tuple[str, str]] = []
    for raw in output.splitlines():
        if not raw.strip():
            continue
        status, rest = raw[:2], raw[3:]
        # Only R and C entries carry ` -> `. Any other status with an arrow in
        # it has an arrow in the *filename*, and treating that as a rename
        # would drop the real path.
        pair = _split_rename(rest) if ("R" in status or "C" in status) else None
        if pair:
            old, new = pair
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


def findings_in_porcelain(output: str, queried: str | None = None) -> list[Finding]:
    """The pure half: porcelain text in, findings out.

    Separated from the git call so the working-tree property can be exercised
    over synthetic porcelain output -- including the shapes that are awkward or
    impossible to produce on a given host, such as a filename containing an
    arrow.

    `queried` is the critical path the output was requested for. git's own
    pathspec matching already established the relationship, so an entry git
    reports for a pathspec is a finding even when it is not literally a
    descendant of it -- a wholly untracked `.github/` is reported as the
    collapsed directory `.github/workflows/`, not as the file inside it.
    """
    findings: list[Finding] = []
    for status, path in parse_porcelain(output):
        crit = _under_critical_path(path) or queried
        if not crit:
            continue
        findings.append(Finding(
            rule="critical-path-dirty", path=path,
            observed=f"status={status.strip() or '??'}",
            expected="committed",
            message=f"under {crit}; deploy.sh runs git clean -fd on the target",
        ))
    return findings


def check_critical_paths_clean(root: Path, report: Report) -> None:
    """`git status --porcelain -- <path>` per critical path (9.1).

    Per path rather than one global scan, because git's pathspec matching sees
    cases a global scan hides: an entirely untracked `.github/` is reported
    globally as the collapsed `?? .github/`, which is not a descendant of
    `.github/workflows/` and would slip past a prefix filter, while the
    pathspec query reports `?? .github/workflows/`.
    """
    seen: set[tuple[str, str]] = set()
    for crit in CRITICAL_PATHS:
        output = _git(root, "status", "--porcelain", "--", crit)
        for finding in findings_in_porcelain(output, queried=crit):
            key = (str(finding.observed), finding.path)
            if key in seen:  # the same file matches only one pathspec today,
                continue     # but overlapping CRITICAL_PATHS must not double-report
            seen.add(key)
            report.add(finding)


def check_deploy_script_slug(root: Path, report: Report) -> None:
    rel = "deploy/host/deploy.sh"
    script = root / rel
    if not script.is_file():
        report.add(Finding(rule="deploy-slug", path=rel, observed="<absent>",
                           expected=EXPECTED_SLUG,
                           message="the deploy script is a required source"))
        return

    text = script.read_text(encoding="utf-8", errors="replace")
    found: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in _URL_IN_TEXT.finditer(line):
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
