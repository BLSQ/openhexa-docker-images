#!/bin/bash
# Configure the Jupyter AI assistant (Jupyternaut) of a notebook server from the
# HEXA_AI_* variables.
#
# Sourced by the entrypoint before the Jupyter server starts, so that the server
# and everything it spawns (kernels, terminals) inherit the result.
#
# OpenHEXA injects, for a workspace whose organization has the AI assistant enabled:
#
#   HEXA_AI_PROVIDER                     "managed" (Vertex AI, OpenHEXA's own
#                                        account) or "anthropic" (the
#                                        organization's own API key)
#   HEXA_AI_MODEL                        Claude model name, e.g. claude-opus-4-6
#
#   managed only:
#   HEXA_AI_VERTEX_PROJECT_ID            GCP project serving the models
#   HEXA_AI_VERTEX_REGION                region of that project, e.g. europe-west1
#   HEXA_AI_VERTEX_ACCESS_TOKEN          short-lived OAuth2 access token
#   HEXA_AI_VERTEX_ACCESS_TOKEN_EXPIRES_AT  (optional) its expiry, epoch seconds
#
#   anthropic only:
#   HEXA_AI_ANTHROPIC_API_KEY            the organization's Anthropic API key
#
# The model itself is picked up by Jupyternaut through its config file
# (/etc/jupyter/jupyter_jupyter_ai_jupyternaut_config.py); this script only takes
# care of the credentials.
#
# Nothing happens when HEXA_AI_PROVIDER is unset, so images keep working with
# OpenHEXA versions that do not send these variables.

case "${HEXA_AI_PROVIDER:-}" in
"managed")
  if [[ -z "${HEXA_AI_VERTEX_PROJECT_ID:-}" || -z "${HEXA_AI_VERTEX_ACCESS_TOKEN:-}" ]]; then
    echo "HEXA_AI_PROVIDER=managed but HEXA_AI_VERTEX_PROJECT_ID or HEXA_AI_VERTEX_ACCESS_TOKEN is missing, AI assistant not configured" >&2
  else
    region="${HEXA_AI_VERTEX_REGION:-europe-west1}"
    port="${HEXA_AI_METADATA_PORT:-4322}"

    # Serve the access token as Application Default Credentials: the Google
    # client libraries (used by litellm for Vertex AI) ask the Compute Engine
    # metadata server for a token when nothing else is configured, and let us
    # point them at a local address.
    hexa-ai-metadata-server.py &
    export GCE_METADATA_HOST="127.0.0.1:${port}"
    export GCE_METADATA_IP="127.0.0.1:${port}"

    # Project resolution for the Google client libraries.
    export GOOGLE_CLOUD_PROJECT="${HEXA_AI_VERTEX_PROJECT_ID}"
    export GCLOUD_PROJECT="${HEXA_AI_VERTEX_PROJECT_ID}"

    # litellm (Jupyternaut, %%ai magics).
    export VERTEXAI_PROJECT="${HEXA_AI_VERTEX_PROJECT_ID}"
    export VERTEXAI_LOCATION="${region}"
  fi
  ;;
"anthropic")
  if [[ -z "${HEXA_AI_ANTHROPIC_API_KEY:-}" ]]; then
    echo "HEXA_AI_PROVIDER=anthropic but HEXA_AI_ANTHROPIC_API_KEY is missing, AI assistant not configured" >&2
  else
    # litellm reads ANTHROPIC_API_KEY.
    export ANTHROPIC_API_KEY="${HEXA_AI_ANTHROPIC_API_KEY}"
  fi
  ;;
esac
