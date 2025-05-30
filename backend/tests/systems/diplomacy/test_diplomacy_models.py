from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from typing import Type
"""
Unit tests for the Diplomacy System models.

Tests the data models defined in backend/systems/diplomacy/models.py
"""

import pytest
from datetime import datetime, timedelta
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


class TestTreaty: pass
    """Tests for the Treaty model."""

    def test_treaty_creation(self): pass
        """Test creating a valid treaty."""
        # Create test data
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        faction_ids = [uuid4(), uuid4()]

        # Create treaty
        treaty = Treaty(
            name="Test Alliance",
            type=TreatyType.ALLIANCE,
            parties=faction_ids,
            terms={"mutual_defense": True, "trade_bonus": 0.1},
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            is_public=True,
            created_by=faction_ids[0],
        )

        # Verify fields
        assert treaty.name == "Test Alliance"
        assert treaty.type == TreatyType.ALLIANCE
        assert treaty.parties == faction_ids
        assert treaty.terms["mutual_defense"] is True
        assert treaty.terms["trade_bonus"] == 0.1
        assert treaty.start_date == start_date
        assert treaty.end_date == end_date
        assert treaty.is_active is True
        assert treaty.is_public is True
        assert treaty.created_by == faction_ids[0]
        assert treaty.duration_days == 30

    def test_end_date_validation(self): pass
        """Test that end_date must be after start_date."""
        # Create test data
        start_date = datetime.utcnow()
        end_date = start_date - timedelta(days=1)  # End date before start date
        faction_ids = [uuid4(), uuid4()]

        # Should raise validation error
        with pytest.raises(ValueError, match="end_date must be after start_date"): pass
            Treaty(
                name="Invalid Treaty",
                type=TreatyType.TRADE,
                parties=faction_ids,
                start_date=start_date,
                end_date=end_date,
            )


class TestNegotiation: pass
    """Tests for the Negotiation model."""

    def test_negotiation_creation(self): pass
        """Test creating a valid negotiation."""
        # Create test data
        faction_ids = [uuid4(), uuid4()]
        initiator_id = faction_ids[0]

        # Create negotiation
        negotiation = Negotiation(
            title="Trade Agreement Negotiation",
            parties=faction_ids,
            initiator_id=initiator_id,
            recipient_id=faction_ids[1],
            status=NegotiationStatus.PENDING,
            treaty_type=TreatyType.TRADE,
            metadata={"previous_attempts": 1},
        )

        # Verify fields
        assert negotiation.parties == faction_ids
        assert negotiation.initiator_id == initiator_id
        assert negotiation.recipient_id == faction_ids[1]
        assert negotiation.status == NegotiationStatus.PENDING
        assert negotiation.treaty_type == TreatyType.TRADE
        assert negotiation.offers == []
        assert negotiation.current_offer_id is None
        assert negotiation.metadata["previous_attempts"] == 1

    def test_negotiation_with_offers(self): pass
        """Test negotiation with offers."""
        # Create test data
        faction_ids = [uuid4(), uuid4()]
        initiator_id = faction_ids[0]

        # Create offers
        offer1 = NegotiationOffer(
            faction_id=faction_ids[0], terms={"trade_tariff": 0.05}
        )
        offer2 = NegotiationOffer(
            faction_id=faction_ids[1],
            terms={"trade_tariff": 0.1},
            counter_offer_id=offer1.faction_id,
        )

        # Create negotiation with offers
        negotiation = Negotiation(
            title="Counter-Offer Trade Negotiation",
            parties=faction_ids,
            initiator_id=initiator_id,
            recipient_id=faction_ids[1],
            status=NegotiationStatus.COUNTER_OFFERED,
            offers=[offer1, offer2],
            current_offer_id=offer2.faction_id,
        )

        # Verify fields
        assert len(negotiation.offers) == 2
        assert negotiation.offers[0].terms["trade_tariff"] == 0.05
        assert negotiation.offers[1].terms["trade_tariff"] == 0.1
        assert negotiation.status == NegotiationStatus.COUNTER_OFFERED
        assert negotiation.current_offer_id == offer2.faction_id


class TestDiplomaticEvent: pass
    """Tests for the DiplomaticEvent model."""

    def test_diplomatic_event_creation(self): pass
        """Test creating a valid diplomatic event."""
        # Create test data
        faction_ids = [uuid4(), uuid4()]

        # Create event
        event = DiplomaticEvent(
            event_type=DiplomaticEventType.ALLIANCE_FORMED,
            factions=faction_ids,
            description="The factions formed a new alliance",
            severity=75,
            public=True,
            metadata={"ceremony_held": True},
            tension_change={f"{faction_ids[0]}_{faction_ids[1]}": -50},
        )

        # Verify fields
        assert event.event_type == DiplomaticEventType.ALLIANCE_FORMED
        assert event.factions == faction_ids
        assert event.description == "The factions formed a new alliance"
        assert event.severity == 75
        assert event.public is True
        assert event.metadata["ceremony_held"] is True
        assert event.tension_change[f"{faction_ids[0]}_{faction_ids[1]}"] == -50


