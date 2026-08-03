"""Workflow topology, over synthetic graphs -- and over the real ones.

The synthetic corpus isolates each rule; `test_real_workflows_are_gated`
(spec task 12.9) then asserts the actual `.github/workflows/*.yml` files pass
under --require-staging, now that task 12.6 added the staging jobs. That test
is what makes Requirement 8.8 a checked property instead of a review habit.
"""
from __future__ import annotations

import textwrap
from argparse import Namespace
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scripts.verify import workflow_gate as wg
from scripts.verify.common import Exit, Report

FIXTURES = Path(__file__).parent / "fixtures" / "workflows"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _graph(yaml_text: str, tmp_path: Path, name: str = "w.yml") -> wg.Graph:
    p = tmp_path / name
    p.write_text(textwrap.dedent(yaml_text), encoding="utf-8")
    return wg.load_graph(p)


def _two_file_repo(tmp_path: Path, caller: str, called: str) -> wg.Graph:
    """Install two fixtures as `.github/workflows/{deploy,ci}.yml` and load the
    caller from there.

    The layout is the point: `uses: ./.github/workflows/ci.yml` resolves against
    the repository root, not against the calling file's directory, so a
    cross-boundary rule cannot be exercised by a single loose file.
    """
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "deploy.yml").write_text(
        (FIXTURES / caller).read_text(encoding="utf-8"), encoding="utf-8")
    (wf / "ci.yml").write_text(
        (FIXTURES / called).read_text(encoding="utf-8"), encoding="utf-8")
    return wg.load_graph(wf / "deploy.yml")


def _check(yaml_text: str, tmp_path: Path, **kw) -> Report:
    report = Report()
    wg.check_graph(_graph(yaml_text, tmp_path), report, **kw)
    return report


GOOD = """
    jobs:
      preflight:
        steps: [{run: python -m scripts.verify.config_drift}]
      ci-gate:
        uses: ./.github/workflows/ci.yml
      deploy:
        needs: [preflight, ci-gate]
        steps: [{uses: FirebaseExtended/action-hosting-deploy@v0}]
      verify-production:
        needs: deploy
        steps: [{run: python -m scripts.verify.deployment_check --env production}]
    """


class TestWellFormed:
    def test_the_shape_this_repository_now_has_passes(self, tmp_path):
        report = _check(GOOD, tmp_path)
        assert report.exit_code() is Exit.OK, report.render()

    def test_transitive_gating_counts(self, tmp_path):
        """`deploy -> test -> ci-gate` is gated. A check that demanded a direct
        edge would force redundant `needs` entries and teach people to add
        them without meaning."""
        report = _check("""
            jobs:
              preflight:
                steps: [{run: echo hi}]
              ci-gate:
                uses: ./.github/workflows/ci.yml
              test:
                needs: [preflight, ci-gate]
                steps: [{run: pytest}]
              deploy:
                needs: test
                steps: [{uses: appleboy/ssh-action@v1}]
              verify-production:
                needs: deploy
                steps: [{run: python -m scripts.verify.deployment_check}]
            """, tmp_path)
        assert report.exit_code() is Exit.OK, report.render()


class TestUngatedDeploy:
    def test_missing_needs_edge_is_found(self, tmp_path):
        report = _check("""
            jobs:
              preflight:
                steps: [{run: echo hi}]
              ci-gate:
                uses: ./.github/workflows/ci.yml
              deploy:
                needs: [preflight]
                steps: [{uses: appleboy/ssh-action@v1}]
              verify-production:
                needs: deploy
                steps: [{run: python -m scripts.verify.deployment_check}]
            """, tmp_path)
        assert report.exit_code() is Exit.FAILED
        assert "ungated-deploy" in report.render()
        assert "ci-gate" in report.render()

    def test_no_needs_at_all(self, tmp_path):
        report = _check("""
            jobs:
              preflight:
                steps: [{run: echo hi}]
              ci-gate:
                uses: ./.github/workflows/ci.yml
              deploy:
                steps: [{run: docker compose -f docker-compose.yml up -d}]
              verify-production:
                needs: deploy
                steps: [{run: python -m scripts.verify.deployment_check}]
            """, tmp_path)
        assert report.exit_code() is Exit.FAILED
        assert report.render().count("ungated-deploy") == 2


