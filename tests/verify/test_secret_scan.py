"""Secret scanning: four detectors, one narrow exemption."""
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
        tmp_repo.write("a.txt", "line one\nline two\nPASSWORD_WAS=kailash_prod_2026\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "a.txt:3" in out

    def test_denylist_applies_to_lockfiles(self, tmp_repo, capsys):
        """Lockfiles are exempt from the heuristics, never from the denylist."""
        tmp_repo.write("yarn.lock", "# yarn\nkailash_redis_2026\n")
        rc, out = _run(tmp_repo.root, capsys)
        assert rc == int(Exit.FAILED)
        assert "yarn.lock:2" in out

    def test_value_is_not_echoed_in_full(self, tmp_repo, capsys):
        """Reporting a leak by reprinting it makes the log a second copy."""
        tmp_repo.write("a.txt", "kailash_prod_2026\n")
        _, out = _run(tmp_repo.root, capsys)
        assert "kailash_prod_2026" not in out


class TestStructuredPatterns:
    @pytest.mark.parametrize("payload,rule", [
        ("-----BEGIN RSA PRIVATE KEY-----", "private-key-block"),
        ("AIzaSyDD70yOW6vheOK2OPzNXT0b0R5B9ZXI1ho", "google-api-key"),
        ("ghp_" + "a" * 36, "github-token"),
        ("AKIAIOSFODNN7EXAMPLE", "aws-access-key"),
        ("xoxb-123-abc", "slack-token"),
        ('"type": "service_account"', "gcp-service-account"),
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
        tmp_repo.write("s.py", 'API_KEY = "sk-live-abcdef123456"\n')
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
    """Both conditions, never either alone."""

    @pytest.mark.parametrize("path,value,should_pass", [
        ("backend/.env.example", "changeme", True),
        ("backend/.env.example", "<your-password>", True),
        ("backend/.env.example", "your-secret-here", True),
        ("backend/.env.example", "hunter2hunter2", False),   # real value in an example
        ("backend/config.py", "changeme", False),            # placeholder outside one
        ("backend/config.py", "hunter2hunter2", False),
    ])
    def test_matrix(self, tmp_repo, capsys, path, value, should_pass):
        tmp_repo.write(path, f'API_KEY = "{value}"\n')
        rc, out = _run(tmp_repo.root, capsys)
        assert (rc == int(Exit.OK)) is should_pass, out


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
