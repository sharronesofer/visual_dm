from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
"""
Comprehensive router tests for inventory system.

This module provides complete test coverage for all FastAPI endpoints
to achieve 90% coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json

from backend.systems.inventory.router import router


class TestInventoryRouter: pass
    """Test class for inventory router endpoints."""

    @pytest.fixture
    def client(self): pass
        """Create test client."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def mock_service(self): pass
        """Mock inventory service."""
        with patch('backend.systems.inventory.router.InventoryService') as mock: pass
            yield mock

    @pytest.fixture
    def sample_item_data(self): pass
        """Sample item data for testing."""
        return {
            "id": 1,
            "name": "Test Item",
            "description": "A test item",
            "weight": 1.0,
            "value": 10.0,
            "stackable": True,
            "max_stack": 100
        }

    @pytest.fixture
    def sample_inventory_data(self): pass
        """Sample inventory data for testing."""
        return {
            "id": 1,
            "name": "Test Inventory",
            "description": "A test inventory",
            "owner_id": 123,
            "owner_type": "character",
            "capacity": 100.0,
            "used_capacity": 25.0
        }

    # Item endpoints tests
    def test_get_items_success(self, client, mock_service, sample_item_data): pass
        """Test successful item retrieval."""
        mock_item = Mock()
        mock_item.to_dict.return_value = sample_item_data
        mock_service.get_items.return_value = (True, "Success", [mock_item])
        
        response = client.get("/inventory/items")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Item"

    def test_get_items_with_filters(self, client, mock_service, sample_item_data): pass
        """Test item retrieval with filters."""
        mock_item = Mock()
        mock_item.to_dict.return_value = sample_item_data
        mock_service.get_items.return_value = (True, "Success", [mock_item])
        
        response = client.get("/inventory/items?limit=50&offset=10&category=weapon")
        
        assert response.status_code == 200
        mock_service.get_items.assert_called_with(limit=50, offset=10, category="weapon")

    def test_get_items_service_error(self, client, mock_service): pass
        """Test item retrieval when service returns error."""
        mock_service.get_items.return_value = (False, "Service error", [])
        
        response = client.get("/inventory/items")
        
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]

    def test_get_items_exception(self, client, mock_service): pass
        """Test item retrieval with exception."""
        mock_service.get_items.side_effect = Exception("Database error")
        
        response = client.get("/inventory/items")
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

    def test_get_item_success(self, client, mock_service, sample_item_data): pass
        """Test successful single item retrieval."""
        mock_item = Mock()
        mock_item.to_dict.return_value = sample_item_data
        mock_service.get_item.return_value = (True, "Success", mock_item)
        
        response = client.get("/inventory/items/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Item"

    def test_get_item_not_found(self, client, mock_service): pass
        """Test item retrieval when item not found."""
        mock_service.get_item.return_value = (False, "Item not found", None)
        
        response = client.get("/inventory/items/999")
        
        assert response.status_code == 404
        assert "Item not found" in response.json()["detail"]

    def test_create_item_success(self, client, mock_service, sample_item_data): pass
        """Test successful item creation."""
        mock_item = Mock()
        mock_item.to_dict.return_value = sample_item_data
        mock_service.create_item.return_value = (True, None, mock_item)
        
        response = client.post("/inventory/items", json=sample_item_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Item"

    def test_create_item_validation_error(self, client, mock_service): pass
        """Test item creation with validation error."""
        mock_service.create_item.return_value = (False, "Invalid data", None)
        
        response = client.post("/inventory/items", json={"invalid": "data"})
        
        assert response.status_code == 400
        assert "Invalid data" in response.json()["detail"]

    def test_create_item_exception(self, client, mock_service): pass
        """Test item creation with exception."""
        mock_service.create_item.side_effect = Exception("Database error")
        
        response = client.post("/inventory/items", json={"name": "Test"})
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

    def test_update_item_success(self, client, mock_service, sample_item_data): pass
        """Test successful item update."""
        mock_item = Mock()
        mock_item.to_dict.return_value = sample_item_data
        mock_service.update_item.return_value = (True, None, mock_item)
        
        response = client.put("/inventory/items/1", json={"name": "Updated Item"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Item"

    def test_update_item_not_found(self, client, mock_service): pass
        """Test item update when item not found."""
        mock_service.update_item.return_value = (False, "Item not found", None)
        
        response = client.put("/inventory/items/999", json={"name": "Updated"})
        
        assert response.status_code == 404
        assert "Item not found" in response.json()["detail"]

    def test_delete_item_success(self, client, mock_service): pass
        """Test successful item deletion."""
        mock_service.delete_item.return_value = (True, None)
        
        response = client.delete("/inventory/items/1")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]

    def test_delete_item_not_found(self, client, mock_service): pass
        """Test item deletion when item not found."""
        mock_service.delete_item.return_value = (False, "Item not found")
        
        response = client.delete("/inventory/items/999")
        
        assert response.status_code == 404
        assert "Item not found" in response.json()["detail"]

    # Inventory endpoints tests
    def test_get_inventories_success(self, client, mock_service, sample_inventory_data): pass
        """Test successful inventory retrieval."""
        mock_inventory = Mock()
        mock_inventory.to_dict.return_value = sample_inventory_data
        mock_service.get_inventories.return_value = (True, "Success", [mock_inventory], 1)
        
        response = client.get("/inventory/inventories")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Inventory"

    def test_get_inventories_with_filters(self, client, mock_service, sample_inventory_data): pass
        """Test inventory retrieval with filters."""
        mock_inventory = Mock()
        mock_inventory.to_dict.return_value = sample_inventory_data
        mock_service.get_inventories.return_value = (True, "Success", [mock_inventory], 1)
        
        response = client.get("/inventory/inventories?owner_id=123&inventory_type=character")
        
        assert response.status_code == 200
        # Verify filters were passed correctly
        call_args = mock_service.get_inventories.call_args
        filters = call_args[1]['filters']
        assert filters['owner_id'] == 123
        assert filters['inventory_type'] == "character"

    def test_get_inventory_success(self, client, mock_service, sample_inventory_data): pass
        """Test successful single inventory retrieval."""
        mock_inventory = Mock()
        mock_inventory.to_dict.return_value = sample_inventory_data
        mock_service.get_inventory.return_value = (True, "Success", mock_inventory)
        
        response = client.get("/inventory/inventories/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Inventory"

    def test_get_inventory_with_items(self, client, mock_service, sample_inventory_data): pass
        """Test inventory retrieval with items included."""
        mock_inventory = Mock()
        mock_inventory.to_dict.return_value = sample_inventory_data
        mock_service.get_inventory.return_value = (True, "Success", mock_inventory)
        
        response = client.get("/inventory/inventories/1?with_items=true")
        
        assert response.status_code == 200
        mock_service.get_inventory.assert_called_with(1, include_items=True)

    def test_create_inventory_success(self, client, mock_service, sample_inventory_data): pass
        """Test successful inventory creation."""
        mock_inventory = Mock()
        mock_inventory.to_dict.return_value = sample_inventory_data
        mock_service.create_inventory.return_value = (True, None, mock_inventory)
        
        response = client.post("/inventory/inventories", json=sample_inventory_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Inventory"

    def test_update_inventory_success(self, client, mock_service, sample_inventory_data): pass
        """Test successful inventory update."""
        mock_inventory = Mock()
        mock_inventory.to_dict.return_value = sample_inventory_data
        mock_service.update_inventory.return_value = (True, None, mock_inventory)
        
        response = client.put("/inventory/inventories/1", json={"name": "Updated"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Inventory"

    def test_delete_inventory_success(self, client, mock_service): pass
        """Test successful inventory deletion."""
        mock_service.delete_inventory.return_value = (True, None)
        
        response = client.delete("/inventory/inventories/1")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]

    # Inventory items endpoints tests
    def test_get_inventory_items_success(self, client, mock_service, sample_item_data): pass
        """Test successful inventory items retrieval."""
        mock_item = Mock()
        mock_item.to_dict.return_value = sample_item_data
        mock_service.get_inventory_items.return_value = (True, "Success", [mock_item])
        
        response = client.get("/inventory/inventories/1/items")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Item"

    def test_add_item_to_inventory_success(self, client, mock_service, sample_item_data): pass
        """Test successful item addition to inventory."""
        mock_item = Mock()
        mock_item.to_dict.return_value = sample_item_data
        mock_service.add_item_to_inventory.return_value = (True, None, mock_item)
        
        item_data = {"item_id": 1, "quantity": 5}
        response = client.post("/inventory/inventories/1/items", json=item_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Item"

    def test_remove_item_from_inventory_success(self, client, mock_service): pass
        """Test successful item removal from inventory."""
        mock_service.remove_item_from_inventory.return_value = (True, None, {"removed": True})
        
        response = client.delete("/inventory/inventories/1/items/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["removed"] is True

    def test_remove_item_partial_quantity(self, client, mock_service): pass
        """Test partial item removal from inventory."""
        mock_service.remove_item_from_inventory.return_value = (True, None, {"removed": True})
        
        response = client.delete("/inventory/inventories/1/items/1?quantity=3")
        
        assert response.status_code == 200
        mock_service.remove_item_from_inventory.assert_called_with(1, 1, quantity=3)

    def test_update_inventory_item_success(self, client, mock_service, sample_item_data): pass
        """Test successful inventory item update."""
        mock_item = Mock()
        mock_item.to_dict.return_value = sample_item_data
        mock_service.update_inventory_item.return_value = (True, None, mock_item)
        
        updates = {"quantity": 10, "is_equipped": True}
        response = client.put("/inventory/inventories/1/items/1", json=updates)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Item"

    # Transfer endpoints tests
    @patch('backend.systems.inventory.router.get_current_user')
    def test_transfer_item_success(self, mock_auth, client, mock_service): pass
        """Test successful item transfer."""
        mock_auth.return_value = Mock(id=1)
        mock_service.transfer_item.return_value = (True, None, {"transferred": True})
        
        transfer_data = {
            "from_inventory_id": 1,
            "to_inventory_id": 2,
            "item_id": 1,
            "quantity": 3
        }
        response = client.post("/inventory/transfer", json=transfer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["transferred"] is True

    @patch('backend.systems.inventory.router.transfer_item_between_inventories')
    def test_transfer_item_alternative_endpoint(self, mock_transfer, client): pass
        """Test alternative transfer endpoint."""
        mock_transfer.return_value = (True, "Transfer successful", {"transferred": True})
        
        response = client.post("/inventory/inventory/1/transfer/2/1", json={"quantity": 3})
        
        assert response.status_code == 200
        data = response.json()
        assert data["transferred"] is True

    @patch('backend.systems.inventory.router.get_current_user')
    def test_bulk_transfer_success(self, mock_auth, client, mock_service): pass
        """Test successful bulk transfer."""
        mock_auth.return_value = Mock(id=1)
        mock_service.bulk_transfer_items.return_value = (True, None, {"transferred": 5})
        
        items_data = [
            {"item_id": 1, "quantity": 3},
            {"item_id": 2, "quantity": 2}
        ]
        response = client.post("/inventory/inventory/1/bulk-transfer/2", json=items_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["transferred"] == 5

    # Stats and utility endpoints tests
    def test_get_inventory_stats_success(self, client, mock_service): pass
        """Test successful inventory stats retrieval."""
        stats = {"total_items": 10, "total_weight": 25.5, "total_value": 100.0}
        mock_service.get_inventory_stats.return_value = (True, None, stats)
        
        response = client.get("/inventory/inventories/1/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == 10
        assert data["total_weight"] == 25.5

    def test_backup_inventory_success(self, client, mock_service): pass
        """Test successful inventory backup."""
        backup_data = {"backup_id": "backup_123", "timestamp": "2023-01-01T00:00:00"}
        mock_service.backup_inventory.return_value = (True, None, backup_data)
        
        response = client.post("/inventory/inventories/1/backup")
        
        assert response.status_code == 200
        data = response.json()
        assert data["backup_id"] == "backup_123"

    def test_restore_inventory_success(self, client, mock_service, sample_inventory_data): pass
        """Test successful inventory restore."""
        mock_inventory = Mock()
        mock_inventory.to_dict.return_value = sample_inventory_data
        mock_service.restore_inventory.return_value = (True, None, mock_inventory)
        
        backup_data = {"backup_id": "backup_123", "data": {}}
        response = client.post("/inventory/inventories/restore", json=backup_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Inventory"

    def test_export_inventory_success(self, client, mock_service): pass
        """Test successful inventory export."""
        export_data = {"export_id": "export_123", "format": "json"}
        mock_service.export_inventory.return_value = (True, None, export_data)
        
        response = client.post("/inventory/inventories/1/export")
        
        assert response.status_code == 200
        data = response.json()
        assert data["export_id"] == "export_123"

    def test_import_inventory_success(self, client, mock_service, sample_inventory_data): pass
        """Test successful inventory import."""
        mock_inventory = Mock()
        mock_inventory.to_dict.return_value = sample_inventory_data
        mock_service.import_inventory.return_value = (True, None, mock_inventory)
        
        import_data = {"format": "json", "data": {}}
        response = client.post("/inventory/inventories/import", json=import_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Inventory"

    # Stack management endpoints tests
    @patch('backend.systems.inventory.router.InventoryService')
    def test_swap_items_success(self, mock_service, client): pass
        """Test successful item swapping."""
        mock_service.swap_items.return_value = (True, None, {"swapped": True})
        
        swap_data = {"item1_id": 1, "item2_id": 2}
        response = client.post("/inventory/inventories/1/swap", json=swap_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["swapped"] is True

    @patch('backend.systems.inventory.router.InventoryService')
    def test_split_stack_success(self, mock_service, client): pass
        """Test successful stack splitting."""
        mock_service.split_stack.return_value = (True, None, {"split": True})
        
        response = client.post("/inventory/inventories/1/split-stack/1", json={"quantity": 5})
        
        assert response.status_code == 200
        data = response.json()
        assert data["split"] is True

    @patch('backend.systems.inventory.router.InventoryService')
    def test_combine_stacks_success(self, mock_service, client): pass
        """Test successful stack combining."""
        mock_service.combine_stacks.return_value = (True, None, {"combined": True})
        
        combine_data = {"stack_ids": [1, 2]}
        response = client.post("/inventory/inventories/1/combine-stacks", json=combine_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["combined"] is True

    @patch('backend.systems.inventory.router.InventoryService')
    def test_optimize_stacks_success(self, mock_service, client): pass
        """Test successful stack optimization."""
        mock_service.optimize_stacks.return_value = (True, None, {"optimized": True})
        
        response = client.post("/inventory/inventories/1/optimize-stacks")
        
        assert response.status_code == 200
        data = response.json()
        assert data["optimized"] is True

    @patch('backend.systems.inventory.router.InventoryService')
    def test_filter_items_success(self, mock_service, client): pass
        """Test successful item filtering."""
        mock_service.filter_items.return_value = (True, None, {"filtered": [1, 2, 3]})
        
        filters = {"category": "weapon", "min_value": 10}
        response = client.post("/inventory/inventories/1/filter", json=filters)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["filtered"]) == 3

    # Admin endpoints tests
    @patch('backend.systems.inventory.router.InventoryService')
    def test_run_migrations_success(self, mock_service, client): pass
        """Test successful migration execution."""
        mock_service.run_migrations.return_value = (True, None, {"migrations_run": 3})
        
        response = client.post("/inventory/admin/inventory/run-migrations")
        
        assert response.status_code == 200
        data = response.json()
        assert data["migrations_run"] == 3

    # Error handling tests
    def test_auth_not_available_error(self, client): pass
        """Test behavior when auth service is not available."""
        with patch('backend.systems.inventory.router._auth_available', False): pass
            response = client.post("/inventory/transfer", json={})
            
            assert response.status_code == 501
            assert "Authentication service not available" in response.json()["detail"]

    def test_service_method_not_found(self, client, mock_service): pass
        """Test behavior when service method doesn't exist."""
        # Remove a method to simulate missing functionality
        del mock_service.get_items
        
        response = client.get("/inventory/items")
        
        assert response.status_code == 500

    def test_invalid_json_request(self, client): pass
        """Test behavior with invalid JSON in request."""
        response = client.post("/inventory/items", data="invalid json")
        
        assert response.status_code == 422  # Unprocessable Entity

    def test_missing_required_fields(self, client, mock_service): pass
        """Test behavior with missing required fields."""
        mock_service.create_item.return_value = (False, "Missing required fields", None)
        
        response = client.post("/inventory/items", json={})
        
        assert response.status_code == 400
        assert "Missing required fields" in response.json()["detail"] 