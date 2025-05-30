from backend.systems.schemas.faction_types import FactionType
from backend.systems.schemas.faction_types import FactionType
from backend.systems.schemas.faction_types import FactionType
from backend.systems.schemas.faction_types import FactionType
from backend.systems.schemas.faction_types import FactionType
from backend.systems.schemas.faction_types import FactionType
from typing import Type
"""
Comprehensive tests for ConsolidatedFactionService.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session

from backend.systems.faction.services.consolidated_faction_service import (
    ConsolidatedFactionService,
    FactionNotFoundError,
    DuplicateFactionError,
    InvalidFactionOperationError,
)
from backend.systems.faction.models.faction import Faction, FactionMembership
from backend.systems.faction.models.faction_goal import FactionGoal
from backend.systems.faction.schemas.faction_types import FactionType, FactionAlignment


class TestCreateFaction:
    """Test faction creation functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_create_faction_success(self, mock_db):
        """Test successful faction creation."""
        # Setup - no existing faction
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Create a mock faction with proper attributes
        mock_faction = Mock(spec=Faction)
        mock_faction.name = "Test Guild"
        mock_faction.type = "guild"
        mock_faction.resources = {}  # Initialize as empty dict
        mock_faction.territory = {}  # Initialize as empty dict
        mock_faction.state = {}      # Initialize as empty dict
        
        # Mock the Faction constructor to return our mock
        with patch('backend.systems.faction.services.consolidated_faction_service.Faction', return_value=mock_faction):
            # Execute
            result = ConsolidatedFactionService.create_faction(
                mock_db,
                name="Test Guild",
                description="A test guild",
                faction_type=FactionType.GUILD,
                alignment=FactionAlignment.LAWFUL_GOOD,
                influence=75.0,
                resources={"gold": 1000},
                leader_id=1
            )

            # Verify
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
            assert result.name == "Test Guild"
            assert result.type == "guild"

    def test_create_faction_duplicate_name(self, mock_db):
        """Test faction creation with duplicate name."""
        # Setup - existing faction found
        existing_faction = Mock(spec=Faction)
        mock_db.query.return_value.filter.return_value.first.return_value = existing_faction

        # Execute & Verify
        with pytest.raises(DuplicateFactionError, match="Faction with name Test Guild already exists"):
            ConsolidatedFactionService.create_faction(
                mock_db,
                name="Test Guild",
                description="A test guild",
                faction_type="guild"
            )

    def test_create_faction_with_string_type(self, mock_db):
        """Test creating faction with string type instead of enum."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = ConsolidatedFactionService.create_faction(
            mock_db,
            name="Test Guild",
            description="A test guild",
            faction_type="guild",  # String instead of enum
            alignment="lawful_good"  # String instead of enum
        )

        # Verify
        assert result.type == "guild"
        assert result.alignment == "lawful_good"

    def test_create_faction_minimal_params(self, mock_db):
        """Test faction creation with minimal parameters."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = ConsolidatedFactionService.create_faction(
            mock_db,
            name="Minimal Guild",
            description="Basic guild",
            faction_type=FactionType.GUILD
        )

        # Verify minimal fields are set
        assert result.name == "Minimal Guild"
        assert result.influence == 50.0  # Default value


