"""Print the User-Agent requests and urllib send, from the main pipeline process
and from a task process, to a local server that echoes it back."""

import http.server
import threading
import urllib.request

import requests
from openhexa.sdk import pipeline


class EchoUserAgent(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = self.headers.get("User-Agent", "").encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def print_user_agents(where: str, port: int):
    url = f"http://127.0.0.1:{port}/"
    print(f"UA {where} requests: {requests.get(url, timeout=10).text}", flush=True)
    with urllib.request.urlopen(url, timeout=10) as response:
        print(f"UA {where} urllib: {response.read().decode()}", flush=True)


@pipeline("user_agent")
def user_agent():
    # Tasks run after this function returns, in processes of the same run; the
    # daemon thread keeps serving until the run ends.
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), EchoUserAgent)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    print_user_agents("main", port)
    send_from_task(port)


@user_agent.task
def send_from_task(port: int):
    print_user_agents("task", port)
