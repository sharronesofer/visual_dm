"""
Test shop utilities SQLAlchemy integration.

This module tests that shop utilities properly integrate with
SQLAlchemy instead of Firebase database.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from backend.infrastructure.utils.shop_utils import (
    get_shop_inventory,
    calculate_sale_value,
    calculate_resale_value,
    buy_item_from_shop,
    restock_shop_inventory,
    calculate_price_with_modifiers,
    generate_inventory_from_tags
)


class TestShopUtilsSQLAlchemyIntegration:
    """Test that shop utilities work with SQLAlchemy instead of Firebase."""
    
    def test_get_shop_inventory_requires_db_session(self):
        """Test that get_shop_inventory requires a database session."""
        with pytest.raises(ValueError, match="Database session required"):
            get_shop_inventory("npc_001")
    
    @patch('backend.infrastructure.utils.shop_utils.EconomyManager')
    def test_get_shop_inventory_uses_economy_manager(self, mock_economy_manager):
        """Test that get_shop_inventory uses EconomyManager."""
        # Setup mock economy manager
        mock_manager_instance = Mock()
        mock_manager_instance.generate_shop_inventory.return_value = [
            {"name": "Test Item 1", "rarity": "common"},
            {"name": "Test Item 2", "rarity": "rare"}
        ]
        mock_economy_manager.get_instance.return_value = mock_manager_instance
        
        # Call function with proper session
        result = get_shop_inventory("npc_001", Mock())
        
        # Verify manager was called correctly
        mock_economy_manager.get_instance.assert_called_once()
        mock_manager_instance.generate_shop_inventory.assert_called_once_with(
            npc_id="npc_001", shop_type="general", item_count=15, average_player_level=10
        )
        
        # Verify returned inventory has proper structure
        assert "npc_001_item_0" in result
        assert "npc_001_item_1" in result
        assert result["npc_001_item_0"]["rarity_color"] == "gray"  # common = gray
        assert result["npc_001_item_1"]["rarity_color"] == "green"  # rare = green
    
    @patch('backend.infrastructure.utils.shop_utils.EconomyManager')
    def test_calculate_sale_value_uses_economy_manager(self, mock_economy_manager):
        """Test that calculate_sale_value uses EconomyManager."""
        mock_manager_instance = Mock()
        mock_manager_instance.calculate_shop_buy_price.return_value = (50.0, {"method": "unified"})
        mock_economy_manager.get_instance.return_value = mock_manager_instance
        
        item = {"name": "Test Sword", "category": "weapon"}
        result = calculate_sale_value(item, 10, mock_manager_instance)
        
        # Verify economy manager method was called
        mock_manager_instance.calculate_shop_buy_price.assert_called_once_with(item, 10)
        assert result == 50
    
    @patch('backend.infrastructure.utils.shop_utils.EconomyManager')
    def test_calculate_resale_value_uses_economy_manager(self, mock_economy_manager):
        """Test that calculate_resale_value uses EconomyManager."""
        mock_manager_instance = Mock()
        mock_manager_instance.calculate_shop_sell_price.return_value = (75.0, {"method": "unified"})
        mock_economy_manager.get_instance.return_value = mock_manager_instance
        
        item = {"name": "Test Sword", "category": "weapon"}
        result = calculate_resale_value(item, 10, mock_manager_instance)
        
        # Verify economy manager method was called
        mock_manager_instance.calculate_shop_sell_price.assert_called_once_with(item, 10)
        assert result == 75
    
    def test_buy_item_from_shop_requires_db_session(self):
        """Test that buy_item_from_shop raises error without db_session."""
        with pytest.raises(ValueError, match="Database session required"):
            buy_item_from_shop("char_001", "npc_001", "item_001")
    
    @patch('backend.infrastructure.utils.shop_utils.EconomyManager')
    def test_buy_item_from_shop_uses_economy_manager(self, mock_economy_manager):
        """Test that buy_item_from_shop integrates with EconomyManager."""
        # Setup mocks
        mock_session = Mock()
        mock_manager_instance = Mock()
        mock_manager_instance.process_shop_transaction.return_value = {"success": True}
        mock_economy_manager.get_instance.return_value = mock_manager_instance
        
        # Mock get_shop_inventory to return an item
        with patch('backend.infrastructure.utils.shop_utils.get_shop_inventory') as mock_get_inventory:
            mock_get_inventory.return_value = {
                "item_001": {"name": "Test Item", "resale_price": 100}
            }
            
            result = buy_item_from_shop("char_001", "npc_001", "item_001", mock_session)
            
            # Verify economy manager integration
            mock_economy_manager.get_instance.assert_called_once_with(mock_session)
            mock_manager_instance.process_shop_transaction.assert_called_once()
            assert result["success"] is True
    
    def test_restock_shop_inventory_requires_db_session(self):
        """Test that restock_shop_inventory raises error without db_session."""
        with pytest.raises(ValueError, match="Database session required"):
            restock_shop_inventory("npc_001")
    
    @patch('backend.infrastructure.utils.shop_utils.EconomyManager')
    @patch('backend.infrastructure.utils.shop_utils.generate_inventory_from_tags')
    def test_restock_shop_inventory_uses_economy_manager(self, mock_generate_inventory, mock_economy_manager):
        """Test that restock_shop_inventory integrates with EconomyManager."""
        # Setup mocks
        mock_session = Mock()
        mock_manager_instance = Mock()
        mock_manager_instance.calculate_shop_sell_price.return_value = (75.0, {"method": "unified"})
        mock_economy_manager.get_instance.return_value = mock_manager_instance
        
        mock_inventory = [
            {"name": "Test Item 1", "category": "gear"},
            {"name": "Test Item 2", "category": "consumables"}
        ]
        mock_generate_inventory.return_value = mock_inventory
        
        # Call function
        result = restock_shop_inventory("npc_001", mock_session)
        
        # Verify EconomyManager integration
        mock_economy_manager.get_instance.assert_called_once_with(mock_session)
        
        # Verify pricing was applied to generated items
        assert mock_manager_instance.calculate_shop_sell_price.call_count == 2
        
        # Verify return structure
        assert result["npc_id"] == "npc_001"
        assert result["restocked_items"] == 2
        assert result["pricing_method"] == "unified_economy_system"
    
    @patch('backend.infrastructure.utils.shop_utils.EconomyManager')
    def test_calculate_price_with_modifiers_uses_economy_manager(self, mock_economy_manager):
        """Test that calculate_price_with_modifiers uses EconomyManager."""
        mock_manager_instance = Mock()
        mock_manager_instance._apply_character_pricing_modifiers.return_value = (120.0, {"modifier": "charisma"})
        mock_economy_manager.get_instance.return_value = mock_manager_instance
        
        character_attributes = {"charisma": 16}
        faction_reputation = {"merchant_guild": 50}
        
        result = calculate_price_with_modifiers(100.0, character_attributes, faction_reputation)
        
        # Verify EconomyManager method was called
        mock_manager_instance._apply_character_pricing_modifiers.assert_called_once_with(
            100.0, character_attributes, faction_reputation
        )
        assert result == 120
    
    @patch('backend.infrastructure.utils.shop_utils.EconomyManager')
    def test_generate_inventory_from_tags_uses_economy_manager(self, mock_economy_manager):
        """Test that generate_inventory_from_tags integrates with EconomyManager resources."""
        # Setup mock economy manager with resources
        mock_manager_instance = Mock()
        mock_resource1 = Mock()
        mock_resource1.id = 1
        mock_resource1.name = "Iron Ore"
        mock_resource1.resource_type = "armor"
        mock_resource1.base_value = 25.0
        
        mock_resource2 = Mock()
        mock_resource2.id = 2
        mock_resource2.name = "Steel Ingot"
        mock_resource2.resource_type = "weapons"
        mock_resource2.base_value = 40.0
        
        mock_manager_instance.get_available_resources.side_effect = [
            [mock_resource1],  # For "armor" tag
            [mock_resource2]   # For "weapons" tag
        ]
        mock_economy_manager.get_instance.return_value = mock_manager_instance
        
        # Call function
        result = generate_inventory_from_tags(["armor", "weapons"], mock_manager_instance)
        
        # Verify resources were queried
        assert mock_manager_instance.get_available_resources.call_count == 2
        mock_manager_instance.get_available_resources.assert_any_call(resource_type="armor")
        mock_manager_instance.get_available_resources.assert_any_call(resource_type="weapons")
        
        # Verify generated inventory
        assert len(result) == 2
        assert any(item["name"] == "Iron Ore" for item in result)
        assert any(item["name"] == "Steel Ingot" for item in result)
        assert all(item.get("resource_id") is not None for item in result)
    
    def test_generate_inventory_from_tags_fallback_without_economy_manager(self):
        """Test that generate_inventory_from_tags falls back to hardcoded items."""
        result = generate_inventory_from_tags(["armor", "weapons"])
        
        # Should generate some items from hardcoded pools
        assert len(result) > 0
        assert all(item.get("name") for item in result)
        assert all(item.get("category") for item in result)
        assert all(item.get("gold_value") for item in result)


class TestFirebaseMigrationCompletion:
    """Test that Firebase migration is complete."""
    
    def test_no_firebase_imports_in_shop_utils(self):
        """Test that shop_utils.py contains no Firebase imports."""
        import backend.infrastructure.utils.shop_utils as shop_utils
        import inspect
        
        source = inspect.getsource(shop_utils)
        
        # Check for Firebase-related imports or references
        firebase_keywords = [
            "firebase_admin",
            "firebase",
            "from firebase",
            "import firebase"
        ]
        
        for keyword in firebase_keywords:
            assert keyword.lower() not in source.lower(), f"Found Firebase reference: {keyword}"
    
    def test_sqlalchemy_integration_present(self):
        """Test that SQLAlchemy integration is present in shop utilities."""
        import backend.infrastructure.utils.shop_utils as shop_utils
        import inspect
        
        source = inspect.getsource(shop_utils)
        
        # Check for SQLAlchemy integration
        sqlalchemy_indicators = [
            "from sqlalchemy.orm import Session",
            "db_session: Session",
            "EconomyManager"
        ]
        
        for indicator in sqlalchemy_indicators:
            assert indicator in source, f"Missing SQLAlchemy integration: {indicator}"
    
    def test_shop_functions_accept_db_session(self):
        """Test that shop functions accept db_session parameter."""
        from backend.infrastructure.utils.shop_utils import (
            get_shop_inventory,
            buy_item_from_shop,
            restock_shop_inventory
        )
        import inspect
        
        # Check function signatures
        functions_requiring_session = [
            get_shop_inventory,
            buy_item_from_shop,
            restock_shop_inventory
        ]
        
        for func in functions_requiring_session:
            sig = inspect.signature(func)
            assert 'db_session' in sig.parameters, f"{func.__name__} missing db_session parameter"
            
            # Verify parameter type annotation
            db_session_param = sig.parameters['db_session']
            assert 'Session' in str(db_session_param.annotation), f"{func.__name__} db_session not typed as Session"


if __name__ == "__main__":
    # Run basic tests if called directly
    test_instance = TestShopUtilsSQLAlchemyIntegration()
    
    print("Testing shop utilities SQLAlchemy integration...")
    
    # Test basic requirements
    try:
        test_instance.test_get_shop_inventory_requires_db_session()
        print("✅ get_shop_inventory requires db_session")
    except Exception as e:
        print(f"❌ get_shop_inventory test failed: {e}")
    
    try:
        test_instance.test_buy_item_from_shop_requires_db_session()
        print("✅ buy_item_from_shop requires db_session")
    except Exception as e:
        print(f"❌ buy_item_from_shop test failed: {e}")
    
    try:
        test_instance.test_restock_shop_inventory_requires_db_session()
        print("✅ restock_shop_inventory requires db_session")
    except Exception as e:
        print(f"❌ restock_shop_inventory test failed: {e}")
    
    # Test migration completion
    migration_test = TestFirebaseMigrationCompletion()
    
    try:
        migration_test.test_no_firebase_imports_in_shop_utils()
        print("✅ No Firebase imports found")
    except Exception as e:
        print(f"❌ Firebase import test failed: {e}")
    
    try:
        migration_test.test_sqlalchemy_integration_present()
        print("✅ SQLAlchemy integration present")
    except Exception as e:
        print(f"❌ SQLAlchemy integration test failed: {e}")
    
    try:
        migration_test.test_shop_functions_accept_db_session()
        print("✅ Shop functions accept db_session parameter")
    except Exception as e:
        print(f"❌ db_session parameter test failed: {e}")
    
    print("\nShop utilities SQLAlchemy migration test completed!") 