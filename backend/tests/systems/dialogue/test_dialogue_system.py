"""
Tests for backend.systems.dialogue.dialogue_system

Comprehensive tests for the core dialogue system functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import uuid
from datetime import datetime
import json
import tempfile
import os

# Import the module being tested
try: pass
    from backend.systems.dialogue.dialogue_system import (
        Conversation, 
        DialogueSystem,
        get_dialogue_system
    )
    from backend.systems.dialogue.utils import clean_text_for_dialogue, count_tokens
except ImportError as e: pass
    pytest.skip(f"Could not import dialogue_system: {e}", allow_module_level=True)


class TestConversation: pass
    """Test class for Conversation functionality."""
    
    @pytest.fixture
    def sample_participants(self): pass
        return {"player_1": "player", "npc_1": "npc"}
    
    @pytest.fixture
    def conversation(self, sample_participants): pass
        return Conversation(
            conversation_id="test_conv_1",
            participants=sample_participants,
            location_id="test_location",
            metadata={"context": "test"}
        )
    
    def test_conversation_initialization(self, sample_participants): pass
        """Test conversation initialization with all parameters."""
        conv = Conversation(
            conversation_id="test_conv",
            participants=sample_participants,
            location_id="location_1",
            metadata={"test": "data"},
            max_tokens=1024,
            max_messages=25
        )
        
        assert conv.id == "test_conv"
        assert conv.participants == sample_participants
        assert conv.location_id == "location_1"
        assert conv.metadata == {"test": "data"}
        assert conv.max_tokens == 1024
        assert conv.max_messages == 25
        assert conv.active is True
        assert conv.messages == []
    
    def test_conversation_initialization_defaults(self): pass
        """Test conversation initialization with defaults."""
        conv = Conversation()
        
        assert conv.id is not None
        assert isinstance(conv.id, str)
        assert conv.participants == {}
        assert conv.location_id is None
        assert conv.metadata == {}
        assert conv.max_tokens == 2048
        assert conv.max_messages == 50
        assert conv.active is True
    
    def test_add_message_success(self, conversation): pass
        """Test adding a message successfully."""
        message = conversation.add_message(
            sender_id="player_1",
            content="Hello there!",
            message_type="dialogue",
            metadata={"emotion": "friendly"}
        )
        
        assert message is not None
        assert message["sender_id"] == "player_1"
        assert message["content"] == "Hello there!"
        assert message["type"] == "dialogue"
        assert message["metadata"]["emotion"] == "friendly"
        assert message["conversation_id"] == conversation.id
        assert len(conversation.messages) == 1
    
    def test_add_message_inactive_conversation(self, conversation): pass
        """Test adding message to inactive conversation."""
        conversation.active = False
        
        message = conversation.add_message(
            sender_id="player_1",
            content="Hello"
        )
        
        assert message is None
        assert len(conversation.messages) == 0
    
    def test_add_message_non_participant(self, conversation): pass
        """Test adding message from non-participant."""
        message = conversation.add_message(
            sender_id="unknown_user",
            content="Hello"
        )
        
        assert message is None
        assert len(conversation.messages) == 0
    
    def test_add_system_message_success(self, conversation): pass
        """Test adding system message bypasses participant check."""
        message = conversation.add_message(
            sender_id="system",
            content="Game event occurred",
            message_type="system"
        )
        
        assert message is not None
        assert message["type"] == "system"
        assert len(conversation.messages) == 1
    
    def test_get_context_default(self, conversation): pass
        """Test getting conversation context with defaults."""
        # Add some messages
        conversation.add_message("player_1", "Hello")
        conversation.add_message("npc_1", "Hi there!")
        
        context = conversation.get_context()
        
        assert "recent_messages" in context
        assert "messages" in context  # backward compatibility
        assert len(context["recent_messages"]) == 2
    
    @patch('backend.systems.dialogue.dialogue_system.relevance_score')
    @patch('backend.systems.dialogue.dialogue_system.count_tokens')
    def test_get_context_with_scoring(self, mock_count_tokens, mock_relevance_score, conversation): pass
        """Test getting context with relevance scoring."""
        mock_count_tokens.return_value = 10
        mock_relevance_score.side_effect = [0.8, 0.9]  # Second message has higher score
        
        conversation.add_message("player_1", "First message")
        conversation.add_message("npc_1", "Second message")
        
        context = conversation.get_context(use_scoring=True, by_tokens=True)
        
        assert len(context["recent_messages"]) == 2
        # Should be sorted by relevance score (higher first)
        assert context["recent_messages"][0]["content"] == "Second message"
        assert context["recent_messages"][1]["content"] == "First message"
    
    @patch('backend.systems.dialogue.dialogue_system.count_tokens')
    def test_get_context_token_limit(self, mock_count_tokens, conversation): pass
        """Test context limiting by token count."""
        # Disable cache to avoid interference
        conversation.cache = None
        
        # Set up token counts: first message fits, second message would exceed limit
        # Messages are processed in reverse order (most recent first)
        mock_count_tokens.side_effect = [40, 60]  # 40 + 60 = 100 > 80 limit
        conversation.max_tokens = 80  # Set limit so second message can't be added
        
        conversation.add_message("player_1", "First message")   # 40 tokens
        conversation.add_message("npc_1", "Second message")     # 60 tokens
        
        context = conversation.get_context(use_scoring=False, by_tokens=True)
        
        # Should only include the most recent message (60 tokens) since it fits alone
        # but both together would exceed the limit
        assert len(context["recent_messages"]) == 1
        assert context["recent_messages"][0]["content"] == "Second message"
    
    def test_get_context_message_limit(self, conversation): pass
        """Test context limiting by message count."""
        conversation.max_messages = 2
        
        conversation.add_message("player_1", "Message 1")
        conversation.add_message("npc_1", "Message 2")
        conversation.add_message("player_1", "Message 3")
        
        context = conversation.get_context(use_scoring=False, by_tokens=False)
        
        # Should only include last 2 messages
        assert len(context["recent_messages"]) == 2
        assert context["recent_messages"][0]["content"] == "Message 3"
        assert context["recent_messages"][1]["content"] == "Message 2"
    
    @patch('backend.systems.dialogue.dialogue_system.extract_key_info')
    def test_extract_information(self, mock_extract_key_info, conversation): pass
        """Test extracting information from conversation."""
        mock_extract_key_info.return_value = [
            {"type": "location", "value": "tavern"},
            {"type": "person", "value": "merchant"}
        ]
        
        message = conversation.add_message("player_1", "I met a merchant at the tavern")
        
        info = conversation.extract_information()
        
        assert len(info) == 2
        assert info[0]["message_id"] == message["id"]
        assert info[0]["sender_id"] == "player_1"
        assert info[0]["type"] == "location"
        assert info[1]["type"] == "person"
    
    def test_end_conversation_success(self, conversation): pass
        """Test ending an active conversation."""
        result = conversation.end_conversation()
        
        assert result is True
        assert conversation.active is False
        assert "ended_at" in conversation.context
    
    def test_end_conversation_already_inactive(self, conversation): pass
        """Test ending an already inactive conversation."""
        conversation.active = False
        
        result = conversation.end_conversation()
        
        assert result is False
    
    def test_is_active(self, conversation): pass
        """Test checking if conversation is active."""
        assert conversation.is_active() is True
        
        conversation.active = False
        assert conversation.is_active() is False
    
    def test_add_to_context(self, conversation): pass
        """Test adding data to conversation context."""
        conversation.add_to_context("mood", "friendly")
        
        assert conversation.context["mood"] == "friendly"
    
    def test_add_participant(self, conversation): pass
        """Test adding a participant."""
        conversation.add_participant("npc_2", "merchant")
        
        assert "npc_2" in conversation.participants
        assert conversation.participants["npc_2"] == "merchant"
        assert conversation.context["participants"] == conversation.participants
    
    def test_remove_participant_success(self, conversation): pass
        """Test removing an existing participant."""
        result = conversation.remove_participant("npc_1")
        
        assert result is True
        assert "npc_1" not in conversation.participants
    
    def test_remove_participant_not_found(self, conversation): pass
        """Test removing a non-existent participant."""
        result = conversation.remove_participant("unknown_user")
        
        assert result is False
    
    def test_get_all_participants(self, conversation): pass
        """Test getting all participant IDs."""
        participants = conversation.get_all_participants()
        
        assert participants == {"player_1", "npc_1"}
    
    def test_save_and_load_conversation(self, conversation): pass
        """Test saving and loading conversation."""
        # Add some data
        conversation.add_message("player_1", "Test message")
        conversation.add_to_context("test_key", "test_value")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f: pass
            filepath = f.name
        
        try: pass
            conversation.save(filepath)
            
            # Load conversation
            loaded_conv = Conversation.load(filepath)
            
            assert loaded_conv.id == conversation.id
            assert loaded_conv.participants == conversation.participants
            assert loaded_conv.location_id == conversation.location_id
            assert loaded_conv.metadata == conversation.metadata
            assert len(loaded_conv.messages) == 1
            assert loaded_conv.context["test_key"] == "test_value"
        finally: pass
            os.unlink(filepath)
    
    def test_clear_cache(self, conversation): pass
        """Test clearing conversation cache."""
        mock_cache = Mock()
        conversation.cache = mock_cache
        
        conversation.clear_cache()
        
        mock_cache.clear_conversation_data.assert_called_once_with(conversation.id)


class TestDialogueSystem: pass
    """Test class for DialogueSystem functionality."""
    
    @pytest.fixture
    def dialogue_system(self): pass
        """Create a fresh DialogueSystem instance for testing."""
        return DialogueSystem()
    
    def test_singleton_pattern(self): pass
        """Test that DialogueSystem follows singleton pattern."""
        system1 = DialogueSystem.get_instance()
        system2 = DialogueSystem.get_instance()
        
        assert system1 is system2
    
    def test_initialization_with_integrations(self): pass
        """Test DialogueSystem initialization with integration modules."""
        mock_memory = Mock()
        mock_analytics = Mock()
        
        system = DialogueSystem(
            memory_integration=mock_memory,
            analytics_integration=mock_analytics
        )
        
        assert system.memory_integration is mock_memory
        assert system.analytics_integration is mock_analytics
    
    def test_start_conversation(self, dialogue_system): pass
        """Test starting a new conversation."""
        participants = {"player_1": "player", "npc_1": "npc"}
        
        conv_id = dialogue_system.start_conversation(
            participants=participants,
            location_id="tavern",
            metadata={"context": "quest"}
        )
        
        assert conv_id is not None
        assert conv_id in dialogue_system.conversations
        
        conv = dialogue_system.conversations[conv_id]
        assert conv.participants == participants
        assert conv.location_id == "tavern"
        assert conv.metadata == {"context": "quest"}
    
    def test_end_conversation_success(self, dialogue_system): pass
        """Test ending an existing conversation."""
        conv_id = dialogue_system.start_conversation({"player_1": "player"})
        
        result = dialogue_system.end_conversation(conv_id)
        
        assert result is True
        assert not dialogue_system.conversations[conv_id].is_active()
    
    def test_end_conversation_not_found(self, dialogue_system): pass
        """Test ending a non-existent conversation."""
        result = dialogue_system.end_conversation("non_existent_id")
        
        assert result is False
    
    def test_add_message_to_conversation_success(self, dialogue_system): pass
        """Test adding message to existing conversation."""
        conv_id = dialogue_system.start_conversation({"player_1": "player"})
        
        message = dialogue_system.add_message_to_conversation(
            conversation_id=conv_id,
            sender_id="player_1",
            content="Hello!",
            message_type="dialogue"
        )
        
        assert message is not None
        assert message["content"] == "Hello!"
        assert len(dialogue_system.conversations[conv_id].messages) == 1
    
    def test_add_message_conversation_not_found(self, dialogue_system): pass
        """Test adding message to non-existent conversation."""
        message = dialogue_system.add_message_to_conversation(
            conversation_id="non_existent",
            sender_id="player_1",
            content="Hello!"
        )
        
        assert message is None
    
    @patch('backend.systems.dialogue.dialogue_system.logger')
    def test_generate_response_no_language_generator(self, mock_logger, dialogue_system): pass
        """Test generating response without language generator."""
        # Ensure no language generator is set
        dialogue_system.language_generator = None
        
        conv_id = dialogue_system.start_conversation({"player_1": "player", "npc_1": "npc"})
        
        response = dialogue_system.generate_response(
            conversation_id=conv_id,
            responder_id="npc_1"
        )
        
        # Should generate a default response and log a warning
        assert response is not None
        assert "DEFAULT RESPONSE" in response["content"]
        assert response["sender_id"] == "npc_1"
        mock_logger.warning.assert_called()
    
    def test_generate_response_conversation_not_found(self, dialogue_system): pass
        """Test generating response for non-existent conversation."""
        response = dialogue_system.generate_response(
            conversation_id="non_existent",
            responder_id="npc_1"
        )
        
        assert response is None
    
    def test_get_conversation_success(self, dialogue_system): pass
        """Test getting an existing conversation."""
        conv_id = dialogue_system.start_conversation({"player_1": "player"})
        
        conv = dialogue_system.get_conversation(conv_id)
        
        assert conv is not None
        assert conv.id == conv_id
    
    def test_get_conversation_not_found(self, dialogue_system): pass
        """Test getting a non-existent conversation."""
        conv = dialogue_system.get_conversation("non_existent")
        
        assert conv is None
    
    def test_get_active_conversations(self, dialogue_system): pass
        """Test getting list of active conversations."""
        conv_id1 = dialogue_system.start_conversation({"player_1": "player"})
        conv_id2 = dialogue_system.start_conversation({"player_2": "player"})
        conv_id3 = dialogue_system.start_conversation({"player_3": "player"})
        
        # End one conversation
        dialogue_system.end_conversation(conv_id2)
        
        active_convs = dialogue_system.get_active_conversations()
        
        assert len(active_convs) == 2
        assert conv_id1 in active_convs
        assert conv_id3 in active_convs
        assert conv_id2 not in active_convs
    
    def test_enhance_context_with_integrations(self, dialogue_system): pass
        """Test context enhancement with integration modules."""
        # Setup mock integrations
        mock_memory = Mock()
        mock_memory.get_memories_for_dialogue.return_value = {"memory": "data"}
        dialogue_system.memory_integration = mock_memory
        
        mock_faction = Mock()
        mock_faction.get_faction_context_for_dialogue.return_value = {"faction": "data"}
        dialogue_system.faction_integration = mock_faction
        
        context = {"base": "context", "location_id": "test_location"}
        enhanced = dialogue_system._enhance_context_with_integrations(context, "npc_1")
        
        assert enhanced["memories"] == {"memory": "data"}
        assert enhanced["factions"] == {"faction": "data"}
        assert enhanced["base"] == "context"


def test_get_dialogue_system(): pass
    """Test the get_dialogue_system function."""
    system = get_dialogue_system()
    
    assert isinstance(system, DialogueSystem)
    
    # Should return the same instance (singleton)
    system2 = get_dialogue_system()
    assert system is system2
