import base64
import http.server
import json
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
STORAGE_ENGINE_TYPE = os.environ.get("WORKSPACE_STORAGE_ENGINE", "gcp")
WORKSPACE_BUCKET_NAME = os.environ.get("WORKSPACE_BUCKET_NAME", "")

if not WORKSPACE_BUCKET_NAME:
    print("No WORKSPACE_BUCKET_NAME environment variable set, skipping Fuse mount")
    exit(0)

path_to_mount = "/home/jovyan/workspace"
subprocess.run(["mkdir", "-p", path_to_mount], check=True)

if STORAGE_ENGINE_TYPE == "gcp":
    access_token = os.environ.get("WORKSPACE_STORAGE_ENGINE_GCP_ACCESS_TOKEN", "")

    class serveGCStoken(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(
                bytes('{ "access_token": "' + access_token + '" }', "utf-8")
            )

    webServer = http.server.HTTPServer(("127.0.0.1", 4321), serveGCStoken)
    proc = multiprocessing.Process(target=webServer.serve_forever, args=())
    proc.start()
    time.sleep(0.5)

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

elif STORAGE_ENGINE_TYPE == "s3":
    # b64("{}") == b'e30='
    fuse_config = json.loads(
        base64.b64decode(
            os.environ.get("WORKSPACE_STORAGE_ENGINE_S3_FUSE_CONFIG", b"e30=")
        )
    )

    # tldr: dont use putenv https://docs.python.org/2/library/os.html#os.environ
    os.environ["AWSACCESSKEYID"] = fuse_config.get("AWS_ACCESS_KEY_ID", "")
    os.environ["AWSSECRETACCESSKEY"] = fuse_config.get("AWS_SECRET_ACCESS_KEY", "")
    os.environ["AWSSESSIONTOKEN"] = fuse_config.get("AWS_SESSION_TOKEN", "")

    aws_endpoint = fuse_config.get("AWS_ENDPOINT", "")
    s3_is_minio = True if aws_endpoint else False

    command = [
        "s3fs",
        WORKSPACE_BUCKET_NAME,
        path_to_mount,
        "-o",
        "allow_other",
        "-o",
        "url=" + aws_endpoint,
        # Debug
        # "-o",
        # "dbglevel=info",
        # "-f",
        # "-o",
        # "curldbg",
    ]

    if s3_is_minio:
        # MinIO doesn't support the subdomain request style, use the older path request style.
        command.extend(["-o", "use_path_request_style"])

    # print(f"debug fusemount {command}")
    results = subprocess.run(command)
