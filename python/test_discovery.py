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
import time
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import paho.mqtt.client as mqtt
import pytest
from oremi_discovery import DiscoveryService
from oremi_discovery import Service


@pytest.fixture
def logger():
  return logging.getLogger()


@pytest.fixture
def discovery_service(logger):
  return DiscoveryService(logger=logger)


def test_start_and_stop(discovery_service):
  asyncio.run(discovery_service.connect('test.mosquitto.org', 1883))
  time.sleep(1)  # Let it connect
  assert discovery_service.connected == True
  discovery_service.disconnect()
  assert discovery_service.connected == False


def test_publish(discovery_service):
  with pytest.raises(RuntimeError):
      discovery_service.publish(Service(name='test', version='v1', protocol='ws', host='localhost', port=1234))
  asyncio.run(discovery_service.connect('test.mosquitto.org', 1883))
  time.sleep(1)  # Let it connect
  discovery_service.publish(Service(name='test', version='v1', protocol='ws', host='localhost', port=1234))
  # Add assertions as necessary


def test_unpublish(discovery_service):
  with pytest.raises(RuntimeError):
      discovery_service.unpublish(Service(name='test', version='v1', protocol='ws', host='localhost', port=1234))
  asyncio.run(discovery_service.connect('test.mosquitto.org', 1883))
  time.sleep(1)  # Let it connect
  discovery_service.unpublish(Service(name='test', version='v1', protocol='ws', host='localhost', port=1234))
  # Add assertions as necessary


def test_watch(discovery_service):
  with pytest.raises(RuntimeError):
    discovery_service.watch('test', lambda x: None)
  asyncio.run(discovery_service.connect('test.mosquitto.org', 1883))
  time.sleep(1)  # Let it connect
  callback_mock = MagicMock()
  discovery_service.watch('test', callback_mock)
  # Add assertions as necessary


def test_on_connect_success(discovery_service):
  discovery_service._on_connect(None, None, None, mqtt.CONNACK_ACCEPTED, None)
  assert discovery_service.connected == True


def test_on_connect_failed(discovery_service):
  discovery_service._on_connect(None, None, None, mqtt.CONNACK_REFUSED_NOT_AUTHORIZED, None)
  assert discovery_service.connected == False


def test_on_disconnect(discovery_service):
  discovery_service._on_connect(None, None, None, mqtt.CONNACK_ACCEPTED, None)
  discovery_service.publish(Service(name='test', version='v1', protocol='ws', host='localhost', port=1234))
  discovery_service.disconnect()
  discovery_service._on_disconnect(None, None, None, 0, None)
  assert len(discovery_service.subscribed_services) == 0
  assert discovery_service.connected == False


@pytest.mark.asyncio
def test_on_message(discovery_service):
  callback_mock = AsyncMock()
  discovery_service._on_connect(None, None, None, mqtt.CONNACK_ACCEPTED, None)
  discovery_service.watch('test', callback_mock)
  discovery_service._on_message(None, None, MagicMock(payload=b'{"service": {"name": "test", "version": "v1", "protocol": "ws", "host": "localhost", "port": 1234}, "available": true}'))
  time.sleep(1)
  callback_mock.assert_awaited()


def test_on_service_unavailability_message(discovery_service):
  on_available_callback_mock = AsyncMock()
  on_unavailable_callback_mock = AsyncMock()
  discovery_service._on_connect(None, None, None, mqtt.CONNACK_ACCEPTED, None)
  discovery_service.watch('test', on_available_callback_mock, on_unavailable_callback_mock)
  discovery_service._on_message(None, None, MagicMock(payload=b'{"service": {"name": "test", "version": "v1", "protocol": "ws", "host": "localhost", "port": 1234}, "available": false}'))
  time.sleep(1)
  on_available_callback_mock.assert_not_awaited()
  on_unavailable_callback_mock.assert_awaited()
