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
from typing import Callable
from typing import Union

from attrs import asdict
from oremi_core.wsjsonrpc import WebsocketJsonRpcClient # pylint: disable=import-error

from oremi_discovery_models import OkResult
from oremi_discovery_models import Service
from oremi_discovery_models import ServiceEvent

__all__ = [
  'Service',
  'ServiceEvent',
  'DiscoveryClient',
]


OnServiceDataCallback = Callable[[ServiceEvent], None]
OkResultCallback = Callable[[OkResult], None]


class DiscoveryClient(WebsocketJsonRpcClient):
  @staticmethod
  def _wrap_ok_done(on_done: Union[OkResultCallback, None] = None):
    if on_done:
      async def _on_done_wrapper(data: dict):
        result = OkResult(**data)
        on_done(result)
      return _on_done_wrapper
    return None

  async def publish(self, event: ServiceEvent, on_done: Union[OkResultCallback, None] = None):
    """
    Publish a service event.

    Args:
      event (ServiceEvent): The service event to publish.
    """
    on_done_wrapper = DiscoveryClient._wrap_ok_done(on_done)

    self.logger.info(f'Publishing {event}')
    await self.send_request('register', asdict(event), on_response = on_done_wrapper) # type: ignore

  async def watch(self, name: str, on_service_data: OnServiceDataCallback):
    """
    Watch a specific service for data changes.

    Args:
      name (str): The name of the service to watch.
      on_service_data (OnServiceDataCallback): The callback function for service data changes.
    """
    async def on_service_data_wrapper(data: dict) -> None:
      event = ServiceEvent(**data)
      on_service_data(event)
    await self.send_request('subscribe', { 'name': name }, on_response = on_service_data_wrapper)

  async def unwatch(self, name: str, on_done: Union[OkResultCallback, None] = None):
    """
    Watch a specific service for data changes.

    Args:
      name (str): The name of the service to watch.
      on_done (OkResultCallback | None): The callback function.
    """
    on_done_wrapper = DiscoveryClient._wrap_ok_done(on_done)

    await self.send_request('unsubscribe', { 'name': name }, on_response = on_done_wrapper) # type: ignore
