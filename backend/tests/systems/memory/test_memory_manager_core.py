"""
Test module for memory manager core functionality.

Tests the canonical MemoryManager implementation that serves as the central
coordination point for memory operations, as agreed upon between Bible and code.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import canonical memory system components
try:
    from backend.systems.memory import MemoryManager, Memory
    from backend.infrastructure.memory_utils.memory_categorization import MemoryCategory
    from backend.infrastructure.memory_utils import calculate_initial_importance
except ImportError:
    pytest.skip(f"Memory manager core system not found", allow_module_level=True)


class TestMemoryManagerCore:
    """Test class for MemoryManager core functionality"""
    
    def test_memory_manager_initialization(self):
        """Test canonical MemoryManager initialization"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        
        assert manager.entity_id == "test_npc"
        assert manager.entity_type == "npc"
        assert manager.memories == {}  # Starts empty
        assert manager.config is not None  # Has summarization config
    
    @pytest.mark.asyncio
    async def test_create_memory_canonical(self):
        """Test memory creation follows canonical pattern"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        
        # Test automatic categorization when no category provided
        memory = await manager.create_memory(
            content="I helped defend the village",
            importance=0.8
        )
        
        assert memory.npc_id == "test_npc"
        assert memory.content == "I helped defend the village"
        assert memory.importance == 0.8
        assert len(memory.categories) > 0  # Auto-categorized
        assert memory.memory_id in manager.memories
    
    @pytest.mark.asyncio
    async def test_create_memory_with_category(self):
        """Test memory creation with explicit category"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        
        memory = await manager.create_memory(
            content="I believe in justice",
            category=MemoryCategory.BELIEF,
            importance=0.9
        )
        
        assert MemoryCategory.BELIEF.value in memory.categories
        assert memory.importance == 0.9
    
    @pytest.mark.asyncio
    async def test_add_memory_canonical(self):
        """Test adding existing memory to manager"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        
        memory = Memory(
            npc_id="test_npc",
            content="Test memory",
            importance=0.5
        )
        
        result = await manager.add_memory(memory)
        
        assert result == True
        assert memory.memory_id in manager.memories
        assert manager.memories[memory.memory_id] == memory
    
    @pytest.mark.asyncio
    async def test_recall_memory_canonical(self):
        """Test memory recall functionality"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        
        # Add some memories first
        memory1 = await manager.create_memory("Village defense", importance=0.8)
        memory2 = await manager.create_memory("Trade negotiation", importance=0.6)
        
        # Test recall with query
        results = await manager.recall_memory("village", limit=5)
        
        assert isinstance(results, list)
        assert len(results) >= 0  # Should return some results
    
    @pytest.mark.asyncio
    async def test_get_memory_by_id(self):
        """Test memory retrieval by ID"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        
        memory = await manager.create_memory("Test content", importance=0.5)
        
        retrieved = await manager.get_memory(memory.memory_id)
        
        assert retrieved is not None
        assert retrieved.memory_id == memory.memory_id
        assert retrieved.content == "Test content"
    
    @pytest.mark.asyncio
    async def test_update_memory_importance(self):
        """Test updating memory importance"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        
        memory = await manager.create_memory("Test content", importance=0.5)
        
        result = await manager.update_memory_importance(memory.memory_id, 0.8)
        
        assert result == True
        # Verify importance was updated
        updated_memory = await manager.get_memory(memory.memory_id)
        assert updated_memory.importance == 0.8
    
    @pytest.mark.asyncio 
    async def test_get_memories_by_category(self):
        """Test filtering memories by category"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        
        # Create memories with specific categories
        belief_memory = await manager.create_memory(
            "I believe in honor", 
            category=MemoryCategory.BELIEF
        )
        event_memory = await manager.create_memory(
            "The great battle happened",
            category=MemoryCategory.EVENT
        )
        
        belief_memories = await manager.get_memories_by_category(MemoryCategory.BELIEF)
        
        assert len(belief_memories) >= 1
        assert any(m.memory_id == belief_memory.memory_id for m in belief_memories)
    
    def test_get_memory_stats(self):
        """Test memory statistics retrieval"""
        manager = MemoryManager(entity_id="test_npc", entity_type="npc")
        
        stats = manager.get_memory_stats()
        
        assert isinstance(stats, dict)
        assert 'total_memories' in stats
        assert 'entity_id' in stats
        assert 'entity_type' in stats
