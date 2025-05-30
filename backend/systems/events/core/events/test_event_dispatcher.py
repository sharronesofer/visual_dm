"""
Tests for the canonical EventDispatcher (event bus) and event-driven integration in Visual DM.
Covers core event bus features and verifies that major services emit events as expected.
"""
import asyncio
import pytest
from unittest.mock import Mock
from pydantic import BaseModel
from backend.app.core.events.event_dispatcher import EventDispatcher, EventBase
from backend.app.core.memory.memory_system import MemoryManager, MemoryCategory
from backend.app.core.rumors.rumor_system import RumorSystem
from backend.app.core.world_state.world_state_manager import WorldStateManager
from backend.app.core.time_system.time_manager import TimeManager

@pytest.mark.asyncio
async def test_basic_subscribe_publish():
    dispatcher = EventDispatcher.get_instance()
    results = []
    class TestEvent(EventBase):
        data: str
    def handler(event):
        results.append(event.data)
    dispatcher.subscribe(TestEvent, handler)
    await dispatcher.publish(TestEvent(event_type="test", data="payload"))
    assert "payload" in results
    dispatcher.unsubscribe(TestEvent, handler)

@pytest.mark.asyncio
async def test_middleware_invocation():
    dispatcher = EventDispatcher.get_instance()
    called = []
    async def middleware(event, next_middleware):
        called.append("middleware")
        return await next_middleware(event)
    dispatcher.add_middleware(middleware)
    class TestEvent(EventBase):
        pass
    def handler(event):
        called.append("handler")
    dispatcher.subscribe(TestEvent, handler)
    await dispatcher.publish(TestEvent(event_type="test"))
    assert called == ["middleware", "handler"]
    dispatcher.unsubscribe(TestEvent, handler)
    dispatcher._middlewares.clear()

@pytest.mark.asyncio
async def test_event_priority():
    dispatcher = EventDispatcher.get_instance()
    order = []
    class TestEvent(EventBase):
        pass
    def high(event): order.append("high")
    def low(event): order.append("low")
    dispatcher.subscribe(TestEvent, low, priority=0)
    dispatcher.subscribe(TestEvent, high, priority=10)
    await dispatcher.publish(TestEvent(event_type="test"))
    assert order == ["high", "low"]
    dispatcher.unsubscribe(TestEvent, high)
    dispatcher.unsubscribe(TestEvent, low)

@pytest.mark.asyncio
async def test_async_and_sync_handlers():
    dispatcher = EventDispatcher.get_instance()
    called = []
    class TestEvent(EventBase):
        pass
    async def async_handler(event):
        called.append("async")
    def sync_handler(event):
        called.append("sync")
    dispatcher.subscribe(TestEvent, async_handler)
    dispatcher.subscribe(TestEvent, sync_handler)
    await dispatcher.publish(TestEvent(event_type="test"))
    assert set(called) == {"async", "sync"}
    dispatcher.unsubscribe(TestEvent, async_handler)
    dispatcher.unsubscribe(TestEvent, sync_handler)

@pytest.mark.asyncio
async def test_memory_manager_emits_event():
    dispatcher = EventDispatcher.get_instance()
    received = []
    from backend.app.core.memory.memory_system import MemoryEvent
    def handler(event):
        received.append(event.operation)
    dispatcher.subscribe(MemoryEvent, handler)
    mm = MemoryManager(storage_path=":memory:")
    await mm.create_memory(entity_id="npc1", summary="Test", categories=[MemoryCategory.OTHER])
    assert "created" in received
    dispatcher.unsubscribe(MemoryEvent, handler)

@pytest.mark.asyncio
async def test_rumor_system_emits_event():
    dispatcher = EventDispatcher.get_instance()
    received = []
    from backend.app.core.rumors.rumor_system import RumorEvent
    def handler(event):
        received.append(event.operation)
    dispatcher.subscribe(RumorEvent, handler)
    rs = RumorSystem(storage_path=":memory:")
    await rs.create_rumor(originator_id="npc1", content="Rumor!")
    assert "created" in received
    dispatcher.unsubscribe(RumorEvent, handler)

@pytest.mark.asyncio
async def test_world_state_manager_emits_event():
    dispatcher = EventDispatcher.get_instance()
    received = []
    from backend.app.core.world_state.world_state_manager import WorldStateEvent
    def handler(event):
        received.append(event.change_type)
    dispatcher.subscribe(WorldStateEvent, handler)
    wsm = WorldStateManager(storage_path=":memory:")
    await wsm.set("foo", 42)
    assert "created" in [str(x).lower() for x in received]
    dispatcher.unsubscribe(WorldStateEvent, handler)

@pytest.mark.asyncio
async def test_time_manager_emits_event():
    dispatcher = EventDispatcher.get_instance()
    received = []
    from backend.app.core.time_system.time_manager import TimeEvent
    def handler(event):
        received.append(event.event_type_detail)
    dispatcher.subscribe(TimeEvent, handler)
    tm = TimeManager(storage_path=":memory:")
    await tm._advance_time(minutes=1)
    assert any(x in ["minute", "tick", "hour", "day"] for x in received)
    dispatcher.unsubscribe(TimeEvent, handler) 