class TestGetFaction:
    """Test faction retrieval functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_faction(self):
        """Create a sample faction."""
        faction = Mock(spec=Faction)
        faction.id = 1
        faction.name = "Test Guild"
        faction.type = "guild"
        return faction

    def test_get_faction_success(self, mock_db, sample_faction):
        """Test successful faction retrieval by ID."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_faction

        # Execute
        result = ConsolidatedFactionService.get_faction(mock_db, 1)

        # Verify
        assert result == sample_faction
        mock_db.query.assert_called_once_with(Faction)

    def test_get_faction_not_found(self, mock_db):
        """Test faction retrieval when faction doesn't exist."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute
        result = ConsolidatedFactionService.get_faction(mock_db, 999)

        # Verify
        assert result is None

    def test_get_faction_by_name_success(self, mock_db, sample_faction):
        """Test successful faction retrieval by name."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_faction

        # Execute
        result = ConsolidatedFactionService.get_faction_by_name(mock_db, "Test Guild")

        # Verify
        assert result == sample_faction

    def test_get_faction_by_name_not_found(self, mock_db):
        """Test faction retrieval by name when faction doesn't exist."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute
        result = ConsolidatedFactionService.get_faction_by_name(mock_db, "Nonexistent Guild")

        # Verify
        assert result is None


class TestGetFactions:
    """Test faction listing with filters."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_factions(self):
        """Create sample factions."""
        factions = []
        for i in range(3):
            faction = Mock(spec=Faction)
            faction.id = i + 1
            faction.name = f"Guild {i + 1}"
            faction.type = "guild"
            faction.is_active = True
            faction.influence = 50.0 + (i * 10)
            factions.append(faction)
        return factions

    def test_get_factions_no_filters(self, mock_db, sample_factions):
        """Test getting all factions without filters."""
        # Setup
        mock_query = Mock()
        mock_query.all.return_value = sample_factions
        mock_db.query.return_value = mock_query

        # Execute
        result = ConsolidatedFactionService.get_factions(mock_db)

        # Verify
        assert result == sample_factions
        mock_db.query.assert_called_once_with(Faction)

    def test_get_factions_with_type_filter(self, mock_db, sample_factions):
        """Test getting factions with type filter."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = sample_factions
        mock_db.query.return_value = mock_query

        # Execute
        result = ConsolidatedFactionService.get_factions(mock_db, faction_type=FactionType.GUILD)

        # Verify
        assert result == sample_factions
        mock_query.filter.assert_called()

    def test_get_factions_with_influence_filter(self, mock_db, sample_factions):
        """Test getting factions with minimum influence filter."""
        # Setup
        filtered_factions = [sample_factions[2]]  # Only the high influence faction
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = filtered_factions
        mock_db.query.return_value = mock_query

        # Execute
        result = ConsolidatedFactionService.get_factions(mock_db, min_influence=65.0)

        # Verify
        assert result == filtered_factions


class TestUpdateFaction:
    """Test faction update functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_faction(self):
        """Create a sample faction."""
        faction = Mock(spec=Faction)
        faction.id = 1
        faction.name = "Test Guild"
        faction.description = "Old description"
        faction.influence = 50.0
        faction.resources = {"gold": 500}
        return faction

    def test_update_faction_success(self, mock_db, sample_faction):
        """Test successful faction update."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_faction

        # Execute
        result = ConsolidatedFactionService.update_faction(
            mock_db, 1, description="New description", influence=75.0
        )

        # Verify
        assert result == sample_faction
        assert sample_faction.description == "New description"
        assert sample_faction.influence == 75.0
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_faction)

    def test_update_faction_not_found(self, mock_db):
        """Test updating faction that doesn't exist."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute & Verify
        with pytest.raises(FactionNotFoundError, match="Faction 999 not found"):
            ConsolidatedFactionService.update_faction(mock_db, 999, description="New description")

    def test_update_faction_resources_merge(self, mock_db, sample_faction):
        """Test that faction resource updates merge correctly."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_faction

        # Execute
        ConsolidatedFactionService.update_faction(
            mock_db, 1, resources={"silver": 200, "gold": 1000}
        )

        # Verify resources are updated
        assert sample_faction.resources["gold"] == 1000  # Updated
        assert sample_faction.resources["silver"] == 200  # Added


class TestDeleteFaction:
    """Test faction deletion functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_faction(self):
        """Create a sample faction."""
        faction = Mock(spec=Faction)
        faction.id = 1
        faction.name = "Test Guild"
        # Initialize state as a dictionary that supports item assignment
        faction.state = {}
        return faction

    def test_delete_faction_success(self, mock_db, sample_faction):
        """Test successful faction deletion (soft delete)."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_faction

        # Execute
        ConsolidatedFactionService.delete_faction(mock_db, 1)

        # Verify soft delete behavior
        assert sample_faction.is_active is False
        assert sample_faction.state["deactivation_reason"] == "admin_delete"
        assert "deactivated_at" in sample_faction.state
        mock_db.commit.assert_called_once()
        # Note: No db.delete call expected for soft deletion

    def test_delete_faction_not_found(self, mock_db):
        """Test deleting faction that doesn't exist."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute & Verify
        with pytest.raises(FactionNotFoundError, match="Faction 999 not found"):
            ConsolidatedFactionService.delete_faction(mock_db, 999)


