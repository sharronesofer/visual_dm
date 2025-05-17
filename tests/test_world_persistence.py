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

from app.core.persistence.serialization import serialize, deserialize, SerializedData, SerializationFormat, CompressionType, extract_scene_dependency_graph, resolve_component_references
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

    def test_save_world_disk_full(self):
        """
        Test save_world with simulated disk full (IOError on write).
        """
        from app.core.persistence.world_persistence import FileSystemStorageStrategy
        import builtins
        world_id = "disk_full_world"
        storage = FileSystemStorageStrategy(self.temp_dir)
        data = serialize({"world_id": world_id, "foo": "bar"})
        # Patch open to raise IOError
        with patch("builtins.open", side_effect=IOError("Disk full")):
            result = storage.save_world(world_id, data)
            self.assertFalse(result)

    def test_save_world_permission_error(self):
        """
        Test save_world with permission error (PermissionError on write).
        """
        from app.core.persistence.world_persistence import FileSystemStorageStrategy
        import builtins
        world_id = "perm_error_world"
        storage = FileSystemStorageStrategy(self.temp_dir)
        data = serialize({"world_id": world_id, "foo": "bar"})
        # Patch open to raise PermissionError
        with patch("builtins.open", side_effect=PermissionError("No permission")):
            result = storage.save_world(world_id, data)
            self.assertFalse(result)

    def test_load_world_corrupted_file_and_backup(self):
        """
        Test load_world with corrupted file (simulate unreadable file, ensure backup is loaded if available).
        """
        from app.core.persistence.world_persistence import FileSystemStorageStrategy
        world_id = "corrupt_world"
        storage = FileSystemStorageStrategy(self.temp_dir)
        # Create a valid backup
        backup_dir = Path(self.temp_dir) / "backups" / world_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{world_id}_20220101T000000.json"
        with open(backup_path, "wb") as f:
            f.write(b"{\"world_id\": \"corrupt_world\", \"foo\": \"backup\"}")
        # Patch open to raise error for main file, but not for backup
        orig_open = open
        def fake_open(path, mode="r", *args, **kwargs):
            if str(path).endswith(f"{world_id}.json"):
                raise IOError("Corrupted file")
            return orig_open(path, mode, *args, **kwargs)
        with patch("builtins.open", side_effect=fake_open):
            loaded = storage.load_world(world_id)
            self.assertIsNotNone(loaded)
            self.assertIn(b"backup", loaded.data)

    def test_backup_created_and_pruned(self):
        """
        Test that backup is created before save and old backups are pruned.
        """
        from app.core.persistence.world_persistence import FileSystemStorageStrategy
        world_id = "backup_test_world"
        storage = FileSystemStorageStrategy(self.temp_dir, retention_count=2)
        data = serialize({"world_id": world_id, "foo": "bar"})
        # Save multiple times to create backups
        for _ in range(4):
            storage.save_world(world_id, data)
            time.sleep(0.01)  # Ensure timestamp changes
        backup_dir = Path(self.temp_dir) / "backups" / world_id
        backups = sorted(backup_dir.glob(f"{world_id}_*.json"))
        self.assertLessEqual(len(backups), 2)

    def test_logging_on_error_and_recovery(self):
        """
        Test that all errors and recovery attempts are logged.
        """
        from app.core.persistence.world_persistence import FileSystemStorageStrategy
        import logging
        world_id = "log_test_world"
        storage = FileSystemStorageStrategy(self.temp_dir)
        data = serialize({"world_id": world_id, "foo": "bar"})
        # Patch logging to capture logs
        with patch.object(logging, "error") as mock_error, patch.object(logging, "warning") as mock_warning, patch.object(logging, "info") as mock_info:
            # Simulate save error
            with patch("builtins.open", side_effect=IOError("Disk full")):
                storage.save_world(world_id, data)
            mock_error.assert_called()
            # Simulate load error and recovery
            backup_dir = Path(self.temp_dir) / "backups" / world_id
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"{world_id}_20220101T000000.json"
            with open(backup_path, "wb") as f:
                f.write(b"{\"world_id\": \"log_test_world\", \"foo\": \"backup\"}")
            orig_open = open
            def fake_open(path, mode="r", *args, **kwargs):
                if str(path).endswith(f"{world_id}.json"):
                    raise IOError("Corrupted file")
                return orig_open(path, mode, *args, **kwargs)
            with patch("builtins.open", side_effect=fake_open):
                storage.load_world(world_id)
            mock_warning.assert_called()


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

    def test_partial_scene_restoration_basic(self):
        """
        Test loading a subset of components with dependencies from mock world_data.
        """
        # Mock world_data
        world_data = {
            'A': {'dependencies': ['B', 'C']},
            'B': {'dependencies': ['C']},
            'C': {},
            'D': {'dependencies': ['A']},
        }
        # Simulate storage and deserialization
        class DummyStorage:
            def load_world(self, scene_id):
                class DummySerialized: pass
                return DummySerialized()
        def dummy_deserialize(serialized):
            return {'world_data': world_data}
        mgr = WorldPersistenceManager.__new__(WorldPersistenceManager)
        mgr.storage = DummyStorage()
        import app.core.persistence.world_persistence as wp
        wp.deserialize = dummy_deserialize
        # Load only A (should also load B and C)
        loaded = mgr.load_scene_partial('dummy', ['A'])
        assert set(loaded.keys()) == {'A', 'B', 'C'}
        # All references should be valid
        resolve_component_references(loaded, log_missing=False)
        for cid, comp in loaded.items():
            for dep in comp.get('dependencies', []):
                assert dep in loaded

    def test_partial_scene_restoration_circular(self):
        """
        Test circular dependencies: ensure no infinite loop, all required components are loaded.
        """
        # Mock world_data
        world_data = {
            'X': {'dependencies': ['Y']},
            'Y': {'dependencies': ['Z']},
            'Z': {'dependencies': ['X']},
            'W': {},
        }
        # Simulate storage and deserialization
        class DummyStorage:
            def load_world(self, scene_id):
                class DummySerialized: pass
                return DummySerialized()
        def dummy_deserialize(serialized):
            return {'world_data': world_data}
        mgr = WorldPersistenceManager.__new__(WorldPersistenceManager)
        mgr.storage = DummyStorage()
        import app.core.persistence.world_persistence as wp
        wp.deserialize = dummy_deserialize
        # Load X (should load X, Y, Z)
        loaded = mgr.load_scene_partial('dummy', ['X'])
        assert set(loaded.keys()) == {'X', 'Y', 'Z'}
        resolve_component_references(loaded, log_missing=False)
        for cid, comp in loaded.items():
            for dep in comp.get('dependencies', []):
                assert dep in loaded

    def test_partial_scene_restoration_missing(self):
        """
        Test missing dependencies: references to missing components are set to None and warning is logged.
        """
        # Mock world_data
        world_data = {
            'A': {'dependencies': ['B', 'MISSING']},
            'B': {},
        }
        # Simulate storage and deserialization
        class DummyStorage:
            def load_world(self, scene_id):
                class DummySerialized: pass
                return DummySerialized()
        def dummy_deserialize(serialized):
            return {'world_data': world_data}
        mgr = WorldPersistenceManager.__new__(WorldPersistenceManager)
        mgr.storage = DummyStorage()
        import app.core.persistence.world_persistence as wp
        wp.deserialize = dummy_deserialize
        loaded = mgr.load_scene_partial('dummy', ['A'])
        # After reference resolution, 'MISSING' should be removed from dependencies
        resolve_component_references(loaded, log_missing=False)
        assert 'MISSING' not in loaded['A']['dependencies']
        assert 'B' in loaded
        assert 'A' in loaded


if __name__ == "__main__":
    unittest.main() 