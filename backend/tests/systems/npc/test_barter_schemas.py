"""
Test NPC Barter Schemas

Tests for NPC bartering request/response schemas.
"""

import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime

# Import schemas from infrastructure
from backend.infrastructure.systems.npc.schemas.barter_schemas import (
    BarterItemRequest,
    BarterInitiateRequest,
    BarterCompleteRequest,
    BarterItemResponse,
    BarterInventoryResponse,
    BarterPriceResponse,
    BarterValidationResponse,
    BarterInitiateResponse,
    BarterTransactionLog,
    BarterCompleteResponse,
    BarterErrorResponse,
    BarterItem
)


class TestBarterItemRequest:
    """Test BarterItemRequest schema"""
    
    def test_valid_item_request(self):
        """Test creating valid item request"""
        data = {
            "id": "item123",
            "name": "Sword",
            "quantity": 2,
            "value": 50.0
        }
        
        item = BarterItemRequest(**data)
        
        assert item.id == "item123"
        assert item.name == "Sword"
        assert item.quantity == 2
        assert item.value == 50.0
    
    def test_item_request_defaults(self):
        """Test item request with default values"""
        item = BarterItemRequest()
        
        assert item.id is None
        assert item.name is None
        assert item.quantity == 1
        assert item.value == 0
    
    def test_item_request_validation_quantity(self):
        """Test quantity validation"""
        with pytest.raises(ValidationError) as exc_info:
            BarterItemRequest(quantity=0)
        
        assert "greater than or equal to 1" in str(exc_info.value)
    
    def test_item_request_validation_value(self):
        """Test value validation"""
        with pytest.raises(ValidationError) as exc_info:
            BarterItemRequest(value=-10)
        
        assert "greater than or equal to 0" in str(exc_info.value)


