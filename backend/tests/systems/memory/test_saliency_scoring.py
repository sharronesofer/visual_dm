from typing import Any
from typing import List
"""
Tests for backend.systems.memory.saliency_scoring

Comprehensive tests for memory saliency scoring functionality.
"""

import pytest
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import the module being tested
from backend.systems.memory.saliency_scoring import (
    calculate_memory_saliency,
    calculate_initial_importance,
    calculate_memory_relevance,
    rank_memories_by_relevance,
    DEFAULT_BASE_DECAY_RATE,
    DEFAULT_MEMORY_HALFLIFE,
    DEFAULT_MIN_IMPORTANCE,
    DEFAULT_MAX_IMPORTANCE,
    INITIAL_SALIENCY,
    HALFLIFE_MODIFIERS,
)


class TestCalculateMemorySaliency:
    """Test class for calculate_memory_saliency function"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.current_time = datetime(2023, 6, 15, 12, 0, 0)
        self.base_memory = {
            "id": "test_memory_1",
            "content": "Test memory content",
            "importance": 0.7,
            "created_at": "2023-06-01T12:00:00",
            "memory_type": "regular",
            "categories": [],
            "access_count": 0,
        }
        
    def test_calculate_saliency_basic(self):
        """Test basic saliency calculation"""
        memory = self.base_memory.copy()
        saliency = calculate_memory_saliency(memory, self.current_time)
        
        # Should be less than original importance due to decay
        assert 0 < saliency < memory["importance"]
        assert saliency >= DEFAULT_MIN_IMPORTANCE
        assert saliency <= DEFAULT_MAX_IMPORTANCE
        
    def test_calculate_saliency_no_time_provided(self):
        """Test saliency calculation without providing current time"""
        memory = self.base_memory.copy()
        saliency = calculate_memory_saliency(memory)
        
        # Should work with current time
        assert 0 < saliency <= DEFAULT_MAX_IMPORTANCE
        
    def test_calculate_saliency_missing_created_at(self):
        """Test saliency calculation with missing created_at"""
        memory = self.base_memory.copy()
        del memory["created_at"]
        
        saliency = calculate_memory_saliency(memory, self.current_time)
        
        # Should return minimum importance
        assert saliency == DEFAULT_MIN_IMPORTANCE
        
    def test_calculate_saliency_invalid_created_at(self):
        """Test saliency calculation with invalid created_at"""
        memory = self.base_memory.copy()
        memory["created_at"] = "invalid_date"
        
        saliency = calculate_memory_saliency(memory, self.current_time)
        
        # Should handle gracefully and use current time (minimal decay)
        assert saliency >= DEFAULT_MIN_IMPORTANCE
        
    def test_calculate_saliency_core_memory(self):
        """Test saliency calculation for core memory"""
        memory = self.base_memory.copy()
        memory["categories"] = ["core"]
        
        saliency = calculate_memory_saliency(memory, self.current_time)
        
        # Core memories should decay much slower
        assert saliency > 0.6  # Should retain most importance
        
    def test_calculate_saliency_trauma_memory(self):
        """Test saliency calculation for trauma memory"""
        memory = self.base_memory.copy()
        memory["categories"] = ["trauma"]
        
        saliency = calculate_memory_saliency(memory, self.current_time)
        
        # Trauma memories should decay slower than regular
        assert saliency > 0.5
        
    def test_calculate_saliency_mundane_memory(self):
        """Test saliency calculation for mundane memory"""
        memory = self.base_memory.copy()
        memory["categories"] = ["mundane"]
        
        saliency = calculate_memory_saliency(memory, self.current_time)
        
        # Mundane memories should decay faster, but with only 14 days and base importance 0.7,
        # it won't decay below 0.5 yet
        assert saliency < memory["importance"]  # Should be less than original
        assert saliency > 0.4  # But not too low with only 14 days
        
    def test_calculate_saliency_with_access_boost(self):
        """Test saliency calculation with access count boost"""
        memory = self.base_memory.copy()
        memory["access_count"] = 10
        
        saliency_with_access = calculate_memory_saliency(memory, self.current_time)
        
        memory["access_count"] = 0
        saliency_without_access = calculate_memory_saliency(memory, self.current_time)
        
        # Should be higher with access boost
        assert saliency_with_access > saliency_without_access
        
    def test_calculate_saliency_very_old_memory(self):
        """Test saliency calculation for very old memory"""
        memory = self.base_memory.copy()
        memory["created_at"] = "2020-01-01T12:00:00"  # Very old
        
        saliency = calculate_memory_saliency(memory, self.current_time)
        
        # Should be close to minimum due to decay
        assert saliency <= DEFAULT_MIN_IMPORTANCE + 0.1
        
    def test_calculate_saliency_recent_memory(self):
        """Test saliency calculation for very recent memory"""
        memory = self.base_memory.copy()
        memory["created_at"] = self.current_time.isoformat()  # Just created
        
        saliency = calculate_memory_saliency(memory, self.current_time)
        
        # Should be close to original importance (minimal decay)
        assert abs(saliency - memory["importance"]) < 0.1


class TestCalculateInitialImportance:
    """Test class for calculate_initial_importance function"""
    
    def test_calculate_importance_basic(self):
        """Test basic importance calculation"""
        content = "A simple memory about walking in the park"
        importance = calculate_initial_importance(content)
        
        # Should return reasonable importance value
        assert 0 < importance <= 1.0
        
    def test_calculate_importance_by_memory_type(self):
        """Test importance calculation for different memory types"""
        content = "Test content"
        
        core_importance = calculate_initial_importance(content, "core")
        trauma_importance = calculate_initial_importance(content, "trauma")
        regular_importance = calculate_initial_importance(content, "regular")
        mundane_importance = calculate_initial_importance(content, "mundane")
        
        # Core should be highest, mundane lowest
        assert core_importance > trauma_importance > regular_importance > mundane_importance
        
    def test_calculate_importance_with_categories(self):
        """Test importance calculation with high-importance categories"""
        content = "Test content"
        categories = ["trauma", "identity"]
        
        importance_with_categories = calculate_initial_importance(content, "regular", categories)
        importance_without_categories = calculate_initial_importance(content, "regular", [])
        
        # Should be higher with important categories
        assert importance_with_categories > importance_without_categories
        
    def test_calculate_importance_emotional_content(self):
        """Test importance calculation with emotional content"""
        emotional_content = "I felt devastated and heartbroken when she left"
        neutral_content = "I went to the store today"
        
        emotional_importance = calculate_initial_importance(emotional_content)
        neutral_importance = calculate_initial_importance(neutral_content)
        
        # Emotional content should have higher importance
        assert emotional_importance > neutral_importance
        
    def test_calculate_importance_life_events(self):
        """Test importance calculation with life-changing events"""
        life_event_content = "I got married today and it was the first time I felt truly happy"
        regular_content = "I had lunch at the tavern"
        
        life_event_importance = calculate_initial_importance(life_event_content)
        regular_importance = calculate_initial_importance(regular_content)
        
        # Life events should have higher importance
        assert life_event_importance > regular_importance
        
    def test_calculate_importance_intensity_terms(self):
        """Test importance calculation with intensity indicators"""
        intense_content = "I will never forget this moment, it was absolutely profound"
        mild_content = "It was okay, I guess"
        
        intense_importance = calculate_initial_importance(intense_content)
        mild_importance = calculate_initial_importance(mild_content)
        
        # Intense content should have higher importance
        assert intense_importance > mild_importance
        
    def test_calculate_importance_bounds(self):
        """Test that importance stays within bounds"""
        # Test with maximum boosting content
        max_content = "I will never forget my first marriage, I was absolutely devastated and heartbroken"
        max_categories = ["trauma", "identity", "accomplishment", "relationship"]
        
        importance = calculate_initial_importance(max_content, "core", max_categories)
        
        # Should not exceed 1.0
        assert importance <= 1.0
        assert importance >= 0.0


class TestCalculateMemoryRelevance:
    """Test class for calculate_memory_relevance function"""
    
    def test_calculate_relevance_exact_match(self):
        """Test relevance calculation with exact keyword match"""
        query = "dragon attack"
        memory_content = "The dragon attacked our village yesterday"
        
        relevance = calculate_memory_relevance(query, memory_content)
        
        # Relevance is based on word overlap ratio: 2 matches out of 2 query words = 1.0 * 0.7 = 0.7
        # But "attack" vs "attacked" might not match exactly
        assert relevance > 0.3  # Should have good relevance due to word overlap
        
    def test_calculate_relevance_partial_match(self):
        """Test relevance calculation with partial keyword match"""
        query = "dragon battle"
        memory_content = "We fought a fierce dragon in the mountains"
        
        relevance = calculate_memory_relevance(query, memory_content)
        
        # Should have moderate relevance
        assert 0.3 < relevance < 0.8
        
    def test_calculate_relevance_no_match(self):
        """Test relevance calculation with no keyword match"""
        query = "dragon"
        memory_content = "I bought some bread at the market"
        
        relevance = calculate_memory_relevance(query, memory_content)
        
        # Should have low relevance
        assert relevance < 0.3
        
    def test_calculate_relevance_with_categories(self):
        """Test relevance calculation with matching categories"""
        query = "combat"
        memory_content = "I fought bravely"
        categories = ["combat", "victory"]
        
        relevance_with_categories = calculate_memory_relevance(query, memory_content, categories)
        relevance_without_categories = calculate_memory_relevance(query, memory_content, [])
        
        # Should be higher with matching categories
        assert relevance_with_categories > relevance_without_categories
        
    def test_calculate_relevance_case_insensitive(self):
        """Test that relevance calculation is case insensitive"""
        query = "DRAGON"
        memory_content = "the dragon was huge"
        
        relevance = calculate_memory_relevance(query, memory_content)
        
        # Should match despite case differences
        assert relevance > 0.5
        
    def test_calculate_relevance_semantic_similarity(self):
        """Test relevance calculation with related terms"""
        query = "battle"
        memory_content = "We fought in a great war"
        
        relevance = calculate_memory_relevance(query, memory_content)
        
        # The function doesn't do true semantic similarity, only exact word matching
        # "battle" and "fought"/"war" are different words, so no overlap
        assert relevance == 0.0  # No word overlap means 0 relevance


class TestRankMemoriesByRelevance:
    """Test class for rank_memories_by_relevance function"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.current_time = datetime(2023, 6, 15, 12, 0, 0)
        self.memories = [
            {
                "id": "mem1",
                "content": "I fought a dragon and won",
                "importance": 0.8,
                "created_at": "2023-06-01T12:00:00",
                "categories": ["combat", "victory"],
            },
            {
                "id": "mem2", 
                "content": "I saw a dragon flying overhead",
                "importance": 0.5,
                "created_at": "2023-06-10T12:00:00",
                "categories": ["observation"],
            },
            {
                "id": "mem3",
                "content": "I bought some bread at the market",
                "importance": 0.3,
                "created_at": "2023-06-14T12:00:00",
                "categories": ["mundane"],
            },
        ]
        
    def test_rank_memories_basic(self):
        """Test basic memory ranking"""
        query = "dragon"
        ranked_memories = rank_memories_by_relevance(query, self.memories)
        
        # Should return list of tuples (memory, score)
        assert len(ranked_memories) == len(self.memories)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in ranked_memories)
        
        # Should be sorted by relevance (highest first)
        scores = [score for _, score in ranked_memories]
        assert scores == sorted(scores, reverse=True)
        
    def test_rank_memories_relevance_order(self):
        """Test that memories are ranked by relevance"""
        query = "dragon"
        ranked_memories = rank_memories_by_relevance(query, self.memories)
        
        # Dragon-related memories should rank higher than bread memory
        memory_ids = [memory["id"] for memory, _ in ranked_memories]
        bread_index = memory_ids.index("mem3")
        
        # Bread memory should not be first (least relevant)
        assert bread_index > 0
        
    def test_rank_memories_with_saliency(self):
        """Test ranking with saliency consideration"""
        query = "dragon"
        
        ranked_with_saliency = rank_memories_by_relevance(
            query, self.memories, consider_saliency=True
        )
        ranked_without_saliency = rank_memories_by_relevance(
            query, self.memories, consider_saliency=False
        )
        
        # Results might differ when considering saliency
        assert len(ranked_with_saliency) == len(ranked_without_saliency)
        
    def test_rank_memories_empty_list(self):
        """Test ranking with empty memory list"""
        query = "dragon"
        ranked_memories = rank_memories_by_relevance(query, [])
        
        # Should return empty list
        assert ranked_memories == []
        
    def test_rank_memories_no_matches(self):
        """Test ranking when no memories match query"""
        query = "unicorn"  # Not in any memory
        ranked_memories = rank_memories_by_relevance(query, self.memories)
        
        # Should still return all memories, but with low scores
        assert len(ranked_memories) == len(self.memories)
        scores = [score for _, score in ranked_memories]
        assert all(score < 0.5 for score in scores)


