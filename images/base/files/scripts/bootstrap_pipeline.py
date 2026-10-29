#!/usr/bin/env python
import argparse
import base64
import json
import os
import shutil
import signal
import subprocess
import sys
import traceback
from pathlib import Path

import papermill as pm
import requests
from openhexa.sdk import workspace
from openhexa.sdk.pipelines import download_pipeline, import_pipeline

# py-spy writes the profile here when it stops (HEXA_PROFILE=true)
PROFILE_PATH = "/tmp/hexa_profile.txt"


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


def start_profiler():
    """Sample this process and its subprocesses (task pool workers, papermill
    kernel) with py-spy. Profiling never changes the pipeline's result: any
    failure is only a warning."""
    try:
        return subprocess.Popen(
            ["py-spy", "record", "--pid", str(os.getpid()), "--subprocesses"]
            + ["--idle", "--nonblocking", "--format", "raw", "-o", PROFILE_PATH]
        )
    except OSError as e:  # EPERM without SYS_PTRACE, see the Dockerfile
        print(f"Warning: profiler could not start: {e}", file=sys.stderr)
        return None


def stop_profiler(profiler, command):
    try:
        profiler.send_signal(signal.SIGINT)  # py-spy writes the file on SIGINT
        profiler.wait(timeout=10)
        path = Path(PROFILE_PATH)
        if not path.exists():
            raise RuntimeError("py-spy wrote no profile")
        if command == "cloudrun":  # the workspace bucket is mounted there
            path = (
                Path(workspace.files_path)
                / ".profiles"
                / f"{os.environ['HEXA_RUN_ID']}.txt"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(PROFILE_PATH, path)
        print(f"Profile saved to {path}")
    except Exception as e:
        profiler.kill()
        print(f"Warning: no profile saved: {e}", file=sys.stderr)


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

    profiler = start_profiler() if os.getenv("HEXA_PROFILE") == "true" else None
    if profiler:
        # A timed-out run gets SIGTERM, then SIGKILL 30s later: save the
        # profile in between. os._exit, as unwinding the task pool can hang.
        def on_sigterm(signum, frame):
            stop_profiler(profiler, args.command)
            os._exit(128 + signum)

        signal.signal(signal.SIGTERM, on_sigterm)
    try:
        run_pipeline(pipeline_config)
        print("Pipeline completed.")
    except Exception as e:
        print(f"Pipeline failed: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
    finally:
        if profiler:  # also for failed runs
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            stop_profiler(profiler, args.command)
