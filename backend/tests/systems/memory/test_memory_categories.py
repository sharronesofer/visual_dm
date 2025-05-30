from typing import Any
from typing import Dict
from typing import List
"""
Tests for backend.systems.memory.memory_categories

Comprehensive tests for memory categorization functionality.
"""

import pytest
from typing import Set, List, Dict, Any

# Import the module being tested
from backend.systems.memory.memory_categories import (
    MemoryCategory,
    MemoryCategoryMetadata,
    categorize_memory_content,
    apply_category_modifiers,
    get_category_metadata,
    get_category_modifier,
    register_custom_category,
    is_valid_category,
    get_all_categories,
    clear_custom_categories,
)


class TestMemoryCategory: pass
    """Test class for MemoryCategory enum"""
    
    def test_memory_category_values(self): pass
        """Test that memory category enum has expected values"""
        assert MemoryCategory.PERSONAL == "personal"
        assert MemoryCategory.TRAUMA == "trauma"
        assert MemoryCategory.WAR == "war"
        assert MemoryCategory.ARC == "arc"
        assert MemoryCategory.FACTION == "faction"
        assert MemoryCategory.LOCATION == "location"
        assert MemoryCategory.RELIGION == "religion"
        assert MemoryCategory.INTERACTION == "interaction"
        
    def test_memory_category_enum_properties(self): pass
        """Test that memory category enum behaves correctly"""
        # Test that it's a string enum
        assert isinstance(MemoryCategory.PERSONAL, str)
        
        # Test that we can iterate over categories
        categories = list(MemoryCategory)
        assert len(categories) > 0
        assert MemoryCategory.PERSONAL in categories


class TestMemoryCategoryMetadata: pass
    """Test class for MemoryCategoryMetadata"""
    
    def test_get_metadata_defined_category(self): pass
        """Test getting metadata for explicitly defined category"""
        metadata = MemoryCategoryMetadata.get_metadata(MemoryCategory.TRAUMA)
        
        assert metadata["display_name"] == "Traumatic Memory"
        assert metadata["description"] == "Negative, impactful experience"
        assert metadata["decay_modifier"] == 0.5
        assert metadata["importance_modifier"] == 1.5
        
    def test_get_metadata_undefined_category(self): pass
        """Test getting metadata for category without explicit metadata"""
        metadata = MemoryCategoryMetadata.get_metadata(MemoryCategory.CUSTOM)
        
        assert metadata["display_name"] == "Custom"  # Auto-generated from enum name
        assert metadata["description"] == "General memory category"
        assert metadata["decay_modifier"] == 1.0
        assert metadata["importance_modifier"] == 1.0
        
    def test_get_decay_modifier(self): pass
        """Test getting decay modifier for categories"""
        # Defined category
        assert MemoryCategoryMetadata.get_decay_modifier(MemoryCategory.TRAUMA) == 0.5
        
        # Undefined category (should use default)
        assert MemoryCategoryMetadata.get_decay_modifier(MemoryCategory.CUSTOM) == 1.0
        
    def test_get_importance_modifier(self): pass
        """Test getting importance modifier for categories"""
        # Defined category
        assert MemoryCategoryMetadata.get_importance_modifier(MemoryCategory.TRAUMA) == 1.5
        
        # Undefined category (should use default)
        assert MemoryCategoryMetadata.get_importance_modifier(MemoryCategory.CUSTOM) == 1.0


