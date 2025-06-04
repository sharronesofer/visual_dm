"""
Integration tests for Region Business Services
Tests business logic flows and error cases
"""
import pytest
from uuid import uuid4, UUID
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, MagicMock

# Import business services
from backend.systems.region.services.services import (
    RegionBusinessService, ContinentBusinessService,
    RegionValidationService, WorldGenerationService
)

# Import models
from backend.systems.region.models import (
    RegionMetadata, ContinentMetadata, RegionProfile, ClimateType, DangerLevel
)


class MockRegionRepository:
    """Mock repository for testing business service logic"""
    
    def __init__(self):
        self.regions = {}
        self.next_id = 1
    
    def get_by_id(self, region_id: UUID) -> Optional[RegionMetadata]:
        return self.regions.get(str(region_id))
    
    def get_by_name(self, name: str) -> Optional[RegionMetadata]:
        for region in self.regions.values():
            if region.name == name:
                return region
        return None
    
    def create(self, region_data: RegionMetadata) -> RegionMetadata:
        self.regions[str(region_data.id)] = region_data
        return region_data
    
    def update(self, region_id: UUID, update_data: Dict[str, Any]) -> Optional[RegionMetadata]:
        region = self.regions.get(str(region_id))
        if not region:
            return None
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(region, key):
                setattr(region, key, value)
        
        return region
    
    def delete(self, region_id: UUID) -> bool:
        region_key = str(region_id)
        if region_key in self.regions:
            del self.regions[region_key]
            return True
        return False
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[RegionMetadata]:
        regions = list(self.regions.values())
        return regions[offset:offset + limit]
    
    def get_by_filters(self, filters: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[RegionMetadata]:
        filtered_regions = []
        for region in self.regions.values():
            match = True
            
            if 'continent_id' in filters and region.continent_id != filters['continent_id']:
                match = False
            if 'region_type' in filters and region.region_type != filters['region_type']:
                match = False
            if 'dominant_biome' in filters and region.profile.dominant_biome != filters['dominant_biome']:
                match = False
            if 'min_population' in filters and region.population < filters['min_population']:
                match = False
            if 'max_population' in filters and region.population > filters['max_population']:
                match = False
            
            if match:
                filtered_regions.append(region)
        
        return filtered_regions[offset:offset + limit]
    
    def search_by_name(self, search_term: str, limit: int = 50) -> List[RegionMetadata]:
        matching_regions = []
        search_lower = search_term.lower()
        
        for region in self.regions.values():
            if search_lower in region.name.lower():
                matching_regions.append(region)
        
        return matching_regions[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_regions": len(self.regions),
            "total_population": sum(r.population for r in self.regions.values())
        }


class MockContinentRepository:
    """Mock continent repository for testing"""
    
    def __init__(self):
        self.continents = {}
    
    def get_by_id(self, continent_id: UUID) -> Optional[ContinentMetadata]:
        return self.continents.get(str(continent_id))
    
    def get_by_name(self, name: str) -> Optional[ContinentMetadata]:
        for continent in self.continents.values():
            if continent.name == name:
                return continent
        return None
    
    def create(self, continent_data: ContinentMetadata) -> ContinentMetadata:
        self.continents[str(continent_data.id)] = continent_data
        return continent_data
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[ContinentMetadata]:
        continents = list(self.continents.values())
        return continents[offset:offset + limit]
    
    def update(self, continent_id: UUID, update_data: Dict[str, Any]) -> Optional[ContinentMetadata]:
        continent = self.continents.get(str(continent_id))
        if not continent:
            return None
        
        for key, value in update_data.items():
            if hasattr(continent, key):
                setattr(continent, key, value)
        
        return continent
    
    def delete(self, continent_id: UUID) -> bool:
        continent_key = str(continent_id)
        if continent_key in self.continents:
            del self.continents[continent_key]
            return True
        return False


@pytest.fixture
def mock_region_repository():
    return MockRegionRepository()


@pytest.fixture
def mock_continent_repository():
    return MockContinentRepository()


@pytest.fixture
def region_service(mock_region_repository):
    return RegionBusinessService(
        repository=mock_region_repository,
        validation_service=RegionValidationService()
    )


@pytest.fixture
def continent_service(mock_continent_repository):
    return ContinentBusinessService(repository=mock_continent_repository)


class TestRegionBusinessService:
    """Test RegionBusinessService business logic"""
    
    def test_create_region_success(self, region_service):
        """Test successful region creation"""
        create_data = {
            "name": "Test Region",
            "description": "A test region",
            "region_type": "wilderness",
            "dominant_biome": "temperate_forest",
            "climate": "temperate",
            "population": 1000
        }
        
        region = region_service.create_region(create_data)
        
        assert region.name == "Test Region"
        assert region.description == "A test region"
        assert region.region_type == "wilderness"
        assert region.profile.dominant_biome == "temperate_forest"
        assert region.population == 1000
        assert region.id is not None
    
    def test_create_region_duplicate_name_fails(self, region_service):
        """Test that creating a region with duplicate name fails"""
        create_data = {
            "name": "Duplicate Region",
            "region_type": "wilderness",
            "dominant_biome": "temperate_forest",
            "climate": "temperate"
        }
        
        # Create first region
        region_service.create_region(create_data)
        
        # Attempt to create second region with same name should fail
        with pytest.raises(ValueError, match="Region with name 'Duplicate Region' already exists"):
            region_service.create_region(create_data)
    
    def test_create_region_validation_errors(self, region_service):
        """Test region creation validation errors"""
        # Test missing name
        with pytest.raises(ValueError):
            region_service.create_region({})
        
        # Test invalid region type
        with pytest.raises(ValueError):
            region_service.create_region({
                "name": "Test",
                "region_type": "invalid_type"
            })
    
    def test_get_region_by_id_success(self, region_service):
        """Test successful region retrieval by ID"""
        create_data = {
            "name": "Test Region",
            "region_type": "wilderness",
            "dominant_biome": "temperate_forest",
            "climate": "temperate"
        }
        
        created_region = region_service.create_region(create_data)
        retrieved_region = region_service.get_region_by_id(created_region.id)
        
        assert retrieved_region.id == created_region.id
        assert retrieved_region.name == "Test Region"
    
    def test_get_region_by_id_not_found(self, region_service):
        """Test region retrieval with non-existent ID"""
        non_existent_id = uuid4()
        
        with pytest.raises(ValueError, match=f"Region {non_existent_id} not found"):
            region_service.get_region_by_id(non_existent_id)
    
    def test_update_region_success(self, region_service):
        """Test successful region update"""
        # Create region
        create_data = {
            "name": "Original Name",
            "region_type": "wilderness",
            "population": 1000
        }
        region = region_service.create_region(create_data)
        
        # Update region
        update_data = {
            "name": "Updated Name",
            "population": 2000
        }
        updated_region = region_service.update_region(region.id, update_data)
        
        assert updated_region.name == "Updated Name"
        assert updated_region.population == 2000
        assert updated_region.region_type == "wilderness"  # Unchanged
    
    def test_update_region_not_found(self, region_service):
        """Test updating non-existent region"""
        non_existent_id = uuid4()
        
        with pytest.raises(ValueError, match=f"Region {non_existent_id} not found"):
            region_service.update_region(non_existent_id, {"name": "New Name"})
    
    def test_update_region_validation_errors(self, region_service):
        """Test region update validation"""
        # Create region
        region = region_service.create_region({
            "name": "Test Region",
            "region_type": "wilderness"
        })
        
        # Test negative population
        with pytest.raises(ValueError, match="Population cannot be negative"):
            region_service.update_region(region.id, {"population": -100})
        
        # Test name too long
        with pytest.raises(ValueError, match="Region name must be 255 characters or less"):
            region_service.update_region(region.id, {"name": "x" * 300})
    
    def test_delete_region_success(self, region_service):
        """Test successful region deletion"""
        region = region_service.create_region({
            "name": "Test Region",
            "region_type": "wilderness"
        })
        
        success = region_service.delete_region(region.id)
        assert success is True
        
        # Verify region is deleted
        with pytest.raises(ValueError):
            region_service.get_region_by_id(region.id)
    
    def test_delete_region_not_found(self, region_service):
        """Test deleting non-existent region"""
        non_existent_id = uuid4()
        
        with pytest.raises(ValueError, match=f"Region {non_existent_id} not found"):
            region_service.delete_region(non_existent_id)
    
    def test_get_regions_all(self, region_service):
        """Test getting all regions"""
        # Create multiple regions
        for i in range(3):
            region_service.create_region({
                "name": f"Region {i}",
                "region_type": "wilderness"
            })
        
        regions = region_service.get_regions()
        assert len(regions) == 3
    
    def test_get_regions_with_filters(self, region_service):
        """Test getting regions with filters"""
        continent_id = uuid4()
        
        # Create regions with different properties
        region_service.create_region({
            "name": "Forest Region",
            "region_type": "wilderness",
            "dominant_biome": "temperate_forest",
            "continent_id": str(continent_id),
            "population": 1000
        })
        
        region_service.create_region({
            "name": "Desert Region",
            "region_type": "wasteland",
            "dominant_biome": "desert",
            "population": 500
        })
        
        # Test continent filter
        filtered = region_service.get_regions({"continent_id": continent_id})
        assert len(filtered) == 1
        assert filtered[0].name == "Forest Region"
        
        # Test region type filter
        filtered = region_service.get_regions({"region_type": "wasteland"})
        assert len(filtered) == 1
        assert filtered[0].name == "Desert Region"
        
        # Test population filter
        filtered = region_service.get_regions({"min_population": 750})
        assert len(filtered) == 1
        assert filtered[0].name == "Forest Region"
    
    def test_search_regions_by_name(self, region_service):
        """Test searching regions by name"""
        # Create regions
        region_service.create_region({
            "name": "Northern Forest",
            "region_type": "wilderness"
        })
        
        region_service.create_region({
            "name": "Southern Desert",
            "region_type": "wasteland"
        })
        
        region_service.create_region({
            "name": "Eastern Forest",
            "region_type": "wilderness"
        })
        
        # Search for "Forest"
        results = region_service.search_regions_by_name("Forest")
        assert len(results) == 2
        region_names = [r.name for r in results]
        assert "Northern Forest" in region_names
        assert "Eastern Forest" in region_names
        
        # Search for "Desert"
        results = region_service.search_regions_by_name("Desert")
        assert len(results) == 1
        assert results[0].name == "Southern Desert"


class TestContinentBusinessService:
    """Test ContinentBusinessService business logic"""
    
    def test_create_continent_success(self, continent_service):
        """Test successful continent creation"""
        continent = continent_service.create_continent(
            name="Test Continent",
            description="A test continent"
        )
        
        assert continent.name == "Test Continent"
        assert continent.description == "A test continent"
        assert continent.id is not None
    
    def test_create_continent_duplicate_name_fails(self, continent_service):
        """Test that creating continent with duplicate name fails"""
        continent_service.create_continent("Duplicate Continent")
        
        with pytest.raises(ValueError, match="Continent with name 'Duplicate Continent' already exists"):
            continent_service.create_continent("Duplicate Continent")
    
    def test_get_continent_by_id_success(self, continent_service):
        """Test successful continent retrieval"""
        created = continent_service.create_continent("Test Continent")
        retrieved = continent_service.get_continent_by_id(created.id)
        
        assert retrieved.id == created.id
        assert retrieved.name == "Test Continent"
    
    def test_get_continent_by_id_not_found(self, continent_service):
        """Test continent retrieval with non-existent ID"""
        non_existent_id = uuid4()
        
        with pytest.raises(ValueError, match=f"Continent {non_existent_id} not found"):
            continent_service.get_continent_by_id(non_existent_id)
    
    def test_get_all_continents(self, continent_service):
        """Test getting all continents"""
        # Create multiple continents
        for i in range(3):
            continent_service.create_continent(f"Continent {i}")
        
        continents = continent_service.get_all_continents()
        assert len(continents) == 3
    
    def test_update_continent_success(self, continent_service):
        """Test successful continent update"""
        continent = continent_service.create_continent("Original Name")
        
        updated = continent_service.update_continent(continent.id, {
            "name": "Updated Name",
            "description": "Updated description"
        })
        
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
    
    def test_update_continent_not_found(self, continent_service):
        """Test updating non-existent continent"""
        non_existent_id = uuid4()
        
        with pytest.raises(ValueError, match=f"Continent {non_existent_id} not found"):
            continent_service.update_continent(non_existent_id, {"name": "New Name"})
    
    def test_delete_continent_success(self, continent_service):
        """Test successful continent deletion"""
        continent = continent_service.create_continent("Test Continent")
        
        success = continent_service.delete_continent(continent.id)
        assert success is True
        
        # Verify continent is deleted
        with pytest.raises(ValueError):
            continent_service.get_continent_by_id(continent.id)
    
    def test_delete_continent_not_found(self, continent_service):
        """Test deleting non-existent continent"""
        non_existent_id = uuid4()
        
        with pytest.raises(ValueError, match=f"Continent {non_existent_id} not found"):
            continent_service.delete_continent(non_existent_id)


class TestRegionValidationService:
    """Test RegionValidationService business rules"""
    
    def test_validate_region_data_success(self):
        """Test successful validation"""
        validation_service = RegionValidationService()
        
        data = {
            "name": "Valid Region",
            "region_type": "wilderness",
            "dominant_biome": "temperate_forest",
            "climate": "temperate"
        }
        
        validated = validation_service.validate_region_data(data)
        assert validated["name"] == "Valid Region"
        assert validated["region_type"] == "wilderness"
    
    def test_validate_region_data_missing_name(self):
        """Test validation with missing name"""
        validation_service = RegionValidationService()
        
        with pytest.raises(ValueError, match="Region name is required"):
            validation_service.validate_region_data({})
    
    def test_validate_region_data_invalid_types(self):
        """Test validation with invalid types"""
        validation_service = RegionValidationService()
        
        # Invalid region type
        with pytest.raises(ValueError, match="Invalid region_type"):
            validation_service.validate_region_data({
                "name": "Test",
                "region_type": "invalid_type"
            })
        
        # Invalid biome
        with pytest.raises(ValueError, match="Invalid dominant_biome"):
            validation_service.validate_region_data({
                "name": "Test",
                "dominant_biome": "invalid_biome"
            })
        
        # Invalid climate
        with pytest.raises(ValueError, match="Invalid climate"):
            validation_service.validate_region_data({
                "name": "Test",
                "climate": "invalid_climate"
            })


class TestBusinessServiceIntegration:
    """Test integration between region and continent services"""
    
    def test_region_continent_relationship(self, region_service, continent_service):
        """Test region-continent relationship through business services"""
        # Create continent
        continent = continent_service.create_continent("Test Continent")
        
        # Create region in continent
        region = region_service.create_region({
            "name": "Test Region",
            "region_type": "wilderness",
            "continent_id": str(continent.id)
        })
        
        # Verify relationship
        assert region.continent_id == continent.id
        
        # Get regions by continent
        regions_in_continent = region_service.get_regions_by_continent(continent.id)
        assert len(regions_in_continent) == 1
        assert regions_in_continent[0].id == region.id 