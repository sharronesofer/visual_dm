from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from typing import Type
from typing import Optional
from dataclasses import field
"""
Test suite for CharacterService.
Tests service methods for character creation, retrieval, updates, and business logic.
"""

import pytest
import uuid
from unittest.mock import patch, MagicMock, call, Mock
from unittest.mock import ANY
import time
from copy import deepcopy

from backend.systems.character.services.character_service import CharacterService
from backend.systems.character.core.character_model import Character
from backend.systems.character.core.character_builder import CharacterBuilder
from backend.systems.character.core.events.event_dispatcher import EventDispatcher
from backend.systems.character.services.mood_service import MoodService
from backend.systems.shared.utils.common.error import NotFoundError, ValidationError, DatabaseError
from backend.systems.character.models.mood import EmotionalState, MoodIntensity
from backend.systems.character.models.goal import GoalType, GoalPriority, GoalStatus
from backend.systems.character.models.relationship import RelationshipType
from backend.systems.events import (
    CharacterCreated,
    CharacterLeveledUp,
    CharacterUpdated,
    CharacterDeleted,
    MoodChanged,
    GoalCreated,
    GoalCompleted,
    GoalFailed,
    GoalProgressUpdated,
)

@pytest.fixture
def event_dispatcher():
    """Create a mocked event dispatcher."""
    mock = MagicMock(spec=EventDispatcher)
    mock.dispatch = MagicMock()
    return mock


@pytest.fixture
def mood_service():
    """Create a mocked mood service."""
    return MagicMock(spec=MoodService)


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock()
    return session


@pytest.fixture
def relationship_service():
    """Fixture for relationship service mock."""
    mock_service = MagicMock()
    return mock_service


@pytest.fixture
def goal_service():
    """Fixture for goal service mock."""
    mock_service = MagicMock()
    return mock_service


@pytest.fixture
def mock_mood():
    """Fixture for mock mood object."""
    mock_mood = MagicMock()
    mock_mood.emotional_state = EmotionalState.HAPPY
    mock_mood.intensity = MoodIntensity.MEDIUM
    return mock_mood


@pytest.fixture
def character_service(event_dispatcher, mood_service, mock_db_session):
    """Create a character service with mocked dependencies."""
    # Create the service with our mock session directly
    service = CharacterService(db_session=mock_db_session)
    
    # Manually set the dependencies
    service.event_dispatcher = event_dispatcher
    service.mood_service = mood_service
    
    yield service


@pytest.fixture
def character_data():
    """Sample character data for testing."""
    return {
        "name": "Test Character",
        "race": "human",
        "class": "fighter",
        "stats": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 15,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 8
        }
    }


@pytest.fixture
def mock_character():
    """Create a mock character object."""
    character = MagicMock(spec=Character)
    character.character_id = str(uuid.uuid4())
    character.uuid = str(uuid.uuid4())
    character.character_name = "Test Character"
    character.selected_race = "human"
    character.attributes = {
        "class": "fighter",
        "strength": 16,
        "dexterity": 14,
        "constitution": 15,
        "intelligence": 10,
        "wisdom": 12,
        "charisma": 8,
        "level": 1,
        "experience": 0
    }
    return character


def test_create_character(character_service, character_data, event_dispatcher):
    """Test creating a new character."""
    # Extract data from the character_data dict to match method signature
    name = character_data["name"]
    race = character_data["race"]
    stats = character_data["stats"]
    
    # Mock the CharacterBuilder with the proper methods
    mock_builder = MagicMock(spec=CharacterBuilder)
    mock_builder.set_name = MagicMock(return_value=mock_builder)  # Builder pattern returns self
    mock_builder.set_race = MagicMock(return_value=mock_builder)
    mock_builder.set_stats = MagicMock(return_value=mock_builder)
    mock_builder.set_class = MagicMock(return_value=mock_builder)
    
    # Create a mock character data dictionary that finalize() would return
    mock_char_data = {
        "character_name": name,
        "race": race,
        "attributes": stats
    }
    mock_builder.finalize.return_value = mock_char_data
    
    # Create a mock character that will be returned from the ORM
    mock_character = MagicMock(spec=Character)
    mock_character.character_id = "test_id"
    mock_character.character_name = name
    
    # Configure the db to return the mock character when created
    character_service.db.add = MagicMock()
    character_service.db.commit = MagicMock()
    character_service.db.refresh = MagicMock()
    
    with patch("backend.systems.character.services.character_service.CharacterBuilder", return_value=mock_builder), \
         patch("backend.systems.character.services.character_service.Character", return_value=mock_character):
        # Call the method
        result = character_service.create_character(name, race, stats)
        
        # Verify the result
        assert result == mock_character
        
        # Verify builder methods were called
        mock_builder.set_name.assert_called_once_with(name)
        mock_builder.set_race.assert_called_once_with(race)
        
        # Verify events were dispatched (both GoalCreated and CharacterCreated)
        # Changed from assert_called_once() to assert_called() since we expect multiple calls
        assert event_dispatcher.dispatch.call_count == 2
        
        # Check that both events were dispatched
        call_args_list = event_dispatcher.dispatch.call_args_list
        event_types = [call.args[0].event_type for call in call_args_list]
        
        # Verify both events were dispatched
        assert 'goal.created' in event_types
        assert 'character.created' in event_types


def test_create_character_with_mood(character_service, mock_character, mood_service, event_dispatcher):
    """Test creating a character with an initial mood."""
    # Mock character builder and creation
    builder_mock = MagicMock()
    character_service.create_character = MagicMock(return_value=mock_character)
    
    # Setup test parameters
    name = "Test Character"
    race = "human"
    stats = {"strength": 16, "dexterity": 14}
    emotional_state = "HAPPY"
    intensity = "MEDIUM"
    reason = "Initial mood"
    
    # Mock mood service
    mock_mood = MagicMock()
    character_service.mood_service.create_mood.return_value = mock_mood
    
    # Call the method
    result = character_service.create_character_with_mood(
        name, race, stats, emotional_state, intensity, reason
    )
    
    # Verify character creation was called
    character_service.create_character.assert_called_once_with(
        name, race, stats
    )
    
    # Verify mood was created
    character_service.mood_service.create_mood.assert_called_once()
    
    # Verify event was dispatched
    event_dispatcher.dispatch.assert_called()
    
    # Verify the result is the mock character
    assert result == mock_character


def test_get_character(character_service, mock_character):
    """Test retrieving a character by ID."""
    character_id = mock_character.character_id
    
    # Configure the mock_db_session to return our mock character
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Call the method
    result = character_service.get_character(character_id)
    
    # Verify the result
    assert result == mock_character
    
    # Verify the session was queried correctly
    character_service.db.query.assert_called_once()
    character_service.db.query.return_value.filter.assert_called_once()


def test_get_character_nonexistent(character_service):
    """Test retrieving a non-existent character."""
    character_id = "nonexistent_id"
    
    # Configure the mock_db_session to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.get_character(character_id)


def test_update_character(character_service, mock_character):
    """Test updating a character."""
    character_id = mock_character.character_id
    update_data = {
        "name": "Updated Name",
        "stats": {
            "strength": 18
        }
    }
    
    # Configure the mock_db_session to return our mock character
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Use a patched Character class for the update logic instead of messing with __setattr__
    with patch("backend.systems.character.services.character_service.Character") as MockCharacter:
        MockCharacter.return_value = mock_character
        
        # Call the method
        result = character_service.update_character_data(character_id, update_data)
        
        # Verify the result
        assert result == mock_character
        
        # Verify that update was successful - DB commit should be called
        character_service.db.commit.assert_called_once()


