from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from backend.systems.inventory.models import Inventory
from typing import Any
from typing import List
"""
Comprehensive utils tests for inventory system.

This module provides complete test coverage for the most important utility functions
in the inventory utils module, focusing on high-impact functions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List, Any

from backend.systems.inventory.utils import (
    InventoryUtils,
    calculate_inventory_stats,
    transfer_item_between_inventories,
    get_inventory_weight,
    validate_weight_limit,
    validate_inventory_capacity,
    optimize_inventory_stacks,
    combine_item_stacks,
    split_item_stack,
    filter_inventory_items,
    RecoveryManager,
)


class TestInventoryUtils:
    """Test class for InventoryUtils static methods."""

    def test_format_datetime_with_datetime(self):
        """Test formatting a datetime object."""
        dt = datetime(2023, 12, 25, 10, 30, 45)
        result = InventoryUtils.format_datetime(dt)
        assert result == "2023-12-25T10:30:45"

    def test_format_datetime_with_none(self):
        """Test formatting None datetime."""
        result = InventoryUtils.format_datetime(None)
        assert result is None

    def test_calculate_total_weight_empty_list(self):
        """Test weight calculation with empty items list."""
        result = InventoryUtils.calculate_total_weight([])
        assert result == 0.0

    def test_calculate_total_weight_basic_items(self):
        """Test weight calculation with basic items."""
        items = [
            {
                "item": {"weight": 5.0, "apply_weight_when_equipped": True},
                "quantity": 2,
                "is_equipped": False
            },
            {
                "item": {"weight": 3.5, "apply_weight_when_equipped": True},
                "quantity": 1,
                "is_equipped": False
            }
        ]
        result = InventoryUtils.calculate_total_weight(items)
        assert result == 13.5  # (5.0 * 2) + (3.5 * 1)

    def test_calculate_total_weight_with_equipped_counted(self):
        """Test weight calculation including equipped items."""
        items = [
            {
                "item": {"weight": 5.0, "apply_weight_when_equipped": True},
                "quantity": 1,
                "is_equipped": True
            },
            {
                "item": {"weight": 3.0, "apply_weight_when_equipped": True},
                "quantity": 1,
                "is_equipped": False
            }
        ]
        result = InventoryUtils.calculate_total_weight(items, count_equipped=True)
        assert result == 8.0

    def test_calculate_total_weight_with_equipped_not_counted(self):
        """Test weight calculation excluding equipped items."""
        items = [
            {
                "item": {"weight": 5.0, "apply_weight_when_equipped": True},
                "quantity": 1,
                "is_equipped": True
            },
            {
                "item": {"weight": 3.0, "apply_weight_when_equipped": True},
                "quantity": 1,
                "is_equipped": False
            }
        ]
        result = InventoryUtils.calculate_total_weight(items, count_equipped=False)
        assert result == 3.0

    def test_calculate_total_weight_equipped_no_weight_when_equipped(self):
        """Test weight calculation with equipped items that don't apply weight."""
        items = [
            {
                "item": {"weight": 5.0, "apply_weight_when_equipped": False},
                "quantity": 1,
                "is_equipped": True
            },
            {
                "item": {"weight": 3.0, "apply_weight_when_equipped": True},
                "quantity": 1,
                "is_equipped": False
            }
        ]
        result = InventoryUtils.calculate_total_weight(items, count_equipped=True)
        assert result == 3.0

    def test_calculate_total_value_empty_list(self):
        """Test value calculation with empty items list."""
        result = InventoryUtils.calculate_total_value([])
        assert result == 0.0

    def test_calculate_total_value_basic_items(self):
        """Test value calculation with basic items."""
        items = [
            {
                "item": {"value": 10.0},
                "quantity": 2
            },
            {
                "item": {"value": 5.5},
                "quantity": 3
            }
        ]
        result = InventoryUtils.calculate_total_value(items)
        assert result == 36.5  # (10.0 * 2) + (5.5 * 3)

    def test_get_inventory_statistics_empty_items(self):
        """Test statistics calculation with empty items."""
        result = InventoryUtils.get_inventory_statistics([])
        expected = {
            "total_items": 0,
            "unique_items": 0,
            "total_weight": 0.0,
            "total_value": 0.0,
            "used_capacity_pct": 0.0,
            "used_weight_pct": 0.0,
            "equipped_items": 0,
            "categories": {},
        }
        assert result == expected

    def test_get_inventory_statistics_with_items(self):
        """Test statistics calculation with items."""
        items = [
            {
                "item": {"weight": 5.0, "value": 10.0, "category": "weapon"},
                "quantity": 2,
                "is_equipped": False
            },
            {
                "item": {"weight": 1.0, "value": 5.0, "category": "consumable"},
                "quantity": 5,
                "is_equipped": False
            },
            {
                "item": {"weight": 3.0, "value": 15.0, "category": "armor"},
                "quantity": 1,
                "is_equipped": True
            }
        ]
        result = InventoryUtils.get_inventory_statistics(
            items, capacity=10, weight_limit=50.0
        )
        
        assert result["total_items"] == 8  # 2 + 5 + 1
        assert result["unique_items"] == 3
        assert result["total_weight"] == 18.0  # (5*2) + (1*5) + (3*1)
        assert result["total_value"] == 50.0  # (10*2) + (5*5) + (15*1)
        assert result["used_capacity_pct"] == 30.0  # 3/10 * 100
        assert result["used_weight_pct"] == 36.0  # 18/50 * 100
        assert result["equipped_items"] == 1
        assert result["categories"] == {"weapon": 2, "consumable": 5, "armor": 1}

    def test_serialize_sqlalchemy_obj_with_to_dict(self):
        """Test serializing object with to_dict method."""
        mock_obj = Mock()
        mock_obj.to_dict.return_value = {"id": 1, "name": "test"}
        
        result = InventoryUtils.serialize_sqlalchemy_obj(mock_obj)
        assert result == {"id": 1, "name": "test"}
        mock_obj.to_dict.assert_called_once()

    @patch('backend.systems.inventory.utils.db.session')
    def test_apply_pagination(self, mock_session):
        """Test pagination utility."""
        mock_query = Mock()
        mock_query.offset.return_value.limit.return_value.all.return_value = ["item1", "item2"]
        mock_query.count.return_value = 25
        
        result, total = InventoryUtils.apply_pagination(mock_query, page=2, size=10)
        
        assert result == ["item1", "item2"]
        assert total == 25
        mock_query.offset.assert_called_once_with(10)  # (page-1) * size
        mock_query.offset.return_value.limit.assert_called_once_with(10)


