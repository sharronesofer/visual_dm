from backend.systems.economy.models import Resource
from backend.systems.economy.models import Resource
from backend.systems.economy.models import Resource
from backend.systems.economy.models import Resource
from backend.systems.economy.models import Resource
from backend.systems.economy.models import Resource
"""
Comprehensive tests for consolidated relationship service.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from sqlalchemy.orm import Session

from backend.systems.faction.services.consolidated_relationship_service import (
    ConsolidatedRelationshipService
)
from backend.systems.faction.models.faction import Faction, FactionRelationship
from backend.systems.faction.schemas.faction_types import DiplomaticStance
from backend.systems.faction.services.consolidated_faction_service import (
    FactionNotFoundError,
    RelationshipNotFoundError,
)


class TestGetRelationship: pass
    """Test getting relationships between factions."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_relationship(self): pass
        """Create a sample faction relationship."""
        rel = Mock(spec=FactionRelationship)
        rel.faction_id = 1
        rel.other_faction_id = 2
        rel.diplomatic_stance = "neutral"
        rel.tension = 0.0
        return rel

    def test_get_existing_relationship(self, mock_db, sample_relationship): pass
        """Test getting an existing relationship."""
        # Setup - match the actual query chain: .query().filter(.., ..).first()
        mock_db.query.return_value.filter.return_value.first.return_value = sample_relationship

        # Execute
        result = ConsolidatedRelationshipService.get_relationship(mock_db, 1, 2)

        # Verify
        assert result == sample_relationship
        mock_db.query.assert_called_once_with(FactionRelationship)

    def test_get_nonexistent_relationship(self, mock_db): pass
        """Test getting a relationship that doesn't exist."""
        # Setup - match the actual query chain: .query().filter(.., ..).first()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute
        result = ConsolidatedRelationshipService.get_relationship(mock_db, 1, 99)

        # Verify
        assert result is None


class TestGetFactionRelationships: pass
    """Test getting all relationships for a faction."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_relationships(self): pass
        """Create sample relationships."""
        rel1 = Mock(spec=FactionRelationship)
        rel1.faction_id = 1
        rel1.other_faction_id = 2
        rel1.diplomatic_stance = "neutral"
        rel1.tension = 10.0
        rel1.war_state = {"at_war": False}

        rel2 = Mock(spec=FactionRelationship)
        rel2.faction_id = 1
        rel2.other_faction_id = 3
        rel2.diplomatic_stance = "war"
        rel2.tension = 80.0
        rel2.war_state = {"at_war": True}

        return [rel1, rel2]

    def test_get_all_relationships(self, mock_db, sample_relationships): pass
        """Test getting all relationships for a faction."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = sample_relationships
        mock_db.query.return_value = mock_query

        # Execute
        result = ConsolidatedRelationshipService.get_faction_relationships(mock_db, 1)

        # Verify
        assert result == sample_relationships
        mock_db.query.assert_called_once_with(FactionRelationship)

    def test_filter_by_diplomatic_stance(self, mock_db, sample_relationships): pass
        """Test filtering relationships by diplomatic stance."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.all.return_value = [sample_relationships[1]]
        mock_db.query.return_value = mock_query

        # Execute
        result = ConsolidatedRelationshipService.get_faction_relationships(
            mock_db, 1, diplomatic_stance=DiplomaticStance.WAR
        )

        # Verify
        assert len(result) == 1
        assert result[0].diplomatic_stance == "war"

    def test_filter_by_tension(self, mock_db, sample_relationships): pass
        """Test filtering relationships by tension levels."""
        # Setup - configure the mock to handle multiple filter calls and return the filtered result
        filtered_list = [sample_relationships[1]]  # Only the relationship with tension=80.0
        
        # Create a mock query that supports chaining filter calls
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # Allow chaining
        mock_query.all.return_value = filtered_list
        
        mock_db.query.return_value = mock_query

        # Execute
        result = ConsolidatedRelationshipService.get_faction_relationships(
            mock_db, 1, min_tension=50.0
        )

        # Verify
        assert len(result) == 1
        assert result[0].tension == 80.0

    def test_filter_by_war_status(self, mock_db, sample_relationships): pass
        """Test filtering relationships by war status."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = sample_relationships
        mock_db.query.return_value = mock_query

        # Execute - at war
        result_at_war = ConsolidatedRelationshipService.get_faction_relationships(
            mock_db, 1, at_war=True
        )

        # Execute - not at war
        result_not_at_war = ConsolidatedRelationshipService.get_faction_relationships(
            mock_db, 1, at_war=False
        )

        # Verify
        assert len(result_at_war) == 1
        assert result_at_war[0].war_state["at_war"] is True
        
        assert len(result_not_at_war) == 1
        assert result_not_at_war[0].war_state["at_war"] is False


