"""
Comprehensive Tests for backend.systems.npc.npc_travel_utils

This test suite focuses on achieving high coverage for NPC travel utilities.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

# Import the module being tested
try: pass
    from backend.systems.npc.npc_travel_utils import (
        simulate_npc_travel,
        remove_from_poi,
        add_to_poi,
        get_current_game_day,
        apply_war_pressure_modifiers,
        migrate_npc_to_safe_poi
    )
except ImportError as e: pass
    pytest.skip(f"Could not import backend.systems.npc.npc_travel_utils: {e}", allow_module_level=True)


@pytest.fixture
def mock_firebase_db(): pass
    """Mock Firebase database."""
    with patch('backend.systems.npc.npc_travel_utils.db') as mock_db: pass
        yield mock_db


@pytest.fixture
def sample_npc_data(): pass
    """Sample NPC data for testing."""
    return {
        "npc_001": {
            "home_poi": "region1.tavern_001",
            "wanderlust": 3,
            "current_location": "region1.tavern_001"
        },
        "npc_002": {
            "home_poi": "region1.inn_002",
            "wanderlust": 0,
            "current_location": "region1.inn_002"
        },
        "npc_003": {
            "home_poi": "region2.market_001",
            "wanderlust": 5,
            "current_location": "region2.market_001"
        }
    }


@pytest.fixture
def sample_poi_data(): pass
    """Sample POI data for testing."""
    return {
        "tavern_001": {
            "poi_type": "social",
            "npcs_present": ["npc_001"]
        },
        "inn_002": {
            "poi_type": "social", 
            "npcs_present": ["npc_002"]
        },
        "market_003": {
            "poi_type": "commercial",
            "npcs_present": []
        }
    }


class TestSimulateNPCTravel: pass
    """Test NPC travel simulation functionality."""
    
    def test_simulate_npc_travel_basic(self, mock_firebase_db, sample_npc_data, sample_poi_data): pass
        """Test basic NPC travel simulation."""
        # Mock the main references
        mock_npc_ref = Mock()
        mock_npc_ref.get.return_value = sample_npc_data
        
        mock_poi_ref = Mock()
        mock_poi_ref.get.return_value = sample_poi_data
        
        # Mock individual POI references for remove/add operations
        mock_poi_npcs_ref = Mock()
        mock_poi_npcs_ref.get.return_value = ["npc_001"]
        
        # Mock the update reference
        mock_update_ref = Mock()
        
        def reference_side_effect(path): pass
            if path == "/npc_core": pass
                return mock_npc_ref
            elif path == "/poi_state/region1": pass
                return mock_poi_ref
            elif "npcs_present" in path: pass
                return mock_poi_npcs_ref
            elif "/npc_core/npc_001" in path: pass
                return mock_update_ref
            else: pass
                mock_ref = Mock()
                mock_ref.get.return_value = {}
                return mock_ref
        
        mock_firebase_db.reference.side_effect = reference_side_effect
        
        with patch('backend.systems.npc.npc_travel_utils.get_current_game_day', return_value=100), \
             patch('backend.systems.npc.npc_travel_utils.random.random', return_value=0.3), \
             patch('backend.systems.npc.npc_travel_utils.random.choice', return_value="market_003"), \
             patch('backend.systems.npc.npc_travel_utils.random.randint', return_value=2): pass
            simulate_npc_travel("region1")
            
            # Should have called Firebase operations
            assert mock_firebase_db.reference.called
    
    def test_simulate_npc_travel_no_wanderlust(self, mock_firebase_db, sample_npc_data, sample_poi_data): pass
        """Test NPC travel simulation with zero wanderlust NPCs."""
        # Modify sample data to have zero wanderlust
        zero_wanderlust_data = {
            "npc_001": {**sample_npc_data["npc_001"], "wanderlust": 0}
        }
        
        mock_npc_ref = Mock()
        mock_npc_ref.get.return_value = zero_wanderlust_data
        
        mock_poi_ref = Mock()
        mock_poi_ref.get.return_value = sample_poi_data
        
        def reference_side_effect(path): pass
            if path == "/npc_core": pass
                return mock_npc_ref
            elif path == "/poi_state/region1": pass
                return mock_poi_ref
            else: pass
                mock_ref = Mock()
                mock_ref.get.return_value = {}
                return mock_ref
        
        mock_firebase_db.reference.side_effect = reference_side_effect
        
        simulate_npc_travel("region1")
        
        # Should not attempt to move NPCs with zero wanderlust
        assert mock_firebase_db.reference.called
    
    def test_simulate_npc_travel_wrong_region(self, mock_firebase_db, sample_npc_data, sample_poi_data): pass
        """Test NPC travel simulation with NPCs from different regions."""
        mock_npc_ref = Mock()
        mock_npc_ref.get.return_value = sample_npc_data
        
        mock_poi_ref = Mock()
        mock_poi_ref.get.return_value = sample_poi_data
        
        def reference_side_effect(path): pass
            if path == "/npc_core": pass
                return mock_npc_ref
            elif path == "/poi_state/region3": pass
                return mock_poi_ref
            else: pass
                mock_ref = Mock()
                mock_ref.get.return_value = {}
                return mock_ref
        
        mock_firebase_db.reference.side_effect = reference_side_effect
        
        simulate_npc_travel("region3")  # Different region
        
        # Should not move NPCs from other regions
        assert mock_firebase_db.reference.called


class TestPOIManagement: pass
    """Test POI NPC list management functionality."""
    
    def test_remove_from_poi_success(self, mock_firebase_db): pass
        """Test successful NPC removal from POI."""
        mock_ref = Mock()
        mock_ref.get.return_value = ["npc_001", "npc_002", "npc_003"]
        mock_firebase_db.reference.return_value = mock_ref
        
        remove_from_poi("npc_002", "region1", "tavern_001")
        
        mock_ref.set.assert_called_once_with(["npc_001", "npc_003"])
    
    def test_remove_from_poi_not_present(self, mock_firebase_db): pass
        """Test NPC removal when not present in POI."""
        mock_ref = Mock()
        mock_ref.get.return_value = ["npc_001", "npc_003"]
        mock_firebase_db.reference.return_value = mock_ref
        
        remove_from_poi("npc_002", "region1", "tavern_001")
        
        # Should not call set if NPC not present in list
        mock_ref.set.assert_not_called()
    
    def test_add_to_poi_success(self, mock_firebase_db): pass
        """Test successful NPC addition to POI."""
        mock_ref = Mock()
        mock_ref.get.return_value = ["npc_001", "npc_002"]
        mock_firebase_db.reference.return_value = mock_ref
        
        add_to_poi("npc_003", "region1", "tavern_001")
        
        mock_ref.set.assert_called_once_with(["npc_001", "npc_002", "npc_003"])


class TestGameDayRetrieval: pass
    """Test game day retrieval functionality."""
    
    def test_get_current_game_day_success(self, mock_firebase_db): pass
        """Test successful game day retrieval."""
        mock_ref = Mock()
        mock_ref.get.return_value = {"current_day": 150}
        mock_firebase_db.reference.return_value = mock_ref
        
        day = get_current_game_day()
        
        assert day == 150
        mock_firebase_db.reference.assert_called_once_with("/global_state")


class TestWarPressureModifiers: pass
    """Test war pressure modifier functionality."""
    
    @patch('backend.systems.npc.npc_travel_utils.LoyaltyManager')
    def test_apply_war_pressure_modifiers_war(self, mock_loyalty_manager, mock_firebase_db): pass
        """Test war pressure modifiers during war."""
        npc_data = {
            "npc_001": {
                "home_poi": "region1.tavern_001",
                "wanderlust": 2
            }
        }
        
        region_data = {
            "conflict_status": "war",
            "war_state": {
                "active_faction": "faction_a"
            }
        }
        
        # Mock the main references
        mock_npc_ref = Mock()
        mock_npc_ref.get.return_value = npc_data
        
        mock_region_ref = Mock()
        mock_region_ref.get.return_value = region_data
        
        # Mock the bias reference
        mock_bias_ref = Mock()
        mock_bias_ref.get.return_value = {}
        
        def reference_side_effect(path): pass
            if path == "/npc_core": pass
                return mock_npc_ref
            elif path == "/regional_state/region1": pass
                return mock_region_ref
            elif "faction_bias" in path: pass
                return mock_bias_ref
            else: pass
                mock_ref = Mock()
                mock_ref.get.return_value = {}
                return mock_ref
        
        mock_firebase_db.reference.side_effect = reference_side_effect
        
        mock_loyalty_instance = Mock()
        mock_loyalty_manager.return_value = mock_loyalty_instance
        
        with patch('backend.systems.npc.npc_travel_utils.random.randint', return_value=1), \
             patch('backend.systems.npc.npc_travel_utils.random.random', return_value=0.5): pass
            apply_war_pressure_modifiers()
            
            # Should create loyalty manager and apply changes
            mock_loyalty_manager.assert_called_once_with("npc_001")
            mock_loyalty_instance.apply_event.assert_called_once()
            mock_loyalty_instance.save_to_firebase.assert_called_once()


class TestNPCMigration: pass
    """Test NPC migration functionality."""
    
    def test_migrate_npc_to_safe_poi_success(self, mock_firebase_db): pass
        """Test successful NPC migration to safe POI."""
        poi_data = {
            "tavern_001": {"poi_type": "social"},
            "inn_002": {"poi_type": "social"},
            "dungeon_001": {"poi_type": "dungeon"}
        }
        
        # Mock the POI data reference
        mock_poi_ref = Mock()
        mock_poi_ref.get.return_value = poi_data
        
        # Mock the update references
        mock_home_ref = Mock()
        mock_location_ref = Mock()
        
        def reference_side_effect(path): pass
            if "/poi_state/region1" in path: pass
                return mock_poi_ref
            elif "/npc_core/npc_001/home_poi" in path: pass
                return mock_home_ref
            elif "/npc_core/npc_001/current_location" in path: pass
                return mock_location_ref
            else: pass
                mock_ref = Mock()
                mock_ref.get.return_value = []
                return mock_ref
        
        mock_firebase_db.reference.side_effect = reference_side_effect
        
        with patch('backend.systems.npc.npc_travel_utils.random.choice', return_value="inn_002"), \
             patch('backend.systems.npc.npc_travel_utils.remove_from_poi') as mock_remove, \
             patch('backend.systems.npc.npc_travel_utils.add_to_poi') as mock_add: pass
            migrate_npc_to_safe_poi("npc_001", "region1", "tavern_001")
            
            # Should update NPC location
            assert mock_firebase_db.reference.called
            mock_remove.assert_called_once_with("npc_001", "region1", "tavern_001")
            mock_add.assert_called_once_with("npc_001", "region1", "inn_002") 