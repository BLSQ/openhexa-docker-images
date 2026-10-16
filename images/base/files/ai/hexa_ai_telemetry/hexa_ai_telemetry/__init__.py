"""Export the telemetry of Jupyternaut to OpenHEXA.

OpenHEXA is the OpenTelemetry collector of its notebook servers: every model
call Jupyternaut makes through litellm is sent as an OTLP trace to
``$HEXA_SERVER_URL/notebooks/telemetry``, authenticated with the workspace
token the server already holds (HEXA_TOKEN). There, the tokens count towards
the organization's AI usage and the traces are forwarded to Logfire. Claude
Code reports to the same endpoint through its own OpenTelemetry support, which
hexa-ai-env.sh configures.

The exporter is only installed when hexa-ai-env.sh has set
HEXA_AI_TELEMETRY_ENDPOINT, i.e. when OpenHEXA configured the AI assistant of
this server; otherwise this extension does nothing.

Runs as a Jupyter server extension because Jupyternaut lives in the server
process, where litellm's callbacks are global.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

SERVICE_NAME = "jupyternaut"
ENDPOINT_VAR = "HEXA_AI_TELEMETRY_ENDPOINT"
TOKEN_VAR = "HEXA_TOKEN"
LOG_CONTENT_VAR = "HEXA_AI_TELEMETRY_LOG_CONTENT"

# OpenTelemetry GenAI attribute names for the prompt-cache token counts, which
# litellm's exporter leaves out of the span even though the usage it logs has
# them. Same names as pydantic-ai and Logfire use.
CACHE_READ_ATTRIBUTE = "gen_ai.usage.cache_read.input_tokens"
CACHE_CREATION_ATTRIBUTE = "gen_ai.usage.cache_creation.input_tokens"


@dataclass(frozen=True)
class TelemetrySettings:
    endpoint: str
    token: str
    # Whether prompts and completions travel with the traces. Off by default:
    # notebooks handle the users' own data.
    log_content: bool = False

    @property
    def traces_url(self) -> str:
        return f"{self.endpoint.rstrip('/')}/v1/traces"

    @classmethod
    def from_env(cls, environ=os.environ) -> TelemetrySettings | None:
        endpoint = environ.get(ENDPOINT_VAR, "")
        token = environ.get(TOKEN_VAR, "")
        if not endpoint or not token:
            return None
        return cls(
            endpoint=endpoint,
            token=token,
            log_content=environ.get(LOG_CONTENT_VAR, "").lower() == "true",
        )


def _usage_object(kwargs: dict, response_obj: Any) -> dict:
    """The usage of a litellm call, as a dict, from wherever litellm put it."""
    payload = kwargs.get("standard_logging_object") or {}
    usage = (payload.get("metadata") or {}).get("usage_object")
    if isinstance(usage, dict):
        return usage
    usage = getattr(response_obj, "usage", None)
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    return dict(usage) if isinstance(usage, dict) else {}


def _cache_tokens(usage: dict) -> tuple[int | None, int | None]:
    """(cache read, cache creation) input tokens of a call, when reported."""
    details = usage.get("prompt_tokens_details") or {}
    if not isinstance(details, dict):
        details = {}
    read = usage.get("cache_read_input_tokens")
    if read is None:
        read = details.get("cached_tokens")
    creation = usage.get("cache_creation_input_tokens")
    if creation is None:
        creation = details.get("cache_creation_tokens")
    return read, creation


def build_callback(settings: TelemetrySettings):
    """litellm's OpenTelemetry callback, exporting to OpenHEXA with our extras."""
    from litellm.integrations.opentelemetry import OpenTelemetry, OpenTelemetryConfig

    class HexaOpenTelemetry(OpenTelemetry):
        """litellm's exporter plus the prompt-cache token counts, which price
        differently from fresh input and which OpenHEXA accounts for."""

        def set_attributes(self, span, kwargs, response_obj):
            super().set_attributes(span, kwargs, response_obj)
            try:
                read, creation = _cache_tokens(_usage_object(kwargs, response_obj))
                if read is not None:
                    self.safe_set_attribute(span, CACHE_READ_ATTRIBUTE, int(read))
                if creation is not None:
                    self.safe_set_attribute(span, CACHE_CREATION_ATTRIBUTE, int(creation))
            except Exception:  # never let telemetry break a chat
                logger.debug("could not add cache token attributes", exc_info=True)

    config = OpenTelemetryConfig(
        exporter="otlp_http",
        endpoint=settings.traces_url,
        headers=f"Authorization={settings.token}",
        service_name=SERVICE_NAME,
        capture_message_content="SPAN_ONLY" if settings.log_content else "NO_CONTENT",
    )
    return HexaOpenTelemetry(config=config)


def configure_litellm(settings: TelemetrySettings | None = None):
    """Register the exporter with litellm, once. Returns it, or None if off."""
    if settings is None:
        settings = TelemetrySettings.from_env()
    if settings is None:
        return None
    import litellm

    for callback in litellm.callbacks:
        if type(callback).__name__ == "HexaOpenTelemetry":
            return callback
    callback = build_callback(settings)
    litellm.callbacks.append(callback)
    return callback


def _jupyter_server_extension_points():
    return [{"module": "hexa_ai_telemetry"}]


def _load_jupyter_server_extension(serverapp):
    settings = TelemetrySettings.from_env()
    if settings is None:
        serverapp.log.info("hexa_ai_telemetry: %s not set, AI telemetry off", ENDPOINT_VAR)
        return
    try:
        configure_litellm(settings)
    except Exception:
        serverapp.log.exception("hexa_ai_telemetry: could not configure the exporter")
        return
    serverapp.log.info("hexa_ai_telemetry: exporting Jupyternaut traces to %s", settings.traces_url)
