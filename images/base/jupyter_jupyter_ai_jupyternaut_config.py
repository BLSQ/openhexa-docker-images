"""Default model of Jupyter AI's Jupyternaut persona, from the HEXA_AI_* variables.

Jupyternaut talks to models through litellm. OpenHEXA tells the notebook server
which provider and model the organization uses (see hexa-ai-env.sh); this makes
that model the "default" entry of the chat model picker, so users don't have to
configure anything. They can still add other models in the Jupyternaut settings.
"""

import os

c = get_config()  # noqa: F821

provider = os.environ.get("HEXA_AI_PROVIDER", "")
model = os.environ.get("HEXA_AI_MODEL", "")

if provider == "managed" and model and os.environ.get("HEXA_AI_VERTEX_PROJECT_ID"):
    # Claude on Vertex AI. Credentials come from the local metadata server
    # started by hexa-ai-env.sh; project and region are given explicitly rather
    # than through the VERTEXAI_* variables so the model works even when a user
    # overrides those in a .env file.
    model_id = f"vertex_ai/{model}"
    c.JupyternautExtension.initial_language_model = model_id
    c.JupyternautExtension.model_parameters = {
        model_id: {
            "vertex_project": os.environ["HEXA_AI_VERTEX_PROJECT_ID"],
            "vertex_location": os.environ.get("HEXA_AI_VERTEX_REGION", "europe-west1"),
        }
    }
elif provider == "anthropic" and model and os.environ.get("HEXA_AI_ANTHROPIC_API_KEY"):
    # The organization's own key, exported as ANTHROPIC_API_KEY by hexa-ai-env.sh.
    c.JupyternautExtension.initial_language_model = f"anthropic/{model}"
