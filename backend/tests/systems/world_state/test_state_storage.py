from typing import Type
from typing import List
"""
Tests for backend.systems.world_state.persistence.state_storage

Comprehensive tests for the StateStorage class including file operations,
serialization, backups, and migration functionality.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, mock_open
import os
import uuid

# Import the module being tested
try: pass
    from backend.systems.world_state.persistence.state_storage import StateStorage
    from backend.systems.world_state.consolidated_state_models import (
        StateVariable,
        StateChangeRecord,
        StateChangeType,
        StateCategory,
        WorldRegion,
        WorldStateSnapshot
    )
except ImportError as e: pass
    pytest.skip(f"Could not import required modules: {e}", allow_module_level=True)


@pytest.fixture
def temp_storage_dir(): pass
    """Create a temporary directory for storage tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def storage(temp_storage_dir): pass
    """Create a StateStorage instance with temporary directory."""
    return StateStorage(base_path=temp_storage_dir)


@pytest.fixture
def sample_variables(): pass
    """Create sample state variables for testing."""
    return {
        "test.var1": StateVariable(
            key="test.var1",
            value="value1",
            category=StateCategory.OTHER,
            region=WorldRegion.GLOBAL,
            tags=["test", "sample"]
        ),
        "test.var2": StateVariable(
            key="test.var2",
            value=42,
            category=StateCategory.ECONOMIC,
            region=WorldRegion.NORTHERN,
            tags=["test", "number"]
        )
    }


@pytest.fixture
def sample_history(): pass
    """Create sample history records for testing."""
    return {
        "test.var1": [
            StateChangeRecord(
                state_key="test.var1",
                old_value=None,
                new_value="value1",
                change_type=StateChangeType.CREATED,
                timestamp=datetime.utcnow(),
                change_reason="Initial creation",
                version=1
            ),
            StateChangeRecord(
                state_key="test.var1",
                old_value="value1",
                new_value="updated_value1",
                change_type=StateChangeType.UPDATED,
                timestamp=datetime.utcnow(),
                change_reason="Updated value",
                version=2
            )
        ]
    }


@pytest.fixture
def sample_snapshot(): pass
    """Create a sample snapshot for testing."""
    return WorldStateSnapshot(
        version=1,
        timestamp=datetime.utcnow(),
        variables={"test.key": "test_value"},
        metadata={"purpose": "testing"}
    )


class TestStateStorageInitialization: pass
    """Test StateStorage initialization and directory setup."""
    
    def test_init_with_custom_path(self, temp_storage_dir): pass
        """Test initialization with custom base path."""
        storage = StateStorage(base_path=temp_storage_dir)
        
        assert storage.base_path == Path(temp_storage_dir)
        assert storage.current_schema_version == 1
        
        # Check that directories were created
        assert (storage.base_path / "current").exists()
        assert (storage.base_path / "snapshots").exists()
        assert (storage.base_path / "backups").exists()
        assert (storage.base_path / "history").exists()
    
    def test_init_with_default_path(self): pass
        """Test initialization with custom temporary path."""
        with tempfile.TemporaryDirectory() as temp_dir: pass
            with patch.dict(os.environ, {"PROJECT_ROOT": temp_dir}): pass
                storage = StateStorage()
                
                expected_path = Path(temp_dir) / "data" / "world_state"
                assert storage.base_path == expected_path
    
    def test_init_without_project_root(self): pass
        """Test initialization with custom temporary path when no PROJECT_ROOT."""
        with tempfile.TemporaryDirectory() as temp_dir: pass
            with patch.dict(os.environ, {}, clear=True): pass
                with patch('os.getcwd', return_value=temp_dir): pass
                    storage = StateStorage()
                    
                    expected_path = Path(temp_dir) / "data" / "world_state"
                    assert storage.base_path == expected_path


