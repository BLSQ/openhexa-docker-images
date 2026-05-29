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
#   make deps        # install the Python test dependencies

BASE_IMAGE   ?= openhexa-base-environment
BLSQ_IMAGE   ?= openhexa-blsq-environment
BLSQ_R_IMAGE ?= openhexa-blsq-r-environment
PLATFORM     ?= linux/amd64

# docker-py ignores Docker CLI contexts, so pin both build and tests to the active endpoint.
ifeq ($(strip $(DOCKER_HOST)),)
DOCKER_HOST := $(shell docker context inspect --format '{{.Endpoints.docker.Host}}' 2>/dev/null)
endif
export DOCKER_HOST

DOCKER_BUILD := docker build --platform $(PLATFORM)
PYTEST       := python -m pytest tests/ -v

## Build

build-base:
	@echo "Building the base image"
	$(DOCKER_BUILD) -t $(BASE_IMAGE) images/base

build-blsq: build-base
	@echo "Building the blsq image"
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(BLSQ_IMAGE) images/blsq

build-blsq-r: build-base
	@echo "Building the blsq-r image"
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(BLSQ_R_IMAGE) images/blsq-r

b build: build-base build-blsq build-blsq-r

## Test

test-base:
	@echo "Testing the base image"
	$(PYTEST) --docker-image $(BASE_IMAGE)

test-blsq:
	@echo "Testing the blsq image"
	$(PYTEST) --docker-image $(BLSQ_IMAGE)

test-blsq-r:
	@echo "Testing the blsq-r image"
	$(PYTEST) --docker-image $(BLSQ_R_IMAGE)

t test: test-base test-blsq test-blsq-r

## Misc

deps:
	@echo "Installing test dependencies"
	pip install .

ci: build-base test-base build-blsq test-blsq build-blsq-r test-blsq-r
