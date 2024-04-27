# Copyright 2024 Sébastien Demanou. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import asyncio
import json
import logging
import signal

from oremi_core.logger import Logger
from oremi_discovery.args import parse_arguments
from oremi_discovery.models import Service
from oremi_discovery.package import APP_NAME
from oremi_discovery.service import DiscoveryService


async def start() -> None:
  loop = asyncio.get_event_loop()
  args = parse_arguments()
  log_level = logging.DEBUG if args.verbose else logging.INFO
  logger = Logger.create(APP_NAME, filename=args.log_file, level=log_level)
  discovery = DiscoveryService(
    client_id=args.client_id if args.service_name else f'{args.service_name}/{args.service_version}',
    channel=args.discovery_channel,
    logger=logger,
  )

  logger.info(f'Starting {discovery.client_id}')
  logger.info(f'Log level {"DEBUG" if logger.level == logging.DEBUG else "INFO"}')

  await discovery.connect(args.mqtt_host, args.mqtt_port)

  service = Service(
    name=args.service_name,
    version=args.service_version,
    uri=args.service_uri,
    data=json.loads(args.service_data),
  )

  async def shutdown(sigid: signal.Signals, loop):
    logger.info(f'Received exit signal {sigid.name}...')
    logger.info('Gracefully stopping...')
    for task in asyncio.all_tasks():
      task.cancel()

  # Register the signal handlers
  for signame in [signal.SIGINT, signal.SIGTERM]:
    loop.add_signal_handler(signame, lambda signame=signame: asyncio.create_task(shutdown(signame, loop)))

  discovery.publish(service)

  # Run the server
  try:
    await asyncio.Future()
  except asyncio.CancelledError:
    logger.info('Shutting down...')


def main() -> None:
  try:
    asyncio.run(start())
  except KeyboardInterrupt:
    pass
