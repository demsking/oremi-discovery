APP_VERSION := $(shell python oremi_discovery/version.py)
IMAGE_NAME := demsking/oremi-discovery

.PHONY: all clean tests install test image

# Start the development environment using tmuxinator
env:
	tmuxinator

start:
	poetry run oremi-discovery --verbose --host 0.0.0.0

client:
	python -m examples.client

# Run linting checks on the codebase using pre-commit
lint:
	pre-commit run --all-files

# Automatically fix any linting issues found by ruff
fix:
	ruff check . --fix

# Run tests using pytest
test:
	pytest

# Generate a coverage report for the codebase using pytest
coverage:
	pytest --cov=oremi

# Generate an HTML coverage report for the codebase using pytest
coverage-html:
	pytest --cov=oremi --cov-report=html

# Show outdated dependencies using poetry
outdated:
	poetry show --outdated

# Update dev env
update:
	poetry update
	nix flake update
	pre-commit autoupdate

# Clean up build artifacts and temporary files
clean:
	rm -rf dist/

# Build a distribution of the project using poetry and twine
dist:
	rm -rf dist/
	poetry build
	twine check dist/*

# Publish a distribution of the project to TestPyPI using twine
publish: dist
	twine upload -r testpypi dist/*

install:
	poetry install

build/images/$(IMAGE_NAME).tar.gz: image.nix
	mkdir -p $(shell dirname $@)
	nix-build -v -A docker --out-link $@ $<
	$@ | docker load
	docker tag $(IMAGE_NAME):$(APP_VERSION) $(IMAGE_NAME):latest

image: build/images/$(IMAGE_NAME).tar.gz

publish-image:
	git commit . -m "Release $(APP_VERSION)"
	git tag v$(APP_VERSION)
	docker push $(IMAGE_NAME):$(APP_VERSION)
	docker push $(IMAGE_NAME):latest
	git push --tags origin main
