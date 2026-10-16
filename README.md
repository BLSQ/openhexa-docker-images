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

### The assistant gateway

The notebook server holds no model credentials. OpenHEXA runs the organization's
model, whatever its provider, behind an OpenAI-compatible endpoint, the assistant
gateway, which charges the usage to the organization's monthly AI budget and
traces the calls (Logfire). `jupyter_jupyter_ai_jupyternaut_config.py` points
litellm's `openai` provider at `$HEXA_SERVER_URL/assistant/gateway/v1`,
authenticated with the workspace token (`HEXA_TOKEN`) the server already
receives, from the variables the OpenHEXA app injects when the organization has
the AI assistant enabled:

| Variable           | Meaning                                                                          |
| ------------------ | -------------------------------------------------------------------------------- |
| `HEXA_AI_PROVIDER` | `openhexa`: the gateway                                                          |
| `HEXA_AI_MODEL`    | name of the model the gateway runs, e.g. `claude-opus-4-6`, for the model picker |

`HEXA_AI_MODEL` becomes the default entry of Jupyternaut's model picker. Without
`HEXA_AI_PROVIDER` nothing is configured and Jupyternaut asks the user to pick a
model and provide credentials themselves; users can also add models with their
own keys in the Jupyternaut settings, whose usage is theirs.

## Quarto

The base image includes the [Quarto](https://quarto.org) CLI, `jupytext` (which
opens `.qmd` files as notebooks through *Open With → Notebook* and keeps paired
files in sync) and the `jupyterlab-quarto` extension, which renders Quarto
markdown (callouts, cross-references, figure options...) in notebook cells.
