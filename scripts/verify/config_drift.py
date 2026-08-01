"""Detect the configuration-drift class of defect.

A value that must agree across several files is read from every one of them and
compared. The defect this catches is real and recent: `frontend/.firebaserc`
named a Firebase project that serves no live domain while the deploy workflow
named a third one, so a deploy would have reported success and changed nothing.

A missing declaration is a finding, not a skip. Skipping absent values would
let the check pass by deleting a line, certifying agreement among three files
while the fourth targets nothing.

An *added* line is drift too, which is why every extractor returns every
declaration a file makes rather than the first one. A file that declares the
value twice with two different values is a defect regardless of which one the
consumer honours: nobody reading it can tell where the deploy lands.
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
class Declaration:
    """One occurrence of a value in a file, with its line when known."""

    value: str
    line: int | None = None


Extractor = Callable[[str], list[Declaration]]


@dataclass(frozen=True)
class Source:
    """One place a value is declared.

    `extract` returns *every* declaration in the file, not the first. A
    first-match extractor cannot distinguish "declared once, correctly" from
    "declared twice, disagreeing", and the second is drift.
    """

    path: str
    extract: Extractor
    required: bool = False


@dataclass
class DriftRule:
    rule_id: str
    sources: list[Source]
    expected: str | None = None
    required_sources: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # One place declares which sources are required: the sources themselves.
        # Two lists that must agree would be the defect this module exists for.
        if not self.required_sources:
            self.required_sources = [s.path for s in self.sources if s.required]


# --------------------------------------------------------------------------
# Extractors
# --------------------------------------------------------------------------

def _lineno(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _firebaserc_default(text: str) -> list[Declaration]:
    """`.projects.default` only.

    Other aliases under `.projects` are deliberately not compared: Requirement 8
    introduces a staging target, and an alias naming a staging project is a
    legitimate second value rather than drift.
    """
    try:
        value = (json.loads(text).get("projects") or {}).get("default")
    except (json.JSONDecodeError, AttributeError):
        return []
    if not isinstance(value, str) or not value:
        return []
    m = re.search(r'"default"\s*:', text)
    return [Declaration(value, _lineno(text, m.start()) if m else None)]


def _dotenv_key(pattern: str) -> Extractor:
    # `\r` is matched explicitly rather than via `\s`: these files are checked
    # out CRLF on the Windows developer host and LF on the CI runner, and `\s`
    # would additionally span newlines and let a match run past its own line.
    rx = re.compile(
        rf"^[ \t]*(?:export[ \t]+)?{pattern}[ \t]*=[ \t]*(.*?)[ \t\r]*$", re.M)

    def extract(text: str) -> list[Declaration]:
        out: list[Declaration] = []
        for m in rx.finditer(text):
            value = m.group(1).strip().strip('"').strip("'")
            if value:
                out.append(Declaration(value, _lineno(text, m.start())))
        return out

    return extract


def _workflow_project_id(text: str) -> list[Declaration]:
    """Every `projectId:` in the workflow, not just the hosting-deploy step's.

    Parsed by regex rather than YAML on purpose: the value may be a `${{ }}`
    expression, and this check cares about the literal that was written.

    Every occurrence participates because the staging channel this repository
    is heading for deploys from a second step in this same file. Reading only
    the first `projectId:` would let that step name any project at all while
    the check reported agreement -- and the step that deploys is the one whose
    value decides where the build lands.
    """
    return [Declaration(m.group(1).strip("\"'"), _lineno(text, m.start()))
            for m in re.finditer(r"^[ \t]*projectId:[ \t]*(\S+)[ \t\r]*$", text, re.M)]


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


def _render(declarations: list[Declaration]) -> str:
    return ",".join(d.value for d in declarations) if declarations else "<absent>"


def run_agreement_rule(rule: DriftRule, corpus: Corpus, report: Report) -> None:
    """Every declaration in every source must equal `rule.expected`.

    Three failure shapes, all of which have to be findings:
    absent from a required source, present but different, and present twice
    with two different values in one file.
    """
    seen: list[tuple[str, list[Declaration]]] = []
    for src in rule.sources:
        text = corpus.read(src.path)
        seen.append((src.path, src.extract(text) if text is not None else []))

    required = set(rule.required_sources)
    disagreed = False

    for path, declarations in seen:
        if not declarations:
            if path in required:
                report.add(Finding(
                    rule=rule.rule_id, path=path, observed="<absent>",
                    expected=rule.expected,
                    message="declaration missing; a deleted line is drift, not an exemption",
                ))
                disagreed = True
            continue
        for decl in declarations:
            if decl.value != rule.expected:
                report.add(Finding(
                    rule=rule.rule_id, path=path, line=decl.line,
                    observed=decl.value, expected=rule.expected,
                ))
                disagreed = True

    if disagreed:
        # Requirement 3.7: every participating path with the value found in it,
        # including the ones that agree -- a reader fixing the drift needs to
        # see which value the majority of the files actually carry.
        report.notes.append(
            f"{rule.rule_id} participants: "
            + "; ".join(f"{p}={_render(d)}" for p, d in seen)
        )


def check_firebase_project_id(corpus: Corpus, report: Report) -> None:
    run_agreement_rule(_firebase_project_id_rule(), corpus, report)


def check_github_repo_slug(corpus: Corpus, report: Report) -> None:
    """Every reference to a kailash repository must name the same one.

    `deploy/vultr/deploy.sh` is a required source: it runs `git reset --hard`,
    `git clean -fd` and `git clone` against whatever it resolves, so a
    vacuous pass there is the most dangerous outcome in the whole check.
    """
    required = "deploy/vultr/deploy.sh"
    required_hits = 0     # matches in the required source that agree
    required_seen = 0     # matches in the required source, agreeing or not

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
                        required_seen += 1
                    if slug == EXPECTED_REPO_SLUG:
                        if rel == required:
                            required_hits += 1
                        continue
                    reason = suppression_on(lines, idx)
                    if rel == required:
                        # Requirement 9.2 is an exact-match obligation on this
                        # file, so a suppression marker cannot discharge it, and
                        # a disagreeing match does not count towards the
                        # required hit. Otherwise `# verify: allow` on this one
                        # line turns `git reset --hard` and `git clean -fd`
                        # loose on another repository behind a green check.
                        report.add(Finding(
                            rule="github-repo-slug", path=rel, line=lineno,
                            observed=slug, expected=EXPECTED_REPO_SLUG,
                            message="required source names another repository"
                                    + ("; suppression ignored here" if reason else ""),
                        ))
                    elif reason:
                        report.suppressions.append(
                            Suppression("github-repo-slug", rel, lineno, reason))
                    else:
                        report.add(Finding(
                            rule="github-repo-slug", path=rel, line=lineno,
                            observed=slug, expected=EXPECTED_REPO_SLUG,
                        ))

    if required_hits == 0 and required_seen == 0:
        # Only when the file names no repository at all. A disagreeing match has
        # already been reported above with its line, and claiming "no reference"
        # on top of that would be untrue.
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
