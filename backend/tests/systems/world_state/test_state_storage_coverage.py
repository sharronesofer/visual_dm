"""
Coverage-focused tests for backend.systems.world_state.persistence.state_storage

Targeting specific uncovered lines to boost coverage efficiently.
"""

import pytest
import json
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock

# Import the module being tested
try: pass
    from backend.systems.world_state.persistence.state_storage import StateStorage
    from backend.systems.world_state.consolidated_manager import (
        StateVariable, StateChangeRecord, WorldStateSnapshot
    )
except ImportError as e: pass
    pytest.skip(f"Could not import state_storage: {e}", allow_module_level=True)


@pytest.fixture
def temp_storage_dir(): pass
    """Create a temporary directory for storage tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def state_storage(temp_storage_dir): pass
    """Create a StateStorage instance with temporary directory."""
    return StateStorage(base_path=temp_storage_dir)


@pytest.fixture
def sample_state_variable(): pass
    """Create a sample state variable for testing."""
    return StateVariable(
        key="test_key",
        value="test_value",
        category="test_category",
        last_updated=datetime.utcnow()
    )


@pytest.fixture
def sample_change_record(): pass
    """Create a sample change record for testing."""
    return StateChangeRecord(
        timestamp=datetime.utcnow(),
        key="test_key",
        old_value="old_value",
        new_value="new_value",
        category="test_category",
        source="test_source"
    )


@pytest.fixture
def sample_snapshot(): pass
    """Create a sample world state snapshot for testing."""
    return WorldStateSnapshot(
        timestamp=datetime.utcnow(),
        version=1,
        variables={"test_key": "test_value"},
        metadata={"source": "test"}
    )


class TestStateStorageErrorHandling: pass
    """Test error handling and edge cases in StateStorage."""

    def test_load_state_corrupted_file_with_backup(self, state_storage, sample_state_variable): pass
        """Test loading state when main file is corrupted but backup exists."""
        # Create a working backup first
        variables = {"test_key": sample_state_variable}
        state_storage.save_state(variables)
        
        # Now corrupt the main file
        state_file = Path(state_storage.base_path) / "state" / "state.json"
        with open(state_file, "w") as f: pass
            f.write("corrupted json content {")
        
        # Mock _restore_from_backup to return True
        with patch.object(state_storage, '_restore_from_backup', return_value=True): pass
            # This should trigger the backup restoration code path
            result = state_storage.load_state()
            # Since we're mocking the restore, it should call load_state again
            assert isinstance(result, dict)

    def test_load_state_corrupted_file_no_backup(self, state_storage): pass
        """Test loading state when main file is corrupted and no backup."""
        # Create a corrupted file
        state_storage._ensure_directories()
        state_file = Path(state_storage.base_path) / "state" / "state.json"
        with open(state_file, "w") as f: pass
            f.write("corrupted json content {")
        
        # Mock _restore_from_backup to return False
        with patch.object(state_storage, '_restore_from_backup', return_value=False): pass
            result = state_storage.load_state()
            assert result == {}

    def test_save_history_error_handling(self, state_storage, sample_change_record): pass
        """Test save_history error handling."""
        history = {"test_key": [sample_change_record]}
        
        # Mock file operations to raise an exception
        with patch("builtins.open", side_effect=IOError("Disk full")): pass
            result = state_storage.save_history(history)
            assert result is False

    def test_load_history_no_file(self, state_storage): pass
        """Test loading history when no history file exists."""
        result = state_storage.load_history()
        assert result == {}

    def test_load_history_corrupted_file(self, state_storage): pass
        """Test loading history when file is corrupted."""
        # Create a corrupted history file
        state_storage._ensure_directories()
        history_file = Path(state_storage.base_path) / "history" / "state_history.json"
        with open(history_file, "w") as f: pass
            f.write("corrupted json {")
        
        result = state_storage.load_history()
        assert result == {}

    def test_save_snapshot_error_handling(self, state_storage, sample_snapshot): pass
        """Test save_snapshot error handling."""
        # Mock file operations to raise an exception
        with patch("builtins.open", side_effect=IOError("Disk full")): pass
            result = state_storage.save_snapshot(sample_snapshot)
            assert result is False

    def test_load_snapshot_no_directory(self, state_storage): pass
        """Test loading snapshot when snapshots directory doesn't exist."""
        result = state_storage.load_snapshot()
        assert result is None

    def test_load_snapshot_no_files(self, state_storage): pass
        """Test loading snapshot when no snapshot files exist."""
        # Create empty snapshots directory
        state_storage._ensure_directories()
        result = state_storage.load_snapshot()
        assert result is None

    def test_load_snapshot_by_version_not_found(self, state_storage): pass
        """Test loading snapshot by version when version doesn't exist."""
        state_storage._ensure_directories()
        result = state_storage.load_snapshot(version=999)
        assert result is None

    def test_load_snapshot_by_timestamp_same_day(self, state_storage, sample_snapshot): pass
        """Test loading snapshot by timestamp when files exist from same day."""
        # Save a snapshot first
        state_storage.save_snapshot(sample_snapshot)
        
        # Try to load by timestamp from same day
        result = state_storage.load_snapshot(timestamp=sample_snapshot.timestamp)
        assert result is not None

    def test_load_snapshot_by_timestamp_different_day(self, state_storage, sample_snapshot): pass
        """Test loading snapshot by timestamp when no files from same day."""
        # Save a snapshot first
        state_storage.save_snapshot(sample_snapshot)
        
        # Try to load by timestamp from different day
        different_day = sample_snapshot.timestamp + timedelta(days=1)
        result = state_storage.load_snapshot(timestamp=different_day)
        assert result is not None

    def test_delete_snapshot_not_found(self, state_storage): pass
        """Test deleting a snapshot that doesn't exist."""
        result = state_storage.delete_snapshot(version=999)
        assert result is False

    def test_delete_snapshot_error_handling(self, state_storage, sample_snapshot): pass
        """Test delete_snapshot error handling."""
        # Save a snapshot first
        state_storage.save_snapshot(sample_snapshot)
        
        # Mock file operations to raise an exception
        with patch("pathlib.Path.unlink", side_effect=OSError("Permission denied")): pass
            result = state_storage.delete_snapshot(version=1)
            assert result is False

    def test_create_backup_error_handling(self, state_storage): pass
        """Test _create_backup error handling."""
        # Mock file operations to raise an exception
        with patch("shutil.copy2", side_effect=IOError("Disk full")): pass
            result = state_storage._create_backup()
            assert result is False

    def test_restore_from_backup_no_backup(self, state_storage): pass
        """Test _restore_from_backup when no backup exists."""
        result = state_storage._restore_from_backup()
        assert result is False

    def test_restore_from_backup_error_handling(self, state_storage): pass
        """Test _restore_from_backup error handling."""
        # Create a backup file
        state_storage._ensure_directories()
        backup_file = Path(state_storage.base_path) / "state" / "state.json.backup"
        backup_file.touch()
        
        # Mock file operations to raise an exception
        with patch("shutil.copy2", side_effect=IOError("Permission denied")): pass
            result = state_storage._restore_from_backup()
            assert result is False


