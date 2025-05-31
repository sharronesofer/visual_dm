"""
Test module for region.models

Comprehensive tests for the region system models including enums, coordinate system,
metadata classes, and SQLAlchemy models.
"""

import pytest
import math
from datetime import datetime
from uuid import uuid4, UUID
from unittest.mock import Mock, patch

# Import the models
try:
    from backend.systems.region.models import (
        # Enums
        RegionType, BiomeType, ClimateType, ResourceType, POIType, DangerLevel,
        # Coordinate system
        HexCoordinate, HexCoordinateSchema,
        # Data classes
        ResourceNode, RegionProfile, RegionMetadata, ContinentMetadata,
        # Schemas
        RegionCreateSchema, RegionUpdateSchema, RegionResponseSchema,
        ContinentCreateSchema, ContinentResponseSchema,
        # Utility functions
        get_hex_neighbors, calculate_hex_distance, validate_region_adjacency
    )
except ImportError as e:
    pytest.skip(f"Module backend.systems.region.models not found: {e}", allow_module_level=True)


class TestRegionEnums:
    """Test class for region enum types"""
    
    def test_region_type_enum(self):
        """Test RegionType enum values"""
        assert RegionType.KINGDOM.value == "kingdom"
        assert RegionType.WILDERNESS.value == "wilderness"
        assert RegionType.CITY_STATE.value == "city_state"
        
        # Test enum has all expected values
        expected_types = [
            'kingdom', 'duchy', 'county', 'city_state', 'tribal_lands',
            'wilderness', 'wasteland', 'frontier', 'disputed_territory', 'neutral_zone'
        ]
        actual_types = [rt.value for rt in RegionType]
        assert set(actual_types) == set(expected_types)
    
    def test_biome_type_enum(self):
        """Test BiomeType enum values"""
        assert BiomeType.TEMPERATE_FOREST.value == "temperate_forest"
        assert BiomeType.DESERT.value == "desert"
        assert BiomeType.MOUNTAINS.value == "mountains"
        
        # Test we have all major biome types
        assert len(list(BiomeType)) >= 15  # Should have at least 15 biome types
    
    def test_climate_type_enum(self):
        """Test ClimateType enum values"""
        assert ClimateType.TROPICAL.value == "tropical"
        assert ClimateType.TEMPERATE.value == "temperate"
        assert ClimateType.ARID.value == "arid"
        
        # Test all climate types are available
        climate_values = [ct.value for ct in ClimateType]
        expected_climates = ['tropical', 'temperate', 'arid', 'polar']
        for climate in expected_climates:
            assert climate in climate_values
    
    def test_danger_level_enum(self):
        """Test DangerLevel enum values and ordering"""
        assert DangerLevel.VERY_SAFE.value == 1
        assert DangerLevel.SAFE.value == 2
        assert DangerLevel.APOCALYPTIC.value == 10
        
        # Test ordering
        assert DangerLevel.VERY_SAFE < DangerLevel.SAFE
        assert DangerLevel.DANGEROUS < DangerLevel.LETHAL
        assert DangerLevel.LETHAL < DangerLevel.APOCALYPTIC