class TestTreatyViolation: pass
    """Tests for the TreatyViolation model."""

    def test_treaty_violation_creation(self): pass
        """Test creating a valid treaty violation."""
        # Create test data
        treaty_id = uuid4()
        faction_id = uuid4()
        reporter_id = uuid4()

        # Create violation
        violation = TreatyViolation(
            treaty_id=treaty_id,
            violator_id=faction_id,
            violation_type=TreatyViolationType.MILITARY_BUILDUP,
            description="Built forces beyond treaty limits",
            evidence={"troop_counts": 5000, "treaty_limit": 3000},
            reported_by=reporter_id,
            severity=80,
        )

        # Verify fields
        assert violation.treaty_id == treaty_id
        assert violation.violator_id == faction_id
        assert violation.violation_type == TreatyViolationType.MILITARY_BUILDUP
        assert violation.description == "Built forces beyond treaty limits"
        assert violation.evidence["troop_counts"] == 5000
        assert violation.evidence["treaty_limit"] == 3000
        assert violation.reported_by == reporter_id
        assert violation.severity == 80
        assert violation.acknowledged is False
        assert violation.resolved is False


class TestDiplomaticIncident: pass
    """Tests for the DiplomaticIncident model."""

    def test_diplomatic_incident_creation(self): pass
        """Test creating a valid diplomatic incident."""
        # Create test data
        perpetrator_id = uuid4()
        victim_id = uuid4()
        witnesses = [uuid4(), uuid4()]

        # Create incident
        incident = DiplomaticIncident(
            title="Espionage Incident",
            incident_type=DiplomaticIncidentType.ESPIONAGE,
            perpetrator_id=perpetrator_id,
            victim_id=victim_id,
            description="Caught spies from the perpetrator faction",
            evidence={"spies_caught": 3, "documents_stolen": 2},
            severity=DiplomaticIncidentSeverity.MAJOR,
            tension_impact=40,
            public=True,
            witnessed_by=witnesses,
        )

        # Verify fields
        assert incident.title == "Espionage Incident"
        assert incident.incident_type == DiplomaticIncidentType.ESPIONAGE
        assert incident.perpetrator_id == perpetrator_id
        assert incident.victim_id == victim_id
        assert incident.description == "Caught spies from the perpetrator faction"
        assert incident.evidence["spies_caught"] == 3
        assert incident.severity == DiplomaticIncidentSeverity.MAJOR
        assert incident.tension_impact == 40
        assert incident.public is True
        assert incident.witnessed_by == witnesses
        assert incident.resolved is False


class TestUltimatum: pass
    """Tests for the Ultimatum model."""

    def test_ultimatum_creation(self): pass
        """Test creating a valid ultimatum."""
        # Create test data
        issuer_id = uuid4()
        recipient_id = uuid4()
        deadline = datetime.utcnow() + timedelta(days=3)

        # Create ultimatum
        ultimatum = Ultimatum(
            sender_id=issuer_id,
            recipient_id=recipient_id,
            demands={"withdraw_troops": True, "pay_reparations": 5000},
            consequences={"declare_war": True},
            status=UltimatumStatus.PENDING,
            deadline=deadline,
            justification="Response to border violations",
            public=True,
            tension_change_on_issue=20,
            tension_change_on_accept=-10,
            tension_change_on_reject=40,
        )

        # Verify fields
        assert ultimatum.sender_id == issuer_id
        assert ultimatum.recipient_id == recipient_id
        assert ultimatum.demands["withdraw_troops"] is True
        assert ultimatum.consequences["declare_war"] is True
        assert ultimatum.status == UltimatumStatus.PENDING
        assert ultimatum.deadline == deadline
        assert ultimatum.justification == "Response to border violations"
        assert ultimatum.public is True
        assert ultimatum.tension_change_on_issue == 20
        assert ultimatum.tension_change_on_accept == -10
        assert ultimatum.tension_change_on_reject == 40


class TestSanction: pass
    """Tests for the Sanction model."""

    def test_sanction_creation(self): pass
        """Test creating a valid sanction."""
        # Create test data
        imposer_id = uuid4()
        target_id = uuid4()
        supporters = [uuid4(), uuid4()]
        opponents = [uuid4()]

        # Create sanction
        sanction = Sanction(
            sender_id=imposer_id,
            target_id=target_id,
            sanction_type=SanctionType.TRADE_EMBARGO,
            reason="Economic disputes",
            justification="Unfair trade practices",
            severity=60,
            economic_impact=70,
            diplomatic_impact=50,
            supporting_factions=supporters,
            opposing_factions=opponents,
        )

        # Verify fields
        assert sanction.sender_id == imposer_id
        assert sanction.target_id == target_id
        assert sanction.sanction_type == SanctionType.TRADE_EMBARGO
        assert sanction.reason == "Economic disputes"
        assert sanction.justification == "Unfair trade practices"
        assert sanction.severity == 60
        assert sanction.economic_impact == 70
        assert sanction.diplomatic_impact == 50
        assert sanction.supporting_factions == supporters
        assert sanction.opposing_factions == opponents
        assert sanction.violations == []
        assert sanction.is_public is True

    def test_sanction_with_violations(self): pass
        """Test sanction with violations recorded."""
        # Create test data
        imposer_id = uuid4()
        target_id = uuid4()
        reporter_id = uuid4()

        # Create violation records
        violation1 = {
            "date": datetime.utcnow().isoformat(),
            "description": "Smuggling of goods detected",
            "evidence": {"ships_caught": 3},
            "reported_by": str(reporter_id),
            "severity": 60,
        }

        # Create sanction with violations
        sanction = Sanction(
            sender_id=imposer_id,
            target_id=target_id,
            sanction_type=SanctionType.TRADE_EMBARGO,
            reason="Economic disputes",
            justification="Unfair trade practices",
            violations=[violation1],
        )

        # Verify violations
        assert len(sanction.violations) == 1
        assert sanction.violations[0]["description"] == "Smuggling of goods detected"
        assert sanction.violations[0]["evidence"]["ships_caught"] == 3
        assert sanction.violations[0]["reported_by"] == str(reporter_id)
        assert sanction.status == SanctionStatus.VIOLATED