def test_update_character_nonexistent(character_service):
    """Test updating a non-existent character."""
    character_id = "nonexistent_id"
    update_data = {"name": "Updated Name"}
    
    # Configure the mock_db_session to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.update_character_data(character_id, update_data)


def test_delete_character(character_service, mock_character):
    """Test deleting a character."""
    character_id = mock_character.character_id
    
    # Configure the mock_db_session to return our mock character
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Mock the CharacterDeleted event
    with patch("backend.systems.character.services.character_service.CharacterDeleted") as mock_event:
        # Call the method
        result = character_service.delete_character(character_id)
        
        # Verify the result
        assert result is True
        
        # Verify character was deleted
        character_service.db.delete.assert_called_once_with(mock_character)
        character_service.db.commit.assert_called_once()


def test_delete_character_nonexistent(character_service):
    """Test deleting a non-existent character."""
    character_id = "nonexistent_id"
    
    # Configure the mock_db_session to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Since we know this will raise NotFoundError, we don't need to mock the CharacterDeleted event
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.delete_character(character_id)


def test_add_experience_points(character_service, mock_character, event_dispatcher):
    """Test adding experience points to a character and leveling up."""
    character_id = mock_character.character_id
    xp_amount = 500
    reason = "Quest completion"
    
    # Configure mock character with initial stats
    mock_character.level = 1
    mock_character.stats = {
        "xp": 0,
        "class": "fighter",
        "constitution": 14,
        "hit_points": 10,
        "skill_points": 4
    }
    
    # Setup for patch of update_character_data
    with patch.object(character_service, 'update_character_data') as mock_update:
        with patch.object(character_service, '_calculate_xp_for_level') as mock_calc_xp:
            mock_calc_xp.return_value = 1000  # Level 2 XP threshold
            
            # Configure the database mock
            character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
            
            # Set up mock_update to maintain the patched behavior
            mock_update.return_value = mock_character
            
            # Call the method
            result = character_service.add_experience_points(character_id, xp_amount, reason)
            
            # Verify update_character_data was called
            mock_update.assert_called_once()
            call_args = mock_update.call_args[0]
            assert call_args[0] == character_id
            assert call_args[1] == 'stats'
            assert 'xp' in call_args[2]
            assert call_args[2]['xp'] == 500  # Updated XP
            
            # Verify event was dispatched
            event_dispatcher.dispatch.assert_called()
            event_args = event_dispatcher.dispatch.call_args[0][0]
            assert event_args.character_id == str(character_id)
            assert event_args.xp_gained == xp_amount
            assert event_args.new_xp == 500
            
            # Verify character was returned
            assert result == mock_character


def test_add_experience_points_no_level_up(character_service, mock_character, event_dispatcher):
    """Test adding experience points without triggering a level up."""
    character_id = mock_character.character_id
    xp_amount = 50
    reason = "Small reward"
    
    # Configure mock character with initial stats
    mock_character.level = 1
    mock_character.stats = {
        "xp": 0,
        "class": "fighter"
    }
    
    # Setup for patch of update_character_data
    with patch.object(character_service, 'update_character_data') as mock_update:
        with patch.object(character_service, '_calculate_xp_for_level') as mock_calc_xp:
            with patch.object(character_service, 'level_up_character') as mock_level_up:
                mock_calc_xp.return_value = 1000  # Level 2 XP threshold
                
                # Configure the database mock
                character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
                
                # Set up mock_update to maintain the patched behavior
                mock_update.return_value = mock_character
                
                # Call the method
                result = character_service.add_experience_points(character_id, xp_amount, reason)
                
                # Verify update_character_data was called
                mock_update.assert_called_once()
                call_args = mock_update.call_args[0]
                assert call_args[0] == character_id
                assert call_args[1] == 'stats'
                assert 'xp' in call_args[2]
                assert call_args[2]['xp'] == 50  # Updated XP
                
                # Verify event was dispatched
                event_dispatcher.dispatch.assert_called()
                event_args = event_dispatcher.dispatch.call_args[0][0]
                assert event_args.character_id == str(character_id)
                assert event_args.xp_gained == xp_amount
                assert event_args.new_xp == 50
                
                # Verify level_up_character was not called
                mock_level_up.assert_not_called()
                
                # Verify character was returned
                assert result == mock_character


def test_add_experience_points_nonexistent_character(character_service):
    """Test adding experience points to a non-existent character."""
    character_id = "nonexistent_id"
    xp_amount = 100
    
    # Configure the mock_db_session to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.add_experience_points(character_id, xp_amount)


def test_update_mood_from_relationship_change(character_service, mock_character, mood_service, event_dispatcher):
    """Test mood update when relationship changes positively."""
    character_id = "test_character_id"
    
    # Create a mock relationship
    mock_relationship = MagicMock()
    mock_relationship.source_id = "source_id"
    mock_relationship.target_id = character_id
    mock_relationship.data = {"affinity": 80}  # High affinity, positive change
    
    # Create a mock mood modifier that will be returned
    mock_modifier = MagicMock()
    mock_modifier.emotional_state = "HAPPY"
    mock_modifier.intensity = "MEDIUM"
    
    # Configure the mock services
    character_service.get_character = MagicMock(return_value=mock_character)
    
    # Create a new mock mood service with the add_mood_modifier method returning our mock modifier
    test_mood_service = MagicMock()
    test_mood_service.add_mood_modifier = MagicMock(return_value=mock_modifier)
    test_mood_service.get_mood = MagicMock(return_value=mock_modifier)
    
    # Set the mood service directly on the character service
    character_service.mood_service = test_mood_service
    
    # Call the method with a positive affinity change
    character_service.update_mood_from_relationship_change(
        mock_relationship, character_id, 15  # Positive change (using > 10 to trigger CONTENT state)
    )
    
    # Verify mood_service was called
    assert test_mood_service.add_mood_modifier.call_count >= 1
    
    # Verify event was dispatched
    event_dispatcher.dispatch.assert_called()


def test_update_mood_from_relationship_change_positive(character_service, mock_character, mood_service, event_dispatcher):
    """Test updating mood from a positive relationship change."""
    # Create mock character and relationship
    mock_character = MagicMock()
    mock_character.id = "test_character_id"
    mock_character.character_id = "test_character_id"
    relationship = MagicMock()
    relationship.target_id = "faction_uuid"
    relationship.affinity = 0
    affinity_change = 40
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Call the method
    result = character_service.update_mood_from_relationship_change(relationship, mock_character.character_id, affinity_change)
    
    # Verify mood service was called with correct parameters
    mood_service.add_mood_modifier.assert_called_once()
    args = mood_service.add_mood_modifier.call_args[0]
    assert args[0] == str(mock_character.character_id)
    assert args[1] == EmotionalState.HAPPY  # Emotional state for large positive change
    assert args[2] == MoodIntensity.MEDIUM  # Intensity
    
    # Verify event dispatch
    event_dispatcher.dispatch.assert_called_once()
    event_args = event_dispatcher.dispatch.call_args[0][0]
    assert event_args.character_id == str(mock_character.character_id)
    assert event_args.new_mood["emotional_state"] in ["HAPPY", "happy"]  # Accept either format


def test_update_mood_from_relationship_change_minimal(character_service, event_dispatcher):
    """Test updating mood from a minimal relationship change."""
    # Create mock relationship
    mock_relationship = MagicMock()
    mock_relationship.target_id = "target_id"
    
    character_id = "test_character_id"
    affinity_change = 5  # Small change, not enough to trigger mood update
    
    # Call the method
    result = character_service.update_mood_from_relationship_change(
        mock_relationship, character_id, affinity_change
    )
    
    # Verify mood service was not called for small change
    character_service.mood_service.add_mood_modifier.assert_not_called()
    
    # Verify event was not dispatched
    event_dispatcher.dispatch.assert_not_called()
    
    # Result should be None for minimal change
    assert result is None


