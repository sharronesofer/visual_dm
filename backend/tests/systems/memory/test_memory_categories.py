"""
Test module for memory categories system.

Tests the canonical memory categorization system that's agreed upon between 
the Development Bible and code implementation.
"""

import pytest
from unittest.mock import Mock, patch

# Import canonical memory category system
try:
    from backend.systems.memory.memory_categories import (
        MemoryCategory, 
        MemoryCategoryInfo,
        MEMORY_CATEGORY_CONFIG,
        get_category_info,
        get_all_categories,
        get_permanent_categories,
        get_decay_categories,
        categorize_memory_content
    )
except ImportError:
    pytest.skip(f"Memory categories system not found", allow_module_level=True)


class TestMemoryCategories:
    """Test class for memory categories functionality"""
    
    def test_memory_category_enum(self):
        """Test that all canonical memory categories are defined"""
        # These 17 categories are agreed upon between Bible and code
        expected_categories = [
            "CORE", "BELIEF", "IDENTITY", "INTERACTION", "CONVERSATION",
            "RELATIONSHIP", "EVENT", "ACHIEVEMENT", "TRAUMA", "KNOWLEDGE",
            "SKILL", "SECRET", "LOCATION", "FACTION", "WORLD_STATE",
            "SUMMARY", "TOUCHSTONE"
        ]
        
        for category_name in expected_categories:
            assert hasattr(MemoryCategory, category_name)
            category = getattr(MemoryCategory, category_name)
            assert isinstance(category, MemoryCategory)
    
    def test_category_config_alignment(self):
        """Test that category configuration aligns with canonical structure"""
        for category in MemoryCategory:
            # Each category should have configuration info
            assert category in MEMORY_CATEGORY_CONFIG
            
            config = MEMORY_CATEGORY_CONFIG[category]
            assert isinstance(config, MemoryCategoryInfo)
            assert config.category == category
            assert isinstance(config.description, str)
            assert isinstance(config.is_permanent, bool)
            assert isinstance(config.default_weight, float)
            
    def test_get_category_info(self):
        """Test category info retrieval"""
        info = get_category_info(MemoryCategory.CORE)
        
        assert info.category == MemoryCategory.CORE
        assert info.is_permanent == True  # Core memories are permanent
        assert info.default_weight >= 1.0  # Core memories have high weight
        
    def test_permanent_vs_decay_categories(self):
        """Test canonical distinction between permanent and decay categories"""
        permanent = get_permanent_categories()
        decay = get_decay_categories()
        
        # Verify no overlap
        assert len(set(permanent).intersection(set(decay))) == 0
        
        # Verify canonical permanent categories
        expected_permanent = [
            MemoryCategory.CORE, MemoryCategory.BELIEF, MemoryCategory.IDENTITY,
            MemoryCategory.RELATIONSHIP, MemoryCategory.ACHIEVEMENT, 
            MemoryCategory.TRAUMA, MemoryCategory.SKILL, MemoryCategory.SECRET,
            MemoryCategory.FACTION, MemoryCategory.TOUCHSTONE
        ]
        
        for category in expected_permanent:
            assert category in permanent
    
    def test_automatic_categorization(self):
        """Test automatic content categorization"""
        # Test belief categorization
        belief_content = "I believe in protecting the innocent"
        category = categorize_memory_content(belief_content)
        assert category == MemoryCategory.BELIEF
        
        # Test conversation categorization  
        conversation_content = "The player told me about the quest"
        category = categorize_memory_content(conversation_content)
        assert category == MemoryCategory.CONVERSATION
        
        # Test achievement categorization
        achievement_content = "I successfully completed the rescue mission"
        category = categorize_memory_content(achievement_content)
        assert category == MemoryCategory.ACHIEVEMENT
    
    def test_category_priorities(self):
        """Test that permanent categories have priority values"""
        for category in get_permanent_categories():
            config = get_category_info(category)
            assert hasattr(config, 'priority')
            assert config.priority >= 1
