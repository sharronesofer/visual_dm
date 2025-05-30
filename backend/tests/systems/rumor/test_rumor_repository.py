"""
Tests for rumor repository.

This module tests the rumor repository functionality including storage, retrieval,
and filtering of rumors.
"""

import unittest
import asyncio
import tempfile
import shutil
import os
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

from backend.systems.rumor.repository import RumorRepository
from backend.systems.rumor.models.rumor import (
    Rumor,
    RumorVariant,
    RumorSpread,
    RumorCategory,
    RumorSeverity,
)


class TestRumorRepository(unittest.TestCase): pass
    """Test case for rumor repository."""

    def setUp(self): pass
        """Set up test environment."""
        # Create temporary directory for test storage
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, "test_rumors/")
        
        # Reset singleton
        RumorRepository._instance = None
        
        # Create repository instance
        self.repository = RumorRepository(storage_path=self.storage_path)

    def tearDown(self): pass
        """Clean up test environment."""
        # Remove temporary directory
        if os.path.exists(self.temp_dir): pass
            shutil.rmtree(self.temp_dir)
        
        # Reset singleton
        RumorRepository._instance = None

    def test_module_imports(self): pass
        """Test that all necessary modules can be imported."""
        from backend.systems.rumor.repository import RumorRepository
        self.assertIsNotNone(RumorRepository)

    def test_repository_initialization(self): pass
        """Test repository initialization."""
        self.assertEqual(self.repository.storage_path, self.storage_path)
        self.assertTrue(os.path.exists(self.storage_path))
        self.assertIsInstance(self.repository._rumor_cache, dict)
        self.assertIsInstance(self.repository._world_rumor_cache, dict)

    def test_singleton_pattern(self): pass
        """Test that repository follows singleton pattern."""
        repo1 = RumorRepository.get_instance(storage_path=self.storage_path)
        repo2 = RumorRepository.get_instance(storage_path=self.storage_path)
        self.assertIs(repo1, repo2)

    async def test_save_and_get_rumor(self): pass
        """Test saving and retrieving a rumor."""
        # Create test rumor
        rumor = Rumor(
            originator_id="entity_1",
            original_content="The king has hidden treasure.",
            categories=[RumorCategory.TREASURE],
            severity=RumorSeverity.MODERATE,
            truth_value=0.8,
        )

        # Save rumor
        await self.repository.save_rumor(rumor)

        # Check that it's in cache
        self.assertIn(rumor.id, self.repository._rumor_cache)

        # Check that file was created
        rumor_file = os.path.join(self.storage_path, f"{rumor.id}.json")
        self.assertTrue(os.path.exists(rumor_file))

        # Retrieve rumor
        retrieved_rumor = await self.repository.get_rumor(rumor.id)

        # Verify retrieved rumor
        self.assertIsNotNone(retrieved_rumor)
        self.assertEqual(retrieved_rumor.id, rumor.id)
        self.assertEqual(retrieved_rumor.originator_id, rumor.originator_id)
        self.assertEqual(retrieved_rumor.original_content, rumor.original_content)
        self.assertEqual(retrieved_rumor.categories, rumor.categories)
        self.assertEqual(retrieved_rumor.severity, rumor.severity)
        self.assertEqual(retrieved_rumor.truth_value, rumor.truth_value)

    async def test_get_nonexistent_rumor(self): pass
        """Test retrieving a rumor that doesn't exist."""
        result = await self.repository.get_rumor("nonexistent_id")
        self.assertIsNone(result)

    async def test_get_all_rumors(self): pass
        """Test retrieving all rumors."""
        # Create multiple test rumors
        rumors = []
        for i in range(3): pass
            rumor = Rumor(
                originator_id=f"entity_{i}",
                original_content=f"Test rumor {i}",
                categories=[RumorCategory.OTHER],
                severity=RumorSeverity.MINOR,
            )
            rumors.append(rumor)
            await self.repository.save_rumor(rumor)

        # Retrieve all rumors
        all_rumors = await self.repository.get_all_rumors()

        # Verify all rumors were retrieved
        self.assertEqual(len(all_rumors), 3)
        retrieved_ids = {r.id for r in all_rumors}
        expected_ids = {r.id for r in rumors}
        self.assertEqual(retrieved_ids, expected_ids)

    async def test_get_world_rumors(self): pass
        """Test retrieving rumors for a specific world."""
        # For now, this returns all rumors since world filtering is disabled
        # Create test rumors
        rumors = []
        for i in range(2): pass
            rumor = Rumor(
                originator_id=f"entity_{i}",
                original_content=f"World rumor {i}",
                categories=[RumorCategory.OTHER],
            )
            rumors.append(rumor)
            await self.repository.save_rumor(rumor)

        # Retrieve world rumors
        world_rumors = await self.repository.get_world_rumors("test_world")

        # Should return all rumors for now
        self.assertEqual(len(world_rumors), 2)

    async def test_get_rumors_by_entity(self): pass
        """Test retrieving rumors known by a specific entity."""
        # Create rumor with spread data
        rumor = Rumor(
            originator_id="entity_1",
            original_content="Entity specific rumor",
            categories=[RumorCategory.OTHER],
        )

        # Add variant and spread
        variant = RumorVariant(
            content="Modified content",
            entity_id="entity_1"
        )
        rumor.variants.append(variant)

        spread = RumorSpread(
            entity_id="entity_2",
            variant_id=variant.id,
            heard_from_entity_id="entity_1",
            believability=0.7,
        )
        rumor.spread.append(spread)

        await self.repository.save_rumor(rumor)

        # Test retrieving rumors for entity_2
        entity_rumors = await self.repository.get_rumors_by_entity("entity_2")
        self.assertEqual(len(entity_rumors), 1)
        self.assertEqual(entity_rumors[0].id, rumor.id)

        # Test retrieving rumors for entity that doesn't know any rumors
        no_rumors = await self.repository.get_rumors_by_entity("entity_3")
        self.assertEqual(len(no_rumors), 0)

    async def test_delete_rumor(self): pass
        """Test deleting a rumor."""
        # Create and save rumor
        rumor = Rumor(
            originator_id="entity_1",
            original_content="Rumor to delete",
            categories=[RumorCategory.OTHER],
        )
        await self.repository.save_rumor(rumor)

        # Verify rumor exists
        retrieved = await self.repository.get_rumor(rumor.id)
        self.assertIsNotNone(retrieved)

        # Delete rumor
        result = await self.repository.delete_rumor(rumor.id)
        self.assertTrue(result)

        # Verify rumor is deleted
        deleted_rumor = await self.repository.get_rumor(rumor.id)
        self.assertIsNone(deleted_rumor)

        # Verify file is deleted
        rumor_file = os.path.join(self.storage_path, f"{rumor.id}.json")
        self.assertFalse(os.path.exists(rumor_file))

        # Test deleting non-existent rumor
        result = await self.repository.delete_rumor("nonexistent_id")
        self.assertFalse(result)

    async def test_get_rumors_by_filters(self): pass
        """Test retrieving rumors with various filters."""
        # Create test rumors with different properties
        rumors = [
            Rumor(
                originator_id="entity_1",
                original_content="Political rumor",
                categories=[RumorCategory.POLITICAL],
                severity=RumorSeverity.MAJOR,
            ),
            Rumor(
                originator_id="entity_2",
                original_content="Treasure rumor",
                categories=[RumorCategory.TREASURE],
                severity=RumorSeverity.MINOR,
            ),
            Rumor(
                originator_id="entity_3",
                original_content="Secret rumor",
                categories=[RumorCategory.SECRET],
                severity=RumorSeverity.CRITICAL,
            ),
        ]

        # Add spread data to test believability filtering
        for i, rumor in enumerate(rumors): pass
            variant = RumorVariant(content=f"Variant {i}", entity_id=f"entity_{i+1}")
            rumor.variants.append(variant)
            
            spread = RumorSpread(
                entity_id="test_entity",
                variant_id=variant.id,
                believability=0.3 + (i * 0.3),  # 0.3, 0.6, 0.9
            )
            rumor.spread.append(spread)
            
            await self.repository.save_rumor(rumor)

        # Test category filter
        political_rumors = await self.repository.get_rumors_by_filters(
            categories=[RumorCategory.POLITICAL]
        )
        self.assertEqual(len(political_rumors), 1)
        self.assertEqual(political_rumors[0].categories[0], RumorCategory.POLITICAL)

        # Test severity filter
        major_rumors = await self.repository.get_rumors_by_filters(
            min_severity=RumorSeverity.MAJOR
        )
        # Should return MAJOR and CRITICAL rumors
        self.assertEqual(len(major_rumors), 2)

        # Test believability filter
        high_belief_rumors = await self.repository.get_rumors_by_filters(
            entity_id="test_entity",
            min_believability=0.5
        )
        # Should return rumors with believability >= 0.5 (0.6 and 0.9)
        self.assertEqual(len(high_belief_rumors), 2)

        # Test query filter
        treasure_rumors = await self.repository.get_rumors_by_filters(
            query="treasure"
        )
        self.assertEqual(len(treasure_rumors), 1)
        self.assertIn("treasure", treasure_rumors[0].original_content.lower())

        # Test limit
        limited_rumors = await self.repository.get_rumors_by_filters(limit=2)
        self.assertEqual(len(limited_rumors), 2)

    def test_async_singleton_creation(self): pass
        """Test async singleton creation."""
        async def test_async_singleton(): pass
            # Reset singleton
            RumorRepository._instance = None
            
            repo1 = await RumorRepository.get_instance_async(storage_path=self.storage_path)
            repo2 = await RumorRepository.get_instance_async(storage_path=self.storage_path)
            
            self.assertIs(repo1, repo2)
            self.assertEqual(repo1.storage_path, self.storage_path)

        # Run the async test
        asyncio.run(test_async_singleton())

    def test_corrupted_file_handling(self): pass
        """Test handling of corrupted rumor files."""
        async def test_corrupted_file(): pass
            # Create a corrupted file
            corrupted_file = os.path.join(self.storage_path, "corrupted.json")
            os.makedirs(self.storage_path, exist_ok=True)
            with open(corrupted_file, "w") as f: pass
                f.write("not valid json")
            
            # Try to retrieve the corrupted rumor
            result = await self.repository.get_rumor("corrupted")
            self.assertIsNone(result)

        asyncio.run(test_corrupted_file())


# Helper function to run async tests
def run_async_test(test_func): pass
    """Helper to run async test methods."""
    def wrapper(self): pass
        asyncio.run(test_func(self))
    return wrapper


# Apply async wrapper to async test methods
TestRumorRepository.test_save_and_get_rumor = run_async_test(TestRumorRepository.test_save_and_get_rumor)
TestRumorRepository.test_get_nonexistent_rumor = run_async_test(TestRumorRepository.test_get_nonexistent_rumor)
TestRumorRepository.test_get_all_rumors = run_async_test(TestRumorRepository.test_get_all_rumors)
TestRumorRepository.test_get_world_rumors = run_async_test(TestRumorRepository.test_get_world_rumors)
TestRumorRepository.test_get_rumors_by_entity = run_async_test(TestRumorRepository.test_get_rumors_by_entity)
TestRumorRepository.test_delete_rumor = run_async_test(TestRumorRepository.test_delete_rumor)
TestRumorRepository.test_get_rumors_by_filters = run_async_test(TestRumorRepository.test_get_rumors_by_filters)


if __name__ == "__main__": pass
    unittest.main()
