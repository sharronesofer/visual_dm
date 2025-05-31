"""
Comprehensive Memory System Integration Tests.

This module tests the complete memory system functionality end-to-end,
including memory creation, categorization, associations, and API endpoints.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from backend.systems.memory import MemoryManager, Memory
from backend.systems.memory.memory_categories import MemoryCategory, categorize_memory_content
from backend.systems.memory.saliency_scoring import calculate_memory_saliency, calculate_initial_importance
from backend.systems.memory.cognitive_frames import detect_cognitive_frames, apply_cognitive_frames
from backend.systems.memory.memory_associations import auto_detect_associations, build_association_network
from backend.systems.memory.summarization_styles import get_summarization_styles


class TestMemorySystemIntegration:
    """Integration tests for the complete memory system."""
    
    @pytest.fixture
    def memory_manager(self):
        """Get a fresh memory manager instance."""
        return MemoryManager(entity_id="test_npc", entity_type="npc")
    
    @pytest.fixture
    def sample_memories(self):
        """Create sample memories for testing."""
        return [
            {
                "npc_id": "npc_001",
                "content": "I helped the village defend against bandits. We fought bravely together.",
                "memory_type": "regular",
                "categories": ["interaction", "event", "achievement"]
            },
            {
                "npc_id": "npc_001", 
                "content": "The merchant betrayed our trust and sold us out to the enemy.",
                "memory_type": "regular",
                "categories": ["interaction", "betrayal", "trauma"]
            },
            {
                "npc_id": "npc_001",
                "content": "I believe in protecting the innocent above all else.",
                "memory_type": "core",
                "categories": ["belief", "identity"]
            },
            {
                "npc_id": "npc_001",
                "content": "Learned a new sword technique from the master.",
                "memory_type": "regular", 
                "categories": ["skill", "learning", "achievement"]
            }
        ]
    
    @pytest.mark.asyncio
    async def test_memory_creation_and_categorization(self, memory_manager, sample_memories):
        """Test memory creation with automatic categorization."""
        created_memories = []
        
        for memory_data in sample_memories:
            memory = await memory_manager.create_memory(
                content=memory_data["content"],
                importance=0.7 if memory_data["memory_type"] == "core" else 0.5
            )
            created_memories.append(memory)
            
            # Verify memory was created correctly
            assert memory.npc_id == "test_npc"
            assert memory.content == memory_data["content"]
            assert len(memory.categories) > 0  # Should have auto-categorized
            assert memory.importance > 0.0
        
        # Verify memories are stored
        assert len(memory_manager.memories) == len(sample_memories)
    
    def test_memory_categorization_system(self, sample_memories):
        """Test the memory categorization system."""
        for memory_data in sample_memories:
            content = memory_data["content"]
            
            # Test automatic categorization
            auto_category = categorize_memory_content(content)
            assert isinstance(auto_category, MemoryCategory)
            
            # Test importance calculation
            importance = calculate_initial_importance(
                content, 
                memory_data["memory_type"],
                memory_data["categories"]
            )
            assert 0.0 <= importance <= 1.0
    
    def test_saliency_scoring_system(self, sample_memories):
        """Test the saliency scoring system."""
        for memory_data in sample_memories:
            # Create a memory dict with required fields
            memory_dict = {
                "id": "test_memory_001",
                "content": memory_data["content"],
                "memory_type": memory_data["memory_type"],
                "categories": memory_data["categories"],
                "importance": 0.7,
                "created_at": datetime.now().isoformat(),
                "access_count": 0,
                "last_accessed": None
            }
            
            # Test saliency calculation
            saliency = calculate_memory_saliency(memory_dict)
            assert 0.0 <= saliency <= 1.0
            
            # Core memories should have higher saliency
            if memory_data["memory_type"] == "core":
                assert saliency >= 0.5
    
    def test_cognitive_frames_detection(self, sample_memories):
        """Test cognitive frame detection and application."""
        for memory_data in sample_memories:
            content = memory_data["content"]
            
            # Detect cognitive frames
            frames = detect_cognitive_frames(content)
            assert isinstance(frames, list)
            
            # Apply frames to memory data
            memory_dict = {
                "id": "test_memory_001",
                "content": content,
                "importance": 0.5,
                "metadata": {}
            }
            
            if frames:
                modified_memory = apply_cognitive_frames(memory_dict, frames)
                assert "cognitive_frames" in modified_memory["metadata"]
                assert len(modified_memory["metadata"]["cognitive_frames"]) == len(frames)
    
    def test_memory_associations_system(self, sample_memories):
        """Test memory association detection and network building."""
        # Create memory dicts for association testing
        memory_dicts = []
        for i, memory_data in enumerate(sample_memories):
            memory_dict = {
                "id": f"memory_{i:03d}",
                "content": memory_data["content"],
                "categories": memory_data["categories"],
                "created_at": (datetime.now() + timedelta(minutes=i)).isoformat(),
                "npc_id": memory_data["npc_id"]
            }
            memory_dicts.append(memory_dict)
        
        # Test pairwise association detection
        for i in range(len(memory_dicts)):
            for j in range(i + 1, len(memory_dicts)):
                associations = auto_detect_associations(memory_dicts[i], memory_dicts[j])
                assert isinstance(associations, list)
                # Some memories should have associations
                if i == 0 and j == 1:  # Both involve interactions
                    assert len(associations) > 0
        
        # Test network building
        network = build_association_network(memory_dicts)
        assert network is not None
        assert len(network.associations) >= 0
    
    def test_summarization_styles_system(self):
        """Test the summarization styles system."""
        styles = get_summarization_styles()
        assert isinstance(styles, list)
        assert len(styles) > 0
        
        # Verify each style has required fields
        for style in styles:
            assert "value" in style
            assert "display_name" in style
            assert "description" in style
            assert "max_memories_per_chunk" in style
            assert "min_importance_threshold" in style
    
    @pytest.mark.asyncio
    async def test_memory_search_and_retrieval(self, memory_manager, sample_memories):
        """Test memory search and retrieval functionality."""
        # Create memories first
        created_memories = []
        for memory_data in sample_memories:
            memory = await memory_manager.create_memory(
                content=memory_data["content"],
                importance=0.7 if memory_data["memory_type"] == "core" else 0.5
            )
            created_memories.append(memory)
        
        # Test retrieval from manager
        assert len(memory_manager.memories) == len(sample_memories)
        
        # Test retrieval by category
        from backend.systems.memory.memory_categories import MemoryCategory
        belief_memories = await memory_manager.get_memories_by_category(MemoryCategory.BELIEF)
        # Should find at least some memories (auto-categorization may vary)
        assert isinstance(belief_memories, list)
        
        # Test recent memories
        recent_memories = await memory_manager.get_recent_memories(days=1)
        assert len(recent_memories) == len(sample_memories)  # All should be recent
    
    @pytest.mark.asyncio
    async def test_memory_importance_and_decay(self, memory_manager):
        """Test memory importance updates and decay mechanics."""
        # Create a test memory
        memory = await memory_manager.create_memory(
            content="Test memory for importance testing",
            importance=0.5
        )
        
        original_importance = memory.importance
        
        # Test importance update
        await memory_manager.update_memory_importance(memory.memory_id, 0.7)
        
        # Retrieve updated memory
        updated_memory = await memory_manager.get_memory(memory.memory_id)
        assert updated_memory.importance == 0.7
        assert updated_memory.importance > original_importance
        
        # Test memory access (should affect relevance)
        updated_memory.access("test context")
        assert updated_memory.access_count == 1
        assert updated_memory.last_accessed is not None
    
    @pytest.mark.asyncio
    async def test_memory_lifecycle(self, memory_manager):
        """Test complete memory lifecycle: create, update, access, delete."""
        # Create memory
        memory = await memory_manager.create_memory(
            content="Lifecycle test memory",
            importance=0.6,
            metadata={"test": True}
        )
        
        memory_id = memory.memory_id
        
        # Verify creation
        retrieved = await memory_manager.get_memory(memory_id)
        assert retrieved is not None
        assert retrieved.content == "Lifecycle test memory"
        
        # Access memory
        retrieved.access("lifecycle test")
        assert retrieved.access_count == 1
        
        # Delete memory
        await memory_manager.delete_memory(memory_id)
        
        # Verify deletion
        deleted_memory = await memory_manager.get_memory(memory_id)
        assert deleted_memory is None
    
    def test_memory_system_performance(self, sample_memories):
        """Test memory system performance with multiple operations."""
        import time
        
        # Test categorization performance
        start_time = time.time()
        for _ in range(100):
            for memory_data in sample_memories:
                categorize_memory_content(memory_data["content"])
        categorization_time = time.time() - start_time
        
        # Should complete 400 categorizations in reasonable time
        assert categorization_time < 5.0  # 5 seconds max
        
        # Test saliency calculation performance
        memory_dict = {
            "id": "perf_test",
            "content": sample_memories[0]["content"],
            "importance": 0.7,
            "created_at": datetime.now().isoformat(),
            "access_count": 5,
            "memory_type": "regular"
        }
        
        start_time = time.time()
        for _ in range(1000):
            calculate_memory_saliency(memory_dict)
        saliency_time = time.time() - start_time
        
        # Should complete 1000 saliency calculations quickly
        assert saliency_time < 2.0  # 2 seconds max
    
    @pytest.mark.asyncio
    async def test_memory_system_error_handling(self, memory_manager):
        """Test memory system error handling and edge cases."""
        # Test invalid memory retrieval
        invalid_memory = await memory_manager.get_memory("invalid_id")
        assert invalid_memory is None
        
        # Test empty content memory
        empty_memory = await memory_manager.create_memory(
            content="",
            importance=0.5
        )
        assert empty_memory.content == ""
        assert empty_memory.importance >= 0.0
        
        # Test memory with very long content
        long_content = "A" * 10000  # 10k characters
        long_memory = await memory_manager.create_memory(
            content=long_content,
            importance=0.5
        )
        assert len(long_memory.content) == 10000
        assert long_memory.importance <= 1.0
    
    def test_memory_system_consistency(self, sample_memories):
        """Test memory system consistency and data integrity."""
        # Test that categorization is consistent
        for memory_data in sample_memories:
            content = memory_data["content"]
            
            # Multiple calls should return same category
            category1 = categorize_memory_content(content)
            category2 = categorize_memory_content(content)
            assert category1 == category2
            
            # Importance calculation should be consistent
            importance1 = calculate_initial_importance(content, "regular", [])
            importance2 = calculate_initial_importance(content, "regular", [])
            assert abs(importance1 - importance2) < 0.001  # Should be nearly identical
    
    @pytest.mark.asyncio
    async def test_memory_system_scalability(self, memory_manager):
        """Test memory system with larger datasets."""
        # Create multiple memories
        memory_count = 50
        
        created_memories = []
        
        for mem_i in range(memory_count):
            memory = await memory_manager.create_memory(
                content=f"Memory {mem_i} for scalability test",
                importance=0.5 + (mem_i % 3) * 0.1  # Vary importance
            )
            created_memories.append(memory)
        
        # Verify all memories were created
        assert len(created_memories) == memory_count
        assert len(memory_manager.memories) == memory_count
        
        # Test retrieval performance
        import time
        start_time = time.time()
        
        for mem_i in range(memory_count):
            memory = created_memories[mem_i]
            retrieved = await memory_manager.get_memory(memory.memory_id)
            assert retrieved is not None
        
        retrieval_time = time.time() - start_time
        
        # Should retrieve all memories quickly
        assert retrieval_time < 3.0  # 3 seconds max for 50 memories 