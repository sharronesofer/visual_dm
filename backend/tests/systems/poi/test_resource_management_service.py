from backend.systems.poi.models import PointOfInterest
from backend.systems.economy.models import Resource
from backend.systems.poi.models import PointOfInterest
from backend.systems.economy.models import Resource
from backend.systems.poi.models import PointOfInterest
from backend.systems.economy.models import Resource
from backend.systems.poi.models import PointOfInterest
from backend.systems.economy.models import Resource
from backend.systems.poi.models import PointOfInterest
from backend.systems.economy.models import Resource
from backend.systems.poi.models import PointOfInterest
from backend.systems.economy.models import Resource
from typing import Any
from typing import Type
"""
Tests for backend.systems.poi.services.resource_management_service

This module contains tests for POI resource management functionality.
"""

import pytest
from unittest.mock import Mock
from typing import Dict, Any

from backend.systems.poi.services.resource_management_service import ResourceManagementService
from backend.systems.poi.models import PointOfInterest, POIType, POIState


class TestResourceManagementService: pass
    """Tests for POI resource management service."""

    @pytest.fixture
    def sample_poi(self): pass
        """Create a sample POI for testing."""
        poi = Mock(spec=PointOfInterest)
        poi.id = "poi_1"
        poi.name = "Test Village"
        poi.poi_type = POIType.VILLAGE
        poi.population = 500
        poi.current_state = POIState.NORMAL
        poi.tags = []
        poi.resources = {}
        return poi

    def test_base_production_rates_constants(self): pass
        """Test that base production rates are properly defined."""
        rates = ResourceManagementService.BASE_PRODUCTION_RATES
        
        # Check required POI types exist
        required_types = [POIType.CITY, POIType.TOWN, POIType.VILLAGE, 
                         POIType.OUTPOST, POIType.FARM, POIType.MINE, POIType.CAMP]
        for poi_type in required_types: pass
            assert poi_type in rates
            assert isinstance(rates[poi_type], dict)

    def test_base_consumption_rates_constants(self): pass
        """Test that base consumption rates are properly defined."""
        rates = ResourceManagementService.BASE_CONSUMPTION_RATES
        
        # Check essential resources exist
        essential_resources = ["food", "water"]
        for resource in essential_resources: pass
            assert resource in rates
            assert rates[resource] > 0

    def test_resource_types_constants(self): pass
        """Test that resource types are properly defined."""
        types = ResourceManagementService.RESOURCE_TYPES
        
        # Check essential resources exist
        essential_resources = ["food", "water", "wood", "stone"]
        for resource in essential_resources: pass
            assert resource in types
            assert "category" in types[resource]
            assert "stackable" in types[resource]
            assert "perishable" in types[resource]

    def test_calculate_production_basic(self, sample_poi): pass
        """Test basic production calculation."""
        production = ResourceManagementService.calculate_production(sample_poi)
        
        assert isinstance(production, dict)
        # Village should produce food, gold, and goods
        expected_resources = ["food", "gold", "goods"]
        for resource in expected_resources: pass
            assert resource in production
            assert production[resource] > 0

    def test_calculate_production_zero_population(self, sample_poi): pass
        """Test production calculation with zero population."""
        sample_poi.population = 0
        
        production = ResourceManagementService.calculate_production(sample_poi)
        
        assert production == {}

    def test_calculate_consumption_basic(self, sample_poi): pass
        """Test basic consumption calculation."""
        consumption = ResourceManagementService.calculate_consumption(sample_poi)
        
        assert isinstance(consumption, dict)

    def test_get_resource_balance(self, sample_poi): pass
        """Test resource balance calculation."""
        balance = ResourceManagementService.get_resource_balance(sample_poi)
        
        assert isinstance(balance, dict)

    def test_add_resource(self, sample_poi): pass
        """Test adding resource to POI."""
        sample_poi.resources = {"food": 100.0}
        
        updated_poi = ResourceManagementService.add_resource(sample_poi, "food", 50.0)
        
        assert updated_poi.resources["food"] == 150.0

    def test_poi_production_modifiers_constants(self): pass
        """Test POI production modifiers are properly defined."""
        modifiers = ResourceManagementService.POI_PRODUCTION_MODIFIERS
        
        # Check that major POI types have modifiers
        major_types = [POIType.CITY, POIType.TOWN, POIType.VILLAGE, POIType.OUTPOST]
        for poi_type in major_types: pass
            assert poi_type in modifiers
            assert isinstance(modifiers[poi_type], dict)

    def test_consumption_rates_constants(self): pass
        """Test consumption rates are properly defined."""
        rates = ResourceManagementService.CONSUMPTION_RATES
        
        # Check essential resources have consumption rates
        essential_resources = ["food", "water"]
        for resource in essential_resources: pass
            assert resource in rates
            assert rates[resource] > 0

    def test_calculate_production_with_modifiers(self, sample_poi): pass
        """Test production calculation with resource modifiers."""
        # Add resource production modifiers
        sample_poi.resource_production_modifiers = {"food": 0.5}  # 50% bonus
        
        production_with_modifier = ResourceManagementService.calculate_production(sample_poi)
        
        # Remove modifiers and calculate baseline
        sample_poi.resource_production_modifiers = {}
        production_baseline = ResourceManagementService.calculate_production(sample_poi)
        
        # Food production should be higher with modifier
        assert production_with_modifier["food"] > production_baseline["food"]

    def test_calculate_production_declining_state(self, sample_poi): pass
        """Test production in declining state."""
        # Set to declining state
        sample_poi.current_state = POIState.DECLINING
        production_declining = ResourceManagementService.calculate_production(sample_poi)
        
        # Set to normal state for comparison
        sample_poi.current_state = POIState.NORMAL
        production_normal = ResourceManagementService.calculate_production(sample_poi)
        
        # Declining should produce less
        for resource in production_normal: pass
            if resource in production_declining: pass
                assert production_declining[resource] < production_normal[resource]

    def test_calculate_production_abandoned_state(self, sample_poi): pass
        """Test production in abandoned state."""
        sample_poi.current_state = POIState.ABANDONED
        
        production = ResourceManagementService.calculate_production(sample_poi)
        
        # Abandoned POIs should produce nothing
        assert production == {}

    def test_calculate_production_mining_bonus(self, sample_poi): pass
        """Test mining tag bonus."""
        sample_poi.tags = ["mining"]
        
        production = ResourceManagementService.calculate_production(sample_poi)
        
        # Should include ore production due to mining tag
        assert "ore" in production

    def test_calculate_production_farming_bonus(self, sample_poi): pass
        """Test farming tag bonus."""
        sample_poi.tags = ["farming"]
        
        production_with_farming = ResourceManagementService.calculate_production(sample_poi)
        
        # Remove farming tag
        sample_poi.tags = []
        production_without_farming = ResourceManagementService.calculate_production(sample_poi)
        
        # Food production should be higher with farming tag
        assert production_with_farming["food"] > production_without_farming["food"]

    def test_remove_resource_success(self, sample_poi): pass
        """Test successfully removing resource from POI."""
        sample_poi.resources = {"food": 100.0}
        
        updated_poi, success = ResourceManagementService.remove_resource(
            sample_poi, "food", 30.0
        )
        
        assert success is True
        assert updated_poi.resources["food"] == 70.0

    def test_remove_resource_insufficient(self, sample_poi): pass
        """Test removing more resource than available."""
        sample_poi.resources = {"food": 100.0}
        
        updated_poi, success = ResourceManagementService.remove_resource(
            sample_poi, "food", 150.0
        )
        
        assert success is False
        assert updated_poi.resources["food"] == 100.0  # Unchanged

    def test_remove_resource_not_exists(self, sample_poi): pass
        """Test removing resource that doesn't exist."""
        sample_poi.resources = {}
        
        updated_poi, success = ResourceManagementService.remove_resource(
            sample_poi, "gold", 10.0
        )
        
        assert success is False

    def test_check_resource_scarcity(self, sample_poi): pass
        """Test resource scarcity detection."""
        # Set up resources with some shortages
        sample_poi.resources = {"food": 1.0, "water": 100.0}  # Low food
        
        scarcity = ResourceManagementService.check_resource_scarcity(sample_poi)
        
        assert isinstance(scarcity, dict)

    def test_set_resource_modifier(self, sample_poi): pass
        """Test setting resource production modifier."""
        updated_poi = ResourceManagementService.set_resource_modifier(
            sample_poi, "food", 0.25
        )
        
        assert hasattr(updated_poi, 'resource_production_modifiers')
        assert updated_poi.resource_production_modifiers["food"] == 0.25

    def test_initialize_resources(self, sample_poi): pass
        """Test resource initialization for POI."""
        updated_poi = ResourceManagementService.initialize_resources(sample_poi)
        
        assert hasattr(updated_poi, 'resources')
        assert isinstance(updated_poi.resources, dict)

    def test_calculate_resource_production_alternative(self, sample_poi): pass
        """Test alternative resource production calculation method."""
        # Set up POI with amenities and land features
        sample_poi.amenities = {"market": 1, "granary": 1}
        sample_poi.land_area = 1000
        
        production = ResourceManagementService.calculate_resource_production(sample_poi)
        
        assert isinstance(production, dict)

    def test_calculate_resource_consumption_alternative(self, sample_poi): pass
        """Test alternative resource consumption calculation method."""
        # Set up POI with different conditions
        sample_poi.amenities = {"tavern": 1}
        
        consumption = ResourceManagementService.calculate_resource_consumption(sample_poi)
        
        assert isinstance(consumption, dict)

    def test_update_resources_with_metadata(self, sample_poi): pass
        """Test resource update with metadata tracking."""
        sample_poi.resources = {"food": 100.0}
        sample_poi.metadata = {}
        
        updated_poi, metadata = ResourceManagementService.update_resources(
            sample_poi, time_delta=2.0
        )
        
        assert isinstance(metadata, dict)

    def test_apply_shortage_effects(self, sample_poi): pass
        """Test application of shortage effects on POI."""
        sample_poi.metadata = {}
        
        # Apply food shortage
        ResourceManagementService.apply_shortage_effects(sample_poi, ["food"])
        
        # Should track shortage effects
        assert hasattr(sample_poi, 'metadata')

    def test_city_vs_village_production(self): pass
        """Test production differences between city and village."""
        # Create city POI
        city_poi = Mock(spec=PointOfInterest)
        city_poi.poi_type = POIType.CITY
        city_poi.population = 2000
        city_poi.current_state = POIState.NORMAL
        city_poi.tags = []
        
        # Create village POI
        village_poi = Mock(spec=PointOfInterest)
        village_poi.poi_type = POIType.VILLAGE
        village_poi.population = 500
        village_poi.current_state = POIState.NORMAL
        village_poi.tags = []
        
        city_production = ResourceManagementService.calculate_production(city_poi)
        village_production = ResourceManagementService.calculate_production(village_poi)
        
        # Both should produce basic resources
        assert "gold" in city_production
        assert "gold" in village_production
        
        # City should produce more total due to higher population
        city_total = sum(city_production.values())
        village_total = sum(village_production.values())
        assert city_total > village_total

    def test_farm_specialization(self): pass
        """Test farm specialization in food production."""
        farm_poi = Mock(spec=PointOfInterest)
        farm_poi.poi_type = POIType.FARM
        farm_poi.population = 50
        farm_poi.current_state = POIState.NORMAL
        farm_poi.tags = ["farming"]
        
        production = ResourceManagementService.calculate_production(farm_poi)
        
        # Farm should primarily produce food
        assert "food" in production
        # Should produce significantly more food than other POI types
        assert production["food"] > 5.0

    def test_edge_cases_empty_poi(self): pass
        """Test handling of POI with minimal attributes."""
        poi = Mock()
        poi.population = 0
        poi.poi_type = POIType.OUTPOST
        poi.current_state = POIState.NORMAL
        poi.tags = []
        
        # Should handle gracefully
        production = ResourceManagementService.calculate_production(poi)
        assert production == {}

    def test_edge_cases_invalid_poi_type(self, sample_poi): pass
        """Test handling of invalid POI type."""
        # Set invalid POI type
        sample_poi.poi_type = None
        
        # Should handle gracefully and use fallback
        production = ResourceManagementService.calculate_production(sample_poi)
        assert isinstance(production, dict) 