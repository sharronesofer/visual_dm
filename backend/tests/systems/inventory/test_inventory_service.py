from backend.systems.inventory.models import Inventory
from backend.systems.inventory.schemas import ItemResponse
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.schemas import ItemResponse
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.schemas import ItemResponse
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.schemas import ItemResponse
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.schemas import ItemResponse
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.schemas import ItemResponse
"""
Tests for Inventory Service.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from backend.systems.inventory.service import InventoryService
from backend.systems.inventory.models.item import Item
from backend.systems.inventory.models.inventory import Inventory
from backend.systems.inventory.models.inventory_item import InventoryItem
from backend.systems.inventory.schemas import ItemResponse, InventoryResponse, InventoryItemResponse


class TestInventoryService(unittest.TestCase):
    """Test cases for InventoryService."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock for validator
        self.validator_patch = patch("backend.systems.inventory.service.InventoryValidator")
        self.mock_validator = self.validator_patch.start()

        # Create mock for inventory repository
        self.inventory_repo_patch = patch("backend.systems.inventory.service.InventoryRepository")
        self.mock_inventory_repo = self.inventory_repo_patch.start()

        # Create mock for item repository
        self.item_repo_patch = patch("backend.systems.inventory.service.ItemRepository")
        self.mock_item_repo = self.item_repo_patch.start()

        # Create mock for inventory item repository
        self.inventory_item_repo_patch = patch("backend.systems.inventory.service.InventoryItemRepository")
        self.mock_inventory_item_repo = self.inventory_item_repo_patch.start()

        # Create mock for database session
        self.db_patch = patch("backend.systems.inventory.service.db")
        self.mock_db = self.db_patch.start()

        # Create mock inventory with proper attributes
        self.mock_inventory = MagicMock(spec=Inventory)
        self.mock_inventory.id = 1
        self.mock_inventory.owner_id = 100
        self.mock_inventory.owner_type = "character"
        self.mock_inventory.name = "Test Inventory"
        self.mock_inventory.description = "A test inventory"
        self.mock_inventory.capacity = 50
        self.mock_inventory.weight_limit = 100.0
        self.mock_inventory.created_at = datetime.now()

        # Create mock items with proper attributes
        self.mock_sword = MagicMock(spec=Item)
        self.mock_sword.id = 1
        self.mock_sword.name = "Test Sword"
        self.mock_sword.description = "A test sword"
        self.mock_sword.category = "weapon"
        self.mock_sword.can_be_equipped = True
        self.mock_sword.equipment_slot = "main_hand"
        self.mock_sword.weight = 5.0
        self.mock_sword.value = 15.0
        self.mock_sword.is_stackable = False
        self.mock_sword.max_stack_size = 1
        self.mock_sword.apply_weight_when_equipped = True
        self.mock_sword.properties = {"damage": 10}
        self.mock_sword.created_at = datetime.now()
        self.mock_sword.updated_at = None

        self.mock_potion = MagicMock(spec=Item)
        self.mock_potion.id = 2
        self.mock_potion.name = "Test Potion"
        self.mock_potion.description = "A test potion"
        self.mock_potion.category = "consumable"
        self.mock_potion.can_be_equipped = False
        self.mock_potion.equipment_slot = None
        self.mock_potion.weight = 0.5
        self.mock_potion.value = 5.0
        self.mock_potion.is_stackable = True
        self.mock_potion.max_stack_size = 10
        self.mock_potion.apply_weight_when_equipped = True
        self.mock_potion.properties = {"healing": 50}
        self.mock_potion.created_at = datetime.now()
        self.mock_potion.updated_at = None

        # Create mock inventory items with proper attributes
        self.mock_inventory_item = MagicMock(spec=InventoryItem)
        self.mock_inventory_item.id = 1
        self.mock_inventory_item.inventory_id = self.mock_inventory.id
        self.mock_inventory_item.item_id = self.mock_sword.id
        self.mock_inventory_item.item = self.mock_sword
        self.mock_inventory_item.quantity = 1
        self.mock_inventory_item.position = {"x": 0, "y": 0}
        self.mock_inventory_item.is_equipped = False
        self.mock_inventory_item.created_at = datetime.now()
        self.mock_inventory_item.updated_at = None

    def tearDown(self):
        """Tear down test fixtures."""
        self.validator_patch.stop()
        self.inventory_repo_patch.stop()
        self.item_repo_patch.stop()
        self.inventory_item_repo_patch.stop()
        self.db_patch.stop()

    def test_create_item_success(self):
        """Test creating an item successfully."""
        # Configure mock
        self.mock_item_repo.create.return_value = self.mock_sword

        # Call method
        success, message, response = InventoryService.create_item({
            "name": "Test Sword",
            "weight": 5.0,
            "category": "weapon"
        })

        # Verify result
        self.assertTrue(success)
        self.assertEqual(message, "Item created successfully")
        self.assertIsNotNone(response)

        # Verify mock was called correctly
        self.mock_item_repo.create.assert_called_once()

    def test_create_item_failure(self):
        """Test creating an item with failure."""
        # Configure mock to raise exception
        self.mock_item_repo.create.side_effect = Exception("Database error")

        # Call method
        success, message, response = InventoryService.create_item({
            "name": "Test Sword",
            "weight": 5.0
        })

        # Verify result
        self.assertFalse(success)
        self.assertIn("Error creating item", message)
        self.assertIsNone(response)

    def test_update_item_success(self):
        """Test updating an item successfully."""
        # Configure mock
        self.mock_item_repo.update.return_value = self.mock_sword

        # Call method
        success, message, response = InventoryService.update_item(1, {
            "name": "Updated Sword",
            "weight": 6.0
        })

        # Verify result
        self.assertTrue(success)
        self.assertEqual(message, "Item updated successfully")
        self.assertIsNotNone(response)

        # Verify mock was called correctly
        self.mock_item_repo.update.assert_called_once_with(1, {"name": "Updated Sword", "weight": 6.0})

    def test_update_item_not_found(self):
        """Test updating a non-existent item."""
        # Configure mock
        self.mock_item_repo.update.return_value = None

        # Call method
        success, message, response = InventoryService.update_item(999, {
            "name": "Updated Sword"
        })

        # Verify result
        self.assertFalse(success)
        self.assertIn("not found", message)
        self.assertIsNone(response)

    def test_delete_item_success(self):
        """Test deleting an item successfully."""
        # Configure mocks
        self.mock_item_repo.get_by_id.return_value = self.mock_sword
        self.mock_db.session.query.return_value.filter.return_value.count.return_value = 0
        self.mock_item_repo.delete.return_value = True

        # Call method
        success, message = InventoryService.delete_item(1)

        # Verify result
        self.assertTrue(success)
        self.assertEqual(message, "Item deleted successfully")

        # Verify mocks were called correctly
        self.mock_item_repo.get_by_id.assert_called_once_with(1)
        self.mock_item_repo.delete.assert_called_once_with(1)

    def test_delete_item_not_found(self):
        """Test deleting a non-existent item."""
        # Configure mock
        self.mock_item_repo.get_by_id.return_value = None

        # Call method
        success, message = InventoryService.delete_item(999)

        # Verify result
        self.assertFalse(success)
        self.assertIn("not found", message)

    def test_delete_item_in_use(self):
        """Test deleting an item that is in use."""
        # Configure mocks
        self.mock_item_repo.get_by_id.return_value = self.mock_sword
        self.mock_db.session.query.return_value.filter.return_value.count.return_value = 3

        # Call method
        success, message = InventoryService.delete_item(1)

        # Verify result
        self.assertFalse(success)
        self.assertIn("Cannot delete item that is used", message)

    def test_get_item_success(self):
        """Test getting an item successfully."""
        # Configure mock
        self.mock_item_repo.get_by_id.return_value = self.mock_sword

        # Call method
        success, message, response = InventoryService.get_item(1)

        # Verify result
        self.assertTrue(success)
        self.assertEqual(message, "Item retrieved successfully")
        self.assertIsNotNone(response)

        # Verify mock was called correctly
        self.mock_item_repo.get_by_id.assert_called_once_with(1)

    def test_get_item_not_found(self):
        """Test getting a non-existent item."""
        # Configure mock
        self.mock_item_repo.get_by_id.return_value = None

        # Call method
        success, message, response = InventoryService.get_item(999)

        # Verify result
        self.assertFalse(success)
        self.assertIn("not found", message)
        self.assertIsNone(response)

    def test_get_items_all(self):
        """Test getting all items."""
        # Configure mock
        self.mock_item_repo.get_all.return_value = [self.mock_sword, self.mock_potion]

        # Call method
        success, message, responses = InventoryService.get_items()

        # Verify result
        self.assertTrue(success)
        self.assertIn("Retrieved 2 items", message)
        self.assertEqual(len(responses), 2)

        # Verify mock was called correctly
        self.mock_item_repo.get_all.assert_called_once_with(100, 0)

    def test_get_items_with_search(self):
        """Test getting items with search query."""
        # Configure mock
        self.mock_item_repo.search.return_value = [self.mock_sword]

        # Call method
        success, message, responses = InventoryService.get_items(search_query="sword")

        # Verify result
        self.assertTrue(success)
        self.assertIn("Retrieved 1 items", message)
        self.assertEqual(len(responses), 1)

        # Verify mock was called correctly
        self.mock_item_repo.search.assert_called_once_with("sword", 100, 0)

    def test_get_items_with_category(self):
        """Test getting items with category filter."""
        # Configure mock
        self.mock_item_repo.get_by_category.return_value = [self.mock_sword]

        # Call method
        success, message, responses = InventoryService.get_items(category="weapon")

        # Verify result
        self.assertTrue(success)
        self.assertIn("Retrieved 1 items", message)
        self.assertEqual(len(responses), 1)

        # Verify mock was called correctly
        self.mock_item_repo.get_by_category.assert_called_once_with("weapon", 100, 0)

    def test_create_inventory_success(self):
        """Test creating an inventory successfully."""
        # Configure mock
        self.mock_inventory_repo.create.return_value = self.mock_inventory

        # Call method
        success, message, response = InventoryService.create_inventory({
            "owner_id": 100,
            "owner_type": "character",
            "capacity": 50
        })

        # Verify result
        self.assertTrue(success)
        self.assertEqual(message, "Inventory created successfully")
        self.assertIsNotNone(response)

        # Verify mock was called correctly
        self.mock_inventory_repo.create.assert_called_once()

    @patch("backend.systems.inventory.service.InventoryItemResponse")
    def test_add_item_to_inventory_success(self, mock_response_class):
        """Test adding an item to inventory successfully."""
        # Configure mocks
        mock_validation = MagicMock()
        mock_validation.is_valid = True
        mock_validation.data = {"inventory": self.mock_inventory}
        self.mock_validator.validate_add_item.return_value = mock_validation
        
        self.mock_inventory_item_repo.add_item.return_value = self.mock_inventory_item
        mock_response_class.from_orm.return_value = MagicMock()

        # Call method
        success, message, response = InventoryService.add_item_to_inventory(1, 1, 1)

        # Verify result
        self.assertTrue(success)
        self.assertEqual(message, "Item added to inventory successfully")
        self.assertIsNotNone(response)

    def test_add_item_to_inventory_not_found(self):
        """Test adding an item to non-existent inventory."""
        # Configure mock validation to fail
        mock_validation = MagicMock()
        mock_validation.is_valid = False
        mock_validation.error_message = "Inventory with ID 999 not found"
        self.mock_validator.validate_add_item.return_value = mock_validation

        # Call method
        success, message, response = InventoryService.add_item_to_inventory(999, 1, 1)

        # Verify result
        self.assertFalse(success)
        self.assertIn("Inventory with ID 999 not found", message)
        self.assertIsNone(response)

    def test_remove_item_from_inventory_success(self):
        """Test removing an item from inventory successfully."""
        # Configure mocks
        self.mock_inventory_item_repo.remove_item.return_value = None  # Item completely removed

        # Call method
        success, message = InventoryService.remove_item_from_inventory(1, 1)

        # Verify result
        self.assertTrue(success)
        self.assertEqual(message, "Item removed from inventory completely")

    @patch("backend.systems.inventory.service.InventoryItemResponse")
    def test_equip_item_success(self, mock_response_class):
        """Test equipping an item successfully."""
        # Configure mocks
        mock_validation = MagicMock()
        mock_validation.is_valid = True
        mock_validation.data = {}
        self.mock_validator.validate_equip_item.return_value = mock_validation
        
        self.mock_inventory_item_repo.equip_item.return_value = self.mock_inventory_item
        mock_response_class.from_orm.return_value = MagicMock()

        # Call method
        success, message, response = InventoryService.equip_item(1, 1)

        # Verify result
        self.assertTrue(success)
        self.assertEqual(message, "Item equipped successfully")
        self.assertIsNotNone(response)

    @patch("backend.systems.inventory.service.InventoryItemResponse")
    def test_unequip_item_success(self, mock_response_class):
        """Test unequipping an item successfully."""
        # Configure mocks
        mock_validation = MagicMock()
        mock_validation.is_valid = True
        mock_validation.data = {}
        self.mock_validator.validate_unequip_item.return_value = mock_validation
        
        self.mock_inventory_item_repo.unequip_item.return_value = self.mock_inventory_item
        mock_response_class.from_orm.return_value = MagicMock()

        # Call method
        success, message, response = InventoryService.unequip_item(1, 1)

        # Verify result
        self.assertTrue(success)
        self.assertEqual(message, "Item unequipped successfully")
        self.assertIsNotNone(response)

    def test_transfer_item_success(self):
        """Test transferring an item between inventories successfully."""
        # Configure mocks
        source_inventory = MagicMock(spec=Inventory)
        source_inventory.id = 1
        target_inventory = MagicMock(spec=Inventory)
        target_inventory.id = 2

        self.mock_inventory_repo.get_by_id.side_effect = [source_inventory, target_inventory]
        self.mock_inventory_item_repo.get_by_id.return_value = self.mock_inventory_item
        self.mock_inventory_item_repo.create.return_value = self.mock_inventory_item

        # Call method
        success, message, result = InventoryService.transfer_item(1, 2, 1, 1)

        # Verify result
        self.assertTrue(success)
        self.assertIn("Successfully transferred", message)
        self.assertIsInstance(result, dict)

    def test_get_inventory_stats_success(self):
        """Test getting inventory statistics successfully."""
        # Configure mocks
        self.mock_inventory_repo.get_by_id.return_value = self.mock_inventory
        
        # Mock InventoryRepository.get_stats to return proper structure
        self.mock_inventory_repo.get_stats.return_value = {
            "total_items": 5,
            "unique_items": 3,
            "total_weight": 10.0,
            "total_value": 500,
            "used_capacity_pct": 10.0,
            "used_weight_pct": 10.0
        }

        # Call method
        success, message, stats = InventoryService.get_inventory_stats(1)

        # Verify result
        self.assertTrue(success)
        self.assertEqual(message, "Inventory statistics retrieved successfully")
        self.assertIsNotNone(stats)

    def test_validate_inventory_operation_success(self):
        """Test validating an inventory operation successfully."""
        # Configure mock
        mock_validation = MagicMock()
        mock_validation.is_valid = True
        mock_validation.error_message = None
        mock_validation.data = {}
        self.mock_validator.validate_add_item.return_value = mock_validation

        # Call method
        success, response = InventoryService.validate_inventory_operation("add_item", {
            "inventory_id": 1,
            "item_id": 1,
            "quantity": 1
        })

        # Verify result
        self.assertTrue(success)
        self.assertIsNotNone(response)
        self.assertTrue(response.valid)

        # Verify mock was called correctly
        self.mock_validator.validate_add_item.assert_called_once_with(1, 1, 1)


if __name__ == "__main__":
    unittest.main()
