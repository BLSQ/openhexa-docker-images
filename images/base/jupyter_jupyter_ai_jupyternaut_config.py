"""Configure Jupyternaut to use the OpenHEXA assistant gateway by default.

When the organization's AI assistant is enabled, OpenHEXA sets:
- HEXA_AI_PROVIDER="openhexa"
- HEXA_AI_MODEL (e.g. "claude-opus-4-6")

This points litellm's OpenAI provider at $HEXA_SERVER_URL/assistant/gateway/v1
using the workspace token ($HEXA_TOKEN), so no model credentials live in the
notebook server. Users can still configure their own models and keys in the
Jupyternaut settings. If these variables are absent, nothing is configured.
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
