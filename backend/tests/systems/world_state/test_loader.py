from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from typing import Type
"""
Tests for backend.systems.world_state.loader

Comprehensive tests for the WorldStateLoader class.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from datetime import datetime

# Import the module being tested
try:
    from backend.systems.world_state.loader import WorldStateLoader
    from backend.systems.world_state.consolidated_world_models import (
        WorldMap, Region, PointOfInterest, WorldState, TerrainType
    )
    from backend.systems.world_state.consolidated_state_models import (
        StateVariable, StateChangeRecord, StateCategory, WorldRegion,
        StateChangeType, WorldStateSnapshot
    )
    from backend.systems.shared.utils.common.error import NotFoundError, ValidationError
except ImportError as e:
    pytest.skip(f"Could not import backend.systems.world_state.loader: {e}", allow_module_level=True)


class TestWorldStateLoaderInitialization:
    """Test WorldStateLoader initialization."""

    def test_init_default_data_root(self):
        """Test initialization with default data root."""
        loader = WorldStateLoader()
        assert loader.data_root == Path("data")
        assert loader.storage_dir == Path("data/world_state")
        assert loader.current_schema_version == "1.0.0"
        assert "1.0.0" in loader.supported_versions

    def test_init_custom_data_root(self):
        """Test initialization with custom data root."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = WorldStateLoader(data_root=temp_dir)
            assert loader.data_root == Path(temp_dir)
            assert loader.storage_dir == Path(temp_dir) / "world_state"

    def test_directory_creation(self):
        """Test that all required directories are created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = WorldStateLoader(data_root=temp_dir)
            
            # Check that all directories exist
            assert loader.storage_dir.exists()
            assert loader.regions_dir.exists()
            assert loader.pois_dir.exists()
            assert loader.state_dir.exists()
            assert loader.history_dir.exists()
            assert loader.versions_dir.exists()
            assert loader.backup_dir.exists()


class TestWorldMapOperations:
    """Test world map loading and saving operations."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = WorldStateLoader(data_root=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_load_world_map_not_found(self):
        """Test loading world map when file doesn't exist."""
        with pytest.raises(NotFoundError, match="No world map found"):
            self.loader.load_world_map()

    @patch('backend.systems.world_state.consolidated_world_models.WorldMap.load_from_file')
    def test_load_world_map_success(self, mock_load):
        """Test successful world map loading."""
        # Create a mock world map file
        world_map_file = self.loader.storage_dir / "current.json"
        world_map_file.write_text('{"test": "data"}')
        
        mock_world_map = Mock(spec=WorldMap)
        mock_load.return_value = mock_world_map
        
        result = self.loader.load_world_map()
        
        assert result == mock_world_map
        mock_load.assert_called_once_with(str(world_map_file))

    @patch('backend.systems.world_state.consolidated_world_models.WorldMap.load_from_file')
    def test_load_world_map_with_id(self, mock_load):
        """Test loading world map with specific ID."""
        world_id = "test_world"
        world_map_file = self.loader.storage_dir / f"{world_id}.json"
        world_map_file.write_text('{"test": "data"}')
        
        mock_world_map = Mock(spec=WorldMap)
        mock_load.return_value = mock_world_map
        
        result = self.loader.load_world_map(world_id)
        
        assert result == mock_world_map
        mock_load.assert_called_once_with(str(world_map_file))

    @patch('backend.systems.world_state.consolidated_world_models.WorldMap.load_from_file')
    def test_load_world_map_corrupted_file(self, mock_load):
        """Test loading corrupted world map file."""
        world_map_file = self.loader.storage_dir / "current.json"
        world_map_file.write_text('{"test": "data"}')
        
        mock_load.side_effect = Exception("Corrupted file")
        
        with pytest.raises(NotFoundError, match="Failed to load world map"):
            self.loader.load_world_map()

    def test_save_world_map_success(self):
        """Test successful world map saving."""
        mock_world_map = Mock(spec=WorldMap)
        mock_world_map.save_to_file = Mock()
        
        self.loader.save_world_map(mock_world_map)
        
        expected_path = str(self.loader.storage_dir / "current.json")
        mock_world_map.save_to_file.assert_called_once_with(expected_path)

    def test_save_world_map_with_id(self):
        """Test saving world map with specific ID."""
        mock_world_map = Mock(spec=WorldMap)
        mock_world_map.save_to_file = Mock()
        world_id = "test_world"
        
        self.loader.save_world_map(mock_world_map, world_id)
        
        expected_path = str(self.loader.storage_dir / f"{world_id}.json")
        mock_world_map.save_to_file.assert_called_once_with(expected_path)

    def test_save_world_map_with_backup(self):
        """Test saving world map creates backup of existing file."""
        # Create existing file
        existing_file = self.loader.storage_dir / "current.json"
        existing_file.write_text('{"old": "data"}')
        
        mock_world_map = Mock(spec=WorldMap)
        mock_world_map.save_to_file = Mock()
        
        self.loader.save_world_map(mock_world_map)
        
        # Check that backup was created
        backup_files = list(self.loader.backup_dir.glob("current_*.json"))
        assert len(backup_files) > 0

    def test_save_world_map_error(self):
        """Test error handling during world map saving."""
        mock_world_map = Mock(spec=WorldMap)
        mock_world_map.save_to_file = Mock(side_effect=Exception("Save error"))
        
        with pytest.raises(ValidationError, match="Failed to save world map"):
            self.loader.save_world_map(mock_world_map)


