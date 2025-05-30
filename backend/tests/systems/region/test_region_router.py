"""
Tests for the region.router module.

This module contains tests for the region system's FastAPI router that
exposes region functionality through HTTP endpoints.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
import json

from backend.systems.region.router import router, get_region_service
from backend.systems.region.service import RegionService


# Setup for FastAPI tests
@pytest.fixture
def mock_region_service(): pass
    """Create a mock RegionService."""
    service = MagicMock(spec=RegionService)

    # Set up responses for various service methods
    service.initialize.return_value = {
        "status": "success",
        "message": "World initialized",
        "world_data": {"seed": 12345},
    }
    service.get_all_continents.return_value = {
        "status": "success",
        "continents": [
            {"continent_id": "c_test1", "name": "Test Continent 1"},
            {"continent_id": "c_test2", "name": "Test Continent 2"},
        ],
    }
    service.get_continent.return_value = {
        "status": "success",
        "continent": {
            "continent_id": "c_test1",
            "name": "Test Continent 1",
            "region_count": 5,
        },
    }
    service.get_all_regions.return_value = {
        "status": "success",
        "regions": [
            {"region_id": "r_test1", "name": "Test Region 1", "biome_type": "forest"},
            {"region_id": "r_test2", "name": "Test Region 2", "biome_type": "plains"},
        ],
    }
    service.get_region.return_value = {
        "status": "success",
        "region": {
            "region_id": "r_test1",
            "name": "Test Region 1",
            "biome_type": "forest",
            "continent_id": "c_test1",
            "resources": {"wood": 0.8},
        },
    }
    # Note: get_regions_by_biome doesn't exist - it's handled by get_all_regions with biome_type parameter
    service.get_adjacent_regions.return_value = {
        "status": "success",
        "adjacent_regions": [
            {"region_id": "r_test2", "name": "Test Region 2", "direction": "north"}
        ],
    }
    service.regenerate_world.return_value = {
        "status": "success",
        "message": "World regenerated",
    }
    service.generate_new_continent.return_value = {
        "status": "success",
        "continent_id": "c_new",
    }
    service.generate_new_region.return_value = {
        "status": "success",
        "region_id": "r_new",
    }

    return service


@pytest.fixture
def app(mock_region_service): pass
    """Create a FastAPI app with the router and dependency override."""
    app = FastAPI()
    app.include_router(router, prefix="/api")

    # Override the dependency
    app.dependency_overrides[get_region_service] = lambda: mock_region_service

    return app


@pytest.fixture
def client(app): pass
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestRegionRouter: pass
    """Tests for the region system's FastAPI router."""

    def test_initialize_world(self, client, mock_region_service): pass
        """Test initializing the world."""
        # Test with default parameters
        response = client.get("/api/regions/initialize")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert mock_region_service.initialize.called

        # Test with custom parameters
        response = client.get(
            "/api/regions/initialize?seed=54321&load_existing=false"
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_region_service.initialize.assert_called_with(
            seed=54321, load_existing=False
        )

    def test_get_all_continents(self, client, mock_region_service): pass
        """Test getting all continents."""
        response = client.get("/api/regions/continents")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "continents" in response.json()
        assert len(response.json()["continents"]) == 2
        mock_region_service.get_all_continents.assert_called_once()

        # Test error case
        mock_region_service.get_all_continents.return_value = {
            "status": "error",
            "message": "World not initialized",
        }
        response = client.get("/api/regions/continents")
        assert response.status_code == 404
        assert "World not initialized" in response.json()["detail"]

    def test_get_continent(self, client, mock_region_service): pass
        """Test getting a specific continent."""
        response = client.get("/api/regions/continents/c_test1")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["continent"]["continent_id"] == "c_test1"
        mock_region_service.get_continent.assert_called_with("c_test1")

        # Test error case - continent not found
        mock_region_service.get_continent.return_value = {
            "status": "error",
            "message": "Continent not found",
        }
        response = client.get("/api/regions/continents/nonexistent")
        assert response.status_code == 404
        assert "Continent not found" in response.json()["detail"]

    def test_get_all_regions(self, client, mock_region_service): pass
        """Test getting all regions."""
        response = client.get("/api/regions/regions")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "regions" in response.json()
        assert len(response.json()["regions"]) == 2
        mock_region_service.get_all_regions.assert_called_once()

        # Test with continent filter
        response = client.get("/api/regions/regions?continent_id=c_test1")
        assert response.status_code == 200
        mock_region_service.get_all_regions.assert_called_with(continent_id="c_test1", biome_type=None)

        # Test with biome filter
        response = client.get("/api/regions/regions?biome_type=forest")
        assert response.status_code == 200
        mock_region_service.get_all_regions.assert_called_with(continent_id=None, biome_type="forest")

    def test_get_region(self, client, mock_region_service): pass
        """Test getting a specific region."""
        response = client.get("/api/regions/regions/r_test1")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["region"]["region_id"] == "r_test1"
        mock_region_service.get_region.assert_called_with("r_test1")

        # Test error case - region not found
        mock_region_service.get_region.return_value = {
            "status": "error",
            "message": "Region not found",
        }
        response = client.get("/api/regions/regions/nonexistent")
        assert response.status_code == 404
        assert "Region not found" in response.json()["detail"]

    def test_get_adjacent_regions(self, client, mock_region_service): pass
        """Test getting adjacent regions."""
        response = client.get("/api/regions/regions/r_test1/adjacent")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "adjacent_regions" in response.json()
        mock_region_service.get_adjacent_regions.assert_called_with("r_test1")

        # Test error case
        mock_region_service.get_adjacent_regions.return_value = {
            "status": "error",
            "message": "Region not found",
        }
        response = client.get("/api/regions/regions/nonexistent/adjacent")
        assert response.status_code == 404
        assert "Region not found" in response.json()["detail"]

    def test_regenerate_world(self, client, mock_region_service): pass
        """Test regenerating the world."""
        # Test with default parameters
        response = client.post("/api/regions/world/regenerate")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_region_service.regenerate_world.assert_called()

        # Test with custom parameters
        response = client.post(
            "/api/regions/world/regenerate?seed=54321&continent_count=5"
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_region_service.regenerate_world.assert_called_with(
            seed=54321,
            continent_count=5,
            region_constraints=None,
        )

        # Test error case
        mock_region_service.regenerate_world.return_value = {
            "status": "error",
            "message": "World not initialized",
        }
        response = client.post("/api/regions/world/regenerate")
        assert response.status_code == 500
        assert "World not initialized" in response.json()["detail"]

    def test_generate_continent(self, client, mock_region_service): pass
        """Test generating a new continent."""
        # Test with default parameters
        response = client.post("/api/regions/continents/generate")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_region_service.generate_new_continent.assert_called()

        # Test with custom parameters
        response = client.post(
            "/api/regions/continents/generate?continent_name=New Continent&origin_x=10&origin_y=20&size=15"
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_region_service.generate_new_continent.assert_called_with(
            continent_name="New Continent",
            origin=(10, 20),
            size=15,
            region_constraints=None,
        )

        # Test error case
        mock_region_service.generate_new_continent.return_value = {
            "status": "error",
            "message": "World not initialized",
        }
        response = client.post("/api/regions/continents/generate")
        assert response.status_code == 500
        assert "World not initialized" in response.json()["detail"]

    def test_generate_region(self, client, mock_region_service): pass
        """Test generating a new region."""
        # Test with default parameters
        response = client.post("/api/regions/regions/generate")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_region_service.generate_new_region.assert_called()

        # Test with custom parameters
        response = client.post(
            "/api/regions/regions/generate?name=New Region&x=5&y=10&continent_id=c_test1&biome_type=forest"
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_region_service.generate_new_region.assert_called_with(
            name="New Region",
            coordinates=(5, 10),
            continent_id="c_test1",
            forced_biome="forest",
            profile_constraints=None,
        )

        # Test error case
        mock_region_service.generate_new_region.return_value = {
            "status": "error",
            "message": "World not initialized",
        }
        response = client.post("/api/regions/regions/generate")
        assert response.status_code == 500
        assert "World not initialized" in response.json()["detail"]

    # Health endpoint not implemented in router - skipping test

    def test_world_metadata(self, client, mock_region_service): pass
        """Test getting world metadata."""
        mock_region_service.get_world_metadata.return_value = {
            "status": "success",
            "metadata": {"seed": 12345, "continent_count": 3, "region_count": 30},
        }

        response = client.get("/api/regions/world/metadata")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "metadata" in response.json()
        assert response.json()["metadata"]["seed"] == 12345
        mock_region_service.get_world_metadata.assert_called_once()

        # Test error case
        mock_region_service.get_world_metadata.return_value = {
            "status": "error",
            "message": "World not initialized",
        }
        response = client.get("/api/regions/world/metadata")
        assert response.status_code == 404
        assert "World not initialized" in response.json()["detail"]
