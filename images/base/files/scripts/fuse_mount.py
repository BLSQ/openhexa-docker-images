import http.server
import multiprocessing
import os
import subprocess
import time

# GCS Fuse
# gcsfuse offers 2 choices to authenticate:
# 1) using a 'JSON key file', with static credentials
# 2) using a token (that can be a short-lived one) served over HTTP
# So we span an HTTP server to use the second option.
# Yes, it's strange, but unless we want to fork gcsfuse, we will have to live with this
GCS_TOKEN = os.environ.get("GCS_TOKEN", "")
WORKSPACE_BUCKET_NAME = os.environ.get("WORKSPACE_BUCKET_NAME", "")

if GCS_TOKEN and WORKSPACE_BUCKET_NAME:

    class serveGCStoken(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes('{ "access_token": "' + GCS_TOKEN + '" }', "utf-8"))

    webServer = http.server.HTTPServer(("127.0.0.1", 4321), serveGCStoken)
    proc = multiprocessing.Process(target=webServer.serve_forever, args=())
    proc.start()
    time.sleep(0.5)

    path_to_mount = "/home/jovyan/workspace"
    subprocess.run(["mkdir", "-p", path_to_mount], check=True)
    args = [
        "gcsfuse",
        "-o",
        "allow_other",
        "--implicit-dirs",  # Also create implicit directories structure (i.e. key /a/b/c/d will create /a, /a/b, /a/b/c)
    ]

    # Use the custom token server to get the token
    args.extend(
        ["--token-url", "http://127.0.0.1:4321/", WORKSPACE_BUCKET_NAME, path_to_mount]
    )
    try:
        subprocess.run(args, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        raise
    finally:
        proc.terminate()
        time.sleep(0.5)
        proc.close()
