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
Tests for backend.systems.memory.models.memory

Tests for the Memory model covering creation, decay, recall,
categorization, and event handling functionality.
"""

import pytest
import time
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import the module being tested
from backend.systems.memory.models.memory import (
    Memory,
    MemoryType,
    MemoryEmotionalValence,
    MemoryGraphLink,
    MemoryCreatedEvent,
    MemoryDecayedEvent,
    MemoryAccessedEvent,
    MemoryRecalledEvent,
    MemoryCategorizedEvent,
)
from backend.systems.memory.memory_categories import MemoryCategory
from backend.systems.events import EventDispatcher


class TestMemory: pass
    """Test class for Memory model"""

    def setup_method(self): pass
        """Set up test fixtures"""
        self.mock_dispatcher = Mock(spec=EventDispatcher)
        # Add the emit_event method to the mock
        self.mock_dispatcher.emit_event = Mock()
        self.current_time = time.time()
        
    def test_memory_creation_basic(self): pass
        """Test basic memory creation with required parameters"""
        memory = Memory(
            owner_id="test_entity",
            content="Test memory content",
            event_dispatcher=self.mock_dispatcher
        )
        
        assert memory.owner_id == "test_entity"
        assert memory.content == "Test memory content"
        assert memory.memory_type == MemoryType.EXPERIENCE
        assert memory.emotional_valence == MemoryEmotionalValence.NEUTRAL
        assert memory.importance >= 0.0 and memory.importance <= 1.0
        assert memory.id is not None
        assert len(memory.id) > 0
        
    def test_memory_creation_with_all_parameters(self): pass
        """Test memory creation with all parameters specified"""
        entities = ["entity1", "entity2"]
        tags = ["important", "combat"]
        categories = ["interaction", "combat"]
        metadata = {"location": "tavern", "witnesses": 3}
        
        memory = Memory(
            owner_id="test_entity",
            content="Fought bandits in tavern",
            memory_type=MemoryType.INTERACTION,
            memory_id="custom_id",
            importance=0.8,
            entities_involved=entities,
            tags=tags,
            categories=categories,
            emotional_valence=MemoryEmotionalValence.NEGATIVE,
            timestamp=self.current_time,
            location="tavern",
            metadata=metadata,
            event_dispatcher=self.mock_dispatcher
        )
        
        assert memory.id == "custom_id"
        assert memory.importance == 0.8
        assert memory.entities_involved == entities
        assert memory.tags == tags
        assert memory.categories == categories
        assert memory.emotional_valence == MemoryEmotionalValence.NEGATIVE
        assert memory.timestamp == self.current_time
        assert memory.location == "tavern"
        assert memory.metadata == metadata
        
    def test_memory_creation_string_types(self): pass
        """Test memory creation with string types"""
        memory = Memory(
            owner_id="test_entity",
            content="Test content",
            memory_type="CORE",
            emotional_valence="POSITIVE",
            event_dispatcher=self.mock_dispatcher
        )
        
        assert memory.memory_type == MemoryType.CORE
        assert memory.emotional_valence == MemoryEmotionalValence.POSITIVE
        
    def test_memory_creation_regular_string_type(self): pass
        """Test memory creation with 'regular' string type"""
        memory = Memory(
            owner_id="test_entity",
            content="Test content",
            memory_type="regular",
            event_dispatcher=self.mock_dispatcher
        )
        
        assert memory.memory_type == MemoryType.EXPERIENCE
        
    def test_memory_decay_regular_memory(self): pass
        """Test that regular memories decay over time"""
        memory = Memory(
            owner_id="test_entity",
            content="Test memory",
            memory_type=MemoryType.EXPERIENCE,
            importance=0.8,
            timestamp=self.current_time,
            event_dispatcher=self.mock_dispatcher
        )
        
        initial_strength = memory.formation_strength
        future_time = self.current_time + 86400  # 1 day later
        
        memory.update_strength(future_time, decay_rate=0.1)
        
        assert memory.current_strength < initial_strength
        
    def test_memory_decay_core_memory(self): pass
        """Test that core memories don't decay"""
        memory = Memory(
            owner_id="test_entity",
            content="Core memory",
            memory_type=MemoryType.CORE,
            importance=0.8,
            timestamp=self.current_time,
            event_dispatcher=self.mock_dispatcher
        )
        
        initial_strength = memory.formation_strength
        future_time = self.current_time + 86400  # 1 day later
        
        memory.update_strength(future_time, decay_rate=0.1)
        
        assert memory.current_strength == initial_strength
        
    def test_memory_recall(self): pass
        """Test memory recall functionality"""
        memory = Memory(
            owner_id="test_entity",
            content="Test memory",
            timestamp=self.current_time,
            event_dispatcher=self.mock_dispatcher
        )
        
        initial_recall_count = memory.recall_count
        
        memory.recall(context="test context")
        
        assert memory.recall_count == initial_recall_count + 1
        assert memory.last_recalled is not None
        
    def test_memory_access(self): pass
        """Test memory access functionality"""
        memory = Memory(
            owner_id="test_entity",
            content="Test memory",
            event_dispatcher=self.mock_dispatcher
        )
        
        initial_access_count = memory.access_count
        
        memory.access(context="test access")
        
        assert memory.access_count == initial_access_count + 1
        assert memory.last_accessed is not None
        
    def test_memory_saliency_calculation(self): pass
        """Test memory saliency calculation"""
        memory = Memory(
            owner_id="test_entity",
            content="Test memory",
            importance=0.8,
            timestamp=self.current_time,
            event_dispatcher=self.mock_dispatcher
        )
        
        saliency = memory.get_current_saliency()
        
        assert saliency >= 0.0
        assert saliency <= 1.0
        
    def test_memory_relevance_calculation(self): pass
        """Test memory relevance calculation for context"""
        memory = Memory(
            owner_id="test_entity",
            content="Fighting bandits in the tavern",
            importance=0.8,
            timestamp=self.current_time,
            tags=["combat", "tavern"],
            event_dispatcher=self.mock_dispatcher
        )
        
        relevance = memory.calculate_relevance(
            query_context="combat situation",
            current_time=self.current_time + 3600
        )
        
        assert relevance >= 0.0
        
    def test_memory_expiration(self): pass
        """Test memory expiration checking"""
        memory = Memory(
            owner_id="test_entity",
            content="Test memory",
            importance=0.1,
            timestamp=self.current_time,
            event_dispatcher=self.mock_dispatcher
        )
        
        # Force decay to make it expire
        future_time = self.current_time + 86400 * 30  # 30 days
        memory.update_strength(future_time, decay_rate=0.2)
        
        # Use a threshold higher than the resulting strength (which will be around 0.2)
        assert memory.is_expired(threshold=0.3)
        
    def test_memory_graph_links(self): pass
        """Test memory graph linking functionality"""
        memory = Memory(
            owner_id="test_entity",
            content="Test memory",
            event_dispatcher=self.mock_dispatcher
        )
        
        memory.add_link("target_memory_id", "caused_by", 0.8)
        
        assert len(memory.memory_graph) == 1
        assert memory.memory_graph[0].target_memory_id == "target_memory_id"
        assert memory.memory_graph[0].relationship_type == "caused_by"
        assert memory.memory_graph[0].strength == 0.8
        
    def test_memory_tag_operations(self): pass
        """Test memory tag operations"""
        memory = Memory(
            owner_id="test_entity",
            content="Test memory",
            tags=["initial_tag"],
            event_dispatcher=self.mock_dispatcher
        )
        
        assert memory.has_tag("initial_tag")
        assert not memory.has_tag("non_existent_tag")
        
        memory.add_tag("new_tag")
        assert memory.has_tag("new_tag")
        assert "new_tag" in memory.tags
        
        removed = memory.remove_tag("initial_tag")
        assert removed
        assert not memory.has_tag("initial_tag")
        
        removed = memory.remove_tag("non_existent_tag")
        assert not removed
        
    def test_memory_category_operations(self): pass
        """Test memory category operations"""
        memory = Memory(
            owner_id="test_entity",
            content="Test memory",
            categories=["interaction"],
            event_dispatcher=self.mock_dispatcher
        )
        
        assert memory.has_category("interaction")
        assert memory.has_category(MemoryCategory.INTERACTION)
        assert not memory.has_category("non_existent_category")
        
        memory.update_categories(["interaction", "combat"])
        assert memory.has_category("combat")
        
    def test_memory_event_emission(self): pass
        """Test that memory operations emit appropriate events"""
        # Test creation event
        memory = Memory(
            owner_id="test_entity",
            content="Test memory",
            event_dispatcher=self.mock_dispatcher
        )
        
        # Should have emitted creation event
        self.mock_dispatcher.emit_event.assert_called()
        
        # Reset mock
        self.mock_dispatcher.reset_mock()
        
        # Test access event
        memory.access("test context")
        self.mock_dispatcher.emit_event.assert_called()
        
    def test_memory_serialization(self): pass
        """Test memory serialization to and from dictionary"""
        original_memory = Memory(
            owner_id="test_entity",
            content="Test memory content",
            memory_type=MemoryType.INTERACTION,
            importance=0.8,
            entities_involved=["entity1"],
            tags=["tag1", "tag2"],
            categories=["interaction"],
            emotional_valence=MemoryEmotionalValence.POSITIVE,
            location="tavern",
            metadata={"key": "value"},
            event_dispatcher=self.mock_dispatcher
        )
        
        # Add a link
        original_memory.add_link("target_id", "caused_by", 0.7)
        
        # Serialize
        memory_dict = original_memory.to_dict()
        
        # Deserialize
        restored_memory = Memory.from_dict(memory_dict, self.mock_dispatcher)
        
        # Verify all properties match
        assert restored_memory.owner_id == original_memory.owner_id
        assert restored_memory.content == original_memory.content
        assert restored_memory.memory_type == original_memory.memory_type
        assert restored_memory.importance == original_memory.importance
        assert restored_memory.entities_involved == original_memory.entities_involved
        assert restored_memory.tags == original_memory.tags
        assert restored_memory.categories == original_memory.categories
        assert restored_memory.emotional_valence == original_memory.emotional_valence
        assert restored_memory.location == original_memory.location
        assert restored_memory.metadata == original_memory.metadata
        assert len(restored_memory.memory_graph) == len(original_memory.memory_graph)
        
    def test_memory_string_representation(self): pass
        """Test memory string representation"""
        memory = Memory(
            owner_id="test_entity",
            content="Test memory content",
            event_dispatcher=self.mock_dispatcher
        )
        
        str_repr = str(memory)
        
        assert "Memory" in str_repr
        assert memory.id in str_repr
        assert "Test memory content" in str_repr


