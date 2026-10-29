from pathlib import Path

from tests.testutils import run_local_pipeline, run_profiled_pipeline

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


def test_fiona_import_success(docker_image):
    logs = run_local_pipeline(docker_image, pipelines_dir / "fiona_import")

    assert "undefined symbol: sqlite3_total_changes64" not in logs
    assert "fiona imported successfully" in logs

def test_profiled_pipeline(docker_image):
    run = run_profiled_pipeline(docker_image, pipelines_dir / "profiled")

    assert run.exit_code == 0
    assert "Profile saved to /tmp/hexa_profile.txt" in run.logs

    def processes(frames):
        return [f for f in frames if f.startswith("process ")]

    def functions(frames):
        return [f.split(" (")[0] for f in frames if not f.startswith("process ")]

    assert any(len(processes(frames)) == 1 for frames, _ in run.stacks)
    worker_busy = sum(
        count
        for frames, count in run.stacks
        if "spawn_main" in processes(frames)[-1]
        and functions(frames)[-2:] == ["burn_cpu", "busy_loop"]
    )
    assert worker_busy >= 150, f"{worker_busy} samples in busy_loop, expected ~300"


def test_profiled_pipeline_without_ptrace(docker_image):
    run = run_profiled_pipeline(docker_image, pipelines_dir / "profiled", ptrace=False)

    assert run.exit_code == 0
    assert "Warning: profiler could not start" in run.logs
    assert run.stacks == []


def test_profiled_pipeline_failure(docker_image):
    run = run_profiled_pipeline(
        docker_image, pipelines_dir / "profiled", config={"fail": True}
    )

    assert run.exit_code == 1
    assert "Failing on purpose" in run.logs
    assert "Profile saved to /tmp/hexa_profile.txt" in run.logs
    assert run.stacks


def test_profiled_pipeline_timeout(docker_image):
    """A timed-out run gets SIGTERM: the profile is saved before SIGKILL."""
    run = run_profiled_pipeline(
        docker_image,
        pipelines_dir / "profiled",
        config={"seconds": 600},
        stop_when="Burning CPU...",
    )

    assert run.exit_code == 143  # SIGTERM, not 137 (SIGKILL)
    assert "Profile saved to /tmp/hexa_profile.txt" in run.logs
    assert run.stacks
