"""Detect the configuration-drift class of defect.

A value that must agree across several files is read from every one of them and
compared. The defect this catches is real and recent: `frontend/.firebaserc`
named a Firebase project that serves no live domain while the deploy workflow
named a third one, so a deploy would have reported success and changed nothing.

A missing declaration is a finding, not a skip. Skipping absent values would
let the check pass by deleting a line, certifying agreement among three files
while the fourth targets nothing.
"""
from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
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

EXPECTED_FIREBASE_PROJECT = "kailash-29111"
EXPECTED_REPO_SLUG = "urgaa-eka/kailash"

DATA_DIR = Path(__file__).parent / "data"


@dataclass(frozen=True)
class Source:
    """One place a value is declared."""

    path: str
    extract: Callable[[str], str | None]
    required: bool = False


@dataclass
class DriftRule:
    rule_id: str
    sources: list[Source]
    expected: str | None = None
    required_sources: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# Extractors
# --------------------------------------------------------------------------

def _firebaserc_default(text: str) -> str | None:
    try:
        return (json.loads(text).get("projects") or {}).get("default")
    except (json.JSONDecodeError, AttributeError):
        return None


def _dotenv_key(pattern: str) -> Callable[[str], str | None]:
    rx = re.compile(rf"^\s*(?:export\s+)?{pattern}\s*=\s*(.*?)\s*$", re.M)

    def extract(text: str) -> str | None:
        m = rx.search(text)
        if not m:
            return None
        return m.group(1).strip().strip('"').strip("'") or None

    return extract


def _workflow_project_id(text: str) -> str | None:
    """`projectId:` under the hosting-deploy step.

    Parsed by regex rather than YAML on purpose: the value may be a `${{ }}`
    expression, and this check cares about the literal that was written.
    """
    m = re.search(r"^\s*projectId:\s*(\S+)\s*$", text, re.M)
    return m.group(1).strip("\"'") if m else None


def _firebase_js_field(field_name: str) -> Callable[[str], str | None]:
    rx = re.compile(rf"""{field_name}\s*:\s*["']([^"']+)["']""")

    def extract(text: str) -> str | None:
        m = rx.search(text)
        return m.group(1) if m else None

    return extract


# Both the URL form and the bare `owner/kailash` form.  # secret-scan: allow documents the slug defect this rule detects
REPO_URL_RX = re.compile(r"github\.com[:/](?P<owner>[\w.-]+)/(?P<name>kailash)(?:\.git)?\b")

# The bare form is genuinely ambiguous: `postgres://user:pw@host:5432/kailash`
# and `mongodb://mongo:27017/kailash` both contain `<something>/kailash`. A
# GitHub owner starts with a letter and is not preceded by a path separator or
# a colon, which excludes ports and URL paths without excluding real owners.
REPO_BARE_RX = re.compile(
    r"(?<![\w./:@-])(?P<owner>[A-Za-z][\w.-]*)/(?P<name>kailash)(?![\w.-])")


# --------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------

def _firebase_project_id_rule() -> DriftRule:
    return DriftRule(
        rule_id="firebase-project-id",
        expected=EXPECTED_FIREBASE_PROJECT,
        sources=[
            Source("frontend/.firebaserc", _firebaserc_default, required=True),
            Source("frontend/.env.production",
                   _dotenv_key(r"[A-Z_]*FIREBASE_PROJECT_ID"), required=True),
            Source(".github/workflows/deploy-frontend.yml",
                   _workflow_project_id, required=True),
            Source("backend/.env.example",
                   _dotenv_key(r"FIREBASE_PROJECT_ID"), required=True),
        ],
    )


def check_firebase_project_id(corpus: Corpus, report: Report) -> None:
    rule = _firebase_project_id_rule()
    seen: list[tuple[str, str | None]] = []
    for src in rule.sources:
        text = corpus.read(src.path)
        value = src.extract(text) if text is not None else None
        seen.append((src.path, value))

    for path, value in seen:
        if value is None:
            report.add(Finding(
                rule=rule.rule_id, path=path, observed="<absent>",
                expected=rule.expected,
                message="declaration missing; a deleted line is drift, not an exemption",
            ))
        elif value != rule.expected:
            report.add(Finding(
                rule=rule.rule_id, path=path, observed=value, expected=rule.expected,
            ))

    if any(v != rule.expected for _, v in seen):
        report.notes.append(
            "firebase-project-id participants: "
            + "; ".join(f"{p}={v or '<absent>'}" for p, v in seen)
        )