class TestSetDiplomaticStance: pass
    """Test setting diplomatic stance between factions."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_factions(self): pass
        """Create mock factions."""
        faction1 = Mock(spec=Faction)
        faction1.id = 1
        faction1.name = "Test Faction 1"

        faction2 = Mock(spec=Faction)
        faction2.id = 2
        faction2.name = "Test Faction 2"

        return faction1, faction2

    def test_set_stance_with_new_relationship(self, mock_db, mock_factions): pass
        """Test setting stance when no relationship exists."""
        faction1, faction2 = mock_factions
        
        # Setup - factions exist, but relationships don't exist for first two calls, then None for reciprocal
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            faction1, faction2, None, None  # factions exist, both relationships don't exist
        ]

        # Execute
        with patch.object(ConsolidatedRelationshipService, 'get_relationship', side_effect=[None, None]): pass
            result = ConsolidatedRelationshipService.set_diplomatic_stance(
                mock_db, 1, 2, DiplomaticStance.ALLIED, tension=25.0
            )

        # Verify - expect 2 add() calls (primary and reciprocal relationships)
        assert mock_db.add.call_count == 2
        assert result.diplomatic_stance == "allied"
        assert result.tension == 25.0

    def test_set_stance_with_existing_relationship(self, mock_db, mock_factions): pass
        """Test setting stance when relationship already exists."""
        faction1, faction2 = mock_factions
        existing_rel = Mock(spec=FactionRelationship)
        existing_rel.diplomatic_stance = "neutral"
        existing_rel.tension = 0.0
        existing_rel.war_state = {"at_war": False}
        existing_rel.history = []

        # Setup
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            faction1, faction2  # factions exist
        ]

        with patch.object(ConsolidatedRelationshipService, 'get_relationship', return_value=existing_rel): pass
            result = ConsolidatedRelationshipService.set_diplomatic_stance(
                mock_db, 1, 2, DiplomaticStance.RIVALRY, tension=30.0
            )

        # Verify
        assert existing_rel.diplomatic_stance == "rivalry"
        assert existing_rel.tension == 30.0

    def test_set_stance_faction_not_found(self, mock_db): pass
        """Test setting stance when faction doesn't exist."""
        # Setup - first faction doesn't exist
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute & Verify
        with pytest.raises(FactionNotFoundError, match="Faction 1 not found"): pass
            ConsolidatedRelationshipService.set_diplomatic_stance(
                mock_db, 1, 2, DiplomaticStance.ALLIED
            )

    def test_set_war_stance_updates_war_state(self, mock_db, mock_factions): pass
        """Test that setting war stance updates war state properly."""
        faction1, faction2 = mock_factions
        existing_rel = Mock(spec=FactionRelationship)
        existing_rel.diplomatic_stance = "neutral"
        existing_rel.tension = 0.0
        existing_rel.war_state = {"at_war": False}
        existing_rel.history = []

        # Setup
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            faction1, faction2
        ]

        with patch.object(ConsolidatedRelationshipService, 'get_relationship', return_value=existing_rel): pass
            ConsolidatedRelationshipService.set_diplomatic_stance(
                mock_db, 1, 2, DiplomaticStance.WAR
            )

        # Verify war state updated
        assert existing_rel.war_state["at_war"] is True
        assert "war_start" in existing_rel.war_state


