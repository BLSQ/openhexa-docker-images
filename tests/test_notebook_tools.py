"""Checks on Jupyter AI and the AI credentials wiring. Everything runs inside the
image under test."""

import json

import pytest

from .testutils import run_in_image

FAKE_TOKEN = "ya29.fake-vertex-access-token"
MANAGED_ENV = {
    "HEXA_AI_PROVIDER": "managed",
    "HEXA_AI_MODEL": "claude-opus-4-6",
    "HEXA_AI_VERTEX_PROJECT_ID": "test-project",
    "HEXA_AI_VERTEX_REGION": "europe-west1",
    "HEXA_AI_VERTEX_ACCESS_TOKEN": FAKE_TOKEN,
}


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
        "source /usr/local/bin/hexa-ai-env.sh && env | grep -cE '^(CLAUDE_CODE_USE_VERTEX|GCE_METADATA_HOST|ANTHROPIC_API_KEY|ANTHROPIC_MODEL)=' || true",
    )
    assert out.strip().splitlines()[-1] == "0"


def test_ai_env_anthropic_provider(docker_image):
    out = run_in_image(
        docker_image,
        "source /usr/local/bin/hexa-ai-env.sh && echo key=$ANTHROPIC_API_KEY model=$ANTHROPIC_MODEL vertex=${CLAUDE_CODE_USE_VERTEX:-unset}",
        environment={
            "HEXA_AI_PROVIDER": "anthropic",
            "HEXA_AI_MODEL": "claude-sonnet-4-6",
            "HEXA_AI_ANTHROPIC_API_KEY": "sk-ant-test",
        },
    )
    assert "key=sk-ant-test model=claude-sonnet-4-6 vertex=unset" in out


def test_ai_env_managed_provider_serves_token_as_adc(docker_image):
    """With the managed provider, the Google client libraries must obtain the
    OpenHEXA-issued token through Application Default Credentials."""
    script = r"""
set -e
source /usr/local/bin/hexa-ai-env.sh
echo "CLAUDE_CODE_USE_VERTEX=$CLAUDE_CODE_USE_VERTEX CLOUD_ML_REGION=$CLOUD_ML_REGION ANTHROPIC_VERTEX_PROJECT_ID=$ANTHROPIC_VERTEX_PROJECT_ID ANTHROPIC_MODEL=$ANTHROPIC_MODEL"
echo "GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION VERTEXAI_PROJECT=$VERTEXAI_PROJECT"
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
        "CLAUDE_CODE_USE_VERTEX=1 CLOUD_ML_REGION=europe-west1 "
        "ANTHROPIC_VERTEX_PROJECT_ID=test-project ANTHROPIC_MODEL=claude-opus-4-6"
    ) in out
    assert (
        "GOOGLE_GENAI_USE_VERTEXAI=true GOOGLE_CLOUD_LOCATION=europe-west1 VERTEXAI_PROJECT=test-project"
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


def test_claude_acp_adapter_when_claude_code_installed(docker_image):
    """Images that ship Claude Code must also ship the ACP adapter that
    exposes it as the @Claude persona of Jupyter AI."""
    out = run_in_image(
        docker_image,
        "command -v claude || echo no-claude; "
        "command -v claude-agent-acp || echo no-adapter; "
        # The adapter must run the Claude Code installed in the image.
        '[ -x "$CLAUDE_CODE_EXECUTABLE" ] || echo "bad-executable=$CLAUDE_CODE_EXECUTABLE"',
    )
    if "no-claude" in out:
        pytest.skip("Claude Code is not part of this image")
    assert "no-adapter" not in out
    assert "bad-executable" not in out
