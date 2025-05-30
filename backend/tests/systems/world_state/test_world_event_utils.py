"""
Tests for backend.systems.world_state.utils.world_event_utils

Comprehensive tests for the world event utilities.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from datetime import datetime
import os

# Import the module being tested
try: pass
    from backend.systems.world_state.utils.world_event_utils import (
        log_world_event, roll_chaos_event, inject_chaos_event,
        trigger_chaos_if_needed, force_chaos, delete_world_event,
        annotate_world_event, create_world_event, link_events,
        get_related_events, filter_events_by_category, filter_events_by_location,
        format_event_description, NARRATIVE_CHAOS_TABLE, EVENTS_PATH
    )
    from backend.systems.world_state import StateCategory, WorldRegion
except ImportError as e: pass
    pytest.skip(f"Could not import backend.systems.world_state.utils.world_event_utils: {e}", allow_module_level=True)


class TestConstants: pass
    """Test module constants."""

    def test_narrative_chaos_table_exists(self): pass
        """Test that the narrative chaos table exists and has content."""
        assert isinstance(NARRATIVE_CHAOS_TABLE, list)
        assert len(NARRATIVE_CHAOS_TABLE) > 0
        assert all(isinstance(item, str) for item in NARRATIVE_CHAOS_TABLE)

    def test_narrative_chaos_table_content(self): pass
        """Test narrative chaos table has expected content."""
        # Check for some expected entries
        expected_entries = [
            "NPC betrays a faction or personal goal",
            "Player receives a divine omen",
            "Time skip or memory blackout (~5 minutes)"
        ]
        
        for expected in expected_entries: pass
            assert expected in NARRATIVE_CHAOS_TABLE

    def test_events_path_constant(self): pass
        """Test that EVENTS_PATH is properly defined."""
        assert isinstance(EVENTS_PATH, Path)
        assert str(EVENTS_PATH).endswith("events")


class TestLogWorldEvent: pass
    """Test log_world_event functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_events_path = None

    def teardown_method(self): pass
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    @patch('backend.systems.world_state.utils.world_event_utils.datetime')
    def test_log_world_event_basic(self, mock_datetime, mock_events_path): pass
        """Test basic world event logging."""
        # Setup mocks
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow().timestamp.return_value = 1672574400
        mock_datetime.utcnow().isoformat.return_value = "2023-01-01T12:00:00"
        
        event_data = {
            "summary": "Test event",
            "type": "test"
        }
        
        result = log_world_event(event_data)
        
        # Check returned data
        assert "event_id" in result
        assert result["event_id"] == "event_1672574400"
        assert result["timestamp"] == "2023-01-01T12:00:00"
        assert result["summary"] == "Test event"
        assert result["type"] == "test"
        assert result["players_present"] == []
        assert result["npcs_present"] == []
        assert result["severity"] == 1
        assert result["affected_systems"] == []

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    @patch('backend.systems.world_state.utils.world_event_utils.datetime')
    def test_log_world_event_with_all_data(self, mock_datetime, mock_events_path): pass
        """Test world event logging with all optional data."""
        # Setup mocks
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow().timestamp.return_value = 1672574400
        mock_datetime.utcnow().isoformat.return_value = "2023-01-01T12:00:00"
        
        event_data = {
            "summary": "Complex event",
            "type": "war",
            "players_present": ["player1", "player2"],
            "npcs_present": ["npc1"],
            "severity": 5,
            "affected_systems": ["diplomacy", "military"]
        }
        
        result = log_world_event(event_data)
        
        # Check that existing data is preserved
        assert result["players_present"] == ["player1", "player2"]
        assert result["npcs_present"] == ["npc1"]
        assert result["severity"] == 5
        assert result["affected_systems"] == ["diplomacy", "military"]

    @patch('backend.systems.world_state.utils.world_event_utils.logger')
    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    @patch('backend.systems.world_state.utils.world_event_utils.datetime')
    def test_log_world_event_logging(self, mock_datetime, mock_events_path, mock_logger): pass
        """Test that event logging creates log entries."""
        # Setup mocks
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow().timestamp.return_value = 1672574400
        mock_datetime.utcnow().isoformat.return_value = "2023-01-01T12:00:00"
        
        event_data = {"summary": "Test event"}
        
        log_world_event(event_data)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "World event logged" in call_args
        assert "event_1672574400" in call_args
        assert "Test event" in call_args