def test_apply_mood_effects_to_relationships(character_service, mock_character, event_dispatcher):
    """Test applying mood effects to character relationships."""
    character_id = mock_character.character_id
    
    # Create mock mood
    mock_mood = MagicMock()
    mock_mood.emotional_state = EmotionalState.ANGRY
    mock_mood.intensity = MoodIntensity.HIGH
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Setup relationship service with patch
    with patch.object(character_service, 'relationship_service') as mock_relationship_service:
        # Create mock relationships
        mock_relationships = [
            MagicMock(target_id="faction1", relationship_type=RelationshipType.FACTION),
            MagicMock(target_id="character2", relationship_type=RelationshipType.CHARACTER)
        ]
        mock_relationship_service.get_relationships_by_source.return_value = mock_relationships
        
        # Setup mood service to return our mock mood
        with patch.object(character_service, 'mood_service') as mock_mood_service:
            mock_mood_service.get_mood.return_value = mock_mood
            
            # Call the method
            character_service.apply_mood_effects_to_relationships(character_id)
            
            # Verify relationship service was called to get relationships
            mock_relationship_service.get_relationships_by_source.assert_called_once()
            
            # Verify relationship service was called to update relationships
            assert mock_relationship_service.update_relationship.call_count == 2
            
            # Verify event dispatch (one per relationship)
            assert event_dispatcher.dispatch.call_count == 2


def test_calculate_xp_for_level(character_service):
    """Test XP calculation for different levels."""
    # Test for level 1
    assert character_service._calculate_xp_for_level(1) == 0
    
    # Test for level 2
    level2_xp = character_service._calculate_xp_for_level(2)
    assert level2_xp > 0
    
    # Test that higher levels require more XP
    assert character_service._calculate_xp_for_level(5) > character_service._calculate_xp_for_level(4)
    assert character_service._calculate_xp_for_level(10) > character_service._calculate_xp_for_level(5)


def test_level_up_character(character_service, mock_character, event_dispatcher):
    """Test leveling up a character."""
    character_id = mock_character.character_id
    
    # Set up mock character with required stats
    mock_character.level = 1
    mock_character.stats = {
        "class": "fighter",
        "constitution": 14,
        "hit_points": 10,
        "skill_points": 4
    }
    
    # Configure the database mock to return our mock character
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Call the method
    result = character_service.level_up_character(character_id)
    
    # Verify the results
    assert result.level == 2
    assert "hit_points" in result.stats
    assert result.stats["hit_points"] > 10  # Should increase
    
    # Verify that events were dispatched
    event_dispatcher.dispatch.assert_called()
    
    # Verify the database commit was called
    character_service.db.commit.assert_called_once()


def test_initialize_character_goals(character_service, mock_character):
    """Test initializing character goals."""
    # Configure mock character
    mock_character.id = 1
    mock_character.stats = {"class": "wizard"}
    
    # Call the method
    character_service.add_character_goal = MagicMock()
    character_service._initialize_character_goals(mock_character)
    
    # Verify that add_character_goal was called at least twice
    # (once for class-specific goal, once for universal goal)
    assert character_service.add_character_goal.call_count >= 2


def test_initialize_character_mood(character_service, mock_character):
    """Test initializing character mood."""
    # Configure mock character
    mock_character.id = 1
    mock_character.background = "noble"
    
    # Call the method
    character_service.add_character_mood_modifier = MagicMock()
    character_service._initialize_character_mood(mock_character)
    
    # Verify that add_character_mood_modifier was called
    character_service.add_character_mood_modifier.assert_called_once()


def test_build_character_from_input(character_service):
    """Test building a character from input data."""
    # Patch CharacterBuilder
    with patch('backend.systems.character.services.character_service.CharacterBuilder') as MockBuilder:
        # Configure mock builder
        mock_builder_instance = MagicMock()
        MockBuilder.return_value = mock_builder_instance
        
        # Mock the validation function
        character_service.validate_character_creation_data = MagicMock(return_value=True)
        
        # Define sample input data - use "elf" instead of "human" as race to match builder expectations
        input_data = {
            "name": "Test Character",
            "race": "elf", 
            "class": "fighter",
            "background": "soldier",
            "stats": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 10,
                "wisdom": 12,
                "charisma": 8
            }
        }
        
        # Set up mock character to return
        mock_character = MagicMock()
        mock_builder_instance.finalize.return_value = mock_character
        
        # Call the method
        result = character_service.build_character_from_input(input_data)
        
        # Verify builder was called correctly
        MockBuilder.assert_called_once()
        mock_builder_instance.load_from_input.assert_called_once_with(input_data)
        mock_builder_instance.finalize.assert_called_once()
        
        # Verify character was returned
        assert result == mock_character


def test_add_faction_relationship(character_service, mock_character):
    """Test adding a faction relationship to a character."""
    character_id = mock_character.character_id
    faction_id = "faction_uuid"
    reputation = 50
    standing = "friendly"
    
    # Configure the database mock to return our mock character
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Mock the relationship service with patch
    with patch.object(character_service, 'relationship_service') as mock_relationship_service:
        # Configure mock relationship
        mock_relationship = MagicMock()
        mock_relationship_service.create_relationship.return_value = mock_relationship
        
        # Call the method
        result = character_service.add_faction_relationship(character_id, faction_id, reputation, standing)
        
        # Verify relationship service was called with correct parameters
        mock_relationship_service.create_relationship.assert_called_once()
        call_args = mock_relationship_service.create_relationship.call_args[0]
        assert call_args[0] == str(character_id)
        assert call_args[1] == faction_id
        assert call_args[2] == RelationshipType.FACTION
        
        # Verify result
        assert result == mock_relationship


def test_get_character_relationships(character_service, mock_character):
    """Test getting character relationships."""
    character_id = mock_character.character_id
    relationship_type = None  # Get all relationships
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Setup relationship service with patch
    with patch.object(character_service, 'relationship_service') as mock_relationship_service:
        # Configure mock relationships
        mock_relationships = [MagicMock(), MagicMock()]
        mock_relationship_service.get_relationships_by_source.return_value = mock_relationships
        
        # Call the method
        result = character_service.get_character_relationships(character_id, relationship_type)
        
        # Verify relationship service was called with correct parameters
        mock_relationship_service.get_relationships_by_source.assert_called_once_with(mock_character.uuid, None)
        
        # Verify result
        assert result == mock_relationships


def test_add_quest_relationship(character_service, mock_character):
    """Test adding a quest relationship."""
    character_id = mock_character.character_id
    quest_id = "quest_uuid"
    relationship_data = {"progress": 0.5, "status": "in_progress"}
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Setup relationship service with patch
    with patch.object(character_service, 'relationship_service') as mock_relationship_service:
        # Configure mock relationship
        mock_relationship = MagicMock()
        mock_relationship_service.create_relationship.return_value = mock_relationship
        
        # Call the method
        result = character_service.add_quest_relationship(character_id, quest_id, relationship_data)
        
        # Verify relationship service was called with correct parameters
        mock_relationship_service.create_relationship.assert_called_once()
        call_args = mock_relationship_service.create_relationship.call_args[0]
        assert call_args[0] == str(character_id)
        assert call_args[1] == quest_id
        assert call_args[2] == RelationshipType.QUEST
        
        # Verify result
        assert result == mock_relationship


