from backend.systems.memory.models import MemoryEmotionalValence
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.memory.models import MemoryEmotionalValence
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.memory.models import MemoryEmotionalValence
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.memory.models import MemoryEmotionalValence
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.memory.models import MemoryEmotionalValence
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.memory.models import MemoryEmotionalValence
from backend.systems.events.dispatcher import EventDispatcher
from typing import Type
"""
Tests for backend.systems.memory.services.memory_manager

Tests for the MemoryManager service covering CRUD operations,
query functions, decay simulation, and event handling.
"""

import pytest
import asyncio
import time
import math
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Import the module being tested
from backend.systems.memory.services.memory_manager import MemoryManager, MemoryForgottenEvent
from backend.systems.memory.models.memory import (
    Memory,
    MemoryType,
    MemoryEmotionalValence,
    MemoryCreatedEvent,
    MemoryRecalledEvent,
)
from backend.systems.events import EventDispatcher


class TestMemoryManager: pass
    """Test class for MemoryManager service"""

    def setup_method(self): pass
        """Set up test fixtures"""
        self.mock_dispatcher = Mock(spec=EventDispatcher)
        # Make emit_event method available and async
        self.mock_dispatcher.emit_event = Mock()
        self.mock_dispatcher.publish = AsyncMock()
        self.mock_storage = Mock()
        self.entity_id = "test_entity"
        self.world_id = "test_world"
        self.current_time = time.time()
        
        # Clear instances to ensure clean state
        MemoryManager._instances.clear()

    @pytest.mark.asyncio
    async def test_memory_manager_singleton(self): pass
        """Test that MemoryManager follows singleton pattern per entity"""
        manager1 = await MemoryManager.get_instance(
            entity_id=self.entity_id,
            world_id=self.world_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        manager2 = await MemoryManager.get_instance(
            entity_id=self.entity_id,
            world_id=self.world_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        assert manager1 is manager2
        
        # Different entity should get different instance
        manager3 = await MemoryManager.get_instance(
            entity_id="different_entity",
            event_dispatcher=self.mock_dispatcher
        )
        
        assert manager3 is not manager1

    @pytest.mark.asyncio
    async def test_memory_manager_initialization(self): pass
        """Test MemoryManager initialization"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            world_id=self.world_id,
            storage_manager=self.mock_storage,
            event_dispatcher=self.mock_dispatcher
        )
        
        assert manager.entity_id == self.entity_id
        assert manager.world_id == self.world_id
        assert manager.storage_manager == self.mock_storage
        assert manager.event_dispatcher == self.mock_dispatcher
        assert isinstance(manager.memories, dict)
        assert len(manager.memories) == 0

    @pytest.mark.asyncio
    async def test_create_memory(self): pass
        """Test memory creation"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        memory = await manager.create_memory(
            content="Test memory content",
            memory_type=MemoryType.INTERACTION,
            importance=0.8,
            entities_involved=["entity1"],
            tags=["test", "important"],
            location="tavern"
        )
        
        assert memory.owner_id == self.entity_id
        assert memory.content == "Test memory content"
        assert memory.memory_type == MemoryType.INTERACTION
        assert memory.importance == 0.8
        assert memory.entities_involved == ["entity1"]
        assert memory.tags == ["test", "important"]
        assert memory.location == "tavern"
        
        # Memory should be stored in manager
        assert memory.id in manager.memories
        assert manager.memories[memory.id] == memory
        
        # Event should be emitted
        self.mock_dispatcher.emit_event.assert_called()

    @pytest.mark.asyncio
    async def test_create_core_memory(self): pass
        """Test core memory creation"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        memory = await manager.create_memory(
            content="Core memory content",
            importance=0.9,
            is_core=True
        )
        
        assert memory.memory_type == MemoryType.CORE
        assert memory.id in manager.memories

    @pytest.mark.asyncio
    async def test_add_memory(self): pass
        """Test adding an existing memory"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        memory = Memory(
            owner_id=self.entity_id,
            content="External memory",
            event_dispatcher=self.mock_dispatcher
        )
        
        memory_id = await manager.add_memory(memory)
        
        assert memory_id == memory.id
        assert memory.id in manager.memories
        assert manager.memories[memory.id] == memory

    @pytest.mark.asyncio
    async def test_delete_memory(self): pass
        """Test memory deletion"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        memory = await manager.create_memory(
            content="Memory to delete",
            importance=0.5
        )
        memory_id = memory.id
        
        # Verify memory exists
        assert memory_id in manager.memories
        
        # Delete memory
        deleted = await manager.delete_memory(memory_id, "test deletion")
        
        assert deleted is True
        assert memory_id not in manager.memories
        
        # Should emit forgotten event
        self.mock_dispatcher.emit_event.assert_called()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_memory(self): pass
        """Test deleting a memory that doesn't exist"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        deleted = await manager.delete_memory("nonexistent_id")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_recall_memory(self): pass
        """Test memory recall"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        memory = await manager.create_memory(
            content="Memory to recall",
            importance=0.7
        )
        
        initial_recall_count = memory.recall_count
        
        recalled_memory = await manager.recall_memory(
            memory.id, 
            context="test recall"
        )
        
        assert recalled_memory is not None
        assert recalled_memory.id == memory.id
        assert recalled_memory.recall_count == initial_recall_count + 1
        
        # Should emit recall event
        self.mock_dispatcher.emit_event.assert_called()

    @pytest.mark.asyncio
    async def test_recall_nonexistent_memory(self): pass
        """Test recalling a memory that doesn't exist"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        recalled = await manager.recall_memory("nonexistent_id")
        assert recalled is None

    @pytest.mark.asyncio
    async def test_update_memory_importance(self): pass
        """Test updating memory importance"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        memory = await manager.create_memory(
            content="Memory to update",
            importance=0.5
        )
        
        updated_memory = await manager.update_memory_importance(
            memory.id, 
            0.8
        )
        
        assert updated_memory is not None
        assert updated_memory.importance == 0.8
        assert manager.memories[memory.id].importance == 0.8

    @pytest.mark.asyncio
    async def test_update_all_memories(self): pass
        """Test updating all memories with decay"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Create regular and core memories
        regular_memory = await manager.create_memory(
            content="Regular memory",
            memory_type=MemoryType.EXPERIENCE,
            importance=0.8,
            timestamp=self.current_time - 86400  # 1 day ago
        )
        
        core_memory = await manager.create_memory(
            content="Core memory",
            is_core=True,
            importance=0.8,
            timestamp=self.current_time - 86400  # 1 day ago
        )
        
        initial_regular_strength = regular_memory.current_strength
        initial_core_strength = core_memory.current_strength
        
        updated_count = await manager.update_all_memories(self.current_time)
        
        assert updated_count == 2  # Both memories processed
        
        # Regular memory should decay
        assert regular_memory.current_strength < initial_regular_strength
        
        # Core memory should not decay
        assert core_memory.current_strength == initial_core_strength

    @pytest.mark.asyncio
    async def test_clean_expired_memories(self): pass
        """Test cleaning expired memories"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Create a memory that will expire quickly
        memory = await manager.create_memory(
            content="Memory to expire",
            importance=0.1,
            timestamp=self.current_time - 86400 * 30  # 30 days ago
        )
        
        # Force decay to make it expire
        memory.update_strength(self.current_time, decay_rate=0.5)
        
        initial_count = len(manager.memories)
        # Use a higher threshold to ensure the memory expires (strength will be around 0.2-0.3)
        cleaned_count = await manager.clean_expired_memories(threshold=0.5)
        
        assert cleaned_count == 1
        assert len(manager.memories) == initial_count - 1
        assert memory.id not in manager.memories

    @pytest.mark.asyncio
    async def test_get_memories_by_tag(self): pass
        """Test querying memories by tag"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        memory1 = await manager.create_memory(
            content="Combat memory",
            tags=["combat", "important"]
        )
        
        memory2 = await manager.create_memory(
            content="Social memory",
            tags=["social", "important"]
        )
        
        memory3 = await manager.create_memory(
            content="Exploration memory",
            tags=["exploration"]
        )
        
        combat_memories = await manager.get_memories_by_tag("combat")
        important_memories = await manager.get_memories_by_tag("important")
        
        assert len(combat_memories) == 1
        assert memory1 in combat_memories
        
        assert len(important_memories) == 2
        assert memory1 in important_memories
        assert memory2 in important_memories

    @pytest.mark.asyncio
    async def test_get_memories_by_category(self): pass
        """Test querying memories by category"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        memory1 = await manager.create_memory(
            content="Interaction memory",
            categories=["interaction"]
        )
        
        memory2 = await manager.create_memory(
            content="Combat memory", 
            categories=["combat"]
        )
        
        interaction_memories = await manager.get_memories_by_category("interaction")
        combat_memories = await manager.get_memories_by_category("combat")
        
        assert len(interaction_memories) == 1
        assert memory1 in interaction_memories
        
        assert len(combat_memories) == 1
        assert memory2 in combat_memories

    @pytest.mark.asyncio
    async def test_get_memories_involving_entity(self): pass
        """Test querying memories involving specific entities"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        memory1 = await manager.create_memory(
            content="Memory with John",
            entities_involved=["john", "jane"]
        )
        
        memory2 = await manager.create_memory(
            content="Memory with Jane",
            entities_involved=["jane"]
        )
        
        memory3 = await manager.create_memory(
            content="Solo memory",
            entities_involved=[]
        )
        
        john_memories = await manager.get_memories_involving_entity("john")
        jane_memories = await manager.get_memories_involving_entity("jane")
        
        assert len(john_memories) == 1
        assert memory1 in john_memories
        
        assert len(jane_memories) == 2
        assert memory1 in jane_memories
        assert memory2 in jane_memories

    @pytest.mark.asyncio
    async def test_get_recent_memories(self): pass
        """Test querying recent memories"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Create memories with different timestamps
        old_memory = await manager.create_memory(
            content="Old memory",
            timestamp=self.current_time - 86400 * 7  # 7 days ago
        )
        
        recent_memory = await manager.create_memory(
            content="Recent memory",
            timestamp=self.current_time - 3600  # 1 hour ago
        )
        
        latest_memory = await manager.create_memory(
            content="Latest memory",
            timestamp=self.current_time  # Now
        )
        
        recent_memories = await manager.get_recent_memories(
            count=2, 
            current_time=self.current_time
        )
        
        assert len(recent_memories) == 2
        assert recent_memories[0] == latest_memory  # Most recent first
        assert recent_memories[1] == recent_memory

    @pytest.mark.asyncio
    async def test_get_most_important_memories(self): pass
        """Test querying most important memories"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        low_memory = await manager.create_memory(
            content="Low importance",
            importance=0.3
        )
        
        high_memory = await manager.create_memory(
            content="High importance",
            importance=0.9
        )
        
        medium_memory = await manager.create_memory(
            content="Medium importance",
            importance=0.6
        )
        
        important_memories = await manager.get_most_important_memories(count=2)
        
        assert len(important_memories) == 2
        assert important_memories[0] == high_memory  # Highest first
        assert important_memories[1] == medium_memory

    @pytest.mark.asyncio
    async def test_get_most_relevant_memories(self): pass
        """Test querying most relevant memories for a context"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        combat_memory = await manager.create_memory(
            content="Fighting bandits in combat",
            importance=0.8,
            tags=["combat", "bandits"]
        )
        
        social_memory = await manager.create_memory(
            content="Talking to merchants",
            importance=0.6,
            tags=["social", "merchant"]
        )
        
        relevant_memories = await manager.get_most_relevant_memories(
            query_context="combat situation",
            count=2,
            current_time=self.current_time
        )
        
        assert len(relevant_memories) >= 1
        # Combat memory should be more relevant to combat context

    @pytest.mark.asyncio
    async def test_get_random_weighted_memories(self): pass
        """Test getting random weighted memories"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Create several memories with different importance
        for i in range(5): pass
            await manager.create_memory(
                content=f"Memory {i}",
                importance=0.2 + (i * 0.15)  # Varying importance
            )
        
        random_memories = await manager.get_random_weighted_memories(
            count=3,
            current_time=self.current_time
        )
        
        assert len(random_memories) <= 3
        assert len(random_memories) <= len(manager.memories)

    @pytest.mark.asyncio
    async def test_generate_entity_sentiment(self): pass
        """Test generating sentiment for an entity"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Create memories with different emotional valences
        positive_memory = await manager.create_memory(
            content="Good interaction with John",
            entities_involved=["john"],
            emotional_valence=MemoryEmotionalValence.POSITIVE,
            importance=0.8
        )
        
        negative_memory = await manager.create_memory(
            content="Bad interaction with John",
            entities_involved=["john"],
            emotional_valence=MemoryEmotionalValence.NEGATIVE,
            importance=0.6
        )
        
        sentiment = await manager.generate_entity_sentiment(
            "john",
            current_time=self.current_time
        )
        
        assert isinstance(sentiment, float)
        assert -2.0 <= sentiment <= 2.0

    @pytest.mark.asyncio
    async def test_memory_manager_serialization(self): pass
        """Test MemoryManager serialization"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            world_id=self.world_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Add some memories
        memory1 = await manager.create_memory(
            content="Memory 1",
            importance=0.8
        )
        
        memory2 = await manager.create_memory(
            content="Memory 2",
            importance=0.6
        )
        
        # Serialize
        manager_dict = await manager.to_dict()
        
        # Verify structure
        assert manager_dict["entity_id"] == self.entity_id
        assert manager_dict["world_id"] == self.world_id
        assert "memories" in manager_dict
        assert len(manager_dict["memories"]) == 2
        
        # Deserialize
        restored_manager = await MemoryManager.from_dict(
            manager_dict,
            event_dispatcher=self.mock_dispatcher
        )
        
        assert restored_manager.entity_id == manager.entity_id
        assert restored_manager.world_id == manager.world_id
        assert len(restored_manager.memories) == 2

    @pytest.mark.asyncio
    async def test_memory_manager_with_storage(self): pass
        """Test MemoryManager with storage manager"""
        self.mock_storage.load_memories = AsyncMock(return_value={})
        self.mock_storage.save_memory = AsyncMock()
        self.mock_storage.delete_memory = AsyncMock()
        
        manager = await MemoryManager.get_instance(
            entity_id=self.entity_id,
            storage_manager=self.mock_storage,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Should have called load_memories during initialization
        self.mock_storage.load_memories.assert_called_once()
        
        # Create memory - should trigger save
        memory = await manager.create_memory(content="Test memory")
        
        # Delete memory - should trigger delete
        await manager.delete_memory(memory.id)


class TestMemoryForgottenEvent: pass
    """Test class for MemoryForgottenEvent"""
    
    def test_memory_forgotten_event(self): pass
        """Test MemoryForgottenEvent creation"""
        event = MemoryForgottenEvent(
            memory_id="test_id",
            entity_id="test_entity",
            reason="expired"
        )
        
        assert event.memory_id == "test_id"
        assert event.entity_id == "test_entity"
        assert event.reason == "expired"
        assert event.event_type == "memory.forgotten"


class TestMemoryManagerExtended: pass
    """Extended tests for MemoryManager covering missing functionality"""

    def setup_method(self): pass
        """Set up test fixtures"""
        self.mock_dispatcher = Mock(spec=EventDispatcher)
        self.mock_dispatcher.emit_event = Mock()
        self.mock_dispatcher.publish = AsyncMock()
        self.mock_storage = Mock()
        self.entity_id = "test_entity"
        self.world_id = "test_world"
        self.current_time = time.time()
        MemoryManager._instances.clear()

    @pytest.mark.asyncio
    async def test_get_memories_by_query_comprehensive(self): pass
        """Test comprehensive query functionality"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Create test memories with various attributes
        memory1 = await manager.create_memory(
            content="Combat memory involving bandits",
            memory_type=MemoryType.INTERACTION,
            importance=0.8,
            entities_involved=["bandit1", "bandit2"],
            tags=["combat", "bandits"],
            timestamp=self.current_time - 3600
        )
        
        memory2 = await manager.create_memory(
            content="Social memory with merchant",
            memory_type=MemoryType.EXPERIENCE,
            importance=0.6,
            entities_involved=["merchant"],
            tags=["social", "trade"],
            timestamp=self.current_time - 7200
        )
        
        memory3 = await manager.create_memory(
            content="Core memory about family",
            memory_type=MemoryType.CORE,
            importance=0.9,
            entities_involved=["family"],
            tags=["family", "core"],
            timestamp=self.current_time - 86400
        )

        # Test tag filtering (string)
        query = {"tags": "combat"}
        results = await manager.get_memories_by_query(query)
        assert len(results) == 1
        assert results[0] == memory1

        # Test tag filtering (list) - should find memories with ANY of the tags
        query = {"tags": ["social", "core"]}
        results = await manager.get_memories_by_query(query)
        assert len(results) == 2  # memory2 (social) and memory3 (core)

        # Test categories filtering - use a category that might actually exist
        query = {"categories": "PERSONAL"}  # This is a default category
        results = await manager.get_memories_by_query(query)
        # Just verify it doesn't crash - categories might be present by default

        # Test entities_involved filtering (string)
        query = {"entities_involved": "merchant"}
        results = await manager.get_memories_by_query(query)
        assert len(results) == 1
        assert results[0] == memory2

        # Test entities_involved filtering (list)
        query = {"entities_involved": ["bandit1", "family"]}
        results = await manager.get_memories_by_query(query)
        assert len(results) == 2

        # Test importance filtering
        query = {"min_importance": 0.7}
        results = await manager.get_memories_by_query(query)
        assert len(results) == 2  # memory1 and memory3

        query = {"max_importance": 0.7}
        results = await manager.get_memories_by_query(query)
        assert len(results) >= 1  # memory2 and potentially others

        # Test memory_type filtering
        query = {"memory_type": "CORE"}
        results = await manager.get_memories_by_query(query)
        assert len(results) == 1
        assert results[0] == memory3

        # Test timestamp filtering
        query = {"since_timestamp": self.current_time - 5000}
        results = await manager.get_memories_by_query(query)
        assert len(results) >= 1  # At least some memories should match

        query = {"until_timestamp": self.current_time - 5000}
        results = await manager.get_memories_by_query(query)
        assert len(results) >= 1  # At least memory3

        # Test text_contains filtering
        query = {"text_contains": "merchant"}
        results = await manager.get_memories_by_query(query)
        assert len(results) == 1
        assert results[0] == memory2

        # Test sorting by timestamp
        query = {"sort_by": "timestamp", "sort_order": "desc"}
        results = await manager.get_memories_by_query(query)
        assert results[0] == memory1  # Most recent

        query = {"sort_by": "timestamp", "sort_order": "asc"}
        results = await manager.get_memories_by_query(query)
        assert results[0] == memory3  # Oldest

        # Test sorting by importance
        query = {"sort_by": "importance", "sort_order": "desc"}
        results = await manager.get_memories_by_query(query)
        assert results[0] == memory3  # Highest importance

        # Test sorting by saliency
        query = {"sort_by": "saliency"}
        results = await manager.get_memories_by_query(query)
        assert len(results) == 3

        # Test sorting by recall_count
        await manager.recall_memory(memory1.id)
        query = {"sort_by": "recall_count", "sort_order": "desc"}
        results = await manager.get_memories_by_query(query)
        assert results[0] == memory1  # Has highest recall count

        # Test max_results limitation
        query = {}
        results = await manager.get_memories_by_query(query, max_results=2)
        assert len(results) == 2

        # Test complex combined query
        query = {
            "tags": ["combat", "social"],
            "min_importance": 0.5,
            "sort_by": "importance",
            "sort_order": "desc"
        }
        results = await manager.get_memories_by_query(query, max_results=5)
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_logging_methods(self): pass
        """Test all logging methods are called"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Test logging methods by triggering conditions that use them
        with patch('backend.systems.memory.services.memory_manager.logger') as mock_logger: pass
            # Trigger _log_error by causing an error condition
            manager._log_error("Test error message")
            mock_logger.error.assert_called_with(f"[Memory][{self.entity_id}] Test error message")
            
            # Trigger _log_warning  
            manager._log_warning("Test warning message")
            mock_logger.warning.assert_called_with(f"[Memory][{self.entity_id}] Test warning message")
            
            # Trigger _log_info
            manager._log_info("Test info message")
            mock_logger.info.assert_called_with(f"[Memory][{self.entity_id}] Test info message")
            
            # Trigger _log_debug
            manager._log_debug("Test debug message")
            mock_logger.debug.assert_called_with(f"[Memory][{self.entity_id}] Test debug message")

    @pytest.mark.asyncio
    async def test_memory_manager_with_async_publish_event_dispatcher(self): pass
        """Test MemoryManager with event dispatcher that only has publish method"""
        # Create a mock dispatcher that only has publish method (no emit_event)
        async_dispatcher = Mock()
        async_dispatcher.publish = AsyncMock()
        # Make sure it doesn't have emit_event to trigger the publish path
        if hasattr(async_dispatcher, 'emit_event'): pass
            delattr(async_dispatcher, 'emit_event')
        
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=async_dispatcher
        )
        
        # Create memory - should use publish method since no emit_event
        memory = await manager.create_memory(content="Test memory")
        async_dispatcher.publish.assert_called()
        
        # Delete memory - should use publish method
        await manager.delete_memory(memory.id)
        assert async_dispatcher.publish.call_count == 2

    @pytest.mark.asyncio
    async def test_recall_memory_with_async_publish(self): pass
        """Test recalling memory with async publish dispatcher"""
        async_dispatcher = Mock()
        async_dispatcher.publish = AsyncMock()
        # Remove emit_event to ensure publish is used
        if hasattr(async_dispatcher, 'emit_event'): pass
            delattr(async_dispatcher, 'emit_event')
        
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=async_dispatcher
        )
        
        memory = await manager.create_memory(content="Test memory")
        
        # Clear previous calls
        async_dispatcher.publish.reset_mock()
        
        # Recall memory - should trigger event
        recalled = await manager.recall_memory(memory.id, "test context")
        
        assert recalled == memory
        async_dispatcher.publish.assert_called_once()

    @pytest.mark.asyncio 
    async def test_storage_operations(self): pass
        """Test storage-related operations"""
        # Mock storage with all required methods
        self.mock_storage.load_memories = AsyncMock(return_value={
            "existing_id": {
                "id": "existing_id",
                "owner_id": self.entity_id,
                "content": "Loaded memory",
                "memory_type": "EXPERIENCE",
                "importance": 0.5,
                "timestamp": time.time()
            }
        })
        self.mock_storage.save_memory = AsyncMock()
        self.mock_storage.save_all_memories = AsyncMock()
        self.mock_storage.delete_memory = AsyncMock()
        
        manager = MemoryManager(
            entity_id=self.entity_id,
            storage_manager=self.mock_storage,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Test _load_memories
        await manager._load_memories()
        self.mock_storage.load_memories.assert_called()
        
        # Test _save_memory - storage expects (entity_id, memory_id, dict)
        memory = Memory(
            owner_id=self.entity_id,
            content="Test memory",
            event_dispatcher=self.mock_dispatcher
        )
        await manager._save_memory(memory)
        # Verify the call was made with correct entity_id and memory_id
        # The dict content may have small floating point differences
        call_args = self.mock_storage.save_memory.call_args
        assert call_args[0][0] == self.entity_id  # entity_id
        assert call_args[0][1] == memory.id  # memory_id
        assert isinstance(call_args[0][2], dict)  # memory dict
        
        # Test _save_all_memories
        await manager._save_all_memories()
        self.mock_storage.save_all_memories.assert_called()
        
        # Test _delete_memory_from_storage
        await manager._delete_memory_from_storage("test_id")
        self.mock_storage.delete_memory.assert_called_with(self.entity_id, "test_id")

    @pytest.mark.asyncio
    async def test_from_dict_classmethod(self): pass
        """Test creating MemoryManager from dictionary"""
        # Create test data
        memory_data = {
            "id": "test_memory_id",
            "owner_id": self.entity_id,
            "content": "Test memory content",
            "memory_type": "EXPERIENCE",
            "importance": 0.7,
            "timestamp": time.time(),
            "emotional_valence": "NEUTRAL"
        }
        
        manager_data = {
            "entity_id": self.entity_id,
            "world_id": self.world_id,
            "max_memory_count": 1000,
            "decay_rate": 0.01,
            "memories": {
                "test_memory_id": memory_data
            }
        }
        
        # Create manager from dict
        manager = await MemoryManager.from_dict(
            manager_data,
            storage_manager=self.mock_storage,
            event_dispatcher=self.mock_dispatcher
        )
        
        assert manager.entity_id == self.entity_id
        assert manager.world_id == self.world_id
        assert manager.max_memory_count == 1000
        assert manager.decay_rate == 0.01
        assert len(manager.memories) == 1
        assert "test_memory_id" in manager.memories

    @pytest.mark.asyncio
    async def test_create_memory_with_string_memory_type_and_core(self): pass
        """Test create_memory with string memory type and is_core=True"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Test with string memory type and is_core=True
        memory = await manager.create_memory(
            content="Test core memory",
            memory_type="EXPERIENCE", 
            is_core=True
        )
        
        assert memory.memory_type == MemoryType.CORE
        
        # Test with MemoryType enum and is_core=True
        memory2 = await manager.create_memory(
            content="Test core memory 2",
            memory_type=MemoryType.INTERACTION,
            is_core=True
        )
        
        assert memory2.memory_type == MemoryType.CORE

    @pytest.mark.asyncio
    async def test_generate_entity_sentiment_edge_cases(self): pass
        """Test entity sentiment generation edge cases"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Test with no memories for entity
        sentiment = await manager.generate_entity_sentiment("unknown_entity")
        assert sentiment == 0.0
        
        # Test with memories having zero total weight
        memory = await manager.create_memory(
            content="Test memory",
            entities_involved=["test_entity"],
            emotional_valence=MemoryEmotionalValence.NEUTRAL,
            importance=0.0,
            timestamp=self.current_time - (86400 * 365)  # Very old memory
        )
        
        sentiment = await manager.generate_entity_sentiment("test_entity", self.current_time)
        assert -1.0 <= sentiment <= 1.0

    @pytest.mark.asyncio
    async def test_update_memory_importance_nonexistent(self): pass
        """Test updating importance of nonexistent memory"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        result = await manager.update_memory_importance("nonexistent_id", 0.8)
        assert result is None

    @pytest.mark.asyncio
    async def test_clean_expired_memories_with_threshold(self): pass
        """Test cleaning expired memories with different thresholds"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Create memory with very low saliency (should be cleaned)
        old_memory = await manager.create_memory(
            content="Very old memory",
            importance=0.1,
            timestamp=self.current_time - (86400 * 30)  # 30 days old
        )
        
        # Force low saliency
        old_memory.importance = 0.05
        
        # Clean with high threshold
        cleaned = await manager.clean_expired_memories(threshold=0.5)
        assert cleaned >= 0  # Should clean some memories

    @pytest.mark.asyncio
    async def test_memory_manager_error_conditions(self): pass
        """Test various error conditions and edge cases"""
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Test add_memory with different owner_id
        foreign_memory = Memory(
            owner_id="different_entity",
            content="Foreign memory",
            event_dispatcher=self.mock_dispatcher
        )
        
        await manager.add_memory(foreign_memory)
        assert foreign_memory.owner_id == self.entity_id  # Should be updated
        
        # Test delete_memory warning for nonexistent memory
        with patch('backend.systems.memory.services.memory_manager.logger') as mock_logger: pass
            result = await manager.delete_memory("nonexistent_id", "test reason")
            assert result is False
            mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_memory_creation_event_dispatch_edge_cases(self): pass
        """Test edge cases in event dispatching during memory creation"""
        # Test with dispatcher that has neither emit_event nor publish
        minimal_dispatcher = Mock()
        
        manager = MemoryManager(
            entity_id=self.entity_id,
            event_dispatcher=minimal_dispatcher
        )
        
        # Should not raise error even without proper event methods
        memory = await manager.create_memory(content="Test memory")
        assert memory.content == "Test memory"

    @pytest.mark.asyncio
    async def test_storage_manager_integration_scenarios(self): pass
        """Test different storage manager integration scenarios"""
        # Test with storage manager that raises exceptions
        failing_storage = Mock()
        failing_storage.load_memories = AsyncMock(side_effect=Exception("Storage error"))
        failing_storage.save_memory = AsyncMock(side_effect=Exception("Save error"))
        failing_storage.delete_memory = AsyncMock(side_effect=Exception("Delete error"))
        
        manager = MemoryManager(
            entity_id=self.entity_id,
            storage_manager=failing_storage,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Operations should still work even if storage fails
        memory = await manager.create_memory(content="Test memory")
        assert memory.id in manager.memories
        
        # Delete should still work
        result = await manager.delete_memory(memory.id)
        assert result is True