class TestChaosEvents: pass
    """Test chaos event functionality."""

    def test_roll_chaos_event(self): pass
        """Test chaos event rolling."""
        with patch('backend.systems.world_state.utils.world_event_utils.random.choice') as mock_choice: pass
            mock_choice.return_value = "Test chaos event"
            
            result = roll_chaos_event()
            
            assert result == "Test chaos event"
            mock_choice.assert_called_once_with(NARRATIVE_CHAOS_TABLE)

    def test_roll_chaos_event_randomness(self): pass
        """Test that chaos event rolling produces different results."""
        # Run multiple times to check randomness (should get different results)
        results = [roll_chaos_event() for _ in range(10)]
        
        # All results should be from the chaos table
        assert all(result in NARRATIVE_CHAOS_TABLE for result in results)
        
        # With 20 entries, getting all the same result in 10 tries is unlikely
        # This is probabilistic but should work most of the time
        assert len(set(results)) > 1

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    @patch('backend.systems.world_state.utils.world_event_utils.datetime')
    @patch('backend.systems.world_state.utils.world_event_utils.logger')
    def test_inject_chaos_event_basic(self, mock_logger, mock_datetime, mock_events_path): pass
        """Test basic chaos event injection."""
        # Setup mocks
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow().timestamp.return_value = 1672574400
        mock_datetime.utcnow().isoformat.return_value = "2023-01-01T12:00:00"
        
        self.temp_dir = tempfile.mkdtemp()
        
        try: pass
            result = inject_chaos_event("Test chaos")
            
            assert result["event_id"] == "chaos_1672574400"
            assert result["summary"] == "[CHAOS EVENT] Test chaos"
            assert result["type"] == "narrative_chaos"
            assert result["timestamp"] == "2023-01-01T12:00:00"
            assert result["context"] == {}
            
            mock_logger.info.assert_called_once()
        finally: pass
            shutil.rmtree(self.temp_dir)

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    @patch('backend.systems.world_state.utils.world_event_utils.datetime')
    def test_inject_chaos_event_with_context(self, mock_datetime, mock_events_path): pass
        """Test chaos event injection with context."""
        # Setup mocks
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow().timestamp.return_value = 1672574400
        mock_datetime.utcnow().isoformat.return_value = "2023-01-01T12:00:00"
        
        self.temp_dir = tempfile.mkdtemp()
        
        try: pass
            context = {"npc_id": "npc123", "severity": 3}
            result = inject_chaos_event("Test chaos", region="test_region", context=context)
            
            assert result["context"] == context
        finally: pass
            shutil.rmtree(self.temp_dir)

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    @patch('backend.systems.world_state.utils.world_event_utils.datetime')
    def test_inject_chaos_event_with_region_sync_success(self, mock_datetime, mock_events_path): pass
        """Test chaos event injection with successful region sync."""
        # Setup mocks
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow().timestamp.return_value = 1672574400
        mock_datetime.utcnow().isoformat.return_value = "2023-01-01T12:00:00"
        
        self.temp_dir = tempfile.mkdtemp()
        
        try: pass
            with patch('app.npc.npc_rumor_utils.sync_event_beliefs') as mock_sync: pass
                result = inject_chaos_event("Test chaos", region="test_region")
                
                assert result["event_id"] == "chaos_1672574400"
                mock_sync.assert_called_once_with("test_region", result)
        finally: pass
            shutil.rmtree(self.temp_dir)

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    @patch('backend.systems.world_state.utils.world_event_utils.datetime')
    @patch('backend.systems.world_state.utils.world_event_utils.logger')
    def test_inject_chaos_event_with_region_sync_failure(self, mock_logger, mock_datetime, mock_events_path): pass
        """Test chaos event injection with failed region sync."""
        # Setup mocks
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow().timestamp.return_value = 1672574400
        mock_datetime.utcnow().isoformat.return_value = "2023-01-01T12:00:00"
        
        self.temp_dir = tempfile.mkdtemp()
        
        try: pass
            # Mock import failure
            with patch('builtins.__import__', side_effect=ImportError("Module not found")): pass
                result = inject_chaos_event("Test chaos", region="test_region")
                
                assert result["event_id"] == "chaos_1672574400"
                mock_logger.warning.assert_called_once()
                assert "Could not import sync_event_beliefs" in mock_logger.warning.call_args[0][0]
        finally: pass
            shutil.rmtree(self.temp_dir)


