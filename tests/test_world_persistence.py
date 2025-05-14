"""
Tests for the world persistence system.

This module tests the functionality of the world persistence system,
including saving, loading, serialization, and version control.
"""

import unittest
import tempfile
import shutil
import os
import json
import time
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.core.persistence.serialization import serialize, deserialize, SerializedData, SerializationFormat, CompressionType
from app.core.persistence.version_control import WorldVersionControl, VersionMetadata
from app.core.persistence.world_persistence import WorldPersistenceManager, FileSystemStorageStrategy


class TestSerialization(unittest.TestCase):
    """Test serialization functionality."""
    
    def test_basic_serialization(self):
        """Test basic serialization and deserialization."""
        # Create test data
        test_data = {
            "world_id": "test_world",
            "name": "Test World",
            "created_at": datetime.utcnow().isoformat(),
            "entities": [
                {"id": "entity1", "name": "Entity 1", "type": "character"},
                {"id": "entity2", "name": "Entity 2", "type": "location"}
            ],
            "metadata": {
                "author": "Test User",
                "version": "1.0"
            }
        }
        
        # Serialize
        serialized = serialize(test_data)
        self.assertIsInstance(serialized, SerializedData)
        
        # Deserialize
        deserialized = deserialize(serialized)
        
        # Verify
        self.assertEqual(deserialized["world_id"], test_data["world_id"])
        self.assertEqual(deserialized["name"], test_data["name"])
        self.assertEqual(len(deserialized["entities"]), len(test_data["entities"]))
        self.assertEqual(deserialized["metadata"]["author"], test_data["metadata"]["author"])
    
    def test_compression(self):
        """Test serialization with different compression types."""
        # Create large test data to better test compression
        test_data = {
            "world_id": "test_world",
            "name": "Test World",
            "description": "A" * 10000,  # Large string to compress
            "entities": [{"id": f"entity{i}", "name": f"Entity {i}"} for i in range(100)]
        }
        
        # Test different compression types
        for compression_type in [CompressionType.NONE, CompressionType.GZIP, CompressionType.BZ2, CompressionType.LZMA, CompressionType.ZLIB]:
            # Serialize with compression
            serialized = serialize(test_data, compression_type=compression_type)
            
            # Verify compression type is recorded
            self.assertEqual(serialized.compression_type, compression_type)
            
            # Deserialize and verify
            deserialized = deserialize(serialized)
            self.assertEqual(deserialized["world_id"], test_data["world_id"])
            self.assertEqual(len(deserialized["entities"]), len(test_data["entities"]))
    
    def test_format_selection(self):
        """Test different serialization formats."""
        test_data = {
            "world_id": "test_world",
            "name": "Test World",
            "entities": [{"id": "entity1", "name": "Entity 1"}]
        }
        
        # Test different formats
        for format_type in [SerializationFormat.JSON, SerializationFormat.PICKLE, SerializationFormat.MSGPACK]:
            # Serialize with format
            serialized = serialize(test_data, format_type=format_type)
            
            # Verify format is recorded
            self.assertEqual(serialized.format_type, format_type)
            
            # Deserialize and verify
            deserialized = deserialize(serialized)
            self.assertEqual(deserialized["world_id"], test_data["world_id"])
            self.assertEqual(deserialized["name"], test_data["name"])


