# Testing

The tests run against a built image, given with `--docker-image`. See
`AGENTS.md` and the `Makefile` for the full workflow.

## Setup

```bash
python -m venv venv
source venv/bin/activate
make deps   # pip install . and python -m playwright install chromium
```

## Running tests

```bash
make test-base                                   # one image, every test
python -m pytest tests/ --docker-image openhexa-base-environment
python -m pytest tests/ -m "not ui" --docker-image openhexa-base-environment
python -m pytest tests/test_ui.py --docker-image openhexa-blsq-environment
```

## Test structure

- `test_local_pipelines.py`: runs sample pipelines in the image.
- `test_packages.py`: the Python modules and R packages each image promises
  load. The image flavor (base, blsq, blsq-r) is guessed from the image name;
  pass `--image-flavor` otherwise.
- `test_ui.py` (marker `ui`): JupyterLab in headless Chromium, via the
  `jupyterlab` and `lab_page` fixtures of `conftest.py`.
- `testutils.py`: helpers to run pipelines and scripts inside an image.
