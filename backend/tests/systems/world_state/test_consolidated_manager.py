from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from typing import Type
from dataclasses import field

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
Tests for backend.systems.world_state.consolidated_manager

Comprehensive tests for the WorldStateManager class including state variables,
history tracking, snapshots, and persistence functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import uuid
import json
import tempfile
import os
from pathlib import Path

# Import the module being tested
try: pass
    from backend.systems.world_state.consolidated_manager import WorldStateManager
    from backend.systems.world_state.consolidated_state_models import (
        StateVariable,
        StateChangeRecord,
        StateChangeType,
        StateCategory,
        WorldRegion,
        WorldStateSnapshot
    )
    from backend.systems.events.event_dispatcher import EventDispatcher
    from backend.systems.shared.utils.common.error import NotFoundError, ValidationError
except ImportError as e: pass
    pytest.skip(f"Could not import required modules: {e}", allow_module_level=True)


@pytest.fixture
def manager(): pass
    """Create a fresh WorldStateManager instance for each test."""
    # Clear any existing instance
    WorldStateManager._instance = None
    
    # Create new instance
    manager = WorldStateManager.get_instance()
    
    # Clean up any existing state
    manager._state_variables.clear()
    manager._state_history.clear()
    manager._next_version = 1
    manager.world_state = None
    
    yield manager
    
    # Clean up after test
    WorldStateManager._instance = None


class TestWorldStateManagerSingleton: pass
    """Test singleton behavior of WorldStateManager."""
    
    def test_singleton_instance(self): pass
        """Test that get_instance returns the same instance."""
        WorldStateManager._instance = None
        
        manager1 = WorldStateManager.get_instance()
        manager2 = WorldStateManager.get_instance()
        
        assert manager1 is manager2
        
        # Clean up
        WorldStateManager._instance = None
    
    def test_init_raises_error_if_instance_exists(self): pass
        """Test that creating a new instance raises an error if one already exists."""
        WorldStateManager._instance = None
        
        # Create first instance
        manager1 = WorldStateManager.get_instance()
        
        # Try to create second instance directly
        with pytest.raises(RuntimeError): pass
            WorldStateManager()
        
        # Clean up
        WorldStateManager._instance = None


class TestStateVariableOperations: pass
    """Test state variable CRUD operations."""
    
    def test_set_state_new_variable(self, manager): pass
        """Test setting a new state variable."""
        result = manager.set_state(
            key="test.new.var",
            value="test_value",
            category=StateCategory.POLITICAL,
            region=WorldRegion.NORTHERN,
            tags=["test", "new"],
            change_reason="Initial creation"
        )
        
        assert isinstance(result, StateVariable)
        assert result.key == "test.new.var"
        assert result.value == "test_value"
        assert result.category == StateCategory.POLITICAL
        assert result.region == WorldRegion.NORTHERN
        assert result.tags == ["test", "new"]
        
        # Check it's stored
        assert "test.new.var" in manager._state_variables
        assert len(manager._state_history["test.new.var"]) == 1
        
        # Check history record
        history = manager._state_history["test.new.var"][0]
        assert history.change_type == StateChangeType.CREATED
        assert history.old_value is None
        assert history.new_value == "test_value"
        assert history.change_reason == "Initial creation"
    
    def test_set_state_update_existing(self, manager): pass
        """Test updating an existing state variable."""
        # Create initial variable
        manager.set_state(key="test.update.var", value="initial_value")
        
        # Update it
        result = manager.set_state(
            key="test.update.var",
            value="updated_value",
            change_reason="Test update"
        )
        
        assert result.value == "updated_value"
        
        # Check history
        history = manager._state_history["test.update.var"]
        assert len(history) == 2
        
        # Check update record
        update_record = history[1]
        assert update_record.change_type == StateChangeType.UPDATED
        assert update_record.old_value == "initial_value"
        assert update_record.new_value == "updated_value"
        assert update_record.change_reason == "Test update"
    
    def test_set_state_no_change_same_value(self, manager): pass
        """Test that setting the same value doesn't create a history record."""
        # Create initial variable
        manager.set_state(key="test.same.var", value="same_value")
        initial_history_length = len(manager._state_history["test.same.var"])
        
        # Set same value again
        manager.set_state(key="test.same.var", value="same_value")
        
        # History should not have changed
        assert len(manager._state_history["test.same.var"]) == initial_history_length
    
    def test_get_state(self, manager): pass
        """Test getting state variable values."""
        # Test non-existent key
        assert manager.get_state("non.existent") is None
        assert manager.get_state("non.existent", "default") == "default"
        
        # Create and test existing key
        manager.set_state(key="test.get.var", value="get_value")
        assert manager.get_state("test.get.var") == "get_value"
    
    def test_get_state_variable(self, manager): pass
        """Test getting state variable objects."""
        # Test non-existent key
        assert manager.get_state_variable("non.existent") is None
        
        # Create and test existing key
        manager.set_state(key="test.get.obj", value="obj_value")
        var = manager.get_state_variable("test.get.obj")
        
        assert isinstance(var, StateVariable)
        assert var.key == "test.get.obj"
        assert var.value == "obj_value"
    
    def test_delete_state(self, manager): pass
        """Test deleting state variables."""
        # Test deleting non-existent key
        assert manager.delete_state("non.existent") is False
        
        # Create and delete existing key
        manager.set_state(key="test.delete.var", value="delete_value")
        assert manager.delete_state("test.delete.var") is True
        
        # Check it's gone
        assert "test.delete.var" not in manager._state_variables
        assert manager.get_state("test.delete.var") is None
        
        # Check history records deletion
        history = manager._state_history["test.delete.var"]
        delete_record = history[-1]
        assert delete_record.change_type == StateChangeType.DELETED
        assert delete_record.old_value == "delete_value"
        assert delete_record.new_value is None


