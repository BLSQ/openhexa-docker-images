"""Burns CPU in a known function, for the HEXA_PROFILE tests."""

import time

from openhexa.sdk import current_run, parameter, pipeline


@pipeline("profiled")
@parameter("fail", type=bool, default=False)
@parameter("seconds", type=int, default=3)
def profiled(fail: bool, seconds: int):
    burn_cpu(fail, seconds)


@profiled.task
def burn_cpu(fail: bool, seconds: int):
    current_run.log_info("Burning CPU...")
    busy_loop(seconds)
    if fail:
        raise RuntimeError("Failing on purpose")


def busy_loop(seconds: float):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        pass


if __name__ == "__main__":
    profiled()
