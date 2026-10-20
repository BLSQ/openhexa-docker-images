# Makefile for building and testing the OpenHexa Docker images locally.
#
# This mirrors the checks in .github/workflows/build_image.yml, but runs them
# against your local Docker daemon. Because `docker build` writes directly to
# the local daemon, the dependent images (blsq, blsq-r) can reference the
# freshly built base image by tag — no local registry is needed like in CI.
#
# Common usage:
#   make ci          # full pipeline: build + test base, blsq, blsq-r
#   make build       # build all three images (alias: make b)
#   make test        # test all three images (alias: make t)
#   make build-base  # build a single image
#   make test-base   # test a single image
#   make test-base-viz  # watch the ui tests of an image in a Chromium window
#   make deps        # install the Python test dependencies and Chromium
#   make run-base    # serve an image as JupyterLab on http://localhost:$(RUN_PORT)
#   make run-base RUN_FAKE_GATEWAY=1  # ... with Jupyternaut answering from a fake gateway
#   make stop        # remove the containers started by the run-* targets
#
# `make` or `make help` lists every target.

.DEFAULT_GOAL := help

BASE_IMAGE   ?= openhexa-base-environment
BLSQ_IMAGE   ?= openhexa-blsq-environment
BLSQ_R_IMAGE ?= openhexa-blsq-r-environment
# The images ship as linux/amd64 (CI). Locally they build for the Docker
# daemon's own architecture: amd64 images run under Rosetta on Apple Silicon,
# where the Jupyter server and kernels intermittently deadlock.
# PLATFORM=linux/amd64 builds what CI ships.
PLATFORM     ?= linux/$(shell docker version -f '{{.Server.Arch}}' 2>/dev/null || echo amd64)

# Settings of the run-* targets. The container name is derived from the image
# name, so worktrees that build their own images (see AGENTS.md) do not stop
# each other's server; give each its own RUN_PORT to run them side by side.
RUN_PORT     ?= 8890
RUN_TOKEN    ?= hexa
RUN_PREFIX   ?= openhexa-run
run_name      = $(RUN_PREFIX)-$(subst :,-,$(subst /,-,$(1)))
# Extra `docker run` flags, e.g. RUN_ARGS="-e HEXA_AI_MODEL=..." to inject the
# variables the OpenHEXA app would.
RUN_ARGS     ?=
# RUN_FAKE_GATEWAY=1 configures Jupyternaut for the OpenHEXA assistant gateway
# and runs tests/fake_gateway.py in its place inside the container, so the chat
# panel answers without the OpenHEXA app or model credentials. The variables
# are those of tests/fake_gateway.py; `docker logs` shows what it received.
RUN_FAKE_GATEWAY ?=
ifneq ($(strip $(RUN_FAKE_GATEWAY)),)
RUN_ARGS  += -e HEXA_AI_PROVIDER=openhexa -e HEXA_AI_MODEL=claude-opus-4-6 \
	-e HEXA_SERVER_URL=http://127.0.0.1:4318/ -e HEXA_TOKEN=workspace-token:signature \
	-e FAKE_GATEWAY="$$(cat tests/fake_gateway.py)"
RUN_SETUP  = python -c "$$FAKE_GATEWAY" &
endif

# docker-py ignores Docker CLI contexts, so pin both build and tests to the active endpoint.
ifeq ($(strip $(DOCKER_HOST)),)
DOCKER_HOST := $(shell docker context inspect --format '{{.Endpoints.docker.Host}}' 2>/dev/null)
endif
export DOCKER_HOST

DOCKER_BUILD := docker build --platform $(PLATFORM)
PYTEST       := python -m pytest tests/ -v
# The test-*-viz targets: only the ui tests, in a visible Chromium, paused
# SLOWMO milliseconds after each browser action so you can follow along.
SLOWMO       ?= 500
PYTEST_VIZ   := $(PYTEST) -m ui --headed --slowmo $(SLOWMO)

.PHONY: help h build-base build-blsq build-blsq-r b build \
	test-base test-blsq test-blsq-r t test test-base-viz test-blsq-viz test-blsq-r-viz \
	run-base run-blsq run-blsq-r stop deps ci

