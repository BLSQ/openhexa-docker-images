"""Regression test: `pandas.DataFrame.to_sql` must not crash on import of the sqlite3 module.

    File ".../pandas/io/sql.py", line 897, in pandasSQL_builder
        import sqlite3
    ...
    ImportError: .../_sqlite3.cpython-313-x86_64-linux-gnu.so:
        undefined symbol: sqlite3_deserialize

The conda Python 3.13 _sqlite3 extension (_sqlite3.cpython-313-x86_64-linux-gnu.so) was linked against a newer libsqlite3 than the one present at runtime, so import sqlite3 fails with undefined symbol: sqlite3_deserialize (a symbol added in SQLite 3.23).
"""

import pandas as pd
from openhexa.sdk import current_run, pipeline
from sqlalchemy import create_engine


@pipeline("pandas_to_sql")
def pandas_to_sql():
    write_to_sql()


@pandas_to_sql.task
def write_to_sql():
    current_run.log_info("Writing DataFrame via to_sql...")
    # In-memory SQLite engine keeps the repro hermetic (no external Postgres).
    # A real pipeline will probably use a Postgres engine and fail one frame later, but
    # the root cause is identical: importing sqlite3 / _sqlite3 at runtime.
    engine = create_engine("sqlite://")
    df = pd.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
    df.to_sql("vaccine_forma_clean", if_exists="replace", con=engine)
    current_run.log_info("to_sql succeeded")


if __name__ == "__main__":
    pandas_to_sql()
