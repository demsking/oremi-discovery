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
import threading
import uuid
from typing import Any
from typing import Callable
from typing import Coroutine
from typing import Optional

import paho.mqtt.client as mqtt
from oremi_core.event import Event
from oremi_discovery.models import Service
from oremi_discovery.models import SubscriptionMessage
from oremi_discovery.package import APP_NAME

ServiceWatchNotify = Callable[[Service], Coroutine[Any, Any, None]]


class DiscoveryService:
  def __init__(
    self,
    *,
    client_id: Optional[str] = None,
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
    self.subscriptions: dict[str, tuple[Event, ServiceWatchNotify, Optional[ServiceWatchNotify]]] = {}
    self.subscribed_services: set[Service] = set()

    self.client.on_connect = self._on_connect
    self.client.on_disconnect = self._on_disconnect
    self.client.on_message = self._on_message
    self.connected = False

    # Enable auto reconnect for MQTT client to avoid losing connection when the broker is down.
    self.client.reconnect_delay_set(min_delay=1, max_delay=120)

  def clear(self):
    self.subscriptions.clear()
    self.subscribed_services.clear()

  async def connect(self, broker_address: str, port: int = 1883) -> None:
    self.clear()
    self.logger.info(f'Connecting to broker {broker_address}:{port} with client ID {self.client_id}')
    self.client.connect_async(broker_address, port, clean_start=True)
    self.client.loop_start()

    await asyncio.sleep(1)  # Allow some time for connection establishment
    while not self.connected:
      await asyncio.sleep(0.1)  # Check connection status periodically
    self.connected = True

  def disconnect(self) -> None:
    self.clear()
    self.logger.info(f'Disconnecting discovery service {self.client_id}...')
    for service in list(self.subscribed_services):
      self.unpublish(service)
    self.client.loop_stop()
    self.client.disconnect()
    self.logger.info(f'Discovery service {self.client_id} disconnected.')

  def publish(self, service: Service) -> None:
    if not self.connected:
      raise RuntimeError(f'Client {self.client_id} is not connected.')

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
      raise RuntimeError(f'Client {self.client_id} is not connected.')

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
    on_service_unavailable: Optional[ServiceWatchNotify] = None,
  ) -> Event:
    if not self.connected:
      raise RuntimeError(f'Client {self.client_id} is not connected.')

    if service_name in self.subscriptions:
      return self.subscriptions[service_name][0]

    event = Event()
    topic = f'{self.channel}/{service_name}'

    self.client.subscribe(topic, qos=1)
    self.subscriptions[service_name] = event, on_service_available, on_service_unavailable
    self.logger.info(f'Subscribed to service availability {service_name}')

    return event

  def unwatch(self, service_name: str) -> None:
    if service_name not in self.subscriptions:
      return
    topic = f'{self.channel}/{service_name}'
    self.client.unsubscribe(topic)
    event = self.subscriptions[service_name][0]
    event.set()
    del self.subscriptions[service_name]
    self.logger.info(f'Unsubscribed from service availability {service_name}')

  def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
    if reason_code == mqtt.CONNACK_ACCEPTED:
      self.logger.info(f'Connected to {self.client.host}:{self.client.port}')
      self.connected = True

      for service in self.subscribed_services:
        self.publish(service)
    else:
      self.logger.error(f'Connection to {self.client.host}:{self.client.port} failed: {mqtt.connack_string(reason_code)}.')

  def _on_disconnect(self, client, userdata, flags, reason_code, properties) -> None:
    self.logger.info(f'Disconnected from {self.client.host}:{self.client.port} - {reason_code}')
    self.connected = False

  def _exec_async(self, notify: ServiceWatchNotify, subscription: SubscriptionMessage):
    # Create a new event loop for the separate thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(notify(subscription.service))

  def _on_message(self, client, userdata, msg: mqtt.MQTTMessage) -> None:
    subscription = SubscriptionMessage.from_json(msg.payload)
    event, on_service_available, on_service_unavailable = self.subscriptions.get(subscription.service.name, (None, None, None))

    if event and on_service_available:
      if subscription.available:
        event.set()
        threading.Thread(
          daemon=True,
          name=f'{APP_NAME}-on-service-available-{subscription.service.name}',
          target=self._exec_async,
          args=(on_service_available, subscription)
        ).start()
      elif on_service_unavailable:
        event.clear()
        threading.Thread(
          daemon=True,
          name=f'{APP_NAME}-on-service-unavailable-{subscription.service.name}',
          target=self._exec_async,
          args=(on_service_unavailable, subscription)
        ).start()
