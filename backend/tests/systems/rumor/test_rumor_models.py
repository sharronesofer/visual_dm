"""
Tests for rumor models.

This module tests the rumor models including Rumor, RumorVariant, and RumorSpread.
"""

import unittest
from datetime import datetime, timedelta

from backend.systems.rumor.models.rumor import (
    Rumor,
    RumorVariant,
    RumorSpread,
    RumorCategory,
    RumorSeverity,
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
            truth_value=0.8,
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
            parent_variant_id=None,
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
            believability=0.7,
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
            categories=[RumorCategory.TREASURE],
        )

        variant_1 = RumorVariant(
            content="The king has hidden treasure in the castle.", entity_id="entity_1"
        )
        rumor.variants.append(variant_1)

        variant_2 = RumorVariant(
            content="The king has hidden gold in the castle basement.",
            entity_id="entity_2",
            parent_variant_id=variant_1.id,
        )
        rumor.variants.append(variant_2)

        spread_1 = RumorSpread(
            entity_id="entity_3",
            variant_id=variant_1.id,
            heard_from_entity_id="entity_1",
            believability=0.8,
        )
        rumor.spread.append(spread_1)

        spread_2 = RumorSpread(
            entity_id="entity_4",
            variant_id=variant_2.id,
            heard_from_entity_id="entity_2",
            believability=0.6,
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
            originator_id="entity_1", original_content="The king has hidden treasure."
        )

        variant = RumorVariant(
            content="The king has hidden treasure in the castle.", entity_id="entity_1"
        )
        rumor.variants.append(variant)

        spread = RumorSpread(
            entity_id="entity_2",
            variant_id=variant.id,
            heard_from_entity_id="entity_1",
            believability=0.75,
        )
        rumor.spread.append(spread)

        # Test getting believability for entity_2 (should be 0.75)
        believability = rumor.get_believability_for_entity("entity_2")
        self.assertEqual(believability, 0.75)

        # Test getting believability for entity_3 (should be None)
        believability = rumor.get_believability_for_entity("entity_3")
        self.assertIsNone(believability)

    def test_get_variant_by_id(self):
        """Test getting a variant by its ID."""
        rumor = Rumor(
            originator_id="entity_1", original_content="The king has hidden treasure."
        )

        variant = RumorVariant(
            content="The king has hidden treasure in the castle.", entity_id="entity_1"
        )
        rumor.variants.append(variant)

        # Test getting the variant by ID
        retrieved_variant = rumor.get_variant_by_id(variant.id)
        self.assertEqual(retrieved_variant.id, variant.id)

        # Test getting a non-existent variant
        retrieved_variant = rumor.get_variant_by_id("non_existent_id")
        self.assertIsNone(retrieved_variant)

    def test_set_believability_for_entity(self):
        """Test setting believability for an entity."""
        rumor = Rumor(
            originator_id="entity_1", original_content="The king has hidden treasure."
        )

        variant = RumorVariant(
            content="The king has hidden treasure in the castle.", entity_id="entity_1"
        )
        rumor.variants.append(variant)

        # Rumor starts with originator spread record
        self.assertEqual(len(rumor.spread), 1)
        self.assertEqual(rumor.spread[0].entity_id, "entity_1")
        self.assertEqual(rumor.spread[0].believability, 1.0)

        # Test setting believability for a new entity
        rumor.set_believability_for_entity("entity_2", variant.id, 0.6)

        # Check that the spread record was created (originator + new entity)
        self.assertEqual(len(rumor.spread), 2)
        
        # Find the entity_2 spread record
        entity_2_spread = next(s for s in rumor.spread if s.entity_id == "entity_2")
        self.assertEqual(entity_2_spread.entity_id, "entity_2")
        self.assertEqual(entity_2_spread.variant_id, variant.id)
        self.assertEqual(entity_2_spread.believability, 0.6)

        # Test updating believability for an existing entity
        rumor.set_believability_for_entity("entity_2", variant.id, 0.8)

        # Check that the spread record was updated
        self.assertEqual(len(rumor.spread), 2)  # Still originator + entity_2
        entity_2_spread = next(s for s in rumor.spread if s.entity_id == "entity_2")
        self.assertEqual(entity_2_spread.believability, 0.8)

    def test_get_most_believed_variant(self):
        """Test getting the most believed variant."""
        rumor = Rumor(
            originator_id="entity_1", original_content="The king has hidden treasure."
        )

        variant_1 = RumorVariant(
            content="The king has hidden treasure in the castle.", entity_id="entity_1"
        )
        rumor.variants.append(variant_1)

        variant_2 = RumorVariant(
            content="The king has hidden gold in the castle basement.",
            entity_id="entity_2",
            parent_variant_id=variant_1.id,
        )
        rumor.variants.append(variant_2)

        # Add spread records to make variant_2 more believed
        for i in range(5):
            spread = RumorSpread(
                entity_id=f"entity_{i+10}",
                variant_id=variant_2.id,
                heard_from_entity_id="entity_2",
                believability=0.7,
            )
            rumor.spread.append(spread)

        # Add fewer spread records for variant_1
        for i in range(2):
            spread = RumorSpread(
                entity_id=f"entity_{i+20}",
                variant_id=variant_1.id,
                heard_from_entity_id="entity_1",
                believability=0.8,
            )
            rumor.spread.append(spread)

        # Test getting the most believed variant (should be variant_2)
        most_believed = rumor.get_most_believed_variant()
        self.assertEqual(most_believed.id, variant_2.id)

    def test_update_spread_record(self):
        """Test updating a spread record."""
        rumor = Rumor(
            originator_id="entity_1", original_content="The king has hidden treasure."
        )

        variant = RumorVariant(
            content="The king has hidden treasure in the castle.", entity_id="entity_1"
        )
        rumor.variants.append(variant)

        # Rumor starts with originator spread record
        self.assertEqual(len(rumor.spread), 1)

        spread = RumorSpread(
            entity_id="entity_2",
            variant_id=variant.id,
            heard_from_entity_id="entity_1",
            believability=0.5,
        )
        rumor.spread.append(spread)

        # Now we have originator + entity_2
        self.assertEqual(len(rumor.spread), 2)

        # Update the spread record's believability
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        rumor.update_spread_record(
            entity_id="entity_2",
            variant_id=variant.id,
            believability=0.9,
            heard_from_entity_id="entity_3",
            heard_at=one_hour_ago,
        )

        # Check that the spread record was updated (still originator + entity_2)
        self.assertEqual(len(rumor.spread), 2)
        
        # Find the entity_2 spread record
        entity_2_spread = next(s for s in rumor.spread if s.entity_id == "entity_2")
        self.assertEqual(entity_2_spread.believability, 0.9)
        self.assertEqual(entity_2_spread.heard_from_entity_id, "entity_3")
        self.assertEqual(entity_2_spread.heard_at, one_hour_ago)


if __name__ == "__main__":
    unittest.main()
