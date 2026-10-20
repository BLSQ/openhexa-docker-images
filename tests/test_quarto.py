"""Quarto support: the CLI, jupytext and the JupyterLab settings that make .qmd
files open as notebooks. Everything runs inside the image under test."""

import json
import re

from .testutils import run_in_image


def test_quarto_and_jupytext_installed(docker_image):
    # Label each version on its own line: the output also carries stderr.
    out = run_in_image(
        docker_image,
        'echo "quarto=$(quarto --version)"; echo "jupytext=$(jupytext --version)"',
    )
    versions = dict(re.findall(r"^(quarto|jupytext)=(\S+)$", out, re.MULTILINE))
    assert versions.get("quarto", "").startswith("1."), out
    assert versions.get("jupytext", "").startswith("1."), out


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
quarto render doc.qmd
grep -o "rendered 42" doc.html | head -1
"""
    out = run_in_image(docker_image, script)
    assert "rendered 42" in out
