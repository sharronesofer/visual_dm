"""
Test module for religion.schemas

Comprehensive tests for religion system schemas including validation,
serialization, edge cases, and API contract compliance.
"""

import pytest
from datetime import datetime
from uuid import uuid4, UUID
from typing import Dict, Any

from backend.systems.religion.schemas.schemas import (
    ReligionSchema,
    ReligionCreateSchema,
    ReligionUpdateSchema,
    ReligionMembershipSchema,
    ReligionMembershipCreateSchema
)


class TestReligionSchema:
    """Test the main religion schema"""
    
    def test_religion_schema_creation(self):
        """Test religion schema with valid data"""
        religion_id = uuid4()
        now = datetime.now()
        
        schema = ReligionSchema(
            id=religion_id,
            name="Test Religion",
            description="A test religion",
            religion_type="monotheistic",
            tenets=["belief1", "belief2"],
            holy_places=["temple", "shrine"],
            created_at=now,
            updated_at=now,
            is_active=True
        )
        
        assert schema.id == religion_id
        assert schema.name == "Test Religion"
        assert schema.description == "A test religion"
        assert schema.religion_type == "monotheistic"
        assert schema.tenets == ["belief1", "belief2"]
        assert schema.holy_places == ["temple", "shrine"]
        assert schema.created_at == now
        assert schema.updated_at == now
        assert schema.is_active is True
    
    def test_religion_schema_minimal(self):
        """Test religion schema with minimal required fields"""
        religion_id = uuid4()
        now = datetime.now()
        
        schema = ReligionSchema(
            id=religion_id,
            name="Minimal Religion",
            religion_type="animistic",
            created_at=now
        )
        
        assert schema.id == religion_id
        assert schema.name == "Minimal Religion"
        assert schema.description is None
        assert schema.religion_type == "animistic"
        assert schema.tenets == []
        assert schema.holy_places == []
        assert schema.created_at == now
        assert schema.updated_at is None
        assert schema.is_active is True
    
    def test_religion_schema_serialization(self):
        """Test religion schema JSON serialization"""
        religion_id = uuid4()
        now = datetime.now()
        
        schema = ReligionSchema(
            id=religion_id,
            name="Serialization Test",
            religion_type="polytheistic",
            tenets=["many gods", "rituals"],
            created_at=now
        )
        
        data = schema.model_dump()
        
        assert data["id"] == religion_id
        assert data["name"] == "Serialization Test"
        assert data["religion_type"] == "polytheistic"
        assert data["tenets"] == ["many gods", "rituals"]
        assert isinstance(data["created_at"], datetime)
    
    def test_religion_schema_from_dict(self):
        """Test creating religion schema from dictionary"""
        religion_id = uuid4()
        now = datetime.now()
        
        data = {
            "id": religion_id,
            "name": "Dict Religion",
            "religion_type": "shamanistic",
            "created_at": now,
            "tenets": ["spirits", "nature"],
            "holy_places": ["forest", "mountain"]
        }
        
        schema = ReligionSchema(**data)
        
        assert schema.id == religion_id
        assert schema.name == "Dict Religion"
        assert schema.religion_type == "shamanistic"
        assert schema.tenets == ["spirits", "nature"]
        assert schema.holy_places == ["forest", "mountain"]


class TestReligionCreateSchema:
    """Test the religion create schema"""
    
    def test_create_schema_valid(self):
        """Test create schema with valid data"""
        schema = ReligionCreateSchema(
            name="New Religion",
            description="A newly created religion",
            religion_type="monotheistic",
            tenets=["one god", "prayer"],
            holy_places=["cathedral", "monastery"]
        )
        
        assert schema.name == "New Religion"
        assert schema.description == "A newly created religion"
        assert schema.religion_type == "monotheistic"
        assert schema.tenets == ["one god", "prayer"]
        assert schema.holy_places == ["cathedral", "monastery"]
    
    def test_create_schema_minimal(self):
        """Test create schema with minimal required fields"""
        schema = ReligionCreateSchema(
            name="Minimal New Religion",
            religion_type="pantheistic"
        )
        
        assert schema.name == "Minimal New Religion"
        assert schema.description is None
        assert schema.religion_type == "pantheistic"
        assert schema.tenets == []
        assert schema.holy_places == []
    
    def test_create_schema_validation_name_required(self):
        """Test that name is required"""
        with pytest.raises(Exception):  # Pydantic validation error
            ReligionCreateSchema(religion_type="monotheistic")
    
    def test_create_schema_validation_name_length(self):
        """Test name length validation"""
        # Test empty name
        with pytest.raises(Exception):
            ReligionCreateSchema(name="", religion_type="monotheistic")
        
        # Test name too long
        with pytest.raises(Exception):
            ReligionCreateSchema(name="x" * 256, religion_type="monotheistic")
    
    def test_create_schema_validation_description_length(self):
        """Test description length validation"""
        with pytest.raises(Exception):
            ReligionCreateSchema(
                name="Valid Name",
                description="x" * 1001,  # Too long
                religion_type="monotheistic"
            )
    
    def test_create_schema_religion_type_required(self):
        """Test that religion_type is required"""
        with pytest.raises(Exception):
            ReligionCreateSchema(name="Test Religion")


