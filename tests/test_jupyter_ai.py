"""Checks on Jupyter AI and the wiring of Jupyternaut to the OpenHEXA assistant
gateway. Everything runs inside the image under test."""

import json

from .testutils import run_in_image

GATEWAY_ENV = {
    "HEXA_AI_PROVIDER": "openhexa",
    "HEXA_AI_MODEL": "claude-opus-4-6",
    "HEXA_SERVER_URL": "http://127.0.0.1:4318/",
    "HEXA_TOKEN": "workspace-token:signature",
}

# Starts a Jupyter server on 127.0.0.1:8899 and waits for it.
START_SERVER = r"""
jupyter server --ServerApp.port=8899 --ServerApp.token=t --ServerApp.ip=127.0.0.1 --ServerApp.root_dir=/tmp > /tmp/server.log 2>&1 &
for i in $(seq 1 120); do curl -sf -o /dev/null http://127.0.0.1:8899/api/status?token=t && break; sleep 0.5; done
"""

# A stand-in for the gateway: answers one streamed chat completion and prints
# what it received.
FAKE_GATEWAY = r"""
cat > /tmp/fake_gateway.py <<'EOF'
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        print("GATEWAY " + json.dumps({
            "path": self.path,
            "authorization": self.headers.get("Authorization"),
            "model": body.get("model"),
            "stream": body.get("stream"),
            "messages": body.get("messages"),
        }), flush=True)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        chunk = {"id": "chatcmpl-1", "object": "chat.completion.chunk", "created": 1, "model": "claude-opus-4-6",
                 "choices": [{"index": 0, "delta": {"role": "assistant", "content": "Hello from the gateway"}, "finish_reason": None}]}
        self.wfile.write(("data: " + json.dumps(chunk) + "\n\n").encode())
        chunk["choices"][0] = {"index": 0, "delta": {}, "finish_reason": "stop"}
        self.wfile.write(("data: " + json.dumps(chunk) + "\n\n").encode())
        self.wfile.write(b"data: [DONE]\n\n")

ThreadingHTTPServer(("127.0.0.1", 4318), Handler).serve_forever()
EOF
python /tmp/fake_gateway.py &
sleep 1
"""


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
    out = run_in_image(docker_image, script, environment=GATEWAY_ENV)
    config = json.loads(out.strip().splitlines()[-1])
    assert config["model_provider_id"] == "openai/claude-opus-4-6"
    assert config["fields"]["openai/claude-opus-4-6"] == {
        "api_base": "http://127.0.0.1:4318/assistant/gateway/v1",
        "api_key": "workspace-token:signature",
    }

    # Without the variables, nothing is configured.
    out = run_in_image(docker_image, script)
    config = json.loads(out.strip().splitlines()[-1])
    assert config["model_provider_id"] is None


def test_jupyternaut_model_reaches_the_gateway(docker_image):
    """litellm, called the way Jupyternaut calls it with the configured
    parameters, streams a completion from the gateway."""
    script = FAKE_GATEWAY + START_SERVER + r"""
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
    out = run_in_image(docker_image, script, environment=GATEWAY_ENV)
    assert "ANSWER Hello from the gateway" in out
    received = json.loads(
        next(line for line in out.splitlines() if line.startswith("GATEWAY "))[8:]
    )
    assert received["path"] == "/assistant/gateway/v1/chat/completions"
    assert received["authorization"] == "Bearer workspace-token:signature"
    assert received["model"] == "claude-opus-4-6"
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
