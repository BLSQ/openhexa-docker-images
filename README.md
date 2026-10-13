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
chat panel in JupyterLab where AI personas can read and edit notebooks, run cells
and use the terminal. Two personas are available:

- **Jupyternaut**, which talks to a model directly (through litellm). It is in
  every image.
- **Claude**, which drives Claude Code through the Agent Client Protocol. It is
  available in the images that ship Claude Code (`blsq`).

Claude Code and Gemini CLI can also be used from a terminal in those images.

### Credentials

The tooling is configured at start-up by `hexa-ai-env.sh`, from variables the
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

Without `HEXA_AI_PROVIDER` nothing is configured and the AI personas ask the user
to log in themselves.

With the managed provider, the Google client libraries cannot take a raw access
token as credentials, so `hexa-ai-metadata-server.py` serves it on
`127.0.0.1:4322` the way the Compute Engine metadata server would, and the
`GCE_METADATA_HOST` variable points every Google client library (Python and Node,
hence litellm, Claude Code and Gemini CLI) at it. The token lives for an hour and
cannot be renewed from inside the container, like the storage token the server
already receives; the notebook server has to be restarted to get a new one.
