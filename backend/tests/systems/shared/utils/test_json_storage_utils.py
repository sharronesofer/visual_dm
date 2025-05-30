from backend.systems.shared.utils.json_storage_utils import VersionedJsonStorage
from backend.systems.shared.utils.json_storage_utils import VersionedJsonStorage
from backend.systems.shared.utils.json_storage_utils import VersionedJsonStorage
from backend.systems.shared.utils.json_storage_utils import VersionedJsonStorage
from backend.systems.shared.utils.json_storage_utils import VersionedJsonStorage
from backend.systems.shared.utils.json_storage_utils import VersionedJsonStorage
from typing import Type
from typing import List
"""
Tests for JSON storage utilities.
"""

import os
import json
import unittest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock, ANY, call

from backend.systems.shared.utils.json_storage_utils import (
    VersionedJsonStorage,
    DataMigrationError,
    load_json_file,
    save_json_file,
    get_data_file_path,
    list_json_files,
)


class TestVersionedJsonStorage(unittest.TestCase): pass
    """Test the VersionedJsonStorage class."""

    def setUp(self): pass
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.storage = VersionedJsonStorage(self.temp_dir)

        # Test data
        self.test_data = {
            "name": "Test Data",
            "value": 42,
            "nested": {"key": "value"},
            "data_version": 1,
            "last_modified": datetime.now().isoformat(),
        }

        # Test parameters
        self.data_type = "test_type"
        self.identifier = "test_id"

    def tearDown(self): pass
        """Clean up after tests."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_init(self): pass
        """Test initialization."""
        # Verify directories are created
        self.assertTrue(os.path.exists(self.temp_dir))

        # Test with custom parameters
        custom_storage = VersionedJsonStorage(
            self.temp_dir,
            max_backups=10,
            allow_auto_migrate=False,
            versioning_field="version",
            timestamp_field="updated_at",
        )

        self.assertEqual(custom_storage.max_backups, 10)
        self.assertFalse(custom_storage.allow_auto_migrate)
        self.assertEqual(custom_storage.versioning_field, "version")
        self.assertEqual(custom_storage.timestamp_field, "updated_at")

    def test_save_and_load(self): pass
        """Test saving and loading data."""
        # Save data
        result = self.storage.save(
            self.test_data, self.data_type, self.identifier, version=1
        )
        self.assertTrue(result)

        # Verify file exists
        file_path = self.storage._get_file_path(self.data_type, self.identifier)
        self.assertTrue(os.path.exists(file_path))

        # Load data
        loaded_data = self.storage.load(self.data_type, self.identifier)

        # Verify data
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data.get("name"), self.test_data["name"])
        self.assertEqual(loaded_data.get("value"), self.test_data["value"])
        self.assertEqual(
            loaded_data.get("nested").get("key"), self.test_data["nested"]["key"]
        )
        self.assertEqual(loaded_data.get("data_version"), 1)

        # Test loading with expected version
        loaded_data = self.storage.load(
            self.data_type, self.identifier, expected_version=1
        )
        self.assertIsNotNone(loaded_data)

        # Test loading with wrong expected version
        loaded_data = self.storage.load(
            self.data_type, self.identifier, expected_version=2
        )
        self.assertIsNone(loaded_data)

    def test_create_backup(self): pass
        """Test backup creation."""
        # Save data first
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Create backup
        backup_path = self.storage._create_backup(self.data_type, self.identifier)

        # Verify backup was created
        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))

        # Verify backup contains correct data
        with open(backup_path, "r") as f: pass
            backup_data = json.load(f)

        self.assertEqual(backup_data.get("name"), self.test_data["name"])

    def test_create_backup_nonexistent_file(self): pass
        """Test backup creation for nonexistent file."""
        # Try to create backup for file that doesn't exist
        backup_path = self.storage._create_backup(self.data_type, "nonexistent")
        self.assertIsNone(backup_path)

    @patch('shutil.copy2')
    def test_create_backup_error_handling(self, mock_copy): pass
        """Test backup creation error handling."""
        # Save data first
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)
        
        # Mock copy2 to raise an exception
        mock_copy.side_effect = OSError("Permission denied")
        
        # Try to create backup
        backup_path = self.storage._create_backup(self.data_type, self.identifier)
        self.assertIsNone(backup_path)

    def test_cleanup_old_backups(self): pass
        """Test cleanup of old backups."""
        # Set max backups to 2
        self.storage.max_backups = 2

        # Save data
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Create 4 backups manually without cleanup to test the cleanup function
        backup_dir = self.storage._get_backup_dir(self.data_type)
        file_path = self.storage._get_file_path(self.data_type, self.identifier)
        
        import time
        for i in range(4): pass
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{i:03d}"
            backup_path = backup_dir / f"{self.identifier}_{timestamp}.json"
            shutil.copy2(file_path, backup_path)
            time.sleep(0.01)  # Small delay to ensure different timestamps

        # Verify we have 4 backups before cleanup
        backups = list(backup_dir.glob(f"{self.identifier}_*.json"))
        self.assertEqual(len(backups), 4)

        # Now call cleanup
        self.storage._cleanup_old_backups(self.data_type, self.identifier)

        # Check backup directory after cleanup
        backups = list(backup_dir.glob(f"{self.identifier}_*.json"))

        # Should only have 2 backups
        self.assertEqual(len(backups), 2)

    @patch('pathlib.Path.unlink')
    def test_cleanup_old_backups_error_handling(self, mock_unlink): pass
        """Test cleanup error handling when file deletion fails."""
        # Set max backups to 1
        self.storage.max_backups = 1

        # Save data
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Create 3 backups manually
        backup_dir = self.storage._get_backup_dir(self.data_type)
        file_path = self.storage._get_file_path(self.data_type, self.identifier)
        
        import time
        for i in range(3): pass
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{i:03d}"
            backup_path = backup_dir / f"{self.identifier}_{timestamp}.json"
            shutil.copy2(file_path, backup_path)
            time.sleep(0.01)

        # Mock unlink to raise an exception
        mock_unlink.side_effect = OSError("Permission denied")

        # Call cleanup - should handle the error gracefully
        self.storage._cleanup_old_backups(self.data_type, self.identifier)
        
        # Verify unlink was called (even though it failed)
        self.assertTrue(mock_unlink.called)

    def test_migration(self): pass
        """Test data migration."""

        # Register a migration function
        def migrate_v1_to_v2(data): pass
            data["value"] *= 2  # Double the value
            data["migrated"] = True
            return data

        self.storage.register_migration_func(self.data_type, 1, migrate_v1_to_v2)

        # Save v1 data
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Load with v2 expected (should trigger migration)
        migrated_data = self.storage.load(
            self.data_type, self.identifier, expected_version=2
        )

        # Verify migration
        self.assertIsNotNone(migrated_data)
        self.assertEqual(migrated_data.get("value"), self.test_data["value"] * 2)
        self.assertTrue(migrated_data.get("migrated"))
        self.assertEqual(migrated_data.get("data_version"), 2)

    def test_migration_no_functions_registered(self): pass
        """Test migration when no functions are registered."""
        # Save v1 data
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Load with v2 expected but no migration functions
        migrated_data = self.storage.load(
            self.data_type, self.identifier, expected_version=2
        )

        # Should return None since migration is not possible
        self.assertIsNone(migrated_data)

    def test_migration_missing_intermediate_function(self): pass
        """Test migration when intermediate migration function is missing."""
        # Register migration for v1->v2 but not v2->v3
        def migrate_v1_to_v2(data): pass
            data["migrated_to_v2"] = True
            return data

        self.storage.register_migration_func(self.data_type, 1, migrate_v1_to_v2)

        # Save v1 data
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Try to load with v3 expected (missing v2->v3 migration)
        migrated_data = self.storage.load(
            self.data_type, self.identifier, expected_version=3
        )

        # Should return None since migration chain is incomplete
        self.assertIsNone(migrated_data)

    def test_migration_disabled(self): pass
        """Test migration when auto-migration is disabled."""
        # Create storage with auto-migration disabled
        storage = VersionedJsonStorage(self.temp_dir, allow_auto_migrate=False)

        # Register a migration function
        def migrate_v1_to_v2(data): pass
            data["migrated"] = True
            return data

        storage.register_migration_func(self.data_type, 1, migrate_v1_to_v2)

        # Save v1 data
        storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Load with v2 expected (should not trigger migration)
        loaded_data = storage.load(
            self.data_type, self.identifier, expected_version=2
        )

        # Should return original data without migration
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data.get("data_version"), 1)
        self.assertNotIn("migrated", loaded_data)

    def test_migrate_data_no_functions(self): pass
        """Test _migrate_data when no migration functions are registered."""
        data = {"test": "data", "data_version": 1}
        result = self.storage._migrate_data(data, "unknown_type", 1, 2)
        
        # Should return original data unchanged
        self.assertEqual(result, data)

    def test_migrate_data_missing_function(self): pass
        """Test _migrate_data when a migration function is missing."""
        # Register migration for v1->v2 but not v2->v3
        def migrate_v1_to_v2(data): pass
            data["migrated_to_v2"] = True
            return data

        self.storage.register_migration_func(self.data_type, 1, migrate_v1_to_v2)

        data = {"test": "data", "data_version": 1}
        result = self.storage._migrate_data(data, self.data_type, 1, 3)
        
        # Should only migrate to v2, then stop
        self.assertEqual(result.get("data_version"), 2)
        self.assertTrue(result.get("migrated_to_v2"))

    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_save_error_handling(self, mock_open): pass
        """Test save error handling."""
        result = self.storage.save(
            self.test_data, self.data_type, self.identifier, version=1
        )
        self.assertFalse(result)

    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_load_error_handling(self, mock_open): pass
        """Test load error handling."""
        # Create a file first so it exists
        file_path = self.storage._get_file_path(self.data_type, self.identifier)
        os.makedirs(file_path.parent, exist_ok=True)
        file_path.touch()
        
        result = self.storage.load(self.data_type, self.identifier)
        self.assertIsNone(result)

    @patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    def test_load_json_decode_error(self, mock_json_load): pass
        """Test load handling of JSON decode errors."""
        # Create a file first so it exists
        file_path = self.storage._get_file_path(self.data_type, self.identifier)
        os.makedirs(file_path.parent, exist_ok=True)
        with open(file_path, 'w') as f: pass
            f.write("invalid json")
        
        result = self.storage.load(self.data_type, self.identifier)
        self.assertIsNone(result)

    def test_load_nonexistent_file(self): pass
        """Test loading nonexistent file to cover debug logging."""
        result = self.storage.load(self.data_type, "nonexistent_file")
        self.assertIsNone(result)

    def test_delete(self): pass
        """Test deleting data."""
        # Save data first
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Verify file exists
        file_path = self.storage._get_file_path(self.data_type, self.identifier)
        self.assertTrue(os.path.exists(file_path))

        # Delete with backup
        result = self.storage.delete(self.data_type, self.identifier)
        self.assertTrue(result)

        # Verify file is deleted
        self.assertFalse(os.path.exists(file_path))

        # Verify a backup was created
        backup_dir = self.storage._get_backup_dir(self.data_type)
        backups = list(backup_dir.glob(f"{self.identifier}_*.json"))
        self.assertEqual(len(backups), 1)

    def test_delete_without_backup(self): pass
        """Test deleting data without creating backup."""
        # Save data first
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Delete without backup
        result = self.storage.delete(self.data_type, self.identifier, create_backup=False)
        self.assertTrue(result)

        # Verify no backup was created
        backup_dir = self.storage._get_backup_dir(self.data_type)
        backups = list(backup_dir.glob(f"{self.identifier}_*.json"))
        self.assertEqual(len(backups), 0)

    def test_delete_nonexistent_file(self): pass
        """Test deleting nonexistent file."""
        result = self.storage.delete(self.data_type, "nonexistent")
        # Should return True (idempotent delete - no error if file doesn't exist)
        self.assertTrue(result)

    @patch('pathlib.Path.unlink')
    def test_delete_error_handling(self, mock_unlink): pass
        """Test delete error handling."""
        # Save data first
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Mock unlink to raise an exception
        mock_unlink.side_effect = OSError("Permission denied")

        result = self.storage.delete(self.data_type, self.identifier, create_backup=False)
        self.assertFalse(result)

    def test_list_all(self): pass
        """Test listing all identifiers."""
        # Save multiple files
        for i in range(3): pass
            data = {"id": i, "name": f"Test {i}"}
            self.storage.save(data, self.data_type, f"test_{i}", version=1)

        # List all
        identifiers = self.storage.list_all(self.data_type)

        # Verify results
        self.assertEqual(len(identifiers), 3)
        self.assertIn("test_0", identifiers)
        self.assertIn("test_1", identifiers)
        self.assertIn("test_2", identifiers)

    def test_list_all_empty_directory(self): pass
        """Test listing all identifiers in empty directory."""
        identifiers = self.storage.list_all("empty_type")
        self.assertEqual(len(identifiers), 0)

    def test_exists(self): pass
        """Test checking if file exists."""
        # File doesn't exist initially
        self.assertFalse(self.storage.exists(self.data_type, self.identifier))

        # Save data
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # File should exist now
        self.assertTrue(self.storage.exists(self.data_type, self.identifier))

    def test_get_version(self): pass
        """Test getting version of data."""
        # Save data with version 3
        self.storage.save(self.test_data, self.data_type, self.identifier, version=3)

        # Get version
        version = self.storage.get_version(self.data_type, self.identifier)
        self.assertEqual(version, 3)

    def test_get_version_nonexistent_file(self): pass
        """Test getting version of nonexistent file."""
        version = self.storage.get_version(self.data_type, "nonexistent")
        self.assertIsNone(version)

    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_get_version_error_handling(self, mock_open): pass
        """Test get_version error handling."""
        # Create a file first so it exists
        file_path = self.storage._get_file_path(self.data_type, self.identifier)
        os.makedirs(file_path.parent, exist_ok=True)
        file_path.touch()
        
        version = self.storage.get_version(self.data_type, self.identifier)
        self.assertIsNone(version)

    def test_get_last_modified(self): pass
        """Test getting last modified timestamp."""
        # Save data
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Get last modified
        last_modified = self.storage.get_last_modified(self.data_type, self.identifier)
        self.assertIsNotNone(last_modified)
        self.assertIsInstance(last_modified, datetime)

    def test_get_last_modified_nonexistent_file(self): pass
        """Test getting last modified of nonexistent file."""
        last_modified = self.storage.get_last_modified(self.data_type, "nonexistent")
        self.assertIsNone(last_modified)

    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_get_last_modified_error_handling(self, mock_open): pass
        """Test get_last_modified error handling."""
        # Create a file first so it exists
        file_path = self.storage._get_file_path(self.data_type, self.identifier)
        os.makedirs(file_path.parent, exist_ok=True)
        file_path.touch()
        
        last_modified = self.storage.get_last_modified(self.data_type, self.identifier)
        self.assertIsNone(last_modified)

    def test_get_last_modified_invalid_timestamp(self): pass
        """Test get_last_modified with invalid timestamp in data."""
        # Save data with invalid timestamp
        data = self.test_data.copy()
        data["last_modified"] = "invalid-timestamp"
        
        file_path = self.storage._get_file_path(self.data_type, self.identifier)
        os.makedirs(file_path.parent, exist_ok=True)
        with open(file_path, 'w') as f: pass
            json.dump(data, f)
        
        # Should fall back to file system timestamp
        last_modified = self.storage.get_last_modified(self.data_type, self.identifier)
        self.assertIsNotNone(last_modified)
        self.assertIsInstance(last_modified, datetime)

    def test_failed_migration(self): pass
        """Test failed migration scenario."""
        # Register a migration function that raises an exception
        def failing_migration(data): pass
            raise ValueError("Migration failed")

        self.storage.register_migration_func(self.data_type, 1, failing_migration)

        # Save v1 data
        self.storage.save(self.test_data, self.data_type, self.identifier, version=1)

        # Try to load with v2 expected (should handle migration failure gracefully)
        result = self.storage.load(self.data_type, self.identifier, expected_version=2)
        # Should return None when migration fails
        self.assertIsNone(result)

    @patch("backend.systems.shared.utils.json_storage_utils.json.dump")
    def test_save_json_error(self, mock_dump): pass
        """Test save error handling when JSON dump fails."""
        mock_dump.side_effect = TypeError("Object not serializable")

        result = self.storage.save(
            self.test_data, self.data_type, self.identifier, version=1
        )
        self.assertFalse(result)


class TestStandaloneFunctions(unittest.TestCase): pass
    """Test standalone utility functions."""

    def setUp(self): pass
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self): pass
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)

    def test_load_json_file(self): pass
        """Test loading JSON file."""
        # Create test file
        test_data = {"key": "value", "number": 42}
        file_path = Path(self.temp_dir) / "test.json"

        with open(file_path, "w") as f: pass
            json.dump(test_data, f)

        # Load file
        loaded_data = load_json_file(file_path)

        # Verify data
        self.assertEqual(loaded_data, test_data)

    def test_load_json_file_nonexistent(self): pass
        """Test loading nonexistent JSON file."""
        file_path = Path(self.temp_dir) / "nonexistent.json"

        # Load with default
        loaded_data = load_json_file(file_path, default={"default": True})

        # Should return default
        self.assertEqual(loaded_data, {"default": True})

    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_load_json_file_error_handling(self, mock_open): pass
        """Test load_json_file error handling."""
        file_path = Path(self.temp_dir) / "test.json"
        file_path.touch()  # Create the file so it exists
        
        result = load_json_file(file_path, default="error_default")
        self.assertEqual(result, "error_default")

    def test_save_json_file(self): pass
        """Test saving JSON file."""
        test_data = {"key": "value", "number": 42}
        file_path = Path(self.temp_dir) / "test.json"

        # Save file
        result = save_json_file(file_path, test_data)
        self.assertTrue(result)

        # Verify file exists and contains correct data
        self.assertTrue(file_path.exists())

        with open(file_path, "r") as f: pass
            loaded_data = json.load(f)

        self.assertEqual(loaded_data, test_data)

    def test_save_json_file_custom_indent(self): pass
        """Test saving JSON file with custom indentation."""
        test_data = {"key": "value"}
        file_path = Path(self.temp_dir) / "test.json"

        # Save with custom indent
        result = save_json_file(file_path, test_data, indent=4)
        self.assertTrue(result)

        # Verify file was saved
        self.assertTrue(file_path.exists())

    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_save_json_file_error_handling(self, mock_open): pass
        """Test save_json_file error handling."""
        test_data = {"key": "value"}
        file_path = Path(self.temp_dir) / "test.json"
        
        result = save_json_file(file_path, test_data)
        self.assertFalse(result)

    def test_get_data_file_path(self): pass
        """Test getting data file path."""
        # Test with default base directory
        path = get_data_file_path("biomes")
        expected = Path("data") / "biomes.json"
        self.assertEqual(path, expected)

        # Test with custom base directory
        path = get_data_file_path("entities", base_dir="custom_data")
        expected = Path("custom_data") / "entities.json"
        self.assertEqual(path, expected)

    @patch.dict(os.environ, {'DATA_DIR': '/custom/data/dir'})
    def test_get_data_file_path_with_env_var(self): pass
        """Test getting data file path with environment variable."""
        path = get_data_file_path("biomes")
        expected = Path("/custom/data/dir") / "biomes.json"
        self.assertEqual(path, expected)

    def test_list_json_files(self): pass
        """Test listing JSON files."""
        # Create test files
        test_dir = Path(self.temp_dir) / "json_files"
        test_dir.mkdir()

        (test_dir / "file1.json").touch()
        (test_dir / "file2.json").touch()
        (test_dir / "file3.txt").touch()  # Not a JSON file

        # List JSON files
        json_files = list_json_files(test_dir)

        # Verify results
        self.assertEqual(len(json_files), 2)
        file_names = [f.name for f in json_files]
        self.assertIn("file1.json", file_names)
        self.assertIn("file2.json", file_names)
        self.assertNotIn("file3.txt", file_names)

    def test_list_json_files_custom_pattern(self): pass
        """Test listing files with custom pattern."""
        # Create test files
        test_dir = Path(self.temp_dir) / "pattern_files"
        test_dir.mkdir()

        (test_dir / "data1.json").touch()
        (test_dir / "config.json").touch()
        (test_dir / "backup.bak").touch()

        # List with custom pattern
        files = list_json_files(test_dir, pattern="data*.json")

        # Verify results
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "data1.json")

    def test_list_json_files_nonexistent_directory(self): pass
        """Test listing files in nonexistent directory."""
        nonexistent_dir = Path(self.temp_dir) / "nonexistent"

        files = list_json_files(nonexistent_dir)

        # Should return empty list
        self.assertEqual(len(files), 0)


if __name__ == "__main__": pass
    unittest.main()