class TestMaskedGate:
    @pytest.mark.parametrize("preflight_body", [
        "    steps: [{run: pytest || true}]",
        "    continue-on-error: true\n    steps: [{run: pytest}]",
    ])
    def test_a_gate_that_cannot_fail_is_reported(self, tmp_path, preflight_body):
        # Built without dedent: the injected body carries its own indentation
        # and textwrap.dedent would find no common prefix to strip.
        text = (
            "jobs:\n"
            "  preflight:\n"
            f"{preflight_body}\n"
            "  ci-gate:\n"
            "    uses: ./.github/workflows/ci.yml\n"
            "  deploy:\n"
            "    needs: [preflight, ci-gate]\n"
            "    steps: [{uses: appleboy/ssh-action@v1}]\n"
            "  verify-production:\n"
            "    needs: deploy\n"
            "    steps: [{run: python -m scripts.verify.deployment_check}]\n"
        )
        report = _check(text, tmp_path)
        assert report.exit_code() is Exit.FAILED, report.render()
        assert "masked-gate" in report.render()

    def test_masking_outside_the_gating_set_is_ignored(self, tmp_path):
        """A `|| true` in a job nothing depends on is untidy, not a gate
        failure. Reporting it would train people to ignore the rule."""
        report = _check("""
            jobs:
              preflight:
                steps: [{run: echo hi}]
              ci-gate:
                uses: ./.github/workflows/ci.yml
              unrelated:
                steps: [{run: flaky-thing || true}]
              deploy:
                needs: [preflight, ci-gate]
                steps: [{uses: appleboy/ssh-action@v1}]
              verify-production:
                needs: deploy
                steps: [{run: python -m scripts.verify.deployment_check}]
            """, tmp_path)
        assert report.exit_code() is Exit.OK, report.render()


