from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher

# Import EventBase and EventDispatcher with fallbacks
try: pass
    from backend.systems.events import EventBase, EventDispatcher
except ImportError: pass
    # Fallback for tests or when events system isn't available
    class EventBase: pass
        def __init__(self, **data): pass
            for key, value in data.items(): pass
                setattr(self, key, value)
    
    class EventDispatcher: pass
        @classmethod
        def get_instance(cls): pass
            return cls()
        
        def dispatch(self, event): pass
            pass
        
        def publish(self, event): pass
            pass
        
        def emit(self, event): pass
            pass

"""
Coverage-focused tests for backend.systems.world_state.consolidated_manager

Targeting specific uncovered lines to boost coverage efficiently.
"""

import pytest
import json
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from backend.systems.shared.utils.error_utils import NotFoundError

# Import the module being tested
try: pass
    from backend.systems.world_state.consolidated_manager import (
        WorldStateManager, StateCategory, WorldRegion, StateVariable,
        StateChangeRecord, WorldStateSnapshot
    )
    from backend.systems.events.event_dispatcher import EventDispatcher
    from backend.systems.world_state.events import WorldStateUpdatedEvent
except ImportError as e: pass
    pytest.skip(f"Could not import consolidated_manager: {e}", allow_module_level=True)


class TestWorldStateManagerSingleton: pass
    """Test WorldStateManager singleton behavior."""

    def teardown_method(self): pass
        """Clean up singleton after each test."""
        WorldStateManager.reset_instance()

    def test_singleton_creation(self): pass
        """Test singleton instance creation."""
        instance1 = WorldStateManager.get_instance()
        instance2 = WorldStateManager.get_instance()
        
        assert instance1 is instance2
        assert WorldStateManager._instance is instance1

    def test_direct_init_raises_error(self): pass
        """Test that direct initialization raises error after singleton creation."""
        # Create singleton first
        WorldStateManager.get_instance()
        
        # Direct init should fail
        with pytest.raises(RuntimeError, match="WorldStateManager is a singleton"): pass
            WorldStateManager()

    def test_reset_instance(self): pass
        """Test resetting singleton instance."""
        instance1 = WorldStateManager.get_instance()
        assert WorldStateManager._instance is instance1
        
        WorldStateManager.reset_instance()
        assert WorldStateManager._instance is None
        
        # Should be able to create new instance
        instance2 = WorldStateManager.get_instance()
        assert instance2 is not instance1

    @patch.object(WorldStateManager, 'shutdown')
    def test_reset_instance_with_shutdown_error(self, mock_shutdown): pass
        """Test reset instance handles shutdown errors gracefully."""
        mock_shutdown.side_effect = Exception("Shutdown error")
        
        WorldStateManager.get_instance()
        
        # Should not raise error despite shutdown exception
        WorldStateManager.reset_instance()
        assert WorldStateManager._instance is None


