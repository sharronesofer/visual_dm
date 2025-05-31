"""
Tests for event_base system models
"""

import pytest
from datetime import datetime
from uuid import uuid4

# REMOVED: deprecated event_base import
    Event_BaseModel,
    Event_BaseEntity,
    CreateEvent_BaseRequest,
    UpdateEvent_BaseRequest,
    Event_BaseResponse
)


class TestEvent_BaseModel:
    """Test event_base model validation"""
    
    def test_create_valid_event_base_model(self):
        """Test creating valid event_base model"""
        model = Event_BaseModel(
            name="Test Event_Base",
            description="Test description"
        )
        assert model.name == "Test Event_Base"
        assert model.description == "Test description"
        assert model.is_active is True

    def test_event_base_model_defaults(self):
        """Test event_base model defaults"""
        model = Event_BaseModel(name="Test")
        assert model.status == "active"
        assert model.is_active is True
        assert model.properties == {}


class TestEvent_BaseEntity:
    """Test event_base SQLAlchemy entity"""
    
    def test_entity_creation(self):
        """Test entity creation"""
        entity = Event_BaseEntity(
            name="Test Entity",
            description="Test description"
        )
        assert entity.name == "Test Entity"
        assert entity.description == "Test description"

    def test_entity_to_dict(self):
        """Test entity to_dict method"""
        entity = Event_BaseEntity(
            id=uuid4(),
            name="Test Entity",
            description="Test description",
            status="active",
            is_active=True,
            created_at=datetime.utcnow()
        )
        result = entity.to_dict()
        assert result["name"] == "Test Entity"
        assert result["description"] == "Test description"
        assert result["status"] == "active"
        assert result["is_active"] is True


class TestCreateEvent_BaseRequest:
    """Test creation request validation"""
    
    def test_valid_creation_request(self):
        """Test valid creation request"""
        request = CreateEvent_BaseRequest(
            name="Test Event_Base",
            description="Test description"
        )
        assert request.name == "Test Event_Base"
        assert request.description == "Test description"

    def test_creation_request_validation(self):
        """Test creation request validation"""
        with pytest.raises(ValueError):
            CreateEvent_BaseRequest(name="")  # Empty name should fail


class TestUpdateEvent_BaseRequest:
    """Test update request validation"""
    
    def test_valid_update_request(self):
        """Test valid update request"""
        request = UpdateEvent_BaseRequest(
            name="Updated Name",
            description="Updated description"
        )
        assert request.name == "Updated Name"
        assert request.description == "Updated description"

    def test_partial_update_request(self):
        """Test partial update request"""
        request = UpdateEvent_BaseRequest(name="Updated Name")
        assert request.name == "Updated Name"
        assert request.description is None