class TestHistoryAndVersioning: pass
    """Test history tracking and versioning functionality."""
    
    def test_get_history(self, manager): pass
        """Test getting change history for a variable."""
        # Test non-existent key
        assert manager.get_history("non.existent") == []
        
        # Create variable with changes
        manager.set_state(key="test.history", value="v1", change_reason="First")
        manager.set_state(key="test.history", value="v2", change_reason="Second")
        manager.set_state(key="test.history", value="v3", change_reason="Third")
        
        history = manager.get_history("test.history")
        assert len(history) == 3
        
        # Check order and content
        assert history[0].new_value == "v1"
        assert history[0].change_reason == "First"
        assert history[1].old_value == "v1"
        assert history[1].new_value == "v2"
        assert history[1].change_reason == "Second"
        assert history[2].old_value == "v2"
        assert history[2].new_value == "v3"
        assert history[2].change_reason == "Third"
    
    def test_get_value_at_time(self, manager): pass
        """Test getting values at specific timestamps."""
        # Record timestamps
        start_time = datetime.utcnow()
        
        # Create variable
        manager.set_state(key="test.time", value="v1")
        first_time = datetime.utcnow()
        
        # Update variable
        manager.set_state(key="test.time", value="v2")
        second_time = datetime.utcnow()
        
        # Update again
        manager.set_state(key="test.time", value="v3")
        
        # Test values at different times
        assert manager.get_value_at_time("test.time", start_time) is None
        assert manager.get_value_at_time("test.time", first_time) == "v1"
        assert manager.get_value_at_time("test.time", second_time) == "v2"
        
        # Test non-existent key
        assert manager.get_value_at_time("non.existent", datetime.utcnow()) is None
        assert manager.get_value_at_time("non.existent", datetime.utcnow(), "default") == "default"
    
    def test_restore_version(self, manager): pass
        """Test restoring variables to specific versions."""
        # Create variable with multiple versions
        manager.set_state(key="test.restore", value="v1")
        manager.set_state(key="test.restore", value="v2")
        manager.set_state(key="test.restore", value="v3")
        
        # Get version 1
        history = manager.get_history("test.restore")
        version_1 = history[0].version
        
        # Restore to version 1
        success = manager.restore_version("test.restore", version_1)
        assert success is True
        assert manager.get_state("test.restore") == "v1"
        
        # Test restoring non-existent version
        success = manager.restore_version("test.restore", 99999)
        assert success is False
        
        # Test restoring non-existent key
        success = manager.restore_version("non.existent", 1)
        assert success is False


