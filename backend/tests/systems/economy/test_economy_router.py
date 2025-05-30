from backend.systems.economy.models import Resource
from backend.systems.economy.models import Resource
from backend.systems.economy.models import Resource
from backend.systems.economy.models import Resource
from backend.systems.economy.models import Resource
from backend.systems.economy.models import Resource
"""
Tests for the economy router module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from httpx import AsyncClient

from backend.systems.economy.routers.economy_router import router, get_economy_service


@pytest.fixture
def app():
    """Create a FastAPI app for testing."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_economy_service():
    """Create a mock economy service."""
    service = AsyncMock()
    service.repository = AsyncMock()
    return service


@pytest.fixture
def sample_resource():
    """Create sample resource for testing."""
    resource = MagicMock()
    resource.to_data_model.return_value = {
        "id": "1",
        "name": "Gold",
        "type": "GOLD",
        "price": 100.0,
        "amount": 500.0,
        "region_id": "1",
        "supply": 100.0,
        "demand": 80.0,
        "tax_rate": 0.05,
        "description": "",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
        "metadata": {}
    }
    return resource


@pytest.fixture
def sample_metric():
    """Create sample economic metric for testing."""
    return {
        "metric_type": "gold",
        "value": 100.0,
        "region_id": 1,
        "faction_id": None,
        "resource_id": 1,
        "timestamp": "2023-01-01T00:00:00"
    }


class TestEconomyRouter:
    """Test suite for the economy router."""

    def test_get_resource_success(self, client, mock_economy_service, sample_resource):
        """Test successful resource retrieval."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.repository.get_resource.return_value = sample_resource
        
        try:
            response = client.get("/economy/resources/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Gold"
            assert data["type"] == "GOLD"
            assert data["price"] == 100.0
        finally: pass
            # Clean up dependency override
            client.app.dependency_overrides.clear()

    def test_get_resource_not_found(self, client, mock_economy_service):
        """Test resource not found."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.repository.get_resource.return_value = None
        
        try:
            response = client.get("/economy/resources/999")
            
            assert response.status_code == 404
            assert "Resource not found" in response.json()["detail"]
        finally: pass
            # Clean up dependency override
            client.app.dependency_overrides.clear()

    def test_get_region_resources_success(self, client, mock_economy_service, sample_resource):
        """Test successful region resources retrieval."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.repository.get_resources_by_region.return_value = [sample_resource]
        
        try:
            response = client.get("/economy/regions/1/resources")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["name"] == "Gold"
        finally: pass
            # Clean up dependency override
            client.app.dependency_overrides.clear()

    def test_get_region_resources_empty(self, client, mock_economy_service):
        """Test region with no resources."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.repository.get_resources_by_region.return_value = []
        
        try:
            response = client.get("/economy/regions/999/resources")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0
        finally: pass
            # Clean up dependency override
            client.app.dependency_overrides.clear()

    def test_get_metrics_success(self, client, mock_economy_service, sample_metric):
        """Test successful metrics retrieval."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.repository.get_metrics_history.return_value = [sample_metric]
        
        try:
            response = client.get("/economy/metrics/gold")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["metric_type"] == "gold"
            assert data[0]["value"] == 100.0
        finally: pass
            # Clean up dependency override
            client.app.dependency_overrides.clear()

    def test_get_metrics_with_filters(self, client, mock_economy_service, sample_metric):
        """Test metrics retrieval with filters."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.repository.get_metrics_history.return_value = [sample_metric]
        
        try:
            response = client.get("/economy/metrics/supply?region_id=1&faction_id=2&resource_id=3&limit=5")
            
            assert response.status_code == 200
            # Verify the service was called
            mock_economy_service.repository.get_metrics_history.assert_called_once()
        finally
            # Clean up dependency override
            client.app.dependency_overrides.clear()

    def test_get_metrics_empty(self, client, mock_economy_service):
        """Test metrics retrieval with no results."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.repository.get_metrics_history.return_value = []
        
        try:
            response = client.get("/economy/metrics/demand")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0
        finally: pass
            # Clean up dependency override
            client.app.dependency_overrides.clear()

    def test_adjust_resource_price_success(self, client, mock_economy_service):
        """Test successful resource price adjustment."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.adjust_price.return_value = 120.0
        
        try:
            response = client.post("/economy/resources/1/price/adjust")
            
            assert response.status_code == 200
            data = response.json()
            assert data["resource_id"] == 1
            assert data["new_price"] == 120.0
        finally: pass
            # Clean up dependency override
            client.app.dependency_overrides.clear()

    def test_adjust_resource_price_not_found(self, client, mock_economy_service):
        """Test resource price adjustment for non-existent resource."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.adjust_price.side_effect = ValueError("Resource not found")
        
        try:
            response = client.post("/economy/resources/999/price/adjust")
            
            assert response.status_code == 404
            assert "Resource not found" in response.json()["detail"]
        finally: pass
            # Clean up dependency override
            client.app.dependency_overrides.clear()

    def test_trade_resources_success(self, client, mock_economy_service):
        """Test successful resource trade."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.transfer_resources.return_value = True
        
        try:
            response = client.post("/economy/trade?source_region_id=1&target_region_id=2&resource_id=1&amount=100.0")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["source_region_id"] == 1
            assert data["target_region_id"] == 2
            assert data["resource_id"] == 1
            assert data["amount"] == 100.0
        finally: pass
            # Clean up dependency override
            client.app.dependency_overrides.clear()

    def test_trade_resources_failure(self, client, mock_economy_service):
        """Test failed resource trade."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.transfer_resources.return_value = False
        
        try:
            response = client.post("/economy/trade?source_region_id=1&target_region_id=2&resource_id=1&amount=1000.0")
            
            assert response.status_code == 400
            assert "Trade failed" in response.json()["detail"]
        finally: pass
            # Clean up dependency override
            client.app.dependency_overrides.clear()

    def test_router_has_correct_prefix_and_tags(self):
        """Test that router has correct configuration."""
        assert router.prefix == "/economy"
        assert router.tags == ["economy"]

    def test_dependency_function_exists(self):
        """Test that get_economy_service dependency function exists."""
        assert callable(get_economy_service)

    def test_trade_resources_query_params(self, client, mock_economy_service):
        """Test resource trade with query parameters."""
        # Override the dependency
        def override_get_economy_service():
            return mock_economy_service
        
        client.app.dependency_overrides[get_economy_service] = override_get_economy_service
        
        # Setup mock
        mock_economy_service.transfer_resources.return_value = True
        
        try:
            response = client.post(
                "/economy/trade",
                params={
                    "source_region_id": 1,
                    "target_region_id": 2,
                    "resource_id": 1,
                    "amount": 50.5
                }
            )
            
            assert response.status_code == 200
            # Verify the service was called with correct parameters
            mock_economy_service.transfer_resources.assert_called_once()
        finally:
            # Clean up dependency override
            client.app.dependency_overrides.clear()
