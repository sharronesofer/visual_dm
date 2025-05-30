from typing import Any
from typing import Type
from typing import List
"""
Tests for backend.systems.shared.utils.json_storage_utils (legacy module)

Comprehensive tests for the legacy JSON storage utilities that provide
common JSON operations used across systems.
"""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from typing import Dict, Any, List, Union
from datetime import datetime

# Import the module being tested
try:
    from backend.systems.shared.utils.json_storage_utils import (
        load_json,
        save_json,
        append_to_json_array,
        update_json_object,
        backup_json,
        merge_json_files,
        validate_json_schema,
        cleanup_old_backups,
    )
except ImportError as e:
    pytest.skip(f"Could not import json_storage_utils: {e}", allow_module_level=True)


def test_module_imports():
    """Test that all expected functions can be imported."""
    assert callable(load_json)
    assert callable(save_json)
    assert callable(append_to_json_array)
    assert callable(update_json_object)
    assert callable(backup_json)
    assert callable(merge_json_files)
    assert callable(validate_json_schema)
    assert callable(cleanup_old_backups)


class TestLoadJson:
    """Test class for load_json function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.json"
        self.test_data = {"key": "value", "number": 42, "nested": {"inner": "data"}}

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_json_success(self):
        """Test successful JSON loading."""
        # Create test file
        with open(self.test_file, "w") as f:
            json.dump(self.test_data, f)

        result = load_json(self.test_file)
        assert result == self.test_data

    def test_load_json_with_path_object(self):
        """Test loading with Path object."""
        # Create test file
        with open(self.test_file, "w") as f:
            json.dump(self.test_data, f)

        result = load_json(self.test_file)
        assert result == self.test_data

    def test_load_json_file_not_found(self):
        """Test loading non-existent file returns default."""
        result = load_json("nonexistent.json")
        assert result is None

        result = load_json("nonexistent.json", default={"default": "value"})
        assert result == {"default": "value"}

    def test_load_json_invalid_json(self):
        """Test loading invalid JSON returns default."""
        # Create file with invalid JSON
        with open(self.test_file, "w") as f:
            f.write("invalid json content")

        result = load_json(self.test_file)
        assert result is None

        result = load_json(self.test_file, default=[])
        assert result == []

    def test_load_json_custom_default(self):
        """Test loading with custom default values."""
        result = load_json("nonexistent.json", default="custom")
        assert result == "custom"

        result = load_json("nonexistent.json", default=123)
        assert result == 123

        result = load_json("nonexistent.json", default=[1, 2, 3])
        assert result == [1, 2, 3]


class TestSaveJson:
    """Test class for save_json function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.json"
        self.test_data = {"key": "value", "number": 42, "nested": {"inner": "data"}}

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_json_success(self):
        """Test successful JSON saving."""
        result = save_json(self.test_data, self.test_file)
        assert result is True

        # Verify file was created and contains correct data
        assert self.test_file.exists()
        with open(self.test_file, "r") as f:
            loaded_data = json.load(f)
        assert loaded_data == self.test_data

    def test_save_json_with_path_object(self):
        """Test saving with Path object."""
        result = save_json(self.test_data, self.test_file)
        assert result is True
        assert self.test_file.exists()

    def test_save_json_create_directories(self):
        """Test saving with directory creation."""
        nested_file = Path(self.temp_dir) / "subdir" / "nested" / "test.json"
        
        result = save_json(self.test_data, nested_file, create_dirs=True)
        assert result is True
        assert nested_file.exists()

        # Verify data
        with open(nested_file, "r") as f:
            loaded_data = json.load(f)
        assert loaded_data == self.test_data

    def test_save_json_no_create_directories(self):
        """Test saving without directory creation fails gracefully."""
        nested_file = Path(self.temp_dir) / "nonexistent" / "test.json"
        
        result = save_json(self.test_data, nested_file, create_dirs=False)
        assert result is False
        assert not nested_file.exists()

    def test_save_json_with_datetime_objects(self):
        """Test saving data with datetime objects (uses default=str)."""
        data_with_datetime = {
            "timestamp": datetime.now(),
            "date": datetime.now().date(),
            "regular": "data"
        }
        
        result = save_json(data_with_datetime, self.test_file)
        assert result is True
        assert self.test_file.exists()

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_save_json_permission_error(self, mock_open):
        """Test saving with permission error."""
        result = save_json(self.test_data, self.test_file)
        assert result is False

    @patch('json.dump', side_effect=TypeError("Not serializable"))
    def test_save_json_serialization_error(self, mock_dump):
        """Test saving with serialization error."""
        with patch('builtins.open', mock_open()):
            result = save_json(self.test_data, self.test_file)
            assert result is False


