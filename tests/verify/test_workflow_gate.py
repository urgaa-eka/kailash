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
