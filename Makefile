# Makefile for Docsray MCP Server
# Provides convenient commands for development, testing, and Docker operations

.PHONY: help install install-dev install-docker clean test test-unit test-integration test-docker
.PHONY: docker-build docker-test docker-run docker-compose-up docker-compose-down
.PHONY: lint format type-check pre-commit
.PHONY: docs docs-serve release

# Default target
help:
	@echo "Docsray MCP Server - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install          Install the package"
	@echo "  install-dev      Install with development dependencies"
	@echo "  install-docker   Install with Docker testing dependencies"
	@echo "  clean            Clean build artifacts and caches"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-docker      Run Docker tests only"
	@echo ""
	@echo "Docker Operations:"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-test      Run Docker tests"
	@echo "  docker-run       Run Docker container"
	@echo "  docker-compose-up    Start with Docker Compose"
	@echo "  docker-compose-down  Stop Docker Compose services"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint             Run linting (ruff)"
	@echo "  format           Format code (black)"
	@echo "  type-check       Run type checking (mypy)"
	@echo "  pre-commit       Run pre-commit hooks"
	@echo ""
	@echo "Documentation:"
	@echo "  docs             Build documentation"
	@echo "  docs-serve       Serve documentation locally"
	@echo ""
	@echo "Release:"
	@echo "  release          Build and publish to PyPI"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-docker:
	pip install -e ".[docker]"

install-all:
	pip install -e ".[all]"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf htmlcov-docker/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Testing targets
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v -k "not docker"

test-docker: install-docker
	@echo "Running Docker tests..."
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "Error: Docker is not installed or not in PATH"; \
		exit 1; \
	fi
	pytest tests/integration/test_docker.py -v -m docker --tb=short

test-docker-verbose: install-docker
	pytest tests/integration/test_docker.py -v -m docker -s --tb=long

test-coverage:
	pytest tests/ --cov=src/docsray --cov-report=html --cov-report=term-missing

# Docker targets
docker-build:
	docker build -t docsray-mcp .

docker-build-dev:
	docker build -f .devcontainer/Dockerfile -t docsray-mcp:dev .

docker-test: docker-build
	@echo "Running Docker container tests..."
	docker run --rm docsray-mcp docsray --version
	docker run --rm -e DOCSRAY_LOG_LEVEL=DEBUG docsray-mcp python -c "from docsray.server import DocsrayServer; print('Import successful')"

docker-run:
	docker run -it --rm docsray-mcp

docker-run-http:
	docker run -it --rm -p 3000:3000 -e DOCSRAY_TRANSPORT=http docsray-mcp docsray start --transport http --port 3000

docker-compose-up:
	docker-compose up -d

docker-compose-up-dev:
	docker-compose -f docker-compose.dev.yml up -d

docker-compose-down:
	docker-compose down

docker-compose-logs:
	docker-compose logs -f

docker-clean:
	docker system prune -f
	docker image prune -f

# Code quality targets
lint:
	ruff check src/ tests/

lint-fix:
	ruff check --fix src/ tests/

format:
	black src/ tests/

format-check:
	black --check src/ tests/

type-check:
	mypy src/

pre-commit: format lint type-check test-unit

# Documentation targets
docs:
	@echo "Building documentation..."
	@if [ -d "docs/" ]; then \
		cd docs && mkdocs build; \
	else \
		echo "No docs directory found"; \
	fi

docs-serve:
	@echo "Serving documentation..."
	@if [ -d "docs/" ]; then \
		cd docs && mkdocs serve; \
	else \
		echo "No docs directory found"; \
	fi

# Release targets
build:
	python -m build

release: clean build
	python -m twine upload dist/*

release-test: clean build
	python -m twine upload --repository testpypi dist/*

# Development helpers
dev-setup: install-all
	pre-commit install

dev-test: pre-commit test

dev-docker: docker-build test-docker

# CI targets (for GitHub Actions)
ci-test:
	pytest tests/ --cov=src/docsray --cov-report=xml

ci-docker-test: install-docker
	pytest tests/integration/test_docker.py -v -m docker --tb=short --maxfail=3

# Utility targets
version:
	python -c "from src.docsray import __version__; print(__version__)"

check-deps:
	pip check

security-check:
	pip-audit

# Docker Compose profiles
compose-full:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

compose-monitoring:
	docker-compose --profile monitoring up -d

compose-jupyter:
	docker-compose -f docker-compose.dev.yml --profile jupyter up -d