class TestStateSaving: pass
    """Test state saving functionality."""
    
    def test_save_state_success(self, storage, sample_variables): pass
        """Test successful state saving."""
        result = storage.save_state(sample_variables)
        
        assert result is True
        
        # Check that state file was created
        state_file = storage.base_path / "current" / "state.json"
        assert state_file.exists()
        
        # Verify file contents
        with open(state_file, 'r') as f: pass
            data = json.load(f)
        
        assert data["schema_version"] == 1
        assert "timestamp" in data
        assert "variables" in data
        assert len(data["variables"]) == 2
        assert "test.var1" in data["variables"]
        assert "test.var2" in data["variables"]
    
    def test_save_state_creates_backup(self, storage, sample_variables): pass
        """Test that saving state creates a backup of existing state."""
        # Save initial state
        storage.save_state(sample_variables)
        
        # Modify and save again
        sample_variables["test.var3"] = StateVariable(
            key="test.var3",
            value="new_value",
            category=StateCategory.OTHER,
            region=WorldRegion.GLOBAL
        )
        
        with patch.object(storage, '_create_backup', return_value=True) as mock_backup: pass
            storage.save_state(sample_variables)
            mock_backup.assert_called_once()
    
    def test_save_state_handles_serialization_error(self, storage): pass
        """Test handling of serialization errors during save."""
        # Create a variable with non-serializable data
        bad_variables = {
            "bad.var": StateVariable(
                key="bad.var",
                value=lambda x: x,  # Non-serializable function
                category=StateCategory.OTHER,
                region=WorldRegion.GLOBAL
            )
        }
        
        with patch('json.dump', side_effect=TypeError("Not serializable")): pass
            result = storage.save_state(bad_variables)
            assert result is False
    
    def test_save_state_handles_file_error(self, storage, sample_variables): pass
        """Test handling of file I/O errors during save."""
        with patch('builtins.open', side_effect=IOError("File error")): pass
            result = storage.save_state(sample_variables)
            assert result is False


class TestStateLoading: pass
    """Test state loading functionality."""
    
    def test_load_state_success(self, storage, sample_variables): pass
        """Test successful state loading."""
        # Save state first
        storage.save_state(sample_variables)
        
        # Load state
        loaded_variables = storage.load_state()
        
        assert len(loaded_variables) == 2
        assert "test.var1" in loaded_variables
        assert "test.var2" in loaded_variables
        
        # Verify variable properties
        var1 = loaded_variables["test.var1"]
        assert var1.key == "test.var1"
        assert var1.value == "value1"
        assert var1.category == StateCategory.OTHER
        assert var1.region == WorldRegion.GLOBAL
    
    def test_load_state_no_file(self, storage): pass
        """Test loading state when no file exists."""
        loaded_variables = storage.load_state()
        
        assert loaded_variables == {}
    
    def test_load_state_corrupted_file(self, storage): pass
        """Test loading state from corrupted file."""
        # Create corrupted state file
        state_file = storage.base_path / "current" / "state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, 'w') as f: pass
            f.write("invalid json content")
        
        with patch.object(storage, '_restore_from_backup', return_value=False): pass
            loaded_variables = storage.load_state()
            assert loaded_variables == {}
    
    def test_load_state_with_migration(self, storage, sample_variables): pass
        """Test loading state that requires migration."""
        # Save state first
        storage.save_state(sample_variables)
        
        # Modify the saved file to have an older schema version
        state_file = storage.base_path / "current" / "state.json"
        with open(state_file, 'r') as f: pass
            data = json.load(f)
        
        data["schema_version"] = 0  # Older version
        
        with open(state_file, 'w') as f: pass
            json.dump(data, f)
        
        with patch.object(storage, '_migrate_state_data', return_value=data) as mock_migrate: pass
            loaded_variables = storage.load_state()
            mock_migrate.assert_called_once()
            assert len(loaded_variables) == 2


