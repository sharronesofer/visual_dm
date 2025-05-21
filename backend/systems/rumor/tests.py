"""
Tests for the rumor system.

This module provides tests for the rumor system components.
"""
import unittest
import os
import tempfile
import json
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from backend.systems.rumor.models.rumor import (
    Rumor, RumorVariant, RumorSpread, RumorCategory, RumorSeverity
)
from backend.systems.rumor.repository import RumorRepository
from backend.systems.rumor.service import RumorService
from backend.systems.rumor.transformer import RumorTransformer
from backend.systems.rumor.decay_and_propagation import (
    calculate_rumor_decay,
    calculate_mutation_probability
)

class TestRumorModels(unittest.TestCase):
    """Test case for rumor models."""
    
    def test_rumor_creation(self):
        """Test creating a rumor."""
        rumor = Rumor(
            originator_id="entity_1",
            original_content="The king has hidden treasure.",
            categories=[RumorCategory.TREASURE],
            severity=RumorSeverity.MODERATE,
            truth_value=0.8
        )
        
        self.assertEqual(rumor.originator_id, "entity_1")
        self.assertEqual(rumor.original_content, "The king has hidden treasure.")
        self.assertEqual(rumor.categories, [RumorCategory.TREASURE])
        self.assertEqual(rumor.severity, RumorSeverity.MODERATE)
        self.assertEqual(rumor.truth_value, 0.8)
        self.assertIsNotNone(rumor.id)
        self.assertIsNotNone(rumor.created_at)
        
    def test_rumor_variant_creation(self):
        """Test creating a rumor variant."""
        variant = RumorVariant(
            content="The queen has hidden jewels.",
            entity_id="entity_2",
            parent_variant_id=None
        )
        
        self.assertEqual(variant.content, "The queen has hidden jewels.")
        self.assertEqual(variant.entity_id, "entity_2")
        self.assertIsNone(variant.parent_variant_id)
        self.assertIsNotNone(variant.id)
        self.assertIsNotNone(variant.created_at)
        
    def test_rumor_spread_creation(self):
        """Test creating a rumor spread record."""
        spread = RumorSpread(
            entity_id="entity_3",
            variant_id="variant_1",
            heard_from_entity_id="entity_2",
            believability=0.7
        )
        
        self.assertEqual(spread.entity_id, "entity_3")
        self.assertEqual(spread.variant_id, "variant_1")
        self.assertEqual(spread.heard_from_entity_id, "entity_2")
        self.assertEqual(spread.believability, 0.7)
        self.assertIsNotNone(spread.heard_at)
        self.assertIsNotNone(spread.last_reinforced_at)
        
    def test_rumor_get_current_variant_for_entity(self):
        """Test getting the current variant for an entity."""
        rumor = Rumor(
            originator_id="entity_1",
            original_content="The king has hidden treasure.",
            categories=[RumorCategory.TREASURE]
        )
        
        variant_1 = RumorVariant(
            content="The king has hidden treasure in the castle.",
            entity_id="entity_1"
        )
        rumor.variants.append(variant_1)
        
        variant_2 = RumorVariant(
            content="The king has hidden gold in the castle basement.",
            entity_id="entity_2",
            parent_variant_id=variant_1.id
        )
        rumor.variants.append(variant_2)
        
        spread_1 = RumorSpread(
            entity_id="entity_3",
            variant_id=variant_1.id,
            heard_from_entity_id="entity_1",
            believability=0.8
        )
        rumor.spread.append(spread_1)
        
        spread_2 = RumorSpread(
            entity_id="entity_4",
            variant_id=variant_2.id,
            heard_from_entity_id="entity_2",
            believability=0.6
        )
        rumor.spread.append(spread_2)
        
        # Test getting variant for entity_3 (should be variant_1)
        current_variant = rumor.get_current_variant_for_entity("entity_3")
        self.assertEqual(current_variant.id, variant_1.id)
        
        # Test getting variant for entity_4 (should be variant_2)
        current_variant = rumor.get_current_variant_for_entity("entity_4")
        self.assertEqual(current_variant.id, variant_2.id)
        
        # Test getting variant for entity_5 (should be None)
        current_variant = rumor.get_current_variant_for_entity("entity_5")
        self.assertIsNone(current_variant)
        
    def test_rumor_get_believability_for_entity(self):
        """Test getting believability for an entity."""
        rumor = Rumor(
            originator_id="entity_1",
            original_content="The king has hidden treasure."
        )
        
        variant = RumorVariant(
            content="The king has hidden treasure in the castle.",
            entity_id="entity_1"
        )
        rumor.variants.append(variant)
        
        spread = RumorSpread(
            entity_id="entity_2",
            variant_id=variant.id,
            heard_from_entity_id="entity_1",
            believability=0.75
        )
        rumor.spread.append(spread)
        
        # Test getting believability for entity_2 (should be 0.75)
        believability = rumor.get_believability_for_entity("entity_2")
        self.assertEqual(believability, 0.75)
        
        # Test getting believability for entity_3 (should be None)
        believability = rumor.get_believability_for_entity("entity_3")
        self.assertIsNone(believability)
        
