"""Tests for the harness the checks are tested through.

The harness gets its own tests for one reason: tasks 13.2, 13.4 and 7.3 prove a
destructive-operation guarantee by asserting a command was *never* issued. An
assertion that cannot observe the call passes whether or not the call happened,
so the harness would certify the guarantee while `docker rm` ran. That failure
is silent, which is the kind worth a test.
"""
from __future__ import annotations

import http.client
import json
import subprocess
from urllib.parse import urlsplit

import pytest

from . import conftest as harness
from .conftest import FakeExecutor, load_fixture, read_fixture


class TestFakeExecutorRecording:
    def test_records_args_and_kwargs_per_call(self, fake_executor):
        fake_executor(["docker", "ps", "-a"], capture_output=True, text=True)
        assert len(fake_executor.calls) == 1
        call = fake_executor.calls[0]
        assert call.args == (["docker", "ps", "-a"],)
        assert call.kwargs == {"capture_output": True, "text": True}

    def test_returns_scripted_exit_code_stdout_and_stderr(self, fake_executor):
        fake_executor.script("docker inspect kailash-backend", 1, "out", "err")
        result = fake_executor(["docker", "inspect", "kailash-backend"])
        assert (result.returncode, result.stdout, result.stderr) == (1, "out", "err")

    def test_unscripted_command_succeeds_silently(self, fake_executor):
        result = fake_executor(["git", "status", "--porcelain"])
        assert (result.returncode, result.stdout, result.stderr) == (0, "", "")

    def test_longest_matching_key_wins(self, fake_executor):
        """One entry scripts a family of per-container inspects; a more
        specific entry overrides it for a single container."""
        fake_executor.script("docker inspect", 0, "generic")
        fake_executor.script("docker inspect kailash-mongo", 1, "specific")
        assert fake_executor(["docker", "inspect", "kailash-rag"]).stdout == "generic"
        assert fake_executor(["docker", "inspect", "kailash-mongo"]).stdout == "specific"

    def test_check_true_raises_like_subprocess(self, fake_executor):
        """A collector written with check=True must fail under the fake too,
        or the fake hides the difference from the real thing."""
        fake_executor.script("docker exec kailash-mongo which mongosh", 1)
        with pytest.raises(subprocess.CalledProcessError):
            fake_executor(["docker", "exec", "kailash-mongo", "which", "mongosh"],
                          check=True)

    def test_check_true_does_not_raise_on_success(self, fake_executor):
        assert fake_executor(["docker", "ps"], check=True).returncode == 0


class TestFakeExecutorDestructiveAssertions:
    """`remove()` in the design calls `execute("docker", "rm", "-f", c)` --
    varargs, not a list. Both forms have to be equally visible."""

    LIST_FORM = (["docker", "rm", "-f", "nervous_dhawan"],)
    VARARG_FORM = ("docker", "rm", "-f", "nervous_dhawan")

    def test_no_call_means_assert_never_passes(self, fake_executor):
        fake_executor(["docker", "ps", "-a", "--format", "{{.Names}}"])
        fake_executor.assert_never("docker rm")

    @pytest.mark.parametrize("form", ["list", "varargs"])
    def test_assert_never_fails_when_the_command_was_issued(self, fake_executor, form):
        fake_executor(*(self.LIST_FORM if form == "list" else self.VARARG_FORM))
        assert fake_executor.called_with("docker rm")
        with pytest.raises(AssertionError, match="docker rm"):
            fake_executor.assert_never("docker rm")

    def test_both_call_forms_normalise_to_the_same_command(self, fake_executor):
        fake_executor(*self.LIST_FORM)
        fake_executor(*self.VARARG_FORM)
        assert fake_executor.commands() == ["docker rm -f nervous_dhawan"] * 2

    def test_matching_gives_exactly_the_targets_acted_on(self, fake_executor):
        """"Exactly the named containers" is a set equality, not a containment
        check, so the matcher has to return the calls rather than a boolean."""
        for name in ("log-reader", "gifted_leavitt"):
            fake_executor("docker", "rm", "-f", name)
        assert fake_executor.matching("docker rm") == [
            "docker rm -f log-reader",
            "docker rm -f gifted_leavitt",
        ]

    def test_fixture_is_a_fresh_recorder_per_test(self, fake_executor):
        assert isinstance(fake_executor, FakeExecutor)
        assert fake_executor.calls == []