def test_add_character_relationship(character_service, mock_character):
    """Test adding a character relationship."""
    source_character_id = mock_character.character_id
    target_character_id = "target_character_uuid"
    relationship_data = {"affinity": 50, "status": "friend"}
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Setup relationship service with patch
    with patch.object(character_service, 'relationship_service') as mock_relationship_service:
        # Configure mock to avoid StopIteration
        mock_relationship_service.get_relationship.return_value = None
        
        # Configure mock relationship creation
        mock_relationship = MagicMock()
        mock_relationship_service.create_relationship.return_value = mock_relationship
        
        # Call the method
        result = character_service.add_character_relationship(source_character_id, target_character_id, relationship_data)
        
        # Verify relationship service was called
        mock_relationship_service.create_relationship.assert_called_once()
        
        # Verify result
        assert result == mock_relationship


def test_get_character_mood(character_service, mock_character, mood_service):
    """Test getting a character's mood."""
    character_id = mock_character.character_id
    
    # Configure the database mock to return our mock character
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Mock the mood service's get_mood method
    mock_mood = MagicMock()
    character_service.mood_service.get_mood.return_value = mock_mood
    
    # Call the method
    result = character_service.get_character_mood(character_id)
    
    # Verify mood service was called correctly
    character_service.mood_service.get_mood.assert_called_once_with(mock_character.uuid)
    
    # Verify the result is the mock mood
    assert result == mock_mood


def test_add_character_mood_modifier(character_service, mock_character, mood_service):
    """Test adding a mood modifier to a character."""
    character_id = mock_character.character_id
    emotional_state = "HAPPY"
    intensity = "MEDIUM"
    reason = "Test reason"
    duration_hours = 4.0
    
    # Configure the database mock to return our mock character
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Mock the mood service's add_mood_modifier method
    mock_modifier = MagicMock()
    character_service.mood_service.add_mood_modifier.return_value = mock_modifier
    
    # Call the method
    result = character_service.add_character_mood_modifier(character_id, emotional_state, intensity, reason, duration_hours)
    
    # Verify mood service was called correctly
    character_service.mood_service.add_mood_modifier.assert_called_once_with(
        mock_character.uuid, emotional_state, intensity, reason, duration_hours
    )
    
    # Verify the result is the mock modifier
    assert result == mock_modifier


def test_add_character_goal(character_service, mock_character):
    """Test adding a goal to a character."""
    character_id = mock_character.character_id
    description = "Test goal description"
    goal_type = GoalType.PERSONAL
    priority = GoalPriority.MEDIUM
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Setup goal service with patch
    with patch.object(character_service, 'goal_service') as mock_goal_service:
        # Configure mock goal
        mock_goal = MagicMock()
        mock_goal_service.add_goal.return_value = mock_goal
        
        # Call the method
        result = character_service.add_character_goal(character_id, description, goal_type, priority)
        
        # Verify goal service was called with correct parameters
        mock_goal_service.add_goal.assert_called_once()
        call_args = mock_goal_service.add_goal.call_args[0]
        assert call_args[0] == str(character_id)
        assert call_args[1] == description
        assert call_args[2] == goal_type
        assert call_args[3] == priority
        
        # Verify result
        assert result == mock_goal


def test_get_character_goals(character_service, mock_character):
    """Test getting character goals."""
    character_id = mock_character.character_id
    goal_type = GoalType.PERSONAL  # Optional filter
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Need to explicitly set character_service.goal_service
    mock_goal_service = MagicMock()
    character_service.goal_service = mock_goal_service
    
    # Configure mock goals
    mock_goals = [MagicMock(), MagicMock()]
    mock_goal_service.get_character_goals.return_value = mock_goals
    
    # Call the method
    result = character_service.get_character_goals(character_id, goal_type)
    
    # Verify goal service was called with correct parameters
    mock_goal_service.get_character_goals.assert_called_once()
    
    # Verify result
    assert result == mock_goals


def test_update_goal_progress(character_service, mock_character):
    """Test updating goal progress."""
    character_id = mock_character.character_id
    goal_id = "test_goal_id"
    progress = 0.75
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Need to explicitly set character_service.goal_service
    mock_goal_service = MagicMock()
    character_service.goal_service = mock_goal_service
    
    # Configure mock goal
    mock_goal = MagicMock()
    mock_goal.character_id = str(character_id)
    mock_goal.goal_id = goal_id
    mock_goal.progress = 0.5  # Old progress
    mock_goal_service.update_goal_progress.return_value = mock_goal
    
    # Call the method
    result = character_service.update_goal_progress(character_id, goal_id, progress)
    
    # Verify goal service was called with correct parameters
    mock_goal_service.update_goal_progress.assert_called_once()
    
    # Verify result
    assert result == mock_goal


def test_complete_goal(character_service, mock_character, event_dispatcher):
    """Test completing a character goal."""
    character_id = mock_character.character_id
    goal_id = "test_goal_id"
    completion_reason = "achieved"
    
    # Configure the database mock to return our mock character with a character_name
    mock_character.character_name = "Test Character"
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Need to explicitly set character_service.goal_service 
    mock_goal_service = MagicMock()
    character_service.goal_service = mock_goal_service
    
    # Configure mock goal
    mock_goal = MagicMock()
    mock_goal.character_id = str(character_id)
    mock_goal.goal_id = goal_id
    mock_goal.description = "Test goal description"
    mock_goal.priority = GoalPriority.MEDIUM
    mock_goal_service.complete_goal.return_value = mock_goal
    mock_goal_service.get_goal.return_value = mock_goal
    
    # Also mock the add_experience_points method to avoid validation errors
    character_service.add_experience_points = MagicMock(return_value=(mock_character, False))
    
    # Call the method
    result = character_service.complete_goal(character_id, goal_id, completion_reason)
    
    # Verify goal service was called with correct parameters
    mock_goal_service.complete_goal.assert_called_once()
    
    # Verify result
    assert result == mock_goal


def test_validate_character_creation_data_valid(character_service):
    """Test validating valid character creation data."""
    valid_data = {
        "name": "Test Character",
        "race": "human",
        "class": "fighter"
    }
    
    # This should not raise an exception
    character_service.validate_character_creation_data(valid_data)


def test_validate_character_creation_data_invalid(character_service):
    """Test validating invalid character creation data."""
    # Define invalid input data
    invalid_data = {
        "name": "",  # Empty name
        "race": "unknown_race",
        "class": "unknown_class"
    }
    
    # Use pytest.raises with the imported ValidationError
    with pytest.raises(ValidationError):
        character_service.validate_character_creation_data(invalid_data)


def test_has_spellcasting(character_service):
    """Test checking if a class has spellcasting."""
    # Mock the balance_constants to have a specific class with spellcasting
    with patch("backend.systems.character.services.character_service.balance_constants") as mock_constants:
        mock_constants.CLASS_SPELLCASTING_ABILITY = {"wizard": "intelligence"}
        
        # Test with a spellcasting class
        assert character_service._has_spellcasting("wizard") is True
        
        # Test with a non-spellcasting class
        assert character_service._has_spellcasting("fighter") is False


def test_calculate_ability_modifier(character_service):
    """Test calculating ability modifiers."""
    # Test various ability scores
    assert character_service._calculate_ability_modifier(1) == -4
    assert character_service._calculate_ability_modifier(10) == 0
    assert character_service._calculate_ability_modifier(11) == 0
    assert character_service._calculate_ability_modifier(12) == 1
    assert character_service._calculate_ability_modifier(20) == 5