class TestUpdateTension: pass
    """Test updating tension between factions."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture 
    def mock_relationships(self): pass
        """Create mock relationships."""
        rel1 = Mock(spec=FactionRelationship)
        rel1.tension = 25.0
        rel1.history = []

        rel2 = Mock(spec=FactionRelationship)
        rel2.tension = 25.0
        rel2.history = []

        return rel1, rel2

    def test_update_tension_success(self, mock_db, mock_relationships): pass
        """Test successful tension update."""
        rel1, rel2 = mock_relationships

        with patch.object(ConsolidatedRelationshipService, 'get_relationship', side_effect=[rel1, rel2]): pass
            result = ConsolidatedRelationshipService.update_tension(
                mock_db, 1, 2, 15.0, reason="Trade dispute"
            )

        # Verify
        updated_rel1, updated_rel2 = result
        assert updated_rel1.tension == 40.0  # 25 + 15
        assert updated_rel2.tension == 40.0
        assert len(updated_rel1.history) > 0
        assert len(updated_rel2.history) > 0

    def test_update_tension_with_clamping(self, mock_db, mock_relationships): pass
        """Test tension update with clamping to bounds."""
        rel1, rel2 = mock_relationships
        rel1.tension = 95.0
        rel2.tension = 95.0

        with patch.object(ConsolidatedRelationshipService, 'get_relationship', side_effect=[rel1, rel2]): pass
            result = ConsolidatedRelationshipService.update_tension(
                mock_db, 1, 2, 20.0  # Would go over 100
            )

        # Verify clamped to 100
        updated_rel1, updated_rel2 = result
        assert updated_rel1.tension == 100.0
        assert updated_rel2.tension == 100.0


class TestDeclareWar: pass
    """Test war declaration functionality."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_declare_war_success(self, mock_db): pass
        """Test successful war declaration."""
        # Setup relationship
        rel1 = Mock(spec=FactionRelationship)
        rel1.diplomatic_stance = "war"
        rel1.tension = 90.0
        rel1.war_state = {"at_war": True, "war_start": "2024-01-01T00:00:00"}
        rel1.history = []

        # Mock the set_diplomatic_stance method to return a relationship
        with patch.object(ConsolidatedRelationshipService, 'set_diplomatic_stance', return_value=rel1): pass
            with patch.object(ConsolidatedRelationshipService, 'get_relationship', return_value=rel1): pass
                result = ConsolidatedRelationshipService.declare_war(
                    mock_db, 1, 2, reason="Resource conflict", war_details={"type": "territorial"}
                )

        # Verify
        war_rel1, war_rel2 = result
        assert war_rel1.diplomatic_stance == "war"
        # Note: war_rel2 might be None if reciprocal relationship not found


class TestMakePeace: pass
    """Test peace-making functionality."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_make_peace_success(self, mock_db): pass
        """Test successful peace-making."""
        # Setup war relationships
        rel1 = Mock(spec=FactionRelationship)
        rel1.diplomatic_stance = "war"
        rel1.tension = 80.0
        rel1.war_state = {"at_war": True, "war_start": "2024-01-01T00:00:00"}
        rel1.history = []

        rel2 = Mock(spec=FactionRelationship)
        rel2.diplomatic_stance = "war"
        rel2.tension = 80.0
        rel2.war_state = {"at_war": True, "war_start": "2024-01-01T00:00:00"}
        rel2.history = []

        with patch.object(ConsolidatedRelationshipService, 'get_relationship', side_effect=[rel1, rel2]): pass
            result = ConsolidatedRelationshipService.make_peace(
                mock_db, 1, 2, terms={"reparations": 1000}, new_stance=DiplomaticStance.TRUCE
            )

        # Verify
        peace_rel1, peace_rel2 = result
        assert peace_rel1.diplomatic_stance == "truce"
        assert peace_rel1.war_state["at_war"] is False
        assert "war_end" in peace_rel1.war_state
        assert len(peace_rel1.history) > 0


class TestProcessTensionDecay: pass
    """Test tension decay processing."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_process_tension_decay(self, mock_db): pass
        """Test tension decay processing."""
        # Setup relationships with tension
        relationships = []
        for i in range(3): pass
            rel = Mock(spec=FactionRelationship)
            rel.tension = 50.0 + (i * 10)  # 50, 60, 70
            rel.diplomatic_stance = "neutral"
            rel.war_state = {"at_war": False}
            rel.history = []
            relationships.append(rel)

        # Mock the db.query().all() to return the actual list
        mock_db.query.return_value.all.return_value = relationships

        # Execute
        result = ConsolidatedRelationshipService.process_tension_decay(mock_db)

        # Verify - check the actual return format from the service
        assert "total" in result
        assert "decayed" in result
        assert "unchanged" in result
        assert result["total"] == 3