class TestHexCoordinate:
    """Test class for hex coordinate system"""
    
    def test_hex_coordinate_creation(self):
        """Test creating hex coordinates"""
        coord = HexCoordinate(1, 2)
        assert coord.q == 1
        assert coord.r == 2
        assert coord.s == -3  # s = -q - r
    
    def test_hex_coordinate_equality(self):
        """Test hex coordinate equality"""
        coord1 = HexCoordinate(1, 2)
        coord2 = HexCoordinate(1, 2)
        coord3 = HexCoordinate(2, 1)
        
        assert coord1 == coord2
        assert coord1 != coord3
        assert hash(coord1) == hash(coord2)
        assert hash(coord1) != hash(coord3)
    
    def test_hex_coordinate_distance(self):
        """Test hex distance calculation"""
        coord1 = HexCoordinate(0, 0)
        coord2 = HexCoordinate(1, 0)
        coord3 = HexCoordinate(2, 0)
        
        assert coord1.distance_to(coord2) == 1
        assert coord1.distance_to(coord3) == 2
        assert coord2.distance_to(coord3) == 1
    
    def test_hex_coordinate_neighbors(self):
        """Test getting hex neighbors"""
        coord = HexCoordinate(0, 0)
        neighbors = coord.neighbors()
        
        assert len(neighbors) == 6
        expected_neighbors = [
            HexCoordinate(1, 0), HexCoordinate(1, -1), HexCoordinate(0, -1),
            HexCoordinate(-1, 0), HexCoordinate(-1, 1), HexCoordinate(0, 1)
        ]
        
        for expected in expected_neighbors:
            assert expected in neighbors
    
    def test_hex_coordinate_serialization(self):
        """Test hex coordinate to/from dict"""
        coord = HexCoordinate(1, 2)
        coord_dict = coord.to_dict()
        
        assert coord_dict == {"q": 1, "r": 2, "s": -3}
        
        restored_coord = HexCoordinate.from_dict(coord_dict)
        assert restored_coord == coord
    
    def test_hex_coordinate_pixel_conversion(self):
        """Test hex to pixel coordinate conversion"""
        coord = HexCoordinate(1, 0)
        x, y = coord.to_pixel(1.0)
        
        # Basic validation - pixel coordinates should be numeric
        assert isinstance(x, float)
        assert isinstance(y, float)
        
        # Test round-trip conversion
        restored_coord = HexCoordinate.from_pixel(x, y, 1.0)
        assert restored_coord == coord
    
    def test_hex_coordinate_fractional_conversion(self):
        """Test fractional coordinate conversion with rounding"""
        # Test exact conversion
        coord = HexCoordinate.from_fractional(1.0, 2.0)
        assert coord.q == 1 and coord.r == 2
        
        # Test rounding
        coord = HexCoordinate.from_fractional(1.4, 1.8)
        # Should round to maintain q + r + s = 0
        assert coord.q + coord.r + coord.s == 0


class TestHexCoordinateSchema:
    """Test class for hex coordinate Pydantic schema"""
    
    def test_hex_coordinate_schema_creation(self):
        """Test creating hex coordinate schema"""
        schema = HexCoordinateSchema(q=1, r=2, s=-3)
        assert schema.q == 1
        assert schema.r == 2
        assert schema.s == -3
    
    def test_hex_coordinate_schema_conversion(self):
        """Test conversion between schema and coordinate"""
        coord = HexCoordinate(1, 2)
        schema = HexCoordinateSchema.from_hex_coordinate(coord)
        
        assert schema.q == 1
        assert schema.r == 2
        assert schema.s == -3
        
        restored_coord = schema.to_hex_coordinate()
        assert restored_coord == coord


class TestResourceNode:
    """Test class for resource nodes"""
    
    def test_resource_node_creation(self):
        """Test creating resource nodes"""
        node = ResourceNode(
            resource_type=ResourceType.GOLD,
            abundance=0.8,
            quality=0.7,
            accessibility=0.6
        )
        
        assert node.resource_type == ResourceType.GOLD
        assert node.abundance == 0.8
        assert node.quality == 0.7
        assert node.accessibility == 0.6
        assert node.current_reserves == 1.0  # Default value
    
    def test_resource_node_value_calculation(self):
        """Test resource value calculation"""
        node = ResourceNode(
            resource_type=ResourceType.GOLD,
            abundance=0.8,
            quality=0.5,
            accessibility=0.6,
            current_reserves=0.9
        )
        
        expected_value = 0.8 * 0.5 * 0.6 * 0.9  # abundance * quality * accessibility * reserves
        assert node.calculate_value() == expected_value
    
    def test_resource_node_with_location(self):
        """Test resource node with hex coordinate location"""
        location = HexCoordinate(1, 2)
        node = ResourceNode(
            resource_type=ResourceType.IRON,
            abundance=0.5,
            quality=0.5,
            accessibility=0.5,
            location=location
        )
        
        assert node.location == location


