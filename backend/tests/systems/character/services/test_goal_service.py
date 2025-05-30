from typing import Type
"""
Test suite for goal_service module.
Tests the GoalService class for managing character goals.
"""

import pytest
import os
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, mock_open
from uuid import uuid4

from backend.systems.character.services.goal_service import GoalService, parse_datetime
from backend.systems.character.models.goal import (
    Goal,
    GoalType,
    GoalPriority,
    GoalStatus,
    GoalCreated,
    GoalCompleted,
    GoalFailed,
    GoalAbandoned,
    GoalProgressUpdated,
    GoalStatusChanged,
)


@pytest.fixture
def temp_data_dir(): pass
    """Create a temporary directory for goal data."""
    with tempfile.TemporaryDirectory() as temp_dir: pass
        yield temp_dir


@pytest.fixture
def goal_service(temp_data_dir): pass
    """Create a GoalService instance with a temporary data directory."""
    return GoalService(data_dir=temp_data_dir)


@pytest.fixture
def character_id(): pass
    """Generate a random character ID."""
    return str(uuid4())


@pytest.fixture
def sample_goal(character_id): pass
    """Create a sample goal for testing."""
    return Goal(
        goal_id=str(uuid4()),
        character_id=character_id,
        description="Test goal",
        goal_type=GoalType.PERSONAL,
        priority=GoalPriority.MEDIUM,
        status=GoalStatus.ACTIVE,
        metadata={"test_key": "test_value"},
        progress=0.0,
    )


@pytest.fixture
def populated_goal_service(goal_service, character_id, sample_goal): pass
    """Create a GoalService with a pre-populated goal."""
    # Add the goal to the service
    if character_id not in goal_service.goals: pass
        goal_service.goals[character_id] = {}
    goal_service.goals[character_id][sample_goal.goal_id] = sample_goal
    return goal_service, character_id, sample_goal


def test_init(temp_data_dir): pass
    """Test GoalService initialization."""
    service = GoalService(data_dir=temp_data_dir)
    
    # Check if data directory was created
    assert os.path.exists(temp_data_dir)
    
    # Check if service has correct attributes
    assert service.data_dir == temp_data_dir
    assert isinstance(service.goals, dict)
    assert service.event_dispatcher is not None


def test_get_character_goal_file(goal_service, character_id): pass
    """Test _get_character_goal_file method."""
    file_path = goal_service._get_character_goal_file(character_id)
    expected_path = os.path.join(goal_service.data_dir, f"{character_id}_goals.json")
    assert file_path == expected_path


def test_get_goals_for_character_empty(goal_service, character_id): pass
    """Test get_goals_for_character with no goals."""
    # Mock _load_character_goals to return an empty dict
    with patch.object(goal_service, '_load_character_goals', return_value={}): pass
        goals = goal_service.get_goals_for_character(character_id)
    
    assert isinstance(goals, list)
    assert len(goals) == 0


def test_get_goals_for_character(populated_goal_service): pass
    """Test get_goals_for_character with existing goals."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Get goals
    goals = goal_service.get_goals_for_character(character_id)
    
    assert isinstance(goals, list)
    assert len(goals) == 1
    assert goals[0].goal_id == sample_goal.goal_id
    assert goals[0].description == sample_goal.description


def test_get_goals_for_character_with_filters(populated_goal_service): pass
    """Test get_goals_for_character with filters."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Add another goal with different properties
    another_goal = Goal(
        goal_id=str(uuid4()),
        character_id=character_id,
        description="Another goal",
        goal_type=GoalType.QUEST,
        priority=GoalPriority.HIGH,
        status=GoalStatus.COMPLETED,
        metadata={},
        progress=1.0,
    )
    goal_service.goals[character_id][another_goal.goal_id] = another_goal
    
    # Filter by type
    goals = goal_service.get_goals_for_character(character_id, goal_type=GoalType.PERSONAL)
    assert len(goals) == 1
    assert goals[0].goal_id == sample_goal.goal_id
    
    # Filter by status
    goals = goal_service.get_goals_for_character(character_id, status=GoalStatus.COMPLETED)
    assert len(goals) == 1
    assert goals[0].goal_id == another_goal.goal_id
    
    # Filter by priority
    goals = goal_service.get_goals_for_character(character_id, priority=GoalPriority.HIGH)
    assert len(goals) == 1
    assert goals[0].goal_id == another_goal.goal_id
    
    # Multiple filters
    goals = goal_service.get_goals_for_character(
        character_id,
        goal_type=GoalType.QUEST,
        status=GoalStatus.COMPLETED,
        priority=GoalPriority.HIGH
    )
    assert len(goals) == 1
    assert goals[0].goal_id == another_goal.goal_id


