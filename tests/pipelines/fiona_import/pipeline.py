"""Regression test: importing `fiona` must not crash on a libgdal/libsqlite3 symbol mismatch.

    File ".../fiona/__init__.py", line 42, in <module>
        from fiona._env import (
    ...
    ImportError: .../fiona/../../../libgdal.so.36:
        undefined symbol: sqlite3_total_changes64

The conda libgdal.so.36 was linked against a newer libsqlite3 than the one present at
runtime, so importing fiona (which loads libgdal) fails with
undefined symbol: sqlite3_total_changes64 (a symbol added in SQLite 3.37).

This is the same class of bug as `pandas_to_sql` (an outdated libsqlite3), but surfaces
through the GDAL stack. Real pipelines hit it via
`from openhexa.toolbox.iaso import dataframe`, which imports fiona at module load time.
"""

# Import at module level so the failure surfaces during pipeline import, exactly as it
# does in a real pipeline (`from openhexa.toolbox.iaso import dataframe` -> `import fiona`).
import fiona  # noqa: F401
from openhexa.sdk import current_run, pipeline


@pipeline("fiona_import")
def fiona_import():
    check_fiona()


@fiona_import.task
def check_fiona():
    current_run.log_info(f"fiona imported successfully (version {fiona.__version__})")


if __name__ == "__main__":
    fiona_import()
