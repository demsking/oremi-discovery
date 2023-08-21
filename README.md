# Oremi Discovery

[![Build status](https://gitlab.com/demsking/oremi-discovery/badges/main/pipeline.svg)](https://gitlab.com/demsking/oremi-discovery/pipelines)
[![Test Coverage](https://gitlab.com/demsking/oremi-discovery/badges/main/coverage.svg)](https://gitlab.com/demsking/oremi-discovery/-/jobs)
[![Buy me a beer](https://img.shields.io/badge/Buy%20me-a%20beer-1f425f.svg)](https://www.buymeacoffee.com/demsking)

A robust WebSocket-powered service discovery solution. Simplify the process of
discovering and connecting to network services dynamically.

With Oremi Discovery, effortlessly locate and interact with services across
your network, enhancing scalability and flexibility in your distributed
systems architecture.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [JSON-RPC API](#json-rpc-api)
  * [`register` Method](#register-method)
  * [`subscribe` Method](#subscribe-method)
  * [`unsubscribe` Method](#unsubscribe-method)
  * [Error Handling](#error-handling)
- [Contribute](#contribute)
- [Versioning](#versioning)
- [License](#license)

## Install

To install the Oremi Discovery service, you have two options:

**1. Install the package from PyPI:**

```sh
pip install oremi-discovery
```

**2. Use the Docker image `demsking/oremi-discovery`:**

```sh
docker run -d -p 5105:5105 demsking/oremi-discovery
```

## Usage

```sh
usage: oremi-discovery [-h] [--host HOST] [-p PORT] [--cert-file CERT_FILE] [--key-file KEY_FILE] [--password PASSWORD]
                       [--log-file LOG_FILE] [--verbose] [-v]

A robust WebSocket-powered service discovery solution

options:
  -h, --help            show this help message and exit
  --host HOST           Host address to connect to (default: 127.0.0.1).
  -p PORT, --port PORT  Port number to connect to (default: 5105).
  --cert-file CERT_FILE
                        Path to the certificate file for secure connection.
  --key-file KEY_FILE   Path to the private key file for secure connection.
  --password PASSWORD   Password to unlock the private key (if protected by a password).
  --log-file LOG_FILE   Name of the log file.
  --verbose             Enable verbose logging.
  -v, --version         Show the version of the application.
```

## JSON-RPC API

Oremi Discovery supports JSON-RPC requests and responses for both registering,
subscribing and unsubscribing to services.

### `register` Method

Registers a service with the Oremi Discovery service.

**Parameters**

| Name      | Type     | Description                                                |
|-----------|----------|------------------------------------------------------------|
| `status`  | String   | Status of the service (`"ONLINE"` or `"OFFLINE"`).         |
| `data`    | Object   | Service data including `name`, `protocol`, `host`, `port`. |

**Example Request**

```json
{
  "id": 1,
  "jsonrpc": "2.0",
  "method": "register",
  "params": {
    "status": "ONLINE",
    "data": {
      "name": "mqtt",
      "protocol": "mqtt",
      "host": "test.mosquitto.org",
      "port": 1883
    }
  }
}
```

**Result**

A successful registration will return a JSON-RPC response indicating success or
an error if registration fails.

```json
{
  "id": 1,
  "jsonrpc": "2.0",
  "result": {
    "ok": true
  }
}
```

### `subscribe` Method

Subscribes to a service registered with the Oremi Discovery service.

**Parameters**

| Name    | Type     | Description                          |
|---------|----------|--------------------------------------|
| `name`  | String   | Name of the service to subscribe to. |

**Example Request**

```json
{
  "id": 2,
  "jsonrpc": "2.0",
  "method": "subscribe",
  "params": {
    "name": "mqtt"
  }
}
```

**Result**

A successful subscription will return a JSON-RPC response indicating success
or an error if subscription fails.

```json
{
  "id": 2,
  "jsonrpc": "2.0",
  "result": {
    "status": "ONLINE",
    "data": {
      "name": "mqtt",
      "protocol": "mqtt",
      "host": "test.mosquitto.org",
      "port": 1883,
      "uri": "mqtt://test.mosquitto.org:1883"
    }
  }
}
```

### `unsubscribe` Method

Unsubscribes from a previously subscribed service.

**Parameters**

| Name    | Type     | Description                              |
|---------|----------|------------------------------------------|
| `name`  | String   | Name of the service to unsubscribe from. |

**Example Request**

```json
{
  "id": 3,
  "jsonrpc": "2.0",
  "method": "unsubscribe",
  "params": {
    "name": "mqtt"
  }
}
```

**Result**

A successful subscription will return a JSON-RPC response indicating success
or an error if subscription fails.

```json
{
  "id": 3,
  "jsonrpc": "2.0",
  "result": {
    "ok": true
  }
}
```

### Error Handling

Possible error codes for failed registration or subscription:

- `1000`: Indicates a normal closure.
- `1003`: Invalid Message
- `4000`: Unexpected Error

## Contribute

Please follow [CONTRIBUTING.md](https://gitlab.com/demsking/oremi-discovery/blob/main/CONTRIBUTING.md).

## Versioning

Given a version number `MAJOR.MINOR.PATCH`, increment the:

- `MAJOR` version when you make incompatible API changes,
- `MINOR` version when you add functionality in a backwards-compatible manner,
  and
- `PATCH` version when you make backwards-compatible bug fixes.

Additional labels for pre-release and build metadata are available as extensions
to the `MAJOR.MINOR.PATCH` format.

See [SemVer.org](https://semver.org/) for more details.

## License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License.
You may obtain a copy of the License at [LICENSE](https://gitlab.com/demsking/oremi-discovery/blob/main/LICENSE).
