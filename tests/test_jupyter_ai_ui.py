import time

import pytest

from . import fake_gateway

pytestmark = pytest.mark.ui


def send_chat_message(page, text: str):
    page.locator(".jp-SideBar .lm-TabBar-tab[data-id='JupyterlabChat:sidepanel']").click()
    panel = page.locator(".jp-chat-sidepanel")
    panel.locator(".jp-chat-add").first.click()
    # MUI renders a hidden second textarea to size the visible one.
    textarea = panel.locator(".jp-chat-input-container textarea").first
    textarea.wait_for(timeout=30_000)
    panel.locator(".jp-jai-personaControls-persona", has_text="Jupyternaut").wait_for(
        timeout=30_000
    )
    textarea.fill(text)
    textarea.press("Enter")
    messages = panel.locator(".jp-chat-message")
    messages.filter(has_text=text).first.wait_for(timeout=30_000)
    return messages


def wait_for_reply(messages, expected: str, timeout: float = 120) -> str:
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
    messages = send_chat_message(lab_page, "hi")
    wait_for_reply(messages, "No chat model is configured")
