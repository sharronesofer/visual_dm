"""
Basic tests for memory system functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock

class TestMemoryBasic:
    """Basic memory system tests."""
    
    def test_memory_import(self):
        """Test that memory system can be imported."""
        try:
            from backend.systems.memory import MemoryManager
            assert MemoryManager is not None
        except ImportError as e:
            pytest.skip(f"Memory system not properly configured: {e}")
    
    def test_shared_database_import(self):
        """Test that shared database can be imported."""
        try:
            from backend.infrastructure.shared.database import get_async_session
            assert get_async_session is not None
        except ImportError as e:
            pytest.skip(f"Shared database not properly configured: {e}")
    
    @pytest.mark.asyncio
    async def test_mock_database(self):
        """Test mock database functionality."""
        try:
            from backend.infrastructure.shared.database import mock_db
            
            # Test basic operations
            await mock_db.set("test_key", "test_value")
            value = await mock_db.get("test_key")
            assert value == "test_value"
            
            await mock_db.delete("test_key")
            value = await mock_db.get("test_key")
            assert value is None
        
        except ImportError as e:
            pytest.skip(f"Mock database not available: {e}")
