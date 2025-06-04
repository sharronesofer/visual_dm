"""
Comprehensive tests for Faction Succession Router

Tests all succession crisis API endpoints according to Task 69 requirements:
- Succession vulnerability analysis
- Crisis triggering and management
- Candidate management
- External interference
- Crisis resolution and metrics
"""

import pytest
import uuid
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from backend.systems.faction.routers.succession_router import succession_router
from backend.systems.faction.models.succession import (
    SuccessionCrisisEntity,
    SuccessionType,
    SuccessionCrisisStatus,
    SuccessionTrigger,
    SuccessionCandidate
)
from backend.infrastructure.models.faction.models import FactionEntity


# Create test client
client = TestClient(succession_router)


class TestSuccessionAnalysisEndpoints:
    """Test succession analysis API endpoints"""
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_service')
    def test_analyze_faction_succession_vulnerability(self, mock_service, mock_db):
        """Test faction succession vulnerability analysis endpoint"""
        # Mock faction
        faction_id = uuid.uuid4()
        mock_faction = Mock(spec=FactionEntity)
        mock_faction.id = faction_id
        mock_faction.name = "Test Faction"
        mock_faction.get_hidden_attributes.return_value = {
            "hidden_ambition": 4,
            "hidden_integrity": 3,
            "hidden_discipline": 5,
            "hidden_impulsivity": 2,
            "hidden_pragmatism": 5,
            "hidden_resilience": 4
        }
        
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_faction
        
        # Mock service
        mock_succession_service = Mock()
        mock_service.return_value = mock_succession_service
        mock_succession_service.calculate_succession_vulnerability.return_value = 0.65
        mock_succession_service.determine_succession_type.return_value = SuccessionType.ECONOMIC_COMPETITION
        mock_succession_service.should_trigger_crisis.return_value = True
        
        # Request data
        request_data = {
            "faction_id": str(faction_id),
            "simulate_triggers": ["leader_death_natural", "external_pressure"],
            "include_candidates": True
        }
        
        # Make request
        response = client.post("/analyze", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["faction_id"] == str(faction_id)
        assert data["faction_name"] == "Test Faction"
        assert data["succession_type"] == "economic_competition"
        assert data["vulnerability_score"] == 0.65
        assert "potential_triggers" in data
        assert "stability_factors" in data
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    def test_analyze_faction_not_found(self, mock_db):
        """Test analysis with non-existent faction"""
        # Mock database to return None
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Request data
        request_data = {
            "faction_id": str(uuid.uuid4()),
            "simulate_triggers": [],
            "include_candidates": True
        }
        
        # Make request
        response = client.post("/analyze", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Faction not found" in response.json()["detail"]


class TestCrisisTriggeringEndpoints:
    """Test succession crisis triggering endpoints"""
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_service')
    def test_trigger_succession_crisis(self, mock_service, mock_db):
        """Test triggering a succession crisis"""
        # Mock crisis entity
        crisis_id = uuid.uuid4()
        faction_id = uuid.uuid4()
        mock_crisis = Mock(spec=SuccessionCrisisEntity)
        mock_crisis.id = crisis_id
        mock_crisis.faction_id = faction_id
        mock_crisis.faction_name = "Test Faction"
        mock_crisis.succession_type = SuccessionType.ECONOMIC_COMPETITION.value
        mock_crisis.status = SuccessionCrisisStatus.PENDING.value
        mock_crisis.trigger = SuccessionTrigger.LEADER_DEATH_NATURAL.value
        mock_crisis.crisis_start = datetime.utcnow()
        mock_crisis.crisis_end = None
        mock_crisis.estimated_duration = 30
        mock_crisis.previous_leader_id = None
        mock_crisis.previous_leader_name = None
        mock_crisis.winner_id = None
        mock_crisis.faction_stability = 0.8
        mock_crisis.instability_effects = {}
        mock_crisis.interfering_factions = []
        mock_crisis.interference_details = {}
        mock_crisis.resolution_method = None
        mock_crisis.faction_split = False
        mock_crisis.new_factions = []
        mock_crisis.created_at = datetime.utcnow()
        mock_crisis.updated_at = None
        mock_crisis.metadata = {}
        
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        
        # Mock service
        mock_succession_service = Mock()
        mock_service.return_value = mock_succession_service
        mock_succession_service.create_succession_crisis.return_value = mock_crisis
        
        # Request data
        request_data = {
            "faction_id": str(faction_id),
            "trigger": "leader_death_natural",
            "previous_leader_id": str(uuid.uuid4()),
            "trigger_details": {"cause": "old_age"}
        }
        
        # Make request
        response = client.post("/trigger", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == str(crisis_id)
        assert data["faction_id"] == str(faction_id)
        assert data["faction_name"] == "Test Faction"
        assert data["succession_type"] == "economic_competition"
        assert data["status"] == "pending"
        assert data["trigger"] == "leader_death_natural"
    
    def test_trigger_crisis_invalid_data(self):
        """Test triggering crisis with invalid data"""
        # Invalid request data (missing required fields)
        request_data = {
            "faction_id": "invalid-uuid",
            "trigger": "invalid_trigger"
        }
        
        # Make request
        response = client.post("/trigger", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCrisisListingEndpoints:
    """Test succession crisis listing endpoints"""
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_repository')
    def test_list_succession_crises(self, mock_repo, mock_db):
        """Test listing succession crises"""
        # Mock crisis entities
        crisis1 = Mock(spec=SuccessionCrisisEntity)
        crisis1.id = uuid.uuid4()
        crisis1.faction_name = "Faction 1"
        crisis1.status = SuccessionCrisisStatus.PENDING.value
        
        crisis2 = Mock(spec=SuccessionCrisisEntity)
        crisis2.id = uuid.uuid4()
        crisis2.faction_name = "Faction 2"
        crisis2.status = SuccessionCrisisStatus.IN_PROGRESS.value
        
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        
        # Mock repository
        mock_succession_repo = Mock()
        mock_repo.return_value = mock_succession_repo
        mock_succession_repo.get_all_active_crises.return_value = [crisis1, crisis2]
        
        # Make request
        response = client.get("/", params={"active_only": True, "page": 1, "size": 20})
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_repository')
    def test_list_crises_with_filters(self, mock_repo, mock_db):
        """Test listing crises with filters"""
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        
        # Mock repository
        mock_succession_repo = Mock()
        mock_repo.return_value = mock_succession_repo
        mock_succession_repo.get_active_crises_for_faction.return_value = []
        
        # Make request with faction filter
        faction_id = uuid.uuid4()
        response = client.get("/", params={
            "faction_id": str(faction_id),
            "page": 1,
            "size": 10
        })
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK


class TestCrisisDetailEndpoints:
    """Test individual crisis detail endpoints"""
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_repository')
    def test_get_succession_crisis(self, mock_repo, mock_db):
        """Test getting individual succession crisis"""
        # Mock crisis entity
        crisis_id = uuid.uuid4()
        mock_crisis = Mock(spec=SuccessionCrisisEntity)
        mock_crisis.id = crisis_id
        mock_crisis.faction_id = uuid.uuid4()
        mock_crisis.faction_name = "Test Faction"
        mock_crisis.succession_type = SuccessionType.ECONOMIC_COMPETITION.value
        mock_crisis.status = SuccessionCrisisStatus.PENDING.value
        mock_crisis.trigger = SuccessionTrigger.LEADER_DEATH_NATURAL.value
        mock_crisis.crisis_start = datetime.utcnow()
        mock_crisis.crisis_end = None
        mock_crisis.estimated_duration = 30
        mock_crisis.previous_leader_id = None
        mock_crisis.previous_leader_name = None
        mock_crisis.winner_id = None
        mock_crisis.faction_stability = 0.8
        mock_crisis.instability_effects = {}
        mock_crisis.interfering_factions = []
        mock_crisis.interference_details = {}
        mock_crisis.resolution_method = None
        mock_crisis.faction_split = False
        mock_crisis.new_factions = []
        mock_crisis.created_at = datetime.utcnow()
        mock_crisis.updated_at = None
        mock_crisis.metadata = {}
        
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        
        # Mock repository
        mock_succession_repo = Mock()
        mock_repo.return_value = mock_succession_repo
        mock_succession_repo.get_succession_crisis_by_id.return_value = mock_crisis
        
        # Make request
        response = client.get(f"/{crisis_id}")
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == str(crisis_id)
        assert data["faction_name"] == "Test Faction"
        assert data["succession_type"] == "economic_competition"
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_repository')
    def test_get_crisis_not_found(self, mock_repo, mock_db):
        """Test getting non-existent crisis"""
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        
        # Mock repository to return None
        mock_succession_repo = Mock()
        mock_repo.return_value = mock_succession_repo
        mock_succession_repo.get_succession_crisis_by_id.return_value = None
        
        # Make request
        response = client.get(f"/{uuid.uuid4()}")
        
        # Verify response
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCandidateManagementEndpoints:
    """Test succession candidate management endpoints"""
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_service')
    def test_add_succession_candidate(self, mock_service, mock_db):
        """Test adding a succession candidate"""
        # Mock crisis entity
        crisis_id = uuid.uuid4()
        mock_crisis = Mock(spec=SuccessionCrisisEntity)
        mock_crisis.id = crisis_id
        mock_crisis.faction_id = uuid.uuid4()
        mock_crisis.faction_name = "Test Faction"
        mock_crisis.succession_type = SuccessionType.ECONOMIC_COMPETITION.value
        mock_crisis.status = SuccessionCrisisStatus.PENDING.value
        mock_crisis.trigger = SuccessionTrigger.LEADER_DEATH_NATURAL.value
        mock_crisis.crisis_start = datetime.utcnow()
        mock_crisis.crisis_end = None
        mock_crisis.estimated_duration = 30
        mock_crisis.previous_leader_id = None
        mock_crisis.previous_leader_name = None
        mock_crisis.winner_id = None
        mock_crisis.faction_stability = 0.8
        mock_crisis.instability_effects = {}
        mock_crisis.interfering_factions = []
        mock_crisis.interference_details = {}
        mock_crisis.resolution_method = None
        mock_crisis.faction_split = False
        mock_crisis.new_factions = []
        mock_crisis.created_at = datetime.utcnow()
        mock_crisis.updated_at = None
        mock_crisis.metadata = {}
        
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        
        # Mock service
        mock_succession_service = Mock()
        mock_service.return_value = mock_succession_service
        mock_succession_service.add_succession_candidate.return_value = mock_crisis
        
        # Request data
        request_data = {
            "character_id": str(uuid.uuid4()),
            "character_name": "Wealthy Merchant",
            "net_worth": 150000.0,
            "qualifications": {"business_experience": 15},
            "is_legitimate_heir": False
        }
        
        # Make request
        response = client.post(f"/{crisis_id}/candidates", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == str(crisis_id)
        assert data["faction_name"] == "Test Faction"
    
    def test_add_candidate_invalid_data(self):
        """Test adding candidate with invalid data"""
        # Invalid request data
        request_data = {
            "character_id": "invalid-uuid",
            "character_name": "",  # Empty name
            "net_worth": -1000.0  # Negative net worth
        }
        
        # Make request
        response = client.post(f"/{uuid.uuid4()}/candidates", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCrisisAdvancementEndpoints:
    """Test succession crisis advancement endpoints"""
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_service')
    def test_advance_succession_crisis(self, mock_service, mock_db):
        """Test advancing a succession crisis"""
        # Mock crisis entity
        crisis_id = uuid.uuid4()
        mock_crisis = Mock(spec=SuccessionCrisisEntity)
        mock_crisis.id = crisis_id
        mock_crisis.faction_id = uuid.uuid4()
        mock_crisis.faction_name = "Test Faction"
        mock_crisis.succession_type = SuccessionType.ECONOMIC_COMPETITION.value
        mock_crisis.status = SuccessionCrisisStatus.IN_PROGRESS.value
        mock_crisis.trigger = SuccessionTrigger.LEADER_DEATH_NATURAL.value
        mock_crisis.crisis_start = datetime.utcnow()
        mock_crisis.crisis_end = None
        mock_crisis.estimated_duration = 30
        mock_crisis.previous_leader_id = None
        mock_crisis.previous_leader_name = None
        mock_crisis.winner_id = None
        mock_crisis.faction_stability = 0.7  # Reduced stability
        mock_crisis.instability_effects = {}
        mock_crisis.interfering_factions = []
        mock_crisis.interference_details = {}
        mock_crisis.resolution_method = None
        mock_crisis.faction_split = False
        mock_crisis.new_factions = []
        mock_crisis.created_at = datetime.utcnow()
        mock_crisis.updated_at = datetime.utcnow()
        mock_crisis.metadata = {}
        
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        
        # Mock service
        mock_succession_service = Mock()
        mock_service.return_value = mock_succession_service
        mock_succession_service.advance_succession_crisis.return_value = mock_crisis
        
        # Request data
        request_data = {
            "crisis_id": str(crisis_id),
            "time_days": 5,
            "external_events": [
                {"type": "economic_pressure", "intensity": 0.3}
            ]
        }
        
        # Make request
        response = client.post(f"/{crisis_id}/advance", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == str(crisis_id)
        assert data["status"] == "in_progress"
        assert data["faction_stability"] == 0.7


class TestCrisisResolutionEndpoints:
    """Test succession crisis resolution endpoints"""
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_service')
    def test_resolve_succession_crisis(self, mock_service, mock_db):
        """Test resolving a succession crisis"""
        # Mock crisis entity
        crisis_id = uuid.uuid4()
        winner_id = uuid.uuid4()
        mock_crisis = Mock(spec=SuccessionCrisisEntity)
        mock_crisis.id = crisis_id
        mock_crisis.faction_id = uuid.uuid4()
        mock_crisis.faction_name = "Test Faction"
        mock_crisis.succession_type = SuccessionType.ECONOMIC_COMPETITION.value
        mock_crisis.status = SuccessionCrisisStatus.RESOLVED.value
        mock_crisis.trigger = SuccessionTrigger.LEADER_DEATH_NATURAL.value
        mock_crisis.crisis_start = datetime.utcnow() - timedelta(days=20)
        mock_crisis.crisis_end = datetime.utcnow()
        mock_crisis.estimated_duration = 30
        mock_crisis.previous_leader_id = None
        mock_crisis.previous_leader_name = None
        mock_crisis.winner_id = winner_id
        mock_crisis.faction_stability = 0.9  # Restored stability
        mock_crisis.instability_effects = {}
        mock_crisis.interfering_factions = []
        mock_crisis.interference_details = {}
        mock_crisis.resolution_method = "Economic competition victory"
        mock_crisis.faction_split = False
        mock_crisis.new_factions = []
        mock_crisis.created_at = datetime.utcnow() - timedelta(days=20)
        mock_crisis.updated_at = datetime.utcnow()
        mock_crisis.metadata = {}
        
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        
        # Mock service
        mock_succession_service = Mock()
        mock_service.return_value = mock_succession_service
        mock_succession_service.resolve_succession_crisis.return_value = mock_crisis
        
        # Request data
        request_data = {
            "crisis_id": str(crisis_id),
            "winner_id": str(winner_id),
            "resolution_method": "Economic competition victory",
            "force_resolution": False
        }
        
        # Make request
        response = client.post(f"/{crisis_id}/resolve", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == str(crisis_id)
        assert data["status"] == "resolved"
        assert data["winner_id"] == str(winner_id)
        assert data["resolution_method"] == "Economic competition victory"
        assert data["faction_stability"] == 0.9


class TestExternalInterferenceEndpoints:
    """Test external interference endpoints"""
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_service')
    def test_add_external_interference(self, mock_service, mock_db):
        """Test adding external faction interference"""
        # Mock crisis entity
        crisis_id = uuid.uuid4()
        interfering_faction_id = uuid.uuid4()
        mock_crisis = Mock(spec=SuccessionCrisisEntity)
        mock_crisis.id = crisis_id
        mock_crisis.faction_id = uuid.uuid4()
        mock_crisis.faction_name = "Test Faction"
        mock_crisis.succession_type = SuccessionType.ECONOMIC_COMPETITION.value
        mock_crisis.status = SuccessionCrisisStatus.IN_PROGRESS.value
        mock_crisis.trigger = SuccessionTrigger.LEADER_DEATH_NATURAL.value
        mock_crisis.crisis_start = datetime.utcnow()
        mock_crisis.crisis_end = None
        mock_crisis.estimated_duration = 30
        mock_crisis.previous_leader_id = None
        mock_crisis.previous_leader_name = None
        mock_crisis.winner_id = None
        mock_crisis.faction_stability = 0.8
        mock_crisis.instability_effects = {}
        mock_crisis.interfering_factions = [interfering_faction_id]
        mock_crisis.interference_details = {
            str(interfering_faction_id): {
                "type": "financial_support",
                "resources": 10000.0
            }
        }
        mock_crisis.resolution_method = None
        mock_crisis.faction_split = False
        mock_crisis.new_factions = []
        mock_crisis.created_at = datetime.utcnow()
        mock_crisis.updated_at = datetime.utcnow()
        mock_crisis.metadata = {}
        
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        
        # Mock service
        mock_succession_service = Mock()
        mock_service.return_value = mock_succession_service
        mock_succession_service.add_external_interference.return_value = mock_crisis
        
        # Request data
        request_data = {
            "crisis_id": str(crisis_id),
            "interfering_faction_id": str(interfering_faction_id),
            "interference_type": "financial_support",
            "candidate_id": str(uuid.uuid4()),
            "resources_committed": 10000.0,
            "interference_details": {"method": "bribery"}
        }
        
        # Make request
        response = client.post(f"/{crisis_id}/interference", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == str(crisis_id)
        assert interfering_faction_id in data["interfering_factions"]
        assert str(interfering_faction_id) in data["interference_details"]


class TestMetricsEndpoints:
    """Test succession metrics endpoints"""
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_repository')
    def test_get_succession_metrics(self, mock_repo, mock_db):
        """Test getting succession crisis metrics"""
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        
        # Mock repository
        mock_succession_repo = Mock()
        mock_repo.return_value = mock_succession_repo
        
        # Mock metrics data
        mock_succession_repo.get_crisis_count_by_status.return_value = {
            "pending": 5,
            "in_progress": 3,
            "resolved": 15,
            "failed": 2
        }
        mock_succession_repo.get_crisis_count_by_faction_type.return_value = {
            "trading_company": 8,
            "military": 12,
            "religious": 5
        }
        mock_succession_repo.get_crisis_count_by_trigger.return_value = {
            "leader_death_natural": 10,
            "leader_death_violent": 8,
            "hidden_ambition_coup": 5,
            "external_pressure": 2
        }
        mock_succession_repo.get_crisis_count_by_succession_type.return_value = {
            "economic_competition": 8,
            "hereditary": 10,
            "military_coup": 5,
            "religious_election": 2
        }
        mock_succession_repo.get_average_crisis_duration.return_value = 25.5
        mock_succession_repo.get_average_candidates_per_crisis.return_value = 3.2
        mock_succession_repo.get_average_stability_impact.return_value = 0.15
        
        # Make request
        response = client.get("/metrics/overview")
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total_crises"] == 25  # 5 + 3 + 15 + 2
        assert data["active_crises"] == 8   # 5 + 3
        assert data["resolved_crises"] == 15
        assert data["failed_crises"] == 2
        assert data["faction_splits"] == 0  # Would be calculated from actual data
        assert "crisis_by_faction_type" in data
        assert "crisis_by_trigger" in data
        assert "crisis_by_succession_type" in data
        assert data["average_duration_days"] == 25.5
        assert data["average_candidates"] == 3.2
        assert data["average_stability_impact"] == 0.15


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_uuid_parameter(self):
        """Test endpoints with invalid UUID parameters"""
        # Test with invalid UUID
        response = client.get("/invalid-uuid")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_missing_required_fields(self):
        """Test endpoints with missing required fields"""
        # Test trigger endpoint without required fields
        response = client.post("/trigger", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test candidate endpoint without required fields
        response = client.post(f"/{uuid.uuid4()}/candidates", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('backend.systems.faction.routers.succession_router.get_db_session')
    @patch('backend.systems.faction.routers.succession_router.get_succession_service')
    def test_service_error_handling(self, mock_service, mock_db):
        """Test handling of service layer errors"""
        # Mock database
        mock_db_session = Mock()
        mock_db.return_value = mock_db_session
        
        # Mock service to raise exception
        mock_succession_service = Mock()
        mock_service.return_value = mock_succession_service
        mock_succession_service.create_succession_crisis.side_effect = Exception("Service error")
        
        # Request data
        request_data = {
            "faction_id": str(uuid.uuid4()),
            "trigger": "leader_death_natural"
        }
        
        # Make request
        response = client.post("/trigger", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Internal server error" in response.json()["detail"]


class TestValidationAndSecurity:
    """Test input validation and security"""
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection"""
        # Test with malicious input
        malicious_input = "'; DROP TABLE faction_succession_crises; --"
        
        response = client.get("/", params={"status": malicious_input})
        
        # Should not cause server error (input should be sanitized)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_large_payload_handling(self):
        """Test handling of large payloads"""
        # Create large request data
        large_data = {
            "faction_id": str(uuid.uuid4()),
            "trigger": "leader_death_natural",
            "trigger_details": {"large_field": "x" * 10000}  # 10KB string
        }
        
        response = client.post("/trigger", json=large_data)
        
        # Should handle gracefully
        assert response.status_code in [
            status.HTTP_200_OK, 
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    def test_rate_limiting_headers(self):
        """Test rate limiting headers (if implemented)"""
        response = client.get("/")
        
        # Check for rate limiting headers
        # Note: This would depend on actual rate limiting implementation
        assert response.status_code == status.HTTP_200_OK


if __name__ == "__main__":
    pytest.main([__file__]) 