"""Checks on Jupyter AI and the wiring of Jupyternaut to the OpenHEXA assistant
gateway. Everything runs inside the image under test."""

import json
from pathlib import Path

from . import fake_gateway
from .testutils import run_in_image

# Starts a Jupyter server on 127.0.0.1:8899 and waits for it.
START_SERVER = r"""
jupyter server --ServerApp.port=8899 --ServerApp.token=t --ServerApp.ip=127.0.0.1 --ServerApp.root_dir=/tmp > /tmp/server.log 2>&1 &
for i in $(seq 1 120); do curl -sf -o /dev/null http://127.0.0.1:8899/api/status?token=t && break; sleep 0.5; done
"""

# Runs tests/fake_gateway.py in the container, from the FAKE_GATEWAY variable.
START_FAKE_GATEWAY = r"""
python -c "$FAKE_GATEWAY" &
sleep 1
"""
FAKE_GATEWAY_ENV = {
    **fake_gateway.GATEWAY_ENV,
    "FAKE_GATEWAY": Path(fake_gateway.__file__).read_text(),
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


def test_jupyternaut_default_model_is_the_gateway(docker_image):
    """The Jupyternaut server extension must make the OpenHEXA gateway its
    default model, from the HEXA_AI_* variables, and the parameters it saves
    must drive litellm to the gateway with the workspace token."""
    script = START_SERVER + r"""
curl -sf http://127.0.0.1:8899/api/jupyternaut/config?token=t || { cat /tmp/server.log; exit 1; }
"""
    out = run_in_image(docker_image, script, environment=fake_gateway.GATEWAY_ENV)
    config = json.loads(out.strip().splitlines()[-1])
    model_id = f"openai/{fake_gateway.MODEL}"
    assert config["model_provider_id"] == model_id
    assert config["fields"][model_id] == {
        "api_base": f"http://127.0.0.1:{fake_gateway.PORT}/assistant/gateway/v1",
        "api_key": fake_gateway.TOKEN,
    }

    # Without the variables, nothing is configured.
    out = run_in_image(docker_image, script)
    config = json.loads(out.strip().splitlines()[-1])
    assert config["model_provider_id"] is None


def test_jupyternaut_model_reaches_the_gateway(docker_image):
    """litellm, called with the parameters Jupyternaut saves, streams a
    completion from the gateway: the transport works. Jupyternaut's own path to
    the model (its agent and tools) is covered in the browser by
    test_jupyter_ai_ui.py."""
    script = START_FAKE_GATEWAY + START_SERVER + r"""
curl -sf http://127.0.0.1:8899/api/jupyternaut/config?token=t > /tmp/config.json
python - <<'EOF'
import asyncio, json
import litellm

config = json.load(open("/tmp/config.json"))
model_id = config["model_provider_id"]
params = config["fields"][model_id]

async def main():
    stream = await litellm.acompletion(
        model=model_id, messages=[{"role": "user", "content": "hi"}], stream=True, **params
    )
    text = "".join([chunk.choices[0].delta.content or "" async for chunk in stream])
    print("ANSWER " + text)

asyncio.run(main())
EOF
"""
    out = run_in_image(docker_image, script, environment=FAKE_GATEWAY_ENV)
    assert f"ANSWER {fake_gateway.REPLY}" in out
    received = fake_gateway.requests_received(out)[0]
    assert received["path"] == "/assistant/gateway/v1/chat/completions"
    assert received["authorization"] == f"Bearer {fake_gateway.TOKEN}"
    assert received["model"] == fake_gateway.MODEL
    assert received["stream"] is True
    assert received["messages"] == [{"role": "user", "content": "hi"}]


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
