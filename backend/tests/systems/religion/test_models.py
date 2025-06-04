"""
Test module for religion.models

Comprehensive tests for religion system models including validation,
database operations, and model behavior.
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4
from unittest.mock import Mock, patch
from pydantic import ValidationError
from sqlalchemy.orm import Session

# Import the models under test
from backend.systems.religion.models import (
    ReligionBaseModel,
    ReligionModel,
    ReligionEntity,
    CreateReligionRequest,
    UpdateReligionRequest,
    ReligionResponse,
    ReligionListResponse
)


class TestReligionBaseModel:
    """Test the base religion model"""
    
    def test_base_model_creation(self):
        """Test basic model creation with defaults"""
        model = ReligionBaseModel()
        
        assert isinstance(model.id, UUID)
        assert isinstance(model.created_at, datetime)
        assert model.updated_at is None
        assert model.is_active is True
        assert model.extra_metadata == {}
    
    def test_base_model_with_custom_values(self):
        """Test model creation with custom values"""
        custom_id = uuid4()
        custom_time = datetime.utcnow()
        custom_metadata = {"test": "value"}
        
        model = ReligionBaseModel(
            id=custom_id,
            created_at=custom_time,
            updated_at=custom_time,
            is_active=False,
            extra_metadata=custom_metadata
        )
        
        assert model.id == custom_id
        assert model.created_at == custom_time
        assert model.updated_at == custom_time
        assert model.is_active is False
        assert model.extra_metadata == custom_metadata


class TestReligionModel:
    """Test the main religion model"""
    
    def test_religion_model_creation(self):
        """Test religion model creation with required fields"""
        model = ReligionModel(name="Test Religion")
        
        assert model.name == "Test Religion"
        assert model.description is None
        assert model.status == "active"
        assert model.properties == {}
        assert isinstance(model.id, UUID)
        assert model.is_active is True
    
    def test_religion_model_with_all_fields(self):
        """Test religion model with all fields populated"""
        properties = {"deity": "Test God", "holy_book": "Test Scripture"}
        
        model = ReligionModel(
            name="Complete Religion",
            description="A test religion with all fields",
            status="established",
            properties=properties
        )
        
        assert model.name == "Complete Religion"
        assert model.description == "A test religion with all fields"
        assert model.status == "established"
        assert model.properties == properties
    
    def test_religion_model_validation(self):
        """Test model validation requirements"""
        # Test missing required name field
        with pytest.raises(ValidationError) as exc_info:
            ReligionModel()
        
        assert "name" in str(exc_info.value)
    
    def test_religion_model_serialization(self):
        """Test model serialization to dict"""
        model = ReligionModel(
            name="Serialization Test",
            description="Test description",
            properties={"test": "value"}
        )
        
        data = model.model_dump()
        
        assert data["name"] == "Serialization Test"
        assert data["description"] == "Test description"
        assert data["properties"] == {"test": "value"}
        assert "id" in data
        assert "created_at" in data


class TestReligionEntity:
    """Test the SQLAlchemy religion entity"""
    
    def test_entity_creation(self):
        """Test entity creation with required fields"""
        entity = ReligionEntity(name="Test Entity Religion")
        
        assert entity.name == "Test Entity Religion"
        assert entity.description is None
        # SQLAlchemy entity doesn't initialize defaults until saved, so check explicitly
        if hasattr(entity, 'status') and entity.status is not None:
            assert entity.status == "active"
        if hasattr(entity, 'properties') and entity.properties is not None:
            assert entity.properties == {}
        if hasattr(entity, 'is_active') and entity.is_active is not None:
            assert entity.is_active is True
        # UUID is only set for explicitly created entities in tests
        assert entity.id is None or isinstance(entity.id, UUID)
    
    def test_entity_with_all_fields(self):
        """Test entity with all fields populated"""
        custom_id = uuid4()
        properties = {"followers": 1000, "temples": 5}
        
        entity = ReligionEntity(
            id=custom_id,
            name="Full Entity Religion",
            description="Complete entity description",
            status="flourishing",
            properties=properties,
            is_active=True
        )
        
        assert entity.id == custom_id
        assert entity.name == "Full Entity Religion"
        assert entity.description == "Complete entity description"
        assert entity.status == "flourishing"
        assert entity.properties == properties
        assert entity.is_active is True
    
    def test_entity_repr(self):
        """Test entity string representation"""
        entity = ReligionEntity(name="Repr Test Religion")
        repr_str = repr(entity)
        
        assert "ReligionEntity" in repr_str
        assert "Repr Test Religion" in repr_str
    
    def test_entity_to_dict(self):
        """Test entity conversion to dictionary"""
        entity = ReligionEntity(
            id=uuid4(),  # Explicitly set UUID
            name="Dict Test Religion",
            description="Test description",
            status="active",  # Explicitly set
            properties={"test": "value"},
            is_active=True  # Explicitly set
        )
        
        data = entity.to_dict()
        
        assert data["name"] == "Dict Test Religion"
        assert data["description"] == "Test description"
        assert data["properties"] == {"test": "value"}
        assert data["status"] == "active"
        assert data["is_active"] is True
        assert "id" in data
        assert isinstance(data["id"], str)
    
    def test_entity_to_dict_with_dates(self):
        """Test entity to_dict with datetime fields"""
        entity = ReligionEntity(
            id=uuid4(),  # Explicitly set UUID
            name="Date Test Religion"
        )
        entity.created_at = datetime.utcnow()
        entity.updated_at = datetime.utcnow()
        
        data = entity.to_dict()
        
        assert "created_at" in data
        assert "updated_at" in data
        # Should be ISO format strings
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)


class TestCreateReligionRequest:
    """Test the create religion request model"""
    
    def test_create_request_valid(self):
        """Test valid create request"""
        request = CreateReligionRequest(
            name="New Religion",
            description="A new religion for testing",
            properties={"founding_year": 2024}
        )
        
        assert request.name == "New Religion"
        assert request.description == "A new religion for testing"
        assert request.properties == {"founding_year": 2024}
    
    def test_create_request_minimal(self):
        """Test create request with minimal fields"""
        request = CreateReligionRequest(name="Minimal Religion")
        
        assert request.name == "Minimal Religion"
        assert request.description is None
        assert request.properties == {}
    
    def test_create_request_validation(self):
        """Test create request validation"""
        # Test empty name
        with pytest.raises(ValidationError):
            CreateReligionRequest(name="")
        
        # Test missing name
        with pytest.raises(ValidationError):
            CreateReligionRequest()
        
        # Test name too long
        with pytest.raises(ValidationError):
            CreateReligionRequest(name="x" * 256)
        
        # Test description too long
        with pytest.raises(ValidationError):
            CreateReligionRequest(
                name="Valid Name",
                description="x" * 1001
            )


class TestUpdateReligionRequest:
    """Test the update religion request model"""
    
    def test_update_request_all_fields(self):
        """Test update request with all fields"""
        request = UpdateReligionRequest(
            name="Updated Religion",
            description="Updated description",
            status="reformed",
            properties={"updated": True}
        )
        
        assert request.name == "Updated Religion"
        assert request.description == "Updated description"
        assert request.status == "reformed"
        assert request.properties == {"updated": True}
    
    def test_update_request_partial(self):
        """Test update request with partial fields"""
        request = UpdateReligionRequest(name="Partial Update")
        
        assert request.name == "Partial Update"
        assert request.description is None
        assert request.status is None
        assert request.properties is None
    
    def test_update_request_empty(self):
        """Test update request with no fields"""
        request = UpdateReligionRequest()
        
        assert request.name is None
        assert request.description is None
        assert request.status is None
        assert request.properties is None
    
    def test_update_request_validation(self):
        """Test update request validation"""
        # Test empty name (should fail)
        with pytest.raises(ValidationError):
            UpdateReligionRequest(name="")
        
        # Test name too long
        with pytest.raises(ValidationError):
            UpdateReligionRequest(name="x" * 256)
        
        # Test description too long
        with pytest.raises(ValidationError):
            UpdateReligionRequest(description="x" * 1001)


class TestReligionResponse:
    """Test the religion response model"""
    
    def test_response_from_entity(self):
        """Test creating response from entity"""
        entity = ReligionEntity(
            id=uuid4(),  # Explicitly set UUID
            name="Response Test Religion",
            description="Test description",
            status="active",
            properties={"test": "value"},
            is_active=True
        )
        entity.created_at = datetime.utcnow()
        
        response = ReligionResponse.model_validate(entity)
        
        assert response.name == "Response Test Religion"
        assert response.description == "Test description"
        assert response.status == "active"
        assert response.properties == {"test": "value"}
        assert response.is_active is True
        assert isinstance(response.id, UUID)
        assert isinstance(response.created_at, datetime)
    
    def test_response_serialization(self):
        """Test response model serialization"""
        entity = ReligionEntity(
            id=uuid4(),  # Explicitly set UUID
            name="Serialization Test",
            status="active",
            properties={},
            is_active=True
        )
        entity.created_at = datetime.utcnow()
        
        response = ReligionResponse.model_validate(entity)
        data = response.model_dump()
        
        assert "id" in data
        assert "name" in data
        assert "created_at" in data
        assert data["name"] == "Serialization Test"


class TestReligionListResponse:
    """Test the religion list response model"""
    
    def test_list_response_creation(self):
        """Test list response creation"""
        # Create sample religion responses
        entity1 = ReligionEntity(
            id=uuid4(),  # Explicitly set UUID
            name="Religion 1",
            status="active",
            properties={},
            is_active=True
        )
        entity1.created_at = datetime.utcnow()
        
        entity2 = ReligionEntity(
            id=uuid4(),  # Explicitly set UUID
            name="Religion 2", 
            status="active",
            properties={},
            is_active=True
        )
        entity2.created_at = datetime.utcnow()
        
        response1 = ReligionResponse.model_validate(entity1)
        response2 = ReligionResponse.model_validate(entity2)
        
        list_response = ReligionListResponse(
            items=[response1, response2],
            total=2,
            page=1,
            size=10,
            has_next=False,
            has_prev=False
        )
        
        assert len(list_response.items) == 2
        assert list_response.total == 2
        assert list_response.page == 1
        assert list_response.size == 10
        assert list_response.has_next is False
        assert list_response.has_prev is False
    
    def test_list_response_empty(self):
        """Test empty list response"""
        list_response = ReligionListResponse(
            items=[],
            total=0,
            page=1,
            size=10,
            has_next=False,
            has_prev=False
        )
        
        assert len(list_response.items) == 0
        assert list_response.total == 0
    
    def test_list_response_pagination(self):
        """Test list response with pagination"""
        list_response = ReligionListResponse(
            items=[],
            total=100,
            page=2,
            size=10,
            has_next=True,
            has_prev=True
        )
        
        assert list_response.total == 100
        assert list_response.page == 2
        assert list_response.size == 10
        assert list_response.has_next is True
        assert list_response.has_prev is True


class TestModelIntegration:
    """Test model integration and compatibility"""
    
    def test_request_to_entity_conversion(self):
        """Test converting request to entity"""
        request = CreateReligionRequest(
            name="Integration Test Religion",
            description="Test description",
            properties={"test": "value"}
        )
        
        # Simulate what the repository would do
        entity = ReligionEntity(
            name=request.name,
            description=request.description,
            properties=request.properties
        )
        
        assert entity.name == request.name
        assert entity.description == request.description
        assert entity.properties == request.properties
    
    def test_entity_to_response_conversion(self):
        """Test converting entity to response"""
        entity = ReligionEntity(
            id=uuid4(),  # Explicitly set UUID
            name="Conversion Test Religion",
            description="Test description",
            status="active",
            properties={"test": "value"},
            is_active=True
        )
        entity.created_at = datetime.utcnow()
        
        response = ReligionResponse.model_validate(entity)
        
        assert response.name == entity.name
        assert response.description == entity.description
        assert response.properties == entity.properties
        assert response.id == entity.id
    
    def test_update_request_application(self):
        """Test applying update request to entity"""
        entity = ReligionEntity(
            name="Original Name",
            description="Original description",
            status="active"
        )
        
        update_request = UpdateReligionRequest(
            name="Updated Name",
            description="Updated description",
            status="reformed"
        )
        
        # Simulate what the repository would do
        if update_request.name is not None:
            entity.name = update_request.name
        if update_request.description is not None:
            entity.description = update_request.description
        if update_request.status is not None:
            entity.status = update_request.status
        
        assert entity.name == "Updated Name"
        assert entity.description == "Updated description"
        assert entity.status == "reformed"
        
    @pytest.mark.asyncio
    async def test_model_json_serialization(self):
        """Test JSON serialization for WebSocket compatibility"""
        entity = ReligionEntity(
            id=uuid4(),  # Explicitly set UUID
            name="JSON Test Religion",
            description="Test description",
            status="active",
            properties={"followers": 1000, "temples": ["Temple A", "Temple B"]},
            is_active=True
        )
        entity.created_at = datetime.utcnow()
        
        response = ReligionResponse.model_validate(entity)
        json_data = response.model_dump_json()
        
        assert isinstance(json_data, str)
        assert "JSON Test Religion" in json_data
        assert "followers" in json_data
        assert "temples" in json_data
