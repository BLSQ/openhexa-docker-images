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
# JupyterLab's own bundles and the federated extensions' remoteEntry bundles;
# a 404 there is an extension whose frontend is missing.
LAB_ASSET = re.compile(r"/(static|lab/extensions)/")
EXTENSION_BUNDLE = re.compile(r"/lab/extensions/(.+?)/static/")


def test_jupyterlab_extensions_load(lab_page):
    failures = [m for m in lab_page.console_messages if EXTENSION_FAILURES.search(m)]
    failures += [e for e in lab_page.http_errors if LAB_ASSET.search(e)]
    assert not failures, "Extensions failed to load:\n" + "\n".join(failures)
    # Every extension the server advertises to the page had its bundle fetched.
    config = json.loads(lab_page.locator("#jupyter-config-data").text_content())
    advertised = {e["name"] for e in config["federated_extensions"]}
    loaded = {
        match.group(1)
        for url, status in lab_page.responses.items()
        if status == 200 and (match := EXTENSION_BUNDLE.search(url))
    }
    assert advertised, "the page lists no federated extensions"
    assert advertised <= loaded, f"bundles not fetched: {advertised - loaded}"


# A cell per kernel, with the output it must print.
CELLS = {
    "python3": ("print('ui ' + str(6 * 7))", "ui 42"),
    "ir": ("cat('ui', 6 * 7)", "ui 42"),
}
KERNELSPECS = {
    "python3": {"display_name": "Python 3 (ipykernel)", "language": "python"},
    "ir": {"display_name": "R", "language": "R"},
}


@pytest.mark.parametrize("kernel", ["python3", "ir"])
def test_notebook_runs_a_cell(jupyterlab, lab_page, image_flavor, kernel):
    if kernel == "ir" and image_flavor == "base":
        pytest.skip("the base image has no R kernel")
    source, expected = CELLS[kernel]
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "id": "c1",
                "metadata": {},
                "outputs": [],
                "source": source,
            }
        ],
        "metadata": {"kernelspec": {**KERNELSPECS[kernel], "name": kernel}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    name = f"ui_test_{kernel}.ipynb"
    jupyterlab.put_file(name, json.dumps(notebook))

    lab_page.locator(".jp-DirListing-item", has_text=name).dblclick()
    panel = lab_page.locator(".jp-NotebookPanel:visible")
    panel.locator(".jp-Notebook").wait_for(timeout=60_000)
    # Wait for the kernel before running, or the run request is dropped.
    jupyterlab.wait_for_kernel(name)
    panel.locator(".jp-Cell").first.click()
    # The toolbar button, rather than Shift+Enter: keyboard focus after the
    # click differs between JupyterLab versions.
    panel.locator("[data-command='notebook:run-cell-and-select-next']").click()
    # When the kernel session is not attached yet (seen on a loaded machine),
    # JupyterLab asks which kernel to use; the preselected one is the right one.
    dialog = lab_page.locator(".jp-Dialog", has_text="Select Kernel")
    if dialog.is_visible():
        dialog.get_by_role("button", name="Select").click()
    panel.locator(".jp-OutputArea-output", has_text=expected).wait_for(timeout=120_000)
