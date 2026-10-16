# openhexa-docker-images

A repository of Docker images for OpenHexa workspaces (notebooks and pipelines)

## Building locally

```bash
docker build -t openhexa-base-environment images/base
docker build -t openhexa-blsq-environment --build-arg BASE_IMAGE=openhexa-base-environment images/blsq
docker build -t openhexa-blsq-r-environment --build-arg BASE_IMAGE=openhexa-base-environment images/blsq-r
```

`make` lists the build and test targets.

## Image tags

| Tag                | When updated                       |
| ------------------ | ---------------------------------- |
| `:latest`          | Official releases only             |
| `:latest-unstable` | Every push to main                 |
| `:main`            | Every push to main                 |
| `:vX.Y.Z`          | Official releases (version number) |

## AI assistant in notebooks

The base image ships [Jupyter AI](https://github.com/jupyterlab/jupyter-ai): a
chat panel in JupyterLab where the **Jupyternaut** assistant can read and edit
notebooks and run cells. It talks to the model through litellm.

Jupyter AI can also expose coding agents (Claude Code, Codex...) as chat
personas when their adapter binary is installed; the images deliberately leave
those out so Jupyternaut is the only persona.

### Credentials

The assistant is configured at start-up by `hexa-ai-env.sh`, from variables the
OpenHEXA app injects into the notebook server when the organization has the AI
assistant enabled:

| Variable                                 | Meaning                                                     |
| ---------------------------------------- | ----------------------------------------------------------- |
| `HEXA_AI_PROVIDER`                       | `managed` (OpenHEXA's Vertex AI project) or `anthropic` (the organization's own key) |
| `HEXA_AI_MODEL`                          | Claude model name, e.g. `claude-opus-4-6`                   |
| `HEXA_AI_VERTEX_PROJECT_ID`              | managed: the GCP project serving the models                 |
| `HEXA_AI_VERTEX_REGION`                  | managed: its region, e.g. `europe-west1`                    |
| `HEXA_AI_VERTEX_ACCESS_TOKEN`            | managed: a short-lived OAuth2 access token                  |
| `HEXA_AI_VERTEX_ACCESS_TOKEN_EXPIRES_AT` | managed, optional: when the token expires, in epoch seconds |
| `HEXA_AI_ANTHROPIC_API_KEY`              | anthropic: the organization's API key                       |

`HEXA_AI_MODEL` becomes the default entry of Jupyternaut's model picker (through
`jupyter_jupyter_ai_jupyternaut_config.py`). Without `HEXA_AI_PROVIDER` nothing is
configured and Jupyternaut asks the user to pick a model and provide credentials
themselves.

With the managed provider, the Google client libraries cannot take a raw access
token as credentials, so `hexa-ai-metadata-server.py` serves it on
`127.0.0.1:4322` the way the Compute Engine metadata server would, and the
`GCE_METADATA_HOST` variable points the Google client library (hence litellm) at
it. The token lives for an hour and cannot be renewed from inside the container,
like the storage token the server already receives; the notebook server has to be
restarted to get a new one.

### Usage accounting and telemetry

OpenHEXA is the OpenTelemetry collector of its notebook servers. When the
assistant is configured and the server knows OpenHEXA (`HEXA_SERVER_URL` and
`HEXA_TOKEN`, which notebook servers already receive), the `hexa_ai_telemetry`
server extension (`files/ai/hexa_ai_telemetry`) registers an OTLP exporter with
litellm, so every model call Jupyternaut makes is sent as a trace, with its token
usage and cost, to `$HEXA_SERVER_URL/notebooks/telemetry/v1/traces`. The request
is authenticated with the workspace token. OpenHEXA counts the tokens towards the
organization's monthly AI budget and forwards the traces to Logfire under its own
token: no Logfire credential enters the container.

| Variable                        | Meaning                                                                 |
| ------------------------------- | ----------------------------------------------------------------------- |
| `HEXA_AI_TELEMETRY`             | `false` switches the telemetry off                                      |
| `HEXA_AI_TELEMETRY_ENDPOINT`    | another OTLP/HTTP collector; defaults to OpenHEXA itself                |
| `HEXA_AI_TELEMETRY_LOG_CONTENT` | `true` includes prompts and responses in the traces; off by default     |

The spans are tagged with the workspace and user (`hexa.workspace`, `hexa.user`
resource attributes, from `HEXA_WORKSPACE` and `JUPYTERHUB_USER`).

## Quarto

The base image includes the [Quarto](https://quarto.org) CLI, `jupytext` (which
opens `.qmd` files as notebooks through *Open With → Notebook* and keeps paired
files in sync) and the `jupyterlab-quarto` extension, which renders Quarto
markdown (callouts, cross-references, figure options...) in notebook cells.
