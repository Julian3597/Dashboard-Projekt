from collections import defaultdict
from typing import Callable, Any

class EventManager:
    def __init__(self):
        self._subscribers: dict[str, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[[Any], None]) -> None:
        """Subscribe a callback to an event.

        When an event gets published, all subscribed callback methods are
        called with the data of the event as the argument.
        Args:
            event_name: string name of event to subscribe to
            callback: method that takes one argument and returns None
        """
        self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable[[Any], None]) -> None:
        """Unsubscribe a callback from an event.

        Args:
            event_name: string name of event to unsubscribe from
            callback: method that takes one argument and returns None
        """
        self._subscribers[event_name].remove(callback)

    def publish(self, event_name: str, data: Any | None = None) -> None:
        """Publish an event to all subscribers of that event.

        All callback methods subscribed to the matching event name will be called with the provided data.
        Args:
            event_name: string name of event to publish
            data: published data passed to subscribers
        """
        for callback in self._subscribers[event_name]:
            callback(data)