class TestSnapshots: pass
    """Test snapshot creation and restoration."""
    
    def test_create_snapshot(self, manager): pass
        """Test creating snapshots."""
        # Set up some state
        manager.set_state(key="snap.var1", value="value1")
        manager.set_state(key="snap.var2", value="value2")
        
        # Create snapshot
        snapshot = manager.create_snapshot(
            label="Test Snapshot",
            metadata={"purpose": "testing"}
        )
        
        assert isinstance(snapshot, WorldStateSnapshot)
        assert snapshot.metadata["label"] == "Test Snapshot"
        assert snapshot.metadata["purpose"] == "testing"
        assert "snap.var1" in snapshot.variables
        assert "snap.var2" in snapshot.variables
        assert snapshot.variables["snap.var1"] == "value1"
        assert snapshot.variables["snap.var2"] == "value2"
    
    def test_restore_snapshot(self, manager): pass
        """Test restoring from snapshots."""
        # Set up initial state
        manager.set_state(key="restore.var1", value="initial1")
        manager.set_state(key="restore.var2", value="initial2")
        
        # Create snapshot
        snapshot = manager.create_snapshot()
        
        # Change state
        manager.set_state(key="restore.var1", value="changed1")
        manager.set_state(key="restore.var3", value="new_var")
        manager.delete_state("restore.var2")
        
        # Verify changed state
        assert manager.get_state("restore.var1") == "changed1"
        assert manager.get_state("restore.var2") is None
        assert manager.get_state("restore.var3") == "new_var"
        
        # Restore snapshot
        success = manager.restore_snapshot(snapshot.id)
        assert success is True
        
        # Verify restored state
        assert manager.get_state("restore.var1") == "initial1"
        assert manager.get_state("restore.var2") == "initial2"
        assert manager.get_state("restore.var3") is None
        
        # Test restoring non-existent snapshot
        success = manager.restore_snapshot("non-existent-id")
        assert success is False


class TestQueryOperations: pass
    """Test state variable query operations."""
    
    def test_query_state_by_category(self, manager): pass
        """Test querying by category."""
        # Set up test data
        manager.set_state(
            key="cat.political.1", value="pol1", category=StateCategory.POLITICAL
        )
        manager.set_state(
            key="cat.political.2", value="pol2", category=StateCategory.POLITICAL
        )
        manager.set_state(
            key="cat.economic.1", value="econ1", category=StateCategory.ECONOMIC
        )
        
        # Query political variables
        political_vars = manager.query_state_by_category(StateCategory.POLITICAL)
        assert len(political_vars) == 2
        assert "cat.political.1" in political_vars
        assert "cat.political.2" in political_vars
        assert "cat.economic.1" not in political_vars
        
        # Query non-existent category
        empty_result = manager.query_state_by_category(StateCategory.MAGICAL)
        assert len(empty_result) == 0
    
    def test_query_state_by_region(self, manager): pass
        """Test querying by region."""
        # Set up test data
        manager.set_state(
            key="reg.north.1", value="n1", region=WorldRegion.NORTHERN
        )
        manager.set_state(
            key="reg.north.2", value="n2", region=WorldRegion.NORTHERN
        )
        manager.set_state(
            key="reg.south.1", value="s1", region=WorldRegion.SOUTHERN
        )
        
        # Query northern variables
        northern_vars = manager.query_state_by_region(WorldRegion.NORTHERN)
        assert len(northern_vars) == 2
        assert "reg.north.1" in northern_vars
        assert "reg.north.2" in northern_vars
        assert "reg.south.1" not in northern_vars
    
    def test_query_state_by_tags(self, manager): pass
        """Test querying by tags."""
        # Set up test data
        manager.set_state(
            key="tag.test1", value="t1", tags=["test", "alpha"]
        )
        manager.set_state(
            key="tag.test2", value="t2", tags=["test", "beta"]
        )
        manager.set_state(
            key="tag.other", value="o1", tags=["other", "gamma"]
        )
        
        # Query with match_any=False (default - must have all tags)
        test_vars = manager.query_state_by_tags(["test"])
        assert len(test_vars) == 2
        assert "tag.test1" in test_vars
        assert "tag.test2" in test_vars
        
        # Query with multiple tags (must have all)
        alpha_test_vars = manager.query_state_by_tags(["test", "alpha"])
        assert len(alpha_test_vars) == 1
        assert "tag.test1" in alpha_test_vars
        
        # Query with match_any=True
        any_vars = manager.query_state_by_tags(["test", "gamma"], match_any=True)
        assert len(any_vars) == 3  # All three should match
        
        # Query non-existent tag
        empty_result = manager.query_state_by_tags(["non_existent"])
        assert len(empty_result) == 0
    
    def test_query_state_by_prefix(self, manager): pass
        """Test querying by key prefix."""
        # Set up test data
        manager.set_state(key="prefix.test.1", value="p1")
        manager.set_state(key="prefix.test.2", value="p2")
        manager.set_state(key="different.key", value="d1")
        
        # Query with prefix
        prefix_vars = manager.query_state_by_prefix("prefix.test")
        assert len(prefix_vars) == 2
        assert "prefix.test.1" in prefix_vars
        assert "prefix.test.2" in prefix_vars
        assert "different.key" not in prefix_vars
        
        # Query non-existent prefix
        empty_result = manager.query_state_by_prefix("non.existent")
        assert len(empty_result) == 0
    
    def test_get_state_snapshot(self, manager): pass
        """Test getting state snapshots at specific times."""
        # Set up state at different times
        start_time = datetime.utcnow()
        
        manager.set_state(key="snap.var1", value="v1")
        first_time = datetime.utcnow()
        
        manager.set_state(key="snap.var2", value="v2")
        manager.set_state(key="snap.var1", value="v1_updated")
        second_time = datetime.utcnow()
        
        # Test snapshot at different times
        start_snapshot = manager.get_state_snapshot(start_time)
        assert len(start_snapshot) == 0
        
        first_snapshot = manager.get_state_snapshot(first_time)
        assert len(first_snapshot) == 1
        assert first_snapshot["snap.var1"] == "v1"
        
        second_snapshot = manager.get_state_snapshot(second_time)
        assert len(second_snapshot) == 2
        assert second_snapshot["snap.var1"] == "v1_updated"
        assert second_snapshot["snap.var2"] == "v2"
        
        # Test current snapshot (no timestamp)
        current_snapshot = manager.get_state_snapshot()
        assert len(current_snapshot) >= 2


