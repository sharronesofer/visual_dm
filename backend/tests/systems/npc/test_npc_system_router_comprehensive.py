"""
Comprehensive Tests for backend.systems.npc.routers.npc_system_router

This test suite focuses on achieving 90% coverage for the NPC system router endpoints.
Tests all memory, faction, rumor, population, and motif endpoints.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException, FastAPI
import json

# Import the module being tested
try: pass
    from backend.systems.npc.routers.npc_system_router import router
except ImportError as e: pass
    pytest.skip(f"Could not import backend.systems.npc.routers.npc_system_router: {e}", allow_module_level=True)


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
    with patch('backend.systems.npc.routers.npc_system_router.get_npc_service') as mock: pass
        service = Mock()
        mock.return_value = service
        yield service


@pytest.fixture
def sample_npc_id(): pass
    """Sample NPC ID for testing."""
    return "test_npc_123"


@pytest.fixture
def sample_memory_data(): pass
    """Sample memory data for testing."""
    return {
        "content": "Test memory content",
        "importance": 8,
        "tags": ["combat", "victory"],
        "related_npcs": ["npc_001"],
        "related_factions": ["faction_001"],
        "related_locations": ["poi_001"]
    }


class TestNPCSystemRouterMemoryEndpoints: pass
    """Test memory-related endpoints."""
    
    def test_get_npc_memories_success(self, client, mock_npc_service, sample_npc_id): pass
        """Test successful memory retrieval."""
        memories = [
            {"memory_id": "mem1", "content": "Memory 1", "importance": 8},
            {"memory_id": "mem2", "content": "Memory 2", "importance": 5}
        ]
        mock_npc_service.get_npc_memories.return_value = memories
        
        response = client.get(f"/api/npc/systems/memories/{sample_npc_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["npc_id"] == sample_npc_id
        assert data["memories"] == memories
        mock_npc_service.get_npc_memories.assert_called_once_with(sample_npc_id, 10, 0, None)
    
    def test_get_npc_memories_with_params(self, client, mock_npc_service, sample_npc_id): pass
        """Test memory retrieval with query parameters."""
        memories = [{"memory_id": "mem1", "content": "Memory 1"}]
        mock_npc_service.get_npc_memories.return_value = memories
        
        response = client.get(
            f"/api/npc/systems/memories/{sample_npc_id}?limit=5&offset=10&tags=combat&tags=victory"
        )
        
        assert response.status_code == 200
        mock_npc_service.get_npc_memories.assert_called_once_with(sample_npc_id, 5, 10, ["combat", "victory"])
    
    def test_get_npc_memories_service_error(self, client, mock_npc_service, sample_npc_id): pass
        """Test memory retrieval when service raises error."""
        mock_npc_service.get_npc_memories.side_effect = Exception("Memory error")
        
        response = client.get(f"/api/npc/systems/memories/{sample_npc_id}")
        
        assert response.status_code == 500
        assert "Memory error" in response.json()["detail"]
    
    def test_create_npc_memory_success(self, client, mock_npc_service, sample_npc_id, sample_memory_data): pass
        """Test successful memory creation."""
        memory_id = "new_memory_123"
        mock_npc_service.add_memory_to_npc.return_value = memory_id
        
        response = client.post(f"/api/npc/systems/memories/{sample_npc_id}", json=sample_memory_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["npc_id"] == sample_npc_id
        assert data["memory_id"] == memory_id
        assert "Memory created successfully" in data["message"]
        mock_npc_service.add_memory_to_npc.assert_called_once_with(
            npc_id=sample_npc_id,
            content=sample_memory_data["content"],
            importance=sample_memory_data["importance"],
            tags=sample_memory_data["tags"],
            related_npcs=sample_memory_data["related_npcs"],
            related_factions=sample_memory_data["related_factions"],
            related_locations=sample_memory_data["related_locations"]
        )
    
    def test_create_npc_memory_service_error(self, client, mock_npc_service, sample_npc_id, sample_memory_data): pass
        """Test memory creation when service raises error."""
        mock_npc_service.add_memory_to_npc.side_effect = Exception("Creation error")
        
        response = client.post(f"/api/npc/systems/memories/{sample_npc_id}", json=sample_memory_data)
        
        assert response.status_code == 500
        assert "Creation error" in response.json()["detail"]
    
    def test_delete_npc_memory_success(self, client, mock_npc_service, sample_npc_id): pass
        """Test successful memory deletion."""
        memory_id = "memory_to_delete"
        mock_npc_service.forget_memory.return_value = True
        
        response = client.delete(f"/api/npc/systems/memories/{sample_npc_id}/{memory_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["npc_id"] == sample_npc_id
        assert data["memory_id"] == memory_id
        assert "Memory deleted successfully" in data["message"]
        mock_npc_service.forget_memory.assert_called_once_with(sample_npc_id, memory_id)
    
    def test_delete_npc_memory_not_found(self, client, mock_npc_service, sample_npc_id): pass
        """Test memory deletion when memory not found."""
        memory_id = "nonexistent_memory"
        mock_npc_service.forget_memory.return_value = False
        
        response = client.delete(f"/api/npc/systems/memories/{sample_npc_id}/{memory_id}")
        
        # The current implementation catches HTTPException and re-raises as 500
        # This is a design issue but we test the current behavior
        assert response.status_code == 500
        assert "Memory not found" in response.json()["detail"]
    
    def test_delete_npc_memory_service_error(self, client, mock_npc_service, sample_npc_id): pass
        """Test memory deletion when service raises error."""
        memory_id = "memory_to_delete"
        mock_npc_service.forget_memory.side_effect = Exception("Delete error")
        
        response = client.delete(f"/api/npc/systems/memories/{sample_npc_id}/{memory_id}")
        
        assert response.status_code == 500
        assert "Delete error" in response.json()["detail"]
    
    def test_get_npc_memory_summary_success(self, client, mock_npc_service, sample_npc_id): pass
        """Test successful memory summary retrieval."""
        memories = [
            {"memory_id": f"mem{i}", "content": f"Memory {i}", "importance": 8-i}
            for i in range(10)
        ]
        mock_npc_service.get_npc_memories.return_value = memories
        
        response = client.get(f"/api/npc/systems/memories/{sample_npc_id}/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["npc_id"] == sample_npc_id
        assert data["summary"]["total_memories"] == 10
        assert len(data["summary"]["recent_memories"]) == 5
        mock_npc_service.get_npc_memories.assert_called_once_with(sample_npc_id, limit=100)
    
    def test_get_npc_memory_summary_service_error(self, client, mock_npc_service, sample_npc_id): pass
        """Test memory summary when service raises error."""
        mock_npc_service.get_npc_memories.side_effect = Exception("Summary error")
        
        response = client.get(f"/api/npc/systems/memories/{sample_npc_id}/summary")
        
        assert response.status_code == 500
        assert "Summary error" in response.json()["detail"]


class TestNPCSystemRouterFactionEndpoints: pass
    """Test faction-related endpoints."""
    
    def test_get_npc_faction_status_success(self, client, mock_npc_service, sample_npc_id): pass
        """Test successful faction status retrieval."""
        faction_status = {
            "faction_affiliations": [
                {"faction_id": "faction1", "allegiance": 80, "rank": "member"}
            ]
        }
        mock_npc_service.get_npc_faction_status.return_value = faction_status
        
        response = client.get(f"/api/npc/systems/factions/{sample_npc_id}")
        
        assert response.status_code == 200
        assert response.json() == faction_status
        mock_npc_service.get_npc_faction_status.assert_called_once_with(sample_npc_id)
    
    def test_get_npc_faction_status_service_error(self, client, mock_npc_service, sample_npc_id): pass
        """Test faction status when service raises error."""
        mock_npc_service.get_npc_faction_status.side_effect = Exception("Faction error")
        
        response = client.get(f"/api/npc/systems/factions/{sample_npc_id}")
        
        assert response.status_code == 500
        assert "Faction error" in response.json()["detail"]
    
    def test_adjust_npc_faction_allegiance_success(self, client, mock_npc_service, sample_npc_id): pass
        """Test successful faction allegiance adjustment."""
        adjustment_data = {
            "faction_id": "faction1",
            "adjustment": 20,
            "reason": "heroic deed"
        }
        result = {"success": True, "new_allegiance": 70}
        mock_npc_service.adjust_npc_faction_allegiance.return_value = result
        
        response = client.post(
            f"/api/npc/systems/factions/{sample_npc_id}/adjust",
            json=adjustment_data
        )
        
        assert response.status_code == 200
        assert response.json() == result
        mock_npc_service.adjust_npc_faction_allegiance.assert_called_once_with(
            npc_id=sample_npc_id,
            faction_id="faction1",
            adjustment=20,
            reason="heroic deed"
        )
    
    def test_adjust_npc_faction_allegiance_service_error(self, client, mock_npc_service, sample_npc_id): pass
        """Test faction allegiance adjustment when service raises error."""
        adjustment_data = {"faction_id": "faction1", "adjustment": 20}
        mock_npc_service.adjust_npc_faction_allegiance.side_effect = Exception("Adjustment error")
        
        response = client.post(
            f"/api/npc/systems/factions/{sample_npc_id}/adjust",
            json=adjustment_data
        )
        
        assert response.status_code == 500
        assert "Adjustment error" in response.json()["detail"]


class TestNPCSystemRouterRumorEndpoints: pass
    """Test rumor-related endpoints."""
    
    def test_get_npc_rumors_success(self, client, mock_npc_service, sample_npc_id): pass
        """Test successful rumor retrieval."""
        rumors = [
            {"rumor_id": "rumor1", "content": "Test rumor", "belief_strength": 0.8}
        ]
        mock_npc_service.get_npc_rumors.return_value = rumors
        
        response = client.get(f"/api/npc/systems/rumors/{sample_npc_id}")
        
        assert response.status_code == 200
        assert response.json() == rumors
        mock_npc_service.get_npc_rumors.assert_called_once_with(sample_npc_id)
    
    def test_get_npc_rumors_service_error(self, client, mock_npc_service, sample_npc_id): pass
        """Test rumor retrieval when service raises error."""
        mock_npc_service.get_npc_rumors.side_effect = Exception("Rumor error")
        
        response = client.get(f"/api/npc/systems/rumors/{sample_npc_id}")
        
        assert response.status_code == 500
        assert "Rumor error" in response.json()["detail"]
    
    def test_seed_rumor_to_npcs_success(self, client, mock_npc_service): pass
        """Test successful rumor seeding."""
        seed_data = {"rumor_id": "rumor1", "seed_count": 3}
        all_npcs = [
            {"npc_id": "npc1"}, {"npc_id": "npc2"}, {"npc_id": "npc3"}, {"npc_id": "npc4"}
        ]
        mock_npc_service.list_npcs.return_value = all_npcs
        mock_npc_service.add_rumor_to_npc.return_value = True
        
        with patch('random.sample', return_value=[{"npc_id": "npc1"}, {"npc_id": "npc2"}, {"npc_id": "npc3"}]): pass
            response = client.post("/api/npc/systems/rumors/seed", json=seed_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["rumor_id"] == "rumor1"
        assert len(data["seeded_npcs"]) == 3
        assert mock_npc_service.add_rumor_to_npc.call_count == 3
    
    def test_seed_rumor_to_npcs_service_error(self, client, mock_npc_service): pass
        """Test rumor seeding when service raises error."""
        seed_data = {"rumor_id": "rumor1", "seed_count": 3}
        mock_npc_service.list_npcs.side_effect = Exception("Seeding error")
        
        response = client.post("/api/npc/systems/rumors/seed", json=seed_data)
        
        assert response.status_code == 500
        assert "Seeding error" in response.json()["detail"]
    
    def test_get_rumor_spread_network_success(self, client, mock_npc_service): pass
        """Test successful rumor network retrieval."""
        rumor_id = "rumor1"
        all_npcs = [{"npc_id": "npc1"}, {"npc_id": "npc2"}, {"npc_id": "npc3"}]
        mock_npc_service.list_npcs.return_value = all_npcs
        
        # Mock rumors for each NPC
        def get_rumors_side_effect(npc_id): pass
            if npc_id in ["npc1", "npc3"]: pass
                return [{"rumor_id": "rumor1", "content": "Test"}]
            return []
        
        mock_npc_service.get_npc_rumors.side_effect = get_rumors_side_effect
        
        response = client.get(f"/api/npc/systems/rumors/network/{rumor_id}")
        
        assert response.status_code == 200
        network = response.json()
        assert "npc1" in network
        assert "npc3" in network
        assert "npc2" not in network
    
    def test_get_rumor_spread_network_service_error(self, client, mock_npc_service): pass
        """Test rumor network when service raises error."""
        rumor_id = "rumor1"
        mock_npc_service.list_npcs.side_effect = Exception("Network error")
        
        response = client.get(f"/api/npc/systems/rumors/network/{rumor_id}")
        
        assert response.status_code == 500
        assert "Network error" in response.json()["detail"]
    
    def test_run_rumor_decay_success(self, client, mock_npc_service): pass
        """Test successful rumor decay."""
        decay_result = {"rumors_decayed": 5, "npcs_affected": 10}
        mock_npc_service.run_rumor_decay.return_value = decay_result
        
        response = client.post("/api/npc/systems/rumors/decay")
        
        assert response.status_code == 200
        assert response.json() == decay_result
        mock_npc_service.run_rumor_decay.assert_called_once()
    
    def test_run_rumor_decay_service_error(self, client, mock_npc_service): pass
        """Test rumor decay when service raises error."""
        mock_npc_service.run_rumor_decay.side_effect = Exception("Decay error")
        
        response = client.post("/api/npc/systems/rumors/decay")
        
        assert response.status_code == 500
        assert "Decay error" in response.json()["detail"]


class TestNPCSystemRouterPopulationEndpoints: pass
    """Test population-related endpoints."""
    
    def test_run_population_update_success(self, client, mock_npc_service): pass
        """Test successful population update."""
        update_result = {"npcs_created": 15, "npcs_removed": 3, "net_change": 12}
        mock_npc_service.run_monthly_population_update.return_value = update_result
        
        response = client.post("/api/npc/systems/population/update")
        
        assert response.status_code == 200
        assert response.json() == update_result
        mock_npc_service.run_monthly_population_update.assert_called_once()
    
    def test_run_population_update_service_error(self, client, mock_npc_service): pass
        """Test population update when service raises error."""
        mock_npc_service.run_monthly_population_update.side_effect = Exception("Update error")
        
        response = client.post("/api/npc/systems/population/update")
        
        assert response.status_code == 500
        assert "Update error" in response.json()["detail"]
    
    def test_get_population_metrics_success(self, client, mock_npc_service): pass
        """Test successful population metrics retrieval."""
        all_npcs = [
            {"npc_id": "npc1", "location": {"poi_id": "poi1"}},
            {"npc_id": "npc2", "location": {"poi_id": "poi1"}},
            {"npc_id": "npc3", "location": {"poi_id": "poi2"}},
            {"npc_id": "npc4", "location": {}}  # No poi_id
        ]
        mock_npc_service.list_npcs.return_value = all_npcs
        
        response = client.get("/api/npc/systems/population/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_npcs"] == 4
        assert data["poi_populations"]["poi1"] == 2
        assert data["poi_populations"]["poi2"] == 1
        assert data["poi_populations"]["unknown"] == 1
    
    def test_get_population_metrics_service_error(self, client, mock_npc_service): pass
        """Test population metrics when service raises error."""
        mock_npc_service.list_npcs.side_effect = Exception("Metrics error")
        
        response = client.get("/api/npc/systems/population/metrics")
        
        assert response.status_code == 500
        assert "Metrics error" in response.json()["detail"]
    
    def test_set_global_population_multiplier_success(self, client): pass
        """Test successful global population multiplier setting."""
        multiplier = 1.5
        
        response = client.post(f"/api/npc/systems/population/multiplier/{multiplier}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["multiplier"] == multiplier
        assert "Global population multiplier set to 1.5" in data["message"]
    
    def test_adjust_population_for_poi_success(self, client): pass
        """Test successful POI population adjustment."""
        poi_id = "poi_001"
        adjustment_data = {"target_population": 50, "adjustment": 10}
        
        response = client.post(
            f"/api/npc/systems/population/poi/{poi_id}",
            json=adjustment_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["poi_id"] == poi_id
        assert data["target_population"] == 50
        assert data["adjustment"] == 10
        assert f"Population adjustment for POI {poi_id}" in data["message"]


class TestNPCSystemRouterMotifEndpoints: pass
    """Test motif-related endpoints."""
    
    def test_get_npc_motifs_success(self, client, mock_npc_service, sample_npc_id): pass
        """Test successful motif retrieval."""
        motifs = {
            "npc_id": sample_npc_id,
            "core_motifs": ["heroic"],
            "motif_entropy": 0.5
        }
        mock_npc_service.get_npc_motifs.return_value = motifs
        
        response = client.get(f"/api/npc/systems/motifs/{sample_npc_id}")
        
        assert response.status_code == 200
        assert response.json() == motifs
        mock_npc_service.get_npc_motifs.assert_called_once_with(sample_npc_id)
    
    def test_get_npc_motifs_service_error(self, client, mock_npc_service, sample_npc_id): pass
        """Test motif retrieval when service raises error."""
        mock_npc_service.get_npc_motifs.side_effect = Exception("Motif error")
        
        response = client.get(f"/api/npc/systems/motifs/{sample_npc_id}")
        
        assert response.status_code == 500
        assert "Motif error" in response.json()["detail"]
    
    def test_apply_global_motifs_success(self, client, mock_npc_service): pass
        """Test successful global motif application."""
        result = {"motifs_applied": 25, "npcs_affected": 100}
        mock_npc_service.apply_global_motifs_to_all_npcs.return_value = result
        
        response = client.post("/api/npc/systems/motifs/apply/global")
        
        assert response.status_code == 200
        assert response.json() == result
        mock_npc_service.apply_global_motifs_to_all_npcs.assert_called_once()
    
    def test_apply_global_motifs_service_error(self, client, mock_npc_service): pass
        """Test global motif application when service raises error."""
        mock_npc_service.apply_global_motifs_to_all_npcs.side_effect = Exception("Global motif error")
        
        response = client.post("/api/npc/systems/motifs/apply/global")
        
        assert response.status_code == 500
        assert "Global motif error" in response.json()["detail"]
    
    def test_apply_regional_motifs_success(self, client): pass
        """Test successful regional motif application."""
        region_id = "region_001"
        
        response = client.post(f"/api/npc/systems/motifs/apply/regional/{region_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["region_id"] == region_id
        assert data["motifs_applied"] == 0  # Placeholder value
        assert f"Regional motifs applied to region {region_id}" in data["message"]
    
    def test_apply_motif_to_npc_success(self, client, mock_npc_service, sample_npc_id): pass
        """Test successful motif application to specific NPC."""
        motif_id = "heroic"
        result = {"success": True, "motif_applied": motif_id}
        mock_npc_service.apply_motif_to_npc.return_value = result
        
        response = client.post(f"/api/npc/systems/motifs/apply/npc/{sample_npc_id}/{motif_id}")
        
        assert response.status_code == 200
        assert response.json() == result
        mock_npc_service.apply_motif_to_npc.assert_called_once_with(sample_npc_id, motif_id)
    
    def test_apply_motif_to_npc_service_error(self, client, mock_npc_service, sample_npc_id): pass
        """Test motif application when service raises error."""
        motif_id = "heroic"
        mock_npc_service.apply_motif_to_npc.side_effect = Exception("Motif application error")
        
        response = client.post(f"/api/npc/systems/motifs/apply/npc/{sample_npc_id}/{motif_id}")
        
        assert response.status_code == 500
        assert "Motif application error" in response.json()["detail"]


class TestNPCSystemRouterErrorHandling: pass
    """Test error handling scenarios."""
    
    def test_invalid_json_payload(self, client, sample_npc_id): pass
        """Test handling of invalid JSON payload."""
        response = client.post(f"/api/npc/systems/memories/{sample_npc_id}", data="invalid json")
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_missing_required_fields_memory(self, client, sample_npc_id): pass
        """Test handling of missing required fields in memory creation."""
        incomplete_data = {"importance": 5}  # Missing content
        
        response = client.post(f"/api/npc/systems/memories/{sample_npc_id}", json=incomplete_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields_faction(self, client, sample_npc_id): pass
        """Test handling of missing required fields in faction adjustment."""
        incomplete_data = {"adjustment": 20}  # Missing faction_id
        
        response = client.post(f"/api/npc/systems/factions/{sample_npc_id}/adjust", json=incomplete_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_invalid_path_parameters(self, client): pass
        """Test handling of invalid path parameters."""
        # Test with empty NPC ID
        response = client.get("/api/npc/systems/memories/")
        
        assert response.status_code == 404  # Not found due to path mismatch 