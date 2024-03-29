import asyncio
import logging

from oremi_discovery_client import DiscoveryService
from oremi_discovery_client import Service
from oremi_discovery_client import Subscription

# Example usage:
async def main():
  logger = logging.getLogger('discovery-example')
  logger.setLevel(logging.INFO)
  ch = logging.StreamHandler()
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)

  discovery = DiscoveryService(client_id='oremi-example', logger=logger)
  service1 = Service(name='Service1', host='192.168.1.100', port=8080)
  service2 = Service(name='Service2', host='192.168.1.100', port=8080)

  await discovery.start('test.mosquitto.org')

  def on_service_available(subscription: Subscription):
    logger.info(subscription)

  discovery.watch('Service1', on_service_available)
  discovery.watch('Service2', on_service_available)

  await asyncio.sleep(1)
  discovery.publish(service1)

  await asyncio.sleep(1)
  discovery.publish(service2)

  await asyncio.sleep(2)
  discovery.publish_unavailable(service1)

  # Keep the script running for a while to observe service availability notifications
  input('Press Enter to stop...\n')
  logger.info('Stopping discovery...')
  discovery.stop()

if __name__ == '__main__':
  try:
    asyncio.run(main())
  except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
    pass
