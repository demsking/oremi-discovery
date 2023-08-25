# Oremi Discovery Client for Python 3

[![Build status](https://gitlab.com/demsking/oremi-discovery/badges/main/pipeline.svg)](https://gitlab.com/demsking/oremi-discovery/pipelines)
[![Test Coverage](https://gitlab.com/demsking/oremi-discovery/badges/main/coverage.svg)](https://gitlab.com/demsking/oremi-discovery/-/jobs)
[![Buy me a beer](https://img.shields.io/badge/Buy%20me-a%20beer-1f425f.svg)](https://www.buymeacoffee.com/demsking)

## Install

```sh
pip install oremi-discovery-client
```

## Usage

```python
from oremi.core.logger import Logger
from oremi_discovery_client import DiscoveryClient, Service


async def register_service() -> None:
    await client.register(service, lambda result: logger.info(f'Subscribing result: {result}'))
    await asyncio.sleep(1)
    await client.watch('mqtt', lambda event: logger.info(f'Watching service event: {event}'))
    await asyncio.sleep(1)
    await client.unwatch('mqtt', lambda result: logger.info(f'Unwatching result: {result}'))
    await asyncio.sleep(1)
    await client.disconnect()


service = Service(
  name = 'mqtt',
  protocol = 'mqtt',
  host = 'test.mosquitto.org',
  port = 1883,
)

client = DiscoveryClient(
  uri = 'ws://localhost:5105',
  user_agent = 'Discovery Client/1.0.0',
  logger = Logger.create('discovery-client', level = logging.DEBUG),
  on_connected = register_service,
)

try:
  asyncio.run(client.connect())
except KeyboardInterrupt:
  pass
```

Please see [example.py](https://gitlab.com/demsking/oremi-discovery/blob/main/clients/python/example.py)
for a complete example with SSL.

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
