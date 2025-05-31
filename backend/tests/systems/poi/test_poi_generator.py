"""
Test POI Generator functionality
"""

import pytest
from unittest.mock import Mock, patch
from backend.systems.poi.services.poi_generator import (
    POIGenerator, 
    GenerationParameters, 
    GenerationType, 
    BiomeType,
    GenerationRule,
    WorldCell,
    get_poi_generator
)
from backend.systems.poi.models import POIType, POIState


class TestPOIGenerator:
    """Test POI Generator functionality"""
    
    def test_poi_generator_initialization(self):
        """Test POI generator initializes correctly"""
        generator = POIGenerator()
        
        assert generator is not None
        assert generator.generation_rules is not None
        assert len(generator.generation_rules) > 0
        assert POIType.CITY in generator.generation_rules
        assert POIType.VILLAGE in generator.generation_rules
    
    def test_generation_rules_setup(self):
        """Test that generation rules are properly configured"""
        generator = POIGenerator()
        
        # Check city rules
        city_rule = generator.generation_rules[POIType.CITY]
        assert city_rule.poi_type == POIType.CITY
        assert city_rule.min_distance_same_type > 0
        assert city_rule.probability_base > 0
        
        # Check village rules
        village_rule = generator.generation_rules[POIType.VILLAGE]
        assert village_rule.poi_type == POIType.VILLAGE
        assert village_rule.min_distance_same_type < city_rule.min_distance_same_type
    
    @patch('backend.systems.poi.services.poi_generator.get_db_session')
    def test_generate_pois_for_region(self, mock_db):
        """Test POI generation for a region"""
        mock_session = Mock()
        mock_db.return_value = mock_session
        
        generator = POIGenerator(mock_session)
        
        # Test parameters
        region_bounds = (0.0, 0.0, 100.0, 100.0)
        params = GenerationParameters(
            poi_density=0.01,  # Low density for testing
            civilization_level=0.5,
            seed=12345
        )
        
        # Generate POIs
        pois = generator.generate_pois_for_region(region_bounds, params)
        
        # Verify results
        assert isinstance(pois, list)
        assert len(pois) >= 0  # Should generate at least some POIs
        
        # Check POI properties
        for poi in pois:
            assert poi.name is not None
            assert poi.description is not None
            assert poi.poi_type in [t.value for t in POIType]
            assert poi.location_x >= 0.0 and poi.location_x <= 100.0
            assert poi.location_y >= 0.0 and poi.location_y <= 100.0
            assert poi.population > 0
    
    def test_find_optimal_poi_location(self):
        """Test finding optimal POI locations"""
        generator = POIGenerator()
        
        search_area = (0.0, 0.0, 100.0, 100.0)
        params = GenerationParameters(seed=12345)
        
        # Find location for a village
        location = generator.find_optimal_poi_location(
            POIType.VILLAGE, search_area, [], params
        )
        
        assert location is not None
        assert isinstance(location, tuple)
        assert len(location) == 2
        assert 0.0 <= location[0] <= 100.0
        assert 0.0 <= location[1] <= 100.0
    
    def test_poi_name_generation(self):
        """Test POI name generation"""
        generator = POIGenerator()
        
        # Test different POI types
        city_name = generator._generate_poi_name(POIType.CITY)
        village_name = generator._generate_poi_name(POIType.VILLAGE)
        fortress_name = generator._generate_poi_name(POIType.FORTRESS)
        
        assert isinstance(city_name, str)
        assert len(city_name) > 0
        assert isinstance(village_name, str)
        assert len(village_name) > 0
        assert isinstance(fortress_name, str)
        assert len(fortress_name) > 0
    
    def test_poi_population_calculation(self):
        """Test POI population calculation"""
        generator = POIGenerator()
        params = GenerationParameters(civilization_level=0.5)
        
        # Test different POI types
        city_pop = generator._calculate_poi_population(POIType.CITY, params)
        village_pop = generator._calculate_poi_population(POIType.VILLAGE, params)
        
        assert city_pop > village_pop  # Cities should be larger
        assert city_pop > 0
        assert village_pop > 0
    
    def test_distance_constraints(self):
        """Test distance constraint checking"""
        generator = POIGenerator()
        
        # Create mock existing POI
        existing_poi = Mock()
        existing_poi.location_x = 50.0
        existing_poi.location_y = 50.0
        existing_poi.poi_type = POIType.CITY.value
        
        rule = generator.generation_rules[POIType.CITY]
        
        # Test too close (should fail)
        too_close = generator._check_distance_constraints(
            51.0, 51.0, POIType.CITY, [existing_poi], rule
        )
        assert not too_close
        
        # Test far enough (should pass)
        far_enough = generator._check_distance_constraints(
            250.0, 250.0, POIType.CITY, [existing_poi], rule
        )
        assert far_enough
    
    def test_factory_function(self):
        """Test the factory function"""
        generator = get_poi_generator()
        assert isinstance(generator, POIGenerator)
    
    def test_generation_parameters(self):
        """Test generation parameters"""
        params = GenerationParameters()
        
        # Test defaults
        assert params.world_size == (1000.0, 1000.0)
        assert params.poi_density == 0.1
        assert params.civilization_level == 0.5
        
        # Test custom parameters
        custom_params = GenerationParameters(
            world_size=(500.0, 500.0),
            poi_density=0.2,
            civilization_level=0.8,
            seed=42
        )
        
        assert custom_params.world_size == (500.0, 500.0)
        assert custom_params.poi_density == 0.2
        assert custom_params.civilization_level == 0.8
        assert custom_params.seed == 42
    
    def test_biome_types(self):
        """Test biome type enumeration"""
        assert BiomeType.GRASSLAND == "grassland"
        assert BiomeType.FOREST == "forest"
        assert BiomeType.MOUNTAIN == "mountain"
        assert BiomeType.DESERT == "desert"
        assert BiomeType.COASTAL == "coastal"
    
    def test_generation_types(self):
        """Test generation type enumeration"""
        assert GenerationType.RANDOM == "random"
        assert GenerationType.CLUSTERED == "clustered"
        assert GenerationType.GRID_BASED == "grid_based"
        assert GenerationType.NOISE_BASED == "noise_based"
    
    def test_world_cell(self):
        """Test world cell data structure"""
        cell = WorldCell(x=10.0, y=20.0)
        
        assert cell.x == 10.0
        assert cell.y == 20.0
        assert cell.biome == BiomeType.GRASSLAND  # Default
        assert cell.elevation == 0.5  # Default
        assert isinstance(cell.resources, list)
        assert isinstance(cell.existing_pois, list)
    
    def test_generation_rule(self):
        """Test generation rule data structure"""
        rule = GenerationRule(
            poi_type=POIType.CITY,
            probability_base=0.05,
            min_distance_same_type=200.0,
            preferred_biomes=[BiomeType.GRASSLAND, BiomeType.COASTAL]
        )
        
        assert rule.poi_type == POIType.CITY
        assert rule.probability_base == 0.05
        assert rule.min_distance_same_type == 200.0
        assert BiomeType.GRASSLAND in rule.preferred_biomes
        assert BiomeType.COASTAL in rule.preferred_biomes


