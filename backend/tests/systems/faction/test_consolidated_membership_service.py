from backend.systems.schemas.faction_types import FactionType
from backend.systems.schemas.faction_types import FactionType
from backend.systems.schemas.faction_types import FactionType
from backend.systems.schemas.faction_types import FactionType
from backend.systems.schemas.faction_types import FactionType
from backend.systems.schemas.faction_types import FactionType
from typing import Type
"""
Comprehensive tests for ConsolidatedMembershipService.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session

from backend.systems.faction.services.consolidated_membership_service import (
    ConsolidatedMembershipService,
)
from backend.systems.faction.services.consolidated_faction_service import (
    FactionNotFoundError,
    MembershipNotFoundError,
)
from backend.systems.faction.models.faction import Faction, FactionMembership
from backend.systems.faction.schemas.faction_types import FactionType, FactionAlignment


class TestAssignFactionToCharacter: pass
    """Test faction assignment functionality."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_faction(self): pass
        """Create a sample faction."""
        faction = Mock(spec=Faction)
        faction.id = 1
        faction.name = "Test Guild"
        return faction

    def test_assign_faction_to_character_new_membership(self, mock_db, sample_faction): pass
        """Test creating new faction membership."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_faction,  # faction exists
            None  # no existing membership
        ]

        # Execute
        result = ConsolidatedMembershipService.assign_faction_to_character(
            mock_db,
            faction_id=1,
            character_id=100,
            loyalty=75,
            role="officer",
            metadata={"join_reason": "recruited"}
        )

        # Verify
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert result.faction_id == 1
        assert result.character_id == 100
        assert result.reputation == 75
        assert result.role == "officer"

    def test_assign_faction_to_character_update_existing(self, mock_db, sample_faction): pass
        """Test updating existing faction membership."""
        # Setup
        existing_membership = Mock(spec=FactionMembership)
        existing_membership.faction_id = 1
        existing_membership.character_id = 100
        existing_membership.role = "member"
        existing_membership.reputation = 50
        existing_membership.metadata = {}

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_faction,  # faction exists
            existing_membership  # existing membership found
        ]

        # Execute
        result = ConsolidatedMembershipService.assign_faction_to_character(
            mock_db,
            faction_id=1,
            character_id=100,
            loyalty=80,
            role="lieutenant",
            metadata={"promotion": "field_promotion"}
        )

        # Verify
        assert result == existing_membership
        assert existing_membership.role == "lieutenant"
        assert existing_membership.reputation == 80
        assert existing_membership.is_active is True
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(existing_membership)

    def test_assign_faction_to_character_faction_not_found(self, mock_db): pass
        """Test assigning character to non-existent faction."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute & Verify
        with pytest.raises(FactionNotFoundError, match="Faction 999 not found"): pass
            ConsolidatedMembershipService.assign_faction_to_character(
                mock_db, faction_id=999, character_id=100
            )

    def test_assign_faction_to_character_default_values(self, mock_db, sample_faction): pass
        """Test faction assignment with default values."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_faction,  # faction exists
            None  # no existing membership
        ]

        # Execute
        result = ConsolidatedMembershipService.assign_faction_to_character(
            mock_db, faction_id=1, character_id=100
        )

        # Verify defaults
        assert result.reputation == 50  # Default loyalty
        assert result.role == "member"  # Default role
        assert result.rank == 1  # Starting rank
        assert result.is_active is True


class TestGetFactionMembers: pass
    """Test faction member retrieval functionality."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_faction(self): pass
        """Create a sample faction."""
        faction = Mock(spec=Faction)
        faction.id = 1
        faction.name = "Test Guild"
        return faction

    @pytest.fixture
    def sample_memberships(self): pass
        """Create sample memberships."""
        memberships = []
        for i in range(3): pass
            membership = Mock(spec=FactionMembership)
            membership.id = i + 1
            membership.faction_id = 1
            membership.character_id = 100 + i
            membership.role = "member" if i < 2 else "officer"
            membership.reputation = 50 + (i * 15)
            membership.is_active = True
            membership.metadata = {"is_public": True}
            memberships.append(membership)
        return memberships

    def test_get_faction_members_success(self, mock_db, sample_faction, sample_memberships): pass
        """Test successful faction member retrieval."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_faction
        mock_db.query.return_value.filter.return_value.all.return_value = sample_memberships

        # Execute
        result = ConsolidatedMembershipService.get_faction_members(mock_db, faction_id=1)

        # Verify
        assert result == sample_memberships

    def test_get_faction_members_with_filters(self, mock_db, sample_faction, sample_memberships): pass
        """Test faction member retrieval with filters."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_faction
        
        # Create filtered mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # Allow chaining
        mock_query.all.return_value = [sample_memberships[2]]  # Only officer
        mock_db.query.return_value.filter.return_value = mock_query

        # Execute
        result = ConsolidatedMembershipService.get_faction_members(
            mock_db, faction_id=1, min_loyalty=70, role="officer"
        )

        # Verify
        assert len(result) == 1
        assert result[0].role == "officer"

    def test_get_faction_members_faction_not_found(self, mock_db): pass
        """Test getting members of non-existent faction."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute & Verify
        with pytest.raises(FactionNotFoundError, match="Faction 999 not found"): pass
            ConsolidatedMembershipService.get_faction_members(mock_db, faction_id=999)

    def test_get_faction_members_filter_by_public_status(self, mock_db, sample_faction, sample_memberships): pass
        """Test filtering members by public/secret status."""
        # Setup - add secret member
        secret_member = Mock(spec=FactionMembership)
        secret_member.metadata = {"is_public": False}
        sample_memberships.append(secret_member)

        mock_db.query.return_value.filter.return_value.first.return_value = sample_faction
        mock_db.query.return_value.filter.return_value.all.return_value = sample_memberships

        # Execute - get only public members
        result = ConsolidatedMembershipService.get_faction_members(
            mock_db, faction_id=1, is_public=True
        )

        # Verify - should exclude the secret member
        assert len(result) == 3  # Original 3 public members


class TestGetCharacterFactions: pass
    """Test character faction retrieval functionality."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_memberships(self): pass
        """Create sample character memberships."""
        memberships = []
        for i in range(3): pass
            membership = Mock(spec=FactionMembership)
            membership.id = i + 1
            membership.faction_id = i + 1
            membership.character_id = 100
            membership.reputation = 40 + (i * 20)
            membership.is_active = True
            membership.metadata = {"is_public": i != 2}  # Third one is secret
            memberships.append(membership)
        return memberships

    def test_get_character_factions_success(self, mock_db, sample_memberships): pass
        """Test successful retrieval of character factions."""
        # Setup metadata for filtering
        sample_memberships[0].metadata = {"is_public": True}
        sample_memberships[1].metadata = {"is_public": True}
        sample_memberships[2].metadata = {"is_public": False}  # Secret membership
        
        mock_db.query.return_value.filter.return_value.all.return_value = sample_memberships

        # Execute - should filter out secret membership by default
        result = ConsolidatedMembershipService.get_character_factions(
            mock_db, character_id=100
        )

        # Verify - should only return 2 public memberships
        assert len(result) == 2
        assert result[0] == sample_memberships[0]
        assert result[1] == sample_memberships[1]

    def test_get_character_factions_with_loyalty_filter(self, mock_db, sample_memberships): pass
        """Test filtering character factions by loyalty."""
        # Setup
        sample_memberships[0].reputation = 30
        sample_memberships[1].reputation = 60
        sample_memberships[2].reputation = 90
        # Set metadata for all
        for membership in sample_memberships: pass
            membership.metadata = {"is_public": True}

        # The method calls query.filter then query.all(), but loyalty filtering is done in SQL
        # Mock the query chain to return only high-loyalty memberships
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [sample_memberships[2]]  # Only the high-loyalty one

        # Execute
        result = ConsolidatedMembershipService.get_character_factions(
            mock_db, character_id=100, min_loyalty=50
        )

        # Verify - should only return the high-loyalty membership
        assert len(result) == 1
        assert result[0] == sample_memberships[2]

    def test_get_character_factions_exclude_secret(self, mock_db, sample_memberships): pass
        """Test excluding secret faction memberships."""
        # Setup
        mock_db.query.return_value.filter.return_value.all.return_value = sample_memberships

        # Execute - don't include secret memberships
        result = ConsolidatedMembershipService.get_character_factions(
            mock_db, character_id=100, include_secret=False
        )

        # Verify - should exclude the secret membership
        assert len(result) == 2  # Exclude the secret one