class TestGatingAcrossTheWorkflowCallBoundary:
    """The gate that can fail is in another file.

    `ci-gate` is a `uses:` job: it has no steps, so nothing *in it* can mask
    anything, and computing the gating set within one file left ci.yml's own
    jobs uninspected. Re-adding `|| true` to ci.yml's `yarn build` -- the exact
    masking tasks 2.2/2.3 removed -- passed the check that exists to forbid it.
    """

    def test_mask_in_the_called_workflow_is_reported(self, tmp_path):
        g = _two_file_repo(tmp_path, "crossfile_deploy.yml",
                           "crossfile_ci_masked.yml")
        report = Report()
        wg.check_graph(g, report, require_staging=True)
        rendered = report.render()
        assert report.exit_code() is Exit.FAILED, rendered
        masked = [f for f in report.findings if f.rule == "masked-gate"]
        assert masked, rendered
        # The finding must name the called workflow and the job inside it,
        # otherwise it points the reader at the file that is not at fault.
        assert masked[0].path == "ci.yml"
        assert masked[0].observed == "frontend: || true"
        assert "ci-gate" in masked[0].message
        # Nothing else broke: the caller is fully gated and verified.
        assert {f.rule for f in report.findings} == {"masked-gate"}

    def test_a_reviewed_mask_in_the_called_workflow_stays_suppressed(self, tmp_path):
        """Same setup, marker added. The marker lives in the called file, so the
        lookup has to read that file's source rather than the caller's."""
        g = _two_file_repo(tmp_path, "crossfile_deploy.yml",
                           "crossfile_ci_suppressed.yml")
        report = Report()
        wg.check_graph(g, report, require_staging=True)
        rendered = report.render()
        assert report.exit_code() is Exit.OK, rendered
        assert [s.rule for s in report.suppressions] == ["masked-gate"]
        assert report.suppressions[0].path == "ci.yml"
        assert "best-effort" in report.suppressions[0].reason

    def test_the_called_jobs_join_the_gating_set(self, tmp_path):
        g = _two_file_repo(tmp_path, "crossfile_deploy.yml",
                           "crossfile_ci_masked.yml")
        report = Report()
        expanded = wg.expand_gating_set(g, {"ci-gate", "preflight"}, report)
        assert {(owner.path, name) for owner, name, _ in expanded} == {
            ("deploy.yml", "ci-gate"), ("deploy.yml", "preflight"),
            ("ci.yml", "lint"), ("ci.yml", "frontend"),
        }

    def test_a_self_calling_workflow_is_noted_not_followed_forever(self, tmp_path):
        """The recursion guard. `Graph.has_cycle` covers `needs` cycles; a
        `uses:` cycle is a different graph and would not return."""
        g = _two_file_repo(tmp_path, "crossfile_deploy.yml",
                           "crossfile_ci_recursive.yml")
        report = Report()
        wg.check_graph(g, report, require_staging=True)
        rendered = report.render()
        assert report.exit_code() is Exit.OK, rendered
        assert "already inspected" in rendered

    def test_a_workflow_calling_its_caller_terminates(self, tmp_path):
        """The two-file cycle: deploy.yml -> ci.yml -> deploy.yml."""
        wf = tmp_path / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "deploy.yml").write_text(
            "jobs:\n"
            "  ci-gate:\n    uses: ./.github/workflows/ci.yml\n"
            "  deploy:\n    needs: [preflight, ci-gate]\n"
            "    steps: [{uses: appleboy/ssh-action@v1}]\n"
            "  preflight:\n    steps: [{run: echo hi}]\n"
            "  verify-production:\n    needs: deploy\n"
            "    steps: [{run: python -m scripts.verify.deployment_check}]\n",
            encoding="utf-8")
        (wf / "ci.yml").write_text(
            "jobs:\n  back:\n    uses: ./.github/workflows/deploy.yml\n",
            encoding="utf-8")
        report = Report()
        wg.check_graph(wg.load_graph(wf / "deploy.yml"), report)
        assert report.exit_code() is Exit.OK, report.render()
        assert "already inspected" in report.render()

    def test_a_third_party_gate_is_reported_as_unresolvable(self, tmp_path):
        """`owner/repo@ref` is not in this checkout, so its steps cannot be read.
        An uninspected gate is not a verified gate, so it is a finding rather
        than a silent pass."""
        report = _check("""
            jobs:
              preflight:
                steps: [{run: echo hi}]
              ci-gate:
                uses: some-org/shared/.github/workflows/ci.yml@v2
              deploy:
                needs: [preflight, ci-gate]
                steps: [{uses: appleboy/ssh-action@v1}]
              verify-production:
                needs: deploy
                steps: [{run: python -m scripts.verify.deployment_check}]
            """, tmp_path)
        assert report.exit_code() is Exit.FAILED
        assert "unresolvable-gate" in report.render()
        assert "some-org/shared" in report.render()

    def test_an_absent_local_gate_is_a_note_not_a_finding(self, tmp_path):
        """A graph analysed away from its repository names a callee that is not
        there. Actions refuses to start such a run, so the loud failure already
        exists; a finding here would make every isolated graph unanalysable."""
        report = _check(GOOD, tmp_path)
        assert report.exit_code() is Exit.OK, report.render()
        assert "absent from this checkout" in report.render()

    def test_a_local_gate_that_does_not_parse_is_reported(self, tmp_path):
        wf = tmp_path / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "deploy.yml").write_text(
            (FIXTURES / "crossfile_deploy.yml").read_text(encoding="utf-8"),
            encoding="utf-8")
        (wf / "ci.yml").write_text("jobs:\n  a: [unclosed\n", encoding="utf-8")
        report = Report()
        wg.check_graph(wg.load_graph(wf / "deploy.yml"), report)
        assert report.exit_code() is Exit.FAILED
        assert "unresolvable-gate" in report.render()

    def test_the_real_deploy_workflows_reach_the_ci_jobs(self):
        """The regression guard for the defect itself: `backend` and `frontend`
        in ci.yml -- the jobs tasks 2.2/2.3 unmasked -- must be inside the
        gating set of both real deploy workflows."""
        root = REPO_ROOT
        for name in ("deploy-backend.yml", "deploy-frontend.yml"):
            g = wg.load_graph(root / ".github" / "workflows" / name, root=root)
            deploys = {j.name for j in g.jobs.values() if j.deploys}
            gating = set(deploys)
            for job in deploys:
                gating |= g.ancestors(job)
            reached = {(owner.path, job)
                       for owner, job, _ in wg.expand_gating_set(g, gating, Report())}
            assert ("ci.yml", "backend") in reached, name
            assert ("ci.yml", "frontend") in reached, name


