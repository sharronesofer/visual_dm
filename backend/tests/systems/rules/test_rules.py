"""
Test for the rules system to demonstrate import fixes working.

This test focuses on the working rules system and provides a foundation
for testing other systems as their imports are fixed.
"""

import pytest
from unittest import TestCase


class TestRulesSystem(TestCase):
    """Test the rules system which has working imports."""
    
    def test_rules_import(self):
        """Test that rules can be imported successfully."""
        from backend.systems.rules.rules import balance_constants
        
        self.assertIsInstance(balance_constants, dict)
        self.assertIn('starting_gold', balance_constants)
        
    def test_balance_constants(self):
        """Test balance constants have expected values."""
        from backend.systems.rules.rules import balance_constants
        
        # Test basic game values
        self.assertEqual(balance_constants['starting_gold'], 100)
        self.assertEqual(balance_constants['starting_level'], 1)
        self.assertEqual(balance_constants['max_level'], 20)
        self.assertEqual(balance_constants['min_stat'], 3)
        self.assertEqual(balance_constants['max_stat'], 20)
        
        # Test currency conversion
        currency = balance_constants['currency_conversion']
        self.assertEqual(currency['copper'], 1)
        self.assertEqual(currency['silver'], 10)
        self.assertEqual(currency['gold'], 100)
        self.assertEqual(currency['platinum'], 1000)
        
    def test_ability_modifier_calculation(self):
        """Test ability modifier calculations."""
        from backend.systems.rules.rules import calculate_ability_modifier
        
        # Test standard ability scores
        self.assertEqual(calculate_ability_modifier(10), 0)  # Average
        self.assertEqual(calculate_ability_modifier(8), -1)   # Below average
        self.assertEqual(calculate_ability_modifier(12), 1)   # Above average
        self.assertEqual(calculate_ability_modifier(16), 3)   # High
        self.assertEqual(calculate_ability_modifier(20), 5)   # Maximum
        self.assertEqual(calculate_ability_modifier(3), -4)   # Minimum
        
    def test_proficiency_bonus_calculation(self):
        """Test proficiency bonus calculations."""
        from backend.systems.rules.rules import calculate_proficiency_bonus
        
        # Test level ranges
        self.assertEqual(calculate_proficiency_bonus(1), 2)   # Level 1-4
        self.assertEqual(calculate_proficiency_bonus(4), 2)   
        self.assertEqual(calculate_proficiency_bonus(5), 3)   # Level 5-8
        self.assertEqual(calculate_proficiency_bonus(8), 3)   
        self.assertEqual(calculate_proficiency_bonus(9), 4)   # Level 9-12
        self.assertEqual(calculate_proficiency_bonus(12), 4)  
        self.assertEqual(calculate_proficiency_bonus(20), 6)  # Level 17-20
        
        # Test edge cases
        self.assertEqual(calculate_proficiency_bonus(0), 2)   # Below minimum
        self.assertEqual(calculate_proficiency_bonus(25), 6)  # Above maximum
        
    def test_hp_calculation(self):
        """Test hit point calculations for different classes."""
        from backend.systems.rules.rules import calculate_hp_for_level
        
        # Test level 1 (max hit die + con modifier)
        hp_fighter_1 = calculate_hp_for_level("fighter", 1, 2)
        self.assertEqual(hp_fighter_1, 12)  # 10 (max d10) + 2 (con)
        
        hp_wizard_1 = calculate_hp_for_level("wizard", 1, 1)
        self.assertEqual(hp_wizard_1, 7)   # 6 (max d6) + 1 (con)
        
        # Test higher levels
        hp_fighter_5 = calculate_hp_for_level("fighter", 5, 2)
        self.assertGreater(hp_fighter_5, hp_fighter_1)  # Should be higher
        
        # Test unknown class defaults to d8
        hp_unknown = calculate_hp_for_level("unknown_class", 1, 0)
        self.assertEqual(hp_unknown, 8)  # 8 (d8) + 0 (con)
        
    def test_starting_equipment(self):
        """Test starting equipment generation."""
        from backend.systems.rules.rules import get_starting_equipment
        
        # Test known classes
        fighter_equipment = get_starting_equipment("fighter")
        self.assertIsInstance(fighter_equipment, list)
        self.assertGreater(len(fighter_equipment), 0)
        self.assertIn("chain mail", fighter_equipment)
        
        wizard_equipment = get_starting_equipment("wizard")
        self.assertIsInstance(wizard_equipment, list)
        self.assertIn("spellbook", wizard_equipment)
        
        # Test with background
        acolyte_equipment = get_starting_equipment("cleric", "acolyte")
        self.assertIn("holy symbol", acolyte_equipment)  # From both class and background
        
        # Test unknown class
        unknown_equipment = get_starting_equipment("unknown_class")
        self.assertEqual(unknown_equipment, ["basic equipment"])
        
    def test_racial_bonuses(self):
        """Test racial bonus data structure."""
        from backend.systems.rules.rules import balance_constants
        
        racial_bonuses = balance_constants['racial_bonuses']
        
        # Test human (gets +1 to all stats)
        self.assertIn('human', racial_bonuses)
        self.assertEqual(racial_bonuses['human']['all_stats'], 1)
        
        # Test elf
        self.assertIn('elf', racial_bonuses)
        self.assertEqual(racial_bonuses['elf']['dexterity'], 2)
        self.assertEqual(racial_bonuses['elf']['intelligence'], 1)
        
        # Test orc (has a penalty)
        self.assertIn('orc', racial_bonuses)
        self.assertEqual(racial_bonuses['orc']['intelligence'], -1)
        
    def test_class_hit_dice(self):
        """Test class hit dice data."""
        from backend.systems.rules.rules import balance_constants
        
        hit_dice = balance_constants['class_hit_dice']
        
        # Test expected hit dice
        self.assertEqual(hit_dice['barbarian'], 12)  # d12
        self.assertEqual(hit_dice['fighter'], 10)    # d10
        self.assertEqual(hit_dice['wizard'], 6)      # d6
        self.assertEqual(hit_dice['bard'], 8)        # d8
        
    def test_load_data_function(self):
        """Test data loading functionality."""
        from backend.systems.rules.rules import load_data, get_default_data
        
        # Test loading non-existent data returns defaults
        spells_data = load_data('spells')
        self.assertIsInstance(spells_data, dict)
        
        # Test get_default_data
        default_spells = get_default_data('spells')
        self.assertIn('cantrips', default_spells)
        self.assertIn('level_1', default_spells)
        
        default_classes = get_default_data('classes')
        self.assertIn('fighter', default_classes)
        self.assertIn('wizard', default_classes)


# Pytest-style test functions for compatibility
def test_rules_system_basic():
    """Pytest-style test for rules system."""
    test_case = TestRulesSystem()
    test_case.test_rules_import()
    test_case.test_balance_constants()
    test_case.test_ability_modifier_calculation()


def test_rules_system_calculations():
    """Pytest-style test for rules calculations."""
    test_case = TestRulesSystem()
    test_case.test_proficiency_bonus_calculation()
    test_case.test_hp_calculation()


def test_rules_system_equipment():
    """Pytest-style test for equipment and data."""
    test_case = TestRulesSystem()
    test_case.test_starting_equipment()
    test_case.test_racial_bonuses()
    test_case.test_class_hit_dice()
    test_case.test_load_data_function()


if __name__ == '__main__':
    # Run tests directly
    import unittest
    unittest.main() 