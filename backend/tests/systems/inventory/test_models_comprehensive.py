from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
"""
Comprehensive test module for inventory model classes.

This module tests the individual model classes in the inventory models directory.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from backend.systems.inventory.models.item import Item
from backend.systems.inventory.models.inventory import Inventory
from backend.systems.inventory.models.inventory_item import InventoryItem
from backend.systems.inventory.models.item_category import ItemCategory


class TestItemModel(unittest.TestCase):
    """Test cases for Item model."""

    def test_item_creation(self):
        """Test Item model creation."""
        item = Item(
            name="Test Sword",
            description="A sharp sword",
            weight=2.5,
            value=100,
            stackable=False
        )
        
        self.assertEqual(item.name, "Test Sword")
        self.assertEqual(item.description, "A sharp sword")
        self.assertEqual(item.weight, 2.5)
        self.assertEqual(item.value, 100)
        self.assertFalse(item.stackable)

    def test_item_str_representation(self):
        """Test Item string representation."""
        item = Item(name="Test Item", id="test_id")
        expected = "<Item Test Item>"
        self.assertEqual(str(item), expected)

    def test_item_repr_representation(self):
        """Test Item repr representation."""
        item = Item(name="Test Item", id="test_id")
        expected = "<Item Test Item>"
        self.assertEqual(repr(item), expected)

    def test_item_attributes(self):
        """Test Item attributes access."""
        item = Item(
            id="test_id",
            name="Test Item",
            description="Test description",
            weight=1.0,
            value=50
        )
        
        self.assertEqual(item.id, "test_id")
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.description, "Test description")
        self.assertEqual(item.weight, 1.0)
        self.assertEqual(item.value, 50)

    def test_item_default_values(self):
        """Test Item with default values."""
        item = Item(name="Simple Item")
        
        self.assertEqual(item.name, "Simple Item")
        self.assertIsNone(item.description)
        self.assertEqual(item.weight, 0.0)
        self.assertEqual(item.value, 0)
        self.assertFalse(item.stackable)
        self.assertEqual(item.max_stack, 1)


class TestInventoryModel(unittest.TestCase):
    """Test cases for Inventory model."""

    def test_inventory_creation(self):
        """Test Inventory model creation."""
        inventory = Inventory(
            name="Player Backpack",
            description="Main inventory",
            owner_id="char_123",
            owner_type="character",
            capacity=50.0
        )
        
        self.assertEqual(inventory.name, "Player Backpack")
        self.assertEqual(inventory.description, "Main inventory")
        self.assertEqual(inventory.owner_id, "char_123")
        self.assertEqual(inventory.owner_type, "character")
        self.assertEqual(inventory.capacity, 50.0)

    def test_inventory_str_representation(self):
        """Test Inventory string representation."""
        inventory = Inventory(name="Test Inventory", id="test_id", owner_id="owner_123", owner_type="character")
        expected = "<Inventory Test Inventory>"
        self.assertEqual(str(inventory), expected)

    def test_inventory_repr_representation(self):
        """Test Inventory repr representation."""
        inventory = Inventory(name="Test Inventory", id="test_id", owner_id="owner_123", owner_type="character")
        expected = "<Inventory Test Inventory>"
        self.assertEqual(repr(inventory), expected)

    def test_inventory_attributes(self):
        """Test Inventory attributes access."""
        inventory = Inventory(
            id="test_id",
            name="Test Inventory",
            description="Test description",
            owner_id="owner_123",
            owner_type="character",
            capacity=50.0
        )
        
        self.assertEqual(inventory.id, "test_id")
        self.assertEqual(inventory.name, "Test Inventory")
        self.assertEqual(inventory.description, "Test description")
        self.assertEqual(inventory.owner_id, "owner_123")
        self.assertEqual(inventory.capacity, 50.0)

    def test_inventory_default_values(self):
        """Test Inventory with default values."""
        inventory = Inventory(name="Simple Inventory", owner_id="test_owner", owner_type="character")
        
        self.assertEqual(inventory.name, "Simple Inventory")
        self.assertIsNone(inventory.description)
        self.assertEqual(inventory.capacity, 100.0)
        self.assertEqual(inventory.used_capacity, 0.0)


class TestInventoryItemModel(unittest.TestCase):
    """Test cases for InventoryItem model."""

    def test_inventory_item_creation(self):
        """Test InventoryItem model creation."""
        inventory_item = InventoryItem(
            inventory_id="inv_1",
            item_id="item_2",
            quantity=5,
            is_equipped=True,
            position={"x": 1, "y": 2}
        )
        
        self.assertEqual(inventory_item.inventory_id, "inv_1")
        self.assertEqual(inventory_item.item_id, "item_2")
        self.assertEqual(inventory_item.quantity, 5)
        self.assertTrue(inventory_item.is_equipped)
        self.assertEqual(inventory_item.position, {"x": 1, "y": 2})

    def test_inventory_item_str_representation(self):
        """Test InventoryItem string representation."""
        inventory_item = InventoryItem(inventory_id="inv_1", item_id="item_2", quantity=3, id="inv_item_1")
        expected = "<InventoryItem inv_item_1: 3x item item_2>"
        self.assertEqual(str(inventory_item), expected)

    def test_inventory_item_repr_representation(self):
        """Test InventoryItem repr representation."""
        inventory_item = InventoryItem(inventory_id="inv_1", item_id="item_2", quantity=3, id="inv_item_1")
        expected = "<InventoryItem inv_item_1: 3x item item_2>"
        self.assertEqual(repr(inventory_item), expected)

    def test_inventory_item_attributes(self):
        """Test InventoryItem attributes access."""
        inventory_item = InventoryItem(
            id="inv_item_1",
            inventory_id="inv_2",
            item_id="item_3",
            quantity=10,
            is_equipped=False
        )
        
        self.assertEqual(inventory_item.id, "inv_item_1")
        self.assertEqual(inventory_item.inventory_id, "inv_2")
        self.assertEqual(inventory_item.item_id, "item_3")
        self.assertEqual(inventory_item.quantity, 10)
        self.assertFalse(inventory_item.is_equipped)

    def test_inventory_item_default_values(self):
        """Test InventoryItem with default values."""
        inventory_item = InventoryItem(inventory_id="inv_1", item_id="item_2")
        
        self.assertEqual(inventory_item.inventory_id, "inv_1")
        self.assertEqual(inventory_item.item_id, "item_2")
        self.assertEqual(inventory_item.quantity, 1)  # Default quantity
        self.assertFalse(inventory_item.is_equipped)  # Default is_equipped


class TestItemCategoryEnum(unittest.TestCase):
    """Test cases for ItemCategory enum."""

    def test_item_category_values(self):
        """Test ItemCategory enum values."""
        self.assertEqual(ItemCategory.WEAPON.value, "weapon")
        self.assertEqual(ItemCategory.ARMOR.value, "armor")
        self.assertEqual(ItemCategory.CONSUMABLE.value, "consumable")
        self.assertEqual(ItemCategory.QUEST.value, "quest")
        self.assertEqual(ItemCategory.MISC.value, "misc")

    def test_item_category_membership(self):
        """Test ItemCategory enum membership."""
        self.assertIn(ItemCategory.WEAPON, ItemCategory)
        self.assertIn(ItemCategory.ARMOR, ItemCategory)
        self.assertIn(ItemCategory.CONSUMABLE, ItemCategory)
        self.assertIn(ItemCategory.QUEST, ItemCategory)
        self.assertIn(ItemCategory.MISC, ItemCategory)

    def test_item_category_string_representation(self):
        """Test ItemCategory string representation."""
        self.assertEqual(str(ItemCategory.WEAPON), "ItemCategory.WEAPON")
        self.assertEqual(str(ItemCategory.ARMOR), "ItemCategory.ARMOR")

    def test_item_category_comparison(self):
        """Test ItemCategory comparison."""
        self.assertEqual(ItemCategory.WEAPON, ItemCategory.WEAPON)
        self.assertNotEqual(ItemCategory.WEAPON, ItemCategory.ARMOR)

    def test_item_category_iteration(self):
        """Test ItemCategory iteration."""
        categories = list(ItemCategory)
        self.assertEqual(len(categories), 5)
        self.assertIn(ItemCategory.WEAPON, categories)
        self.assertIn(ItemCategory.ARMOR, categories)
        self.assertIn(ItemCategory.CONSUMABLE, categories)
        self.assertIn(ItemCategory.QUEST, categories)
        self.assertIn(ItemCategory.MISC, categories)


if __name__ == '__main__':
    unittest.main() 