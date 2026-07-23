import http.server
import multiprocessing
import os
import shutil
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
if not os.path.exists(path_to_mount):
    os.makedirs(path_to_mount, mode=0o777, exist_ok=True)
    # This script is ran as root in the infra. We need to change the ownership to jovyan
    shutil.chown(path_to_mount, user="jovyan", group="users")


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
        "rw",
        "--implicit-dirs",  # Also create implicit directories structure (i.e. key /a/b/c/d will create /a, /a/b, /a/b/c)
        "--uid=1000",  # jovyan user id
        "--gid=100",  # users group id
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
elif STORAGE_ENGINE_TYPE == "azure":
    account_name = os.environ.get("WORKSPACE_STORAGE_ENGINE_AZURE_ACCOUNT_NAME", None)
    token = os.environ.get("WORKSPACE_STORAGE_ENGINE_AZURE_STORAGE_SAS_TOKEN", None)
    if not token or not account_name:
        raise ValueError(
            "No WORKSPACE_STORAGE_ENGINE_AZURE_STORAGE_SAS_TOKEN or WORKSPACE_STORAGE_ENGINE_AZURE_ACCOUNT_NAME environment variable set"
        )

    os.environ["AZURE_STORAGE_ACCOUNT"] = account_name
    os.environ["AZURE_STORAGE_ACCOUNT_CONTAINER"] = WORKSPACE_BUCKET_NAME
    os.environ["AZURE_STORAGE_AUTH_TYPE"] = "SAS"
    os.environ["AZURE_STORAGE_SAS_TOKEN"] = token
    command = [
        "blobfuse2",
        "mount",
        path_to_mount,
        "--tmp-path",
        "/tmp/blobfuse",
        "-o",
        "attr_timeout=240",
        "-o",
        "entry_timeout=240",
        "-o",
        "negative_timeout=120",
        "-o",
        "allow_other",
    ]

    results = subprocess.run(command)

elif STORAGE_ENGINE_TYPE == "s3":
    # tldr: dont use putenv https://docs.python.org/2/library/os.html#os.environ
    # Only export credentials that are actually set: the session token is only
    # provided when the app uses STS assume-role, and s3fs exits with "session
    # token is invalid" if AWSSESSIONTOKEN exists but is empty.
    for source, target in [
        ("WORKSPACE_STORAGE_ENGINE_S3_ACCESS_KEY_ID", "AWSACCESSKEYID"),
        ("WORKSPACE_STORAGE_ENGINE_S3_SECRET_ACCESS_KEY", "AWSSECRETACCESSKEY"),
        ("WORKSPACE_STORAGE_ENGINE_S3_SESSION_TOKEN", "AWSSESSIONTOKEN"),
    ]:
        value = os.environ.get(source)
        if value:
            os.environ[target] = value

    aws_endpoint = os.environ.get("WORKSPACE_STORAGE_ENGINE_S3_ENDPOINT_URL", "")
    # A custom endpoint means MinIO (or another S3 clone), unless it points to
    # real AWS, which some deployments set explicitly.
    s3_is_minio = bool(aws_endpoint) and ".amazonaws.com" not in aws_endpoint

    command = [
        "s3fs",
        WORKSPACE_BUCKET_NAME,
        path_to_mount,
        "-o",
        "allow_other",
        # Debug
        # "-o",
        # "dbglevel=info",
        # "-f",
        # "-o",
        # "curldbg",
    ]

    if aws_endpoint:
        # Only pass a custom endpoint when one is set (e.g. MinIO); real AWS S3
        # must not receive an empty url.
        command.extend(["-o", "url=" + aws_endpoint])

    if s3_is_minio:
        # MinIO doesn't support the subdomain request style, use the older path request style.
        command.extend(["-o", "use_path_request_style"])

    # print(f"debug fusemount {command}")
    results = subprocess.run(command)
    results.check_returncode()

elif STORAGE_ENGINE_TYPE == "local":
    # Nothing to do as the workspace is already mounted
    pass
