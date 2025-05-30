"""
Tests for the canonical dialogue system.

This file has been updated to test the canonical DialogueSystem
instead of the deprecated DialogueManager.
"""

import pytest
from datetime import datetime
import tempfile
import os

from backend.systems.dialogue import (
    get_dialogue_system,
    create_conversation,
    DialogueSystem,
    Conversation,
)
from backend.systems.dialogue.conversation import ConversationHistory, ConversationEntry
from backend.systems.dialogue.cache import DialogueCache
from backend.systems.dialogue.utils import (
    count_tokens,
    relevance_score,
    extract_key_info,
)


@pytest.fixture
def dialogue_system():
    """Fixture to provide a fresh DialogueSystem instance for each test."""
    # Reset singleton for testing
    DialogueSystem._instance = None
    return get_dialogue_system()


@pytest.fixture
def test_conversation(dialogue_system):
    """Fixture to provide a test conversation."""
    conversation_id = create_conversation(
        participants={"player": "player", "npc": "npc"}, location_id="test_location"
    )
    return conversation_id


def test_dialogue_system_initialization(dialogue_system):
    """Test that DialogueSystem initializes correctly."""
    assert isinstance(dialogue_system, DialogueSystem)
    assert dialogue_system.conversations == {}


def test_create_conversation(dialogue_system):
    """Test creating a conversation with DialogueSystem."""
    conversation_id = create_conversation(
        participants={"player": "player", "npc": "npc"}, location_id="test_location"
    )

    assert conversation_id is not None
    assert conversation_id in dialogue_system.conversations

    conversation = dialogue_system.get_conversation(conversation_id)
    assert isinstance(conversation, Conversation)
    assert conversation.participants == {"player": "player", "npc": "npc"}
    assert conversation.location_id == "test_location"


def test_add_message_to_conversation(dialogue_system, test_conversation):
    """Test adding messages to a conversation."""
    conversation_id = test_conversation

    # Add first message
    message1 = dialogue_system.add_message_to_conversation(
        conversation_id=conversation_id, sender_id="player", content="Hello there!"
    )

    # Add second message
    message2 = dialogue_system.add_message_to_conversation(
        conversation_id=conversation_id, sender_id="npc", content="Greetings, traveler!"
    )

    conversation = dialogue_system.get_conversation(conversation_id)
    assert len(conversation.messages) == 2
    assert conversation.messages[0]["sender_id"] == "player"
    assert conversation.messages[0]["content"] == "Hello there!"
    assert conversation.messages[1]["sender_id"] == "npc"
    assert conversation.messages[1]["content"] == "Greetings, traveler!"


def test_conversation_get_context(dialogue_system, test_conversation):
    """Test getting context from a conversation."""
    conversation_id = test_conversation

    dialogue_system.add_message_to_conversation(
        conversation_id=conversation_id, sender_id="player", content="Hello there!"
    )
    dialogue_system.add_message_to_conversation(
        conversation_id=conversation_id, sender_id="npc", content="Greetings, traveler!"
    )

    conversation = dialogue_system.get_conversation(conversation_id)
    context = conversation.get_context(use_scoring=False)

    assert isinstance(context, dict)
    assert "messages" in context
    assert len(context["messages"]) == 2


def test_conversation_extract_information(dialogue_system, test_conversation):
    """Test extracting information from a conversation."""
    conversation_id = test_conversation

    dialogue_system.add_message_to_conversation(
        conversation_id=conversation_id,
        sender_id="player",
        content="I need to complete the quest: Dragon Slayer",
    )
    dialogue_system.add_message_to_conversation(
        conversation_id=conversation_id,
        sender_id="npc",
        content="The reward for that quest is 500 gold",
    )

    conversation = dialogue_system.get_conversation(conversation_id)
    info = conversation.extract_information()

    # Check that information was extracted (exact format may vary)
    assert isinstance(info, list)


def test_conversation_save_load(dialogue_system, test_conversation):
    """Test saving and loading conversation data."""
    conversation_id = test_conversation

    dialogue_system.add_message_to_conversation(
        conversation_id=conversation_id, sender_id="player", content="Hello there!"
    )
    dialogue_system.add_message_to_conversation(
        conversation_id=conversation_id, sender_id="npc", content="Greetings, traveler!"
    )

    conversation = dialogue_system.get_conversation(conversation_id)

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        filepath = temp.name

    try:
        conversation.save(filepath)

        # Load conversation from file
        loaded_conversation = Conversation.load(filepath)

        # Verify the conversation was loaded correctly
        assert len(loaded_conversation.messages) == 2
        assert loaded_conversation.messages[0]["sender_id"] == "player"
        assert loaded_conversation.messages[0]["content"] == "Hello there!"
        assert loaded_conversation.messages[1]["sender_id"] == "npc"
        assert loaded_conversation.messages[1]["content"] == "Greetings, traveler!"
    finally
        # Clean up the temporary file
        os.unlink(filepath)


def test_conversation_cache_functionality(dialogue_system, test_conversation):
    """Test that conversation caching works correctly."""
    conversation_id = test_conversation

    dialogue_system.add_message_to_conversation(
        conversation_id=conversation_id, sender_id="player", content="Hello there!"
    )

    conversation = dialogue_system.get_conversation(conversation_id)

    # First call should compute the context
    context1 = conversation.get_context()

    # Second call should potentially use cache (implementation detail)
    context2 = conversation.get_context()

    # Both contexts should be equivalent
    assert context1.keys() == context2.keys()

    # Clear cache and verify it's recomputed
    conversation.clear_cache()
    context3 = conversation.get_context()
    assert context3.keys() == context1.keys()


def test_generate_response(dialogue_system, test_conversation):
    """Test generating a response using the dialogue system."""
    conversation_id = test_conversation

    dialogue_system.add_message_to_conversation(
        conversation_id=conversation_id, sender_id="player", content="Hello there!"
    )

    # Generate a response (this uses the stub language generator)
    response = dialogue_system.generate_response(
        conversation_id=conversation_id, responder_id="npc"
    )

    assert response is not None
    assert "content" in response
    assert response["type"] == "dialogue"


def test_end_conversation(dialogue_system, test_conversation):
    """Test ending a conversation."""
    conversation_id = test_conversation

    # Conversation should be active initially
    conversation = dialogue_system.get_conversation(conversation_id)
    assert conversation.is_active()

    # End the conversation
    success = dialogue_system.end_conversation(conversation_id)
    assert success

    # Conversation should no longer be active
    assert not conversation.is_active()