class TestInventoryStatsFunction:
    """Test the standalone calculate_inventory_stats function."""

    @patch('backend.systems.inventory.utils.InventoryItemRepository.get_all_by_inventory')
    def test_calculate_inventory_stats_success(self, mock_get_items):
        """Test successful inventory stats calculation."""
        mock_inventory = Mock()
        mock_inventory.id = 1
        mock_inventory.capacity = 20
        mock_inventory.weight_limit = 100.0
        
        mock_items = [
            Mock(to_dict=lambda: {
                "item": {"weight": 5.0, "value": 10.0, "category": "weapon"},
                "quantity": 2,
                "is_equipped": False
            })
        ]
        mock_get_items.return_value = mock_items
        
        result = calculate_inventory_stats(mock_inventory)
        
        assert "total_items" in result
        assert "total_weight" in result
        assert "total_value" in result
        mock_get_items.assert_called_once_with(1)


class TestTransferFunction:
    """Test the transfer_item_between_inventories function."""

    @patch('backend.systems.inventory.utils.db.session')
    @patch('backend.systems.inventory.utils.InventoryItemRepository')
    def test_transfer_item_success(self, mock_repo, mock_session):
        """Test successful item transfer."""
        # Mock the inventory item
        mock_item = Mock()
        mock_item.quantity = 5
        mock_item.item.weight = 2.0
        mock_item.inventory_id = 1
        mock_item.item_id = "item_1"
        
        mock_repo.get_by_id.return_value = mock_item
        mock_repo.get_by_inventory_and_item.return_value = None  # No existing stack
        
        # Mock validation functions
        with patch('backend.systems.inventory.utils.validate_weight_limit') as mock_weight, \
             patch('backend.systems.inventory.utils.validate_inventory_capacity') as mock_capacity:
            mock_weight.return_value = (True, None)
            mock_capacity.return_value = (True, None)
            
            success, error, result = transfer_item_between_inventories(
                from_inventory_id=1,
                to_inventory_id=2,
                inventory_item_id="inv_item_1",
                quantity=3
            )
            
            assert success is True
            assert error is None
            assert result is not None