class TestReligionUpdateSchema:
    """Test the religion update schema"""
    
    def test_update_schema_partial(self):
        """Test update schema with partial fields"""
        schema = ReligionUpdateSchema(name="Updated Name")
        
        assert schema.name == "Updated Name"
        assert schema.description is None
        assert schema.religion_type is None
        assert schema.tenets is None
        assert schema.holy_places is None
    
    def test_update_schema_full(self):
        """Test update schema with all fields"""
        schema = ReligionUpdateSchema(
            name="Fully Updated Religion",
            description="Updated description",
            religion_type="reformed_monotheistic",
            tenets=["updated belief", "new practice"],
            holy_places=["new temple", "rebuilt shrine"]
        )
        
        assert schema.name == "Fully Updated Religion"
        assert schema.description == "Updated description"
        assert schema.religion_type == "reformed_monotheistic"
        assert schema.tenets == ["updated belief", "new practice"]
        assert schema.holy_places == ["new temple", "rebuilt shrine"]
    
    def test_update_schema_validation_name_length(self):
        """Test name length validation on update"""
        # Test empty name
        with pytest.raises(Exception):
            ReligionUpdateSchema(name="")
        
        # Test name too long
        with pytest.raises(Exception):
            ReligionUpdateSchema(name="x" * 256)
    
    def test_update_schema_validation_description_length(self):
        """Test description length validation on update"""
        with pytest.raises(Exception):
            ReligionUpdateSchema(description="x" * 1001)
    
    def test_update_schema_empty_allowed(self):
        """Test that empty update schema is allowed"""
        schema = ReligionUpdateSchema()
        
        assert schema.name is None
        assert schema.description is None
        assert schema.religion_type is None
        assert schema.tenets is None
        assert schema.holy_places is None


class TestReligionMembershipSchema:
    """Test the religion membership schema"""
    
    def test_membership_schema_creation(self):
        """Test membership schema with valid data"""
        membership_id = uuid4()
        entity_id = uuid4()
        religion_id = uuid4()
        joined_at = datetime.now()
        
        schema = ReligionMembershipSchema(
            id=membership_id,
            entity_id=entity_id,
            religion_id=religion_id,
            devotion_level=0.75,
            role="priest",
            joined_at=joined_at,
            status="active"
        )
        
        assert schema.id == membership_id
        assert schema.entity_id == entity_id
        assert schema.religion_id == religion_id
        assert schema.devotion_level == 0.75
        assert schema.role == "priest"
        assert schema.joined_at == joined_at
        assert schema.status == "active"
    
    def test_membership_schema_minimal(self):
        """Test membership schema with minimal fields"""
        membership_id = uuid4()
        entity_id = uuid4()
        religion_id = uuid4()
        joined_at = datetime.now()
        
        schema = ReligionMembershipSchema(
            id=membership_id,
            entity_id=entity_id,
            religion_id=religion_id,
            joined_at=joined_at
        )
        
        assert schema.id == membership_id
        assert schema.entity_id == entity_id
        assert schema.religion_id == religion_id
        assert schema.devotion_level == 0.0  # Default from Field
        assert schema.role is None
        assert schema.joined_at == joined_at
        assert schema.status == "active"
    
    def test_membership_schema_devotion_validation(self):
        """Test devotion level validation"""
        membership_id = uuid4()
        entity_id = uuid4()
        religion_id = uuid4()
        joined_at = datetime.now()
        
        # Test valid devotion levels
        valid_schema = ReligionMembershipSchema(
            id=membership_id,
            entity_id=entity_id,
            religion_id=religion_id,
            devotion_level=0.5,
            joined_at=joined_at
        )
        assert valid_schema.devotion_level == 0.5
        
        # Test edge cases (0.0 and 1.0 should be valid)
        edge_schema_low = ReligionMembershipSchema(
            id=membership_id,
            entity_id=entity_id,
            religion_id=religion_id,
            devotion_level=0.0,
            joined_at=joined_at
        )
        assert edge_schema_low.devotion_level == 0.0
        
        edge_schema_high = ReligionMembershipSchema(
            id=membership_id,
            entity_id=entity_id,
            religion_id=religion_id,
            devotion_level=1.0,
            joined_at=joined_at
        )
        assert edge_schema_high.devotion_level == 1.0
        
        # Test invalid devotion levels
        with pytest.raises(Exception):
            ReligionMembershipSchema(
                id=membership_id,
                entity_id=entity_id,
                religion_id=religion_id,
                devotion_level=-0.1,  # Too low
                joined_at=joined_at
            )
        
        with pytest.raises(Exception):
            ReligionMembershipSchema(
                id=membership_id,
                entity_id=entity_id,
                religion_id=religion_id,
                devotion_level=1.1,  # Too high
                joined_at=joined_at
            )