def check_github_repo_slug(corpus: Corpus, report: Report) -> None:
    """Every reference to a kailash repository must name the same one.

    `deploy/vultr/deploy.sh` is a required source: it runs `git reset --hard`,
    `git clean -fd` and `git clone` against whatever it resolves, so a
    vacuous pass there is the most dangerous outcome in the whole check.
    """
    required = "deploy/vultr/deploy.sh"
    required_hits = 0

    for rel, text in corpus.texts():
        if rel.startswith(".kiro/") or rel == "CHANGELOG.md":
            continue  # prose describing the defect, not a live reference
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            lineno = idx + 1
            for rx in (REPO_URL_RX, REPO_BARE_RX):
                for m in rx.finditer(line):
                    slug = f"{m.group('owner')}/{m.group('name')}"
                    if rel == required:
                        required_hits += 1
                    if slug == EXPECTED_REPO_SLUG:
                        continue
                    reason = suppression_on(lines, idx)
                    if reason:
                        report.suppressions.append(
                            Suppression("github-repo-slug", rel, lineno, reason))
                    else:
                        report.add(Finding(
                            rule="github-repo-slug", path=rel, line=lineno,
                            observed=slug, expected=EXPECTED_REPO_SLUG,
                        ))

    if required_hits == 0:
        report.add(Finding(
            rule="github-repo-slug", path=required, observed="<no match>",
            expected=EXPECTED_REPO_SLUG,
            message="required source yielded no repository reference; "
                    "this script runs git reset --hard and git clean -fd",
        ))


def check_firebase_app_identity(corpus: Corpus, report: Report) -> None:
    """The project number must agree across appId, messagingSenderId and the map.

    A project *id* and project *number* are unrelated strings; no string
    operation derives one from the other, hence the reviewed map file.

    Note the limit of the first comparison: a wholesale copy of another
    project's config is internally consistent and passes it. Only the map
    catches that, which is how the kailash-38268 drift survived review.
    """
    path = "frontend/src/lib/firebase.js"
    text = corpus.read(path)
    if text is None:
        report.add(Finding(rule="firebase-app-identity", path=path,
                           observed="<absent>", expected="a firebase config"))
        return

    app_id = _firebase_js_field("appId")(text)
    sender = _firebase_js_field("messagingSenderId")(text)
    project_id = _firebase_js_field("projectId")(text)

    if not app_id or ":" not in app_id:
        report.add(Finding(rule="firebase-app-identity", path=path,
                           observed=app_id or "<absent>",
                           expected="<project-number>:web:<hash>",
                           message="appId missing or malformed"))
        return

    from_app_id = app_id.split(":")[1]

    if sender is None:
        report.add(Finding(rule="firebase-app-identity", path=path,
                           observed="<absent>", expected=from_app_id,
                           message="messagingSenderId missing"))
    elif sender != from_app_id:
        report.add(Finding(rule="firebase-app-identity", path=path,
                           observed=f"messagingSenderId={sender}",
                           expected=f"appId project number={from_app_id}",
                           message="partial copy-paste from another project"))

    map_path = DATA_DIR / "project_map.json"
    try:
        project_map = json.loads(map_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        report.add(Finding(rule="firebase-app-identity",
                           path="scripts/verify/data/project_map.json",
                           observed="<unreadable>", expected="a JSON object"))
        return

    if project_id not in project_map:
        report.add(Finding(rule="firebase-app-identity", path=path,
                           observed=project_id or "<absent>",
                           expected="|".join(sorted(project_map)),
                           message="project id absent from the reviewed map; "
                                   "add a line so a reviewer sees the new environment"))
    elif project_map[project_id] != from_app_id:
        report.add(Finding(rule="firebase-app-identity", path=path,
                           observed=from_app_id,
                           expected=project_map[project_id],
                           message=f"map says {project_id} is {project_map[project_id]}"))


CHECKS = (
    check_firebase_project_id,
    check_github_repo_slug,
    check_firebase_app_identity,
)


def build_report(args) -> Report:
    root = resolve_root(args.root)
    corpus = load_corpus(root)
    report = Report()
    for check in CHECKS:
        check(corpus, report)
    if corpus.skipped_binary:
        report.notes.append(f"{corpus.skipped_binary} non-UTF-8 file(s) skipped")
    return report


def main(argv=None) -> int:
    parser = base_parser("Detect configuration drift across files that must agree.")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
