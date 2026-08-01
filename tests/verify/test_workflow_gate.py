"""Workflow topology, over synthetic graphs.

Deliberately not asserted against the real workflow files: spec task 12.9 does
that once the staging jobs exist. Asserting now would fail for work that has
not been scheduled, and a check that is red for a known reason gets ignored.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scripts.verify import workflow_gate as wg
from scripts.verify.common import Exit, Report

FIXTURES = Path(__file__).parent / "fixtures" / "workflows"


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
        """Those jobs do not exist yet. Requiring them now would make the
        check red for unscheduled work, and a check that is red for a known
        reason stops being read."""
        report = _check(GOOD, tmp_path)
        assert report.exit_code() is Exit.OK


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
