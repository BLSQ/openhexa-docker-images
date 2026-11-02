import json
import re
from pathlib import Path

from .testutils import run_in_image, run_local_pipeline

pipelines_dir = Path(__file__).parent / "pipelines"

RUN_CONTEXT = {
    "HEXA_WORKSPACE": "my-workspace",
    "HEXA_PIPELINE_CODE": "my-pipeline",
    "HEXA_RUN_ID": "0e5c1f9e-4a8d-4a3e-9d5b-2f6a7b8c9d0e",
}
OPENHEXA_UA = re.compile(
    r"openhexa-sdk/\S+ \(workspace=my-workspace; pipeline=my-pipeline; "
    r"run_id=0e5c1f9e-4a8d-4a3e-9d5b-2f6a7b8c9d0e\)"
)

PRINT_DEFAULT_USER_AGENTS = """python - <<'PY'
import urllib.request

import requests.utils

print("requests:", requests.utils.default_user_agent())
print("urllib:", dict(urllib.request.build_opener().addheaders)["User-agent"])
PY
"""


def test_sitecustomize_is_ours(docker_image):
    out = run_in_image(
        docker_image,
        "python -c 'import sitecustomize; print(open(sitecustomize.__file__).read())'",
    )
    assert "install_default_user_agent" in out, out


def test_default_user_agent_in_pipeline_run(docker_image):
    out = run_in_image(docker_image, PRINT_DEFAULT_USER_AGENTS, environment=RUN_CONTEXT)
    for client in ("requests", "urllib"):
        line = next(l for l in out.splitlines() if l.startswith(f"{client}:"))
        assert OPENHEXA_UA.fullmatch(line.split(": ", 1)[1]), out


def test_default_user_agent_unchanged_outside_pipeline_run(docker_image):
    out = run_in_image(docker_image, PRINT_DEFAULT_USER_AGENTS)
    assert "requests: python-requests/" in out, out
    assert "urllib: Python-urllib/" in out, out
    assert "openhexa-sdk" not in out, out


def test_code_pipeline_sends_user_agent_from_main_and_task(docker_image):
    logs = run_local_pipeline(docker_image, pipelines_dir / "user_agent", RUN_CONTEXT)
    sent = dict(re.findall(r"^UA (\w+ \w+): (.*)$", logs, re.MULTILINE))
    assert set(sent) == {
        "main requests",
        "main urllib",
        "task requests",
        "task urllib",
    }, logs
    for where, user_agent in sent.items():
        assert OPENHEXA_UA.fullmatch(user_agent), f"{where}: {user_agent}"


def test_notebook_pipeline_sends_user_agent_from_kernel(docker_image):
    # bootstrap_pipeline.py writes the executed notebook to .runs_outputs next
    # to the notebook. A bind mount is not writable by jovyan when the host
    # directory belongs to another uid (Linux, CI), so the notebook is written
    # inside the container and the executed one printed after a marker.
    notebook = (pipelines_dir / "user_agent_notebook" / "user_agent.ipynb").read_text()
    out = run_in_image(
        docker_image,
        f"""set -e
mkdir -p /tmp/workspace
cat > /tmp/workspace/user_agent.ipynb <<'NOTEBOOK'
{notebook}
NOTEBOOK
/usr/local/bin/entrypoint.sh pipeline run
echo EXECUTED NOTEBOOK
cat /tmp/workspace/.runs_outputs/user_agent.ipynb
""",
        environment={
            **RUN_CONTEXT,
            "HEXA_ENVIRONMENT": "LOCAL_PIPELINE",
            "HEXA_PIPELINE_TYPE": "notebook",
            "HEXA_NOTEBOOK_PATH": "user_agent.ipynb",
            # workspace.files_path, where the notebook is looked up.
            "WORKSPACE_FILES_PATH": "/tmp/workspace",
        },
    )
    logs, _, executed = out.partition("EXECUTED NOTEBOOK\n")
    assert "Pipeline completed." in logs, out
    executed = json.loads(executed)
    text = "".join(
        "".join(output.get("text", ""))
        for cell in executed["cells"]
        for output in cell.get("outputs", [])
    )
    sent = dict(re.findall(r"^UA (\w+ \w+): (.*)$", text, re.MULTILINE))
    assert set(sent) == {"kernel requests", "kernel urllib"}, text
    for where, user_agent in sent.items():
        assert OPENHEXA_UA.fullmatch(user_agent), f"{where}: {user_agent}"
