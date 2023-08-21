import asyncio
import logging
from clients.oremi_discovery_client import DiscoveryClient, Service


async def register_service():
  await client.register(service, lambda result: print(f'Subscribing result: {result}'))
  await asyncio.sleep(1)
  await client.watch('mqtt', lambda event: print(f'Watching service event: {event}'))
  await asyncio.sleep(1)
  await client.unwatch('mqtt', lambda result: print(f'Unwatching result: {result}'))


service = Service(
  name = 'mqtt',
  protocol = 'mqtt',
  host = 'test.mosquitto.org',
  port = 1883,
)

logger = logging.Logger('discovery-client', logging.DEBUG)
client = DiscoveryClient(
  uri = 'ws://127.0.0.1:5105',
  user_agent = 'Discovery Client/1.0.0',
  logger = logger,
  on_connected = register_service,
)

try:
  asyncio.run(client.connect())
except KeyboardInterrupt:
  pass
