#!/opt/conda/bin/python
"""Serve the OpenHEXA-issued Vertex AI access token as a Compute Engine metadata server.

OpenHEXA authenticates to Vertex AI with its own service account and hands the
notebook server a short-lived OAuth2 access token (HEXA_AI_VERTEX_ACCESS_TOKEN).
Google client libraries cannot take a raw access token as Application Default
Credentials, but all of them (google-auth for Python, google-auth-library for
Node, hence litellm, the Google GenAI SDK, Claude Code and Gemini CLI) fall back
to the Compute Engine metadata server, whose address can be overridden with the
GCE_METADATA_HOST / GCE_METADATA_IP environment variables.

This script is that metadata server: it listens on 127.0.0.1 and answers the
handful of endpoints the libraries use (ping, project id, service account token).
It is started by hexa-ai-env.sh when the managed provider is configured, and only
reachable from inside the container.
"""

import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = int(os.environ.get("HEXA_AI_METADATA_PORT", "4322"))
FLAVOR_HEADER = "Metadata-Flavor"
FLAVOR_VALUE = "Google"
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
# Google issues one-hour access tokens; used when the app does not say when
# the token expires.
DEFAULT_TOKEN_LIFETIME = 3600


def load_token() -> tuple[str, float]:
    """The access token and the epoch time at which it expires."""
    token = os.environ.get("HEXA_AI_VERTEX_ACCESS_TOKEN", "")
    if not token:
        print("HEXA_AI_VERTEX_ACCESS_TOKEN is not set", file=sys.stderr)
        sys.exit(1)
    expires_at = os.environ.get("HEXA_AI_VERTEX_ACCESS_TOKEN_EXPIRES_AT", "")
    try:
        expires_at = (
            float(expires_at) if expires_at else time.time() + DEFAULT_TOKEN_LIFETIME
        )
    except ValueError:
        expires_at = time.time() + DEFAULT_TOKEN_LIFETIME
    return token, expires_at


class MetadataHandler(BaseHTTPRequestHandler):
    token: str = ""
    expires_at: float = 0.0
    project_id: str = ""
    debug: bool = False

    def log_message(self, format, *args):
        if self.debug:
            super().log_message(format, *args)

    def _reply(
        self, status: int, body: str | bytes, content_type: str = "application/text"
    ):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(status)
        self.send_header(FLAVOR_HEADER, FLAVOR_VALUE)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict):
        self._reply(status, json.dumps(payload), "application/json")

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path

        # Both google-auth libraries ping the root (or /computeMetadata/v1) and
        # only check for the Metadata-Flavor response header.
        if path in ("/", "/computeMetadata/v1", "/computeMetadata/v1/"):
            return self._reply(200, "computeMetadata/\n")

        if not path.startswith("/computeMetadata/v1/"):
            return self._reply(404, "Not Found\n")

        # The real server refuses requests that could come from a browser.
        if self.headers.get(FLAVOR_HEADER) != FLAVOR_VALUE:
            return self._reply(403, f"Missing {FLAVOR_HEADER}:{FLAVOR_VALUE} header.\n")

        resource = path.removeprefix("/computeMetadata/v1/")
        if resource == "project/project-id":
            return self._reply(200, self.project_id)
        if resource == "universe/universe-domain":
            return self._reply(200, "googleapis.com")
        if resource == "instance/service-accounts/":
            return self._reply(200, "default/\n")

        if resource.startswith("instance/service-accounts/default/"):
            attribute = resource.removeprefix("instance/service-accounts/default/")
            if attribute == "token":
                expires_in = max(int(self.expires_at - time.time()), 0)
                return self._json(
                    200,
                    {
                        "access_token": self.token,
                        "expires_in": expires_in,
                        "token_type": "Bearer",
                    },
                )
            if attribute == "":
                return self._json(
                    200, {"aliases": ["default"], "email": "default", "scopes": SCOPES}
                )
            if attribute == "email":
                return self._reply(200, "default")
            if attribute == "scopes":
                return self._reply(200, "\n".join(SCOPES) + "\n")
            if attribute == "aliases":
                return self._reply(200, "default\n")

        return self._reply(404, "Not Found\n")


def main():
    MetadataHandler.token, MetadataHandler.expires_at = load_token()
    MetadataHandler.project_id = os.environ.get("HEXA_AI_VERTEX_PROJECT_ID", "")
    MetadataHandler.debug = os.environ.get("HEXA_AI_DEBUG", "") == "true"
    server = ThreadingHTTPServer((HOST, PORT), MetadataHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
