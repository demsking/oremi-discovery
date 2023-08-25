import argparse
import asyncio
import logging
import ssl

from oremi.core.logger import Logger
from oremi_discovery_client import DiscoveryClient, Service


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


async def main() -> None:
  async def register_service() -> None:
    await client.register(service, lambda result: logger.info(f'Subscribing result: {result}'))
    await asyncio.sleep(1)
    await client.watch('mqtt', lambda event: logger.info(f'Watching service event: {event}'))
    await asyncio.sleep(1)
    await client.unwatch('mqtt', lambda result: logger.info(f'Unwatching result: {result}'))
    await asyncio.sleep(1)
    await client.disconnect()


  args = parse_arguments()
  service = Service(
    name = 'mqtt',
    protocol = 'mqtt',
    host = 'test.mosquitto.org',
    port = 1883,
  )

  host = f'{args.host}:{args.port}'
  logger = Logger.create('discovery-client', level = logging.DEBUG)
  ssl_context = None

  if args.cert_file:
    logger.info(f'Using certificat file "{args.cert_file}"')
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(args.cert_file)

  client = DiscoveryClient(
    uri = f'wss://{host}' if args.cert_file else f'ws://{host}',
    user_agent = 'Discovery Client/1.0.0',
    logger = logger,
    on_connected = register_service,
    ssl = ssl_context,
  )

  await client.connect()


try:
  asyncio.run(main())
except KeyboardInterrupt:
  pass
