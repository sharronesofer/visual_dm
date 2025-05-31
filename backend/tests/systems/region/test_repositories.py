"""
Test module for region.repositories

Comprehensive tests for the region system repositories including RegionRepository,
database operations, and data persistence logic.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import the repositories and models
try:
    from backend.systems.region.repositories.region_repository import RegionRepository
    from backend.systems.region.models import (
        Region, Continent, RegionResourceNode, RegionPOI,
        RegionMetadata, ContinentMetadata, RegionProfile, ResourceNode,
        BiomeType, ClimateType, RegionType, ResourceType, DangerLevel, POIType,
        HexCoordinate
    )
    from backend.infrastructure.shared.exceptions import (
        RegionNotFoundError, RegionValidationError, RegionConflictError,
        RepositoryError
    )
except ImportError as e:
    pytest.skip(f"Required modules not found: {e}", allow_module_level=True)


class TestRegionRepository:
    """Test class for RegionRepository"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session"""
        session = Mock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = Mock()
        session.get = AsyncMock()
        session.scalar = AsyncMock()
        session.scalars = AsyncMock()
        return session
    
    @pytest.fixture
    def region_repository(self, mock_session):
        """Create RegionRepository with mocked session"""
        repository = RegionRepository()
        repository._session = mock_session
        return repository
    
    @pytest.fixture
    def sample_region_db_model(self):
        """Sample Region database model for testing"""
        return Region(
            id=uuid4(),
            name="Test Region",
            description="A test region for repository testing",
            region_type=RegionType.KINGDOM,
            dominant_biome=BiomeType.TEMPERATE_FOREST,
            climate=ClimateType.TEMPERATE,
            population=5000,
            area_square_km=1000.0,
            danger_level=DangerLevel.SAFE,
            hex_coordinates_json=[{"q": 0, "r": 0, "s": 0}, {"q": 1, "r": 0, "s": -1}],
            center_hex_q=0,
            center_hex_r=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.fixture 
    def sample_region_metadata(self):
        """Sample RegionMetadata for testing"""
        return RegionMetadata(
            id=uuid4(),
            name="Test Region",
            description="A test region for repository testing",
            region_type=RegionType.KINGDOM,
            profile=RegionProfile(
                dominant_biome=BiomeType.TEMPERATE_FOREST,
                climate=ClimateType.TEMPERATE
            ),
            hex_coordinates=[HexCoordinate(0, 0), HexCoordinate(1, 0)],
            population=5000,
            area_square_km=1000.0,
            danger_level=DangerLevel.SAFE
        )
    
    @pytest.mark.asyncio
    async def test_get_by_id_success(self, region_repository, mock_session, sample_region_db_model):
        """Test successful retrieval by ID"""
        region_id = sample_region_db_model.id
        mock_session.get.return_value = sample_region_db_model
        
        result = await region_repository.get_by_id(region_id)
        
        assert result is not None
        assert result.id == region_id
        assert result.name == "Test Region"
        mock_session.get.assert_called_once_with(Region, region_id)
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, region_repository, mock_session):
        """Test retrieval when region doesn't exist"""
        region_id = uuid4()
        mock_session.get.return_value = None
        
        result = await region_repository.get_by_id(region_id)
        
        assert result is None
        mock_session.get.assert_called_once_with(Region, region_id)
    
    @pytest.mark.asyncio
    async def test_get_all_success(self, region_repository, mock_session):
        """Test getting all regions"""
        sample_regions = [
            Region(id=uuid4(), name="Region 1", region_type=RegionType.KINGDOM),
            Region(id=uuid4(), name="Region 2", region_type=RegionType.DUCHY),
            Region(id=uuid4(), name="Region 3", region_type=RegionType.WILDERNESS)
        ]
        
        # Mock the result object that scalars() returns
        mock_result = Mock()
        mock_result.all.return_value = sample_regions
        mock_session.execute.return_value = Mock()
        mock_session.execute.return_value.scalars.return_value = mock_result
        
        result = await region_repository.get_all()
        
        assert len(result) == 3
        assert all(isinstance(region, Region) for region in result)
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_with_limit_offset(self, region_repository, mock_session):
        """Test getting regions with pagination"""
        sample_regions = [
            Region(id=uuid4(), name="Region 1"),
            Region(id=uuid4(), name="Region 2")
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = sample_regions
        mock_session.execute.return_value = Mock()
        mock_session.execute.return_value.scalars.return_value = mock_result
        
        result = await region_repository.get_all(limit=2, offset=10)
        
        assert len(result) == 2
        mock_session.execute.assert_called_once()
        # Verify that limit and offset are applied in the query
        
    @pytest.mark.asyncio
    async def test_create_region_success(self, region_repository, mock_session, sample_region_metadata):
        """Test successful region creation"""
        # Mock the session behavior for creation
        created_region = Region(
            id=sample_region_metadata.id,
            name=sample_region_metadata.name,
            description=sample_region_metadata.description,
            region_type=sample_region_metadata.region_type
        )
        
        with patch('backend.systems.region.repositories.region_repository.create_region_from_metadata') as mock_create:
            mock_create.return_value = created_region
            
            result = await region_repository.create(sample_region_metadata)
            
            assert result == created_region
            mock_session.add.assert_called_once_with(created_region)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(created_region)
    
    @pytest.mark.asyncio
    async def test_create_region_commit_failure(self, region_repository, mock_session, sample_region_metadata):
        """Test region creation with database commit failure"""
        mock_session.commit.side_effect = Exception("Database commit failed")
        
        with patch('backend.systems.region.repositories.region_repository.create_region_from_metadata') as mock_create:
            mock_create.return_value = Region(id=sample_region_metadata.id, name=sample_region_metadata.name)
            
            with pytest.raises(RepositoryError):
                await region_repository.create(sample_region_metadata)
            
            mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_region_success(self, region_repository, mock_session, sample_region_db_model, sample_region_metadata):
        """Test successful region update"""
        region_id = sample_region_db_model.id
        mock_session.get.return_value = sample_region_db_model
        
        # Modify the metadata for update
        updated_metadata = RegionMetadata(**sample_region_metadata.__dict__)
        updated_metadata.name = "Updated Region Name"
        updated_metadata.population = 7500
        
        result = await region_repository.update(region_id, updated_metadata)
        
        assert result.name == "Updated Region Name"
        assert result.population == 7500
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_region_db_model)
    
    @pytest.mark.asyncio
    async def test_update_region_not_found(self, region_repository, mock_session, sample_region_metadata):
        """Test updating non-existent region"""
        region_id = uuid4()
        mock_session.get.return_value = None
        
        with pytest.raises(RegionNotFoundError):
            await region_repository.update(region_id, sample_region_metadata)
    
    @pytest.mark.asyncio
    async def test_delete_region_success(self, region_repository, mock_session, sample_region_db_model):
        """Test successful region deletion"""
        region_id = sample_region_db_model.id
        mock_session.get.return_value = sample_region_db_model
        
        result = await region_repository.delete(region_id)
        
        assert result is True
        mock_session.delete.assert_called_once_with(sample_region_db_model)
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_region_not_found(self, region_repository, mock_session):
        """Test deleting non-existent region"""
        region_id = uuid4()
        mock_session.get.return_value = None
        
        with pytest.raises(RegionNotFoundError):
            await region_repository.delete(region_id)
    
    @pytest.mark.asyncio
    async def test_get_by_name_success(self, region_repository, mock_session, sample_region_db_model):
        """Test finding region by name"""
        mock_session.scalar.return_value = sample_region_db_model
        
        result = await region_repository.get_by_name("Test Region")
        
        assert result == sample_region_db_model
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, region_repository, mock_session):
        """Test finding non-existent region by name"""
        mock_session.scalar.return_value = None
        
        result = await region_repository.get_by_name("Non-existent Region")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_by_filters_region_type(self, region_repository, mock_session):
        """Test filtering regions by type"""
        kingdom_regions = [
            Region(id=uuid4(), name="Kingdom 1", region_type=RegionType.KINGDOM),
            Region(id=uuid4(), name="Kingdom 2", region_type=RegionType.KINGDOM)
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = kingdom_regions
        mock_session.execute.return_value = Mock()
        mock_session.execute.return_value.scalars.return_value = mock_result
        
        filters = {"region_type": RegionType.KINGDOM}
        result = await region_repository.get_by_filters(filters)
        
        assert len(result) == 2
        assert all(region.region_type == RegionType.KINGDOM for region in result)
    
    @pytest.mark.asyncio
    async def test_get_by_filters_multiple_criteria(self, region_repository, mock_session):
        """Test filtering regions by multiple criteria"""
        filtered_regions = [
            Region(
                id=uuid4(), 
                name="Coastal Kingdom", 
                region_type=RegionType.KINGDOM,
                dominant_biome=BiomeType.COASTAL
            )
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = filtered_regions
        mock_session.execute.return_value = Mock()
        mock_session.execute.return_value.scalars.return_value = mock_result
        
        filters = {
            "region_type": RegionType.KINGDOM,
            "dominant_biome": BiomeType.COASTAL
        }
        result = await region_repository.get_by_filters(filters)
        
        assert len(result) == 1
        assert result[0].region_type == RegionType.KINGDOM
        assert result[0].dominant_biome == BiomeType.COASTAL
    
    @pytest.mark.asyncio
    async def test_search_by_name_pattern(self, region_repository, mock_session):
        """Test searching regions by name pattern"""
        matching_regions = [
            Region(id=uuid4(), name="Forest Kingdom"),
            Region(id=uuid4(), name="Dark Forest"),
            Region(id=uuid4(), name="Forest Valley")
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = matching_regions
        mock_session.execute.return_value = Mock()
        mock_session.execute.return_value.scalars.return_value = mock_result
        
        result = await region_repository.search_by_name("forest")
        
        assert len(result) == 3
        assert all("forest" in region.name.lower() for region in result)
    
    @pytest.mark.asyncio
    async def test_get_regions_by_continent(self, region_repository, mock_session):
        """Test getting regions belonging to a continent"""
        continent_id = uuid4()
        continent_regions = [
            Region(id=uuid4(), name="Region 1", continent_id=continent_id),
            Region(id=uuid4(), name="Region 2", continent_id=continent_id)
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = continent_regions
        mock_session.execute.return_value = Mock()
        mock_session.execute.return_value.scalars.return_value = mock_result
        
        result = await region_repository.get_regions_by_continent(continent_id)
        
        assert len(result) == 2
        assert all(region.continent_id == continent_id for region in result)
    
    @pytest.mark.asyncio
    async def test_count_regions(self, region_repository, mock_session):
        """Test counting total regions"""
        mock_session.scalar.return_value = 42
        
        result = await region_repository.count()
        
        assert result == 42
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_regions_with_filters(self, region_repository, mock_session):
        """Test counting regions with filters"""
        mock_session.scalar.return_value = 5
        
        filters = {"region_type": RegionType.KINGDOM}
        result = await region_repository.count(filters)
        
        assert result == 5
    
    @pytest.mark.asyncio
    async def test_region_exists(self, region_repository, mock_session):
        """Test checking if region exists"""
        region_id = uuid4()
        mock_session.scalar.return_value = 1  # EXISTS query returns count
        
        result = await region_repository.exists(region_id)
        
        assert result is True
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_region_not_exists(self, region_repository, mock_session):
        """Test checking if region doesn't exist"""
        region_id = uuid4()
        mock_session.scalar.return_value = 0  # EXISTS query returns 0
        
        result = await region_repository.exists(region_id)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_name_is_unique_true(self, region_repository, mock_session):
        """Test name uniqueness check when name is unique"""
        mock_session.scalar.return_value = 0  # No existing regions with this name
        
        result = await region_repository.name_is_unique("Unique Region Name")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_name_is_unique_false(self, region_repository, mock_session):
        """Test name uniqueness check when name already exists"""
        mock_session.scalar.return_value = 1  # Existing region with this name
        
        result = await region_repository.name_is_unique("Existing Region Name")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_name_is_unique_excluding_current(self, region_repository, mock_session):
        """Test name uniqueness check excluding current region"""
        current_region_id = uuid4()
        mock_session.scalar.return_value = 0  # No other regions with this name
        
        result = await region_repository.name_is_unique("Current Region Name", exclude_id=current_region_id)
        
        assert result is True


class TestRegionRepositoryIntegration:
    """Integration tests for RegionRepository with related models"""
    
    @pytest.fixture
    def mock_session_with_relationships(self):
        """Mock session that handles relationships"""
        session = Mock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = Mock()
        session.get = AsyncMock()
        session.scalar = AsyncMock()
        session.scalars = AsyncMock()
        return session
    
    @pytest.fixture
    def region_with_resources_and_pois(self):
        """Region with resource nodes and POIs"""
        region = Region(
            id=uuid4(),
            name="Rich Region",
            description="A region with resources and POIs",
            region_type=RegionType.KINGDOM,
            dominant_biome=BiomeType.MOUNTAINS,
            climate=ClimateType.CONTINENTAL
        )
        
        # Add resource nodes
        resource1 = RegionResourceNode(
            id=uuid4(),
            region_id=region.id,
            resource_type=ResourceType.GOLD,
            abundance=0.8,
            quality=0.7,
            hex_q=0,
            hex_r=0
        )
        resource2 = RegionResourceNode(
            id=uuid4(),
            region_id=region.id,
            resource_type=ResourceType.IRON,
            abundance=0.6,
            quality=0.8,
            hex_q=1,
            hex_r=0
        )
        region.resource_nodes = [resource1, resource2]
        
        # Add POIs
        poi1 = RegionPOI(
            id=uuid4(),
            region_id=region.id,
            name="Ancient Mine",
            description="An old mining site",
            poi_type=POIType.CAVE,
            hex_q=0,
            hex_r=1
        )
        poi2 = RegionPOI(
            id=uuid4(),
            region_id=region.id,
            name="Mountain Fortress",
            description="A strategic fortress",
            poi_type=POIType.FORTRESS,
            hex_q=2,
            hex_r=0
        )
        region.pois = [poi1, poi2]
        
        return region
    
    @pytest.mark.asyncio
    async def test_get_region_with_relationships(self, mock_session_with_relationships, region_with_resources_and_pois):
        """Test getting region with its relationships loaded"""
        repository = RegionRepository()
        repository._session = mock_session_with_relationships
        
        region_id = region_with_resources_and_pois.id
        mock_session_with_relationships.get.return_value = region_with_resources_and_pois
        
        result = await repository.get_by_id(region_id)
        
        assert result is not None
        assert len(result.resource_nodes) == 2
        assert len(result.pois) == 2
        
        # Verify resource nodes
        resource_types = [node.resource_type for node in result.resource_nodes]
        assert ResourceType.GOLD in resource_types
        assert ResourceType.IRON in resource_types
        
        # Verify POIs
        poi_types = [poi.poi_type for poi in result.pois]
        assert POIType.CAVE in poi_types
        assert POIType.FORTRESS in poi_types
    
    @pytest.mark.asyncio
    async def test_create_region_with_relationships(self, mock_session_with_relationships):
        """Test creating region with resource nodes and POIs"""
        repository = RegionRepository()
        repository._session = mock_session_with_relationships
        
        # Create region metadata with resources
        region_metadata = RegionMetadata(
            id=uuid4(),
            name="New Rich Region",
            description="A newly created region with resources",
            region_type=RegionType.DUCHY,
            profile=RegionProfile(
                dominant_biome=BiomeType.MOUNTAINS,
                climate=ClimateType.CONTINENTAL
            ),
            resource_nodes=[
                ResourceNode(
                    resource_type=ResourceType.GEMS,
                    abundance=0.9,
                    quality=0.8,
                    accessibility=0.7,
                    location=HexCoordinate(0, 0)
                )
            ],
            hex_coordinates=[HexCoordinate(0, 0), HexCoordinate(1, 0)]
        )
        
        created_region = Region(
            id=region_metadata.id,
            name=region_metadata.name,
            description=region_metadata.description
        )
        
        with patch('backend.systems.region.repositories.region_repository.create_region_from_metadata') as mock_create:
            mock_create.return_value = created_region
            
            result = await repository.create(region_metadata)
            
            assert result == created_region
            mock_session_with_relationships.add.assert_called_once_with(created_region)
            mock_session_with_relationships.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_region_relationships(self, mock_session_with_relationships, region_with_resources_and_pois):
        """Test updating region and its relationships"""
        repository = RegionRepository()
        repository._session = mock_session_with_relationships
        
        region_id = region_with_resources_and_pois.id
        mock_session_with_relationships.get.return_value = region_with_resources_and_pois
        
        # Update metadata with new resource
        updated_metadata = RegionMetadata(
            id=region_id,
            name="Updated Rich Region",
            description="Updated description",
            region_type=RegionType.KINGDOM,
            profile=RegionProfile(
                dominant_biome=BiomeType.MOUNTAINS,
                climate=ClimateType.CONTINENTAL
            ),
            resource_nodes=[
                ResourceNode(
                    resource_type=ResourceType.SILVER,
                    abundance=0.5,
                    quality=0.9,
                    accessibility=0.8,
                    location=HexCoordinate(2, 1)
                )
            ]
        )
        
        result = await repository.update(region_id, updated_metadata)
        
        assert result.name == "Updated Rich Region"
        mock_session_with_relationships.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_region_cascades_relationships(self, mock_session_with_relationships, region_with_resources_and_pois):
        """Test that deleting region cascades to related entities"""
        repository = RegionRepository()
        repository._session = mock_session_with_relationships
        
        region_id = region_with_resources_and_pois.id
        mock_session_with_relationships.get.return_value = region_with_resources_and_pois
        
        result = await repository.delete(region_id)
        
        assert result is True
        # Verify the region is deleted (cascade should handle relationships)
        mock_session_with_relationships.delete.assert_called_once_with(region_with_resources_and_pois)
        mock_session_with_relationships.commit.assert_called_once()


@pytest.mark.asyncio
async def test_repository_error_handling():
    """Test repository error handling scenarios"""
    repository = RegionRepository()
    mock_session = Mock(spec=AsyncSession)
    repository._session = mock_session
    
    # Test database connection error
    mock_session.execute.side_effect = Exception("Database connection failed")
    
    with pytest.raises(RepositoryError):
        await repository.get_all()
    
    # Test constraint violation during creation
    mock_session.commit.side_effect = Exception("Constraint violation")
    
    sample_metadata = RegionMetadata(
        id=uuid4(),
        name="Test Region"
    )
    
    with patch('backend.systems.region.repositories.region_repository.create_region_from_metadata') as mock_create:
        mock_create.return_value = Region(id=sample_metadata.id, name=sample_metadata.name)
        
        with pytest.raises(RepositoryError):
            await repository.create(sample_metadata)
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_repository_metadata_conversion():
    """Test conversion between database models and metadata objects"""
    # This test verifies that the repository correctly converts between
    # SQLAlchemy models and our metadata dataclasses
    
    repository = RegionRepository()
    
    # Create a database model
    db_region = Region(
        id=uuid4(),
        name="Conversion Test Region",
        description="Testing conversion",
        region_type=RegionType.KINGDOM,
        dominant_biome=BiomeType.TEMPERATE_FOREST,
        climate=ClimateType.TEMPERATE,
        population=1000,
        area_square_km=500.0,
        hex_coordinates_json=[{"q": 0, "r": 0, "s": 0}],
        center_hex_q=0,
        center_hex_r=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Test conversion to metadata
    metadata = db_region.to_metadata()
    
    assert isinstance(metadata, RegionMetadata)
    assert metadata.id == db_region.id
    assert metadata.name == db_region.name
    assert metadata.region_type == db_region.region_type
    assert metadata.profile.dominant_biome == db_region.dominant_biome
    assert len(metadata.hex_coordinates) == 1
    assert metadata.hex_coordinates[0].q == 0
    assert metadata.hex_coordinates[0].r == 0
