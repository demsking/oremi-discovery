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
import uuid
from collections.abc import Callable
from collections.abc import Coroutine
from typing import Any

import paho.mqtt.client as mqtt
from oremi_discovery.models import Service
from oremi_discovery.models import SubscriptionMessage


ServiceWatchNotify = Callable[[Service], Coroutine[Any, Any, None]]

class DiscoveryService:
  def __init__(
    self,
    *,
    client_id: str | None = None,
    channel: str = 'discovery',
    logger: logging.Logger,
  ) -> None:
    self.client_id = client_id or str(uuid.uuid4())
    self.client = mqtt.Client(
      callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
      client_id=self.client_id,
      protocol=mqtt.MQTTv5,
    )

    self.channel = channel
    self.logger = logger
    self.subscriptions: dict[str, tuple[asyncio.Event, ServiceWatchNotify, ServiceWatchNotify | None]] = {}
    self.subscribed_services: set[Service] = set()

    self.client.on_connect = self._on_connect
    self.client.on_disconnect = self._on_disconnect
    self.connected = False

  async def connect(self, broker_address: str, port: int = 1883) -> None:
    self.logger.info(f'Connecting to {broker_address}:{port}')
    self.client.connect_async(broker_address, port, clean_start=True)
    self.client.loop_start()

    await asyncio.sleep(1)  # Allow some time for connection establishment
    while not self.connected:
      await asyncio.sleep(0.1)  # Check connection status periodically
    self.connected = True

  def disconnect(self) -> None:
    self.logger.info(f'Stopping discovery service {self.client_id}...')
    for service in list(self.subscribed_services):
      self.unpublish(service)
    self.client.loop_stop()
    self.client.disconnect()
    self.logger.info(f'Discovery service {self.client_id} stopped.')

  def publish(self, service: Service) -> None:
    if not self.connected:
      raise RuntimeError('Client is not connected.')

    topic = f'{self.channel}/{service.name}'
    subscription = SubscriptionMessage(service=service, available=True)
    payload = subscription.to_json().encode('utf-8')

    properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
    properties.UserProperty = ('client_id', self.client_id)

    self.client.publish(topic, payload=payload, qos=1, retain=True, properties=properties)
    self.logger.info(f'Published service availability {service.name}')
    self.subscribed_services.add(service)

  def unpublish(self, service: Service) -> None:
    if not self.connected:
      raise RuntimeError('Client is not connected.')

    topic = f'{self.channel}/{service.name}'
    subscription = SubscriptionMessage(service=service, available=False)
    payload = subscription.to_json().encode('utf-8')

    properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
    properties.UserProperty = ('client_id', self.client_id)

    self.client.publish(topic, payload=payload, qos=1, retain=False, properties=properties)
    self.logger.info(f'Published service unavailability {service.name}')

    if service in self.subscribed_services:
      self.subscribed_services.remove(service)

  def watch(
    self,
    service_name: str,
    on_service_available: ServiceWatchNotify,
    on_service_unavailable: ServiceWatchNotify | None = None,
  ) -> asyncio.Event:
    if not self.connected:
      raise RuntimeError('Client is not connected.')

    if service_name in self.subscriptions:
      return self.subscriptions[service_name][0]

    topic = f'{self.channel}/{service_name}'
    event = asyncio.Event()
    self.client.subscribe(topic, qos=1)
    self.subscriptions[service_name] = event, on_service_available, on_service_unavailable
    self.client.message_callback_add(topic, self._on_service_availability_message)
    self.logger.info(f'Subscribed to service availability {service_name}')

    return event

  def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
    if reason_code == mqtt.CONNACK_ACCEPTED:
      self.logger.info(f'Connected to {self.client.host}:{self.client.port}')
      self.connected = True

      for service in self.subscribed_services:
        self.publish(service)
    else:
      self.logger.error(f'Connection to {self.client.host}:{self.client.port} failed: {mqtt.connack_string(reason_code)}.')

  def _on_disconnect(self, client, userdata, flags, reason_code, properties) -> None:
    self.subscribed_services.clear()
    self.logger.info(f'Disconnected from {self.client.host}:{self.client.port} - {reason_code}')
    self.connected = False

  def _on_service_availability_message(self, client, userdata, msg: mqtt.MQTTMessage) -> None:
    subscription = SubscriptionMessage.from_json(msg.payload)
    event, on_service_available, on_service_unavailable = self.subscriptions.get(subscription.service.name, (None, None, None))

    if event and on_service_available:
      loop = asyncio.new_event_loop()

      if subscription.available:
        event.set()
        loop.run_until_complete(on_service_available(subscription.service))
      elif on_service_unavailable:
        event.clear()
        loop.run_until_complete(on_service_unavailable(subscription.service))
