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
import concurrent.futures
import logging
import os
import traceback

import pydantic
import websockets.exceptions
import websockets.legacy.server
import websockets.typing

from .discovery import Discovery
from .models import OkResult, Request, Response, ServiceEvent, ServiceNameParams
from .vars import APP_DISPLAY_NAME, APP_NAME, __version__

__all__ = [
  'listen',
]

WebSocketServerProtocol = websockets.legacy.server.WebSocketServerProtocol
Data = websockets.typing.Data


async def listen(
  *,
  host: str,
  port: int,
  cert_file: str | None = None,
  key_file: str | None = None,
  password: str | None = None,
  logger: logging.Logger,
) -> None:
  pool = concurrent.futures.ThreadPoolExecutor(os.cpu_count() or 1)
  server_header: str = f'{APP_NAME}/{__version__}'
  loop = asyncio.get_running_loop()
  discovery = Discovery[tuple[str, int]](logger)
  ssl_context = None
  verbose = logger.level != logging.INFO

  async def process_request(websocket: WebSocketServerProtocol, message: Data) -> None:
    request = Request.model_validate_json(message)

    if request.method == 'register':
      if isinstance(request.params, ServiceEvent):
        await discovery.register_service(websocket.remote_address, event = request.params)
        await websocket.send(Response(id = request.id, result = OkResult(ok = True)).model_dump_json())
    elif isinstance(request.params, ServiceNameParams):
      if request.method == 'subscribe':
        await discovery.watch_service(
          key = websocket.remote_address,
          name = request.params.name,
          on_service_data = lambda event: websocket.send(Response(id = request.id, result = event).model_dump_json()),
        )
      elif request.method == 'unsubscribe':
        discovery.unwatch_service(websocket.remote_address, name = request.params.name)
        await websocket.send(Response(id = request.id, result = OkResult(ok = True)).model_dump_json())

  def handle_connection_close(websocket: WebSocketServerProtocol, exception: websockets.exceptions.ConnectionClosedOK):
    if exception.reason:
      logger.info(f'Connection closed {websocket.remote_address} with code {exception.code}. Reason: {exception.reason}')
    else:
      logger.info(f'Connection closed {websocket.remote_address} with code {exception.code}')

  def create_process_message_function(websocket: WebSocketServerProtocol, message: Data):
    def process_message() -> None:
      loop.create_task(process_request(websocket, message), name = 'Process Message Task')
    return process_message

  async def handle_client_requests(websocket: WebSocketServerProtocol) -> None:
    try:
      logger.info(f'Connection from {websocket.remote_address} {websocket.request_headers["User-Agent"]}')

      async for message in websocket:
        await loop.run_in_executor(pool, create_process_message_function(websocket, message))
    except (ValueError, pydantic.ValidationError):
      error_message = 'Invalid Message'
      logger.error(error_message)
      await websocket.close(code = 1003, reason = error_message)
    except websockets.exceptions.ConnectionClosedOK as exception:
      handle_connection_close(websocket, exception)
    finally:
      discovery.dispose_service_key(websocket.remote_address)

  async def handler_client(websocket: WebSocketServerProtocol) -> None:
    try:
      await handle_client_requests(websocket)
    except Exception as error:
      error_message = f'Unexpected Error: {error}'
      logger.error(error_message)
      await websocket.close(code = 4000, reason = error_message)
      if verbose:
        traceback.print_exc()

  logger.info(f'{APP_DISPLAY_NAME} {__version__}')
  logger.info(f'Log level {"INFO" if logger.level == logging.INFO else "DEBUG"}')

  if cert_file:
    import ssl

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    ssl_context.load_cert_chain(cert_file, key_file, password)
    logger.info(f'Using certificat file "{cert_file}"')
    logger.info(f'Using key file "{key_file}"')

  async with websockets.legacy.server.serve(handler_client, host, port, ssl = ssl_context, server_header = server_header, logger = logger):
    await asyncio.Future()  # run forever

  discovery.terminate()
