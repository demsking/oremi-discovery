import argparse

from .config import APP_DESCRIPTION
from .config import APP_NAME
from .config import APP_VERSION


def parse_arguments() -> argparse.Namespace:
  parser = argparse.ArgumentParser(prog = APP_NAME, description = APP_DESCRIPTION)

  parser.add_argument(
    '--host',
    type = str,
    default = 'test.mosquitto.org',
    help = 'Host address of the MQTT broker (default: test.mosquitto.org).',
  )

  parser.add_argument(
    '-p', '--port',
    type = int,
    default = 1883,
    help = 'Port number of the MQTT broker (default: 1883).',
  )

  parser.add_argument(
    '--client-id',
    type=str,
    default=None,
    help='Client ID for MQTT connection (default: randomly generated).',
  )

  parser.add_argument(
    '-v', '--version',
    action = 'version',
    version = f'%(prog)s {APP_VERSION}',
    help = 'Show the version of the application.',
  )

  return parser.parse_args()
