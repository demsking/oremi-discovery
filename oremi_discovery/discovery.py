import logging
from collections.abc import Callable, Coroutine
from typing import Generic, TypeVar

from oremi.core.event import EventManager

from .models import ServiceEvent

EventData = ServiceEvent
ServiceKey = TypeVar('ServiceKey')
OnServiceDataCallback = Callable[[EventData], Coroutine[None, None, None]]


class Discovery(Generic[ServiceKey]):
  """
  A class for service discovery.
  """

  def __init__(self, logger: logging.Logger) -> None:
    self.logger = logger
    self._exposed_services: dict[str, ServiceEvent] = {}
    self._watched_services: dict[tuple[ServiceKey, str], OnServiceDataCallback] = {}
    self._event_manager = EventManager[str | ServiceKey, EventData]()

  async def _del_subscribed_service(self, event: EventData):
    del self._exposed_services[event.service.name]

  async def register_service(self, key: ServiceKey, *, event: ServiceEvent) -> None:
    """
    Register a service and publish an 'ONLINE' event.

    Args:
      key (ServiceKey): The watcher unique key.
      service (Service): The service to be registered.
    """
    self.logger.info(f'Registering {event} from {key}')
    await self._event_manager.trigger(event.service.name, event)
    self._exposed_services[event.service.name] = event

  async def watch_service(self, key: ServiceKey, *, name: str, on_service_data: OnServiceDataCallback) -> None:
    """
    Watch a specific service for data changes.

    Args:
      key (ServiceKey): The watcher unique key.
      name (str): The name of the service to watch.
      on_service_data (OnServiceDataCallback): The callback function for service data changes.
    """
    self.logger.info(f'Watching service {name} from {key}')

    watcher_key: tuple[ServiceKey, str] = (key, name)

    if watcher_key in self._watched_services:
      self.unwatch_service(key, name = name)

    self._watched_services[watcher_key] = on_service_data
    self._event_manager.subscribe(name, on_service_data)

    if name in self._exposed_services:
      await on_service_data(self._exposed_services[name])

  def unwatch_service(self, key: ServiceKey, *, name: str) -> None:
    """
    Unwatch a specific service.

    Args:
      key (ServiceKey): The watcher unique key.
      name (str): The name of the service to unwatch.
    """
    watcher_key: tuple[ServiceKey, str] = (key, name)

    if watcher_key in self._watched_services:
      existing_on_service_data = self._watched_services[watcher_key]

      self.logger.info(f'Unwatching service {name} from {key}')
      self._event_manager.unsubscribe(name, existing_on_service_data)

      del self._watched_services[watcher_key]

  def dispose_service_key(self, key: ServiceKey) -> None:
    """
    Unwatch a specific service using its key.

    Args:
      key (ServiceKey): The watcher unique key.
    """
    service_names_to_unwatch: list[str] = []

    for watcher_key in self._watched_services:
      if key in watcher_key:
        _, service_name = watcher_key
        service_names_to_unwatch.append(service_name)

    for service_name in service_names_to_unwatch:
      self.unwatch_service(key, name = service_name) # type: ignore

  def terminate(self) -> None:
    """
    Terminate the Discovery instance and cleaning up subscriptions.
    """
    for service_name in self._exposed_services:
      self._event_manager.clear(service_name)
    self._watched_services.clear()
    self._exposed_services.clear()
