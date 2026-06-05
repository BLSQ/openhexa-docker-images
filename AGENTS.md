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
make deps    # install Python test dependencies
make build   # build all three images (alias: make b)
make test    # test all three images (alias: make t)
make ci      # full pipeline: build + test base, blsq, blsq-r
```

Single-image targets are also available, e.g. `make build-base`, `make test-blsq`.

Tests live in `tests/` and run via pytest against a built image:

```bash
python -m pytest tests/ -v --docker-image openhexa-base-environment
```
