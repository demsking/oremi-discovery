.PHONY: all certificates clean dist tests install test discovery-package publish-discovery

# Start the development environment using tmuxinator
env:
	tmuxinator

install:
	poetry -C python install
	dart pub -C dart update

outdated:
	poetry -C python show --outdated
	dart pub -C dart outdated

update:
	poetry -C python update
	dart pub -C dart/ upgrade
	nix flake update
	pre-commit autoupdate

server:
	poetry run oremi-discovery

.PHONY: python
python:
	python -m python.example

.PHONY: dart
dart:
	dart run dart/example/main.dart --port 8107

# Run linting checks on the codebase using pre-commit
lint:
	cd dart && dart fix --dry-run
	pre-commit run --all-files

# Automatically fix any linting issues found by ruff
fix:
	ruff check . --fix
	cd dart && dart fix --apply

test-dart:
	cd dart && dart test \
	  --chain-stack-traces \
	  --platform vm \
	  --coverage ../coverage/dart

test-python:
	pytest

test: test-python test-dart

watch-test-dart:
	nodemon -w dart -e dart -x 'make test-dart'

watch-test-python:
	nodemon -w python -e py -x 'make test-python'

watch-test:
	$(MAKE) -j2 watch-test-dart watch-test-python

# Generate a coverage report for the codebase using pytest
.PHONY: coverage
coverage:
	pytest --cov=python/oremi_discovery

# Generate an HTML coverage report for the codebase using pytest
coverage-html:
	pytest --cov=python/oremi_discovery --cov-report=html

# Clean up build artifacts and temporary files
clean:
	rm -rf **/dist **/__pycache__ .ruff_cache .pytest_cache **/.ruff_cache **/.pytest_cache

# Build a distribution of the project using poetry and twine
discovery-package:
	cd python \
	  && rm -rf dist/ \
	  && poetry build --no-cache \
	  && twine check dist/*

packages: discovery-package

# Publish a distribution of the project to TestPyPI using twine
publish: discovery-package
	twine upload -r testpypi python/dist/*