class TestCategorizeMemoryContent: pass
    """Test class for categorize_memory_content function"""
    
    def test_categorize_personal_memory(self): pass
        """Test categorization of personal memories"""
        content = "I feel very happy about this achievement"
        categories = categorize_memory_content(content)
        
        assert MemoryCategory.PERSONAL in categories
        
    def test_categorize_trauma_memory(self): pass
        """Test categorization of traumatic memories"""
        content = "I was terrified and hurt during the attack"
        categories = categorize_memory_content(content)
        
        assert MemoryCategory.TRAUMA in categories
        
    def test_categorize_war_memory(self): pass
        """Test categorization of war memories"""
        content = "The battle was fierce and the army fought bravely"
        categories = categorize_memory_content(content)
        
        assert MemoryCategory.WAR in categories
        assert MemoryCategory.COMBAT in categories
        
    def test_categorize_quest_memory(self): pass
        """Test categorization of quest memories"""
        content = "We embarked on a dangerous quest to find the artifact"
        categories = categorize_memory_content(content)
        
        assert MemoryCategory.QUEST in categories
        
    def test_categorize_faction_memory(self): pass
        """Test categorization of faction memories"""
        content = "The guild decided to form an alliance with our organization"
        categories = categorize_memory_content(content)
        
        assert MemoryCategory.FACTION in categories
        
    def test_categorize_location_memory(self): pass
        """Test categorization of location memories"""
        content = "The city was beautiful and the place was peaceful"
        categories = categorize_memory_content(content)
        
        assert MemoryCategory.LOCATION in categories
        
    def test_categorize_religion_memory(self): pass
        """Test categorization of religious memories"""
        content = "We prayed to the deity and showed our faith"
        categories = categorize_memory_content(content)
        
        assert MemoryCategory.RELIGION in categories
        
    def test_categorize_multiple_categories(self): pass
        """Test categorization with multiple categories"""
        content = "I feel afraid as the war rages in our city"
        categories = categorize_memory_content(content)
        
        assert MemoryCategory.PERSONAL in categories
        assert MemoryCategory.TRAUMA in categories
        assert MemoryCategory.WAR in categories
        assert MemoryCategory.LOCATION in categories
        
    def test_categorize_default_personal(self): pass
        """Test that uncategorized content defaults to personal"""
        content = "Something completely unrelated happened"
        categories = categorize_memory_content(content)
        
        assert MemoryCategory.PERSONAL in categories
        assert len(categories) == 1
        
    def test_categorize_case_insensitive(self): pass
        """Test that categorization is case insensitive"""
        content = "I FEEL TERRIFIED during the WAR"
        categories = categorize_memory_content(content)
        
        assert MemoryCategory.PERSONAL in categories
        assert MemoryCategory.TRAUMA in categories
        assert MemoryCategory.WAR in categories


class TestApplyCategoryModifiers: pass
    """Test class for apply_category_modifiers function"""
    
    def test_apply_single_category_modifier(self): pass
        """Test applying modifiers for single category"""
        base_importance = 1.0
        base_decay_rate = 0.1
        categories = [MemoryCategory.TRAUMA]
        
        result = apply_category_modifiers(base_importance, base_decay_rate, categories)
        
        # Trauma has importance_modifier=1.5 and decay_modifier=0.5
        assert result["importance"] == 1.5  # 1.0 * 1.5
        assert result["decay_rate"] == 0.05  # 0.1 * 0.5
        
    def test_apply_multiple_category_modifiers(self): pass
        """Test applying modifiers for multiple categories"""
        base_importance = 1.0
        base_decay_rate = 0.1
        categories = [MemoryCategory.TRAUMA, MemoryCategory.WAR]
        
        result = apply_category_modifiers(base_importance, base_decay_rate, categories)
        
        # Modifiers are multiplied together
        # Trauma: importance=1.5, decay=0.5
        # War: importance=1.3, decay=0.7
        # Combined: importance=1.5*1.3=1.95, decay=0.5*0.7=0.35
        assert abs(result["importance"] - 1.95) < 0.001  # 1.0 * 1.5 * 1.3
        assert abs(result["decay_rate"] - 0.035) < 0.001  # 0.1 * 0.5 * 0.7
        
    def test_apply_default_category_modifiers(self): pass
        """Test applying modifiers for categories with default values"""
        base_importance = 1.0
        base_decay_rate = 0.1
        categories = [MemoryCategory.CUSTOM]
        
        result = apply_category_modifiers(base_importance, base_decay_rate, categories)
        
        # Custom category should use default modifiers (1.0)
        assert result["importance"] == 1.0
        assert result["decay_rate"] == 0.1
        
    def test_apply_empty_categories(self): pass
        """Test applying modifiers with empty categories list"""
        base_importance = 1.0
        base_decay_rate = 0.1
        categories = []
        
        result = apply_category_modifiers(base_importance, base_decay_rate, categories)
        
        # Should return base values unchanged
        assert result["importance"] == 1.0
        assert result["decay_rate"] == 0.1