def test_process_goal_completion(character_service, mock_character, event_dispatcher):
    """Test processing a completed goal with rewards and events."""
    # Configure mock goal
    mock_goal = MagicMock()
    mock_goal.character_id = str(mock_character.character_id)
    mock_goal.goal_id = "test_goal_id"
    mock_goal.description = "Test goal description"
    mock_goal.priority = GoalPriority.MEDIUM
    
    # Mock add_experience_points to avoid validation errors
    character_service.add_experience_points = MagicMock(return_value=mock_character)
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Call the method
    character_service.process_goal_completion(mock_goal)
    
    # Verify experience points were awarded
    character_service.add_experience_points.assert_called_once()
    
    # Verify mood modifier was added
    character_service.mood_service.add_mood_modifier.assert_called_once()
    
    # Verify event was dispatched
    event_dispatcher.dispatch.assert_called_once()
    event_args = event_dispatcher.dispatch.call_args[0][0]
    assert isinstance(event_args, GoalCompleted)
    assert event_args.character_id == str(mock_character.character_id)
    assert event_args.goal_id == "test_goal_id"
    assert event_args.reward_given is True


def test_process_goal_failure(character_service, mock_character, event_dispatcher):
    """Test processing a failed goal with mood effects and events."""
    # Configure mock goal
    mock_goal = MagicMock()
    mock_goal.character_id = str(mock_character.character_id)
    mock_goal.goal_id = "test_goal_id"
    mock_goal.description = "Test goal description"
    
    # Call the method
    character_service.process_goal_failure(mock_goal)
    
    # Verify mood modifier was added (negative mood)
    character_service.mood_service.add_mood_modifier.assert_called_once()
    call_args = character_service.mood_service.add_mood_modifier.call_args[0]
    assert call_args[0] == str(mock_character.character_id)
    
    # Check emotional state - handle both enum and string representations
    assert call_args[1] in [EmotionalState.DISAPPOINTED, "DISAPPOINTED"]
    
    # Check intensity - handle both enum and string representations
    assert call_args[2] in [MoodIntensity.MEDIUM, "MEDIUM"]
    
    # Verify event was dispatched
    event_dispatcher.dispatch.assert_called_once()
    event_args = event_dispatcher.dispatch.call_args[0][0]
    assert isinstance(event_args, GoalFailed)
    assert event_args.character_id == str(mock_character.character_id)
    assert event_args.goal_id == "test_goal_id"
    assert hasattr(event_args, "failure_time")


def test_update_personal_goal_progress(character_service, mock_character, event_dispatcher):
    """Test updating progress for a personal goal."""
    # Configure mock goal
    mock_goal = MagicMock()
    mock_goal.character_id = str(mock_character.character_id)
    mock_goal.goal_id = "test_goal_id"
    mock_goal.goal_type = GoalType.PERSONAL
    mock_goal.progress = 0.3
    
    # Configure mock character
    mock_character.level = 5  # Should result in progress of 0.5
    
    # Configure the goal service
    character_service.goal_service = MagicMock()
    character_service.goal_service.update_goal_progress.return_value = mock_goal
    
    # Call the method
    character_service.update_personal_goal_progress(mock_character, mock_goal)
    
    # Verify goal progress was updated
    character_service.goal_service.update_goal_progress.assert_called_once()
    call_args = character_service.goal_service.update_goal_progress.call_args[0]
    assert call_args[0] == str(mock_character.character_id)
    assert call_args[1] == "test_goal_id"
    assert call_args[2] == 0.5  # Progress should be level/10
    
    # Verify event was dispatched
    event_dispatcher.dispatch.assert_called_once()
    event_args = event_dispatcher.dispatch.call_args[0][0]
    assert isinstance(event_args, GoalProgressUpdated)
    assert event_args.character_id == str(mock_character.character_id)
    assert event_args.goal_id == "test_goal_id"
    assert event_args.old_progress == 0.3
    assert event_args.new_progress == 0.5
    assert event_args.progress_delta == 0.2


def test_update_mood_from_relationship_change_nonexistent(character_service):
    """Test updating mood for a non-existent character."""
    # Create mock relationship
    mock_relationship = MagicMock()
    mock_relationship.target_id = "target_id"
    
    character_id = "nonexistent_id"
    affinity_change = 20  # Significant change
    
    # Configure the database mock to return None (nonexistent character)
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.update_mood_from_relationship_change(
            mock_relationship, character_id, affinity_change
        )


def test_create_character_from_builder_validation_error(character_service):
    """Test handling validation error in create_character_from_builder."""
    # Create a mock builder that fails validation
    mock_builder = MagicMock()
    mock_builder.is_valid.return_value = False
    
    # Test validation error is raised
    with pytest.raises(ValidationError):
        character_service.create_character_from_builder(mock_builder)
    
    # Verify that db operations were not called
    character_service.db.add.assert_not_called()
    character_service.db.commit.assert_not_called()


def test_create_character_from_builder_database_error(character_service):
    """Test handling database error in create_character_from_builder."""
    # Create a mock builder that passes validation
    mock_builder = MagicMock()
    mock_builder.is_valid.return_value = True
    
    # Configure the mock builder to return valid data
    mock_builder.finalize.return_value = {
        "character_name": "Test Character",
        "race": "human",
        "level": 1,
        "attributes": {"strength": 16}
    }
    
    # Configure the database to raise an exception on commit
    character_service.db.commit.side_effect = Exception("Database error")
    
    # Now we need to patch the implementation to propagate the DatabaseError
    with patch('backend.systems.character.services.character_service.DatabaseError', side_effect=DatabaseError):
        # Test that DatabaseError is raised
        with pytest.raises(DatabaseError):
            character_service.create_character_from_builder(mock_builder)
    
    # Verify rollback was called
    character_service.db.rollback.assert_called_once()


def test_get_character_by_uuid(character_service, mock_character):
    """Test retrieving a character by UUID."""
    # Configure mock character
    mock_uuid = str(uuid.uuid4())
    mock_character.uuid = mock_uuid
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Call the method
    result = character_service.get_character_by_uuid(mock_uuid)
    
    # Verify the result
    assert result == mock_character
    
    # Verify the query was called correctly
    character_service.db.query.assert_called_once()
    character_service.db.query.return_value.filter.assert_called_once()


def test_get_character_by_uuid_nonexistent(character_service):
    """Test retrieving a non-existent character by UUID."""
    uuid_str = str(uuid.uuid4())
    
    # Configure the database mock to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.get_character_by_uuid(uuid_str)


def test_get_character_builder_by_id(character_service, mock_character):
    """Test retrieving a character builder by ID."""
    character_id = mock_character.character_id
    
    # Mock the to_builder method on the character
    mock_builder = MagicMock()
    mock_character.to_builder = MagicMock(return_value=mock_builder)
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Call the method
    result = character_service.get_character_builder_by_id(character_id)
    
    # Verify the result
    assert result == mock_builder
    
    # Verify to_builder was called
    mock_character.to_builder.assert_called_once()


def test_get_character_builder_by_id_not_implemented(character_service, mock_character):
    """Test retrieving a character builder when to_builder is not implemented."""
    character_id = mock_character.character_id
    
    # Remove to_builder method from mock character
    mock_character.to_builder = None
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Test that NotImplementedError is raised
    with pytest.raises(NotImplementedError):
        character_service.get_character_builder_by_id(character_id)


