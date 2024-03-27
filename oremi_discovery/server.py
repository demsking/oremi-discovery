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
import traceback

import websockets.exceptions # pylint: disable=import-error
import websockets.legacy.server as Websockets # pylint: disable=import-error
import websockets.typing # pylint: disable=import-error
from attrs import asdict
from oremi_core.wsserver import WebsocketServer

from .discovery import Discovery
from .package import SERVER_HEADER
from oremi_discovery_models import OkResult
from oremi_discovery_models import Request
from oremi_discovery_models import Response
from oremi_discovery_models import ServiceEvent
from oremi_discovery_models import ServiceNameParams

__all__ = [
  'DiscoveryServer',
]

WebSocketServerProtocol = Websockets.WebSocketServerProtocol
Data = websockets.typing.Data


class DiscoveryServer(WebsocketServer):
  def __init__(
    self,
    *,
    cert_file: str | None = None,
    key_file: str | None = None,
    password: str | None = None,
    logger: logging.Logger,
  ) -> None:
    self.verbose = logger.level != logging.INFO
    self.logger = logger
    self.discovery = Discovery[tuple[str, int]](logger)
    self.ssl_context = self._create_ssl_context(cert_file = cert_file, key_file = key_file, password = password)

  def _create_ssl_context(self, *, cert_file: str | None, key_file: str | None = None, password: str | None = None):
    ssl_context = None

    if cert_file:
      import ssl # pylint: disable=import-outside-toplevel

      ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
      self.logger.info(f'Using certificat file "{cert_file}"')

      if key_file:
        self.logger.info(f'Using key file "{key_file}"')

      ssl_context.load_cert_chain(cert_file, key_file, password)
    return ssl_context

  def _handle_connection_close(self, websocket: WebSocketServerProtocol, exception: websockets.exceptions.ConnectionClosedOK):
    if exception.reason:
      self.logger.info(f'Connection closed {websocket.remote_address} with code {exception.code}. Reason: {exception.reason}')
    else:
      self.logger.info(f'Connection closed {websocket.remote_address} with code {exception.code}')

  async def _process_request(self, websocket: WebSocketServerProtocol, message: Data) -> None:
    data = json.loads(message)
    request = Request(**data)

    if request.method == 'register':
      event = ServiceEvent(**request.params)
      await self.discovery.register_service(websocket.remote_address, event = event)
      await websocket.send(json.dumps(asdict(Response(id = request.id, result = OkResult(ok = True)))))
    else:
      params = ServiceNameParams(**request.params)

      if request.method == 'subscribe':
        await self.discovery.watch_service(
          key = websocket.remote_address,
          name = params.name,
          on_service_data = lambda event: websocket.send(json.dumps(asdict(Response(id = request.id, result = event)))),
        )
      elif request.method == 'unsubscribe':
        self.discovery.unwatch_service(websocket.remote_address, name = params.name)
        await websocket.send(json.dumps(asdict(Response(id = request.id, result = OkResult(ok = True)))))

  async def _handle_client_requests(self, websocket: WebSocketServerProtocol) -> None:
    self.logger.info(f'Connection from {websocket.remote_address} {websocket.request_headers["User-Agent"]}')

    try:
      async for message in websocket:
        await self._process_request(websocket, message)
    except (ValueError, TypeError) as exception:
      error_message = f'Invalid Message: {exception}'
      await websocket.close(code = 1003, reason = error_message)
      self.logger.error(error_message)
      if self.verbose:
        traceback.print_exc()
    except websockets.exceptions.ConnectionClosedOK as exception:
      self._handle_connection_close(websocket, exception)
    finally:
      self.discovery.dispose_service_key(websocket.remote_address)

  async def _handler_client(self, websocket: WebSocketServerProtocol) -> None:
    try:
      await self._handle_client_requests(websocket)
    except websockets.exceptions.ConnectionClosedOK as exception:
      self._handle_connection_close(websocket, exception)
    except Exception as error:
      error_message = f'Unexpected Error: {error}'
      self.logger.error(error_message)
      await websocket.close(code = 4000, reason = error_message)
      if self.verbose:
        traceback.print_exc()

  async def listen(self, host: str, port: int) -> None:
    async with Websockets.serve(self._handler_client, host, port, ssl = self.ssl_context, server_header = SERVER_HEADER, logger = self.logger):
      await asyncio.Future()
