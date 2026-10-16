"""Default model of Jupyter AI's Jupyternaut persona: the OpenHEXA assistant gateway.

Jupyternaut talks to models through litellm. OpenHEXA runs the organization's
model behind an OpenAI-compatible endpoint, the assistant gateway, so the
notebook server holds no model credentials: litellm's "openai" provider is
pointed at $HEXA_SERVER_URL/assistant/gateway/v1 and authenticates with the
workspace token the server already has. OpenHEXA charges the usage to the
organization and traces the calls.

OpenHEXA injects, when the organization's assistant is on:

  HEXA_AI_PROVIDER   "openhexa", meaning the gateway
  HEXA_AI_MODEL      name of the model the gateway runs, e.g. claude-opus-4-6,
                     for the model picker (the gateway decides what runs)

This makes that model the "default" entry of the chat model picker, so users
don't have to configure anything. They can still add other models, with their
own keys, in the Jupyternaut settings. Nothing is configured without these
variables, so images keep working with OpenHEXA versions that do not send them.
"""

import os

c = get_config()  # noqa: F821

GATEWAY_PATH = "/assistant/gateway/v1"

provider = os.environ.get("HEXA_AI_PROVIDER", "")
model = os.environ.get("HEXA_AI_MODEL", "")
server_url = os.environ.get("HEXA_SERVER_URL", "").rstrip("/")
token = os.environ.get("HEXA_TOKEN", "")

if provider == "openhexa" and model and server_url and token:
    model_id = f"openai/{model}"
    c.JupyternautExtension.initial_language_model = model_id
    c.JupyternautExtension.model_parameters = {
        model_id: {"api_base": f"{server_url}{GATEWAY_PATH}", "api_key": token}
    }
