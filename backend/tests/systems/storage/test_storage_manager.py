from typing import Type
"""
Unit tests for the StorageManager base class.

These tests verify that: pass
1. The singleton pattern works correctly
2. The interface contract is enforced
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from backend.systems.storage.storage_service import StorageManager

class TestStorageManager: pass
    """Test suite for the StorageManager class."""
    
    def test_singleton_pattern(self): pass
        """Test that the singleton pattern works correctly."""
        # Reset singleton first
        StorageManager._instance = None
        
        # Patch JSONStorageManager to prevent actual instantiation
        with patch('backend.systems.storage.storage_service.JSONStorageManager') as mock_json: pass
            # Setup mock
            mock_instance = MagicMock()
            mock_json.return_value = mock_instance
            
            # First call should create instance
            instance1 = StorageManager.get_instance()
            assert instance1 == mock_instance
            assert mock_json.call_count == 1
            
            # Second call should reuse instance
            instance2 = StorageManager.get_instance()
            assert instance2 == instance1
            assert mock_json.call_count == 1
        
        # Reset singleton after test
        StorageManager._instance = None
    
    def test_abstract_methods(self): pass
        """Test that instantiating StorageManager directly raises TypeError."""
        with pytest.raises(TypeError): pass
            StorageManager()
    
    @pytest.mark.asyncio
    async def test_interface_contract(self): pass
        """Test that all required methods are present in JSONStorageManager."""
        from unittest.mock import AsyncMock
        
        # Reset singleton first
        StorageManager._instance = None
        
        with patch('backend.systems.storage.storage_service.JSONStorageManager') as mock_json: pass
            # Setup mock with async methods
            mock_instance = AsyncMock()
            mock_json.return_value = mock_instance
            
            # Get instance
            manager = StorageManager.get_instance()
            
            # Verify required methods exist by calling them
            await manager.get("test")
            mock_instance.get.assert_called_once_with("test")
            
            await manager.set("test", {"value": 123})
            mock_instance.set.assert_called_once_with("test", {"value": 123})
            
            await manager.delete("test")
            mock_instance.delete.assert_called_once_with("test")
            
            await manager.list("test")
            mock_instance.list.assert_called_once_with("test")
            
            await manager.exists("test")
            mock_instance.exists.assert_called_once_with("test")
            
            await manager.get_version_history("test")
            mock_instance.get_version_history.assert_called_once_with("test")
        
        # Reset singleton after test
        StorageManager._instance = None 