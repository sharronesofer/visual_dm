"""
Test NPC Barter Router

Tests for NPC bartering API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, patch
from uuid import uuid4
from fastapi import HTTPException, status
import json

# Import router from infrastructure
from backend.infrastructure.systems.npc.routers.barter_router import router
from backend.systems.npc.services.npc_barter_service import NPCBarterService
from backend.infrastructure.shared.exceptions import (
    NpcNotFoundError,
    NpcValidationError
)


class TestBarterRouter:
    """Test NPC Bartering Router endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.test_npc_id = uuid4()
        self.test_character_id = "test_character"
        
        # Mock service responses
        self.mock_inventory_response = {
            "npc_id": str(self.test_npc_id),
            "npc_name": "Test Merchant",
            "relationship_trust": 0.5,
            "total_items": 3,
            "items": {
                "always_available": [
                    {
                        "id": "item1",
                        "name": "Bread",
                        "value": 2,
                        "tier": "always_available",
                        "can_trade": True
                    }
                ],
                "high_trust_required": [
                    {
                        "id": "item2",
                        "name": "Magic Sword",
                        "value": 500,
                        "tier": "high_price_relationship",
                        "can_trade": True
                    }
                ],
                "not_available": [
                    {
                        "id": "item3",
                        "name": "Shop Keys",
                        "value": 10,
                        "tier": "never_available",
                        "can_trade": False,
                        "reason": "Essential for role"
                    }
                ]
            }
        }
        
        self.mock_price_response = {
            "item_id": "item1",
            "item_name": "Bread",
            "can_trade": True,
            "price": 1.8,
            "base_value": 2,
            "tier": "always_available",
            "relationship_trust": 0.5,
            "price_factors": {
                "tier_multiplier": 1.0,
                "relationship_discount": 0.1,
                "npc_charisma": 14,
                "npc_pragmatism": 2
            }
        }
        
        self.mock_initiate_response = {
            "npc_id": str(self.test_npc_id),
            "character_id": self.test_character_id,
            "trade_acceptable": True,
            "value_ratio": 0.9,
            "required_ratio": 0.8,
            "total_offer_value": 100,
            "total_request_value": 50,
            "relationship_trust": 0.5,
            "item_validations": [
                {
                    "item_id": "item1",
                    "valid": True,
                    "price": 1.8,
                    "tier": "always_available"
                }
            ],
            "message": "Test Merchant agrees this is a fair trade."
        }
        
        self.mock_complete_response = {
            "success": True,
            "transaction_id": "barter_123_456",
            "npc_id": str(self.test_npc_id),
            "character_id": self.test_character_id,
            "relationship_improvement": 0.05,
            "message": "Test Merchant thanks you for the trade!",
            "transaction_log": {
                "timestamp": "2023-01-01T00:00:00",
                "character_id": self.test_character_id,
                "items_given": [{"name": "Gold", "value": 100}],
                "items_received": [{"name": "Bread", "value": 2}],
                "value_exchanged": 50
            }
        }
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_get_npc_tradeable_inventory_success(self, mock_get_service):
        """Test getting NPC tradeable inventory successfully"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.get_tradeable_items = AsyncMock(return_value=self.mock_inventory_response)
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get(
            f"/npc/{self.test_npc_id}/barter/inventory",
            params={"character_id": self.test_character_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["npc_id"] == str(self.test_npc_id)
        assert data["npc_name"] == "Test Merchant"
        assert data["total_items"] == 3
        assert "always_available" in data["items"]
        
        mock_service.get_tradeable_items.assert_called_once_with(
            self.test_npc_id, self.test_character_id
        )
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_get_npc_tradeable_inventory_npc_not_found(self, mock_get_service):
        """Test getting inventory when NPC not found"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.get_tradeable_items = AsyncMock(
            side_effect=NpcNotFoundError("NPC not found")
        )
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get(f"/npc/{self.test_npc_id}/barter/inventory")
        
        assert response.status_code == 404
        assert "NPC not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_get_npc_tradeable_inventory_server_error(self, mock_get_service):
        """Test getting inventory with server error"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.get_tradeable_items = AsyncMock(
            side_effect=Exception("Database error")
        )
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get(f"/npc/{self.test_npc_id}/barter/inventory")
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_get_item_barter_price_success(self, mock_get_service):
        """Test getting item barter price successfully"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.get_item_barter_price = AsyncMock(return_value=self.mock_price_response)
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get(
            f"/npc/{self.test_npc_id}/barter/price/item1",
            params={"character_id": self.test_character_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == "item1"
        assert data["can_trade"] is True
        assert data["price"] == 1.8
        
        mock_service.get_item_barter_price.assert_called_once_with(
            self.test_npc_id, "item1", self.test_character_id
        )
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_get_item_barter_price_validation_error(self, mock_get_service):
        """Test getting item price with validation error"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.get_item_barter_price = AsyncMock(
            side_effect=NpcValidationError("Item not found")
        )
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get(f"/npc/{self.test_npc_id}/barter/price/invalid_item")
        
        assert response.status_code == 400
        assert "Item not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_initiate_barter_success(self, mock_get_service):
        """Test initiating barter successfully"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.initiate_barter = AsyncMock(return_value=self.mock_initiate_response)
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        request_data = {
            "character_id": self.test_character_id,
            "offer_items": [
                {"id": "gold", "name": "Gold Coins", "quantity": 10, "value": 10}
            ],
            "request_items": [
                {"id": "item1", "name": "Bread", "quantity": 1}
            ]
        }
        
        response = client.post(
            f"/npc/{self.test_npc_id}/barter/initiate",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["trade_acceptable"] is True
        assert data["npc_id"] == str(self.test_npc_id)
        
        mock_service.initiate_barter.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_initiate_barter_npc_not_found(self, mock_get_service):
        """Test initiating barter when NPC not found"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.initiate_barter = AsyncMock(
            side_effect=NpcNotFoundError("NPC not found")
        )
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        request_data = {
            "character_id": self.test_character_id,
            "offer_items": [],
            "request_items": []
        }
        
        response = client.post(
            f"/npc/{self.test_npc_id}/barter/initiate",
            json=request_data
        )
        
        assert response.status_code == 404
        assert "NPC not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_complete_barter_success(self, mock_get_service):
        """Test completing barter successfully"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.complete_barter = AsyncMock(return_value=self.mock_complete_response)
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        request_data = {
            "character_id": self.test_character_id,
            "transaction_data": {
                "transaction_id": "barter_123_456",
                "validated": True
            }
        }
        
        response = client.post(
            f"/npc/{self.test_npc_id}/barter/complete",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["transaction_id"] == "barter_123_456"
        
        mock_service.complete_barter.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_complete_barter_validation_error(self, mock_get_service):
        """Test completing barter with validation error"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.complete_barter = AsyncMock(
            side_effect=NpcValidationError("Invalid transaction data")
        )
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        request_data = {
            "character_id": self.test_character_id,
            "transaction_data": {}
        }
        
        response = client.post(
            f"/npc/{self.test_npc_id}/barter/complete",
            json=request_data
        )
        
        assert response.status_code == 400
        assert "Invalid transaction data" in response.json()["detail"]
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_get_npc_barter_status_success(self, mock_get_service):
        """Test getting NPC barter status successfully"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.get_tradeable_items = AsyncMock(return_value=self.mock_inventory_response)
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get(
            f"/npc/{self.test_npc_id}/barter/status",
            params={"character_id": self.test_character_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_items" in data
        assert "available_items" in data
        assert "high_trust_items" in data
        assert "unavailable_items" in data
        assert "relationship_trust" in data
        assert "willing_to_trade" in data
        
        mock_service.get_tradeable_items.assert_called_once_with(
            self.test_npc_id, self.test_character_id
        )
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_get_npc_barter_status_npc_not_found(self, mock_get_service):
        """Test getting barter status when NPC not found"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.get_tradeable_items = AsyncMock(
            side_effect=NpcNotFoundError("NPC not found")
        )
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get(f"/npc/{self.test_npc_id}/barter/status")
        
        assert response.status_code == 404
        assert "NPC not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    @patch('backend.systems.npc.routers.barter_router.get_npc_barter_service')
    async def test_get_npc_barter_status_server_error(self, mock_get_service):
        """Test getting barter status with server error"""
        mock_service = Mock(spec=NPCBarterService)
        mock_service.get_tradeable_items = AsyncMock(
            side_effect=Exception("Database error")
        )
        mock_get_service.return_value = mock_service
        
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get(f"/npc/{self.test_npc_id}/barter/status")
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    
    def test_router_configuration(self):
        """Test router is properly configured"""
        assert router.prefix == "/npc"
        assert "npc-barter" in router.tags
    
    @pytest.mark.asyncio
    async def test_invalid_uuid_handling(self):
        """Test handling of invalid UUID format"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get("/npc/invalid-uuid/barter/inventory")
        
        # FastAPI should return 422 for invalid UUID format
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self):
        """Test handling of missing required fields in requests"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Missing required fields in initiate barter request
        response = client.post(
            f"/npc/{uuid4()}/barter/initiate",
            json={}
        )
        
        # FastAPI should return 422 for validation error
        assert response.status_code == 422 