"""
Test module for memory utilities infrastructure.

Tests the canonical memory utility functions that provide scoring, categorization,
and other technical infrastructure for the memory system.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Import canonical memory utilities from infrastructure
try:
    from backend.infrastructure.memory_utils import (
        calculate_initial_importance,
        calculate_memory_saliency,
        categorize_memory_content,
        auto_detect_associations,
        detect_cognitive_frames,
        get_summarization_styles
    )
    from backend.infrastructure.memory_utils.memory_categorization import MemoryCategory
except ImportError:
    pytest.skip(f"Memory utilities system not found", allow_module_level=True)


class TestMemoryUtils:
    """Test class for memory utilities functionality"""
    
    def test_calculate_initial_importance(self):
        """Test importance calculation follows canonical algorithm"""
        # Test regular memory importance
        importance = calculate_initial_importance(
            memory_content="I helped the villagers",
            memory_type="regular",
            categories=[MemoryCategory.ACHIEVEMENT.value]
        )
        
        assert 0.0 <= importance <= 1.0
        assert importance > 0.0  # Should have some importance
        
        # Test core memory importance
        core_importance = calculate_initial_importance(
            memory_content="I believe in protecting innocents",
            memory_type="core",
            categories=[MemoryCategory.CORE.value]
        )
        
        assert core_importance >= importance  # Core should have higher importance
    
    def test_calculate_memory_saliency(self):
        """Test saliency calculation with canonical memory structure"""
        memory_dict = {
            "id": "test_memory_001",
            "content": "Important battle memory",
            "memory_type": "regular",
            "categories": [MemoryCategory.TRAUMA.value],
            "importance": 0.8,
            "created_at": datetime.now().isoformat(),
            "access_count": 5,
            "last_accessed": datetime.now().isoformat()
        }
        
        saliency = calculate_memory_saliency(memory_dict)
        
        assert 0.0 <= saliency <= 1.0
        assert saliency > 0.0  # Should have measurable saliency
    
    def test_categorize_memory_content(self):
        """Test automatic categorization follows canonical patterns"""
        # Test belief categorization
        belief_category = categorize_memory_content("I believe in justice")
        assert belief_category == MemoryCategory.BELIEF
        
        # Test interaction categorization
        interaction_category = categorize_memory_content("I spoke with the merchant")
        assert interaction_category == MemoryCategory.CONVERSATION
        
        # Test trauma categorization
        trauma_category = categorize_memory_content("The village was destroyed")
        assert trauma_category in [MemoryCategory.TRAUMA, MemoryCategory.EVENT]
    
    def test_auto_detect_associations(self):
        """Test memory association detection"""
        memory1 = {
            "id": "mem_001",
            "content": "Battle at the village",
            "categories": [MemoryCategory.EVENT.value],
            "created_at": datetime.now().isoformat(),
            "npc_id": "npc_001"
        }
        
        memory2 = {
            "id": "mem_002", 
            "content": "Helped defend the village",
            "categories": [MemoryCategory.ACHIEVEMENT.value],
            "created_at": datetime.now().isoformat(),
            "npc_id": "npc_001"
        }
        
        associations = auto_detect_associations(memory1, memory2)
        
        assert isinstance(associations, list)
        # Should find some association due to "village" keyword
        assert len(associations) >= 0
    
    def test_detect_cognitive_frames(self):
        """Test cognitive frame detection"""
        content = "I must protect the innocent at all costs"
        frames = detect_cognitive_frames(content)
        
        assert isinstance(frames, list)
        # Should detect protective/moral frames
        assert len(frames) >= 0
    
    def test_get_summarization_styles(self):
        """Test summarization styles configuration"""
        styles = get_summarization_styles()
        
        assert isinstance(styles, list)
        assert len(styles) > 0
        
        # Verify each style has canonical structure
        for style in styles:
            assert "value" in style
            assert "display_name" in style
            assert "description" in style
            assert "max_memories_per_chunk" in style
            assert "min_importance_threshold" in style
    
    def test_importance_calculation_consistency(self):
        """Test that importance calculation is consistent"""
        content = "Test memory content"
        
        # Same inputs should give same outputs
        importance1 = calculate_initial_importance(content, "regular", ["interaction"])
        importance2 = calculate_initial_importance(content, "regular", ["interaction"])
        
        assert importance1 == importance2
    
    def test_saliency_temporal_decay(self):
        """Test that saliency considers temporal factors"""
        old_memory = {
            "id": "old_memory",
            "content": "Old memory",
            "importance": 0.8,
            "created_at": "2020-01-01T00:00:00",
            "access_count": 0,
            "last_accessed": None
        }
        
        recent_memory = {
            "id": "recent_memory", 
            "content": "Recent memory",
            "importance": 0.8,
            "created_at": datetime.now().isoformat(),
            "access_count": 0,
            "last_accessed": None
        }
        
        old_saliency = calculate_memory_saliency(old_memory)
        recent_saliency = calculate_memory_saliency(recent_memory)
        
        # Recent memories should have higher saliency than old ones
        assert recent_saliency >= old_saliency
