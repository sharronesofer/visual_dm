from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from typing import Type
"""
Tests for the shop utils module.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from backend.systems.economy.utils.shop_utils import (
    get_shop_inventory,
    restock_shop,
    calculate_sale_value,
    calculate_purchase_value,
    get_shop_type_from_poi,
    initialize_shop_metadata,
    purchase_item_from_shop,
    sell_item_to_shop,
    _generate_shop_inventory,
    _apply_current_pricing,
    _generate_fallback_inventory,
    SHOP_TYPES
)
from backend.systems.poi.models import PointOfInterest, POIType


@pytest.fixture
def sample_poi():
    """Create a sample POI for testing."""
    poi = MagicMock(spec=PointOfInterest)
    poi.id = "shop-1"
    poi.name = "Test Shop"
    poi.region_id = "1"
    poi.faction_id = "1"
    poi.population = 100
    poi.poi_type = POIType.SHOP
    poi.metadata = {
        "shop": {
            "type": "general",
            "tier": 1,
            "last_restock": datetime.utcnow().isoformat()
        }
    }
    poi.update_timestamp = MagicMock()
    return poi


@pytest.fixture
def sample_inventory():
    """Create sample inventory data for testing."""
    return [
        {
            "id": "item-1",
            "name": "Health Potion",
            "category": "consumable",
            "base_price": 50.0,
            "shop_price": 60.0,
            "quantity": 5,
            "metadata": {}
        },
        {
            "id": "item-2",
            "name": "Iron Sword",
            "category": "weapon",
            "base_price": 100.0,
            "shop_price": 130.0,
            "quantity": 2,
            "metadata": {}
        }
    ]


@pytest.fixture
def sample_item_data():
    """Create sample item data for testing."""
    return {
        "id": "item-1",
        "name": "Health Potion",
        "category": "consumable",
        "base_value": 50.0,
        "condition": 1.0,
        "metadata": {}
    }


class TestShopUtils:
    """Test suite for the shop utils module."""

    def test_shop_types_configuration(self):
        """Test that shop types are properly configured."""
        assert "general" in SHOP_TYPES
        assert "blacksmith" in SHOP_TYPES
        assert "alchemist" in SHOP_TYPES
        assert "tavern" in SHOP_TYPES
        assert "market" in SHOP_TYPES
        
        # Check general store configuration
        general = SHOP_TYPES["general"]
        assert general["name"] == "General Store"
        assert general["base_inventory_size"] == 15
        assert general["restock_days"] == 3
        assert general["markup_modifier"] == 1.2

    @patch('backend.systems.economy.utils.shop_utils._generate_shop_inventory')
    def test_get_shop_inventory_no_existing_inventory(self, mock_generate, sample_poi):
        """Test getting shop inventory when none exists."""
        sample_poi.metadata = {"shop": {"type": "general", "tier": 1}}
        mock_generate.return_value = [{"id": "item-1", "name": "Test Item"}]
        
        result = get_shop_inventory(sample_poi)
        
        assert result == [{"id": "item-1", "name": "Test Item"}]
        mock_generate.assert_called_once_with(sample_poi)

    @patch('backend.systems.economy.utils.shop_utils._apply_current_pricing')
    def test_get_shop_inventory_existing_fresh(self, mock_pricing, sample_poi, sample_inventory):
        """Test getting shop inventory when existing inventory is fresh."""
        # Set recent restock time
        recent_time = datetime.utcnow() - timedelta(hours=1)
        sample_poi.metadata["shop"]["last_restock"] = recent_time.isoformat()
        sample_poi.metadata["shop"]["inventory"] = sample_inventory
        
        mock_pricing.return_value = sample_inventory
        
        result = get_shop_inventory(sample_poi)
        
        assert result == sample_inventory
        mock_pricing.assert_called_once_with(sample_inventory, "general", 1, "1")

    @patch('backend.systems.economy.utils.shop_utils._generate_shop_inventory')
    def test_get_shop_inventory_existing_stale(self, mock_generate, sample_poi, sample_inventory):
        """Test getting shop inventory when existing inventory is stale."""
        # Set old restock time
        old_time = datetime.utcnow() - timedelta(days=5)
        sample_poi.metadata["shop"]["last_restock"] = old_time.isoformat()
        sample_poi.metadata["shop"]["inventory"] = sample_inventory
        
        mock_generate.return_value = [{"id": "new-item", "name": "New Item"}]
        
        result = get_shop_inventory(sample_poi)
        
        assert result == [{"id": "new-item", "name": "New Item"}]
        mock_generate.assert_called_once_with(sample_poi)

    def test_get_shop_inventory_error_handling(self, sample_poi):
        """Test error handling in get_shop_inventory."""
        # Create POI with invalid metadata that will cause an error
        sample_poi.metadata = {"shop": {"last_restock": "invalid-date"}}
        
        result = get_shop_inventory(sample_poi)
        
        assert result == []

    @patch('backend.systems.economy.utils.shop_utils._generate_shop_inventory')
    def test_restock_shop_success(self, mock_generate, sample_poi):
        """Test successful shop restocking."""
        new_inventory = [{"id": "new-item", "name": "New Item"}]
        mock_generate.return_value = new_inventory
        
        restock_shop(sample_poi)
        
        assert sample_poi.metadata["shop"]["inventory"] == new_inventory
        assert "last_restock" in sample_poi.metadata["shop"]
        sample_poi.update_timestamp.assert_called_once()

    def test_restock_shop_no_shop_metadata(self, sample_poi):
        """Test restocking shop without existing shop metadata."""
        sample_poi.metadata = {}
        
        with patch('backend.systems.economy.utils.shop_utils._generate_shop_inventory') as mock_generate:
            mock_generate.return_value = []
            restock_shop(sample_poi)
            
            assert "shop" in sample_poi.metadata
            assert "inventory" in sample_poi.metadata["shop"]
            assert "last_restock" in sample_poi.metadata["shop"]

    def test_restock_shop_error_handling(self, sample_poi):
        """Test error handling in restock_shop."""
        # Force an error by making metadata non-dict
        sample_poi.metadata = None
        
        # Should not raise an exception
        restock_shop(sample_poi)

    @patch('backend.systems.economy.utils.shop_utils.loot_generate_shop_inventory')
    def test_generate_shop_inventory_success(self, mock_loot_gen, sample_poi):
        """Test successful shop inventory generation."""
        mock_loot_items = [
            MagicMock(id="item-1", name="Test Item", base_value=50.0, category="consumable")
        ]
        mock_loot_gen.return_value = mock_loot_items
        
        with patch('backend.systems.economy.utils.shop_utils.get_dynamic_item_price', return_value=60.0):
            result = _generate_shop_inventory(sample_poi)
            
            assert len(result) > 0
            mock_loot_gen.assert_called_once()

    @patch('backend.systems.economy.utils.shop_utils.loot_generate_shop_inventory')
    def test_generate_shop_inventory_loot_error(self, mock_loot_gen, sample_poi):
        """Test shop inventory generation when loot system fails."""
        mock_loot_gen.side_effect = Exception("Loot system error")
        
        with patch('backend.systems.economy.utils.shop_utils._generate_fallback_inventory') as mock_fallback:
            mock_fallback.return_value = [{"id": "fallback-item"}]
            
            result = _generate_shop_inventory(sample_poi)
            
            assert result == [{"id": "fallback-item"}]
            mock_fallback.assert_called_once()

    def test_generate_fallback_inventory(self):
        """Test fallback inventory generation."""
        shop_config = SHOP_TYPES["general"]
        inventory_size = 5
        
        result = _generate_fallback_inventory(shop_config, inventory_size)
        
        assert len(result) == inventory_size
        for item in result:
            assert "id" in item
            assert "name" in item
            assert "category" in item
            assert "base_price" in item
            assert "shop_price" in item

    @patch('backend.systems.economy.utils.shop_utils.get_dynamic_item_price')
    def test_apply_current_pricing(self, mock_price, sample_inventory):
        """Test applying current pricing to inventory."""
        mock_price.return_value = 75.0
        
        result = _apply_current_pricing(sample_inventory, "general", 1, "1")
        
        assert len(result) == len(sample_inventory)
        # Prices should be updated
        for item in result:
            assert "shop_price" in item

    def test_calculate_sale_value_basic(self):
        """Test basic sale value calculation."""
        result = calculate_sale_value(100.0)
        
        assert result == 100.0

    def test_calculate_sale_value_with_modifiers(self):
        """Test sale value calculation with modifiers."""
        result = calculate_sale_value(
            item_base_value=100.0,
            condition=0.8,
            market_modifier=1.2,
            quantity=2
        )
        
        expected = 100.0 * 0.8 * 1.2 * 2
        assert result == expected

    def test_calculate_sale_value_minimum_enforced(self):
        """Test that minimum sale value is enforced."""
        result = calculate_sale_value(0.5)  # Very low value
        
        assert result == 0.5

    def test_calculate_sale_value_below_minimum(self):
        """Test sale value below minimum threshold."""
        result = calculate_sale_value(0.05)  # Below minimum
        
        assert result == 0.1

    def test_calculate_purchase_value_basic(self):
        """Test basic purchase value calculation."""
        result = calculate_purchase_value(100.0)
        
        assert result == 100.0

    def test_calculate_purchase_value_with_modifiers(self):
        """Test purchase value calculation with modifiers."""
        result = calculate_purchase_value(
            item_shop_price=100.0,
            negotiation_bonus=0.1,  # 20% of 0.1 = 2% discount
            reputation_modifier=0.9,
            quantity=2
        )
        
        expected = 100.0 * (1.0 - 0.1 * 0.2) * 0.9 * 2
        assert result == expected

    def test_calculate_purchase_value_minimum_enforced(self):
        """Test that minimum purchase value is enforced."""
        result = calculate_purchase_value(
            item_shop_price=2.0,
            negotiation_bonus=0.9,  # 90% discount
            reputation_modifier=0.1
        )
        
        assert result == 1.0  # Should be minimum

    def test_get_shop_type_from_poi_with_metadata(self, sample_poi):
        """Test getting shop type from POI with metadata."""
        result = get_shop_type_from_poi(sample_poi)
        
        assert result == "general"

    def test_get_shop_type_from_poi_no_metadata(self, sample_poi):
        """Test getting shop type from POI without metadata."""
        sample_poi.metadata = {}
        sample_poi.poi_type = POIType.SHOP
        
        result = get_shop_type_from_poi(sample_poi)
        
        assert result == "general"  # Default

    def test_get_shop_type_from_poi_by_name(self, sample_poi):
        """Test getting shop type from POI by name inference."""
        sample_poi.metadata = {}
        sample_poi.name = "Village Blacksmith"
        sample_poi.poi_type = POIType.SHOP
        
        result = get_shop_type_from_poi(sample_poi)
        
        assert result == "blacksmith"

    def test_get_shop_type_from_poi_market_type(self, sample_poi):
        """Test getting shop type from POI with market type."""
        sample_poi.metadata = {}
        sample_poi.poi_type = POIType.MARKET
        
        result = get_shop_type_from_poi(sample_poi)
        
        assert result == "market"

    def test_initialize_shop_metadata_new(self, sample_poi):
        """Test initializing shop metadata for new shop."""
        sample_poi.metadata = {}
        sample_poi.poi_type = POIType.SHOP
        
        initialize_shop_metadata(sample_poi)
        
        assert "shop" in sample_poi.metadata
        assert sample_poi.metadata["shop"]["type"] == "general"
        assert sample_poi.metadata["shop"]["tier"] == 1
        assert "last_restock" in sample_poi.metadata["shop"]

    def test_initialize_shop_metadata_existing(self, sample_poi):
        """Test initializing shop metadata for existing shop."""
        original_type = sample_poi.metadata["shop"]["type"]
        
        initialize_shop_metadata(sample_poi)
        
        # Should not overwrite existing metadata
        assert sample_poi.metadata["shop"]["type"] == original_type

    @patch('backend.systems.economy.utils.shop_utils.get_shop_inventory')
    def test_purchase_item_from_shop_success(self, mock_inventory, sample_poi, sample_inventory):
        """Test successful item purchase from shop."""
        mock_inventory.return_value = sample_inventory
        
        success, message, result = purchase_item_from_shop(sample_poi, "item-1", 123, 1)
        
        assert success is True
        assert "purchased" in message.lower()
        assert "item_id" in result
        assert "total_cost" in result

    @patch('backend.systems.economy.utils.shop_utils.get_shop_inventory')
    def test_purchase_item_from_shop_not_found(self, mock_inventory, sample_poi, sample_inventory):
        """Test purchasing item that doesn't exist in shop."""
        mock_inventory.return_value = sample_inventory
        
        success, message, result = purchase_item_from_shop(sample_poi, "nonexistent", 123, 1)
        
        assert success is False
        assert "not found" in message.lower()
        assert result == {}

    @patch('backend.systems.economy.utils.shop_utils.get_shop_inventory')
    def test_purchase_item_from_shop_insufficient_quantity(self, mock_inventory, sample_poi, sample_inventory):
        """Test purchasing more items than available."""
        mock_inventory.return_value = sample_inventory
        
        success, message, result = purchase_item_from_shop(sample_poi, "item-1", 123, 10)  # More than available
        
        assert success is False
        assert "stock" in message.lower()
        assert result == {}

    def test_purchase_item_from_shop_error_handling(self, sample_poi):
        """Test error handling in purchase_item_from_shop."""
        # Force an error by making metadata invalid
        sample_poi.metadata = None
        
        success, message, result = purchase_item_from_shop(sample_poi, "item-1", 123, 1)
        
        assert success is False
        assert "not found" in message.lower()
        assert result == {}

    @patch('backend.systems.economy.utils.shop_utils.get_shop_inventory')
    def test_sell_item_to_shop_success(self, mock_inventory, sample_poi, sample_inventory, sample_item_data):
        """Test successful item sale to shop."""
        mock_inventory.return_value = sample_inventory
        
        success, message, result = sell_item_to_shop(sample_poi, sample_item_data, 123, 1)
        
        assert success is True
        assert "sold" in message.lower()
        assert "sale_value" in result
        assert "item_name" in result

    def test_sell_item_to_shop_error_handling(self, sample_poi, sample_item_data):
        """Test error handling in sell_item_to_shop."""
        # Force an error by making metadata invalid
        sample_poi.metadata = None
        
        success, message, result = sell_item_to_shop(sample_poi, sample_item_data, 123, 1)
        
        assert success is False
        assert "error" in message.lower()
        assert result == {}
