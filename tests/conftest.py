import json
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import docker
import pytest

from . import fake_gateway

# c.ServerApp.root_dir in images/base/jupyter_notebook_config.py. The hub mounts
# the workspace files there; the standalone server of the tests and of the
# `make run-*` targets gets an empty directory instead, created at startup.
WORKSPACE_DIR = "/home/jovyan/workspace"
ENTRYPOINT = "/usr/local/bin/entrypoint.sh"


def pytest_addoption(parser):
    parser.addoption(
        "--docker-image",
        action="store",
        default=None,
        help="Docker image to use for testing. If not specified, all configured images will be tested.",
    )
    parser.addoption(
        "--image-flavor",
        action="store",
        choices=["base", "blsq", "blsq-r"],
        default=None,
        help="Which image the tested image is built from, for image-specific "
        "checks. Guessed from the image name when not given.",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        help="Show the Chromium window the ui tests drive instead of running it headless.",
    )
    parser.addoption(
        "--slowmo",
        type=int,
        default=0,
        metavar="MS",
        help="Pause this many milliseconds after each browser action of the ui "
        "tests, to follow them with --headed.",
    )


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Keep each phase's report on the item, so fixtures can tell on teardown
    whether the test failed (`item.rep_call.failed`)."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(scope="session")
def docker_image(request):
    """Fixture that returns the docker image specified via command line or None."""
    docker_image = request.config.getoption("--docker-image")
    if docker_image is None:
        pytest.fail("Docker image not specified")
    return docker_image


@pytest.fixture(scope="session")
def image_flavor(request, docker_image):
    """base, blsq or blsq-r: the image directory the tested image comes from."""
    flavor = request.config.getoption("--image-flavor")
    if flavor:
        return flavor
    name = docker_image.rsplit("/", 1)[-1].split(":", 1)[0]
    if "blsq-r" in name:
        return "blsq-r"
    if "blsq" in name:
        return "blsq"
    return "base"


@dataclass
class JupyterLab:
    """A standalone JupyterLab served by the image under test (no hub, no
    OpenHEXA app), reachable from the host."""

    container: object
    base_url: str
    token: str
    _headers: dict = field(init=False)

    def __post_init__(self):
        self._headers = {"Authorization": f"token {self.token}"}

    @property
    def lab_url(self) -> str:
        return f"{self.base_url}/lab?token={self.token}"

    def request(self, method: str, path: str, body: dict | None = None):
        """Send an authenticated request and return the (opened) response."""
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={**self._headers, "Content-Type": "application/json"},
        )
        return urllib.request.urlopen(request, timeout=30)

    def api(self, method: str, path: str, body: dict | None = None) -> dict:
        """Call a JSON endpoint and return the decoded body ({} when empty)."""
        with self.request(method, path, body) as response:
            payload = response.read()
            return json.loads(payload) if payload else {}

    def put_file(self, path: str, content: str) -> None:
        """Create a text file through the contents API, relative to the
        server's root directory, creating the parent directories. No host
        volume mount is involved, so this works with Docker Desktop's file
        sharing restrictions too."""
        parts = path.split("/")
        for depth in range(1, len(parts)):
            directory = urllib.parse.quote("/".join(parts[:depth]))
            try:
                self.api("GET", f"/api/contents/{directory}?content=0")
            except urllib.error.HTTPError as error:
                if error.code != 404:
                    raise
                self.api("PUT", f"/api/contents/{directory}", {"type": "directory"})
        self.api(
            "PUT",
            f"/api/contents/{urllib.parse.quote(path)}",
            {"type": "file", "format": "text", "content": content},
        )

    def wait_for_kernel(self, path: str, timeout: float = 120) -> dict:
        """Wait until the notebook at `path` has an idle kernel with a frontend
        connected to it (an open websocket), and return the kernel model. The
        execution indicator in the page can show idle before that, and a run
        request sent then is dropped."""
        deadline = time.monotonic() + timeout
        while True:
            for session in self.api("GET", "/api/sessions"):
                kernel = session.get("kernel") or {}
                if (
                    session["path"] == path
                    and kernel.get("execution_state") == "idle"
                    and kernel.get("connections", 0) > 0
                ):
                    return kernel
            if time.monotonic() > deadline:
                raise TimeoutError(f"no connected idle kernel for {path} after {timeout}s")
            time.sleep(0.5)

    def logs(self) -> str:
        return self.container.logs().decode("utf-8", errors="replace")


