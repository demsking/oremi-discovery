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
import logging

from oremi_core.logger import Logger

from .args import parse_arguments # pylint: disable=import-error
from .package import APP_NAME
from .package import APP_VERSION
from .server import DiscoveryServer

__all__ = ['DiscoveryServer', 'main']


async def start() -> None:
  args = parse_arguments()
  verbose: bool = args.verbose
  log_level = logging.DEBUG if verbose else logging.INFO
  logger = Logger.create(APP_NAME, filename = args.log_file, level = log_level)

  logger.info(f'Starting {APP_NAME} {APP_VERSION}')
  logger.info(f'Log level {"DEBUG" if logger.level == logging.DEBUG else "INFO"}')

  server = DiscoveryServer(
    logger = logger,
    cert_file = args.cert_file,
    key_file = args.key_file,
    password = args.password,
  )

  await server.listen(args.host, args.port)


def main() -> None:
  try:
    asyncio.run(start())
  except KeyboardInterrupt:
    pass
