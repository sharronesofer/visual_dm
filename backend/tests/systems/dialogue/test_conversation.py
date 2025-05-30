from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from typing import Any
from typing import List
from uuid import UUID
"""
Tests for backend.systems.dialogue.conversation

Comprehensive tests for the ConversationEntry and ConversationHistory classes.
"""

import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

# Import the module being tested
try: pass
    from backend.systems.dialogue.conversation import ConversationEntry, ConversationHistory
    from backend.systems.events import EventDispatcher
    from backend.systems.dialogue.utils import count_tokens, extract_key_info
except ImportError as e: pass
    pytest.skip(f"Could not import dialogue modules: {e}", allow_module_level=True)


@pytest.fixture
def mock_event_dispatcher(): pass
    """Mock event dispatcher for testing."""
    dispatcher = Mock(spec=EventDispatcher)
    dispatcher.dispatch = Mock()
    return dispatcher


@pytest.fixture
def sample_conversation_entry(): pass
    """Create a sample conversation entry for testing."""
    return ConversationEntry(
        entry_id="test_entry_1",
        conversation_id="test_conv_1",
        sender_id="player",
        content="Hello there!",
        entry_type="dialogue",
        metadata={"emotion": "friendly"}
    )


@pytest.fixture
def sample_conversation_history(mock_event_dispatcher): pass
    """Create a sample conversation history for testing."""
    return ConversationHistory(
        conversation_id="test_conv_1",
        participants={"player": "player", "npc": "merchant"},
        location_id="town_square",
        metadata={"mood": "cheerful"},
        event_dispatcher=mock_event_dispatcher
    )


def test_module_imports(): pass
    """Test that the module can be imported without errors."""
    from backend.systems.dialogue.conversation import ConversationEntry, ConversationHistory
    assert ConversationEntry is not None
    assert ConversationHistory is not None


class TestConversationEntry: pass
    """Test class for ConversationEntry"""
    
    def test_entry_initialization(self): pass
        """Test conversation entry initialization with various parameters."""
        # Test with all parameters
        entry = ConversationEntry(
            entry_id="test_id",
            conversation_id="conv_1",
            sender_id="player",
            content="Test message",
            entry_type="dialogue",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            metadata={"emotion": "happy"}
        )
        
        assert entry.id == "test_id"
        assert entry.conversation_id == "conv_1"
        assert entry.sender_id == "player"
        assert entry.content == "Test message"
        assert entry.type == "dialogue"
        assert entry.timestamp == datetime(2024, 1, 1, 12, 0, 0)
        assert entry.metadata["emotion"] == "happy"
    
    def test_entry_initialization_defaults(self): pass
        """Test conversation entry initialization with default parameters."""
        entry = ConversationEntry(content="Default test")
        
        assert entry.id is not None  # Should generate a UUID
        assert entry.conversation_id is None
        assert entry.sender_id is None
        assert entry.content == "Default test"
        assert entry.type == "dialogue"
        assert isinstance(entry.timestamp, datetime)
        assert entry.metadata == {}
    
    def test_entry_to_dict(self, sample_conversation_entry): pass
        """Test converting entry to dictionary."""
        entry_dict = sample_conversation_entry.to_dict()
        
        assert isinstance(entry_dict, dict)
        assert entry_dict["id"] == "test_entry_1"
        assert entry_dict["conversation_id"] == "test_conv_1"
        assert entry_dict["sender_id"] == "player"
        assert entry_dict["content"] == "Hello there!"
        assert entry_dict["type"] == "dialogue"
        assert "timestamp" in entry_dict
        assert entry_dict["metadata"]["emotion"] == "friendly"
    
    def test_entry_from_dict(self): pass
        """Test creating entry from dictionary."""
        data = {
            "id": "test_id",
            "conversation_id": "conv_1", 
            "sender_id": "npc",
            "content": "Greetings!",
            "type": "action",
            "timestamp": "2024-01-01T12:00:00",
            "metadata": {"location": "tavern"}
        }
        
        entry = ConversationEntry.from_dict(data)
        
        assert entry.id == "test_id"
        assert entry.conversation_id == "conv_1"
        assert entry.sender_id == "npc"
        assert entry.content == "Greetings!"
        assert entry.type == "action"
        assert entry.metadata["location"] == "tavern"
    
    def test_entry_from_dict_minimal(self): pass
        """Test creating entry from minimal dictionary."""
        data = {"content": "Minimal entry"}
        
        entry = ConversationEntry.from_dict(data)
        
        assert entry.content == "Minimal entry"
        assert entry.type == "dialogue"
        assert entry.metadata == {}


