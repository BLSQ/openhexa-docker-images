from pathlib import Path

from tests.testutils import run_local_pipeline

# Get the pipelines directory
pipelines_dir = Path(__file__).parent / "pipelines"


def test_multiply_by_two_success(docker_image):
    logs = run_local_pipeline(docker_image, pipelines_dir / "multiply_by_two")

    assert "Multiplying by two..." in logs
    assert "42 * 2 = 84" in logs

    logs = run_local_pipeline(
        docker_image, pipelines_dir / "multiply_by_two", config={"number": 43}
    )
    assert "Multiplying by two..." in logs
    assert "43 * 2 = 86" in logs


def test_pandas_to_sql_success(docker_image):
    logs = run_local_pipeline(docker_image, pipelines_dir / "pandas_to_sql")

    assert "undefined symbol: sqlite3_deserialize" not in logs
    assert "to_sql succeeded" in logs
