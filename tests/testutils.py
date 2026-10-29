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
    # py-spy's raw profile, one (frames, sample count) per stack, outermost
    # frame first; with --subprocesses, each process in the chain adds a
    # `process <pid>:"<command>"` frame. Empty when no profile was saved.
    stacks: list[tuple[list[str], int]]


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
            stacks = read_profile(container)
        finally:
            container.remove(force=True)

        print("\n")
        effect_underline(f"Pipeline logs (exit code {exit_code})")
        effect_dim(logs)
        print_profile_summary(stacks)
        return ProfiledRun(exit_code, logs, stacks)
    finally:
        client.close()


def read_profile(container) -> list[tuple[list[str], int]]:
    try:
        stream, _ = container.get_archive("/tmp/hexa_profile.txt")
    except docker.errors.NotFound:
        return []
    with tarfile.open(fileobj=io.BytesIO(b"".join(stream))) as tar:
        raw = tar.extractfile(tar.getmembers()[0]).read().decode("utf-8", "replace")
    stacks, line = [], ""
    for part in raw.splitlines():
        line += part
        frames, _, count = line.rpartition(" ")
        if count.isdigit():
            stacks.append((frames.split(";"), int(count)))
            line = ""
        else:
            line += "\n"
    return stacks


def print_profile_summary(stacks: list[tuple[list[str], int]], top: int = 10):
    """Print the samples per process and the functions they were taken in."""
    processes, functions = Counter(), Counter()
    for frames, count in stacks:
        processes[[f for f in frames if f.startswith("process ")][-1][:100]] += count
        functions[frames[-1]] += count
    effect_underline(f"Profile: {sum(processes.values())} samples")
    effect_dim(
        "\n".join(
            ["Samples per process:"]
            + [f"{n:>7}  {p}" for p, n in processes.most_common()]
            + [f"Top {top} functions sampled:"]
            + [f"{n:>7}  {f}" for f, n in functions.most_common(top)]
        )
    )
