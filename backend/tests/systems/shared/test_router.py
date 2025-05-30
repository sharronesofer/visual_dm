from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from backend.systems.world_generation.schemas import ContinentSchema
from typing import List
"""
Tests for world generation router module.

Comprehensive tests for FastAPI endpoints and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime

from backend.systems.world_generation.router import router
from backend.systems.world_generation.models import (
    ContinentSchema,
    ContinentCreationRequestSchema,
    ContinentBoundarySchema,
    CoordinateSchema,
)


class TestWorldGenerationRouter:
    """Test suite for world generation FastAPI router."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app with router for testing."""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_continent(self):
        """Sample continent for testing."""
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

    @pytest.fixture
    def sample_creation_request(self):
        """Sample creation request."""
        return {
            "name": "Test Continent",
            "num_regions_target": 60,
            "seed": "test_seed_123",
            "metadata": {"test_key": "test_value"}
        }

    @patch('backend.systems.world_generation.router.continent_service')
    def test_create_continent_endpoint_success(self, mock_service, client, sample_continent, sample_creation_request):
        """Test successful continent creation endpoint."""
        mock_service.create_new_continent.return_value = sample_continent
        
        response = client.post("/world/continents", json=sample_creation_request)
        
        assert response.status_code == 201
        data = response.json()
        assert data["continent_id"] == "test_continent_123"
        assert data["name"] == "Test Continent"
        assert data["num_regions"] == 2
        mock_service.create_new_continent.assert_called_once()

    @patch('backend.systems.world_generation.router.continent_service')
    def test_create_continent_endpoint_service_error(self, mock_service, client, sample_creation_request):
        """Test continent creation endpoint when service raises exception."""
        mock_service.create_new_continent.side_effect = Exception("Service error")
        
        response = client.post("/world/continents", json=sample_creation_request)
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to create continent" in data["detail"]
        assert "Service error" in data["detail"]

    def test_create_continent_endpoint_invalid_request(self, client):
        """Test continent creation endpoint with invalid request data."""
        invalid_request = {
            "name": "",  # Invalid empty name
            "num_regions_target": 10,  # Below minimum
        }
        
        response = client.post("/world/continents", json=invalid_request)
        
        assert response.status_code == 422  # Validation error

    @patch('backend.systems.world_generation.router.continent_service')
    def test_get_continent_endpoint_success(self, mock_service, client, sample_continent):
        """Test successful continent retrieval endpoint."""
        mock_service.get_continent_details.return_value = sample_continent
        
        response = client.get("/world/continents/test_continent_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["continent_id"] == "test_continent_123"
        assert data["name"] == "Test Continent"
        mock_service.get_continent_details.assert_called_once_with("test_continent_123")

    @patch('backend.systems.world_generation.router.continent_service')
    def test_get_continent_endpoint_not_found(self, mock_service, client):
        """Test continent retrieval endpoint when continent not found."""
        mock_service.get_continent_details.return_value = None
        
        response = client.get("/world/continents/nonexistent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Continent not found"

    @patch('backend.systems.world_generation.router.continent_service')
    def test_list_all_continents_endpoint_success(self, mock_service, client, sample_continent):
        """Test successful continent listing endpoint."""
        continents = [sample_continent]
        mock_service.list_all_continents.return_value = continents
        
        response = client.get("/world/continents")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["continent_id"] == "test_continent_123"
        mock_service.list_all_continents.assert_called_once()

    @patch('backend.systems.world_generation.router.continent_service')
    def test_list_all_continents_endpoint_with_pagination(self, mock_service, client):
        """Test continent listing endpoint with pagination parameters."""
        # Create multiple continents for pagination test
        continents = []
        for i in range(5):
            continent = ContinentSchema(
                continent_id=f"continent_{i}",
                name=f"Continent {i}",
                seed=f"seed_{i}",
                region_coordinates=[],
                region_ids=[],
                origin_coordinate=CoordinateSchema(x=i, y=i),
                boundary=None,
                creation_timestamp=datetime.utcnow(),
                num_regions=0,
                metadata={}
            )
            continents.append(continent)
        
        mock_service.list_all_continents.return_value = continents
        
        # Test with limit and offset
        response = client.get("/world/continents?limit=2&offset=1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Limited to 2
        assert data[0]["continent_id"] == "continent_1"  # Offset by 1
        assert data[1]["continent_id"] == "continent_2"

    @patch('backend.systems.world_generation.router.continent_service')
    def test_list_all_continents_endpoint_empty_list(self, mock_service, client):
        """Test continent listing endpoint when no continents exist."""
        mock_service.list_all_continents.return_value = []
        
        response = client.get("/world/continents")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_all_continents_endpoint_invalid_pagination(self, client):
        """Test continent listing endpoint with invalid pagination parameters."""
        # Test negative limit
        response = client.get("/world/continents?limit=-1")
        assert response.status_code == 422
        
        # Test limit too high
        response = client.get("/world/continents?limit=2000")
        assert response.status_code == 422
        
        # Test negative offset
        response = client.get("/world/continents?offset=-1")
        assert response.status_code == 422

    @patch('backend.systems.world_generation.router.continent_service')
    def test_update_continent_metadata_endpoint_success(self, mock_service, client, sample_continent):
        """Test successful continent metadata update endpoint."""
        updated_continent = sample_continent.model_copy()
        updated_continent.metadata = {"updated": "data"}
        mock_service.update_continent_metadata.return_value = updated_continent
        
        metadata_update = {"updated": "data"}
        response = client.patch("/world/continents/test_continent_123/metadata", json=metadata_update)
        
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["updated"] == "data"
        mock_service.update_continent_metadata.assert_called_once_with("test_continent_123", metadata_update)

    @patch('backend.systems.world_generation.router.continent_service')
    def test_update_continent_metadata_endpoint_not_found(self, mock_service, client):
        """Test continent metadata update endpoint when continent not found."""
        mock_service.update_continent_metadata.return_value = None
        
        metadata_update = {"updated": "data"}
        response = client.patch("/world/continents/nonexistent_id/metadata", json=metadata_update)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Continent not found"

    @patch('backend.systems.world_generation.router.continent_service')
    def test_delete_continent_endpoint_success(self, mock_service, client):
        """Test successful continent deletion endpoint."""
        mock_service.delete_continent.return_value = True
        
        response = client.delete("/world/continents/test_continent_123")
        
        assert response.status_code == 204
        assert response.content == b""  # No content for 204
        mock_service.delete_continent.assert_called_once_with("test_continent_123")

    @patch('backend.systems.world_generation.router.continent_service')
    def test_delete_continent_endpoint_not_found(self, mock_service, client):
        """Test continent deletion endpoint when continent not found."""
        mock_service.delete_continent.return_value = False
        
        response = client.delete("/world/continents/nonexistent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Continent not found"


class TestRouterConfiguration:
    """Test router configuration and setup."""

    def test_router_prefix(self):
        """Test that router has correct prefix."""
        assert router.prefix == "/world"

    def test_router_tags(self):
        """Test that router has correct tags."""
        assert "World Generation" in router.tags

    def test_router_routes_exist(self):
        """Test that all expected routes are registered."""
        route_paths = [route.path for route in router.routes]
        
        expected_paths = [
            "/world/continents",
            "/world/continents/{continent_id}",
            "/world/continents/{continent_id}/metadata",
        ]
        
        for expected_path in expected_paths:
            assert expected_path in route_paths

    def test_router_methods(self):
        """Test that routes have correct HTTP methods."""
        # Collect all methods for each path (since FastAPI creates separate route objects)
        routes_by_path = {}
        for route in router.routes:
            if route.path not in routes_by_path:
                routes_by_path[route.path] = set()
            routes_by_path[route.path].update(route.methods)
        
        assert "POST" in routes_by_path["/world/continents"]
        assert "GET" in routes_by_path["/world/continents"]
        assert "GET" in routes_by_path["/world/continents/{continent_id}"]
        assert "PATCH" in routes_by_path["/world/continents/{continent_id}/metadata"]
        assert "DELETE" in routes_by_path["/world/continents/{continent_id}"]


class TestRouterIntegration:
    """Integration tests for router with real FastAPI app."""

    @pytest.fixture
    def app_with_router(self):
        """Create FastAPI app with router included."""
        app = FastAPI(title="Test World Generation API")
        app.include_router(router)
        return app

    @pytest.fixture
    def integration_client(self, app_with_router):
        """Create test client for integration tests."""
        return TestClient(app_with_router)

    def test_openapi_schema_generation(self, app_with_router):
        """Test that OpenAPI schema is generated correctly."""
        schema = app_with_router.openapi()
        
        assert "paths" in schema
        assert "/world/continents" in schema["paths"]
        assert "/world/continents/{continent_id}" in schema["paths"]
        assert "/world/continents/{continent_id}/metadata" in schema["paths"]

    def test_docs_endpoint_accessible(self, integration_client):
        """Test that API docs endpoint is accessible."""
        response = integration_client.get("/docs")
        assert response.status_code == 200

    @patch('backend.systems.world_generation.router.continent_service')
    def test_full_crud_workflow(self, mock_service, integration_client):
        """Test complete CRUD workflow through the API."""
        # Mock continent for testing
        test_continent = ContinentSchema(
            continent_id="workflow_test_123",
            name="Workflow Test Continent",
            seed="workflow_seed",
            region_coordinates=[CoordinateSchema(x=0, y=0)],
            region_ids=["region1"],
            origin_coordinate=CoordinateSchema(x=0, y=0),
            boundary=ContinentBoundarySchema(min_x=0, max_x=1, min_y=0, max_y=1),
            creation_timestamp=datetime.utcnow(),
            num_regions=1,
            metadata={"workflow": "test"}
        )
        
        # Setup mocks for the workflow
        mock_service.create_new_continent.return_value = test_continent
        mock_service.get_continent_details.return_value = test_continent
        mock_service.list_all_continents.return_value = [test_continent]
        
        updated_continent = test_continent.model_copy()
        updated_continent.metadata = {"workflow": "test", "updated": "true"}
        mock_service.update_continent_metadata.return_value = updated_continent
        mock_service.delete_continent.return_value = True
        
        # 1. Create continent
        create_request = {
            "name": "Workflow Test Continent",
            "num_regions_target": 60,
            "seed": "workflow_seed"
        }
        create_response = integration_client.post("/world/continents", json=create_request)
        assert create_response.status_code == 201
        
        # 2. Get continent
        get_response = integration_client.get("/world/continents/workflow_test_123")
        assert get_response.status_code == 200
        
        # 3. List continents
        list_response = integration_client.get("/world/continents")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        
        # 4. Update metadata
        metadata_update = {"updated": "true"}
        update_response = integration_client.patch(
            "/world/continents/workflow_test_123/metadata", 
            json=metadata_update
        )
        assert update_response.status_code == 200
        
        # 5. Delete continent
        delete_response = integration_client.delete("/world/continents/workflow_test_123")
        assert delete_response.status_code == 204
        
        # Verify all service methods were called
        mock_service.create_new_continent.assert_called_once()
        mock_service.get_continent_details.assert_called_once()
        mock_service.list_all_continents.assert_called_once()
        mock_service.update_continent_metadata.assert_called_once()
        mock_service.delete_continent.assert_called_once() 