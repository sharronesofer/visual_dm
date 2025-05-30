from typing import Type
from typing import List
"""
Tests for backend.systems.world_state.api.state_api

Comprehensive tests for the WorldStateAPI class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, List

# Import the module being tested
try: pass
    from backend.systems.world_state.api.state_api import WorldStateAPI
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
def mock_manager(): pass
    """Create a mock WorldStateManager."""
    manager = Mock()
    return manager


@pytest.fixture
def sample_state_variable(): pass
    """Create a sample state variable for testing."""
    return StateVariable(
        key="test.variable",
        value="test_value",
        category=StateCategory.POLITICAL,
        region=WorldRegion.NORTHERN,
        tags=["test", "sample"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_change_record(): pass
    """Create a sample change record for testing."""
    return StateChangeRecord(
        state_key="test.variable",
        old_value=None,
        new_value="test_value",
        change_type=StateChangeType.CREATED,
        timestamp=datetime.utcnow(),
        change_reason="Initial creation",
        version=1
    )


@pytest.fixture
def sample_snapshot(): pass
    """Create a sample snapshot for testing."""
    return WorldStateSnapshot(
        version=1,
        timestamp=datetime.utcnow(),
        variables={"test.key": "test_value"},
        metadata={"purpose": "testing"}
    )


class TestGetManager: pass
    """Test the get_manager method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateManager.get_instance')
    def test_get_manager(self, mock_get_instance, mock_manager): pass
        """Test getting the manager instance."""
        mock_get_instance.return_value = mock_manager
        
        result = WorldStateAPI.get_manager()
        
        assert result == mock_manager
        mock_get_instance.assert_called_once()


