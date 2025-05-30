from typing import Type
"""
Tests for backend.systems.world_state.api.endpoints

Comprehensive tests for the World State REST API endpoints.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from fastapi import FastAPI
import json

# Import the module being tested
try:
    from backend.systems.world_state.api.endpoints import router
    from backend.systems.world_state.api.endpoints import (
        StateVariableResponse,
        SetStateRequest,
        StateHistoryResponse,
        StateQueryResponse,
        StateSnapshotResponse,
        StateStatisticsResponse
    )
    from backend.systems.world_state.consolidated_state_models import (
        StateVariable,
        StateChangeRecord,
        StateChangeType,
        StateCategory,
        WorldRegion,
        WorldStateSnapshot
    )
except ImportError as e:
    pytest.skip(f"Could not import required modules: {e}", allow_module_level=True)


@pytest.fixture
def app():
    """Create a FastAPI app with the router for testing."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_state_variable():
    """Create a sample state variable for testing."""
    return StateVariable(
        key="test.variable",
        value="test_value",
        category=StateCategory.POLITICAL,
        region=WorldRegion.NORTHERN,
        tags=["test", "sample"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_history():
    """Create sample history records for testing."""
    return [
        StateChangeRecord(
            state_key="test.variable",
            old_value=None,
            new_value="initial_value",
            change_type=StateChangeType.CREATED,
            timestamp=datetime.utcnow(),
            change_reason="Initial creation",
            version=1
        ),
        StateChangeRecord(
            state_key="test.variable",
            old_value="initial_value",
            new_value="updated_value",
            change_type=StateChangeType.UPDATED,
            timestamp=datetime.utcnow(),
            change_reason="Updated value",
            version=2
        )
    ]


@pytest.fixture
def sample_snapshot():
    """Create a sample snapshot for testing."""
    return WorldStateSnapshot(
        version=1,
        timestamp=datetime.utcnow(),
        variables={"test.key": "test_value"},
        metadata={"purpose": "testing"}
    )


class TestGetAllVariables:
    """Test the GET /variables endpoint."""
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_all_variables')
    def test_get_all_variables_success(self, mock_get_all, client, sample_state_variable):
        """Test successful retrieval of all variables."""
        mock_get_all.return_value = {"test.variable": sample_state_variable}
        
        response = client.get("/api/world-state/variables")
        
        assert response.status_code == 200
        data = response.json()
        assert "test.variable" in data
        assert data["test.variable"]["key"] == "test.variable"
        assert data["test.variable"]["value"] == "test_value"
        assert data["test.variable"]["category"] == "POLITICAL"
        assert data["test.variable"]["region"] == "NORTHERN"
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_all_variables')
    def test_get_all_variables_empty(self, mock_get_all, client):
        """Test retrieval when no variables exist."""
        mock_get_all.return_value = {}
        
        response = client.get("/api/world-state/variables")
        
        assert response.status_code == 200
        assert response.json() == {}


class TestGetVariable:
    """Test the GET /variables/{key} endpoint."""
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_state_variable')
    def test_get_variable_success(self, mock_get_var, client, sample_state_variable):
        """Test successful retrieval of a specific variable."""
        mock_get_var.return_value = sample_state_variable
        
        response = client.get("/api/world-state/variables/test.variable")
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test.variable"
        assert data["value"] == "test_value"
        assert data["category"] == "POLITICAL"
        assert data["region"] == "NORTHERN"
        assert data["tags"] == ["test", "sample"]
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_state_variable')
    def test_get_variable_not_found(self, mock_get_var, client):
        """Test retrieval of non-existent variable."""
        mock_get_var.return_value = None
        
        response = client.get("/api/world-state/variables/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestSetVariable:
    """Test the POST /variables endpoint."""
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.set_state')
    def test_set_variable_success(self, mock_set_state, client, sample_state_variable):
        """Test successful setting of a variable."""
        mock_set_state.return_value = sample_state_variable
        
        request_data = {
            "key": "test.variable",
            "value": "test_value",
            "category": "POLITICAL",
            "region": "NORTHERN",
            "tags": ["test", "sample"]
        }
        
        response = client.post("/api/world-state/variables", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test.variable"
        assert data["value"] == "test_value"
        
        # Verify the API was called with correct parameters
        mock_set_state.assert_called_once_with(
            key="test.variable",
            value="test_value",
            category="POLITICAL",
            region="NORTHERN",
            tags=["test", "sample"],
            entity_id=None
        )
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.set_state')
    def test_set_variable_with_defaults(self, mock_set_state, client, sample_state_variable):
        """Test setting a variable with default values."""
        mock_set_state.return_value = sample_state_variable
        
        request_data = {
            "key": "test.variable",
            "value": "test_value"
        }
        
        response = client.post("/api/world-state/variables", json=request_data)
        
        assert response.status_code == 200
        
        # Verify defaults were used
        mock_set_state.assert_called_once_with(
            key="test.variable",
            value="test_value",
            category="OTHER",
            region="GLOBAL",
            tags=None,
            entity_id=None
        )
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.set_state')
    def test_set_variable_error(self, mock_set_state, client):
        """Test error handling when setting a variable fails."""
        mock_set_state.side_effect = ValueError("Invalid value")
        
        request_data = {
            "key": "test.variable",
            "value": "test_value"
        }
        
        response = client.post("/api/world-state/variables", json=request_data)
        
        assert response.status_code == 400
        assert "Invalid value" in response.json()["detail"]


class TestDeleteVariable:
    """Test the DELETE /variables/{key} endpoint."""
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.delete_state')
    def test_delete_variable_success(self, mock_delete, client):
        """Test successful deletion of a variable."""
        mock_delete.return_value = True
        
        response = client.delete("/api/world-state/variables/test.variable")
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_delete.assert_called_once_with("test.variable", None)
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.delete_state')
    def test_delete_variable_with_entity_id(self, mock_delete, client):
        """Test deletion with entity ID."""
        mock_delete.return_value = True
        
        response = client.delete("/api/world-state/variables/test.variable?entity_id=entity123")
        
        assert response.status_code == 200
        mock_delete.assert_called_once_with("test.variable", "entity123")
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.delete_state')
    def test_delete_variable_not_found(self, mock_delete, client):
        """Test deletion of non-existent variable."""
        mock_delete.return_value = False
        
        response = client.delete("/api/world-state/variables/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestGetVariableHistory:
    """Test the GET /variables/{key}/history endpoint."""
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_history')
    def test_get_history_success(self, mock_get_history, client, sample_history):
        """Test successful retrieval of variable history."""
        mock_get_history.return_value = sample_history
        
        response = client.get("/api/world-state/variables/test.variable/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test.variable"
        assert len(data["history"]) == 2
        assert data["history"][0]["change_type"] == "CREATED"
        assert data["history"][1]["change_type"] == "UPDATED"
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_history')
    def test_get_history_not_found(self, mock_get_history, client):
        """Test retrieval of history for non-existent variable."""
        mock_get_history.return_value = []
        
        response = client.get("/api/world-state/variables/nonexistent/history")
        
        assert response.status_code == 404
        assert "No history found" in response.json()["detail"]


class TestGetValueAtTime:
    """Test the GET /variables/{key}/at-time endpoint."""
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_value_at_time')
    def test_get_value_at_time_success(self, mock_get_value, client):
        """Test successful retrieval of value at specific time."""
        mock_get_value.return_value = "historical_value"
        timestamp = datetime.utcnow().isoformat()
        
        response = client.get(f"/api/world-state/variables/test.variable/at-time?timestamp={timestamp}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test.variable"
        assert data["value"] == "historical_value"
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_value_at_time')
    def test_get_value_at_time_not_found(self, mock_get_value, client):
        """Test retrieval when no value exists at specified time."""
        mock_get_value.return_value = None
        timestamp = datetime.utcnow().isoformat()
        
        response = client.get(f"/api/world-state/variables/test.variable/at-time?timestamp={timestamp}")
        
        assert response.status_code == 404


class TestGetValueAtVersion:
    """Test the GET /variables/{key}/at-version endpoint."""
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_value_at_version')
    def test_get_value_at_version_success(self, mock_get_value, client):
        """Test successful retrieval of value at specific version."""
        mock_get_value.return_value = "version_value"
        
        response = client.get("/api/world-state/variables/test.variable/at-version?version=1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test.variable"
        assert data["value"] == "version_value"
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_value_at_version')
    def test_get_value_at_version_not_found(self, mock_get_value, client):
        """Test retrieval when no value exists at specified version."""
        mock_get_value.return_value = None
        
        response = client.get("/api/world-state/variables/test.variable/at-version?version=999")
        
        assert response.status_code == 404


class TestQueryEndpoints:
    """Test the various query endpoints."""
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.query_by_category')
    def test_query_by_category(self, mock_query, client, sample_state_variable):
        """Test querying by category."""
        mock_query.return_value = {"test.variable": sample_state_variable}
        
        response = client.get("/api/world-state/query/category/POLITICAL")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert "test.variable" in data["results"]
        
        # Verify query was called with correct category
        mock_query.assert_called_once_with("POLITICAL")
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.query_by_region')
    def test_query_by_region(self, mock_query, client, sample_state_variable):
        """Test querying by region."""
        mock_query.return_value = {"test.variable": sample_state_variable}
        
        response = client.get("/api/world-state/query/region/NORTHERN")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        
        mock_query.assert_called_once_with("NORTHERN")
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.query_by_tags')
    def test_query_by_tags(self, mock_query, client, sample_state_variable):
        """Test querying by tags."""
        mock_query.return_value = {"test.variable": sample_state_variable}
        
        request_data = {
            "tags": ["test", "sample"],
            "match_any": False
        }
        
        response = client.post("/api/world-state/query/tags", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        
        mock_query.assert_called_once_with(["test", "sample"], False)
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.query_by_prefix')
    def test_query_by_prefix(self, mock_query, client, sample_state_variable):
        """Test querying by prefix."""
        mock_query.return_value = {"test.variable": sample_state_variable}
        
        response = client.get("/api/world-state/query/prefix/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        
        mock_query.assert_called_once_with("test")
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.query_by_category')
    def test_query_empty_results(self, mock_query, client):
        """Test query with no results."""
        mock_query.return_value = {}
        
        response = client.get("/api/world-state/query/category/NONEXISTENT")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == {}


class TestSnapshotEndpoints:
    """Test snapshot-related endpoints."""
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_snapshot')
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_manager')
    def test_get_snapshot_current(self, mock_get_manager, mock_get_snapshot, client, sample_snapshot):
        """Test getting current snapshot."""
        # Mock the snapshot data as a dictionary (what get_snapshot returns)
        snapshot_data = {
            "test.key": "test_value"
        }
        mock_get_snapshot.return_value = snapshot_data
        
        # Mock the manager to return the expected version
        mock_manager = Mock()
        mock_manager._next_version = 2  # So version will be 2 - 1 = 1
        mock_get_manager.return_value = mock_manager
        
        response = client.get("/api/world-state/snapshot")
        
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 1  # next_version - 1 = 2 - 1 = 1
        assert "variables" in data
        
        mock_get_snapshot.assert_called_once_with(None)
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_snapshot')
    def test_get_snapshot_at_time(self, mock_get_snapshot, client, sample_snapshot):
        """Test getting snapshot at specific time."""
        # Mock the snapshot data as a dictionary
        snapshot_data = {
            "version": sample_snapshot.version,
            "timestamp": sample_snapshot.timestamp.isoformat(),
            "variables": sample_snapshot.variables,
            "metadata": sample_snapshot.metadata
        }
        mock_get_snapshot.return_value = snapshot_data
        timestamp = datetime.utcnow().isoformat()
        
        response = client.get(f"/api/world-state/snapshot?timestamp={timestamp}")
        
        assert response.status_code == 200
        # Verify timestamp was parsed and passed correctly
        mock_get_snapshot.assert_called_once()
        # Check that the timestamp argument is a datetime object
        call_args = mock_get_snapshot.call_args[0]
        assert len(call_args) == 1
        assert isinstance(call_args[0], datetime)
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.create_snapshot')
    def test_create_snapshot(self, mock_create_snapshot, client, sample_snapshot):
        """Test creating a new snapshot."""
        mock_create_snapshot.return_value = sample_snapshot
        
        metadata = {"purpose": "test", "author": "test_user"}
        response = client.post("/api/world-state/snapshot", json=metadata)
        
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 1
        
        mock_create_snapshot.assert_called_once_with(metadata)


class TestStateManagementEndpoints:
    """Test state save/load endpoints."""
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.save_state')
    def test_save_state_success(self, mock_save, client):
        """Test successful state saving."""
        mock_save.return_value = True
        
        response = client.post("/api/world-state/save")
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_save.assert_called_once()
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.save_state')
    def test_save_state_failure(self, mock_save, client):
        """Test state saving failure."""
        mock_save.return_value = False
        
        response = client.post("/api/world-state/save")
        
        assert response.status_code == 200  # The endpoint returns 200 with success: false
        assert response.json()["success"] is False
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.load_state')
    def test_load_state_success(self, mock_load, client):
        """Test successful state loading."""
        mock_load.return_value = True
        
        response = client.post("/api/world-state/load")
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_load.assert_called_once()
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.load_state')
    def test_load_state_failure(self, mock_load, client):
        """Test state loading failure."""
        mock_load.return_value = False
        
        response = client.post("/api/world-state/load")
        
        assert response.status_code == 200  # The endpoint returns 200 with success: false
        assert response.json()["success"] is False


class TestStatisticsEndpoint:
    """Test the statistics endpoint."""
    
    @patch('backend.systems.world_state.api.endpoints.WorldStateAPI.get_statistics')
    def test_get_statistics(self, mock_get_stats, client):
        """Test getting system statistics."""
        mock_stats = {
            "total_variables": 100,
            "total_history_entries": 500,
            "next_version": 51,
            "categories": {"POLITICAL": 20, "ECONOMIC": 30},
            "regions": {"NORTHERN": 40, "SOUTHERN": 60},
            "last_updated": "2024-01-01T12:00:00"
        }
        mock_get_stats.return_value = mock_stats
        
        response = client.get("/api/world-state/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_variables"] == 100
        assert data["total_history_entries"] == 500
        assert data["categories"]["POLITICAL"] == 20
        assert data["regions"]["NORTHERN"] == 40
        
        mock_get_stats.assert_called_once()


class TestResponseModels:
    """Test the Pydantic response models."""
    
    def test_state_variable_response_model(self):
        """Test StateVariableResponse model."""
        data = {
            "key": "test.key",
            "value": "test_value",
            "category": "POLITICAL",
            "region": "NORTHERN",
            "tags": ["test"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        response = StateVariableResponse(**data)
        assert response.key == "test.key"
        assert response.value == "test_value"
        assert response.category == "POLITICAL"
    
    def test_set_state_request_model(self):
        """Test SetStateRequest model."""
        data = {
            "key": "test.key",
            "value": "test_value"
        }
        
        request = SetStateRequest(**data)
        assert request.key == "test.key"
        assert request.value == "test_value"
        assert request.category == "OTHER"  # Default
        assert request.region == "GLOBAL"   # Default
        assert request.tags is None         # Default
    
    def test_state_query_response_model(self):
        """Test StateQueryResponse model."""
        var_response = StateVariableResponse(
            key="test.key",
            value="test_value",
            category="POLITICAL",
            region="NORTHERN",
            tags=["test"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        query_response = StateQueryResponse(
            results={"test.key": var_response},
            count=1
        )
        
        assert query_response.count == 1
        assert "test.key" in query_response.results


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 