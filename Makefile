APP_NAME := $(shell python metadata.py name)
APP_VERSION := $(shell python metadata.py version)
IMAGE_NAME := demsking/$(APP_NAME)

SSL_PATH := ./build/ssl
SSL_CERT_FILE := $(SSL_PATH)/localhost.pem

.PHONY: all certificates clean dist tests install test image discovery-server-package discovery-client-package publish-discovery-server publish-discovery-client build/requirements.txt

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

server-wss: certificates
	poetry run oremi-discovery \
	  --verbose \
	  --host localhost \
	  --port 8106 \
	  --cert-file $(SSL_CERT_FILE) \
	  --key-file $(SSL_PATH)/localhost-key.pem

server-ws:
	poetry run oremi-discovery \
	  --verbose \
	  --host localhost \
	  --port 8107

client-python-ws:
	python -m clients.python.example --port 8107

client-python-wss: certificates
	python -m clients.python.example \
	  --port 8106 \
	  --cert-file $(SSL_CERT_FILE)

client-dart-ws:
	dart run clients/dart/example/main.dart --port 8107

client-dart-wss: certificates
	dart run clients/dart/example/main.dart \
	  --port 8106 \
	  --cert-file $(SSL_CERT_FILE)

help-server:
	poetry run oremi-discovery --help

help-cli:
	poetry -C clients/python run oremi-discovery-cli --help

# Run linting checks on the codebase using pre-commit
lint:
	cd clients/dart && dart fix --dry-run
	pre-commit run --all-files

# Automatically fix any linting issues found by ruff
fix:
	ruff check . --fix
	cd clients/dart && dart fix

test-dart:
	cd dart && clients/dart test \
	  --chain-stack-traces \
	  --platform vm \
	  --coverage ../../coverage/dart

test-python:
	pytest

test: test-dart test-python

watch-test-dart:
	nodemon -e dart -w dart -x 'make test-dart'

watch-test-python:
	nodemon -e oremi -w dart -x 'make test-python'

watch-test:
	$(MAKE) -j2 watch-test-dart watch-test-python

# Generate a coverage report for the codebase using pytest
coverage:
	pytest --cov=oremi

# Generate an HTML coverage report for the codebase using pytest
coverage-html:
	pytest --cov=oremi --cov-report=html

# Show outdated dependencies using poetry
outdated:
	poetry show --outdated
	poetry show -C clients/dart --outdated

# Update dev env
update:
	poetry update
	dart pub -C clients/dart/ upgrade
	nix flake update
	pre-commit autoupdate

# Clean up build artifacts and temporary files
clean:
	rm -rf dist/ build/ clients/python/dist/

# Build a distribution of the project using poetry and twine
discovery-server-package:
	rm -rf dist/
	poetry build --no-cache --format=wheel
	twine check dist/*

discovery-client-package:
	cd clients/python \
	  && rm -rf dist/ \
	  && poetry build --no-cache \
	  && twine check dist/*

dist: discovery-server-package discovery-client-package

# Publish a distribution of the project to TestPyPI using twine
publish-discovery-server: discovery-server-package
	twine upload -r testpypi dist/*

publish-discovery-client: discovery-client-package
	twine upload -r testpypi clients/python/dist/*

install:
	poetry install

build/requirements.txt:
	poetry export --only=main --without-hashes -f requirements.txt -o $@

image: build/requirements.txt
	docker build \
	  --progress plain . -t $(IMAGE_NAME):$(APP_VERSION) \
	  --build-arg PACKAGE_NAME="$(APP_NAME)" \
	  --build-arg CREATED_DATE="$(shell date --rfc-3339=seconds)" \
	  --build-arg MAINTAINER="$(shell python metadata.py authors)" \
	  --build-arg DESCRIPTION="$(shell python metadata.py description)" \
	  --build-arg DOCUMENTATION="$(shell python metadata.py documentation)" \
	  --build-arg VERSION="$(APP_VERSION)" \
	  --build-arg REVISION="$(shell git rev-parse HEAD)" \
	  --build-arg SOURCE_URL="$(shell python metadata.py repository)" \
	  --build-arg LICENSE="$(shell python metadata.py license)"
	docker tag $(IMAGE_NAME):$(APP_VERSION) $(IMAGE_NAME):latest

publish-image: image
	git commit pyproject.toml -m "Release $(APP_VERSION)"
	git tag v$(APP_VERSION)
	docker push $(IMAGE_NAME):$(APP_VERSION)
	docker push $(IMAGE_NAME):latest
	git push --tags origin main
