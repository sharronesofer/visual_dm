"""
Test module for population.models

Tests the population data models according to Development Bible standards.
Validates data structures, validation logic, and API compliance.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import ValidationError

from backend.infrastructure.models.population.models import (
    PopulationModel,
    PopulationEntity,
    CreatePopulationRequest,
    UpdatePopulationRequest,
    PopulationResponse,
    POIState
)


class TestPopulationModel:
    """Test PopulationModel Pydantic model"""
    
    def test_population_model_creation_success(self):
        """Test successful population model creation"""
        model = PopulationModel(
            name="Test Settlement",
            description="A test settlement",
            status="active"
        )
        
        # Verify required fields are set
        assert model.name == "Test Settlement"
        assert model.description == "A test settlement"
        assert model.status == "active"
        assert model.is_active is True
        assert isinstance(model.id, UUID)
        assert isinstance(model.created_at, datetime)
    
    def test_population_model_minimal_creation(self):
        """Test population model creation with minimal required fields"""
        model = PopulationModel(name="Minimal Settlement")
        
        # Verify defaults are applied correctly
        assert model.name == "Minimal Settlement"
        assert model.description is None
        assert model.status == "active"
        assert model.is_active is True
        assert isinstance(model.properties, dict)
    
    def test_population_model_properties_dictionary(self):
        """Test that properties field properly stores population-specific data"""
        properties = {
            "population_count": 1500,
            "capacity": 2000,
            "growth_rate": 0.02,
            "state": "growing",
            "hidden_attributes": {
                "hidden_ambition": 75,
                "hidden_resilience": 80
            }
        }
        
        model = PopulationModel(
            name="Test Settlement",
            properties=properties
        )
        
        assert model.properties["population_count"] == 1500
        assert model.properties["capacity"] == 2000
        assert model.properties["hidden_attributes"]["hidden_ambition"] == 75


class TestPopulationEntity:
    """Test PopulationEntity SQLAlchemy model"""
    
    def test_population_entity_creation(self):
        """Test population entity creation with proper fields"""
        entity = PopulationEntity(
            name="Test Settlement",
            description="A test settlement for the database",
            status="active",
            properties={"population_count": 1000}
        )
        
        # Verify entity structure matches Development Bible requirements
        assert entity.name == "Test Settlement"
        assert entity.description == "A test settlement for the database"
        assert entity.status == "active"
        assert entity.properties["population_count"] == 1000
        # Note: is_active may be None initially and set by database defaults
        # Note: ID is None until entity is persisted to database
    
    def test_population_entity_to_dict(self):
        """Test entity to dictionary conversion for API responses"""
        entity = PopulationEntity(
            name="Test Settlement",
            description="Test description",
            status="active",
            properties={"population_count": 1500}
        )
        entity.created_at = datetime.utcnow()
        entity.updated_at = datetime.utcnow()
        
        result_dict = entity.to_dict()
        
        # Verify all required fields are present for API compliance
        assert "id" in result_dict
        assert "name" in result_dict
        assert "description" in result_dict
        assert "status" in result_dict
        assert "properties" in result_dict
        assert "created_at" in result_dict
        assert "updated_at" in result_dict
        assert "is_active" in result_dict
        
        # Verify values are correctly converted
        assert result_dict["name"] == "Test Settlement"
        assert result_dict["properties"]["population_count"] == 1500


class TestCreatePopulationRequest:
    """Test population creation request validation"""
    
    def test_create_request_valid_data(self):
        """Test valid population creation request"""
        request = CreatePopulationRequest(
            name="New Settlement",
            description="A newly created settlement",
            properties={"initial_population": 100}
        )
        
        assert request.name == "New Settlement"
        assert request.description == "A newly created settlement"
        assert request.properties["initial_population"] == 100
    
    def test_create_request_name_validation(self):
        """Test name field validation according to business rules"""
        # Test minimum length
        with pytest.raises(ValidationError):
            CreatePopulationRequest(name="")  # Empty name should fail
        
        # Test maximum length (255 characters)
        long_name = "a" * 256
        with pytest.raises(ValidationError):
            CreatePopulationRequest(name=long_name)
        
        # Test valid name
        valid_request = CreatePopulationRequest(name="Valid Settlement Name")
        assert valid_request.name == "Valid Settlement Name"
    
    def test_create_request_optional_fields(self):
        """Test that optional fields work correctly"""
        # Minimal request with only required fields
        minimal_request = CreatePopulationRequest(name="Minimal")
        assert minimal_request.name == "Minimal"
        assert minimal_request.description is None
        assert isinstance(minimal_request.properties, dict)


class TestUpdatePopulationRequest:
    """Test population update request validation"""
    
    def test_update_request_partial_fields(self):
        """Test partial updates with only some fields"""
        request = UpdatePopulationRequest(
            name="Updated Name",
            status="declining"
        )
        
        assert request.name == "Updated Name"
        assert request.status == "declining"
        assert request.description is None  # Not updated
    
    def test_update_request_properties_update(self):
        """Test updating properties field"""
        new_properties = {
            "population_count": 1200,
            "last_war_impact": {"casualties": 50, "date": "2024-01-01"}
        }
        
        request = UpdatePopulationRequest(properties=new_properties)
        assert request.properties["population_count"] == 1200
        assert request.properties["last_war_impact"]["casualties"] == 50


class TestPopulationResponse:
    """Test population response model for API compliance"""
    
    def test_population_response_complete_data(self):
        """Test response with all population data fields"""
        response_data = {
            "id": uuid4(),
            "name": "Test Settlement",
            "description": "Test description",
            "status": "active",
            "properties": {
                "population_count": 1500,
                "capacity": 2000,
                "growth_rate": 0.025,
                "casualties": 25,
                "refugees": 10
            },
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            # Include the computed fields that PopulationResponse expects
            "population_count": 1500,
            "capacity": 2000,
            "growth_rate": 0.025,
            "casualties": 25,
            "refugees": 10
        }
        
        response = PopulationResponse(**response_data)
        
        # Verify basic fields
        assert response.name == "Test Settlement"
        assert response.status == "active"
        
        # Verify computed properties are set correctly
        assert response.population_count == 1500
        assert response.capacity == 2000
        assert response.growth_rate == 0.025
        assert response.casualties == 25
        assert response.refugees == 10
    
    def test_population_response_from_orm_entity(self):
        """Test creating response from ORM entity (common API pattern)"""
        # Mock ORM entity
        class MockEntity:
            def __init__(self):
                self.id = uuid4()
                self.name = "ORM Settlement"
                self.description = "From database"
                self.status = "active"
                self.properties = {
                    "population_count": 800,
                    "state": "growing",
                    "last_war_date": "2024-01-15"
                }
                self.is_active = True
                self.created_at = datetime.utcnow()
                self.updated_at = datetime.utcnow()
        
        entity = MockEntity()
        response = PopulationResponse.from_orm(entity)
        
        # Verify ORM conversion works correctly
        assert response.name == "ORM Settlement"
        assert response.population_count == 800
        assert response.state == "growing"
        assert response.last_war_date == "2024-01-15"


class TestPOIState:
    """Test POI state enum for population management"""
    
    def test_poi_state_values(self):
        """Test that POI states match Development Bible settlement management"""
        # Verify all expected states exist
        assert POIState.TINY == "tiny"
        assert POIState.SMALL == "small"
        assert POIState.MEDIUM == "medium"
        assert POIState.LARGE == "large"
        assert POIState.HUGE == "huge"
        assert POIState.DECLINING == "declining"
        assert POIState.ABANDONED == "abandoned"
    
    def test_poi_state_usage_in_models(self):
        """Test that POI states can be used in population models"""
        # Test that states can be assigned to population properties
        model = PopulationModel(
            name="Settlement",
            properties={"poi_state": POIState.MEDIUM.value}
        )
        
        assert model.properties["poi_state"] == "medium"


class TestPopulationDataStructureCompliance:
    """Test that data structures comply with Development Bible requirements"""
    
    def test_mathematical_model_data_fields(self):
        """Test that models support mathematical calculation data"""
        # Test that all fields needed for mathematical models are supported
        mathematical_properties = {
            # War impact data (Bible requirement)
            "casualties": 150,
            "refugees": 75,
            "last_war_impact": {"severity": "moderate", "duration_days": 45},
            "last_war_date": "2024-01-10",
            
            # Catastrophe impact data (Bible requirement)
            "catastrophe_deaths": 25,
            "catastrophe_displaced": 100,
            "catastrophe_injured": 50,
            "last_catastrophe_impact": {"type": "earthquake", "severity": 0.7},
            "last_catastrophe_date": "2024-02-01",
            
            # Resource shortage data (Bible requirement)
            "shortage_deaths": 10,
            "shortage_migrants": 30,
            "last_shortage_impact": {"resource": "food", "duration": 14},
            
            # Migration data (Bible requirement)
            "last_migration_in": 45,
            "last_migration_out": 20,
            "last_migration_date": "2024-01-20",
            
            # Population dynamics data
            "population_count": 1200,
            "capacity": 1500,
            "growth_rate": 0.018,
            "state": "stable",
            "previous_state": "growing"
        }
        
        model = PopulationModel(
            name="Mathematical Test Settlement",
            properties=mathematical_properties
        )
        
        # Verify all mathematical model data is preserved
        assert model.properties["casualties"] == 150
        assert model.properties["last_war_impact"]["severity"] == "moderate"
        assert model.properties["catastrophe_displaced"] == 100
        assert model.properties["population_count"] == 1200
        assert model.properties["growth_rate"] == 0.018
    
    def test_api_contract_compliance(self):
        """Test that models comply with API contract requirements"""
        # Create a complete population response that matches API contracts
        complete_response = PopulationResponse(
            id=uuid4(),
            name="API Compliant Settlement",
            description="Test for API compliance",
            status="active",
            properties={},
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            
            # Population tracking fields (API contract requirement)
            population_count=1800,
            capacity=2200,
            growth_rate=0.022,
            state="growing",
            
            # Event tracking fields (API contract requirement) 
            last_war_date="2024-01-05",
            last_catastrophe_date="2024-02-10",
            last_migration_date="2024-01-25"
        )
        
        # Verify API compliance
        assert complete_response.population_count == 1800
        assert complete_response.state == "growing"
        assert complete_response.last_war_date == "2024-01-05"
        
        # Verify response can be serialized (critical for API)
        response_dict = complete_response.dict()
        assert "population_count" in response_dict
        assert "last_war_date" in response_dict
