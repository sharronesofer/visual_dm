from backend.systems.quest.models import QuestStep
from backend.systems.quest.models import QuestStep
from backend.systems.quest.models import QuestStep
from backend.systems.quest.models import QuestStep
from backend.systems.quest.models import QuestStep
from backend.systems.quest.models import QuestStep
import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from backend.systems.quest.models import Quest, QuestStep

# This line is no longer needed since we use the new event system
# patch("backend.core.event_bus", MagicMock()).start()


class TestQuestStep(unittest.TestCase): pass
    """Test cases for the QuestStep model."""

    def test_quest_step_creation(self): pass
        """Test creating a basic QuestStep."""
        step = QuestStep(
            id=1,
            description="Find the lost sword",
            type="collect",
            target_item_id="item_123",
        )

        self.assertEqual(step.id, 1)
        self.assertEqual(step.description, "Find the lost sword")
        self.assertEqual(step.type, "collect")
        self.assertEqual(step.target_item_id, "item_123")
        self.assertFalse(step.completed)
        self.assertEqual(step.quantity, 1)
        self.assertEqual(step.required_count, 1)
        self.assertEqual(step.current_count, 0)

    def test_quest_step_to_dict(self): pass
        """Test converting a QuestStep to dictionary."""
        step = QuestStep(
            id=2,
            description="Talk to the blacksmith",
            type="dialogue",
            target_npc_id="npc_456",
            required_skills=[{"skill": "persuasion", "level": 3}],
        )

        step_dict = step.to_dict()

        self.assertEqual(step_dict["id"], 2)
        self.assertEqual(step_dict["description"], "Talk to the blacksmith")
        self.assertEqual(step_dict["type"], "dialogue")
        self.assertEqual(step_dict["target_npc_id"], "npc_456")
        self.assertEqual(
            step_dict["required_skills"], [{"skill": "persuasion", "level": 3}]
        )
        self.assertFalse(step_dict["completed"])

    def test_quest_step_from_dict(self): pass
        """Test creating a QuestStep from a dictionary."""
        step_dict = {
            "id": 3,
            "description": "Defeat the bandit leader",
            "type": "kill",
            "target_enemy_id": "enemy_789",
            "completed": True,
            "required_count": 1,
            "current_count": 1,
        }

        step = QuestStep.from_dict(step_dict)

        self.assertEqual(step.id, 3)
        self.assertEqual(step.description, "Defeat the bandit leader")
        self.assertEqual(step.type, "kill")
        self.assertEqual(step.target_enemy_id, "enemy_789")
        self.assertTrue(step.completed)
        self.assertEqual(step.required_count, 1)
        self.assertEqual(step.current_count, 1)

    def test_quest_step_from_dict_with_defaults(self): pass
        """Test that QuestStep.from_dict correctly fills in defaults."""
        step_dict = {"id": 4, "description": "Simple test step", "type": "visit"}

        step = QuestStep.from_dict(step_dict)

        self.assertEqual(step.id, 4)
        self.assertEqual(step.description, "Simple test step")
        self.assertEqual(step.type, "visit")
        self.assertFalse(step.completed)
        self.assertEqual(step.required_items, [])
        self.assertEqual(step.required_skills, [])
        self.assertIsNone(step.target_npc_id)
        self.assertEqual(step.quantity, 1)
        self.assertEqual(step.required_count, 1)
        self.assertEqual(step.current_count, 0)