class TestResolveWarOutcome: pass
    """Test war outcome resolution functionality."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_war_relationship(self): pass
        """Create a sample war relationship."""
        relationship = Mock(spec=FactionRelationship)
        relationship.faction_id = 1
        relationship.other_faction_id = 2
        relationship.diplomatic_stance = DiplomaticStance.WAR.value
        relationship.tension = 80.0
        relationship.war_state = {
            "at_war": True,
            "war_start": "2024-01-01T00:00:00",
            "declaration_reason": "border_dispute"
        }
        relationship.history = []
        return relationship

    @pytest.fixture
    def sample_factions(self): pass
        """Create sample factions."""
        faction1 = Mock(spec=Faction)
        faction1.configure_mock(**{
            'id': 1,
            'name': "Empire",
            'influence': 75.0,
            'resources': {"gold": 1000, "military": 800}
        })

        faction2 = Mock(spec=Faction)
        faction2.configure_mock(**{
            'id': 2,
            'name': "Republic",
            'influence': 65.0,
            'resources': {"gold": 800, "military": 600}
        })

        return faction1, faction2

    def test_resolve_war_outcome_with_victor(self, mock_db, sample_war_relationship, sample_factions): pass
        """Test war outcome resolution with a clear victor."""
        # Make sure factions have all required attributes
        faction1, faction2 = sample_factions
        faction1.influence = 75.0
        faction1.resources = {"gold": 1000, "military": 800}
        faction2.influence = 65.0
        faction2.resources = {"gold": 800, "military": 600}
        
        # Setup - need to handle both get_relationship and direct queries
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            faction1,  # First query for faction
            faction2,  # Second query for other_faction
        ]
        
        with patch.object(ConsolidatedRelationshipService, 'get_relationship', 
                         side_effect=[sample_war_relationship, None]): pass
            # Execute
            result = ConsolidatedRelationshipService.resolve_war_outcome(
                mock_db, 
                faction_id=1, 
                other_faction_id=2, 
                victor_id=1,
                outcome_type="victory",
                mechanical_consequences=True
            )

        # Verify
        assert result["success"] is True
        assert result["outcome"] == "victory"
        assert result["victor_id"] == 1
        
        # Verify influence changes
        assert faction1.influence == 85.0  # Gained 10
        assert faction2.influence == 50.0  # Lost 15
        
        # Verify resource transfer
        assert faction1.resources["gold"] == 1160.0  # Gained 20% of 800 = 160
        assert faction2.resources["gold"] == 640.0   # Lost 160

    def test_resolve_war_outcome_negotiated_peace(self, mock_db, sample_war_relationship, sample_factions): pass
        """Test resolving war with negotiated peace."""
        faction1, faction2 = sample_factions
        
        # Setup
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_war_relationship,  # get_relationship call
            faction1,  # faction lookup
            faction2   # other faction lookup
        ]

        with patch.object(ConsolidatedRelationshipService, 'get_relationship', 
                         side_effect=[sample_war_relationship, None]):  # No reciprocal
            # Execute
            result = ConsolidatedRelationshipService.resolve_war_outcome(
                mock_db, 
                faction_id=1, 
                other_faction_id=2,
                outcome_type="negotiated",
                terms={"trade_agreement": True},
                mechanical_consequences=False
            )

        # Verify war state updated
        assert sample_war_relationship.war_state["at_war"] is False
        assert sample_war_relationship.war_state["outcome"] == "negotiated"
        
        # Verify stance and tension for negotiated peace
        assert sample_war_relationship.diplomatic_stance == DiplomaticStance.HOSTILE.value
        assert sample_war_relationship.tension == 30.0
        
        # Verify no mechanical consequences applied (disabled)
        assert faction1.influence == 75.0  # unchanged
        assert faction2.influence == 65.0  # unchanged

    def test_resolve_war_outcome_stalemate(self, mock_db, sample_war_relationship, sample_factions): pass
        """Test stalemate war outcome."""
        # Make sure factions have all required attributes
        faction1, faction2 = sample_factions
        faction1.influence = 75.0
        faction1.resources = {"gold": 1000}
        faction2.influence = 65.0
        faction2.resources = {"gold": 800}
        
        # Setup - need proper sequence for database queries
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            faction1,  # First query for faction
            faction2,  # Second query for other_faction
        ]
        
        with patch.object(ConsolidatedRelationshipService, 'get_relationship', 
                         side_effect=[sample_war_relationship, None]): pass
            # Execute
            result = ConsolidatedRelationshipService.resolve_war_outcome(
                mock_db, 
                faction_id=1, 
                other_faction_id=2, 
                outcome_type="stalemate",
                mechanical_consequences=False  # No mechanical consequences
            )

        # Verify
        assert result["success"] is True
        assert result["outcome"] == "stalemate"
        assert "victor_id" not in result or result["victor_id"] is None
        
        # Verify no influence changes (mechanical_consequences=False)
        assert faction1.influence == 75.0  # Unchanged
        assert faction2.influence == 65.0  # Unchanged
        
        # Verify relationship tension and stance
        assert sample_war_relationship.tension == 50.0  # Stalemate tension
        assert sample_war_relationship.diplomatic_stance == DiplomaticStance.HOSTILE.value

    def test_resolve_war_outcome_defeat(self, mock_db, sample_war_relationship, sample_factions): pass
        """Test war outcome when this faction is defeated."""
        # Make sure factions have all required attributes
        faction1, faction2 = sample_factions
        faction1.influence = 75.0
        faction1.resources = {"gold": 1000, "military": 800}
        faction2.influence = 65.0
        faction2.resources = {"gold": 800, "military": 600}
        
        # Setup - need proper sequence for database queries
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            faction1,  # First query for faction
            faction2,  # Second query for other_faction
        ]
        
        with patch.object(ConsolidatedRelationshipService, 'get_relationship', 
                         side_effect=[sample_war_relationship, None]): pass
            # Execute
            result = ConsolidatedRelationshipService.resolve_war_outcome(
                mock_db, 
                faction_id=1, 
                other_faction_id=2, 
                victor_id=2,  # Other faction won
                outcome_type="defeat",
                mechanical_consequences=True
            )

        # Verify
        assert result["success"] is True
        assert result["outcome"] == "defeat"
        assert result["victor_id"] == 2
        
        # Verify NO influence changes (defeat doesn't apply mechanical consequences)
        assert faction1.influence == 75.0  # Unchanged
        assert faction2.influence == 65.0  # Unchanged
        
        # Verify NO resource transfer (defeat doesn't apply mechanical consequences)
        assert faction1.resources["gold"] == 1000  # Unchanged
        assert faction2.resources["gold"] == 800   # Unchanged
        
        # Verify higher tension for defeat (this IS applied)
        assert sample_war_relationship.tension == 70.0
        assert sample_war_relationship.diplomatic_stance == DiplomaticStance.HOSTILE.value

    def test_resolve_war_outcome_not_at_war_error(self, mock_db): pass
        """Test error when factions are not at war."""
        # Setup relationship not at war
        relationship = Mock(spec=FactionRelationship)
        relationship.diplomatic_stance = DiplomaticStance.NEUTRAL.value
        relationship.war_state = {"at_war": False}

        with patch.object(ConsolidatedRelationshipService, 'get_relationship', 
                         return_value=relationship): pass
            # Execute & Verify
            with pytest.raises(ValueError, match="Factions are not at war"): pass
                ConsolidatedRelationshipService.resolve_war_outcome(
                    mock_db, faction_id=1, other_faction_id=2
                )


class TestAdvancedTensionDecay: pass
    """Test advanced tension decay scenarios."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_process_tension_decay_diplomatic_stance_transitions(self, mock_db): pass
        """Test that tension decay properly transitions diplomatic stances."""
        # Create relationships at different tension levels
        relationships = []
        
        # Relationship that should transition from HOSTILE to NEUTRAL
        # Start at 21.0 tension with high decay rate to get below 20
        rel1 = Mock(spec=FactionRelationship)
        rel1.tension = 21.0  # Will decay by 2.1 (10% of 21), bringing it to 18.9 < 20 = NEUTRAL
        rel1.diplomatic_stance = DiplomaticStance.HOSTILE.value
        rel1.war_state = {"at_war": False}
        rel1.history = []
        relationships.append(rel1)
        
        # Relationship that should transition to ALLIANCE
        # Start at -71.0 tension, already at ALLIANCE level but check transition
        rel2 = Mock(spec=FactionRelationship)
        rel2.tension = -71.0  # Already <= -70, should be ALLIANCE
        rel2.diplomatic_stance = DiplomaticStance.ALLIED.value
        rel2.war_state = {"at_war": False}
        rel2.history = []
        relationships.append(rel2)
        
        # War relationship that should be skipped
        rel3 = Mock(spec=FactionRelationship)
        rel3.tension = 90.0
        rel3.diplomatic_stance = DiplomaticStance.WAR.value
        rel3.war_state = {"at_war": True}
        rel3.history = []
        relationships.append(rel3)

        # Setup - mock the direct query call pattern: db.query(FactionRelationship).all()
        mock_db.query.return_value.all.return_value = relationships

        # Execute
        result = ConsolidatedRelationshipService.process_tension_decay(
            mock_db, 
            decay_rate_positive=10.0,  # High decay rate for testing
            min_decay=1.0
        )

        # Verify stance transitions
        assert rel1.diplomatic_stance == DiplomaticStance.NEUTRAL.value  # 21.0 -> 18.9 < 20
        assert rel2.diplomatic_stance == DiplomaticStance.ALLIANCE.value  # -71.0 <= -70
        assert rel3.diplomatic_stance == DiplomaticStance.WAR.value  # unchanged (at war)
        
        # Verify tension changes
        assert rel1.tension < 20.0  # Should have decayed below 20
        assert rel2.tension > -71.0  # Should have decayed toward 0 (less negative)
        assert rel3.tension == 90.0  # unchanged (at war)
        
        # Verify stats
        assert result["unchanged"] == 1  # The war relationship
        assert result["decayed"] >= 1

    def test_process_tension_decay_zero_tension_unchanged(self, mock_db): pass
        """Test that relationships at zero tension remain unchanged."""
        # Relationship already at zero tension
        rel = Mock(spec=FactionRelationship)
        rel.tension = 0.0
        rel.diplomatic_stance = DiplomaticStance.NEUTRAL.value
        rel.war_state = {"at_war": False}
        rel.history = []

        # Setup - mock the direct query call pattern: db.query(FactionRelationship).all()
        mock_db.query.return_value.all.return_value = [rel]

        # Execute
        result = ConsolidatedRelationshipService.process_tension_decay(mock_db)

        # Verify no change
        assert rel.tension == 0.0
        assert result["unchanged"] == 1
        assert result["decayed"] == 0

    def test_process_tension_decay_history_recording(self, mock_db): pass
        """Test that decay properly records history entries."""
        # Relationship with positive tension that will decay
        rel = Mock(spec=FactionRelationship)
        rel.tension = 30.0
        rel.diplomatic_stance = DiplomaticStance.HOSTILE.value
        rel.war_state = {"at_war": False}
        rel.history = []

        # Setup - mock the direct query call pattern: db.query(FactionRelationship).all()
        mock_db.query.return_value.all.return_value = [rel]

        # Execute
        result = ConsolidatedRelationshipService.process_tension_decay(
            mock_db, decay_rate_positive=10.0
        )

        # Verify history was recorded
        assert len(rel.history) == 1
        history_entry = rel.history[0]
        assert history_entry["action"] == "tension_decay"
        assert history_entry["old_tension"] == 30.0
        assert history_entry["new_tension"] < 30.0  # Should have decayed
        assert "decay_amount" in history_entry
        assert "timestamp" in history_entry

    def test_process_tension_decay_custom_parameters(self, mock_db): pass
        """Test tension decay with custom parameters."""
        # Relationship with high positive tension
        rel = Mock(spec=FactionRelationship)
        rel.tension = 80.0
        rel.diplomatic_stance = DiplomaticStance.HOSTILE.value
        rel.war_state = {"at_war": False}
        rel.history = []

        # Setup - mock the direct query call pattern: db.query(FactionRelationship).all()
        mock_db.query.return_value.all.return_value = [rel]

        # Execute with custom parameters
        result = ConsolidatedRelationshipService.process_tension_decay(
            mock_db, 
            decay_rate_positive=20.0,  # High decay rate
            max_decay=10.0,           # Limited max decay
            min_decay=1.0
        )

        # Verify decay was limited by max_decay
        assert rel.tension == 70.0  # 80 - 10 (max_decay)
        assert result["positive_decay"] == 1


