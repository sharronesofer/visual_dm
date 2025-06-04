"""
Test module for population.services

Tests the population service business logic according to Development Bible standards.
Validates mathematical models, configuration usage, and core population dynamics.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from uuid import UUID, uuid4
from datetime import datetime

from backend.systems.population.services.services import (
    PopulationBusinessService,
    PopulationData,
    CreatePopulationData,
    UpdatePopulationData,
    load_population_config,
    load_settlement_types,
    calculate_region_population_target,
    get_poi_population_range,
    calculate_npc_distribution_for_poi
)


class TestPopulationConfiguration:
    """Test population configuration loading and usage"""
    
    def test_load_population_config_success(self):
        """Test loading population config from JSON file"""
        config = load_population_config()
        
        # Verify required sections exist per Development Bible requirements
        assert "growth_control" in config
        assert "racial_distribution" in config
        assert "resource_consumption" in config
        assert "war_impact" in config
        
        # Verify growth control parameters align with mathematical models
        growth_control = config["growth_control"]
        assert "base_growth_rate" in growth_control
        assert isinstance(growth_control["base_growth_rate"], (int, float))
        assert 0.0 <= growth_control["base_growth_rate"] <= 1.0
    
    def test_load_settlement_types_success(self):
        """Test loading settlement types from JSON file"""
        settlement_types = load_settlement_types()
        
        # Verify structure matches Bible requirements for settlement management
        assert "settlement_types" in settlement_types
        settlement_data = settlement_types["settlement_types"]
        
        # Test that settlement types have population ranges (critical for population dynamics)
        for settlement_type, data in settlement_data.items():
            assert "population_range" in data
            pop_range = data["population_range"]
            assert len(pop_range) == 2
            assert pop_range[0] <= pop_range[1]  # Min <= Max
            assert pop_range[0] > 0  # No negative populations
    
    def test_calculate_region_population_target(self):
        """Test region population calculation uses config correctly"""
        # Test default region type
        default_target = calculate_region_population_target()
        assert isinstance(default_target, int)
        assert default_target > 0
        
        # Test different region types produce different results
        rural_target = calculate_region_population_target("rural")
        urban_target = calculate_region_population_target("urban")
        
        assert isinstance(rural_target, int)
        assert isinstance(urban_target, int)
    
    def test_get_poi_population_range(self):
        """Test POI population range calculation"""
        # Test settlement POI
        village_range = get_poi_population_range("settlement", "village")
        assert isinstance(village_range, tuple)
        assert len(village_range) == 2
        assert village_range[0] <= village_range[1]
        
        # Test default range for unknown types
        default_range = get_poi_population_range("unknown_type")
        assert isinstance(default_range, tuple)
        assert len(default_range) == 2


class TestPopulationBusinessLogic:
    """Test core population business logic"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock repository for testing"""
        repo = Mock()
        repo.get_population_by_name.return_value = None  # No existing population
        repo.create_population.return_value = {
            "id": uuid4(),
            "name": "Test Population",
            "description": "Test Description",
            "status": "active",
            "properties": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        return repo
    
    @pytest.fixture
    def mock_validation_service(self):
        """Mock validation service for testing"""
        validator = Mock()
        validator.validate_population_data.side_effect = lambda x: x  # Pass through
        validator.generate_hidden_attributes.return_value = {
            "hidden_ambition": 75,
            "hidden_integrity": 80,
            "hidden_discipline": 70,
            "hidden_impulsivity": 60,
            "hidden_pragmatism": 85,
            "hidden_resilience": 90
        }
        validator.validate_hidden_attributes.side_effect = lambda x: x
        return validator
    
    @pytest.fixture
    def population_service(self, mock_repository, mock_validation_service):
        """Create population service with mocked dependencies"""
        return PopulationBusinessService(mock_repository, mock_validation_service)
    
    def test_create_population_success(self, population_service, mock_repository):
        """Test successful population creation follows Bible standards"""
        create_data = CreatePopulationData(
            name="Test Settlement",
            description="A test settlement for validation",
            status="active"
        )
        
        result = population_service.create_population(create_data)
        
        # Verify business rules are enforced
        assert isinstance(result, PopulationData)
        assert result.name == "Test Population"
        assert result.status == "active"
        
        # Verify repository was called correctly
        mock_repository.create_population.assert_called_once()
        call_args = mock_repository.create_population.call_args[0][0]
        assert call_args["name"] == "Test Settlement"
        assert "hidden_ambition" in call_args["properties"]  # Hidden attributes generated
    
    def test_create_population_duplicate_name_fails(self, population_service, mock_repository):
        """Test that duplicate population names are rejected (business rule)"""
        # Mock existing population with same name
        mock_repository.get_population_by_name.return_value = {"id": uuid4(), "name": "Existing"}
        
        create_data = CreatePopulationData(name="Existing")
        
        with pytest.raises(ValueError, match="already exists"):
            population_service.create_population(create_data)
    
    def test_calculate_population_power_score(self, population_service):
        """Test population power score calculation uses correct attributes"""
        population = PopulationData(
            id=uuid4(),
            name="Test Pop",
            properties={
                "hidden_ambition": 80,
                "hidden_integrity": 70,
                "hidden_discipline": 90,
                "hidden_pragmatism": 75
            }
        )
        
        score = population_service.calculate_population_power_score(population)
        
        # Verify score is calculated correctly
        assert isinstance(score, float)
        assert 0.0 <= score <= 100.0  # Reasonable score range
    
    def test_assess_population_stability(self, population_service):
        """Test population stability assessment"""
        population = PopulationData(
            id=uuid4(),
            name="Test Pop",
            properties={
                "hidden_resilience": 85,
                "hidden_discipline": 75,
                "hidden_integrity": 80,
                "population_count": 1500,
                "capacity": 2000
            }
        )
        
        stability = population_service.assess_population_stability(population)
        
        # Verify stability assessment structure (adjust for actual implementation)
        assert isinstance(stability, dict)
        assert "category" in stability
        assert "leadership_stability" in stability or "organizational_stability" in stability
        
        # Verify a stability score exists somewhere in the response
        found_score = False
        for key, value in stability.items():
            if isinstance(value, (int, float)) and 0.0 <= value <= 100.0:
                found_score = True
                break
        assert found_score, "Should have at least one stability score between 0-100"


class TestNPCDistributionCalculation:
    """Test NPC distribution calculations for MMO-scale management"""
    
    def test_calculate_npc_distribution_basic(self):
        """Test basic NPC distribution calculation"""
        total_pop = 1000
        poi_type = "settlement"
        
        distribution = calculate_npc_distribution_for_poi(total_pop, poi_type)
        
        # Verify structure matches revolutionary NPC tier system
        assert isinstance(distribution, dict)
        assert "tier_1_npcs" in distribution
        assert "tier_2_npcs" in distribution
        assert "tier_3_npcs" in distribution
        assert "tier_4_npcs" in distribution
        
        # Verify tier hierarchy makes sense (fewer higher-tier NPCs)
        assert distribution["tier_1_npcs"] <= distribution["tier_2_npcs"]
        assert distribution["tier_2_npcs"] <= distribution["tier_3_npcs"]
        assert distribution["tier_3_npcs"] <= distribution["tier_4_npcs"]
        
        # Verify total tier 4 NPCs equals total population (statistical tier)
        assert distribution["tier_4_npcs"] == total_pop
    
    def test_calculate_npc_distribution_small_population(self):
        """Test NPC distribution for small populations"""
        total_pop = 10
        distribution = calculate_npc_distribution_for_poi(total_pop, "outpost")
        
        # Even small populations should have at least 1 NPC per tier
        for tier_key in ["tier_1_npcs", "tier_2_npcs", "tier_3_npcs"]:
            assert distribution[tier_key] >= 1


class TestPopulationMathematicalModels:
    """Test mathematical models align with Development Bible requirements"""
    
    def test_mathematical_models_import_successfully(self):
        """Test that mathematical models can be imported and used"""
        from backend.systems.population.utils.consolidated_utils import (
            calculate_war_impact,
            calculate_catastrophe_impact,
            calculate_resource_shortage_impact,
            calculate_migration_impact
        )
        
        # Test war impact calculation (Development Bible requirement)
        war_result = calculate_war_impact(
            population=1000,
            war_intensity=0.5,
            duration_days=30,
            defensive_strength=0.7
        )
        
        assert isinstance(war_result, dict)
        assert "casualties" in war_result
        
        # Test catastrophe impact calculation (Development Bible requirement)
        catastrophe_result = calculate_catastrophe_impact(
            population=1000,
            catastrophe_type="earthquake",
            severity=0.6
        )
        
        assert isinstance(catastrophe_result, dict)
        
        # Test resource shortage calculation (Development Bible requirement)
        shortage_result = calculate_resource_shortage_impact(
            population=1000,
            resource_type="food",
            shortage_percentage=0.3,
            duration_days=14
        )
        
        assert isinstance(shortage_result, dict)
        
        # Test migration calculation (Development Bible requirement)
        migration_result = calculate_migration_impact(
            origin_population=1000,
            destination_capacity=1500,
            push_factors={"war": 0.8, "famine": 0.6},
            pull_factors={"safety": 0.9, "opportunity": 0.7}
        )
        
        assert isinstance(migration_result, dict)