class TestChaosTriggering: pass
    """Test chaos triggering functionality."""

    def test_trigger_chaos_if_needed_no_threshold(self): pass
        """Test chaos triggering when threshold is not met."""
        with patch('backend.systems.motif.get_motif_manager') as mock_get_manager: pass
            with patch('backend.systems.motif.utils.check_chaos_threshold') as mock_check: pass
                mock_check.return_value = None
                
                result = trigger_chaos_if_needed("npc123")
                
                assert result == {"message": "No chaos triggered"}
                mock_check.assert_called_once_with("npc123")

    @patch('backend.systems.world_state.utils.world_event_utils.roll_chaos_event')
    @patch('backend.systems.world_state.utils.world_event_utils.inject_chaos_event')
    def test_trigger_chaos_if_needed_with_threshold(self, mock_inject, mock_roll): pass
        """Test chaos triggering when threshold is met."""
        with patch('backend.systems.motif.get_motif_manager') as mock_get_manager: pass
            with patch('backend.systems.motif.utils.check_chaos_threshold') as mock_check: pass
                mock_check.return_value = {"type": "high_tension", "value": 0.8}
                mock_roll.return_value = "NPC betrays a faction"
                mock_inject.return_value = {"event_id": "test_event"}
                
                result = trigger_chaos_if_needed("npc123", region="test_region")
                
                assert result["chaos_triggered"] == True
                assert result["event"] == {"event_id": "test_event"}
                mock_roll.assert_called_once()
                mock_inject.assert_called_once_with(
                    "NPC betrays a faction",
                    "test_region",
                    context={"npc_id": "npc123", "threshold": {"type": "high_tension", "value": 0.8}}
                )

    @patch('backend.systems.world_state.utils.world_event_utils.logger')
    def test_trigger_chaos_if_needed_import_error(self, mock_logger): pass
        """Test chaos triggering with import error."""
        with patch('builtins.__import__', side_effect=ImportError("Module not found")): pass
            result = trigger_chaos_if_needed("npc123")
            
            assert result == {"error": "Motif system not available"}
            mock_logger.warning.assert_called_once()
            assert "Consolidated motif system not available" in mock_logger.warning.call_args[0][0]

    @patch('backend.systems.world_state.utils.world_event_utils.inject_chaos_event')
    def test_force_chaos_success(self, mock_inject): pass
        """Test forcing chaos event."""
        with patch('backend.systems.motif.get_motif_manager') as mock_get_manager: pass
            with patch('backend.systems.motif.utils.roll_chaos_event') as mock_roll: pass
                mock_roll.return_value = "Divine intervention"
                mock_inject.return_value = {"event_id": "forced_event"}
                
                result = force_chaos("npc123", region="test_region")
                
                assert result == {"event": {"event_id": "forced_event"}}
                mock_inject.assert_called_once_with(
                    "Divine intervention",
                    "test_region",
                    context={"npc_id": "npc123", "forced": True}
                )

    @patch('backend.systems.world_state.utils.world_event_utils.logger')
    def test_force_chaos_import_error(self, mock_logger): pass
        """Test forcing chaos with import error."""
        with patch('builtins.__import__', side_effect=ImportError("Module not found")): pass
            result = force_chaos("npc123")
            
            assert result == {"error": "Motif system not available"}
            mock_logger.warning.assert_called_once()


