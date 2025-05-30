"""
Test suite for npc_rumor_utils module.
Tests utility functions for handling NPC rumors and gossip mechanics.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from backend.systems.rumor.utils import (
    sync_event_beliefs,
    generate_rumor,
    spread_rumor
)


def test_sync_event_beliefs():
    """Test synchronizing event beliefs with NPCs in a region."""
    # Arrange
    region = "test_region"
    event = {
        "event_id": "event_123",
        "description": "A test event",
        "type": "battle",
        "location": "town_square"
    }
    
    # Act
    with patch("backend.systems.character.npc.npc_rumor_utils.logger") as mock_logger:
        result = sync_event_beliefs(region, event)
    
    # Assert
    assert isinstance(result, int)
    mock_logger.info.assert_called_once()
    # Verify the log message contains both the region and event ID
    log_message = mock_logger.info.call_args[0][0]
    assert region in log_message
    assert event["event_id"] in log_message


def test_generate_rumor():
    """Test generating a rumor from an NPC."""
    # Arrange
    npc_id = "npc_123"
    topic = "politics"
    
    # Act
    with patch("random.choice", side_effect=lambda x: x[0]): pass
        rumor = generate_rumor(npc_id, topic)
    
    # Assert
    assert rumor is not None
    assert "content" in rumor
    assert "source_npc" in rumor
    assert "timestamp" in rumor
    assert "reliability" in rumor
    
    assert rumor["source_npc"] == npc_id
    assert isinstance(rumor["timestamp"], datetime)
    assert 0 <= rumor["reliability"] <= 1
    
    # The content should be formatted from the template
    assert "{target}" not in rumor["content"]
    assert "{action}" not in rumor["content"]
    assert "{location}" not in rumor["content"]


def test_generate_rumor_with_exception():
    """Test error handling when generating a rumor."""
    # Arrange
    npc_id = "npc_123"
    
    # Act
    with patch("random.choice", side_effect=Exception("Test error")), \
         patch("backend.systems.character.npc.npc_rumor_utils.logger") as mock_logger:
        rumor = generate_rumor(npc_id)
    
    # Assert
    assert rumor is None
    mock_logger.error.assert_called_once()
    assert "Error generating rumor" in mock_logger.error.call_args[0][0]


def test_spread_rumor_success():
    """Test successfully spreading a rumor to target NPCs."""
    # Arrange
    rumor_data = {
        "content": "Test rumor content",
        "source_npc": "npc_123",
        "timestamp": datetime.utcnow(),
        "reliability": 0.75
    }
    target_npcs = ["npc_456", "npc_789", "npc_101"]
    
    # Act
    with patch("backend.systems.character.npc.npc_rumor_utils.logger") as mock_logger:
        result = spread_rumor(rumor_data, target_npcs)
    
    # Assert
    assert result is True
    mock_logger.info.assert_called_once()
    # Verify the log message contains the number of target NPCs
    log_message = mock_logger.info.call_args[0][0]
    assert str(len(target_npcs)) in log_message


def test_spread_rumor_empty_targets():
    """Test spreading a rumor with no target NPCs."""
    # Arrange
    rumor_data = {
        "content": "Test rumor content",
        "source_npc": "npc_123",
        "timestamp": datetime.utcnow(),
        "reliability": 0.75
    }
    target_npcs = []
    
    # Act
    with patch("backend.systems.character.npc.npc_rumor_utils.logger") as mock_logger:
        result = spread_rumor(rumor_data, [])
    
    # Assert
    assert result is True
    mock_logger.info.assert_called_once()
    # Verify the log message indicates 0 targets
    log_message = mock_logger.info.call_args[0][0]
    assert "0" in log_message


def test_spread_rumor_with_exception():
    """Test error handling when spreading a rumor."""
    # Arrange
    rumor_data = {
        "content": "Test rumor content",
        "source_npc": "npc_123",
        "timestamp": datetime.utcnow(),
        "reliability": 0.75
    }
    target_npcs = ["npc_456", "npc_789"]
    
    # Act
    with patch("backend.systems.character.npc.npc_rumor_utils.logger") as mock_logger, \
         patch("backend.systems.character.npc.npc_rumor_utils.logger.info", side_effect=Exception("Test error")):
        result = spread_rumor(rumor_data, target_npcs)
    
    # Assert
    assert result is False
    mock_logger.error.assert_called_once()
    assert "Error spreading rumor" in mock_logger.error.call_args[0][0] 