class TestUpdateCharacterLoyalty: pass
    """Test loyalty update functionality."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_membership(self): pass
        """Create a sample membership."""
        membership = Mock(spec=FactionMembership)
        membership.faction_id = 1
        membership.character_id = 100
        membership.reputation = 60
        membership.history = {}  # Initialize as dict, not list
        return membership

    def test_update_character_loyalty_increase(self, mock_db, sample_membership): pass
        """Test increasing character loyalty."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_membership

        # Execute
        result = ConsolidatedMembershipService.update_character_loyalty(
            mock_db, faction_id=1, character_id=100, delta=15, reason="completed_quest"
        )

        # Verify
        assert result == sample_membership
        assert sample_membership.reputation == 75  # 60 + 15
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_membership)

    def test_update_character_loyalty_decrease(self, mock_db, sample_membership): pass
        """Test decreasing character loyalty."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_membership

        # Execute
        result = ConsolidatedMembershipService.update_character_loyalty(
            mock_db, faction_id=1, character_id=100, delta=-20, reason="betrayal"
        )

        # Verify
        assert sample_membership.reputation == 40  # 60 - 20

    def test_update_character_loyalty_clamp_bounds(self, mock_db, sample_membership): pass
        """Test loyalty update with clamping to bounds."""
        # Setup
        sample_membership.reputation = 95
        mock_db.query.return_value.filter.return_value.first.return_value = sample_membership

        # Execute - would go over 100
        ConsolidatedMembershipService.update_character_loyalty(
            mock_db, faction_id=1, character_id=100, delta=20
        )

        # Verify clamped to 100
        assert sample_membership.reputation == 100

    def test_update_character_loyalty_membership_not_found(self, mock_db): pass
        """Test updating loyalty for non-existent membership."""
        # Setup - first call checks faction, second checks membership
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            Mock(spec=Faction),  # faction exists
            None  # no membership found
        ]

        # Execute & Verify
        with pytest.raises(MembershipNotFoundError): pass
            ConsolidatedMembershipService.update_character_loyalty(
                mock_db, faction_id=1, character_id=999, delta=10
            )


class TestRemoveCharacterFromFaction: pass
    """Test character removal functionality."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_membership(self): pass
        """Create a sample membership."""
        membership = Mock(spec=FactionMembership)
        membership.faction_id = 1
        membership.character_id = 100
        membership.is_active = True
        membership.history = {}  # Initialize as dict
        membership.metadata = {}
        return membership

    def test_remove_character_from_faction_success(self, mock_db, sample_membership): pass
        """Test successful character removal from faction."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            Mock(spec=Faction),  # faction exists
            sample_membership  # membership found
        ]

        # Execute
        result = ConsolidatedMembershipService.remove_character_from_faction(
            mock_db, faction_id=1, character_id=100, reason="expelled"
        )

        # Verify
        assert result is True
        assert sample_membership.is_active is False
        assert sample_membership.status == "left"
        mock_db.commit.assert_called_once()
        # Note: remove_character_from_faction doesn't call db.refresh

    def test_remove_character_from_faction_membership_not_found(self, mock_db): pass
        """Test removing character from faction when membership doesn't exist."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            Mock(spec=Faction),  # faction exists
            None  # no membership found
        ]

        # Execute
        result = ConsolidatedMembershipService.remove_character_from_faction(
            mock_db, faction_id=1, character_id=999
        )

        # Verify
        assert result is False


