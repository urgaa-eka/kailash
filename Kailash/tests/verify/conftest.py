"""Harness the verification checks are tested through.

The point of `tmp_repo` is that every check reads its corpus from `git
ls-files`, so a test that writes a file without staging it is testing nothing.
The fixture stages by default.
"""
from __future__ import annotations

import http.server
import json
import re
import shutil
import socket
import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def pytest_configure(config):
    config.addinivalue_line("markers", "docker: needs a docker daemon")
    config.addinivalue_line("markers", "network: needs outbound network")


def read_fixture(name: str) -> str:
    """Raw fixture text. Used for the malformed captures, which must not parse."""
    return (FIXTURES / name).read_text(encoding="utf-8")


def load_fixture(name: str) -> dict:
    """A captured `docker inspect` shape, keyed by the Phase A capture names:
    `health` (.State.Health), `effective` (.Config.Healthcheck), `state`
    (.State) and `restarts` (.RestartCount)."""
    return json.loads(read_fixture(name))


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DEPLOY_SH = REPO_ROOT / "deploy" / "host" / "deploy.sh"


def find_bash() -> str | None:
    """A bash that can see this filesystem.

    Git bash in preference to WSL: WSL's `bash.exe` lives in System32 and its
    filesystem view is not the host's, so a script written to a Windows temp
    path is invisible to it.
    """
    for candidate in (r"C:\Program Files\Git\bin\bash.exe",
                      r"C:\Program Files (x86)\Git\bin\bash.exe"):
        if Path(candidate).is_file():
            return candidate
    found = shutil.which("bash")
    if found and "system32" in found.lower():
        return None
    return found


def extract_shell_function(name: str, text: str) -> str:
    """One `name() { ... }` definition, by brace matching.

    Sourcing `deploy.sh` is not an option: it ends in `main "$@"`, so sourcing
    it would install Docker and deploy the stack from inside a test run.
    """
    m = re.search(rf"^{name}\(\)\s*\{{", text, re.M)
    if not m:
        raise AssertionError(f"{name}() not found")
    depth, i = 0, m.end() - 1
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[m.start():i + 1]
        i += 1
    raise AssertionError(f"unbalanced braces in {name}()")


def _posix(p: Path | str) -> str:
    s = str(p).replace("\\", "/")
    if len(s) > 1 and s[1] == ":":
        s = f"/{s[0].lower()}{s[2:]}"
    return s


@pytest.fixture(scope="session")
def bash_normalise(tmp_path_factory):
    """The bash `normalise_remote()` from `deploy/host/deploy.sh`, batched.

    One process per *call*, not per URL: the parity property compares many URLs
    per example, and a bash process each would dominate the suite's runtime.

    Skips rather than fails when no usable bash exists, so the suite still runs
    on a host without one -- the Python-side properties still hold there, only
    the cross-implementation agreement goes unchecked.
    """
    bash = find_bash()
    if bash is None:
        pytest.skip("no usable bash")
    script = SCRIPT_DEPLOY_SH.read_text(encoding="utf-8")
    body = extract_shell_function("normalise_remote", script)
    harness = tmp_path_factory.mktemp("bash") / "normalise.sh"
    harness.write_text("#!/usr/bin/env bash\n" + body + "\n"
                       'for u in "$@"; do normalise_remote "$u"; echo; done\n',
                       encoding="utf-8", newline="\n")

    def normalise(urls):
        urls = list(urls)
        if not urls:
            return []
        out = subprocess.run([bash, _posix(harness), *urls],
                             capture_output=True, text=True, check=False)
        assert out.returncode == 0, out.stderr
        lines = out.stdout.split("\n")[:len(urls)]
        assert len(lines) == len(urls), (out.stdout, urls)
        return lines

    return normalise


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

    def workflow(self, name: str, body: str) -> Path:
        """An arbitrary `.github/workflows/<name>` file, staged."""
        if not name.endswith((".yml", ".yaml")):
            name += ".yml"
        return self.write(f".github/workflows/{name}", body)

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
        self.write("deploy/host/deploy.sh",
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


def _argv(args: tuple) -> tuple[str, ...]:
    """Normalise both call conventions to one argv tuple.

    `execute(["docker", "rm", "-f", name])` and `execute("docker", "rm", "-f",
    name)` are the same command and must be equally visible. The design's
    removal gate uses the second form, so a matcher that only understood the
    first would make `assert_never("docker rm")` pass while `docker rm` was
    being issued -- a vacuous assertion guarding an irreversible command.
    """
    if not args:
        return ()
    if isinstance(args[0], list | tuple):
        return tuple(str(a) for a in args[0])
    return tuple(str(a) for a in args)


@dataclass
class Call:
    args: tuple
    kwargs: dict

    @property
    def argv(self) -> tuple[str, ...]:
        return _argv(self.args)

    @property
    def command(self) -> str:
        return " ".join(self.argv)


@dataclass
class FakeExecutor:
    """Records calls and returns scripted results, so destructive commands can
    be asserted on without a daemon: the assertion is that `docker rm` was
    never called, which needs no docker.

    `scripted` maps a command string to `(returncode, stdout, stderr)`. An
    exact match wins; otherwise the longest key that is a substring of the
    command is used, so a family of `docker inspect ... <name>` calls can be
    scripted by their common prefix. Unscripted commands return 0 and empty
    output.
    """

    scripted: dict = field(default_factory=dict)
    calls: list[Call] = field(default_factory=list)

    def __call__(self, *args, **kwargs):
        call = Call(args, kwargs)
        self.calls.append(call)
        rc, out, err = self._result_for(call.command)
        completed = subprocess.CompletedProcess(list(call.argv), rc, out, err)
        if rc and kwargs.get("check"):
            # Mirror subprocess: a collector written with check=True must fail
            # here too, or the fake would hide the difference.
            raise subprocess.CalledProcessError(rc, list(call.argv), out, err)
        return completed

    def _result_for(self, command: str) -> tuple[int, str, str]:
        if command in self.scripted:
            return self.scripted[command]
        matches = [k for k in self.scripted if k and k in command]
        if matches:
            return self.scripted[max(matches, key=len)]
        return (0, "", "")

    def script(self, command: str, returncode: int = 0, stdout: str = "",
               stderr: str = "") -> None:
        self.scripted[command] = (returncode, stdout, stderr)

    def commands(self) -> list[str]:
        return [c.command for c in self.calls]

    def matching(self, fragment: str) -> list[str]:
        """Every recorded command containing `fragment`, in call order.

        Assert against this when the requirement is *exactly* which targets
        were acted on, not merely that something was.
        """
        return [c for c in self.commands() if fragment in c]

    def called_with(self, fragment: str) -> bool:
        return bool(self.matching(fragment))

    def assert_never(self, fragment: str) -> None:
        issued = self.matching(fragment)
        assert not issued, f"{fragment!r} was called: {issued}"


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
