from dataclasses import field
"""
Tests for Tension System Schemas

This module contains comprehensive tests for tension system Pydantic schemas.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from backend.systems.tension_war.schemas.tension_schemas import (
    TensionRequest,
    TensionHistoryEntry,
    FactionTensionData,
    TensionResponse,
    TensionHistoryResponse,
    TensionEventRequest,
)


class TestTensionRequest: pass
    """Test TensionRequest schema validation."""

    def test_tension_request_valid(self): pass
        """Test valid tension request creation."""
        data = {
            "faction": {"faction_a": "faction_123", "faction_b": "faction_456"},
            "value": 25.0,
            "reason": "Border dispute escalation"
        }
        
        request = TensionRequest(**data)
        
        assert request.faction == {"faction_a": "faction_123", "faction_b": "faction_456"}
        assert request.value == 25.0
        assert request.reason == "Border dispute escalation"

    def test_tension_request_without_reason(self): pass
        """Test tension request without optional reason field."""
        data = {
            "faction": {"faction_a": "faction_123", "faction_b": "faction_456"},
            "value": -10.0
        }
        
        request = TensionRequest(**data)
        
        assert request.faction == {"faction_a": "faction_123", "faction_b": "faction_456"}
        assert request.value == -10.0
        assert request.reason is None

    def test_tension_request_missing_faction(self): pass
        """Test tension request validation with missing faction."""
        data = {
            "value": 25.0,
            "reason": "Border dispute"
        }
        
        with pytest.raises(ValidationError) as exc_info: pass
            TensionRequest(**data)
        
        assert "faction" in str(exc_info.value)

    def test_tension_request_missing_value(self): pass
        """Test tension request validation with missing value."""
        data = {
            "faction": {"faction_a": "faction_123", "faction_b": "faction_456"},
            "reason": "Border dispute"
        }
        
        with pytest.raises(ValidationError) as exc_info: pass
            TensionRequest(**data)
        
        assert "value" in str(exc_info.value)

    def test_tension_request_invalid_faction_format(self): pass
        """Test tension request with invalid faction format."""
        data = {
            "faction": "invalid_string_format",  # Should be dict
            "value": 25.0
        }
        
        with pytest.raises(ValidationError) as exc_info: pass
            TensionRequest(**data)
        
        assert "faction" in str(exc_info.value)

    def test_tension_request_invalid_value_type(self): pass
        """Test tension request with invalid value type."""
        data = {
            "faction": {"faction_a": "faction_123", "faction_b": "faction_456"},
            "value": "not_a_number"  # Should be float
        }
        
        with pytest.raises(ValidationError) as exc_info: pass
            TensionRequest(**data)
        
        assert "value" in str(exc_info.value)

    def test_tension_request_extreme_values(self): pass
        """Test tension request with extreme values."""
        # Very large positive value
        data = {
            "faction": {"faction_a": "faction_123", "faction_b": "faction_456"},
            "value": 999999.0
        }
        request = TensionRequest(**data)
        assert request.value == 999999.0
        
        # Very large negative value
        data["value"] = -999999.0
        request = TensionRequest(**data)
        assert request.value == -999999.0

    def test_tension_request_zero_value(self): pass
        """Test tension request with zero value."""
        data = {
            "faction": {"faction_a": "faction_123", "faction_b": "faction_456"},
            "value": 0.0
        }
        
        request = TensionRequest(**data)
        assert request.value == 0.0

    def test_tension_request_serialization(self): pass
        """Test tension request serialization."""
        data = {
            "faction": {"faction_a": "faction_123", "faction_b": "faction_456"},
            "value": 25.0,
            "reason": "Border dispute"
        }
        
        request = TensionRequest(**data)
        serialized = request.dict()
        
        assert serialized == data


class TestTensionHistoryEntry: pass
    """Test TensionHistoryEntry schema validation."""

    def test_history_entry_valid(self): pass
        """Test valid history entry creation."""
        data = {
            "timestamp": "2024-01-01T12:00:00Z",
            "tension": 45.0,
            "level": "hostile",
            "reason": "Border skirmish"
        }
        
        entry = TensionHistoryEntry(**data)
        
        assert entry.timestamp == "2024-01-01T12:00:00Z"
        assert entry.tension == 45.0
        assert entry.level == "hostile"
        assert entry.reason == "Border skirmish"

    def test_history_entry_without_reason(self): pass
        """Test history entry without optional reason."""
        data = {
            "timestamp": "2024-01-01T12:00:00Z",
            "tension": 45.0,
            "level": "hostile"
        }
        
        entry = TensionHistoryEntry(**data)
        
        assert entry.reason is None

    def test_history_entry_missing_required_fields(self): pass
        """Test history entry validation with missing required fields."""
        # Missing timestamp
        with pytest.raises(ValidationError): pass
            TensionHistoryEntry(tension=45.0, level="hostile")
        
        # Missing tension
        with pytest.raises(ValidationError): pass
            TensionHistoryEntry(timestamp="2024-01-01T12:00:00Z", level="hostile")
        
        # Missing level
        with pytest.raises(ValidationError): pass
            TensionHistoryEntry(timestamp="2024-01-01T12:00:00Z", tension=45.0)

    def test_history_entry_invalid_types(self): pass
        """Test history entry with invalid field types."""
        # Invalid tension type
        with pytest.raises(ValidationError): pass
            TensionHistoryEntry(
                timestamp="2024-01-01T12:00:00Z",
                tension="not_a_number",
                level="hostile"
            )


class TestFactionTensionData: pass
    """Test FactionTensionData schema validation."""

    def test_faction_tension_data_valid(self): pass
        """Test valid faction tension data creation."""
        data = {
            "tension": 67.5,
            "level": "war",
            "last_updated": "2024-01-01T12:00:00Z",
            "history": [
                {
                    "timestamp": "2024-01-01T11:00:00Z",
                    "tension": 60.0,
                    "level": "hostile",
                    "reason": "Previous conflict"
                }
            ]
        }
        
        faction_data = FactionTensionData(**data)
        
        assert faction_data.tension == 67.5
        assert faction_data.level == "war"
        assert faction_data.last_updated == "2024-01-01T12:00:00Z"
        assert len(faction_data.history) == 1

    def test_faction_tension_data_without_history(self): pass
        """Test faction tension data without optional history."""
        data = {
            "tension": 67.5,
            "level": "war",
            "last_updated": "2024-01-01T12:00:00Z"
        }
        
        faction_data = FactionTensionData(**data)
        
        assert faction_data.history is None

    def test_faction_tension_data_missing_required_fields(self): pass
        """Test faction tension data with missing required fields."""
        # Missing tension
        with pytest.raises(ValidationError): pass
            FactionTensionData(level="war", last_updated="2024-01-01T12:00:00Z")
        
        # Missing level
        with pytest.raises(ValidationError): pass
            FactionTensionData(tension=67.5, last_updated="2024-01-01T12:00:00Z")
        
        # Missing last_updated
        with pytest.raises(ValidationError): pass
            FactionTensionData(tension=67.5, level="war")

    def test_faction_tension_data_empty_history(self): pass
        """Test faction tension data with empty history list."""
        data = {
            "tension": 67.5,
            "level": "war",
            "last_updated": "2024-01-01T12:00:00Z",
            "history": []
        }
        
        faction_data = FactionTensionData(**data)
        
        assert faction_data.history == []


class TestTensionResponse: pass
    """Test TensionResponse schema validation."""

    def test_tension_response_valid(self): pass
        """Test valid tension response creation."""
        data = {
            "region_id": "region_123",
            "factions": {
                "faction_1_faction_2": {
                    "tension": 45.0,
                    "level": "tense",
                    "last_updated": "2024-01-01T12:00:00Z"
                }
            },
            "last_updated": "2024-01-01T12:00:00Z"
        }
        
        response = TensionResponse(**data)
        
        assert response.region_id == "region_123"
        assert "faction_1_faction_2" in response.factions
        assert response.factions["faction_1_faction_2"].tension == 45.0

    def test_tension_response_empty_factions(self): pass
        """Test tension response with empty factions dict."""
        data = {
            "region_id": "region_123",
            "factions": {},
            "last_updated": "2024-01-01T12:00:00Z"
        }
        
        response = TensionResponse(**data)
        
        assert response.factions == {}

    def test_tension_response_multiple_factions(self): pass
        """Test tension response with multiple faction pairs."""
        data = {
            "region_id": "region_123",
            "factions": {
                "faction_1_faction_2": {
                    "tension": 45.0,
                    "level": "tense",
                    "last_updated": "2024-01-01T12:00:00Z"
                },
                "faction_1_faction_3": {
                    "tension": -25.0,
                    "level": "friendly",
                    "last_updated": "2024-01-01T12:00:00Z"
                }
            },
            "last_updated": "2024-01-01T12:00:00Z"
        }
        
        response = TensionResponse(**data)
        
        assert len(response.factions) == 2
        assert response.factions["faction_1_faction_2"].tension == 45.0
        assert response.factions["faction_1_faction_3"].tension == -25.0

    def test_tension_response_missing_required_fields(self): pass
        """Test tension response with missing required fields."""
        # Missing region_id
        with pytest.raises(ValidationError): pass
            TensionResponse(
                factions={},
                last_updated="2024-01-01T12:00:00Z"
            )
        
        # Missing factions
        with pytest.raises(ValidationError): pass
            TensionResponse(
                region_id="region_123",
                last_updated="2024-01-01T12:00:00Z"
            )


class TestTensionHistoryResponse: pass
    """Test TensionHistoryResponse schema validation."""

    def test_tension_history_response_valid(self): pass
        """Test valid tension history response creation."""
        data = {
            "region_id": "region_123",
            "faction_a": "faction_1",
            "faction_b": "faction_2",
            "current_tension": 45.0,
            "current_level": "tense",
            "history": [
                {
                    "timestamp": "2024-01-01T11:00:00Z",
                    "tension": 40.0,
                    "level": "tense",
                    "reason": "Border incident"
                }
            ]
        }
        
        response = TensionHistoryResponse(**data)
        
        assert response.region_id == "region_123"
        assert response.faction_a == "faction_1"
        assert response.faction_b == "faction_2"
        assert response.current_tension == 45.0
        assert len(response.history) == 1

    def test_tension_history_response_empty_history(self): pass
        """Test tension history response with empty history."""
        data = {
            "region_id": "region_123",
            "faction_a": "faction_1",
            "faction_b": "faction_2",
            "current_tension": 0.0,
            "current_level": "neutral",
            "history": []
        }
        
        response = TensionHistoryResponse(**data)
        
        assert response.history == []

    def test_tension_history_response_missing_fields(self): pass
        """Test tension history response with missing required fields."""
        # Missing faction_a
        with pytest.raises(ValidationError): pass
            TensionHistoryResponse(
                region_id="region_123",
                faction_b="faction_2",
                current_tension=45.0,
                current_level="tense",
                history=[]
            )


class TestTensionEventRequest: pass
    """Test TensionEventRequest schema validation."""

    def test_tension_event_request_valid(self): pass
        """Test valid tension event request creation."""
        data = {
            "region_id": "region_123",
            "event_type": "border_incident",
            "event_severity": 0.6,
            "affected_factions": [
                {"faction_a": "faction_1", "faction_b": "faction_2"},
                {"faction_a": "faction_1", "faction_b": "faction_3"}
            ],
            "reason": "Military skirmish at the border"
        }
        
        request = TensionEventRequest(**data)
        
        assert request.region_id == "region_123"
        assert request.event_type == "border_incident"
        assert request.event_severity == 0.6
        assert len(request.affected_factions) == 2
        assert request.reason == "Military skirmish at the border"

    def test_tension_event_request_without_reason(self): pass
        """Test tension event request without optional reason."""
        data = {
            "region_id": "region_123",
            "event_type": "border_incident",
            "event_severity": 0.6,
            "affected_factions": [
                {"faction_a": "faction_1", "faction_b": "faction_2"}
            ]
        }
        
        request = TensionEventRequest(**data)
        
        assert request.reason is None

    def test_tension_event_request_severity_boundaries(self): pass
        """Test tension event request with severity boundary values."""
        # Minimum valid severity
        data = {
            "region_id": "region_123",
            "event_type": "minor_incident",
            "event_severity": 0.0,
            "affected_factions": [
                {"faction_a": "faction_1", "faction_b": "faction_2"}
            ]
        }
        request = TensionEventRequest(**data)
        assert request.event_severity == 0.0
        
        # Maximum valid severity
        data["event_severity"] = 1.0
        request = TensionEventRequest(**data)
        assert request.event_severity == 1.0

    def test_tension_event_request_invalid_severity(self): pass
        """Test tension event request with invalid severity values."""
        # Severity too low
        data = {
            "region_id": "region_123",
            "event_type": "border_incident",
            "event_severity": -0.1,
            "affected_factions": [
                {"faction_a": "faction_1", "faction_b": "faction_2"}
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info: pass
            TensionEventRequest(**data)
        
        assert "event_severity" in str(exc_info.value)
        
        # Severity too high
        data["event_severity"] = 1.1
        
        with pytest.raises(ValidationError) as exc_info: pass
            TensionEventRequest(**data)
        
        assert "event_severity" in str(exc_info.value)

    def test_tension_event_request_missing_required_fields(self): pass
        """Test tension event request with missing required fields."""
        # Missing region_id
        with pytest.raises(ValidationError): pass
            TensionEventRequest(
                event_type="border_incident",
                event_severity=0.6,
                affected_factions=[
                    {"faction_a": "faction_1", "faction_b": "faction_2"}
                ]
            )
        
        # Missing event_type
        with pytest.raises(ValidationError): pass
            TensionEventRequest(
                region_id="region_123",
                event_severity=0.6,
                affected_factions=[
                    {"faction_a": "faction_1", "faction_b": "faction_2"}
                ]
            )
        
        # Missing affected_factions
        with pytest.raises(ValidationError): pass
            TensionEventRequest(
                region_id="region_123",
                event_type="border_incident",
                event_severity=0.6
            )

    def test_tension_event_request_empty_affected_factions(self): pass
        """Test tension event request with empty affected factions list."""
        data = {
            "region_id": "region_123",
            "event_type": "border_incident",
            "event_severity": 0.6,
            "affected_factions": []
        }
        
        request = TensionEventRequest(**data)
        
        assert request.affected_factions == []

    def test_tension_event_request_single_faction_pair(self): pass
        """Test tension event request with single faction pair."""
        data = {
            "region_id": "region_123",
            "event_type": "border_incident",
            "event_severity": 0.6,
            "affected_factions": [
                {"faction_a": "faction_1", "faction_b": "faction_2"}
            ]
        }
        
        request = TensionEventRequest(**data)
        
        assert len(request.affected_factions) == 1
        assert request.affected_factions[0]["faction_a"] == "faction_1"
        assert request.affected_factions[0]["faction_b"] == "faction_2"


class TestSchemaIntegration: pass
    """Test schema integration and real-world usage patterns."""

    def test_request_response_cycle(self): pass
        """Test creating a request, processing it, and returning a response."""
        # Create a tension modification request
        request_data = {
            "faction": {"faction_a": "empire", "faction_b": "rebels"},
            "value": 20.0,
            "reason": "Trade embargo imposed"
        }
        request = TensionRequest(**request_data)
        
        # Simulate processing and creating a response
        response_data = {
            "region_id": "central_province",
            "factions": {
                "empire_rebels": {
                    "tension": 45.0,  # Previous 25.0 + request 20.0
                    "level": "tense",
                    "last_updated": "2024-01-01T12:00:00Z"
                }
            },
            "last_updated": "2024-01-01T12:00:00Z"
        }
        response = TensionResponse(**response_data)
        
        assert request.value == 20.0
        assert response.factions["empire_rebels"].tension == 45.0

    def test_event_processing_workflow(self): pass
        """Test event request and history response workflow."""
        # Create an event request
        event_data = {
            "region_id": "border_region",
            "event_type": "military_exercise",
            "event_severity": 0.4,
            "affected_factions": [
                {"faction_a": "kingdom_a", "faction_b": "kingdom_b"},
                {"faction_a": "kingdom_a", "faction_b": "republic_c"}
            ],
            "reason": "Large-scale military exercises near borders"
        }
        event_request = TensionEventRequest(**event_data)
        
        # Create a history response showing the impact
        history_data = {
            "region_id": "border_region",
            "faction_a": "kingdom_a",
            "faction_b": "kingdom_b",
            "current_tension": 35.0,
            "current_level": "tense",
            "history": [
                {
                    "timestamp": "2024-01-01T12:00:00Z",
                    "tension": 35.0,
                    "level": "tense",
                    "reason": "Large-scale military exercises near borders"
                },
                {
                    "timestamp": "2024-01-01T11:00:00Z",
                    "tension": 25.0,
                    "level": "neutral",
                    "reason": "Previous state before exercises"
                }
            ]
        }
        history_response = TensionHistoryResponse(**history_data)
        
        assert event_request.event_severity == 0.4
        assert len(event_request.affected_factions) == 2
        assert history_response.current_tension == 35.0
        assert len(history_response.history) == 2

    def test_schema_serialization_deserialization(self): pass
        """Test full serialization and deserialization cycle."""
        # Create complex response data
        response_data = {
            "region_id": "contested_valley",
            "factions": {
                "north_alliance_south_coalition": {
                    "tension": 78.5,
                    "level": "hostile",
                    "last_updated": "2024-01-01T15:30:00Z",
                    "history": [
                        {
                            "timestamp": "2024-01-01T14:00:00Z",
                            "tension": 65.0,
                            "level": "tense",
                            "reason": "Border fortification"
                        }
                    ]
                }
            },
            "last_updated": "2024-01-01T15:30:00Z"
        }
        
        # Create response object
        response = TensionResponse(**response_data)
        
        # Serialize to dict
        serialized = response.dict()
        
        # Create new object from serialized data
        deserialized_response = TensionResponse(**serialized)
        
        # Verify data integrity
        assert response.region_id == deserialized_response.region_id
        assert response.factions.keys() == deserialized_response.factions.keys()
        faction_key = "north_alliance_south_coalition"
        assert response.factions[faction_key].tension == deserialized_response.factions[faction_key].tension
        assert len(response.factions[faction_key].history) == len(deserialized_response.factions[faction_key].history) 