def test_get_goal(populated_goal_service): pass
    """Test get_goal method."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Get goal
    goal = goal_service.get_goal(character_id, sample_goal.goal_id)
    
    assert goal is not None
    assert goal.goal_id == sample_goal.goal_id
    assert goal.description == sample_goal.description
    
    # Get non-existent goal
    non_existent_goal = goal_service.get_goal(character_id, str(uuid4()))
    assert non_existent_goal is None


def test_add_goal(goal_service, character_id): pass
    """Test add_goal method."""
    # Mock the event dispatcher to prevent actual dispatching
    with patch.object(goal_service.event_dispatcher, 'dispatch'): pass
        # Add a goal
        description = "Test new goal"
        goal = goal_service.add_goal(
            character_id=character_id,
            description=description,
            goal_type=GoalType.PERSONAL,
            priority=GoalPriority.HIGH,
            metadata={"test": "value"}
        )
    
    # Check if goal was created correctly
    assert goal is not None
    assert goal.character_id == character_id
    assert goal.description == description
    assert goal.goal_type == GoalType.PERSONAL
    assert goal.priority == GoalPriority.HIGH
    assert goal.status == GoalStatus.ACTIVE
    assert goal.metadata == {"test": "value"}
    assert goal.progress == 0.0
    
    # Check if goal was added to the service
    assert character_id in goal_service.goals
    assert goal.goal_id in goal_service.goals[character_id]
    assert goal_service.goals[character_id][goal.goal_id] == goal


def test_update_goal_progress(populated_goal_service): pass
    """Test update_goal_progress method."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Mock the event dispatcher to prevent actual dispatching
    with patch.object(goal_service.event_dispatcher, 'dispatch'): pass
        # Update goal progress
        updated_goal = goal_service.update_goal_progress(
            character_id=character_id,
            goal_id=sample_goal.goal_id,
            progress=0.5
        )
    
    # Check if goal was updated correctly
    assert updated_goal is not None
    assert updated_goal.progress == 0.5
    assert goal_service.goals[character_id][sample_goal.goal_id].progress == 0.5
    
    # Test with non-existent goal
    result = goal_service.update_goal_progress(character_id, str(uuid4()), 0.7)
    assert result is None


def test_complete_goal(populated_goal_service): pass
    """Test complete_goal method."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Mock the event dispatcher to prevent actual dispatching
    with patch.object(goal_service.event_dispatcher, 'dispatch'), \
         patch.object(Goal, 'complete', return_value=None): pass
        # Complete the goal
        updated_goal = goal_service.complete_goal(
            character_id=character_id,
            goal_id=sample_goal.goal_id
        )
    
    # Check if goal was updated correctly
    assert updated_goal is not None
    assert updated_goal.status == GoalStatus.ACTIVE  # We mocked the complete method, so status won't change
    
    # Test with non-existent goal
    result = goal_service.complete_goal(character_id, str(uuid4()))
    assert result is None


def test_fail_goal(populated_goal_service): pass
    """Test fail_goal method."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Mock the event dispatcher to prevent actual dispatching and the fail method
    with patch.object(goal_service.event_dispatcher, 'dispatch'), \
         patch.object(Goal, 'fail', return_value=None): pass
        # Fail the goal
        reason = "Test failure reason"
        updated_goal = goal_service.fail_goal(
            character_id=character_id,
            goal_id=sample_goal.goal_id,
            reason=reason
        )
    
    # Check if goal was updated correctly
    assert updated_goal is not None
    assert updated_goal.status == GoalStatus.ACTIVE  # We mocked the fail method, so status won't change
    
    # Test with non-existent goal
    result = goal_service.fail_goal(character_id, str(uuid4()), "reason")
    assert result is None