class TestFileSystemStorageStrategy(unittest.TestCase):
    """Test file system storage strategy."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FileSystemStorageStrategy(self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_save_load_world(self):
        """Test saving and loading a world."""
        # Create test data
        world_id = "test_world"
        test_data = {
            "world_id": world_id,
            "name": "Test World",
            "entities": [{"id": "entity1", "name": "Entity 1"}]
        }
        
        # Serialize
        serialized = serialize(test_data)
        
        # Save
        success = self.storage.save_world(world_id, serialized)
        self.assertTrue(success)
        
        # Verify file exists
        world_path = Path(self.temp_dir) / "worlds" / f"{world_id}.json"
        self.assertTrue(world_path.exists())
        
        # Load
        loaded = self.storage.load_world(world_id)
        self.assertIsNotNone(loaded)
        
        # Deserialize and verify
        deserialized = deserialize(loaded)
        self.assertEqual(deserialized["world_id"], test_data["world_id"])
        self.assertEqual(deserialized["name"], test_data["name"])
    
    def test_delete_world(self):
        """Test deleting a world."""
        # Create and save test world
        world_id = "test_delete_world"
        test_data = {
            "world_id": world_id,
            "name": "Test Delete World"
        }
        
        serialized = serialize(test_data)
        self.storage.save_world(world_id, serialized)
        
        # Delete
        success = self.storage.delete_world(world_id)
        self.assertTrue(success)
        
        # Verify file is gone
        world_path = Path(self.temp_dir) / "worlds" / f"{world_id}.json"
        self.assertFalse(world_path.exists())
        
        # Load should return None
        loaded = self.storage.load_world(world_id)
        self.assertIsNone(loaded)
    
    def test_list_worlds(self):
        """Test listing worlds."""
        # Create and save test worlds
        world_ids = ["test_world_1", "test_world_2", "test_world_3"]
        
        for world_id in world_ids:
            test_data = {
                "world_id": world_id,
                "name": f"Test World {world_id}"
            }
            serialized = serialize(test_data)
            self.storage.save_world(world_id, serialized)
        
        # List worlds
        listed_worlds = self.storage.list_worlds()
        
        # Verify all worlds are listed
        for world_id in world_ids:
            self.assertIn(world_id, listed_worlds)
    
    def test_version_storage(self):
        """Test version storage functionality."""
        # Create test world and version
        world_id = "test_version_world"
        version_id = "v1.0"
        
        version_data = {
            "version_id": version_id,
            "timestamp": datetime.utcnow().isoformat(),
            "description": "Test version",
            "metadata": {"test": True}
        }
        
        # Save version
        success = self.storage.save_version(world_id, version_id, version_data)
        self.assertTrue(success)
        
        # Verify file exists
        version_path = Path(self.temp_dir) / "versions" / world_id / f"{version_id}.json"
        self.assertTrue(version_path.exists())
        
        # Load version
        loaded_version = self.storage.load_version(world_id, version_id)
        self.assertIsNotNone(loaded_version)
        
        # Verify data
        self.assertEqual(loaded_version["version_id"], version_data["version_id"])
        self.assertEqual(loaded_version["description"], version_data["description"])
        self.assertEqual(loaded_version["metadata"]["test"], version_data["metadata"]["test"])
        
        # List versions
        versions = self.storage.list_versions(world_id)
        self.assertIn(version_id, versions)


class TestWorldPersistenceManager(unittest.TestCase):
    """Test world persistence manager."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FileSystemStorageStrategy(self.temp_dir)
        self.manager = WorldPersistenceManager(self.storage, auto_save_interval=60)
    
    def tearDown(self):
        """Clean up after tests."""
        # Shut down manager
        self.manager.shutdown()
        
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_create_world(self):
        """Test creating a new world."""
        # Create world
        world_id = self.manager.create_world(metadata={"test": True})
        
        # Verify ID was returned
        self.assertIsNotNone(world_id)
        
        # Verify world is in cache
        self.assertIn(world_id, self.manager.worlds_cache)
        
        # Verify world data
        world_data = self.manager.worlds_cache[world_id]
        self.assertEqual(world_data["world_id"], world_id)
        self.assertEqual(world_data["metadata"]["test"], True)
        
        # Verify file was created
        world_path = Path(self.temp_dir) / "worlds" / f"{world_id}.json"
        self.assertTrue(world_path.exists())
        
        # Verify version control was initialized
        self.assertIn(world_id, self.manager.version_controls)
        
        # Verify version file was created
        versions_dir = Path(self.temp_dir) / "versions" / world_id
        self.assertTrue(versions_dir.exists())
        self.assertTrue(any(versions_dir.glob("*.json")))
    
    def test_load_world(self):
        """Test loading a world."""
        # Create world
        world_id = self.manager.create_world()
        
        # Clear cache
        self.manager.worlds_cache.clear()
        self.manager.version_controls.clear()
        self.manager.change_trackers.clear()
        self.manager.transaction_managers.clear()
        
        # Load world
        world_data = self.manager.load_world(world_id)
        
        # Verify data
        self.assertIsNotNone(world_data)
        self.assertEqual(world_data["world_id"], world_id)
        
        # Verify systems were initialized
        self.assertIn(world_id, self.manager.version_controls)
        self.assertIn(world_id, self.manager.change_trackers)
        self.assertIn(world_id, self.manager.transaction_managers)
    
    def test_save_world(self):
        """Test saving a world."""
        # Create world
        world_id = self.manager.create_world()
        
        # Modify world data
        world_data = self.manager.worlds_cache[world_id]
        world_data["test_field"] = "test_value"
        
        # Save world
        success = self.manager.save_world(world_id)
        self.assertTrue(success)
        
        # Clear cache
        self.manager.worlds_cache.clear()
        
        # Load world
        loaded_data = self.manager.load_world(world_id)
        
        # Verify changes were saved
        self.assertEqual(loaded_data["test_field"], "test_value")
    
    def test_create_snapshot(self):
        """Test creating a version snapshot."""
        # Create world
        world_id = self.manager.create_world()
        
        # Modify world data
        world_data = self.manager.worlds_cache[world_id]
        world_data["test_field"] = "initial_value"
        
        # Create snapshot
        version_id1 = self.manager.create_snapshot(world_id, "First snapshot")
        self.assertIsNotNone(version_id1)
        
        # Modify world data again
        world_data["test_field"] = "updated_value"
        
        # Create another snapshot
        version_id2 = self.manager.create_snapshot(world_id, "Second snapshot")
        self.assertIsNotNone(version_id2)
        
        # Verify different version IDs
        self.assertNotEqual(version_id1, version_id2)
        
        # Verify version files were created
        versions_dir = Path(self.temp_dir) / "versions" / world_id
        self.assertTrue((versions_dir / f"{version_id1}.json").exists())
        self.assertTrue((versions_dir / f"{version_id2}.json").exists())
    
    def test_rollback(self):
        """Test rolling back to a previous version."""
        # Create world
        world_id = self.manager.create_world()
        
        # Modify world data
        world_data = self.manager.worlds_cache[world_id]
        world_data["test_field"] = "initial_value"
        
        # Create snapshot
        version_id1 = self.manager.create_snapshot(world_id, "First snapshot")
        
        # Modify world data again
        world_data["test_field"] = "updated_value"
        world_data["new_field"] = "new_value"
        
        # Create another snapshot
        version_id2 = self.manager.create_snapshot(world_id, "Second snapshot")
        
        # Roll back to first version
        rolled_back_data = self.manager.rollback_to_version(world_id, version_id1)
        
        # Verify rollback
        self.assertIsNotNone(rolled_back_data)
        self.assertEqual(rolled_back_data["test_field"], "initial_value")
        self.assertNotIn("new_field", rolled_back_data)
        
        # Verify cache is updated
        self.assertEqual(self.manager.worlds_cache[world_id]["test_field"], "initial_value")
        self.assertNotIn("new_field", self.manager.worlds_cache[world_id])
    
    def test_auto_save(self):
        """Test auto-save functionality."""
        # Create a manager with a short auto-save interval
        short_interval_manager = WorldPersistenceManager(self.storage, auto_save_interval=1)
        
        try:
            # Create world
            world_id = short_interval_manager.create_world()
            
            # Modify world data
            world_data = short_interval_manager.worlds_cache[world_id]
            world_data["test_field"] = "auto_save_test"
            
            # Mark as dirty
            short_interval_manager.mark_world_dirty(world_id)
            
            # Wait for auto-save
            time.sleep(2)
            
            # Clear cache
            short_interval_manager.worlds_cache.clear()
            
            # Load world
            loaded_data = short_interval_manager.load_world(world_id)
            
            # Verify changes were auto-saved
            self.assertEqual(loaded_data["test_field"], "auto_save_test")
        finally:
            # Shut down manager
            short_interval_manager.shutdown()


if __name__ == "__main__":
    unittest.main() 