class TestWeightValidation:
    """Test weight validation functions."""

    @patch('backend.systems.inventory.utils.get_inventory_weight')
    @patch('backend.systems.inventory.utils.db.session')
    def test_validate_weight_limit_success(self, mock_session, mock_get_weight):
        """Test weight limit validation success."""
        mock_inventory = Mock()
        mock_inventory.weight_limit = 100.0
        mock_session.query.return_value.filter.return_value.first.return_value = mock_inventory
        mock_get_weight.return_value = 50.0
        
        success, result = validate_weight_limit(1, additional_weight=30.0)
        
        assert success is True
        assert result is None

    @patch('backend.systems.inventory.utils.get_inventory_weight')
    @patch('backend.systems.inventory.utils.db.session')
    def test_validate_weight_limit_exceeded(self, mock_session, mock_get_weight):
        """Test weight limit validation failure."""
        mock_inventory = Mock()
        mock_inventory.weight_limit = 100.0
        mock_session.query.return_value.filter.return_value.first.return_value = mock_inventory
        mock_get_weight.return_value = 80.0
        
        success, result = validate_weight_limit(1, additional_weight=30.0)
        
        assert success is False
        assert result is not None
        assert "weight_limit_exceeded" in result


class TestCapacityValidation:
    """Test capacity validation functions."""

    @patch('backend.systems.inventory.utils.db.session')
    def test_validate_inventory_capacity_success(self, mock_session):
        """Test capacity validation success."""
        mock_inventory = Mock()
        mock_inventory.capacity = 20
        mock_session.query.return_value.filter.return_value.first.return_value = mock_inventory
        mock_session.query.return_value.filter.return_value.count.return_value = 15
        
        success, result = validate_inventory_capacity(1, additional_items=3)
        
        assert success is True
        assert result is None

    @patch('backend.systems.inventory.utils.db.session')
    def test_validate_inventory_capacity_exceeded(self, mock_session):
        """Test capacity validation failure."""
        mock_inventory = Mock()
        mock_inventory.capacity = 20
        mock_session.query.return_value.filter.return_value.first.return_value = mock_inventory
        mock_session.query.return_value.filter.return_value.count.return_value = 18
        
        success, result = validate_inventory_capacity(1, additional_items=5)
        
        assert success is False
        assert result is not None
        assert "capacity_exceeded" in result