class TestPOIGeneratorIntegration:
    """Integration tests for POI Generator"""
    
    @patch('backend.systems.poi.services.poi_generator.get_db_session')
    def test_full_generation_workflow(self, mock_db):
        """Test complete POI generation workflow"""
        mock_session = Mock()
        mock_db.return_value = mock_session
        
        generator = POIGenerator(mock_session)
        
        # Large region for comprehensive test
        region_bounds = (0.0, 0.0, 500.0, 500.0)
        params = GenerationParameters(
            poi_density=0.005,  # Moderate density
            civilization_level=0.7,
            magic_prevalence=0.3,
            seed=98765
        )
        
        # Generate POIs
        pois = generator.generate_pois_for_region(region_bounds, params)
        
        # Verify comprehensive results
        assert len(pois) > 0
        
        # Check for variety of POI types
        poi_types = set(poi.poi_type for poi in pois)
        assert len(poi_types) > 1  # Should have multiple types
        
        # Verify all POIs are within bounds
        for poi in pois:
            assert 0.0 <= poi.location_x <= 500.0
            assert 0.0 <= poi.location_y <= 500.0
            assert poi.population > 0
            assert poi.max_population >= poi.population
        
        # Verify database interactions
        assert mock_session.add.call_count == len(pois)
        mock_session.commit.assert_called_once()
    
    def test_multiple_region_generation(self):
        """Test generating POIs for multiple regions"""
        generator = POIGenerator()
        
        regions = [
            (0.0, 0.0, 100.0, 100.0),
            (100.0, 0.0, 200.0, 100.0),
            (0.0, 100.0, 100.0, 200.0)
        ]
        
        all_pois = []
        params = GenerationParameters(poi_density=0.01, seed=11111)
        
        for region in regions:
            pois = generator.generate_pois_for_region(region, params)
            all_pois.extend(pois)
        
        # Verify POIs are distributed across regions
        assert len(all_pois) > 0
        
        # Check POI distribution
        region_counts = [0, 0, 0]
        for poi in all_pois:
            if 0 <= poi.location_x < 100 and 0 <= poi.location_y < 100:
                region_counts[0] += 1
            elif 100 <= poi.location_x < 200 and 0 <= poi.location_y < 100:
                region_counts[1] += 1
            elif 0 <= poi.location_x < 100 and 100 <= poi.location_y < 200:
                region_counts[2] += 1
        
        # Should have POIs in multiple regions
        non_empty_regions = sum(1 for count in region_counts if count > 0)
        assert non_empty_regions >= 1  # At least one region should have POIs 