class TestQuest(unittest.TestCase): pass
    """Test cases for the Quest model."""

    def test_quest_creation(self): pass
        """Test creating a basic Quest."""
        quest = Quest(
            id="quest_123",
            title="The Lost Sword",
            description="Find the king's lost sword",
        )

        self.assertEqual(quest.id, "quest_123")
        self.assertEqual(quest.title, "The Lost Sword")
        self.assertEqual(quest.description, "Find the king's lost sword")
        self.assertEqual(quest.status, "pending")
        self.assertEqual(quest.type, "SideQuest")
        self.assertEqual(quest.difficulty, "medium")
        self.assertEqual(quest.level, 1)
        self.assertEqual(quest.theme, "general")
        self.assertIsNone(quest.motif)
        self.assertEqual(quest.motif_intensity, 0)

        # Check timestamps were generated
        self.assertIsNotNone(quest.created_at)
        self.assertIsNotNone(quest.updated_at)
        self.assertIsNone(quest.completed_at)

    def test_quest_with_steps(self): pass
        """Test creating a Quest with steps."""
        steps = [
            QuestStep(
                id=1,
                description="Find the map",
                type="collect",
                target_item_id="item_map",
            ),
            QuestStep(
                id=2,
                description="Talk to the captain",
                type="dialogue",
                target_npc_id="npc_captain",
            ),
        ]

        quest = Quest(
            id="quest_456",
            title="Treasure Hunt",
            description="Find the hidden treasure",
            steps=steps,
        )

        self.assertEqual(len(quest.steps), 2)
        self.assertEqual(quest.steps[0].id, 1)
        self.assertEqual(quest.steps[1].description, "Talk to the captain")

    def test_quest_to_dict(self): pass
        """Test converting a Quest to dictionary."""
        steps = [
            QuestStep(
                id=1,
                description="Find the map",
                type="collect",
                target_item_id="item_map",
            ),
            QuestStep(
                id=2,
                description="Talk to the captain",
                type="dialogue",
                target_npc_id="npc_captain",
            ),
        ]

        quest = Quest(
            id="quest_789",
            title="Adventure Begins",
            description="Start your adventure",
            steps=steps,
            status="active",
            player_id="player_123",
            rewards={"gold": 100, "xp": 500},
        )

        quest_dict = quest.to_dict()

        self.assertEqual(quest_dict["id"], "quest_789")
        self.assertEqual(quest_dict["title"], "Adventure Begins")
        self.assertEqual(quest_dict["status"], "active")
        self.assertEqual(len(quest_dict["steps"]), 2)
        self.assertEqual(quest_dict["steps"][0]["id"], 1)
        self.assertEqual(quest_dict["player_id"], "player_123")
        self.assertEqual(quest_dict["rewards"], {"gold": 100, "xp": 500})

    def test_quest_from_dict(self): pass
        """Test creating a Quest from a dictionary."""
        now = datetime.utcnow().isoformat()
        quest_dict = {
            "id": "quest_abc",
            "title": "The Dark Forest",
            "description": "Explore the dark forest",
            "status": "completed",
            "type": "MainQuest",
            "difficulty": "hard",
            "level": 5,
            "theme": "exploration",
            "motif": "Mystery",
            "motif_intensity": 3,
            "player_id": "player_xyz",
            "created_at": now,
            "updated_at": now,
            "completed_at": now,
            "steps": [
                {
                    "id": 1,
                    "description": "Enter the forest",
                    "type": "visit",
                    "target_location_id": "loc_forest",
                    "completed": True,
                },
                {
                    "id": 2,
                    "description": "Find the ancient tree",
                    "type": "visit",
                    "target_location_id": "loc_tree",
                    "completed": True,
                },
            ],
            "rewards": {"item": "magic_amulet", "xp": 1000},
        }

        quest = Quest.from_dict(quest_dict)

        self.assertEqual(quest.id, "quest_abc")
        self.assertEqual(quest.title, "The Dark Forest")
        self.assertEqual(quest.description, "Explore the dark forest")
        self.assertEqual(quest.status, "completed")
        self.assertEqual(quest.type, "MainQuest")
        self.assertEqual(quest.difficulty, "hard")
        self.assertEqual(quest.level, 5)
        self.assertEqual(quest.theme, "exploration")
        self.assertEqual(quest.motif, "Mystery")
        self.assertEqual(quest.motif_intensity, 3)
        self.assertEqual(quest.player_id, "player_xyz")
        self.assertEqual(quest.created_at, now)
        self.assertEqual(quest.updated_at, now)
        self.assertEqual(quest.completed_at, now)
        self.assertEqual(len(quest.steps), 2)
        self.assertTrue(quest.steps[0].completed)
        self.assertEqual(quest.steps[1].target_location_id, "loc_tree")
        self.assertEqual(quest.rewards, {"item": "magic_amulet", "xp": 1000})

    def test_quest_is_complete(self): pass
        """Test the is_complete method."""
        # Create a quest with incomplete steps
        steps = [
            QuestStep(id=1, description="Step 1", type="collect", completed=True),
            QuestStep(id=2, description="Step 2", type="dialogue", completed=False),
        ]

        quest = Quest(
            id="quest_test",
            title="Test Quest",
            description="Test description",
            steps=steps,
        )

        # Initially, not all steps are complete
        self.assertFalse(quest.is_complete())

        # Complete all steps
        quest.steps[1].completed = True

        # Now the quest should be complete
        self.assertTrue(quest.is_complete())

    @patch("backend.systems.events.get_event_dispatcher")
    def test_quest_update_step(self, mock_event_dispatcher): pass
        """Test the update_step method."""
        # Mock EventBus for testing to avoid actual event emission
        mock_event_bus = MagicMock()
        mock_event_dispatcher.return_value = mock_event_bus

        steps = [
            QuestStep(id=1, description="Step 1", type="collect", completed=False),
            QuestStep(id=2, description="Step 2", type="dialogue", completed=False),
        ]

        quest = Quest(
            id="quest_update",
            title="Update Quest",
            description="Test updating steps",
            steps=steps,
            player_id="player_123",
            status="in-progress",
        )

        # Update a step to be completed
        old_updated_at = quest.updated_at
        result = quest.update_step(1, True)

        # Verify step was updated
        self.assertTrue(result)
        self.assertTrue(quest.steps[0].completed)
        self.assertFalse(quest.steps[1].completed)

        # Verify updated_at timestamp changed
        self.assertNotEqual(quest.updated_at, old_updated_at)

        # Verify quest is still in progress (one step remains)
        self.assertEqual(quest.status, "in-progress")
        self.assertIsNone(quest.completed_at)

        # No event should be published yet
        mock_event_bus.publish.assert_not_called()

        # Update the second step to complete the quest
        result = quest.update_step(2, True)

        # Verify step and quest are updated
        self.assertTrue(result)
        self.assertTrue(quest.steps[1].completed)
        self.assertEqual(quest.status, "completed")
        self.assertIsNotNone(quest.completed_at)

        # Verify event was published
        mock_event_bus.publish.assert_called_once()
        # Get the call arguments to check the event
        call_args = mock_event_bus.publish.call_args[0]
        event = call_args[0]
        
        # Check that a QuestUpdatedEvent was published with correct data
        self.assertEqual(event.quest_id, "quest_update")
        self.assertEqual(event.character_id, None)  # player_123 is not a pure integer
        self.assertEqual(event.old_status, "in-progress")
        self.assertEqual(event.new_status, "completed")
        self.assertEqual(event.progress, 100.0)
        self.assertTrue(event.is_completed)
        self.assertFalse(event.rewards_given)

    def test_quest_update_nonexistent_step(self): pass
        """Test updating a nonexistent step."""
        quest = Quest(
            id="quest_nonexistent",
            title="Nonexistent Step Quest",
            description="Test with nonexistent step",
            steps=[QuestStep(id=1, description="Only Step", type="collect")],
        )

        # Try to update a nonexistent step ID
        result = quest.update_step(99, True)

        # Should return False for failure
        self.assertFalse(result)

    def test_quest_post_init(self): pass
        """Test the post init method."""
        # Create a quest without timestamps
        quest = Quest(
            id="quest_timestamps",
            title="Timestamps Quest",
            description="Test timestamp generation",
        )

        # Verify timestamps were generated
        self.assertIsNotNone(quest.created_at)
        self.assertIsNotNone(quest.updated_at)
        self.assertIsNone(quest.completed_at)

        # Create a quest with provided timestamps
        now = datetime.utcnow().isoformat()
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()

        quest = Quest(
            id="quest_custom_timestamps",
            title="Custom Timestamps",
            description="Test custom timestamps",
            created_at=yesterday,
            updated_at=now,
        )

        # Verify timestamps were preserved
        self.assertEqual(quest.created_at, yesterday)
        self.assertEqual(quest.updated_at, now)

    @patch("backend.systems.events.get_event_dispatcher")
    def test_update_step_marks_uncompleted_quest(self, mock_event_dispatcher): pass
        """Test updating a step to uncompleted on a completed quest."""
        # Mock EventBus for testing
        mock_event_bus = MagicMock()
        mock_event_dispatcher.return_value = mock_event_bus

        # Create a completed quest
        steps = [
            QuestStep(id=1, description="Step 1", type="collect", completed=True),
            QuestStep(id=2, description="Step 2", type="dialogue", completed=True),
        ]

        completed_time = datetime.utcnow().isoformat()
        quest = Quest(
            id="quest_revert",
            title="Revert Quest",
            description="Test reverting quest completion",
            steps=steps,
            status="completed",
            completed_at=completed_time,
            player_id="player_456",
        )

        # Verify quest starts as completed
        self.assertEqual(quest.status, "completed")
        self.assertEqual(quest.completed_at, completed_time)
        self.assertTrue(quest.is_complete())

        # Update a step to be incomplete
        result = quest.update_step(1, False)

        # Verify step was updated and quest is no longer complete
        self.assertTrue(result)
        self.assertFalse(quest.steps[0].completed)
        self.assertTrue(quest.steps[1].completed)

        # Quest should no longer be complete
        self.assertFalse(quest.is_complete())

        # Status should still be "completed" since we don't change status when uncompleting steps
        # This behavior may differ from QuestStateManager which should be tested separately
        self.assertEqual(quest.status, "completed")

        # No new event should be published for uncompleting a step
        mock_event_bus.publish.assert_not_called()

    def test_quest_with_time_requirements(self): pass
        """Test quest with time requirements."""
        time_req = {
            "start_time": "08:00",
            "end_time": "18:00",
            "days": ["Monday", "Wednesday"],
        }
        step = QuestStep(
            id=1,
            description="Time-limited step",
            type="visit",
            time_requirement=time_req,
        )

        quest = Quest(
            id="time_quest",
            title="Time Quest",
            description="Quest with time requirements",
            steps=[step],
            time_dependent=True,
        )

        # Verify time requirement was stored
        self.assertEqual(quest.steps[0].time_requirement, time_req)
        self.assertTrue(quest.time_dependent)

        # Verify dictionary conversion preserves time requirements
        quest_dict = quest.to_dict()
        self.assertEqual(quest_dict["steps"][0]["time_requirement"], time_req)
        self.assertTrue(quest_dict["time_dependent"])


if __name__ == "__main__": pass
    unittest.main()
