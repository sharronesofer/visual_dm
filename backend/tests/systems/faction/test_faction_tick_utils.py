"""
Comprehensive tests for faction tick utilities.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.systems.faction.faction_tick_utils import (
    decay_faction_tensions,
    propagate_faction_influence
)
from backend.systems.faction.models.faction import FactionRelationship


class TestDecayFactionTensions: pass
    """Test faction tension decay functionality."""

    @pytest.fixture
    def mock_session(self): pass
        """Create a mock database session."""
        session = Mock(spec=Session)
        return session

    @pytest.fixture
    def sample_relationship(self): pass
        """Create a sample faction relationship."""
        rel = Mock(spec=FactionRelationship)
        rel.faction_id = 1
        rel.other_faction_id = 2
        rel.tension = 50.0
        rel.diplomatic_stance = "neutral"
        rel.war_state = {}
        rel.history = []
        return rel

    @pytest.fixture
    def sample_war_relationship(self): pass
        """Create a sample war relationship."""
        rel = Mock(spec=FactionRelationship)
        rel.faction_id = 1
        rel.other_faction_id = 3
        rel.tension = 80.0
        rel.diplomatic_stance = "war"
        rel.war_state = {"at_war": True}
        rel.history = []
        return rel

    @pytest.fixture
    def sample_alliance_relationship(self): pass
        """Create a sample alliance relationship."""
        rel = Mock(spec=FactionRelationship)
        rel.faction_id = 2
        rel.other_faction_id = 3
        rel.tension = -40.0
        rel.diplomatic_stance = "alliance"
        rel.war_state = {}
        rel.history = []
        return rel

    def test_decay_no_relationships(self, mock_session): pass
        """Test decay when no relationships exist."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query

        # Execute
        result = decay_faction_tensions(mock_session)

        # Verify
        assert result["relationships_processed"] == 0
        assert result["tensions_decayed"] == 0
        assert result["total_decay_amount"] == 0.0
        mock_session.commit.assert_not_called()

    def test_decay_positive_tension(self, mock_session, sample_relationship): pass
        """Test decay of positive tension (conflict)."""
        # Setup
        sample_relationship.tension = 60.0
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [sample_relationship]
        mock_session.query.return_value = mock_query

        # Mock reciprocal relationship query
        reciprocal_rel = Mock(spec=FactionRelationship)
        reciprocal_rel.tension = 60.0
        reciprocal_rel.history = []
        mock_session.query.return_value.filter.return_value.first.return_value = reciprocal_rel

        # Execute with fixed random for predictable results
        with patch('random.random', return_value=0.5):  # randomness_factor = 1.0
            result = decay_faction_tensions(mock_session, decay_rate_positive=2.0)

        # Verify
        assert result["relationships_processed"] == 1
        assert result["tensions_decayed"] == 1
        assert result["total_decay_amount"] > 0
        assert sample_relationship.tension < 60.0
        assert reciprocal_rel.tension == sample_relationship.tension
        mock_session.commit.assert_called_once()

    def test_decay_negative_tension(self, mock_session, sample_alliance_relationship): pass
        """Test decay of negative tension (alliance)."""
        # Setup
        sample_alliance_relationship.tension = -50.0
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [sample_alliance_relationship]
        mock_session.query.return_value = mock_query

        # Mock reciprocal relationship query
        reciprocal_rel = Mock(spec=FactionRelationship)
        reciprocal_rel.tension = -50.0
        reciprocal_rel.history = []
        mock_session.query.return_value.filter.return_value.first.return_value = reciprocal_rel

        # Execute with fixed random for predictable results
        with patch('random.random', return_value=0.5):  # randomness_factor = 1.0
            result = decay_faction_tensions(mock_session, decay_rate_negative=2.0)

        # Verify
        assert result["relationships_processed"] == 1
        assert result["tensions_decayed"] == 1
        assert result["total_decay_amount"] > 0
        assert sample_alliance_relationship.tension > -50.0  # Closer to zero
        assert reciprocal_rel.tension == sample_alliance_relationship.tension
        mock_session.commit.assert_called_once()

    def test_decay_war_relationship_skipped(self, mock_session, sample_war_relationship): pass
        """Test that war relationships don't decay automatically."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [sample_war_relationship]
        mock_session.query.return_value = mock_query

        original_tension = sample_war_relationship.tension

        # Execute
        result = decay_faction_tensions(mock_session)

        # Verify
        assert result["relationships_processed"] == 0  # War relationships are skipped
        assert result["tensions_decayed"] == 0
        assert sample_war_relationship.tension == original_tension  # Unchanged
        mock_session.commit.assert_not_called()

    def test_decay_with_bounds(self, mock_session, sample_relationship): pass
        """Test decay respects min and max bounds."""
        # Setup
        sample_relationship.tension = 5.0  # Low tension
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [sample_relationship]
        mock_session.query.return_value = mock_query

        # Mock reciprocal relationship query
        reciprocal_rel = Mock(spec=FactionRelationship)
        reciprocal_rel.tension = 5.0
        reciprocal_rel.history = []
        mock_session.query.return_value.filter.return_value.first.return_value = reciprocal_rel

        # Execute with high decay rate but min_decay constraint
        with patch('random.random', return_value=0.0):  # randomness_factor = 0.7
            result = decay_faction_tensions(
                mock_session, 
                decay_rate_positive=10.0,
                min_decay=0.5,
                max_decay=1.0
            )

        # Verify decay was applied but within bounds
        assert result["relationships_processed"] == 1
        assert result["tensions_decayed"] == 1
        assert sample_relationship.tension >= 0  # Can't go below zero
        assert sample_relationship.tension < 5.0  # Some decay occurred

    def test_decay_to_zero(self, mock_session, sample_relationship): pass
        """Test tension decaying to exactly zero."""
        # Setup
        sample_relationship.tension = 0.5  # Very low tension
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [sample_relationship]
        mock_session.query.return_value = mock_query

        # Mock reciprocal relationship query
        reciprocal_rel = Mock(spec=FactionRelationship)
        reciprocal_rel.tension = 0.5
        reciprocal_rel.history = []
        mock_session.query.return_value.filter.return_value.first.return_value = reciprocal_rel

        # Execute with sufficient decay to reach zero
        with patch('random.random', return_value=0.5): pass
            result = decay_faction_tensions(mock_session, decay_rate_positive=2.0)

        # Verify
        assert sample_relationship.tension == 0.0
        assert reciprocal_rel.tension == 0.0

    def test_decay_history_recording(self, mock_session, sample_relationship): pass
        """Test that significant decay is recorded in history."""
        # Setup
        sample_relationship.tension = 80.0  # High tension for significant decay
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [sample_relationship]
        mock_session.query.return_value = mock_query

        # Mock reciprocal relationship query
        reciprocal_rel = Mock(spec=FactionRelationship)
        reciprocal_rel.tension = 80.0
        reciprocal_rel.history = []
        mock_session.query.return_value.filter.return_value.first.return_value = reciprocal_rel

        # Execute with high decay rate to ensure significant change
        with patch('random.random', return_value=0.5): pass
            result = decay_faction_tensions(mock_session, decay_rate_positive=5.0)

        # Verify history was recorded
        assert len(sample_relationship.history) > 0
        assert len(reciprocal_rel.history) > 0
        
        history_entry = sample_relationship.history[0]
        assert history_entry["type"] == "tension_decay"
        assert history_entry["old_tension"] == 80.0
        assert history_entry["new_tension"] == sample_relationship.tension
        assert "timestamp" in history_entry

    def test_decay_no_reciprocal_relationship(self, mock_session, sample_relationship): pass
        """Test decay when no reciprocal relationship exists."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [sample_relationship]
        mock_session.query.return_value = mock_query

        # Mock no reciprocal relationship found
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Execute
        with patch('random.random', return_value=0.5): pass
            result = decay_faction_tensions(mock_session)

        # Verify decay still works without reciprocal
        assert result["relationships_processed"] == 1
        assert result["tensions_decayed"] == 1

    def test_decay_custom_parameters(self, mock_session, sample_relationship): pass
        """Test decay with custom parameters."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [sample_relationship]
        mock_session.query.return_value = mock_query

        # Mock reciprocal relationship query
        reciprocal_rel = Mock(spec=FactionRelationship)
        reciprocal_rel.tension = 50.0
        reciprocal_rel.history = []
        mock_session.query.return_value.filter.return_value.first.return_value = reciprocal_rel

        # Execute with custom parameters
        with patch('random.random', return_value=0.5): pass
            result = decay_faction_tensions(
                mock_session,
                decay_rate_positive=1.0,
                decay_rate_negative=1.5,
                min_decay=0.2,
                max_decay=3.0
            )

        # Verify function accepts custom parameters
        assert result["relationships_processed"] == 1
        assert "timestamp" in result

    def test_decay_multiple_relationships(self, mock_session): pass
        """Test decay with multiple relationships."""
        # Setup multiple relationships
        rel1 = Mock(spec=FactionRelationship)
        rel1.faction_id = 1
        rel1.other_faction_id = 2
        rel1.tension = 30.0
        rel1.diplomatic_stance = "neutral"
        rel1.war_state = {}
        rel1.history = []

        rel2 = Mock(spec=FactionRelationship)
        rel2.faction_id = 2
        rel2.other_faction_id = 3
        rel2.tension = -20.0
        rel2.diplomatic_stance = "alliance"
        rel2.war_state = {}
        rel2.history = []

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [rel1, rel2]
        mock_session.query.return_value = mock_query

        # Mock reciprocal relationships
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Execute
        with patch('random.random', return_value=0.5): pass
            result = decay_faction_tensions(mock_session)

        # Verify both relationships processed
        assert result["relationships_processed"] == 2
        assert result["tensions_decayed"] == 2


class TestPropagateFactionInfluence: pass
    """Test faction influence propagation functionality."""

    @pytest.fixture
    def mock_session(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_propagate_influence_placeholder(self, mock_session): pass
        """Test the placeholder implementation."""
        # Execute
        result = propagate_faction_influence(mock_session)

        # Verify placeholder response
        assert "message" in result
        assert "not yet implemented" in result["message"]
        assert "timestamp" in result

    def test_propagate_influence_with_faction_id(self, mock_session): pass
        """Test propagation with specific faction ID."""
        # Execute
        result = propagate_faction_influence(mock_session, faction_id=1)

        # Verify placeholder response
        assert "message" in result
        assert "timestamp" in result

    def test_propagate_influence_without_faction_id(self, mock_session): pass
        """Test propagation without specific faction ID."""
        # Execute
        result = propagate_faction_influence(mock_session, faction_id=None)

        # Verify placeholder response
        assert "message" in result
        assert "timestamp" in result


class TestFactionTickUtilsIntegration: pass
    """Integration tests for faction tick utilities."""

    @pytest.fixture
    def mock_session(self): pass
        """Create a mock database session."""
        return Mock(spec=Session)

    def test_decay_and_propagate_workflow(self, mock_session): pass
        """Test typical workflow of decay followed by propagation."""
        # Setup relationships for decay
        rel = Mock(spec=FactionRelationship)
        rel.faction_id = 1
        rel.other_faction_id = 2
        rel.tension = 40.0
        rel.diplomatic_stance = "neutral"
        rel.war_state = {}
        rel.history = []

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [rel]
        mock_session.query.return_value = mock_query
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Execute decay
        with patch('random.random', return_value=0.5): pass
            decay_result = decay_faction_tensions(mock_session)

        # Execute propagation
        propagate_result = propagate_faction_influence(mock_session)

        # Verify both operations completed
        assert decay_result["relationships_processed"] == 1
        assert "timestamp" in propagate_result

    @patch('backend.systems.faction.faction_tick_utils.datetime')
    def test_timestamp_consistency(self, mock_datetime, mock_session): pass
        """Test that timestamps are properly generated."""
        # Setup mock datetime
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = fixed_time

        # Setup empty relationships for decay
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query

        # Execute
        decay_result = decay_faction_tensions(mock_session)
        propagate_result = propagate_faction_influence(mock_session)

        # Verify timestamps
        assert decay_result["timestamp"] == fixed_time.isoformat()
        assert propagate_result["timestamp"] == fixed_time.isoformat()
