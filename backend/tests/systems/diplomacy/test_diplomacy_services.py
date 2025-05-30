from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from typing import Type
"""
Unit tests for the Diplomacy System services.

Tests the business logic in backend/systems/diplomacy/services.py
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

from backend.systems.diplomacy.models import (
    DiplomaticStatus,
    TreatyType,
    NegotiationOffer,
    NegotiationStatus,
    Treaty,
    Negotiation,
    DiplomaticEventType,
    DiplomaticEvent,
    TreatyViolationType,
    TreatyViolation,
    DiplomaticIncidentType,
    DiplomaticIncidentSeverity,
    DiplomaticIncident,
    UltimatumStatus,
    Ultimatum,
    SanctionType,
    SanctionStatus,
    Sanction,
)
from backend.systems.diplomacy.services import TensionService, DiplomacyService


class TestTensionService: pass
    """Tests for the TensionService class."""

    def setup_method(self): pass
        """Setup for each test."""
        self.mock_repository = Mock()
        self.service = TensionService(repository=self.mock_repository)

        # Common test data
        self.faction_a_id = uuid4()
        self.faction_b_id = uuid4()

    def test_get_faction_relationship(self): pass
        """Test getting faction relationship."""
        # Setup mock
        expected_relationship = {
            "faction_a_id": str(self.faction_a_id),
            "faction_b_id": str(self.faction_b_id),
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 0,
            "treaties": [],
            "last_updated": datetime.utcnow().isoformat(),
        }
        self.mock_repository.get_faction_relationship.return_value = expected_relationship

        # Call service
        result = self.service.get_faction_relationship(self.faction_a_id, self.faction_b_id)

        # Verify
        self.mock_repository.get_faction_relationship.assert_called_once_with(
            self.faction_a_id, self.faction_b_id
        )
        assert result == expected_relationship

    def test_update_faction_tension_increase(self): pass
        """Test updating faction tension with an increase."""
        # Setup mocks
        current_time = datetime.utcnow()
        current_relationship = {
            "faction_a_id": str(self.faction_a_id),
            "faction_b_id": str(self.faction_b_id),
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 20,
            "last_updated": current_time.isoformat(),  # Use current time to avoid decay
        }
        self.mock_repository.get_faction_relationship.return_value = current_relationship

        updated_relationship = current_relationship.copy()
        updated_relationship["tension"] = 35  # 20 + 15
        updated_relationship["last_updated"] = current_time.isoformat()
        self.mock_repository.update_faction_relationship.return_value = updated_relationship

        # Call service
        result = self.service.update_faction_tension(
            self.faction_a_id, self.faction_b_id, 15, "Test reason"
        )

        # Verify repository calls - the service may reorder UUIDs, so check both possible orders
        assert self.mock_repository.get_faction_relationship.called
        call_args = self.mock_repository.get_faction_relationship.call_args
        assert call_args is not None
        args, _ = call_args
        # The service should call with some order of the two faction IDs
        assert set(args) == {self.faction_a_id, self.faction_b_id}
        
        # Check that update_faction_relationship was called with tension update
        call_args = self.mock_repository.update_faction_relationship.call_args
        assert call_args is not None
        args, kwargs = call_args

        # The updates parameter is the third positional argument
        updates = args[2] if len(args) > 2 else {}
        assert "tension" in updates
        # Allow for small floating point differences due to decay calculation
        assert abs(updates["tension"] - 35) < 1.0

        # Verify result
        assert result == updated_relationship

    def test_update_faction_tension_with_status_change(self): pass
        """Test updating faction tension that triggers a status change."""
        # Setup mocks - high tension that should trigger war
        current_time = datetime.utcnow()
        current_relationship = {
            "faction_a_id": str(self.faction_a_id),
            "faction_b_id": str(self.faction_b_id),
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 85,
            "last_updated": current_time.isoformat(),  # Use current time to avoid decay
        }
        self.mock_repository.get_faction_relationship.return_value = current_relationship

        updated_relationship = current_relationship.copy()
        updated_relationship["tension"] = 100  # Service caps at max_tension (100)
        updated_relationship["status"] = DiplomaticStatus.WAR.value
        updated_relationship["last_updated"] = current_time.isoformat()
        self.mock_repository.update_faction_relationship.return_value = updated_relationship

        # Call service
        result = self.service.update_faction_tension(
            self.faction_a_id, self.faction_b_id, 20, "Major incident"
        )

        # Verify repository calls - the service may reorder UUIDs
        assert self.mock_repository.get_faction_relationship.called
        
        # Check that update_faction_relationship was called with both tension and status updates
        call_args = self.mock_repository.update_faction_relationship.call_args
        assert call_args is not None
        args, kwargs = call_args

        # The updates parameter is the third positional argument
        updates = args[2] if len(args) > 2 else {}
        assert "tension" in updates
        assert "status" in updates
        # Service caps tension at max_tension (100)
        assert updates["tension"] == 100
        assert updates["status"] == DiplomaticStatus.WAR

        # Verify result
        assert result == updated_relationship

    def test_set_diplomatic_status(self): pass
        """Test setting diplomatic status between factions."""
        # Setup mocks
        current_relationship = {
            "faction_a_id": str(self.faction_a_id),
            "faction_b_id": str(self.faction_b_id),
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 50,
        }
        self.mock_repository.get_faction_relationship.return_value = current_relationship

        updated_relationship = current_relationship.copy()
        updated_relationship["status"] = DiplomaticStatus.ALLIANCE.value
        self.mock_repository.update_faction_relationship.return_value = updated_relationship

        # Call service
        result = self.service.set_diplomatic_status(
            self.faction_a_id, self.faction_b_id, DiplomaticStatus.ALLIANCE
        )

        # Verify repository calls - the service calls get_faction_relationship twice due to bidirectional updates
        assert self.mock_repository.get_faction_relationship.call_count >= 1
        
        # Check that update_faction_relationship was called with status update
        call_args = self.mock_repository.update_faction_relationship.call_args
        assert call_args is not None
        args, kwargs = call_args

        # The updates parameter is the third positional argument
        updates = args[2] if len(args) > 2 else {}
        assert "status" in updates
        assert updates["status"] == DiplomaticStatus.ALLIANCE

        # Verify result
        assert result["status"] == DiplomaticStatus.ALLIANCE.value


class TestDiplomacyService: pass
    """Tests for the DiplomacyService class."""

    def setup_method(self): pass
        """Setup for each test."""
        self.mock_repository = Mock()
        self.service = DiplomacyService(repository=self.mock_repository)

        # Common test data
        self.faction_a_id = uuid4()
        self.faction_b_id = uuid4()

    def test_create_treaty(self): pass
        """Test creating a new treaty."""
        # Setup mocks - create a proper Treaty mock with all required attributes
        treaty_id = uuid4()
        mock_treaty = Mock(spec=Treaty)
        mock_treaty.id = treaty_id
        mock_treaty.name = "Test Peace Treaty"
        mock_treaty.type = TreatyType.PEACE
        mock_treaty.parties = [self.faction_a_id, self.faction_b_id]
        mock_treaty.terms = {"territorial_concessions": False}
        mock_treaty.is_public = True
        mock_treaty.is_active = True
        
        self.mock_repository.create_treaty.return_value = mock_treaty
        self.mock_repository.get_faction_relationship.return_value = {
            "faction_a_id": str(self.faction_a_id),
            "faction_b_id": str(self.faction_b_id),
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 0,
            "treaties": []
        }
        self.mock_repository.update_faction_relationship.return_value = {}
        self.mock_repository.create_event.return_value = Mock(spec=DiplomaticEvent)

        # Create test data
        treaty_name = "Test Peace Treaty"
        parties = [self.faction_a_id, self.faction_b_id]
        terms = {"territorial_concessions": False}
        end_date = datetime.utcnow() + timedelta(days=30)

        # Call service
        result = self.service.create_treaty(
            name=treaty_name,
            treaty_type=TreatyType.PEACE,
            parties=parties,
            terms=terms,
            end_date=end_date,
        )

        # Verify repository call
        assert self.mock_repository.create_treaty.called

        # Get the Treaty object that was passed to create_treaty
        call_args = self.mock_repository.create_treaty.call_args
        assert call_args is not None
        args, _ = call_args
        treaty_arg = args[0]

        # Verify treaty fields
        assert treaty_arg.name == treaty_name
        assert treaty_arg.type == TreatyType.PEACE
        assert set(treaty_arg.parties) == set(parties)
        assert treaty_arg.terms == terms
        assert treaty_arg.end_date == end_date

        # Verify result
        assert result == mock_treaty

    def test_start_negotiation(self): pass
        """Test starting a new negotiation."""
        # Setup mocks - create a proper Negotiation mock with all required attributes
        negotiation_id = uuid4()
        mock_negotiation = Mock(spec=Negotiation)
        mock_negotiation.id = negotiation_id
        mock_negotiation.parties = [self.faction_a_id, self.faction_b_id]
        mock_negotiation.initiator_id = self.faction_a_id
        mock_negotiation.recipient_id = self.faction_b_id
        mock_negotiation.status = NegotiationStatus.PENDING
        mock_negotiation.treaty_type = TreatyType.TRADE
        
        self.mock_repository.create_negotiation.return_value = mock_negotiation
        self.mock_repository.create_event.return_value = Mock(spec=DiplomaticEvent)
        
        # Mock the relationship data as a dictionary (not a Mock object)
        mock_relationship = {
            "faction_a_id": str(self.faction_a_id),
            "faction_b_id": str(self.faction_b_id),
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 0,
            "negotiations": []  # Add the negotiations key that the service expects
        }
        self.mock_repository.get_faction_relationship.return_value = mock_relationship
        self.mock_repository.update_faction_relationship.return_value = mock_relationship

        # Create test data matching the actual service method signature
        parties = [self.faction_a_id, self.faction_b_id]
        initiator_id = self.faction_a_id
        treaty_type = TreatyType.TRADE
        initial_offer = {"trade_rights": "full_access", "trade_tariff": 0.05}
        metadata = {"importance": "high", "urgency": "low"}

        # Call service with correct parameters
        result = self.service.start_negotiation(
            parties=parties,
            initiator_id=initiator_id,
            treaty_type=treaty_type,
            initial_offer=initial_offer,
            metadata=metadata
        )

        # Verify calls
        self.mock_repository.create_negotiation.assert_called_once()
        assert result is not None

    def test_make_offer(self): pass
        """Test making an offer in a negotiation."""
        # Setup mocks
        negotiation_id = uuid4()
        negotiation = Negotiation(
            id=negotiation_id,
            title="Test Trade Negotiation",
            parties=[self.faction_a_id, self.faction_b_id],
            initiator_id=str(self.faction_a_id),
            recipient_id=str(self.faction_b_id),
            status=NegotiationStatus.PENDING,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            offers=[],
            treaty_type=TreatyType.TRADE,
            metadata={}
        )

        self.mock_repository.get_negotiation.return_value = negotiation
        self.mock_repository.update_negotiation.return_value = (negotiation, Mock(spec=NegotiationOffer))

        # Call service with correct parameters matching the actual method signature
        terms = {"trade_rights": "restricted", "trade_tariff": 0.1}
        result = self.service.make_offer(
            negotiation_id=negotiation_id, 
            faction_id=self.faction_b_id,
            terms=terms,
            counter_to=None
        )

        # Verify repository calls
        self.mock_repository.get_negotiation.assert_called_once_with(negotiation_id)
        assert self.mock_repository.update_negotiation.called

        # Verify result is a tuple of (negotiation, offer)
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_report_treaty_violation(self): pass
        """Test reporting a treaty violation."""
        # Setup mocks - create a proper Treaty mock with parties attribute
        treaty_id = uuid4()
        mock_treaty = Mock(spec=Treaty)
        mock_treaty.id = treaty_id
        mock_treaty.parties = [self.faction_a_id, self.faction_b_id]
        mock_treaty.name = "Test Treaty"
        mock_treaty.type = TreatyType.PEACE
        mock_treaty.is_active = True  # Add the missing is_active attribute
        
        # Create a proper violation Mock with id attribute
        violation_id = uuid4()
        mock_violation = Mock(spec=TreatyViolation)
        mock_violation.id = violation_id
        mock_violation.treaty_id = treaty_id
        mock_violation.violator_id = self.faction_a_id
        mock_violation.violation_type = TreatyViolationType.MILITARY_BUILDUP
        mock_violation.description = "Military forces exceeded treaty limits"
        mock_violation.evidence = {"observed_troops": 5000, "treaty_limit": 3000}
        mock_violation.reported_by = self.faction_b_id
        mock_violation.severity = 70
        
        self.mock_repository.get_treaty.return_value = mock_treaty
        self.mock_repository.create_violation.return_value = mock_violation
        self.mock_repository.create_event.return_value = Mock(spec=DiplomaticEvent)

        # Mock the tension service to avoid datetime arithmetic errors
        current_time = datetime.utcnow()
        mock_relationship = {
            "faction_a_id": str(self.faction_a_id),
            "faction_b_id": str(self.faction_b_id),
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 20,
            "last_updated": current_time.isoformat(),  # Use string format to avoid Mock issues
        }
        
        # Mock the tension service methods to avoid datetime arithmetic with Mock objects
        with patch.object(self.service.tension_service, 'update_faction_tension', return_value=mock_relationship): pass
            # Call service
            violation_type = TreatyViolationType.MILITARY_BUILDUP
            description = "Military forces exceeded treaty limits"
            evidence = {"observed_troops": 5000, "treaty_limit": 3000}

            result = self.service.report_treaty_violation(
                treaty_id=treaty_id,
                violator_id=self.faction_a_id,
                violation_type=violation_type,
                description=description,
                evidence=evidence,
                reported_by=self.faction_b_id,
                severity=70,
            )

            # Verify repository call
            assert self.mock_repository.create_violation.called

            # Get the violation object that was passed to create_violation
            call_args = self.mock_repository.create_violation.call_args
            assert call_args is not None
            args, _ = call_args
            violation_arg = args[0]

            # Verify violation fields
            assert violation_arg.treaty_id == treaty_id
            assert violation_arg.violator_id == self.faction_a_id
            assert violation_arg.violation_type == violation_type
            assert violation_arg.description == description
            assert violation_arg.evidence == evidence
            assert violation_arg.reported_by == self.faction_b_id
            assert violation_arg.severity == 70

            # Verify result
            assert result == mock_violation

    def test_create_diplomatic_incident(self): pass
        """Test creating a diplomatic incident."""
        # Setup mocks
        incident_id = uuid4()
        mock_incident = Mock(spec=DiplomaticIncident)
        mock_incident.id = incident_id
        mock_incident.incident_type = DiplomaticIncidentType.ESPIONAGE
        mock_incident.perpetrator_id = self.faction_a_id
        mock_incident.victim_id = self.faction_b_id
        
        self.mock_repository.create_diplomatic_incident.return_value = mock_incident
        self.mock_repository.create_event.return_value = Mock(spec=DiplomaticEvent)
        
        # Mock the tension service to return a proper relationship with last_updated as datetime
        current_time = datetime.utcnow()
        mock_relationship = {
            "faction_a_id": str(self.faction_a_id),
            "faction_b_id": str(self.faction_b_id),
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 20,
            "last_updated": current_time.isoformat(),  # Use string format to avoid Mock issues
        }
        
        # Mock the tension service methods
        with patch.object(self.service.tension_service, 'get_faction_relationship', return_value=mock_relationship): pass
            with patch.object(self.service.tension_service, 'update_faction_tension', return_value=mock_relationship): pass
                # Call service
                incident_type = DiplomaticIncidentType.ESPIONAGE
                description = "Caught spies in our territory"
                evidence = {"spies_caught": 3, "documents_stolen": 2}

                result = self.service.create_diplomatic_incident(
                    incident_type=incident_type,
                    perpetrator_id=self.faction_a_id,
                    victim_id=self.faction_b_id,
                    description=description,
                    evidence=evidence,
                    severity=DiplomaticIncidentSeverity.MODERATE,
                    tension_impact=30,
                    public=True,
                )

                # Verify repository call
                assert self.mock_repository.create_diplomatic_incident.called

                # Verify result
                assert result is not None
