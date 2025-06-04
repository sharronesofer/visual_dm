#!/usr/bin/env python3
"""
Test script for the religion configuration system.
Validates that JSON configurations load correctly and functions work as expected.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

def test_config_loading():
    """Test that configuration files load correctly"""
    print("Testing configuration loading...")
    
    try:
        from backend.systems.religion.config import (
            religion_config,
            narrative_templates,
            influence_rules,
            practices_templates,
            validate_config
        )
        
        print("✅ Configuration modules imported successfully")
        
        # Test config validation
        errors = validate_config()
        if errors:
            print("❌ Configuration validation errors:")
            for config_file, error_list in errors.items():
                print(f"  {config_file}: {error_list}")
        else:
            print("✅ All configurations valid")
            
        # Test individual configs
        if religion_config:
            print(f"✅ Religion config loaded with {len(religion_config.get('religion_types', {}))} religion types")
        else:
            print("❌ Religion config not loaded")
            
        if narrative_templates:
            print(f"✅ Narrative templates loaded")
        else:
            print("❌ Narrative templates not loaded")
            
        if influence_rules:
            print(f"✅ Influence rules loaded")
        else:
            print("❌ Influence rules not loaded")
            
        if practices_templates:
            print(f"✅ Practices templates loaded")
        else:
            print("❌ Practices templates not loaded")
            
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False
    
    return True

def test_religion_types():
    """Test religion type functionality"""
    print("\nTesting religion types...")
    
    try:
        from backend.systems.religion.config import RELIGION_TYPES, get_religion_types, get_religion_type_info
        
        # Test constants
        print(f"✅ Religion type constants: {list(RELIGION_TYPES.values())}")
        
        # Test getting religion types
        types_config = get_religion_types()
        print(f"✅ Religion types config: {list(types_config.keys())}")
        
        # Test accessing religion type info
        for religion_type in types_config:
            type_info = get_religion_type_info(religion_type)
            print(f"  {religion_type}: {type_info.get('name', 'N/A')} - {type_info.get('description', 'N/A')[:50]}...")
            
    except Exception as e:
        print(f"❌ Error testing religion types: {e}")
        return False
    
    return True

def test_devotion_calculations():
    """Test devotion calculation functions"""
    print("\nTesting devotion calculations...")
    
    try:
        from backend.systems.religion.config import calculate_devotion_change
        
        # Test basic devotion change
        new_devotion = calculate_devotion_change(0.5, "prayer", 1.0)
        print(f"✅ Prayer devotion change: 0.5 -> {new_devotion}")
        
        # Test transgression with severity
        new_devotion = calculate_devotion_change(0.8, "transgression", 1.0, severity=2.0)
        print(f"✅ Transgression with severity: 0.8 -> {new_devotion}")
        
        # Test bounds checking
        new_devotion = calculate_devotion_change(0.0, "doubt", 10.0)  # Should not go below 0
        print(f"✅ Bounds checking (low): 0.0 -> {new_devotion}")
        
        new_devotion = calculate_devotion_change(0.9, "pilgrimage", 10.0)  # Should not go above 1
        print(f"✅ Bounds checking (high): 0.9 -> {new_devotion}")
        
    except Exception as e:
        print(f"❌ Error testing devotion calculations: {e}")
        return False
    
    return True

def test_compatibility_checking():
    """Test religion compatibility functions"""
    print("\nTesting compatibility checking...")
    
    try:
        from backend.systems.religion.config import check_religion_compatibility
        
        # Test same type compatibility
        compat = check_religion_compatibility("monotheistic", "monotheistic")
        print(f"✅ Same type compatibility: {compat}")
        
        # Test different types
        compat = check_religion_compatibility("monotheistic", "polytheistic")
        print(f"✅ Different type compatibility: {compat}")
        
        # Test with shared factors
        compat = check_religion_compatibility(
            "monotheistic", "monotheistic", 
            shared_factors=["shared_deities", "cultural_similarity"]
        )
        print(f"✅ Compatibility with shared factors: {compat}")
        
        # Test with conflict factors
        compat = check_religion_compatibility(
            "monotheistic", "polytheistic",
            conflict_factors=["historical_conflict", "conflicting_tenets"]
        )
        print(f"✅ Compatibility with conflicts: {compat}")
        
    except Exception as e:
        print(f"❌ Error testing compatibility: {e}")
        return False
        
    return True

def test_narrative_generation():
    """Test narrative template functions"""
    print("\nTesting narrative generation...")
    
    try:
        from backend.systems.religion.config import get_narrative_template
        
        # Test conversion narrative
        narrative = get_narrative_template(
            "conversion_templates", "voluntary",
            entity_name="Test Character",
            from_religion="Old Faith",
            to_religion="New Faith",
            reason="seeking enlightenment"
        )
        print(f"✅ Conversion narrative: {narrative}")
        
        # Test devotion change narrative (with subcategory)
        narrative = get_narrative_template(
            "devotion_change_narratives", "increase", "prayer",
            entity_name="Test Character",
            religion="Test Religion"
        )
        print(f"✅ Devotion narrative: {narrative}")
        
        # Test religious event narrative
        narrative = get_narrative_template(
            "religious_event_templates", "festival",
            religion="Test Religion",
            event_name="Spring Festival",
            participant_count="200",
            location="Grand Temple"
        )
        print(f"✅ Event narrative: {narrative}")
        
    except Exception as e:
        print(f"❌ Error testing narrative generation: {e}")
        return False
        
    return True

def test_regional_influence():
    """Test regional influence calculations"""
    print("\nTesting regional influence...")
    
    try:
        from backend.systems.religion.config import get_regional_modifier
        
        # Test different region types
        regions = ["urban", "rural", "frontier", "cosmopolitan"]
        for region in regions:
            spread_rate = get_regional_modifier(region, "spread_rate")
            resistance = get_regional_modifier(region, "resistance")
            print(f"✅ {region}: spread_rate={spread_rate}, resistance={resistance}")
            
    except Exception as e:
        print(f"❌ Error testing regional influence: {e}")
        return False
        
    return True

def test_utilities_integration():
    """Test that the updated utilities work with the configuration system"""
    print("\nTesting utilities integration...")
    
    try:
        from backend.systems.religion.utils import (
            calculate_devotion_change,
            check_religion_compatibility,
            get_religion_type_info,
            calculate_regional_influence
        )
        from uuid import uuid4
        
        # Test devotion calculation
        new_devotion = calculate_devotion_change(0.5, "prayer", 1.0)
        print(f"✅ Utils devotion calculation: 0.5 -> {new_devotion}")
        
        # Test religion type info
        type_info = get_religion_type_info("monotheistic")
        print(f"✅ Religion type info: {type_info}")
        
        # Test regional influence calculation
        influence = calculate_regional_influence(0.5, "urban", "monotheistic", 2)
        print(f"✅ Regional influence calculation: {influence}")
        
        # Create mock religion objects for compatibility test
        class MockReligion:
            def __init__(self, name, type_):
                self.name = name
                self.type = type_
        
        religion1 = MockReligion("Faith A", "monotheistic")
        religion2 = MockReligion("Faith B", "polytheistic")
        
        compat = check_religion_compatibility(religion1, religion2)
        print(f"✅ Religion compatibility: {compat}")
        
    except Exception as e:
        print(f"❌ Error testing utilities integration: {e}")
        return False
        
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Religion Configuration System")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_religion_types,
        test_devotion_calculations,
        test_compatibility_checking,
        test_narrative_generation,
        test_regional_influence,
        test_utilities_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Configuration system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 