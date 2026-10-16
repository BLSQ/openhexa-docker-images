"""Checks on the tooling available to notebook users: Jupyter AI, Quarto and the
AI credentials wiring. Everything runs inside the image under test."""

import json

from .testutils import run_in_image

FAKE_TOKEN = "ya29.fake-vertex-access-token"
MANAGED_ENV = {
    "HEXA_AI_PROVIDER": "managed",
    "HEXA_AI_MODEL": "claude-opus-4-6",
    "HEXA_AI_VERTEX_PROJECT_ID": "test-project",
    "HEXA_AI_VERTEX_REGION": "europe-west1",
    "HEXA_AI_VERTEX_ACCESS_TOKEN": FAKE_TOKEN,
}


def test_quarto_and_jupytext_installed(docker_image):
    out = run_in_image(docker_image, "quarto --version && jupytext --version")
    quarto_version, jupytext_version = out.strip().splitlines()[-2:]
    assert quarto_version.startswith("1.")
    assert jupytext_version.startswith("1.")


def test_quarto_extensions_registered(docker_image):
    out = run_in_image(docker_image, "jupyter labextension list 2>&1")
    assert "jupyterlab-quarto" in out
    assert "jupyterlab-jupytext" in out


def test_qmd_round_trip(docker_image):
    """A .qmd file converts to a notebook and back with jupytext, as the
    "Open with -> Notebook" action in JupyterLab does."""
    script = r"""
set -e
cd /tmp
cat > doc.qmd <<'QMD'
---
title: "Test"
---

## A heading

```{python}
print(1 + 1)
```
QMD
jupytext --to ipynb doc.qmd > /dev/null
python -c "
import nbformat
nb = nbformat.read('doc.ipynb', as_version=4)
cells = [(c.cell_type, c.source) for c in nb.cells]
assert ('code', 'print(1 + 1)') in cells, cells
print('cells ok')
"
"""
    out = run_in_image(docker_image, script)
    assert "cells ok" in out


def test_jupyter_ai_extensions_registered(docker_image):
    out = run_in_image(docker_image, "jupyter server extension list 2>&1")
    for extension in [
        "jupyter_ai_persona_manager",
        "jupyter_ai_acp_client",
        "jupyter_ai_jupyternaut",
        "jupyterlab_chat",
    ]:
        assert extension in out, f"{extension} missing from:\n{out}"
    assert "jupyterlab-chat" in run_in_image(
        docker_image, "jupyter labextension list 2>&1"
    )


def test_ai_env_without_provider_is_a_noop(docker_image):
    out = run_in_image(
        docker_image,
        "source /usr/local/bin/hexa-ai-env.sh && env | grep -cE '^(GCE_METADATA_HOST|VERTEXAI_PROJECT|ANTHROPIC_API_KEY)=' || true",
    )
    assert out.strip().splitlines()[-1] == "0"


def test_ai_env_anthropic_provider(docker_image):
    out = run_in_image(
        docker_image,
        "source /usr/local/bin/hexa-ai-env.sh && echo key=$ANTHROPIC_API_KEY metadata=${GCE_METADATA_HOST:-unset}",
        environment={
            "HEXA_AI_PROVIDER": "anthropic",
            "HEXA_AI_MODEL": "claude-sonnet-4-6",
            "HEXA_AI_ANTHROPIC_API_KEY": "sk-ant-test",
        },
    )
    assert "key=sk-ant-test metadata=unset" in out


def test_ai_env_managed_provider_serves_token_as_adc(docker_image):
    """With the managed provider, the Google client libraries must obtain the
    OpenHEXA-issued token through Application Default Credentials."""
    script = r"""
set -e
source /usr/local/bin/hexa-ai-env.sh
echo "VERTEXAI_PROJECT=$VERTEXAI_PROJECT VERTEXAI_LOCATION=$VERTEXAI_LOCATION GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT"
# Give the metadata server a moment to bind.
for i in $(seq 1 20); do curl -sf -o /dev/null "http://$GCE_METADATA_HOST/" && break; sleep 0.25; done
curl -s -H 'Metadata-Flavor: Google' "http://$GCE_METADATA_HOST/computeMetadata/v1/instance/service-accounts/default/token"
echo
python - <<'PY'
import google.auth
from google.auth.transport.requests import Request
credentials, project = google.auth.default()
credentials.refresh(Request())
print(f"ADC token={credentials.token} project={project}")
PY
"""
    out = run_in_image(docker_image, script, environment=MANAGED_ENV)
    assert (
        "VERTEXAI_PROJECT=test-project VERTEXAI_LOCATION=europe-west1 "
        "GOOGLE_CLOUD_PROJECT=test-project"
    ) in out
    token_line = next(
        line for line in out.splitlines() if line.startswith('{"access_token"')
    )
    assert json.loads(token_line)["access_token"] == FAKE_TOKEN
    assert f"ADC token={FAKE_TOKEN} project=test-project" in out


def test_jupyternaut_default_model_follows_managed_provider(docker_image):
    """The Jupyternaut server extension must pick up the model from the
    HEXA_AI_* variables through its config file."""
    script = r"""
set -e
source /usr/local/bin/hexa-ai-env.sh
jupyter server --ServerApp.port=8899 --ServerApp.token=t --ServerApp.ip=127.0.0.1 --ServerApp.root_dir=/tmp > /tmp/server.log 2>&1 &
for i in $(seq 1 120); do curl -sf -o /dev/null http://127.0.0.1:8899/api/status?token=t && break; sleep 0.5; done
curl -sf http://127.0.0.1:8899/api/jupyternaut/config?token=t || { cat /tmp/server.log; exit 1; }
"""
    out = run_in_image(docker_image, script, environment=MANAGED_ENV)
    config = json.loads(out.strip().splitlines()[-1])
    assert config["model_provider_id"] == "vertex_ai/claude-opus-4-6"
    assert config["fields"]["vertex_ai/claude-opus-4-6"] == {
        "vertex_project": "test-project",
        "vertex_location": "europe-west1",
    }


def test_jupyternaut_is_the_only_persona(docker_image):
    """Jupyter AI also ships personas for coding agents (Claude Code, Codex...)
    that register themselves as soon as their binary is on the PATH. We only
    offer Jupyternaut, so none of those must be loadable."""
    script = r"""
python - <<'PY'
from importlib.metadata import entry_points
from jupyter_ai_persona_manager import PersonaRequirementsUnmet

loaded = []
for ep in entry_points(group="jupyter_ai.personas"):
    try:
        ep.load()
    except PersonaRequirementsUnmet:
        continue
    loaded.append(ep.name)
print("personas:", ",".join(sorted(loaded)))
PY
"""
    out = run_in_image(docker_image, script)
    assert out.strip().splitlines()[-1] == "personas: jupyternaut"