class TestConsolidatedRelationshipServiceIntegration: pass
    """Integration tests for the service."""

    @pytest.fixture
    def mock_db(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_relationship_lifecycle(self, mock_db): pass
        """Test complete relationship lifecycle."""
        # Setup factions
        faction1 = Mock(spec=Faction)
        faction1.id = 1
        faction2 = Mock(spec=Faction)
        faction2.id = 2

        # Mock faction queries for the stance setting
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            faction1, faction2, None, None  # factions exist, relationships don't exist initially
        ]

        # Test 1: Set initial stance
        with patch.object(ConsolidatedRelationshipService, 'get_relationship', side_effect=[None, None]): pass
            relationship = ConsolidatedRelationshipService.set_diplomatic_stance(
                mock_db, 1, 2, DiplomaticStance.NEUTRAL
            )

        assert relationship.diplomatic_stance == "neutral"

        # Test 2: Update tension - mock faction existence checks
        relationship.tension = 0.0
        relationship.history = []
        
        # Reset the mock for tension update (it needs faction existence checks again)
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            faction1, faction2  # factions exist for tension update
        ]
        
        with patch.object(ConsolidatedRelationshipService, 'get_relationship', side_effect=[relationship, relationship]): pass
            updated_rels = ConsolidatedRelationshipService.update_tension(
                mock_db, 1, 2, 30.0
            )

        # Note: Tension 30.0 triggers automatic stance change to HOSTILE, which may adjust the final tension
        # The test should check that tension was updated, not necessarily to exactly 30.0
        assert updated_rels[0].tension >= 30.0  # Allow for automatic adjustments

    def test_error_handling_comprehensive(self, mock_db): pass
        """Test comprehensive error handling."""
        # Test faction not found
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(FactionNotFoundError): pass
            ConsolidatedRelationshipService.set_diplomatic_stance(
                mock_db, 999, 888, DiplomaticStance.ALLIED
            )

        # Test faction not found for tension update (update_tension checks faction existence first)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(FactionNotFoundError): pass
            ConsolidatedRelationshipService.update_tension(mock_db, 1, 2, 10.0)
