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
import socket
import uuid
from collections.abc import Callable

import paho.mqtt.client as mqtt

class ServiceDiscoveryPayload:
  def __init__(self, service_name: str, service_address: str, service_port: int) -> None:
    self.service_name = service_name
    self.service_address = service_address
    self.service_port = service_port

class SubscriptionManager:
  def __init__(
    self,
    *,
    client_id: str | None = None,
    topic_prefix: str = 'discovery',
    logger: logging.Logger,
  ) -> None:
    self.client = mqtt.Client(
      callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
      client_id=client_id or str(uuid.uuid4()),
      protocol=mqtt.MQTTv5,
    )

    self.topic_prefix = topic_prefix
    self.subscriptions: dict[str, tuple[Callable[[str, ServiceDiscoveryPayload], None], str, int]] = {}
    self.logger = logger

    self.client.on_connect = self._on_connect
    self.client.on_message = self._on_message
    self.client.on_disconnect = self._on_disconnect

  def start(self, broker_address: str, port: int = 1883) -> None:
    self.logger.info(f'Connecting to {broker_address}:{port}')
    self.client.connect(broker_address, port)
    self.client.loop_start()

  def stop(self) -> None:
    self.client.loop_stop()
    self.client.disconnect()

  def add_subscription(self, topic: str, callback: Callable[[str, ServiceDiscoveryPayload], None], qos: int = 0):
    full_topic = f'{self.topic_prefix}/{topic}'
    if full_topic not in self.subscriptions:
      self.logger.info(f'Incomming subscription {full_topic}')
      self.subscriptions[full_topic] = (callback, '', 0)  # Initialize address and port as empty
      self.client.subscribe(full_topic, qos=qos)

  def remove_subscription(self, topic: str) -> None:
    full_topic = f'{self.topic_prefix}/{topic}'
    if full_topic in self.subscriptions:
      del self.subscriptions[full_topic]
      self.client.unsubscribe(full_topic)

  def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
    if reason_code == mqtt.CONNACK_ACCEPTED:
      self.logger.info(f'Connected to {self.client.host}:{self.client.port}')
      self.logger.info(f'Listening subscriptions {self.topic_prefix}/#')
    else:
      self.logger.error(f'Connection to {self.client.host}:{self.client.port} failed: {mqtt.connack_string(reason_code)}.')

  def _on_message(self, client, userdata, msg) -> None:
    full_topic = msg.topic
    if full_topic in self.subscriptions:
      payload_data = json.loads(msg.payload.decode())
      service_payload = ServiceDiscoveryPayload(**payload_data)
      callback, _, _ = self.subscriptions[full_topic]
      callback(full_topic, service_payload)

  def _on_disconnect(self, client, userdata, flags, reason_code, properties) -> None:
    self.logger.info(f'Disconnected to {self.client.host}:{self.client.port} - {reason_code}')

  async def check_subscriptions(self, timeout: int = 5):
    while True:
      for topic, (callback, address, port) in list(self.subscriptions.items()):
        if address and port:
          try:
            self._check_service_availability(topic, callback, address, port, timeout)
          except Exception as error:
            self.logger.error(f'Error checking service availability for topic {topic}: {error}')
      await asyncio.sleep(30)  # Adjust the interval as needed

  def _check_service_availability(self, topic: str, callback: Callable[[str, ServiceDiscoveryPayload], None], address: str, port: int, timeout: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.settimeout(timeout)
      result = s.connect_ex((address, port))
      if result != 0:  # Service is not available
        self.remove_subscription(topic)