class TestAppendToJsonArray:
    """Test class for append_to_json_array function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "array.json"

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_append_to_new_file(self):
        """Test appending to non-existent file creates new array."""
        result = append_to_json_array("first_item", self.test_file)
        assert result is True

        # Verify file was created with array
        with open(self.test_file, "r") as f:
            data = json.load(f)
        assert data == ["first_item"]

    def test_append_to_existing_array(self):
        """Test appending to existing array file."""
        # Create initial array
        initial_data = ["item1", "item2"]
        with open(self.test_file, "w") as f:
            json.dump(initial_data, f)

        result = append_to_json_array("item3", self.test_file)
        assert result is True

        # Verify item was appended
        with open(self.test_file, "r") as f:
            data = json.load(f)
        assert data == ["item1", "item2", "item3"]

    def test_append_to_non_array_file(self):
        """Test appending to file containing non-array data."""
        # Create file with object data
        with open(self.test_file, "w") as f:
            json.dump({"key": "value"}, f)

        result = append_to_json_array("new_item", self.test_file)
        assert result is True

        # Verify file was converted to array with new item
        with open(self.test_file, "r") as f:
            data = json.load(f)
        assert data == ["new_item"]

    def test_append_complex_objects(self):
        """Test appending complex objects to array."""
        items = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2", "nested": {"key": "value"}},
            [1, 2, 3]
        ]

        for item in items:
            result = append_to_json_array(item, self.test_file)
            assert result is True

        # Verify all items were appended
        with open(self.test_file, "r") as f:
            data = json.load(f)
        assert data == items

    @patch('backend.systems.shared.utils.json_storage_utils.save_json', return_value=False)
    def test_append_save_failure(self, mock_save):
        """Test handling of save failure."""
        result = append_to_json_array("item", self.test_file)
        assert result is False

    @patch('backend.systems.shared.utils.json_storage_utils.load_json', side_effect=Exception("Load error"))
    def test_append_load_exception(self, mock_load):
        """Test handling of load exception."""
        result = append_to_json_array("item", self.test_file)
        assert result is False


class TestUpdateJsonObject:
    """Test class for update_json_object function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "object.json"

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_update_new_file(self):
        """Test updating non-existent file creates new object."""
        updates = {"key1": "value1", "key2": 42}
        result = update_json_object(updates, self.test_file)
        assert result is True

        # Verify file was created with updates
        with open(self.test_file, "r") as f:
            data = json.load(f)
        assert data == updates

    def test_update_existing_object(self):
        """Test updating existing object file."""
        # Create initial object
        initial_data = {"existing": "data", "key1": "old_value"}
        with open(self.test_file, "w") as f:
            json.dump(initial_data, f)

        updates = {"key1": "new_value", "key2": "added"}
        result = update_json_object(updates, self.test_file)
        assert result is True

        # Verify updates were applied
        with open(self.test_file, "r") as f:
            data = json.load(f)
        expected = {"existing": "data", "key1": "new_value", "key2": "added"}
        assert data == expected

    def test_update_non_object_file(self):
        """Test updating file containing non-object data."""
        # Create file with array data
        with open(self.test_file, "w") as f:
            json.dump(["item1", "item2"], f)

        updates = {"key": "value"}
        result = update_json_object(updates, self.test_file)
        assert result is True

        # Verify file was converted to object with updates
        with open(self.test_file, "r") as f:
            data = json.load(f)
        assert data == updates

    def test_update_nested_objects(self):
        """Test updating with nested objects."""
        initial_data = {"level1": {"level2": {"key": "old"}}}
        with open(self.test_file, "w") as f:
            json.dump(initial_data, f)

        updates = {
            "level1": {"level2": {"key": "new", "added": "value"}},
            "new_key": "new_value"
        }
        result = update_json_object(updates, self.test_file)
        assert result is True

        # Verify updates were applied (note: dict.update replaces nested dicts)
        with open(self.test_file, "r") as f:
            data = json.load(f)
        expected = {
            "level1": {"level2": {"key": "new", "added": "value"}},
            "new_key": "new_value"
        }
        assert data == expected

    @patch('backend.systems.shared.utils.json_storage_utils.save_json', return_value=False)
    def test_update_save_failure(self, mock_save):
        """Test handling of save failure."""
        result = update_json_object({"key": "value"}, self.test_file)
        assert result is False

    @patch('backend.systems.shared.utils.json_storage_utils.load_json', side_effect=Exception("Load error"))
    def test_update_load_exception(self, mock_load):
        """Test handling of load exception."""
        result = update_json_object({"key": "value"}, self.test_file)
        assert result is False


