# Testing

The tests run against a built image, given with `--docker-image`. See
`AGENTS.md` and the `Makefile` for the full workflow.

## Setup

```bash
python -m venv venv
source venv/bin/activate
make deps   # pip install . and python -m playwright install chromium
```

On Linux, Chromium also needs system libraries: `python -m playwright
install-deps chromium` (CI runs `playwright install --with-deps chromium`).

## Running tests

```bash
make test-base                                   # one image, every test
python -m pytest tests/ --docker-image openhexa-base-environment
python -m pytest tests/ -m "not ui" --docker-image openhexa-base-environment
python -m pytest tests/test_ui.py --docker-image openhexa-blsq-environment
make test-base-viz                               # watch the ui tests in a Chromium window
```

