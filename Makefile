.PHONY: help install install-dev test test-cov lint format clean build publish docs

help: ## Show this help message
	@echo "Autoppia SDK - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e .[dev]

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=autoppia --cov-report=html --cov-report=term

lint: ## Run linting checks
	flake8 autoppia/ tests/
	mypy autoppia/

format: ## Format code with black and isort
	black autoppia/ tests/
	isort autoppia/ tests/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build package
	python -m build

publish: ## Publish to PyPI (requires twine)
	twine upload dist/*

docs: ## Build documentation
	cd docs && make html

check: ## Run all checks (lint, test, format)
	@echo "Running all checks..."
	@make lint
	@make test
	@echo "All checks passed!"

pre-commit: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	pre-commit run --all-files

version: ## Show current version
	@python -c "import autoppia; print(autoppia.__version__)"

requirements: ## Update requirements.txt
	pip freeze > requirements.txt

docker-build: ## Build Docker image
	docker build -t autoppia-sdk .

docker-run: ## Run Docker container
	docker run -it --rm autoppia-sdk

docker-test: ## Run tests in Docker
	docker run -it --rm autoppia-sdk make test
