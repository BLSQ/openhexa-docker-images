"""Template for newly generated pipelines."""

from openhexa.sdk import current_run, parameter, pipeline


@pipeline("multiply_by_two")
@parameter("number", type=int, default=42)
def multiply_by_two(number: int):
    """Write your pipeline orchestration here.

    Pipeline functions should only call tasks and should never perform IO operations or expensive computations.
    """
    result = task_1(number)
    task_2(number, result)


@multiply_by_two.task
def task_1(number: int):
    current_run.log_info("Multiplying by two...")

    return number * 2


@multiply_by_two.task
def task_2(number: int, result: int):
    current_run.log_info(f"{number} * 2 = {result}")


if __name__ == "__main__":
    multiply_by_two()