class TestRegionProfile:
    """Test class for region environmental profiles"""
    
    def test_region_profile_creation(self):
        """Test creating region profiles"""
        profile = RegionProfile(
            dominant_biome=BiomeType.TEMPERATE_FOREST,
            climate=ClimateType.TEMPERATE
        )
        
        assert profile.dominant_biome == BiomeType.TEMPERATE_FOREST
        assert profile.climate == ClimateType.TEMPERATE
        assert profile.elevation == 0.0  # Default value
        assert profile.soil_fertility == 0.5  # Default value
    
    def test_region_profile_habitability(self):
        """Test habitability calculation"""
        # High habitability profile
        profile = RegionProfile(
            dominant_biome=BiomeType.GRASSLAND,
            soil_fertility=0.9,
            water_availability=0.8,
            humidity=0.5,  # Optimal
            natural_hazards=[]  # No hazards
        )
        
        habitability = profile.calculate_habitability()
        assert 0.0 <= habitability <= 1.0
        assert habitability > 0.7  # Should be high
        
        # Low habitability profile
        profile_low = RegionProfile(
            dominant_biome=BiomeType.DESERT,
            soil_fertility=0.1,
            water_availability=0.2,
            humidity=0.1,  # Very dry
            natural_hazards=['sandstorms', 'extreme_heat']
        )
        
        habitability_low = profile_low.calculate_habitability()
        assert habitability_low < habitability  # Should be lower


class TestRegionMetadata:
    """Test class for region metadata"""
    
    def test_region_metadata_creation(self):
        """Test creating region metadata"""
        region_id = uuid4()
        metadata = RegionMetadata(
            id=region_id,
            name="Test Region",
            description="A test region"
        )
        
        assert metadata.id == region_id
        assert metadata.name == "Test Region"
        assert metadata.description == "A test region"
        assert metadata.region_type == RegionType.WILDERNESS  # Default
        assert isinstance(metadata.created_at, datetime)
    
    def test_region_metadata_hex_coordinates(self):
        """Test hex coordinate management"""
        metadata = RegionMetadata(
            id=uuid4(),
            name="Test Region"
        )
        
        # Add hex coordinates
        coord1 = HexCoordinate(0, 0)
        coord2 = HexCoordinate(1, 0)
        
        metadata.add_hex_coordinate(coord1)
        metadata.add_hex_coordinate(coord2)
        
        assert len(metadata.hex_coordinates) == 2
        assert coord1 in metadata.hex_coordinates
        assert coord2 in metadata.hex_coordinates
        
        # Center should be calculated
        assert metadata.center_coordinate is not None
        assert metadata.area_square_km > 0
    
    def test_region_metadata_resource_management(self):
        """Test resource management in metadata"""
        metadata = RegionMetadata(
            id=uuid4(),
            name="Test Region"
        )
        
        # Add resource nodes
        gold_node = ResourceNode(
            resource_type=ResourceType.GOLD,
            abundance=0.8,
            quality=0.7,
            accessibility=0.6
        )
        iron_node = ResourceNode(
            resource_type=ResourceType.IRON,
            abundance=0.6,
            quality=0.5,
            accessibility=0.8
        )
        
        metadata.resource_nodes = [gold_node, iron_node]
        
        # Test total value calculation
        total_value = metadata.calculate_total_resource_value()
        expected_value = gold_node.calculate_value() + iron_node.calculate_value()
        assert total_value == expected_value
        
        # Test resource abundance lookup
        gold_abundance = metadata.get_resource_abundance(ResourceType.GOLD)
        assert gold_abundance == 0.8
        
        iron_abundance = metadata.get_resource_abundance(ResourceType.IRON)
        assert iron_abundance == 0.6
        
        # Test non-existent resource
        copper_abundance = metadata.get_resource_abundance(ResourceType.COPPER)
        assert copper_abundance == 0.0


