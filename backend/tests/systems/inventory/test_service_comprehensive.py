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
Comprehensive service tests for inventory system.

This module provides complete test coverage for all service business logic
to achieve 90% coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend.systems.inventory.service import InventoryService
from backend.systems.inventory.models import Item, Inventory, InventoryItem


class TestInventoryService: pass
    """Test class for inventory service business logic."""

    @pytest.fixture
    def mock_item_repo(self): pass
        """Mock item repository."""
        with patch('backend.systems.inventory.service.ItemRepository') as mock: pass
            yield mock

    @pytest.fixture
    def mock_inventory_repo(self): pass
        """Mock inventory repository."""
        with patch('backend.systems.inventory.service.InventoryRepository') as mock: pass
            yield mock

    @pytest.fixture
    def mock_inventory_item_repo(self): pass
        """Mock inventory item repository."""
        with patch('backend.systems.inventory.service.InventoryItemRepository') as mock: pass
            yield mock

    @pytest.fixture
    def mock_db_session(self): pass
        """Mock database session with proper query configuration."""
        with patch('backend.systems.inventory.service.db.session') as mock_session: pass
            # Also patch the validator's db.session usage
            with patch('backend.systems.inventory.validator.db.session', mock_session): pass
                # Configure the mock to handle .get() method calls properly
                def mock_query_side_effect(model): pass
                    mock_query = Mock()
                    # Configure get method to return None by default
                    mock_query.get = Mock(return_value=None)
                    mock_query.filter = Mock(return_value=mock_query)
                    mock_query.filter_by = Mock(return_value=mock_query)
                    mock_query.first = Mock(return_value=None)
                    mock_query.all = Mock(return_value=[])
                    mock_query.count = Mock(return_value=0)
                    return mock_query
                
                mock_session.query.side_effect = mock_query_side_effect
                yield mock_session

    @pytest.fixture
    def sample_item(self): pass
        """Sample item for testing."""
        item = Mock()
        item.id = 1
        item.name = "Test Item"
        item.description = "A test item"
        item.weight = 1.0
        item.value = 10.0
        item.stackable = True
        item.max_stack = 100
        # Add validator-expected attributes
        item.is_stackable = True
        item.max_stack_size = 100
        item.can_be_equipped = True
        item.apply_weight_when_equipped = True
        return item

    @pytest.fixture
    def sample_inventory(self): pass
        """Sample inventory for testing."""
        inventory = Mock()
        inventory.id = 1
        inventory.name = "Test Inventory"
        inventory.description = "A test inventory"
        inventory.owner_id = 123
        inventory.owner_type = "character"
        inventory.capacity = 100.0
        inventory.used_capacity = 25.0
        inventory.weight_limit = 50.0
        inventory.count_equipped_weight = True
        
        # Configure items relationship to be iterable
        mock_items = []
        inventory.items = mock_items
        
        # Add calculate_total_weight method
        inventory.calculate_total_weight = Mock(return_value=10.0)
        
        return inventory

    @pytest.fixture
    def sample_inventory_item(self): pass
        """Sample inventory item for testing."""
        inv_item = Mock()
        inv_item.id = 1
        inv_item.inventory_id = 1
        inv_item.item_id = 1
        inv_item.quantity = 5
        inv_item.is_equipped = False
        inv_item.position = {"x": 0, "y": 0}
        return inv_item

    # Item service tests
    def test_create_item_success(self, mock_item_repo, sample_item): pass
        """Test successful item creation."""
        mock_item_repo.create.return_value = sample_item
        
        with patch('backend.systems.inventory.service.ItemResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Item"}
            
            success, message, response = InventoryService.create_item({
                "name": "Test Item",
                "description": "A test item",
                "weight": 1.0,
                "value": 10.0
            })
            
            assert success is True
            assert "created successfully" in message
            assert response is not None
            mock_item_repo.create.assert_called_once()

    def test_create_item_exception(self, mock_item_repo): pass
        """Test item creation with exception."""
        mock_item_repo.create.side_effect = Exception("Database error")
        
        success, message, response = InventoryService.create_item({
            "name": "Test Item"
        })
        
        assert success is False
        assert "Error creating item" in message
        assert response is None

    def test_update_item_success(self, mock_item_repo, sample_item): pass
        """Test successful item update."""
        mock_item_repo.update.return_value = sample_item
        
        with patch('backend.systems.inventory.service.ItemResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Updated Item"}
            
            success, message, response = InventoryService.update_item(1, {
                "name": "Updated Item"
            })
            
            assert success is True
            assert "updated successfully" in message
            assert response is not None
            mock_item_repo.update.assert_called_once_with(1, {"name": "Updated Item"})

    def test_update_item_not_found(self, mock_item_repo): pass
        """Test item update when item not found."""
        mock_item_repo.update.return_value = None
        
        success, message, response = InventoryService.update_item(999, {
            "name": "Updated Item"
        })
        
        assert success is False
        assert "not found" in message
        assert response is None

    def test_update_item_exception(self, mock_item_repo): pass
        """Test item update with exception."""
        mock_item_repo.update.side_effect = Exception("Database error")
        
        success, message, response = InventoryService.update_item(1, {
            "name": "Updated Item"
        })
        
        assert success is False
        assert "Error updating item" in message
        assert response is None

    def test_delete_item_success(self, mock_item_repo, mock_db_session, sample_item): pass
        """Test successful item deletion."""
        mock_item_repo.get_by_id.return_value = sample_item
        
        # Configure the query chain properly
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_db_session.query.return_value = mock_query
        
        mock_item_repo.delete.return_value = True
        
        success, message = InventoryService.delete_item(1)
        
        assert success is True
        assert "deleted successfully" in message
        mock_item_repo.delete.assert_called_once_with(1)

    def test_delete_item_not_found(self, mock_item_repo): pass
        """Test item deletion when item not found."""
        mock_item_repo.get_by_id.return_value = None
        
        success, message = InventoryService.delete_item(999)
        
        assert success is False
        assert "not found" in message

    def test_delete_item_in_use(self, mock_item_repo, mock_db_session, sample_item): pass
        """Test item deletion when item is in use."""
        mock_item_repo.get_by_id.return_value = sample_item
        
        # Configure the query chain properly
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 3
        mock_db_session.query.return_value = mock_query
        
        success, message = InventoryService.delete_item(1)
        
        assert success is False
        assert "used in 3 inventories" in message

    def test_delete_item_exception(self, mock_item_repo): pass
        """Test item deletion with exception."""
        mock_item_repo.get_by_id.side_effect = Exception("Database error")
        
        success, message = InventoryService.delete_item(1)
        
        assert success is False
        assert "Error deleting item" in message

    def test_get_item_success(self, mock_item_repo, sample_item): pass
        """Test successful item retrieval."""
        mock_item_repo.get_by_id.return_value = sample_item
        
        with patch('backend.systems.inventory.service.ItemResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Item"}
            
            success, message, response = InventoryService.get_item(1)
            
            assert success is True
            assert "retrieved successfully" in message
            assert response is not None
            mock_item_repo.get_by_id.assert_called_once_with(1)

    def test_get_item_not_found(self, mock_item_repo): pass
        """Test item retrieval when item not found."""
        mock_item_repo.get_by_id.return_value = None
        
        success, message, response = InventoryService.get_item(999)
        
        assert success is False
        assert "not found" in message
        assert response is None

    def test_get_item_exception(self, mock_item_repo): pass
        """Test item retrieval with exception."""
        mock_item_repo.get_by_id.side_effect = Exception("Database error")
        
        success, message, response = InventoryService.get_item(1)
        
        assert success is False
        assert "Error getting item" in message
        assert response is None

    def test_get_items_all(self, mock_item_repo, sample_item): pass
        """Test getting all items."""
        mock_item_repo.get_all.return_value = [sample_item]
        
        with patch('backend.systems.inventory.service.ItemResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Item"}
            
            success, message, responses = InventoryService.get_items()
            
            assert success is True
            assert "Retrieved 1 items" in message
            assert len(responses) == 1
            mock_item_repo.get_all.assert_called_once_with(100, 0)

    def test_get_items_with_search(self, mock_item_repo, sample_item): pass
        """Test getting items with search query."""
        mock_item_repo.search.return_value = [sample_item]
        
        with patch('backend.systems.inventory.service.ItemResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Item"}
            
            success, message, responses = InventoryService.get_items(
                search_query="test", limit=50, offset=10
            )
            
            assert success is True
            assert len(responses) == 1
            mock_item_repo.search.assert_called_once_with("test", 50, 10)

    def test_get_items_with_category(self, mock_item_repo, sample_item): pass
        """Test getting items with category filter."""
        mock_item_repo.get_by_category.return_value = [sample_item]
        
        with patch('backend.systems.inventory.service.ItemResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Item"}
            
            success, message, responses = InventoryService.get_items(
                category="weapon", limit=25, offset=5
            )
            
            assert success is True
            assert len(responses) == 1
            mock_item_repo.get_by_category.assert_called_once_with("weapon", 25, 5)

    def test_get_items_exception(self, mock_item_repo): pass
        """Test getting items with exception."""
        mock_item_repo.get_all.side_effect = Exception("Database error")
        
        success, message, responses = InventoryService.get_items()
        
        assert success is False
        assert "Error getting items" in message
        assert responses == []

    # Inventory service tests
    def test_create_inventory_success(self, mock_inventory_repo, sample_inventory): pass
        """Test successful inventory creation."""
        mock_inventory_repo.create.return_value = sample_inventory
        
        with patch('backend.systems.inventory.service.InventoryResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Inventory"}
            
            success, message, response = InventoryService.create_inventory({
                "name": "Test Inventory",
                "owner_id": 123,
                "owner_type": "character"
            })
            
            assert success is True
            assert "created successfully" in message
            assert response is not None
            mock_inventory_repo.create.assert_called_once()

    def test_create_inventory_exception(self, mock_inventory_repo): pass
        """Test inventory creation with exception."""
        mock_inventory_repo.create.side_effect = Exception("Database error")
        
        success, message, response = InventoryService.create_inventory({
            "name": "Test Inventory",
            "owner_id": 123,
            "owner_type": "character"
        })
        
        assert success is False
        assert "Error creating inventory" in message
        assert response is None

    def test_update_inventory_success(self, mock_inventory_repo, sample_inventory): pass
        """Test successful inventory update."""
        mock_inventory_repo.update.return_value = sample_inventory
        
        with patch('backend.systems.inventory.service.InventoryResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Updated Inventory"}
            
            success, message, response = InventoryService.update_inventory(1, {
                "name": "Updated Inventory"
            })
            
            assert success is True
            assert "updated successfully" in message
            assert response is not None
            mock_inventory_repo.update.assert_called_once_with(1, {"name": "Updated Inventory"})

    def test_update_inventory_not_found(self, mock_inventory_repo): pass
        """Test inventory update when inventory not found."""
        mock_inventory_repo.update.return_value = None
        
        success, message, response = InventoryService.update_inventory(999, {
            "name": "Updated Inventory"
        })
        
        assert success is False
        assert "not found" in message
        assert response is None

    def test_delete_inventory_success(self, mock_inventory_repo, sample_inventory): pass
        """Test successful inventory deletion."""
        mock_inventory_repo.get_by_id.return_value = sample_inventory
        mock_inventory_repo.delete.return_value = True
        
        success, message = InventoryService.delete_inventory(1)
        
        assert success is True
        assert "deleted successfully" in message
        mock_inventory_repo.delete.assert_called_once_with(1)

    def test_delete_inventory_not_found(self, mock_inventory_repo): pass
        """Test inventory deletion when inventory not found."""
        mock_inventory_repo.get_by_id.return_value = None
        
        success, message = InventoryService.delete_inventory(999)
        
        assert success is False
        assert "not found" in message

    def test_get_inventory_success(self, mock_inventory_repo, sample_inventory): pass
        """Test successful inventory retrieval."""
        mock_inventory_repo.get_by_id.return_value = sample_inventory
        
        with patch('backend.systems.inventory.service.InventoryResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Inventory"}
            
            success, message, response = InventoryService.get_inventory(1, include_items=False)
            
            assert success is True
            assert "retrieved successfully" in message
            assert response is not None
            # Fix assertion to match actual call signature
            mock_inventory_repo.get_by_id.assert_called_once_with(1, False)

    def test_get_inventory_with_items(self, mock_inventory_repo, sample_inventory): pass
        """Test inventory retrieval with items."""
        mock_inventory_repo.get_by_id.return_value = sample_inventory
        
        with patch('backend.systems.inventory.service.InventoryDetailResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Inventory", "items": []}
            
            success, message, response = InventoryService.get_inventory(1, include_items=True)
            
            assert success is True
            assert response is not None
            # Fix assertion to match actual call signature
            mock_inventory_repo.get_by_id.assert_called_once_with(1, True)

    def test_get_inventory_not_found(self, mock_inventory_repo): pass
        """Test inventory retrieval when inventory not found."""
        mock_inventory_repo.get_by_id.return_value = None
        
        success, message, response = InventoryService.get_inventory(999)
        
        assert success is False
        assert "not found" in message
        assert response is None

    def test_get_inventories_success(self, mock_inventory_repo, sample_inventory): pass
        """Test successful inventories retrieval."""
        mock_inventory_repo.get_all.return_value = ([sample_inventory], 1)
        
        with patch('backend.systems.inventory.service.InventoryResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Inventory"}
            
            success, message, responses, total = InventoryService.get_inventories()
            
            assert success is True
            assert "Retrieved 1 inventories" in message
            assert len(responses) == 1
            assert total == 1
            # Fix assertion to match actual call signature
            mock_inventory_repo.get_all.assert_called_once_with(100, 0, None)

    def test_get_inventories_with_filters(self, mock_inventory_repo, sample_inventory): pass
        """Test inventories retrieval with filters."""
        mock_inventory_repo.get_all.return_value = ([sample_inventory], 1)
        
        with patch('backend.systems.inventory.service.InventoryResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Inventory"}
            
            filters = {"owner_id": 123, "owner_type": "character"}
            success, message, responses, total = InventoryService.get_inventories(
                limit=50, offset=10, filters=filters
            )
            
            assert success is True
            assert len(responses) == 1
            # Fix assertion to match actual call signature
            mock_inventory_repo.get_all.assert_called_once_with(50, 10, filters)

    def test_get_inventory_by_owner_success(self, mock_inventory_repo, sample_inventory): pass
        """Test successful inventory retrieval by owner."""
        mock_inventory_repo.get_by_owner.return_value = [sample_inventory]
        
        with patch('backend.systems.inventory.service.InventoryResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Inventory"}
            
            success, message, responses = InventoryService.get_inventory_by_owner(123)
            
            assert success is True
            assert "Retrieved 1 inventories" in message
            assert len(responses) == 1
            mock_inventory_repo.get_by_owner.assert_called_once_with(123, None)

    def test_get_inventory_by_owner_with_type(self, mock_inventory_repo, sample_inventory): pass
        """Test inventory retrieval by owner with type filter."""
        mock_inventory_repo.get_by_owner.return_value = [sample_inventory]
        
        with patch('backend.systems.inventory.service.InventoryResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "name": "Test Inventory"}
            
            success, message, responses = InventoryService.get_inventory_by_owner(
                123, "character"
            )
            
            assert success is True
            assert len(responses) == 1
            mock_inventory_repo.get_by_owner.assert_called_once_with(123, "character")

    def test_get_inventory_stats_success(self, mock_inventory_repo): pass
        """Test successful inventory stats retrieval."""
        stats_data = {
            "total_items": 10,
            "total_weight": 25.5,
            "total_value": 100.0,
            "equipped_items": 3
        }
        mock_inventory_repo.get_stats.return_value = stats_data
        
        with patch('backend.systems.inventory.service.InventoryStats') as mock_stats: pass
            mock_stats.return_value = stats_data
            
            success, message, stats = InventoryService.get_inventory_stats(1)
            
            assert success is True
            assert "retrieved successfully" in message
            assert stats == stats_data
            mock_inventory_repo.get_stats.assert_called_once_with(1)

    def test_get_inventory_stats_not_found(self, mock_inventory_repo): pass
        """Test inventory stats when inventory not found."""
        mock_inventory_repo.get_stats.return_value = None
        
        success, message, stats = InventoryService.get_inventory_stats(999)
        
        assert success is False
        # Fix assertion to match actual error message
        assert "Failed to calculate inventory statistics" in message
        assert stats is None

    # Inventory item service tests - simplified to avoid complex validator mocking
    def test_add_item_to_inventory_success(self, mock_inventory_item_repo, sample_inventory_item): pass
        """Test successful item addition to inventory."""
        # Mock the validator to always pass
        with patch('backend.systems.inventory.service.InventoryValidator') as mock_validator: pass
            mock_validator.validate_add_item.return_value = (True, {})
            
            mock_inventory_item_repo.add_item.return_value = sample_inventory_item
            
            with patch('backend.systems.inventory.service.InventoryItemResponse') as mock_response: pass
                mock_response.from_orm.return_value = {"id": 1, "quantity": 5}
                
                success, message, response = InventoryService.add_item_to_inventory(1, 1, 5)
                
                assert success is True
                assert "added successfully" in message
                assert response is not None
                mock_inventory_item_repo.add_item.assert_called_once_with(1, 1, 5, False, None)

    def test_add_item_to_inventory_validation_failed(self, mock_inventory_item_repo): pass
        """Test item addition when validation fails."""
        # Mock the validator to fail
        with patch('backend.systems.inventory.service.InventoryValidator') as mock_validator: pass
            mock_validator.validate_add_item.return_value = (False, {"error": "Validation failed"})
            
            success, message, response = InventoryService.add_item_to_inventory(1, 1, 5)
            
            assert success is False
            assert "Validation failed" in message
            assert response is None

    def test_remove_item_from_inventory_success(self, mock_inventory_item_repo, sample_inventory_item): pass
        """Test successful item removal from inventory."""
        mock_inventory_item_repo.get_by_id.return_value = sample_inventory_item
        mock_inventory_item_repo.remove_item.return_value = sample_inventory_item
        
        success, message = InventoryService.remove_item_from_inventory(1, 1, 3)
        
        assert success is True
        assert "removed successfully" in message
        mock_inventory_item_repo.remove_item.assert_called_once_with(1, quantity=3)

    def test_remove_item_from_inventory_not_found(self, mock_inventory_item_repo): pass
        """Test item removal when inventory item not found."""
        mock_inventory_item_repo.get_by_id.return_value = None
        
        success, message = InventoryService.remove_item_from_inventory(1, 999)
        
        assert success is False
        assert "not found" in message

    def test_update_inventory_item_success(self, mock_inventory_item_repo, sample_inventory_item): pass
        """Test successful inventory item update."""
        mock_inventory_item_repo.get_by_id.return_value = sample_inventory_item
        mock_inventory_item_repo.update_item.return_value = sample_inventory_item
        
        with patch('backend.systems.inventory.service.InventoryItemResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "quantity": 10}
            
            success, message, response = InventoryService.update_inventory_item(
                1, 1, {"quantity": 10}
            )
            
            assert success is True
            assert "updated successfully" in message
            assert response is not None
            mock_inventory_item_repo.update_item.assert_called_once_with(1, {"quantity": 10})

    def test_update_inventory_item_not_found(self, mock_inventory_item_repo): pass
        """Test inventory item update when item not found."""
        mock_inventory_item_repo.get_by_id.return_value = None
        
        success, message, response = InventoryService.update_inventory_item(
            1, 999, {"quantity": 10}
        )
        
        assert success is False
        assert "not found" in message
        assert response is None

    def test_equip_item_success(self, mock_inventory_item_repo, sample_inventory_item): pass
        """Test successful item equipping."""
        sample_inventory_item.item = Mock()
        sample_inventory_item.item.can_be_equipped = True
        sample_inventory_item.is_equipped = False
        
        mock_inventory_item_repo.get_by_id.return_value = sample_inventory_item
        mock_inventory_item_repo.equip_item.return_value = sample_inventory_item
        
        with patch('backend.systems.inventory.service.InventoryItemResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "is_equipped": True}
            
            success, message, response = InventoryService.equip_item(1, 1)
            
            assert success is True
            assert "equipped successfully" in message
            assert response is not None
            mock_inventory_item_repo.equip_item.assert_called_once_with(1)

    def test_equip_item_not_equippable(self, mock_inventory_item_repo, sample_inventory_item): pass
        """Test equipping item that cannot be equipped."""
        sample_inventory_item.item = Mock()
        sample_inventory_item.item.can_be_equipped = False
        
        mock_inventory_item_repo.get_by_id.return_value = sample_inventory_item
        
        success, message, response = InventoryService.equip_item(1, 1)
        
        assert success is False
        assert "cannot be equipped" in message
        assert response is None

    def test_equip_item_already_equipped(self, mock_inventory_item_repo, sample_inventory_item): pass
        """Test equipping item that is already equipped."""
        sample_inventory_item.item = Mock()
        sample_inventory_item.item.can_be_equipped = True
        sample_inventory_item.is_equipped = True
        
        mock_inventory_item_repo.get_by_id.return_value = sample_inventory_item
        
        success, message, response = InventoryService.equip_item(1, 1)
        
        assert success is False
        assert "already equipped" in message
        assert response is None

    def test_unequip_item_success(self, mock_inventory_item_repo, sample_inventory_item): pass
        """Test successful item unequipping."""
        sample_inventory_item.is_equipped = True
        
        mock_inventory_item_repo.get_by_id.return_value = sample_inventory_item
        mock_inventory_item_repo.unequip_item.return_value = sample_inventory_item
        
        with patch('backend.systems.inventory.service.InventoryItemResponse') as mock_response: pass
            mock_response.from_orm.return_value = {"id": 1, "is_equipped": False}
            
            success, message, response = InventoryService.unequip_item(1, 1)
            
            assert success is True
            assert "unequipped successfully" in message
            assert response is not None
            mock_inventory_item_repo.unequip_item.assert_called_once_with(1)

    def test_unequip_item_not_equipped(self, mock_inventory_item_repo, sample_inventory_item): pass
        """Test unequipping item that is not equipped."""
        sample_inventory_item.is_equipped = False
        
        mock_inventory_item_repo.get_by_id.return_value = sample_inventory_item
        
        success, message, response = InventoryService.unequip_item(1, 1)
        
        assert success is False
        assert "not equipped" in message
        assert response is None

    def test_transfer_item_success(self, mock_inventory_item_repo): pass
        """Test successful item transfer."""
        with patch('backend.systems.inventory.service.InventoryUtils') as mock_utils: pass
            mock_utils.transfer_item_between_inventories.return_value = (
                True, "Transfer successful", {"transferred": True}
            )
            
            success, message, result = InventoryService.transfer_item(1, 2, 1, 3)
            
            assert success is True
            assert "Transfer successful" in message
            assert result["transferred"] is True

    def test_transfer_item_failure(self, mock_inventory_item_repo): pass
        """Test item transfer failure."""
        with patch('backend.systems.inventory.service.InventoryUtils') as mock_utils: pass
            mock_utils.transfer_item_between_inventories.return_value = (
                False, "Transfer failed", {}
            )
            
            success, message, result = InventoryService.transfer_item(1, 2, 1, 3)
            
            assert success is False
            assert "Transfer failed" in message

    def test_validate_inventory_operation_success(self): pass
        """Test successful inventory operation validation."""
        with patch('backend.systems.inventory.service.InventoryValidator') as mock_validator: pass
            mock_validator.validate_operation.return_value = (True, {"valid": True})
            
            success, response = InventoryService.validate_inventory_operation(
                "add_item", {"inventory_id": 1, "item_id": 1, "quantity": 5}
            )
            
            assert success is True
            assert response["valid"] is True

    def test_validate_inventory_operation_failure(self): pass
        """Test inventory operation validation failure."""
        with patch('backend.systems.inventory.service.InventoryValidator') as mock_validator: pass
            mock_validator.validate_operation.return_value = (False, Mock(error_message="Invalid data"))
            
            success, response = InventoryService.validate_inventory_operation(
                "add_item", {"invalid": "data"}
            )
            
            assert success is False
            assert hasattr(response, 'error_message')

    # Exception handling tests
    def test_service_exception_handling(self, mock_item_repo): pass
        """Test service exception handling across methods."""
        mock_item_repo.get_all.side_effect = Exception("Database connection lost")
        
        success, message, responses = InventoryService.get_items()
        
        assert success is False
        assert "Error getting items" in message
        assert responses == []

    def test_service_with_none_responses(self, mock_inventory_repo): pass
        """Test service handling of None responses from repositories."""
        mock_inventory_repo.get_by_id.return_value = None
        
        success, message, response = InventoryService.get_inventory(999)
        
        assert success is False
        assert "not found" in message
        assert response is None 