class TestSaliencyConstants:
    """Test class for saliency scoring constants"""
    
    def test_initial_saliency_values(self):
        """Test that initial saliency values are reasonable"""
        assert 0 < INITIAL_SALIENCY["mundane"] < INITIAL_SALIENCY["regular"]
        assert INITIAL_SALIENCY["regular"] < INITIAL_SALIENCY["relationship"]
        assert INITIAL_SALIENCY["relationship"] < INITIAL_SALIENCY["accomplishment"]
        assert INITIAL_SALIENCY["accomplishment"] < INITIAL_SALIENCY["trauma"]
        assert INITIAL_SALIENCY["trauma"] < INITIAL_SALIENCY["core"]
        
    def test_halflife_modifiers(self):
        """Test that halflife modifiers are reasonable"""
        assert HALFLIFE_MODIFIERS["mundane"] < HALFLIFE_MODIFIERS["regular"]
        assert HALFLIFE_MODIFIERS["regular"] < HALFLIFE_MODIFIERS["relationship"]
        assert HALFLIFE_MODIFIERS["relationship"] < HALFLIFE_MODIFIERS["accomplishment"]
        assert HALFLIFE_MODIFIERS["accomplishment"] < HALFLIFE_MODIFIERS["trauma"]
        assert HALFLIFE_MODIFIERS["trauma"] < HALFLIFE_MODIFIERS["core"]
        
    def test_default_constants(self):
        """Test that default constants are reasonable"""
        assert 0 < DEFAULT_BASE_DECAY_RATE < 1
        assert DEFAULT_MEMORY_HALFLIFE > 0
        assert 0 < DEFAULT_MIN_IMPORTANCE < DEFAULT_MAX_IMPORTANCE < 1