def test_delete_character_database_error(character_service, mock_character):
    """Test handling database error in delete_character."""
    character_id = mock_character.character_id
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    character_service.db.commit.side_effect = Exception("Database error")
    
    # Now we need to patch the implementation to propagate the DatabaseError
    with patch('backend.systems.character.services.character_service.DatabaseError', side_effect=DatabaseError):
        # Test that DatabaseError is raised
        with pytest.raises(DatabaseError):
            character_service.delete_character(character_id)
    
    # Verify rollback was called
    character_service.db.rollback.assert_called_once()


def test_level_up_character_with_spellcaster(character_service, mock_character):
    """Test leveling up a spellcaster character."""
    character_id = mock_character.character_id
    
    # Set up mock character with required stats for a spellcaster
    mock_character.level = 1
    mock_character.stats = {
        "class": "wizard",  # Spellcaster class
        "constitution": 14,
        "intelligence": 16,  # Spellcasting ability for wizard
        "hit_points": 10,
        "mana_points": 10,
        "skill_points": 4
    }
    
    # Patch the _has_spellcasting method to return True
    with patch.object(character_service, '_has_spellcasting', return_value=True):
        # Configure the database mock
        character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
        
        # Call the method
        result = character_service.level_up_character(character_id)
        
        # Verify the results
        assert result.level == 2
        assert "hit_points" in result.stats
        assert "mana_points" in result.stats
        assert result.stats["mana_points"] > 10  # Should increase for spellcaster
        
        # Verify that events were dispatched
        character_service.event_dispatcher.dispatch.assert_called()


def test_level_up_character_with_validation_error(character_service, mock_character):
    """Test leveling up a character with missing class."""
    character_id = mock_character.character_id
    
    # Set up mock character with missing class
    mock_character.level = 1
    mock_character.stats = {
        # No class defined
        "constitution": 14,
        "hit_points": 10
    }
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Test that ValidationError is raised
    with pytest.raises(ValidationError):
        character_service.level_up_character(character_id)


def test_create_character_with_mood_validation(character_service):
    """Test validation in create_character_with_mood."""
    # Mock character builder and creation with validation error
    character_service.create_character = MagicMock(side_effect=ValidationError("Invalid character data"))
    
    # Setup test parameters
    name = "Test Character"
    race = "human"
    stats = {"strength": 16, "dexterity": 14}
    emotional_state = "HAPPY"
    intensity = "MEDIUM"
    
    # Test that ValidationError is propagated
    with pytest.raises(ValidationError):
        character_service.create_character_with_mood(
            name, race, stats, emotional_state, intensity
        )
    
    # Verify character creation was attempted
    character_service.create_character.assert_called_once()
    
    # Verify mood was not created
    character_service.mood_service.create_mood.assert_not_called()


def test_add_faction_relationship_nonexistent_character(character_service):
    """Test adding faction relationship for non-existent character."""
    character_id = "nonexistent_id"
    faction_id = "faction_uuid"
    relationship_type = "allies"
    affinity = 50
    
    # Configure the database mock to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Mock the relationship_service.create_relationship method
    character_service.relationship_service.create_relationship = MagicMock()
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.add_faction_relationship(character_id, faction_id, relationship_type, affinity)
    
    # Verify relationship_service was not called
    character_service.relationship_service.create_relationship.assert_not_called()


def test_add_quest_relationship_nonexistent_character(character_service):
    """Test adding quest relationship for non-existent character."""
    character_id = "nonexistent_id"
    quest_id = "quest_uuid"
    relationship_data = {"progress": 0.5}
    
    # Configure the database mock to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Mock the relationship_service.create_relationship method
    character_service.relationship_service.create_relationship = MagicMock()
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.add_quest_relationship(character_id, quest_id, relationship_data)
    
    # Verify relationship_service was not called
    character_service.relationship_service.create_relationship.assert_not_called()


def test_apply_mood_effects_to_relationships_no_relationships(character_service, mock_character):
    """Test applying mood effects when character has no relationships."""
    character_id = mock_character.character_id
    
    # Create mock mood
    mock_mood = MagicMock()
    mock_mood.emotional_state = EmotionalState.HAPPY
    mock_mood.intensity = MoodIntensity.MEDIUM
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Patch both logging and services
    with patch('backend.systems.character.services.character_service.logger') as mock_logger:
        # Use patching to create proper mocks
        with patch.object(character_service, 'mood_service') as mock_mood_service:
            # Setup mood service to return our mock mood
            mock_mood_service.get_mood.return_value = mock_mood
            
            with patch.object(character_service, 'relationship_service') as mock_relationship_service:
                # Setup relationship service to return our mock relationships
                mock_relationship_service.get_relationships_by_source.return_value = []
                mock_relationship_service.update_relationship = MagicMock()
                
                # Call the method
                character_service.apply_mood_effects_to_relationships(character_id)
                
                # Verify relationship service was called to get relationships
                mock_relationship_service.get_relationships_by_source.assert_called_once()
                
                # Verify relationship service was not called to update any relationships
                mock_relationship_service.update_relationship.assert_not_called()
                
                # Verify debug message was logged
                mock_logger.debug.assert_called_once()


def test_apply_mood_effects_to_relationships_no_mood(character_service, mock_character):
    """Test applying mood effects when character has no mood."""
    character_id = mock_character.character_id
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Patch both logging and services
    with patch('backend.systems.character.services.character_service.logger') as mock_logger:
        # Use patching to create proper mocks
        with patch.object(character_service, 'mood_service') as mock_mood_service:
            # Setup mood service to return None (no mood)
            mock_mood_service.get_mood.return_value = None
            
            # Call the method
            character_service.apply_mood_effects_to_relationships(character_id)
            
            # Verify mood service was called
            mock_mood_service.get_mood.assert_called_once()
            
            # Verify debug message was logged
            mock_logger.debug.assert_called_once()


def test_apply_mood_effects_to_relationships_non_affinity_relationships(character_service, mock_character):
    """Test applying mood effects to relationships that don't support affinity changes."""
    character_id = mock_character.character_id
    
    # Create mock mood
    mock_mood = MagicMock()
    mock_mood.emotional_state = EmotionalState.HAPPY
    mock_mood.intensity = MoodIntensity.MEDIUM
    
    # Create mock relationships with types that don't support affinity
    mock_relationships = [
        MagicMock(relationship_type="QUEST", target_id="quest1"),
        MagicMock(relationship_type="ITEM", target_id="item1")
    ]
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Patch both logging and services
    with patch('backend.systems.character.services.character_service.logger') as mock_logger:
        # Use patching to create proper mocks
        with patch.object(character_service, 'mood_service') as mock_mood_service:
            # Setup mood service to return our mock mood
            mock_mood_service.get_mood.return_value = mock_mood
            
            with patch.object(character_service, 'relationship_service') as mock_relationship_service:
                # Setup relationship service to return our mock relationships
                mock_relationship_service.get_relationships_by_source.return_value = mock_relationships
                mock_relationship_service.update_relationship = MagicMock()
                
                # Call the method
                character_service.apply_mood_effects_to_relationships(character_id)
                
                # Verify relationship service was called to get relationships
                mock_relationship_service.get_relationships_by_source.assert_called_once()
                
                # Verify relationship service was not called to update any relationships
                mock_relationship_service.update_relationship.assert_not_called()


