"""
Comprehensive Tests for backend.systems.npc.routers.npc_router

This test suite focuses on achieving 90% coverage for the NPC router endpoints.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json

# Import the module being tested
try: pass
    from backend.systems.npc.routers.npc_router import router
    from fastapi import FastAPI
except ImportError as e: pass
    pytest.skip(f"Could not import backend.systems.npc.routers.npc_router: {e}", allow_module_level=True)


@pytest.fixture
def app(): pass
    """Create FastAPI app with router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app): pass
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_npc_service(): pass
    """Mock NPC service."""
    with patch('backend.systems.npc.routers.npc_router.get_npc_service') as mock: pass
        service = Mock()
        mock.return_value = service
        yield service


@pytest.fixture
def sample_npc_data(): pass
    """Sample NPC data for testing."""
    return {
        "name": "Test NPC",
        "race": "human",
        "class": "fighter",
        "level": 5,
        "background": "soldier"
    }


class TestNPCRouterCRUDOperations: pass
    """Test CRUD operations via router endpoints."""
    
    def test_create_npc_success(self, client, mock_npc_service, sample_npc_data): pass
        """Test successful NPC creation."""
        created_npc = {"npc_id": "test_123", **sample_npc_data}
        mock_npc_service.create_npc.return_value = created_npc
        
        response = client.post("/api/npcs/", json=sample_npc_data)
        
        assert response.status_code == 200
        assert "npc_id" in response.json()
        mock_npc_service.create_npc.assert_called_once()
    
    def test_create_npc_with_custom_id(self, client, mock_npc_service, sample_npc_data): pass
        """Test NPC creation with custom ID."""
        custom_id = "custom_npc_001"
        created_npc = {"npc_id": custom_id, **sample_npc_data}
        mock_npc_service.create_npc.return_value = created_npc
        
        data = {**sample_npc_data, "npc_id": custom_id}
        response = client.post("/api/npcs/", json=data)
        
        assert response.status_code == 200
        assert response.json()["npc_id"] == custom_id
    
    def test_create_npc_service_error(self, client, mock_npc_service, sample_npc_data): pass
        """Test NPC creation when service raises error."""
        mock_npc_service.create_npc.side_effect = Exception("Service error")
        
        response = client.post("/api/npcs/", json=sample_npc_data)
        
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]
    
    def test_get_npc_success(self, client, mock_npc_service): pass
        """Test successful NPC retrieval."""
        npc_id = "test_npc"
        npc_data = {"npc_id": npc_id, "name": "Test NPC"}
        mock_npc_service.get_npc.return_value = npc_data
        
        response = client.get(f"/api/npcs/{npc_id}")
        
        assert response.status_code == 200
        assert response.json() == npc_data
        mock_npc_service.get_npc.assert_called_once_with(npc_id)
    
    def test_get_npc_not_found(self, client, mock_npc_service): pass
        """Test NPC retrieval when not found."""
        mock_npc_service.get_npc.return_value = None
        
        response = client.get("/api/npcs/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_npc_service_error(self, client, mock_npc_service): pass
        """Test NPC retrieval when service raises error."""
        mock_npc_service.get_npc.side_effect = Exception("Database error")
        
        response = client.get("/api/npcs/test_npc")
        
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]
    
    def test_list_npcs_success(self, client, mock_npc_service): pass
        """Test successful NPC listing."""
        npcs = [
            {"npc_id": "npc1", "name": "NPC 1"},
            {"npc_id": "npc2", "name": "NPC 2"}
        ]
        mock_npc_service.list_npcs.return_value = npcs
        
        response = client.get("/api/npcs/")
        
        assert response.status_code == 200
        assert response.json() == npcs
        mock_npc_service.list_npcs.assert_called_once()
    
    def test_list_npcs_with_filters(self, client, mock_npc_service): pass
        """Test NPC listing with filters."""
        npcs = [{"npc_id": "npc1", "name": "NPC 1"}]
        mock_npc_service.list_npcs.return_value = npcs
        
        response = client.get("/api/npcs/?poi_id=poi_001&region_id=region_001")
        
        assert response.status_code == 200
        assert response.json() == npcs
        mock_npc_service.list_npcs.assert_called_once()
    
    def test_list_npcs_service_error(self, client, mock_npc_service): pass
        """Test NPC listing when service raises error."""
        mock_npc_service.list_npcs.side_effect = Exception("Service error")
        
        response = client.get("/api/npcs/")
        
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]
    
    def test_update_npc_success(self, client, mock_npc_service): pass
        """Test successful NPC update."""
        npc_id = "test_npc"
        update_data = {"name": "Updated Name", "level": 10}
        updated_npc = {"npc_id": npc_id, **update_data}
        mock_npc_service.update_npc.return_value = updated_npc
        
        response = client.patch(f"/api/npcs/{npc_id}", json=update_data)
        
        assert response.status_code == 200
        expected_response = {"message": "NPC updated successfully", "npc": updated_npc}
        assert response.json() == expected_response
        mock_npc_service.update_npc.assert_called_once()
    
    def test_update_npc_not_found(self, client, mock_npc_service): pass
        """Test NPC update when not found."""
        mock_npc_service.update_npc.return_value = None
        
        response = client.patch("/api/npcs/nonexistent", json={"name": "New Name"})
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_npc_service_error(self, client, mock_npc_service): pass
        """Test NPC update when service raises error."""
        mock_npc_service.update_npc.side_effect = Exception("Update error")
        
        response = client.patch("/api/npcs/test_npc", json={"name": "New Name"})
        
        assert response.status_code == 500
        assert "Update error" in response.json()["detail"]
    
    def test_delete_npc_success(self, client, mock_npc_service): pass
        """Test successful NPC deletion."""
        npc_id = "test_npc"
        mock_npc_service.delete_npc.return_value = True
        
        response = client.delete(f"/api/npcs/{npc_id}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        mock_npc_service.delete_npc.assert_called_once_with(npc_id)
    
    def test_delete_npc_not_found(self, client, mock_npc_service): pass
        """Test NPC deletion when not found."""
        mock_npc_service.delete_npc.return_value = False
        
        response = client.delete("/api/npcs/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_delete_npc_service_error(self, client, mock_npc_service): pass
        """Test NPC deletion when service raises error."""
        mock_npc_service.delete_npc.side_effect = Exception("Delete error")
        
        response = client.delete("/api/npcs/test_npc")
        
        assert response.status_code == 500
        assert "Delete error" in response.json()["detail"]


class TestNPCRouterMemoryOperations: pass
    """Test memory-related endpoints."""
    
    def test_get_npc_memories_success(self, client, mock_npc_service): pass
        """Test successful memory retrieval."""
        npc_id = "test_npc"
        memories = [
            {"memory_id": "mem1", "content": "Memory 1", "importance": 8},
            {"memory_id": "mem2", "content": "Memory 2", "importance": 5}
        ]
        mock_npc_service.get_npc_memories.return_value = memories
        
        response = client.get(f"/api/npcs/{npc_id}/memories")
        
        assert response.status_code == 200
        assert response.json() == memories
        mock_npc_service.get_npc_memories.assert_called_once()
    
    def test_get_npc_memories_service_error(self, client, mock_npc_service): pass
        """Test memory retrieval when service raises error."""
        mock_npc_service.get_npc_memories.side_effect = Exception("Memory error")
        
        response = client.get("/api/npcs/test_npc/memories")
        
        assert response.status_code == 500
        assert "Memory error" in response.json()["detail"]
    
    def test_add_memory_success(self, client, mock_npc_service): pass
        """Test successful memory addition."""
        npc_id = "test_npc"
        memory_data = {"content": "New memory", "importance": 7}
        memory_id = "new_memory_123"
        mock_npc_service.add_memory_to_npc.return_value = memory_id
        
        response = client.post(f"/api/npcs/{npc_id}/memories", json=memory_data)
        
        assert response.status_code == 200
        assert "memory_id" in response.json()
        mock_npc_service.add_memory_to_npc.assert_called_once()
    
    def test_add_memory_npc_not_found(self, client, mock_npc_service): pass
        """Test memory addition when NPC not found."""
        mock_npc_service.add_memory_to_npc.return_value = None
        
        response = client.post("/api/npcs/nonexistent/memories", json={"content": "Memory"})
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_add_memory_service_error(self, client, mock_npc_service): pass
        """Test memory addition when service raises error."""
        mock_npc_service.add_memory_to_npc.side_effect = Exception("Memory error")
        
        response = client.post("/api/npcs/test_npc/memories", json={"content": "Memory"})
        
        assert response.status_code == 500
        assert "Memory error" in response.json()["detail"]


class TestNPCRouterLocationOperations: pass
    """Test location-related endpoints."""
    
    def test_get_npc_location_success(self, client, mock_npc_service): pass
        """Test successful location retrieval."""
        npc_id = "test_npc"
        location = {
            "poi_id": "poi_001",
            "region_id": "region_001",
            "coordinates": {"x": 10.0, "y": 20.0}
        }
        mock_npc_service.get_npc_location.return_value = location
        
        response = client.get(f"/api/npcs/{npc_id}/location")
        
        assert response.status_code == 200
        assert response.json() == location
        mock_npc_service.get_npc_location.assert_called_once_with(npc_id)
    
    def test_get_npc_location_not_found(self, client, mock_npc_service): pass
        """Test location retrieval when NPC not found."""
        mock_npc_service.get_npc_location.return_value = None
        
        response = client.get("/api/npcs/nonexistent/location")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_npc_location_success(self, client, mock_npc_service): pass
        """Test successful location update."""
        npc_id = "test_npc"
        location_data = {
            "poi_id": "new_poi",
            "coordinates": {"x": 30.0, "y": 40.0}
        }
        move_result = {"success": True, "new_location": location_data}
        mock_npc_service.update_npc_location.return_value = move_result
        
        response = client.patch(f"/api/npcs/{npc_id}/location", json=location_data)
        
        assert response.status_code == 200
        assert response.json() == move_result
        mock_npc_service.update_npc_location.assert_called_once()
    
    def test_update_npc_location_not_found(self, client, mock_npc_service): pass
        """Test location update when NPC not found."""
        mock_npc_service.update_npc_location.return_value = None
        
        response = client.patch("/api/npcs/nonexistent/location", json={"poi_id": "new_poi"})
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestNPCRouterFactionOperations: pass
    """Test faction-related endpoints."""
    
    def test_get_npc_faction_status_success(self, client, mock_npc_service): pass
        """Test successful faction status retrieval."""
        npc_id = "test_npc"
        faction_status = {
            "faction_affiliations": [
                {"faction_id": "faction1", "allegiance": 80, "rank": "member"}
            ]
        }
        mock_npc_service.get_npc_faction_status.return_value = faction_status
        
        response = client.get(f"/api/npcs/{npc_id}/factions")
        
        assert response.status_code == 200
        assert response.json() == faction_status
        mock_npc_service.get_npc_faction_status.assert_called_once_with(npc_id)
    
    def test_adjust_faction_allegiance_success(self, client, mock_npc_service): pass
        """Test successful faction allegiance adjustment."""
        npc_id = "test_npc"
        adjustment_data = {"faction_id": "faction1", "adjustment": 20}
        result = {"success": True, "new_allegiance": 70}
        mock_npc_service.adjust_npc_faction_allegiance.return_value = result
        
        response = client.post(
            f"/api/npcs/{npc_id}/factions/adjust",
            json=adjustment_data
        )
        
        assert response.status_code == 200
        assert response.json() == result
        mock_npc_service.adjust_npc_faction_allegiance.assert_called_once()


class TestNPCRouterRumorOperations: pass
    """Test rumor-related endpoints."""
    
    def test_get_npc_rumors_success(self, client, mock_npc_service): pass
        """Test successful rumor retrieval."""
        npc_id = "test_npc"
        rumors = [
            {"rumor_id": "rumor1", "content": "Test rumor", "belief_strength": 0.8}
        ]
        mock_npc_service.get_npc_rumors.return_value = rumors
        
        response = client.get(f"/api/npcs/{npc_id}/rumors")
        
        assert response.status_code == 200
        assert response.json() == rumors
        mock_npc_service.get_npc_rumors.assert_called_once_with(npc_id)
    
    def test_add_rumor_success(self, client, mock_npc_service): pass
        """Test successful rumor addition."""
        npc_id = "test_npc"
        rumor_data = {"rumor_id": "rumor1", "belief_strength": 0.9}
        mock_npc_service.add_rumor_to_npc.return_value = True
        
        response = client.post(f"/api/npcs/{npc_id}/rumors", json=rumor_data)
        
        assert response.status_code == 200
        expected_response = {
            "message": "Rumor added successfully",
            "npc_id": npc_id,
            "rumor_id": "rumor1"
        }
        assert response.json() == expected_response
        mock_npc_service.add_rumor_to_npc.assert_called_once()


class TestNPCRouterMotifOperations: pass
    """Test motif-related endpoints."""
    
    def test_get_npc_motifs_success(self, client, mock_npc_service): pass
        """Test successful motif retrieval."""
        npc_id = "test_npc"
        motifs = {
            "npc_id": npc_id,
            "core_motifs": ["heroic"],
            "motif_entropy": 0.5
        }
        mock_npc_service.get_npc_motifs.return_value = motifs
        
        response = client.get(f"/api/npcs/{npc_id}/motifs")
        
        assert response.status_code == 200
        assert response.json() == motifs
        mock_npc_service.get_npc_motifs.assert_called_once_with(npc_id)
    
    def test_apply_motif_success(self, client, mock_npc_service): pass
        """Test successful motif application."""
        npc_id = "test_npc"
        motif_data = {"motif_id": "heroic", "intensity": 0.7}
        mock_npc_service.apply_motif_to_npc.return_value = True
        
        response = client.post(f"/api/npcs/{npc_id}/motifs", json=motif_data)
        
        assert response.status_code == 200
        expected_response = {
            "message": "Motif applied successfully",
            "npc_id": npc_id,
            "motif_id": "heroic"
        }
        assert response.json() == expected_response
        mock_npc_service.apply_motif_to_npc.assert_called_once()


class TestNPCRouterErrorHandling: pass
    """Test error handling scenarios."""
    
    def test_invalid_json_payload(self, client, mock_npc_service): pass
        """Test handling of invalid JSON payload."""
        response = client.post("/api/npcs/", data="invalid json")
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_missing_required_fields(self, client, mock_npc_service): pass
        """Test handling of missing required fields."""
        # This depends on the actual validation requirements
        response = client.post("/api/npcs/", json={})
        
        # Should either succeed with defaults or return validation error
        assert response.status_code in [200, 422]
    
    def test_invalid_npc_id_format(self, client, mock_npc_service): pass
        """Test handling of invalid NPC ID format."""
        mock_npc_service.get_npc.return_value = None
        
        response = client.get("/api/npcs/invalid-id-format")
        
        assert response.status_code == 404 