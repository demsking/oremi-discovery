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

- [Getting Started with Oremi Discovery](#getting-started-with-oremi-discovery)
- [Starting the Server with Certificates](#starting-the-server-with-certificates)
- [JSON-RPC API](#json-rpc-api)
  * [`register` Method](#register-method)
  * [`subscribe` Method](#subscribe-method)
  * [`unsubscribe` Method](#unsubscribe-method)
  * [Error Handling](#error-handling)
- [Contribute](#contribute)
- [Versioning](#versioning)
- [License](#license)

## Getting Started with Oremi Discovery

The easiest way to use Oremi Discovery is with Docker. Start with Docker for a
quick setup. Follow these steps:

**Using Docker**

Use the official Docker image `demsking/oremi-discovery`. Open your terminal
and run:

```sh
docker run -d -p 5105:5105 demsking/oremi-discovery
```

This fetches Oremi Discovery and starts it on port `5105`.

**Alternative Installation**

If you prefer installing Oremi Discovery directly:

```sh
pip install oremi-discovery
```

After installation, start Oremi Discovery using the provided command.

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

## Starting the Server with Certificates

To start the Oremi Discovery server with a certificate, you can use the
`--cert-file` and `--key-file` options to specify the certificate and private
key files. Additionally, if your private key is password-protected, you can use
the `--password` option to provide the password. Here's how to proceed:

1. **Generate a Self-Signed SSL Certificate (For Testing):**

   If you're testing Oremi Discovery locally, you can generate a self-signed
   SSL certificate.
   Follow these steps to generate a self-signed certificate using OpenSSL:

   ```sh
   # Generate a self-signed certificate
   openssl req -x509 -nodes -new -sha256 -days 365 -newkey rsa:2048 \
     -subj "/C=CM/CN=localhost" \
     -keyout key.pem \
     -out cert.pem
   ```

   It's important to note that these certificates are self-signed, which means
   they are not issued by a recognized Certificate Authority (CA). While
   suitable for testing and development purposes, self-signed certificates may
   trigger security warnings in browsers and other client applications.

   Please note that this is a simplified example for generating self-signed
   certificates for testing purposes. In production environments, it's
   recommended to obtain SSL certificates from a trusted Certificate
   Authority (CA) like [Let's Encrypt](https://letsencrypt.org/) to ensure
   security and proper authentication..
   Let's Encrypt provides free and automated certificates that are recognized
   by most browsers and clients.

2. **Start the Server using Docker:**

   The quickest way to start the Oremi Discovery server with certificates is by
   using Docker. Run the following command in your terminal:

   ```sh
   docker run -d \
      -p 5105:5105 \
      -v /path/to/cert.pem:/cert.pem \
      -v /path/to/key.pem:/key.pem \
    demsking/oremi-discovery \
      --cert-file /cert.pem \
      --key-file /key.pem \
      --password your_private_key_password
   ```

   > Replace `/path/to/cert.pem`, `/path/to/key.pem`, and
   > `your_private_key_password` with the appropriate values.

   This command mounts the certificate and key files into the Docker container
   and starts the server.

## JSON-RPC API

Oremi Discovery supports JSON-RPC requests and responses for both registering,
subscribing and unsubscribing to services.

### `register` Method

Registers a service with the Oremi Discovery service.

**Parameters**

| Name      | Type     | Description                                                        |
|-----------|----------|--------------------------------------------------------------------|
| `status`  | String   | Status of the service (`"ONLINE"` or `"OFFLINE"`).                 |
| `service` | Object   | Service data including `name`, `protocol`, `host`, `port`, `data`. |

**Example Request**

```json
{
  "id": 1,
  "jsonrpc": "2.0",
  "method": "register",
  "params": {
    "status": "ONLINE",
    "service": {
      "name": "mqtt",
      "protocol": "mqtt",
      "host": "test.mosquitto.org",
      "port": 1883,
      "data": {
        "optional": "additional data"
      }
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
    "service": {
      "name": "mqtt",
      "protocol": "mqtt",
      "host": "test.mosquitto.org",
      "port": 1883,
      "uri": "mqtt://test.mosquitto.org:1883",
      "data": {
        "optional": "additional data"
      }
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
