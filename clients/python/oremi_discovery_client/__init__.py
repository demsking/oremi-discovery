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

from typing import Literal
from collections.abc import Callable

from attrs import asdict, define
from oremi.core.wsjsonrpc import WebsocketJsonRpcClient

__all__ = [
  'Service',
  'ServiceEvent',
  'DiscoveryClient',
]


@define(auto_attribs = True)
class Service:
  """
  Represents a service with its details.

  Args:
    name (str): The name of the service.
    protocol (str): The protocol used by the service.
    host (str): The host address of the service.
    port (int): The port number the service is running on.
    uri (str): The URI of the service. This.
    data (dict | None, optional): Additional data associated with the service. Defaults to None.
  """
  name: str
  protocol: str
  host: str
  port: int
  data: dict | None = None

  @property
  def uri(self): # pylint: disable=no-self-argument
    return f'{self.protocol}://{self.host}:{self.port}'

  def __hash__(self):
    return hash((self.name, self.protocol, self.host, self.port))

  def __str__(self) -> str:
    return f'Service(name: {self.name}, uri: {self.uri}, data: {self.data})'


@define(auto_attribs = True)
class ServiceEvent:
  """
  Represents an event related to a service.

  Args:
    status (Literal['ONLINE', 'OFFLINE']): The status of the service.
    service (Service): The service associated with the event.
  """
  status: Literal['ONLINE', 'OFFLINE']
  service: Service

  def __str__(self) -> str:
    return f'Event(status: {self.status}, service: {self.service})'


@define(auto_attribs = True)
class OkResult:
  ok: bool


OnServiceDataCallback = Callable[[ServiceEvent], None]
OkResultCallback = Callable[[OkResult], None]


class DiscoveryClient(WebsocketJsonRpcClient):
  @staticmethod
  def _wrap_ok_done(on_done: OkResultCallback | None = None):
    if on_done:
      async def _on_done_wrapper(data: dict):
        result = OkResult(**data)
        on_done(result)
      return _on_done_wrapper
    return None

  async def register(self, service: Service, on_done: OkResultCallback | None = None):
    """
    Register a service and publish an 'ONLINE' event.

    Args:
      service (Service): The service to be registered.
    """
    event = ServiceEvent(status = 'ONLINE', service = service)
    on_done_wrapper = DiscoveryClient._wrap_ok_done(on_done)

    self.logger.info(f'Registering {service}')
    await self.send_request('register', asdict(event), on_response = on_done_wrapper) # type: ignore

  async def watch(self, name: str, on_service_data: OnServiceDataCallback):
    """
    Watch a specific service for data changes.

    Args:
      name (str): The name of the service to watch.
      on_service_data (OnServiceDataCallback): The callback function for service data changes.
    """
    async def on_service_data_wrapper(data: dict):
      event = ServiceEvent(**data)
      on_service_data(event)
    await self.send_request('subscribe', { 'name': name }, on_response = on_service_data_wrapper)

  async def unwatch(self, name: str, on_done: OkResultCallback | None = None):
    """
    Watch a specific service for data changes.

    Args:
      name (str): The name of the service to watch.
      on_done (OkResultCallback | None): The callback function.
    """
    on_done_wrapper = DiscoveryClient._wrap_ok_done(on_done)

    await self.send_request('unsubscribe', { 'name': name }, on_response = on_done_wrapper) # type: ignore