class TestWorldStateManagerGetState: pass
    """Test world state retrieval functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = WorldStateManager.get_instance()
        self.manager.storage_dir = Path(self.temp_dir) / "world_state"
        self.manager.storage_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self): pass
        """Clean up test environment."""
        WorldStateManager.reset_instance()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_world_state_not_found(self): pass
        """Test getting world state when file doesn't exist."""
        with pytest.raises(NotFoundError, match="No world state found"): pass
            self.manager.get_world_state()

    def test_get_world_state_from_file(self): pass
        """Test loading world state from file."""
        # Create test state file
        test_state = {
            "name": "Test World",
            "current_date": {"year": 1, "month": 1, "day": 1, "hour": 12, "minute": 0}
        }
        
        current_file = self.manager.storage_dir / "current.json"
        with open(current_file, "w") as f: pass
            json.dump(test_state, f)
        
        result = self.manager.get_world_state()
        
        assert result["name"] == "Test World"
        assert self.manager.world_state is not None
        assert self.manager.last_update_time is not None

    def test_get_world_state_with_incomplete_date(self): pass
        """Test loading world state with incomplete date fields."""
        test_state = {
            "name": "Test World",
            "current_date": {"year": 1, "month": 1}  # Missing day, hour, minute
        }
        
        current_file = self.manager.storage_dir / "current.json"
        with open(current_file, "w") as f: pass
            json.dump(test_state, f)
        
        result = self.manager.get_world_state()
        
        # Should fill in missing date fields
        assert result["current_date"]["day"] == 0
        assert result["current_date"]["hour"] == 0
        assert result["current_date"]["minute"] == 0

    def test_get_world_state_cached(self): pass
        """Test getting cached world state."""
        # Set up cached state
        self.manager.world_state = {"name": "Cached World"}
        
        result = self.manager.get_world_state()
        assert result["name"] == "Cached World"

    def test_get_world_state_force_reload(self): pass
        """Test forcing reload from file."""
        # Set up cached state
        self.manager.world_state = {"name": "Cached World"}
        
        # Create different file state
        test_state = {"name": "File World"}
        current_file = self.manager.storage_dir / "current.json"
        with open(current_file, "w") as f: pass
            json.dump(test_state, f)
        
        result = self.manager.get_world_state(reload=True)
        assert result["name"] == "File World"

    @patch("builtins.open", side_effect=Exception("File error"))
    def test_get_world_state_file_error(self, mock_open): pass
        """Test handling file read errors."""
        # Create file to pass existence check
        current_file = self.manager.storage_dir / "current.json"
        current_file.touch()
        
        with pytest.raises(NotFoundError, match="Failed to load world state"): pass
            self.manager.get_world_state()


class TestWorldStateManagerUpdate: pass
    """Test world state update functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = WorldStateManager.get_instance()
        self.manager.storage_dir = Path(self.temp_dir) / "world_state"
        self.manager.versions_dir = self.manager.storage_dir / "versions"
        self.manager.storage_dir.mkdir(parents=True, exist_ok=True)
        self.manager.versions_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self): pass
        """Clean up test environment."""
        WorldStateManager.reset_instance()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_update_world_state_no_existing_state(self): pass
        """Test updating when no world state exists."""
        with pytest.raises(NotFoundError, match="Cannot update world state: No world state exists"): pass
            self.manager.update_world_state({"test": "value"})

    @patch.object(WorldStateManager, '_deep_update')
    @patch.object(WorldStateManager, '_save_world_state_to_file')
    def test_update_world_state_success(self, mock_save, mock_deep_update): pass
        """Test successful world state update."""
        # Set up existing state
        self.manager.world_state = {"name": "Test World", "level": 1}
        
        updates = {"level": 2, "new_field": "value"}
        
        with patch.object(self.manager.event_dispatcher, 'publish') as mock_publish: pass
            result = self.manager.update_world_state(updates)
        
        mock_deep_update.assert_called_once()
        mock_save.assert_called_once()
        mock_publish.assert_called_once()
        
        assert "updated_at" in result
        assert self.manager.last_update_time is not None

    def test_update_world_state_no_save(self): pass
        """Test updating without saving to file."""
        self.manager.world_state = {"name": "Test World"}
        
        with patch.object(self.manager, '_save_world_state_to_file') as mock_save: pass
            self.manager.update_world_state({"test": "value"}, save=False)
        
        mock_save.assert_not_called()


class TestWorldStateManagerFileOperations: pass
    """Test file operation functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = WorldStateManager.get_instance()
        self.manager.storage_dir = Path(self.temp_dir) / "world_state"
        self.manager.versions_dir = self.manager.storage_dir / "versions"
        self.manager.storage_dir.mkdir(parents=True, exist_ok=True)
        self.manager.versions_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self): pass
        """Clean up test environment."""
        WorldStateManager.reset_instance()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_world_state_to_file_new(self): pass
        """Test saving world state to new file."""
        test_state = {"name": "Test World", "level": 1}
        
        self.manager._save_world_state_to_file(test_state)
        
        current_file = self.manager.storage_dir / "current.json"
        assert current_file.exists()
        
        with open(current_file) as f: pass
            saved_state = json.load(f)
        assert saved_state["name"] == "Test World"

    def test_save_world_state_to_file_with_backup(self): pass
        """Test saving world state creates backup of existing file."""
        # Create existing file
        current_file = self.manager.storage_dir / "current.json"
        with open(current_file, "w") as f: pass
            json.dump({"old": "state"}, f)
        
        test_state = {"name": "New World"}
        
        self.manager._save_world_state_to_file(test_state)
        
        # Check backup was created
        backup_files = list(self.manager.versions_dir.glob("state_*.json"))
        assert len(backup_files) == 1

    @patch.object(WorldStateManager, '_cleanup_old_backups')
    def test_save_triggers_backup_cleanup(self, mock_cleanup): pass
        """Test that saving triggers backup cleanup."""
        # Create existing file
        current_file = self.manager.storage_dir / "current.json"
        with open(current_file, "w") as f: pass
            json.dump({"old": "state"}, f)
        
        test_state = {"name": "New World"}
        self.manager._save_world_state_to_file(test_state)
        
        mock_cleanup.assert_called_once_with(self.manager.max_backup_versions)

    @patch("builtins.open", side_effect=Exception("Write error"))
    def test_save_world_state_file_error(self, mock_open): pass
        """Test handling file write errors."""
        test_state = {"name": "Test World"}
        
        # Should not raise error, just log
        self.manager._save_world_state_to_file(test_state)

    def test_prepare_for_file_datetime_conversion(self): pass
        """Test preparing data for file storage converts datetime objects."""
        test_data = {
            "timestamp": datetime.now(),
            "nested": {
                "date": datetime.now()
            },
            "list": [datetime.now(), "string"],
            "normal": "value"
        }
        
        self.manager._prepare_for_file(test_data)
        
        # Should convert datetime objects to ISO strings
        assert isinstance(test_data["timestamp"], str)
        assert isinstance(test_data["nested"]["date"], str)
        assert isinstance(test_data["list"][0], str)
        assert test_data["normal"] == "value"


