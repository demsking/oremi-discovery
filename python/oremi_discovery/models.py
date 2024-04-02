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
import json


class Service:
  def __init__(
    self,
    *,
    name: str,
    protocol: str,
    host: str,
    port: int,
    version: str | None = None,
    data: dict | None = None,
  ) -> None:
    self.name = name
    self.protocol = protocol
    self.host = host
    self.port = port
    self.version = version
    self.data = data or {}

  @property
  def uri(self) -> str:
    return f'{self.protocol}://{self.host}:{self.port}'

  def __str__(self) -> str:
    return f'{self.name}@{self.uri}'

  def __hash__(self) -> int:
    return hash((self.name, self.host, self.port))

  @classmethod
  def from_dict(cls, data: dict):
    return cls(**data)

  @classmethod
  def from_json(cls, json_str: str | bytes | bytearray):
    json_data = json.loads(json_str)
    return cls(**json_data)

  def to_json(self) -> str:
    return json.dumps(self.__dict__)

  def to_dict(self) -> dict:
    return self.__dict__


class SubscriptionMessage:
  def __init__(self, service: Service, available: bool = False) -> None:
    self.service = service
    self.available = available

  @classmethod
  def from_json(cls, json_str: str | bytes | bytearray):
    json_data = json.loads(json_str)
    service = Service.from_dict(json_data['service'])
    return cls(service=service, available=json_data['available'])

  def to_json(self) -> str:
    return json.dumps({
      'service': self.service.to_dict(),
      'available': self.available,
    })
