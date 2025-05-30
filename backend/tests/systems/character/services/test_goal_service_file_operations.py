import pytest
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.systems.character.services.goal_service import GoalService, parse_datetime
from backend.systems.character.models.goal import Goal, GoalType, GoalPriority, GoalStatus
from typing import Type


class TestGoalServiceFileOperations: pass
    """Tests for Goal Service file operations."""
    
    @pytest.fixture
    def temp_data_dir(self): pass
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Clean up after tests
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def goal_service(self, temp_data_dir): pass
        """Create a GoalService instance with a temporary data directory."""
        return GoalService(data_dir=temp_data_dir)
    
    def test_get_character_goal_file(self, goal_service): pass
        """Test the _get_character_goal_file method."""
        character_id = "test-character-123"
        file_path = goal_service._get_character_goal_file(character_id)
        expected_path = os.path.join(goal_service.data_dir, f"{character_id}_goals.json")
        assert file_path == expected_path
    
    def test_load_character_goals_no_file(self, goal_service): pass
        """Test _load_character_goals when the file doesn't exist."""
        character_id = "nonexistent-character"
        goals = goal_service._load_character_goals(character_id)
        assert goals == {}
    
    def test_load_character_goals_with_file(self, goal_service, temp_data_dir): pass
        """Test _load_character_goals when the file exists."""
        character_id = "test-character-456"
        file_path = os.path.join(temp_data_dir, f"{character_id}_goals.json")
        
        # Create test goal data
        now = datetime.utcnow()
        goal_data = {
            "goal1": {
                "goal_id": "goal1",
                "character_id": character_id,
                "description": "Test goal",
                "goal_type": GoalType.PERSONAL.value,
                "priority": GoalPriority.MEDIUM.value,
                "status": GoalStatus.ACTIVE.value,
                "metadata": {"test": "data"},
                "progress": 0.5,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "completed_at": None,
                "failure_reason": None
            }
        }
        
        # Write test data to file
        with open(file_path, "w") as f: pass
            json.dump(goal_data, f)
        
        # Load goals
        goals = goal_service._load_character_goals(character_id)
        
        # Verify loaded goals
        assert len(goals) == 1
        assert "goal1" in goals
        
        loaded_goal = goals["goal1"]
        assert loaded_goal.goal_id == "goal1"
        assert loaded_goal.character_id == character_id
        assert loaded_goal.description == "Test goal"
        assert loaded_goal.goal_type == GoalType.PERSONAL
        assert loaded_goal.priority == GoalPriority.MEDIUM
        assert loaded_goal.status == GoalStatus.ACTIVE
        assert loaded_goal.metadata == {"test": "data"}
        assert loaded_goal.progress == 0.5
    
    def test_load_character_goals_with_invalid_file(self, goal_service, temp_data_dir): pass
        """Test _load_character_goals with an invalid JSON file."""
        character_id = "test-character-invalid"
        file_path = os.path.join(temp_data_dir, f"{character_id}_goals.json")
        
        # Create invalid JSON file
        with open(file_path, "w") as f: pass
            f.write("This is not valid JSON")
        
        # Load goals - should handle error and return empty dict
        goals = goal_service._load_character_goals(character_id)
        assert goals == {}
    
    def test_save_character_goals(self, goal_service, temp_data_dir): pass
        """Test _save_character_goals method."""
        character_id = "test-character-789"
        
        # Create test goal
        goal = Goal(
            goal_id="goal2",
            character_id=character_id,
            description="Test goal for saving",
            goal_type=GoalType.PERSONAL,
            priority=GoalPriority.HIGH,
            status=GoalStatus.ACTIVE,
            metadata={"test": "save"}
        )
        goal.progress = 0.75
        
        # Add goal to service
        goal_service.goals[character_id] = {goal.goal_id: goal}
        
        # Save goals
        result = goal_service._save_character_goals(character_id)
        assert result is True
        
        # Verify file was created
        file_path = os.path.join(temp_data_dir, f"{character_id}_goals.json")
        assert os.path.exists(file_path)
        
        # Verify file contents
        with open(file_path, "r") as f: pass
            data = json.load(f)
            assert goal.goal_id in data
            assert "character_id" in data[goal.goal_id]
            assert data[goal.goal_id]["character_id"] == character_id
            assert data[goal.goal_id]["description"] == "Test goal for saving"
            assert data[goal.goal_id]["goal_type"] == GoalType.PERSONAL.value
            assert data[goal.goal_id]["priority"] == GoalPriority.HIGH.value
            assert data[goal.goal_id]["progress"] == 0.75
    
    def test_save_character_goals_with_error(self, goal_service): pass
        """Test _save_character_goals with an error during saving."""
        character_id = "test-character-error"
        
        # Add goal to service
        goal = Goal(
            goal_id="goal3",
            character_id=character_id,
            description="Test goal for error handling",
            goal_type=GoalType.PERSONAL,
            priority=GoalPriority.MEDIUM
        )
        goal_service.goals[character_id] = {goal.goal_id: goal}
        
        # Mock open to raise an exception
        with patch("builtins.open", side_effect=Exception("Test error")): pass
            result = goal_service._save_character_goals(character_id)
            assert result is False
    
    def test_save_character_goals_no_goals(self, goal_service): pass
        """Test _save_character_goals when no goals exist for the character."""
        character_id = "nonexistent-character"
        # Character doesn't exist in goal_service.goals
        result = goal_service._save_character_goals(character_id)
        assert result is False
    
    def test_parse_datetime(self): pass
        """Test the parse_datetime helper function."""
        # Test with valid datetime string
        dt_str = "2023-05-15T12:30:45.123456"
        result = parse_datetime(dt_str)
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 5
        assert result.day == 15
        assert result.hour == 12
        assert result.minute == 30
        assert result.second == 45
        
        # Test with None input
        assert parse_datetime(None) is None
        
        # Test with invalid datetime string
        assert parse_datetime("not a datetime") is None 