class TestUtilityMethods: pass
    """Test utility and information methods."""
    
    def test_get_all_state_variables(self, manager): pass
        """Test getting all state variables."""
        # Initially empty
        all_vars = manager.get_all_state_variables()
        assert len(all_vars) == 0
        
        # Add some variables
        manager.set_state(key="util.var1", value="u1")
        manager.set_state(key="util.var2", value="u2")
        
        all_vars = manager.get_all_state_variables()
        assert len(all_vars) == 2
        assert "util.var1" in all_vars
        assert "util.var2" in all_vars
    
    def test_get_state_count(self, manager): pass
        """Test getting state variable count."""
        assert manager.get_state_count() == 0
        
        manager.set_state(key="count.var1", value="c1")
        assert manager.get_state_count() == 1
        
        manager.set_state(key="count.var2", value="c2")
        assert manager.get_state_count() == 2
        
        manager.delete_state("count.var1")
        assert manager.get_state_count() == 1
    
    def test_get_statistics(self, manager): pass
        """Test getting manager statistics."""
        # Set up diverse state
        manager.set_state(
            key="stats.pol1", value="p1", 
            category=StateCategory.POLITICAL, 
            region=WorldRegion.NORTHERN
        )
        manager.set_state(
            key="stats.pol2", value="p2", 
            category=StateCategory.POLITICAL, 
            region=WorldRegion.SOUTHERN
        )
        manager.set_state(
            key="stats.econ1", value="e1", 
            category=StateCategory.ECONOMIC, 
            region=WorldRegion.NORTHERN
        )
        
        stats = manager.get_statistics()
        
        assert stats["state_count"] == 3
        assert stats["next_version"] > 1
        assert stats["history_size"] >= 3
        
        # Check category counts
        assert stats["category_counts"]["political"] == 2
        assert stats["category_counts"]["economic"] == 1
        
        # Check region counts
        assert stats["region_counts"]["northern"] == 2
        assert stats["region_counts"]["southern"] == 1


