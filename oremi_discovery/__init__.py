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

import argparse
import asyncio
import logging

from oremi.core.logger import Logger

from .package import APP_DESCRIPTION, APP_NAME, APP_VERSION
from .server import listen

__all__ = ['listen', 'main']


def parse_arguments() -> argparse.Namespace:
  """
  Parse command-line arguments.

  Returns:
    argparse.Namespace: The parsed command-line arguments.
  """
  # Create the ArgumentParser instance
  parser = argparse.ArgumentParser(prog = APP_NAME, description = APP_DESCRIPTION)

  # Define command-line arguments
  parser.add_argument(
    '--host',
    type = str,
    default = '127.0.0.1',
    help = 'Host address to connect to (default: 127.0.0.1).',
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

  parser.add_argument(
    '--key-file',
    type = str,
    help = 'Path to the private key file for secure connection.',
  )

  parser.add_argument(
    '--password',
    type = str,
    help = 'Password to unlock the private key (if protected by a password).',
  )

  parser.add_argument(
    '--log-file',
    type = str,
    default = None,
    help = 'Name of the log file.',
  )

  parser.add_argument(
    '--verbose',
    action = 'store_true',
    help = 'Enable verbose logging.',
  )

  parser.add_argument(
    '-v', '--version',
    action = 'version',
    version = f'%(prog)s {APP_VERSION}',
    help = 'Show the version of the application.',
  )

  return parser.parse_args()


async def start() -> None:
  args = parse_arguments()
  verbose: bool = args.verbose
  log_level = logging.DEBUG if verbose else logging.INFO
  logger = Logger.create(APP_NAME, filename = args.log_file, level = log_level)

  await listen(
    host = args.host,
    port = args.port,
    cert_file = args.cert_file,
    key_file = args.key_file,
    password = args.password,
    logger = logger,
  )


def main():
  try:
    asyncio.run(start())
  except KeyboardInterrupt:
    pass
