from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
"""
Tests for Inventory Export functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from backend.systems.inventory.export import InventoryExporter
from backend.systems.inventory.models.item import Item
from backend.systems.inventory.models.inventory import Inventory
from backend.systems.inventory.models.inventory_item import InventoryItem


class TestInventoryExporter(unittest.TestCase): pass
    """Test cases for InventoryExporter."""

    def setUp(self): pass
        """Set up test fixtures."""
        # Create mock inventory
        self.mock_inventory = MagicMock(spec=Inventory)
        self.mock_inventory.id = 1
        self.mock_inventory.name = "Test Inventory"
        self.mock_inventory.description = "A test inventory"
        self.mock_inventory.inventory_type = "character"
        self.mock_inventory.owner_id = 100
        self.mock_inventory.capacity = 50
        self.mock_inventory.weight_limit = 100.0
        self.mock_inventory.is_public = False
        self.mock_inventory.created_at = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_inventory.updated_at = datetime(2023, 1, 2, 12, 0, 0)

        # Create mock item
        self.mock_item = MagicMock(spec=Item)
        self.mock_item.id = 1
        self.mock_item.name = "Test Sword"
        self.mock_item.description = "A test sword"
        self.mock_item.category = "weapon"
        self.mock_item.weight = 5.0
        self.mock_item.value = 15.0
        self.mock_item.properties = {"damage": 10}

        # Create mock inventory item
        self.mock_inventory_item = MagicMock(spec=InventoryItem)
        self.mock_inventory_item.id = 1
        self.mock_inventory_item.item_id = 1
        self.mock_inventory_item.item = self.mock_item
        self.mock_inventory_item.quantity = 1
        self.mock_inventory_item.is_equipped = False
        self.mock_inventory_item.custom_name = None
        self.mock_inventory_item.position = {"x": 0, "y": 0}

        # Set up inventory items relationship
        self.mock_inventory.items = [self.mock_inventory_item]

    @patch("backend.systems.inventory.export.InventoryService")
    @patch("backend.systems.inventory.export.InventoryRepository")
    def test_export_to_json_success(self, mock_inventory_repo, mock_inventory_service): pass
        """Test successful export to JSON."""
        # Configure mocks
        mock_inventory_repo.get_inventory.return_value = self.mock_inventory
        mock_inventory_service.calculate_inventory_stats.return_value = {
            "total_weight": 5.0,
            "total_value": 15.0,
            "item_count": 1
        }

        # Call method
        success, error, data = InventoryExporter.export_to_json(1)

        # Verify result
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertIsNotNone(data)

        # Verify data structure
        self.assertIn("inventory", data)
        self.assertIn("items", data)
        self.assertIn("stats", data)
        self.assertIn("export_timestamp", data)

        # Verify inventory data
        inventory_data = data["inventory"]
        self.assertEqual(inventory_data["id"], 1)
        self.assertEqual(inventory_data["name"], "Test Inventory")
        self.assertEqual(inventory_data["owner_id"], 100)

        # Verify items data
        items_data = data["items"]
        self.assertEqual(len(items_data), 1)
        item_data = items_data[0]
        self.assertEqual(item_data["item_id"], 1)
        self.assertEqual(item_data["name"], "Test Sword")
        self.assertEqual(item_data["quantity"], 1)

        # Verify mocks were called
        mock_inventory_repo.get_inventory.assert_called_once_with(1)
        mock_inventory_service.calculate_inventory_stats.assert_called_once_with(1)

    @patch("backend.systems.inventory.export.InventoryRepository")
    def test_export_to_json_inventory_not_found(self, mock_inventory_repo): pass
        """Test export when inventory is not found."""
        # Configure mock
        mock_inventory_repo.get_inventory.return_value = None

        # Call method
        success, error, data = InventoryExporter.export_to_json(999)

        # Verify result
        self.assertFalse(success)
        self.assertEqual(error, "Inventory not found")
        self.assertIsNone(data)

        # Verify mock was called
        mock_inventory_repo.get_inventory.assert_called_once_with(999)

    @patch("backend.systems.inventory.export.InventoryRepository")
    def test_export_to_json_exception(self, mock_inventory_repo): pass
        """Test export when an exception occurs."""
        # Configure mock to raise exception
        mock_inventory_repo.get_inventory.side_effect = Exception("Database error")

        # Call method
        success, error, data = InventoryExporter.export_to_json(1)

        # Verify result
        self.assertFalse(success)
        self.assertIn("Error: Database error", error)
        self.assertIsNone(data)

    @patch("backend.systems.inventory.export.db")
    @patch("backend.systems.inventory.export.InventoryItemRepository")
    @patch("backend.systems.inventory.export.ItemRepository")
    @patch("backend.systems.inventory.export.InventoryRepository")
    def test_import_from_json_success(self, mock_inventory_repo, mock_item_repo, 
                                     mock_inventory_item_repo, mock_db): pass
        """Test successful import from JSON."""
        # Prepare test data
        import_data = {
            "inventory": {
                "name": "Imported Inventory",
                "description": "An imported inventory",
                "inventory_type": "character",
                "owner_id": 200,
                "capacity": 30,
                "weight_limit": 80.0,
                "is_public": True
            },
            "items": [
                {
                    "item_id": 1,
                    "quantity": 2,
                    "is_equipped": True
                },
                {
                    "item_id": 2,
                    "quantity": 1,
                    "is_equipped": False
                }
            ]
        }

        # Configure mocks
        mock_inventory_repo.create_inventory.return_value = self.mock_inventory
        mock_item_repo.get_item.return_value = self.mock_item
        mock_db.session.begin.return_value.__enter__ = MagicMock()
        mock_db.session.begin.return_value.__exit__ = MagicMock()

        # Call method
        success, error, inventory = InventoryExporter.import_from_json(import_data)

        # Verify result
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertIsNotNone(inventory)

        # Verify mocks were called
        mock_inventory_repo.create_inventory.assert_called_once()
        self.assertEqual(mock_item_repo.get_item.call_count, 2)
        self.assertEqual(mock_inventory_item_repo.add_item_to_inventory.call_count, 2)

    @patch("backend.systems.inventory.export.db")
    @patch("backend.systems.inventory.export.InventoryItemRepository")
    @patch("backend.systems.inventory.export.ItemRepository")
    @patch("backend.systems.inventory.export.InventoryRepository")
    def test_import_from_json_with_owner_override(self, mock_inventory_repo, mock_item_repo, 
                                                 mock_inventory_item_repo, mock_db): pass
        """Test import with owner ID override."""
        # Prepare test data
        import_data = {
            "inventory": {
                "name": "Imported Inventory",
                "owner_id": 200
            },
            "items": []
        }

        # Configure mocks
        mock_inventory_repo.create_inventory.return_value = self.mock_inventory
        mock_db.session.begin.return_value.__enter__ = MagicMock()
        mock_db.session.begin.return_value.__exit__ = MagicMock()

        # Call method with owner override
        success, error, inventory = InventoryExporter.import_from_json(import_data, owner_id=300)

        # Verify result
        self.assertTrue(success)
        self.assertIsNone(error)

        # Verify owner was overridden
        call_args = mock_inventory_repo.create_inventory.call_args[0][0]
        self.assertEqual(call_args["owner_id"], 300)

    @patch("backend.systems.inventory.export.db")
    @patch("backend.systems.inventory.export.ItemRepository")
    @patch("backend.systems.inventory.export.InventoryRepository")
    def test_import_from_json_skip_missing_item(self, mock_inventory_repo, mock_item_repo, mock_db): pass
        """Test import skips items that don't exist."""
        # Prepare test data
        import_data = {
            "inventory": {
                "name": "Imported Inventory"
            },
            "items": [
                {
                    "item_id": 999,  # Non-existent item
                    "quantity": 1
                }
            ]
        }

        # Configure mocks
        mock_inventory_repo.create_inventory.return_value = self.mock_inventory
        mock_item_repo.get_item.return_value = None  # Item not found
        mock_db.session.begin.return_value.__enter__ = MagicMock()
        mock_db.session.begin.return_value.__exit__ = MagicMock()

        # Call method
        success, error, inventory = InventoryExporter.import_from_json(import_data)

        # Verify result
        self.assertTrue(success)
        self.assertIsNone(error)

        # Verify item lookup was attempted
        mock_item_repo.get_item.assert_called_once_with(999)

    @patch("backend.systems.inventory.export.db")
    @patch("backend.systems.inventory.export.InventoryRepository")
    def test_import_from_json_skip_item_without_id(self, mock_inventory_repo, mock_db): pass
        """Test import skips items without item_id."""
        # Prepare test data
        import_data = {
            "inventory": {
                "name": "Imported Inventory"
            },
            "items": [
                {
                    "quantity": 1  # Missing item_id
                }
            ]
        }

        # Configure mocks
        mock_inventory_repo.create_inventory.return_value = self.mock_inventory
        mock_db.session.begin.return_value.__enter__ = MagicMock()
        mock_db.session.begin.return_value.__exit__ = MagicMock()

        # Call method
        success, error, inventory = InventoryExporter.import_from_json(import_data)

        # Verify result
        self.assertTrue(success)
        self.assertIsNone(error)

    @patch("backend.systems.inventory.export.db")
    @patch("backend.systems.inventory.export.InventoryRepository")
    def test_import_from_json_exception(self, mock_inventory_repo, mock_db): pass
        """Test import when an exception occurs."""
        # Configure mock to raise exception
        mock_inventory_repo.create_inventory.side_effect = Exception("Database error")
        
        # Mock the context manager to allow the exception to propagate
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock()
        mock_context.__exit__ = MagicMock(return_value=False)  # Don't suppress exceptions
        mock_db.session.begin.return_value = mock_context

        # Prepare test data
        import_data = {
            "inventory": {
                "name": "Imported Inventory"
            },
            "items": []
        }

        # Call method
        success, error, inventory = InventoryExporter.import_from_json(import_data)

        # Verify result
        self.assertFalse(success)
        self.assertIn("Error: Database error", error)
        self.assertIsNone(inventory)

        # Verify rollback was called
        mock_db.session.rollback.assert_called_once()

    def test_export_to_json_with_none_timestamps(self): pass
        """Test export handles None timestamps correctly."""
        # Create inventory with None timestamps
        self.mock_inventory.created_at = None
        self.mock_inventory.updated_at = None

        with patch("backend.systems.inventory.export.InventoryRepository") as mock_repo, \
             patch("backend.systems.inventory.export.InventoryService") as mock_service: pass
            mock_repo.get_inventory.return_value = self.mock_inventory
            mock_service.calculate_inventory_stats.return_value = {}

            # Call method
            success, error, data = InventoryExporter.export_to_json(1)

            # Verify result
            self.assertTrue(success)
            self.assertIsNone(error)
            
            # Verify None timestamps are handled
            inventory_data = data["inventory"]
            self.assertIsNone(inventory_data["created_at"])
            self.assertIsNone(inventory_data["updated_at"])


if __name__ == "__main__": pass
    unittest.main()
