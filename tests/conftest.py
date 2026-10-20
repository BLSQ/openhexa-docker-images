import json
import secrets
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

import docker
import pytest


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

    def api(self, method: str, path: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={**self._headers, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
            return json.loads(payload) if payload else {}

    def put_file(self, path: str, content: str) -> None:
        """Create a text file through the contents API, relative to the
        server's root directory. No host volume mount is involved, so this
        works with Docker Desktop's file sharing restrictions too."""
        self.api(
            "PUT",
            f"/api/contents/{path}",
            {"type": "file", "format": "text", "content": content},
        )

    def logs(self) -> str:
        return self.container.logs().decode("utf-8", errors="replace")


@pytest.fixture(scope="module")
def jupyterlab(docker_image):
    """Serve the image under test as JupyterLab on a free host port."""
    client = docker.from_env()
    token = secrets.token_hex(16)
    container = client.containers.run(
        docker_image,
        command=[
            "notebook",
            f"--ServerApp.token={token}",
            "--ServerApp.password=",
        ],
        environment={"CONTENT_SECURITY_POLICY": "frame-ancestors 'self'"},
        ports={"8888/tcp": ("127.0.0.1", None)},
        detach=True,
    )
    try:
        container.reload()
        port = container.ports["8888/tcp"][0]["HostPort"]
        lab = JupyterLab(container, f"http://127.0.0.1:{port}", token)
        deadline = time.monotonic() + 120
        while True:
            try:
                lab.api("GET", "/api/status")
                break
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                container.reload()
                if container.status == "exited" or time.monotonic() > deadline:
                    pytest.fail(f"JupyterLab did not start:\n{lab.logs()}")
                time.sleep(0.5)
        yield lab
    finally:
        container.remove(force=True)
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
def lab_page(browser, jupyterlab):
    """A browser page with JupyterLab open and its file browser ready. The
    console messages and uncaught errors of the page are collected in
    `page.console_messages` as "[type] text" strings."""
    context = browser.new_context(viewport={"width": 1400, "height": 900})
    page = context.new_page()
    messages: list[str] = []
    page.on("console", lambda m: messages.append(f"[{m.type}] {m.text}"))
    page.on("pageerror", lambda e: messages.append(f"[pageerror] {e}"))
    page.console_messages = messages
    page.goto(jupyterlab.lab_url)
    page.locator(".jp-DirListing-content").wait_for(timeout=120_000)
    # Extensions keep activating for a moment after the shell is visible.
    page.wait_for_load_state("networkidle")
    yield page
    context.close()
