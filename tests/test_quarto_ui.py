"""Quarto in JupyterLab, driven in Chromium: a .qmd file opens as a notebook on
double-click, and the launcher offers a Quarto Markdown notebook. The server-side
checks in test_quarto.py cannot tell when the jupytext frontend fails to load,
which is what happens when it was built for another JupyterLab minor version."""

import re

import pytest

pytestmark = pytest.mark.ui

QMD = """---
title: "UI test"
---

## A heading

```{python}
print(1 + 1)
```
"""

JUPYTEXT_CONSOLE = re.compile(r"jupytext", re.IGNORECASE)


def dump_diagnostics(lab_page, tmp_path, name):
    screenshot = tmp_path / f"{name}.png"
    lab_page.screenshot(path=str(screenshot))
    print(f"Screenshot of the failure: {screenshot}")
    jupytext = [m for m in lab_page.console_messages if JUPYTEXT_CONSOLE.search(m)]
    if jupytext:
        print("Browser console messages mentioning jupytext:\n" + "\n".join(jupytext))


def test_qmd_opens_as_notebook_on_double_click(jupyterlab, lab_page, tmp_path):
    jupyterlab.put_file("quarto_ui.qmd", QMD)

    lab_page.locator(".jp-DirListing-item", has_text="quarto_ui.qmd").dblclick()
    panel = lab_page.locator(".jp-NotebookPanel:visible")
    try:
        panel.locator(".jp-CodeCell", has_text="print(1 + 1)").wait_for(timeout=60_000)
        panel.locator(".jp-MarkdownCell", has_text="A heading").wait_for(timeout=10_000)
    except Exception:
        dump_diagnostics(lab_page, tmp_path, "qmd_double_click")
        raise
    # The notebook is the .qmd file itself (jupytext), not a converted copy.
    lab_page.locator(
        "#jp-main-dock-panel .lm-TabBar-tabLabel", has_text="quarto_ui.qmd"
    ).wait_for(timeout=10_000)
    assert lab_page.locator(".jp-FileEditor:visible").count() == 0, (
        "the .qmd file opened in the text editor"
    )


def test_launcher_offers_quarto_notebook(lab_page, tmp_path):
    """jupytext adds a launcher card per enabled format; overrides.json enables
    the Quarto one."""
    lab_page.locator(".jp-FileBrowser-toolbar [data-command='launcher:create']").click()
    card = lab_page.locator(".jp-Launcher:visible .jp-LauncherCard[title*='Quarto']")
    try:
        card.wait_for(timeout=30_000)
    except Exception:
        dump_diagnostics(lab_page, tmp_path, "launcher")
        raise
