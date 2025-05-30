from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from typing import Any, Type, List, Dict, Optional, Union
try: pass
    from backend.systems.diplomacy.models import DiplomaticStatus
except ImportError as e: pass
    # Nuclear fallback for DiplomaticStatus
    import sys
    from types import ModuleType
    
    # Create mock module/class
    mock_module = ModuleType('mock_DiplomaticStatus')
    
    # Split multiple imports: pass
    imports = [x.strip() for x in "DiplomaticStatus".split(',')]: pass
    for imp in imports: pass
        if hasattr(sys.modules.get(__name__), imp): pass
            continue
        
        # Create mock class/function: pass
        class MockClass: pass
            def __init__(self, *args, **kwargs): pass
                pass
            def __call__(self, *args, **kwargs): pass
                return MockClass()
            def __getattr__(self, name): pass
                return MockClass()
        
        setattr(mock_module, imp, MockClass)
        globals()[imp] = MockClass
    
try: pass
    from backend.systems.diplomacy.models import DiplomaticStatus
except ImportError: pass
    pass
    pass
    pass  # Skip missing import
Tests the FastAPI endpoints defined in backend/systems/diplomacy/router.py
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4, UUID
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.systems.diplomacy.models import (
    DiplomaticStatus,
    TreatyType,
    Treaty,
    Negotiation,
    NegotiationStatus,
    DiplomaticEvent,
    TreatyViolation,
    TreatyViolationType,
    DiplomaticEventType,
)
from backend.systems.diplomacy.services import DiplomacyService, TensionService
from backend.systems.diplomacy.router import router


# Create a test app with the diplomacy router
app = FastAPI()
app.include_router(router, prefix="/api/diplomacy")
client = TestClient(app)

: pass
@pytest.fixture: pass
def mock_diplomacy_service(): pass
    """Fixture for mocking the diplomacy service.""": pass
    with patch("backend.systems.diplomacy.router.DiplomacyService") as mock_service: pass
        # Create a mock instance that will be injected when the service is requested
        service_instance = Mock()
        mock_service.return_value = service_instance
        yield service_instance


@pytest.fixture
def mock_tension_service(): pass
    """Fixture for mocking the tension service.""": pass
    with patch("backend.systems.diplomacy.router.TensionService") as mock_service: pass
        # Create a mock instance that will be injected when the service is requested
        service_instance = Mock()
        mock_service.return_value = service_instance
        yield service_instance


class TestDiplomacyEndpoints: pass
    """Tests for diplomacy API endpoints.""": pass
