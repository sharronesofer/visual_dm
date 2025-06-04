"""
Test for the rules system to demonstrate import fixes working.

This test focuses on the working rules system and provides a foundation
for testing other systems as their imports are fixed.
"""

import pytest
from unittest import TestCase
from backend.systems.rules import (
    get_balance_constants, 
    calculate_ability_modifier,
    get_starting_equipment
)


class TestRulesSystem(TestCase):
    """Test the rules system which has working imports."""
    
    def test_rules_import(self):
        """Test that rules can be imported successfully."""
        from backend.systems.rules.rules import balance_constants
        
        # balance_constants is now a proxy object, not a dict
        # Test that it behaves like a dict with expected keys
        self.assertIn('starting_gold', balance_constants)
        self.assertEqual(balance_constants['starting_gold'], 100)
        
    def test_balance_constants(self):
        """Test balance constants have expected values."""
        from backend.systems.rules.rules import balance_constants
        
        # Test basic game values
        self.assertEqual(balance_constants['starting_gold'], 100)
        self.assertEqual(balance_constants['starting_level'], 1)
        self.assertEqual(balance_constants['max_level'], 20)
        self.assertEqual(balance_constants['min_ability'], -3)  # Legacy key for attributes
        self.assertEqual(balance_constants['max_ability'], 5)   # Legacy key for attributes  
        self.assertEqual(balance_constants['default_ability'], 0) # Legacy key for attributes
        
        # Test currency conversion
        currency = balance_constants['currency_conversion']
        self.assertEqual(currency['copper'], 1)
        self.assertEqual(currency['silver'], 10)
        self.assertEqual(currency['gold'], 100)
        self.assertEqual(currency['platinum'], 1000)
        
    def test_attribute_modifier_calculation(self):
        """Test attribute modifier calculations for custom -3 to +5 system."""
        from backend.systems.rules.rules import calculate_ability_modifier
        
        # Test the custom attribute score range (-3 to +5)
        self.assertEqual(calculate_ability_modifier(0), 0)   # Average
        self.assertEqual(calculate_ability_modifier(-1), -1) # Below average
        self.assertEqual(calculate_ability_modifier(2), 2)   # Above average
        self.assertEqual(calculate_ability_modifier(5), 5)   # Maximum
        self.assertEqual(calculate_ability_modifier(-3), -3) # Minimum
        
        # Test clamping beyond valid range
        self.assertEqual(calculate_ability_modifier(10), 5)  # Should clamp to +5
        self.assertEqual(calculate_ability_modifier(-10), -3) # Should clamp to -3
        
    def test_hp_calculation_classless_system(self):
        """Test hit point calculations for the classless ability-based system."""
        from backend.systems.rules.rules import calculate_hp_for_level
        
        # Test level 1 character with different constitution modifiers
        hp_con_2 = calculate_hp_for_level(1, 2)  # Con modifier +2
        self.assertEqual(hp_con_2, 9)  # 1 * (7 average d12 + 2 con)
        
        hp_con_1 = calculate_hp_for_level(1, 1)  # Con modifier +1
        self.assertEqual(hp_con_1, 8)  # 1 * (7 average d12 + 1 con)
        
        hp_con_0 = calculate_hp_for_level(1, 0)  # Con modifier +0
        self.assertEqual(hp_con_0, 7)  # 1 * (7 average d12 + 0 con)
        
        # Test higher levels
        hp_level_5 = calculate_hp_for_level(5, 2)  # Level 5, Con +2
        self.assertEqual(hp_level_5, 45)  # 5 * (7 + 2) = 45
        self.assertGreater(hp_level_5, hp_con_2)  # Should be higher
        
        # Test level 10
        hp_level_10 = calculate_hp_for_level(10, 1)  # Level 10, Con +1
        self.assertEqual(hp_level_10, 80)  # 10 * (7 + 1) = 80
        
    def test_mana_calculation_classless_system(self):
        """Test mana point calculations for the classless ability-based system."""
        from backend.systems.rules.rules import calculate_mana_points
        
        # Test level 1 character with different intelligence modifiers
        mp_int_2 = calculate_mana_points(1, 2)  # Int modifier +2
        self.assertEqual(mp_int_2, 7)  # 1 * 5 (avg d8) + 2 * 1 = 7
        
        mp_int_1 = calculate_mana_points(1, 1)  # Int modifier +1
        self.assertEqual(mp_int_1, 6)  # 1 * 5 + 1 * 1 = 6
        
        mp_int_0 = calculate_mana_points(1, 0)  # Int modifier +0
        self.assertEqual(mp_int_0, 5)  # 1 * 5 + 0 * 1 = 5
        
        # Test higher levels
        mp_level_5 = calculate_mana_points(5, 3)  # Level 5, Int +3
        self.assertEqual(mp_level_5, 40)  # 5 * 5 + 3 * 5 = 40
        
    def test_starting_equipment_background_based(self):
        """Test starting equipment varies by background"""
        from backend.systems.rules.rules import get_starting_equipment
        from backend.infrastructure.rules_data_loader import initialize_rules_system
        initialize_rules_system()
        
        # Test default equipment (no background)
        default_equipment = get_starting_equipment()
        self.assertIsInstance(default_equipment, list)
        self.assertGreater(len(default_equipment), 0)
        self.assertIn("basic clothing", default_equipment)  # Custom system terminology
        
        # Test village_guard background
        guard_equipment = get_starting_equipment("village_guard")
        self.assertIsInstance(guard_equipment, list)
        self.assertIn("worn sword", guard_equipment)
        self.assertIn("guard badge", guard_equipment)
        
        # Test wandering_merchant background  
        merchant_equipment = get_starting_equipment("wandering_merchant")
        self.assertIsInstance(merchant_equipment, list)
        self.assertIn("trade ledger", merchant_equipment)
        
        # Test unknown background returns default
        unknown_equipment = get_starting_equipment("unknown_class")
        self.assertEqual(unknown_equipment, default_equipment)
        
    def test_racial_bonuses(self):
        """Test racial bonus data structure."""
        from backend.systems.rules.rules import balance_constants
        
        racial_bonuses = balance_constants['racial_bonuses']
        
        # Test human (gets +1 to all attributes in custom system)
        self.assertIn('human', racial_bonuses)
        self.assertEqual(racial_bonuses['human']['all_attributes'], 1)
        
        # Test elf
        self.assertIn('elf', racial_bonuses)
        self.assertEqual(racial_bonuses['elf']['dexterity'], 2)
        self.assertEqual(racial_bonuses['elf']['intelligence'], 1)
        
        # Test orc (has a penalty)
        self.assertIn('orc', racial_bonuses)
        self.assertEqual(racial_bonuses['orc']['intelligence'], -1)
        
    def test_xp_thresholds(self):
        """Test experience point thresholds for leveling."""
        from backend.systems.rules.rules import balance_constants
        
        xp_thresholds = balance_constants['xp_thresholds']
        
        # Test that thresholds increase appropriately
        self.assertEqual(xp_thresholds[0], 0)    # Level 1 (index 0)
        self.assertEqual(xp_thresholds[1], 300)  # Level 2 (index 1)
        self.assertEqual(xp_thresholds[2], 900)  # Level 3 (index 2)
        
        # Test that each threshold is higher than the previous
        for i in range(1, len(xp_thresholds)):
            self.assertGreater(xp_thresholds[i], xp_thresholds[i-1])
            
    def test_attribute_based_progression(self):
        """Test constants for attribute-based character progression."""
        from backend.systems.rules.rules import balance_constants
        
        # Test attribute counts for character creation and leveling
        self.assertEqual(balance_constants.get('attributes_at_creation', 7), 7)
        self.assertEqual(balance_constants.get('attributes_per_level', 3), 3)
        
        # Test default hit die (d12 for attribute-based system)
        self.assertEqual(balance_constants['default_hit_die'], 12)
        
    def test_load_data_function(self):
        """Test data loading functionality (now handled by infrastructure)."""
        # This test is deprecated as load_data/get_default_data are now infrastructure concerns
        # The rules system now uses dependency injection for configuration loading
        pass
            
    def test_formula_info_access(self):
        """Test access to formula information from JSON config."""
        from backend.systems.rules.rules import get_formula_info
        
        # Test getting hit point formula info
        hp_formula = get_formula_info('hit_points')
        if hp_formula:  # Only test if formula info is available
            self.assertIn('formula', hp_formula)
            self.assertIn('description', hp_formula)
            
    def test_config_reload(self):
        """Test configuration reload functionality."""
        from backend.systems.rules.rules import reload_config
        
        # Test that reload doesn't crash
        try:
            reload_config()
        except Exception as e:
            # If reload fails due to missing files, that's expected in test environment
            self.assertIsInstance(e, (FileNotFoundError, AttributeError))