class TestBackupJson:
    """Test class for backup_json function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.json"
        self.test_data = {"key": "value", "number": 42}

        # Create test file
        with open(self.test_file, "w") as f:
            json.dump(self.test_data, f)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_backup_json_default_location(self):
        """Test creating backup in default location (same directory)."""
        result = backup_json(self.test_file)
        assert result is not None
        assert isinstance(result, str)

        # Verify backup file exists
        backup_path = Path(result)
        assert backup_path.exists()
        assert backup_path.parent == self.test_file.parent

        # Verify backup contains correct data
        with open(backup_path, "r") as f:
            backup_data = json.load(f)
        assert backup_data == self.test_data

        # Verify backup filename format
        assert self.test_file.stem in backup_path.name
        assert backup_path.suffix == self.test_file.suffix

    def test_backup_json_custom_directory(self):
        """Test creating backup in custom directory."""
        backup_dir = Path(self.temp_dir) / "backups"
        
        result = backup_json(self.test_file, backup_dir)
        assert result is not None

        # Verify backup file exists in custom directory
        backup_path = Path(result)
        assert backup_path.exists()
        assert backup_path.parent == backup_dir

        # Verify backup contains correct data
        with open(backup_path, "r") as f:
            backup_data = json.load(f)
        assert backup_data == self.test_data

    def test_backup_json_creates_backup_directory(self):
        """Test that backup directory is created if it doesn't exist."""
        backup_dir = Path(self.temp_dir) / "nested" / "backup" / "dir"
        assert not backup_dir.exists()

        result = backup_json(self.test_file, backup_dir)
        assert result is not None

        # Verify directory was created
        assert backup_dir.exists()
        assert backup_dir.is_dir()

        # Verify backup file exists
        backup_path = Path(result)
        assert backup_path.exists()

    def test_backup_json_nonexistent_file(self):
        """Test backing up non-existent file returns None."""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.json"
        
        result = backup_json(nonexistent_file)
        assert result is None

    def test_backup_json_with_path_objects(self):
        """Test backup with Path objects."""
        backup_dir = Path(self.temp_dir) / "backups"
        
        result = backup_json(self.test_file, backup_dir)
        assert result is not None
        assert Path(result).exists()

    @patch('shutil.copy2', side_effect=PermissionError("Permission denied"))
    def test_backup_json_copy_error(self, mock_copy):
        """Test handling of copy error."""
        result = backup_json(self.test_file)
        assert result is None

    @patch('pathlib.Path.mkdir', side_effect=OSError("Cannot create directory"))
    def test_backup_json_mkdir_error(self, mock_mkdir):
        """Test handling of directory creation error."""
        backup_dir = Path(self.temp_dir) / "new_backup_dir"
        result = backup_json(self.test_file, backup_dir)
        assert result is None


