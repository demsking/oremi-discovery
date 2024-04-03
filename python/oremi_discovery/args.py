import argparse

from oremi_discovery.package import APP_DESCRIPTION
from oremi_discovery.package import APP_NAME


def parse_arguments():
  parser = argparse.ArgumentParser(prog=APP_NAME, description=APP_DESCRIPTION)

  parser.add_argument(
    '--mqtt-host',
    type=str,
    required=True,
    help='MQTT broker host address.'
  )

  parser.add_argument(
    '--mqtt-port',
    type=int,
    default=1883,
    help='MQTT broker port number.'
  )

  parser.add_argument(
    '--discovery-channel',
    type=str,
    default='discovery',
    help='MQTT base topic for discovery messages.'
  )

  parser.add_argument(
    '--service-name',
    type=str,
    required=True,
    help='Name of the service used to register discovery service.',
  )

  parser.add_argument(
    '--service-version',
    type=str,
    required=True,
    help='Version of the service used to register discovery service.',
  )

  parser.add_argument(
    '--service-protocol',
    type=str,
    required=True,
    help='Protocol used to register discovery service. Example: "http", "wss", "ws".',
  )

  parser.add_argument(
    '--service-host',
    type=str,
    required=True,
    help='Host used to register discovery service.',
  )

  parser.add_argument(
    '--service-port',
    type=int,
    required=True,
    help='Port used to register discovery service.',
  )

  parser.add_argument(
    '--service-data',
    type=str,
    default='{}',
    help='Data used to register discovery service.',
  )

  parser.add_argument(
    '--log-file',
    type=str,
    default=None,
    help='Name of the log file.',
  )

  parser.add_argument(
    '--verbose',
    action='store_true',
    help='Enable verbose logging.',
  )

  return parser.parse_args()
