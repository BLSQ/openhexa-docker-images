"""Telemetry of the AI assistant: Jupyternaut's model calls are exported over
OTLP to OpenHEXA, which accounts for the tokens and forwards the traces to
Logfire (see images/base/files/ai/hexa_ai_telemetry). A local HTTP server
stands in for OpenHEXA here."""

import json

from .testutils import run_in_image

# Collects OTLP/HTTP requests: prints one "SINK {...}" line per request and keeps
# the bodies for decoding.
SINK_SERVER = r"""
cat > /tmp/otlp_sink.py <<'PY'
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        print("SINK " + json.dumps({
            "path": self.path,
            "authorization": self.headers.get("Authorization"),
            "content_type": self.headers.get("Content-Type"),
        }), flush=True)
        with open("/tmp/sink" + self.path.replace("/", "_") + ".bin", "ab") as f:
            f.write(body)
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

ThreadingHTTPServer(("127.0.0.1", 4318), Handler).serve_forever()
PY
python /tmp/otlp_sink.py &
sleep 1
"""

TELEMETRY_ENV = {
    "HEXA_AI_PROVIDER": "anthropic",
    "HEXA_AI_MODEL": "claude-sonnet-4-6",
    "HEXA_AI_ANTHROPIC_API_KEY": "sk-ant-test",
    "HEXA_SERVER_URL": "http://127.0.0.1:4318/",
    "HEXA_TOKEN": "workspace-token:signature",
    "HEXA_WORKSPACE": "my-workspace",
    "JUPYTERHUB_USER": "user@example.org",
}


def _sink_requests(out: str) -> list[dict]:
    return [json.loads(line[5:]) for line in out.splitlines() if line.startswith("SINK ")]


def test_ai_telemetry_env_needs_a_configured_assistant_and_a_server(docker_image):
    script = (
        "source /usr/local/bin/hexa-ai-env.sh && "
        "echo endpoint=${HEXA_AI_TELEMETRY_ENDPOINT:-unset} resource=${OTEL_RESOURCE_ATTRIBUTES:-unset}"
    )
    # No HEXA_SERVER_URL: nowhere to send the telemetry.
    env = {k: v for k, v in TELEMETRY_ENV.items() if k != "HEXA_SERVER_URL"}
    assert "endpoint=unset resource=unset" in run_in_image(docker_image, script, environment=env)

    # No assistant configured: nothing to account for.
    env = {k: v for k, v in TELEMETRY_ENV.items() if not k.startswith("HEXA_AI_")}
    assert "endpoint=unset resource=unset" in run_in_image(docker_image, script, environment=env)

    # Switched off explicitly.
    out = run_in_image(docker_image, script, environment={**TELEMETRY_ENV, "HEXA_AI_TELEMETRY": "false"})
    assert "endpoint=unset resource=unset" in out

    out = run_in_image(docker_image, script, environment=TELEMETRY_ENV)
    assert (
        "endpoint=http://127.0.0.1:4318/notebooks/telemetry "
        "resource=hexa.workspace=my-workspace,hexa.user=user@example.org"
    ) in out


def test_ai_telemetry_extension_registered(docker_image):
    out = run_in_image(docker_image, "jupyter server extension list 2>&1")
    assert "hexa_ai_telemetry \x1b[32menabled\x1b[0m" in out, out
    validation = next(line for line in out.splitlines() if "Validating hexa_ai_telemetry" in line)
    assert "X" not in validation, out  # an import error prints a red X


def test_ai_telemetry_extension_configures_the_server(docker_image):
    """The extension must install the exporter in the server process, where
    Jupyternaut runs, and stay quiet when telemetry is not configured."""
    script = r"""
source /usr/local/bin/hexa-ai-env.sh
timeout 90 jupyter server --ServerApp.port=8899 --ServerApp.token=t --ServerApp.ip=127.0.0.1 --ServerApp.root_dir=/tmp > /tmp/server.log 2>&1 &
for i in $(seq 1 120); do curl -sf -o /dev/null http://127.0.0.1:8899/api/status?token=t && break; sleep 0.5; done
grep hexa_ai_telemetry /tmp/server.log
"""
    out = run_in_image(docker_image, script, environment=TELEMETRY_ENV)
    assert (
        "hexa_ai_telemetry: exporting Jupyternaut traces to "
        "http://127.0.0.1:4318/notebooks/telemetry/v1/traces"
    ) in out

    out = run_in_image(docker_image, script)
    assert "hexa_ai_telemetry: HEXA_AI_TELEMETRY_ENDPOINT not set, AI telemetry off" in out


