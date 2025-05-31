import pytest
import asyncio
from pydantic import BaseModel
from backend.infrastructure.integration.event_bus import integration_event_bus
from backend.infrastructure.integration.state_sync import state_sync_manager
from backend.infrastructure.integration.validation import validation_manager
from backend.infrastructure.integration.monitoring import integration_logger, integration_metrics, integration_alerting
import logging

@pytest.mark.asyncio
async def test_event_bus_register_and_dispatch():
    results = []
    async def handler(data):
        results.append(data)
    await integration_event_bus.register('test_event', handler)
    await integration_event_bus.dispatch('test_event', 'payload')
    assert 'payload' in results
    await integration_event_bus.unregister('test_event', handler)

@pytest.mark.asyncio
async def test_state_sync_notify_and_rollback():
    received = []
    async def callback(system, state):
        received.append((system, state))
    await state_sync_manager.subscribe('test_system', callback)
    await state_sync_manager.notify_state_change('other_system', {'foo': 1})
    assert received[-1] == ('other_system', {'foo': 1})
    await state_sync_manager.rollback('other_system', {'foo': 2})
    assert received[-1] == ('other_system', {'foo': 2})
    await state_sync_manager.unsubscribe('test_system')

class DummySchema(BaseModel):
    x: int

def test_validation_manager():
    validation_manager.register_schema('dummy', DummySchema)
    assert validation_manager.validate('dummy', {'x': 1})
    assert not validation_manager.validate('dummy', {'y': 2})

@pytest.mark.asyncio
async def test_monitoring_logger_and_metrics():
    await integration_logger.log(logging.INFO, 'test log', foo='bar')
    await integration_metrics.record('test_metric', 42)
    value = await integration_metrics.get('test_metric')
    assert value == 42
    await integration_alerting.alert('test_alert', 'alert message')
    alert = await integration_alerting.get_alert('test_alert')
    assert alert == 'alert message' 
