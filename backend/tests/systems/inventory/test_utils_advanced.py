from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from typing import Any
from typing import List
"""
Advanced utils tests for inventory system.

This module provides targeted test coverage for high-impact utility functions
to achieve 90% coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

from backend.systems.inventory.utils import (
    InventoryUtils,
    RecoveryManager,
    calculate_inventory_stats,
    transfer_item_between_inventories,
    get_inventory_weight,
    validate_weight_limit,
    validate_inventory_capacity,
    optimize_inventory_stacks,
    combine_item_stacks,
    split_item_stack,
    filter_inventory_items
)


class TestInventoryUtilsAdvanced: pass
    """Test class for advanced inventory utility functions."""

    @pytest.fixture
    def sample_items_dict(self): pass
        """Sample items in dictionary format for testing."""
        items = []
        for i in range(3): pass
            item_data = {
                "id": i + 1,
                "item_id": i + 1,
                "quantity": (i + 1) * 2,
                "is_equipped": i == 0,
                "position": {"x": i, "y": 0},
                "item": {
                    "id": i + 1,
                    "name": f"Item {i + 1}",
                    "weight": (i + 1) * 1.0,
                    "value": (i + 1) * 10.0,
                    "category": "weapon" if i % 2 == 0 else "armor",
                    "stackable": i % 2 == 0,
                    "apply_weight_when_equipped": True
                }
            }
            items.append(item_data)
        return items

    @pytest.fixture
    def sample_inventory(self): pass
        """Sample inventory for testing."""
        inventory = Mock()
        inventory.id = 1
        inventory.name = "Test Inventory"
        inventory.capacity = 100.0
        inventory.weight_limit = 50.0
        inventory.owner_id = 123
        inventory.owner_type = "character"
        return inventory

    # InventoryUtils static methods tests
    def test_format_datetime_success(self): pass
        """Test successful datetime formatting."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        formatted = InventoryUtils.format_datetime(dt)
        assert "2023-01-01T12:00:00" in formatted

    def test_format_datetime_none(self): pass
        """Test datetime formatting with None."""
        formatted = InventoryUtils.format_datetime(None)
        assert formatted is None

    def test_calculate_total_weight_with_equipped(self, sample_items_dict): pass
        """Test total weight calculation including equipped items."""
        total_weight = InventoryUtils.calculate_total_weight(sample_items_dict, count_equipped=True)
        # (1*2) + (2*4) + (3*6) = 2 + 8 + 18 = 28
        assert total_weight == 28.0

    def test_calculate_total_weight_without_equipped(self, sample_items_dict): pass
        """Test total weight calculation excluding equipped items."""
        total_weight = InventoryUtils.calculate_total_weight(sample_items_dict, count_equipped=False)
        # (2*4) + (3*6) = 8 + 18 = 26 (excluding first item which is equipped)
        assert total_weight == 26.0

    def test_calculate_total_weight_empty(self): pass
        """Test total weight calculation with empty list."""
        total_weight = InventoryUtils.calculate_total_weight([])
        assert total_weight == 0.0

    def test_calculate_total_weight_with_non_weight_equipped(self, sample_items_dict): pass
        """Test weight calculation with equipped items that don't apply weight."""
        # Modify first item to not apply weight when equipped
        sample_items_dict[0]["item"]["apply_weight_when_equipped"] = False
        
        total_weight = InventoryUtils.calculate_total_weight(sample_items_dict, count_equipped=True)
        # (2*4) + (3*6) = 8 + 18 = 26 (first item weight not counted when equipped)
        assert total_weight == 26.0

    def test_calculate_total_value(self, sample_items_dict): pass
        """Test total value calculation."""
        total_value = InventoryUtils.calculate_total_value(sample_items_dict)
        # (10*2) + (20*4) + (30*6) = 20 + 80 + 180 = 280
        assert total_value == 280.0

    def test_calculate_total_value_empty(self): pass
        """Test total value calculation with empty list."""
        total_value = InventoryUtils.calculate_total_value([])
        assert total_value == 0.0

    def test_get_inventory_statistics_full(self, sample_items_dict): pass
        """Test comprehensive inventory statistics calculation."""
        stats = InventoryUtils.get_inventory_statistics(
            sample_items_dict, capacity=10, weight_limit=50.0, count_equipped_weight=True
        )
        
        assert stats["total_items"] == 12  # 2 + 4 + 6
        assert stats["unique_items"] == 3
        assert stats["total_weight"] == 28.0
        assert stats["total_value"] == 280.0
        assert stats["equipped_items"] == 1
        assert stats["used_capacity_pct"] == 30.0  # 3/10 * 100
        assert stats["used_weight_pct"] == 56.0  # 28/50 * 100
        assert "weapon" in stats["categories"]
        assert "armor" in stats["categories"]

    def test_get_inventory_statistics_empty(self): pass
        """Test statistics calculation with empty inventory."""
        stats = InventoryUtils.get_inventory_statistics([])
        
        assert stats["total_items"] == 0
        assert stats["unique_items"] == 0
        assert stats["total_weight"] == 0.0
        assert stats["total_value"] == 0.0
        assert stats["equipped_items"] == 0
        assert stats["used_capacity_pct"] == 0.0
        assert stats["used_weight_pct"] == 0.0
        assert stats["categories"] == {}

    def test_get_inventory_statistics_no_limits(self, sample_items_dict): pass
        """Test statistics calculation without capacity/weight limits."""
        stats = InventoryUtils.get_inventory_statistics(sample_items_dict)
        
        assert stats["used_capacity_pct"] == 0.0
        assert stats["used_weight_pct"] == 0.0

    def test_serialize_sqlalchemy_obj_with_to_dict(self): pass
        """Test serialization of SQLAlchemy object with to_dict method."""
        obj = Mock()
        obj.to_dict.return_value = {"id": 1, "name": "Test"}
        
        result = InventoryUtils.serialize_sqlalchemy_obj(obj)
        
        assert result == {"id": 1, "name": "Test"}
        obj.to_dict.assert_called_once()

    def test_serialize_sqlalchemy_obj_without_to_dict(self): pass
        """Test serialization of SQLAlchemy object without to_dict method."""
        # Create a mock SQLAlchemy object
        obj = Mock()
        obj.__class__ = Mock()
        obj.__class__.__bases__ = (Mock(),)  # Mock DeclarativeMeta
        obj.__table__ = Mock()
        
        # Mock columns
        column1 = Mock()
        column1.name = "id"
        column2 = Mock()
        column2.name = "name"
        obj.__table__.columns = [column1, column2]
        
        # Mock attribute values
        obj.id = 1
        obj.name = "Test Item"
        
        # Mock DeclarativeMeta check
        with patch('backend.systems.inventory.utils.DeclarativeMeta') as mock_meta: pass
            mock_meta.__instancecheck__ = lambda self, instance: True
            
            result = InventoryUtils.serialize_sqlalchemy_obj(obj)
            
            assert "id" in result
            assert "name" in result

    def test_apply_pagination_first_page(self): pass
        """Test pagination on first page."""
        mock_query = Mock()
        mock_items = [Mock() for _ in range(5)]
        mock_query.offset.return_value.limit.return_value.all.return_value = mock_items
        mock_query.count.return_value = 25
        
        items, total = InventoryUtils.apply_pagination(mock_query, page=1, size=5)
        
        assert len(items) == 5
        assert total == 25
        mock_query.offset.assert_called_with(0)
        mock_query.offset.return_value.limit.assert_called_with(5)

    def test_apply_pagination_second_page(self): pass
        """Test pagination on second page."""
        mock_query = Mock()
        mock_items = [Mock() for _ in range(5)]
        mock_query.offset.return_value.limit.return_value.all.return_value = mock_items
        mock_query.count.return_value = 25
        
        items, total = InventoryUtils.apply_pagination(mock_query, page=2, size=5)
        
        assert len(items) == 5
        assert total == 25
        mock_query.offset.assert_called_with(5)

    @patch('backend.systems.inventory.utils.db.session')
    def test_generate_grid_position_success(self, mock_session): pass
        """Test successful grid position generation."""
        # Mock existing positions
        mock_session.query.return_value.filter.return_value.all.return_value = [
            Mock(position={"x": 0, "y": 0}),
            Mock(position={"x": 1, "y": 0})
        ]
        
        position = InventoryUtils.generate_grid_position(1, mock_session)
        
        assert position is not None
        assert "x" in position
        assert "y" in position

    @patch('backend.systems.inventory.utils.db.session')
    def test_generate_grid_position_no_existing(self, mock_session): pass
        """Test grid position generation with no existing items."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        position = InventoryUtils.generate_grid_position(1, mock_session)
        
        assert position == {"x": 0, "y": 0}

    # Standalone utility function tests
    @patch('backend.systems.inventory.utils.InventoryRepository')
    def test_calculate_inventory_stats_success(self, mock_repo): pass
        """Test successful inventory stats calculation."""
        mock_inventory = Mock()
        mock_inventory.items = [
            Mock(quantity=2, item=Mock(weight=1.0, value=10.0), is_equipped=False),
            Mock(quantity=3, item=Mock(weight=2.0, value=20.0), is_equipped=True)
        ]
        mock_repo.get_by_id.return_value = mock_inventory
        
        stats = calculate_inventory_stats(mock_inventory)
        
        assert "total_items" in stats
        assert "total_weight" in stats
        assert "total_value" in stats

    @patch('backend.systems.inventory.utils.InventoryRepository')
    @patch('backend.systems.inventory.utils.InventoryItemRepository')
    def test_transfer_item_between_inventories_success(self, mock_item_repo, mock_inv_repo): pass
        """Test successful item transfer between inventories."""
        # Mock inventories
        source_inv = Mock()
        source_inv.id = 1
        source_inv.weight_limit = 100.0
        
        target_inv = Mock()
        target_inv.id = 2
        target_inv.weight_limit = 100.0
        
        mock_inv_repo.get_by_id.side_effect = [source_inv, target_inv]
        
        # Mock inventory item
        inv_item = Mock()
        inv_item.quantity = 10
        inv_item.item = Mock(weight=1.0)
        
        mock_item_repo.get_by_id.return_value = inv_item
        
        # Mock weight calculations
        with patch('backend.systems.inventory.utils.get_inventory_weight') as mock_weight: pass
            mock_weight.side_effect = [20.0, 30.0]  # source, target weights
            
            success, message, result = transfer_item_between_inventories(1, 2, 1, 5)
            
            assert success is True
            assert "transferred successfully" in message

    @patch('backend.systems.inventory.utils.InventoryRepository')
    def test_transfer_item_source_not_found(self, mock_repo): pass
        """Test item transfer when source inventory not found."""
        mock_repo.get_by_id.return_value = None
        
        success, message, result = transfer_item_between_inventories(999, 2, 1, 5)
        
        assert success is False
        assert "Source inventory not found" in message

    @patch('backend.systems.inventory.utils.db.session')
    def test_get_inventory_weight_success(self, mock_session): pass
        """Test successful inventory weight calculation."""
        # Mock inventory items
        mock_items = [
            Mock(quantity=2, item=Mock(weight=1.0), is_equipped=False),
            Mock(quantity=3, item=Mock(weight=2.0), is_equipped=True)
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_items
        
        weight = get_inventory_weight(1, mock_session)
        
        assert weight == 8.0  # (2*1) + (3*2) = 8

    @patch('backend.systems.inventory.utils.get_inventory_weight')
    def test_validate_weight_limit_success(self, mock_weight): pass
        """Test weight limit validation success."""
        mock_weight.return_value = 25.0
        
        is_valid, details = validate_weight_limit(1, additional_weight=10.0)
        
        assert is_valid is True
        assert details is None

    @patch('backend.systems.inventory.utils.get_inventory_weight')
    @patch('backend.systems.inventory.utils.InventoryRepository')
    def test_validate_weight_limit_exceeded(self, mock_repo, mock_weight): pass
        """Test weight limit validation when exceeded."""
        mock_inventory = Mock()
        mock_inventory.weight_limit = 50.0
        mock_repo.get_by_id.return_value = mock_inventory
        mock_weight.return_value = 45.0
        
        is_valid, details = validate_weight_limit(1, additional_weight=10.0)
        
        assert is_valid is False
        assert details is not None
        assert "weight_limit_exceeded" in details

    @patch('backend.systems.inventory.utils.db.session')
    def test_validate_inventory_capacity_success(self, mock_session): pass
        """Test inventory capacity validation success."""
        # Mock inventory
        mock_inventory = Mock()
        mock_inventory.capacity = 100
        mock_session.query.return_value.filter.return_value.first.return_value = mock_inventory
        
        # Mock current item count
        mock_session.query.return_value.filter.return_value.count.return_value = 50
        
        is_valid, details = validate_inventory_capacity(1, additional_items=10)
        
        assert is_valid is True
        assert details is None

    @patch('backend.systems.inventory.utils.db.session')
    def test_validate_inventory_capacity_exceeded(self, mock_session): pass
        """Test inventory capacity validation when exceeded."""
        # Mock inventory
        mock_inventory = Mock()
        mock_inventory.capacity = 100
        mock_session.query.return_value.filter.return_value.first.return_value = mock_inventory
        
        # Mock current item count
        mock_session.query.return_value.filter.return_value.count.return_value = 95
        
        is_valid, details = validate_inventory_capacity(1, additional_items=10)
        
        assert is_valid is False
        assert details is not None
        assert "capacity_exceeded" in details

    @patch('backend.systems.inventory.utils.db.session')
    def test_optimize_inventory_stacks_success(self, mock_session): pass
        """Test successful inventory stack optimization."""
        # Mock stackable items
        mock_items = [
            Mock(item_id=1, quantity=50, item=Mock(stackable=True, max_stack=100)),
            Mock(item_id=1, quantity=30, item=Mock(stackable=True, max_stack=100))
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_items
        
        success, message, result = optimize_inventory_stacks(1, mock_session)
        
        assert success is True
        assert "optimized" in message.lower()
        assert "stacks_optimized" in result

    @patch('backend.systems.inventory.utils.db.session')
    def test_combine_item_stacks_success(self, mock_session): pass
        """Test successful item stack combining."""
        # Mock source and target stacks
        source_stack = Mock()
        source_stack.quantity = 30
        source_stack.item = Mock(stackable=True, max_stack=100)
        
        target_stack = Mock()
        target_stack.quantity = 40
        target_stack.item_id = source_stack.item.id
        target_stack.item = source_stack.item
        
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            source_stack, target_stack
        ]
        
        success, message, result = combine_item_stacks(1, 1, 2, quantity=20)
        
        assert success is True
        assert "combined" in message.lower()

    @patch('backend.systems.inventory.utils.db.session')
    def test_split_item_stack_success(self, mock_session): pass
        """Test successful item stack splitting."""
        # Mock stack to split
        stack = Mock()
        stack.quantity = 50
        stack.item = Mock(stackable=True)
        stack.inventory_id = 1
        
        mock_session.query.return_value.filter.return_value.first.return_value = stack
        
        # Mock position generation
        with patch('backend.systems.inventory.utils.InventoryUtils.generate_grid_position') as mock_pos: pass
            mock_pos.return_value = {"x": 1, "y": 0}
            
            success, message, result = split_item_stack(1, 1, 20)
            
            assert success is True
            assert "split" in message.lower()

    @patch('backend.systems.inventory.utils.db.session')
    def test_filter_inventory_items_by_category(self, mock_session): pass
        """Test filtering inventory items by category."""
        # Mock inventory items
        mock_items = [
            Mock(item=Mock(category="weapon"), to_dict=lambda: {"category": "weapon"}),
            Mock(item=Mock(category="armor"), to_dict=lambda: {"category": "armor"}),
            Mock(item=Mock(category="weapon"), to_dict=lambda: {"category": "weapon"})
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_items
        
        success, message, items = filter_inventory_items(1, {"category": "weapon"})
        
        assert success is True
        assert len(items) == 2  # Should return 2 weapon items

    @patch('backend.systems.inventory.utils.db.session')
    def test_filter_inventory_items_by_equipped(self, mock_session): pass
        """Test filtering inventory items by equipped status."""
        # Mock inventory items
        mock_items = [
            Mock(is_equipped=True, to_dict=lambda: {"is_equipped": True}),
            Mock(is_equipped=False, to_dict=lambda: {"is_equipped": False}),
            Mock(is_equipped=True, to_dict=lambda: {"is_equipped": True})
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_items
        
        success, message, items = filter_inventory_items(1, {"is_equipped": True})
        
        assert success is True
        assert len(items) == 2  # Should return 2 equipped items

    # RecoveryManager tests
    @patch('backend.systems.inventory.utils.InventoryRepository')
    def test_recovery_manager_backup_inventory(self, mock_repo): pass
        """Test inventory backup creation."""
        mock_inventory = Mock()
        mock_inventory.to_dict.return_value = {"id": 1, "name": "Test"}
        mock_inventory.items = []
        mock_repo.get_by_id.return_value = mock_inventory
        
        backup_data = RecoveryManager.backup_inventory(1)
        
        assert "inventory" in backup_data
        assert "items" in backup_data
        assert "metadata" in backup_data

    @patch('backend.systems.inventory.utils.InventoryRepository')
    @patch('backend.systems.inventory.utils.InventoryItemRepository')
    def test_recovery_manager_restore_inventory(self, mock_item_repo, mock_inv_repo): pass
        """Test inventory restoration from backup."""
        backup_data = {
            "inventory": {"id": 1, "name": "Test"},
            "items": [{"id": 1, "quantity": 5}],
            "metadata": {"backup_date": "2023-01-01"}
        }
        
        mock_inventory = Mock()
        mock_inv_repo.create.return_value = mock_inventory
        
        result = RecoveryManager.restore_inventory(backup_data)
        
        assert "success" in result
        assert "inventory" in result

    # Exception handling tests
    def test_utils_exception_handling(self): pass
        """Test utility functions exception handling."""
        # Test with invalid data types
        result = InventoryUtils.calculate_total_weight(None)
        assert result == 0.0
        
        result = InventoryUtils.calculate_total_value(None)
        assert result == 0.0

    def test_statistics_with_malformed_data(self): pass
        """Test statistics calculation with malformed data."""
        malformed_items = [
            {"invalid": "data"},
            {"item": None, "quantity": "invalid"},
            {}
        ]
        
        # Should handle gracefully without crashing
        stats = InventoryUtils.get_inventory_statistics(malformed_items)
        assert isinstance(stats, dict)
        assert stats["total_items"] >= 0

    def test_serialization_with_datetime(self): pass
        """Test serialization handling of datetime objects."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        
        # Mock object with datetime attribute
        obj = Mock()
        obj.__class__ = Mock()
        obj.__table__ = Mock()
        
        column = Mock()
        column.name = "created_at"
        obj.__table__.columns = [column]
        obj.created_at = dt
        
        with patch('backend.systems.inventory.utils.DeclarativeMeta') as mock_meta: pass
            mock_meta.__instancecheck__ = lambda self, instance: True
            
            result = InventoryUtils.serialize_sqlalchemy_obj(obj)
            
            assert "created_at" in result
            assert isinstance(result["created_at"], str) 