class TestRegionOperations:
    """Test region loading and saving operations."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = WorldStateLoader(data_root=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_load_region_not_found(self):
        """Test loading region when file doesn't exist."""
        with pytest.raises(NotFoundError, match="Region not found: test_region"): pass
            self.loader.load_region("test_region")

    @patch('backend.systems.world_state.consolidated_world_models.Region.from_dict')
    def test_load_region_success(self, mock_from_dict):
        """Test successful region loading."""
        region_id = "test_region"
        region_file = self.loader.regions_dir / f"{region_id}.json"
        region_data = {"id": region_id, "name": "Test Region"}
        
        with open(region_file, "w") as f:
            json.dump(region_data, f)
        
        mock_region = Mock(spec=Region)
        mock_from_dict.return_value = mock_region
        
        result = self.loader.load_region(region_id)
        
        assert result == mock_region
        mock_from_dict.assert_called_once_with(region_data)

    @patch('backend.systems.world_state.consolidated_world_models.Region.from_dict')
    def test_load_region_corrupted_file(self, mock_from_dict):
        """Test loading corrupted region file."""
        region_id = "test_region"
        region_file = self.loader.regions_dir / f"{region_id}.json"
        region_file.write_text("invalid json")
        
        with pytest.raises(NotFoundError, match=f"Failed to load region {region_id}"):
            self.loader.load_region(region_id)

    def test_save_region_success(self):
        """Test successful region saving."""
        mock_region = Mock(spec=Region)
        mock_region.id = "test_region"
        mock_region.to_dict.return_value = {"id": "test_region", "name": "Test Region"}
        
        self.loader.save_region(mock_region)
        
        # Check that file was created
        region_file = self.loader.regions_dir / "test_region.json"
        assert region_file.exists()
        
        # Check file contents
        with open(region_file) as f:
            data = json.load(f)
        assert data["id"] == "test_region"

    def test_save_region_with_backup(self):
        """Test saving region creates backup of existing file."""
        # Create existing file
        region_id = "test_region"
        existing_file = self.loader.regions_dir / f"{region_id}.json"
        existing_file.write_text('{"old": "data"}')
        
        mock_region = Mock(spec=Region)
        mock_region.id = region_id
        mock_region.to_dict.return_value = {"id": region_id, "name": "Test Region"}
        
        self.loader.save_region(mock_region)
        
        # Check that backup was created
        backup_files = list(self.loader.backup_dir.glob(f"{region_id}_*.json"))
        assert len(backup_files) > 0

    def test_save_region_error(self):
        """Test error handling during region saving."""
        mock_region = Mock(spec=Region)
        mock_region.id = "test_region"
        mock_region.to_dict.side_effect = Exception("Serialization error")
        
        with pytest.raises(ValidationError, match="Failed to save region test_region"):
            self.loader.save_region(mock_region)


class TestPOIOperations:
    """Test POI loading and saving operations."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = WorldStateLoader(data_root=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_load_poi_not_found(self):
        """Test loading POI when file doesn't exist."""
        with pytest.raises(NotFoundError, match="POI not found: test_poi"): pass
            self.loader.load_poi("test_poi")

    @patch('backend.systems.world_state.consolidated_world_models.PointOfInterest.from_dict')
    def test_load_poi_success(self, mock_from_dict):
        """Test successful POI loading."""
        poi_id = "test_poi"
        poi_file = self.loader.pois_dir / f"{poi_id}.json"
        poi_data = {"id": poi_id, "name": "Test POI"}
        
        with open(poi_file, "w") as f:
            json.dump(poi_data, f)
        
        mock_poi = Mock(spec=PointOfInterest)
        mock_from_dict.return_value = mock_poi
        
        result = self.loader.load_poi(poi_id)
        
        assert result == mock_poi
        mock_from_dict.assert_called_once_with(poi_data)

    def test_save_poi_success(self):
        """Test successful POI saving."""
        mock_poi = Mock(spec=PointOfInterest)
        mock_poi.id = "test_poi"
        mock_poi.to_dict.return_value = {"id": "test_poi", "name": "Test POI"}
        
        self.loader.save_poi(mock_poi)
        
        # Check that file was created
        poi_file = self.loader.pois_dir / "test_poi.json"
        assert poi_file.exists()


