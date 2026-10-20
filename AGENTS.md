# AGENTS.md

Guidance for AI agents working in this repository.

## What this repo is

A collection of Docker images for OpenHexa workspaces (notebooks and pipelines).
There are three images, layered:

- `images/base` — the base environment.
- `images/blsq` — built on top of base (`--build-arg BASE_IMAGE=...`).
- `images/blsq-r` — built on top of base, adds R.

## Rules

- **Never commit to git.** Do not run `git commit`, `git push`, `git tag`, or
  any other command that writes to git history. Committing is a human
  responsibility. Make and stage changes if asked, but leave the actual commit
  to a person.
- **Work in your own worktree.** Each branch an agent works on gets a git
  worktree under `../openhexa-docker-images-worktrees/<branch>`, created from
  `origin/main` with `git worktree add --no-track -b <branch> <dir> origin/main`.
  Do not edit a checkout a person is also committing in: a commit landing
  mid-task means the tree you built and tested is no longer the one on the
  branch. Use separate image names per worktree (`make ci BASE_IMAGE=...
  BLSQ_IMAGE=... BLSQ_R_IMAGE=...`) so parallel builds do not overwrite each
  other's images.

## Build & test

The `Makefile` mirrors the CI checks in `.github/workflows/build_image.yml` and
runs them against the local Docker daemon.

Create and activate a Python virtual environment before running any `make`
commands, so test dependencies install into an isolated environment rather than
your system Python:

```bash
python -m venv venv
source venv/bin/activate
```

```bash
make deps    # install Python test dependencies and Playwright's Chromium
make build   # build all three images (alias: make b)
make test    # test all three images (alias: make t)
make ci      # full pipeline: build + test base, blsq, blsq-r
```

Single-image targets are also available, e.g. `make build-base`, `make test-blsq`.

Tests live in `tests/` and run via pytest against a built image:

```bash
python -m pytest tests/ -v --docker-image openhexa-base-environment
```

Useful options: `-k <expr>` to select tests, `-m "not ui"` to skip the browser
tests, `--image-flavor base|blsq|blsq-r` when the image name does not say which
image it is (the package tests use it).

## Verifying a change

Run the tests that cover it, and add one when nothing does. For anything a user
sees in JupyterLab, check it in a browser, not only from the server side:
`jupyter labextension list` reports an extension as OK even when its frontend
bundle fails to load in the browser.

- **Browser tests** (`tests/test_ui.py`, marker `ui`) drive JupyterLab in
  headless Chromium with Playwright. The `jupyterlab` fixture serves the image
  under test on a free port with a random token; `jupyterlab.put_file()` creates
  files through the Jupyter contents API, so no volume mount is needed. The
  `lab_page` fixture opens JupyterLab and records the browser console in
  `page.console_messages`; `test_jupyterlab_extensions_load` fails on
  extension load errors.
- **Trying an image by hand:** `make run-base` (or `run-blsq`, `run-blsq-r`)
  serves an image as standalone JupyterLab on `http://localhost:8890/lab?token=hexa`
  (`RUN_PORT`, `RUN_TOKEN` to change); `make stop` removes it. For a one-off
  check, write a short Playwright script against that URL rather than relying
  on a browser extension.
- **Volume mounts:** with Docker Desktop, only shared host paths can be mounted;
  temporary directories such as `/tmp/...` are usually not shared. Copy files in
  with the contents API or `docker cp` instead.

The standalone server skips what the OpenHEXA stack adds: the JupyterHub
proxy, the real Content-Security-Policy, the `HEXA_*` variables the app injects
and the mounted workspace files. Changes depending on those need the full stack.

## Testing against the local OpenHEXA stack

The local stack is the app (`openhexa-app`, Docker Compose) plus JupyterHub
(`openhexa-notebooks`, `docker compose up`). The hub spawns workspace servers
on the local Docker daemon, by image name:

- A workspace's own image, if set (workspace settings, `docker_image`), wins;
  otherwise the hub's `JUPYTER_IMAGE` / the app's `DEFAULT_WORKSPACE_IMAGE`.
- So a locally built `openhexa-base-environment:latest` is used directly: set
  it as the workspace image, rebuild, then stop and start the workspace server
  (an already running server keeps its old container).
- Docker rejects image names with surrounding whitespace ("invalid reference
  format" in the hub logs, with `%20` in the URL); check the stored value.

## Known noise

- `ERROR 1: PROJ: proj_create_from_database` during the geospatial tests.
- In the browser console: the git extension's `Fail to find Git top level` and
  the 500 response behind it, when the server root is no repository.
- Version warnings ("Unsatisfied version ... of shared singleton module") from
  extensions built against other JupyterLab or chat versions; they are only a
  problem when followed by "Failed to create module".