class TestContinentMetadata:
    """Test class for continent metadata"""
    
    def test_continent_metadata_creation(self):
        """Test creating continent metadata"""
        continent_id = uuid4()
        metadata = ContinentMetadata(
            id=continent_id,
            name="Test Continent",
            description="A test continent"
        )
        
        assert metadata.id == continent_id
        assert metadata.name == "Test Continent"
        assert metadata.description == "A test continent"
        assert metadata.political_situation == "stable"  # Default
        assert isinstance(metadata.created_at, datetime)
    
    def test_continent_metadata_population_calculation(self):
        """Test total population calculation"""
        continent_id = uuid4()
        continent = ContinentMetadata(
            id=continent_id,
            name="Test Continent"
        )
        
        # Create test regions
        region1 = RegionMetadata(
            id=uuid4(),
            name="Region 1",
            continent_id=continent_id,
            population=1000
        )
        region2 = RegionMetadata(
            id=uuid4(),
            name="Region 2",
            continent_id=continent_id,
            population=2000
        )
        region3 = RegionMetadata(
            id=uuid4(),
            name="Other Region",
            continent_id=uuid4(),  # Different continent
            population=500
        )
        
        regions = [region1, region2, region3]
        total_population = continent.get_total_population(regions)
        
        # Should only include regions from this continent
        assert total_population == 3000  # 1000 + 2000
    
    def test_continent_metadata_dominant_climate(self):
        """Test dominant climate calculation"""
        continent = ContinentMetadata(
            id=uuid4(),
            name="Test Continent",
            climate_zones=[
                ClimateType.TEMPERATE,
                ClimateType.TEMPERATE,
                ClimateType.TROPICAL,
                ClimateType.TEMPERATE
            ]
        )
        
        dominant_climate = continent.get_dominant_climate()
        assert dominant_climate == ClimateType.TEMPERATE
        
        # Test with no climate zones
        empty_continent = ContinentMetadata(
            id=uuid4(),
            name="Empty Continent"
        )
        assert empty_continent.get_dominant_climate() is None


class TestRegionSchemas:
    """Test class for region Pydantic schemas"""
    
    def test_region_create_schema(self):
        """Test region creation schema"""
        data = {
            "name": "New Region",
            "description": "A new test region",
            "region_type": RegionType.KINGDOM,
            "dominant_biome": BiomeType.GRASSLAND,
            "climate": ClimateType.TEMPERATE
        }
        
        schema = RegionCreateSchema(**data)
        assert schema.name == "New Region"
        assert schema.region_type == RegionType.KINGDOM
        assert schema.dominant_biome == BiomeType.GRASSLAND
    
    def test_region_update_schema(self):
        """Test region update schema with optional fields"""
        data = {
            "name": "Updated Region",
            "population": 5000,
            "wealth_level": 0.8
        }
        
        schema = RegionUpdateSchema(**data)
        assert schema.name == "Updated Region"
        assert schema.population == 5000
        assert schema.wealth_level == 0.8
        assert schema.description is None  # Optional field not provided
    
    def test_region_response_schema(self):
        """Test region response schema"""
        region_id = uuid4()
        now = datetime.utcnow()
        
        data = {
            "id": region_id,
            "name": "Response Region",
            "description": "A region for response testing",
            "region_type": RegionType.CITY_STATE,
            "dominant_biome": BiomeType.COASTAL,
            "climate": ClimateType.OCEANIC,
            "population": 10000,
            "area_square_km": 500.0,
            "danger_level": DangerLevel.SAFE,
            "exploration_status": 0.75,
            "continent_id": uuid4(),
            "center_coordinate": HexCoordinateSchema(q=0, r=0, s=0),
            "created_at": now,
            "updated_at": now
        }
        
        schema = RegionResponseSchema(**data)
        assert schema.id == region_id
        assert schema.region_type == RegionType.CITY_STATE
        assert schema.population == 10000


