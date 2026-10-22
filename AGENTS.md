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
- **Work in your own worktree.** The repository lives in a parent folder with
  one checkout per branch: the main checkout is `openhexa-docker-images/main`
  and each branch an agent works on gets a sibling git worktree at
  `openhexa-docker-images/<branch>`, created from `main` with
  `git worktree add --no-track -b <branch> ../<branch> origin/main`.
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
Run one test suite at a time: two `make test-*` in parallel share the Docker
VM and slow each other down tenfold, until the Docker API itself times out.

Tests live in `tests/` and run via pytest against a built image:

```bash
python -m pytest tests/ -v --docker-image openhexa-base-environment
```

Useful options: `-k <expr>` to select tests, `-m "not ui"` to skip the browser
tests, `--image-flavor base|blsq|blsq-r` when the image name does not say which
image it is (the package and server tests use it). On Linux, Chromium needs
system libraries that `make deps` does not install; when it fails to launch,
run `python -m playwright install-deps chromium` (CI does `--with-deps`).

## Verifying a change

Run the tests that cover it, and add one when nothing does. For anything a user
sees in JupyterLab, check it in a browser, not only from the server side:
`jupyter labextension list` reports an extension as OK even when its frontend
bundle fails to load in the browser.

- **Server tests** (`tests/test_server.py`) talk to the standalone JupyterLab
  the `jupyterlab` fixture serves (session-scoped, free localhost port, random
  token, `/home/jovyan/workspace` as root like the hub). `jupyterlab.api()`
  calls the REST API, `jupyterlab.put_file()` creates files through the
  contents API, so no volume mount is needed, and
  `jupyterlab.wait_for_kernel(path)` blocks until a notebook's kernel is idle
  with the frontend connected: before that, a run request is dropped.
- **Browser tests** (`tests/test_ui.py`, `tests/test_quarto_ui.py`, marker
  `ui`) drive that server in headless Chromium with Playwright. The `lab_page`
  fixture opens JupyterLab with a clean layout and records the browser console
  in `page.console_messages` and the 4xx/5xx responses in `page.http_errors`;
  `test_jupyterlab_extensions_load` fails on either. When a ui test fails, the
  fixture writes a full-page screenshot and the recorded messages to the test's
  `tmp_path` and prints their paths: look at them before guessing. Watch a test
  with `--headed --slowmo 500` (`make test-base-viz` runs the ui tests of an
  image that way, `SLOWMO=...` to change the pause), or step through it with
  `PWDEBUG=1`.
- **Trying an image by hand:** `make run-base` (or `run-blsq`, `run-blsq-r`)
  serves an image as standalone JupyterLab on `http://localhost:8890/lab?token=hexa`
  and returns once it answers (`RUN_PORT`, `RUN_TOKEN` to change); `make stop`
  removes it. The container is named after the image, so pass the same
  `BASE_IMAGE=...` as to `make build` and a free `RUN_PORT` in a worktree. For a
  one-off check, write a short Playwright script against that URL rather than
  relying on a browser extension.
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

- Version warnings ("Unsatisfied version ... of shared singleton module") from
  extensions built against other JupyterLab or chat versions; they are only a
  problem when followed by "Failed to create module".

