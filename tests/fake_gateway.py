"""A stand-in for the OpenHEXA assistant gateway, run inside the image under test.

It answers every chat completion with one streamed reply and prints what it
received as a `GATEWAY {json}` line, so a test can check from the container
logs how Jupyternaut called it. The module is both imported by the tests (for
the constants and `requests_received`) and executed inside the container, where
`jupyter_jupyter_ai_jupyternaut_config.py` points Jupyternaut at it through
`GATEWAY_ENV`:

    python -c "$FAKE_GATEWAY" &   # with FAKE_GATEWAY=$(cat tests/fake_gateway.py)

`make run-base RUN_FAKE_GATEWAY=1` serves an image this way.
"""

import json

PORT = 4318
MODEL = "claude-opus-4-6"
TOKEN = "workspace-token:signature"
REPLY = "Hello from the gateway"

# What the OpenHEXA app injects when the organization's assistant is on,
# pointing at this gateway.
GATEWAY_ENV = {
    "HEXA_AI_PROVIDER": "openhexa",
    "HEXA_AI_MODEL": MODEL,
    "HEXA_SERVER_URL": f"http://127.0.0.1:{PORT}/",
    "HEXA_TOKEN": TOKEN,
}

PREFIX = "GATEWAY "


def requests_received(logs: str) -> list[dict]:
    """The requests the gateway logged, in order."""
    return [
        json.loads(line[len(PREFIX) :])
        for line in logs.splitlines()
        if line.startswith(PREFIX)
    ]


def serve():
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            print(
                PREFIX
                + json.dumps(
                    {
                        "path": self.path,
                        "authorization": self.headers.get("Authorization"),
                        "model": body.get("model"),
                        "stream": body.get("stream"),
                        "messages": body.get("messages"),
                        "tools": [
                            tool.get("function", {}).get("name")
                            for tool in body.get("tools") or []
                        ],
                    }
                ),
                flush=True,
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            chunk = {
                "id": "chatcmpl-1",
                "object": "chat.completion.chunk",
                "created": 1,
                "model": MODEL,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": REPLY},
                        "finish_reason": None,
                    }
                ],
            }
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            chunk["choices"][0] = {"index": 0, "delta": {}, "finish_reason": "stop"}
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")

    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    serve()