class TestRumorRepository(unittest.TestCase):
    """Test case for rumor repository."""
    
    def setUp(self):
        """Set up the test case."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo = RumorRepository(storage_path=self.temp_dir)
        
        # Create a test rumor
        self.test_rumor = Rumor(
            id="test_rumor_1",
            originator_id="entity_1",
            original_content="Test rumor content",
            categories=[RumorCategory.SCANDAL],
            severity=RumorSeverity.MINOR,
            truth_value=0.6
        )
        
        # Add a variant
        variant = RumorVariant(
            id="test_variant_1",
            content="Test variant content",
            entity_id="entity_1"
        )
        self.test_rumor.variants.append(variant)
        
        # Add a spread record
        spread = RumorSpread(
            entity_id="entity_2",
            variant_id=variant.id,
            heard_from_entity_id="entity_1",
            believability=0.8
        )
        self.test_rumor.spread.append(spread)
        
    def tearDown(self):
        """Tear down the test case."""
        shutil.rmtree(self.temp_dir)
        
    def test_save_and_get_rumor(self):
        """Test saving and retrieving a rumor."""
        # Save the rumor
        self.repo.save(self.test_rumor)
        
        # Get the rumor
        retrieved_rumor = self.repo.get("test_rumor_1")
        
        # Check if it's the same
        self.assertEqual(retrieved_rumor.id, self.test_rumor.id)
        self.assertEqual(retrieved_rumor.original_content, self.test_rumor.original_content)
        self.assertEqual(len(retrieved_rumor.variants), 1)
        self.assertEqual(len(retrieved_rumor.spread), 1)
        
    def test_list_all(self):
        """Test listing all rumors."""
        # Save the rumor
        self.repo.save(self.test_rumor)
        
        # Create and save another rumor
        rumor2 = Rumor(
            id="test_rumor_2",
            originator_id="entity_3",
            original_content="Another test rumor",
            categories=[RumorCategory.DISASTER]
        )
        self.repo.save(rumor2)
        
        # List all rumors
        rumors = self.repo.list_all()
        
        # Check if both rumors are returned
        self.assertEqual(len(rumors), 2)
        self.assertIn("test_rumor_1", [r.id for r in rumors])
        self.assertIn("test_rumor_2", [r.id for r in rumors])
        
    def test_update_rumor(self):
        """Test updating a rumor."""
        # Save the rumor
        self.repo.save(self.test_rumor)
        
        # Update the rumor
        self.test_rumor.truth_value = 0.3
        self.repo.save(self.test_rumor)
        
        # Get the updated rumor
        updated_rumor = self.repo.get("test_rumor_1")
        
        # Check if it's updated
        self.assertEqual(updated_rumor.truth_value, 0.3)
        
    def test_delete_rumor(self):
        """Test deleting a rumor."""
        # Save the rumor
        self.repo.save(self.test_rumor)
        
        # Delete the rumor
        result = self.repo.delete("test_rumor_1")
        
        # Check if deletion was successful
        self.assertTrue(result)
        
        # Try to get the deleted rumor
        deleted_rumor = self.repo.get("test_rumor_1")
        
        # Check if it's None
        self.assertIsNone(deleted_rumor)
        
    def test_get_by_entity(self):
        """Test getting rumors by entity."""
        # Save the rumor
        self.repo.save(self.test_rumor)
        
        # Get rumors for entity_2
        rumors = self.repo.get_by_entity("entity_2")
        
        # Check if the rumor is returned
        self.assertEqual(len(rumors), 1)
        self.assertEqual(rumors[0].id, "test_rumor_1")
        
        # Get rumors for entity_3 (should be empty)
        rumors = self.repo.get_by_entity("entity_3")
        self.assertEqual(len(rumors), 0)
        
class TestDecayAndPropagation(unittest.TestCase):
    """Test case for decay and propagation utilities."""
    
    def test_calculate_rumor_decay(self):
        """Test calculating rumor decay."""
        # Test minor rumor with 10 days inactive
        decay = calculate_rumor_decay(10, RumorSeverity.MINOR)
        self.assertGreater(decay, 0.0)
        
        # Test critical rumor with 10 days inactive (should decay less)
        critical_decay = calculate_rumor_decay(10, RumorSeverity.CRITICAL)
        self.assertLess(critical_decay, decay)
        
        # Test 0 days inactive (should be 0)
        zero_decay = calculate_rumor_decay(0, RumorSeverity.MINOR)
        self.assertEqual(zero_decay, 0.0)
        
    def test_calculate_mutation_probability(self):
        """Test calculating mutation probability."""
        # Test positive relationship
        prob_positive = calculate_mutation_probability(0.8)
        
        # Test negative relationship (should have higher mutation chance)
        prob_negative = calculate_mutation_probability(-0.8)
        self.assertGreater(prob_negative, prob_positive)
        
        # Test neutral relationship
        prob_neutral = calculate_mutation_probability(0.0)
        self.assertGreater(prob_neutral, prob_positive)
        self.assertLess(prob_neutral, prob_negative)
        
class TestRumorService(unittest.TestCase):
    """Test case for rumor service."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a mock repository
        self.mock_repo = MagicMock()
        
        # Create a mock event dispatcher
        self.mock_dispatcher = MagicMock()
        
        # Create the service with mocks
        self.service = RumorService(
            repository=self.mock_repo,
            event_dispatcher=self.mock_dispatcher
        )
        
    def test_create_rumor(self):
        """Test creating a rumor."""
        # Set up the mock repository
        self.mock_repo.save.return_value = True
        
        # Create a rumor
        rumor = self.service.create_rumor(
            originator_id="entity_1",
            content="New rumor content",
            categories=[RumorCategory.TREASURE],
            severity=RumorSeverity.MODERATE,
            truth_value=0.7
        )
        
        # Check if the rumor was created correctly
        self.assertEqual(rumor.originator_id, "entity_1")
        self.assertEqual(rumor.original_content, "New rumor content")
        self.assertEqual(rumor.categories, [RumorCategory.TREASURE])
        self.assertEqual(rumor.severity, RumorSeverity.MODERATE)
        self.assertEqual(rumor.truth_value, 0.7)
        
        # Check if save was called
        self.mock_repo.save.assert_called_once()
        
        # Check if event was dispatched
        self.mock_dispatcher.dispatch.assert_called_once()
        
    def test_get_rumor(self):
        """Test getting a rumor."""
        # Create a test rumor
        test_rumor = Rumor(
            id="test_id",
            originator_id="entity_1",
            original_content="Test content"
        )
        
        # Set up the mock repository
        self.mock_repo.get.return_value = test_rumor
        
        # Get the rumor
        rumor = self.service.get_rumor("test_id")
        
        # Check if the correct rumor was returned
        self.assertEqual(rumor, test_rumor)
        
        # Check if get was called with the correct ID
        self.mock_repo.get.assert_called_once_with("test_id")
        
    def test_spread_rumor(self):
        """Test spreading a rumor."""
        # Create a test rumor
        test_rumor = Rumor(
            id="test_id",
            originator_id="entity_1",
            original_content="Test content"
        )
        
        # Add a variant
        variant = RumorVariant(
            id="variant_id",
            content="Variant content",
            entity_id="entity_1"
        )
        test_rumor.variants.append(variant)
        
        # Set up the mock repository
        self.mock_repo.get.return_value = test_rumor
        self.mock_repo.save.return_value = True
        
        # Spread the rumor
        result = self.service.spread_rumor(
            rumor_id="test_id",
            from_entity_id="entity_1",
            to_entity_id="entity_2",
            mutation_chance=0.0,  # No mutation for simplicity
            relationship_factor=0.5,
            believability_modifier=0.1
        )
        
        # Check if the spread was successful
        self.assertTrue(result)
        
        # Check if get was called with the correct ID
        self.mock_repo.get.assert_called_once_with("test_id")
        
        # Check if save was called
        self.mock_repo.save.assert_called_once()
        
        # Check if the spread was recorded
        self.assertEqual(len(test_rumor.spread), 1)
        self.assertEqual(test_rumor.spread[0].entity_id, "entity_2")
        self.assertEqual(test_rumor.spread[0].variant_id, "variant_id")
        self.assertEqual(test_rumor.spread[0].heard_from_entity_id, "entity_1")
        
        # Check if event was dispatched
        self.mock_dispatcher.dispatch.assert_called_once()
        
