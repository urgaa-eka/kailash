"""Deployment verification: status, content type, asset containment, cert margin."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scripts.verify import deployment_check as dc
from scripts.verify.common import Exit, Report


def _endpoint(url, statuses=(200,), ctype=None, assets=False):
    return dc.Endpoint(url, statuses, ctype, check_certificate=False, parse_assets=assets)


class TestEnvironmentTables:
    def test_both_environments_defined(self):
        assert set(dc.ENVIRONMENTS) == {"production", "staging"}

    def test_corresponding_endpoints_share_allowed_sets(self):
        """One check with two tables is how staging and production stay in
        step by construction, rather than by a parallel implementation that
        drifts."""
        prod, stag = dc.ENVIRONMENTS["production"], dc.ENVIRONMENTS["staging"]
        assert len(prod) == len(stag)
        for p, s in zip(prod, stag):
            assert p.allowed_statuses == s.allowed_statuses
            assert p.content_type == s.content_type

    def test_redirects_are_not_followed(self):
        """Following a redirect would let a 301 to an unrelated host pass as
        200 -- not hypothetical: kailash-ai.in 301s to another domain."""
        assert dc._NoRedirect().redirect_request(None, None, 301, "", {}, "x") is None


class TestStatusAndContentType:
    def test_expected_status_passes(self, local_http_server):
        local_http_server.script(status=200, content_type="text/html")
        report = Report()
        dc.check_endpoint(_endpoint(local_http_server.url, (200,), "text/html"), report, None)
        assert report.exit_code() is Exit.OK

    def test_unexpected_status_reports_url_and_code(self, local_http_server):
        local_http_server.script(status=500)
        report = Report()
        dc.check_endpoint(_endpoint(local_http_server.url, (200,)), report, None)
        assert report.exit_code() is Exit.FAILED
        rendered = report.render()
        assert local_http_server.url in rendered and "500" in rendered

    def test_redirect_within_allowed_set_passes(self, local_http_server):
        local_http_server.script(status=301)
        report = Report()
        dc.check_endpoint(_endpoint(local_http_server.url, (200, 301, 308)), report, None)
        assert report.exit_code() is Exit.OK

    def test_wrong_content_type_reports(self, local_http_server):
        local_http_server.script(status=200, content_type="application/json")
        report = Report()
        dc.check_endpoint(_endpoint(local_http_server.url, (200,), "text/html"), report, None)
        assert report.exit_code() is Exit.FAILED
        assert "content-type" in report.render()

    def test_unreachable_is_unavailable_not_failed(self):
        """A runner that lost egress is a different event from production
        being down. Conflating them trains people to ignore the check."""
        report = Report()
        dc.check_endpoint(_endpoint("http://127.0.0.1:1/"), report, None)
        assert report.exit_code() is Exit.UNAVAILABLE
        assert not report.findings


class TestAssetManifest:
    HTML = ('<html><script src="/static/js/main.448921c0.js"></script>'
            '<link href="/static/css/main.3ad437bc.css"></html>')

    def test_containment_passes(self, local_http_server):
        local_http_server.script(body=self.HTML)
        manifest = {"files": {
            "main.js": "/static/js/main.448921c0.js",
            "main.css": "/static/css/main.3ad437bc.css",
        }}
        report = Report()
        dc.check_endpoint(_endpoint(local_http_server.url, (200,), assets=True),
                          report, manifest)
        assert report.exit_code() is Exit.OK

    def test_manifest_superset_passes(self, local_http_server):
        """Lazy chunks and source maps are listed but never referenced by the
        entry HTML, so equality would fail every code-split build."""
        local_http_server.script(body=self.HTML)
        manifest = {"files": {
            "main.js": "/static/js/main.448921c0.js",
            "main.css": "/static/css/main.3ad437bc.css",
            "lazy.js": "/static/js/lazy.deadbeef12.js",
        }}
        report = Report()
        dc.check_endpoint(_endpoint(local_http_server.url, (200,), assets=True),
                          report, manifest)
        assert report.exit_code() is Exit.OK

    def test_served_asset_absent_from_manifest_fails(self, local_http_server):
        local_http_server.script(body=self.HTML)
        manifest = {"files": {"main.css": "/static/css/main.3ad437bc.css"}}
        report = Report()
        dc.check_endpoint(_endpoint(local_http_server.url, (200,), assets=True),
                          report, manifest)
        assert report.exit_code() is Exit.FAILED
        assert "main.448921c0.js" in report.render()

    def test_asset_extraction_ignores_unhashed(self):
        found = dc.assets_in_html('<script src="/static/js/vendor.js"></script>')
        assert found == set()


class TestCertificateMargin:
    def test_days_until_is_pure_and_testable(self):
        now = datetime(2026, 1, 1, tzinfo=UTC)
        assert dc.days_until("Feb  1 00:00:00 2026 GMT", now=now) == 31

    @pytest.mark.parametrize("days,expect_finding", [
        (30, False), (15, False), (14, False), (13, True), (0, True), (-1, True),
    ])
    def test_boundary(self, days, expect_finding):
        now = datetime(2026, 1, 1, tzinfo=UTC)
        expiry = now + timedelta(days=days, hours=1)
        not_after = expiry.strftime("%b %d %H:%M:%S %Y GMT")
        remaining = dc.days_until(not_after, now=now)
        assert (remaining < dc.CERT_MIN_DAYS) is expect_finding


@given(
    observed=st.integers(min_value=100, max_value=599),
    allowed=st.lists(st.integers(min_value=100, max_value=599),
                     min_size=1, max_size=4, unique=True),
)
def test_property_status_pass_iff_in_allowed_set(observed, allowed):
    report = Report()
    ep = _endpoint("http://x/", tuple(allowed))
    if observed not in ep.allowed_statuses:
        report.add(__import__("scripts.verify.common", fromlist=["Finding"]).Finding(
            rule="status", path=ep.url, observed=observed, expected=list(allowed)))
    assert (report.exit_code() is Exit.OK) == (observed in allowed)


@given(
    served=st.sets(st.sampled_from(["a.11111111.js", "b.22222222.js", "c.33333333.css"])),
    extra=st.sets(st.sampled_from(["d.44444444.js", "e.55555555.css"])),
)
def test_property_containment_not_equality(served, extra):
    manifest = {"files": {f"k{i}": f"/static/{n}" for i, n in enumerate(served | extra)}}
    known = dc.assets_in_manifest(manifest)
    assert served <= known


@given(days=st.integers(min_value=-400, max_value=400))
def test_property_certificate_margin(days):
    now = datetime(2026, 6, 1, tzinfo=UTC)
    expiry = now + timedelta(days=days, hours=1)
    remaining = dc.days_until(expiry.strftime("%b %d %H:%M:%S %Y GMT"), now=now)
    assert remaining == days