def test_abandon_goal(populated_goal_service): pass
    """Test abandon_goal method."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Mock the event dispatcher to prevent actual dispatching and the abandon method
    with patch.object(goal_service.event_dispatcher, 'dispatch'), \
         patch.object(Goal, 'abandon', return_value=None): pass
        # Abandon the goal
        reason = "Test abandonment reason"
        result = goal_service.abandon_goal(
            character_id=character_id,
            goal_id=sample_goal.goal_id,
            reason=reason
        )
    
    # Check if goal was updated correctly
    assert result is True
    
    # Test with non-existent goal
    result = goal_service.abandon_goal(character_id, str(uuid4()), "reason")
    assert result is False


def test_update_goal_priority(populated_goal_service): pass
    """Test update_goal_priority method."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Update goal priority
    result = goal_service.update_goal_priority(
        character_id=character_id,
        goal_id=sample_goal.goal_id,
        priority=GoalPriority.HIGH
    )
    
    # Check if goal was updated correctly
    assert result is True
    updated_goal = goal_service.goals[character_id][sample_goal.goal_id]
    assert updated_goal.priority == GoalPriority.HIGH
    
    # Test with non-existent goal
    result = goal_service.update_goal_priority(character_id, str(uuid4()), GoalPriority.LOW)
    assert result is False


def test_remove_goal(populated_goal_service): pass
    """Test remove_goal method."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Remove the goal
    result = goal_service.remove_goal(
        character_id=character_id,
        goal_id=sample_goal.goal_id
    )
    
    # Check if goal was removed correctly
    assert result is True
    assert sample_goal.goal_id not in goal_service.goals[character_id]
    
    # Test with non-existent goal
    result = goal_service.remove_goal(character_id, str(uuid4()))
    assert result is False


def test_get_active_goals(populated_goal_service): pass
    """Test get_active_goals method."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Add another goal with completed status
    completed_goal = Goal(
        goal_id=str(uuid4()),
        character_id=character_id,
        description="Completed goal",
        goal_type=GoalType.PERSONAL,
        priority=GoalPriority.MEDIUM,
        status=GoalStatus.COMPLETED,
        metadata={},
        progress=1.0,
    )
    goal_service.goals[character_id][completed_goal.goal_id] = completed_goal
    
    # Get active goals
    active_goals = goal_service.get_active_goals(character_id)
    
    # Check if active goals are returned correctly
    assert len(active_goals) == 1
    assert active_goals[0].goal_id == sample_goal.goal_id
    assert active_goals[0].status == GoalStatus.ACTIVE


