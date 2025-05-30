"""
Tests for the shop router module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.systems.economy.routers.shop_router import router


@pytest.fixture
def app():
    """Create a FastAPI app for testing."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_economy_manager():
    """Create a mock economy manager."""
    manager = MagicMock()
    manager.get_instance.return_value = manager
    return manager


@pytest.fixture
def mock_user():
    """Create a mock user."""
    return {"id": 1, "name": "test_user"}


class TestShopRouter:
    """Test cases for shop router endpoints."""

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.get_shop_inventory')
    def test_get_shop_inventory_success(self, mock_get_inventory, mock_economy_manager, 
                                      mock_get_user, mock_get_db, client):
        """Test successful shop inventory retrieval."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_get_inventory.return_value = [
            {"item_id": 1, "name": "Sword", "quantity": 5, "price": 100},
            {"item_id": 2, "name": "Shield", "quantity": 3, "price": 50}
        ]

        # Make request
        response = client.get("/inventory/1")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["item_id"] == 1
        assert data[0]["name"] == "Sword"
        assert data[1]["item_id"] == 2
        assert data[1]["name"] == "Shield"
        mock_get_inventory.assert_called_once()

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.get_shop_inventory')
    def test_get_shop_inventory_error(self, mock_get_inventory, mock_economy_manager,
                                    mock_get_user, mock_get_db, client):
        """Test shop inventory retrieval with error."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_get_inventory.side_effect = Exception("Shop not found")

        # Make request
        response = client.get("/inventory/999")

        # Assertions
        assert response.status_code == 400
        assert "Shop not found" in response.json()["detail"]

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.calculate_sale_value')
    def test_sell_item_to_shop_success(self, mock_calc_sale, mock_economy_manager,
                                     mock_get_user, mock_get_db, client):
        """Test successful item sale to shop."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_calc_sale.return_value = 75.0

        # Make request
        response = client.post("/sell/1", json={"item_id": 1, "quantity": 2})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["gold_received"] == 75.0
        assert data["item_id"] == 1
        assert data["quantity"] == 2
        assert data["shop_id"] == 1
        mock_calc_sale.assert_called_once()

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.calculate_sale_value')
    def test_sell_item_to_shop_error(self, mock_calc_sale, mock_economy_manager,
                                   mock_get_user, mock_get_db, client):
        """Test item sale to shop with error."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_calc_sale.side_effect = Exception("Item not found")

        # Make request
        response = client.post("/sell/1", json={"item_id": 999, "quantity": 1})

        # Assertions
        assert response.status_code == 400
        assert "Item not found" in response.json()["detail"]

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.calculate_purchase_value')
    def test_buy_item_from_shop_success(self, mock_calc_purchase, mock_economy_manager,
                                      mock_get_user, mock_get_db, client):
        """Test successful item purchase from shop."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_calc_purchase.return_value = 120.0

        # Make request
        response = client.post("/buy/1", json={"item_id": 1, "quantity": 1})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["gold_spent"] == 120.0
        assert data["item_id"] == 1
        assert data["quantity"] == 1
        assert data["shop_id"] == 1
        mock_calc_purchase.assert_called_once()

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.calculate_purchase_value')
    def test_buy_item_from_shop_error(self, mock_calc_purchase, mock_economy_manager,
                                    mock_get_user, mock_get_db, client):
        """Test item purchase from shop with error."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_calc_purchase.side_effect = Exception("Insufficient funds")

        # Make request
        response = client.post("/buy/1", json={"item_id": 1, "quantity": 10})

        # Assertions
        assert response.status_code == 400
        assert "Insufficient funds" in response.json()["detail"]

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.restock_shop')
    def test_restock_shop_success(self, mock_restock, mock_economy_manager,
                                mock_get_user, mock_get_db, client):
        """Test successful shop restocking."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_restock.return_value = {
            "success": True,
            "items_added": 5,
            "shop_id": 1
        }

        # Make request
        response = client.post("/restock/1")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["items_added"] == 5
        assert data["shop_id"] == 1
        mock_restock.assert_called_once()

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.restock_shop')
    def test_restock_shop_error(self, mock_restock, mock_economy_manager,
                              mock_get_user, mock_get_db, client):
        """Test shop restocking with error."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_restock.side_effect = Exception("Shop not found")

        # Make request
        response = client.post("/restock/999")

        # Assertions
        assert response.status_code == 400
        assert "Shop not found" in response.json()["detail"]

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.calculate_purchase_value')
    def test_preview_item_price_buying(self, mock_calc_purchase, mock_economy_manager,
                                     mock_get_user, mock_get_db, client):
        """Test price preview for buying an item."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_calc_purchase.return_value = 150.0

        # Make request
        response = client.post("/preview_price", json={
            "item_id": 1,
            "shop_id": 1,
            "is_buying": True,
            "quantity": 2
        })

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 1
        assert data["shop_id"] == 1
        assert data["is_buying"] is True
        assert data["quantity"] == 2
        assert data["value"] == 150.0
        mock_calc_purchase.assert_called_once()

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.calculate_sale_value')
    def test_preview_item_price_selling(self, mock_calc_sale, mock_economy_manager,
                                      mock_get_user, mock_get_db, client):
        """Test price preview for selling an item."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_calc_sale.return_value = 80.0

        # Make request
        response = client.post("/preview_price", json={
            "item_id": 1,
            "shop_id": 1,
            "is_buying": False,
            "quantity": 1
        })

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 1
        assert data["shop_id"] == 1
        assert data["is_buying"] is False
        assert data["quantity"] == 1
        assert data["value"] == 80.0
        mock_calc_sale.assert_called_once()

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.calculate_purchase_value')
    def test_preview_item_price_error(self, mock_calc_purchase, mock_economy_manager,
                                    mock_get_user, mock_get_db, client):
        """Test price preview with error."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_calc_purchase.side_effect = Exception("Item not available")

        # Make request
        response = client.post("/preview_price", json={
            "item_id": 999,
            "shop_id": 1,
            "is_buying": True,
            "quantity": 1
        })

        # Assertions
        assert response.status_code == 400
        assert "Item not available" in response.json()["detail"]

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.get_shop_inventory')
    def test_get_shop_inventory_with_path_parameter(self, mock_get_inventory, mock_economy_manager,
                                                  mock_get_user, mock_get_db, client):
        """Test shop inventory retrieval with different shop IDs."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_get_inventory.return_value = []

        # Make request with different shop ID
        response = client.get("/inventory/42")

        # Assertions
        assert response.status_code == 200
        assert response.json() == []
        mock_get_inventory.assert_called_once()

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.calculate_sale_value')
    def test_sell_item_default_quantity(self, mock_calc_sale, mock_economy_manager,
                                      mock_get_user, mock_get_db, client):
        """Test selling item with default quantity."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_calc_sale.return_value = 50.0

        # Make request without quantity (should default to 1)
        response = client.post("/sell/1", json={"item_id": 1})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 1  # Default quantity
        assert data["gold_received"] == 50.0

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.calculate_purchase_value')
    def test_buy_item_default_quantity(self, mock_calc_purchase, mock_economy_manager,
                                     mock_get_user, mock_get_db, client):
        """Test buying item with default quantity."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_calc_purchase.return_value = 100.0

        # Make request without quantity (should default to 1)
        response = client.post("/buy/1", json={"item_id": 1})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 1  # Default quantity
        assert data["gold_spent"] == 100.0

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    @patch('backend.systems.economy.routers.shop_router.EconomyManager')
    @patch('backend.systems.economy.routers.shop_router.calculate_purchase_value')
    def test_preview_price_default_quantity(self, mock_calc_purchase, mock_economy_manager,
                                          mock_get_user, mock_get_db, client):
        """Test price preview with default quantity."""
        # Setup mocks
        mock_get_db.return_value = MagicMock()
        mock_get_user.return_value = {"id": 1, "name": "test_user"}
        mock_economy_manager.get_instance.return_value = MagicMock()
        mock_calc_purchase.return_value = 75.0

        # Make request without quantity (should default to 1)
        response = client.post("/preview_price", json={
            "item_id": 1,
            "shop_id": 1,
            "is_buying": True
        })

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 1  # Default quantity
        assert data["value"] == 75.0

    def test_router_tags(self):
        """Test that router has correct tags."""
        assert router.tags == ["shops"]

    @patch('backend.systems.economy.routers.shop_router.get_db')
    @patch('backend.systems.economy.routers.shop_router.get_current_user')
    def test_dependency_injection_mocking(self, mock_get_user, mock_get_db, client):
        """Test that dependency injection can be properly mocked."""
        # Setup mocks
        mock_db = MagicMock()
        mock_user = {"id": 1, "name": "test_user"}
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # The dependencies should be called when making requests
        # This test verifies the mocking infrastructure works
        with patch('backend.systems.economy.routers.shop_router.get_shop_inventory') as mock_inventory:
            mock_inventory.return_value = []
            with patch('backend.systems.economy.routers.shop_router.EconomyManager') as mock_manager:
                mock_manager.get_instance.return_value = MagicMock()
                
                response = client.get("/inventory/1")
                assert response.status_code == 200
                # Verify the mocking infrastructure works by checking response
                assert response.json() == []
