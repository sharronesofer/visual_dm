from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.models import DiplomaticStatus
from typing import Type
"""
Unit tests for the Diplomacy System repository.

Tests the data persistence layer in backend/systems/diplomacy/repository.py
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open, MagicMock
from uuid import UUID, uuid4

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
from backend.systems.diplomacy.repository import DiplomacyRepository


class TestDiplomacyRepository: pass
    """Tests for the DiplomacyRepository class."""

    def setup_method(self): pass
        """Setup for each test."""
        # Use a test data directory
        self.test_data_dir = "/tmp/diplomacy_test_data"
        os.makedirs(self.test_data_dir, exist_ok=True)

        # Create repository with test directory
        self.repository = DiplomacyRepository(data_dir=self.test_data_dir)

        # Common test data
        self.faction_a_id = uuid4()
        self.faction_b_id = uuid4()

    def teardown_method(self): pass
        """Cleanup after each test."""
        # Clean up test files
        for filename in os.listdir(self.test_data_dir): pass
            if filename.startswith("test_"): pass
                os.remove(os.path.join(self.test_data_dir, filename))

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("json.load")
    def test_get_faction_relationship_existing(
        self, mock_json_load, mock_exists, mock_file
    ): pass
        """Test getting an existing faction relationship."""
        # Setup mocks
        mock_exists.return_value = True
        expected_relationship = {
            "faction_a_id": str(self.faction_a_id),
            "faction_b_id": str(self.faction_b_id),
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 0,
            "last_updated": datetime.utcnow().isoformat(),
        }
        mock_json_load.return_value = expected_relationship

        # Call repository
        result = self.repository.get_faction_relationship(
            self.faction_a_id, self.faction_b_id
        )

        # The repository sorts faction IDs by string value to ensure consistent ordering
        # So we need to determine the expected order
        if str(self.faction_a_id) > str(self.faction_b_id): pass
            expected_path = f"{self.test_data_dir}/relationships/faction_{self.faction_b_id}_{self.faction_a_id}.json"
        else: pass
            expected_path = f"{self.test_data_dir}/relationships/faction_{self.faction_a_id}_{self.faction_b_id}.json"
        
        mock_exists.assert_called_with(expected_path)

        # Verify result has expected fields (converted to string format)
        assert result["faction_a_id"] == str(self.faction_a_id) or result["faction_a_id"] == str(self.faction_b_id)
        assert result["faction_b_id"] == str(self.faction_b_id) or result["faction_b_id"] == str(self.faction_a_id)
        assert result["status"] == DiplomaticStatus.NEUTRAL.value
        assert result["tension"] == 0
        assert "last_updated" in result

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("json.dump")
    def test_get_faction_relationship_new(
        self, mock_json_dump, mock_makedirs, mock_exists, mock_file
    ): pass
        """Test getting a new faction relationship that doesn't exist yet."""
        # Setup mocks - file doesn't exist
        mock_exists.return_value = False

        # Call repository
        result = self.repository.get_faction_relationship(
            self.faction_a_id, self.faction_b_id
        )

        # Verify directory creation
        mock_makedirs.assert_called()

        # Verify file was created with defaults
        mock_json_dump.assert_called()

        # Verify default fields (repository returns string UUIDs)
        assert result["faction_a_id"] == str(self.faction_a_id) or result["faction_a_id"] == str(self.faction_b_id)
        assert result["faction_b_id"] == str(self.faction_b_id) or result["faction_b_id"] == str(self.faction_a_id)
        assert result["status"] == DiplomaticStatus.NEUTRAL.value
        assert result["tension"] == 0
        assert "last_updated" in result

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("json.load")
    @patch("json.dump")
    def test_update_faction_relationship(
        self, mock_json_dump, mock_json_load, mock_exists, mock_file
    ): pass
        """Test updating a faction relationship."""
        # Setup mocks
        mock_exists.return_value = True
        initial_relationship = {
            "faction_a_id": str(self.faction_a_id),
            "faction_b_id": str(self.faction_b_id),
            "status": DiplomaticStatus.NEUTRAL.value,
            "tension": 0,
            "last_updated": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        }
        mock_json_load.return_value = initial_relationship

        # Call repository to update
        updates = {"tension": 25, "status": DiplomaticStatus.TENSE}
        result = self.repository.update_faction_relationship(
            self.faction_a_id, self.faction_b_id, updates=updates
        )

        # Verify json.dump was called
        mock_json_dump.assert_called()

        # Verify result contains updates
        assert result["tension"] == 25
        assert result["status"] == DiplomaticStatus.TENSE.value  # Repository stores enum values
        assert "last_updated" in result

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("json.dump")
    def test_create_treaty(self, mock_json_dump, mock_makedirs, mock_exists, mock_file): pass
        """Test creating a treaty."""
        # Setup mocks - directories don't exist
        mock_exists.return_value = False

        # Create a treaty
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        treaty = Treaty(
            name="Test Alliance",
            type=TreatyType.ALLIANCE,
            parties=[self.faction_a_id, self.faction_b_id],
            terms={"mutual_defense": True},
            start_date=start_date,
            end_date=end_date,
        )

        # Call repository
        result = self.repository.create_treaty(treaty)

        # Verify directory creation
        mock_makedirs.assert_called()

        # Verify file was written (repository uses model_dump_json now, not json.dump)
        mock_json_dump.assert_called()

        # Verify result
        assert result.id is not None  # Should have assigned ID
        assert result.name == treaty.name
        assert result.type == treaty.type
        assert set(result.parties) == set(treaty.parties)
        assert result.terms == treaty.terms
        assert result.start_date == treaty.start_date
        assert result.end_date == treaty.end_date

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_get_treaty(self, mock_exists, mock_file): pass
        """Test getting a treaty."""
        # Setup mocks
        treaty_id = uuid4()
        mock_exists.return_value = True
        
        # Create valid mock data with proper UUID
        valid_treaty_data = {
            "id": str(treaty_id),
            "name": "Test Treaty",
            "type": "alliance",
            "parties": [str(self.faction_a_id), str(self.faction_b_id)],
            "terms": {"mutual_defense": True},
            "start_date": "2023-01-01T00:00:00",
            "end_date": "2023-02-01T00:00:00",
            "is_active": True,
            "is_public": True,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        # Configure mock to return valid JSON
        mock_file.return_value.read.return_value = json.dumps(valid_treaty_data)

        # Call repository
        result = self.repository.get_treaty(treaty_id)

        # Verify correct path
        expected_path = f"{self.test_data_dir}/treaties/{treaty_id}.json"
        mock_exists.assert_called_with(expected_path)

        # Verify result
        assert result is not None
        assert result.id == treaty_id
        assert result.name == "Test Treaty"

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_negotiation(
        self, mock_makedirs, mock_exists, mock_file
    ): pass
        """Test creating a negotiation."""
        # Setup mocks
        mock_exists.return_value = False

        # Create a negotiation (the repository will assign its own ID)
        negotiation = Negotiation(
            title="Trade Negotiation",
            parties=[self.faction_a_id, self.faction_b_id],
            initiator_id=self.faction_a_id,
            recipient_id=self.faction_b_id,
            status=NegotiationStatus.PENDING,
            treaty_type=TreatyType.TRADE,
        )

        # Call repository
        result = self.repository.create_negotiation(negotiation)

        # Verify directory creation
        mock_makedirs.assert_called()

        # Verify file was written (repository uses model_dump_json now)
        mock_file.assert_called()

        # Verify result has an assigned ID (repository assigns its own)
        assert result.id is not None
        assert set(result.parties) == set(negotiation.parties)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_update_negotiation(
        self, mock_exists, mock_file
    ): pass
        """Test updating a negotiation."""
        # Setup mocks
        negotiation_id = uuid4()
        mock_exists.return_value = True
        
        # Create valid mock data with proper UUID
        valid_negotiation_data = {
            "id": str(negotiation_id),
            "title": "Test Negotiation",
            "parties": [str(self.faction_a_id), str(self.faction_b_id)],
            "initiator_id": str(self.faction_a_id),
            "recipient_id": str(self.faction_b_id),
            "status": "pending",
            "offers": [],
            "treaty_type": "trade",
            "start_date": "2023-01-01T00:00:00",
            "metadata": {},
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        # Configure mock to return valid JSON
        mock_file.return_value.read.return_value = json.dumps(valid_negotiation_data)

        # Call repository to update (use ACCEPTED instead of COMPLETED)
        updates = {"status": NegotiationStatus.ACCEPTED}
        result = self.repository.update_negotiation(negotiation_id, updates)

        # Verify file operations
        mock_file.assert_called()

        # Verify result is not None
        assert result is not None

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_violation(
        self, mock_makedirs, mock_exists, mock_file
    ): pass
        """Test creating a treaty violation."""
        # Setup mocks
        mock_exists.return_value = False

        # Create a violation (the repository will assign its own ID)
        violation = TreatyViolation(
            treaty_id=uuid4(),
            violator_id=self.faction_a_id,
            violation_type=TreatyViolationType.MILITARY_BUILDUP,
            description="Exceeded troop limits",
            evidence={"observed_troops": 5000, "limit": 3000},
            reported_by=self.faction_b_id,
            severity=70,
        )

        # Call repository
        result = self.repository.create_violation(violation)

        # Verify directory creation
        mock_makedirs.assert_called()

        # Verify file was written (repository uses model_dump_json now)
        mock_file.assert_called()

        # Verify result has an assigned ID (repository assigns its own)
        assert result.id is not None
        assert result.violator_id == violation.violator_id

    @patch("uuid.uuid4")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_event(
        self, mock_makedirs, mock_exists, mock_file, mock_uuid
    ): pass
        """Test creating a diplomatic event."""
        # Setup mocks
        event_id = uuid4()
        mock_uuid.return_value = event_id
        mock_exists.return_value = False

        # Create an event
        event = DiplomaticEvent(
            id=event_id,
            event_type=DiplomaticEventType.TREATY,
            factions=[self.faction_a_id, self.faction_b_id],
            description="Treaty signed",
            severity=50,
            public=True,
        )

        # Call repository
        result = self.repository.create_event(event)

        # Verify directory creation
        mock_makedirs.assert_called()

        # Verify file was written (repository uses model_dump_json now)
        mock_file.assert_called()

        # Verify result
        assert result.id == event_id
        assert result.event_type == event.event_type
