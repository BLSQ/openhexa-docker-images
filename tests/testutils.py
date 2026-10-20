import base64
import json
from pathlib import Path

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