class TestSetState: pass
    """Test the set_state method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_set_state_basic(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test basic state setting."""
        mock_get_manager.return_value = mock_manager
        mock_manager.set_state.return_value = sample_state_variable
        
        result = WorldStateAPI.set_state("test.key", "test_value")
        
        assert result == sample_state_variable
        mock_manager.set_state.assert_called_once_with(
            key="test.key",
            value="test_value",
            category=StateCategory.OTHER,
            region=WorldRegion.GLOBAL,
            tags=None,
            entity_id=None
        )
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_set_state_with_all_params(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test state setting with all parameters."""
        mock_get_manager.return_value = mock_manager
        mock_manager.set_state.return_value = sample_state_variable
        
        result = WorldStateAPI.set_state(
            key="test.key",
            value="test_value",
            category=StateCategory.POLITICAL,
            region=WorldRegion.NORTHERN,
            tags=["test", "sample"],
            entity_id="entity123"
        )
        
        assert result == sample_state_variable
        mock_manager.set_state.assert_called_once_with(
            key="test.key",
            value="test_value",
            category=StateCategory.POLITICAL,
            region=WorldRegion.NORTHERN,
            tags=["test", "sample"],
            entity_id="entity123"
        )
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_set_state_with_string_category(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test state setting with string category."""
        mock_get_manager.return_value = mock_manager
        mock_manager.set_state.return_value = sample_state_variable
        
        result = WorldStateAPI.set_state(
            key="test.key",
            value="test_value",
            category="POLITICAL"
        )
        
        assert result == sample_state_variable
        mock_manager.set_state.assert_called_once_with(
            key="test.key",
            value="test_value",
            category=StateCategory.POLITICAL,
            region=WorldRegion.GLOBAL,
            tags=None,
            entity_id=None
        )
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_set_state_with_string_region(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test state setting with string region."""
        mock_get_manager.return_value = mock_manager
        mock_manager.set_state.return_value = sample_state_variable
        
        result = WorldStateAPI.set_state(
            key="test.key",
            value="test_value",
            region="NORTHERN"
        )
        
        assert result == sample_state_variable
        mock_manager.set_state.assert_called_once_with(
            key="test.key",
            value="test_value",
            category=StateCategory.OTHER,
            region=WorldRegion.NORTHERN,
            tags=None,
            entity_id=None
        )
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_set_state_with_invalid_category(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test state setting with invalid category string."""
        mock_get_manager.return_value = mock_manager
        mock_manager.set_state.return_value = sample_state_variable
        
        result = WorldStateAPI.set_state(
            key="test.key",
            value="test_value",
            category="INVALID_CATEGORY"
        )
        
        assert result == sample_state_variable
        # Should default to OTHER for invalid category
        mock_manager.set_state.assert_called_once_with(
            key="test.key",
            value="test_value",
            category=StateCategory.OTHER,
            region=WorldRegion.GLOBAL,
            tags=None,
            entity_id=None
        )
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_set_state_with_invalid_region(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test state setting with invalid region string."""
        mock_get_manager.return_value = mock_manager
        mock_manager.set_state.return_value = sample_state_variable
        
        result = WorldStateAPI.set_state(
            key="test.key",
            value="test_value",
            region="INVALID_REGION"
        )
        
        assert result == sample_state_variable
        # Should default to GLOBAL for invalid region
        mock_manager.set_state.assert_called_once_with(
            key="test.key",
            value="test_value",
            category=StateCategory.OTHER,
            region=WorldRegion.GLOBAL,
            tags=None,
            entity_id=None
        )


class TestGetState: pass
    """Test the get_state method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_state_success(self, mock_get_manager, mock_manager): pass
        """Test successful state retrieval."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_state.return_value = "test_value"
        
        result = WorldStateAPI.get_state("test.key")
        
        assert result == "test_value"
        mock_manager.get_state.assert_called_once_with("test.key", None)
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_state_with_default(self, mock_get_manager, mock_manager): pass
        """Test state retrieval with default value."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_state.return_value = "default_value"
        
        result = WorldStateAPI.get_state("test.key", "default_value")
        
        assert result == "default_value"
        mock_manager.get_state.assert_called_once_with("test.key", "default_value")


class TestGetStateVariable: pass
    """Test the get_state_variable method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_state_variable_success(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test successful state variable retrieval."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_state_variable.return_value = sample_state_variable
        
        result = WorldStateAPI.get_state_variable("test.key")
        
        assert result == sample_state_variable
        mock_manager.get_state_variable.assert_called_once_with("test.key")
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_state_variable_not_found(self, mock_get_manager, mock_manager): pass
        """Test state variable retrieval when not found."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_state_variable.return_value = None
        
        result = WorldStateAPI.get_state_variable("nonexistent.key")
        
        assert result is None
        mock_manager.get_state_variable.assert_called_once_with("nonexistent.key")


class TestDeleteState: pass
    """Test the delete_state method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_delete_state_success(self, mock_get_manager, mock_manager): pass
        """Test successful state deletion."""
        mock_get_manager.return_value = mock_manager
        mock_manager.delete_state.return_value = True
        
        result = WorldStateAPI.delete_state("test.key")
        
        assert result is True
        mock_manager.delete_state.assert_called_once_with("test.key", None)
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_delete_state_with_entity_id(self, mock_get_manager, mock_manager): pass
        """Test state deletion with entity ID."""
        mock_get_manager.return_value = mock_manager
        mock_manager.delete_state.return_value = True
        
        result = WorldStateAPI.delete_state("test.key", "entity123")
        
        assert result is True
        mock_manager.delete_state.assert_called_once_with("test.key", "entity123")
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_delete_state_not_found(self, mock_get_manager, mock_manager): pass
        """Test state deletion when key not found."""
        mock_get_manager.return_value = mock_manager
        mock_manager.delete_state.return_value = False
        
        result = WorldStateAPI.delete_state("nonexistent.key")
        
        assert result is False
        mock_manager.delete_state.assert_called_once_with("nonexistent.key", None)


class TestGetHistory: pass
    """Test the get_history method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_history_success(self, mock_get_manager, mock_manager, sample_change_record): pass
        """Test successful history retrieval."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_history.return_value = [sample_change_record]
        
        result = WorldStateAPI.get_history("test.key")
        
        assert result == [sample_change_record]
        mock_manager.get_history.assert_called_once_with("test.key")
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_history_empty(self, mock_get_manager, mock_manager): pass
        """Test history retrieval when no history exists."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_history.return_value = []
        
        result = WorldStateAPI.get_history("test.key")
        
        assert result == []
        mock_manager.get_history.assert_called_once_with("test.key")


class TestGetValueAtTime: pass
    """Test the get_value_at_time method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_value_at_time_success(self, mock_get_manager, mock_manager): pass
        """Test successful value retrieval at specific time."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_value_at_time.return_value = "historical_value"
        timestamp = datetime.utcnow()
        
        result = WorldStateAPI.get_value_at_time("test.key", timestamp)
        
        assert result == "historical_value"
        mock_manager.get_value_at_time.assert_called_once_with("test.key", timestamp, None)
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_value_at_time_with_default(self, mock_get_manager, mock_manager): pass
        """Test value retrieval at time with default."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_value_at_time.return_value = "default_value"
        timestamp = datetime.utcnow()
        
        result = WorldStateAPI.get_value_at_time("test.key", timestamp, "default_value")
        
        assert result == "default_value"
        mock_manager.get_value_at_time.assert_called_once_with("test.key", timestamp, "default_value")


class TestGetValueAtVersion: pass
    """Test the get_value_at_version method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_value_at_version_success(self, mock_get_manager, mock_manager): pass
        """Test successful value retrieval at specific version."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_value_at_version.return_value = "version_value"
        
        result = WorldStateAPI.get_value_at_version("test.key", 1)
        
        assert result == "version_value"
        mock_manager.get_value_at_version.assert_called_once_with("test.key", 1, None)
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_value_at_version_with_default(self, mock_get_manager, mock_manager): pass
        """Test value retrieval at version with default."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_value_at_version.return_value = "default_value"
        
        result = WorldStateAPI.get_value_at_version("test.key", 999, "default_value")
        
        assert result == "default_value"
        mock_manager.get_value_at_version.assert_called_once_with("test.key", 999, "default_value")


class TestQueryByCategory: pass
    """Test the query_by_category method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_query_by_category_enum(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test querying by category enum."""
        mock_get_manager.return_value = mock_manager
        mock_manager.query_state_by_category.return_value = {"test.key": sample_state_variable}
        
        result = WorldStateAPI.query_by_category(StateCategory.POLITICAL)
        
        assert result == {"test.key": sample_state_variable}
        mock_manager.query_state_by_category.assert_called_once_with(StateCategory.POLITICAL)
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_query_by_category_string(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test querying by category string."""
        mock_get_manager.return_value = mock_manager
        mock_manager.query_state_by_category.return_value = {"test.key": sample_state_variable}
        
        result = WorldStateAPI.query_by_category("POLITICAL")
        
        assert result == {"test.key": sample_state_variable}
        mock_manager.query_state_by_category.assert_called_once_with(StateCategory.POLITICAL)
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_query_by_category_invalid_string(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test querying by invalid category string."""
        mock_get_manager.return_value = mock_manager
        mock_manager.query_state_by_category.return_value = {"test.key": sample_state_variable}
        
        result = WorldStateAPI.query_by_category("INVALID_CATEGORY")
        
        assert result == {"test.key": sample_state_variable}
        # Should default to OTHER for invalid category
        mock_manager.query_state_by_category.assert_called_once_with(StateCategory.OTHER)


class TestQueryByRegion: pass
    """Test the query_by_region method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_query_by_region_enum(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test querying by region enum."""
        mock_get_manager.return_value = mock_manager
        mock_manager.query_state_by_region.return_value = {"test.key": sample_state_variable}
        
        result = WorldStateAPI.query_by_region(WorldRegion.NORTHERN)
        
        assert result == {"test.key": sample_state_variable}
        mock_manager.query_state_by_region.assert_called_once_with(WorldRegion.NORTHERN)
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_query_by_region_string(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test querying by region string."""
        mock_get_manager.return_value = mock_manager
        mock_manager.query_state_by_region.return_value = {"test.key": sample_state_variable}
        
        result = WorldStateAPI.query_by_region("NORTHERN")
        
        assert result == {"test.key": sample_state_variable}
        mock_manager.query_state_by_region.assert_called_once_with(WorldRegion.NORTHERN)
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_query_by_region_invalid_string(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test querying by invalid region string."""
        mock_get_manager.return_value = mock_manager
        mock_manager.query_state_by_region.return_value = {"test.key": sample_state_variable}
        
        result = WorldStateAPI.query_by_region("INVALID_REGION")
        
        assert result == {"test.key": sample_state_variable}
        # Should default to GLOBAL for invalid region
        mock_manager.query_state_by_region.assert_called_once_with(WorldRegion.GLOBAL)


class TestQueryByTags: pass
    """Test the query_by_tags method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_query_by_tags_match_all(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test querying by tags with match all."""
        mock_get_manager.return_value = mock_manager
        mock_manager.query_state_by_tags.return_value = {"test.key": sample_state_variable}
        
        result = WorldStateAPI.query_by_tags(["test", "sample"], False)
        
        assert result == {"test.key": sample_state_variable}
        mock_manager.query_state_by_tags.assert_called_once_with(["test", "sample"], False)
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_query_by_tags_match_any(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test querying by tags with match any."""
        mock_get_manager.return_value = mock_manager
        mock_manager.query_state_by_tags.return_value = {"test.key": sample_state_variable}
        
        result = WorldStateAPI.query_by_tags(["test", "sample"], True)
        
        assert result == {"test.key": sample_state_variable}
        mock_manager.query_state_by_tags.assert_called_once_with(["test", "sample"], True)


class TestQueryByPrefix: pass
    """Test the query_by_prefix method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_query_by_prefix(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test querying by prefix."""
        mock_get_manager.return_value = mock_manager
        mock_manager.query_state_by_prefix.return_value = {"test.key": sample_state_variable}
        
        result = WorldStateAPI.query_by_prefix("test")
        
        assert result == {"test.key": sample_state_variable}
        mock_manager.query_state_by_prefix.assert_called_once_with("test")


class TestGetSnapshot: pass
    """Test the get_snapshot method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_snapshot_current(self, mock_get_manager, mock_manager): pass
        """Test getting current snapshot."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_state_snapshot.return_value = {"test.key": "test_value"}
        
        result = WorldStateAPI.get_snapshot()
        
        assert result == {"test.key": "test_value"}
        mock_manager.get_state_snapshot.assert_called_once_with(None)
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_snapshot_at_time(self, mock_get_manager, mock_manager): pass
        """Test getting snapshot at specific time."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_state_snapshot.return_value = {"test.key": "historical_value"}
        timestamp = datetime.utcnow()
        
        result = WorldStateAPI.get_snapshot(timestamp)
        
        assert result == {"test.key": "historical_value"}
        mock_manager.get_state_snapshot.assert_called_once_with(timestamp)


class TestCreateSnapshot: pass
    """Test the create_snapshot method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_create_snapshot_no_metadata(self, mock_get_manager, mock_manager): pass
        """Test creating snapshot without metadata."""
        mock_get_manager.return_value = mock_manager
        mock_manager._state_variables = {"test.key": Mock(value="test_value")}
        mock_manager._next_version = 2
        
        result = WorldStateAPI.create_snapshot()
        
        assert isinstance(result, WorldStateSnapshot)
        assert result.variables == {"test.key": "test_value"}
        assert result.version == 2
        assert result.metadata == {}
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_create_snapshot_with_metadata(self, mock_get_manager, mock_manager): pass
        """Test creating snapshot with metadata."""
        mock_get_manager.return_value = mock_manager
        mock_manager._state_variables = {"test.key": Mock(value="test_value")}
        mock_manager._next_version = 2
        metadata = {"purpose": "testing", "author": "test_user"}
        
        result = WorldStateAPI.create_snapshot(metadata)
        
        assert isinstance(result, WorldStateSnapshot)
        assert result.variables == {"test.key": "test_value"}
        assert result.version == 2
        assert result.metadata == metadata


class TestGetChangesInTimespan: pass
    """Test the get_changes_in_timespan method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_changes_in_timespan(self, mock_get_manager, mock_manager, sample_change_record): pass
        """Test getting changes in timespan."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_changes_in_timespan.return_value = [sample_change_record]
        
        start_time = datetime.utcnow() - timedelta(hours=1)
        end_time = datetime.utcnow()
        
        result = WorldStateAPI.get_changes_in_timespan(start_time, end_time)
        
        assert result == [sample_change_record]
        mock_manager.get_changes_in_timespan.assert_called_once_with(start_time, end_time)


class TestSaveState: pass
    """Test the save_state method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_save_state_success(self, mock_get_manager, mock_manager): pass
        """Test successful state saving."""
        mock_get_manager.return_value = mock_manager
        mock_manager.save_state_to_db.return_value = True
        
        result = WorldStateAPI.save_state()
        
        assert result is True
        mock_manager.save_state_to_db.assert_called_once()
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_save_state_failure(self, mock_get_manager, mock_manager): pass
        """Test state saving failure."""
        mock_get_manager.return_value = mock_manager
        mock_manager.save_state_to_db.return_value = False
        
        result = WorldStateAPI.save_state()
        
        assert result is False
        mock_manager.save_state_to_db.assert_called_once()


class TestLoadState: pass
    """Test the load_state method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_load_state_success(self, mock_get_manager, mock_manager): pass
        """Test successful state loading."""
        mock_get_manager.return_value = mock_manager
        mock_manager.load_state_from_db.return_value = True
        
        result = WorldStateAPI.load_state()
        
        assert result is True
        mock_manager.load_state_from_db.assert_called_once()
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_load_state_failure(self, mock_get_manager, mock_manager): pass
        """Test state loading failure."""
        mock_get_manager.return_value = mock_manager
        mock_manager.load_state_from_db.return_value = False
        
        result = WorldStateAPI.load_state()
        
        assert result is False
        mock_manager.load_state_from_db.assert_called_once()


class TestGetAllVariables: pass
    """Test the get_all_variables method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_all_variables(self, mock_get_manager, mock_manager, sample_state_variable): pass
        """Test getting all variables."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_all_state_variables.return_value = {"test.key": sample_state_variable}
        
        result = WorldStateAPI.get_all_variables()
        
        assert result == {"test.key": sample_state_variable}
        mock_manager.get_all_state_variables.assert_called_once()


class TestGetVariableCount: pass
    """Test the get_variable_count method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_variable_count(self, mock_get_manager, mock_manager): pass
        """Test getting variable count."""
        mock_get_manager.return_value = mock_manager
        mock_manager.get_state_count.return_value = 42
        
        result = WorldStateAPI.get_variable_count()
        
        assert result == 42
        mock_manager.get_state_count.assert_called_once()


class TestGetStatistics: pass
    """Test the get_statistics method."""
    
    @patch('backend.systems.world_state.api.state_api.WorldStateAPI.get_manager')
    def test_get_statistics(self, mock_get_manager, mock_manager): pass
        """Test getting statistics."""
        mock_get_manager.return_value = mock_manager
        mock_stats = {
            "total_variables": 100,
            "total_history_entries": 500,
            "categories": {"POLITICAL": 20, "ECONOMIC": 30},
            "regions": {"NORTHERN": 40, "SOUTHERN": 60}
        }
        mock_manager.get_statistics.return_value = mock_stats
        
        result = WorldStateAPI.get_statistics()
        
        assert result == mock_stats
        mock_manager.get_statistics.assert_called_once()


# Run the tests
if __name__ == "__main__": pass
    pytest.main([__file__, "-v"]) 