from backend.systems.shared.database.session import get_db_session
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.session import get_db_session
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.session import get_db_session
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.session import get_db_session
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.session import get_db_session
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.session import get_db_session
from backend.systems.events.dispatcher import EventDispatcher
from typing import Type

# Import EventBase and EventDispatcher with fallbacks
try: pass
    from backend.systems.events import EventBase, EventDispatcher
except ImportError: pass
    # Fallback for tests or when events system isn't available
    class EventBase: pass
        def __init__(self, **data): pass
            for key, value in data.items(): pass
                setattr(self, key, value)
    
    class EventDispatcher: pass
        @classmethod
        def get_instance(cls): pass
            return cls()
        
        def dispatch(self, event): pass
            pass
        
        def publish(self, event): pass
            pass
        
        def emit(self, event): pass
            pass

"""
Integration tests for the character system services.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from uuid import uuid4

from backend.systems.character.services.character_service import CharacterService
from backend.systems.character.services.relationship_service import RelationshipService
from backend.systems.character.services.mood_service import MoodService
from backend.systems.character.services.goal_service import GoalService
from backend.systems.character.core.character_model import Character
from backend.systems.character.models.relationship import Relationship, RelationshipType
from backend.systems.character.models.mood import (
    CharacterMood,
    EmotionalState,
    MoodIntensity,
)
from backend.systems.character.models.goal import (
    Goal,
    GoalType,
    GoalPriority,
    GoalStatus,
)
from backend.systems.events.event_dispatcher import EventDispatcher


# Mock the get_db_session to return a synchronous session
@pytest.fixture(autouse=True)
def mock_db_session(): pass
    """Create a mock DB session and patch get_db_session to use it."""
    mock_session = MagicMock()
    
    # Create a generator function that yields the mock session
    def mock_get_db_session(): pass
        yield mock_session
    
    # Patch the get_db_session in character_service
    with patch('backend.systems.character.services.character_service.get_db_session', 
              return_value=mock_get_db_session()): pass
        yield mock_session


@pytest.fixture
def mock_event_dispatcher(): pass
    """Create a mock event dispatcher."""
    return MagicMock(spec=EventDispatcher)


@pytest.fixture
def character_service(mock_event_dispatcher, mock_db_session): pass
    """Create a character service with dependencies."""
    service = CharacterService(db_session=mock_db_session)
    service.event_dispatcher = mock_event_dispatcher
    service.data_dir = "/tmp/characters_test"
    return service


@pytest.fixture
def relationship_service(mock_event_dispatcher, mock_db_session): pass
    """Create a relationship service with dependencies."""
    service = RelationshipService(db_session=mock_db_session)
    service.event_dispatcher = mock_event_dispatcher
    service.data_dir = "/tmp/relationships_test"
    return service


@pytest.fixture
def mood_service(mock_event_dispatcher): pass
    """Create a mood service with dependencies."""
    service = MoodService()
    service.event_dispatcher = mock_event_dispatcher
    service.data_dir = "/tmp/moods_test"
    return service


@pytest.fixture
def goal_service(mock_event_dispatcher): pass
    """Create a goal service with dependencies."""
    service = GoalService()
    service.event_dispatcher = mock_event_dispatcher
    service.data_dir = "/tmp/goals_test"
    return service


@pytest.fixture
def integrated_services(
    character_service, relationship_service, mood_service, goal_service
): pass
    """Create integrated services with interconnected references."""
    # Set up cross-references between services
    character_service.relationship_service = relationship_service
    character_service.mood_service = mood_service
    character_service.goal_service = goal_service

    # Mock the persistence methods
    character_service.save_character = MagicMock(return_value=True)
    relationship_service.save_relationships = MagicMock(return_value=True)
    mood_service.save_moods = MagicMock(return_value=True)
    goal_service.save_goals = MagicMock(return_value=True)

    return {
        "character_service": character_service,
        "relationship_service": relationship_service,
        "mood_service": mood_service,
        "goal_service": goal_service,
    }


@pytest.fixture
def sample_character(): pass
    """Create a sample character for testing."""
    character = Character(
        id=str(uuid4()),
        name="Tester",
        race="Human",
        level=1,
        stats={
            "strength": 14,
            "dexterity": 12,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 8,
            "charisma": 13,
            "class": "Warrior"  # Include class as part of stats
        },
        skills=[],
        notes=[],
        created_at=datetime.utcnow(),
    )
    return character


# --- Integration Tests ---


def test_character_creation_with_initial_mood(integrated_services, sample_character): pass
    """Test creating a character with an initial mood."""
    # Setup
    character_service = integrated_services["character_service"]
    mood_service = integrated_services["mood_service"]

    # Mock the character creation
    with patch.object(
        CharacterService, "create_character", return_value=sample_character
    ): pass
        # Execute - create character
        character = character_service.create_character(
            name=sample_character.name,
            race=sample_character.race,
            stats=sample_character.stats,  # Use stats instead of character_class
        )

        # Mock the mood service's get_mood to simulate no existing mood
        with patch.object(MoodService, "get_mood", return_value=None): pass
            # Mock the add_mood_modifier method
            with patch.object(MoodService, "add_mood_modifier") as mock_add_mood_modifier: pass
                # Execute - check character's mood (should create a default one)
                mood = mood_service.get_or_create_default_mood(character.id)

                # Verify
                mock_add_mood_modifier.assert_called_once()
                assert character is not None
                assert character.id == sample_character.id


def test_character_with_relationships_and_moods(integrated_services, sample_character): pass
    """Test a character with relationships and moods."""
    # Setup
    character_service = integrated_services["character_service"]
    relationship_service = integrated_services["relationship_service"]
    mood_service = integrated_services["mood_service"]

    # Create two characters
    character1 = sample_character
    character2 = Character(
        id=str(uuid4()),
        name="NPC",
        race="Elf",
        level=1,
        stats={
            "class": "Mage"
        },
        skills=[],
        notes=[],
        created_at=datetime.utcnow(),
    )

    # Mock character retrieval
    with patch.object(
        CharacterService, "get_character", side_effect=[character1, character2]
    ): pass
        # Mock creating a relationship
        relationship = Relationship(
            id=str(uuid4()),
            source_id=character1.id,
            target_id=character2.id,
            relationship_type=RelationshipType.CHARACTER,
            affinity=75,
            created_at=datetime.utcnow(),
        )

        with patch.object(
            RelationshipService, "create_relationship", return_value=relationship
        ): pass
            # Execute - create relationship
            created_relationship = relationship_service.create_relationship(
                source_id=character1.id,
                target_id=character2.id,
                relationship_type=RelationshipType.CHARACTER,
                affinity=75,
            )

            # Mock the mood creation for both characters
            mood1 = CharacterMood(
                mood_id=str(uuid4()),
                character_id=character1.id,
                emotional_state=EmotionalState.HAPPY,
                intensity=MoodIntensity.MODERATE,
                modifiers=[],
                created_at=datetime.utcnow(),
            )

            mood2 = CharacterMood(
                mood_id=str(uuid4()),
                character_id=character2.id,
                emotional_state=EmotionalState.NEUTRAL,
                intensity=MoodIntensity.LOW,
                modifiers=[],
                created_at=datetime.utcnow(),
            )

            with patch.object(MoodService, "create_mood", side_effect=[mood1, mood2]): pass
                # Execute - create moods
                char1_mood = mood_service.create_mood(
                    character_id=character1.id,
                    emotional_state=EmotionalState.HAPPY,
                    intensity=MoodIntensity.MODERATE,
                )

                char2_mood = mood_service.create_mood(
                    character_id=character2.id,
                    emotional_state=EmotionalState.NEUTRAL,
                    intensity=MoodIntensity.LOW,
                )

                # Now test that a relationship update can affect mood
                with patch.object(
                    RelationshipService,
                    "update_relationship",
                    return_value=relationship,
                ): pass
                    # Mock mood service to verify it receives the mood modifier
                    with patch.object(
                        MoodService, "add_mood_modifier"
                    ) as mock_add_modifier: pass
                        # Execute - update relationship (in a real system, this might trigger mood changes)
                        relationship_service.update_relationship(
                            source_id=character1.id,
                            target_id=character2.id,
                            affinity=30,  # Significant decrease
                        )

                        # In a complete integration test, we would verify that the mood system
                        # was notified of the relationship change
                        # This is a simplified test focusing on the interaction pattern
                        character_service.update_mood_from_relationship_change(
                            relationship, character1.id, -45  # The affinity change
                        )

                        # Verify the mood modifier was added
                        mock_add_modifier.assert_called_once()


def test_character_with_goals(integrated_services, sample_character): pass
    """Test a character with goals."""
    # Setup
    character_service = integrated_services["character_service"]
    goal_service = integrated_services["goal_service"]

    # Mock character retrieval
    with patch.object(CharacterService, "get_character", return_value=sample_character): pass
        # Mock goal creation
        goal = Goal(
            goal_id=str(uuid4()),
            character_id=sample_character.id,
            description="Defeat the dragon",
            type=GoalType.QUEST,
            priority=GoalPriority.HIGH,
            status=GoalStatus.ACTIVE,
            created_at=datetime.utcnow(),
            metadata={"reward": "Dragon treasure"},
        )

        with patch.object(GoalService, "add_goal", return_value=goal): pass
            # Execute - add goal
            created_goal = goal_service.add_goal(
                character_id=sample_character.id,
                description="Defeat the dragon",
                goal_type=GoalType.QUEST,
                priority=GoalPriority.HIGH,
                metadata={"reward": "Dragon treasure"},
            )

            # Verify
            assert created_goal is not None
            assert created_goal.character_id == sample_character.id

            # Mock getting character goals
            with patch.object(
                GoalService, "get_goals_for_character", return_value=[goal]
            ): pass
                # Execute - get character goals
                character_goals = goal_service.get_goals_for_character(
                    sample_character.id
                )

                # Verify
                assert len(character_goals) == 1
                assert character_goals[0].goal_id == goal.goal_id

                # Now test goal completion affecting character
                with patch.object(GoalService, "complete_goal", return_value=goal): pass
                    # Mock character XP gain method
                    with patch.object(
                        CharacterService, "add_experience_points"
                    ) as mock_add_xp: pass
                        # Execute - complete goal
                        completed_goal = goal_service.complete_goal(
                            sample_character.id, goal.goal_id
                        )

                        # In a real system, goal completion might trigger XP gain
                        character_service.process_goal_completion(completed_goal)

                        # Verify XP was added
                        mock_add_xp.assert_called_once()


def test_character_mood_affecting_relationships(integrated_services, sample_character): pass
    """Test character mood affecting relationships."""
    # Setup
    character_service = integrated_services["character_service"]
    relationship_service = integrated_services["relationship_service"]
    mood_service = integrated_services["mood_service"]

    # Create two characters
    character1 = sample_character
    character2 = Character(
        id=str(uuid4()),
        name="NPC",
        race="Elf",
        level=1,
        stats={"class": "Mage"},
        skills=[],
        notes=[],
        created_at=datetime.utcnow(),
    )

    # Mock character retrieval
    with patch.object(
        CharacterService, "get_character", side_effect=[character1, character2]
    ): pass
        # Create a relationship
        relationship = Relationship(
            id=str(uuid4()),
            source_id=character1.id,
            target_id=character2.id,
            relationship_type=RelationshipType.CHARACTER,
            affinity=60,
            created_at=datetime.utcnow(),
        )

        with patch.object(
            RelationshipService, "get_relationship", return_value=relationship
        ): pass
            # Mock get_relationships_by_source to return our relationship
            with patch.object(
                RelationshipService, "get_relationships_by_source", return_value=[relationship]
            ): pass
                # Create an angry mood
                mood = CharacterMood(
                    mood_id=str(uuid4()),
                    character_id=character1.id,
                    emotional_state=EmotionalState.ANGRY,
                    intensity=MoodIntensity.HIGH,
                    modifiers=[],
                    created_at=datetime.utcnow(),
                )

                # Mock mood retrieval to return our angry mood
                with patch.object(MoodService, "get_mood", return_value=mood): pass
                    # Mock the relationship update
                    with patch.object(
                        RelationshipService, "update_relationship"
                    ) as mock_update_relationship: pass
                        # Execute - mood affecting relationship
                        # In a real system, this might be triggered by an event or periodic update
                        character_service.apply_mood_effects_to_relationships(character1.id)

                        # Verify that the relationship was updated (mood affected relationship)
                        mock_update_relationship.assert_called_once()


def test_goals_affecting_mood(integrated_services, sample_character): pass
    """Test how goals affect character moods."""
    # Setup
    character_service = integrated_services["character_service"]
    goal_service = integrated_services["goal_service"]
    mood_service = integrated_services["mood_service"]

    # Mock character retrieval
    with patch.object(CharacterService, "get_character", return_value=sample_character): pass
        # Create a goal
        goal = Goal(
            goal_id=str(uuid4()),
            character_id=sample_character.id,
            description="Find the lost artifact",
            type=GoalType.QUEST,
            priority=GoalPriority.HIGH,
            status=GoalStatus.ACTIVE,
            created_at=datetime.utcnow(),
        )

        with patch.object(GoalService, "get_goal_by_id", return_value=goal): pass
            # Mock the mood service
            with patch.object(
                MoodService, "add_mood_modifier"
            ) as mock_add_mood_modifier: pass
                # Execute - fail the goal, which should affect mood
                with patch.object(GoalService, "fail_goal", return_value=goal): pass
                    failed_goal = goal_service.fail_goal(
                        character_id=sample_character.id,
                        goal_id=goal.goal_id,
                        reason="Could not find the artifact in time",
                    )

                    # In a real system, this might be triggered by the goal failure event
                    character_service.process_goal_failure(failed_goal)

                    # Verify that a mood modifier was added
                    mock_add_mood_modifier.assert_called_once()


def test_complete_character_lifecycle(integrated_services, sample_character): pass
    """Test a complete character lifecycle with all services."""
    # Setup
    character_service = integrated_services["character_service"]
    relationship_service = integrated_services["relationship_service"]
    mood_service = integrated_services["mood_service"]
    goal_service = integrated_services["goal_service"]

    # 1. Create character
    with patch.object(
        CharacterService, "create_character", return_value=sample_character
    ): pass
        character = character_service.create_character(
            name=sample_character.name,
            race=sample_character.race,
            stats=sample_character.stats,  # Use stats instead of character_class
        )

        # 2. Create initial mood
        mood = CharacterMood(
            mood_id=str(uuid4()),
            character_id=character.id,
            emotional_state=EmotionalState.HAPPY,
            intensity=MoodIntensity.MODERATE,
            modifiers=[],
            created_at=datetime.utcnow(),
        )

        with patch.object(MoodService, "create_mood", return_value=mood): pass
            character_mood = mood_service.create_mood(
                character_id=character.id,
                emotional_state=EmotionalState.HAPPY,
                intensity=MoodIntensity.MODERATE,
            )

            # 3. Add a goal
            goal = Goal(
                goal_id=str(uuid4()),
                character_id=character.id,
                description="Become a famous wizard",
                type=GoalType.PERSONAL,
                priority=GoalPriority.MEDIUM,
                status=GoalStatus.ACTIVE,
                created_at=datetime.utcnow(),
                metadata={},
            )
            
            # Add progress attribute for test compatibility
            goal.progress = 0.0
            goal.goal_type = GoalType.PERSONAL

            with patch.object(GoalService, "add_goal", return_value=goal): pass
                character_goal = goal_service.add_goal(
                    character_id=character.id,
                    description="Become a famous wizard",
                    goal_type=GoalType.PERSONAL,
                    priority=GoalPriority.MEDIUM,
                )

                # 4. Create a relationship with an NPC
                npc_id = str(uuid4())
                relationship = Relationship(
                    id=str(uuid4()),
                    source_id=character.id,
                    target_id=npc_id,
                    relationship_type=RelationshipType.CHARACTER,
                    affinity=80,
                    created_at=datetime.utcnow(),
                )

                with patch.object(
                    RelationshipService,
                    "create_relationship",
                    return_value=relationship,
                ): pass
                    character_relationship = relationship_service.create_relationship(
                        source_id=character.id,
                        target_id=npc_id,
                        relationship_type=RelationshipType.CHARACTER,
                        affinity=80,
                    )

                    # 5. Level up character (would affect goal progress)
                    with patch.object(
                        CharacterService, "level_up_character", return_value=character
                    ): pass
                        # Mock goal progress update
                        with patch.object(
                            GoalService, "update_goal_progress"
                        ) as mock_update_progress: pass
                            # Execute - level up
                            character_service.level_up_character(character.id)

                            # Calculate progress level
                            level_progress = min(1.0, character.level / 10.0)
                            
                            # Call the character service method which triggers goal_service.update_goal_progress
                            character_service.update_personal_goal_progress(
                                character, goal
                            )

                            # Verify goal progress was updated
                            mock_update_progress.assert_called_once()

                            # 6. Complete goal and verify rewards
                            with patch.object(
                                GoalService, "complete_goal", return_value=goal
                            ): pass
                                # Mock mood update from goal completion
                                with patch.object(
                                    MoodService, "add_mood_modifier"
                                ) as mock_add_mood_modifier: pass
                                    # Execute - complete goal
                                    goal_service.complete_goal(character.id, goal.goal_id)

                                    # Update mood based on goal completion
                                    character_service.process_goal_completion(goal)

                                    # Verify mood was updated
                                    mock_add_mood_modifier.assert_called_once()

                                    # 7. Final step - character progression check
                                    assert character is not None
                                    assert character_mood is not None
                                    assert character_goal is not None
                                    assert character_relationship is not None