class TestStackOperations:
    """Test stack optimization and manipulation functions."""

    @patch('backend.systems.inventory.utils.db.session')
    @patch('backend.systems.inventory.utils.InventoryItemRepository')
    def test_optimize_inventory_stacks_success(self, mock_repo, mock_session):
        """Test inventory stack optimization."""
        mock_items = [
            Mock(item_id="item_1", quantity=5, item=Mock(max_stack_size=10, is_stackable=True)),
            Mock(item_id="item_1", quantity=3, item=Mock(max_stack_size=10, is_stackable=True)),
        ]
        mock_repo.get_all_by_inventory.return_value = mock_items
        
        success, message, result = optimize_inventory_stacks(1)
        
        assert success is True
        assert "optimized" in message.lower()
        assert result is not None

    @patch('backend.systems.inventory.utils.db.session')
    @patch('backend.systems.inventory.utils.InventoryItemRepository')
    def test_combine_item_stacks_success(self, mock_repo, mock_session):
        """Test combining item stacks."""
        mock_source = Mock(quantity=5, item=Mock(max_stack_size=10, is_stackable=True))
        mock_target = Mock(quantity=3, item=Mock(max_stack_size=10, is_stackable=True))
        
        mock_repo.get_by_id.side_effect = [mock_source, mock_target]
        
        success, message, result = combine_item_stacks(1, "source_id", "target_id", quantity=3)
        
        assert success is True
        assert result is not None

    @patch('backend.systems.inventory.utils.db.session')
    @patch('backend.systems.inventory.utils.InventoryItemRepository')
    def test_split_item_stack_success(self, mock_repo, mock_session):
        """Test splitting item stacks."""
        mock_stack = Mock(
            quantity=10, 
            item=Mock(is_stackable=True),
            inventory_id=1,
            item_id="item_1",
            position={"x": 0, "y": 0}
        )
        mock_repo.get_by_id.return_value = mock_stack
        
        success, message, result = split_item_stack(1, "stack_id", quantity=4)
        
        assert success is True
        assert result is not None


class TestRecoveryManager:
    """Test the RecoveryManager class."""

    @patch('backend.systems.inventory.utils.db.session')
    @patch('backend.systems.inventory.utils.InventoryItemRepository')
    def test_backup_inventory(self, mock_repo, mock_session):
        """Test inventory backup."""
        mock_inventory = Mock(id=1, name="Test Inventory")
        mock_session.query.return_value.filter.return_value.first.return_value = mock_inventory
        
        mock_items = [Mock(to_dict=lambda: {"id": "item_1", "quantity": 5})]
        mock_repo.get_all_by_inventory.return_value = mock_items
        
        result = RecoveryManager.backup_inventory(1)
        
        assert "inventory" in result
        assert "items" in result
        assert "timestamp" in result

    @patch('backend.systems.inventory.utils.db.session')
    def test_restore_inventory(self, mock_session):
        """Test inventory restoration."""
        backup_data = {
            "inventory": {"id": 1, "name": "Test Inventory"},
            "items": [{"id": "item_1", "quantity": 5}],
            "timestamp": "2023-12-25T10:30:45"
        }
        
        result = RecoveryManager.restore_inventory(backup_data)
        
        assert "success" in result
        assert "restored_items" in result


class TestFilterFunction:
    """Test the filter_inventory_items function."""

    @patch('backend.systems.inventory.utils.db.session')
    @patch('backend.systems.inventory.utils.InventoryItemRepository')
    def test_filter_inventory_items_by_category(self, mock_repo, mock_session):
        """Test filtering inventory items by category."""
        mock_items = [
            Mock(to_dict=lambda: {
                "item": {"category": "weapon", "name": "Sword"},
                "quantity": 1
            }),
            Mock(to_dict=lambda: {
                "item": {"category": "armor", "name": "Shield"},
                "quantity": 1
            })
        ]
        mock_repo.get_all_by_inventory.return_value = mock_items
        
        success, message, result = filter_inventory_items(
            1, 
            filters={"category": "weapon"}
        )
        
        assert success is True
        assert len(result) <= len(mock_items)

    @patch('backend.systems.inventory.utils.db.session')
    @patch('backend.systems.inventory.utils.InventoryItemRepository')
    def test_filter_inventory_items_by_equipped(self, mock_repo, mock_session):
        """Test filtering inventory items by equipped status."""
        mock_items = [
            Mock(to_dict=lambda: {
                "item": {"name": "Sword"},
                "is_equipped": True,
                "quantity": 1
            }),
            Mock(to_dict=lambda: {
                "item": {"name": "Potion"},
                "is_equipped": False,
                "quantity": 5
            })
        ]
        mock_repo.get_all_by_inventory.return_value = mock_items
        
        success, message, result = filter_inventory_items(
            1, 
            filters={"equipped": True}
        )
        
        assert success is True
        assert len(result) <= len(mock_items) 