class TestHistorySaving: pass
    """Test history saving functionality."""
    
    def test_save_history_success(self, storage, sample_history): pass
        """Test successful history saving."""
        result = storage.save_history(sample_history)
        
        assert result is True
        
        # Check that history file was created
        history_file = storage.base_path / "history" / "state_history.json"
        assert history_file.exists()
        
        # Verify file contents
        with open(history_file, 'r') as f: pass
            data = json.load(f)
        
        assert data["schema_version"] == 1
        assert "timestamp" in data
        assert "history" in data
        assert "test.var1" in data["history"]
        assert len(data["history"]["test.var1"]) == 2
    
    def test_save_history_handles_error(self, storage, sample_history): pass
        """Test handling of errors during history save."""
        with patch('builtins.open', side_effect=IOError("File error")): pass
            result = storage.save_history(sample_history)
            assert result is False


class TestHistoryLoading: pass
    """Test history loading functionality."""
    
    def test_load_history_success(self, storage, sample_history): pass
        """Test successful history loading."""
        # Save history first
        storage.save_history(sample_history)
        
        # Load history
        loaded_history = storage.load_history()
        
        assert "test.var1" in loaded_history
        assert len(loaded_history["test.var1"]) == 2
        
        # Verify record properties
        record = loaded_history["test.var1"][0]
        assert record.state_key == "test.var1"
        assert record.old_value is None
        assert record.new_value == "value1"
        assert record.change_type == StateChangeType.CREATED
    
    def test_load_history_no_file(self, storage): pass
        """Test loading history when no file exists."""
        loaded_history = storage.load_history()
        
        assert loaded_history == {}
    
    def test_load_history_with_migration(self, storage, sample_history): pass
        """Test loading history that requires migration."""
        # Save history first
        storage.save_history(sample_history)
        
        # Modify the saved file to have an older schema version
        history_file = storage.base_path / "history" / "state_history.json"
        with open(history_file, 'r') as f: pass
            data = json.load(f)
        
        data["schema_version"] = 0  # Older version
        
        with open(history_file, 'w') as f: pass
            json.dump(data, f)
        
        with patch.object(storage, '_migrate_history_data', return_value=data) as mock_migrate: pass
            loaded_history = storage.load_history()
            mock_migrate.assert_called_once()
            assert "test.var1" in loaded_history