class TestMergeJsonFiles:
    """Test class for merge_json_files function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.file1 = Path(self.temp_dir) / "file1.json"
        self.file2 = Path(self.temp_dir) / "file2.json"
        self.file3 = Path(self.temp_dir) / "file3.json"
        self.output_file = Path(self.temp_dir) / "merged.json"

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_merge_json_files_success(self):
        """Test successful merging of JSON files."""
        # Create test files
        data1 = {"key1": "value1", "shared": "from_file1"}
        data2 = {"key2": "value2", "shared": "from_file2"}  # This will override
        data3 = {"key3": "value3", "nested": {"inner": "value"}}

        with open(self.file1, "w") as f:
            json.dump(data1, f)
        with open(self.file2, "w") as f:
            json.dump(data2, f)
        with open(self.file3, "w") as f:
            json.dump(data3, f)

        result = merge_json_files([self.file1, self.file2, self.file3], self.output_file)
        assert result is True

        # Verify merged file
        assert self.output_file.exists()
        with open(self.output_file, "r") as f:
            merged_data = json.load(f)

        expected = {
            "key1": "value1",
            "key2": "value2", 
            "key3": "value3",
            "shared": "from_file2",  # Last file wins
            "nested": {"inner": "value"}
        }
        assert merged_data == expected

    def test_merge_json_files_with_path_objects(self):
        """Test merging with Path objects."""
        data1 = {"key1": "value1"}
        data2 = {"key2": "value2"}

        with open(self.file1, "w") as f:
            json.dump(data1, f)
        with open(self.file2, "w") as f:
            json.dump(data2, f)

        result = merge_json_files([self.file1, self.file2], self.output_file)
        assert result is True
        assert self.output_file.exists()

    def test_merge_json_files_nonexistent_files(self):
        """Test merging with some non-existent files."""
        # Create one valid file
        data1 = {"key1": "value1"}
        with open(self.file1, "w") as f:
            json.dump(data1, f)

        # Include non-existent files
        nonexistent = Path(self.temp_dir) / "nonexistent.json"
        
        result = merge_json_files([self.file1, nonexistent], self.output_file)
        assert result is True

        # Verify only valid data was merged
        with open(self.output_file, "r") as f:
            merged_data = json.load(f)
        assert merged_data == data1

    def test_merge_json_files_non_dict_data(self):
        """Test merging files with non-dictionary data."""
        # Create files with different data types
        with open(self.file1, "w") as f:
            json.dump({"key1": "value1"}, f)  # Valid dict
        with open(self.file2, "w") as f:
            json.dump(["item1", "item2"], f)  # Array - should be ignored
        with open(self.file3, "w") as f:
            json.dump("string_value", f)  # String - should be ignored

        result = merge_json_files([self.file1, self.file2, self.file3], self.output_file)
        assert result is True

        # Verify only dict data was merged
        with open(self.output_file, "r") as f:
            merged_data = json.load(f)
        assert merged_data == {"key1": "value1"}

    def test_merge_json_files_empty_list(self):
        """Test merging empty list of files."""
        result = merge_json_files([], self.output_file)
        assert result is True

        # Verify empty object was created
        with open(self.output_file, "r") as f:
            merged_data = json.load(f)
        assert merged_data == {}

    @patch('backend.systems.shared.utils.json_storage_utils.save_json', return_value=False)
    def test_merge_json_files_save_failure(self, mock_save):
        """Test handling of save failure."""
        # Create test file
        with open(self.file1, "w") as f:
            json.dump({"key": "value"}, f)

        result = merge_json_files([self.file1], self.output_file)
        assert result is False

    @patch('backend.systems.shared.utils.json_storage_utils.load_json', side_effect=Exception("Load error"))
    def test_merge_json_files_load_exception(self, mock_load):
        """Test handling of load exception."""
        result = merge_json_files([self.file1], self.output_file)
        assert result is False


class TestValidateJsonSchema:
    """Test class for validate_json_schema function."""

    def test_validate_object_type_success(self):
        """Test successful object type validation."""
        data = {"key": "value", "number": 42}
        schema = {"type": "object"}
        
        errors = validate_json_schema(data, schema)
        assert errors == []

    def test_validate_object_type_failure(self):
        """Test failed object type validation."""
        data = ["item1", "item2"]
        schema = {"type": "object"}
        
        errors = validate_json_schema(data, schema)
        assert len(errors) == 1
        assert "Expected object, got list" in errors[0]

    def test_validate_array_type_success(self):
        """Test successful array type validation."""
        data = ["item1", "item2", 42]
        schema = {"type": "array"}
        
        errors = validate_json_schema(data, schema)
        assert errors == []

    def test_validate_array_type_failure(self):
        """Test failed array type validation."""
        data = {"key": "value"}
        schema = {"type": "array"}
        
        errors = validate_json_schema(data, schema)
        assert len(errors) == 1
        assert "Expected array, got dict" in errors[0]

    def test_validate_string_type_success(self):
        """Test successful string type validation."""
        data = "test string"
        schema = {"type": "string"}
        
        errors = validate_json_schema(data, schema)
        assert errors == []

    def test_validate_string_type_failure(self):
        """Test failed string type validation."""
        data = 42
        schema = {"type": "string"}
        
        errors = validate_json_schema(data, schema)
        assert len(errors) == 1
        assert "Expected string, got int" in errors[0]

    def test_validate_number_type_success_int(self):
        """Test successful number type validation with integer."""
        data = 42
        schema = {"type": "number"}
        
        errors = validate_json_schema(data, schema)
        assert errors == []

    def test_validate_number_type_success_float(self):
        """Test successful number type validation with float."""
        data = 3.14
        schema = {"type": "number"}
        
        errors = validate_json_schema(data, schema)
        assert errors == []

    def test_validate_number_type_failure(self):
        """Test failed number type validation."""
        data = "not a number"
        schema = {"type": "number"}
        
        errors = validate_json_schema(data, schema)
        assert len(errors) == 1
        assert "Expected number, got str" in errors[0]

    def test_validate_no_type_specified(self):
        """Test validation with no type specified in schema."""
        data = {"any": "data"}
        schema = {"other_property": "value"}
        
        errors = validate_json_schema(data, schema)
        assert errors == []

    def test_validate_empty_schema(self):
        """Test validation with empty schema."""
        data = {"any": "data"}
        schema = {}
        
        errors = validate_json_schema(data, schema)
        assert errors == []

    def test_validate_unknown_type(self):
        """Test validation with unknown type (should not cause errors)."""
        data = {"key": "value"}
        schema = {"type": "unknown_type"}
        
        errors = validate_json_schema(data, schema)
        assert errors == []


class TestCleanupOldBackups:
    """Test class for cleanup_old_backups function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.temp_dir) / "backups"
        self.backup_dir.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cleanup_old_backups_success(self):
        """Test successful cleanup of old backup files."""
        # Create 7 backup files with different timestamps
        import time
        for i in range(7):
            backup_file = self.backup_dir / f"backup_{i:02d}.json"
            backup_file.write_text(f'{{"backup": {i}}}')
            time.sleep(0.01)  # Small delay to ensure different modification times

        # Keep only 3 most recent
        deleted_count = cleanup_old_backups(self.backup_dir, "backup_*.json", keep_count=3)
        assert deleted_count == 4

        # Verify only 3 files remain
        remaining_files = list(self.backup_dir.glob("backup_*.json"))
        assert len(remaining_files) == 3

        # Verify the most recent files were kept
        remaining_names = sorted([f.name for f in remaining_files])
        expected_names = ["backup_04.json", "backup_05.json", "backup_06.json"]
        assert remaining_names == expected_names

    def test_cleanup_old_backups_fewer_than_keep_count(self):
        """Test cleanup when fewer files exist than keep_count."""
        # Create only 2 backup files
        for i in range(2):
            backup_file = self.backup_dir / f"backup_{i}.json"
            backup_file.write_text(f'{{"backup": {i}}}')

        # Try to keep 5 files
        deleted_count = cleanup_old_backups(self.backup_dir, "backup_*.json", keep_count=5)
        assert deleted_count == 0

        # Verify all files remain
        remaining_files = list(self.backup_dir.glob("backup_*.json"))
        assert len(remaining_files) == 2

    def test_cleanup_old_backups_exact_keep_count(self):
        """Test cleanup when file count equals keep_count."""
        # Create exactly 3 backup files
        for i in range(3):
            backup_file = self.backup_dir / f"backup_{i}.json"
            backup_file.write_text(f'{{"backup": {i}}}')

        # Keep exactly 3 files
        deleted_count = cleanup_old_backups(self.backup_dir, "backup_*.json", keep_count=3)
        assert deleted_count == 0

        # Verify all files remain
        remaining_files = list(self.backup_dir.glob("backup_*.json"))
        assert len(remaining_files) == 3

    def test_cleanup_old_backups_no_matching_files(self):
        """Test cleanup with no matching files."""
        # Create files that don't match pattern
        for i in range(3):
            other_file = self.backup_dir / f"other_{i}.txt"
            other_file.write_text(f"other {i}")

        deleted_count = cleanup_old_backups(self.backup_dir, "backup_*.json", keep_count=2)
        assert deleted_count == 0

        # Verify other files remain untouched
        other_files = list(self.backup_dir.glob("other_*.txt"))
        assert len(other_files) == 3

    def test_cleanup_old_backups_nonexistent_directory(self):
        """Test cleanup with non-existent directory."""
        nonexistent_dir = Path(self.temp_dir) / "nonexistent"
        
        deleted_count = cleanup_old_backups(nonexistent_dir, "*.json", keep_count=3)
        assert deleted_count == 0

    def test_cleanup_old_backups_with_path_object(self):
        """Test cleanup with Path object."""
        # Create backup files
        for i in range(5):
            backup_file = self.backup_dir / f"backup_{i}.json"
            backup_file.write_text(f'{{"backup": {i}}}')

        deleted_count = cleanup_old_backups(self.backup_dir, "backup_*.json", keep_count=2)
        assert deleted_count == 3

        remaining_files = list(self.backup_dir.glob("backup_*.json"))
        assert len(remaining_files) == 2

    @patch('pathlib.Path.unlink', side_effect=PermissionError("Permission denied"))
    def test_cleanup_old_backups_delete_error(self, mock_unlink):
        """Test cleanup with file deletion errors."""
        # Create backup files
        for i in range(5):
            backup_file = self.backup_dir / f"backup_{i}.json"
            backup_file.write_text(f'{{"backup": {i}}}')

        # Should handle deletion errors gracefully
        deleted_count = cleanup_old_backups(self.backup_dir, "backup_*.json", keep_count=2)
        assert deleted_count == 0  # No files actually deleted due to error

    @patch('pathlib.Path.glob', side_effect=OSError("Glob error"))
    def test_cleanup_old_backups_glob_error(self, mock_glob):
        """Test cleanup with glob error."""
        deleted_count = cleanup_old_backups(self.backup_dir, "*.json", keep_count=3)
        assert deleted_count == 0


