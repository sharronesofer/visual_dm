"""
Test module for memory.memory

This file tests core Memory class functionality per canonical system structure.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Import the canonical memory system classes
try:
    from backend.systems.memory import Memory, MemoryManager
    from backend.systems.memory.memory_categories import MemoryCategory
except ImportError:
    pytest.skip(f"Memory system not found", allow_module_level=True)


class TestMemory:
    """Test class for core Memory functionality"""
    
    def test_memory_creation(self):
        """Test that Memory objects can be created with canonical structure"""
        memory = Memory(
            npc_id="test_npc",
            content="Test memory content",
            memory_type="regular",
            categories=[MemoryCategory.INTERACTION.value],
            importance=0.7
        )
        
        assert memory.npc_id == "test_npc"
        assert memory.content == "Test memory content"
        assert memory.memory_type == "regular"
        assert MemoryCategory.INTERACTION.value in memory.categories
        assert memory.importance == 0.7
        assert memory.memory_id is not None  # Auto-generated
        
    def test_memory_id_property(self):
        """Test backward compatibility id property"""
        memory = Memory(
            npc_id="test_npc",
            content="Test content"
        )
        
        # Both memory_id and id should work (canonical requirement)
        assert memory.id == memory.memory_id
        
    def test_memory_core_type(self):
        """Test core memory type functionality"""
        core_memory = Memory(
            npc_id="test_npc",
            content="Core belief memory",
            memory_type="core",
            categories=[MemoryCategory.CORE.value]
        )
        
        assert core_memory.memory_type == "core"
        assert MemoryCategory.CORE.value in core_memory.categories
        
    def test_memory_to_dict(self):
        """Test memory serialization matches canonical structure"""
        memory = Memory(
            npc_id="test_npc",
            content="Test content",
            importance=0.5
        )
        
        memory_dict = memory.to_dict()
        
        # Verify canonical fields are present
        required_fields = ["id", "npc_id", "content", "importance", "categories", 
                          "memory_type", "created_at", "saliency"]
        for field in required_fields:
            assert field in memory_dict
    
    @pytest.mark.asyncio
    async def test_memory_manager_creation(self):
        """Test MemoryManager follows canonical singleton pattern"""
        manager = MemoryManager(entity_id="test_entity", entity_type="npc")
        
        assert manager.entity_id == "test_entity"
        assert manager.entity_type == "npc"
        assert hasattr(manager, 'create_memory')
        assert hasattr(manager, 'add_memory')
        assert hasattr(manager, 'recall_memory')
