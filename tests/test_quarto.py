"""Quarto support: the CLI, jupytext and the JupyterLab settings that make .qmd
files open as notebooks. Everything runs inside the image under test."""

import json

from .testutils import run_in_image


def test_quarto_and_jupytext_installed(docker_image):
    out = run_in_image(docker_image, "quarto --version && jupytext --version")
    quarto_version, jupytext_version = out.strip().splitlines()[-2:]
    assert quarto_version.startswith("1.")
    assert jupytext_version.startswith("1.")


def test_quarto_extensions_registered(docker_image):
    out = run_in_image(docker_image, "jupyter labextension list 2>&1")
    assert "jupyterlab-quarto" in out
    assert "jupyterlab-jupytext" in out


def test_qmd_opens_as_notebook_by_default(docker_image):
    """The JupyterLab settings shipped with the image make Notebook the default
    viewer of the jupytext "quarto" file type and list Quarto Notebook in the
    launcher."""
    out = run_in_image(
        docker_image, "cat /opt/conda/share/jupyter/lab/settings/overrides.json"
    )
    overrides = json.loads(out[out.index("{") :])
    viewers = overrides["@jupyterlab/docmanager-extension:plugin"]["defaultViewers"]
    assert viewers["quarto"] == "Notebook"
    assert overrides["jupyterlab-jupytext:plugin"]["qmd"] is True


def test_qmd_round_trip(docker_image):
    """A .qmd file converts to a notebook and back with jupytext, as opening it
    in JupyterLab does."""
    script = r"""
set -e
cd /tmp
cat > doc.qmd <<'QMD'
---
title: "Test"
---

## A heading

```{python}
print(1 + 1)
```
QMD
jupytext --to ipynb doc.qmd > /dev/null
python -c "
import nbformat
nb = nbformat.read('doc.ipynb', as_version=4)
cells = [(c.cell_type, c.source) for c in nb.cells]
assert ('code', 'print(1 + 1)') in cells, cells
print('cells ok')
"
"""
    out = run_in_image(docker_image, script)
    assert "cells ok" in out


def test_quarto_render(docker_image):
    """quarto render executes the Python cells of a .qmd through Jupyter."""
    script = r"""
set -e
cd /tmp
cat > doc.qmd <<'QMD'
---
title: "Render"
format: html
jupyter: python3
---

```{python}
print("rendered " + str(6 * 7))
```
QMD
quarto render doc.qmd --quiet
grep -o "rendered 42" doc.html | head -1
"""
    out = run_in_image(docker_image, script)
    assert "rendered 42" in out
