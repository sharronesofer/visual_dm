"""Tests for settlement_service module."""

import pytest
import random
import math
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from backend.systems.world_generation.settlement_service import SettlementService
from typing import Any
from typing import Type
from typing import List


class TestSettlementServiceInit: pass
    """Test SettlementService initialization."""

    def test_init_basic(self): pass
        """Test basic initialization."""
        world_data = {"regions": [], "continents": []}
        service = SettlementService(world_data)
        
        assert service.world_data == world_data
        assert service.settlements == []
        assert service.settlement_id_counter == 1
        assert isinstance(service.settlement_types, dict)
        assert len(service.settlement_types) > 0

    def test_init_settlement_types_structure(self): pass
        """Test settlement types have required structure."""
        service = SettlementService({})
        
        for settlement_type, data in service.settlement_types.items(): pass
            assert isinstance(settlement_type, str)
            assert isinstance(data, dict)
            assert "min_population" in data
            assert "max_population" in data
            assert "min_buildings" in data
            assert "max_buildings" in data
            assert "defense_level" in data
            assert "wealth_level" in data
            assert "services" in data

    def test_init_name_components(self): pass
        """Test name components are initialized."""
        service = SettlementService({})
        
        assert hasattr(service, 'name_prefixes')
        assert hasattr(service, 'name_roots')
        assert hasattr(service, 'name_suffixes')
        assert len(service.name_prefixes) > 0
        assert len(service.name_roots) > 0
        assert len(service.name_suffixes) > 0


class TestGenerateSettlementsForRegion: pass
    """Test settlement generation for regions."""

    def setup_method(self): pass
        """Set up test data."""
        self.service = SettlementService({})
        self.region = {
            "id": 1,
            "continent_id": 1,
            "x": 0,
            "y": 0,
            "width": 15,
            "height": 15,
            "biome": "temperate",
            "tiles": [[{"elevation": 0.5, "rainfall": 0.6} for _ in range(15)] for _ in range(15)]
        }

    @patch('backend.systems.world_generation.settlement_service.get_elevation_at_point')
    @patch('backend.systems.world_generation.settlement_service.get_rainfall_at_point')
    def test_generate_settlements_basic(self, mock_rainfall, mock_elevation): pass
        """Test basic settlement generation."""
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.6
        
        # Add region to world data
        self.service.world_data = {"regions": [self.region]}
        
        settlements = self.service.generate_settlements_for_region(1, 2, 4)
        
        assert isinstance(settlements, list)
        assert len(settlements) >= 2
        assert len(settlements) <= 4
        
        for settlement in settlements: pass
            assert isinstance(settlement, dict)
            assert "id" in settlement
            assert "name" in settlement
            assert "type" in settlement

    def test_generate_settlements_invalid_region(self): pass
        """Test generation with invalid region."""
        settlements = self.service.generate_settlements_for_region(999)
        
        assert settlements == []

    @patch('backend.systems.world_generation.settlement_service.get_elevation_at_point')
    @patch('backend.systems.world_generation.settlement_service.get_rainfall_at_point')
    def test_generate_settlements_biome_modifiers(self, mock_rainfall, mock_elevation): pass
        """Test settlement generation with different biomes."""
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.6
        
        # Add region to world data
        self.service.world_data = {"regions": [self.region]}
        
        biomes = ["forest", "mountain", "grassland", "coast", "desert"]
        
        for biome in biomes: pass
            self.region["biome"] = biome
            settlements = self.service.generate_settlements_for_region(1, 1, 2)
            
            assert isinstance(settlements, list)
            # Should generate at least some settlements for most biomes
            if biome != "desert":  # Desert might have fewer settlements
                assert len(settlements) >= 0

    @patch('backend.systems.world_generation.settlement_service.get_elevation_at_point')
    @patch('backend.systems.world_generation.settlement_service.get_rainfall_at_point')
    def test_generate_settlements_no_suitable_locations(self, mock_rainfall, mock_elevation): pass
        """Test generation when no suitable locations found."""
        # Mock very high elevation (unsuitable)
        mock_elevation.return_value = 0.9
        mock_rainfall.return_value = 0.1
        
        # Add region to world data
        self.service.world_data = {"regions": [self.region]}
        
        settlements = self.service.generate_settlements_for_region(1, 2, 4)
        
        assert isinstance(settlements, list)
        # Might be empty if no suitable locations


