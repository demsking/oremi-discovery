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
import uuid
from collections.abc import Callable
from dataclasses import dataclass

import paho.mqtt.client as mqtt
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass(kw_only=True)
class Service:
  name: str
  host: str
  port: int

@dataclass_json
@dataclass(kw_only=True)
class Subscription:
  service: Service
  available: bool = False

class DiscoveryService:
  def __init__(self, *, client_id: str | None = None, topic_prefix: str = 'discovery', logger: logging.Logger):
    self.client_id = client_id or str(uuid.uuid4())
    self.client = mqtt.Client(
      callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
      client_id=self.client_id,
      protocol=mqtt.MQTTv5,
    )

    self.topic_prefix = topic_prefix
    self.logger = logger
    self.subscriptions: dict[str, Callable[[Subscription], None]] = {}
    self.subscribed_services: list[Service] = []

    self.client.on_connect = self._on_connect
    self.client.on_disconnect = self._on_disconnect
    self.connected = False

  async def start(self, broker_address: str, port: int = 1883) -> None:
    self.logger.info(f'Connecting to {broker_address}:{port}')
    self.client.connect_async(broker_address, port, clean_start=True)
    self.client.loop_start()

    await asyncio.sleep(1)  # Allow some time for connection establishment
    while not self.connected:
      await asyncio.sleep(0.1)  # Check connection status periodically
    self.connected = True

  def stop(self) -> None:
    self.logger.info('Stopping DiscoveryService...')
    for service in self.subscribed_services:
      self.publish_unavailable(service)
    self.client.loop_stop()
    self.client.disconnect()
    self.logger.info('DiscoveryService stopped.')

  def publish(self, service: Service) -> None:
    if not self.connected:
      raise RuntimeError('Client is not connected.')

    topic = f'{self.topic_prefix}/{service.name}'
    subscription = Subscription(service=service, available=True)
    payload = subscription.to_json().encode('utf-8')

    properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
    properties.UserProperty = ('client_id', self.client_id)

    self.client.publish(topic, payload=payload, qos=1, retain=False, properties=properties)
    self.logger.info(f"Published service announcement to topic '{topic}'")
    self.subscribed_services.append(service)

  def publish_unavailable(self, service: Service) -> None:
    if not self.connected:
      raise RuntimeError('Client is not connected.')

    topic = f'{self.topic_prefix}/{service.name}'
    subscription = Subscription(service=service, available=False)
    payload = subscription.to_json().encode('utf-8')

    properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
    properties.UserProperty = ('client_id', self.client_id)

    self.client.publish(topic, payload=payload, qos=1, retain=False, properties=properties)
    self.logger.info(f"Published service unavailability to topic '{topic}'")

  def watch(self, service_name: str, callback: Callable[[Subscription], None], qos: int = 0) -> None:
    if not self.connected:
      raise RuntimeError('Client is not connected.')

    topic = f'{self.topic_prefix}/{service_name}'
    self.client.subscribe(topic, qos=qos)
    self.subscriptions[service_name] = callback
    self.client.message_callback_add(topic, self._on_service_availability_message)
    self.logger.info(f"Subscribed to service availability topic '{topic}'")

  def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
    if reason_code == mqtt.CONNACK_ACCEPTED:
      self.logger.info(f'Connected to {self.client.host}:{self.client.port}')
      self.logger.info(f'Listening subscriptions {self.topic_prefix}/#')
      self.connected = True
    else:
      self.logger.error(f'Connection to {self.client.host}:{self.client.port} failed: {mqtt.connack_string(reason_code)}.')

  def _on_disconnect(self, client, userdata, flags, reason_code, properties) -> None:
    for service in self.subscribed_services:
      self.publish_unavailable(service)
    self.subscribed_services.clear()
    self.logger.info(f'Disconnected from {self.client.host}:{self.client.port} - {reason_code}')
    self.connected = False

  def _on_service_availability_message(self, client, userdata, msg: mqtt.MQTTMessage) -> None:
    subscription = Subscription.from_json(msg.payload)
    notify = self.subscriptions.get(subscription.service.name, (None, None))
    notify(subscription)
