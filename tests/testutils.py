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
        )
        logs = logs.decode("utf-8")

        # Print logs to console in gray color
        print("\n")
        effect_underline("Pipeline logs")
        effect_dim(logs)

        return logs
    finally:
        client.close()
