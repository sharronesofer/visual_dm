"""
Test module for equipment.set_bonus_utils

Tests set bonus utility functions according to Development Bible standards.
Tests actual implementation functions for equipment set bonus management.
"""

import pytest
from unittest.mock import Mock, patch

# Import the actual functions from the module
try:
    from backend.infrastructure.systems.equipment.utils.set_bonus_utils import (
        get_equipment_sets, get_equipment_set, get_item_set_membership,
        calculate_set_bonuses, apply_set_bonuses
    )
    set_bonus_utils_available = True
except ImportError:
    set_bonus_utils_available = False


@pytest.mark.skipif(not set_bonus_utils_available, reason="Set bonus utils module not available")
class TestSetBonusUtils:
    """Test class for set bonus utility functions matching Bible requirements"""
    
    def test_set_bonus_calculation(self):
        """Test set bonus calculation logic"""
        # Bible requirement: Equipment sets provide bonuses when multiple pieces are worn
        test_character_attributes = {
            "strength": 100,
            "defense": 50,
            "health": 200
        }
        
        # Mock set bonuses data
        mock_set_bonuses = {
            "active_sets": {
                "1": {
                    "name": "Warrior Set",
                    "equipped_count": 2,
                    "total_pieces": 3,
                    "active_bonuses": {
                        "2": {
                            "stats": {"strength": 10, "defense": 5}
                        }
                    }
                }
            }
        }
        
        result = apply_set_bonuses(test_character_attributes, mock_set_bonuses)
        
        # Bible requirement: Set bonuses should increase character attributes
        assert result["strength"] == 110  # Original 100 + 10 from set
        assert result["defense"] == 55    # Original 50 + 5 from set
        assert result["health"] == 200    # Unchanged
        
        # Bible requirement: Track applied bonuses for transparency
        assert "applied_set_bonuses" in result
        assert len(result["applied_set_bonuses"]) > 0
        
    def test_set_bonus_application_progression(self):
        """Test that set bonuses apply correctly as more pieces are equipped"""
        # Bible requirement: More pieces = better bonuses
        test_attributes = {"attack": 50}
        
        # Test with 2 pieces equipped
        two_piece_bonuses = {
            "active_sets": {
                "1": {
                    "name": "Test Set",
                    "equipped_count": 2,
                    "total_pieces": 4,
                    "active_bonuses": {
                        "2": {"stats": {"attack": 5}}
                    }
                }
            }
        }
        
        # Test with 4 pieces equipped (full set)
        four_piece_bonuses = {
            "active_sets": {
                "1": {
                    "name": "Test Set", 
                    "equipped_count": 4,
                    "total_pieces": 4,
                    "active_bonuses": {
                        "2": {"stats": {"attack": 5}},
                        "4": {"stats": {"attack": 10}}  # Additional bonus for full set
                    }
                }
            }
        }
        
        two_piece_result = apply_set_bonuses(test_attributes.copy(), two_piece_bonuses)
        four_piece_result = apply_set_bonuses(test_attributes.copy(), four_piece_bonuses)
        
        # Bible requirement: Full set should provide greater bonus than partial set
        assert two_piece_result["attack"] == 55   # 50 + 5
        assert four_piece_result["attack"] == 65  # 50 + 5 + 10
        
    def test_multiple_set_bonuses(self):
        """Test that multiple equipment sets can be active simultaneously"""
        # Bible requirement: Multiple set bonuses can be active at once
        test_attributes = {"strength": 100, "intelligence": 50}
        
        multiple_set_bonuses = {
            "active_sets": {
                "1": {
                    "name": "Warrior Set",
                    "equipped_count": 2,
                    "total_pieces": 3,
                    "active_bonuses": {
                        "2": {"stats": {"strength": 15}}
                    }
                },
                "2": {
                    "name": "Mage Set",
                    "equipped_count": 2,
                    "total_pieces": 3,
                    "active_bonuses": {
                        "2": {"stats": {"intelligence": 20}}
                    }
                }
            }
        }
        
        result = apply_set_bonuses(test_attributes, multiple_set_bonuses)
        
        # Bible requirement: Both set bonuses should apply
        assert result["strength"] == 115      # 100 + 15 from Warrior Set
        assert result["intelligence"] == 70   # 50 + 20 from Mage Set
        
        # Bible requirement: Track all applied bonuses
        assert len(result["applied_set_bonuses"]) == 2