class TestJsonStorageUtilsIntegration:
    """Integration tests for JSON storage utilities."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_workflow_integration(self):
        """Test a complete workflow using multiple functions."""
        # 1. Create initial data file
        data_file = Path(self.temp_dir) / "data.json"
        initial_data = {"version": 1, "items": []}
        
        result = save_json(initial_data, data_file)
        assert result is True

        # 2. Create backup
        backup_path = backup_json(data_file)
        assert backup_path is not None
        assert Path(backup_path).exists()

        # 3. Append items to array (this converts the object to an array)
        for i in range(3):
            item = {"id": i, "name": f"Item {i}"}
            result = append_to_json_array(item, data_file)
            assert result is True

        # 4. Update object with metadata (this converts the array back to an object)
        metadata = {"last_updated": datetime.now().isoformat(), "count": 3}
        result = update_json_object(metadata, data_file)
        assert result is True

        # 5. Verify final state (note: the array operations converted the file to array, then back to object)
        final_data = load_json(data_file)
        assert "last_updated" in final_data
        assert final_data["count"] == 3
        # The original version and items are lost due to the array conversion

        # 6. Validate schema
        schema = {"type": "object"}
        errors = validate_json_schema(final_data, schema)
        assert errors == []

    def test_merge_and_backup_workflow(self):
        """Test merging files and creating backups."""
        # Create multiple data files
        file1 = Path(self.temp_dir) / "config1.json"
        file2 = Path(self.temp_dir) / "config2.json"
        merged_file = Path(self.temp_dir) / "merged_config.json"

        data1 = {"database": {"host": "localhost", "port": 5432}}
        data2 = {"cache": {"redis_url": "redis://localhost"}, "debug": True}

        save_json(data1, file1)
        save_json(data2, file2)

        # Merge files
        result = merge_json_files([file1, file2], merged_file)
        assert result is True

        # Create backup of merged file
        backup_path = backup_json(merged_file)
        assert backup_path is not None

        # Verify merged content
        merged_data = load_json(merged_file)
        assert "database" in merged_data
        assert "cache" in merged_data
        assert merged_data["debug"] is True

        # Verify backup content matches
        backup_data = load_json(backup_path)
        assert backup_data == merged_data 