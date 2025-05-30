from backend.systems.quest.quest_manager import QuestManager
from backend.systems.quest.quest_manager import QuestManager
from backend.systems.quest.quest_manager import QuestManager
from backend.systems.quest.quest_manager import QuestManager
from backend.systems.quest.quest_manager import QuestManager
from backend.systems.quest.quest_manager import QuestManager
import unittest
from unittest.mock import patch, MagicMock
from backend.systems.quest.quest_manager import QuestManager
from backend.systems.shared.utils.common.error import ValidationError, NotFoundError
from dataclasses import field


class TestQuestManager(unittest.TestCase): pass
    """Test cases for the QuestManager class."""

    def setUp(self): pass
        """Set up for each test."""
        self.manager = QuestManager()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_update_step_status_success(self, mock_repository): pass
        """Test updating a step status successfully."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "steps": [
                {"id": 0, "description": "Step 1", "completed": False},
                {"id": 1, "description": "Step 2", "completed": False},
            ],
            "status": "in-progress",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call the method
        result = self.manager.update_step_status("quest_123", 1, True)

        # Verify the step was updated
        self.assertTrue(result["steps"][1]["completed"])
        self.assertEqual(result["status"], "in-progress")  # Not all steps complete yet

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("quest_123")
        mock_repository.update_quest.assert_called_once_with(
            "quest_123", mock_quest_data
        )

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_update_step_status_complete_quest(self, mock_repository): pass
        """Test updating the last incomplete step to complete the quest."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "steps": [
                {"id": 0, "description": "Step 1", "completed": True},
                {"id": 1, "description": "Step 2", "completed": False},
            ],
            "status": "in-progress",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call the method
        result = self.manager.update_step_status("quest_123", 1, True)

        # Verify the quest status was updated
        self.assertTrue(result["steps"][1]["completed"])
        self.assertEqual(result["status"], "completed")

        # Verify the repository was called correctly
        mock_repository.update_quest.assert_called_once_with(
            "quest_123", mock_quest_data
        )

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_update_step_status_quest_not_found(self, mock_repository): pass
        """Test updating a step for a nonexistent quest."""
        # Mock the quest repository
        mock_repository.get_quest.return_value = None

        # Call should raise NotFoundError
        with self.assertRaises(NotFoundError): pass
            self.manager.update_step_status("nonexistent_quest", 0, True)

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("nonexistent_quest")
        mock_repository.update_quest.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_update_step_status_invalid_step(self, mock_repository): pass
        """Test updating a nonexistent step."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "steps": [{"id": 0, "description": "Step 1", "completed": False}],
            "status": "in-progress",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call should raise ValidationError
        with self.assertRaises(ValidationError): pass
            self.manager.update_step_status("quest_123", 5, True)

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("quest_123")
        mock_repository.update_quest.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_update_step_revert_to_in_progress(self, mock_repository): pass
        """Test reverting a completed quest to in-progress."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "steps": [
                {"id": 0, "description": "Step 1", "completed": True},
                {"id": 1, "description": "Step 2", "completed": True},
            ],
            "status": "completed",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call the method
        result = self.manager.update_step_status("quest_123", 1, False)

        # Verify the quest status was reverted
        self.assertFalse(result["steps"][1]["completed"])
        self.assertEqual(result["status"], "in-progress")

        # Verify the repository was called correctly
        mock_repository.update_quest.assert_called_once_with(
            "quest_123", mock_quest_data
        )

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_accept_quest_success(self, mock_repository): pass
        """Test accepting a quest successfully."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "available",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call the method
        result = self.manager.accept_quest("quest_123", "player_123")

        # Verify the quest was updated
        self.assertEqual(result["status"], "in-progress")
        self.assertEqual(result["player_id"], "player_123")

        # Verify the repository was called correctly
        mock_repository.update_quest.assert_called_once_with(
            "quest_123", mock_quest_data
        )
        mock_repository.create_journal_entry.assert_called_once()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_accept_quest_not_found(self, mock_repository): pass
        """Test accepting a nonexistent quest."""
        # Mock the quest repository
        mock_repository.get_quest.return_value = None

        # Call should raise NotFoundError
        with self.assertRaises(NotFoundError): pass
            self.manager.accept_quest("nonexistent_quest", "player_123")

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("nonexistent_quest")
        mock_repository.update_quest.assert_not_called()
        mock_repository.create_journal_entry.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_accept_quest_invalid_status(self, mock_repository): pass
        """Test accepting a quest with invalid status."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "completed",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call should raise ValidationError
        with self.assertRaises(ValidationError): pass
            self.manager.accept_quest("quest_123", "player_123")

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("quest_123")
        mock_repository.update_quest.assert_not_called()
        mock_repository.create_journal_entry.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_abandon_quest_success(self, mock_repository): pass
        """Test abandoning a quest successfully."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "in-progress",
            "player_id": "player_123",
            "location": "test_location",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call the method
        result = self.manager.abandon_quest("quest_123", "player_123")

        # Verify the quest was updated
        self.assertEqual(result["status"], "abandoned")

        # Verify the repository was called correctly
        mock_repository.update_quest.assert_called_once_with(
            "quest_123", mock_quest_data
        )
        mock_repository.create_journal_entry.assert_called_once()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_abandon_quest_not_found(self, mock_repository): pass
        """Test abandoning a nonexistent quest."""
        # Mock the quest repository
        mock_repository.get_quest.return_value = None

        # Call should raise NotFoundError
        with self.assertRaises(NotFoundError): pass
            self.manager.abandon_quest("nonexistent_quest", "player_123")

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("nonexistent_quest")
        mock_repository.update_quest.assert_not_called()
        mock_repository.create_journal_entry.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_abandon_quest_wrong_player(self, mock_repository): pass
        """Test abandoning a quest with wrong player."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "in-progress",
            "player_id": "player_456",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call should raise ValidationError
        with self.assertRaises(ValidationError): pass
            self.manager.abandon_quest("quest_123", "player_123")

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("quest_123")
        mock_repository.update_quest.assert_not_called()
        mock_repository.create_journal_entry.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_abandon_quest_invalid_status(self, mock_repository): pass
        """Test abandoning a quest with invalid status."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "available",
            "player_id": "player_123",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call should raise ValidationError
        with self.assertRaises(ValidationError): pass
            self.manager.abandon_quest("quest_123", "player_123")

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("quest_123")
        mock_repository.update_quest.assert_not_called()
        mock_repository.create_journal_entry.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_complete_quest_success(self, mock_repository): pass
        """Test completing a quest successfully."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "in-progress",
            "player_id": "player_123",
            "steps": [
                {"id": 0, "description": "Step 1", "completed": True},
                {"id": 1, "description": "Step 2", "completed": False},
            ],
            "location": "test_location",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call the method
        result = self.manager.complete_quest("quest_123", "player_123")

        # Verify the quest was updated
        self.assertEqual(result["status"], "completed")
        self.assertTrue(all(step["completed"] for step in result["steps"]))

        # Verify the repository was called correctly
        mock_repository.update_quest.assert_called_once_with(
            "quest_123", mock_quest_data
        )
        mock_repository.create_journal_entry.assert_called_once()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_complete_quest_not_found(self, mock_repository): pass
        """Test completing a nonexistent quest."""
        # Mock the quest repository
        mock_repository.get_quest.return_value = None

        # Call should raise NotFoundError
        with self.assertRaises(NotFoundError): pass
            self.manager.complete_quest("nonexistent_quest", "player_123")

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("nonexistent_quest")
        mock_repository.update_quest.assert_not_called()
        mock_repository.create_journal_entry.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_complete_quest_wrong_player(self, mock_repository): pass
        """Test completing a quest with wrong player."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "in-progress",
            "player_id": "player_456",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call should raise ValidationError
        with self.assertRaises(ValidationError): pass
            self.manager.complete_quest("quest_123", "player_123")

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("quest_123")
        mock_repository.update_quest.assert_not_called()
        mock_repository.create_journal_entry.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_fail_quest_success(self, mock_repository): pass
        """Test failing a quest successfully."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "in-progress",
            "player_id": "player_123",
            "location": "test_location",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call the method
        reason = "Player died during quest"
        result = self.manager.fail_quest("quest_123", "player_123", reason)

        # Verify the quest was updated
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["fail_reason"], reason)

        # Verify the repository was called correctly
        mock_repository.update_quest.assert_called_once_with(
            "quest_123", mock_quest_data
        )
        mock_repository.create_journal_entry.assert_called_once()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_fail_quest_no_reason_provided(self, mock_repository): pass
        """Test failing a quest without providing a reason."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "in-progress",
            "player_id": "player_123",
            "location": "test_location",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call the method without a reason
        result = self.manager.fail_quest("quest_123", "player_123")

        # Verify the quest was updated with a default reason
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["fail_reason"], "Unknown reason")

        # Verify the repository was called correctly
        mock_repository.update_quest.assert_called_once_with(
            "quest_123", mock_quest_data
        )
        mock_repository.create_journal_entry.assert_called_once()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_fail_quest_not_found(self, mock_repository): pass
        """Test failing a nonexistent quest."""
        # Mock the quest repository
        mock_repository.get_quest.return_value = None

        # Call should raise NotFoundError
        with self.assertRaises(NotFoundError): pass
            self.manager.fail_quest("nonexistent_quest", "player_123")

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("nonexistent_quest")
        mock_repository.update_quest.assert_not_called()
        mock_repository.create_journal_entry.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_fail_quest_wrong_player(self, mock_repository): pass
        """Test failing a quest with wrong player."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "in-progress",
            "player_id": "player_456",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call should raise ValidationError
        with self.assertRaises(ValidationError): pass
            self.manager.fail_quest("quest_123", "player_123")

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("quest_123")
        mock_repository.update_quest.assert_not_called()
        mock_repository.create_journal_entry.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_fail_quest_invalid_status(self, mock_repository): pass
        """Test failing a quest with invalid status."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "available",
            "player_id": "player_123",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call should raise ValidationError
        with self.assertRaises(ValidationError): pass
            self.manager.fail_quest("quest_123", "player_123")

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("quest_123")
        mock_repository.update_quest.assert_not_called()
        mock_repository.create_journal_entry.assert_not_called()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_complete_quest_already_completed_steps(self, mock_repository): pass
        """Test completing a quest when all steps are already completed."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "in-progress",
            "player_id": "player_123",
            "steps": [
                {"id": 0, "description": "Step 1", "completed": True},
                {"id": 1, "description": "Step 2", "completed": True},
            ],
            "location": "test_location",
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call the method
        result = self.manager.complete_quest("quest_123", "player_123")

        # Verify the quest was updated
        self.assertEqual(result["status"], "completed")

        # Steps should still be completed
        self.assertTrue(all(step["completed"] for step in result["steps"]))

        # Verify the repository was called correctly
        mock_repository.update_quest.assert_called_once_with(
            "quest_123", mock_quest_data
        )
        mock_repository.create_journal_entry.assert_called_once()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_complete_quest_no_steps(self, mock_repository): pass
        """Test completing a quest that has no steps."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "in-progress",
            "player_id": "player_123",
            "location": "test_location",
            # No steps field
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call the method
        result = self.manager.complete_quest("quest_123", "player_123")

        # Verify the quest was updated
        self.assertEqual(result["status"], "completed")

        # Verify the repository was called correctly
        mock_repository.update_quest.assert_called_once_with(
            "quest_123", mock_quest_data
        )
        mock_repository.create_journal_entry.assert_called_once()

    @patch("backend.systems.quest.quest_manager.QuestRepository")
    def test_update_step_with_null_steps(self, mock_repository): pass
        """Test updating a step when steps field is null."""
        # Mock the quest repository
        mock_quest_data = {
            "id": "quest_123",
            "title": "Test Quest",
            "status": "in-progress",
            "player_id": "player_123",
            "steps": None,  # Explicitly null steps
        }
        mock_repository.get_quest.return_value = mock_quest_data

        # Call should raise ValidationError
        with self.assertRaises(ValidationError): pass
            self.manager.update_step_status("quest_123", 0, True)

        # Verify the repository was called correctly
        mock_repository.get_quest.assert_called_once_with("quest_123")
        mock_repository.update_quest.assert_not_called()


if __name__ == "__main__": pass
    unittest.main()