class TestWorldStateManagerEventHandlers: pass
    """Test event handler functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.manager = WorldStateManager.get_instance()

    def teardown_method(self): pass
        """Clean up test environment."""
        WorldStateManager.reset_instance()

    def test_handle_time_event(self): pass
        """Test time event handler."""
        mock_event = Mock()
        mock_event.hours = 2
        
        with patch.object(self.manager, 'save_world_state') as mock_save: pass
            self.manager._handle_time_event(mock_event)
        
        mock_save.assert_called_once()

    def test_handle_world_reset(self): pass
        """Test world reset event handler."""
        mock_event = Mock()
        
        with patch.object(self.manager, 'save_world_state') as mock_save: pass
            self.manager._handle_world_reset(mock_event)
        
        mock_save.assert_called_once()

    def test_handle_save_request(self): pass
        """Test save request event handler."""
        mock_event = Mock()
        
        with patch.object(self.manager, 'save_world_state') as mock_save: pass
            self.manager._handle_save_request(mock_event)
        
        mock_save.assert_called_once()


class TestWorldStateManagerStateVariables: pass
    """Test state variable management."""

    def setup_method(self): pass
        """Set up test environment."""
        self.manager = WorldStateManager.get_instance()

    def teardown_method(self): pass
        """Clean up test environment."""
        WorldStateManager.reset_instance()

    def test_set_state_basic(self): pass
        """Test setting a basic state variable."""
        result = self.manager.set_state("test_key", "test_value")
        
        assert isinstance(result, StateVariable)
        assert result.key == "test_key"
        assert result.current_value == "test_value"
        assert "test_key" in self.manager._state_variables

    def test_set_state_with_all_params(self): pass
        """Test setting state with all parameters."""
        result = self.manager.set_state(
            key="complex_key",
            value={"nested": "data"},
            category=StateCategory.PLAYER,
            region=WorldRegion.ARCTIC,
            tags=["tag1", "tag2"],
            entity_id="entity_123",
            change_reason="Test reason"
        )
        
        assert result.category == StateCategory.PLAYER
        assert result.region == WorldRegion.ARCTIC
        assert result.tags == ["tag1", "tag2"]
        assert result.entity_id == "entity_123"

    def test_set_state_update_existing(self): pass
        """Test updating existing state variable."""
        # Set initial value
        self.manager.set_state("update_key", "initial")
        
        # Update value
        result = self.manager.set_state("update_key", "updated")
        
        assert result.current_value == "updated"
        assert len(self.manager._state_history["update_key"]) == 2

    def test_get_state_exists(self): pass
        """Test getting existing state value."""
        self.manager.set_state("existing_key", "existing_value")
        
        result = self.manager.get_state("existing_key")
        assert result == "existing_value"

    def test_get_state_not_exists(self): pass
        """Test getting non-existent state returns default."""
        result = self.manager.get_state("nonexistent_key", "default")
        assert result == "default"

    def test_get_state_variable_exists(self): pass
        """Test getting existing state variable."""
        self.manager.set_state("var_key", "var_value")
        
        result = self.manager.get_state_variable("var_key")
        assert result is not None
        assert result.current_value == "var_value"

    def test_get_state_variable_not_exists(self): pass
        """Test getting non-existent state variable."""
        result = self.manager.get_state_variable("nonexistent_var")
        assert result is None

    def test_delete_state_exists(self): pass
        """Test deleting existing state."""
        self.manager.set_state("delete_key", "delete_value")
        
        result = self.manager.delete_state("delete_key")
        assert result is True
        assert "delete_key" not in self.manager._state_variables

    def test_delete_state_not_exists(self): pass
        """Test deleting non-existent state."""
        result = self.manager.delete_state("nonexistent_delete")
        assert result is False

    def test_delete_state_with_entity_id(self): pass
        """Test deleting state with entity ID."""
        self.manager.set_state("entity_key", "entity_value", entity_id="entity_123")
        
        # Should not delete without entity_id
        result1 = self.manager.delete_state("entity_key")
        assert result1 is False
        
        # Should delete with correct entity_id
        result2 = self.manager.delete_state("entity_key", entity_id="entity_123")
        assert result2 is True


class TestWorldStateManagerQueries: pass
    """Test state querying functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.manager = WorldStateManager.get_instance()
        
        # Set up test data
        self.manager.set_state("player_hp", 100, category=StateCategory.PLAYER)
        self.manager.set_state("world_time", "noon", category=StateCategory.WORLD)
        self.manager.set_state("arctic_temp", -10, region=WorldRegion.ARCTIC)
        self.manager.set_state("desert_temp", 45, region=WorldRegion.DESERT)
        self.manager.set_state("tagged_item", "sword", tags=["weapon", "magic"])
        self.manager.set_state("other_item", "shield", tags=["armor"])
        self.manager.set_state("prefix_test_1", "value1")
        self.manager.set_state("prefix_test_2", "value2")
        self.manager.set_state("other_prefix", "value3")

    def teardown_method(self): pass
        """Clean up test environment."""
        WorldStateManager.reset_instance()

    def test_query_state_by_category(self): pass
        """Test querying state by category."""
        result = self.manager.query_state_by_category(StateCategory.PLAYER)
        
        assert "player_hp" in result
        assert "world_time" not in result
        assert result["player_hp"].current_value == 100

    def test_query_state_by_region(self): pass
        """Test querying state by region."""
        result = self.manager.query_state_by_region(WorldRegion.ARCTIC)
        
        assert "arctic_temp" in result
        assert "desert_temp" not in result
        assert result["arctic_temp"].current_value == -10

    def test_query_state_by_tags_match_all(self): pass
        """Test querying state by tags (match all)."""
        result = self.manager.query_state_by_tags(["weapon", "magic"], match_any=False)
        
        assert "tagged_item" in result
        assert "other_item" not in result

    def test_query_state_by_tags_match_any(self): pass
        """Test querying state by tags (match any)."""
        result = self.manager.query_state_by_tags(["weapon", "armor"], match_any=True)
        
        assert "tagged_item" in result
        assert "other_item" in result

    def test_query_state_by_prefix(self): pass
        """Test querying state by key prefix."""
        result = self.manager.query_state_by_prefix("prefix_test")
        
        assert "prefix_test_1" in result
        assert "prefix_test_2" in result
        assert "other_prefix" not in result

    def test_get_all_state_variables(self): pass
        """Test getting all state variables."""
        result = self.manager.get_all_state_variables()
        
        # Should include all the test variables we set up
        assert len(result) >= 8
        assert "player_hp" in result
        assert "world_time" in result

    def test_get_state_count(self): pass
        """Test getting state variable count."""
        count = self.manager.get_state_count()
        assert count >= 8  # At least the test variables

    def test_get_statistics(self): pass
        """Test getting state statistics."""
        stats = self.manager.get_statistics()
        
        assert "total_variables" in stats
        assert "categories" in stats
        assert "regions" in stats
        assert "tags" in stats
        assert stats["total_variables"] >= 8


