"""Jupyternaut in the chat panel, driven in Chromium: the whole chain from the
chat input through the persona manager, Jupyternaut's agent and litellm to the
OpenHEXA assistant gateway (tests/fake_gateway.py, inside the container).

The server-side checks in test_jupyter_ai.py call litellm directly with the
parameters Jupyternaut saves; they cannot tell when Jupyternaut's own path to
the model breaks, such as a litellm release whose tool-calling code needs a
package version the rest of the stack cannot have.
"""

import time

import pytest

from . import fake_gateway

pytestmark = pytest.mark.ui


def send_chat_message(page, text: str):
    """Open the chat side panel, start a new chat, send `text` and return the
    locator of the chat messages."""
    page.locator(".jp-SideBar .lm-TabBar-tab[data-id='JupyterlabChat:sidepanel']").click()
    panel = page.locator(".jp-chat-sidepanel")
    panel.locator(".jp-chat-add").first.click()
    # MUI renders a hidden second textarea to size the visible one.
    textarea = panel.locator(".jp-chat-input-container textarea").first
    textarea.wait_for(timeout=30_000)
    # Jupyternaut, the only persona, is preselected in the input toolbar.
    panel.locator(".jp-jai-personaControls-persona", has_text="Jupyternaut").wait_for(
        timeout=30_000
    )
    textarea.fill(text)
    textarea.press("Enter")
    messages = panel.locator(".jp-chat-message")
    messages.filter(has_text=text).first.wait_for(timeout=30_000)
    return messages


def wait_for_reply(messages, expected: str, timeout: float = 120) -> str:
    """Wait until Jupyternaut's reply contains `expected` and return it. An
    error reply fails at once, with its text, rather than at the timeout."""
    deadline = time.monotonic() + timeout
    while True:
        reply = messages.filter(has_text="Jupyternaut").last
        text = (
            reply.locator(".jp-chat-rendered-message").inner_text()
            if reply.count()
            else ""
        )
        if expected in text:
            return text
        if text.startswith("Error:"):
            pytest.fail(f"Jupyternaut answered with an error:\n{text}")
        if time.monotonic() > deadline:
            pytest.fail(f"no reply containing {expected!r} after {timeout}s; got:\n{text}")
        time.sleep(0.5)


def test_jupyternaut_answers_through_the_gateway(jupyterlab_with_gateway, open_lab):
    page = open_lab(jupyterlab_with_gateway)
    messages = send_chat_message(page, "hi")

    wait_for_reply(messages, fake_gateway.REPLY)

    # The gateway got the workspace token and the configured model, and the
    # agent's tools (Jupyternaut without its notebook tools would be a loss).
    requests = fake_gateway.requests_received(jupyterlab_with_gateway.logs())
    assert requests, "the gateway received no request"
    request = requests[-1]
    assert request["path"] == "/assistant/gateway/v1/chat/completions"
    assert request["authorization"] == f"Bearer {fake_gateway.TOKEN}"
    assert request["model"] == fake_gateway.MODEL
    assert request["stream"] is True
    assert request["messages"][-1] == {"role": "user", "content": "hi"}, request["messages"]
    assert request["messages"][0]["role"] == "system", request["messages"]
    assert request["tools"], "Jupyternaut sent no tools"


def test_jupyternaut_asks_for_a_model_without_the_variables(lab_page):
    """Without HEXA_AI_* nothing is configured: Jupyternaut must say so rather
    than fail, and the user can then pick a model with their own key."""
    messages = send_chat_message(lab_page, "hi")
    wait_for_reply(messages, "No chat model is configured")
