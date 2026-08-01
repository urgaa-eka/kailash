"""Secret scanning: four detectors, one narrow exemption.

This file necessarily contains the shapes it tests -- a scanner whose test
corpus avoided them would be testing nothing. Each is suppressed with a
reason, which also exercises the suppression mechanism on real input.
"""
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scripts.verify import secret_scan
from scripts.verify.common import Exit


def _run(root, capsys) -> tuple[int, str]:
    rc = secret_scan.main(["--root", str(root)])
    return rc, capsys.readouterr().out


class TestDenylist:
    def test_known_literal_is_found_at_the_right_line(self, tmp_repo, capsys):
        tmp_repo.write("a.txt", "line one\nline two\nPASSWORD_WAS=kailash_prod_2026\n")  # secret-scan: allow test corpus for the denylist detector
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "a.txt:3" in out

    def test_denylist_applies_to_lockfiles(self, tmp_repo, capsys):
        """Lockfiles are exempt from the heuristics, never from the denylist."""
        tmp_repo.write("yarn.lock", "# yarn\nkailash_redis_2026\n")  # secret-scan: allow test corpus for the denylist detector
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "yarn.lock:2" in out

    def test_value_is_not_echoed_in_full(self, tmp_repo, capsys):
        """Reporting a leak by reprinting it makes the log a second copy."""
        tmp_repo.write("a.txt", "kailash_prod_2026\n")  # secret-scan: allow test corpus for the denylist detector
        _, out = _run(tmp_repo.root, capsys)
        assert "kailash_prod_2026" not in out  # secret-scan: allow test corpus for the denylist detector


class TestStructuredPatterns:
    @pytest.mark.parametrize("payload,rule", [
        ("-----BEGIN RSA PRIVATE KEY-----", "private-key-block"),  # secret-scan: allow test corpus for the private-key-block detector
        ("AIzaSyDD70yOW6vheOK2OPzNXT0b0R5B9ZXI1ho", "google-api-key"),  # secret-scan: allow test corpus for the google-api-key detector
        ("ghp_" + "a" * 36, "github-token"),
        ("AKIAIOSFODNN7EXAMPLE", "aws-access-key"),  # secret-scan: allow test corpus for the aws-access-key detector
        ("xoxb-123-abc", "slack-token"),  # secret-scan: allow test corpus for the slack-token detector
        ('"type": "service_account"', "gcp-service-account"),  # secret-scan: allow test corpus for the gcp-service-account detector
    ])
    def test_each_shape_fires(self, tmp_repo, capsys, payload, rule):
        tmp_repo.write("f.txt", f"prefix\n{payload}\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert rule in out and "f.txt:2" in out

    def test_lockfiles_exempt_from_structured(self, tmp_repo, capsys):
        tmp_repo.write("package-lock.json", '{"integrity":"AIza' + "b" * 35 + '"}\n')
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)


class TestAssignmentHeuristic:
    def test_literal_secret_fires(self, tmp_repo, capsys):
        tmp_repo.write("s.py", 'API_KEY = "sk-live-abcdef123456"\n')  # secret-scan: allow test corpus for the assignment detector
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "assignment" in out

    @pytest.mark.parametrize("line", [
        'PASSWORD = os.environ.get("PASSWORD")',
        'DB_PASSWORD="${POSTGRES_PASSWORD}"',
        "token: ${{ secrets.GITHUB_TOKEN }}",
        'API_KEY = process.env.API_KEY',
    ])
    def test_environment_references_do_not_fire(self, tmp_repo, capsys, line):
        """A password-shaped name pointing at an environment variable is the
        absence of a secret, not the presence of one."""
        tmp_repo.write("s.py", line + "\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out

    def test_short_value_does_not_fire(self, tmp_repo, capsys):
        tmp_repo.write("s.py", 'SECRET = "abc"\n')
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)


class TestPlaceholderMatrix:
    """The exemption needs both conditions; the failure needs only one.

    The security property runs one way: a real credential in a `.env.example`
    is a finding. A placeholder outside one is reported as a note, not a
    failure -- it is nearly always documentation showing a reader what to
    type, and failing on those makes the check unusable in any repository
    that has docs. An unusable check gets weakened, which costs more than the
    noise it saves.
    """

    @pytest.mark.parametrize("path,value,should_pass", [
        ("backend/.env.example", "changeme", True),
        ("backend/.env.example", "<your-password>", True),
        ("backend/.env.example", "your-secret-here", True),
        ("backend/.env.example", "hunter2hunter2", False),   # real value in an example
        ("backend/config.py", "changeme", True),             # note, not a finding
        ("backend/config.py", "hunter2hunter2", False),      # real value anywhere
    ])
    def test_matrix(self, tmp_repo, capsys, path, value, should_pass):
        tmp_repo.write(path, f'API_KEY = "{value}"\n')
        rc, out = _run(tmp_repo.root, capsys)
        assert (rc == int(Exit.OK)) is should_pass, out

    def test_placeholder_outside_example_is_still_reported(self, tmp_repo, capsys):
        """Reported, so it is visible -- just not a build failure."""
        tmp_repo.write("backend/config.py", 'API_KEY = "changeme"\n')
        _, out = _run(tmp_repo.root, capsys)
        assert "placeholder outside" in out


class TestSuppression:
    def test_same_line_suppresses_and_is_counted(self, tmp_repo, capsys):
        tmp_repo.write("f.txt", 'K = "kailash_prod_2026"  # secret-scan: allow historical\n')
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)
        assert "1 suppression(s) in force" in out
        assert "historical" in out

    def test_preceding_line_suppresses(self, tmp_repo, capsys):
        tmp_repo.write("f.txt", "# secret-scan: allow documented defect\nkailash_redis_2026\n")
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)

    def test_html_comment_form_works_for_markdown(self, tmp_repo, capsys):
        tmp_repo.write("d.md", "<!-- secret-scan: allow describes the incident -->\n"
                               "The old password was kailash_prod_2026.\n")
        rc, _ = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK)


class TestComposeStrictness:
    def test_default_on_strict_var_fires(self, tmp_repo, capsys):
        tmp_repo.compose("services:\n  db:\n    environment:\n"
                         "      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-hunter2}\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "compose-strictness" in out

    def test_strict_form_passes(self, tmp_repo, capsys):
        tmp_repo.compose("services:\n  db:\n    environment:\n"
                         "      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?must be set}\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.OK), out


@given(secret=st.text(alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd")),
                      min_size=8, max_size=40))
def test_property_literal_assignment_always_fires(secret):
    """Any credential-shaped key assigned a non-placeholder literal of at
    least 8 characters is reported.

    scan_file is pure over (path, text), so no repository is built here --
    `git init` per generated example costs ~600ms and blows the deadline."""
    from scripts.verify.common import Report
    report = Report()
    secret_scan.scan_file("s.py", f'API_KEY = "{secret}"\n', [], report)

    is_placeholder = bool(secret_scan.PLACEHOLDER.match(secret.strip()))
    assert bool(report.findings) or is_placeholder


@given(name=st.sampled_from(["PASSWORD", "API_KEY", "SECRET", "DB_TOKEN",
                             "PRIVATE_KEY", "AWS_CREDENTIAL"]),
       ref=st.sampled_from(["${VAR}", "os.environ['X']", "process.env.X",
                            "${{ secrets.X }}", "os.getenv('X')"]))
def test_property_environment_references_never_fire(name, ref):
    """The absence of a secret must never be reported as one, or the check
    gets muted."""
    from scripts.verify.common import Report
    report = Report()
    secret_scan.scan_file("s.py", f"{name} = {ref}\n", [], report)
    assert not report.findings
