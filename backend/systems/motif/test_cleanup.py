#!/usr/bin/env python3
"""
Test script to verify Motif System cleanup implementation
"""

import sys
import os
from pathlib import Path

def test_config_system():
    """Test that the configuration system is working."""
    print("Testing configuration system...")
    
    try:
        from backend.infrastructure.config.motif_config_loader import config
        
        # Test chaos events
        chaos_events = config.get_chaos_events()
        print(f"✅ Loaded {len(chaos_events)} chaos events")
        
        # Test categories
        categories = config.get_chaos_categories()
        print(f"✅ Found {len(categories)} chaos categories: {categories}")
        
        # Test action mapping
        action_mapping = config.get_action_motif_mapping()
        print(f"✅ Loaded {len(action_mapping)} action-to-motif mappings")
        
        # Test theme relationships
        opposing = config.get_opposing_themes()
        complementary = config.get_complementary_themes()
        print(f"✅ Loaded {len(opposing)} opposing pairs and {len(complementary)} complementary pairs")
        
        # Test settings
        max_motifs = config.get_setting("max_concurrent_motifs_per_region")
        print(f"✅ Settings loaded, max motifs per region: {max_motifs}")
        
        print("✅ Configuration system working correctly\n")
        return True
        
    except Exception as e:
        print(f"❌ Configuration system error: {e}\n")
        return False

def test_business_utils():
    """Test that business utilities are working with configuration."""
    print("Testing business utilities...")
    
    try:
        from backend.systems.motif.utils import roll_chaos_event
        
        # Test chaos event generation
        event = roll_chaos_event()
        print(f"✅ Generated chaos event: {event}")
        
        # Test with category
        event_social = roll_chaos_event("social")
        print(f"✅ Generated social chaos event: {event_social}")
        
        print("✅ Business utilities working correctly\n")
        return True
        
    except Exception as e:
        print(f"❌ Business utilities error: {e}\n")
        return False

def test_imports():
    """Test that all imports are working after cleanup."""
    print("Testing imports after cleanup...")
    
    try:
        # Test config import from new location
        from backend.infrastructure.config.motif_config_loader import config
        print("✅ Config import from infrastructure works")
        
        # Test utils imports 
        from backend.systems.motif.utils import roll_chaos_event
        from backend.systems.motif.utils.business_utils import generate_motif_name
        print("✅ Utils imports work")
        
        # Test services imports
        from backend.systems.motif.services.service import MotifService
        print("✅ Services imports work")
        
        print("✅ All imports working correctly\n")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}\n")
        return False

def test_removed_files():
    """Test that legacy files have been properly removed."""
    print("Testing removed files...")
    
    base_path = Path(__file__).parent
    
    removed_files = [
        "utils/chaos_utils.py",
        "services/motif_engine_class.py",
        "services/services.py"
    ]
    
    all_removed = True
    for file_path in removed_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"❌ File should be removed but still exists: {file_path}")
            all_removed = False
        else:
            print(f"✅ File properly removed: {file_path}")
    
    if all_removed:
        print("✅ All legacy files properly removed\n")
    else:
        print("❌ Some legacy files still exist\n")
    
    return all_removed

def test_configuration_files():
    """Test that configuration files exist and are valid in their new locations."""
    print("Testing configuration files in new locations...")
    
    # Get project root path
    base_path = Path(__file__).parent
    project_root = base_path
    while project_root.parent != project_root:
        if (project_root / "backend").exists() and (project_root / "data").exists():
            break
        project_root = project_root.parent
    
    # Configuration files in their new locations
    config_files = [
        ("backend/infrastructure/config/motif_config_loader.py", "Config loader in infrastructure"),
        ("data/systems/motif/motif_config.json", "JSON config data")
    ]
    
    all_exist = True
    for relative_path, description in config_files:
        full_path = project_root / relative_path
        if not full_path.exists():
            print(f"❌ {description} missing: {relative_path}")
            all_exist = False
        else:
            print(f"✅ {description} exists: {relative_path}")
    
    # Check that old config directory is removed
    old_config_dir = base_path / "config"
    if old_config_dir.exists():
        print(f"❌ Old config directory still exists: {old_config_dir}")
        all_exist = False
    else:
        print("✅ Old config directory properly removed")
    
    if all_exist:
        print("✅ All configuration files in correct new locations\n")
    else:
        print("❌ Some configuration files in wrong locations\n")
    
    return all_exist

def main():
    """Run all tests."""
    print("🧪 Motif System Cleanup Verification Tests\n")
    print("=" * 50)
    
    tests = [
        test_configuration_files,
        test_removed_files,
        test_imports,
        test_config_system,
        test_business_utils
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Cleanup successful!")
        return 0
    else:
        print("⚠️  Some tests failed. Review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 