class TestStateVariableOperations:
    """Test state variable loading and saving operations."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = WorldStateLoader(data_root=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_load_state_variable_not_found(self):
        """Test loading state variable when file doesn't exist."""
        result = self.loader.load_state_variable("test.key")
        assert result is None

    @patch('backend.systems.world_state.consolidated_state_models.StateVariable.from_dict')
    def test_load_state_variable_success(self, mock_from_dict):
        """Test successful state variable loading."""
        key = "test.key"
        filename = self.loader._key_to_filename(key)
        var_file = self.loader.state_dir / f"{filename}.json"
        var_data = {"key": key, "value": "test_value"}
        
        with open(var_file, "w") as f:
            json.dump(var_data, f)
        
        mock_variable = Mock(spec=StateVariable)
        mock_from_dict.return_value = mock_variable
        
        result = self.loader.load_state_variable(key)
        
        assert result == mock_variable
        mock_from_dict.assert_called_once_with(var_data)

    def test_save_state_variable_success(self):
        """Test successful state variable saving."""
        mock_variable = Mock(spec=StateVariable)
        mock_variable.key = "test.key"
        mock_variable.to_dict.return_value = {"key": "test.key", "value": "test_value"}
        
        self.loader.save_state_variable(mock_variable)
        
        # Check that file was created
        filename = self.loader._key_to_filename("test.key")
        var_file = self.loader.state_dir / f"{filename}.json"
        assert var_file.exists()


class TestStateHistoryOperations:
    """Test state history loading and saving operations."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = WorldStateLoader(data_root=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_load_state_history_not_found(self):
        """Test loading state history when file doesn't exist."""
        result = self.loader.load_state_history("test.key")
        assert result == []

    @patch('backend.systems.world_state.consolidated_state_models.StateChangeRecord.from_dict')
    def test_load_state_history_success(self, mock_from_dict):
        """Test successful state history loading."""
        key = "test.key"
        filename = self.loader._key_to_filename(key)
        history_file = self.loader.history_dir / f"{filename}.json"
        
        history_data = [
            {"key": key, "old_value": None, "new_value": "value1"},
            {"key": key, "old_value": "value1", "new_value": "value2"}
        ]
        
        with open(history_file, "w") as f:
            json.dump(history_data, f)
        
        mock_record1 = Mock(spec=StateChangeRecord)
        mock_record2 = Mock(spec=StateChangeRecord)
        mock_from_dict.side_effect = [mock_record1, mock_record2]
        
        result = self.loader.load_state_history(key)
        
        assert len(result) == 2
        assert result[0] == mock_record1
        assert result[1] == mock_record2

    def test_load_state_history_with_limit(self):
        """Test loading state history with limit."""
        key = "test.key"
        filename = self.loader._key_to_filename(key)
        history_file = self.loader.history_dir / f"{filename}.json"
        
        # Create more records than the limit
        history_data = [{"key": key, "value": f"value{i}"} for i in range(20)]
        
        with open(history_file, "w") as f:
            json.dump(history_data, f)
        
        with patch('backend.systems.world_state.consolidated_state_models.StateChangeRecord.from_dict') as mock_from_dict:
            mock_from_dict.side_effect = [Mock(spec=StateChangeRecord) for _ in range(5)]
            
            result = self.loader.load_state_history(key, limit=5)
            
            assert len(result) == 5

    def test_save_state_history_success(self):
        """Test successful state history saving."""
        key = "test.key"
        mock_record1 = Mock(spec=StateChangeRecord)
        mock_record1.to_dict.return_value = {"key": key, "value": "value1"}
        mock_record2 = Mock(spec=StateChangeRecord)
        mock_record2.to_dict.return_value = {"key": key, "value": "value2"}
        
        history = [mock_record1, mock_record2]
        
        self.loader.save_state_history(key, history)
        
        # Check that file was created
        filename = self.loader._key_to_filename(key)
        history_file = self.loader.history_dir / f"{filename}.json"
        assert history_file.exists()
        
        # Check file contents
        with open(history_file) as f:
            data = json.load(f)
        assert len(data) == 2