class TestRumorTransformer(unittest.TestCase):
    """Test case for rumor transformer."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a mock GPT client
        self.mock_gpt = AsyncMock()
        self.transformer = RumorTransformer(gpt_client=self.mock_gpt)
        
    @patch('backend.systems.rumor.transformer.RumorTransformer._extract_transformed_rumor')
    async def test_transform_rumor(self, mock_extract):
        """Test transforming a rumor."""
        # Set up the mock GPT client
        self.mock_gpt.generate_text.return_value = "Transformed content"
        
        # Set up the mock extract method
        mock_extract.return_value = "Cleaned transformed content"
        
        # Transform the rumor
        transformed = await self.transformer.transform_rumor(
            event="Original event",
            rumor="Original rumor",
            traits="Traits",
            distortion_level=0.5
        )
        
        # Check if the transformation was correct
        self.assertEqual(transformed, "Cleaned transformed content")
        
        # Check if GPT was called
        self.mock_gpt.generate_text.assert_called_once()
        
        # Check if extract was called
        mock_extract.assert_called_once_with("Transformed content")
        
    def test_calculate_truth_value(self):
        """Test calculating truth value."""
        # Calculate truth value
        truth = self.transformer.calculate_truth_value(
            original_event="The king has hidden treasure in the castle basement.",
            transformed_rumor="The king has hidden gold in the castle.",
            base_truth=0.8
        )
        
        # Check if the truth value is between 0 and 1
        self.assertGreaterEqual(truth, 0.0)
        self.assertLessEqual(truth, 0.8)
        
    def test_fallback_transform(self):
        """Test fallback transformation."""
        # Transform the rumor
        transformed = self.transformer.fallback_transform(
            rumor="The king has hidden treasure in the castle.",
            distortion_level=0.5
        )
        
        # Check if the transformation produced a string
        self.assertIsInstance(transformed, str)
        
        # Check if the transformation has the same word count
        self.assertEqual(len(transformed.split()), 7)
        
if __name__ == '__main__':
    unittest.main() 