import base64
import io
import json
import tarfile
import time
from collections import Counter
from pathlib import Path
from typing import NamedTuple

import docker
from colorist import effect_dim, effect_underline


def run_local_pipeline(
    docker_image: str,
    pipeline_dir: Path,
    environment: dict[str, str] = {},
    config: dict[str, str] = {},
):
    client = docker.from_env()
    try:
        command = ["pipeline", "run"]
        if config:
            command.append("--config")
            command.append(
                base64.b64encode(json.dumps(config).encode("utf-8")).decode("utf-8")
            )

        logs = client.containers.run(
            docker_image,
            command=command,
            volumes={pipeline_dir: {"bind": "/home/hexa/pipeline"}},
            environment={"HEXA_ENVIRONMENT": "LOCAL_PIPELINE", **environment},
            stdout=True,
            stderr=True,
            remove=True,
        )
        logs = logs.decode("utf-8")

        # Print logs to console in gray color
        print("\n")
        effect_underline("Pipeline logs")
        effect_dim(logs)

        return logs
    finally:
        client.close()


def run_in_image(
    docker_image: str,
    script: str,
    environment: dict[str, str] | None = None,
) -> str:
    """Run a bash script inside the image, bypassing the OpenHEXA entrypoint,
    and return its combined stdout and stderr. A non-zero exit raises a
    RuntimeError carrying that output, so the failure can be read from the
    test report. The container is removed either way."""
    client = docker.from_env()
    try:
        container = client.containers.create(
            docker_image,
            command=["bash", "-c", script],
            entrypoint=[],
            environment=environment or {},
        )
        try:
            container.start()
            status = container.wait()["StatusCode"]
            logs = container.logs(stdout=True, stderr=True).decode("utf-8", "replace")
        finally:
            container.remove(force=True)
        print("\n")
        effect_underline("Container logs")
        effect_dim(logs)
        if status != 0:
            raise RuntimeError(
                f"script exited with status {status} in {docker_image}:\n{logs}"
            )
        return logs
    finally:
        client.close()


class ProfiledRun(NamedTuple):
    exit_code: int
    logs: str
    # py-spy's Chrome trace: "B" and "E" events when a frame enters and leaves
    # the stack of a thread. With --subprocesses, each process in the chain
    # adds a `process <pid>:"<command>"` frame. Empty when no profile was
    # saved.
    events: list[dict]


def run_profiled_pipeline(
    docker_image: str,
    pipeline_dir: Path,
    config: dict[str, str] = {},
    ptrace: bool = True,
    stop_when: str | None = None,
) -> ProfiledRun:
    """Run a pipeline with HEXA_PROFILE=true, with SYS_PTRACE unless `ptrace`
    is False, and return its exit code, logs and profile. With `stop_when`,
    stop it (SIGTERM, SIGKILL 30s later, as Kubernetes does) once that text is
    in its logs."""
    client = docker.from_env()
    try:
        command = ["pipeline", "run"]
        if config:
            command.append("--config")
            command.append(
                base64.b64encode(json.dumps(config).encode("utf-8")).decode("utf-8")
            )

        # Created rather than run, to read the profile before removing it
        container = client.containers.create(
            docker_image,
            command=command,
            volumes={pipeline_dir: {"bind": "/home/hexa/pipeline"}},
            environment={"HEXA_ENVIRONMENT": "LOCAL_PIPELINE", "HEXA_PROFILE": "true"},
            cap_add=["SYS_PTRACE"] if ptrace else [],
        )
        try:
            container.start()
            if stop_when:
                while stop_when not in container.logs().decode("utf-8"):
                    time.sleep(0.5)
                container.stop(timeout=30)
            exit_code = container.wait()["StatusCode"]
            logs = container.logs().decode("utf-8")
            events = read_profile(container)
        finally:
            container.remove(force=True)

        print("\n")
        effect_underline(f"Pipeline logs (exit code {exit_code})")
        effect_dim(logs)
        print_profile_summary(events)
        return ProfiledRun(exit_code, logs, events)
    finally:
        client.close()


def read_profile(container) -> list[dict]:
    try:
        stream, _ = container.get_archive("/tmp/hexa_profile.json")
    except docker.errors.NotFound:
        return []
    with tarfile.open(fileobj=io.BytesIO(b"".join(stream))) as tar:
        raw = tar.extractfile(tar.getmembers()[0]).read().decode("utf-8", "replace")
    return json.loads(raw)


def frame_times(events: list[dict]) -> Counter:
    """Return the seconds spent in each (pid, frame name), callees included."""
    stacks, times = {}, Counter()
    for event in events:
        stack = stacks.setdefault((event["pid"], event["tid"]), [])
        if event["ph"] == "B":
            stack.append((event["name"], event["ts"]))
        elif stack:
            name, start = stack.pop()
            times[(event["pid"], name)] += (event["ts"] - start) / 1e6
    return times


def process_names(events: list[dict]) -> dict[int, str]:
    return {
        event["pid"]: event["name"]
        for event in events
        if event["ph"] == "B" and event["name"].startswith(f"process {event['pid']}:")
    }


def print_profile_summary(events: list[dict], top: int = 10):
    """Print the functions that took the most time, per process."""
    names = process_names(events)
    times = frame_times(events)
    effect_underline(f"Profile: {len(events)} events")
    effect_dim(
        "\n".join(
            f"{seconds:>7.2f}s  {name}  ({names.get(pid, pid)[:60]})"
            for (pid, name), seconds in times.most_common(top)
        )
    )
