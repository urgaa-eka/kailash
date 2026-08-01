"""Harness the verification checks are tested through.

The point of `tmp_repo` is that every check reads its corpus from `git
ls-files`, so a test that writes a file without staging it is testing nothing.
The fixture stages by default.
"""
from __future__ import annotations

import http.server
import json
import shutil
import socket
import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "docker: needs a docker daemon")
    config.addinivalue_line("markers", "network: needs outbound network")


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


@pytest.fixture(autouse=True)
def _skip_when_prerequisite_absent(request):
    """Keep the unit suite runnable anywhere.

    A suite that cannot run without a docker daemon is a suite that stops being
    run, and a check nobody runs is not a gate.
    """
    if request.node.get_closest_marker("docker") and not _have("docker"):
        pytest.skip("docker not available")
    if request.node.get_closest_marker("network"):
        try:
            socket.create_connection(("1.1.1.1", 443), timeout=2).close()
        except OSError:
            pytest.skip("no outbound network")


class Repo:
    """A throwaway git repository with helpers for the files checks read."""

    def __init__(self, root: Path):
        self.root = root

    def write(self, rel: str, content: str, *, add: bool = True) -> Path:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        if add:
            self.git("add", "--", rel)
        return p

    def write_bytes(self, rel: str, data: bytes, *, add: bool = True) -> Path:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        if add:
            self.git("add", "--", rel)
        return p

    def git(self, *args: str) -> str:
        out = subprocess.run(["git", *args], cwd=self.root,
                             capture_output=True, text=True, check=False)
        return out.stdout

    def commit(self, message: str = "wip") -> None:
        self.git("commit", "-q", "-m", message)

    # ---- shaped writers for the files the checks actually read -------------

    def firebaserc(self, project: str) -> None:
        self.write("frontend/.firebaserc",
                   json.dumps({"projects": {"default": project,
                                            "production": project}}, indent=2))

    def env_production(self, project: str, extra: str = "") -> None:
        self.write("frontend/.env.production",
                   f"REACT_APP_FIREBASE_PROJECT_ID={project}\n{extra}")

    def backend_env_example(self, project: str) -> None:
        self.write("backend/.env.example", f"FIREBASE_PROJECT_ID={project}\n")

    def deploy_workflow(self, project: str) -> None:
        self.write(".github/workflows/deploy-frontend.yml",
                   "jobs:\n  d:\n    steps:\n"
                   "      - uses: FirebaseExtended/action-hosting-deploy@v0\n"
                   "        with:\n"
                   "          channelId: live\n"
                   f"          projectId: {project}\n")

    def firebase_js(self, project: str, app_id: str, sender: str) -> None:
        self.write("frontend/src/lib/firebase.js",
                   "const firebaseConfig = {\n"
                   f'  projectId: "{project}",\n'
                   f'  appId: "{app_id}",\n'
                   f'  messagingSenderId: "{sender}",\n'
                   "};\n")

    def deploy_sh(self, url: str) -> None:
        self.write("deploy/vultr/deploy.sh",
                   "#!/usr/bin/env bash\n"
                   f'REPO_URL="{url}"\n'
                   "git reset --hard origin/main\n")

    def compose(self, body: str) -> None:
        self.write("docker-compose.yml", body)

    def all_firebase_sites(self, project: str) -> None:
        """The four sites the firebase-project-id rule reads."""
        self.firebaserc(project)
        self.env_production(project)
        self.backend_env_example(project)
        self.deploy_workflow(project)


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Repo:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"],
                   cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    return Repo(tmp_path)


@dataclass
class Call:
    args: tuple
    kwargs: dict


@dataclass
class FakeExecutor:
    """Records calls and returns scripted results, so destructive commands can
    be asserted on without a daemon: the assertion is that `docker rm` was
    never called, which needs no docker."""

    scripted: dict = field(default_factory=dict)
    calls: list[Call] = field(default_factory=list)

    def __call__(self, *args, **kwargs):
        self.calls.append(Call(args, kwargs))
        key = " ".join(args[0]) if args and isinstance(args[0], list | tuple) else str(args)
        rc, out, err = self.scripted.get(key, (0, "", ""))
        return subprocess.CompletedProcess(args[0] if args else [], rc, out, err)

    def called_with(self, fragment: str) -> bool:
        return any(fragment in " ".join(map(str, c.args[0])) for c in self.calls
                   if c.args and isinstance(c.args[0], list | tuple))

    def assert_never(self, fragment: str) -> None:
        assert not self.called_with(fragment), f"{fragment!r} was called"


@pytest.fixture
def fake_executor() -> FakeExecutor:
    return FakeExecutor()


@pytest.fixture
def local_http_server():
    """A server on an ephemeral port returning a scripted response."""
    state = {"status": 200, "content_type": "text/html; charset=utf-8", "body": "<html></html>"}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            # Content-Length must match what is actually written, or a client
            # blocks waiting for a body that never arrives.
            body = state["body"].encode() if state["status"] not in (301, 302, 307, 308) else b""
            self.send_response(state["status"])
            self.send_header("Content-Type", state["content_type"])
            self.send_header("Content-Length", str(len(body)))
            if not body:
                self.send_header("Location", "https://example.invalid/")
            self.end_headers()
            if body:
                self.wfile.write(body)

        def log_message(self, *a):  # silence
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    class Control:
        url = f"http://127.0.0.1:{server.server_port}/"

        @staticmethod
        def script(status=200, content_type="text/html; charset=utf-8", body="<html></html>"):
            state.update(status=status, content_type=content_type, body=body)

    yield Control
    server.shutdown()
    server.server_close()