class TestStateStorageMigration: pass
    """Test migration functionality in StateStorage."""

    def test_load_history_with_old_schema(self, state_storage, sample_change_record): pass
        """Test loading history with old schema version."""
        # Create a history file with old schema
        state_storage._ensure_directories()
        history_file = Path(state_storage.base_path) / "history" / "state_history.json"
        
        old_data = {
            "schema_version": 1,  # Older than current
            "timestamp": datetime.utcnow().isoformat(),
            "history": {
                "test_key": [{
                    "timestamp": sample_change_record.timestamp.isoformat(),
                    "key": sample_change_record.key,
                    "old_value": sample_change_record.old_value,
                    "new_value": sample_change_record.new_value,
                    "category": sample_change_record.category,
                    "source": sample_change_record.source
                }]
            }
        }
        
        with open(history_file, "w") as f: pass
            json.dump(old_data, f)
        
        # Mock _migrate_history_data to return modified data
        with patch.object(state_storage, '_migrate_history_data', return_value=old_data): pass
            result = state_storage.load_history()
            assert isinstance(result, dict)

    def test_load_state_with_old_schema(self, state_storage, sample_state_variable): pass
        """Test loading state with old schema version."""
        # Create a state file with old schema
        state_storage._ensure_directories()
        state_file = Path(state_storage.base_path) / "state" / "state.json"
        
        old_data = {
            "schema_version": 1,  # Older than current
            "timestamp": datetime.utcnow().isoformat(),
            "variables": {
                "test_key": {
                    "_type": "StateVariable",
                    "key": sample_state_variable.key,
                    "value": sample_state_variable.value,
                    "category": sample_state_variable.category,
                    "last_updated": sample_state_variable.last_updated.isoformat()
                }
            }
        }
        
        with open(state_file, "w") as f: pass
            json.dump(old_data, f)
        
        # Mock _migrate_state_data to return modified data
        with patch.object(state_storage, '_migrate_state_data', return_value=old_data): pass
            result = state_storage.load_state()
            assert isinstance(result, dict)

    def test_load_snapshot_with_old_schema(self, state_storage, sample_snapshot): pass
        """Test loading snapshot with old schema version."""
        # Create a snapshot file with old schema
        state_storage._ensure_directories()
        snapshot_file = Path(state_storage.base_path) / "snapshots" / "snapshot_v1_20240101_120000.json"
        
        old_data = {
            "schema_version": 1,  # Older than current
            "timestamp": sample_snapshot.timestamp.isoformat(),
            "version": sample_snapshot.version,
            "metadata": sample_snapshot.metadata,
            "variables": sample_snapshot.variables
        }
        
        with open(snapshot_file, "w") as f: pass
            json.dump(old_data, f)
        
        # Mock _migrate_snapshot_data to return modified data
        with patch.object(state_storage, '_migrate_snapshot_data', return_value=old_data): pass
            result = state_storage.load_snapshot(version=1)
            assert result is not None


class TestStateStorageSerializationEdgeCases: pass
    """Test serialization edge cases."""

    def test_save_snapshot_with_serialized_variables(self, state_storage): pass
        """Test saving snapshot when variables are already serialized."""
        # Create a snapshot with pre-serialized variables
        snapshot = WorldStateSnapshot(
            timestamp=datetime.utcnow(),
            version=1,
            variables={"test_key": {"_type": "StateVariable", "value": "test"}},
            metadata={"source": "test"}
        )
        
        result = state_storage.save_snapshot(snapshot)
        assert result is True

    def test_deserialize_variable_missing_fields(self, state_storage): pass
        """Test deserializing variable with missing fields."""
        # Test with minimal data
        data = {"_type": "StateVariable", "key": "test_key"}
        
        result = state_storage._deserialize_variable(data)
        assert result.key == "test_key"
        # Other fields should have defaults

    def test_deserialize_change_record_with_none_values(self, state_storage): pass
        """Test deserializing change record with None values."""
        data = {
            "_type": "StateChangeRecord",
            "timestamp": datetime.utcnow().isoformat(),
            "key": "test_key",
            "old_value": None,
            "new_value": "new_value",
            "category": "test_category",
            "source": "test_source"
        }
        
        result = state_storage._deserialize_change_record(data)
        assert result.old_value is None
        assert result.new_value == "new_value" 