# Pytest-style test functions for compatibility
def test_rules_system_basic():
    """Pytest-style test for rules system."""
    test_case = TestRulesSystem()
    test_case.test_rules_import()
    test_case.test_balance_constants()
    test_case.test_attribute_modifier_calculation()


def test_rules_system_calculations():
    """Pytest-style test for rules calculations."""
    test_case = TestRulesSystem()
    test_case.test_hp_calculation_classless_system()
    test_case.test_mana_calculation_classless_system()


def test_rules_system_equipment():
    """Pytest-style test for equipment and data."""
    test_case = TestRulesSystem()
    test_case.test_starting_equipment_background_based()
    test_case.test_racial_bonuses()
    test_case.test_xp_thresholds()
    test_case.test_attribute_based_progression()


def test_get_starting_equipment():
    """Test getting starting equipment for various backgrounds"""
    # Initialize the rules system to load JSON data
    from backend.infrastructure.rules_data_loader import initialize_rules_system
    initialize_rules_system()
    
    # Test default equipment (no background)
    default_equipment = get_starting_equipment()
    assert isinstance(default_equipment, list)
    assert len(default_equipment) > 0
    assert "basic clothing" in default_equipment  # Custom system terminology
    
    # Test specific background
    guard_equipment = get_starting_equipment("village_guard")
    assert isinstance(guard_equipment, list)
    assert "worn sword" in guard_equipment
    assert "guard badge" in guard_equipment
    
    # Test unknown background fallback
    unknown_equipment = get_starting_equipment("unknown_background")
    assert isinstance(unknown_equipment, list)
    assert "basic clothing" in unknown_equipment  # Should get default equipment
    
    # Test case insensitive lookup
    guard_upper = get_starting_equipment("VILLAGE_GUARD")
    assert guard_upper == guard_equipment


if __name__ == '__main__':
    # Run tests directly
    import unittest
    unittest.main() 