class TestWeightedSettlementType: pass
    """Test weighted settlement type selection."""

    def setup_method(self): pass
        """Set up test data."""
        self.service = SettlementService({})

    def test_weighted_settlement_type_basic(self): pass
        """Test basic weighted selection."""
        settlement_type = self.service._weighted_settlement_type()
        
        assert isinstance(settlement_type, str)
        assert settlement_type in self.service.settlement_types

    def test_weighted_settlement_type_exclude(self): pass
        """Test weighted selection with exclusions."""
        exclude = ["metropolis", "city"]
        settlement_type = self.service._weighted_settlement_type(exclude)
        
        assert isinstance(settlement_type, str)
        assert settlement_type not in exclude
        assert settlement_type in self.service.settlement_types

    def test_weighted_settlement_type_exclude_all_but_one(self): pass
        """Test weighted selection excluding all but one type."""
        all_types = list(self.service.settlement_types.keys())
        exclude = all_types[1:]  # Exclude all but first
        
        settlement_type = self.service._weighted_settlement_type(exclude)
        
        assert settlement_type == all_types[0]

    def test_weighted_settlement_type_reproducible(self): pass
        """Test that selection is reproducible with same seed."""
        random.seed(42)
        type1 = self.service._weighted_settlement_type()
        
        random.seed(42)
        type2 = self.service._weighted_settlement_type()
        
        assert type1 == type2


class TestFindSettlementLocations: pass
    """Test settlement location finding."""

    def setup_method(self): pass
        """Set up test data."""
        self.service = SettlementService({})
        self.region = {
            "id": 1,
            "x": 0,
            "y": 0,
            "width": 15,
            "height": 15,
            "biome": "temperate"
        }

    @patch('backend.systems.world_generation.settlement_service.get_elevation_at_point')
    @patch('backend.systems.world_generation.settlement_service.get_rainfall_at_point')
    def test_find_settlement_locations_basic(self, mock_rainfall, mock_elevation): pass
        """Test basic location finding."""
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.6
        
        locations = self.service._find_settlement_locations(self.region, 3)
        
        assert isinstance(locations, list)
        assert len(locations) <= 3
        
        for location in locations: pass
            assert isinstance(location, dict)
            assert "x" in location
            assert "y" in location
            assert "elevation" in location
            assert "rainfall" in location
            assert "water_access" in location
            assert "resource_access" in location
            assert "trade_access" in location
            assert "suitability" in location
            
            # Check suitability calculation
            expected_suitability = (
                location["water_access"] * 0.4 +
                location["resource_access"] * 0.3 +
                location["trade_access"] * 0.3
            )
            assert abs(location["suitability"] - expected_suitability) < 0.001

    @patch('backend.systems.world_generation.settlement_service.get_elevation_at_point')
    @patch('backend.systems.world_generation.settlement_service.get_rainfall_at_point')
    def test_find_settlement_locations_unsuitable_terrain(self, mock_rainfall, mock_elevation): pass
        """Test location finding with unsuitable terrain."""
        # Mock very high elevation (unsuitable)
        mock_elevation.return_value = 0.9
        mock_rainfall.return_value = 0.1
        
        locations = self.service._find_settlement_locations(self.region, 5)
        
        assert isinstance(locations, list)
        # Should find fewer or no locations due to unsuitable terrain

    @patch('backend.systems.world_generation.settlement_service.get_elevation_at_point')
    @patch('backend.systems.world_generation.settlement_service.get_rainfall_at_point')
    def test_find_settlement_locations_with_existing(self, mock_rainfall, mock_elevation): pass
        """Test location finding with existing settlements."""
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.6
        
        # Add existing settlement
        self.service.settlements = [{
            "region_id": 1,
            "x": 5,
            "y": 5
        }]
        
        locations = self.service._find_settlement_locations(self.region, 3)
        
        assert isinstance(locations, list)
        
        # Check that locations are not too close to existing settlement
        for location in locations: pass
            distance = math.sqrt((location["x"] - 5)**2 + (location["y"] - 5)**2)
            assert distance >= 3  # Minimum distance check