class TestGateConditions:
    """A status function in a job-level `if:` outranks every `needs` edge."""

    def _with_condition(self, condition: str) -> str:
        return (
            "jobs:\n"
            "  preflight:\n"
            f"    if: {condition}\n"
            "    steps: [{run: echo hi}]\n"
            "  ci-gate:\n    uses: ./.github/workflows/ci.yml\n"
            "  deploy:\n    needs: [preflight, ci-gate]\n"
            "    steps: [{uses: appleboy/ssh-action@v1}]\n"
            "  verify-production:\n    needs: deploy\n"
            "    steps: [{run: python -m scripts.verify.deployment_check}]\n"
        )

    @pytest.mark.parametrize("condition", [
        "always()",
        "${{ always() }}",
        "success() || failure()",
        "${{ success() || github.event_name == 'workflow_dispatch' }}",
        "cancelled()",
    ])
    def test_a_condition_that_survives_failure_is_reported(self, tmp_path, condition):
        report = _check(self._with_condition(condition), tmp_path)
        assert report.exit_code() is Exit.FAILED, report.render()
        assert "conditional-gate" in report.render()

    @pytest.mark.parametrize("condition", [
        "github.ref == 'refs/heads/main'",
        "${{ github.event_name == 'push' }}",
        "success()",
    ])
    def test_a_condition_naming_no_status_function_is_benign(self, tmp_path, condition):
        """`github.ref == ...` narrows *when* the job runs without changing
        whether a failed gate stops it. The two conditions the real workflows
        carry are of this shape, which is why this is a coverage gap and not a
        live hole."""
        report = _check(self._with_condition(condition), tmp_path)
        assert "conditional-gate" not in report.render(), report.render()

    def test_the_condition_on_a_deploy_job_itself_counts(self, tmp_path):
        """A deploy job is not its own ancestor, so a set built only from
        ancestors would miss the one `if:` that matters most."""
        report = _check("""
            jobs:
              preflight:
                steps: [{run: echo hi}]
              ci-gate:
                uses: ./.github/workflows/ci.yml
              deploy:
                needs: [preflight, ci-gate]
                if: always()
                steps: [{uses: appleboy/ssh-action@v1}]
              verify-production:
                needs: deploy
                steps: [{run: python -m scripts.verify.deployment_check}]
            """, tmp_path)
        assert report.exit_code() is Exit.FAILED
        assert "conditional-gate" in report.render()

    def test_the_real_workflow_conditions_are_benign(self):
        for name in ("deploy-backend.yml", "deploy-frontend.yml", "ci.yml"):
            g = wg.load_graph(REPO_ROOT / ".github" / "workflows" / name,
                              root=REPO_ROOT)
            for job in g.jobs.values():
                assert job.defeating_condition is None, (name, job.name)


