"""
Tests for backend.systems.region.utils.region_revolt_utils

This module contains tests for the region revolt simulation utilities.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend.systems.region.utils.region_revolt_utils import simulate_revolt_in_poi


class TestRegionRevoltUtils: pass
    """Tests for region revolt simulation utilities."""

    @patch('backend.systems.region.utils.region_revolt_utils.db')
    @patch('backend.systems.region.utils.region_revolt_utils.get_npc_level')
    @patch('backend.systems.region.utils.region_revolt_utils.log_world_event')
    def test_simulate_revolt_tension_too_low(self, mock_log_event, mock_get_level, mock_db): pass
        """Test that no revolt occurs when tension is below war level."""
        result = simulate_revolt_in_poi(
            region_id="region_1",
            poi_id="poi_1",
            factions_present=["faction_a", "faction_b"],
            npc_list=[],
            tension_level=70.0  # Below 80
        )
        
        assert result is None
        mock_db.assert_not_called()
        mock_get_level.assert_not_called()
        mock_log_event.assert_not_called()

    @patch('backend.systems.region.utils.region_revolt_utils.db')
    @patch('backend.systems.region.utils.region_revolt_utils.get_npc_level')
    @patch('backend.systems.region.utils.region_revolt_utils.log_world_event')
    def test_simulate_revolt_no_clear_winner(self, mock_log_event, mock_get_level, mock_db): pass
        """Test that no revolt occurs when no faction clearly dominates."""
        # Mock NPC levels to be equal across factions
        mock_get_level.side_effect = lambda role: {"leader": 10, "guard": 5, "laborer": 1}.get(role, 1)
        
        npc_list = [
            {"faction_affiliations": ["faction_a"], "role": "leader", "npc_id": "npc_1"},
            {"faction_affiliations": ["faction_b"], "role": "leader", "npc_id": "npc_2"},
        ]
        
        result = simulate_revolt_in_poi(
            region_id="region_1",
            poi_id="poi_1",
            factions_present=["faction_a", "faction_b"],
            npc_list=npc_list,
            tension_level=90.0
        )
        
        assert result is None
        mock_db.assert_not_called()
        mock_log_event.assert_not_called()

    @patch('backend.systems.region.utils.region_revolt_utils.db')
    @patch('backend.systems.region.utils.region_revolt_utils.get_npc_level')
    @patch('backend.systems.region.utils.region_revolt_utils.log_world_event')
    def test_simulate_revolt_winner_already_ruling(self, mock_log_event, mock_get_level, mock_db): pass
        """Test that no change occurs when winning faction is already ruling."""
        # Mock NPC levels - faction_a dominates
        mock_get_level.side_effect = lambda role: {"leader": 10, "guard": 5, "laborer": 1}.get(role, 1)
        
        # Mock POI data showing faction_a already ruling
        mock_poi_ref = MagicMock()
        mock_poi_ref.get.return_value = {"ruling_faction": "faction_a"}
        mock_db.reference.return_value = mock_poi_ref
        
        npc_list = [
            {"faction_affiliations": ["faction_a"], "role": "leader", "npc_id": "npc_1"},
            {"faction_affiliations": ["faction_a"], "role": "guard", "npc_id": "npc_2"},
            {"faction_affiliations": ["faction_b"], "role": "laborer", "npc_id": "npc_3"},
        ]
        
        result = simulate_revolt_in_poi(
            region_id="region_1",
            poi_id="poi_1",
            factions_present=["faction_a", "faction_b"],
            npc_list=npc_list,
            tension_level=90.0
        )
        
        assert result is None
        mock_log_event.assert_not_called()

    @patch('backend.systems.region.utils.region_revolt_utils.db')
    @patch('backend.systems.region.utils.region_revolt_utils.get_npc_level')
    @patch('backend.systems.region.utils.region_revolt_utils.log_world_event')
    @patch('backend.systems.region.utils.region_revolt_utils.datetime')
    def test_simulate_revolt_successful_capitol_change(self, mock_datetime, mock_log_event, mock_get_level, mock_db): pass
        """Test successful revolt leading to capitol change."""
        # Mock current time
        mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
        
        # Mock NPC levels - faction_a dominates
        mock_get_level.side_effect = lambda role: {"leader": 10, "guard": 5, "laborer": 1}.get(role, 1)
        
        # Mock POI data showing faction_b currently ruling
        mock_poi_ref = MagicMock()
        mock_poi_ref.get.return_value = {"ruling_faction": "faction_b"}
        
        # Mock memory reference
        mock_mem_ref = MagicMock()
        mock_mem_ref.get.return_value = []
        
        mock_db.reference.side_effect = lambda path: {
            "/poi_state/region_1/poi_1": mock_poi_ref,
            "/regions/region_1/memory": mock_mem_ref
        }.get(path, MagicMock())
        
        npc_list = [
            {"faction_affiliations": ["faction_a"], "role": "leader", "npc_id": "npc_1"},
            {"faction_affiliations": ["faction_a"], "role": "guard", "npc_id": "npc_2"},
            {"faction_affiliations": ["faction_a"], "role": "guard", "npc_id": "npc_3"},
            {"faction_affiliations": ["faction_b"], "role": "laborer", "npc_id": "npc_4"},
        ]
        
        result = simulate_revolt_in_poi(
            region_id="region_1",
            poi_id="poi_1",
            factions_present=["faction_a", "faction_b"],
            npc_list=npc_list,
            tension_level=90.0
        )
        
        # Verify revolt result
        assert result is not None
        assert result["revolt"] is True
        assert result["winner"] == "faction_a"
        assert result["old_faction"] == "faction_b"
        assert "faction_strength" in result
        assert result["faction_strength"]["faction_a"] > result["faction_strength"]["faction_b"]
        
        # Verify POI ruling faction was updated
        mock_poi_ref.child.assert_called_with("ruling_faction")
        mock_poi_ref.child().set.assert_called_with("faction_a")
        
        # Verify world event was logged
        mock_log_event.assert_called_once()
        event_call = mock_log_event.call_args[0][0]
        assert event_call["type"] == "capitol_change"
        assert event_call["region_id"] == "region_1"
        assert event_call["poi_id"] == "poi_1"
        assert event_call["old_faction"] == "faction_b"
        assert event_call["new_faction"] == "faction_a"
        assert event_call["details"]["revolt"] is True
        
        # Verify memory was updated
        mock_mem_ref.set.assert_called_once()
        memory_call = mock_mem_ref.set.call_args[0][0]
        assert len(memory_call) == 1
        assert memory_call[0]["event_type"] == "capitol_change"
        assert memory_call[0]["core"] is True

    @patch('backend.systems.region.utils.region_revolt_utils.db')
    @patch('backend.systems.region.utils.region_revolt_utils.get_npc_level')
    @patch('backend.systems.region.utils.region_revolt_utils.log_world_event')
    @patch('backend.systems.region.utils.region_revolt_utils.datetime')
    def test_simulate_revolt_empty_poi_data(self, mock_datetime, mock_log_event, mock_get_level, mock_db): pass
        """Test revolt when POI has no existing data."""
        # Mock current time
        mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
        
        # Mock NPC levels
        mock_get_level.side_effect = lambda role: {"leader": 10, "guard": 5}.get(role, 1)
        
        # Mock empty POI data
        mock_poi_ref = MagicMock()
        mock_poi_ref.get.return_value = None  # No existing data
        
        # Mock memory reference
        mock_mem_ref = MagicMock()
        mock_mem_ref.get.return_value = None  # No existing memory
        
        mock_db.reference.side_effect = lambda path: {
            "/poi_state/region_1/poi_1": mock_poi_ref,
            "/regions/region_1/memory": mock_mem_ref
        }.get(path, MagicMock())
        
        npc_list = [
            {"faction_affiliations": ["faction_a"], "role": "leader", "npc_id": "npc_1"},
            {"faction_affiliations": ["faction_b"], "role": "guard", "npc_id": "npc_2"},
        ]
        
        result = simulate_revolt_in_poi(
            region_id="region_1",
            poi_id="poi_1",
            factions_present=["faction_a", "faction_b"],
            npc_list=npc_list,
            tension_level=85.0
        )
        
        # Should still process revolt (faction_a wins with leader vs guard)
        assert result is not None
        assert result["revolt"] is True
        assert result["winner"] == "faction_a"
        assert result["old_faction"] is None  # No previous ruling faction

    @patch('backend.systems.region.utils.region_revolt_utils.db')
    @patch('backend.systems.region.utils.region_revolt_utils.get_npc_level')
    @patch('backend.systems.region.utils.region_revolt_utils.log_world_event')
    def test_simulate_revolt_npc_without_factions(self, mock_log_event, mock_get_level, mock_db): pass
        """Test revolt simulation with NPCs that have no faction affiliations."""
        mock_get_level.side_effect = lambda role: {"leader": 10}.get(role, 1)
        
        # Mock POI data
        mock_poi_ref = MagicMock()
        mock_poi_ref.get.return_value = {"ruling_faction": "faction_b"}
        mock_db.reference.return_value = mock_poi_ref
        
        npc_list = [
            {"faction_affiliations": ["faction_a"], "role": "leader", "npc_id": "npc_1"},
            {"npc_id": "npc_2"},  # No faction_affiliations
            {"faction_affiliations": [], "role": "guard", "npc_id": "npc_3"},  # Empty affiliations
        ]
        
        result = simulate_revolt_in_poi(
            region_id="region_1",
            poi_id="poi_1",
            factions_present=["faction_a", "faction_b"],
            npc_list=npc_list,
            tension_level=90.0
        )
        
        # faction_a should win (only faction with actual members)
        assert result is not None
        assert result["winner"] == "faction_a"

    @patch('backend.systems.region.utils.region_revolt_utils.db')
    @patch('backend.systems.region.utils.region_revolt_utils.get_npc_level')
    @patch('backend.systems.region.utils.region_revolt_utils.log_world_event')
    def test_simulate_revolt_npc_without_role(self, mock_log_event, mock_get_level, mock_db): pass
        """Test revolt simulation with NPCs that have no role specified."""
        # Mock get_npc_level to handle missing roles
        mock_get_level.side_effect = lambda role: {"leader": 10, "laborer": 1}.get(role, 1)
        
        # Mock POI data
        mock_poi_ref = MagicMock()
        mock_poi_ref.get.return_value = {"ruling_faction": "faction_b"}
        mock_db.reference.return_value = mock_poi_ref
        
        npc_list = [
            {"faction_affiliations": ["faction_a"], "role": "leader", "npc_id": "npc_1"},
            {"faction_affiliations": ["faction_b"], "npc_id": "npc_2"},  # No role specified
        ]
        
        result = simulate_revolt_in_poi(
            region_id="region_1",
            poi_id="poi_1",
            factions_present=["faction_a", "faction_b"],
            npc_list=npc_list,
            tension_level=90.0
        )
        
        # faction_a should win (leader level 10 vs laborer level 1)
        assert result is not None
        assert result["winner"] == "faction_a"
        
        # Verify get_npc_level was called with "laborer" for NPC without role
        mock_get_level.assert_any_call("laborer")

    @patch('backend.systems.region.utils.region_revolt_utils.db')
    @patch('backend.systems.region.utils.region_revolt_utils.get_npc_level')
    @patch('backend.systems.region.utils.region_revolt_utils.log_world_event')
    def test_simulate_revolt_multiple_faction_affiliations(self, mock_log_event, mock_get_level, mock_db): pass
        """Test revolt with NPCs belonging to multiple factions."""
        mock_get_level.side_effect = lambda role: {"leader": 10, "guard": 5}.get(role, 1)
        
        # Mock POI data
        mock_poi_ref = MagicMock()
        mock_poi_ref.get.return_value = {"ruling_faction": "faction_c"}
        mock_db.reference.return_value = mock_poi_ref
        
        npc_list = [
            # NPC belongs to both factions - contributes to both
            {"faction_affiliations": ["faction_a", "faction_b"], "role": "leader", "npc_id": "npc_1"},
            {"faction_affiliations": ["faction_b"], "role": "guard", "npc_id": "npc_2"},
        ]
        
        result = simulate_revolt_in_poi(
            region_id="region_1",
            poi_id="poi_1",
            factions_present=["faction_a", "faction_b"],
            npc_list=npc_list,
            tension_level=90.0
        )
        
        # faction_b should win (leader 10 + guard 5 = 15 vs faction_a with leader 10)
        assert result is not None
        assert result["winner"] == "faction_b"
        assert result["faction_strength"]["faction_b"] > result["faction_strength"]["faction_a"]