class TestUtilityFunctions:
    """Test class for utility functions"""
    
    def test_get_hex_neighbors(self):
        """Test getting hex neighbors utility"""
        coord = HexCoordinate(0, 0)
        neighbors = get_hex_neighbors(coord)
        
        assert len(neighbors) == 6
        # Should be same as coord.neighbors() method
        assert set(neighbors) == set(coord.neighbors())
    
    def test_calculate_hex_distance(self):
        """Test hex distance calculation utility"""
        coord1 = HexCoordinate(0, 0)
        coord2 = HexCoordinate(2, 1)
        
        distance = calculate_hex_distance(coord1, coord2)
        # Should be same as coord1.distance_to(coord2) method
        assert distance == coord1.distance_to(coord2)
    
    def test_validate_region_adjacency(self):
        """Test region adjacency validation"""
        # Create adjacent regions
        region1 = RegionMetadata(
            id=uuid4(),
            name="Region 1",
            hex_coordinates=[HexCoordinate(0, 0), HexCoordinate(1, 0)]
        )
        region2 = RegionMetadata(
            id=uuid4(),
            name="Region 2", 
            hex_coordinates=[HexCoordinate(1, -1), HexCoordinate(2, -1)]
        )
        
        # Test adjacency (regions share neighboring hexes)
        is_adjacent = validate_region_adjacency(region1, region2)
        assert isinstance(is_adjacent, bool)


@pytest.mark.asyncio
async def test_models_integration():
    """Integration test for models working together"""
    # Create a complete region with all components
    continent_id = uuid4()
    continent = ContinentMetadata(
        id=continent_id,
        name="Integration Test Continent",
        climate_zones=[ClimateType.TEMPERATE],
        major_biomes=[BiomeType.TEMPERATE_FOREST]
    )
    
    # Create region profile
    profile = RegionProfile(
        dominant_biome=BiomeType.TEMPERATE_FOREST,
        climate=ClimateType.TEMPERATE,
        soil_fertility=0.8,
        water_availability=0.7
    )
    
    # Create resource nodes
    resources = [
        ResourceNode(
            resource_type=ResourceType.TIMBER,
            abundance=0.9,
            quality=0.8,
            accessibility=0.7,
            location=HexCoordinate(0, 0)
        ),
        ResourceNode(
            resource_type=ResourceType.FRESH_WATER,
            abundance=0.7,
            quality=0.9,
            accessibility=0.9,
            location=HexCoordinate(1, 0)
        )
    ]
    
    # Create region
    region = RegionMetadata(
        id=uuid4(),
        name="Integration Test Region",
        description="A region for integration testing",
        continent_id=continent_id,
        region_type=RegionType.KINGDOM,
        profile=profile,
        hex_coordinates=[HexCoordinate(0, 0), HexCoordinate(1, 0), HexCoordinate(0, 1)],
        population=5000,
        resource_nodes=resources,
        danger_level=DangerLevel.SAFE
    )
    
    # Manually update geographic data since RegionMetadata doesn't auto-calculate
    region._update_geographic_data()
    
    # Validate the integration
    assert region.continent_id == continent.id
    assert region.profile.dominant_biome == BiomeType.TEMPERATE_FOREST
    assert len(region.resource_nodes) == 2
    assert region.calculate_total_resource_value() > 0
    assert region.area_square_km > 0  # Should be calculated from hex coordinates
    assert region.center_coordinate is not None
    
    # Test continent population calculation
    regions_list = [region]
    total_pop = continent.get_total_population(regions_list)
    assert total_pop == 5000
