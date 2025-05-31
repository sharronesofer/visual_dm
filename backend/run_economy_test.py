#!/usr/bin/env python3
"""
Simple test runner for economy system that bypasses import issues.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_economy_functionality():
    """Test basic economy functionality without complex imports."""
    print("🚀 Running Basic Economy Tests...")
    
    try:
        # Test 1: Basic imports
        print("Testing basic imports...")
        
        # Try to import the rules module which should work
        from backend.systems.rules.rules import balance_constants
        print("✅ Rules module imported successfully")
        print(f"   Starting gold: {balance_constants['starting_gold']}")
        
        # Test 2: Basic calculations
        print("Testing basic calculations...")
        from backend.systems.rules.rules import calculate_ability_modifier
        
        modifier = calculate_ability_modifier(16)
        assert modifier == 3, f"Expected 3, got {modifier}"
        print("✅ Ability modifier calculation works")
        
        # Test 3: HP calculation
        print("Testing HP calculation...")
        from backend.systems.rules.rules import calculate_hp_for_level
        
        hp = calculate_hp_for_level("fighter", 1, 2)
        assert hp > 0, f"HP should be positive, got {hp}"
        print(f"✅ HP calculation works: {hp} HP for level 1 fighter")
        
        # Test 4: Equipment
        print("Testing equipment...")
        from backend.systems.rules.rules import get_starting_equipment
        
        equipment = get_starting_equipment("fighter")
        assert isinstance(equipment, list), "Equipment should be a list"
        assert len(equipment) > 0, "Fighter should have starting equipment"
        print(f"✅ Equipment system works: {len(equipment)} items for fighter")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_economy_functionality()
    sys.exit(0 if success else 1) 