class TestMemoryGraphLink: pass
    """Test class for MemoryGraphLink"""
    
    def test_memory_graph_link_creation(self): pass
        """Test memory graph link creation"""
        link = MemoryGraphLink("target_id", "caused_by", 0.8)
        
        assert link.target_memory_id == "target_id"
        assert link.relationship_type == "caused_by"
        assert link.strength == 0.8
        
    def test_memory_graph_link_serialization(self): pass
        """Test memory graph link serialization"""
        link = MemoryGraphLink("target_id", "follows", 0.6)
        
        link_dict = link.to_dict()
        restored_link = MemoryGraphLink.from_dict(link_dict)
        
        assert restored_link.target_memory_id == link.target_memory_id
        assert restored_link.relationship_type == link.relationship_type
        assert restored_link.strength == link.strength


class TestMemoryEvents: pass
    """Test class for memory event classes"""
    
    def test_memory_created_event(self): pass
        """Test MemoryCreatedEvent"""
        event = MemoryCreatedEvent(
            memory_id="test_id",
            entity_id="test_entity",
            content="test content",
            memory_type="EXPERIENCE",
            categories=["interaction"],
            importance=0.8
        )
        
        assert event.memory_id == "test_id"
        assert event.entity_id == "test_entity"
        assert event.content == "test content"
        assert event.memory_type == "EXPERIENCE"
        assert event.categories == ["interaction"]
        assert event.importance == 0.8
        assert event.event_type == "memory.created"
        
    def test_memory_decayed_event(self): pass
        """Test MemoryDecayedEvent"""
        event = MemoryDecayedEvent(
            memory_id="test_id",
            entity_id="test_entity",
            old_saliency=0.8,
            new_saliency=0.7
        )
        
        assert event.memory_id == "test_id"
        assert event.entity_id == "test_entity"
        assert event.old_saliency == 0.8
        assert event.new_saliency == 0.7
        assert event.event_type == "memory.decayed"
        
    def test_memory_accessed_event(self): pass
        """Test MemoryAccessedEvent"""
        event = MemoryAccessedEvent(
            memory_id="test_id",
            entity_id="test_entity",
            context="test context"
        )
        
        assert event.memory_id == "test_id"
        assert event.entity_id == "test_entity"
        assert event.context == "test context"
        assert event.event_type == "memory.accessed"
        
    def test_memory_recalled_event(self): pass
        """Test MemoryRecalledEvent"""
        event = MemoryRecalledEvent(
            memory_id="test_id",
            entity_id="test_entity",
            context="recall context"
        )
        
        assert event.memory_id == "test_id"
        assert event.entity_id == "test_entity"
        assert event.context == "recall context"
        assert event.event_type == "memory.recalled"
        
    def test_memory_categorized_event(self): pass
        """Test MemoryCategorizedEvent"""
        event = MemoryCategorizedEvent(
            memory_id="test_id",
            entity_id="test_entity",
            categories=["interaction", "combat"]
        )
        
        assert event.memory_id == "test_id"
        assert event.entity_id == "test_entity"
        assert event.categories == ["interaction", "combat"]
        assert event.event_type == "memory.categorized"
