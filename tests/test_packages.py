"""The libraries each image promises can be imported or loaded.

Some installs do not fail the build when a package fails to install (for
example CRAN installs, which only warn), so these catch silent regressions.
"""

import pytest

from .testutils import run_in_image

PYTHON_MODULES = {
    "base": [
        "openhexa.sdk",
        "openhexa.toolbox",
        "pandas",
        "papermill",
        "duckdb",
        "gcsfs",
        "psycopg2",
        # The R stack has broken `import sqlite3` before by downgrading sqlite.
        "sqlite3",
    ],
    "blsq": [
        "geopandas",
        "polars",
        "pyarrow",
        "boto3",
        "rasterstats",
        "xarray",
        "pyodbc",
    ],
    "blsq-r": [],
}

R_PACKAGES = {
    "base": [],
    "blsq": ["IRkernel", "arrow", "sf", "raster", "RPostgres", "GISTools", "OpenStreetMap"],
    "blsq-r": [
        "IRkernel",
        "arrow",
        "sf",
        "raster",
        "RPostgres",
        "tidyverse",
        "reticulate",
        "GISTools",
        "OpenStreetMap",
        "DHS.rates",
    ],
}


def _expected(table, flavor):
    if flavor == "base":
        return table["base"]
    return table["base"] + table[flavor]


def test_python_modules_import(docker_image, image_flavor):
    modules = _expected(PYTHON_MODULES, image_flavor)
    script = "python - <<'PY'\nimport importlib\nmissing = []\n"
    script += f"for name in {modules!r}:\n"
    script += "    try:\n        importlib.import_module(name)\n"
    script += "    except Exception as e:\n        missing.append(f'{name}: {e}')\n"
    script += "print('MISSING ' + ' | '.join(missing) if missing else 'ALL OK')\nPY\n"
    out = run_in_image(docker_image, script)
    assert out.strip().splitlines()[-1] == "ALL OK", out


def test_r_packages_load(docker_image, image_flavor):
    packages = _expected(R_PACKAGES, image_flavor)
    if not packages:
        pytest.skip(f"no R packages expected in the {image_flavor} image")
    vector = ", ".join(f"'{p}'" for p in packages)
    script = f"""Rscript -e "pkgs <- c({vector}); \\
ok <- vapply(pkgs, function(p) suppressWarnings(requireNamespace(p, quietly = TRUE)), logical(1)); \\
cat(if (all(ok)) 'ALL OK' else paste('MISSING', paste(pkgs[!ok], collapse = ', ')), '\\n')" 2>&1
"""
    out = run_in_image(docker_image, script)
    assert out.strip().splitlines()[-1].strip() == "ALL OK", out
