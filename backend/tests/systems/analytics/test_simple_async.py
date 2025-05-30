"""Simple async test for isolating the issue with mocking."""

import asyncio
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch
import logging

from backend.systems.analytics.services.analytics_service import AnalyticsService, AnalyticsEventType
from typing import Type

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_simple_async_mock(): pass
    """Simple test to verify that AsyncMock works as expected."""
    # Create a temporary directory for testing
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)

    try: pass
        logger.debug("Creating test service")
        # Create service with test_mode=True
        service = AnalyticsService(storage_path=temp_path, test_mode=True)
        
        # Make sure it's a fresh instance
        AnalyticsService._instance = service
        
        # Replace _store_event with AsyncMock
        store_event_mock = AsyncMock()
        service._store_event = store_event_mock
        
        logger.debug(f"Service created, _store_event type: {type(service._store_event)}")
        logger.debug(f"Is callable: {callable(service._store_event)}")
        logger.debug(f"Has _mock_name: {hasattr(service._store_event, '_mock_name')}")
        
        # Directly check the _store_event method to make sure it's actually set
        assert hasattr(service, "_store_event"), "Service should have _store_event attribute"
        assert service._store_event is store_event_mock, "Mock should be properly assigned"
        
        # Call log_event_async directly - use a canonical event type
        logger.debug("Calling log_event_async")
        await service.log_event_async(
            event_type=AnalyticsEventType.CUSTOM_EVENT,  # Using a canonical event type
            entity_id="test123",
            metadata={"key": "value"}
        )
        
        logger.debug(f"After log_event_async, mock was called: {service._store_event.call_count} times")
        
        # Verify the mock was called with the right parameters
        service._store_event.assert_called_once_with(
            AnalyticsEventType.CUSTOM_EVENT, 
            "test123", 
            {"key": "value"}
        )
        
    finally: pass
        # Clean up
        temp_dir.cleanup()
        # Reset singleton instance
        AnalyticsService._instance = None 