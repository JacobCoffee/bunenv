SHELL := /bin/bash
# =============================================================================
# Variables
# =============================================================================

.DEFAULT_GOAL:=help
.ONESHELL:
UV_OPTS ?=
UV ?= uv $(UV_OPTS)

.EXPORT_ALL_VARIABLES:

.PHONY: help
.PHONY: docs-clean docs-serve docs

help: ## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# =============================================================================
# Docs
# =============================================================================

##@ Documentation

docs-clean: ## Dump the existing built docs
	@echo "=> Cleaning documentation build assets"
	@rm -rf docs/_build
	@echo "=> Removed existing documentation build assets"

docs-serve: docs-clean ## Serve the docs locally
	@echo "=> Serving documentation"
	$(UV) run sphinx-autobuild docs docs/_build/ -j auto --watch src --watch docs --port 8002

docs: docs-clean ## Dump the existing built docs and rebuild them
	@echo "=> Building documentation"
	@$(UV) run sphinx-build -M html docs docs/_build/ -E -a -j auto --keep-going