class TestJobIntrospection:
    def test_needs_alone_does_not_make_a_job_a_verifier(self, tmp_path):
        """`needs: [verify-staging]` names a verifier; it does not perform a
        verification. Searching the whole job body made every production deploy
        job vouch for itself."""
        g = _graph("""
            jobs:
              deploy:
                needs: [verify-staging, deploy-staging]
                steps: [{uses: appleboy/ssh-action@v1}]
              verify-staging:
                steps: [{run: python -m scripts.verify.deployment_check --env staging}]
            """, tmp_path)
        assert not g.jobs["deploy"].verifies
        assert g.jobs["verify-staging"].verifies

    def test_the_real_production_deploy_jobs_do_not_verify_themselves(self):
        for name, job in (("deploy-backend.yml", "deploy"),
                          ("deploy-frontend.yml", "build-and-deploy")):
            g = wg.load_graph(REPO_ROOT / ".github" / "workflows" / name,
                              root=REPO_ROOT)
            assert not g.jobs[job].verifies, name

    def test_every_mask_in_a_job_is_returned(self, tmp_path):
        """One match per job hid a second mask behind the first one's
        suppression."""
        g = _graph("""
            jobs:
              gate:
                continue-on-error: true
                steps:
                  - run: pytest -q || true
            """, tmp_path)
        assert g.jobs["gate"].masks == ["|| true", "continue-on-error: true"]

    def test_a_reviewed_mask_does_not_cover_an_unreviewed_one(self, tmp_path):
        """Two masks, one marker. The unmarked one must still be a finding, and
        the marker in one job must not reach into another."""
        text = (
            "jobs:\n"
            "  preflight:\n"
            "    steps:\n"
            "      # verify: allow best-effort install checked by the next step\n"
            "      - run: pip install optional-thing || true\n"
            "      - run: python -c \"import app.main\"\n"
            "  other-gate:\n"
            "    needs: preflight\n"
            "    steps: [{run: pytest -q || true}]\n"
            "  ci-gate:\n    uses: ./.github/workflows/ci.yml\n"
            "  deploy:\n    needs: [preflight, ci-gate, other-gate]\n"
            "    steps: [{uses: appleboy/ssh-action@v1}]\n"
            "  verify-production:\n    needs: deploy\n"
            "    steps: [{run: python -m scripts.verify.deployment_check}]\n"
        )
        report = _check(text, tmp_path)
        assert report.exit_code() is Exit.FAILED, report.render()
        masked = [f for f in report.findings if f.rule == "masked-gate"]
        assert [f.observed for f in masked] == ["other-gate: || true"]
        assert len(report.suppressions) == 1


class TestUnverifiedDeploy:
    def test_deploy_with_no_verification_successor(self, tmp_path):
        report = _check("""
            jobs:
              preflight:
                steps: [{run: echo hi}]
              ci-gate:
                uses: ./.github/workflows/ci.yml
              deploy:
                needs: [preflight, ci-gate]
                steps: [{uses: appleboy/ssh-action@v1}]
            """, tmp_path)
        assert report.exit_code() is Exit.FAILED
        assert "unverified-deploy" in report.render()


class TestStagingOrdering:
    def test_production_before_staging_is_reported(self, tmp_path):
        report = _check("""
            jobs:
              preflight:
                steps: [{run: echo hi}]
              ci-gate:
                uses: ./.github/workflows/ci.yml
              deploy-staging:
                needs: [preflight, ci-gate]
                steps: [{uses: appleboy/ssh-action@v1}]
              verify-staging:
                needs: deploy-staging
                steps: [{run: python -m scripts.verify.deployment_check --env staging}]
              deploy:
                needs: [preflight, ci-gate]
                steps: [{uses: appleboy/ssh-action@v1}]
              verify-production:
                needs: deploy
                steps: [{run: python -m scripts.verify.deployment_check --env production}]
            """, tmp_path, require_staging=True)
        assert report.exit_code() is Exit.FAILED
        assert "production-before-staging" in report.render()

    def test_correct_staging_order_passes(self, tmp_path):
        report = _check("""
            jobs:
              preflight:
                steps: [{run: echo hi}]
              ci-gate:
                uses: ./.github/workflows/ci.yml
              deploy-staging:
                needs: [preflight, ci-gate]
                steps: [{uses: appleboy/ssh-action@v1}]
              verify-staging:
                needs: deploy-staging
                steps: [{run: python -m scripts.verify.deployment_check --env staging}]
              deploy:
                needs: [verify-staging]
                steps: [{uses: appleboy/ssh-action@v1}]
              verify-production:
                needs: deploy
                steps: [{run: python -m scripts.verify.deployment_check --env production}]
            """, tmp_path, require_staging=True)
        assert report.exit_code() is Exit.OK, report.render()

    def test_staging_not_required_by_default(self, tmp_path):
        """Default mode stays usable on a checkout without the staging jobs;
        ci.yml passes --require-staging (spec task 12.9), so the enforced
        mode is the one CI actually runs."""
        report = _check(GOOD, tmp_path)
        assert report.exit_code() is Exit.OK


