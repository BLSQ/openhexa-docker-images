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
#   make deps        # install the Python test dependencies and Chromium
#   make run-base    # serve an image as JupyterLab on http://localhost:$(RUN_PORT)
#   make stop        # remove the containers started by the run-* targets
#
# `make` or `make help` lists every target.

.DEFAULT_GOAL := help

BASE_IMAGE   ?= openhexa-base-environment
BLSQ_IMAGE   ?= openhexa-blsq-environment
BLSQ_R_IMAGE ?= openhexa-blsq-r-environment
PLATFORM     ?= linux/amd64

# Settings of the run-* targets.
RUN_PORT     ?= 8890
RUN_TOKEN    ?= hexa
RUN_PREFIX   := openhexa-run

# docker-py ignores Docker CLI contexts, so pin both build and tests to the active endpoint.
ifeq ($(strip $(DOCKER_HOST)),)
DOCKER_HOST := $(shell docker context inspect --format '{{.Endpoints.docker.Host}}' 2>/dev/null)
endif
export DOCKER_HOST

DOCKER_BUILD := docker build --platform $(PLATFORM)
PYTEST       := python -m pytest tests/ -v

.PHONY: help h build-base build-blsq build-blsq-r b build \
	test-base test-blsq test-blsq-r t test run-base run-blsq run-blsq-r stop deps ci

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

##@ Run

# Serves an image as a standalone JupyterLab, the way the tests do: no hub, no
# OpenHEXA app. CONTENT_SECURITY_POLICY is required by jupyter_notebook_config.py.
define run_image
	docker rm -f $(RUN_PREFIX)-$(1) >/dev/null 2>&1 || true
	docker run -d --name $(RUN_PREFIX)-$(1) -p $(RUN_PORT):8888 \
		-e CONTENT_SECURITY_POLICY="frame-ancestors 'self'" \
		$(2) notebook --ServerApp.token=$(RUN_TOKEN) --ServerApp.password=''
	@echo "JupyterLab: http://localhost:$(RUN_PORT)/lab?token=$(RUN_TOKEN)  (make stop to remove)"
endef

run-base: ## Serve the base image as JupyterLab on RUN_PORT (default 8890)
	$(call run_image,base,$(BASE_IMAGE))

run-blsq: ## Serve the blsq image as JupyterLab on RUN_PORT
	$(call run_image,blsq,$(BLSQ_IMAGE))

run-blsq-r: ## Serve the blsq-r image as JupyterLab on RUN_PORT
	$(call run_image,blsq-r,$(BLSQ_R_IMAGE))

stop: ## Remove the containers started by the run-* targets
	docker rm -f $(RUN_PREFIX)-base $(RUN_PREFIX)-blsq $(RUN_PREFIX)-blsq-r 2>/dev/null || true

##@ Misc

deps: ## Install the Python test dependencies and the Chromium the UI tests drive
	pip install .
	python -m playwright install chromium

ci: build-base test-base build-blsq test-blsq build-blsq-r test-blsq-r ## Full pipeline: build + test base, blsq, blsq-r
