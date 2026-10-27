"""Fake OpenHEXA assistant gateway for testing Jupyternaut inside a container.

Responds to every chat completion request with a streamed reply and logs each
request as a `GATEWAY {json}` line to stdout. Imported by tests (for constants
and `requests_received`) and executed inside the container via `GATEWAY_ENV`
(or `make run-base RUN_FAKE_GATEWAY=1`).
"""

import json

PORT = 4318
MODEL = "claude-opus-4-6"
TOKEN = "workspace-token:signature"
REPLY = "Hello from the gateway"

# Environment variables injected by OpenHEXA when the AI assistant is enabled.
GATEWAY_ENV = {
    "HEXA_AI_PROVIDER": "openhexa",
    "HEXA_AI_MODEL": MODEL,
    "HEXA_SERVER_URL": f"http://127.0.0.1:{PORT}/",
    "HEXA_TOKEN": TOKEN,
}

PREFIX = "GATEWAY "


def requests_received(logs: str) -> list[dict]:
    """Parse logged gateway requests from container output."""
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