def test_ai_telemetry_off_without_endpoint(docker_image):
    out = run_in_image(
        docker_image,
        "python -c 'import hexa_ai_telemetry, litellm; "
        "print(hexa_ai_telemetry.configure_litellm(), len(litellm.callbacks))'",
    )
    assert out.strip().splitlines()[-1] == "None 0"


def test_jupyternaut_calls_are_exported_to_openhexa(docker_image):
    """A (mocked) litellm call made the way Jupyternaut makes them reaches the
    collector as an OTLP trace carrying the token usage, authenticated with the
    workspace token and without the prompt text."""
    script = SINK_SERVER + r"""
source /usr/local/bin/hexa-ai-env.sh
python - <<'PY'
import asyncio, time
import litellm
import hexa_ai_telemetry
from litellm.types.utils import ModelResponse, PromptTokensDetailsWrapper, Usage

callback = hexa_ai_telemetry.configure_litellm()
assert callback is not None and hexa_ai_telemetry.configure_litellm() is callback

response = ModelResponse(
    choices=[{"message": {"role": "assistant", "content": "hello"}}],
    model="claude-sonnet-4-6",
    usage=Usage(
        prompt_tokens=1000, completion_tokens=20, total_tokens=1020,
        prompt_tokens_details=PromptTokensDetailsWrapper(cached_tokens=600),
        cache_creation_input_tokens=100, cache_read_input_tokens=600,
    ),
)

async def main():
    await litellm.acompletion(
        model="anthropic/claude-sonnet-4-6", api_key="x",
        messages=[{"role": "user", "content": "a secret prompt"}],
        mock_response=response,
    )
    stream = await litellm.acompletion(
        model="anthropic/claude-sonnet-4-6", api_key="x",
        messages=[{"role": "user", "content": "hi"}],
        mock_response="streamed", stream=True,
    )
    async for _ in stream:
        pass
    await asyncio.sleep(1)

asyncio.run(main())
time.sleep(6)  # the batch exporter flushes every 5s
PY
python - <<'PY'
import json
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

def value(any_value):
    return getattr(any_value, any_value.WhichOneof("value"))

request = ExportTraceServiceRequest()
request.ParseFromString(open("/tmp/sink_notebooks_telemetry_v1_traces.bin", "rb").read())
spans = []
for resource_spans in request.resource_spans:
    resource = {kv.key: value(kv.value) for kv in resource_spans.resource.attributes}
    for scope_spans in resource_spans.scope_spans:
        for span in scope_spans.spans:
            attributes = {kv.key: value(kv.value) for kv in span.attributes}
            spans.append({"name": span.name, "resource": resource, "attributes": attributes})
print("SPANS " + json.dumps(spans))
PY
"""
    out = run_in_image(docker_image, script, environment=TELEMETRY_ENV)

    requests = _sink_requests(out)
    assert requests, out
    for request in requests:
        assert request["path"] == "/notebooks/telemetry/v1/traces"
        assert request["authorization"] == "workspace-token:signature"
        assert request["content_type"] == "application/x-protobuf"

    spans_line = next(line for line in out.splitlines() if line.startswith("SPANS "))
    spans = [s for s in json.loads(spans_line[6:]) if s["name"] == "litellm_request"]
    assert len(spans) == 2, spans
    for span in spans:
        assert span["resource"]["service.name"] == "jupyternaut"
        assert span["resource"]["hexa.workspace"] == "my-workspace"
        assert span["resource"]["hexa.user"] == "user@example.org"
        assert span["attributes"]["gen_ai.system"] == "anthropic"
        assert span["attributes"]["gen_ai.request.model"] == "claude-sonnet-4-6"
        assert "gen_ai.input.messages" not in span["attributes"]
        assert "gen_ai.output.messages" not in span["attributes"]

    full, streamed = sorted(spans, key=lambda s: s["attributes"]["gen_ai.usage.input_tokens"], reverse=True)
    assert full["attributes"]["gen_ai.usage.input_tokens"] == 1000
    assert full["attributes"]["gen_ai.usage.output_tokens"] == 20
    assert full["attributes"]["gen_ai.usage.cache_read.input_tokens"] == 600
    assert full["attributes"]["gen_ai.usage.cache_creation.input_tokens"] == 100
    assert streamed["attributes"]["gen_ai.usage.output_tokens"] > 0
    assert "gen_ai.usage.cache_read.input_tokens" not in streamed["attributes"]
