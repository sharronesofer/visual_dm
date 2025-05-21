"""
Central Event Bus for Cross-System Communication
- Supports event registration, dispatch, and listener management
- Async/await compatible for FastAPI
- Designed for extensibility and monitoring hooks
"""
from typing import Callable, Dict, List, Any, Coroutine, Union
import asyncio

EventHandler = Union[Callable[..., Any], Callable[..., Coroutine[Any, Any, Any]]]

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[EventHandler]] = {}
        self._lock = asyncio.Lock()

    async def register(self, event_type: str, handler: EventHandler):
        async with self._lock:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            self._listeners[event_type].append(handler)

    async def unregister(self, event_type: str, handler: EventHandler):
        async with self._lock:
            if event_type in self._listeners:
                self._listeners[event_type] = [h for h in self._listeners[event_type] if h != handler]
                if not self._listeners[event_type]:
                    del self._listeners[event_type]

    async def dispatch(self, event_type: str, *args, **kwargs):
        listeners = self._listeners.get(event_type, [])
        for handler in listeners:
            if asyncio.iscoroutinefunction(handler):
                await handler(*args, **kwargs)
            else:
                handler(*args, **kwargs)

    def get_listeners(self, event_type: str) -> List[EventHandler]:
        return self._listeners.get(event_type, [])

# Singleton instance for global use
integration_event_bus = EventBus() 