class TestReligionMembershipCreateSchema:
    """Test the religion membership create schema"""
    
    def test_membership_create_schema_creation(self):
        """Test membership create schema with valid data"""
        entity_id = uuid4()
        religion_id = uuid4()
        
        schema = ReligionMembershipCreateSchema(
            entity_id=entity_id,
            religion_id=religion_id,
            devotion_level=0.8,
            role="follower"
        )
        
        assert schema.entity_id == entity_id
        assert schema.religion_id == religion_id
        assert schema.devotion_level == 0.8
        assert schema.role == "follower"
    
    def test_membership_create_schema_minimal(self):
        """Test membership create schema with minimal fields"""
        entity_id = uuid4()
        religion_id = uuid4()
        
        schema = ReligionMembershipCreateSchema(
            entity_id=entity_id,
            religion_id=religion_id
        )
        
        assert schema.entity_id == entity_id
        assert schema.religion_id == religion_id
        assert schema.devotion_level == 0.5  # Default value
        assert schema.role is None
    
    def test_membership_create_schema_devotion_validation(self):
        """Test devotion level validation on create"""
        entity_id = uuid4()
        religion_id = uuid4()
        
        # Test valid devotion levels
        valid_schema = ReligionMembershipCreateSchema(
            entity_id=entity_id,
            religion_id=religion_id,
            devotion_level=0.7
        )
        assert valid_schema.devotion_level == 0.7
        
        # Test invalid devotion levels
        with pytest.raises(Exception):
            ReligionMembershipCreateSchema(
                entity_id=entity_id,
                religion_id=religion_id,
                devotion_level=-0.5  # Too low
            )
        
        with pytest.raises(Exception):
            ReligionMembershipCreateSchema(
                entity_id=entity_id,
                religion_id=religion_id,
                devotion_level=1.5  # Too high
            )
    
    def test_membership_create_schema_required_fields(self):
        """Test that required fields are enforced"""
        entity_id = uuid4()
        religion_id = uuid4()
        
        # Test missing entity_id
        with pytest.raises(Exception):
            ReligionMembershipCreateSchema(religion_id=religion_id)
        
        # Test missing religion_id
        with pytest.raises(Exception):
            ReligionMembershipCreateSchema(entity_id=entity_id)


