"""The standalone JupyterLab server the ui tests and `make run-*` use.

It must come up the way the hub starts it: serving the workspace directory,
with the Content-Security-Policy header of the environment and the kernels
the image flavor promises. These need Docker only, no browser.
"""

from .conftest import WORKSPACE_DIR


def test_server_serves_the_workspace_directory(jupyterlab):
    logs = jupyterlab.logs()
    # Without the directory, jupyter_server logs a TraitError per extension
    # and falls back to serving the home directory.
    assert "TraitError" not in logs, logs
    assert f"Serving notebooks from local directory: {WORKSPACE_DIR}" in logs, logs


def test_server_runs_in_its_root_directory(jupyterlab):
    # Jupyternaut's file tools resolve paths against cwd while notebook tools
    # and the frontend use the server root; both must point to WORKSPACE_DIR.
    code, out = jupyterlab.container.exec_run(
        ["bash", "-c", "readlink /proc/$(pgrep -of jupyter-lab)/cwd"]
    )
    assert out.decode().strip() == WORKSPACE_DIR, out


def test_contents_api_is_rooted_at_the_workspace(jupyterlab):
    listing = jupyterlab.api("GET", "/api/contents")
    names = {entry["name"] for entry in listing["content"]}
    # These live in the home directory, one level up from the workspace.
    assert not names & {"DO_NOT_WRITE_HERE.md", ".hexa_scripts", "work"}, names


def test_put_file_creates_a_file_under_the_root(jupyterlab):
    jupyterlab.put_file("server test/hello world.txt", "hi\n")
    model = jupyterlab.api("GET", "/api/contents/server%20test/hello%20world.txt")
    assert model["content"] == "hi\n"


def test_content_security_policy_header(jupyterlab):
    with jupyterlab.request("GET", "/lab") as response:
        assert response.status == 200
        assert response.headers["Content-Security-Policy"] == "frame-ancestors 'self'"


def test_kernels_of_the_image(jupyterlab, image_flavor):
    specs = jupyterlab.api("GET", "/api/kernelspecs")["kernelspecs"]
    expected = {"python3"} if image_flavor == "base" else {"python3", "ir"}
    assert expected <= set(specs), set(specs)
