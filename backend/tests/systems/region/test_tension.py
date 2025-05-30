from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
from backend.systems.shared.config import TensionConfig
"""
Tests for the region.tension module.

This module contains tests for the TensionManager class and tension-related functions.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from backend.systems.region.tension import (
    TensionManager,
    TensionConfig,
    simulate_revolt_in_poi,
    decay_region_tension,
    check_faction_war_triggers,
    get_regions_by_tension,
    get_region_factions_at_war,
)
from backend.systems.shared.utils.error import TensionError


class TestTensionManager: pass
    """Tests for the TensionManager class."""

    @pytest.fixture
    def tension_manager(self): pass
        """Create a TensionManager instance for testing."""
        return TensionManager()

    def test_initialization(self, tension_manager): pass
        """Test that the TensionManager initializes correctly."""
        # Check that configs were loaded
        assert len(tension_manager.tension_configs) > 0
        assert "city" in tension_manager.tension_configs
        assert "dungeon" in tension_manager.tension_configs
        assert "wilderness" in tension_manager.tension_configs
        assert "default" in tension_manager.tension_configs

        # Check that state dictionaries are empty
        assert len(tension_manager.tension_state) == 0
        assert len(tension_manager.last_updated) == 0

    def test_calculate_tension_initial(self, tension_manager): pass
        """Test calculating tension for a location with no history."""
        region_id = "r_test123"
        poi_id = "p_test456"

        # Get the default config
        config = tension_manager.tension_configs["default"]

        # Calculate tension
        tension = tension_manager.calculate_tension(region_id, poi_id)

        # Should return the base tension from config
        assert tension == config.base_tension

        # Should initialize state dictionaries
        assert region_id in tension_manager.tension_state
        assert poi_id in tension_manager.tension_state[region_id]
        assert region_id in tension_manager.last_updated
        assert poi_id in tension_manager.last_updated[region_id]

    def test_calculate_tension_with_decay(self, tension_manager): pass
        """Test calculating tension with time-based decay."""
        region_id = "r_test123"
        poi_id = "p_test456"

        # Set up initial state
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)

        # Initialize with higher tension
        tension_manager.tension_state = {region_id: {poi_id: 0.8}}
        tension_manager.last_updated = {region_id: {poi_id: one_hour_ago}}

        # Get config and expected decay
        config = tension_manager.tension_configs["default"]
        expected_decay = config.decay_rate  # 1 hour of decay

        # Calculate new tension
        tension = tension_manager.calculate_tension(region_id, poi_id, current_time=now)

        # Check that decay was applied correctly
        expected_tension = max(config.min_tension, 0.8 - expected_decay)
        assert tension == pytest.approx(expected_tension, 0.001)

    def test_update_tension(self, tension_manager): pass
        """Test updating tension based on different factors."""
        region_id = "r_test123"
        poi_id = "p_test456"

        # Mock the impact methods to return fixed values
        tension_manager._get_player_impact = MagicMock(return_value=0.1)
        tension_manager._get_npc_impact = MagicMock(return_value=0.2)
        tension_manager._get_environmental_impact = MagicMock(return_value=0.3)

        # Update tension with all factors
        tension_manager.update_tension(
            region_id,
            poi_id,
            player_action="test_action",
            npc_change={"type": "test"},
            environmental_change={"type": "test"},
        )

        # Get config to calculate expected change
        config = tension_manager.tension_configs["default"]
        expected_delta = (
            0.1 * config.player_impact
            + 0.2 * config.npc_impact
            + 0.3 * config.environmental_impact
        )

        # Get the base tension (what would be set initially)
        base_tension = config.base_tension

        # Check that tension was updated correctly
        assert tension_manager.tension_state[region_id][poi_id] == pytest.approx(
            base_tension + expected_delta, 0.001
        )

    def test_tension_bounds(self, tension_manager): pass
        """Test that tension stays within min/max bounds."""
        region_id = "r_test123"
        poi_id = "p_test456"

        # Set up config
        config = tension_manager.tension_configs["default"]

        # Test upper bound
        # Set tension very high, then update with positive impacts
        tension_manager.tension_state = {region_id: {poi_id: 0.9}}
        tension_manager.last_updated = {region_id: {poi_id: datetime.utcnow()}}

        tension_manager._get_player_impact = MagicMock(return_value=0.5)
        tension_manager.update_tension(region_id, poi_id, player_action="test_action")

        # Should be capped at max_tension
        assert tension_manager.tension_state[region_id][poi_id] == config.max_tension

        # Test lower bound
        # Set tension very low, then apply heavy decay
        tension_manager.tension_state = {region_id: {poi_id: 0.15}}
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        tension_manager.last_updated = {region_id: {poi_id: one_day_ago}}

        # Calculate tension (should apply decay)
        tension = tension_manager.calculate_tension(region_id, poi_id)

        # Should be capped at min_tension
        assert tension == config.min_tension

    def test_error_handling(self, tension_manager): pass
        """Test error handling in tension calculations."""
        region_id = "r_test123"
        poi_id = "p_test456"

        # Set up existing tension state so _calculate_time_decay will be called
        tension_manager.tension_state = {region_id: {poi_id: 0.5}}
        tension_manager.last_updated = {region_id: {poi_id: datetime.utcnow()}}

        # Mock _calculate_time_decay to raise an exception
        with patch.object(
            tension_manager,
            "_calculate_time_decay",
            side_effect=Exception("Test error"),
        ): pass
            # Should raise a TensionError
            with pytest.raises(TensionError): pass
                tension_manager.calculate_tension(region_id, poi_id)


class TestTensionUtils: pass
    """Tests for the tension utility functions."""

    @patch("backend.systems.region.tension.log_world_event")
    @patch("backend.systems.region.tension.random.random", return_value=0.1)  # Force revolt to trigger
    def test_simulate_revolt_in_poi(self, mock_random, mock_log_event): pass
        """Test simulating a revolt in a POI."""
        region_id = "r_test123"
        poi_id = "p_test456"
        factions = ["faction1", "faction2"]
        npcs = [{"id": "npc1"}, {"id": "npc2"}, {"id": "npc3"}]
        tension = 0.9  # High tension

        # Call the function
        result = simulate_revolt_in_poi(region_id, poi_id, factions, npcs, tension)

        # Check that a world event was logged
        assert mock_log_event.called

        # Basic assertions on return value (would depend on implementation)
        assert result is not None

    def test_decay_region_tension(self): pass
        """Test decaying region tension."""
        region = {"id": "r_test123", "tension": 0.8}

        # Call the function
        decay_region_tension(region)

        # Check that tension was reduced
        assert region["tension"] < 0.8

    def test_check_faction_war_triggers(self): pass
        """Test checking for faction war triggers."""
        region = {
            "id": "r_test123",
            "faction_control": {"faction1": 0.6, "faction2": 0.4},
            "tension": 0.9,  # High tension
        }

        # Call the function
        triggers = check_faction_war_triggers(region)

        # Should return a list of potential conflicts
        assert isinstance(triggers, list)
        assert len(triggers) > 0

    def test_get_regions_by_tension(self): pass
        """Test getting regions by tension threshold."""
        # Mock session with regions
        mock_session = MagicMock()
        mock_session.query().filter().all.return_value = [
            {"id": "r_1", "tension": 0.3},
            {"id": "r_2", "tension": 0.7},
            {"id": "r_3", "tension": 0.9},
        ]

        # Call with medium threshold
        regions = get_regions_by_tension(mock_session, min_tension=0.5)

        # Should return only high-tension regions
        assert len(regions) == 2
        assert all(r["tension"] >= 0.5 for r in regions)

    def test_get_region_factions_at_war(self): pass
        """Test getting factions at war in a region."""
        # Mock session with faction conflicts
        mock_session = MagicMock()
        mock_conflicts = [
            {"faction1": "f1", "faction2": "f2", "war_state": True},
            {"faction1": "f1", "faction2": "f3", "war_state": False},
            {"faction1": "f2", "faction2": "f3", "war_state": True},
        ]
        mock_session.query().filter().all.return_value = mock_conflicts

        # Call the function
        at_war = get_region_factions_at_war(mock_session, "r_test123")

        # Should return only the factions at war
        assert len(at_war) == 2
        assert all(conflict["war_state"] for conflict in at_war)
