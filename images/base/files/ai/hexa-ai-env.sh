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
#   telemetry (optional, see below):
#   HEXA_AI_TELEMETRY                    "false" turns the telemetry off
#   HEXA_AI_TELEMETRY_ENDPOINT           OTLP collector; defaults to OpenHEXA
#                                        itself, $HEXA_SERVER_URL/notebooks/telemetry
#   HEXA_AI_TELEMETRY_LOG_CONTENT        "true" includes prompts and responses
#                                        in the traces (off by default)
#
# The Jupyternaut model is picked up through its config file
# (/etc/jupyter/jupyter_jupyter_ai_jupyternaut_config.py); this script takes
# care of the credentials and of the telemetry.
#
# Nothing happens when HEXA_AI_PROVIDER is unset, so images keep working with
# OpenHEXA versions that do not send these variables.

hexa_ai_configured=false

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
    hexa_ai_configured=true
  fi
  ;;
"anthropic")
  if [[ -z "${HEXA_AI_ANTHROPIC_API_KEY:-}" ]]; then
    echo "HEXA_AI_PROVIDER=anthropic but HEXA_AI_ANTHROPIC_API_KEY is missing, AI assistant not configured" >&2
  else
    # litellm reads ANTHROPIC_API_KEY.
    export ANTHROPIC_API_KEY="${HEXA_AI_ANTHROPIC_API_KEY}"
    hexa_ai_configured=true
  fi
  ;;
esac

# Telemetry. OpenHEXA is the OpenTelemetry collector of its notebook servers:
# the hexa_ai_telemetry server extension exports Jupyternaut's model calls
# (litellm traces, with the token usage) over OTLP/HTTP to
# $HEXA_SERVER_URL/notebooks/telemetry, authenticated with the workspace token
# the server already holds. OpenHEXA counts the tokens towards the
# organization's AI usage and forwards the traces to Logfire. No other secret
# enters the container for this.
#
# Only when OpenHEXA configured the assistant above: usage made on the
# organization's credentials is what its AI budget accounts for.
if [[ "$hexa_ai_configured" == true && "${HEXA_AI_TELEMETRY:-true}" != "false" ]]; then
  if [[ -z "${HEXA_AI_TELEMETRY_ENDPOINT:-}" && -n "${HEXA_SERVER_URL:-}" ]]; then
    HEXA_AI_TELEMETRY_ENDPOINT="${HEXA_SERVER_URL%/}/notebooks/telemetry"
  fi
  if [[ -n "${HEXA_AI_TELEMETRY_ENDPOINT:-}" && -n "${HEXA_TOKEN:-}" ]]; then
    export HEXA_AI_TELEMETRY_ENDPOINT

    # Resource attributes name the workspace and user on every span (the
    # OpenTelemetry SDK reads this variable). Values may not contain spaces,
    # commas or non-ASCII characters, so anything odd is left out rather than
    # breaking the export; OpenHEXA stamps the identities it knows anyway.
    hexa_otel_attributes=""
    hexa_otel_attribute() {
      if [[ -n "$2" && "$2" =~ ^[A-Za-z0-9._~@+/:-]+$ ]]; then
        hexa_otel_attributes="${hexa_otel_attributes:+${hexa_otel_attributes},}$1=$2"
      fi
    }
    hexa_otel_attribute "hexa.workspace" "${HEXA_WORKSPACE:-}"
    hexa_otel_attribute "hexa.user" "${JUPYTERHUB_USER:-}"
    if [[ -n "$hexa_otel_attributes" ]]; then
      export OTEL_RESOURCE_ATTRIBUTES="${OTEL_RESOURCE_ATTRIBUTES:+${OTEL_RESOURCE_ATTRIBUTES},}${hexa_otel_attributes}"
    fi
    unset -f hexa_otel_attribute
  fi
fi
unset hexa_ai_configured hexa_otel_attributes
