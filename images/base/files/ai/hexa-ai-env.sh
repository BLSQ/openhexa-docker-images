#!/bin/bash
# Configure the AI tooling of a notebook server from the HEXA_AI_* variables.
#
# Sourced by the entrypoint before the Jupyter server starts, so that the server
# and everything it spawns (kernels, terminals, the ACP agent subprocesses of
# Jupyter AI) inherit the result.
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
# Nothing happens when HEXA_AI_PROVIDER is unset, so images keep working with
# OpenHEXA versions that do not send these variables.

case "${HEXA_AI_PROVIDER:-}" in
"managed")
  if [[ -z "${HEXA_AI_VERTEX_PROJECT_ID:-}" || -z "${HEXA_AI_VERTEX_ACCESS_TOKEN:-}" ]]; then
    echo "HEXA_AI_PROVIDER=managed but HEXA_AI_VERTEX_PROJECT_ID or HEXA_AI_VERTEX_ACCESS_TOKEN is missing, AI tooling not configured" >&2
  else
    region="${HEXA_AI_VERTEX_REGION:-europe-west1}"
    port="${HEXA_AI_METADATA_PORT:-4322}"

    # Serve the access token as Application Default Credentials: every Google
    # client library (Python and Node) asks the Compute Engine metadata server
    # for a token when nothing else is configured, and lets us point it at a
    # local address.
    hexa-ai-metadata-server.py &
    export GCE_METADATA_HOST="127.0.0.1:${port}"
    export GCE_METADATA_IP="127.0.0.1:${port}"
    # Node's gcp-metadata: skip the availability probe, the server is there.
    export METADATA_SERVER_DETECTION="assume-present"

    # Project resolution for the Google client libraries.
    export GOOGLE_CLOUD_PROJECT="${HEXA_AI_VERTEX_PROJECT_ID}"
    export GCLOUD_PROJECT="${HEXA_AI_VERTEX_PROJECT_ID}"

    # Claude Code (used directly and through Jupyter AI's @Claude persona).
    export CLAUDE_CODE_USE_VERTEX=1
    export CLOUD_ML_REGION="${region}"
    export ANTHROPIC_VERTEX_PROJECT_ID="${HEXA_AI_VERTEX_PROJECT_ID}"
    # Claude Code can't sign in with a claude.ai account here, the credentials
    # come from OpenHEXA.
    export DISABLE_LOGIN_COMMAND=1

    # Gemini CLI and the Google GenAI SDK.
    export GOOGLE_GENAI_USE_VERTEXAI=true
    export GOOGLE_CLOUD_LOCATION="${region}"

    # litellm (Jupyternaut persona, %%ai magics).
    export VERTEXAI_PROJECT="${HEXA_AI_VERTEX_PROJECT_ID}"
    export VERTEXAI_LOCATION="${region}"
  fi
  ;;
"anthropic")
  if [[ -z "${HEXA_AI_ANTHROPIC_API_KEY:-}" ]]; then
    echo "HEXA_AI_PROVIDER=anthropic but HEXA_AI_ANTHROPIC_API_KEY is missing, AI tooling not configured" >&2
  else
    # Claude Code and litellm both read ANTHROPIC_API_KEY.
    export ANTHROPIC_API_KEY="${HEXA_AI_ANTHROPIC_API_KEY}"
    export DISABLE_LOGIN_COMMAND=1
  fi
  ;;
esac

if [[ -n "${HEXA_AI_MODEL:-}" ]]; then
  # Claude Code: the primary model; background tasks follow it.
  export ANTHROPIC_MODEL="${HEXA_AI_MODEL}"
fi
