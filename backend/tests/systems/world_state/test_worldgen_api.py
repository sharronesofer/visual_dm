from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from typing import Optional
from dataclasses import field
"""
Comprehensive tests for World Generation API endpoints

This module tests all FastAPI routes and data models in the worldgen_api.py module
to achieve 90% test coverage.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, patch, MagicMock
import json

from backend.systems.world_state.worldgen_api import (
    router,
    BiomeData,
    PointOfInterestData,
    RegionRequest,
    RegionResponse,
    ContinentResponse,
    WorldResponse,
    get_world_generator,
)
from backend.systems.world_state.optimized_worldgen import OptimizedWorldGenerator


@pytest.fixture
def app(): pass
    """Create test FastAPI application."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app): pass
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_world_generator(): pass
    """Create mock world generator."""
    generator = Mock(spec=OptimizedWorldGenerator)
    
    # Mock terrain generator with biomes data
    generator.terrain_generator = Mock()
    generator.terrain_generator.biomes = {
        "forest": {
            "name": "Forest",
            "temperature_range": [0.3, 0.7],
            "moisture_range": [0.6, 1.0],
            "elevation_range": [0.3, 0.7],
            "features": ["trees", "wildlife"],
            "resources": {"wood": 0.9, "game": 0.7},
            "color": "#228B22",
            "is_water": False
        },
        "ocean": {
            "name": "Ocean",
            "temperature_range": [0.0, 1.0],
            "moisture_range": [1.0, 1.0],
            "elevation_range": [0.0, 0.2],
            "features": ["water", "marine_life"],
            "resources": {"fish": 0.8, "salt": 0.5},
            "color": "#4169E1",
            "is_water": True
        }
    }
    
    # Mock region generation
    mock_region = Mock()
    mock_region.x = 0
    mock_region.y = 0
    mock_region.elevation = [[0.3, 0.4], [0.5, 0.6]]
    mock_region.moisture = [[0.5, 0.6], [0.7, 0.8]]
    mock_region.temperature = [[0.4, 0.5], [0.6, 0.7]]
    mock_region.biome_map = [["forest", "forest"], ["plains", "mountains"]]
    mock_region.rivers = [[False, False], [True, False]]
    
    # Mock POI with proper attributes
    mock_poi = Mock()
    mock_poi.name = "Ancient Grove"
    mock_poi.poi_type = "grove"
    mock_poi.description = "An ancient grove of mystical trees"
    mock_region.points_of_interest = [mock_poi]
    
    generator.generate_region.return_value = mock_region
    
    return generator