class TestEnvironmentIsolation:
    """Property 16: isolated by name, identical by shape (spec task 12.7)."""

    def test_shared_secret_name_is_reported(self):
        g = wg.load_graph(FIXTURES / "shared_secret.yml")
        report = Report()
        wg.check_graph(g, report, require_staging=True)
        assert report.exit_code() is Exit.FAILED
        rendered = report.render()
        assert "shared-environment-secret" in rendered
        assert "VULTR_SSH_KEY" in rendered and "VULTR_HOST" in rendered
        # The fixture is otherwise fully gated, so the shared names are the
        # only findings -- a second rule firing would mean the fixture no
        # longer isolates this one.
        assert {f.rule for f in report.findings} == {"shared-environment-secret"}

    def test_disjoint_secret_names_pass(self, tmp_path):
        report = _check("""
            jobs:
              deploy-staging:
                steps:
                  - uses: appleboy/ssh-action@v1
                    with: {key: "${{ secrets.STAGING_VULTR_SSH_KEY }}"}
              verify-staging:
                needs: deploy-staging
                steps: [{run: python -m scripts.verify.deployment_check --env staging}]
              deploy:
                needs: verify-staging
                steps:
                  - uses: appleboy/ssh-action@v1
                    with: {key: "${{ secrets.VULTR_SSH_KEY }}"}
              verify-production:
                needs: deploy
                steps: [{run: python -m scripts.verify.deployment_check --env production}]
            """, tmp_path)
        assert "shared-environment-secret" not in report.render()

    def test_github_token_is_not_an_environment_credential(self, tmp_path):
        """The runner issues GITHUB_TOKEN per run; both environments carry it
        by construction, so it cannot be evidence of shared credentials."""
        report = _check("""
            jobs:
              deploy-staging:
                steps:
                  - uses: FirebaseExtended/action-hosting-deploy@v0
                    with: {repoToken: "${{ secrets.GITHUB_TOKEN }}"}
              verify-staging:
                needs: deploy-staging
                steps: [{run: python -m scripts.verify.deployment_check --env staging}]
              deploy:
                needs: verify-staging
                steps:
                  - uses: FirebaseExtended/action-hosting-deploy@v0
                    with: {repoToken: "${{ secrets.GITHUB_TOKEN }}"}
              verify-production:
                needs: deploy
                steps: [{run: python -m scripts.verify.deployment_check --env production}]
            """, tmp_path)
        assert "shared-environment-secret" not in report.render()

    def test_overlapping_hostname_is_reported(self):
        report = Report()
        wg.check_hostname_isolation(
            {"staging.example.com", "api.example.com"},
            {"example.com", "api.example.com"}, report)
        assert report.exit_code() is Exit.FAILED
        assert "shared-environment-hostname" in report.render()
        assert "api.example.com" in report.render()

    def test_disjoint_hostnames_pass(self):
        report = Report()
        wg.check_hostname_isolation(
            {"staging.example.com"}, {"example.com"}, report)
        assert report.exit_code() is Exit.OK

    def test_normalisation_defeats_case_and_trailing_dot(self):
        """`HTTPS://Staging.X.COM.` and `https://staging.x.com` are one host;
        treating them as two would certify isolation DNS does not provide."""
        assert wg.normalise_host("HTTPS://Staging.X.COM./path") == "staging.x.com"

    def test_real_environment_hostnames_are_disjoint(self):
        hosts = wg.environment_hostnames()
        report = Report()
        wg.check_hostname_isolation(hosts["staging"], hosts["production"], report)
        assert report.exit_code() is Exit.OK, report.render()

    @pytest.mark.parametrize("production, staging, missing", [
        ({"backend", "redis"}, {"backend"}, "redis missing from staging"),
        ({"backend"}, {"backend", "redis"}, "redis only in staging"),
    ])
    def test_service_in_one_set_only_is_reported(self, production, staging, missing):
        report = Report()
        wg.check_service_parity(production, staging, report, path="overlay.yml")
        assert report.exit_code() is Exit.FAILED
        assert "service-parity" in report.render()
        assert missing in report.render()

    def test_identical_service_sets_pass(self):
        report = Report()
        wg.check_service_parity({"backend", "redis"}, {"backend", "redis"}, report)
        assert report.exit_code() is Exit.OK

    def test_real_overlay_covers_the_real_compose_file(self):
        """Also proves the loader tolerates the `!override` merge tags the
        overlay needs for its port lists."""
        base = wg.compose_services(
            (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
        overlay = wg.compose_services(
            (REPO_ROOT / wg.STAGING_OVERLAY).read_text(encoding="utf-8"))
        assert base and overlay == base

    def test_missing_overlay_is_a_finding_only_when_staging_is_required(self, tmp_repo):
        tmp_repo.workflow("ci", "jobs:\n  lint:\n    steps: [{run: ruff check .}]\n")
        tmp_repo.compose("services:\n  backend: {}\n")
        strict = wg.build_report(Namespace(root=tmp_repo.root, require_staging=True))
        assert strict.exit_code() is Exit.FAILED
        assert "service-parity" in strict.render()
        lax = wg.build_report(Namespace(root=tmp_repo.root, require_staging=False))
        assert lax.exit_code() is Exit.OK


def test_real_workflows_are_gated():
    """Spec task 12.9: the actual workflows, under the mode ci.yml runs.

    Every production deploy job must reach preflight, ci-gate, deploy-staging
    and verify-staging through `needs`; nothing in the gating set may mask a
    failure; the environments must be isolated by name and identical in
    compose shape. This is what makes Requirement 8.8 a checked property
    instead of a review habit.
    """
    report = wg.build_report(Namespace(root=REPO_ROOT, require_staging=True))
    assert report.exit_code() is Exit.OK, report.render()


class TestMalformedGraphs:
    def test_cycle_is_reported_not_hung_on(self, tmp_path):
        report = _check("""
            jobs:
              a:
                needs: b
                steps: [{run: echo}]
              b:
                needs: a
                steps: [{run: echo}]
            """, tmp_path)
        assert report.exit_code() is Exit.FAILED
        assert "workflow-cycle" in report.render()

    def test_orphan_need_is_reported(self, tmp_path):
        """A typo'd gate name is how a gate silently stops gating."""
        report = _check("""
            jobs:
              deploy:
                needs: [ci-gat]
                steps: [{uses: appleboy/ssh-action@v1}]
            """, tmp_path)
        assert "workflow-orphan-need" in report.render()

    def test_workflow_with_no_deploy_jobs_passes(self, tmp_path):
        report = _check("""
            jobs:
              lint:
                steps: [{run: ruff check .}]
              test:
                needs: lint
                steps: [{run: pytest}]
            """, tmp_path)
        assert report.exit_code() is Exit.OK


class TestDeployDetection:
    @pytest.mark.parametrize("step", [
        "uses: FirebaseExtended/action-hosting-deploy@v0",
        "uses: appleboy/ssh-action@v1",
        "run: firebase deploy --only hosting",
        "run: firebase hosting:clone a:live b:live",
        "run: docker compose -f docker-compose.yml up -d --build",
    ])
    def test_each_marker_is_recognised(self, tmp_path, step):
        g = _graph(f"jobs:\n  d:\n    steps: [{{{step}}}]\n", tmp_path)
        assert g.jobs["d"].deploys, step

    @pytest.mark.parametrize("step", [
        "run: docker compose config",
        "run: docker compose -f docker-compose.yml build --pull",
        "run: echo deploying",
    ])
    def test_non_deploying_steps_are_not(self, tmp_path, step):
        g = _graph(f"jobs:\n  d:\n    steps: [{{{step}}}]\n", tmp_path)
        assert not g.jobs["d"].deploys, step


@given(chain=st.lists(st.sampled_from(["a", "b", "c", "d"]), min_size=1, max_size=4,
                      unique=True))
def test_property_ancestors_is_transitive_closure(chain, tmp_path_factory):
    """Reachability, not adjacency: every job earlier in a linear chain is an
    ancestor of every later one."""
    tmp = tmp_path_factory.mktemp("wg")
    lines = ["jobs:"]
    for i, name in enumerate(chain):
        lines.append(f"  {name}:")
        if i:
            lines.append(f"    needs: [{chain[i - 1]}]")
        lines.append("    steps: [{run: echo}]")
    g = _graph("\n".join(lines) + "\n", tmp)

    for i, name in enumerate(chain):
        assert g.ancestors(name) == set(chain[:i])


@given(gated=st.booleans(), verified=st.booleans())
def test_property_deploy_needs_both_gate_and_verifier(gated, verified, tmp_path_factory):
    tmp = tmp_path_factory.mktemp("wg2")
    needs = "[preflight, ci-gate]" if gated else "[]"
    verifier = (
        "  verify-production:\n"
        "    needs: deploy\n"
        "    steps: [{run: python -m scripts.verify.deployment_check}]\n"
    ) if verified else ""
    text = (
        "jobs:\n"
        "  preflight:\n    steps: [{run: echo}]\n"
        "  ci-gate:\n    uses: ./.github/workflows/ci.yml\n"
        f"  deploy:\n    needs: {needs}\n"
        "    steps: [{uses: appleboy/ssh-action@v1}]\n"
        + verifier
    )
    report = Report()
    wg.check_graph(_graph(text, tmp), report)
    assert (report.exit_code() is Exit.OK) == (gated and verified)


_CI_JOBS = ("lint", "shared", "backend", "frontend")


@given(masked=st.sets(st.sampled_from(_CI_JOBS), max_size=4))
def test_property_every_mask_in_a_called_gate_is_reported(masked, tmp_path_factory):
    """Requirement 8.8 as a property: for any subset of the called workflow's
    jobs that mask a failure, the report names exactly that subset.

    Nothing about the rule may depend on which job, or how many: the defect was
    that the answer was always "none of them".

    **Validates: Requirements 8.8**
    """
    tmp = tmp_path_factory.mktemp("wg-crossfile")
    wf = tmp / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "deploy.yml").write_text(
        (FIXTURES / "crossfile_deploy.yml").read_text(encoding="utf-8"),
        encoding="utf-8")
    lines = ["on:\n  workflow_call:\n", "jobs:"]
    for job in _CI_JOBS:
        suffix = " || true" if job in masked else ""
        lines.append(f"  {job}:")
        lines.append(f"    steps: [{{run: make {job}{suffix}}}]")
    (wf / "ci.yml").write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = Report()
    wg.check_graph(wg.load_graph(wf / "deploy.yml"), report, require_staging=True)
    assert {f.observed for f in report.findings if f.rule == "masked-gate"} == {
        f"{job}: || true" for job in masked}


_HOSTS = st.sets(st.sampled_from(
    ["a.example.com", "b.example.com", "c.example.com", "d.example.com"]),
    max_size=4)


@given(staging=_HOSTS, production=_HOSTS)
def test_property_hostname_isolation_fails_iff_sets_overlap(staging, production):
    """Property 16, hostname clause: a finding exactly when a normalised
    hostname is shared, and the findings name exactly the shared hosts."""
    report = Report()
    wg.check_hostname_isolation(staging, production, report)
    assert bool(report.findings) == bool(staging & production)
    assert {f.observed for f in report.findings} == staging & production


_SERVICES = st.sets(st.sampled_from(["backend", "mongo", "postgres", "redis"]),
                    max_size=4)


@given(production=_SERVICES, staging=_SERVICES)
def test_property_service_parity_fails_iff_sets_differ(production, staging):
    """Property 16, shape clause: identical sets pass; any difference, in
    either direction, is a finding per differing service."""
    report = Report()
    wg.check_service_parity(production, staging, report)
    assert bool(report.findings) == (production != staging)
    assert len(report.findings) == len(production ^ staging)


@pytest.mark.parametrize("command", [
    "npx --yes firebase-tools@13 deploy --only hosting --project kailash-29111 --non-interactive",
    "npx --yes firebase-tools@13 deploy --only hosting:production --project kailash-29111 --non-interactive",
    "npx --yes firebase-tools@13 deploy --only hosting:staging --project kailash-29111 --non-interactive",
    "npx --yes firebase-tools@13 hosting:channel:deploy staging --expires 30d --project kailash-29111",
    "firebase deploy --only hosting",
])
def test_cli_deploy_forms_are_recognised_as_deploys(command):
    """The WIF rewrite swapped action-hosting-deploy for the firebase CLI via
    npx, where no whitespace follows the word `firebase`. A deploy the markers
    cannot see exits the gating set silently, which is the vacuous pass this
    whole check exists to prevent."""
    assert any(rx.search(command) for rx in wg.DEPLOY_MARKERS), command