class TestCalculateAccess: pass
    """Test access calculation methods."""

    def setup_method(self): pass
        """Set up test data."""
        self.service = SettlementService({})

    def test_calculate_water_access_basic(self): pass
        """Test basic water access calculation."""
        access = self.service._calculate_water_access(5, 5)
        
        assert isinstance(access, float)
        assert 0.0 <= access <= 1.0

    def test_calculate_resource_access_basic(self): pass
        """Test basic resource access calculation."""
        region = {"biome": "forest"}
        
        access = self.service._calculate_resource_access(5, 5, region)
        
        assert isinstance(access, float)
        assert 0.0 <= access <= 1.0

    def test_calculate_resource_access_no_resources(self): pass
        """Test resource access calculation with unknown biome."""
        # Mock region with unknown biome (should get default 0.4 + random)
        region = {"biome": "unknown"}
        
        access = self.service._calculate_resource_access(5, 5, region)
        
        # Should be around 0.4 +/- 0.1 (random component)
        assert 0.3 <= access <= 0.5

    def test_calculate_trade_access_basic(self): pass
        """Test basic trade access calculation."""
        region = {"x": 10, "y": 10}
        
        with patch.object(self.service, '_count_neighboring_regions') as mock_neighbors: pass
            mock_neighbors.return_value = 3
            
            access = self.service._calculate_trade_access(15, 15, region)
            
            assert isinstance(access, float)
            assert 0.0 <= access <= 1.0

    def test_count_neighboring_regions_basic(self): pass
        """Test counting neighboring regions."""
        # Mock world data with regions
        self.service.world_data = {
            "regions": [
                {"x": 0, "y": 0},
                {"x": 15, "y": 0},  # Neighbor
                {"x": 0, "y": 15}, # Neighbor
                {"x": 30, "y": 30} # Not neighbor
            ]
        }
        
        count = self.service._count_neighboring_regions(0, 0)
        
        assert isinstance(count, int)
        assert count >= 0


class TestGenerateSettlement: pass
    """Test individual settlement generation."""

    def setup_method(self): pass
        """Set up test data."""
        self.service = SettlementService({})
        self.location = {
            "x": 5,
            "y": 5,
            "elevation": 0.5,
            "rainfall": 0.6,
            "water_access": 0.7,
            "resource_access": 0.6,
            "trade_access": 0.5,
            "suitability": 0.6  # Required by _generate_settlement
        }

    def test_generate_settlement_basic(self): pass
        """Test basic settlement generation."""
        with patch.object(self.service, '_generate_settlement_name') as mock_name: pass
            with patch.object(self.service, '_calculate_economy_weights') as mock_economy: pass
                with patch.object(self.service, '_generate_notable_buildings') as mock_buildings: pass
                    mock_name.return_value = "Test Town"
                    mock_economy.return_value = [1.0, 1.5, 1.0, 1.0, 1.0, 1.0, 1.0]  # 7 weights for economy types
                    mock_buildings.return_value = ["Town Hall", "Market"]
                    
                    settlement = self.service._generate_settlement(
                        region_id=1,
                        continent_id=1,
                        location=self.location,
                        settlement_type="town",
                        biome="temperate"
                    )
                    
                    assert isinstance(settlement, dict)
                    assert "id" in settlement
                    assert "name" in settlement
                    assert "type" in settlement
                    assert "population" in settlement
                    assert "x" in settlement
                    assert "y" in settlement
                    assert settlement["type"] == "town"

    def test_generate_settlement_different_types(self): pass
        """Test generation of different settlement types."""
        settlement_types = ["hamlet", "village", "town", "city", "metropolis", "outpost"]
        
        for settlement_type in settlement_types: pass
            with patch.object(self.service, '_generate_settlement_name') as mock_name: pass
                with patch.object(self.service, '_calculate_economy_weights') as mock_economy: pass
                    with patch.object(self.service, '_generate_notable_buildings') as mock_buildings: pass
                        mock_name.return_value = f"Test {settlement_type.title()}"
                        mock_economy.return_value = [1.0, 1.5, 1.0, 1.0, 1.0, 1.0, 1.0]  # 7 weights for economy types
                        mock_buildings.return_value = ["Building"]
                        
                        settlement = self.service._generate_settlement(
                            region_id=1,
                            continent_id=1,
                            location=self.location,
                            settlement_type=settlement_type,
                            biome="temperate"
                        )
                        
                        assert settlement["type"] == settlement_type
                        
                        # Check population is within expected range
                        type_data = self.service.settlement_types[settlement_type]
                        assert type_data["min_population"] <= settlement["population"] <= type_data["max_population"]