class TestDataModels: pass
    """Test Pydantic data models."""
    
    def test_biome_data_model(self): pass
        """Test BiomeData model creation and validation."""
        biome = BiomeData(
            id="forest",
            name="Forest",
            temperature_range=[0.3, 0.7],
            moisture_range=[0.6, 1.0],
            elevation_range=[0.3, 0.7],
            features=["trees", "wildlife"],
            resources={"wood": 0.9, "game": 0.7},
            color="#228B22",
            is_water=False
        )
        
        assert biome.id == "forest"
        assert biome.name == "Forest"
        assert biome.temperature_range == [0.3, 0.7]
        assert biome.is_water is False
    
    def test_biome_data_validation_temperature_range(self): pass
        """Test BiomeData temperature range validation."""
        with pytest.raises(ValueError): pass
            BiomeData(
                id="invalid",
                name="Invalid",
                temperature_range=[0.3],  # Too few items
                moisture_range=[0.6, 1.0],
                elevation_range=[0.3, 0.7],
                features=[],
                resources={},
                color="#000000"
            )
    
    def test_point_of_interest_data_model(self): pass
        """Test PointOfInterestData model creation."""
        poi = PointOfInterestData(
            id="poi_123",
            name="Test POI",
            type="grove",
            x=10,
            y=15,
            biome="forest",
            elevation=0.45,
            attributes={"difficulty": 3}
        )
        
        assert poi.id == "poi_123"
        assert poi.x == 10
        assert poi.y == 15
        assert poi.attributes["difficulty"] == 3
    
    def test_region_request_model(self): pass
        """Test RegionRequest model creation and defaults."""
        request = RegionRequest(
            x=3,
            y=5,
            world_seed=12345,
            continent_id="continent_1"
        )
        
        assert request.x == 3
        assert request.y == 5
        assert request.size == 64  # Default value
        assert request.world_seed == 12345
        assert request.continent_id == "continent_1"
        assert request.biome_influence is None  # Optional field
    
    def test_region_request_with_biome_influence(self): pass
        """Test RegionRequest with biome influence."""
        request = RegionRequest(
            x=3,
            y=5,
            world_seed=12345,
            continent_id="continent_1",
            biome_influence={"forest": 0.3, "mountains": 0.1}
        )
        
        assert request.biome_influence == {"forest": 0.3, "mountains": 0.1}
    
    def test_region_response_model(self): pass
        """Test RegionResponse model creation."""
        response = RegionResponse(
            region_id="3:5",
            world_seed=12345,
            continent_id="continent_1",
            size=64,
            elevation=[[0.3, 0.4]],
            moisture=[[0.5, 0.6]],
            temperature=[[0.4, 0.5]],
            biomes=[["forest"]],
            rivers=[[False]],
            pois=[],
            generation_time=0.125
        )
        
        assert response.region_id == "3:5"
        assert response.size == 64
        assert response.generation_time == 0.125
    
    def test_continent_response_model(self): pass
        """Test ContinentResponse model creation."""
        response = ContinentResponse(
            continent_id="continent_1",
            name="Eastern Lands",
            regions=["3:5", "3:6"],
            predominant_biomes={"forest": 0.5},
            size=4
        )
        
        assert response.continent_id == "continent_1"
        assert response.name == "Eastern Lands"
        assert len(response.regions) == 2
    
    def test_world_response_model(self): pass
        """Test WorldResponse model creation."""
        response = WorldResponse(
            world_seed=12345,
            name="Mystical Realms",
            continents=["continent_1", "continent_2"],
            ocean_level=0.3,
            total_regions=120
        )
        
        assert response.world_seed == 12345
        assert response.name == "Mystical Realms"
        assert len(response.continents) == 2


