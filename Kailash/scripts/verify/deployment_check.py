"""Verify a deployed environment actually serves the build that was deployed.

Three rules:

1. Status and content type per endpoint, without following redirects.
   Following them would let a 301 to an unrelated host pass as 200. That
   matters most for the two apex domains: both are expected to serve the SPA
   themselves, and if one were reconfigured to bounce to the other, a
   redirect-following client would report 200 `text/html` for a host that
   serves nothing. Refusing to follow is what lets this check tell "serves the
   SPA" from "redirects to something that does".
2. Asset-manifest containment: every hashed asset the served HTML references
   must appear in the manifest from the deploying build. Containment, not
   equality -- the manifest legitimately lists lazy chunks the entry HTML
   never references.
3. Certificate margin, reported as days remaining rather than a bare pass, so
   the output is useful before it is failing.

DNS and connection failures are UNAVAILABLE, not FAILED. A pipeline that went
red because the runner lost egress is a different event from production being
down, and conflating them trains people to ignore the check.
"""
from __future__ import annotations

import json
import re
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .common import Finding, Report, Usage, base_parser, run

CERT_MIN_DAYS = 14

# CRA emits `main.<8+ hex>.js`; this is the shape to look for in the HTML.
HASHED_ASSET = re.compile(r"""["'](?P<path>[^"']*\.[0-9a-f]{8,}\.(?:js|css))["']""")


@dataclass(frozen=True)
class Endpoint:
    url: str
    allowed_statuses: tuple[int, ...]
    content_type: str | None = None
    check_certificate: bool = False
    parse_assets: bool = False
    # What this host is for, not which host it is. Production has two apexes
    # and staging one, so the "staging is verified by the same rules as
    # production" obligation (Requirement 8.6) is expressed per role rather
    # than by pairing the two tables position by position.
    role: str = "apex"


# Both apex domains are owned by the operator and both are synced to serve the
# same site, so both are production and both are verified: `kailash-ai.in` (the
# domain Requirements 2.1/2.2 name, and the one baked into the bundle as
# REACT_APP_DOMAIN) and `kailash-ai.com` (observed serving the SPA from
# Firebase Hosting on 2026-08-01). Neither is a redirect to the other; a host
# that only bounced would fail its `text/html` assertion here, which is the
# point.
#
# The API hostname is `.in` only. `api.kailash-ai.com` has never resolved and
# nothing in the repository references it, so adding it would assert an
# intention no file declares. The shipped bundle calls `api.kailash-ai.in`
# (frontend/.env.production REACT_APP_BACKEND_URL), and that is the single API
# origin. Evidence and the operator actions this implies:
# docs/records/production-domain.md.
ENVIRONMENTS: dict[str, tuple[Endpoint, ...]] = {
    "production": (
        Endpoint("https://kailash-ai.in/", (200,), "text/html",
                 check_certificate=True, parse_assets=True, role="apex"),
        Endpoint("https://kailash-ai.com/", (200,), "text/html",
                 check_certificate=True, parse_assets=True, role="apex"),
        Endpoint("https://www.kailash-ai.in/", (200, 301, 308),
                 check_certificate=True, role="www"),
        Endpoint("https://www.kailash-ai.com/", (200, 301, 308),
                 check_certificate=True, role="www"),
        Endpoint("https://api.kailash-ai.in/api/health", (200,),
                 check_certificate=True, role="api"),
    ),
    "staging": (
        Endpoint("https://staging.kailash-ai.com/", (200,), "text/html",
                 check_certificate=True, parse_assets=True, role="apex"),
        Endpoint("https://www.staging.kailash-ai.com/", (200, 301, 308),
                 check_certificate=True, role="www"),
        Endpoint("https://staging-api.kailash-ai.in/api/health", (200,),
                 check_certificate=True, role="api"),
    ),
}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url: str, timeout: float = 15.0) -> tuple[int, str, str]:
    """(status, content_type, body). Redirects are surfaced, never followed."""
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, resp.headers.get("Content-Type", ""), body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return exc.code, exc.headers.get("Content-Type", "") if exc.headers else "", body


