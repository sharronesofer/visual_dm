"""Fixed test for analytics service that uses proper patching."""

import asyncio
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
import logging

from backend.systems.analytics.services.analytics_service import AnalyticsService, AnalyticsEventType
from typing import Type

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_analytics_async_event_processing(): pass
    """Test that events are processed asynchronously using proper patching."""
    # Create a temporary directory for testing
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)
    
    try: pass
        # Create service with test_mode=True
        service = AnalyticsService(storage_path=temp_path, test_mode=True)
        
        # Explicitly set the instance for singleton pattern
        AnalyticsService._instance = service
        
        # Create a mock function and assign it directly to the instance
        mock_store_event = AsyncMock()
        
        # Save the original method
        original_method = service._store_event
        
        try: pass
            # Replace the method
            service._store_event = mock_store_event
            
            # Call log_event_async directly
            await service.log_event_async(
                event_type=AnalyticsEventType.CUSTOM_EVENT,
                entity_id="test_entity",
                metadata={"test": "data"}
            )
            
            # Verify the mock was called with correct parameters
            mock_store_event.assert_called_once_with(
                AnalyticsEventType.CUSTOM_EVENT,
                "test_entity",
                {"test": "data"}
            )
        finally: pass
            # Restore the original method
            service._store_event = original_method
    finally: pass
        # Clean up
        temp_dir.cleanup()
        # Reset singleton instance
        AnalyticsService._instance = None 