def start_jupyterlab(
    client, docker_image: str, environment: dict[str, str] | None = None, setup: str = ""
) -> JupyterLab:
    """Start JupyterLab on a free localhost port and wait until it responds.
    `environment` sets extra container env vars; `setup` is a bash snippet run
    before the server starts."""
    token = secrets.token_hex(16)
    container = client.containers.run(
        docker_image,
        entrypoint=["bash", "-c"],
        command=[
            f"{setup} mkdir -p {WORKSPACE_DIR} && exec {ENTRYPOINT} notebook "
            f"--ServerApp.token={token} --ServerApp.password="
        ],
        environment={
            "CONTENT_SECURITY_POLICY": "frame-ancestors 'self'",
            **(environment or {}),
        },
        ports={"8888/tcp": ("127.0.0.1", None)},
        detach=True,
    )
    try:
        deadline = time.monotonic() + 120
        while True:
            container.reload()
            # The port mapping only exists while the container runs.
            mapping = container.ports.get("8888/tcp")
            if mapping:
                lab = JupyterLab(
                    container, f"http://127.0.0.1:{mapping[0]['HostPort']}", token
                )
                try:
                    lab.api("GET", "/api/status")
                    return lab
                except (urllib.error.URLError, ConnectionError, TimeoutError):
                    pass
            if container.status == "exited" or time.monotonic() > deadline:
                logs = container.logs().decode("utf-8", errors="replace")
                pytest.fail(f"JupyterLab did not start ({container.status}):\n{logs}")
            time.sleep(0.5)
    except BaseException:
        container.remove(force=True)
        raise


@pytest.fixture(scope="session")
def jupyterlab(docker_image):
    """Standalone JupyterLab server for the session (without `HEXA_*` env vars)."""
    client = docker.from_env()
    lab = start_jupyterlab(client, docker_image)
    try:
        yield lab
    finally:
        lab.container.remove(force=True)
        client.close()


@pytest.fixture(scope="session")
def jupyterlab_with_gateway(docker_image):
    """JupyterLab server configured with `HEXA_AI_*` and running
    `tests/fake_gateway.py` inside the container. Use
    `fake_gateway.requests_received(lab.logs())` to inspect received requests."""
    client = docker.from_env()
    lab = start_jupyterlab(
        client,
        docker_image,
        environment={
            **fake_gateway.GATEWAY_ENV,
            "FAKE_GATEWAY": Path(fake_gateway.__file__).read_text(),
        },
        setup='python -c "$FAKE_GATEWAY" &',
    )
    try:
        yield lab
    finally:
        lab.container.remove(force=True)
        client.close()


@pytest.fixture(scope="session")
def browser(request):
    """Chromium from Playwright (`python -m playwright install chromium`), headless
    unless --headed is given; --slowmo slows it down to watch. PWDEBUG=1 in the
    environment opens the Playwright Inspector to step through the actions."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=not request.config.getoption("--headed"),
            slow_mo=request.config.getoption("--slowmo"),
        )
        yield browser
        browser.close()


@pytest.fixture
def open_lab(browser, request, tmp_path):
    """Return a helper that opens a `JupyterLab` server in a fresh browser
    context and waits for the file browser.

    The returned page records:
    - `page.console_messages`: console logs and uncaught errors
    - `page.responses`: `{url: status}` for every response
    - `page.http_errors`: 4xx/5xx responses and failed requests

    On test failure, a full-page screenshot and browser logs are saved to `tmp_path`.
    """
    pages = []

    def dump_diagnostics(page):
        prefix = f"{len(pages)}-" if len(pages) > 1 else ""
        screenshot = tmp_path / f"{prefix}failure.png"
        page.screenshot(path=str(screenshot), full_page=True)
        log = tmp_path / f"{prefix}browser.log"
        log.write_text("\n".join([*page.console_messages, *page.http_errors]) + "\n")
        errors = [
            m for m in page.console_messages if m.startswith(("[error]", "[pageerror]"))
        ]
        print(
            f"\nScreenshot of the failure: {screenshot}"
            f"\nBrowser console and HTTP errors: {log}"
            + ("\nBrowser errors:\n" + "\n".join(errors[:20]) if errors else "")
        )

    def open_lab(lab: JupyterLab):
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()
        messages: list[str] = []
        responses: dict[str, int] = {}
        http_errors: list[str] = []

        def on_response(response):
            responses[response.url] = response.status
            if response.status >= 400:
                http_errors.append(f"[http {response.status}] {response.url}")

        page.on("console", lambda m: messages.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: messages.append(f"[pageerror] {e}"))
        page.on("response", on_response)
        page.on(
            "requestfailed",
            lambda r: http_errors.append(f"[requestfailed] {r.url} {r.failure}"),
        )
        page.console_messages = messages
        page.responses = responses
        page.http_errors = http_errors
        pages.append(page)

        try:
            # `reset` drops the saved layout, so the tabs an earlier test opened
            # on this shared server do not come back.
            page.goto(lab.lab_url + "&reset")
            page.locator(".jp-DirListing-content").wait_for(timeout=120_000)
            # Extensions keep activating for a moment after the shell is visible.
            page.wait_for_load_state("networkidle")
        except Exception:
            dump_diagnostics(page)
            raise
        return page

    yield open_lab
    report = getattr(request.node, "rep_call", None)
    for page in pages:
        if not page.is_closed():
            if report is not None and report.failed:
                dump_diagnostics(page)
            page.context.close()


@pytest.fixture
def lab_page(open_lab, jupyterlab):
    """Open the default `jupyterlab` server in a fresh browser page."""
    return open_lab(jupyterlab)