class TestWorldStateManagerSnapshots: pass
    """Test snapshot functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.manager = WorldStateManager.get_instance()
        self.manager.set_state("snapshot_test", "initial_value")

    def teardown_method(self): pass
        """Clean up test environment."""
        WorldStateManager.reset_instance()

    def test_create_snapshot(self): pass
        """Test creating a state snapshot."""
        snapshot = self.manager.create_snapshot(
            label="Test Snapshot",
            metadata={"test": "data"}
        )
        
        assert isinstance(snapshot, WorldStateSnapshot)
        assert snapshot.label == "Test Snapshot"
        assert snapshot.metadata["test"] == "data"
        assert snapshot.id in self.manager._snapshots

    def test_get_state_snapshot_current(self): pass
        """Test getting current state snapshot."""
        result = self.manager.get_state_snapshot()
        
        assert "snapshot_test" in result
        assert result["snapshot_test"] == "initial_value"

    def test_restore_snapshot_exists(self): pass
        """Test restoring existing snapshot."""
        # Create snapshot
        snapshot = self.manager.create_snapshot()
        
        # Modify state
        self.manager.set_state("snapshot_test", "modified_value")
        assert self.manager.get_state("snapshot_test") == "modified_value"
        
        # Restore snapshot
        result = self.manager.restore_snapshot(snapshot.id)
        
        assert result is True
        assert self.manager.get_state("snapshot_test") == "initial_value"

    def test_restore_snapshot_not_exists(self): pass
        """Test restoring non-existent snapshot."""
        result = self.manager.restore_snapshot("nonexistent_id")
        assert result is False


class TestWorldStateManagerUtilities: pass
    """Test utility functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = WorldStateManager.get_instance()
        self.manager.versions_dir = Path(self.temp_dir) / "versions"
        self.manager.versions_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self): pass
        """Clean up test environment."""
        WorldStateManager.reset_instance()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cleanup_old_backups(self): pass
        """Test cleaning up old backup files."""
        # Create test backup files
        for i in range(10): pass
            backup_file = self.manager.versions_dir / f"state_{i:02d}.json"
            backup_file.write_text(f"backup_{i}")
        
        # Clean up to keep only 3
        self.manager._cleanup_old_backups(3)
        
        remaining_files = list(self.manager.versions_dir.glob("*.json"))
        assert len(remaining_files) == 3

    def test_deep_update(self): pass
        """Test deep dictionary update."""
        target = {
            "level1": {
                "level2": {
                    "existing": "value",
                    "to_update": "old"
                },
                "simple": "value"
            },
            "top_level": "value"
        }
        
        source = {
            "level1": {
                "level2": {
                    "to_update": "new",
                    "new_key": "new_value"
                },
                "new_simple": "new"
            },
            "new_top": "new"
        }
        
        self.manager._deep_update(target, source)
        
        # Should preserve existing values and add/update from source
        assert target["level1"]["level2"]["existing"] == "value"
        assert target["level1"]["level2"]["to_update"] == "new"
        assert target["level1"]["level2"]["new_key"] == "new_value"
        assert target["level1"]["simple"] == "value"
        assert target["level1"]["new_simple"] == "new"
        assert target["top_level"] == "value"
        assert target["new_top"] == "new"

    def test_shutdown(self): pass
        """Test manager shutdown."""
        # Set up some state
        self.manager.set_state("shutdown_test", "value")
        
        with patch.object(self.manager, 'save_world_state') as mock_save: pass
            self.manager.shutdown()
        
        # Should save state on shutdown
        mock_save.assert_called_once() 