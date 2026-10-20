"""Drive JupyterLab in headless Chromium against the image under test.

These catch problems that only show in the browser, such as a JupyterLab
extension whose frontend bundle fails to load against the JupyterLab version of
the image (the server-side `jupyter labextension list` still reports it OK).
"""

import json
import re

import pytest

pytestmark = pytest.mark.ui

# Console messages JupyterLab prints when an extension's frontend fails to
# load or activate.
EXTENSION_FAILURES = re.compile(
    r"Failed to create module|Plugin .* failed to activate|Error: No provider for"
)
# JupyterLab's own bundles and the federated extensions' remoteEntry bundles.
# A 404 there is an extension whose frontend is missing; other HTTP errors are
# noise (the git extension's 500 when the server root is no repository).
LAB_ASSET = re.compile(r"/(static|lab/extensions)/")


def test_jupyterlab_extensions_load(lab_page):
    failures = [m for m in lab_page.console_messages if EXTENSION_FAILURES.search(m)]
    failures += [e for e in lab_page.http_errors if LAB_ASSET.search(e)]
    assert not failures, "Extensions failed to load:\n" + "\n".join(failures)


def test_notebook_runs_a_cell(jupyterlab, lab_page):
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "id": "c1",
                "metadata": {},
                "outputs": [],
                "source": "print('ui ' + str(6 * 7))",
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    jupyterlab.put_file("ui_test.ipynb", json.dumps(notebook))

    lab_page.locator(".jp-DirListing-item", has_text="ui_test.ipynb").dblclick()
    panel = lab_page.locator(".jp-NotebookPanel:visible")
    panel.locator(".jp-Notebook").wait_for(timeout=60_000)
    # Wait for the kernel before running, or the run request is dropped.
    panel.locator(".jp-Notebook-ExecutionIndicator[data-status='idle']").wait_for(
        timeout=120_000
    )
    panel.locator(".jp-Cell").first.click()
    # The toolbar button, rather than Shift+Enter: keyboard focus after the
    # click differs between JupyterLab versions.
    panel.locator("[data-command='notebook:run-cell-and-select-next']").click()
    panel.locator(".jp-OutputArea-output", has_text="ui 42").wait_for(timeout=120_000)
