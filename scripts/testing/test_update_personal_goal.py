#!/usr/bin/env python
"""
Simple script to test the update_personal_goal_progress method

NOTE: This is a manual test script used for debugging the character service,
      not an actual test file that should be part of the test suite.
      It was created to verify the fix for update_personal_goal_progress
      without requiring the full test infrastructure.
"""

from unittest.mock import MagicMock, patch
import sys
import os
import types

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Mock the problematic imports
sys.modules['backend.systems.analytics'] = MagicMock()
sys.modules['backend.systems.analytics.services'] = MagicMock()
sys.modules['backend.systems.analytics.services.analytics_service'] = MagicMock()
sys.modules['backend.infrastructure.shared.database'] = MagicMock()
sys.modules['backend.infrastructure.shared.database.database_objects'] = MagicMock()
sys.modules['backend.systems.world_state.world_state_manager'] = MagicMock()
sys.modules['backend.systems.world_state'] = MagicMock()

# Create a mock for the world state manager
mock_world_state_manager = MagicMock()
mock_world_state_manager.get_instance.return_value = mock_world_state_manager
sys.modules['backend.systems.world_state.world_state_manager'].WorldStateManager = mock_world_state_manager

# Setup db mock
mock_db = MagicMock()
sys.modules['backend.infrastructure.shared.database.database_objects'].db = mock_db

# Setup get_db_session mock to return a fake session
mock_session = MagicMock()
mock_get_db_session = MagicMock()
mock_get_db_session.return_value = iter([mock_session])
sys.modules['backend.infrastructure.shared.database'].get_db_session = mock_get_db_session

# Import our module
from backend.systems.character.services.character_service import CharacterService
from backend.systems.character.models.goal import GoalType
from backend.infrastructure.events import GoalProgressUpdated

# Extract the update_personal_goal_progress method directly from the CharacterService class
# This is a trick to test the method in isolation without instantiating the class
update_personal_goal_progress = CharacterService.update_personal_goal_progress

def test_update_personal_goal_progress():
    """Test updating personal goal progress"""
    # Create mock objects
    mock_self = MagicMock()
    mock_self.goal_service = MagicMock()
    mock_self.event_dispatcher = MagicMock()
    
    # Create mock character
    mock_character = MagicMock()
    mock_character.character_id = "test_character_id"
    mock_character.level = 5
    mock_character.name = "Test Character"
    
    # Create mock goal
    mock_goal = MagicMock()
    mock_goal.goal_id = "test_goal_id"
    mock_goal.goal_type = GoalType.PERSONAL
    mock_goal.progress = 0.3
    
    # Configure the goal service
    mock_self.goal_service.update_goal_progress.return_value = mock_goal
    
    # Call the method directly
    result = update_personal_goal_progress(mock_self, mock_character, mock_goal)
    
    # Verify goal progress was updated
    mock_self.goal_service.update_goal_progress.assert_called_once()
    call_args = mock_self.goal_service.update_goal_progress.call_args[0]
    assert call_args[0] == "test_character_id"
    assert call_args[1] == "test_goal_id"
    assert call_args[2] == 0.5  # Progress should be level/10
    
    # Verify event was dispatched
    mock_self.event_dispatcher.dispatch.assert_called_once()
    
    print("Test passed successfully!")
    return True


def test_update_personal_goal_progress_with_level_progress():
    """Test updating personal goal progress based on character level."""
    # Create mock objects
    mock_self = MagicMock()
    mock_self.goal_service = MagicMock()
    mock_self.event_dispatcher = MagicMock()
    
    # Configure mock character
    mock_character = MagicMock()
    mock_character.character_id = "test_character_id"
    mock_character.level = 8  # High level to ensure significant progress
    mock_character.name = "Test Character"
    
    # Configure mock goal
    mock_goal = MagicMock()
    mock_goal.goal_id = "test_goal_id"
    mock_goal.goal_type = GoalType.PERSONAL
    mock_goal.progress = 0.5  # Starting at 50% progress
    
    # Configure goal service to return our mock goal
    mock_self.goal_service.update_goal_progress.return_value = mock_goal
    
    # Call the method directly
    result = update_personal_goal_progress(mock_self, mock_character, mock_goal)
    
    # Verify goal progress was updated
    mock_self.goal_service.update_goal_progress.assert_called_once()
    
    # Check positional args
    call_args = mock_self.goal_service.update_goal_progress.call_args[0]
    assert call_args[0] == "test_character_id"
    assert call_args[1] == "test_goal_id"
    assert call_args[2] == 0.8  # Progress should be level/10 = 8/10 = 0.8
    
    # Verify event was dispatched
    mock_self.event_dispatcher.dispatch.assert_called_once()
    
    print("Test with level progress passed successfully!")
    return True


if __name__ == "__main__":
    test_update_personal_goal_progress()
    test_update_personal_goal_progress_with_level_progress()
    print("All tests passed!") 