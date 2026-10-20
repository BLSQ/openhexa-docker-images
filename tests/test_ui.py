"""Drive JupyterLab in headless Chromium against the image under test.

These catch problems that only show in the browser, such as a JupyterLab
extension whose frontend bundle fails to load against the JupyterLab version of
the image (the server-side `jupyter labextension list` still reports it OK).
"""

import json
import re

import pytest

pytestmark = pytest.mark.ui

# Console messages JupyterLab prints when an extension's frontend fails to load
# or activate.
EXTENSION_FAILURES = re.compile(
    r"Failed to create module|Failed to load|Plugin .* failed to activate|"
    r"Error: No provider for"
)
# Known noise, unrelated to extension loading: the git extension probing a
# directory that is no repository, and the 500 response it gets for that.
NOISE = re.compile(r"Fail to find Git top level|Failed to load resource")


def test_jupyterlab_extensions_load(lab_page):
    failures = [
        m
        for m in lab_page.console_messages
        if EXTENSION_FAILURES.search(m) and not NOISE.search(m)
    ]
    assert not failures, "Extensions failed to load:\n" + "\n".join(failures)


def test_notebook_runs_a_cell(jupyterlab, lab_page, tmp_path):
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
    lab_page.locator(".jp-Notebook-ExecutionIndicator[data-status='idle']").wait_for(
        timeout=120_000
    )
    panel.locator(".jp-Cell").first.click()
    # The toolbar button, rather than Shift+Enter: keyboard focus after the
    # click differs between JupyterLab versions.
    panel.locator("[data-command='notebook:run-cell-and-select-next']").click()
    output = panel.locator(".jp-OutputArea-output", has_text="ui 42")
    try:
        output.wait_for(timeout=120_000)
    except Exception:
        screenshot = tmp_path / "notebook_runs_a_cell.png"
        lab_page.screenshot(path=str(screenshot))
        print(f"Screenshot of the failure: {screenshot}")
        raise
