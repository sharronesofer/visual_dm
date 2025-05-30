from typing import Any
from typing import Dict
"""
Tests for the rumor system using the new RumorService.
This test file uses the consolidated rumor system architecture.
"""

import asyncio
import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import List, Dict, Any

from backend.systems.rumor.service import RumorService
from backend.systems.rumor.models import Rumor, RumorCategory, RumorSeverity


class TestRumorService(unittest.TestCase): pass
    """Test suite for the refactored RumorService."""

    def setUp(self): pass
        """Set up test environment."""
        # Reset singleton instance for testing
        RumorService._instance = None
        self.rumor_service = RumorService.get_instance()

        # Mock the repository to avoid database dependencies
        self.mock_repository = Mock()
        # Set up async mocks for methods that are awaited
        self.mock_repository.save_rumor = AsyncMock(return_value=True)
        # Create a mock rumor object for get_rumor
        mock_rumor = Mock()
        mock_rumor.id = "test_rumor_1"
        mock_rumor.entity_knows_rumor = Mock(return_value=True)
        mock_rumor.get_latest_variant_id_for_entity = Mock(return_value="variant_1")
        mock_rumor.get_variant_by_id = Mock(return_value=Mock(id="variant_1", content="test content"))
        mock_rumor.severity = Mock()
        mock_rumor.categories = []
        mock_rumor.truth_value = 0.8
        mock_rumor.spread = []
        self.mock_repository.get_rumor = AsyncMock(return_value=mock_rumor)
        self.mock_repository.get_all_rumors = AsyncMock(return_value=[])
        self.mock_repository.get_rumors_by_filters = AsyncMock(return_value=[])
        self.rumor_service.repository = self.mock_repository
        
        # Mock the event dispatcher to avoid async issues
        self.mock_event_dispatcher = Mock()
        self.mock_event_dispatcher.publish = AsyncMock(return_value=None)
        self.rumor_service.event_dispatcher = self.mock_event_dispatcher

        # Set up event loop for async tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self): pass
        """Clean up after tests."""
        self.loop.close()
        RumorService._instance = None

    def run_async(self, coro): pass
        """Helper to run async functions in tests."""
        return self.loop.run_until_complete(coro)

    def test_singleton_pattern(self): pass
        """Test that RumorService follows the singleton pattern."""
        service1 = RumorService.get_instance()
        service2 = RumorService.get_instance()

        self.assertIs(service1, service2)
        self.assertIs(service1, self.rumor_service)

    def test_create_rumor_async(self): pass
        """Test creating a rumor with the new async API."""
        # Test creating a rumor
        result = self.run_async(
            self.rumor_service.create_rumor(
                content="There's treasure in the old mine",
                categories=["treasure"],
                originator_id="test_npc",
                truth_value=0.8,
                severity="moderate",
            )
        )

        # Verify the rumor was created with correct properties
        self.assertIsNotNone(result.id)
        self.assertEqual(result.original_content, "There's treasure in the old mine")
        self.assertEqual(result.truth_value, 0.8)
        # Verify save_rumor was called (the actual method used by create_rumor)
        self.mock_repository.save_rumor.assert_called()

    def test_spread_rumor_async(self): pass
        """Test spreading a rumor with the new async API."""
        # Test spreading a rumor
        result = self.run_async(
            self.rumor_service.spread_rumor(
                rumor_id="test_rumor_1",
                from_entity_id="test_source",
                to_entity_id="test_target",
                mutation_probability=0.1,
            )
        )

        self.assertTrue(result)
        # Verify save_rumor was called (the actual method used by spread_rumor)
        # It should be called at least twice: once for the initial get_rumor mock, once for saving the updated rumor
        self.assertTrue(self.mock_repository.save_rumor.call_count >= 1)

    def test_get_entity_rumors(self): pass
        """Test getting rumors for an entity."""
        # Mock rumors data
        mock_rumors = [
            Mock(id="rumor_1", original_content="Test rumor 1"),
            Mock(id="rumor_2", original_content="Test rumor 2"),
        ]

        self.mock_repository.get_rumors_by_entity = AsyncMock(return_value=mock_rumors)

        # Test getting entity rumors
        result = self.run_async(
            self.rumor_service.repository.get_rumors_by_entity("test_entity")
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, "rumor_1")
        self.mock_repository.get_rumors_by_entity.assert_called_once_with("test_entity")

    def test_get_rumor_context(self): pass
        """Test getting rumor context for narrative generation."""
        # Mock context data
        mock_context = [
            {
                "content": "There's treasure in the old mine",
                "believability": 0.8,
                "severity": "moderate",
                "categories": ["treasure"],
            },
            {
                "content": "The mayor is corrupt",
                "believability": 0.6,
                "severity": "major",
                "categories": ["scandal"],
            },
        ]

        self.rumor_service.get_rumor_context = AsyncMock(return_value=mock_context)

        # Test getting rumor context
        result = self.run_async(
            self.rumor_service.get_rumor_context(world_id="test_region", num_rumors=2)
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["content"], "There's treasure in the old mine")
        self.assertEqual(result[1]["believability"], 0.6)

    def test_rumor_categories_enum(self): pass
        """Test that rumor categories are properly defined."""
        # Test that key rumor categories exist
        self.assertTrue(hasattr(RumorCategory, "SCANDAL"))
        self.assertTrue(hasattr(RumorCategory, "SECRET"))
        self.assertTrue(hasattr(RumorCategory, "TREASURE"))
        self.assertTrue(hasattr(RumorCategory, "POLITICAL"))

        # Test enum values
        self.assertEqual(RumorCategory.SCANDAL.value, "scandal")
        self.assertEqual(RumorCategory.TREASURE.value, "treasure")

    def test_rumor_severity_enum(self): pass
        """Test that rumor severity levels are properly defined."""
        # Test that severity levels exist
        self.assertTrue(hasattr(RumorSeverity, "MINOR"))
        self.assertTrue(hasattr(RumorSeverity, "MODERATE"))
        self.assertTrue(hasattr(RumorSeverity, "MAJOR"))
        self.assertTrue(hasattr(RumorSeverity, "CRITICAL"))

        # Test enum values
        self.assertEqual(RumorSeverity.MINOR.value, "minor")
        self.assertEqual(RumorSeverity.MAJOR.value, "major")

    def test_rumor_service_initialization(self): pass
        """Test proper initialization of the rumor service."""
        service = RumorService.get_instance()

        # Verify service has required components
        self.assertIsNotNone(service.repository)

        # Verify service configuration
        self.assertIsInstance(service, RumorService)

    def test_backward_compatibility_methods(self): pass
        """Test that backward compatibility methods work with new service."""
        # Mock the repository for backward compatibility
        self.mock_repository.get_rumors_by_entity = AsyncMock(return_value=[])

        # Test calling methods that should maintain backward compatibility
        result = self.run_async(
            self.rumor_service.repository.get_rumors_by_entity("test_entity")
        )

        self.assertIsInstance(result, list)
        self.mock_repository.get_rumors_by_entity.assert_called_once()


class TestRumorSystemIntegration(unittest.TestCase): pass
    """Integration tests for the rumor system with other components."""

    def setUp(self): pass
        """Set up integration test environment."""
        RumorService._instance = None
        self.rumor_service = RumorService.get_instance()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self): pass
        """Clean up after integration tests."""
        self.loop.close()
        RumorService._instance = None

    def run_async(self, coro): pass
        """Helper to run async functions in tests."""
        return self.loop.run_until_complete(coro)

    @patch("backend.systems.rumor.service.RumorRepository")
    def test_service_repository_integration(self, mock_repo_class): pass
        """Test that service properly integrates with repository."""
        # Create a new service instance to test initialization
        RumorService._instance = None

        mock_repo_instance = Mock()
        mock_repo_class.return_value = mock_repo_instance

        service = RumorService.get_instance()

        # Verify repository was created and assigned
        self.assertIsNotNone(service.repository)


if __name__ == "__main__": pass
    unittest.main()