class TestSwitchFaction: pass
    """Test faction switching functionality."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_memberships(self): pass
        """Create sample memberships for switching."""
        current_membership = Mock(spec=FactionMembership)
        current_membership.faction_id = 1
        current_membership.character_id = 100
        current_membership.is_active = True

        target_faction = Mock(spec=Faction)
        target_faction.id = 2
        target_faction.name = "Target Guild"

        return current_membership, target_faction

    def test_switch_faction_success(self, mock_db, sample_memberships): pass
        """Test successful faction switching."""
        current_membership, target_faction = sample_memberships

        # Setup - switch_faction makes multiple queries in sequence
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            Mock(spec=Faction),  # current faction exists  
            target_faction,  # target faction exists
            current_membership,  # current membership found
        ]

        # Execute
        result = ConsolidatedMembershipService.switch_faction(
            mock_db,
            character_id=100,
            current_faction_id=1,
            target_faction_id=2,
            affinity=75,
            role="recruit"
        )

        # Verify - check the actual return format
        assert result["success"] is True
        assert result["previous_faction"] == 1  # Not old_faction_id
        assert result["new_faction"] == 2
        assert current_membership.is_active is False  # Left old faction
        mock_db.add.assert_called()  # New membership created

    def test_switch_faction_current_membership_not_found(self, mock_db): pass
        """Test switching when current membership doesn't exist."""
        # Setup - both factions exist but membership doesn't
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            Mock(spec=Faction),  # current faction exists
            Mock(spec=Faction),  # target faction exists
            None,  # no current membership found
        ]

        # Execute & Verify - should raise MembershipNotFoundError, not FactionNotFoundError
        with pytest.raises(MembershipNotFoundError): pass
            ConsolidatedMembershipService.switch_faction(
                mock_db, character_id=100, current_faction_id=1, target_faction_id=2
            )


