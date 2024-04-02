# Copyright 2023 Sébastien Demanou. All Rights Reserved.
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

from .args import parse_arguments
from .models import Service
from .package import APP_NAME
from .package import APP_VERSION
from .service import DiscoveryService


async def start() -> None:
  loop = asyncio.get_event_loop()
  args = parse_arguments()
  log_level = logging.DEBUG if args.verbose else logging.INFO
  logger = Logger.create(APP_NAME, filename=args.log_file, level=log_level)
  discovery = DiscoveryService(
    client_id=f'{APP_NAME}/{APP_VERSION}',
    channel=args.discovery_channel,
    logger=logger,
  )

  logger.info(f'Starting {discovery.client_id}')
  logger.info(f'Log level {"DEBUG" if logger.level == logging.DEBUG else "INFO"}')

  await discovery.connect(args.mqtt_host, args.mqtt_port)

  service = Service(
    name=args.service_name,
    version=args.service_version,
    protocol=args.service_protocol,
    host=args.service_host,
    port=args.service_port,
    data=json.loads(args.service_data),
  )

  discovery.publish(service)

  # Register the signal handlers
  for signame in [signal.SIGINT, signal.SIGTERM]:
    loop.add_signal_handler(signame, lambda signame=signame: discovery.disconnect())

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