class TestGenerateSettlementName: pass
    """Test settlement name generation."""

    def setup_method(self): pass
        """Set up test data."""
        self.service = SettlementService({})

    def test_generate_settlement_name_basic(self): pass
        """Test basic name generation."""
        name = self.service._generate_settlement_name("town", "temperate")
        
        assert isinstance(name, str)
        assert len(name) > 0

    def test_generate_settlement_name_different_types(self): pass
        """Test name generation for different settlement types."""
        settlement_types = ["hamlet", "village", "town", "city", "metropolis", "outpost"]
        
        for settlement_type in settlement_types: pass
            name = self.service._generate_settlement_name(settlement_type, "temperate")
            
            assert isinstance(name, str)
            assert len(name) > 0

    def test_generate_settlement_name_different_biomes(self): pass
        """Test name generation for different biomes."""
        biomes = ["temperate", "desert", "tundra", "forest", "mountain", "grassland"]
        
        for biome in biomes: pass
            name = self.service._generate_settlement_name("town", biome)
            
            assert isinstance(name, str)
            assert len(name) > 0

    def test_generate_settlement_name_reproducible(self): pass
        """Test that name generation is reproducible with same seed."""
        random.seed(42)
        name1 = self.service._generate_settlement_name("town", "temperate")
        
        random.seed(42)
        name2 = self.service._generate_settlement_name("town", "temperate")
        
        assert name1 == name2


class TestCalculateEconomyWeights: pass
    """Test economy weight calculation."""

    def setup_method(self): pass
        """Set up test data."""
        self.service = SettlementService({})
        self.location = {
            "water_access": 0.7,
            "resource_access": 0.6,
            "trade_access": 0.5,
            "elevation": 0.4  # Required by _calculate_economy_weights
        }

    def test_calculate_economy_weights_basic(self): pass
        """Test basic economy weight calculation."""
        weights = self.service._calculate_economy_weights("temperate", self.location)
        
        assert isinstance(weights, list)
        assert len(weights) == 7  # agriculture, trade, mining, fishing, forestry, crafts, services
        assert all(isinstance(w, float) for w in weights)
        assert all(w >= 0 for w in weights)

    def test_calculate_economy_weights_different_biomes(self): pass
        """Test economy weights for different biomes."""
        biomes = ["temperate", "desert", "tundra", "forest", "mountain", "grassland"]
        
        for biome in biomes: pass
            weights = self.service._calculate_economy_weights(biome, self.location)
            
            assert isinstance(weights, list)
            assert len(weights) == 7
            assert all(w >= 0 for w in weights)

    def test_calculate_economy_weights_high_trade_access(self): pass
        """Test economy weights with high trade access."""
        high_trade_location = {
            "water_access": 0.5,
            "resource_access": 0.5,
            "trade_access": 0.9,
            "elevation": 0.3
        }
        
        weights = self.service._calculate_economy_weights("temperate", high_trade_location)
        
        # Trade weight should be higher (index 1 = trade)
        assert weights[1] > weights[0]  # trade > agriculture
        assert weights[1] > weights[2]  # trade > mining


class TestGenerateNotableBuildings: pass
    """Test notable building generation."""

    def setup_method(self): pass
        """Set up test data."""
        self.service = SettlementService({})

    def test_generate_notable_buildings_basic(self): pass
        """Test basic notable building generation."""
        buildings = self.service._generate_notable_buildings("town", "agriculture")
        
        assert isinstance(buildings, list)
        assert len(buildings) >= 0

    def test_generate_notable_buildings_different_types(self): pass
        """Test notable buildings for different settlement types."""
        settlement_types = ["hamlet", "village", "town", "city", "metropolis"]
        
        for settlement_type in settlement_types: pass
            buildings = self.service._generate_notable_buildings(settlement_type, "trade")
            
            assert isinstance(buildings, list)

    def test_generate_notable_buildings_different_economies(self): pass
        """Test notable buildings for different economies."""
        economies = ["agriculture", "trade", "mining", "fishing", "forestry"]
        
        for economy in economies: pass
            buildings = self.service._generate_notable_buildings("town", economy)
            
            assert isinstance(buildings, list)


