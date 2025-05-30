from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from typing import List
"""
Tests for continent_repository module.

Comprehensive tests for continent data persistence and CRUD operations.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from backend.systems.world_generation.continent_repository import (
    ContinentRepository,
    continent_repository,
)
from backend.systems.world_generation.models import (
    ContinentSchema,
    ContinentBoundarySchema,
    CoordinateSchema,
)


class TestContinentRepository: pass
    """Test suite for ContinentRepository class."""

    @pytest.fixture
    def repository(self): pass
        """Create a fresh repository instance for each test."""
        repo = ContinentRepository()
        # Clear any existing data
        repo._continents = {}
        return repo

    @pytest.fixture
    def sample_continent(self): pass
        """Sample continent schema for testing."""
        return ContinentSchema(
            continent_id="test_continent_123",
            name="Test Continent",
            seed="test_seed",
            region_coordinates=[
                CoordinateSchema(x=0, y=0),
                CoordinateSchema(x=1, y=1)
            ],
            region_ids=["region1", "region2"],
            origin_coordinate=CoordinateSchema(x=0, y=0),
            boundary=ContinentBoundarySchema(min_x=0, max_x=1, min_y=0, max_y=1),
            creation_timestamp=datetime(2023, 1, 1),
            num_regions=2,
            metadata={"test": "data"}
        )

    def test_create_continent_success(self, repository, sample_continent): pass
        """Test successful continent creation."""
        result = repository.create_continent(sample_continent)
        
        assert result == sample_continent
        assert result.continent_id == "test_continent_123"
        assert repository._continents["test_continent_123"] == sample_continent

    @patch('backend.systems.world_generation.continent_repository.uuid4')
    def test_create_continent_without_id(self, mock_uuid4, repository): pass
        """Test continent creation when no ID is provided."""
        mock_uuid4.return_value = Mock(__str__=Mock(return_value="generated_id"))
        
        continent = ContinentSchema(
            continent_id="",  # Empty ID to trigger fallback
            name="Test Continent",
            seed="test_seed",
            region_coordinates=[],
            region_ids=[],
            origin_coordinate=CoordinateSchema(x=0, y=0),
            boundary=None,
            creation_timestamp=datetime.utcnow(),
            num_regions=0,
            metadata={}
        )
        
        result = repository.create_continent(continent)
        
        assert result.continent_id == "generated_id"
        assert repository._continents["generated_id"] == continent
        mock_uuid4.assert_called_once()

    def test_get_continent_by_id_success(self, repository, sample_continent): pass
        """Test successful continent retrieval by ID."""
        repository._continents["test_continent_123"] = sample_continent
        
        result = repository.get_continent_by_id("test_continent_123")
        
        assert result == sample_continent

    def test_get_continent_by_id_not_found(self, repository): pass
        """Test continent retrieval when ID not found."""
        result = repository.get_continent_by_id("nonexistent_id")
        
        assert result is None

    def test_list_all_continents_empty(self, repository): pass
        """Test listing continents when repository is empty."""
        result = repository.list_all_continents()
        
        assert result == []

    def test_list_all_continents_with_data(self, repository, sample_continent): pass
        """Test listing continents when repository has data."""
        continent2 = ContinentSchema(
            continent_id="continent_456",
            name="Second Continent",
            seed="seed2",
            region_coordinates=[],
            region_ids=[],
            origin_coordinate=CoordinateSchema(x=5, y=5),
            boundary=None,
            creation_timestamp=datetime.utcnow(),
            num_regions=0,
            metadata={}
        )
        
        repository._continents["test_continent_123"] = sample_continent
        repository._continents["continent_456"] = continent2
        
        result = repository.list_all_continents()
        
        assert len(result) == 2
        assert sample_continent in result
        assert continent2 in result

    def test_update_continent_success(self, repository, sample_continent): pass
        """Test successful continent update."""
        # First create the continent
        repository._continents["test_continent_123"] = sample_continent
        
        # Create updated version
        updated_continent = ContinentSchema(
            continent_id="test_continent_123",
            name="Updated Continent",
            seed="updated_seed",
            region_coordinates=[CoordinateSchema(x=2, y=2)],
            region_ids=["region3"],
            origin_coordinate=CoordinateSchema(x=2, y=2),
            boundary=ContinentBoundarySchema(min_x=2, max_x=2, min_y=2, max_y=2),
            creation_timestamp=datetime(2023, 1, 2),
            num_regions=1,
            metadata={"updated": "data"}
        )
        
        result = repository.update_continent("test_continent_123", updated_continent)
        
        assert result == updated_continent
        assert repository._continents["test_continent_123"] == updated_continent

    def test_update_continent_id_mismatch(self, repository, sample_continent): pass
        """Test continent update when IDs don't match."""
        repository._continents["test_continent_123"] = sample_continent
        
        # Create continent with different ID
        updated_continent = ContinentSchema(
            continent_id="different_id",
            name="Updated Continent",
            seed="updated_seed",
            region_coordinates=[],
            region_ids=[],
            origin_coordinate=CoordinateSchema(x=0, y=0),
            boundary=None,
            creation_timestamp=datetime.utcnow(),
            num_regions=0,
            metadata={}
        )
        
        result = repository.update_continent("test_continent_123", updated_continent)
        
        # Should update and fix the ID
        assert result.continent_id == "test_continent_123"
        assert repository._continents["test_continent_123"].continent_id == "test_continent_123"

    def test_update_continent_not_found(self, repository): pass
        """Test continent update when continent doesn't exist."""
        updated_continent = ContinentSchema(
            continent_id="nonexistent_id",
            name="Updated Continent",
            seed="updated_seed",
            region_coordinates=[],
            region_ids=[],
            origin_coordinate=CoordinateSchema(x=0, y=0),
            boundary=None,
            creation_timestamp=datetime.utcnow(),
            num_regions=0,
            metadata={}
        )
        
        result = repository.update_continent("nonexistent_id", updated_continent)
        
        assert result is None
        assert "nonexistent_id" not in repository._continents

    def test_delete_continent_success(self, repository, sample_continent): pass
        """Test successful continent deletion."""
        repository._continents["test_continent_123"] = sample_continent
        
        result = repository.delete_continent("test_continent_123")
        
        assert result is True
        assert "test_continent_123" not in repository._continents

    def test_delete_continent_not_found(self, repository): pass
        """Test continent deletion when continent doesn't exist."""
        result = repository.delete_continent("nonexistent_id")
        
        assert result is False

    def test_repository_isolation(self, repository, sample_continent): pass
        """Test that repository operations don't affect other instances."""
        # Create another repository instance
        repo2 = ContinentRepository()
        repo2._continents = {}
        
        # Add continent to first repository
        repository.create_continent(sample_continent)
        
        # Second repository should be empty
        assert len(repo2.list_all_continents()) == 0
        assert repository.get_continent_by_id("test_continent_123") is not None
        assert repo2.get_continent_by_id("test_continent_123") is None