class TestWorldStateFileOperations: pass
    """Test world state file persistence operations."""
    
    def test_get_world_state_not_found(self, manager): pass
        """Test getting world state when file doesn't exist."""
        with pytest.raises(NotFoundError): pass
            manager.get_world_state()
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open')
    def test_get_world_state_file_exists(self, mock_open, mock_exists, manager): pass
        """Test loading world state from file."""
        # Mock file exists
        mock_exists.return_value = True
        
        # Mock file content
        test_world_state = {
            "name": "Test World",
            "current_date": {"year": 2023, "month": 1, "day": 1, "hour": 0, "minute": 0}
        }
        mock_file = MagicMock()
        mock_file.read.return_value = json.dumps(test_world_state)
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Test loading
        world_state = manager.get_world_state()
        
        assert world_state["name"] == "Test World"
        assert world_state["current_date"]["year"] == 2023
        assert manager.world_state is not None
    
    def test_update_world_state_no_existing_state(self, manager): pass
        """Test updating world state when none exists."""
        with pytest.raises(NotFoundError): pass
            manager.update_world_state({"test": "update"})
    
    @patch.object(WorldStateManager, 'get_world_state')
    @patch.object(WorldStateManager, '_save_world_state_to_file')
    def test_update_world_state_success(self, mock_save, mock_get, manager): pass
        """Test successful world state update."""
        # Mock existing state
        existing_state = {"name": "Test World", "version": 1}
        mock_get.return_value = existing_state
        
        # Update state
        updates = {"version": 2, "new_field": "new_value"}
        result = manager.update_world_state(updates)
        
        assert result["version"] == 2
        assert result["new_field"] == "new_value"
        assert result["name"] == "Test World"  # Original field preserved
        assert "updated_at" in result
        
        # Verify save was called
        mock_save.assert_called_once()
    
    def test_save_world_state_no_state(self, manager): pass
        """Test saving when no world state exists."""
        with pytest.raises(NotFoundError): pass
            manager.save_world_state()


class TestEventHandling: pass
    """Test event handling and publishing."""
    
    @patch.object(EventDispatcher, 'publish')
    def test_set_state_publishes_created_event(self, mock_publish, manager): pass
        """Test that setting new state publishes a created event."""
        manager.set_state(key="event.test", value="test_value")
        
        # Should have published a StateVariableCreatedEvent
        mock_publish.assert_called()
        published_event = mock_publish.call_args[0][0]
        assert published_event.key == "event.test"
        assert published_event.value == "test_value"
    
    @patch.object(EventDispatcher, 'publish')
    def test_set_state_publishes_updated_event(self, mock_publish, manager): pass
        """Test that updating state publishes an updated event."""
        # Create initial state
        manager.set_state(key="event.update", value="initial")
        mock_publish.reset_mock()
        
        # Update state
        manager.set_state(key="event.update", value="updated")
        
        # Should have published a StateVariableUpdatedEvent
        mock_publish.assert_called()
        published_event = mock_publish.call_args[0][0]
        assert published_event.key == "event.update"
        assert published_event.old_value == "initial"
        assert published_event.new_value == "updated"
    
    @patch.object(EventDispatcher, 'publish')
    def test_delete_state_publishes_deleted_event(self, mock_publish, manager): pass
        """Test that deleting state publishes a deleted event."""
        # Create state to delete
        manager.set_state(key="event.delete", value="to_delete")
        mock_publish.reset_mock()
        
        # Delete state
        manager.delete_state("event.delete")
        
        # Should have published a StateVariableDeletedEvent
        mock_publish.assert_called()
        published_event = mock_publish.call_args[0][0]
        assert published_event.key == "event.delete"
        assert published_event.old_value == "to_delete"


class TestPrivateHelperMethods: pass
    """Test private helper methods."""
    
    def test_deep_update(self, manager): pass
        """Test the _deep_update helper method."""
        target = {
            "level1": {
                "level2": {
                    "existing": "old_value",
                    "keep": "unchanged"
                },
                "other": "preserved"
            },
            "top_level": "original"
        }
        
        source = {
            "level1": {
                "level2": {
                    "existing": "new_value",
                    "added": "new_field"
                }
            },
            "new_top": "added"
        }
        
        manager._deep_update(target, source)
        
        # Check nested update
        assert target["level1"]["level2"]["existing"] == "new_value"
        assert target["level1"]["level2"]["added"] == "new_field"
        assert target["level1"]["level2"]["keep"] == "unchanged"  # Preserved
        assert target["level1"]["other"] == "preserved"  # Preserved
        assert target["top_level"] == "original"  # Preserved
        assert target["new_top"] == "added"  # Added


# Run the tests
if __name__ == "__main__": pass
    pytest.main([__file__, "-v"]) 