class TestCalculateFactionSchismProbability: pass
    """Test faction schism calculation functionality."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_faction(self): pass
        """Create a sample faction."""
        faction = Mock(spec=Faction)
        faction.id = 1
        faction.name = "Test Guild"
        faction.state = {"internal_tension": 60.0}
        faction.created_at = datetime.utcnow()
        return faction

    @pytest.fixture
    def sample_memberships(self): pass
        """Create sample faction memberships."""
        memberships = []
        for i in range(5): pass
            membership = Mock(spec=FactionMembership)
            membership.character_id = 100 + i
            membership.reputation = 30 + (i * 15)  # Varying loyalty
            membership.role = "member" if i < 3 else "officer"
            memberships.append(membership)
        return memberships

    def test_calculate_faction_schism_probability_high_tension(self, mock_db, sample_faction, sample_memberships): pass
        """Test schism probability calculation with high tension."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_faction
        # Mock count() to return an integer instead of Mock
        mock_db.query.return_value.filter.return_value.count.return_value = 150  # Large faction

        # Execute
        result = ConsolidatedMembershipService.calculate_faction_schism_probability(
            mock_db, faction_id=1, internal_tension=85.0, schism_threshold=80.0
        )

        # Verify
        assert result["final_probability"] > 0
        assert result["faction_id"] == 1
        assert result["internal_tension"] == 85.0
        assert result["member_count"] == 150

    def test_calculate_faction_schism_probability_low_tension(self, mock_db, sample_faction, sample_memberships): pass
        """Test schism probability calculation with low tension."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = sample_faction
        # Mock count() to return an integer
        mock_db.query.return_value.filter.return_value.count.return_value = 25  # Medium faction

        # Execute
        result = ConsolidatedMembershipService.calculate_faction_schism_probability(
            mock_db, faction_id=1, internal_tension=30.0, schism_threshold=80.0
        )

        # Verify
        assert result["final_probability"] >= 0
        assert result["member_count"] == 25

    def test_calculate_faction_schism_probability_faction_not_found(self, mock_db): pass
        """Test schism calculation for non-existent faction."""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute & Verify
        with pytest.raises(FactionNotFoundError, match="Faction 999 not found"): pass
            ConsolidatedMembershipService.calculate_faction_schism_probability(
                mock_db, faction_id=999
            )


class TestConsolidatedMembershipServiceIntegration: pass
    """Integration tests for the service."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_membership_lifecycle(self, mock_db): pass
        """Test complete membership lifecycle."""
        # Setup
        faction = Mock(spec=Faction)
        faction.id = 1
        faction.name = "Test Guild"

        membership = Mock(spec=FactionMembership)
        membership.faction_id = 1
        membership.character_id = 100
        membership.reputation = 50
        membership.is_active = True
        membership.history = {}  # Initialize as dict
        membership.metadata = {}

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            faction,  # faction exists (assign)
            None,  # no existing membership (assign)
            faction,  # faction exists (update loyalty)
            membership,  # membership exists (update loyalty)
            faction,  # faction exists (remove)
            membership,  # membership exists (remove)
        ]

        # Test 1: Assign character to faction
        assigned = ConsolidatedMembershipService.assign_faction_to_character(
            mock_db, faction_id=1, character_id=100
        )
        assert assigned.faction_id == 1

        # Test 2: Update loyalty
        updated = ConsolidatedMembershipService.update_character_loyalty(
            mock_db, faction_id=1, character_id=100, delta=25
        )
        assert updated.reputation == 75

        # Test 3: Remove from faction
        removed = ConsolidatedMembershipService.remove_character_from_faction(
            mock_db, faction_id=1, character_id=100
        )
        assert removed is True
        assert membership.is_active is False

    def test_error_handling_comprehensive(self, mock_db): pass
        """Test comprehensive error handling."""
        # Setup - no entities exist
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Test various error conditions
        with pytest.raises(FactionNotFoundError): pass
            ConsolidatedMembershipService.assign_faction_to_character(
                mock_db, faction_id=999, character_id=100
            )

        with pytest.raises(FactionNotFoundError): pass
            ConsolidatedMembershipService.get_faction_members(mock_db, faction_id=999)

        # For update_character_loyalty, we need to mock faction existing but membership not
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            Mock(spec=Faction),  # faction exists
            None  # membership doesn't exist
        ]
        
        with pytest.raises(MembershipNotFoundError): pass
            ConsolidatedMembershipService.update_character_loyalty(
                mock_db, faction_id=1, character_id=999, delta=10
            )

        # Reset for faction schism test
        mock_db.query.return_value.filter.return_value.first.side_effect = None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(FactionNotFoundError): pass
            ConsolidatedMembershipService.calculate_faction_schism_probability(
                mock_db, faction_id=999
            )
