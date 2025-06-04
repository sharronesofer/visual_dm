"""
Test module for inventory.models

Tests the business models according to Development_Bible.md standards.
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import ValidationError

from backend.systems.inventory.models import (
    InventoryBaseModel,
    InventoryModel,
    CreateInventoryRequest,
    UpdateInventoryRequest,
    InventoryResponse,
    InventoryListResponse
)


class TestInventoryBaseModel:
    """Test the base inventory model."""
    
    def test_base_model_creation(self):
        """Test creating base inventory model."""
        model = InventoryBaseModel()
        
        assert isinstance(model.id, UUID)
        assert isinstance(model.created_at, datetime)
        assert model.updated_at is None
        assert model.is_active is True
        assert model.metadata == {}
    
    def test_base_model_with_data(self):
        """Test creating base model with specific data."""
        test_id = uuid4()
        test_time = datetime.utcnow()
        
        model = InventoryBaseModel(
            id=test_id,
            created_at=test_time,
            updated_at=test_time,
            is_active=False,
            metadata={"test": "value"}
        )
        
        assert model.id == test_id
        assert model.created_at == test_time
        assert model.updated_at == test_time
        assert model.is_active is False
        assert model.metadata == {"test": "value"}


class TestInventoryModel:
    """Test the main inventory model."""
    
    def test_inventory_model_creation(self):
        """Test creating inventory model with required fields."""
        inventory = InventoryModel(name="Test Inventory")
        
        assert inventory.name == "Test Inventory"
        assert inventory.description is None
        assert inventory.status == "active"
        assert inventory.properties == {}
        assert isinstance(inventory.id, UUID)
        assert isinstance(inventory.created_at, datetime)
    
    def test_inventory_model_full_data(self):
        """Test creating inventory model with all fields."""
        inventory = InventoryModel(
            name="Full Test Inventory",
            description="Test description",
            status="inactive",
            properties={"capacity": 50, "weight_limit": 100.0}
        )
        
        assert inventory.name == "Full Test Inventory"
        assert inventory.description == "Test description"
        assert inventory.status == "inactive"
        assert inventory.properties == {"capacity": 50, "weight_limit": 100.0}


class TestCreateInventoryRequest:
    """Test the inventory creation request model."""
    
    def test_create_request_minimal(self):
        """Test creating request with minimal data."""
        request = CreateInventoryRequest(name="Test")
        
        assert request.name == "Test"
        assert request.description is None
        assert request.properties == {}
    
    def test_create_request_full(self):
        """Test creating request with all fields."""
        request = CreateInventoryRequest(
            name="Full Test",
            description="Test description",
            properties={"test": "value"}
        )
        
        assert request.name == "Full Test"
        assert request.description == "Test description"
        assert request.properties == {"test": "value"}
    
    def test_create_request_validation(self):
        """Test validation rules for create request."""
        # Test name length validation
        with pytest.raises(ValidationError):
            CreateInventoryRequest(name="")  # Too short
        
        with pytest.raises(ValidationError):
            CreateInventoryRequest(name="x" * 256)  # Too long
        
        # Test description length validation
        with pytest.raises(ValidationError):
            CreateInventoryRequest(
                name="Test",
                description="x" * 1001  # Too long
            )


class TestUpdateInventoryRequest:
    """Test the inventory update request model."""
    
    def test_update_request_empty(self):
        """Test creating empty update request."""
        request = UpdateInventoryRequest()
        
        assert request.name is None
        assert request.description is None
        assert request.status is None
        assert request.properties is None
    
    def test_update_request_partial(self):
        """Test updating only some fields."""
        request = UpdateInventoryRequest(
            name="Updated Name",
            status="inactive"
        )
        
        assert request.name == "Updated Name"
        assert request.description is None
        assert request.status == "inactive"
        assert request.properties is None
    
    def test_update_request_validation(self):
        """Test validation for update request."""
        # Test name length validation
        with pytest.raises(ValidationError):
            UpdateInventoryRequest(name="")  # Too short
        
        with pytest.raises(ValidationError):
            UpdateInventoryRequest(name="x" * 256)  # Too long


class TestInventoryResponse:
    """Test the inventory response model."""
    
    def test_response_creation(self):
        """Test creating response model."""
        test_id = uuid4()
        test_time = datetime.utcnow()
        
        response = InventoryResponse(
            id=test_id,
            name="Test Inventory",
            description="Test description",
            inventory_type="character",
            status="active",
            properties={"test": "value"},
            owner_id=uuid4(),
            player_id=uuid4(),
            max_capacity=50,
            max_weight=100.0,
            current_item_count=0,
            current_weight=0.0,
            encumbrance_level="normal",
            capacity_percentage=0.0,
            weight_percentage=0.0,
            allows_trading=True,
            allows_sorting=True,
            allows_filtering=True,
            default_sort="name",
            available_filters=["type", "rarity"],
            created_at=test_time,
            updated_at=None,
            is_active=True
        )
        
        assert response.id == test_id
        assert response.name == "Test Inventory"
        assert response.description == "Test description"
        assert response.inventory_type == "character"
        assert response.status == "active"
        assert response.properties == {"test": "value"}
        assert response.max_capacity == 50
        assert response.max_weight == 100.0
        assert response.encumbrance_level == "normal"
        assert response.created_at == test_time
        assert response.updated_at is None
        assert response.is_active is True
    
    def test_response_from_model(self):
        """Test creating response from inventory model."""
        inventory = InventoryModel(
            name="Test",
            description="Description",
            inventory_type="character",
            status="active",
            properties={"key": "value"},
            owner_id=uuid4(),
            player_id=uuid4(),
            max_capacity=50,
            max_weight=100.0,
            current_item_count=10,
            current_weight=25.0
        )
        
        # Use the from_model class method
        response = InventoryResponse.from_model(inventory)
        
        assert response.id == inventory.id
        assert response.name == inventory.name
        assert response.description == inventory.description
        assert response.inventory_type == inventory.inventory_type
        assert response.status == inventory.status
        assert response.properties == inventory.properties
        assert response.max_capacity == inventory.max_capacity
        assert response.max_weight == inventory.max_weight
        assert response.current_item_count == inventory.current_item_count
        assert response.current_weight == inventory.current_weight
        assert response.encumbrance_level == inventory.get_encumbrance_level()
        assert response.capacity_percentage == inventory.get_capacity_percentage()
        assert response.weight_percentage == inventory.get_weight_percentage()


class TestInventoryListResponse:
    """Test the inventory list response model."""
    
    def test_list_response_creation(self):
        """Test creating list response."""
        test_id = uuid4()
        test_time = datetime.utcnow()
        
        inventory_response = InventoryResponse(
            id=test_id,
            name="Test",
            description=None,
            inventory_type="character",
            status="active",
            properties={},
            owner_id=uuid4(),
            player_id=uuid4(),
            max_capacity=50,
            max_weight=100.0,
            current_item_count=0,
            current_weight=0.0,
            encumbrance_level="normal",
            capacity_percentage=0.0,
            weight_percentage=0.0,
            allows_trading=True,
            allows_sorting=True,
            allows_filtering=True,
            default_sort="name",
            available_filters=[],
            created_at=test_time,
            updated_at=None,
            is_active=True
        )
        
        list_response = InventoryListResponse(
            items=[inventory_response],
            total=1,
            page=1,
            size=50,
            has_next=False,
            has_prev=False
        )
        
        assert len(list_response.items) == 1
        assert list_response.items[0] == inventory_response
        assert list_response.total == 1
        assert list_response.page == 1
        assert list_response.size == 50
        assert list_response.has_next is False
        assert list_response.has_prev is False
    
    def test_list_response_pagination_flags(self):
        """Test pagination flags calculation."""
        # Test has_next = True case
        list_response = InventoryListResponse(
            items=[],
            total=100,
            page=1,
            size=50,
            has_next=True,  # 50 < 100, so has next
            has_prev=False  # page 1, so no prev
        )
        
        assert list_response.has_next is True
        assert list_response.has_prev is False
        
        # Test has_prev = True case
        list_response = InventoryListResponse(
            items=[],
            total=100,
            page=3,
            size=50,
            has_next=False,  # page 3 * 50 >= 100, so no next
            has_prev=True   # page > 1, so has prev
        )
        
        assert list_response.has_next is False
        assert list_response.has_prev is True


# Model tests focus on:
# - Data validation and constraints
# - Field requirements and defaults
# - Serialization and deserialization
# - Business rule compliance
