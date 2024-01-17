import base64
import json
import os
import subprocess

# Git plugin / deactivate if no feature flag
# TODO: this has nothing to do with Fuse, this file should be reworked
if not os.environ.get("GIT_EXTENSION_ENABLED", "false") == "true":
    subprocess.run(
        ["/opt/conda/bin/jupyter", "labextension", "disable", "@jupyterlab/git"]
    )

# S3 Fuse
# b64("{}") == b'e30='
aws_fuse_config = json.loads(
    base64.b64decode(os.environ.get("AWS_S3_FUSE_CONFIG", b"e30="))
)

# tldr: dont use putenv https://docs.python.org/2/library/os.html#os.environ
os.environ["AWSACCESSKEYID"] = aws_fuse_config.get("AWS_ACCESS_KEY_ID", "")
os.environ["AWSSECRETACCESSKEY"] = aws_fuse_config.get("AWS_SECRET_ACCESS_KEY", "")
os.environ["AWSSESSIONTOKEN"] = aws_fuse_config.get("AWS_SESSION_TOKEN", "")
aws_endpoint = aws_fuse_config.get("AWS_ENDPOINT", "")
s3_is_minio = True if aws_endpoint else False

for bucket in filter(None, aws_fuse_config.get("buckets", [])):
    path_to_mount = f"/home/jovyan/s3-{bucket['name']}"
    region_url = (
        aws_endpoint
        if aws_endpoint
        else f"https://s3-{bucket['region']}.amazonaws.com/"
    )
    subprocess.run(["mkdir", "-p", path_to_mount])
    subprocess.run(
        [
            "s3fs",
            bucket["name"],
            path_to_mount,
            "-o",
            "allow_other",
            "-o",
            "url=" + region_url,
            # Debug
            # "-o",
            # "dbglevel=info",
            # "-f",
            # "-o",
            # "curldbg",
        ]
        + (["-o", "ro"] if bucket["mode"] == "RO" else [])
        # MinIO doesn't support the subdomain request style, use the older path request style.
        + (["-o", "use_path_request_style"] if s3_is_minio else [])
    )