h help: ## Show this help
	@awk 'BEGIN { FS = ":.*## " } \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } \
		/^[a-zA-Z0-9_ -]+:.*## / { target = $$1; gsub(/ /, ", ", target); printf "  \033[36m%-32s\033[0m %s\n", target, $$2 }' $(MAKEFILE_LIST)
	@echo

##@ Build

build-base: ## Build the base image
	$(DOCKER_BUILD) -t $(BASE_IMAGE) images/base

build-blsq: build-base ## Build the blsq image (on top of base)
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(BLSQ_IMAGE) images/blsq

build-blsq-r: build-base ## Build the blsq-r image (on top of base, adds R)
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(BLSQ_R_IMAGE) images/blsq-r

b build: build-base build-blsq build-blsq-r ## Build all three images

##@ Test

test-base: ## Test the base image
	$(PYTEST) --docker-image $(BASE_IMAGE)

test-blsq: ## Test the blsq image
	$(PYTEST) --docker-image $(BLSQ_IMAGE)

test-blsq-r: ## Test the blsq-r image
	$(PYTEST) --docker-image $(BLSQ_R_IMAGE)

t test: test-base test-blsq test-blsq-r ## Test all three images

test-base-viz: ## Watch the ui tests of the base image in a Chromium window
	$(PYTEST_VIZ) --docker-image $(BASE_IMAGE)

test-blsq-viz: ## Watch the ui tests of the blsq image in a Chromium window
	$(PYTEST_VIZ) --docker-image $(BLSQ_IMAGE)

test-blsq-r-viz: ## Watch the ui tests of the blsq-r image in a Chromium window
	$(PYTEST_VIZ) --docker-image $(BLSQ_R_IMAGE)

##@ Run

# Serves an image as a standalone JupyterLab, the way the tests do: no hub, no
# OpenHEXA app (RUN_ARGS, RUN_FAKE_GATEWAY above). CONTENT_SECURITY_POLICY is required by jupyter_notebook_config.py,
# and the server root (/home/jovyan/workspace, mounted by the hub) must exist.
# Published on localhost only: the token is fixed and the server gives a shell.
define run_image
	docker rm -f $(call run_name,$(1)) >/dev/null 2>&1 || true
	docker run -d --name $(call run_name,$(1)) -p 127.0.0.1:$(RUN_PORT):8888 \
		-e CONTENT_SECURITY_POLICY="frame-ancestors 'self'" $(RUN_ARGS) \
		--entrypoint bash $(1) -c '$(RUN_SETUP) mkdir -p ~/workspace && exec /usr/local/bin/entrypoint.sh notebook --ServerApp.token=$(RUN_TOKEN) --ServerApp.password='
	@for i in $$(seq 1 120); do \
		curl -sf -o /dev/null "http://127.0.0.1:$(RUN_PORT)/api/status?token=$(RUN_TOKEN)" && exit 0; \
		[ "$$(docker inspect -f '{{.State.Running}}' $(call run_name,$(1)))" = true ] \
			|| { docker logs $(call run_name,$(1)); echo "$(call run_name,$(1)) exited"; exit 1; }; \
		sleep 1; \
	done; docker logs $(call run_name,$(1)); echo "JupyterLab did not start in 120 s"; exit 1
	@echo "JupyterLab: http://localhost:$(RUN_PORT)/lab?token=$(RUN_TOKEN)  (container $(call run_name,$(1)); make stop to remove)"
endef

run-base: ## Serve the base image as JupyterLab on RUN_PORT (default 8890)
	$(call run_image,$(BASE_IMAGE))

run-blsq: ## Serve the blsq image as JupyterLab on RUN_PORT
	$(call run_image,$(BLSQ_IMAGE))

run-blsq-r: ## Serve the blsq-r image as JupyterLab on RUN_PORT
	$(call run_image,$(BLSQ_R_IMAGE))

stop: ## Remove the containers started by the run-* targets
	docker rm -f $(call run_name,$(BASE_IMAGE)) $(call run_name,$(BLSQ_IMAGE)) $(call run_name,$(BLSQ_R_IMAGE)) 2>/dev/null || true

##@ Misc

deps: ## Install the Python test dependencies and the Chromium the UI tests drive
	pip install .
	python -m playwright install chromium

ci: build-base test-base build-blsq test-blsq build-blsq-r test-blsq-r ## Full pipeline: build + test base, blsq, blsq-r
