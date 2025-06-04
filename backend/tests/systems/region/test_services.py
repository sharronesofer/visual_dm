"""
Test module for region.services

Comprehensive tests for the region system services including RegionService,
WorldGenerationService, and RegionEventService.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime

# Import the services
try:
    from backend.systems.region.services.services import RegionBusinessService as RegionService
    from backend.systems.world_generation.services.world_generator import WorldGenerator as WorldGenerationService
    from backend.systems.region.services.event_service import RegionEventService
    from backend.systems.region.models import (
        RegionMetadata, ContinentMetadata, RegionProfile, ResourceNode,
        BiomeType, ClimateType, RegionType, ResourceType, DangerLevel,
        HexCoordinate
    )
    from backend.infrastructure.shared.exceptions import (
        RegionNotFoundError, RegionValidationError, RegionConflictError
    )
except ImportError as e:
    pytest.skip(f"Required modules not found: {e}", allow_module_level=True)


class TestRegionService:
    """Test class for RegionService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock repository for testing"""
        repository = Mock()
        repository.get_by_id = AsyncMock()
        repository.get_all = AsyncMock()
        repository.create = AsyncMock()
        repository.update = AsyncMock()
        repository.delete = AsyncMock()
        repository.get_by_name = AsyncMock()
        repository.get_by_filters = AsyncMock()
        return repository
    
    @pytest.fixture
    def region_service(self, mock_repository):
        """Create RegionService instance with mocked dependencies"""
        service = RegionService(repository=mock_repository)
        return service
    
    @pytest.fixture
    def sample_region_metadata(self):
        """Sample region metadata for testing"""
        return RegionMetadata(
            id=uuid4(),
            name="Test Region",
            description="A test region for unit testing",
            region_type="kingdom",
            profile=RegionProfile(
                dominant_biome="temperate_forest",
                climate=ClimateType.TEMPERATE
            ),
            population=5000,
            hex_coordinates=[HexCoordinate(0, 0), HexCoordinate(1, 0)],
            danger_level=DangerLevel.SAFE
        )
    
    @pytest.mark.asyncio
    async def test_get_region_by_id_success(self, region_service, mock_repository, sample_region_metadata):
        """Test successful retrieval of region by ID"""
        region_id = sample_region_metadata.id
        mock_repository.get_by_id.return_value = sample_region_metadata
        
        result = await region_service.get_region_by_id(region_id)
        
        assert result == sample_region_metadata
        mock_repository.get_by_id.assert_called_once_with(region_id)
    
    @pytest.mark.asyncio
    async def test_get_region_by_id_not_found(self, region_service, mock_repository):
        """Test region not found scenario"""
        region_id = uuid4()
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(RegionNotFoundError):
            await region_service.get_region_by_id(region_id)
    
    @pytest.mark.asyncio
    async def test_get_regions_all(self, region_service, mock_repository):
        """Test getting all regions"""
        sample_regions = [
            RegionMetadata(id=uuid4(), name="Region 1"),
            RegionMetadata(id=uuid4(), name="Region 2"),
            RegionMetadata(id=uuid4(), name="Region 3")
        ]
        mock_repository.get_all.return_value = sample_regions
        
        result = await region_service.get_regions()
        
        assert result == sample_regions
        mock_repository.get_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_regions_with_filters(self, region_service, mock_repository):
        """Test getting regions with filters"""
        filtered_regions = [
            RegionMetadata(id=uuid4(), name="Kingdom 1", region_type="kingdom"),
            RegionMetadata(id=uuid4(), name="Kingdom 2", region_type="kingdom")
        ]
        mock_repository.get_by_filters.return_value = filtered_regions
        
        filters = {"region_type": "kingdom"}
        result = await region_service.get_regions(filters=filters)
        
        assert result == filtered_regions
        mock_repository.get_by_filters.assert_called_once_with(filters)
    
    @pytest.mark.asyncio
    async def test_create_region_success(self, region_service, mock_repository, sample_region_metadata):
        """Test successful region creation"""
        mock_repository.create.return_value = sample_region_metadata
        
        create_data = {
            "name": sample_region_metadata.name,
            "description": sample_region_metadata.description,
            "region_type": sample_region_metadata.region_type
        }
        
        result = await region_service.create_region(create_data)
        
        assert result == sample_region_metadata
        mock_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_region_duplicate_name(self, region_service, mock_repository):
        """Test region creation with duplicate name"""
        existing_region = RegionMetadata(id=uuid4(), name="Existing Region")
        mock_repository.get_by_name.return_value = existing_region
        
        create_data = {"name": "Existing Region", "description": "Duplicate"}
        
        with pytest.raises(RegionConflictError):
            await region_service.create_region(create_data)
    
    @pytest.mark.asyncio
    async def test_update_region_success(self, region_service, mock_repository, sample_region_metadata):
        """Test successful region update"""
        region_id = sample_region_metadata.id
        mock_repository.get_by_id.return_value = sample_region_metadata
        
        updated_metadata = RegionMetadata(**sample_region_metadata.__dict__)
        updated_metadata.name = "Updated Region"
        updated_metadata.population = 7500
        mock_repository.update.return_value = updated_metadata
        
        update_data = {"name": "Updated Region", "population": 7500}
        result = await region_service.update_region(region_id, update_data)
        
        assert result.name == "Updated Region"
        assert result.population == 7500
        mock_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_region_not_found(self, region_service, mock_repository):
        """Test updating non-existent region"""
        region_id = uuid4()
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(RegionNotFoundError):
            await region_service.update_region(region_id, {"name": "New Name"})
    
    @pytest.mark.asyncio
    async def test_delete_region_success(self, region_service, mock_repository, sample_region_metadata):
        """Test successful region deletion"""
        region_id = sample_region_metadata.id
        mock_repository.get_by_id.return_value = sample_region_metadata
        mock_repository.delete.return_value = True
        
        result = await region_service.delete_region(region_id)
        
        assert result is True
        mock_repository.delete.assert_called_once_with(region_id)
    
    @pytest.mark.asyncio
    async def test_delete_region_not_found(self, region_service, mock_repository):
        """Test deleting non-existent region"""
        region_id = uuid4()
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(RegionNotFoundError):
            await region_service.delete_region(region_id)
    
    @pytest.mark.asyncio
    async def test_get_regions_by_continent(self, region_service, mock_repository):
        """Test getting regions by continent"""
        continent_id = uuid4()
        continent_regions = [
            RegionMetadata(id=uuid4(), name="Region 1", continent_id=continent_id),
            RegionMetadata(id=uuid4(), name="Region 2", continent_id=continent_id)
        ]
        mock_repository.get_by_filters.return_value = continent_regions
        
        result = await region_service.get_regions_by_continent(continent_id)
        
        assert result == continent_regions
        mock_repository.get_by_filters.assert_called_once_with({"continent_id": continent_id})
    
    @pytest.mark.asyncio
    async def test_search_regions_by_name(self, region_service, mock_repository):
        """Test searching regions by name pattern"""
        search_results = [
            RegionMetadata(id=uuid4(), name="Forest Kingdom"),
            RegionMetadata(id=uuid4(), name="Forest Valley")
        ]
        mock_repository.search_by_name = AsyncMock(return_value=search_results)
        
        result = await region_service.search_regions_by_name("forest")
        
        assert result == search_results
        mock_repository.search_by_name.assert_called_once_with("forest")


class TestWorldGenerationService:
    """Test class for WorldGenerationService"""
    
    @pytest.fixture
    def world_generation_service(self):
        """Create WorldGenerationService instance"""
        # Create a mock repository for the world generation service
        mock_repository = AsyncMock()
        return WorldGenerationService(repository=mock_repository)
    
    @pytest.fixture
    def sample_generation_params(self):
        """Sample generation parameters for testing"""
        return {
            "num_continents": 3,
            "continent_size_range": (50, 150),
            "num_regions_per_continent": 100,
            "biome_distribution": {
                "temperate_forest": 0.3,  # Use strings
                "grassland": 0.25,        # Use strings
                "mountains": 0.2,         # Use strings
                "desert": 0.15,           # Use strings
                "coastal": 0.1            # Use strings
            },
            "major_biomes": ["temperate_forest", "grassland"]  # Use strings
        }
    
    def test_generate_continent_metadata(self, world_generation_service):
        """Test continent metadata generation"""
        params = {
            "name": "Test Continent",
            "seed": 12345,
            "climate_zones": [ClimateType.TEMPERATE, ClimateType.TROPICAL],
            "major_biomes": [BiomeType.TEMPERATE_FOREST, BiomeType.GRASSLAND]
        }
        
        continent = world_generation_service.generate_continent_metadata(params)
        
        assert isinstance(continent, ContinentMetadata)
        assert continent.name == "Test Continent"
        assert continent.generation_seed == 12345
        assert len(continent.climate_zones) == 2
        assert len(continent.major_biomes) == 2
        assert isinstance(continent.id, UUID)
    
    def test_generate_region_metadata_for_continent(self, world_generation_service):
        """Test generating region metadata for continent"""
        continent_id = uuid4()
        region_params = {
            "name": "Test Region",
            "biome": "temperate_forest",  # Use string
            "climate": ClimateType.TEMPERATE,
            "population": 5000
        }
        
        region = world_generation_service.generate_region_metadata_for_continent(
            continent_id, region_params
        )
        
        assert region.continent_id == continent_id
        assert region.name == "Test Region"
        assert region.profile.dominant_biome == "temperate_forest"  # Use string
        assert region.profile.climate == ClimateType.TEMPERATE
        assert region.population == 5000
    
    def test_generate_hex_coordinates_for_region(self, world_generation_service):
        """Test hex coordinate generation for regions"""
        params = {
            "size": "large",
            "center": HexCoordinate(0, 0),
            "shape": "irregular"
        }
        
        coordinates = world_generation_service.generate_hex_coordinates(params)
        
        assert isinstance(coordinates, list)
        assert len(coordinates) > 0
        assert all(isinstance(coord, HexCoordinate) for coord in coordinates)
        # Large region should have more coordinates
        assert len(coordinates) >= 5
    
    def test_generate_resource_nodes(self, world_generation_service):
        """Test resource node generation"""
        region_params = {
            "biome": "mountains",  # Use string
            "size": "large",
            "resource_richness": 0.8
        }
        
        resource_nodes = world_generation_service.generate_resource_nodes(region_params)
        
        assert isinstance(resource_nodes, list)
        assert len(resource_nodes) > 0
        
        # Mountains should generate metals and stone
        resource_types = [node.resource_type for node in resource_nodes]
        # Check for expected mountain resources (using strings)
        expected_resources = ["iron", "stone", "gems"]
        assert any(rt in expected_resources for rt in resource_types)
    
    def test_calculate_region_profile(self, world_generation_service):
        """Test region profile calculation"""
        region_params = {
            "biome": "tropical_rainforest",  # Use string
            "climate": ClimateType.TROPICAL,
            "elevation": 200,
            "rainfall": 3000
        }
        
        profile = world_generation_service.calculate_region_profile(region_params)
        
        assert isinstance(profile, RegionProfile)
        assert profile.dominant_biome == "tropical_rainforest"  # Use string
        assert profile.climate == ClimateType.TROPICAL
        assert profile.precipitation == 3000
        assert profile.elevation == 200
    
    @pytest.mark.asyncio
    async def test_generate_full_world(self, world_generation_service, sample_generation_params):
        """Test full world generation"""
        with patch.object(world_generation_service, 'generate_continent_metadata') as mock_continent:
            with patch.object(world_generation_service, 'generate_region_metadata') as mock_region:
                # Mock continent generation
                mock_continent.return_value = ContinentMetadata(
                    id=uuid4(),
                    name="Generated Continent"
                )
                
                # Mock region generation
                mock_region.return_value = RegionMetadata(
                    id=uuid4(),
                    name="Generated Region"
                )
                
                result = await world_generation_service.generate_world(sample_generation_params)
                
                assert "continents" in result
                assert "regions" in result
                assert len(result["continents"]) == sample_generation_params["num_continents"]
                # Should generate regions for each continent
                expected_total_regions = (sample_generation_params["num_continents"] * 
                                        sample_generation_params["num_regions_per_continent"])
                assert len(result["regions"]) == expected_total_regions
    
    def test_validate_generation_parameters(self, world_generation_service):
        """Test parameter validation"""
        # Valid parameters
        valid_params = {
            "num_continents": 2,
            "continent_size_range": (50, 100),
            "num_regions_per_continent": 50,
            "seed": 12345
        }
        assert world_generation_service.validate_generation_parameters(valid_params) is True
        
        # Invalid parameters
        invalid_params = {
            "num_continents": 0,  # Must be positive
            "continent_size_range": (0, 0),  # Must be positive
            "num_regions_per_continent": -1,  # Must be positive
            "seed": "not_a_number"  # Must be int
        }
        assert world_generation_service.validate_generation_parameters(invalid_params) is False


class TestRegionEventService:
    """Test class for RegionEventService"""
    
    @pytest.fixture
    def mock_event_dispatcher(self):
        """Mock event dispatcher"""
        dispatcher = Mock()
        dispatcher.dispatch = AsyncMock()
        return dispatcher
    
    @pytest.fixture
    def region_event_service(self, mock_event_dispatcher):
        """Create RegionEventService with mocked dispatcher"""
        with patch('backend.systems.region.services.event_service.RegionEventService') as mock_dispatcher_class:
            mock_dispatcher_class.return_value = mock_event_dispatcher
            service = RegionEventService()
            service.event_dispatcher = mock_event_dispatcher
            return service
    
    @pytest.fixture
    def sample_region_data(self):
        """Sample region data for testing"""
        return {
            "region_id": str(uuid4()),
            "name": "Test Region",
            "region_type": "kingdom",
            "population": 5000,
            "continent_id": str(uuid4())
        }
    
    @pytest.mark.asyncio
    async def test_publish_region_created(self, region_event_service, mock_event_dispatcher, sample_region_data):
        """Test publishing region created event"""
        await region_event_service.publish_region_created(sample_region_data)
        
        mock_event_dispatcher.dispatch.assert_called_once()
        call_args = mock_event_dispatcher.dispatch.call_args[0][0]
        
        assert call_args.event_type == "RegionCreated"
        assert call_args.data["region_id"] == sample_region_data["region_id"]
        assert call_args.data["name"] == sample_region_data["name"]
    
    @pytest.mark.asyncio
    async def test_publish_region_updated(self, region_event_service, mock_event_dispatcher, sample_region_data):
        """Test publishing region updated event"""
        old_data = sample_region_data.copy()
        new_data = sample_region_data.copy()
        new_data["population"] = 7500
        new_data["name"] = "Updated Region"
        
        await region_event_service.publish_region_updated(old_data, new_data)
        
        mock_event_dispatcher.dispatch.assert_called_once()
        call_args = mock_event_dispatcher.dispatch.call_args[0][0]
        
        assert call_args.event_type == "RegionUpdated"
        assert call_args.data["region_id"] == sample_region_data["region_id"]
        assert call_args.data["old_data"]["population"] == 5000
        assert call_args.data["new_data"]["population"] == 7500
    
    @pytest.mark.asyncio
    async def test_publish_region_deleted(self, region_event_service, mock_event_dispatcher, sample_region_data):
        """Test publishing region deleted event"""
        await region_event_service.publish_region_deleted(sample_region_data)
        
        mock_event_dispatcher.dispatch.assert_called_once()
        call_args = mock_event_dispatcher.dispatch.call_args[0][0]
        
        assert call_args.event_type == "RegionDeleted"
        assert call_args.data["region_id"] == sample_region_data["region_id"]
        assert call_args.data["name"] == sample_region_data["name"]
    
    @pytest.mark.asyncio
    async def test_publish_character_entered_region(self, region_event_service, mock_event_dispatcher):
        """Test publishing character entered region event"""
        character_id = str(uuid4())
        region_id = str(uuid4())
        
        await region_event_service.publish_character_entered_region(character_id, region_id)
        
        mock_event_dispatcher.dispatch.assert_called_once()
        call_args = mock_event_dispatcher.dispatch.call_args[0][0]
        
        assert call_args.event_type == "CharacterEnteredRegion"
        assert call_args.data["character_id"] == character_id
        assert call_args.data["region_id"] == region_id
    
    @pytest.mark.asyncio
    async def test_publish_territory_claimed(self, region_event_service, mock_event_dispatcher):
        """Test publishing territory claimed event"""
        faction_id = str(uuid4())
        region_id = str(uuid4())
        territory_data = {
            "territory_name": "Northern Territories",
            "control_level": 0.8
        }
        
        await region_event_service.publish_territory_claimed(faction_id, region_id, territory_data)
        
        mock_event_dispatcher.dispatch.assert_called_once()
        call_args = mock_event_dispatcher.dispatch.call_args[0][0]
        
        assert call_args.event_type == "TerritoryClaimed"
        assert call_args.data["faction_id"] == faction_id
        assert call_args.data["region_id"] == region_id
        assert call_args.data["territory_data"]["territory_name"] == "Northern Territories"
    
    @pytest.mark.asyncio
    async def test_publish_resource_discovered(self, region_event_service, mock_event_dispatcher):
        """Test publishing resource discovered event"""
        region_id = str(uuid4())
        resource_data = {
            "resource_type": "gold",
            "abundance": 0.8,
            "location": {"q": 1, "r": 2}
        }
        
        await region_event_service.publish_resource_discovered(region_id, resource_data)
        
        mock_event_dispatcher.dispatch.assert_called_once()
        call_args = mock_event_dispatcher.dispatch.call_args[0][0]
        
        assert call_args.event_type == "ResourceDiscovered"
        assert call_args.data["region_id"] == region_id
        assert call_args.data["resource_data"]["resource_type"] == "gold"
    
    @pytest.mark.asyncio
    async def test_publish_environmental_change(self, region_event_service, mock_event_dispatcher):
        """Test publishing environmental change event"""
        region_id = str(uuid4())
        change_data = {
            "change_type": "climate_shift",
            "old_climate": "temperate",
            "new_climate": "continental",
            "cause": "magical_influence"
        }
        
        await region_event_service.publish_environmental_change(region_id, change_data)
        
        mock_event_dispatcher.dispatch.assert_called_once()
        call_args = mock_event_dispatcher.dispatch.call_args[0][0]
        
        assert call_args.event_type == "EnvironmentalChange"
        assert call_args.data["region_id"] == region_id
        assert call_args.data["change_data"]["change_type"] == "climate_shift"
    
    def test_event_service_singleton(self):
        """Test that RegionEventService follows singleton pattern"""
        service1 = RegionEventService()
        service2 = RegionEventService()
        
        assert service1 is service2
    
    @pytest.mark.asyncio
    async def test_error_handling_in_event_publishing(self, region_event_service, mock_event_dispatcher):
        """Test error handling when event publishing fails"""
        # Mock dispatcher to raise an exception
        mock_event_dispatcher.dispatch.side_effect = Exception("Event dispatch failed")
        
        sample_data = {"region_id": str(uuid4()), "name": "Test Region"}
        
        # Should not raise exception, but handle gracefully
        await region_event_service.publish_region_created(sample_data)
        
        # Verify the dispatch was attempted
        mock_event_dispatcher.dispatch.assert_called_once()


@pytest.mark.asyncio
async def test_services_integration():
    """Test integration between region services"""
    # Create mock repository
    mock_repository = AsyncMock()
    
    # Create services with mocked dependencies
    region_service = RegionService(repository=mock_repository)
    
    # Mock some basic behavior
    sample_region = RegionMetadata(
        id=uuid4(),
        name="Integration Test Region",
        description="A region for integration testing",
        region_type="kingdom",
        profile=RegionProfile(
            dominant_biome="temperate_forest",
            climate=ClimateType.TEMPERATE
        ),
        population=1000,
        hex_coordinates=[HexCoordinate(0, 0)],
        danger_level=DangerLevel.SAFE
    )
    
    mock_repository.create.return_value = sample_region
    mock_repository.get_by_id.return_value = sample_region
    
    # Test integration workflow
    created_region = await region_service.create_region({
        "name": "Integration Test Region",
        "description": "A region for integration testing"
    })
    
    assert created_region.name == "Integration Test Region"
    mock_repository.create.assert_called_once()
    
    # Test retrieval
    retrieved_region = await region_service.get_region_by_id(created_region.id)
    assert retrieved_region.id == created_region.id
    mock_repository.get_by_id.assert_called_once_with(created_region.id)