class TestEventManagement: pass
    """Test event management functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self): pass
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    def test_delete_world_event_success(self, mock_events_path): pass
        """Test successful event deletion."""
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        
        # Create a test event file
        event_file = Path(self.temp_dir) / "test_event.json"
        event_file.write_text('{"event_id": "test_event"}')
        
        result = delete_world_event("test_event")
        
        assert result == True
        assert not event_file.exists()

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    @patch('backend.systems.world_state.utils.world_event_utils.logger')
    def test_delete_world_event_not_found(self, mock_logger, mock_events_path): pass
        """Test event deletion when file doesn't exist."""
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        
        result = delete_world_event("nonexistent_event")
        
        assert result == False
        mock_logger.error.assert_called_once()

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    def test_annotate_world_event_success(self, mock_events_path): pass
        """Test successful event annotation."""
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        
        # Create a test event file
        event_file = Path(self.temp_dir) / "test_event.json"
        original_data = {"event_id": "test_event", "summary": "Test"}
        event_file.write_text(json.dumps(original_data))
        
        result = annotate_world_event("test_event", "This is an annotation")
        
        assert result == True
        
        # Check that annotation was added
        updated_data = json.loads(event_file.read_text())
        assert "annotations" in updated_data
        assert len(updated_data["annotations"]) == 1
        assert updated_data["annotations"][0]["text"] == "This is an annotation"
        assert "timestamp" in updated_data["annotations"][0]

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    @patch('backend.systems.world_state.utils.world_event_utils.logger')
    def test_annotate_world_event_not_found(self, mock_logger, mock_events_path): pass
        """Test event annotation when file doesn't exist."""
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        
        result = annotate_world_event("nonexistent_event", "annotation")
        
        assert result == False
        mock_logger.error.assert_called_once()

    @patch('backend.systems.world_state.utils.world_event_utils.datetime')
    def test_create_world_event_basic(self, mock_datetime): pass
        """Test basic world event creation."""
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow().isoformat.return_value = "2023-01-01T12:00:00"
        
        with patch('backend.systems.world_state.utils.world_event_utils.log_world_event') as mock_log: pass
            mock_log.return_value = {"event_id": "created_event"}
            
            result = create_world_event("test_type", "Test description")
            
            assert result == {"event_id": "created_event"}
            
            # Check that log_world_event was called with correct data
            call_args = mock_log.call_args[0][0]
            assert call_args["type"] == "test_type"
            assert call_args["description"] == "Test description"
            assert call_args["timestamp"] == "2023-01-01T12:00:00"

    @patch('backend.systems.world_state.utils.world_event_utils.datetime')
    def test_create_world_event_with_all_params(self, mock_datetime): pass
        """Test world event creation with all parameters."""
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow().isoformat.return_value = "2023-01-01T12:00:00"
        
        with patch('backend.systems.world_state.utils.world_event_utils.log_world_event') as mock_log: pass
            mock_log.return_value = {"event_id": "created_event"}
            
            result = create_world_event(
                event_type="war",
                description="Major battle",
                location="test_location",
                category=StateCategory.MILITARY,
                region=WorldRegion.NORTH,
                entity_id="entity123",
                related_events=["event1", "event2"],
                metadata={"severity": 5}
            )
            
            call_args = mock_log.call_args[0][0]
            assert call_args["location"] == "test_location"
            assert call_args["category"] == StateCategory.MILITARY
            assert call_args["region"] == WorldRegion.NORTH
            assert call_args["entity_id"] == "entity123"
            assert call_args["related_events"] == ["event1", "event2"]
            assert call_args["metadata"] == {"severity": 5}


