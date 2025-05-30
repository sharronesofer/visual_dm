"""Basic test of AsyncMock functionality."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SimpleAsyncClass: pass
    """Simple class with async methods to test mocking."""
    
    def __init__(self): pass
        self.value = 0
        
    async def async_method(self, arg1, arg2): pass
        """Sample async method."""
        self.value += 1
        return arg1 + arg2
        
    def sync_method(self, arg1, arg2): pass
        """Sample sync method."""
        self.value += 1
        return arg1 + arg2

@pytest.mark.asyncio
async def test_basic_async_mock(): pass
    """Test that AsyncMock works correctly at the most basic level."""
    # Create instance
    obj = SimpleAsyncClass()
    
    # Replace async_method with a mock
    original_method = obj.async_method
    obj.async_method = AsyncMock(return_value=42)
    
    # Call the method
    result = await obj.async_method(10, 20)
    
    # Verify the mock was called
    obj.async_method.assert_called_once_with(10, 20)
    assert result == 42
    
    # Restore original method
    obj.async_method = original_method

@pytest.mark.asyncio
async def test_patch_async_method(): pass
    """Test patching an async method."""
    with patch.object(SimpleAsyncClass, 'async_method', new_callable=AsyncMock, return_value=42) as mock_method: pass
        # Create instance
        obj = SimpleAsyncClass()
        
        # Call the method
        result = await obj.async_method(10, 20)
        
        # Verify the mock was called
        mock_method.assert_called_once_with(10, 20)
        assert result == 42 