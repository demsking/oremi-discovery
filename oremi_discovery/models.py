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

from attrs import define, field


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
    return f'Service(name = {self.name}, uri = {self.uri})'


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
    return f'{self.service}, status = {self.status})'


@define(auto_attribs = True)
class ServiceNameParams:
  name: str


@define(auto_attribs = True)
class Request:
  id: int
  method: Literal['register', 'subscribe', 'unsubscribe']
  params: ServiceEvent | ServiceNameParams
  jsonrpc: Literal['2.0'] = field(default = '2.0')


@define(auto_attribs = True)
class OkResult:
  ok: bool


@define(auto_attribs = True)
class Response:
  id: int
  result: ServiceEvent | OkResult
  jsonrpc: Literal['2.0'] = field(default = '2.0')
