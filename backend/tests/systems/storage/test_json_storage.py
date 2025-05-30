from typing import List
from pathlib import Path
"""
Unit tests for the JSONStorageManager class.

These tests verify that:
1. Basic CRUD operations work correctly
2. Versioning functionality works
3. Path handling works correctly
4. Error handling is appropriate
"""

import pytest
import asyncio
import os
import shutil
import json
import tempfile
from unittest.mock import patch, mock_open

from backend.systems.storage.storage_service import JSONStorageManager

class TestJSONStorageManager:
    """Test suite for the JSONStorageManager class."""
    
    @pytest.fixture
    def storage_manager(self):
        """Create a temporary JSONStorageManager for testing."""
        # Create temp directory for test data
        temp_dir = tempfile.mkdtemp()
        
        # Create storage manager with temp directory
        manager = JSONStorageManager(base_path=temp_dir)
        
        yield manager
        
        # Clean up temp directory after tests
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_get_nonexistent(self, storage_manager):
        """Test get() with nonexistent path returns None."""
        result = await storage_manager.get("nonexistent/path")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, storage_manager):
        """Test set() and get() work correctly."""
        test_data = {"name": "test", "value": 123}
        test_path = "test/data"
        
        # Set data
        await storage_manager.set(test_path, test_data)
        
        # Get data and verify
        result = await storage_manager.get(test_path)
        assert result == test_data
    
    @pytest.mark.asyncio
    async def test_set_and_overwrite(self, storage_manager):
        """Test set() overwrites existing data."""
        test_path = "test/data"
        
        # Set initial data
        await storage_manager.set(test_path, {"value": 1})
        
        # Set new data
        new_data = {"value": 2}
        await storage_manager.set(test_path, new_data)
        
        # Get data and verify
        result = await storage_manager.get(test_path)
        assert result == new_data
    
    @pytest.mark.asyncio
    async def test_delete(self, storage_manager):
        """Test delete() removes data."""
        test_path = "test/data"
        
        # Set data
        await storage_manager.set(test_path, {"value": 1})
        
        # Verify data exists
        assert await storage_manager.exists(test_path)
        
        # Delete data
        await storage_manager.delete(test_path)
        
        # Verify data no longer exists
        assert not await storage_manager.exists(test_path)
    
    @pytest.mark.asyncio
    async def test_exists(self, storage_manager):
        """Test exists() returns correct values."""
        test_path = "test/data"
        
        # Test nonexistent path
        assert not await storage_manager.exists(test_path)
        
        # Set data
        await storage_manager.set(test_path, {"value": 1})
        
        # Test existing path
        assert await storage_manager.exists(test_path)
    
    @pytest.mark.asyncio
    async def test_list(self, storage_manager):
        """Test list() returns correct values."""
        # Create several files under a common path
        await storage_manager.set("users/1", {"id": 1, "name": "Alice"})
        await storage_manager.set("users/2", {"id": 2, "name": "Bob"})
        await storage_manager.set("users/3", {"id": 3, "name": "Charlie"})
        
        # List all users
        result = await storage_manager.list("users")
        
        # Verify result
        assert len(result) == 3
        assert result["1"] == {"id": 1, "name": "Alice"}
        assert result["2"] == {"id": 2, "name": "Bob"}
        assert result["3"] == {"id": 3, "name": "Charlie"}
    
    @pytest.mark.asyncio
    async def test_version_history(self, storage_manager):
        """Test get_version_history() returns correct versions."""
        test_path = "test/data"
        
        # Set data multiple times
        await storage_manager.set(test_path, {"version": 1})
        await storage_manager.set(test_path, {"version": 2})
        await storage_manager.set(test_path, {"version": 3})
        
        # Get version history
        history = await storage_manager.get_version_history(test_path)
        
        # Verify history
        assert len(history) == 3
        assert history[0]["data"] == {"version": 1}
        assert history[1]["data"] == {"version": 2}
        assert history[2]["data"] == {"version": 3}
        
        # Check timestamps are ascending
        assert history[0]["timestamp"] <= history[1]["timestamp"]
        assert history[1]["timestamp"] <= history[2]["timestamp"]
    
    @pytest.mark.asyncio
    async def test_file_path_conversion(self, storage_manager):
        """Test that paths are converted to file paths correctly."""
        # Test various path formats
        test_cases = [
            ("simple", "simple.json"),
            ("nested/path", "nested_path.json"),
            ("/leading/slash", "leading_slash.json"),
            ("trailing/slash/", "trailing_slash.json"),
            ("multiple///slashes", "multiple_slashes.json"),
        ]
        
        for input_path, expected_filename in test_cases:
            file_path = storage_manager._get_file_path(input_path)
            assert os.path.basename(file_path) == expected_filename
    
    @pytest.mark.asyncio
    async def test_get_error_handling(self, storage_manager):
        """Test that get() handles errors gracefully."""
        # Test with corrupted JSON file
        test_path = "test/corrupted"
        
        # Directly write corrupted JSON
        file_path = storage_manager._get_file_path(test_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write("{invalid: json")
        
        # Try to get data
        result = await storage_manager.get(test_path)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_error_handling(self, storage_manager):
        """Test that set() handles errors appropriately."""
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(Exception):
                await storage_manager.set("test/path", {"data": 123})
    
    @pytest.mark.asyncio
    async def test_delete_error_handling(self, storage_manager):
        """Test that delete() handles errors appropriately."""
        test_path = "test/data"
        
        # Set data
        await storage_manager.set(test_path, {"value": 1})
        
        # Mock os.remove to raise an exception
        with patch('os.remove', side_effect=PermissionError("Permission denied")):
            with pytest.raises(Exception):
                await storage_manager.delete(test_path) 