class TestEventLinking: pass
    """Test event linking functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self): pass
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    def test_link_events_success(self, mock_events_path): pass
        """Test successful event linking."""
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        
        # Create test event files
        source_file = Path(self.temp_dir) / "source_event.json"
        target_file = Path(self.temp_dir) / "target_event.json"
        
        source_data = {"event_id": "source_event", "related_events": []}
        target_data = {"event_id": "target_event", "related_events": []}
        
        source_file.write_text(json.dumps(source_data))
        target_file.write_text(json.dumps(target_data))
        
        result = link_events("source_event", "target_event", "causes")
        
        assert result == True
        
        # Check that links were created
        updated_source = json.loads(source_file.read_text())
        updated_target = json.loads(target_file.read_text())
        
        assert len(updated_source["related_events"]) == 1
        assert updated_source["related_events"][0]["target_id"] == "target_event"
        assert updated_source["related_events"][0]["relationship"] == "causes"
        
        assert len(updated_target["related_events"]) == 1
        assert updated_target["related_events"][0]["target_id"] == "source_event"
        assert updated_target["related_events"][0]["relationship"] == "caused_by"

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    @patch('backend.systems.world_state.utils.world_event_utils.logger')
    def test_link_events_source_not_found(self, mock_logger, mock_events_path): pass
        """Test event linking when source event doesn't exist."""
        mock_events_path.__truediv__ = lambda self, other: Path(self.temp_dir) / other
        
        result = link_events("nonexistent_source", "target_event")
        
        assert result == False
        mock_logger.error.assert_called()


class TestEventFiltering: pass
    """Test event filtering functionality."""

    def setup_method(self): pass
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self): pass
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    def test_filter_events_by_category(self, mock_events_path): pass
        """Test filtering events by category."""
        mock_events_path.glob = lambda pattern: [
            Path(self.temp_dir) / "event1.json",
            Path(self.temp_dir) / "event2.json",
            Path(self.temp_dir) / "event3.json"
        ]
        
        # Create test event files
        event1 = {"event_id": "event1", "category": "military"}
        event2 = {"event_id": "event2", "category": "diplomatic"}
        event3 = {"event_id": "event3", "category": "military"}
        
        (Path(self.temp_dir) / "event1.json").write_text(json.dumps(event1))
        (Path(self.temp_dir) / "event2.json").write_text(json.dumps(event2))
        (Path(self.temp_dir) / "event3.json").write_text(json.dumps(event3))
        
        result = filter_events_by_category("military")
        
        assert len(result) == 2
        assert all(event["category"] == "military" for event in result)

    @patch('backend.systems.world_state.utils.world_event_utils.EVENTS_PATH')
    def test_filter_events_by_location(self, mock_events_path): pass
        """Test filtering events by location."""
        mock_events_path.glob = lambda pattern: [
            Path(self.temp_dir) / "event1.json",
            Path(self.temp_dir) / "event2.json"
        ]
        
        # Create test event files
        event1 = {"event_id": "event1", "location": "city_a"}
        event2 = {"event_id": "event2", "location": "city_b"}
        
        (Path(self.temp_dir) / "event1.json").write_text(json.dumps(event1))
        (Path(self.temp_dir) / "event2.json").write_text(json.dumps(event2))
        
        result = filter_events_by_location("city_a")
        
        assert len(result) == 1
        assert result[0]["location"] == "city_a"


class TestEventFormatting: pass
    """Test event formatting functionality."""

    def test_format_event_description_basic(self): pass
        """Test basic event description formatting."""
        event = {
            "event_id": "test_event",
            "type": "battle",
            "description": "A great battle occurred",
            "timestamp": "2023-01-01T12:00:00"
        }
        
        result = format_event_description(event)
        
        assert "test_event" in result
        assert "battle" in result
        assert "A great battle occurred" in result
        assert "2023-01-01T12:00:00" in result

    def test_format_event_description_with_metadata(self): pass
        """Test event description formatting with metadata."""
        event = {
            "event_id": "test_event",
            "type": "battle",
            "description": "A great battle occurred",
            "timestamp": "2023-01-01T12:00:00",
            "location": "Test City",
            "severity": 5,
            "participants": ["army1", "army2"]
        }
        
        result = format_event_description(event, include_metadata=True)
        
        assert "test_event" in result
        assert "Test City" in result
        assert "5" in result
        assert "army1" in result

    def test_format_event_description_missing_fields(self): pass
        """Test event description formatting with missing fields."""
        event = {
            "event_id": "test_event"
        }
        
        result = format_event_description(event)
        
        # Should not crash and should include available information
        assert "test_event" in result


def test_module_imports(): pass
    """Test that the module can be imported without errors."""
    from backend.systems.world_state.utils.world_event_utils import log_world_event
    assert log_world_event is not None
