import argparse
import asyncio
import logging

from oremi_core.logger import Logger # pylint: disable=import-error
from oremi_discovery_client import DiscoveryClient
from oremi_discovery_client import Service

from oremi_discovery_models import ServiceEvent

def parse_arguments() -> argparse.Namespace:
  parser = argparse.ArgumentParser(prog = 'Discovery Test Client')

  parser.add_argument(
    '--host',
    type = str,
    default = 'localhost',
    help = 'Host address to connect to (default: localhost).',
  )

  parser.add_argument(
    '-p', '--port',
    type = int,
    default = 5105,
    help = 'Port number to connect to (default: 5105).',
  )

  parser.add_argument(
    '--cert-file',
    type = str,
    help = 'Path to the certificate file for secure connection.',
  )

  return parser.parse_args()


class ExampleClient(DiscoveryClient):
  async def on_connect(self) -> None:
    await super().on_connect()

    service = Service(
      name = 'mqtt',
      protocol = 'mqtt',
      host = 'test.mosquitto.org',
      port = 1883,
      data = {
        'env': 'test',
      },
    )

    event = ServiceEvent(status = 'ONLINE', service = service)
    await self.publish(event, lambda result: self.logger.info(f'Subscribing result: {result}'))
    await asyncio.sleep(1)
    await self.watch('mqtt', lambda event: self.logger.info(f'Watching service event: {event}'))
    await asyncio.sleep(1)
    await self.unwatch('mqtt', lambda result: self.logger.info(f'Unwatching result: {result}'))
    await asyncio.sleep(1)
    await self.disconnect()

async def main() -> None:
  args = parse_arguments()

  host = f'{args.host}:{args.port}'
  logger = Logger.create('discovery-client', level = logging.DEBUG)
  ssl_context = None

  if args.cert_file:
    import ssl  # pylint: disable=import-outside-toplevel

    logger.info(f'Using certificat file "{args.cert_file}"')
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(args.cert_file)

  client = ExampleClient(
    uri = f'wss://{host}' if args.cert_file else f'ws://{host}',
    user_agent = 'Discovery Client Python Example/1.0.0',
    logger = logger,
    ssl = ssl_context,
  )

  await client.connect()


try:
  asyncio.run(main())
except KeyboardInterrupt:
  pass
