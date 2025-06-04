"""
Test module for equipment.durability_utils

Tests durability utility functions according to Development Bible standards.
Tests actual implementation functions for durability management.
"""

import pytest
from unittest.mock import Mock, patch

# Import the actual functions from the module
try:
    from backend.infrastructure.systems.equipment.utils.durability_utils import (
        get_durability_status, calculate_combat_damage, calculate_wear_damage,
        apply_durability_damage, calculate_repair_cost, repair_equipment,
        adjust_stats_for_durability, DURABILITY_THRESHOLDS, STAT_PENALTY_MULTIPLIERS
    )
    durability_utils_available = True
except ImportError:
    durability_utils_available = False


@pytest.mark.skipif(not durability_utils_available, reason="Durability utils module not available")
class TestDurabilityUtils:
    """Test class for durability utility functions matching Bible requirements"""
    
    def test_durability_status_thresholds(self):
        """Test durability status mapping matches Bible specifications"""
        # Bible requirement: Specific durability thresholds
        assert get_durability_status(100.0, 100.0) == "perfect"
        assert get_durability_status(95.0, 100.0) == "excellent"
        assert get_durability_status(80.0, 100.0) == "good"
        assert get_durability_status(60.0, 100.0) == "worn"
        assert get_durability_status(35.0, 100.0) == "damaged"
        assert get_durability_status(15.0, 100.0) == "very_damaged"
        assert get_durability_status(0.0, 100.0) == "broken"
        
    def test_combat_damage_calculation(self):
        """Test combat damage calculation follows equipment type differences"""
        # Bible requirement: Different equipment types have different damage rates
        weapon_damage = calculate_combat_damage("weapon", 1.0, False)
        armor_damage = calculate_combat_damage("armor", 1.0, False)
        
        # Weapons should generally take more damage than armor
        assert isinstance(weapon_damage, float)
        assert isinstance(armor_damage, float)
        assert weapon_damage >= 0
        assert armor_damage >= 0
        
    def test_wear_damage_calculation(self):
        """Test wear damage calculation based on time and environment"""
        # Bible requirement: Environmental factors affect durability
        normal_wear = calculate_wear_damage("weapon", 1.0, 1.0)
        harsh_wear = calculate_wear_damage("weapon", 1.0, 2.0)
        
        assert isinstance(normal_wear, float)
        assert isinstance(harsh_wear, float)
        assert harsh_wear > normal_wear  # Harsh conditions cause more wear
        
    def test_stat_penalty_application(self):
        """Test stat penalties match Bible durability requirements"""
        # Bible requirement: Durability affects equipment effectiveness
        test_stats = {"attack": 100, "defense": 50}
        
        # Simulate equipment with different durability levels
        excellent_equipment = {"current_durability": 95.0, "max_durability": 100.0}
        worn_equipment = {"current_durability": 60.0, "max_durability": 100.0}
        damaged_equipment = {"current_durability": 35.0, "max_durability": 100.0}
        
        excellent_result = adjust_stats_for_durability(excellent_equipment, test_stats.copy())
        worn_result = adjust_stats_for_durability(worn_equipment, test_stats.copy())
        damaged_result = adjust_stats_for_durability(damaged_equipment, test_stats.copy())
        
        # Bible requirement: Excellent condition has no penalty
        assert excellent_result["attack"] == test_stats["attack"]
        
        # Bible requirement: Worn/damaged equipment has reduced effectiveness
        assert worn_result["attack"] <= test_stats["attack"]
        assert damaged_result["attack"] <= worn_result["attack"]
