from collections import defaultdict
from typing import Callable, Any

class EventManager:
    def __init__(self):
        self._subscribers: dict[str, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[[Any], None]) -> None:
        self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable[[Any], None]) -> None:
        self._subscribers[event_name].remove(callback)

    def publish(self, event_name: str, data: Any | None = None) -> None:
        for callback in self._subscribers[event_name]:
            callback(data)
