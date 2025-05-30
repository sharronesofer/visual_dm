from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
"""
Tests for Inventory Factory functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
from backend.systems.inventory.factory import InventoryFactory
from backend.systems.inventory.models.inventory import Inventory


class TestInventoryFactory(unittest.TestCase):
    """Test cases for InventoryFactory."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock inventory
        self.mock_inventory = MagicMock(spec=Inventory)
        self.mock_inventory.id = 1
        self.mock_inventory.name = "Test Inventory"
        self.mock_inventory.description = "A test inventory"
        self.mock_inventory.inventory_type = "character"
        self.mock_inventory.owner_id = 100
        self.mock_inventory.capacity = 50
        self.mock_inventory.weight_limit = 150.0
        self.mock_inventory.is_public = False

    @patch("backend.systems.inventory.factory.InventoryRepository")
    def test_create_character_inventory_default_name(self, mock_repo):
        """Test creating character inventory with default name."""
        # Configure mock
        mock_repo.create_inventory.return_value = self.mock_inventory

        # Call method
        result = InventoryFactory.create_character_inventory(100)

        # Verify result
        self.assertIsNotNone(result)

        # Verify repository was called with correct data
        mock_repo.create_inventory.assert_called_once()
        call_args = mock_repo.create_inventory.call_args[0][0]
        
        self.assertEqual(call_args["name"], "Character Inventory")
        self.assertEqual(call_args["description"], "Main inventory for character #100")
        self.assertEqual(call_args["inventory_type"], "character")
        self.assertEqual(call_args["owner_id"], 100)
        self.assertEqual(call_args["capacity"], 50)
        self.assertEqual(call_args["weight_limit"], 150.0)
        self.assertFalse(call_args["is_public"])

    @patch("backend.systems.inventory.factory.InventoryRepository")
    def test_create_character_inventory_custom_name(self, mock_repo):
        """Test creating character inventory with custom name."""
        # Configure mock
        mock_repo.create_inventory.return_value = self.mock_inventory

        # Call method
        result = InventoryFactory.create_character_inventory(100, "My Backpack")

        # Verify result
        self.assertIsNotNone(result)

        # Verify repository was called with correct data
        mock_repo.create_inventory.assert_called_once()
        call_args = mock_repo.create_inventory.call_args[0][0]
        
        self.assertEqual(call_args["name"], "My Backpack")
        self.assertEqual(call_args["description"], "Main inventory for character #100")
        self.assertEqual(call_args["inventory_type"], "character")
        self.assertEqual(call_args["owner_id"], 100)

    @patch("backend.systems.inventory.factory.InventoryRepository")
    def test_create_container_inventory_minimal(self, mock_repo):
        """Test creating container inventory with minimal parameters."""
        # Configure mock
        mock_repo.create_inventory.return_value = self.mock_inventory

        # Call method
        result = InventoryFactory.create_container_inventory("Treasure Chest")

        # Verify result
        self.assertIsNotNone(result)

        # Verify repository was called with correct data
        mock_repo.create_inventory.assert_called_once()
        call_args = mock_repo.create_inventory.call_args[0][0]
        
        self.assertEqual(call_args["name"], "Treasure Chest")
        self.assertEqual(call_args["description"], "Treasure Chest container")
        self.assertEqual(call_args["inventory_type"], "container")
        self.assertIsNone(call_args["capacity"])
        self.assertIsNone(call_args["weight_limit"])
        self.assertIsNone(call_args["owner_id"])
        self.assertFalse(call_args["is_public"])

    @patch("backend.systems.inventory.factory.InventoryRepository")
    def test_create_container_inventory_full_params(self, mock_repo):
        """Test creating container inventory with all parameters."""
        # Configure mock
        mock_repo.create_inventory.return_value = self.mock_inventory

        # Call method
        result = InventoryFactory.create_container_inventory(
            name="Magic Bag",
            description="A magical storage bag",
            capacity=100,
            weight_limit=200.0,
            owner_id=123
        )

        # Verify result
        self.assertIsNotNone(result)

        # Verify repository was called with correct data
        mock_repo.create_inventory.assert_called_once()
        call_args = mock_repo.create_inventory.call_args[0][0]
        
        self.assertEqual(call_args["name"], "Magic Bag")
        self.assertEqual(call_args["description"], "A magical storage bag")
        self.assertEqual(call_args["inventory_type"], "container")
        self.assertEqual(call_args["capacity"], 100)
        self.assertEqual(call_args["weight_limit"], 200.0)
        self.assertEqual(call_args["owner_id"], 123)
        self.assertFalse(call_args["is_public"])

    @patch("backend.systems.inventory.factory.InventoryRepository")
    def test_create_shop_inventory_minimal(self, mock_repo):
        """Test creating shop inventory with minimal parameters."""
        # Configure mock
        mock_repo.create_inventory.return_value = self.mock_inventory

        # Call method
        result = InventoryFactory.create_shop_inventory("Weapon Shop", 456)

        # Verify result
        self.assertIsNotNone(result)

        # Verify repository was called with correct data
        mock_repo.create_inventory.assert_called_once()
        call_args = mock_repo.create_inventory.call_args[0][0]
        
        self.assertEqual(call_args["name"], "Weapon Shop")
        self.assertEqual(call_args["description"], "Weapon Shop shop inventory")
        self.assertEqual(call_args["inventory_type"], "shop")
        self.assertEqual(call_args["owner_id"], 456)
        self.assertIsNone(call_args["capacity"])  # Shops don't have capacity limits
        self.assertIsNone(call_args["weight_limit"])  # Shops don't have weight limits
        self.assertTrue(call_args["is_public"])

    @patch("backend.systems.inventory.factory.InventoryRepository")
    def test_create_shop_inventory_full_params(self, mock_repo):
        """Test creating shop inventory with all parameters."""
        # Configure mock
        mock_repo.create_inventory.return_value = self.mock_inventory

        # Call method
        result = InventoryFactory.create_shop_inventory(
            name="Potion Shop",
            owner_id=789,
            description="A shop selling magical potions",
            is_public=False
        )

        # Verify result
        self.assertIsNotNone(result)

        # Verify repository was called with correct data
        mock_repo.create_inventory.assert_called_once()
        call_args = mock_repo.create_inventory.call_args[0][0]
        
        self.assertEqual(call_args["name"], "Potion Shop")
        self.assertEqual(call_args["description"], "A shop selling magical potions")
        self.assertEqual(call_args["inventory_type"], "shop")
        self.assertEqual(call_args["owner_id"], 789)
        self.assertIsNone(call_args["capacity"])
        self.assertIsNone(call_args["weight_limit"])
        self.assertFalse(call_args["is_public"])

    @patch("backend.systems.inventory.factory.InventoryRepository")
    def test_create_character_inventory_exception(self, mock_repo):
        """Test character inventory creation when repository raises exception."""
        # Configure mock to raise exception
        mock_repo.create_inventory.side_effect = Exception("Database error")

        # Call method and verify exception is propagated
        with self.assertRaises(Exception) as context:
            InventoryFactory.create_character_inventory(100)
        
        self.assertIn("Database error", str(context.exception))

    @patch("backend.systems.inventory.factory.InventoryRepository")
    def test_create_container_inventory_exception(self, mock_repo):
        """Test container inventory creation when repository raises exception."""
        # Configure mock to raise exception
        mock_repo.create_inventory.side_effect = Exception("Database error")

        # Call method and verify exception is propagated
        with self.assertRaises(Exception) as context:
            InventoryFactory.create_container_inventory("Test Container")
        
        self.assertIn("Database error", str(context.exception))

    @patch("backend.systems.inventory.factory.InventoryRepository")
    def test_create_shop_inventory_exception(self, mock_repo):
        """Test shop inventory creation when repository raises exception."""
        # Configure mock to raise exception
        mock_repo.create_inventory.side_effect = Exception("Database error")

        # Call method and verify exception is propagated
        with self.assertRaises(Exception) as context:
            InventoryFactory.create_shop_inventory("Test Shop", 123)
        
        self.assertIn("Database error", str(context.exception))


if __name__ == "__main__":
    unittest.main()