class TestFactionGoals:
    """Test faction goal functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_faction(self):
        """Create a sample faction."""
        faction = Mock(spec=Faction)
        faction.id = 1
        faction.name = "Test Guild"
        # Initialize goals as a proper dictionary
        faction.goals = {"current": [], "completed": [], "failed": []}
        return faction

    def test_add_faction_goal_success(self, mock_db, sample_faction):
        """Test successful faction goal creation."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_faction
        
        # Create a mock goal
        mock_goal = Mock(spec=FactionGoal)
        mock_goal.id = 1
        mock_goal.title = "Expand Territory"
        mock_goal.priority = 8
        
        # Mock the FactionGoal constructor
        with patch('backend.systems.faction.services.consolidated_faction_service.FactionGoal', return_value=mock_goal):
            # Execute
            result = ConsolidatedFactionService.add_faction_goal(
                mock_db,
                faction_id=1,
                title="Expand Territory",
                description="Gain control of 3 new regions",
                goal_type="territorial",  # This will be mapped to 'type' parameter
                priority=8,
                completion_conditions={"regions_controlled": 3}
            )

            # Verify
            mock_db.add.assert_called_once()
            assert mock_db.commit.call_count == 2  # Called twice in the method
            mock_db.refresh.assert_called_once()
            assert result.title == "Expand Territory"
            assert result.priority == 8

    def test_add_faction_goal_faction_not_found(self, mock_db):
        """Test adding goal to non-existent faction."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute & Verify
        with pytest.raises(FactionNotFoundError, match="Faction 999 not found"):
            ConsolidatedFactionService.add_faction_goal(
                mock_db,
                faction_id=999,
                title="Test Goal",
                description="Test description",
                goal_type="test"
            )


class TestFactionUtilities:
    """Test utility functions."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_assign_faction_to_poi_success(self, mock_db):
        """Test successful faction assignment to POI."""
        # Setup
        faction = Mock(spec=Faction)
        faction.id = 1
        faction.name = "Test Guild"
        faction.territory = {"pois": []}  # Initialize territory as dict with pois list
        mock_db.query.return_value.filter.return_value.first.return_value = faction

        # Execute
        result = ConsolidatedFactionService.assign_faction_to_poi(
            mock_db, faction_id=1, poi_id=5, control_level=75
        )

        # Verify
        assert result["success"] is True
        assert result["faction_id"] == 1
        assert result["poi_id"] == 5
        assert result["control_level"] == 75

    def test_assign_faction_to_poi_faction_not_found(self, mock_db):
        """Test assigning non-existent faction to POI."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute & Verify
        with pytest.raises(FactionNotFoundError, match="Faction 999 not found"):
            ConsolidatedFactionService.assign_faction_to_poi(mock_db, faction_id=999, poi_id=5)

    def test_calculate_affinity_success(self, mock_db):
        """Test affinity calculation."""
        # Setup - mock get_faction call to return a faction
        faction = Mock(spec=Faction)
        faction.id = 1
        faction.alignment = "lawful_good"
        faction.influence = 60.0
        
        # Mock the get_faction method to return our faction
        with patch.object(ConsolidatedFactionService, 'get_faction', return_value=faction):
            # Mock membership query to return None
            mock_db.query.return_value.filter.return_value.first.return_value = None

            # Execute
            with patch('random.randint', return_value=10):
                result = ConsolidatedFactionService.calculate_affinity(mock_db, character_id=1, faction_id=1)

            # Verify
            assert isinstance(result, int)
            assert 0 <= result <= 100

    def test_calculate_affinity_faction_not_found(self, mock_db):
        """Test affinity calculation with non-existent faction."""
        # The calculate_affinity method doesn't check faction existence,
        # but we still need to handle the membership query properly
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute - this should not raise an error since the method doesn't validate faction existence
        with patch('random.randint', return_value=10):
            result = ConsolidatedFactionService.calculate_affinity(mock_db, character_id=1, faction_id=999)
        
        # Verify it returns a valid affinity score even for non-existent factions
        assert isinstance(result, int)
        assert 0 <= result <= 100

    def test_propagate_faction_influence(self, mock_db):
        """Test faction influence propagation."""
        # Setup
        factions = []
        for i in range(3):
            faction = Mock(spec=Faction)
            faction.id = i + 1
            faction.influence = 60.0 + (i * 10)
            faction.territory = {"pois": [{"id": f"poi_{i}", "control_level": 5 + i}]}
            factions.append(faction)

        # Return the actual list instead of mock
        mock_db.query.return_value.filter.return_value.all.return_value = factions

        # Execute
        result = ConsolidatedFactionService.propagate_faction_influence(mock_db, decay_rate=0.1)

        # Verify
        assert isinstance(result, list)
        assert len(result) == 3
        for update in result:
            assert "faction_id" in update
            assert "poi_id" in update
            assert "influence_level" in update


class TestConsolidatedFactionServiceIntegration:
    """Integration tests for the service."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_faction_lifecycle(self, mock_db):
        """Test complete faction lifecycle."""
        # Setup for creation
        faction_mock = Mock(spec=Faction)
        faction_mock.id = 1
        faction_mock.name = "Test Guild"
        faction_mock.description = "Updated description"
        faction_mock.state = {}
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            None,  # No existing faction (create)
            faction_mock,  # Faction exists (update)
            faction_mock,  # Faction exists (delete)
        ]

        # Test 1: Create faction
        faction = ConsolidatedFactionService.create_faction(
            mock_db,
            name="Test Guild",
            description="A test guild",
            faction_type=FactionType.GUILD
        )
        assert faction.name == "Test Guild"

        # Test 2: Update faction
        updated_faction = ConsolidatedFactionService.update_faction(
            mock_db, 1, description="Updated description"
        )
        assert updated_faction.description == "Updated description"

        # Test 3: Delete faction
        ConsolidatedFactionService.delete_faction(mock_db, 1)
        assert faction_mock.is_active is False

    def test_error_handling_comprehensive(self, mock_db):
        """Test comprehensive error handling."""
        # Setup - no factions exist for all queries
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Test various error conditions
        with pytest.raises(FactionNotFoundError):
            ConsolidatedFactionService.update_faction(mock_db, 999, name="New Name")

        with pytest.raises(FactionNotFoundError):
            ConsolidatedFactionService.delete_faction(mock_db, 999)

        with pytest.raises(FactionNotFoundError):
            ConsolidatedFactionService.add_faction_goal(
                mock_db, 999, "Goal", "Description", "type"
            )

        # Note: calculate_affinity doesn't validate faction existence,
        # so it won't raise FactionNotFoundError