class TestWorldGenAPI: pass
    """Test WorldGen API endpoints."""
    
    def test_get_biomes_endpoint(self, client, mock_world_generator): pass
        """Test GET /worldgen/biomes endpoint."""
        # Use FastAPI dependency override instead of patch
        from backend.systems.world_state.worldgen_api import get_world_generator
        
        def mock_get_world_generator(): pass
            return mock_world_generator
            
        client.app.dependency_overrides[get_world_generator] = mock_get_world_generator
        
        try: pass
            response = client.get("/worldgen/biomes")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["id"] == "forest"
            assert data[1]["id"] == "ocean"
            assert data[1]["is_water"] is True
        finally: pass
            # Clean up the override
            client.app.dependency_overrides.clear()
    
    def test_get_biomes_empty(self, client): pass
        """Test GET /worldgen/biomes with no biomes."""
        from backend.systems.world_state.worldgen_api import get_world_generator
        
        mock_generator = Mock()
        mock_generator.terrain_generator = Mock()
        mock_generator.terrain_generator.biomes = {}
        
        def mock_get_world_generator(): pass
            return mock_generator
            
        client.app.dependency_overrides[get_world_generator] = mock_get_world_generator
        
        try: pass
            response = client.get("/worldgen/biomes")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0
        finally: pass
            client.app.dependency_overrides.clear()
    
    def test_generate_region_endpoint(self, client, mock_world_generator): pass
        """Test POST /worldgen/region endpoint."""
        from backend.systems.world_state.worldgen_api import get_world_generator
        
        def mock_get_world_generator(): pass
            return mock_world_generator
            
        client.app.dependency_overrides[get_world_generator] = mock_get_world_generator
        
        try: pass
            with patch('time.time') as mock_time: pass
                mock_time.side_effect = [1000.0, 1000.125, 1001.0, 1001.125]  # More values
                
                request_data = {
                    "x": 3,
                    "y": 5,
                    "size": 64,
                    "world_seed": 12345,
                    "continent_id": "continent_1"
                }
                
                response = client.post("/worldgen/region", json=request_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["region_id"] == "3:5"
                assert data["world_seed"] == 12345
                assert data["continent_id"] == "continent_1"
                assert data["size"] == 64
                assert data["generation_time"] == 0.125
                assert len(data["pois"]) == 1
                assert data["pois"][0]["name"] == "Ancient Grove"
        finally: pass
            client.app.dependency_overrides.clear()
    
    def test_generate_region_with_biome_influence(self, client, mock_world_generator): pass
        """Test POST /worldgen/region with biome influence."""
        from backend.systems.world_state.worldgen_api import get_world_generator
        
        def mock_get_world_generator(): pass
            return mock_world_generator
            
        client.app.dependency_overrides[get_world_generator] = mock_get_world_generator
        
        try: pass
            request_data = {
                "x": 3,
                "y": 5,
                "world_seed": 12345,
                "continent_id": "continent_1",
                "biome_influence": {"forest": 0.3, "mountains": 0.1}
            }
            
            response = client.post("/worldgen/region", json=request_data)
            
            assert response.status_code == 200
            # Verify the generator was called with biome influence
            mock_world_generator.generate_region.assert_called_once()
            call_args = mock_world_generator.generate_region.call_args
            assert call_args[1]["biome_influence"] == {"forest": 0.3, "mountains": 0.1}
        finally: pass
            client.app.dependency_overrides.clear()
    
    def test_generate_region_error_handling(self, client): pass
        """Test POST /worldgen/region error handling."""
        from backend.systems.world_state.worldgen_api import get_world_generator
        
        mock_generator = Mock()
        mock_generator.generate_region.side_effect = Exception("Generation failed")
        
        def mock_get_world_generator(): pass
            return mock_generator
            
        client.app.dependency_overrides[get_world_generator] = mock_get_world_generator
        
        try: pass
            request_data = {
                "x": 3,
                "y": 5,
                "world_seed": 12345,
                "continent_id": "continent_1"
            }
            
            response = client.post("/worldgen/region", json=request_data)
            
            assert response.status_code == 500
            assert "Failed to generate region" in response.json()["detail"]
        finally: pass
            client.app.dependency_overrides.clear()
    
    def test_generate_region_invalid_request(self, client): pass
        """Test POST /worldgen/region with invalid request data."""
        request_data = {
            "x": "invalid",  # Should be int
            "y": 5,
            "world_seed": 12345,
            "continent_id": "continent_1"
        }
        
        response = client.post("/worldgen/region", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_region_endpoint(self, client, mock_world_generator): pass
        """Test GET /worldgen/region/{x}/{y} endpoint."""
        from backend.systems.world_state.worldgen_api import get_world_generator
        
        def mock_get_world_generator(): pass
            return mock_world_generator
            
        client.app.dependency_overrides[get_world_generator] = mock_get_world_generator
        
        try: pass
            response = client.get(
                "/worldgen/region/3/5",
                params={
                    "size": 128,
                    "seed": 12345,
                    "continent_id": "continent_1"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["region_id"] == "3:5"
            assert data["world_seed"] == 12345
            assert data["size"] == 128
        finally: pass
            client.app.dependency_overrides.clear()
    
    def test_get_region_missing_params(self, client): pass
        """Test GET /worldgen/region/{x}/{y} with missing parameters."""
        response = client.get("/worldgen/region/3/5")
        
        assert response.status_code == 422  # Missing required query params
    
    def test_get_region_invalid_size(self, client): pass
        """Test GET /worldgen/region/{x}/{y} with invalid size."""
        response = client.get(
            "/worldgen/region/3/5",
            params={
                "size": 10,  # Below minimum of 16
                "seed": 12345,
                "continent_id": "continent_1"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_continent_endpoint(self, client): pass
        """Test GET /worldgen/continent/{continent_id} endpoint."""
        response = client.get(
            "/worldgen/continent/continent_1",
            params={"world_seed": 12345}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["continent_id"] == "continent_1"
        assert "name" in data
        assert "regions" in data
        assert "predominant_biomes" in data
    
    def test_get_continent_missing_seed(self, client): pass
        """Test GET /worldgen/continent/{continent_id} with missing seed."""
        response = client.get("/worldgen/continent/continent_1")
        
        assert response.status_code == 422  # Missing required query param
    
    def test_get_world_endpoint(self, client): pass
        """Test GET /worldgen/world/{world_seed} endpoint."""
        response = client.get("/worldgen/world/12345")
        
        assert response.status_code == 200
        data = response.json()
        assert data["world_seed"] == 12345
        assert "name" in data
        assert "continents" in data
        assert "ocean_level" in data
        assert "total_regions" in data
    
    def test_test_region_endpoint(self, client, mock_world_generator): pass
        """Test GET /worldgen/test-region endpoint."""
        from backend.systems.world_state.worldgen_api import get_world_generator
        
        def mock_get_world_generator(): pass
            return mock_world_generator
            
        client.app.dependency_overrides[get_world_generator] = mock_get_world_generator
        
        try: pass
            response = client.get("/worldgen/test-region", params={"size": 32})
            
            assert response.status_code == 200
            data = response.json()
            assert data["region_id"] == "0:0"  # Test region coordinates
            assert data["size"] == 32
        finally: pass
            client.app.dependency_overrides.clear()
    
    def test_test_region_default_size(self, client, mock_world_generator): pass
        """Test GET /worldgen/test-region with default size."""
        from backend.systems.world_state.worldgen_api import get_world_generator
        
        def mock_get_world_generator(): pass
            return mock_world_generator
            
        client.app.dependency_overrides[get_world_generator] = mock_get_world_generator
        
        try: pass
            response = client.get("/worldgen/test-region")
            
            assert response.status_code == 200
            data = response.json()
            assert data["size"] == 64  # Default size
        finally: pass
            client.app.dependency_overrides.clear()


class TestDependencyInjection: pass
    """Test dependency injection functions."""
    
    def test_get_world_generator_dependency(self): pass
        """Test get_world_generator dependency function."""
        generator = get_world_generator()
        
        assert generator is not None
        assert hasattr(generator, 'generate_region')
        assert hasattr(generator, 'terrain_generator')


class TestErrorHandling: pass
    """Test error handling scenarios."""
    
    def test_biomes_endpoint_error(self, client): pass
        """Test biomes endpoint with generator error."""
        from backend.systems.world_state.worldgen_api import get_world_generator
        
        mock_generator = Mock()
        mock_generator.terrain_generator.biomes = None  # Cause AttributeError
        
        def mock_get_world_generator(): pass
            return mock_generator
            
        client.app.dependency_overrides[get_world_generator] = mock_get_world_generator
        
        try: pass
            response = client.get("/worldgen/biomes")
            
            assert response.status_code == 500
        finally: pass
            client.app.dependency_overrides.clear()
    
    def test_get_region_generation_error(self, client): pass
        """Test region retrieval with generation error."""
        from backend.systems.world_state.worldgen_api import get_world_generator
        
        mock_generator = Mock()
        mock_generator.generate_region.side_effect = ValueError("Invalid coordinates")
        
        def mock_get_world_generator(): pass
            return mock_generator
            
        client.app.dependency_overrides[get_world_generator] = mock_get_world_generator
        
        try: pass
            response = client.get(
                "/worldgen/region/999/999",
                params={
                    "seed": 12345,
                    "continent_id": "continent_1"
                }
            )
            
            assert response.status_code == 500
        finally: pass
            client.app.dependency_overrides.clear()


class TestAPIDocumentation: pass
    """Test API documentation and metadata."""
    
    def test_router_metadata(self): pass
        """Test router configuration."""
        assert router.prefix == "/worldgen"
        assert "world_generation" in router.tags
        assert 404 in router.responses
    
    def test_model_examples(self): pass
        """Test that Pydantic models have proper examples."""
        # BiomeData should have example in config
        assert hasattr(BiomeData.model_config, 'get')
        
        # RegionRequest should have example
        assert hasattr(RegionRequest.model_config, 'get')
        
        # Verify example structure for RegionRequest
        example = RegionRequest.model_config.get('schema_extra', {}).get('example', {})
        assert 'x' in example
        assert 'y' in example
        assert 'world_seed' in example 