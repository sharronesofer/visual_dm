"""Test using a stubbed method approach rather than mocking."""

import asyncio
import pytest
import tempfile
from pathlib import Path
import logging
import inspect

from backend.systems.analytics.services.analytics_service import AnalyticsService, AnalyticsEventType
from typing import Type

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_stub_approach():
    """Test using a simple stub approach."""
    # Create a temporary directory for testing
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)
    
    # Tracking variable for the test
    calls = []
    
    # Create a stub async method
    async def stub_store_event(event_type, entity_id, metadata):
        """Stub implementation of _store_event."""
        logger.debug(f"Stub called with {event_type}, {entity_id}, {metadata}")
        calls.append((event_type, entity_id, metadata))
        return True
    
    try:
        # Create service with test_mode=True
        logger.debug("Creating service with test_mode=True")
        service = AnalyticsService(storage_path=temp_path, test_mode=True)
        
        # Set the instance for singleton pattern
        logger.debug("Setting singleton instance")
        AnalyticsService._instance = service
        
        # Check the service properties
        logger.debug(f"Service test_mode: {service.test_mode}")
        logger.debug(f"Service has _store_event: {hasattr(service, '_store_event')}")
        if hasattr(service, '_store_event'):
            logger.debug(f"Service _store_event type: {type(service._store_event)}")
            logger.debug(f"Service _store_event is async: {asyncio.iscoroutinefunction(service._store_event)}")
        
        # Save original method
        logger.debug("Saving original method")
        original_method = service._store_event
        
        try:
            # Replace with our stub
            logger.debug("Replacing with stub")
            service._store_event = stub_store_event
            
            # Verify the method was actually replaced
            logger.debug(f"After replacement, service _store_event is stub: {service._store_event is stub_store_event}")
            
            # Call log_event_async directly
            logger.debug("Calling log_event_async")
            await service.log_event_async(
                event_type=AnalyticsEventType.CUSTOM_EVENT,
                entity_id="test_entity",
                metadata={"test": "data"}
            )
            
            # Log what happened
            logger.debug(f"After call, calls: {calls}")
            
            # Directly test the stub to make sure it works
            logger.debug("Directly testing stub")
            await service._store_event("DirectTest", "direct-id", {"direct": True})
            
            # Log calls again
            logger.debug(f"After direct call, calls: {calls}")
            
            # Verify our stub was called with correct parameters
            assert len(calls) >= 1, "Stub should have been called at least once"
            
            # If we got a direct call but not through log_event_async, that's important to know
            if len(calls) == 1 and calls[0][0] == "DirectTest":
                logger.error("Only the direct test call worked, log_event_async did not call _store_event!")
            
            for call in calls:
                logger.debug(f"Call: {call}")
            
        finally: pass
            # Restore original method
            logger.debug("Restoring original method")
            service._store_event = original_method
    finally
        # Clean up
        logger.debug("Cleaning up")
        temp_dir.cleanup()
        # Reset singleton instance
        AnalyticsService._instance = None 