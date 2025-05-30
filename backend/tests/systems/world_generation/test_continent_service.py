from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
"""
Tests for continent_service module.

Comprehensive tests for continent creation, management, and business logic.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from uuid import uuid4

from backend.systems.world_generation.continent_service import (
    ContinentService,
    continent_service,
)
from backend.systems.world_generation.models import (
    ContinentSchema,
    ContinentBoundarySchema,
    CoordinateSchema,
    ContinentCreationRequestSchema,
)


class TestContinentService: pass
    """Test suite for ContinentService class."""

    @pytest.fixture
    def mock_repository(self): pass
        """Mock continent repository."""
        return Mock()

    @pytest.fixture
    def mock_region_service(self): pass
        """Mock region service."""
        return Mock()

    @pytest.fixture
    def continent_svc(self, mock_repository, mock_region_service): pass
        """Create ContinentService instance with mocked dependencies."""
        return ContinentService(mock_repository, mock_region_service)

    @pytest.fixture
    def sample_creation_request(self): pass
        """Sample continent creation request."""
        return ContinentCreationRequestSchema(
            name="Test Continent",
            num_regions_target=60,
            seed="test_seed_123",
            metadata={"test_key": "test_value"}
        )

    @pytest.fixture
    def sample_continent_schema(self): pass
        """Sample continent schema."""
        return ContinentSchema(
            continent_id="test_continent_id",
            name="Test Continent",
            seed="test_seed",
            region_coordinates=[
                CoordinateSchema(x=0, y=0),
                CoordinateSchema(x=1, y=1)
            ],
            region_ids=["region1", "region2"],
            origin_coordinate=CoordinateSchema(x=0, y=0),
            boundary=ContinentBoundarySchema(min_x=0, max_x=1, min_y=0, max_y=1),
            creation_timestamp=datetime.utcnow(),
            num_regions=2,
            metadata={"test": "data"}
        )

    @patch('backend.systems.world_generation.continent_service.RegionCreationSchema')
    @patch('backend.systems.world_generation.continent_service.uuid4')
    @patch('backend.systems.world_generation.continent_service.random')
    @patch('backend.systems.world_generation.continent_service.generate_continent_region_coordinates')
    @patch('backend.systems.world_generation.continent_service.get_continent_boundary')
    @patch('backend.systems.world_generation.continent_service.datetime')
    def test_create_new_continent_success(self, mock_datetime, mock_boundary, 
                                        mock_coords, mock_random, mock_uuid4, 
                                        mock_region_schema, continent_svc, sample_creation_request): pass
        """Test successful continent creation."""
        # Setup mocks
        mock_uuid4.return_value = Mock(hex="test_continent_id")
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1)
        mock_coords.return_value = [
            CoordinateSchema(x=0, y=0),
            CoordinateSchema(x=1, y=1)
        ]
        mock_boundary.return_value = [0, 1, 0, 1]
        mock_random.choice.return_value = "Forest"  # Return actual string
        mock_region_schema.return_value = Mock()  # Mock schema creation
        
        # Mock region service
        mock_region = Mock()
        mock_region.region_id = "region_123"
        continent_svc.region_service.create_new_region.return_value = mock_region
        
        # Mock repository
        expected_continent = Mock()
        continent_svc.repository.create_continent.return_value = expected_continent
        
        # Execute
        result = continent_svc.create_new_continent(sample_creation_request)
        
        # Verify
        assert result == expected_continent
        continent_svc.repository.create_continent.assert_called_once()
        mock_random.seed.assert_called_once_with("test_seed_123")
        assert continent_svc.region_service.create_new_region.call_count == 2

    @patch('backend.systems.world_generation.continent_service.RegionCreationSchema')
    @patch('backend.systems.world_generation.continent_service.random')
    def test_create_new_continent_invalid_regions_target(self, mock_random, 
                                                       mock_region_schema, continent_svc): pass
        """Test continent creation with invalid regions target."""
        mock_random.randint.return_value = 55
        mock_random.choice.return_value = "Forest"
        mock_region_schema.return_value = Mock()
        
        # Create request with valid regions target (schema validates >= 50)
        request = ContinentCreationRequestSchema(
            name="Test",
            num_regions_target=55,  # Valid value
            seed="test"
        )
        
        # Mock the CONTINENT_MIN_REGIONS and CONTINENT_MAX_REGIONS to test the logic
        with patch('backend.systems.world_generation.continent_service.CONTINENT_MIN_REGIONS', 60): pass
            with patch('backend.systems.world_generation.continent_service.CONTINENT_MAX_REGIONS', 80): pass
                with patch('backend.systems.world_generation.continent_service.generate_continent_region_coordinates') as mock_coords: pass
                    mock_coords.return_value = [CoordinateSchema(x=0, y=0)]
                    with patch('backend.systems.world_generation.continent_service.get_continent_boundary') as mock_boundary: pass
                        mock_boundary.return_value = [0, 1, 0, 1]
                        
                        mock_region = Mock()
                        mock_region.region_id = "region_123"
                        continent_svc.region_service.create_new_region.return_value = mock_region
                        continent_svc.repository.create_continent.return_value = Mock()
                        
                        continent_svc.create_new_continent(request)
                        
                        # Should use random value instead of invalid target (55 is outside 60-80 range)
                        mock_coords.assert_called_once_with(mock_random.randint.return_value)

    @patch('backend.systems.world_generation.continent_service.RegionCreationSchema')
    @patch('backend.systems.world_generation.continent_service.uuid4')
    @patch('backend.systems.world_generation.continent_service.random')
    def test_create_new_continent_no_seed(self, mock_random, mock_uuid4, mock_region_schema, continent_svc): pass
        """Test continent creation without provided seed."""
        mock_uuid4.return_value = Mock(hex="test_id")
        mock_random.getrandbits.return_value = 12345
        mock_random.choice.return_value = "Plains"
        mock_region_schema.return_value = Mock()
        
        request = ContinentCreationRequestSchema(
            name="Test",
            num_regions_target=55,
            seed=None  # No seed provided
        )
        
        with patch('backend.systems.world_generation.continent_service.generate_continent_region_coordinates') as mock_coords: pass
            mock_coords.return_value = [CoordinateSchema(x=0, y=0)]
            with patch('backend.systems.world_generation.continent_service.get_continent_boundary') as mock_boundary: pass
                mock_boundary.return_value = [0, 1, 0, 1]
                
                mock_region = Mock()
                mock_region.region_id = "region_123"
                continent_svc.region_service.create_new_region.return_value = mock_region
                continent_svc.repository.create_continent.return_value = Mock()
                
                continent_svc.create_new_continent(request)
                
                # Should generate random seed
                mock_random.getrandbits.assert_called_once_with(64)
                mock_random.seed.assert_called_once_with("12345")

    def test_get_continent_details_success(self, continent_svc, sample_continent_schema): pass
        """Test successful continent details retrieval."""
        continent_svc.repository.get_continent_by_id.return_value = sample_continent_schema
        
        result = continent_svc.get_continent_details("test_id")
        
        assert result == sample_continent_schema
        continent_svc.repository.get_continent_by_id.assert_called_once_with("test_id")

    def test_get_continent_details_not_found(self, continent_svc): pass
        """Test continent details retrieval when not found."""
        continent_svc.repository.get_continent_by_id.return_value = None
        
        result = continent_svc.get_continent_details("nonexistent_id")
        
        assert result is None

    def test_list_all_continents(self, continent_svc, sample_continent_schema): pass
        """Test listing all continents."""
        expected_continents = [sample_continent_schema]
        continent_svc.repository.list_all_continents.return_value = expected_continents
        
        result = continent_svc.list_all_continents()
        
        assert result == expected_continents
        continent_svc.repository.list_all_continents.assert_called_once()

    def test_update_continent_metadata_success(self, continent_svc, sample_continent_schema): pass
        """Test successful continent metadata update."""
        continent_svc.repository.get_continent_by_id.return_value = sample_continent_schema
        updated_continent = Mock()
        continent_svc.repository.update_continent.return_value = updated_continent
        
        new_metadata = {"new_key": "new_value"}
        result = continent_svc.update_continent_metadata("test_id", new_metadata)
        
        assert result == updated_continent
        assert sample_continent_schema.metadata["new_key"] == "new_value"
        continent_svc.repository.update_continent.assert_called_once_with("test_id", sample_continent_schema)

    def test_update_continent_metadata_no_existing_metadata(self, continent_svc): pass
        """Test metadata update when continent has no existing metadata."""
        continent = Mock()
        continent.metadata = None
        continent_svc.repository.get_continent_by_id.return_value = continent
        updated_continent = Mock()
        continent_svc.repository.update_continent.return_value = updated_continent
        
        new_metadata = {"key": "value"}
        result = continent_svc.update_continent_metadata("test_id", new_metadata)
        
        assert result == updated_continent
        assert continent.metadata == {"key": "value"}

    def test_update_continent_metadata_not_found(self, continent_svc): pass
        """Test metadata update when continent not found."""
        continent_svc.repository.get_continent_by_id.return_value = None
        
        result = continent_svc.update_continent_metadata("nonexistent_id", {"key": "value"})
        
        assert result is None
        continent_svc.repository.update_continent.assert_not_called()

    def test_delete_continent_success(self, continent_svc): pass
        """Test successful continent deletion."""
        continent_svc.repository.delete_continent.return_value = True
        
        result = continent_svc.delete_continent("test_id")
        
        assert result is True
        continent_svc.repository.delete_continent.assert_called_once_with("test_id")

    def test_delete_continent_failure(self, continent_svc): pass
        """Test continent deletion failure."""
        continent_svc.repository.delete_continent.return_value = False
        
        result = continent_svc.delete_continent("test_id")
        
        assert result is False

    @patch('backend.systems.world_generation.continent_service.uuid4')
    def test_create_continent_compatibility_method_defaults(self, mock_uuid4, continent_svc): pass
        """Test compatibility method with default parameters."""
        mock_uuid_obj = Mock()
        mock_uuid_obj.__str__ = Mock(return_value="test_id_full_string")
        mock_uuid4.return_value = mock_uuid_obj
        
        # Mock the create_new_continent method
        mock_continent = Mock()
        mock_continent.continent_id = "continent_123"
        mock_continent.name = "Test Continent"
        mock_continent.region_ids = ["region1", "region2"]
        mock_continent.seed = "test_seed"
        mock_continent.num_regions = 2
        mock_continent.metadata = {"test": "data"}
        mock_continent.creation_timestamp = datetime(2023, 1, 1)
        
        continent_svc.create_new_continent = Mock(return_value=mock_continent)
        
        result = continent_svc.create_continent()
        
        # Verify defaults were used
        call_args = continent_svc.create_new_continent.call_args[0][0]
        assert call_args.num_regions_target == 60  # (50 + 70) // 2
        assert "Continent test_id_" in call_args.name
        assert call_args.metadata["min_regions"] == 50
        assert call_args.metadata["max_regions"] == 70
        assert call_args.metadata["origin_x"] == 0
        assert call_args.metadata["origin_y"] == 0

    def test_create_continent_compatibility_method_custom_params(self, continent_svc): pass
        """Test compatibility method with custom parameters."""
        mock_continent = Mock()
        mock_continent.continent_id = "continent_123"
        mock_continent.name = "Custom Continent"
        mock_continent.region_ids = ["region1"]
        mock_continent.seed = "custom_seed"
        mock_continent.num_regions = 1
        mock_continent.metadata = {"custom": "data"}
        mock_continent.creation_timestamp = datetime(2023, 1, 1)
        
        continent_svc.create_new_continent = Mock(return_value=mock_continent)
        
        result = continent_svc.create_continent(
            name="Custom Continent",
            min_regions=30,
            max_regions=40,
            origin_x=10,
            origin_y=20
        )
        
        # Verify custom parameters were used
        call_args = continent_svc.create_new_continent.call_args[0][0]
        assert call_args.name == "Custom Continent"
        assert call_args.num_regions_target == 50  # Minimum enforced
        assert call_args.metadata["min_regions"] == 30
        assert call_args.metadata["max_regions"] == 40
        assert call_args.metadata["origin_x"] == 10
        assert call_args.metadata["origin_y"] == 20

    def test_create_continent_compatibility_method_return_format(self, continent_svc): pass
        """Test compatibility method return format."""
        mock_continent = Mock()
        mock_continent.continent_id = "continent_123"
        mock_continent.name = "Test Continent"
        mock_continent.region_ids = ["region1", "region2"]
        mock_continent.seed = "test_seed"
        mock_continent.num_regions = 2
        mock_continent.metadata = {"test": "data"}
        mock_continent.creation_timestamp = datetime(2023, 1, 1)
        
        continent_svc.create_new_continent = Mock(return_value=mock_continent)
        
        result = continent_svc.create_continent()
        
        # Verify return format
        assert result["id"] == "continent_123"
        assert result["name"] == "Test Continent"
        assert result["regions"] == ["region1", "region2"]
        assert result["seed"] == "test_seed"
        assert result["num_regions"] == 2
        assert result["metadata"] == {"test": "data"}
        assert result["creation_timestamp"] == "2023-01-01T00:00:00"


class TestContinentServiceSingleton: pass
    """Test the singleton continent service instance."""

    def test_singleton_instance_exists(self): pass
        """Test that the singleton instance exists."""
        assert continent_service is not None
        assert isinstance(continent_service, ContinentService)

    def test_singleton_has_dependencies(self): pass
        """Test that the singleton has proper dependencies."""
        assert continent_service.repository is not None
        assert continent_service.region_service is not None


class TestContinentServiceIntegration: pass
    """Integration tests for continent service."""

    @patch('backend.systems.world_generation.continent_service.RegionCreationSchema')
    @patch('backend.systems.world_generation.continent_service.generate_continent_region_coordinates')
    @patch('backend.systems.world_generation.continent_service.get_continent_boundary')
    def test_create_continent_with_boundary_calculation(self, mock_boundary, mock_coords, mock_region_schema): pass
        """Test continent creation with boundary calculation."""
        mock_coords.return_value = [
            CoordinateSchema(x=0, y=0),
            CoordinateSchema(x=5, y=5),
            CoordinateSchema(x=10, y=10)
        ]
        mock_boundary.return_value = [0, 10, 0, 10]
        mock_region_schema.return_value = Mock()
        
        mock_repository = Mock()
        mock_region_service = Mock()
        mock_region = Mock()
        mock_region.region_id = "region_123"
        mock_region_service.create_new_region.return_value = mock_region
        
        service = ContinentService(mock_repository, mock_region_service)
        
        request = ContinentCreationRequestSchema(
            name="Test Continent",
            num_regions_target=55,
            seed="test_seed"
        )
        
        # Mock the repository to capture the continent being created
        created_continent = None
        def capture_continent(continent): pass
            nonlocal created_continent
            created_continent = continent
            return continent
        
        mock_repository.create_continent.side_effect = capture_continent
        
        service.create_new_continent(request)
        
        # Verify boundary was calculated and set
        assert created_continent is not None
        assert created_continent.boundary is not None
        assert created_continent.boundary.min_x == 0
        assert created_continent.boundary.max_x == 10
        assert created_continent.boundary.min_y == 0
        assert created_continent.boundary.max_y == 10

    @patch('backend.systems.world_generation.continent_service.RegionCreationSchema')
    @patch('backend.systems.world_generation.continent_service.generate_continent_region_coordinates')
    @patch('backend.systems.world_generation.continent_service.get_continent_boundary')
    def test_create_continent_no_boundary(self, mock_boundary, mock_coords, mock_region_schema): pass
        """Test continent creation when boundary calculation returns None."""
        mock_coords.return_value = [CoordinateSchema(x=0, y=0)]
        mock_boundary.return_value = None  # No boundary calculated
        mock_region_schema.return_value = Mock()
        
        mock_repository = Mock()
        mock_region_service = Mock()
        mock_region = Mock()
        mock_region.region_id = "region_123"
        mock_region_service.create_new_region.return_value = mock_region
        
        service = ContinentService(mock_repository, mock_region_service)
        
        request = ContinentCreationRequestSchema(
            name="Test Continent",
            num_regions_target=55,
            seed="test_seed"
        )
        
        created_continent = None
        def capture_continent(continent): pass
            nonlocal created_continent
            created_continent = continent
            return continent
        
        mock_repository.create_continent.side_effect = capture_continent
        
        service.create_new_continent(request)
        
        # Verify boundary is None when calculation fails
        assert created_continent is not None
        assert created_continent.boundary is None