class TestCategoryUtilityFunctions: pass
    """Test class for category utility functions"""
    
    def setup_method(self): pass
        """Set up test fixtures"""
        # Clear any existing custom categories
        clear_custom_categories()
        
    def teardown_method(self): pass
        """Clean up after tests"""
        # Clear any custom categories added during tests
        clear_custom_categories()
        
    def test_get_category_metadata_existing(self): pass
        """Test getting metadata for existing category"""
        metadata = get_category_metadata("trauma")
        
        assert metadata is not None
        assert metadata["display_name"] == "Traumatic Memory"
        
    def test_get_category_metadata_nonexistent(self): pass
        """Test getting metadata for non-existent category"""
        metadata = get_category_metadata("nonexistent")
        
        assert metadata is None
        
    def test_get_category_modifier_existing(self): pass
        """Test getting modifier for existing category"""
        modifier = get_category_modifier("trauma", "decay_modifier")
        
        assert modifier == 0.5
        
    def test_get_category_modifier_nonexistent_category(self): pass
        """Test getting modifier for non-existent category"""
        modifier = get_category_modifier("nonexistent", "decay_modifier")
        
        assert modifier is None
        
    def test_get_category_modifier_nonexistent_modifier(self): pass
        """Test getting non-existent modifier for existing category"""
        modifier = get_category_modifier("trauma", "nonexistent_modifier")
        
        assert modifier is None
        
    def test_register_custom_category_success(self): pass
        """Test successful registration of custom category"""
        metadata = {
            "display_name": "Test Category",
            "description": "A test category",
            "decay_modifier": 0.8,
            "importance_modifier": 1.2,
        }
        
        result = register_custom_category("test_category", metadata)
        
        assert result is True
        
        # Verify the category was registered
        retrieved_metadata = get_category_metadata("test_category")
        assert retrieved_metadata == metadata
        
    def test_register_custom_category_existing(self): pass
        """Test registering custom category that already exists"""
        metadata = {
            "display_name": "Test Category",
            "description": "A test category",
            "decay_modifier": 0.8,
            "importance_modifier": 1.2,
        }
        
        # Register once
        result1 = register_custom_category("test_category", metadata)
        assert result1 is True
        
        # Register again - the function always returns True (overwrites existing)
        result2 = register_custom_category("test_category", metadata)
        assert result2 is True
        
    def test_is_valid_category_builtin(self): pass
        """Test validation of built-in category"""
        assert is_valid_category("trauma") is True
        assert is_valid_category("personal") is True
        
    def test_is_valid_category_custom(self): pass
        """Test validation of custom category"""
        metadata = {
            "display_name": "Test Category",
            "description": "A test category",
        }
        register_custom_category("test_category", metadata)
        
        assert is_valid_category("test_category") is True
        
    def test_is_valid_category_invalid(self): pass
        """Test validation of invalid category"""
        assert is_valid_category("nonexistent") is False
        
    def test_get_all_categories_builtin_only(self): pass
        """Test getting all categories with only built-in categories"""
        categories = get_all_categories()
        
        # Should include all built-in categories
        builtin_categories = [category.value for category in MemoryCategory]
        for category in builtin_categories: pass
            assert category in categories
            
    def test_get_all_categories_with_custom(self): pass
        """Test getting all categories including custom ones"""
        metadata = {
            "display_name": "Test Category",
            "description": "A test category",
        }
        register_custom_category("test_category", metadata)
        
        categories = get_all_categories()
        
        # Should include built-in and custom categories
        assert "test_category" in categories
        assert "trauma" in categories
        
    def test_clear_custom_categories(self): pass
        """Test clearing custom categories"""
        metadata = {
            "display_name": "Test Category",
            "description": "A test category",
        }
        register_custom_category("test_category", metadata)
        
        # Verify it was registered
        assert is_valid_category("test_category") is True
        
        # Clear custom categories
        clear_custom_categories()
        
        # Verify it was removed
        assert is_valid_category("test_category") is False
        
        # Verify built-in categories still exist
        assert is_valid_category("trauma") is True
