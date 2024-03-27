import argparse

from .package import APP_DESCRIPTION
from .package import APP_NAME
from .package import APP_VERSION


def parse_arguments() -> argparse.Namespace:
  parser = argparse.ArgumentParser(prog = APP_NAME, description = APP_DESCRIPTION)

  parser.add_argument(
    '--host',
    type = str,
    default = '127.0.0.1',
    help = 'Host address to listen on (default: 127.0.0.1).',
  )

  parser.add_argument(
    '-p', '--port',
    type = int,
    default = 5105,
    help = 'Port number to listen on (default: 5105).',
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