def test_apply_mood_effects_to_relationships_with_error(character_service, mock_character, event_dispatcher):
    """Test handling errors when applying mood effects to relationships."""
    character_id = mock_character.character_id
    
    # Create mock mood
    mock_mood = MagicMock()
    mock_mood.emotional_state = EmotionalState.ANGRY
    mock_mood.intensity = MoodIntensity.HIGH
    
    # Create mock relationships
    mock_relationship = MagicMock(
        target_id="faction1", 
        relationship_type=RelationshipType.FACTION,
        attributes={"affinity": 50}
    )
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Patch both logging and services
    with patch('backend.systems.character.services.character_service.logger') as mock_logger:
        # Use patching to create proper mocks
        with patch.object(character_service, 'mood_service') as mock_mood_service:
            # Setup mood service to return our mock mood
            mock_mood_service.get_mood.return_value = mock_mood
            
            with patch.object(character_service, 'relationship_service') as mock_relationship_service:
                # Setup relationship service to return our mock relationships and raise an exception on update
                mock_relationship_service.get_relationships_by_source.return_value = [mock_relationship]
                mock_relationship_service.update_relationship.side_effect = Exception("Update error")
                
                # Call the method
                character_service.apply_mood_effects_to_relationships(character_id)
                
                # Verify relationship service was called to get relationships
                mock_relationship_service.get_relationships_by_source.assert_called_once()
                
                # Verify relationship service was called to update relationships
                mock_relationship_service.update_relationship.assert_called_once()
                
                # Verify error was logged
                mock_logger.error.assert_called_once()
                
                # Verify no events were dispatched
                event_dispatcher.dispatch.assert_not_called()


def test_process_goal_completion_with_exceptions(character_service, mock_character, event_dispatcher):
    """Test processing a completed goal with error handling."""
    # Configure mock goal
    mock_goal = MagicMock()
    mock_goal.character_id = str(mock_character.character_id)
    mock_goal.goal_id = "test_goal_id"
    mock_goal.description = "Test goal description"
    mock_goal.priority = GoalPriority.MEDIUM
    
    # Patch both logging and services
    with patch('backend.systems.character.services.character_service.logger') as mock_logger:
        # Mock add_experience_points to raise an exception
        with patch.object(character_service, 'add_experience_points', side_effect=Exception("XP error")):
            # Call the method
            character_service.process_goal_completion(mock_goal)
            
            # Verify error was logged
            mock_logger.error.assert_called_once()
            
            # Verify mood modifier was still added despite XP error
            character_service.mood_service.add_mood_modifier.assert_called_once()
            
            # Verify event was still dispatched despite XP error
            event_dispatcher.dispatch.assert_called_once()


def test_process_goal_failure_with_missing_character_id(character_service, event_dispatcher):
    """Test processing a failed goal with missing character ID."""
    # Configure mock goal with missing character_id
    mock_goal = MagicMock()
    mock_goal.character_id = None
    mock_goal.goal_id = "test_goal_id"
    mock_goal.description = "Test goal description"
    
    # Configure the character_service._get_character_orm_by_id to raise an exception
    character_service._get_character_orm_by_id = MagicMock(side_effect=NotFoundError("Character not found"))
    
    # Mock the mood_service to prevent it from being called
    character_service.mood_service.add_mood_modifier = MagicMock()
    
    # Mock event_dispatcher
    event_dispatcher.dispatch = MagicMock()
    
    # Configure logger to avoid actual logging during test
    with patch('backend.systems.character.services.character_service.logger') as mock_logger:
        # Call the method
        character_service.process_goal_failure(mock_goal)
        
        # Verify mood service was not called
        character_service.mood_service.add_mood_modifier.assert_not_called()
        
        # Verify event was not dispatched
        event_dispatcher.dispatch.assert_not_called()
        
        # Verify log was created
        mock_logger.error.assert_called_once()


def test_update_personal_goal_progress_with_no_progress(character_service, mock_character, event_dispatcher):
    """Test updating personal goal progress with no change."""
    # Configure mock character with a low level to ensure no progress
    mock_character.level = 3
    
    # Configure mock goal with existing progress higher than level/10 would provide
    mock_goal = MagicMock()
    mock_goal.character_id = str(mock_character.character_id)
    mock_goal.goal_id = "test_goal_id"
    mock_goal.goal_type = GoalType.PERSONAL
    mock_goal.progress = 0.5  # Higher than level/10 would give
    
    # Override the update_goal_progress method
    with patch.object(character_service, 'update_goal_progress') as mock_update_progress:
        # Call the method
        character_service.update_personal_goal_progress(mock_character, mock_goal)
        
        # Verify goal progress was not updated (since there's no increase)
        mock_update_progress.assert_not_called()
    
    # Verify no event was dispatched
    event_dispatcher.dispatch.assert_not_called()


def test_update_personal_goal_progress_with_level_progress(character_service, mock_character, event_dispatcher):
    """Test updating personal goal progress based on character level."""
    # Configure mock character
    mock_character.level = 8  # High level to ensure significant progress
    
    # Configure mock goal
    mock_goal = MagicMock()
    mock_goal.character_id = str(mock_character.character_id)
    mock_goal.goal_id = "test_goal_id"
    mock_goal.goal_type = GoalType.PERSONAL
    mock_goal.progress = 0.5  # Starting at 50% progress
    
    # Use patching to ensure proper mocking
    with patch.object(character_service, 'goal_service') as mock_goal_service:
        # Configure goal service to return our mock goal
        mock_goal_service.update_goal_progress.return_value = mock_goal
        
        # Call the method
        character_service.update_personal_goal_progress(mock_character, mock_goal)
        
        # Verify goal progress was updated
        mock_goal_service.update_goal_progress.assert_called_once()
        
        # Handle both positional and keyword args
        if mock_goal_service.update_goal_progress.call_args[0]:  # If using positional args
            call_args = mock_goal_service.update_goal_progress.call_args[0]
            assert call_args[0] == str(mock_character.character_id)
            assert call_args[1] == "test_goal_id"
            assert call_args[2] > 0.5  # Progress should increase
        else:  # If using keyword args
            kwargs = mock_goal_service.update_goal_progress.call_args.kwargs
            assert kwargs.get('character_id') == str(mock_character.character_id)
            assert kwargs.get('goal_id') == "test_goal_id"
            assert kwargs.get('progress') > 0.5  # Progress should increase
        
        # Verify event was dispatched
        event_dispatcher.dispatch.assert_called_once()
        event_args = event_dispatcher.dispatch.call_args[0][0]
        assert isinstance(event_args, GoalProgressUpdated)


def test_update_personal_goal_progress_with_non_personal_goal(character_service, mock_character):
    """Test updating a non-personal goal progress."""
    # Configure mock character
    mock_character.level = 5
    
    # Configure mock goal with non-personal type
    mock_goal = MagicMock()
    mock_goal.character_id = str(mock_character.character_id)
    mock_goal.goal_id = "test_goal_id"
    mock_goal.goal_type = GoalType.QUEST  # Not a personal goal
    mock_goal.progress = 0.3
    
    # Override the update_goal_progress method
    with patch.object(character_service, 'update_goal_progress') as mock_update_progress:
        # Call the method
        character_service.update_personal_goal_progress(mock_character, mock_goal)
        
        # Verify goal progress was not updated
        mock_update_progress.assert_not_called()


def test_complete_goal_nonexistent_character(character_service):
    """Test completing a goal for a non-existent character."""
    character_id = "nonexistent_id"
    goal_id = "test_goal_id"
    
    # Configure the database mock to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.complete_goal(character_id, goal_id)


def test_get_character_mood_nonexistent_character(character_service):
    """Test getting mood for a non-existent character."""
    character_id = "nonexistent_id"
    
    # Configure the database mock to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.get_character_mood(character_id)


def test_add_character_mood_modifier_nonexistent_character(character_service):
    """Test adding mood modifier to a non-existent character."""
    character_id = "nonexistent_id"
    emotional_state = "HAPPY"
    intensity = "MEDIUM"
    reason = "Test reason"
    
    # Configure the database mock to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.add_character_mood_modifier(
            character_id, emotional_state, intensity, reason
        )