class TestContinentRepositorySingleton: pass
    """Test the singleton continent repository instance."""

    def test_singleton_instance_exists(self): pass
        """Test that the singleton instance exists."""
        assert continent_repository is not None
        assert isinstance(continent_repository, ContinentRepository)

    def test_singleton_has_storage(self): pass
        """Test that the singleton has proper storage."""
        assert hasattr(continent_repository, '_continents')
        assert isinstance(continent_repository._continents, dict)


class TestContinentRepositoryIntegration: pass
    """Integration tests for continent repository."""

    def test_full_crud_cycle(self): pass
        """Test complete CRUD cycle on singleton repository."""
        # Clear any existing data
        continent_repository._continents.clear()
        
        # Create
        continent = ContinentSchema(
            continent_id="integration_test_123",
            name="Integration Test Continent",
            seed="integration_seed",
            region_coordinates=[CoordinateSchema(x=10, y=10)],
            region_ids=["integration_region"],
            origin_coordinate=CoordinateSchema(x=10, y=10),
            boundary=ContinentBoundarySchema(min_x=10, max_x=10, min_y=10, max_y=10),
            creation_timestamp=datetime.utcnow(),
            num_regions=1,
            metadata={"integration": "test"}
        )
        
        created = continent_repository.create_continent(continent)
        assert created.continent_id == "integration_test_123"
        
        # Read
        retrieved = continent_repository.get_continent_by_id("integration_test_123")
        assert retrieved is not None
        assert retrieved.name == "Integration Test Continent"
        
        # Update
        retrieved.name = "Updated Integration Continent"
        updated = continent_repository.update_continent("integration_test_123", retrieved)
        assert updated.name == "Updated Integration Continent"
        
        # List
        all_continents = continent_repository.list_all_continents()
        assert len(all_continents) == 1
        assert all_continents[0].name == "Updated Integration Continent"
        
        # Delete
        deleted = continent_repository.delete_continent("integration_test_123")
        assert deleted is True
        
        # Verify deletion
        final_check = continent_repository.get_continent_by_id("integration_test_123")
        assert final_check is None
        
        final_list = continent_repository.list_all_continents()
        assert len(final_list) == 0

    def test_multiple_continents_management(self): pass
        """Test managing multiple continents simultaneously."""
        # Clear any existing data
        continent_repository._continents.clear()
        
        # Create multiple continents
        continents = []
        for i in range(3): pass
            continent = ContinentSchema(
                continent_id=f"multi_test_{i}",
                name=f"Multi Test Continent {i}",
                seed=f"multi_seed_{i}",
                region_coordinates=[CoordinateSchema(x=i, y=i)],
                region_ids=[f"multi_region_{i}"],
                origin_coordinate=CoordinateSchema(x=i, y=i),
                boundary=ContinentBoundarySchema(min_x=i, max_x=i, min_y=i, max_y=i),
                creation_timestamp=datetime.utcnow(),
                num_regions=1,
                metadata={"multi": f"test_{i}"}
            )
            continents.append(continent)
            continent_repository.create_continent(continent)
        
        # Verify all were created
        all_continents = continent_repository.list_all_continents()
        assert len(all_continents) == 3
        
        # Verify individual retrieval
        for i in range(3): pass
            retrieved = continent_repository.get_continent_by_id(f"multi_test_{i}")
            assert retrieved is not None
            assert retrieved.name == f"Multi Test Continent {i}"
        
        # Update one
        continent_repository.update_continent("multi_test_1", continents[1])
        
        # Delete one
        deleted = continent_repository.delete_continent("multi_test_2")
        assert deleted is True
        
        # Verify final state
        final_list = continent_repository.list_all_continents()
        assert len(final_list) == 2
        assert continent_repository.get_continent_by_id("multi_test_0") is not None
        assert continent_repository.get_continent_by_id("multi_test_1") is not None
        assert continent_repository.get_continent_by_id("multi_test_2") is None
        
        # Cleanup
        continent_repository.delete_continent("multi_test_0")
        continent_repository.delete_continent("multi_test_1")
