#!/usr/bin/env python
import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

import papermill as pm
import requests
from openhexa.sdk import workspace
from openhexa.sdk.pipelines import download_pipeline, import_pipeline


def run_pipeline(config):
    if os.getenv("HEXA_PIPELINE_TYPE", "zipFile") == "notebook":
        notebook_path = Path(workspace.files_path) / os.environ["HEXA_NOTEBOOK_PATH"]
        if not notebook_path.exists():
            print(f"{notebook_path} not found", file=sys.stderr)
            sys.exit(1)

        output_path = notebook_path.parent.absolute() / ".runs_outputs"
        output_path.mkdir(exist_ok=True)
        return pm.execute_notebook(
            input_path=notebook_path,
            output_path=output_path / notebook_path.name,
        )
    else:
        if not os.path.exists("pipeline/pipeline.py"):
            print("No pipeline found", file=sys.stderr)
            sys.exit(1)

        if os.path.exists("./pipeline/requirements.txt"):
            print("Installing requirements...")
            os.system("pip install -r ./pipeline/requirements.txt")

        installed, uninstalled = version_info()
        if len(installed) > 0:
            print("Using {}".format(", ".join(installed)))
        if len(uninstalled) > 0:
            print("Warning, uninstalled libraries: {}".format(", ".join(uninstalled)))

        print("Running pipeline...")
        pipeline = import_pipeline("pipeline")
        pipeline(config=config)


def configure_cloud_run():
    # cloud run -> need to download the code from cloud (except for notebooks as pipeline)
    if "HEXA_TOKEN" not in os.environ or "HEXA_SERVER_URL" not in os.environ:
        print("Need token and url to download the code", file=sys.stderr)
        sys.exit(1)

    access_token = os.environ["HEXA_TOKEN"]
    server_url = os.environ["HEXA_SERVER_URL"]
    workspace_slug = os.environ["HEXA_WORKSPACE"]

    print("Injecting credentials...")
    r = requests.post(
        f"{server_url}/workspaces/credentials/",
        headers={"Authorization": f"Bearer {access_token}"},
        data={"workspace": workspace_slug},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    os.environ.update(data["env"])
    print("Credentials injected.")

    print("Mounting buckets...")
    # setup fuse for buckets
    if os.path.exists("/home/jovyan/.hexa_scripts/fuse_mount.py"):
        # import fuse mount script _after_ env variables injection
        sys.path.insert(1, "/home/jovyan/.hexa_scripts")
        import fuse_mount  # noqa: F401, E402


def version_info():
    installed = []
    uninstalled = []
    for lib in ["openhexa.sdk", "openhexa.toolbox"]:
        completed_process = subprocess.run(
            f"pip freeze | grep {lib}", shell=True, capture_output=True
        )
        lib_version = completed_process.stdout.decode("utf-8").strip()
        if lib_version == "":
            uninstalled.append(lib)
        else:
            installed.append(lib_version)

    return installed, uninstalled


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["cloudrun", "run"])
    parser.add_argument(
        "--config", default=None, help="Pipeline configuration base64 encoded"
    )
    args = parser.parse_args()
    pipeline_config = (
        json.loads(base64.b64decode(args.config).decode("utf-8")) if args.config else {}
    )

    if args.command == "cloudrun":
        configure_cloud_run()
        # cloud run -> need to download the code from cloud (except for notebooks as pipeline)
        if "HEXA_TOKEN" not in os.environ or "HEXA_SERVER_URL" not in os.environ:
            print("Need token and url to download the code", file=sys.stderr)
            sys.exit(1)
        if os.getenv("HEXA_PIPELINE_TYPE", "zipFile") == "zipFile":
            run_id = os.environ["HEXA_RUN_ID"]
            access_token = os.environ["HEXA_TOKEN"]
            server_url = os.environ["HEXA_SERVER_URL"]

            print("Downloading pipeline...")
            os.mkdir("pipeline")

            download_pipeline(
                server_url,
                access_token,
                run_id,
                "pipeline",
            )

            print("Pipeline downloaded.")

    try:
        run_pipeline(pipeline_config)
        print("Pipeline completed.")
    except Exception as e:
        print(f"Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)