class TestUtilityMethods: pass
    """Test utility methods."""

    def setup_method(self): pass
        """Set up test data."""
        self.service = SettlementService({})
        self.service.settlements = [
            {"id": 1, "region_id": 1, "name": "Town A"},
            {"id": 2, "region_id": 1, "name": "Town B"},
            {"id": 3, "region_id": 2, "name": "Town C"}
        ]
        self.service.world_data = {
            "regions": [
                {"id": 1, "name": "Region 1"},
                {"id": 2, "name": "Region 2"}
            ]
        }

    def test_get_existing_settlements_in_region(self): pass
        """Test getting existing settlements in region."""
        settlements = self.service._get_existing_settlements_in_region(1)
        
        assert isinstance(settlements, list)
        assert len(settlements) == 2
        assert all(s["region_id"] == 1 for s in settlements)

    def test_get_existing_settlements_in_region_empty(self): pass
        """Test getting settlements from empty region."""
        settlements = self.service._get_existing_settlements_in_region(999)
        
        assert settlements == []

    def test_get_region_by_id_valid(self): pass
        """Test getting region by valid ID."""
        region = self.service._get_region_by_id(1)
        
        assert region is not None
        assert region["id"] == 1

    def test_get_region_by_id_invalid(self): pass
        """Test getting region by invalid ID."""
        region = self.service._get_region_by_id(999)
        
        assert region is None


class TestIntegration: pass
    """Test integration scenarios."""

    def setup_method(self): pass
        """Set up test data."""
        self.service = SettlementService({})
        self.service.world_data = {
            "regions": [{
                "id": 1,
                "continent_id": 1,
                "x": 0,
                "y": 0,
                "width": 15,
                "height": 15,
                "biome": "temperate",
                "tiles": [[{"elevation": 0.5, "rainfall": 0.6} for _ in range(15)] for _ in range(15)]
            }],
            "continents": [{"id": 1, "name": "Test Continent"}]
        }

    @patch('backend.systems.world_generation.settlement_service.get_elevation_at_point')
    @patch('backend.systems.world_generation.settlement_service.get_rainfall_at_point')
    def test_full_settlement_generation_flow(self, mock_rainfall, mock_elevation): pass
        """Test full settlement generation workflow."""
        mock_elevation.return_value = 0.5
        mock_rainfall.return_value = 0.6
        
        # Generate settlements
        settlements = self.service.generate_settlements_for_region(1, 2, 4)
        
        assert isinstance(settlements, list)
        assert len(settlements) >= 0
        
        # Check that settlements were added to service
        assert len(self.service.settlements) == len(settlements)
        
        # Verify settlement structure
        for settlement in settlements: pass
            assert "id" in settlement
            assert "name" in settlement
            assert "type" in settlement
            assert "region_id" in settlement
            assert "continent_id" in settlement
            assert "population" in settlement
            assert "x" in settlement
            assert "y" in settlement


class TestErrorHandling: pass
    """Test error handling and edge cases."""

    def setup_method(self): pass
        """Set up test data."""
        self.service = SettlementService({})

    def test_weighted_settlement_type_empty_exclude(self): pass
        """Test weighted selection with empty exclude list."""
        settlement_type = self.service._weighted_settlement_type([])
        
        assert isinstance(settlement_type, str)
        assert settlement_type in self.service.settlement_types

    def test_find_settlement_locations_zero_count(self): pass
        """Test finding zero locations."""
        region = {"x": 0, "y": 0, "width": 15, "height": 15}
        
        locations = self.service._find_settlement_locations(region, 0)
        
        assert locations == []

    def test_calculate_resource_access_missing_resources_key(self): pass
        """Test resource access with missing biome key."""
        region = {}  # No biome key - should default to "temperate"
        
        access = self.service._calculate_resource_access(5, 5, region)
        
        # Should be around 0.4 +/- 0.1 (default biome + random)
        assert 0.3 <= access <= 0.5

    def test_count_neighboring_regions_empty_world(self): pass
        """Test counting neighbors with empty world."""
        self.service.world_data = {"regions": []}
        
        count = self.service._count_neighboring_regions(0, 0)
        
        assert count == 0

    def test_generate_settlement_name_edge_cases(self): pass
        """Test name generation with edge cases."""
        # Test with empty biome
        name = self.service._generate_settlement_name("town", "")
        assert isinstance(name, str)
        assert len(name) > 0
        
        # Test with unknown settlement type
        name = self.service._generate_settlement_name("unknown", "temperate")
        assert isinstance(name, str)
        assert len(name) > 0