class TestBarterInitiateRequest:
    """Test BarterInitiateRequest schema"""
    
    def test_valid_initiate_request(self):
        """Test creating valid initiate request"""
        data = {
            "character_id": "char123",
            "offer_items": [
                {"name": "Gold", "value": 100, "quantity": 1}
            ],
            "request_items": [
                {"id": "item1", "name": "Sword", "quantity": 1}
            ]
        }
        
        request = BarterInitiateRequest(**data)
        
        assert request.character_id == "char123"
        assert len(request.offer_items) == 1
        assert len(request.request_items) == 1
        assert request.offer_items[0].name == "Gold"
        assert request.request_items[0].id == "item1"
    
    def test_initiate_request_missing_character_id(self):
        """Test validation with missing character_id"""
        data = {
            "offer_items": [],
            "request_items": []
        }
        
        with pytest.raises(ValidationError) as exc_info:
            BarterInitiateRequest(**data)
        
        assert "character_id" in str(exc_info.value)
    
    def test_initiate_request_missing_items(self):
        """Test validation with missing items"""
        data = {
            "character_id": "char123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            BarterInitiateRequest(**data)
        
        assert "offer_items" in str(exc_info.value) or "request_items" in str(exc_info.value)


class TestBarterCompleteRequest:
    """Test BarterCompleteRequest schema"""
    
    def test_valid_complete_request(self):
        """Test creating valid complete request"""
        data = {
            "character_id": "char123",
            "transaction_data": {
                "offer_items": [{"name": "Gold", "value": 100}],
                "request_items": [{"name": "Sword", "value": 50}],
                "total_value": 50
            }
        }
        
        request = BarterCompleteRequest(**data)
        
        assert request.character_id == "char123"
        assert "offer_items" in request.transaction_data
        assert "request_items" in request.transaction_data
    
    def test_complete_request_missing_fields(self):
        """Test validation with missing fields"""
        with pytest.raises(ValidationError):
            BarterCompleteRequest(character_id="char123")


class TestBarterItemResponse:
    """Test BarterItemResponse schema"""
    
    def test_valid_item_response(self):
        """Test creating valid item response"""
        data = {
            "id": "item123",
            "name": "Sword",
            "description": "A sharp blade",
            "value": 50.0,
            "item_type": "weapon",
            "tier": "always_available",
            "can_trade": True,
            "reason": "Available for trade",
            "price": 45.0
        }
        
        response = BarterItemResponse(**data)
        
        assert response.id == "item123"
        assert response.name == "Sword"
        assert response.description == "A sharp blade"
        assert response.value == 50.0
        assert response.item_type == "weapon"
        assert response.tier == "always_available"
        assert response.can_trade is True
        assert response.reason == "Available for trade"
        assert response.price == 45.0
    
    def test_item_response_minimal(self):
        """Test item response with minimal required fields"""
        data = {
            "name": "Bread",
            "value": 2.0,
            "tier": "always_available",
            "can_trade": True
        }
        
        response = BarterItemResponse(**data)
        
        assert response.name == "Bread"
        assert response.value == 2.0
        assert response.tier == "always_available"
        assert response.can_trade is True
        assert response.id is None
        assert response.description is None


class TestBarterInventoryResponse:
    """Test BarterInventoryResponse schema"""
    
    def test_valid_inventory_response(self):
        """Test creating valid inventory response"""
        data = {
            "npc_id": str(uuid4()),
            "npc_name": "Test Merchant",
            "relationship_trust": 0.5,
            "total_items": 3,
            "items": {
                "always_available": [
                    {
                        "name": "Bread",
                        "value": 2.0,
                        "tier": "always_available",
                        "can_trade": True
                    }
                ],
                "high_trust_required": [],
                "not_available": []
            }
        }
        
        response = BarterInventoryResponse(**data)
        
        assert response.npc_name == "Test Merchant"
        assert response.relationship_trust == 0.5
        assert response.total_items == 3
        assert "always_available" in response.items
        assert len(response.items["always_available"]) == 1
    
    def test_inventory_response_missing_fields(self):
        """Test validation with missing required fields"""
        with pytest.raises(ValidationError):
            BarterInventoryResponse(npc_id="123")


class TestBarterPriceResponse:
    """Test BarterPriceResponse schema"""
    
    def test_valid_price_response(self):
        """Test creating valid price response"""
        data = {
            "item_id": "item123",
            "item_name": "Sword",
            "can_trade": True,
            "price": 45.0,
            "base_value": 50.0,
            "tier": "always_available",
            "relationship_trust": 0.5,
            "reason": "Available for trade",
            "price_factors": {
                "tier_multiplier": 1.0,
                "relationship_discount": 0.1
            }
        }
        
        response = BarterPriceResponse(**data)
        
        assert response.item_id == "item123"
        assert response.item_name == "Sword"
        assert response.can_trade is True
        assert response.price == 45.0
        assert response.base_value == 50.0
        assert response.tier == "always_available"
        assert response.relationship_trust == 0.5
        assert "tier_multiplier" in response.price_factors
    
    def test_price_response_cannot_trade(self):
        """Test price response for non-tradeable item"""
        data = {
            "item_id": "item123",
            "can_trade": False,
            "reason": "Item is equipped"
        }
        
        response = BarterPriceResponse(**data)
        
        assert response.item_id == "item123"
        assert response.can_trade is False
        assert response.reason == "Item is equipped"
        assert response.price is None


class TestBarterValidationResponse:
    """Test BarterValidationResponse schema"""
    
    def test_valid_validation_response(self):
        """Test creating valid validation response"""
        data = {
            "item_id": "item123",
            "valid": True,
            "reason": "Item available",
            "price": 45.0,
            "tier": "always_available"
        }
        
        response = BarterValidationResponse(**data)
        
        assert response.item_id == "item123"
        assert response.valid is True
        assert response.reason == "Item available"
        assert response.price == 45.0
        assert response.tier == "always_available"
    
    def test_validation_response_invalid(self):
        """Test validation response for invalid item"""
        data = {
            "item_id": "item123",
            "valid": False,
            "reason": "Item not found"
        }
        
        response = BarterValidationResponse(**data)
        
        assert response.item_id == "item123"
        assert response.valid is False
        assert response.reason == "Item not found"
        assert response.price is None
        assert response.tier is None


class TestBarterInitiateResponse:
    """Test BarterInitiateResponse schema"""
    
    def test_valid_initiate_response(self):
        """Test creating valid initiate response"""
        data = {
            "npc_id": str(uuid4()),
            "character_id": "char123",
            "trade_acceptable": True,
            "value_ratio": 0.9,
            "required_ratio": 0.8,
            "total_offer_value": 100.0,
            "total_request_value": 50.0,
            "relationship_trust": 0.5,
            "item_validations": [
                {
                    "item_id": "item1",
                    "valid": True,
                    "price": 45.0
                }
            ],
            "message": "Trade acceptable"
        }
        
        response = BarterInitiateResponse(**data)
        
        assert response.character_id == "char123"
        assert response.trade_acceptable is True
        assert response.value_ratio == 0.9
        assert response.required_ratio == 0.8
        assert response.total_offer_value == 100.0
        assert response.total_request_value == 50.0
        assert response.relationship_trust == 0.5
        assert len(response.item_validations) == 1
        assert response.message == "Trade acceptable"
    
    def test_initiate_response_unacceptable_trade(self):
        """Test initiate response for unacceptable trade"""
        data = {
            "npc_id": str(uuid4()),
            "character_id": "char123",
            "trade_acceptable": False,
            "value_ratio": 0.5,
            "required_ratio": 0.8,
            "total_offer_value": 50.0,
            "total_request_value": 100.0,
            "relationship_trust": 0.3,
            "item_validations": [],
            "message": "Offer too low"
        }
        
        response = BarterInitiateResponse(**data)
        
        assert response.trade_acceptable is False
        assert response.value_ratio == 0.5
        assert response.message == "Offer too low"


class TestBarterTransactionLog:
    """Test BarterTransactionLog schema"""
    
    def test_valid_transaction_log(self):
        """Test creating valid transaction log"""
        data = {
            "timestamp": "2023-01-01T00:00:00",
            "character_id": "char123",
            "items_given": [{"name": "Gold", "value": 100}],
            "items_received": [{"name": "Sword", "value": 50}],
            "value_exchanged": 50.0
        }
        
        log = BarterTransactionLog(**data)
        
        assert log.timestamp == "2023-01-01T00:00:00"
        assert log.character_id == "char123"
        assert len(log.items_given) == 1
        assert len(log.items_received) == 1
        assert log.value_exchanged == 50.0
    
    def test_transaction_log_missing_fields(self):
        """Test validation with missing required fields"""
        with pytest.raises(ValidationError):
            BarterTransactionLog(character_id="char123")


class TestBarterCompleteResponse:
    """Test BarterCompleteResponse schema"""
    
    def test_valid_complete_response(self):
        """Test creating valid complete response"""
        transaction_log_data = {
            "timestamp": "2023-01-01T00:00:00",
            "character_id": "char123",
            "items_given": [{"name": "Gold", "value": 100}],
            "items_received": [{"name": "Sword", "value": 50}],
            "value_exchanged": 50.0
        }
        
        data = {
            "success": True,
            "transaction_id": "barter_123_456",
            "npc_id": str(uuid4()),
            "character_id": "char123",
            "relationship_improvement": 0.05,
            "message": "Trade completed successfully",
            "transaction_log": transaction_log_data
        }
        
        response = BarterCompleteResponse(**data)
        
        assert response.success is True
        assert response.transaction_id == "barter_123_456"
        assert response.character_id == "char123"
        assert response.relationship_improvement == 0.05
        assert response.message == "Trade completed successfully"
        assert response.transaction_log.character_id == "char123"
    
    def test_complete_response_failure(self):
        """Test complete response for failed transaction"""
        transaction_log_data = {
            "timestamp": "2023-01-01T00:00:00",
            "character_id": "char123",
            "items_given": [],
            "items_received": [],
            "value_exchanged": 0.0
        }
        
        data = {
            "success": False,
            "transaction_id": "barter_123_456",
            "npc_id": str(uuid4()),
            "character_id": "char123",
            "relationship_improvement": 0.0,
            "message": "Trade failed",
            "transaction_log": transaction_log_data
        }
        
        response = BarterCompleteResponse(**data)
        
        assert response.success is False
        assert response.message == "Trade failed"
        assert response.relationship_improvement == 0.0


class TestBarterErrorResponse:
    """Test BarterErrorResponse schema"""
    
    def test_valid_error_response(self):
        """Test creating valid error response"""
        data = {
            "error": "ValidationError",
            "message": "Invalid item data",
            "details": {
                "field": "item_id",
                "issue": "Item not found"
            }
        }
        
        response = BarterErrorResponse(**data)
        
        assert response.error == "ValidationError"
        assert response.message == "Invalid item data"
        assert response.details["field"] == "item_id"
        assert response.details["issue"] == "Item not found"
    
    def test_error_response_minimal(self):
        """Test error response with minimal fields"""
        data = {
            "error": "NotFound",
            "message": "NPC not found"
        }
        
        response = BarterErrorResponse(**data)
        
        assert response.error == "NotFound"
        assert response.message == "NPC not found"
        assert response.details is None
    
    def test_error_response_missing_fields(self):
        """Test validation with missing required fields"""
        with pytest.raises(ValidationError):
            BarterErrorResponse(error="TestError")


class TestSchemaIntegration:
    """Test schema integration and serialization"""
    
    def test_schema_serialization(self):
        """Test that schemas can be serialized to JSON"""
        item = BarterItemRequest(
            id="item123",
            name="Sword",
            quantity=1,
            value=50.0
        )
        
        # Test model_dump (Pydantic v2)
        data = item.model_dump()
        
        assert data["id"] == "item123"
        assert data["name"] == "Sword"
        assert data["quantity"] == 1
        assert data["value"] == 50.0
    
    def test_schema_deserialization(self):
        """Test that schemas can be created from dictionaries"""
        data = {
            "id": "item123",
            "name": "Sword",
            "quantity": 1,
            "value": 50.0
        }
        
        item = BarterItemRequest(**data)
        
        assert item.id == "item123"
        assert item.name == "Sword"
        assert item.quantity == 1
        assert item.value == 50.0
    
    def test_nested_schema_validation(self):
        """Test validation of nested schemas"""
        data = {
            "character_id": "char123",
            "offer_items": [
                {"name": "Gold", "value": 100, "quantity": 1}
            ],
            "request_items": [
                {"id": "item1", "name": "Sword", "quantity": 0}  # Invalid quantity
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            BarterInitiateRequest(**data)
        
        assert "quantity" in str(exc_info.value) 