class TestSnapshotOperations: pass
    """Test snapshot save/load/list/delete operations."""
    
    def test_save_snapshot_success(self, storage, sample_snapshot): pass
        """Test successful snapshot saving."""
        result = storage.save_snapshot(sample_snapshot)
        
        assert result is True
        
        # Check that snapshot file was created (with the actual filename format)
        snapshot_dir = storage.base_path / "snapshots"
        snapshot_files = list(snapshot_dir.glob(f"snapshot_v{sample_snapshot.version}_*.json"))
        assert len(snapshot_files) > 0
    
    def test_save_snapshot_handles_error(self, storage, sample_snapshot): pass
        """Test handling of errors during snapshot save."""
        with patch('builtins.open', side_effect=IOError("File error")): pass
            result = storage.save_snapshot(sample_snapshot)
            assert result is False
    
    def test_load_snapshot_by_version(self, storage, sample_snapshot): pass
        """Test loading snapshot by version."""
        # Save snapshot first
        storage.save_snapshot(sample_snapshot)
        
        # Load by version
        loaded_snapshot = storage.load_snapshot(version=sample_snapshot.version)
        
        assert loaded_snapshot is not None
        assert loaded_snapshot.version == sample_snapshot.version
        assert loaded_snapshot.variables == sample_snapshot.variables
    
    def test_load_snapshot_by_timestamp(self, storage, sample_snapshot): pass
        """Test loading snapshot by timestamp."""
        # Save snapshot first
        storage.save_snapshot(sample_snapshot)
        
        # Load by timestamp
        loaded_snapshot = storage.load_snapshot(timestamp=sample_snapshot.timestamp)
        
        assert loaded_snapshot is not None
        assert loaded_snapshot.version == sample_snapshot.version
    
    def test_load_snapshot_latest(self, storage): pass
        """Test loading latest snapshot."""
        # Create multiple snapshots
        for i in range(3): pass
            snapshot = WorldStateSnapshot(
                version=i + 1,
                timestamp=datetime.utcnow() + timedelta(seconds=i),
                variables={"key": f"value{i + 1}"}
            )
            storage.save_snapshot(snapshot)
        
        # Load latest (no parameters)
        loaded_snapshot = storage.load_snapshot()
        
        assert loaded_snapshot is not None
        assert loaded_snapshot.version == 3  # Latest version
    
    def test_load_snapshot_not_found(self, storage): pass
        """Test loading non-existent snapshot."""
        loaded_snapshot = storage.load_snapshot(version=999)
        
        assert loaded_snapshot is None
    
    def test_list_snapshots(self, storage): pass
        """Test listing snapshots."""
        # Create multiple snapshots
        for i in range(3): pass
            snapshot = WorldStateSnapshot(
                version=i + 1,
                timestamp=datetime.utcnow() + timedelta(seconds=i),
                variables={"key": f"value{i + 1}"}
            )
            storage.save_snapshot(snapshot)
        
        # List snapshots
        snapshots = storage.list_snapshots()
        
        assert len(snapshots) == 3
        assert all("version" in s for s in snapshots)
        assert all("timestamp" in s for s in snapshots)
        assert all("metadata" in s for s in snapshots)  # Changed from "variables" to "metadata"
        assert all("variable_count" in s for s in snapshots)  # This is what's actually returned
    
    def test_delete_snapshot_success(self, storage, sample_snapshot): pass
        """Test successful snapshot deletion."""
        # Save snapshot first
        storage.save_snapshot(sample_snapshot)
        
        # Verify it exists
        assert storage.load_snapshot(version=sample_snapshot.version) is not None
        
        # Delete it
        result = storage.delete_snapshot(sample_snapshot.version)
        
        assert result is True
        assert storage.load_snapshot(version=sample_snapshot.version) is None
    
    def test_delete_snapshot_not_found(self, storage): pass
        """Test deleting non-existent snapshot."""
        result = storage.delete_snapshot(999)
        
        assert result is False


class TestBackupOperations: pass
    """Test backup creation and restoration."""
    
    def test_create_backup_success(self, storage, sample_variables): pass
        """Test successful backup creation."""
        # Save initial state
        storage.save_state(sample_variables)
        
        # Create backup
        result = storage._create_backup()
        
        assert result is True
        
        # Check that backup directory was created
        backup_dirs = list((storage.base_path / "backups").glob("*"))
        backup_dirs = [d for d in backup_dirs if d.is_dir()]
        assert len(backup_dirs) > 0
        
        # Check that the backup contains the state file
        latest_backup = max(backup_dirs, key=lambda d: d.name)
        backup_state_file = latest_backup / "state.json"
        assert backup_state_file.exists()
    
    def test_create_backup_no_current_state(self, storage): pass
        """Test backup creation when no current state exists."""
        result = storage._create_backup()
        
        assert result is False  # Should fail when no current state exists
    
    def test_restore_from_backup_success(self, storage, sample_variables): pass
        """Test successful backup restoration."""
        # Save state and create backup
        storage.save_state(sample_variables)
        storage._create_backup()
        
        # Corrupt current state
        state_file = storage.base_path / "current" / "state.json"
        with open(state_file, 'w') as f: pass
            f.write("corrupted data")
        
        # Restore from backup
        result = storage._restore_from_backup()
        
        assert result is True
        
        # Verify state was restored
        loaded_variables = storage.load_state()
        assert len(loaded_variables) == 2
    
    def test_restore_from_backup_no_backups(self, storage): pass
        """Test backup restoration when no backups exist."""
        result = storage._restore_from_backup()
        
        assert result is False


