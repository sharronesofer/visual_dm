"""
State Synchronization System
- Notifies systems of state changes
- Handles conflict resolution and rollback
- Async/await compatible
"""
from typing import Any, Dict, Callable, Coroutine, Optional
import asyncio

class StateSyncManager:
    def __init__(self):
        self._subscribers: Dict[str, Callable[[str, Any], Coroutine[Any, Any, None]]] = {}
        self._lock = asyncio.Lock()
        self._snapshots: Dict[str, Any] = {}

    async def subscribe(self, system_name: str, callback: Callable[[str, Any], Coroutine[Any, Any, None]]):
        async with self._lock:
            self._subscribers[system_name] = callback

    async def unsubscribe(self, system_name: str):
        async with self._lock:
            if system_name in self._subscribers:
                del self._subscribers[system_name]

    async def notify_state_change(self, system_name: str, state: Any):
        async with self._lock:
            self._snapshots[system_name] = state
            for name, callback in self._subscribers.items():
                if name != system_name:
                    await callback(system_name, state)

    async def get_snapshot(self, system_name: str) -> Optional[Any]:
        return self._snapshots.get(system_name)

    async def rollback(self, system_name: str, to_state: Any):
        async with self._lock:
            self._snapshots[system_name] = to_state
            # Notify all subscribers of rollback
            for name, callback in self._subscribers.items():
                if name != system_name:
                    await callback(system_name, to_state)

state_sync_manager = StateSyncManager() 