def certificate_days_remaining(host: str, port: int = 443,
                               now: datetime | None = None) -> int:
    ctx = ssl.create_default_context()
    with (
        socket.create_connection((host, port), timeout=15) as sock,
        ctx.wrap_socket(sock, server_hostname=host) as tls,
    ):
        cert = tls.getpeercert()
    return days_until(cert["notAfter"], now=now)


def days_until(not_after: str, now: datetime | None = None) -> int:
    """Days from `now` to an OpenSSL `notAfter` string. Pure, so it is testable."""
    expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(
        tzinfo=UTC)
    reference = now or datetime.now(UTC)
    return (expiry - reference).days


def assets_in_html(html: str) -> set[str]:
    return {Path(m.group("path")).name for m in HASHED_ASSET.finditer(html)}


def assets_in_manifest(manifest: dict) -> set[str]:
    """Every asset filename the manifest knows about, from either CRA shape."""
    names: set[str] = set()
    files = manifest.get("files")
    if isinstance(files, dict):
        names.update(Path(v).name for v in files.values() if isinstance(v, str))
    entrypoints = manifest.get("entrypoints")
    if isinstance(entrypoints, list):
        names.update(Path(v).name for v in entrypoints if isinstance(v, str))
    if not names:  # a bare {name: path} mapping
        names.update(Path(v).name for v in manifest.values() if isinstance(v, str))
    return names


def check_endpoint(ep: Endpoint, report: Report, manifest: dict | None) -> None:
    host = urllib.parse.urlparse(ep.url).hostname or ""

    try:
        status, ctype, body = fetch(ep.url)
    except (TimeoutError, urllib.error.URLError, socket.gaierror, OSError) as exc:
        # Cannot reach it. That is not evidence the deployment is wrong.
        report.unavailable.append(f"{ep.url} unreachable: {exc}")
        return

    if status not in ep.allowed_statuses:
        report.add(Finding(rule="status", path=ep.url, observed=status,
                           expected=list(ep.allowed_statuses)))

    if ep.content_type and ep.content_type not in ctype:
        report.add(Finding(rule="content-type", path=ep.url, observed=ctype or "<none>",
                           expected=ep.content_type))

    if ep.parse_assets and manifest is not None:
        served = assets_in_html(body)
        known = assets_in_manifest(manifest)
        missing = sorted(served - known)
        if missing:
            report.add(Finding(
                rule="asset-manifest", path=ep.url, observed=missing,
                expected="all served assets present in asset-manifest.json",
                message="the served build is not the build that was deployed",
            ))

    if ep.check_certificate:
        try:
            remaining = certificate_days_remaining(host)
        except (TimeoutError, socket.gaierror, ssl.SSLError, OSError) as exc:
            report.unavailable.append(f"{host} certificate unreadable: {exc}")
            return
        report.notes.append(f"{host} certificate expires in {remaining} day(s)")
        if remaining < CERT_MIN_DAYS:
            report.add(Finding(rule="certificate-margin", path=host,
                               observed=f"{remaining}d", expected=f">={CERT_MIN_DAYS}d"))


def build_report(args) -> Report:
    if args.env not in ENVIRONMENTS:
        raise Usage(f"--env must be one of {sorted(ENVIRONMENTS)}")

    manifest = None
    if args.manifest:
        try:
            manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise Usage(f"--manifest {args.manifest} unreadable: {exc}") from exc

    report = Report()
    if manifest is None:
        report.notes.append("no --manifest given; asset containment not checked")
    for ep in ENVIRONMENTS[args.env]:
        check_endpoint(ep, report, manifest)
    return report


def main(argv=None) -> int:
    parser = base_parser("Verify a deployed environment serves the current build.")
    parser.add_argument("--env", required=True, choices=sorted(ENVIRONMENTS))
    parser.add_argument("--manifest", type=Path, default=None,
                        help="asset-manifest.json from the deploying build")
    return run(build_report, argv, parser)


if __name__ == "__main__":
    raise SystemExit(main())