class TestSerialization: pass
    """Test serialization and deserialization methods."""
    
    def test_serialize_variable(self, storage): pass
        """Test variable serialization."""
        variable = StateVariable(
            key="test.key",
            value="test_value",
            category=StateCategory.POLITICAL,
            region=WorldRegion.EASTERN,
            tags=["test", "serialize"]
        )
        
        # Test the serialization directly - the getattr handles missing entity_id
        serialized = storage._serialize_variable(variable)
        
        assert serialized["key"] == "test.key"
        assert serialized["value"] == "test_value"
        assert serialized["category"] == "POLITICAL"  # Uses .name
        assert serialized["region"] == "EASTERN"      # Uses .name
        assert serialized["tags"] == ["test", "serialize"]
        assert serialized["entity_id"] is None  # Should be None due to getattr default
    
    def test_deserialize_variable(self, storage): pass
        """Test variable deserialization."""
        data = {
            "key": "test.key",
            "value": "test_value",
            "category": "POLITICAL",
            "region": "EASTERN",
            "tags": ["test", "deserialize"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "entity_id": None
        }
        
        variable = storage._deserialize_variable(data)
        
        assert variable.key == "test.key"
        assert variable.value == "test_value"
        assert variable.category == StateCategory.POLITICAL
        assert variable.region == WorldRegion.EASTERN
        assert variable.tags == ["test", "deserialize"]
    
    def test_serialize_change_record(self, storage): pass
        """Test change record serialization."""
        record = StateChangeRecord(
            state_key="test.key",
            old_value="old",
            new_value="new",
            change_type=StateChangeType.UPDATED,
            timestamp=datetime.utcnow(),
            change_reason="Test update",
            version=1
        )
        
        serialized = storage._serialize_change_record(record)
        
        assert serialized["key"] == "test.key"
        assert serialized["old_value"] == "old"
        assert serialized["new_value"] == "new"
        assert serialized["change_type"] == "UPDATED"  # Uses .name
        assert serialized["change_reason"] == "Test update"
        assert "timestamp" in serialized
    
    def test_deserialize_change_record(self, storage): pass
        """Test change record deserialization."""
        data = {
            "id": str(uuid.uuid4()),
            "key": "test.key",
            "old_value": "old",
            "new_value": "new",
            "change_type": "UPDATED",
            "timestamp": datetime.utcnow().isoformat(),
            "change_reason": "Test update",
            "version": 1,
            "entity_id": None
        }
        
        record = storage._deserialize_change_record(data)
        
        assert record.state_key == "test.key"
        assert record.old_value == "old"
        assert record.new_value == "new"
        assert record.change_type == StateChangeType.UPDATED
        assert record.change_reason == "Test update"


class TestMigration: pass
    """Test data migration functionality."""
    
    def test_migrate_state_data(self, storage): pass
        """Test state data migration."""
        old_data = {
            "schema_version": 0,
            "variables": {"test.key": "test_value"}
        }
        
        migrated_data = storage._migrate_state_data(old_data)
        
        # Should return the same data for now (no migration logic implemented)
        assert migrated_data == old_data
    
    def test_migrate_history_data(self, storage): pass
        """Test history data migration."""
        old_data = {
            "schema_version": 0,
            "history": {"test.key": []}
        }
        
        migrated_data = storage._migrate_history_data(old_data)
        
        # Should return the same data for now (no migration logic implemented)
        assert migrated_data == old_data
    
    def test_migrate_snapshot_data(self, storage): pass
        """Test snapshot data migration."""
        old_data = {
            "schema_version": 0,
            "state_data": {"test.key": "test_value"}
        }
        
        migrated_data = storage._migrate_snapshot_data(old_data)
        
        # Should return the same data for now (no migration logic implemented)
        assert migrated_data == old_data


# Run the tests
if __name__ == "__main__": pass
    pytest.main([__file__, "-v"]) 