class TestTmpRepo:
    def test_written_files_are_tracked(self, tmp_repo):
        """Every check reads its corpus from `git ls-files`, so an unstaged
        file is a file the check cannot see."""
        tmp_repo.write("frontend/src/lib/firebase.js", "// x\n")
        assert "frontend/src/lib/firebase.js" in tmp_repo.git("ls-files")

    def test_staging_can_be_declined(self, tmp_repo):
        tmp_repo.write("untracked.txt", "x\n", add=False)
        assert "untracked.txt" not in tmp_repo.git("ls-files")
        assert (tmp_repo.root / "untracked.txt").exists()

    def test_binary_writer_stages_too(self, tmp_repo):
        tmp_repo.write_bytes("blob.bin", b"\xff\xfe\x00")
        assert "blob.bin" in tmp_repo.git("ls-files")

    def test_shaped_writers_cover_the_four_firebase_sites(self, tmp_repo):
        tmp_repo.all_firebase_sites("kailash-38268")
        assert set(tmp_repo.git("ls-files").split()) == {
            "frontend/.firebaserc",
            "frontend/.env.production",
            "backend/.env.example",
            ".github/workflows/deploy-frontend.yml",
        }
        firebaserc = json.loads((tmp_repo.root / "frontend/.firebaserc").read_text())
        assert firebaserc["projects"]["default"] == "kailash-38268"

    def test_compose_and_deploy_script_writers(self, tmp_repo):
        tmp_repo.compose("services:\n  postgres: {}\n")
        tmp_repo.deploy_sh("https://github.com/urgaa-eka/kailash.git")
        tracked = tmp_repo.git("ls-files").split()
        assert "docker-compose.yml" in tracked
        assert "deploy/vultr/deploy.sh" in tracked

    def test_arbitrary_workflow_writer_appends_the_extension(self, tmp_repo):
        tmp_repo.workflow("ci", "jobs:\n  lint:\n    steps: []\n")
        assert ".github/workflows/ci.yml" in tmp_repo.git("ls-files")

    def test_commit_leaves_a_clean_tree(self, tmp_repo):
        tmp_repo.compose("services: {}\n")
        tmp_repo.commit()
        assert tmp_repo.git("status", "--porcelain").strip() == ""

    def test_each_test_gets_its_own_repository(self, tmp_repo):
        assert tmp_repo.git("ls-files").strip() == ""
        assert (tmp_repo.root / ".git").is_dir()


class TestLocalHttpServer:
    """Read with http.client rather than urlopen: urlopen follows redirects,
    which would turn the 301 case into a request for the Location host."""

    @staticmethod
    def _get(url):
        parts = urlsplit(url)
        conn = http.client.HTTPConnection(parts.hostname, parts.port, timeout=5)
        try:
            conn.request("GET", parts.path or "/")
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            conn.close()

    def test_serves_the_scripted_status_type_and_body(self, local_http_server):
        local_http_server.script(status=200, content_type="application/json",
                                 body='{"status":"ok"}')
        status, headers, body = self._get(local_http_server.url)
        assert status == 200
        assert headers["Content-Type"] == "application/json"
        assert body == b'{"status":"ok"}'

    def test_scripted_error_status_is_served_as_given(self, local_http_server):
        local_http_server.script(status=503, body="down")
        status, _, body = self._get(local_http_server.url)
        assert status == 503
        assert body == b"down"

    def test_redirect_sends_a_location_and_an_empty_body(self, local_http_server):
        """Content-Length has to match what is written or a client blocks
        waiting for a body that never arrives."""
        local_http_server.script(status=301)
        status, headers, body = self._get(local_http_server.url)
        assert status == 301
        assert headers["Location"]
        assert headers["Content-Length"] == "0" and body == b""

    def test_bound_to_loopback_on_an_ephemeral_port(self, local_http_server):
        parts = urlsplit(local_http_server.url)
        assert parts.hostname == "127.0.0.1"
        assert parts.port > 1024


class TestMarkerSkipping:
    def test_docker_and_network_markers_are_registered(self, pytestconfig):
        """An unregistered marker is a typo away from silently selecting
        nothing, which would let the docker suite run with no daemon."""
        declared = " ".join(pytestconfig.getini("markers"))
        assert "docker:" in declared and "network:" in declared

    def test_prerequisite_probe_detects_absence(self):
        assert harness._have("git")
        assert not harness._have("no-such-binary-on-this-path-42")

    @pytest.mark.docker
    def test_docker_marked_test_is_gated_by_the_autouse_skip(self, request):
        """Reached only when docker is on PATH; skipped otherwise, which is
        what keeps the unit suite runnable anywhere."""
        assert request.node.get_closest_marker("docker") is not None

    @pytest.mark.network
    def test_network_marked_test_is_gated_by_the_autouse_skip(self, request):
        assert request.node.get_closest_marker("network") is not None


class TestFixtureCorpus:
    CAPTURES = [
        "inspect_healthy.json",
        "inspect_unhealthy_serves_200.json",
        "inspect_executable_absent.json",
        "inspect_replay_succeeds.json",
        "inspect_connection_refused.json",
        "inspect_http_error_traceback.json",
        "inspect_no_healthcheck.json",
    ]
    GRAPHS = [
        "gated.yml",
        "missing_needs.yml",
        "masked_gate.yml",
        "production_before_staging.yml",
        "deploy_without_verify.yml",
        "cycle.yml",
        "orphan.yml",
    ]

    @pytest.mark.parametrize("name", CAPTURES)
    def test_capture_parses_and_carries_the_phase_a_keys(self, name):
        captured = load_fixture(name)
        assert {"name", "health", "effective", "state", "restarts"} <= set(captured)

    def test_malformed_capture_does_not_parse(self):
        """The classifier has to preserve a truncated capture as evidence
        rather than raise on it, so the corpus needs one that cannot parse."""
        with pytest.raises(json.JSONDecodeError):
            load_fixture("inspect_truncated.json")
        assert read_fixture("inspect_truncated.json").strip()

    def test_no_healthcheck_capture_declares_no_probe(self):
        captured = load_fixture("inspect_no_healthcheck.json")
        assert captured["effective"] is None and captured["health"] is None

    @pytest.mark.parametrize("name", GRAPHS)
    def test_synthetic_workflow_graphs_are_present_and_non_empty(self, name, fixtures_dir):
        body = (fixtures_dir / "workflows" / name).read_text(encoding="utf-8")
        assert "jobs:" in body