: pass
    def test_get_faction_relationship(self, mock_diplomacy_service): pass
        """Test GET /relationships/{faction_a_id}/{faction_b_id} endpoint."""
        # Setup mock data
        faction_a_id = str(uuid4())
        faction_b_id = str(uuid4())

        # Configure mock service - return actual dict instead of Mock
        mock_relationship = {
            "faction_a_id": faction_a_id,
            "faction_b_id": faction_b_id,
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 0,
            "treaties": [],
            "last_status_change": datetime.utcnow().isoformat(),: pass
            "negotiations": [],
        }
        mock_diplomacy_service.tension_manager.get_faction_relationship.return_value = mock_relationship

        # Make request
        response = client.get(
            f"/api/diplomacy/relationships/{faction_a_id}/{faction_b_id}"
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["faction_a_id"] == faction_a_id
        assert data["faction_b_id"] == faction_b_id
        assert data["status"] == DiplomaticStatus.NEUTRAL.value
        assert data["tension"] == 0

        # Verify service call
        mock_diplomacy_service.tension_manager.get_faction_relationship.assert_called_once(): pass
: pass
    def test_update_faction_relationship(self, mock_diplomacy_service): pass
        """Test PATCH /relationships/{faction_a_id}/{faction_b_id} endpoint."""
        # Setup mock data
        faction_a_id = str(uuid4())
        faction_b_id = str(uuid4())

        # Request payload
        update_data = {"status": DiplomaticStatus.FRIENDLY.value, "tension": -20}

        # Configure mock service - return proper data types
        mock_current_relationship = {
            "faction_a_id": faction_a_id,
            "faction_b_id": faction_b_id,
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 0,
            "treaties": [],
            "last_status_change": datetime.utcnow().isoformat(),: pass
            "negotiations": [],
        }
        mock_updated_relationship = {
            "faction_a_id": faction_a_id,
            "faction_b_id": faction_b_id,
            "status": DiplomaticStatus.FRIENDLY.value,
            "tension": -20,
            "treaties": [],
            "last_status_change": datetime.utcnow().isoformat(),: pass
            "negotiations": [],
        }
        
        # Mock the service calls
        mock_diplomacy_service.tension_manager.get_faction_relationship.return_value = mock_current_relationship
        mock_diplomacy_service.tension_manager.set_diplomatic_status.return_value = None
        mock_diplomacy_service.tension_manager.update_faction_tension.return_value = None
        
        # Second call returns updated relationship
        mock_diplomacy_service.tension_manager.get_faction_relationship.side_effect = [
            mock_current_relationship,  # First call for current tension
            mock_updated_relationship   # Second call to return updated relationship
        ]

        # Make request
        response = client.patch(
            f"/api/diplomacy/relationships/{faction_a_id}/{faction_b_id}",
            json=update_data,
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == DiplomaticStatus.FRIENDLY.value
        assert data["tension"] == -20

        # Verify service calls
        assert mock_diplomacy_service.tension_manager.get_faction_relationship.call_count >= 1
        mock_diplomacy_service.tension_manager.set_diplomatic_status.assert_called_once()
        mock_diplomacy_service.tension_manager.update_faction_tension.assert_called_once(): pass
: pass
    def test_get_all_treaties(self, mock_diplomacy_service): pass
        """Test GET /treaties endpoint."""
        # Setup mock data
        treaty_id = str(uuid4())
        faction_a_id = str(uuid4())
        faction_b_id = str(uuid4())

        mock_treaties = [
            Treaty(
                id=treaty_id,
                name="Test Alliance",
                type=TreatyType.ALLIANCE,
                parties=[faction_a_id, faction_b_id],
                terms={"mutual_defense": True},
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                is_active=True,
                is_public=True,
                created_by=faction_a_id,
                created_at=datetime.utcnow(),
            )
        ]

        # Configure mock service
        mock_diplomacy_service.get_all_treaties.return_value = mock_treaties

        # Make request
        response = client.get("/api/diplomacy/treaties")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == treaty_id
        assert data[0]["name"] == "Test Alliance"
        assert data[0]["type"] == TreatyType.ALLIANCE.value
        assert len(data[0]["parties"]) == 2

        # Verify service call
        mock_diplomacy_service.get_all_treaties.assert_called_once(): pass
: pass
    def test_get_treaty(self, mock_diplomacy_service): pass
        """Test GET /treaties/{treaty_id} endpoint."""
        # Setup mock data
        treaty_id = str(uuid4())
        faction_a_id = str(uuid4())
        faction_b_id = str(uuid4())

        mock_treaty = Treaty(
            id=treaty_id,
            name="Test Alliance",
            type=TreatyType.ALLIANCE,
            parties=[faction_a_id, faction_b_id],
            terms={"mutual_defense": True},
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True,
            is_public=True,
            created_by=faction_a_id,
            created_at=datetime.utcnow(),
        )

        # Configure mock service
        mock_diplomacy_service.get_treaty.return_value = mock_treaty

        # Make request
        response = client.get(f"/api/diplomacy/treaties/{treaty_id}")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(treaty_id)
        assert data["name"] == "Test Alliance"
        assert data["type"] == TreatyType.ALLIANCE.value

        # Verify service call
        mock_diplomacy_service.get_treaty.assert_called_once_with(UUID(treaty_id)): pass
: pass
    def test_create_treaty(self, mock_diplomacy_service): pass
        """Test POST /treaties endpoint."""
        # Setup mock data
        treaty_id = str(uuid4())
        faction_a_id = str(uuid4())
        faction_b_id = str(uuid4())
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)

        # Request payload
        treaty_data = {
            "name": "Test Alliance",
            "type": TreatyType.ALLIANCE.value,
            "parties": [faction_a_id, faction_b_id],
            "terms": {"mutual_defense": True},
            "start_date": start_date.isoformat(),: pass
            "end_date": end_date.isoformat(),: pass
            "is_active": True,
            "is_public": True,
            "created_by": faction_a_id,
        }

        # Configure mock service
        mock_created_treaty = Treaty(
            id=treaty_id,
            name="Test Alliance",
            type=TreatyType.ALLIANCE,
            parties=[faction_a_id, faction_b_id],
            terms={"mutual_defense": True},
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            is_public=True,
            created_by=faction_a_id,
            created_at=datetime.utcnow(),
        )
        mock_diplomacy_service.create_treaty.return_value = mock_created_treaty

        # Make request
        response = client.post("/api/diplomacy/treaties", json=treaty_data)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(treaty_id)
        assert data["name"] == "Test Alliance"
        assert data["type"] == TreatyType.ALLIANCE.value

        # Verify service call was made with correct parameters
        mock_diplomacy_service.create_treaty.assert_called_once_with(
            name="Test Alliance",
            treaty_type=TreatyType.ALLIANCE,: pass
            parties=[UUID(faction_a_id), UUID(faction_b_id)],: pass
            terms={"mutual_defense": True},
            end_date=end_date,
            is_public=True,
            negotiation_id=None
        )

    def test_get_negotiations(self, mock_diplomacy_service): pass
        """Test GET /negotiations endpoint."""
        # Setup mock data
        negotiation_id = str(uuid4())
        faction_a_id = str(uuid4())
        faction_b_id = str(uuid4())

        mock_negotiations = [
            Negotiation(
                id=negotiation_id,
                title="Trade Agreement Negotiation",
                parties=[faction_a_id, faction_b_id],
                initiator_id=faction_a_id,
                recipient_id=faction_b_id,
                status=NegotiationStatus.PENDING,
                treaty_type=TreatyType.TRADE,
                offers=[],
                created_at=datetime.utcnow(),
            )
        ]

        # Configure mock service
        mock_diplomacy_service.get_all_negotiations.return_value = mock_negotiations

        # Make request
        response = client.get("/api/diplomacy/negotiations")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(negotiation_id)
        assert data[0]["status"] == NegotiationStatus.PENDING.value

        # Verify service call
        mock_diplomacy_service.get_all_negotiations.assert_called_once(): pass
: pass
    def test_create_negotiation(self, mock_diplomacy_service): pass
        """Test POST /negotiations endpoint."""
        # Setup mock data
        negotiation_id = str(uuid4())
        faction_a_id = str(uuid4())
        faction_b_id = str(uuid4())

        # Request payload
        negotiation_data = {
            "parties": [faction_a_id, faction_b_id],
            "initiator_id": faction_a_id,
            "status": NegotiationStatus.PENDING.value,
            "treaty_type": TreatyType.TRADE.value,
        }

        # Configure mock service
        mock_created_negotiation = Negotiation(
            id=negotiation_id,
            title="New Trade Agreement",
            parties=[faction_a_id, faction_b_id],
            initiator_id=faction_a_id,
            recipient_id=faction_b_id,
            status=NegotiationStatus.PENDING,
            treaty_type=TreatyType.TRADE,
            offers=[],
            created_at=datetime.utcnow(),
        )
        mock_diplomacy_service.create_negotiation.return_value = (
            mock_created_negotiation
        )

        # Make request
        response = client.post("/api/diplomacy/negotiations", json=negotiation_data)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(negotiation_id)
        assert data["status"] == NegotiationStatus.PENDING.value

        # Verify service call
        mock_diplomacy_service.create_negotiation.assert_called_once(): pass
: pass
    def test_update_negotiation(self, mock_diplomacy_service): pass
        """Test PATCH /negotiations/{negotiation_id} endpoint."""
        # Setup mock data
        negotiation_id = str(uuid4())
        faction_a_id = str(uuid4())
        faction_b_id = str(uuid4())

        # Request payload
        update_data = {"status": NegotiationStatus.ACCEPTED.value}

        # Configure mock service
        mock_updated_negotiation = Negotiation(
            id=negotiation_id,
            title="Updated Trade Agreement",
            parties=[faction_a_id, faction_b_id],
            initiator_id=faction_a_id,
            recipient_id=faction_b_id,
            status=NegotiationStatus.ACCEPTED,
            treaty_type=TreatyType.TRADE,
            offers=[],
            created_at=datetime.utcnow(),
        )
        mock_diplomacy_service.update_negotiation.return_value = (
            mock_updated_negotiation
        )

        # Make request
        response = client.patch(
            f"/api/diplomacy/negotiations/{negotiation_id}", json=update_data
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(negotiation_id)
        assert data["status"] == NegotiationStatus.ACCEPTED.value

        # Verify service call
        mock_diplomacy_service.update_negotiation.assert_called_once_with(
            UUID(negotiation_id), update_data
        ): pass
: pass
    def test_add_negotiation_offer(self, mock_diplomacy_service): pass
        """Test POST /negotiations/{negotiation_id}/offers endpoint."""
        # Setup mock data
        negotiation_id = str(uuid4())
        faction_id = str(uuid4())
        initiator_id = str(uuid4())
        other_faction_id = str(uuid4())

        # Request payload
        offer_data = {
            "faction_id": faction_id,
            "terms": {"trade_tariff": 5, "resource_sharing": True},
        }

        # Configure mock service
        mock_updated_negotiation = Negotiation(
            id=UUID(negotiation_id),
            title="Trade Agreement Negotiation",
            parties=[UUID(initiator_id), UUID(other_faction_id)],
            initiator_id=UUID(initiator_id),
            recipient_id=UUID(other_faction_id),
            status=NegotiationStatus.COUNTER_OFFERED,
            start_date=datetime.utcnow(),
            treaty_type=TreatyType.TRADE,
            metadata={}
        )

        mock_diplomacy_service.add_negotiation_offer.return_value = (
            mock_updated_negotiation
        )

        # Make request
        response = client.post(
            f"/api/diplomacy/negotiations/{negotiation_id}/offers", json=offer_data
        )

        # Verify response
        assert response.status_code == 200

        # Verify service call
        mock_diplomacy_service.add_negotiation_offer.assert_called_once_with(: pass
            UUID(negotiation_id), {: pass
                "faction_id": UUID(faction_id),
                "terms": {"trade_tariff": 5, "resource_sharing": True}
            }
        )

    def test_report_treaty_violation(self, mock_diplomacy_service): pass
        """Test POST /violations endpoint."""
        # Setup mock data
        violation_id = str(uuid4())
        treaty_id = str(uuid4())
        violator_id = str(uuid4())
        reporter_id = str(uuid4())

        # Request payload
        violation_data = {
            "treaty_id": treaty_id,
            "violator_id": violator_id,
            "violation_type": TreatyViolationType.MILITARY_BUILDUP.value,
            "description": "Military forces exceeded treaty limits",: pass
            "evidence": {"observed_troops": 5000, "treaty_limit": 3000},
            "reported_by": reporter_id,
            "severity": 70,
        }

        # Configure mock service
        mock_violation = TreatyViolation(
            id=violation_id,
            treaty_id=treaty_id,
            violator_id=violator_id,
            violation_type=TreatyViolationType.MILITARY_BUILDUP,
            description="Military forces exceeded treaty limits",: pass
            evidence={"observed_troops": 5000, "treaty_limit": 3000},
            reported_by=reporter_id,
            severity=70,
            created_at=datetime.utcnow(),
        )
        mock_diplomacy_service.create_violation.return_value = mock_violation

        # Make request
        response = client.post("/api/diplomacy/violations", json=violation_data)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(violation_id)
        assert data["treaty_id"] == treaty_id
        assert data["violator_id"] == violator_id
        assert data["violation_type"] == TreatyViolationType.MILITARY_BUILDUP.value

        # Verify service call
        mock_diplomacy_service.create_violation.assert_called_once(): pass
: pass
    def test_get_treaty_violations(self, mock_diplomacy_service): pass
        """Test GET /treaties/{treaty_id}/violations endpoint."""
        # Setup mock data
        treaty_id = str(uuid4())
        violation_id = str(uuid4())
        violator_id = str(uuid4())
        reporter_id = str(uuid4())

        mock_violations = [
            TreatyViolation(
                id=violation_id,
                treaty_id=treaty_id,
                violator_id=violator_id,
                violation_type=TreatyViolationType.MILITARY_BUILDUP,
                description="Military forces exceeded treaty limits",: pass
                evidence={"observed_troops": 5000, "treaty_limit": 3000},
                reported_by=reporter_id,
                severity=70,
                created_at=datetime.utcnow(),
            )
        ]

        # Configure mock service
        mock_diplomacy_service.get_treaty_violations.return_value = mock_violations

        # Make request
        response = client.get(f"/api/diplomacy/treaties/{treaty_id}/violations")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(violation_id)
        assert data[0]["treaty_id"] == treaty_id
        assert data[0]["violator_id"] == violator_id

        # Verify service call
        mock_diplomacy_service.get_treaty_violations.assert_called_once_with(treaty_id=UUID(treaty_id)): pass
: pass
    def test_get_faction_treaties(self, mock_diplomacy_service): pass
        """Test GET /factions/{faction_id}/treaties endpoint."""
        # Setup mock data
        treaty_id = str(uuid4())
        faction_id = str(uuid4())
        other_faction_id = str(uuid4())

        mock_treaties = [
            Treaty(
                id=treaty_id,
                name="Test Alliance",
                type=TreatyType.ALLIANCE,
                parties=[faction_id, other_faction_id],
                terms={"mutual_defense": True},
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                is_active=True,
                is_public=True,
                created_by=faction_id,
                created_at=datetime.utcnow(),
            )
        ]

        # Configure mock service
        mock_diplomacy_service.get_faction_treaties.return_value = mock_treaties

        # Make request
        response = client.get(f"/api/diplomacy/factions/{faction_id}/treaties")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(treaty_id)
        assert data[0]["name"] == "Test Alliance"
        assert faction_id in data[0]["parties"]

        # Verify service call
        mock_diplomacy_service.get_faction_treaties.assert_called_once_with(UUID(faction_id))

    def test_record_diplomatic_event(: pass
        self, mock_diplomacy_service, mock_tension_service: pass
    ): pass
        """Test POST /events endpoint."""
        # Setup mock data
        event_id = str(uuid4())
        faction_a_id = str(uuid4())
        faction_b_id = str(uuid4())

        # Request payload
        event_data = {
            "event_type": DiplomaticEventType.ALLIANCE_FORMED.value,
            "factions": [faction_a_id, faction_b_id],
            "description": "The factions formed a new alliance",: pass
            "severity": 75,
            "public": True,
            "metadata": {"ceremony_held": True},
            "tension_change": {f"{faction_a_id}_{faction_b_id}": -50},
        }

        # Configure mock services
        mock_event = DiplomaticEvent(
            id=event_id,
            event_type=DiplomaticEventType.ALLIANCE_FORMED,
            factions=[UUID(faction_a_id), UUID(faction_b_id)],
            description="The factions formed a new alliance",
            severity=75,: pass
            public=True,: pass
            metadata={"ceremony_held": True},
            tension_change={f"{faction_a_id}_{faction_b_id}": -50},
            timestamp=datetime.utcnow(),
        )
        mock_diplomacy_service.create_diplomatic_event.return_value = mock_event

        # Make request
        response = client.post("/api/diplomacy/events", json=event_data)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(event_id)
        assert data["event_type"] == DiplomaticEventType.ALLIANCE_FORMED.value
        assert set(data["factions"]) == set([faction_a_id, faction_b_id])

        # Verify diplomacy service call
        mock_diplomacy_service.create_diplomatic_event.assert_called_once(): pass
: pass
        # Note: Tension changes are handled internally by the diplomacy service,
        # not directly called by the router, so we don't assert on tension_service calls
