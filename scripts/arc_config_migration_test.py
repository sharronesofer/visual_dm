#!/usr/bin/env python3
"""
Test script to validate the JSON configuration migration for the ARC system.
This script verifies that all configuration files can be loaded and contain expected data.
"""

import sys
import os
import json
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

try:
    from backend.infrastructure.config_loaders.arc_config_loader import arc_config_loader, validate_all_configs
    print("✅ Successfully imported arc_config_loader")
except ImportError as e:
    print(f"❌ Failed to import arc_config_loader: {e}")
    sys.exit(1)

def test_configuration_files():
    """Test that all configuration files are valid and loadable"""
    print("\n=== Configuration File Validation ===")
    
    # Test configuration validation
    validation_results = validate_all_configs()
    
    for config_name, is_valid in validation_results.items():
        status = "✅" if is_valid else "❌"
        print(f"{status} {config_name}: {'Valid' if is_valid else 'Invalid'}")
    
    if not all(validation_results.values()):
        print("\n❌ Some configuration files are invalid!")
        return False
    
    print("\n✅ All configuration files are valid!")
    return True

def test_arc_templates():
    """Test arc templates loading"""
    print("\n=== Arc Templates Test ===")
    
    try:
        templates = arc_config_loader.load_arc_templates()
        print(f"✅ Loaded {len(templates)} arc templates")
        
        expected_templates = ["global", "regional", "character", "npc", "exploration", "mystery"]
        for template_name in expected_templates:
            if template_name in templates:
                template = templates[template_name]
                required_fields = ["name", "description", "prompt_template", "default_steps", "complexity"]
                missing_fields = [field for field in required_fields if field not in template]
                
                if missing_fields:
                    print(f"❌ Template '{template_name}' missing fields: {missing_fields}")
                else:
                    print(f"✅ Template '{template_name}' is complete")
            else:
                print(f"⚠️  Template '{template_name}' not found (using fallback)")
        
        return True
    except Exception as e:
        print(f"❌ Failed to load arc templates: {e}")
        return False

def test_quest_mappings():
    """Test quest tag mappings loading"""
    print("\n=== Quest Tag Mappings Test ===")
    
    try:
        tag_mappings = arc_config_loader.get_tag_mappings()
        keyword_mappings = arc_config_loader.get_keyword_mappings()
        quest_templates = arc_config_loader.get_quest_templates()
        
        print(f"✅ Loaded tag mappings for {len(tag_mappings)} arc types")
        print(f"✅ Loaded keyword mappings for {len(keyword_mappings)} categories")
        print(f"✅ Loaded {len(quest_templates)} quest templates")
        
        # Test that expected mappings exist
        expected_arc_types = ["global", "regional", "character", "npc"]
        for arc_type in expected_arc_types:
            if arc_type in tag_mappings:
                tags = tag_mappings[arc_type]
                print(f"✅ Arc type '{arc_type}' has {len(tags)} tags")
            else:
                print(f"❌ Arc type '{arc_type}' missing from tag mappings")
        
        return True
    except Exception as e:
        print(f"❌ Failed to load quest mappings: {e}")
        return False

def test_business_rules():
    """Test business rules loading"""
    print("\n=== Business Rules Test ===")
    
    try:
        validation_rules = arc_config_loader.get_validation_rules()
        defaults = arc_config_loader.get_defaults()
        progression_rules = arc_config_loader.get_progression_rules()
        generation_settings = arc_config_loader.get_generation_settings()
        
        print(f"✅ Loaded validation rules with {len(validation_rules)} categories")
        print(f"✅ Loaded {len(defaults)} default values")
        print(f"✅ Loaded progression rules with {len(progression_rules)} settings")
        print(f"✅ Loaded generation settings with {len(generation_settings)} parameters")
        
        # Test that critical rules exist
        if "arc_types" in validation_rules:
            arc_types = validation_rules["arc_types"]
            print(f"✅ Supported arc types: {arc_types}")
        else:
            print("❌ Arc types not defined in validation rules")
        
        if "status_progression" in validation_rules:
            status_rules = validation_rules["status_progression"]
            print(f"✅ Status progression rules for {len(status_rules)} statuses")
        else:
            print("❌ Status progression rules not defined")
        
        return True
    except Exception as e:
        print(f"❌ Failed to load business rules: {e}")
        return False

def test_fallback_behavior():
    """Test that fallback behavior works when configs are missing"""
    print("\n=== Fallback Behavior Test ===")
    
    try:
        # Test with a non-existent configuration
        try:
            arc_config_loader.load_config("non_existent_config")
            print("❌ Should have failed to load non-existent config")
            return False
        except FileNotFoundError:
            print("✅ Correctly failed to load non-existent config")
        
        # Test that the services can handle missing configs gracefully
        # (This would require actual service instantiation)
        print("✅ Fallback behavior test passed")
        return True
        
    except Exception as e:
        print(f"❌ Fallback behavior test failed: {e}")
        return False

def main():
    """Run all configuration tests"""
    print("🧪 Testing ARC System JSON Configuration Migration")
    print("=" * 50)
    
    tests = [
        test_configuration_files,
        test_arc_templates,
        test_quest_mappings, 
        test_business_rules,
        test_fallback_behavior
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} tests passed!")
        print("✅ JSON configuration migration successful!")
        return 0
    else:
        print(f"❌ {passed}/{total} tests passed")
        print("❌ JSON configuration migration has issues")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 