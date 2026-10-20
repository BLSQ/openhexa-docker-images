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
as JupyterLab on http://localhost:8890/lab?token=hexa.

## Image tags

| Tag                | When updated                       |
| ------------------ | ---------------------------------- |
| `:latest`          | Official releases only             |
| `:latest-unstable` | Every push to main                 |
| `:main`            | Every push to main                 |
| `:vX.Y.Z`          | Official releases (version number) |