def test_update_goal_progress_complete(character_service, mock_character, event_dispatcher):
    """Test updating goal progress to completion."""
    character_id = mock_character.character_id
    goal_id = "test_goal_id"
    progress = 1.0  # Complete progress
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Need to explicitly set character_service.goal_service
    mock_goal_service = MagicMock()
    character_service.goal_service = mock_goal_service
    
    # Configure mock goal
    mock_goal = MagicMock()
    mock_goal.character_id = str(character_id)
    mock_goal.goal_id = goal_id
    mock_goal.progress = 0.8  # Old progress
    mock_goal_service.update_goal_progress.return_value = mock_goal
    
    # Mock the complete_goal method to verify it's called
    character_service.complete_goal = MagicMock()
    
    # Call the method
    result = character_service.update_goal_progress(character_id, goal_id, progress)
    
    # Verify goal service was called with correct parameters
    mock_goal_service.update_goal_progress.assert_called_once()
    
    # Verify complete_goal was called since progress is 1.0
    character_service.complete_goal.assert_called_once_with(str(character_id), goal_id, "achieved")
    
    # Verify result
    assert result == mock_goal


def test_add_character_relationship_existing_relationship(character_service, mock_character):
    """Test adding a character relationship when relationship already exists."""
    source_character_id = mock_character.character_id
    target_character_id = "target_character_uuid"
    relationship_data = {"affinity": 50, "status": "friend"}
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Create mock existing relationship
    mock_relationship = MagicMock()
    
    # Use patching to properly mock the relationship service
    with patch.object(character_service, 'relationship_service') as mock_relationship_service:
        # Setup relationship service methods
        mock_relationship_service.get_relationship.return_value = mock_relationship
        mock_relationship_service.update_relationship.return_value = mock_relationship
        mock_relationship_service.create_relationship = MagicMock()
        
        # Call the method
        result = character_service.add_character_relationship(source_character_id, target_character_id, relationship_data)
        
        # Verify get_relationship was called
        mock_relationship_service.get_relationship.assert_called_once()
        
        # Verify update_relationship was called instead of create_relationship
        mock_relationship_service.update_relationship.assert_called_once()
        mock_relationship_service.create_relationship.assert_not_called()
        
        # Verify result
        assert result == mock_relationship


def test_validate_character_creation_data_empty(character_service):
    """Test validating empty character creation data."""
    empty_data = {}
    
    # Test ValidationError is raised
    with pytest.raises(ValidationError):
        character_service.validate_character_creation_data(empty_data)


def test_update_goal_progress_nonexistent_character(character_service):
    """Test updating goal progress for a non-existent character."""
    character_id = "nonexistent_id"
    goal_id = "test_goal_id"
    progress = 0.5
    
    # Configure the database mock to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Use a mock for goal_service
    mock_goal_service = MagicMock()
    character_service.goal_service = mock_goal_service
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.update_goal_progress(character_id, goal_id, progress)


def test_create_character_with_inventory(character_service):
    """Test creating a character with inventory items."""
    # Setup test data
    name = "Test Character"
    race = "human"
    stats = {"strength": 16, "dexterity": 14}
    inventory_items = ["sword", "shield"]
    
    # Mock character and builder
    mock_builder = MagicMock()
    mock_builder.is_valid.return_value = True
    mock_builder.finalize.return_value = {
        "character_name": name,
        "race": race,
        "attributes": stats,
        "starter_kit": {"equipment": inventory_items}
    }
    
    # Mock CharacterBuilder creation
    with patch('backend.systems.character.core.character_builder.CharacterBuilder', return_value=mock_builder):
        # Call the method
        result = character_service.create_character(name, race, stats, inventory_items=inventory_items)
        
        # Verify character was created
        assert result is not None
        assert result.name == name
        assert result.race == race


def test_level_up_character_max_level(character_service, mock_character):
    """Test level up character that's already at max level."""
    # Configure mock character to be at max level
    mock_character.level = 20  # Assuming 20 is max level
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Call the method
    result = character_service.level_up_character(mock_character.character_id)
    
    # Verify level didn't increase
    assert result.level == 20
    
    # Verify event was not dispatched
    character_service.event_dispatcher.dispatch.assert_not_called()


def test_add_experience_points_level_up(character_service, mock_character, event_dispatcher):
    """Test adding experience points that trigger level up."""
    character_id = mock_character.character_id
    amount = 1000  # Large amount to trigger level up
    reason = "Test reason"
    
    # Configure mock character
    mock_character.level = 1
    mock_character.xp = 0
    
    # Configure level calculation to return threshold that will be exceeded
    with patch.object(character_service, '_calculate_xp_for_level', return_value=100):
        # Configure the database mock
        character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
        
        # Mock level_up_character method
        character_service.level_up_character = MagicMock()
        
        # Call the method
        result = character_service.add_experience_points(character_id, amount, reason)
        
        # Verify experience was added
        assert result.xp == amount
        
        # Verify level_up_character was called
        character_service.level_up_character.assert_called_once()


def test_update_character_data_invalid_field(character_service, mock_character):
    """Test updating character with invalid field."""
    character_id = mock_character.character_id
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Test ValidationError is raised
    with pytest.raises(ValidationError):
        character_service.update_character_data(character_id, "invalid_field", "value")


def test_update_character_data_dict(character_service, mock_character):
    """Test updating character with a dictionary of updates."""
    character_id = mock_character.character_id
    updates = {
        "name": "Updated Name",
        "race": "elf",
        "level": 5
    }
    
    # Configure the database mock
    character_service.db.query.return_value.filter.return_value.first.return_value = mock_character
    
    # Call the method
    result = character_service.update_character_data(character_id, updates)
    
    # Verify character was updated
    assert result.name == updates["name"]
    assert result.race == updates["race"]
    assert result.level == updates["level"]
    
    # Verify database commit was called
    character_service.db.commit.assert_called_once()
    
    # Verify event was dispatched
    character_service.event_dispatcher.dispatch.assert_called_once()


def test_initialize_character_goals_exception(character_service, mock_character):
    """Test initializing character goals with exception handling."""
    # Configure mock goal service to raise an exception
    with patch.object(character_service, 'goal_service') as mock_goal_service:
        mock_goal_service.add_goal.side_effect = Exception("Goal error")
        
        # Configure logger
        with patch('backend.systems.character.services.character_service.logger') as mock_logger:
            # Call the method
            character_service._initialize_character_goals(mock_character)
            
            # Verify error was logged
            mock_logger.error.assert_called_once()


def test_initialize_character_mood_exception(character_service, mock_character):
    """Test initializing character mood with exception handling."""
    # Configure mock mood service to raise an exception
    with patch.object(character_service, 'mood_service') as mock_mood_service:
        mock_mood_service.initialize_mood.side_effect = Exception("Mood error")
        
        # Configure logger
        with patch('backend.systems.character.services.character_service.logger') as mock_logger:
            # Call the method
            character_service._initialize_character_mood(mock_character)
            
            # Verify error was logged
            mock_logger.error.assert_called_once()


def test_get_character_goals_nonexistent_character(character_service):
    """Test getting goals for a non-existent character."""
    character_id = "nonexistent_id"
    
    # Configure the database mock to return None
    character_service.db.query.return_value.filter.return_value.first.return_value = None
    
    # Test that NotFoundError is raised
    with pytest.raises(NotFoundError):
        character_service.get_character_goals(character_id) 