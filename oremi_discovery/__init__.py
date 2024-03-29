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
import logging
import signal

from .args import parse_arguments # pylint: disable=import-error
from .config import APP_NAME
from .config import APP_VERSION
from .manager import SubscriptionManager

__all__ = ['start', 'main']


async def start() -> None:
  loop = asyncio.get_event_loop()
  args = parse_arguments()

  # Set up logging
  logger = logging.getLogger(APP_NAME)
  logger.setLevel(logging.INFO)
  ch = logging.StreamHandler()
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)

  # Set up manager
  manager = SubscriptionManager(client_id=args.client_id, logger=logger)

  def shutdown():
    logger.info(f'Shutting down {APP_NAME} {APP_VERSION}')
    manager.stop()
    for task in asyncio.all_tasks():
      task.cancel()

  # Wait until a signal is received
  for signame in [signal.SIGINT, signal.SIGTERM]:
    loop.add_signal_handler(signame, lambda signame=signame: shutdown())

  logger.info(f'Starting {APP_NAME} {APP_VERSION}')
  manager.start(args.host, args.port)

  # Keep the main coroutine running until SIGINT or SIGTERM is received
  await asyncio.Future()


def main() -> None:
  try:
    asyncio.run(start())
  except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
    pass