class TestSchemaIntegration:
    """Test integration between different schema types"""
    
    def test_create_to_main_schema_compatibility(self):
        """Test that create schema data is compatible with main schema"""
        create_data = {
            "name": "Integration Test Religion",
            "description": "Testing schema compatibility",
            "religion_type": "syncretic",
            "tenets": ["multiple sources", "harmony"],
            "holy_places": ["compound temple", "sacred grove"]
        }
        
        create_schema = ReligionCreateSchema(**create_data)
        
        # Simulate what happens after creation
        religion_data = {
            "id": uuid4(),
            "created_at": datetime.now(),
            **create_data
        }
        
        main_schema = ReligionSchema(**religion_data)
        
        assert main_schema.name == create_schema.name
        assert main_schema.description == create_schema.description
        assert main_schema.religion_type == create_schema.religion_type
        assert main_schema.tenets == create_schema.tenets
        assert main_schema.holy_places == create_schema.holy_places
    
    def test_update_schema_partial_application(self):
        """Test applying update schema to existing data"""
        # Original data
        original_data = {
            "id": uuid4(),
            "name": "Original Religion",
            "description": "Original description",
            "religion_type": "original_type",
            "tenets": ["old belief"],
            "holy_places": ["old temple"],
            "created_at": datetime.now()
        }
        
        original_schema = ReligionSchema(**original_data)
        
        # Update data
        update_schema = ReligionUpdateSchema(
            name="Updated Religion",
            tenets=["new belief", "reformed practice"]
        )
        
        # Simulate update application
        updated_data = original_data.copy()
        update_dict = update_schema.model_dump(exclude_none=True)
        updated_data.update(update_dict)
        
        updated_schema = ReligionSchema(**updated_data)
        
        assert updated_schema.name == "Updated Religion"  # Updated
        assert updated_schema.description == original_schema.description  # Unchanged
        assert updated_schema.religion_type == original_schema.religion_type  # Unchanged
        assert updated_schema.tenets == ["new belief", "reformed practice"]  # Updated
        assert updated_schema.holy_places == original_schema.holy_places  # Unchanged
    
    def test_membership_schemas_compatibility(self):
        """Test membership create and main schema compatibility"""
        entity_id = uuid4()
        religion_id = uuid4()
        
        create_data = {
            "entity_id": entity_id,
            "religion_id": religion_id,
            "devotion_level": 0.6,
            "role": "deacon"
        }
        
        create_schema = ReligionMembershipCreateSchema(**create_data)
        
        # Simulate creation
        membership_data = {
            "id": uuid4(),
            "joined_at": datetime.now(),
            "status": "active",
            **create_data
        }
        
        membership_schema = ReligionMembershipSchema(**membership_data)
        
        assert membership_schema.entity_id == create_schema.entity_id
        assert membership_schema.religion_id == create_schema.religion_id
        assert membership_schema.devotion_level == create_schema.devotion_level
        assert membership_schema.role == create_schema.role


class TestSchemaEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_schema_with_unicode_characters(self):
        """Test schemas with unicode characters"""
        schema = ReligionCreateSchema(
            name="神道",  # Japanese
            description="أديان التوحيد",  # Arabic
            religion_type="多神教",  # Chinese
            tenets=["हिंदू धर्म", "ॐ"],  # Hindi
            holy_places=["Θεός", "Ἀθήνη"]  # Greek
        )
        
        assert schema.name == "神道"
        assert "أديان" in schema.description
        assert schema.religion_type == "多神教"
        assert "हिंदू" in schema.tenets[0]
        assert "Θεός" in schema.holy_places
    
    def test_schema_with_special_characters(self):
        """Test schemas with special characters"""
        schema = ReligionCreateSchema(
            name="Religion-X_2.0",
            description="A religion with symbols: @#$%^&*()[]{}|\\:;\"'<>?,./",
            religion_type="neo-traditional",
            tenets=["belief with symbols: !@#", "practice & ritual"],
            holy_places=["Temple-X", "Sacred_Grove_2.0"]
        )
        
        assert "-" in schema.name
        assert "symbols:" in schema.description
        assert "neo-" in schema.religion_type
    
    def test_schema_with_empty_lists(self):
        """Test schemas with empty lists"""
        schema = ReligionCreateSchema(
            name="Minimal Religion",
            religion_type="simple",
            tenets=[],
            holy_places=[]
        )
        
        assert schema.tenets == []
        assert schema.holy_places == []
    
    def test_schema_with_long_lists(self):
        """Test schemas with long lists"""
        long_tenets = [f"tenet_{i}" for i in range(100)]
        long_places = [f"place_{i}" for i in range(50)]
        
        schema = ReligionCreateSchema(
            name="Complex Religion",
            religion_type="complex",
            tenets=long_tenets,
            holy_places=long_places
        )
        
        assert len(schema.tenets) == 100
        assert len(schema.holy_places) == 50
        assert schema.tenets[99] == "tenet_99"
        assert schema.holy_places[49] == "place_49" 