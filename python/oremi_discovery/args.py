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
    '--client-id',
    type=str,
    help='MQTT base client ID. Default service-name/service-version.'
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
    '--service-uri',
    type=str,
    required=True,
    help='Service URI used to register discovery service. Example: "http://host:port", "wss://host:port", "ws://host:port".',
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
