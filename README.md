# openhexa-docker-images

A repository of Docker images for OpenHexa workspaces (notebooks and pipelines)

There are three images, layered:

- `images/base` — the base environment.
- `images/blsq` — built on top of base.
- `images/blsq-r` — built on top of base, adds R.

## Building and testing locally

The `Makefile` mirrors the CI checks in `.github/workflows/build_image.yml` and
runs them against your local Docker daemon. Run `make` (or `make help`) to list
every target.

Create and activate a Python virtual environment first, so the test
dependencies install into an isolated environment rather than your system
Python:

```bash
python -m venv venv
source venv/bin/activate
make deps    # install the Python test dependencies and Chromium
```

Then build and test the images:

```bash
make build   # build all three images (alias: make b)
make test    # test all three images (alias: make t)
make ci      # full pipeline: build + test base, blsq, blsq-r
```

Single-image targets are also available:

```bash
make build-base      # or build-blsq, build-blsq-r
make test-base       # or test-blsq, test-blsq-r
```

The image tags and platform can be overridden with `BASE_IMAGE`, `BLSQ_IMAGE`,
`BLSQ_R_IMAGE` and `PLATFORM` (default `linux/amd64`), for example:

```bash
make build-base BASE_IMAGE=openhexa-base-environment:dev
```

To run a single test file directly:

```bash
make test-base PYTEST="python -m pytest tests/test_quarto_ui.py --headed --slowmo 500"
```

`make` lists the build, test and run targets; `make run-base` serves an image
as JupyterLab on http://localhost:8890/lab?token=hexa (`RUN_PORT` and
`RUN_TOKEN` to change) and `make stop` removes it.

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

