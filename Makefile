# Makefile for building and testing the OpenHexa Docker images locally.
#
# This mirrors the checks in .github/workflows/build_image.yml, but runs them
# against your local Docker daemon. Because `docker build` writes directly to
# the local daemon, the dependent images (blsq, blsq-r) can reference the
# freshly built base image by tag — no local registry is needed like in CI.
#
# Common usage:
#   make ci          # full pipeline: build + test base, build + test blsq, build blsq-r
#   make build       # build all three images
#   make test        # test base and blsq (matches CI)
#   make build-base  # build a single image
#   make test-base   # test a single image

# Image tags (local, no registry prefix needed).
BASE_IMAGE   ?= openhexa-base-environment
BLSQ_IMAGE   ?= openhexa-blsq-environment
BLSQ_R_IMAGE ?= openhexa-blsq-r-environment

# CI builds for linux/amd64. Override with `make PLATFORM=linux/arm64 ...` if needed.
PLATFORM ?= linux/amd64

# The test suite talks to Docker via docker-py, which ignores Docker CLI
# contexts and connects to the default socket. On setups like Docker Desktop,
# `docker build` (which honours the active context) and the tests can end up on
# different daemons, so the tests fail to find the freshly built image. Pin both
# to the active context's endpoint unless DOCKER_HOST is already set explicitly.
ifeq ($(strip $(DOCKER_HOST)),)
DOCKER_HOST := $(shell docker context inspect --format '{{.Endpoints.docker.Host}}' 2>/dev/null)
endif
export DOCKER_HOST

DOCKER_BUILD := docker build --platform $(PLATFORM)
PYTEST       := python -m pytest tests/ -v

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: deps
deps: ## Install Python test dependencies (pytest, docker, ...)
	pip install .

# --- Build targets --------------------------------------------------------

.PHONY: build-base
build-base: ## Build the base image
	$(DOCKER_BUILD) -t $(BASE_IMAGE) images/base

.PHONY: build-blsq
build-blsq: build-base ## Build the blsq image (depends on base)
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(BLSQ_IMAGE) images/blsq

.PHONY: build-blsq-r
build-blsq-r: build-base ## Build the blsq-r image (depends on base)
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(BLSQ_R_IMAGE) images/blsq-r

.PHONY: build
build: build-base build-blsq build-blsq-r ## Build all images

# --- Test targets ---------------------------------------------------------

.PHONY: test-base
test-base: ## Run the test suite against the base image
	$(PYTEST) --docker-image $(BASE_IMAGE)

.PHONY: test-blsq
test-blsq: ## Run the test suite against the blsq image
	$(PYTEST) --docker-image $(BLSQ_IMAGE)

.PHONY: test-blsq-r
test-blsq-r: ## Run the test suite against the blsq-r image
	$(PYTEST) --docker-image $(BLSQ_R_IMAGE)

.PHONY: test
test: test-base test-blsq test-blsq-r ## Run tests for base, blsq and blsq-r (matches CI)

# --- Full pipeline --------------------------------------------------------

.PHONY: ci
ci: build-base test-base build-blsq test-blsq build-blsq-r test-blsq-r ## Run the full CI build/test pipeline locally
