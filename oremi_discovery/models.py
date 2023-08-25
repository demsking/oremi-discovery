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

from pydantic import BaseModel, validator


class Service(BaseModel):
  """
  Represents a service with its details.

  Args:
    name (str): The name of the service.
    protocol (str): The protocol used by the service.
    host (str): The host address of the service.
    port (int): The port number the service is running on.
    uri (str, optional): The URI of the service. This.
    data (dict | None, optional): Additional data associated with the service. Defaults to None.
  """
  name: str
  protocol: str
  host: str
  port: int
  uri: str = None # type: ignore
  data: dict | None = None

  @validator('uri', pre = True, always = True)
  def compute_uri(cls, _v, values, **kwargs): # pylint: disable=no-self-argument
    """
    Compute the URI of the service based on protocol, host, and port.

    Args:
      _v: The current value of the field.
      values (dict): The values of the other fields in the model.
      **kwargs: Additional keyword arguments.

    Returns:
        str: The computed URI.
    """
    return f'{values["protocol"]}://{values["host"]}:{values["port"]}'

  def __hash__(self):
    return hash((self.name, self.protocol, self.host, self.port))

  def __str__(self) -> str:
    return f'Service(name = {self.name}, uri = {self.uri})'


class ServiceEvent(BaseModel):
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


class _RPC(BaseModel):
  jsonrpc: Literal['2.0'] = '2.0'
  id: int


class ServiceNameParams(BaseModel):
  name: str


class Request(_RPC, BaseModel):
  method: Literal['register', 'subscribe', 'unsubscribe']
  params: ServiceEvent | ServiceNameParams


class OkResult(BaseModel):
  ok: bool

class Response(_RPC, BaseModel):
  result: ServiceEvent | OkResult