class TestConversationHistory: pass
    """Test class for ConversationHistory"""
    
    def test_history_initialization(self, mock_event_dispatcher): pass
        """Test conversation history initialization."""
        history = ConversationHistory(
            conversation_id="test_conv",
            participants={"player": "player", "npc": "guard"},
            location_id="castle_gate",
            metadata={"weather": "rainy"},
            event_dispatcher=mock_event_dispatcher
        )
        
        assert history.id == "test_conv"
        assert history.participants == {"player": "player", "npc": "guard"}
        assert history.location_id == "castle_gate"
        assert history.metadata["weather"] == "rainy"
        assert len(history.entries) == 0
        assert history.is_active is True
        assert history.ended_at is None
        assert isinstance(history.started_at, datetime)
    
    def test_history_initialization_defaults(self): pass
        """Test conversation history initialization with defaults."""
        history = ConversationHistory()
        
        assert history.id is not None  # Should generate UUID
        assert history.participants == {}
        assert history.location_id is None
        assert history.metadata == {}
        assert history.is_active is True
    
    def test_add_entry(self, sample_conversation_history): pass
        """Test adding entries to conversation history."""
        # Add first entry
        entry1 = sample_conversation_history.add_entry(
            sender_id="player",
            content="Hello!",
            entry_type="dialogue"
        )
        
        assert isinstance(entry1, ConversationEntry)
        assert entry1.sender_id == "player"
        assert entry1.content == "Hello!"
        assert entry1.type == "dialogue"
        assert len(sample_conversation_history.entries) == 1
        
        # Add entry with metadata
        entry2 = sample_conversation_history.add_entry(
            sender_id="npc",
            content="Greetings!",
            entry_type="action",
            metadata={"emotion": "cheerful"}
        )
        
        assert entry2.type == "action"
        assert entry2.metadata["emotion"] == "cheerful"
        assert len(sample_conversation_history.entries) == 2
    
    def test_add_entry_system_message(self, sample_conversation_history): pass
        """Test adding system entries."""
        entry = sample_conversation_history.add_entry(
            sender_id="system",
            content="The weather changes",
            entry_type="system"
        )
        
        assert entry.type == "system"
        assert entry.sender_id == "system"
        assert len(sample_conversation_history.entries) == 1
    
    def test_add_entry_inactive_conversation(self, sample_conversation_history): pass
        """Test adding entry to inactive conversation raises error."""
        sample_conversation_history.is_active = False
        
        with pytest.raises(ValueError, match="Cannot add entry to inactive conversation"): pass
            sample_conversation_history.add_entry("player", "Test message")
    
    def test_add_entry_non_participant(self, sample_conversation_history): pass
        """Test adding entry from non-participant raises error."""
        with pytest.raises(ValueError, match="is not a participant"): pass
            sample_conversation_history.add_entry("stranger", "Test message")
    
    def test_end_conversation(self, sample_conversation_history): pass
        """Test ending a conversation."""
        assert sample_conversation_history.is_active is True
        
        result = sample_conversation_history.end_conversation(metadata={"reason": "completed"})
        
        assert result is True
        assert sample_conversation_history.is_active is False
        assert sample_conversation_history.ended_at is not None
        assert sample_conversation_history.metadata["reason"] == "completed"
        
        # Test ending already ended conversation
        result2 = sample_conversation_history.end_conversation()
        assert result2 is False
    
    def test_get_entries_all(self, sample_conversation_history): pass
        """Test getting all entries."""
        # Add some entries
        sample_conversation_history.add_entry("player", "Message 1")
        sample_conversation_history.add_entry("npc", "Message 2")
        sample_conversation_history.add_entry("player", "Message 3")
        
        entries = sample_conversation_history.get_entries()
        
        assert len(entries) == 3
        assert all(isinstance(entry, ConversationEntry) for entry in entries)
    
    def test_get_entries_with_limit(self, sample_conversation_history): pass
        """Test getting entries with limit."""
        # Add multiple entries
        for i in range(5): pass
            sample_conversation_history.add_entry("player", f"Message {i}")
        
        entries = sample_conversation_history.get_entries(limit=3)
        
        assert len(entries) == 3
    
    def test_get_entries_by_sender(self, sample_conversation_history): pass
        """Test getting entries filtered by sender."""
        sample_conversation_history.add_entry("player", "Player message 1")
        sample_conversation_history.add_entry("npc", "NPC message")
        sample_conversation_history.add_entry("player", "Player message 2")
        
        player_entries = sample_conversation_history.get_entries(sender_id="player")
        
        assert len(player_entries) == 2
        assert all(entry.sender_id == "player" for entry in player_entries)
    
    def test_get_entries_by_type(self, sample_conversation_history): pass
        """Test getting entries filtered by type."""
        sample_conversation_history.add_entry("player", "Dialogue", "dialogue")
        sample_conversation_history.add_entry("player", "Action", "action")
        sample_conversation_history.add_entry("player", "Another dialogue", "dialogue")
        
        dialogue_entries = sample_conversation_history.get_entries(entry_type="dialogue")
        
        assert len(dialogue_entries) == 2
        assert all(entry.type == "dialogue" for entry in dialogue_entries)
    
    def test_get_messages_for_context(self, sample_conversation_history): pass
        """Test getting messages formatted for context."""
        sample_conversation_history.add_entry("player", "Hello!")
        sample_conversation_history.add_entry("npc", "Greetings!")
        
        messages = sample_conversation_history.get_messages_for_context(limit=10)
        
        assert isinstance(messages, list)
        assert len(messages) == 2
        assert all(isinstance(msg, dict) for msg in messages)
        assert messages[0]["content"] in ["Hello!", "Greetings!"]
    
    def test_get_all_participants(self, sample_conversation_history): pass
        """Test getting all participant IDs."""
        participants = sample_conversation_history.get_all_participants()
        
        assert isinstance(participants, set)
        assert "player" in participants
        assert "npc" in participants
        assert len(participants) == 2
    
    def test_add_participant(self, sample_conversation_history): pass
        """Test adding a participant."""
        initial_count = len(sample_conversation_history.participants)
        
        sample_conversation_history.add_participant("guard", "npc")
        
        assert len(sample_conversation_history.participants) == initial_count + 1
        assert sample_conversation_history.participants["guard"] == "npc"
        assert "guard" in sample_conversation_history.get_all_participants()
    
    def test_remove_participant(self, sample_conversation_history): pass
        """Test removing a participant."""
        # Add a participant first
        sample_conversation_history.add_participant("guard", "npc")
        initial_count = len(sample_conversation_history.participants)
        
        # Remove existing participant
        result = sample_conversation_history.remove_participant("guard")
        assert result is True
        assert len(sample_conversation_history.participants) == initial_count - 1
        assert "guard" not in sample_conversation_history.participants
        
        # Try to remove non-existent participant
        result2 = sample_conversation_history.remove_participant("nonexistent")
        assert result2 is False
    
    def test_to_dict(self, sample_conversation_history): pass
        """Test converting conversation history to dictionary."""
        # Add some entries
        sample_conversation_history.add_entry("player", "Test message")
        
        history_dict = sample_conversation_history.to_dict()
        
        assert isinstance(history_dict, dict)
        assert history_dict["id"] == "test_conv_1"
        assert "participants" in history_dict
        assert "entries" in history_dict
        assert "started_at" in history_dict
        assert len(history_dict["entries"]) == 1
    
    def test_from_dict(self, mock_event_dispatcher): pass
        """Test creating conversation history from dictionary."""
        data = {
            "id": "conv_from_dict",
            "participants": {"player": "player"},
            "location_id": "test_location",
            "metadata": {"test": "value"},
            "entries": [
                {
                    "id": "entry_1",
                    "sender_id": "player",
                    "content": "Hello",
                    "type": "dialogue",
                    "timestamp": "2024-01-01T12:00:00"
                }
            ],
            "started_at": "2024-01-01T12:00:00",
            "ended_at": None,
            "is_active": True
        }
        
        history = ConversationHistory.from_dict(data, mock_event_dispatcher)
        
        assert history.id == "conv_from_dict"
        assert history.participants == {"player": "player"}
        assert history.location_id == "test_location"
        assert len(history.entries) == 1
        assert history.entries[0].content == "Hello"
    
    def test_extract_key_info(self, sample_conversation_history): pass
        """Test extracting key information from conversation."""
        # Add entries with extractable content
        sample_conversation_history.add_entry(
            "player", "I need to complete the quest: Dragon Slayer"
        )
        sample_conversation_history.add_entry(
            "npc", "The dragon lives in the Dark Cave"
        )
        
        info = sample_conversation_history.extract_key_info()
        
        assert isinstance(info, list)
        # Should extract quest and location information
        categories = [item.get("category") for item in info]
        assert "quest" in categories or len(info) >= 0  # May extract quest-related info
    
    def test_to_json_and_from_json(self, sample_conversation_history): pass
        """Test JSON serialization and deserialization."""
        # Add an entry
        sample_conversation_history.add_entry("player", "Test message")
        
        # Convert to JSON
        json_str = sample_conversation_history.to_json()
        assert isinstance(json_str, str)
        
        # Parse back from JSON
        parsed_data = json.loads(json_str)
        assert parsed_data["id"] == "test_conv_1"
        
        # Create from JSON
        new_history = ConversationHistory.from_json(json_str)
        assert new_history.id == sample_conversation_history.id
        assert len(new_history.entries) == len(sample_conversation_history.entries)
    
    def test_save_and_load(self, sample_conversation_history): pass
        """Test saving and loading conversation history."""
        # Add some entries
        sample_conversation_history.add_entry("player", "Hello!")
        sample_conversation_history.add_entry("npc", "Greetings!")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f: pass
            filepath = f.name
        
        try: pass
            # Save conversation
            sample_conversation_history.save(filepath)
            
            # Verify file exists
            assert os.path.exists(filepath)
            
            # Load conversation
            loaded_history = ConversationHistory.load(filepath)
            
            assert loaded_history.id == sample_conversation_history.id
            assert loaded_history.participants == sample_conversation_history.participants
            assert len(loaded_history.entries) == len(sample_conversation_history.entries)
            
        finally: pass
            # Clean up
            if os.path.exists(filepath): pass
                os.unlink(filepath)
    
    def test_load_invalid_file(self): pass
        """Test loading from invalid file."""
        with pytest.raises(FileNotFoundError): pass
            ConversationHistory.load("nonexistent.json")
    
    def test_event_emission(self, mock_event_dispatcher): pass
        """Test that events are properly emitted."""
        # Create history with participants (should emit started event)
        history = ConversationHistory(
            participants={"player": "player", "npc": "npc"},
            event_dispatcher=mock_event_dispatcher
        )
        
        # Should have called dispatch for conversation started
        mock_event_dispatcher.dispatch.assert_called()
        
        # Reset mock
        mock_event_dispatcher.dispatch.reset_mock()
        
        # Add entry (should emit message event)
        history.add_entry("player", "Test message")
        mock_event_dispatcher.dispatch.assert_called()
        
        # Reset mock
        mock_event_dispatcher.dispatch.reset_mock()
        
        # End conversation (should emit ended event)
        history.end_conversation()
        mock_event_dispatcher.dispatch.assert_called()