class TestSnapshotOperations:
    """Test snapshot loading and saving operations."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = WorldStateLoader(data_root=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_save_state_snapshot_success(self):
        """Test successful snapshot saving."""
        mock_snapshot = Mock(spec=WorldStateSnapshot)
        mock_snapshot.version = 1
        mock_snapshot.to_dict.return_value = {"version": 1, "data": "test"}
        
        self.loader.save_state_snapshot(mock_snapshot)
        
        # Check that file was created
        snapshot_file = self.loader.versions_dir / "snapshot_1.json"
        assert snapshot_file.exists()

    def test_load_state_snapshot_not_found(self):
        """Test loading snapshot when no snapshots exist."""
        result = self.loader.load_state_snapshot()
        assert result is None

    @patch('backend.systems.world_state.consolidated_state_models.WorldStateSnapshot.from_dict')
    def test_load_state_snapshot_latest(self, mock_from_dict):
        """Test loading latest snapshot."""
        # Create multiple snapshot files
        for version in [1, 2, 3]:
            snapshot_file = self.loader.versions_dir / f"snapshot_{version}.json"
            with open(snapshot_file, "w") as f:
                json.dump({"version": version}, f)
        
        mock_snapshot = Mock(spec=WorldStateSnapshot)
        mock_from_dict.return_value = mock_snapshot
        
        result = self.loader.load_state_snapshot()
        
        assert result == mock_snapshot
        # Should load the latest version (3)
        mock_from_dict.assert_called_once_with({"version": 3})

    @patch('backend.systems.world_state.consolidated_state_models.WorldStateSnapshot.from_dict')
    def test_load_state_snapshot_specific_version(self, mock_from_dict):
        """Test loading specific snapshot version."""
        # Create snapshot file
        snapshot_file = self.loader.versions_dir / "snapshot_2.json"
        with open(snapshot_file, "w") as f:
            json.dump({"version": 2}, f)
        
        mock_snapshot = Mock(spec=WorldStateSnapshot)
        mock_from_dict.return_value = mock_snapshot
        
        result = self.loader.load_state_snapshot(version=2)
        
        assert result == mock_snapshot
        mock_from_dict.assert_called_once_with({"version": 2})

    def test_load_state_snapshot_version_not_found(self):
        """Test loading snapshot when specific version doesn't exist."""
        result = self.loader.load_state_snapshot(version=999)
        assert result is None


class TestBackupOperations:
    """Test backup and utility operations."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = WorldStateLoader(data_root=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_create_backup_success(self):
        """Test successful backup creation."""
        # Create source file
        source_file = self.loader.storage_dir / "test.json"
        source_file.write_text('{"test": "data"}')
        
        backup_path = self.loader.create_backup(source_file)
        
        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.parent == self.loader.backup_dir

    def test_create_backup_source_not_exists(self):
        """Test backup creation when source doesn't exist."""
        non_existent_file = self.loader.storage_dir / "nonexistent.json"
        
        backup_path = self.loader.create_backup(non_existent_file)
        
        assert backup_path is None

    def test_backup_file_success(self):
        """Test internal backup file method."""
        # Create source file
        source_file = self.loader.storage_dir / "test.json"
        source_file.write_text('{"test": "data"}')
        
        backup_path = self.loader._backup_file(source_file)
        
        assert backup_path is not None
        assert backup_path.exists()

    def test_key_to_filename(self):
        """Test key to filename conversion."""
        # Test normal key
        result = self.loader._key_to_filename("region.population")
        assert result == "region_population"
        
        # Test key with special characters
        result = self.loader._key_to_filename("test/key:with.special-chars")
        assert result == "test_key_with_special-chars"

    def test_cleanup_old_backups(self):
        """Test cleanup of old backup files."""
        # Create multiple backup files
        for i in range(15):
            backup_file = self.loader.backup_dir / f"test_{i}.json"
            backup_file.write_text(f'{{"backup": {i}}}')
        
        self.loader.cleanup_old_backups(max_backups=10)
        
        # Should have only 10 files remaining
        remaining_files = list(self.loader.backup_dir.glob("*.json"))
        assert len(remaining_files) == 10

    def test_create_empty_world_state(self):
        """Test creation of empty world state."""
        world_state = self.loader.create_empty_world_state()
        
        assert isinstance(world_state, WorldState)
        assert world_state.current_time is not None
        assert world_state.world_map is not None


class TestErrorHandling:
    """Test error handling and edge cases."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = WorldStateLoader(data_root=self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_load_corrupted_json_file(self):
        """Test handling of corrupted JSON files."""
        # Create corrupted JSON file
        corrupted_file = self.loader.state_dir / "test_key.json"
        corrupted_file.write_text("invalid json content")
        
        result = self.loader.load_state_variable("test.key")
        assert result is None

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_permission_error_handling(self, mock_open):
        """Test handling of permission errors."""
        with pytest.raises(ValidationError):
            mock_variable = Mock(spec=StateVariable)
            mock_variable.key = "test.key"
            mock_variable.to_dict.return_value = {"key": "test.key"}
            self.loader.save_state_variable(mock_variable)

    def test_directory_creation_failure(self):
        """Test handling when directory creation fails."""
        # Try to create loader with invalid path
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                WorldStateLoader(data_root="/invalid/path")


def test_module_imports():
    """Test that the module can be imported without errors."""
    from backend.systems.world_state.loader import WorldStateLoader
    assert WorldStateLoader is not None
