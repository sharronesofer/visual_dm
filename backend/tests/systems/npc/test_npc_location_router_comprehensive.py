"""
Comprehensive Tests for backend.systems.npc.routers.npc_location_router

This test suite focuses on achieving high coverage for the NPC location router endpoints.
Tests all location and movement endpoints.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException, FastAPI
from uuid import uuid4, UUID
import json

# Import the module being tested
try: pass
    from backend.systems.npc.routers.npc_location_router import router, get_location_service
except ImportError as e: pass
    pytest.skip(f"Could not import backend.systems.npc.routers.npc_location_router: {e}", allow_module_level=True)


@pytest.fixture
def mock_location_service(): pass
    """Mock NPC location service."""
    return Mock()


@pytest.fixture
def app(mock_location_service): pass
    """Create FastAPI app with router and mocked dependencies."""
    app = FastAPI()
    
    # Override the dependency
    def get_mock_location_service(): pass
        return mock_location_service
    
    app.dependency_overrides[get_location_service] = get_mock_location_service
    app.include_router(router)
    return app


@pytest.fixture
def client(app): pass
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_npc_id(): pass
    """Sample NPC UUID for testing."""
    return uuid4()


@pytest.fixture
def sample_npc_data(): pass
    """Sample NPC data for testing."""
    return {
        "id": "test-uuid",
        "character_name": "Test NPC",
        "mobility": {
            "home_poi": "5_7",
            "current_poi": "5_7",
            "radius": 2,
            "travel_chance": 0.15,
            "last_moved": "2024-01-01T12:00:00Z"
        },
        "travel_motive": "wander",
    }


class TestNPCLocationRouterUpdateLocation: pass
    """Test NPC location update endpoint."""
    
    def test_update_npc_location_success_stayed(self, client, mock_location_service, sample_npc_id): pass
        """Test successful location update when NPC stays."""
        result = {
            "npc_id": str(sample_npc_id),
            "stayed": True,
            "reason": "Low travel chance"
        }
        mock_location_service.update_npc_location.return_value = result
        
        response = client.post(f"/npcs/{sample_npc_id}/update-location")
        
        assert response.status_code == 200
        assert response.json() == result
        mock_location_service.update_npc_location.assert_called_once_with(sample_npc_id)
    
    def test_update_npc_location_success_moved(self, client, mock_location_service, sample_npc_id): pass
        """Test successful location update when NPC moves."""
        result = {
            "npc_id": str(sample_npc_id),
            "moved_to": "6_7",
            "motive": "wander",
            "previous_location": "5_7"
        }
        mock_location_service.update_npc_location.return_value = result
        
        response = client.post(f"/npcs/{sample_npc_id}/update-location")
        
        assert response.status_code == 200
        assert response.json() == result
        mock_location_service.update_npc_location.assert_called_once_with(sample_npc_id)
    
    def test_update_npc_location_error(self, client, mock_location_service, sample_npc_id): pass
        """Test location update when service returns error."""
        result = {"error": "NPC not found"}
        mock_location_service.update_npc_location.return_value = result
        
        response = client.post(f"/npcs/{sample_npc_id}/update-location")
        
        assert response.status_code == 400
        assert "NPC not found" in response.json()["detail"]
    
    def test_update_npc_location_invalid_uuid(self, client, mock_location_service): pass
        """Test location update with invalid UUID format."""
        invalid_id = "not-a-uuid"
        
        response = client.post(f"/npcs/{invalid_id}/update-location")
        
        assert response.status_code == 422  # Validation error
    
    def test_update_npc_location_service_exception(self, client, mock_location_service, sample_npc_id): pass
        """Test location update when service raises exception."""
        mock_location_service.update_npc_location.side_effect = Exception("Service error")
        
        # The current router implementation doesn't catch exceptions properly
        # so they bubble up and cause the test client to raise them
        with pytest.raises(Exception, match="Service error"): pass
            client.post(f"/npcs/{sample_npc_id}/update-location")


class TestNPCLocationRouterGetLocation: pass
    """Test NPC location retrieval endpoint."""
    
    def test_get_npc_location_success(self, client, mock_location_service, sample_npc_id, sample_npc_data): pass
        """Test successful location retrieval."""
        mock_location_service._get_npc.return_value = sample_npc_data
        
        response = client.get(f"/npcs/{sample_npc_id}/location")
        
        assert response.status_code == 200
        data = response.json()
        assert data["npc_id"] == str(sample_npc_id)
        assert data["current_location"] == "5_7"
        assert data["home_location"] == "5_7"
        assert data["last_moved"] == "2024-01-01T12:00:00Z"
        assert data["travel_motive"] == "wander"
        mock_location_service._get_npc.assert_called_once_with(sample_npc_id)
    
    def test_get_npc_location_minimal_data(self, client, mock_location_service, sample_npc_id): pass
        """Test location retrieval with minimal NPC data."""
        minimal_npc_data = {"id": "test-uuid"}  # Missing mobility and travel_motive
        mock_location_service._get_npc.return_value = minimal_npc_data
        
        response = client.get(f"/npcs/{sample_npc_id}/location")
        
        assert response.status_code == 200
        data = response.json()
        assert data["npc_id"] == str(sample_npc_id)
        assert data["current_location"] == "unknown"
        assert data["home_location"] == "unknown"
        assert data["last_moved"] is None
        assert data["travel_motive"] == "wander"
    
    def test_get_npc_location_partial_mobility(self, client, mock_location_service, sample_npc_id): pass
        """Test location retrieval with partial mobility data."""
        partial_npc_data = {
            "id": "test-uuid",
            "mobility": {
                "current_poi": "6_8"
                # Missing home_poi and last_moved
            },
            "travel_motive": "seek_revenge"
        }
        mock_location_service._get_npc.return_value = partial_npc_data
        
        response = client.get(f"/npcs/{sample_npc_id}/location")
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_location"] == "6_8"
        assert data["home_location"] == "unknown"
        assert data["last_moved"] is None
        assert data["travel_motive"] == "seek_revenge"
    
    def test_get_npc_location_not_found(self, client, mock_location_service, sample_npc_id): pass
        """Test location retrieval when NPC not found."""
        mock_location_service._get_npc.return_value = None
        
        response = client.get(f"/npcs/{sample_npc_id}/location")
        
        assert response.status_code == 404
        assert f"NPC {sample_npc_id} not found" in response.json()["detail"]
    
    def test_get_npc_location_invalid_uuid(self, client, mock_location_service): pass
        """Test location retrieval with invalid UUID format."""
        invalid_id = "not-a-uuid"
        
        response = client.get(f"/npcs/{invalid_id}/location")
        
        assert response.status_code == 422  # Validation error
    
    def test_get_npc_location_service_exception(self, client, mock_location_service, sample_npc_id): pass
        """Test location retrieval when service raises exception."""
        mock_location_service._get_npc.side_effect = Exception("Database error")
        
        # The current router implementation doesn't catch exceptions properly
        # so they bubble up and cause the test client to raise them
        with pytest.raises(Exception, match="Database error"): pass
            client.get(f"/npcs/{sample_npc_id}/location")


class TestNPCLocationRouterDailyMovementTick: pass
    """Test daily movement tick endpoint."""
    
    def test_run_daily_movement_tick_success(self, client, mock_location_service): pass
        """Test successful daily movement tick."""
        response = client.post("/npcs/daily-movement-tick")
        
        assert response.status_code == 200
        data = response.json()
        assert "Daily NPC movement tick completed" in data["message"]
        assert "npcs_moved" in data
        assert "npcs_stayed" in data
        assert data["npcs_moved"] == 0  # Stub implementation
        assert data["npcs_stayed"] == 0  # Stub implementation
    
    def test_run_daily_movement_tick_with_service_dependency(self, client, mock_location_service): pass
        """Test daily movement tick with service dependency injection."""
        # The endpoint doesn't currently use the service, but this tests the dependency injection
        response = client.post("/npcs/daily-movement-tick")
        
        assert response.status_code == 200
        # The service dependency is injected but not used in the current stub implementation


class TestNPCLocationRouterErrorHandling: pass
    """Test error handling scenarios."""
    
    def test_invalid_http_methods(self, client, sample_npc_id): pass
        """Test invalid HTTP methods on endpoints."""
        # Test wrong method on update-location (should be POST)
        response = client.get(f"/npcs/{sample_npc_id}/update-location")
        assert response.status_code == 405  # Method not allowed
        
        # Test wrong method on location (should be GET)
        response = client.post(f"/npcs/{sample_npc_id}/location")
        assert response.status_code == 405  # Method not allowed
        
        # Test wrong method on daily-movement-tick (should be POST)
        response = client.get("/npcs/daily-movement-tick")
        assert response.status_code == 405  # Method not allowed
    
    def test_malformed_uuid_formats(self, client): pass
        """Test various malformed UUID formats."""
        malformed_uuids = [
            "123",
            "not-a-uuid-at-all",
            "12345678-1234-1234-1234-12345678901",  # Too short
            "12345678-1234-1234-1234-1234567890123",  # Too long
            "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",  # Invalid characters
        ]
        
        for malformed_uuid in malformed_uuids: pass
            response = client.post(f"/npcs/{malformed_uuid}/update-location")
            assert response.status_code == 422
            
            response = client.get(f"/npcs/{malformed_uuid}/location")
            assert response.status_code == 422
    
    def test_empty_path_parameters(self, client): pass
        """Test endpoints with empty path parameters."""
        # Test with empty NPC ID
        response = client.post("/npcs//update-location")
        assert response.status_code == 404  # Not found due to path mismatch
        
        response = client.get("/npcs//location")
        assert response.status_code == 404  # Not found due to path mismatch


class TestNPCLocationRouterIntegration: pass
    """Test integration scenarios."""
    
    def test_location_workflow_sequence(self, client, mock_location_service, sample_npc_id, sample_npc_data): pass
        """Test a complete workflow: get location, update location, get location again."""
        # First, get initial location
        mock_location_service._get_npc.return_value = sample_npc_data
        
        response1 = client.get(f"/npcs/{sample_npc_id}/location")
        assert response1.status_code == 200
        initial_location = response1.json()["current_location"]
        
        # Then, update location (NPC moves)
        update_result = {
            "npc_id": str(sample_npc_id),
            "moved_to": "6_7",
            "motive": "wander",
            "previous_location": initial_location
        }
        mock_location_service.update_npc_location.return_value = update_result
        
        response2 = client.post(f"/npcs/{sample_npc_id}/update-location")
        assert response2.status_code == 200
        assert response2.json()["moved_to"] == "6_7"
        
        # Finally, get updated location
        updated_npc_data = {**sample_npc_data}
        updated_npc_data["mobility"]["current_poi"] = "6_7"
        mock_location_service._get_npc.return_value = updated_npc_data
        
        response3 = client.get(f"/npcs/{sample_npc_id}/location")
        assert response3.status_code == 200
        assert response3.json()["current_location"] == "6_7"
    
    def test_multiple_npc_operations(self, client, mock_location_service, sample_npc_data): pass
        """Test operations on multiple NPCs."""
        npc_ids = [uuid4() for _ in range(3)]
        
        for npc_id in npc_ids: pass
            # Test location retrieval for each NPC
            mock_location_service._get_npc.return_value = sample_npc_data
            response = client.get(f"/npcs/{npc_id}/location")
            assert response.status_code == 200
            assert response.json()["npc_id"] == str(npc_id)
            
            # Test location update for each NPC
            update_result = {"npc_id": str(npc_id), "stayed": True}
            mock_location_service.update_npc_location.return_value = update_result
            response = client.post(f"/npcs/{npc_id}/update-location")
            assert response.status_code == 200
            assert response.json()["npc_id"] == str(npc_id)
    
    def test_edge_case_location_data(self, client, mock_location_service, sample_npc_id): pass
        """Test edge cases in location data."""
        edge_case_data = [
            # Empty mobility
            {"id": "test-uuid", "mobility": {}},
            # Null values in mobility
            {"id": "test-uuid", "mobility": {"current_poi": None, "home_poi": None}},
            # Missing travel_motive
            {"id": "test-uuid", "mobility": {"current_poi": "5_7"}},
            # Empty strings
            {"id": "test-uuid", "mobility": {"current_poi": "", "home_poi": ""}},
        ]
        
        for npc_data in edge_case_data: pass
            mock_location_service._get_npc.return_value = npc_data
            response = client.get(f"/npcs/{sample_npc_id}/location")
            assert response.status_code == 200
            # Should handle edge cases gracefully
            data = response.json()
            assert "npc_id" in data
            assert "current_location" in data
            assert "home_location" in data 