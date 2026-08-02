"""Deployment verification: status, content type, asset containment, cert margin."""
from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scripts.verify import deployment_check as dc
from scripts.verify.common import Exit, Report


def _endpoint(url, statuses=(200,), ctype=None, assets=False, role="apex"):
    return dc.Endpoint(url, statuses, ctype, check_certificate=False,
                       parse_assets=assets, role=role)


def _roles(env: str) -> dict[str, list[dc.Endpoint]]:
    out: dict[str, list[dc.Endpoint]] = {}
    for ep in dc.ENVIRONMENTS[env]:
        out.setdefault(ep.role, []).append(ep)
    return out


class TestEnvironmentTables:
    def test_both_environments_defined(self):
        assert set(dc.ENVIRONMENTS) == {"production", "staging"}

    def test_corresponding_roles_share_allowed_sets(self):
        """One check with two tables is how staging and production stay in
        step by construction, rather than by a parallel implementation that
        drifts.

        Compared by role, not by position: production has two apex domains and
        staging one, so a positional pairing would have to be loosened the
        moment a second production domain was verified -- which is exactly the
        change that prompted this."""
        prod, stag = _roles("production"), _roles("staging")
        assert set(prod) == set(stag) == {"apex", "www", "api"}
        for role in prod:
            for p in prod[role]:
                for s in stag[role]:
                    assert p.allowed_statuses == s.allowed_statuses
                    assert p.content_type == s.content_type
                    assert p.parse_assets == s.parse_assets

    def test_redirects_are_not_followed(self):
        """Following a redirect would let a 301 to an unrelated host pass as
        200. With two apexes serving the same site that is the load-bearing
        case: an apex reconfigured to bounce to the other would look healthy to
        a redirect-following client while serving nothing itself."""
        assert dc._NoRedirect().redirect_request(None, None, 301, "", {}, "x") is None

    def test_both_apex_domains_are_verified_as_serving_the_spa(self):
        """Both domains are owned and both are synced to the same site, so
        neither is a redirect to the other and both must serve the SPA
        themselves. Recorded in docs/records/production-domain.md; change that
        record before this table."""
        apex = {ep.url: ep for ep in _roles("production")["apex"]}
        assert set(apex) == {"https://kailash-ai.in/", "https://kailash-ai.com/"}
        for ep in apex.values():
            assert ep.allowed_statuses == (200,)
            assert ep.content_type == "text/html"
            # The served build is checked against the deploying manifest on
            # both, because "both serve the same site" is an assertion about
            # the build, not only about the status code.
            assert ep.parse_assets

    def test_both_www_hosts_are_verified(self):
        www = {ep.url for ep in _roles("production")["www"]}
        assert www == {"https://www.kailash-ai.in/", "https://www.kailash-ai.com/"}

    def test_api_host_is_the_one_the_bundle_calls(self):
        """`api.kailash-ai.com` has never resolved and no file references it.
        Verifying it would assert an intention nothing declares."""
        api = [ep.url for ep in _roles("production")["api"]]
        assert api == ["https://api.kailash-ai.in/api/health"]
        assert not any("api.kailash-ai.com" in ep.url
                       for ep in dc.ENVIRONMENTS["production"])

    def test_every_verified_hostname_has_a_certificate_check(self):
        """Requirement 2.5. A host verified for status but not for expiry is a
        host that will silently break on a lapsed certificate."""
        for env in dc.ENVIRONMENTS.values():
            for ep in env:
                assert ep.check_certificate, ep.url

    def test_no_production_host_is_verified_twice(self):
        urls = [ep.url for ep in dc.ENVIRONMENTS["production"]]
        assert len(urls) == len(set(urls))


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


class TestProductionTableAgainstALocalServer:
    """The real production entries, aimed at a scripted local server.

    Exercising `dc.ENVIRONMENTS["production"]` itself rather than hand-built
    look-alikes: a rule that holds for a copy of the table proves nothing about
    the table that ships.
    """

    @staticmethod
    def _aimed(ep, url):
        return replace(ep, url=url, check_certificate=False)

    @pytest.mark.parametrize("url", ["https://kailash-ai.in/", "https://kailash-ai.com/"])
    def test_apex_serving_html_passes(self, url, local_http_server):
        ep = next(e for e in dc.ENVIRONMENTS["production"] if e.url == url)
        local_http_server.script(status=200, content_type="text/html; charset=utf-8")
        report = Report()
        dc.check_endpoint(self._aimed(ep, local_http_server.url), report, None)
        assert report.exit_code() is Exit.OK, report.render()

    @pytest.mark.parametrize("url", ["https://kailash-ai.in/", "https://kailash-ai.com/"])
    def test_apex_that_only_redirects_fails(self, url, local_http_server):
        """Both domains are synced to the same site. One of them answering with
        a bounce to the other means half the operator's traffic reaches a host
        that serves nothing -- so 301 is a finding here, not a pass."""
        ep = next(e for e in dc.ENVIRONMENTS["production"] if e.url == url)
        local_http_server.script(status=301)
        report = Report()
        dc.check_endpoint(self._aimed(ep, local_http_server.url), report, None)
        assert report.exit_code() is Exit.FAILED
        assert "301" in report.render()

    @pytest.mark.parametrize("url", ["https://www.kailash-ai.in/",
                                     "https://www.kailash-ai.com/"])
    @pytest.mark.parametrize("status", [200, 301, 308])
    def test_www_may_serve_or_redirect(self, url, status, local_http_server):
        ep = next(e for e in dc.ENVIRONMENTS["production"] if e.url == url)
        local_http_server.script(status=status)
        report = Report()
        dc.check_endpoint(self._aimed(ep, local_http_server.url), report, None)
        assert report.exit_code() is Exit.OK, report.render()

    def test_api_health_must_be_200(self, local_http_server):
        ep = next(e for e in dc.ENVIRONMENTS["production"]
                  if e.url.endswith("/api/health"))
        local_http_server.script(status=503, content_type="application/json",
                                 body='{"status":"down"}')
        report = Report()
        dc.check_endpoint(self._aimed(ep, local_http_server.url), report, None)
        assert report.exit_code() is Exit.FAILED
        assert "503" in report.render()

    def test_apex_serving_a_foreign_build_fails_on_both_domains(self, local_http_server):
        """The two apexes are synced, so the manifest containment rule applies
        to each of them independently: a stale copy on one is exactly the
        split-brain this catches."""
        local_http_server.script(
            body='<html><script src="/static/js/main.deadbeef99.js"></script></html>')
        manifest = {"files": {"main.js": "/static/js/main.448921c0.js"}}
        for ep in _roles("production")["apex"]:
            report = Report()
            dc.check_endpoint(self._aimed(ep, local_http_server.url), report, manifest)
            assert report.exit_code() is Exit.FAILED
            assert "main.deadbeef99.js" in report.render()


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