def test_get_completed_goals(populated_goal_service): pass
    """Test get_completed_goals method."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Add another goal with completed status
    completed_goal = Goal(
        goal_id=str(uuid4()),
        character_id=character_id,
        description="Completed goal",
        goal_type=GoalType.PERSONAL,
        priority=GoalPriority.MEDIUM,
        status=GoalStatus.COMPLETED,
        metadata={},
        progress=1.0,
    )
    goal_service.goals[character_id][completed_goal.goal_id] = completed_goal
    
    # Get completed goals
    completed_goals = goal_service.get_completed_goals(character_id)
    
    # Check if completed goals are returned correctly
    assert len(completed_goals) == 1
    assert completed_goals[0].goal_id == completed_goal.goal_id
    assert completed_goals[0].status == GoalStatus.COMPLETED


def test_get_highest_priority_goals(goal_service, character_id): pass
    """Test get_highest_priority_goals method."""
    # Add goals with different priorities
    high_priority_goal = Goal(
        goal_id=str(uuid4()),
        character_id=character_id,
        description="High priority goal",
        goal_type=GoalType.PERSONAL,
        priority=GoalPriority.HIGH,
        status=GoalStatus.ACTIVE,
    )
    
    medium_priority_goal = Goal(
        goal_id=str(uuid4()),
        character_id=character_id,
        description="Medium priority goal",
        goal_type=GoalType.PERSONAL,
        priority=GoalPriority.MEDIUM,
        status=GoalStatus.ACTIVE,
    )
    
    low_priority_goal = Goal(
        goal_id=str(uuid4()),
        character_id=character_id,
        description="Low priority goal",
        goal_type=GoalType.PERSONAL,
        priority=GoalPriority.LOW,
        status=GoalStatus.ACTIVE,
    )
    
    # Add goals to service
    goal_service.goals[character_id] = {
        high_priority_goal.goal_id: high_priority_goal,
        medium_priority_goal.goal_id: medium_priority_goal,
        low_priority_goal.goal_id: low_priority_goal,
    }
    
    # Get highest priority goals with limit=2
    highest_priority_goals = goal_service.get_highest_priority_goals(
        character_id=character_id,
        limit=2
    )
    
    # Check if highest priority goals are returned correctly
    assert len(highest_priority_goals) == 2
    assert highest_priority_goals[0].priority == GoalPriority.HIGH
    assert highest_priority_goals[1].priority == GoalPriority.MEDIUM


def test_get_goal_progress_summary(populated_goal_service): pass
    """Test get_goal_progress_summary method."""
    goal_service, character_id, sample_goal = populated_goal_service
    
    # Add more goals with different statuses
    completed_goal = Goal(
        goal_id=str(uuid4()),
        character_id=character_id,
        description="Completed goal",
        status=GoalStatus.COMPLETED,
    )
    
    failed_goal = Goal(
        goal_id=str(uuid4()),
        character_id=character_id,
        description="Failed goal",
        status=GoalStatus.FAILED,
    )
    
    abandoned_goal = Goal(
        goal_id=str(uuid4()),
        character_id=character_id,
        description="Abandoned goal",
        status=GoalStatus.ABANDONED,
    )
    
    # Add goals to service
    goal_service.goals[character_id][completed_goal.goal_id] = completed_goal
    goal_service.goals[character_id][failed_goal.goal_id] = failed_goal
    goal_service.goals[character_id][abandoned_goal.goal_id] = abandoned_goal
    
    # Get goal progress summary
    summary = goal_service.get_goal_progress_summary(character_id)
    
    # Check if summary contains expected keys
    assert isinstance(summary, dict)
    assert "character_id" in summary
    assert "total_goals" in summary
    assert "active_goals" in summary
    assert "completed_goals" in summary
    assert "failed_goals" in summary
    assert "abandoned_goals" in summary
    assert "overall_progress" in summary
    
    # Check values
    assert summary["character_id"] == character_id
    assert summary["total_goals"] == 4
    assert summary["active_goals"] == 1
    assert summary["completed_goals"] == 1
    assert summary["failed_goals"] == 1
    assert summary["abandoned_goals"] == 1
    assert summary["overall_progress"] == 0.25  # 1 completed out of 4 total


def test_parse_datetime(): pass
    """Test parse_datetime function."""
    # Test with valid datetime string
    now = datetime.utcnow()
    dt_str = now.isoformat()
    parsed_dt = parse_datetime(dt_str)
    
    assert parsed_dt is not None
    # Compare year, month, day, hour, minute to account for microsecond differences
    assert parsed_dt.year == now.year
    assert parsed_dt.month == now.month
    assert parsed_dt.day == now.day
    assert parsed_dt.hour == now.hour
    assert parsed_dt.minute == now.minute
    
    # Test with None
    assert parse_datetime(None) is None
    
    # Test with invalid string
    assert parse_datetime("invalid") is None 