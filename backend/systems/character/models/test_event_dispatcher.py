import pytest
import asyncio
from typing import List
from pydantic import BaseModel
from backend.app.core.events.event_dispatcher import (
    EventDispatcher, EventBase, logging_middleware, error_handling_middleware
)

class TestEvent(EventBase):
    event_type: str = "test.event"
    payload: str = ""

class ParentEvent(EventBase):
    event_type: str = "parent.event"
    data: int = 0

class ChildEvent(ParentEvent):
    event_type: str = "child.event"
    extra: str = ""

@pytest.mark.asyncio
async def test_singleton_behavior():
    d1 = EventDispatcher.get_instance()
    d2 = EventDispatcher.get_instance()
    assert d1 is d2

@pytest.mark.asyncio
async def test_subscribe_and_publish():
    dispatcher = EventDispatcher.get_instance()
    results = []
    def handler(event):
        results.append(event.payload)
    dispatcher.subscribe(TestEvent, handler)
    event = TestEvent(payload="foo")
    await dispatcher.publish(event)
    assert "foo" in results
    dispatcher.unsubscribe(TestEvent, handler)

@pytest.mark.asyncio
async def test_unsubscribe():
    dispatcher = EventDispatcher.get_instance()
    called = []
    def handler(event):
        called.append(True)
    dispatcher.subscribe(TestEvent, handler)
    dispatcher.unsubscribe(TestEvent, handler)
    event = TestEvent(payload="bar")
    await dispatcher.publish(event)
    assert not called

@pytest.mark.asyncio
async def test_handler_priority():
    dispatcher = EventDispatcher.get_instance()
    order = []
    def h1(event):
        order.append("h1")
    def h2(event):
        order.append("h2")
    dispatcher.subscribe(TestEvent, h1, priority=1)
    dispatcher.subscribe(TestEvent, h2, priority=10)
    event = TestEvent(payload="baz")
    await dispatcher.publish(event)
    assert order == ["h2", "h1"]
    dispatcher.unsubscribe(TestEvent, h1)
    dispatcher.unsubscribe(TestEvent, h2)

@pytest.mark.asyncio
async def test_parent_class_subscription():
    dispatcher = EventDispatcher.get_instance()
    called = []
    def parent_handler(event):
        called.append("parent")
    dispatcher.subscribe(ParentEvent, parent_handler)
    event = ChildEvent(data=42, extra="x")
    await dispatcher.publish(event)
    assert "parent" in called
    dispatcher.unsubscribe(ParentEvent, parent_handler)

@pytest.mark.asyncio
async def test_async_and_sync_handlers():
    dispatcher = EventDispatcher.get_instance()
    called = []
    async def async_handler(event):
        called.append("async")
    def sync_handler(event):
        called.append("sync")
    dispatcher.subscribe(TestEvent, async_handler)
    dispatcher.subscribe(TestEvent, sync_handler)
    event = TestEvent(payload="asyncsync")
    await dispatcher.publish(event)
    assert set(called) == {"async", "sync"}
    dispatcher.unsubscribe(TestEvent, async_handler)
    dispatcher.unsubscribe(TestEvent, sync_handler)

@pytest.mark.asyncio
async def test_middleware_chain(monkeypatch):
    dispatcher = EventDispatcher.get_instance()
    called = []
    async def mw1(event, next_):
        called.append("mw1")
        return await next_(event)
    async def mw2(event, next_):
        called.append("mw2")
        return await next_(event)
    dispatcher._middlewares.clear()
    dispatcher.add_middleware(mw1)
    dispatcher.add_middleware(mw2)
    def handler(event):
        called.append("handler")
    dispatcher.subscribe(TestEvent, handler)
    event = TestEvent(payload="middleware")
    await dispatcher.publish(event)
    assert called == ["mw1", "mw2", "handler"]
    dispatcher.unsubscribe(TestEvent, handler)
    dispatcher._middlewares.clear()

@pytest.mark.asyncio
async def test_logging_and_error_handling_middleware(caplog):
    dispatcher = EventDispatcher.get_instance()
    dispatcher._middlewares.clear()
    dispatcher.add_middleware(logging_middleware)
    dispatcher.add_middleware(error_handling_middleware)
    def handler(event):
        raise ValueError("fail")
    dispatcher.subscribe(TestEvent, handler)
    event = TestEvent(payload="fail")
    await dispatcher.publish(event)
    dispatcher.unsubscribe(TestEvent, handler)
    dispatcher._middlewares.clear()
    assert any("Error in event handler" in r or "Error processing event" in r for r in caplog.text.splitlines())

@pytest.mark.asyncio
async def test_publish_sync():
    import sys
    import asyncio
    # Skip this test if running inside an event loop (pytest-asyncio context)
    if sys.platform != "win32" and asyncio.get_event_loop().is_running():
        pytest.skip("publish_sync cannot be tested inside a running event loop")
    dispatcher = EventDispatcher.get_instance()
    called = []
    def handler(event):
        called.append(event.payload)
    dispatcher.subscribe(TestEvent, handler)
    event = TestEvent(payload="sync")
    dispatcher.publish_sync(event)
    assert "sync" in called
    dispatcher.unsubscribe(TestEvent, handler)

@pytest.mark.asyncio
async def test_unsubscribe_nonexistent():
    dispatcher = EventDispatcher.get_instance()
    def handler(event):
        pass
    # Should not raise
    assert dispatcher.unsubscribe(TestEvent, handler) is False

@pytest.mark.asyncio
async def test_handler_exception_is_logged(caplog):
    dispatcher = EventDispatcher.get_instance()
    def bad_handler(event):
        raise RuntimeError("bad handler")
    dispatcher.subscribe(TestEvent, bad_handler)
    event = TestEvent(payload="err")
    await dispatcher.publish(event)
    dispatcher.unsubscribe(TestEvent, bad_handler)
    assert any("Error in event handler" in r for r in caplog.text.splitlines()) 
