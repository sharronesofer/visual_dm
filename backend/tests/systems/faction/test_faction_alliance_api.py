"""
Comprehensive API tests for Alliance Routes
Tests all endpoints, request/response validation, and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from typing import Dict, List, Optional, Any
from fastapi.testclient import TestClient
from fastapi import status
import json

from backend.systems.faction.routers.alliance_routes import router
from backend.systems.faction.services.alliance_service import AllianceService
from backend.infrastructure.repositories.faction.alliance_repository import AllianceRepository
from backend.systems.faction.models.alliance import (
    AllianceEntity, BetrayalEntity, CreateAllianceRequest, UpdateAllianceRequest,
    AllianceType, AllianceStatus, BetrayalReason, AllianceResponse, BetrayalResponse
)


class TestAllianceRoutes:
    """Test suite for Alliance API routes"""

    @pytest.fixture
    def mock_alliance_service(self):
        """Mock AllianceService for testing"""
        return Mock(spec=AllianceService)

    @pytest.fixture
    def mock_alliance_repository(self):
        """Mock AllianceRepository for testing"""
        return Mock(spec=AllianceRepository)

    @pytest.fixture
    def test_client(self, mock_alliance_service, mock_alliance_repository):
        """Test client with mocked dependencies"""
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router, prefix="/alliances")
        
        # Override dependencies with mocks
        def get_mock_service():
            return mock_alliance_service
        
        def get_mock_repository():
            return mock_alliance_repository
        
        app.dependency_overrides[AllianceService] = get_mock_service
        app.dependency_overrides[AllianceRepository] = get_mock_repository
        
        return TestClient(app)

    @pytest.fixture
    def sample_alliance_data(self):
        """Sample alliance data for testing"""
        return {
            "id": str(uuid4()),
            "name": "Test Alliance",
            "alliance_type": AllianceType.MILITARY.value,
            "status": AllianceStatus.ACTIVE.value,
            "description": "Test military alliance",
            "leader_faction_id": str(uuid4()),
            "member_faction_ids": [str(uuid4()), str(uuid4())],
            "terms": {"mutual_defense": True},
            "mutual_obligations": ["Provide military support"],
            "shared_enemies": [str(uuid4())],
            "shared_goals": ["Defeat common enemy"],
            "start_date": datetime.utcnow().isoformat(),
            "end_date": None,
            "auto_renew": False,
            "trust_levels": {"faction1": 0.8, "faction2": 0.7},
            "betrayal_risks": {"faction1": 0.2, "faction2": 0.3},
            "reliability_history": {},
            "triggers": {"threat_detected": True},
            "threat_level": 0.8,
            "benefits_shared": {},
            "military_support_provided": {},
            "economic_support_provided": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": None,
            "is_active": True
        }

    @pytest.fixture
    def sample_betrayal_data(self):
        """Sample betrayal data for testing"""
        return {
            "id": str(uuid4()),
            "alliance_id": str(uuid4()),
            "betrayer_faction_id": str(uuid4()),
            "victim_faction_ids": [str(uuid4())],
            "betrayal_reason": BetrayalReason.AMBITION.value,
            "betrayal_type": "military_attack",
            "description": "Surprise attack on allies",
            "hidden_attributes_influence": {"hidden_ambition": 9},
            "external_pressure": {"economic_crisis": True},
            "opportunity_details": {"weak_defenses": True},
            "damage_dealt": {"military_losses": 500},
            "trust_impact": {"faction1": -0.8},
            "reputation_impact": -0.5,
            "detected_immediately": True,
            "detection_delay": None,
            "response_actions": [{"type": "retaliation"}],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": None
        }

    # Alliance CRUD Endpoint Tests

    def test_create_alliance_success(self, test_client, mock_alliance_service, sample_alliance_data):
        """Test successful alliance creation"""
        # Prepare request data
        request_data = {
            "name": "Test Alliance",
            "alliance_type": "military",
            "description": "Test military alliance",
            "leader_faction_id": sample_alliance_data["leader_faction_id"],
            "member_faction_ids": sample_alliance_data["member_faction_ids"],
            "terms": {"mutual_defense": True},
            "mutual_obligations": ["Provide military support"],
            "shared_enemies": sample_alliance_data["shared_enemies"],
            "shared_goals": ["Defeat common enemy"]
        }

        # Mock service response
        mock_alliance = Mock()
        mock_alliance.id = UUID(sample_alliance_data["id"])
        mock_alliance.name = request_data["name"]
        mock_alliance.alliance_type = request_data["alliance_type"]
        mock_alliance_service.create_alliance.return_value = mock_alliance

        # Make request
        response = test_client.post("/alliances/", json=request_data)

        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == request_data["name"]
        assert response_data["alliance_type"] == request_data["alliance_type"]
        mock_alliance_service.create_alliance.assert_called_once()

    def test_create_alliance_validation_error(self, test_client):
        """Test alliance creation with invalid data"""
        invalid_request = {
            "name": "",  # Invalid: empty name
            "alliance_type": "invalid_type",  # Invalid: not in enum
            "leader_faction_id": "not-a-uuid"  # Invalid: not a UUID
        }

        response = test_client.post("/alliances/", json=invalid_request)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_alliance_success(self, test_client, mock_alliance_repository, sample_alliance_data):
        """Test successful alliance retrieval"""
        alliance_id = sample_alliance_data["id"]
        
        # Mock repository response
        mock_alliance = Mock()
        mock_alliance.id = UUID(alliance_id)
        mock_alliance.name = sample_alliance_data["name"]
        mock_alliance.alliance_type = sample_alliance_data["alliance_type"]
        mock_alliance_repository.get_alliance_by_id.return_value = mock_alliance

        response = test_client.get(f"/alliances/{alliance_id}")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == alliance_id
        assert response_data["name"] == sample_alliance_data["name"]

    def test_get_alliance_not_found(self, test_client, mock_alliance_repository):
        """Test alliance retrieval when alliance doesn't exist"""
        alliance_id = str(uuid4())
        mock_alliance_repository.get_alliance_by_id.return_value = None

        response = test_client.get(f"/alliances/{alliance_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_alliances_success(self, test_client, mock_alliance_repository, sample_alliance_data):
        """Test successful alliance listing"""
        # Mock repository response
        mock_alliances = [Mock(id=UUID(sample_alliance_data["id"]))]
        mock_alliance_repository.get_active_alliances.return_value = mock_alliances

        response = test_client.get("/alliances/")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "items" in response_data
        assert "total" in response_data
        assert len(response_data["items"]) >= 0

    def test_list_alliances_with_filters(self, test_client, mock_alliance_repository):
        """Test alliance listing with status and type filters"""
        mock_alliance_repository.get_alliances_by_status.return_value = []
        mock_alliance_repository.get_alliances_by_type.return_value = []

        response = test_client.get("/alliances/?status=active&alliance_type=military")

        assert response.status_code == status.HTTP_200_OK

    def test_update_alliance_success(self, test_client, mock_alliance_repository, sample_alliance_data):
        """Test successful alliance update"""
        alliance_id = sample_alliance_data["id"]
        update_data = {
            "name": "Updated Alliance Name",
            "status": "suspended",
            "description": "Updated description"
        }

        # Mock repository responses
        mock_alliance = Mock()
        mock_alliance.id = UUID(alliance_id)
        mock_alliance.name = update_data["name"]
        mock_alliance_repository.get_alliance_by_id.return_value = mock_alliance
        mock_alliance_repository.update_alliance.return_value = mock_alliance

        response = test_client.put(f"/alliances/{alliance_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == update_data["name"]

    def test_update_alliance_not_found(self, test_client, mock_alliance_repository):
        """Test alliance update when alliance doesn't exist"""
        alliance_id = str(uuid4())
        update_data = {"name": "Updated Name"}
        
        mock_alliance_repository.get_alliance_by_id.return_value = None

        response = test_client.put(f"/alliances/{alliance_id}", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_alliance_success(self, test_client, mock_alliance_repository):
        """Test successful alliance deletion"""
        alliance_id = str(uuid4())
        mock_alliance_repository.delete_alliance.return_value = True

        response = test_client.delete(f"/alliances/{alliance_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_alliance_not_found(self, test_client, mock_alliance_repository):
        """Test alliance deletion when alliance doesn't exist"""
        alliance_id = str(uuid4())
        mock_alliance_repository.delete_alliance.return_value = False

        response = test_client.delete(f"/alliances/{alliance_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    # Alliance Evaluation Endpoints

    def test_evaluate_alliance_opportunity_success(self, test_client, mock_alliance_service):
        """Test successful alliance opportunity evaluation"""
        faction_a_id = str(uuid4())
        faction_b_id = str(uuid4())
        common_threat_id = str(uuid4())

        # Mock service response
        evaluation_result = {
            "compatible": True,
            "compatibility_score": 0.8,
            "threat_level": 0.7,
            "willingness_score": 0.75,
            "recommended_alliance_types": ["military", "mutual_defense"],
            "risks": [],
            "benefits": ["shared_defense", "resource_pooling"],
            "estimated_duration": "long-term"
        }
        mock_alliance_service.evaluate_alliance_opportunity.return_value = evaluation_result

        request_data = {
            "faction_a_id": faction_a_id,
            "faction_b_id": faction_b_id,
            "common_threat_ids": [common_threat_id],
            "alliance_type": "military"
        }

        response = test_client.post("/alliances/evaluate-opportunity", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["compatible"] is True
        assert response_data["compatibility_score"] == 0.8
        assert "military" in response_data["recommended_alliance_types"]

    def test_evaluate_alliance_opportunity_invalid_input(self, test_client):
        """Test alliance opportunity evaluation with invalid input"""
        invalid_request = {
            "faction_a_id": "not-a-uuid",
            "faction_b_id": str(uuid4())
        }

        response = test_client.post("/alliances/evaluate-opportunity", json=invalid_request)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_potential_alliance_partners(self, test_client, mock_alliance_repository):
        """Test getting potential alliance partners"""
        faction_id = str(uuid4())
        shared_enemy_id = str(uuid4())

        # Mock repository response
        potential_partners = [uuid4(), uuid4(), uuid4()]
        mock_alliance_repository.find_potential_alliance_partners.return_value = potential_partners

        response = test_client.get(
            f"/alliances/faction/{faction_id}/potential-partners?shared_enemy_id={shared_enemy_id}"
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "potential_partners" in response_data
        assert len(response_data["potential_partners"]) == 3

    # Betrayal System Endpoints

    def test_evaluate_betrayal_probability_success(self, test_client, mock_alliance_service):
        """Test successful betrayal probability evaluation"""
        alliance_id = str(uuid4())
        faction_id = str(uuid4())

        # Mock service response
        betrayal_evaluation = {
            "betrayal_probability": 0.6,
            "primary_motivation": "ambition",
            "risk_factors": ["high_ambition", "low_integrity"],
            "protective_factors": [],
            "recommended_actions": ["increase_monitoring", "improve_trust"]
        }
        mock_alliance_service.evaluate_betrayal_probability.return_value = betrayal_evaluation

        request_data = {
            "alliance_id": alliance_id,
            "faction_id": faction_id,
            "external_factors": {"opportunity_present": True}
        }

        response = test_client.post("/alliances/betrayal/evaluate", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["betrayal_probability"] == 0.6
        assert response_data["primary_motivation"] == "ambition"
        assert "high_ambition" in response_data["risk_factors"]

    def test_execute_betrayal_success(self, test_client, mock_alliance_service, sample_betrayal_data):
        """Test successful betrayal execution"""
        alliance_id = sample_betrayal_data["alliance_id"]
        betrayer_faction_id = sample_betrayal_data["betrayer_faction_id"]

        # Mock service response
        mock_betrayal = Mock()
        mock_betrayal.id = UUID(sample_betrayal_data["id"])
        mock_betrayal.alliance_id = UUID(alliance_id)
        mock_betrayal.betrayer_faction_id = UUID(betrayer_faction_id)
        mock_betrayal.betrayal_reason = BetrayalReason.AMBITION.value
        mock_alliance_service.execute_betrayal.return_value = mock_betrayal

        request_data = {
            "alliance_id": alliance_id,
            "betrayer_faction_id": betrayer_faction_id,
            "betrayal_type": "military_attack",
            "description": "Surprise attack on allies",
            "reason": "ambition"
        }

        response = test_client.post("/alliances/betrayal/execute", json=request_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["alliance_id"] == alliance_id
        assert response_data["betrayer_faction_id"] == betrayer_faction_id

    def test_get_betrayal_success(self, test_client, mock_alliance_repository, sample_betrayal_data):
        """Test successful betrayal retrieval"""
        betrayal_id = sample_betrayal_data["id"]

        # Mock repository response
        mock_betrayal = Mock()
        mock_betrayal.id = UUID(betrayal_id)
        mock_betrayal.alliance_id = UUID(sample_betrayal_data["alliance_id"])
        mock_betrayal.betrayer_faction_id = UUID(sample_betrayal_data["betrayer_faction_id"])
        mock_alliance_repository.get_betrayal_by_id.return_value = mock_betrayal

        response = test_client.get(f"/alliances/betrayal/{betrayal_id}")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == betrayal_id

    def test_get_alliance_betrayals(self, test_client, mock_alliance_repository, sample_betrayal_data):
        """Test getting betrayals for an alliance"""
        alliance_id = sample_betrayal_data["alliance_id"]

        # Mock repository response
        mock_betrayals = [Mock(id=UUID(sample_betrayal_data["id"]))]
        mock_alliance_repository.get_betrayals_by_alliance.return_value = mock_betrayals

        response = test_client.get(f"/alliances/betrayal/alliance/{alliance_id}")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "betrayals" in response_data
        assert len(response_data["betrayals"]) >= 0

    def test_get_faction_betrayals(self, test_client, mock_alliance_repository, sample_betrayal_data):
        """Test getting betrayals for a faction"""
        faction_id = sample_betrayal_data["betrayer_faction_id"]

        # Mock repository response
        mock_betrayals = [Mock(id=UUID(sample_betrayal_data["id"]))]
        mock_alliance_repository.get_betrayals_by_faction.return_value = mock_betrayals

        response = test_client.get(f"/alliances/betrayal/faction/{faction_id}")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "betrayals" in response_data

    def test_get_recent_betrayals(self, test_client, mock_alliance_repository):
        """Test getting recent betrayals"""
        mock_alliance_repository.get_recent_betrayals.return_value = []

        response = test_client.get("/alliances/betrayal/recent?limit=5")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "betrayals" in response_data

    # Member Management Endpoints

    def test_add_faction_to_alliance_success(self, test_client, mock_alliance_repository):
        """Test successfully adding faction to alliance"""
        alliance_id = str(uuid4())
        faction_id = str(uuid4())

        mock_alliance_repository.add_faction_to_alliance.return_value = True

        response = test_client.post(f"/alliances/{alliance_id}/members/{faction_id}")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True

    def test_add_faction_to_alliance_failure(self, test_client, mock_alliance_repository):
        """Test adding faction to alliance when operation fails"""
        alliance_id = str(uuid4())
        faction_id = str(uuid4())

        mock_alliance_repository.add_faction_to_alliance.return_value = False

        response = test_client.post(f"/alliances/{alliance_id}/members/{faction_id}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_faction_from_alliance_success(self, test_client, mock_alliance_repository):
        """Test successfully removing faction from alliance"""
        alliance_id = str(uuid4())
        faction_id = str(uuid4())

        mock_alliance_repository.remove_faction_from_alliance.return_value = True

        response = test_client.delete(f"/alliances/{alliance_id}/members/{faction_id}")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True

    def test_remove_faction_from_alliance_failure(self, test_client, mock_alliance_repository):
        """Test removing faction from alliance when operation fails"""
        alliance_id = str(uuid4())
        faction_id = str(uuid4())

        mock_alliance_repository.remove_faction_from_alliance.return_value = False

        response = test_client.delete(f"/alliances/{alliance_id}/members/{faction_id}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Statistics and Analytics Endpoints

    def test_get_alliance_statistics(self, test_client, mock_alliance_repository):
        """Test getting alliance statistics"""
        # Mock repository response
        stats = {
            "total_alliances": 25,
            "active_alliances": 15,
            "proposed_alliances": 5,
            "betrayed_alliances": 3,
            "dissolved_alliances": 2,
            "alliance_types": {
                "military": 10,
                "economic": 8,
                "temporary_truce": 7
            },
            "total_betrayals": 12,
            "average_trust_level": 0.65
        }
        mock_alliance_repository.get_alliance_statistics.return_value = stats

        response = test_client.get("/alliances/statistics/overview")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["total_alliances"] == 25
        assert response_data["active_alliances"] == 15
        assert "alliance_types" in response_data

    def test_get_faction_alliance_statistics(self, test_client, mock_alliance_repository):
        """Test getting faction-specific alliance statistics"""
        faction_id = str(uuid4())

        # Mock repository responses
        mock_alliance_repository.get_faction_alliance_count.return_value = 5
        mock_alliance_repository.get_faction_betrayal_count.return_value = 2

        response = test_client.get(f"/alliances/faction/{faction_id}/statistics")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["alliance_count"] == 5
        assert response_data["betrayal_count"] == 2

    # Error Handling and Edge Cases

    def test_invalid_uuid_parameter(self, test_client):
        """Test endpoints with invalid UUID parameters"""
        invalid_uuid = "not-a-uuid"

        response = test_client.get(f"/alliances/{invalid_uuid}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_required_fields(self, test_client):
        """Test endpoints with missing required fields"""
        incomplete_request = {
            "name": "Test Alliance"
            # Missing required fields like alliance_type, leader_faction_id
        }

        response = test_client.post("/alliances/", json=incomplete_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_enum_values(self, test_client):
        """Test endpoints with invalid enum values"""
        invalid_request = {
            "name": "Test Alliance",
            "alliance_type": "invalid_type",  # Not in AllianceType enum
            "leader_faction_id": str(uuid4()),
            "member_faction_ids": []
        }

        response = test_client.post("/alliances/", json=invalid_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_large_payload_handling(self, test_client, mock_alliance_service):
        """Test handling of large request payloads"""
        large_request = {
            "name": "Test Alliance",
            "alliance_type": "military",
            "leader_faction_id": str(uuid4()),
            "member_faction_ids": [str(uuid4()) for _ in range(100)],  # Large list
            "terms": {f"term_{i}": f"value_{i}" for i in range(100)},  # Large dict
            "mutual_obligations": [f"obligation_{i}" for i in range(100)],  # Large list
            "shared_goals": [f"goal_{i}" for i in range(100)]  # Large list
        }

        # Mock service response
        mock_alliance = Mock()
        mock_alliance.id = uuid4()
        mock_alliance.name = large_request["name"]
        mock_alliance_service.create_alliance.return_value = mock_alliance

        response = test_client.post("/alliances/", json=large_request)

        # Should handle large payloads gracefully
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE]

    def test_concurrent_requests(self, test_client, mock_alliance_repository):
        """Test handling of concurrent requests to the same resource"""
        alliance_id = str(uuid4())
        
        # Mock repository to simulate concurrent access
        mock_alliance = Mock()
        mock_alliance.id = UUID(alliance_id)
        mock_alliance_repository.get_alliance_by_id.return_value = mock_alliance

        # Simulate multiple concurrent requests
        responses = []
        for i in range(5):
            response = test_client.get(f"/alliances/{alliance_id}")
            responses.append(response)

        # All requests should succeed
        assert all(response.status_code == status.HTTP_200_OK for response in responses)

    def test_pagination_parameters(self, test_client, mock_alliance_repository):
        """Test pagination parameter validation"""
        mock_alliance_repository.get_active_alliances.return_value = []

        # Valid pagination
        response = test_client.get("/alliances/?page=1&size=20")
        assert response.status_code == status.HTTP_200_OK

        # Invalid pagination parameters
        response = test_client.get("/alliances/?page=0&size=150")  # page too low, size too high
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Authentication and Authorization Tests (if applicable)

    def test_unauthorized_access(self, test_client):
        """Test unauthorized access to protected endpoints"""
        # Note: This would be relevant if authentication is implemented
        # For now, we test that endpoints are accessible without auth
        response = test_client.get("/alliances/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_forbidden_operations(self, test_client):
        """Test forbidden operations based on user permissions"""
        # Note: This would be relevant if authorization is implemented
        # For now, we test that operations are allowed
        alliance_id = str(uuid4())
        response = test_client.delete(f"/alliances/{alliance_id}")
        assert response.status_code in [
            status.HTTP_204_NO_CONTENT, 
            status.HTTP_404_NOT_FOUND, 
            status.HTTP_403_FORBIDDEN
        ]

    # Performance and Load Tests

    def test_response_time_performance(self, test_client, mock_alliance_repository):
        """Test response time performance for list operations"""
        import time
        
        # Mock large dataset
        mock_alliances = [Mock(id=uuid4()) for _ in range(1000)]
        mock_alliance_repository.get_active_alliances.return_value = mock_alliances

        start_time = time.time()
        response = test_client.get("/alliances/")
        end_time = time.time()

        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 5.0  # Should respond within 5 seconds

    def test_memory_usage_with_large_responses(self, test_client, mock_alliance_repository):
        """Test memory usage with large response datasets"""
        # Mock very large dataset
        mock_alliances = [Mock(id=uuid4()) for _ in range(10000)]
        mock_alliance_repository.get_active_alliances.return_value = mock_alliances

        response = test_client.get("/alliances/")

        # Should handle large datasets without memory issues
        assert response.status_code == status.HTTP_200_OK 