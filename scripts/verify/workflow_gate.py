"""Assert the workflow topology by reachability, not by review habit.

Every argument in this session about whether a deploy is gated has been made
by reading YAML and tracing `needs` by eye. That works until someone adds a
job, renames one, or introduces a second path to the same deployment. This
makes the argument executable.

Five properties:

1. Every job containing a deployment command has the required gates as
   *transitive* needs. Transitive matters: `deploy -> test -> ci-gate` is
   gated even though `deploy` does not name `ci-gate` directly, and a check
   that only looked at direct edges would demand redundant ones.
2. Every production deployment job is preceded by its staging counterpart.
3. No job in the gating set masks a non-zero exit, and no job in it carries an
   `if:` that runs regardless of upstream failure. A gate that cannot fail is
   not a gate, which is the exact defect `|| true` created in ci.yml; a gate
   guarded by `always()` is the same defect spelled in Actions expressions,
   because it defeats every `needs` edge the graph otherwise proves.

   The gating set crosses the `workflow_call` boundary. `ci-gate` is a
   *reusable workflow call*, so the jobs that can actually fail live in
   another file; reading `needs` within one file made the six ci.yml jobs
   invisible to this rule, which is how re-adding `|| true` to ci.yml's
   `yarn build` would have passed a check whose stated purpose is
   Requirement 8.8. Local `uses: ./.github/workflows/<file>` references are
   resolved and every job of the called workflow joins the gating set -- a
   reusable call succeeds only if all of its jobs do. A reference this
   checkout cannot read is reported, not skipped: an unreadable gate is not
   a verified gate.
4. A verification job follows each deployment job. Deploying without checking
   is how a green pipeline coexists with a broken site. Detected from the
   job's *steps* only: a job that merely names `verify-staging` in `needs`
   would otherwise vouch for itself.
5. Staging and production are isolated by name and identical by shape
   (Requirement 8, Property 16): their hostname sets are disjoint under
   normalisation, their credential secret-name sets are disjoint, and their
   compose service-name sets are identical. Hostnames are read from the
   ENVIRONMENTS table in deployment_check.py and secret names from the
   parsed workflow jobs -- the same declarations Requirement 8.3 names as
   the verification source, so this rule cannot drift from what it checks.

Pure graph reachability over parsed YAML. No network, no git.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

import yaml

from .common import (
    Finding,
    Report,
    Suppression,
    Unavailable,
    base_parser,
    resolve_root,
    run,
    suppression_on,
)

# Commands that put something into an environment users can reach.
DEPLOY_MARKERS = (
    # `firebase deploy ...` and the npx form `firebase-tools@13 deploy ...`:
    # `firebase\S*` covers both, since the package token has no space after
    # the word "firebase".
    re.compile(r"firebase\S*\s+(?:\S+\s+)*deploy"),
    re.compile(r"hosting:channel:deploy"),
    re.compile(r"hosting:clone"),
    re.compile(r"action-hosting-deploy"),
    re.compile(r"ssh-action"),
    re.compile(r"docker\s+compose[^\n]*\bup\b"),
)

VERIFY_MARKERS = (
    re.compile(r"deployment_check"),
    re.compile(r"verify[-_]production"),
    re.compile(r"verify[-_]staging"),
)

# A step that swallows a failure. `continue-on-error` is the YAML spelling of
# the same thing `|| true` does in shell.
MASK_MARKERS = (
    re.compile(r"\|\|\s*true"),
    re.compile(r"continue-on-error:\s*true"),
    re.compile(r"^\s*exit\s+0\s*$", re.M),
)

# Status functions in a job-level `if:` that make the job run even when the
# jobs it `needs` failed. `always()` is the blatant one; `failure()` and
# `cancelled()` select exactly the runs the gates were meant to stop, and
# `success() || <anything>` is `always()` written the long way. A condition
# naming no status function -- `github.ref == 'refs/heads/main'` -- narrows
# *when* the job runs without changing *whether* a failed gate stops it, so it
# is not a defeat.
CONDITION_DEFEATS = (
    re.compile(r"\balways\s*\("),
    re.compile(r"\bfailure\s*\("),
    re.compile(r"\bcancelled\s*\("),
)
SUCCESS_CALL = re.compile(r"\bsuccess\s*\(")

# A reusable-workflow reference this repository owns. GitHub resolves these
# against the repository root at the calling commit, never against the calling
# file's directory, so resolution needs the root rather than the file.
LOCAL_USES_PREFIX = "./"

# What today's workflows are required to have. The staging gates exist since
# spec task 12.6; they stay behind --require-staging so the check remains
# usable on a checkout that predates them, and ci.yml passes the flag
# (spec task 12.9).
REQUIRED_GATES = ("preflight", "ci-gate")
STAGING_GATES = ("deploy-staging", "verify-staging")

# `${{ secrets.NAME }}` references, wherever a job carries them -- `env:`,
# `with:`, or a run step. The reference is the *declaration* Requirement 8.3
# reads; the value never appears in the file.
SECRET_REF = re.compile(r"\$\{\{\s*secrets\.([A-Za-z_][A-Za-z0-9_]*)")

# GITHUB_TOKEN is issued by the runner per run and is identical in every job
# by construction. It is not an environment credential anyone declared, so
# sharing it across staging and production jobs is not an isolation defect.
SHARED_RUN_SECRETS = frozenset({"GITHUB_TOKEN"})

# The staging compose overlay (spec task 12.3). Its service set must equal
# the base file's: a service added to docker-compose.yml and forgotten here
# would collide with production on container name or port at `up` time.
STAGING_OVERLAY = Path("deploy") / "staging" / "docker-compose.staging.yml"
COMPOSE_BASE = Path("docker-compose.yml")


class _ComposeLoader(yaml.SafeLoader):
    """SafeLoader that tolerates compose merge tags (`!override`, `!reset`).

    The overlay needs `!override` on port lists because compose merges
    sequences by appending, and safe_load would otherwise refuse the file the
    rule exists to read.
    """


def _tagged(loader, _suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


_ComposeLoader.add_multi_constructor("!", _tagged)


@dataclass
class Job:
    name: str
    needs: list[str] = field(default_factory=list)
    body: str = ""
    steps_body: str = ""
    uses: str = ""
    condition: str = ""

    @property
    def deploys(self) -> bool:
        return any(rx.search(self.body) for rx in DEPLOY_MARKERS)

    @property
    def verifies(self) -> bool:
        """A verification job, judged by what it *runs*.

        Scoped to the steps on purpose. Searching the whole job body made
        `needs: [verify-staging]` count as verification, so `deploy` and
        `build-and-deploy` both claimed to verify themselves and the
        unverified-deploy rule could not fire on the jobs it exists for.
        """
        return any(rx.search(self.steps_body) for rx in VERIFY_MARKERS)

    @property
    def masks(self) -> list[str]:
        """Every distinct failure-masking token in the job, not just the first.

        One match per job meant a second mask in a job whose first mask was
        suppressed went unreported -- a suppression for the optional install
        would have covered a `|| true` on the test step beside it.
        """
        found: list[str] = []
        for rx in MASK_MARKERS:
            for m in rx.finditer(self.body):
                token = m.group(0).strip()
                if token not in found:
                    found.append(token)
        return found

    @property
    def defeating_condition(self) -> str | None:
        """The job-level `if:` that runs this job despite a failed gate."""
        cond = self.condition
        if not cond:
            return None
        if any(rx.search(cond) for rx in CONDITION_DEFEATS):
            return cond
        if SUCCESS_CALL.search(cond) and "||" in cond:
            return cond
        return None

    @property
    def is_staging(self) -> bool:
        return "staging" in self.name.lower()

    @property
    def is_production(self) -> bool:
        """Anything that deploys and is not explicitly a staging job."""
        return self.deploys and not self.is_staging

    def secret_names(self) -> set[str]:
        """Every GitHub secret this job references, minus run-scoped ones."""
        return set(SECRET_REF.findall(self.body)) - SHARED_RUN_SECRETS


@dataclass
class Graph:
    path: str
    jobs: dict[str, Job]
    source: str | None = None
    # Where the file is and which root its `uses: ./...` references resolve
    # against. Both are optional so a graph can still be analysed in isolation,
    # which is how the synthetic corpus exercises one rule at a time.
    file: Path | None = None
    root: Path | None = None
    _regions: dict[str, tuple[int, int]] | None = field(
        default=None, repr=False, compare=False)

    def job_regions(self) -> dict[str, tuple[int, int]]:
        """Line span (0-based, inclusive) of each job in the raw source.

        Suppression markers are comments, so they exist only in the text, and
        attributing one to the right job needs the job's own lines. Without
        this, a reviewed exception in one job silently exempted an identical
        token in another.
        """
        if self._regions is None:
            self._regions = _job_regions(self.source or "")
        return self._regions

    def needs_of(self, name: str) -> list[str]:
        return self.jobs[name].needs if name in self.jobs else []

    def ancestors(self, name: str) -> set[str]:
        """Every job reachable backwards through `needs`.

        Cycle-safe: a workflow with a `needs` cycle never runs, but this check
        must report that rather than hang on it.
        """
        seen: set[str] = set()
        stack = list(self.needs_of(name))
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(self.needs_of(n))
        return seen

    def has_cycle(self) -> str | None:
        colour: dict[str, int] = {}

        def visit(n: str) -> str | None:
            colour[n] = 1
            for m in self.needs_of(n):
                if colour.get(m) == 1:
                    return f"{n} -> {m}"
                if colour.get(m, 0) == 0 and m in self.jobs:
                    found = visit(m)
                    if found:
                        return found
            colour[n] = 2
            return None

        for name in self.jobs:
            if colour.get(name, 0) == 0:
                found = visit(name)
                if found:
                    return found
        return None

    def orphan_needs(self) -> list[tuple[str, str]]:
        """`needs` entries naming a job that does not exist.

        Actions treats these as an error, but a typo'd gate name is the exact
        way a gate silently stops gating, so it is reported here too.
        """
        return [(name, dep)
                for name, job in self.jobs.items()
                for dep in job.needs if dep not in self.jobs]


_JOBS_KEY = re.compile(r"jobs:\s*(#.*)?$")
_MAPPING_KEY = re.compile(r"([A-Za-z_][\w.\-]*)\s*:")


def _job_regions(source: str) -> dict[str, tuple[int, int]]:
    """Each job's line span under the top-level `jobs:` mapping.

    Indentation-based rather than a YAML round trip, because safe_load discards
    comments and the markers this feeds are comments.
    """
    lines = source.splitlines()
    regions: dict[str, tuple[int, int]] = {}
    in_jobs = False
    job_indent: int | None = None
    current: str | None = None
    start = 0

    def close(end: int) -> None:
        nonlocal current
        if current is not None:
            regions[current] = (start, end)
            current = None

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lead = len(line) - len(line.lstrip())
        if not in_jobs:
            if lead == 0 and _JOBS_KEY.match(stripped):
                in_jobs = True
            continue
        if lead == 0:  # a sibling top-level key ends the jobs block
            close(idx - 1)
            in_jobs = False
            continue
        if job_indent is None:
            job_indent = lead
        if lead == job_indent:
            m = _MAPPING_KEY.match(stripped)
            if m:
                close(idx - 1)
                current, start = m.group(1), idx
    close(len(lines) - 1)
    return regions


def load_graph(path: Path, root: Path | None = None) -> Graph:
    """Parse one workflow file.

    `root` is what `uses: ./...` resolves against. When absent it is inferred:
    a file under `.github/workflows/` implies the repository two levels up,
    and anything else -- a synthetic graph in a temp directory -- implies its
    own directory.
    """
    source = path.read_text(encoding="utf-8")
    try:
        doc = yaml.safe_load(source) or {}
    except yaml.YAMLError as exc:
        raise Unavailable(f"{path.name} is not parseable YAML: {exc}") from exc

    if root is None:
        parent = path.parent
        root = (path.parents[2]
                if parent.name == "workflows" and parent.parent.name == ".github"
                else parent)

    jobs: dict[str, Job] = {}
    for name, spec in (doc.get("jobs") or {}).items():
        spec = spec or {}
        needs = spec.get("needs", [])
        needs = [needs] if isinstance(needs, str) else list(needs or [])
        # `uses:` jobs carry their gate identity in the job name, and their
        # body is a workflow reference rather than steps. The reference is read
        # structurally: a regex over the dumped body would depend on how
        # safe_dump chose to quote it.
        uses = spec.get("uses") or ""
        condition = spec.get("if")
        body = yaml.safe_dump(spec, default_flow_style=False)
        steps_body = yaml.safe_dump(spec.get("steps") or [],
                                    default_flow_style=False)
        jobs[name] = Job(name=name, needs=needs, body=body,
                         steps_body=steps_body,
                         uses=str(uses),
                         condition="" if condition is None else str(condition))
    return Graph(path=path.name, jobs=jobs, source=source, file=path, root=root)


# A masking token often sits on a shell continuation, and a comment cannot be
# placed between a trailing `\` and the line it continues, so the marker is
# looked for further above than suppression_on's one line.
_MASK_LOOKBACK = 4


def _suppression_for_mask(g: Graph, job: str, masked: str) -> str | None:
    """A `verify: allow <reason>` covering every occurrence of `masked` in `job`.

    The graph is parsed YAML and carries no line numbers, so the raw text is
    consulted for the marker -- scoped to the job's own lines, and skipping
    full-line comments, because ci.yml documents in prose the `|| true` that
    task 2.2 removed and prose is not a mask.

    Every occurrence must be covered. One marked occurrence used to exempt the
    whole token, so a reviewed exception on an optional install would also
    have silenced an unreviewed mask on the step below it.
    """
    if g.source is None:
        return None
    lines = g.source.splitlines()
    lo, hi = g.job_regions().get(job, (0, len(lines) - 1))
    reasons: list[str] = []
    for idx in range(lo, min(hi, len(lines) - 1) + 1):
        line = lines[idx]
        if line.lstrip().startswith("#") or masked not in line:
            continue
        found = None
        for probe in range(idx, max(lo, idx - _MASK_LOOKBACK) - 1, -1):
            found = suppression_on(lines, probe)
            if found:
                break
        if not found:
            return None
        reasons.append(found)
    return reasons[0] if reasons else None


# --------------------------------------------------------------------------
# Property 5: staging/production isolation (Requirement 8, Property 16)
# --------------------------------------------------------------------------

def normalise_host(url: str) -> str | None:
    """Hostname comparison form: lowercase, no trailing dot.

    `HTTPS://Staging.Example.COM./x` and `https://staging.example.com/` name
    the same host, and a disjointness check that treated them as different
    would certify isolation that DNS does not provide.
    """
    host = urlsplit(url).hostname
    return host.lower().rstrip(".") if host else None


def environment_hostnames() -> dict[str, set[str]]:
    """Hostname sets per environment, from deployment_check's ENVIRONMENTS.

    Read from the table the staging verification actually probes, not from a
    copy: Requirement 8.1's declarations and this rule's inputs must be the
    same object or the rule can pass while the check probes something else.
    """
    from .deployment_check import ENVIRONMENTS
    return {
        env: {h for e in endpoints if (h := normalise_host(e.url))}
        for env, endpoints in ENVIRONMENTS.items()
    }


def check_hostname_isolation(staging: set[str], production: set[str],
                             report: Report) -> None:
    for host in sorted(staging & production):
        report.add(Finding(
            rule="shared-environment-hostname",
            path="scripts/verify/deployment_check.py", observed=host,
            expected="disjoint staging and production hostname sets",
            message="a shared hostname means a staging check can pass "
                    "against production, or the reverse"))


def check_secret_isolation(g: Graph, report: Report) -> None:
    """Staging and production jobs must not share credential secret names.

    A shared name is a shared value: GitHub resolves `secrets.X` to one value
    per environment scope, and the recurring defect this spec closes is a
    staging stack quietly running on production credentials.
    """
    staging: set[str] = set()
    production: set[str] = set()
    for job in g.jobs.values():
        (staging if job.is_staging else production).update(job.secret_names())
    for name in sorted(staging & production):
        report.add(Finding(
            rule="shared-environment-secret", path=g.path, observed=name,
            expected="disjoint staging and production secret names",
            message="a staging job holding a production credential is the "
                    "isolation Requirement 8.3 exists to prevent"))


def compose_services(text: str) -> set[str]:
    """Service names a compose file declares, tolerating merge tags."""
    doc = yaml.load(text, Loader=_ComposeLoader) or {}
    return set(doc.get("services") or {})


def check_service_parity(production: set[str], staging: set[str],
                         report: Report, *, path: str = "") -> None:
    """Identical by shape: the overlay must cover exactly the base services.

    A service only in the base would collide with production on container
    name or port; a service only in the overlay configures something the
    merged model does not run. Both directions are drift.
    """
    for svc in sorted(production - staging):
        report.add(Finding(
            rule="service-parity", path=path, observed=f"{svc} missing from staging",
            expected="the same service set in both environments"))
    for svc in sorted(staging - production):
        report.add(Finding(
            rule="service-parity", path=path, observed=f"{svc} only in staging",
            expected="the same service set in both environments"))


# --------------------------------------------------------------------------
# Property 3: the gating set, across the workflow_call boundary
# --------------------------------------------------------------------------

def _add_once(report: Report, item: Finding | Suppression) -> None:
    """Record `item` unless an identical one is already recorded.

    Both deploy workflows call ci.yml, so an unsuppressed mask in ci.yml is one
    defect reached twice. Reporting it twice would make the count a function of
    how many workflows call the gate rather than of how many defects exist.
    """
    bucket = report.findings if isinstance(item, Finding) else report.suppressions
    if item not in bucket:
        bucket.append(item)


def expand_gating_set(g: Graph, names: set[str],
                      report: Report) -> list[tuple[Graph, str, str]]:
    """(graph, job, call chain) for every job a deployment's gates depend on.

    `ci-gate` is a `uses:` job: nothing in it can fail, because it has no
    steps -- the six jobs that can fail live in ci.yml. Following the call is
    what makes Requirement 8.8 enforceable, and every job of a called workflow
    joins the set because a reusable call succeeds only if all of its jobs do.
    """
    out = [(g, n, "") for n in sorted(names) if n in g.jobs]
    # Keyed by resolved path, seeded with the caller: a workflow that calls
    # itself, or any call cycle, is visited once and noted instead of hanging.
    # `Graph.has_cycle` covers `needs` cycles, which are a different graph.
    seen: set[Path] = {g.file.resolve()} if g.file else set()
    queue = list(out)
    while queue:
        owner, name, via = queue.pop(0)
        ref = owner.jobs[name].uses.strip()
        if not ref:
            continue
        chain = f"{via} -> {name}" if via else name
        if not ref.startswith(LOCAL_USES_PREFIX):
            # `owner/repo/.github/workflows/x.yml@ref` is not in this checkout,
            # so its steps cannot be read. Reported rather than skipped: the
            # whole point of this rule is that an uninspected gate is not a
            # verified gate, and silence here would be exactly the blind spot
            # the local case just stopped having.
            _add_once(report, Finding(
                rule="unresolvable-gate", path=owner.path,
                observed=f"{chain} uses {ref}",
                expected="a gate whose definition is in this checkout",
                message="a called workflow from another repository cannot be "
                        "inspected for masking, so its gating is unverified"))
            continue
        if owner.root is None:
            report.notes.append(
                f"{owner.path}: {chain} calls {ref}; no root to resolve it against")
            continue
        target = owner.root / ref[len(LOCAL_USES_PREFIX):]
        if not target.is_file():
            # A graph analysed on its own -- the synthetic corpus, a partial
            # checkout -- names a callee that is not here. Actions refuses to
            # start a run whose local `uses:` target is missing, so that failure
            # mode is already loud; a finding here would only make every
            # isolated graph unanalysable.
            report.notes.append(
                f"{owner.path}: {chain} calls {ref}, absent from this "
                f"checkout; its jobs were not inspected")
            continue
        resolved = target.resolve()
        if resolved in seen:
            report.notes.append(
                f"{owner.path}: {chain} calls {ref}, already inspected; "
                f"not followed again")
            continue
        seen.add(resolved)
        try:
            called = load_graph(target, root=owner.root)
        except Unavailable as exc:
            _add_once(report, Finding(
                rule="unresolvable-gate", path=owner.path,
                observed=f"{chain} uses {ref}", expected="a parseable called workflow",
                message=str(exc)))
            continue
        report.notes.append(
            f"{owner.path}: {chain} calls {ref}; {len(called.jobs)} job(s) "
            f"inspected across the workflow_call boundary")
        for job_name in sorted(called.jobs):
            entry = (called, job_name, chain)
            out.append(entry)
            queue.append(entry)
    return out


def check_gate_integrity(g: Graph, gating: set[str], report: Report) -> None:
    """Nothing in the gating set may mask a failure or outrun one."""
    for owner, name, via in expand_gating_set(g, gating, report):
        job = owner.jobs[name]
        for masked in job.masks:
            # A mask can be legitimate when a later step catches the
            # consequence -- e.g. a best-effort install whose failure surfaces
            # at the next step's import. That is not derivable from the graph,
            # so it is an explicit, reviewed exception rather than a silent
            # exemption, and it is read from the file the mask lives in.
            reason = _suppression_for_mask(owner, name, masked)
            if reason:
                _add_once(report, Suppression("masked-gate", owner.path, 0, reason))
            else:
                _add_once(report, Finding(
                    rule="masked-gate", path=owner.path,
                    observed=f"{name}: {masked}",
                    expected="a step that can fail",
                    message="a gate that cannot fail is not a gate"
                            + (f"; reached through {via}" if via else "")))
        defeat = job.defeating_condition
        if defeat:
            _add_once(report, Finding(
                rule="conditional-gate", path=owner.path,
                observed=f"{name}: if: {defeat}",
                expected="an `if:` that cannot run past a failed gate",
                message="`always()`, `failure()`, `cancelled()` and "
                        "`success() || ...` run the job whatever its `needs` "
                        "did, which defeats every edge in the graph"
                        + (f"; reached through {via}" if via else "")))


def check_graph(g: Graph, report: Report, *, require_staging: bool = False) -> None:
    check_secret_isolation(g, report)

    cycle = g.has_cycle()
    if cycle:
        report.add(Finding(rule="workflow-cycle", path=g.path, observed=cycle,
                           expected="an acyclic needs graph",
                           message="a workflow with a needs cycle never runs"))
        return  # reachability is meaningless past this point

    for name, dep in g.orphan_needs():
        report.add(Finding(rule="workflow-orphan-need", path=g.path,
                           observed=f"{name} needs {dep}", expected="an existing job",
                           message="a typo'd gate name is a gate that stops gating"))

    deploy_jobs = [j for j in g.jobs.values() if j.deploys]

    for job in deploy_jobs:
        # Staging gates are required upstream of *production* deploys only.
        # Requiring them of the staging deploy itself is circular: deploy-staging
        # would have to be its own ancestor.
        required = list(REQUIRED_GATES)
        if require_staging and job.is_production:
            required += list(STAGING_GATES)

        reachable = g.ancestors(job.name)
        for gate in required:
            if gate not in reachable and gate in g.jobs:
                report.add(Finding(
                    rule="ungated-deploy", path=g.path, observed=job.name,
                    expected=f"transitive needs on {gate}",
                    message="this job deploys; the gate is not upstream of it"))
            elif gate not in g.jobs:
                report.add(Finding(
                    rule="missing-gate", path=g.path, observed=f"no job named {gate}",
                    expected=f"{gate} defined and upstream of {job.name}"))

        # A deployment needs a verification successor.
        successors = [o for o in g.jobs.values() if job.name in g.ancestors(o.name)]
        if not any(o.verifies for o in successors):
            report.add(Finding(
                rule="unverified-deploy", path=g.path, observed=job.name,
                expected="a verification job downstream",
                message="deploying without checking is how a green pipeline "
                        "coexists with a broken site"))

        if require_staging and job.is_production:
            # ancestors() yields names, not Jobs.
            staged = any(n in g.jobs and g.jobs[n].deploys and "staging" in n.lower()
                         for n in g.ancestors(job.name))
            if not staged:
                report.add(Finding(
                    rule="production-before-staging", path=g.path,
                    observed=job.name, expected="a staging deploy upstream"))

    # Nothing the deployment depends on may mask a failure or run past one.
    # The deploy jobs are included alongside their ancestors: an `if: always()`
    # on the deploy job itself would ignore the very gates this graph proves.
    gating: set[str] = {job.name for job in deploy_jobs}
    for job in deploy_jobs:
        gating |= g.ancestors(job.name)
    check_gate_integrity(g, gating, report)


def build_report(args) -> Report:
    root = resolve_root(args.root)
    wf_dir = root / ".github" / "workflows"
    if not wf_dir.is_dir():
        raise Unavailable(f"{wf_dir} does not exist")

    report = Report()
    files = sorted(p for p in wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml"))
    if not files:
        raise Unavailable(f"no workflow files in {wf_dir}")

    for path in files:
        check_graph(load_graph(path, root=root), report,
                    require_staging=args.require_staging)

    # Property 5, repo-level parts: hostname disjointness from the table the
    # deployment check probes, and service parity between the compose base
    # and the staging overlay.
    hosts = environment_hostnames()
    check_hostname_isolation(hosts.get("staging", set()),
                             hosts.get("production", set()), report)

    overlay = root / STAGING_OVERLAY
    base = root / COMPOSE_BASE
    if overlay.is_file() and base.is_file():
        check_service_parity(
            compose_services(base.read_text(encoding="utf-8")),
            compose_services(overlay.read_text(encoding="utf-8")),
            report, path=STAGING_OVERLAY.as_posix())
    elif args.require_staging:
        report.add(Finding(
            rule="service-parity", path=STAGING_OVERLAY.as_posix(),
            observed="<absent>",
            expected="the staging compose overlay (spec task 12.3)",
            message="staging cannot be identical by shape to production "
                    "without the overlay that declares its shape"))
    else:
        report.notes.append("staging overlay absent; service parity not checked")

    report.notes.append(f"{len(files)} workflow file(s) analysed")
    return report


def main(argv=None) -> int:
    parser = base_parser("Assert the workflow topology gates every deployment.")
    parser.add_argument(
        "--require-staging", action="store_true",
        help="require deploy-staging/verify-staging upstream of every "
             "production deploy, and the staging overlay to exist "
             "(spec tasks 12.6/12.9; ci.yml passes this)")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
