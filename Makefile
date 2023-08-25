APP_VERSION := $(shell python oremi_discovery/version.py)
IMAGE_NAME := demsking/oremi-discovery

SSL_PATH := ssl
SSL_CERT_FILE := $(SSL_PATH)/localhost.pem

.PHONY: all certificates clean dist tests install test image discovery-server-package discovery-client-package publish-discovery-server publish-discovery-client

# Start the development environment using tmuxinator
env:
	tmuxinator

$(SSL_CERT_FILE):
	mkdir -p $(shell dirname $@)
	openssl req -x509 -nodes -new -sha256 -days 1024 -newkey rsa:2048 \
	  -subj "/C=CM/CN=localhost" \
	  -keyout $(SSL_PATH)/localhost-key.pem \
	  -out $(SSL_CERT_FILE)

certificates: $(SSL_CERT_FILE)

start-wss: certificates
	poetry run oremi-discovery \
	  --verbose \
	  --host :: \
	  --port 5106 \
	  --cert-file $(SSL_CERT_FILE) \
	  --key-file $(SSL_PATH)/localhost-key.pem

start-ws:
	poetry run oremi-discovery --verbose --host ::

client-wss: certificates
	python -m clients.python.example --port 5106 \
	  --cert-file $(SSL_CERT_FILE)

client-ws:
	python -m clients.python.example

# Run linting checks on the codebase using pre-commit
lint:
	pre-commit run --all-files

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
	rm -rf dist/ ssl/ build/

# Build a distribution of the project using poetry and twine
discovery-server-package:
	rm -rf dist/
	poetry build --no-cache --format=wheel
	twine check dist/*

discovery-client-package:
	cd clients/python \
	  && rm -rf dist/ \
	  && poetry build --no-cache --format=wheel \
	  && twine check dist/*

dist: discovery-server-package discovery-client-package

# Publish a distribution of the project to TestPyPI using twine
publish-discovery-server: discovery-server-package
	twine upload -r testpypi dist/*

publish-discovery-client: discovery-client-package
	twine upload -r testpypi clients/python/dist/*

install:
	pip install poetry pylint pylint_pydantic
	poetry install

build/images/$(IMAGE_NAME).tar.gz: image.nix
	mkdir -p $(shell dirname $@)
	nix-build -v -A docker --out-link $@ $<
	$@ | docker load
	docker tag $(IMAGE_NAME):$(APP_VERSION) $(IMAGE_NAME):latest

image: build/images/$(IMAGE_NAME).tar.gz

publish-image: image
	git commit . -m "Release $(APP_VERSION)"
	git tag v$(APP_VERSION)
	docker push $(IMAGE_NAME):$(APP_VERSION)
	docker push $(IMAGE_NAME):latest
	git push --tags origin main
