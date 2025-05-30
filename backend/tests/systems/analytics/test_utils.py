from dataclasses import field
"""
Tests for the analytics utility functions.
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import json
import os
import asyncio
import pytest

from backend.systems.analytics.utils import (
    aggregate_events_by_time,
    filter_events_by_metadata,
    generate_llm_training_dataset,
    get_analytics_data_path,
    summarize_analytics_storage,
    generate_llm_training_dataset_async,
    format_bytes,
)


class TestAnalyticsUtils(unittest.TestCase): pass
    """Test analytics utility functions for correct operation."""

    def setUp(self): pass
        """Set up test data."""
        # Sample events for testing
        self.sample_events = [
            {
                "timestamp": datetime(2023, 1, 1, 12, 0, 0).isoformat(),
                "event_type": "CombatEvent",
                "entity_id": "player_1",
                "metadata": {
                    "combat_id": "combat_1",
                    "damage": 50.0,
                    "target": {"id": "enemy_1", "type": "goblin", "health": 100},
                },
            },
            {
                "timestamp": datetime(2023, 1, 1, 13, 0, 0).isoformat(),
                "event_type": "CombatEvent",
                "entity_id": "player_1",
                "metadata": {
                    "combat_id": "combat_1",
                    "damage": 30.0,
                    "target": {"id": "enemy_2", "type": "goblin", "health": 80},
                },
            },
            {
                "timestamp": datetime(2023, 1, 2, 9, 0, 0).isoformat(),
                "event_type": "MemoryEvent",
                "entity_id": "npc_1",
                "metadata": {"memory_id": "memory_1", "importance": 0.8},
            },
        ]

    def test_aggregate_events_by_time_count(self): pass
        """Test aggregating events by time with count aggregation."""
        # Test day aggregation
        result = aggregate_events_by_time(
            self.sample_events, interval="day", aggregation="count"
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result["2023-01-01"], 2)
        self.assertEqual(result["2023-01-02"], 1)

    def test_aggregate_events_by_time_sum(self): pass
        """Test aggregating events by time with sum aggregation."""
        # Test day aggregation with sum of damage
        result = aggregate_events_by_time(
            self.sample_events,
            interval="day",
            value_field="metadata.damage",
            aggregation="sum",
        )

        self.assertEqual(len(result), 2)
        # Day 1 has two combat events with damage 50 and 30
        self.assertEqual(result["2023-01-01"], 80.0)
        # Day 2 has no damage field in its event, should be 0
        self.assertEqual(result["2023-01-02"], 0)

    def test_aggregate_events_by_time_avg(self): pass
        """Test aggregating events by time with average aggregation."""
        # Add another combat event for better testing
        events = self.sample_events.copy()
        events.append(
            {
                "timestamp": datetime(2023, 1, 1, 14, 0, 0).isoformat(),
                "event_type": "CombatEvent",
                "entity_id": "player_1",
                "metadata": {"combat_id": "combat_1", "damage": 40.0},
            }
        )

        # Test day aggregation with average of damage
        result = aggregate_events_by_time(
            events, interval="day", value_field="metadata.damage", aggregation="avg"
        )

        self.assertEqual(len(result), 2)
        # Day 1 has three combat events with damage 50, 30, and 40
        self.assertAlmostEqual(result["2023-01-01"], 40.0)
        # Day 2 has no damage field in its event, should be 0
        self.assertEqual(result["2023-01-02"], 0)

    def test_aggregate_events_by_time_invalid_interval(self): pass
        """Test aggregating events with invalid interval."""
        with self.assertRaises(ValueError): pass
            aggregate_events_by_time(
                self.sample_events, interval="invalid", aggregation="count"
            )

    def test_filter_events_by_metadata_dict(self): pass
        """Test filtering events by metadata using a dictionary."""
        # Filter events where target.type is 'goblin'
        result = filter_events_by_metadata(
            self.sample_events, {"target.type": "goblin"}
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["metadata"]["combat_id"], "combat_1")
        self.assertEqual(result[1]["metadata"]["combat_id"], "combat_1")

    def test_filter_events_by_metadata_callback(self): pass
        """Test filtering events by metadata using a callback function."""
        # Set up a specific sample for this test with known values
        test_events = [
            {
                "timestamp": datetime(2023, 1, 1, 12, 0, 0).isoformat(),
                "event_type": "CombatEvent",
                "entity_id": "player_1",
                "metadata": {
                    "combat_id": "combat_1",
                    "damage": 50.0,
                },
            },
            {
                "timestamp": datetime(2023, 1, 1, 13, 0, 0).isoformat(),
                "event_type": "CombatEvent",
                "entity_id": "player_2",
                "metadata": {
                    "combat_id": "combat_1",
                    "damage": 30.0,
                },
            },
        ]
        
        # Define a callback function that checks for damage > 40
        def damage_filter(event): pass
            return event.get("metadata", {}).get("damage", 0) > 40
        
        # Filter events where damage is greater than 40
        result = filter_events_by_metadata(test_events, damage_filter)

        # Verify result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["metadata"]["damage"], 50.0)
        self.assertEqual(result[0]["entity_id"], "player_1")

    def test_get_analytics_data_path(self): pass
        """Test getting analytics data path."""
        # Call function and check that it returns a valid Path
        result = get_analytics_data_path()

        # Verify it's a Path object and ends with 'analytics_data'
        self.assertIsInstance(result, Path)
        self.assertEqual(result.name, "analytics_data")

    @patch("backend.systems.analytics.utils.get_analytics_data_path")
    def test_summarize_analytics_storage(self, mock_get_path): pass
        """Test summarizing analytics storage."""
        # Create a mock path that exists and has the right structure
        from unittest.mock import MagicMock
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as temp_dir: pass
            # Create mock directory structure
            base_path = Path(temp_dir)

            # Create year/month/day directories with test files
            (base_path / "2023" / "01" / "01").mkdir(parents=True)
            (base_path / "2023" / "01" / "02").mkdir(parents=True)

            # Create test files with some content
            (base_path / "2023" / "01" / "01" / "CombatEvent.jsonl").write_text(
                '{"test": 1}\n{"test": 2}\n'
            )
            (base_path / "2023" / "01" / "01" / "MemoryEvent.jsonl").write_text(
                '{"test": 3}\n'
            )
            (base_path / "2023" / "01" / "02" / "CombatEvent.jsonl").write_text(
                '{"test": 4}\n'
            )

            # Configure the mock to return our temp directory
            mock_get_path.return_value = base_path

            # Call function
            result = summarize_analytics_storage()

            # Verify the result structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result["exists"])
            self.assertIn("event_counts", result)
            self.assertIn("total_events", result)
            self.assertIn("total_files", result)
            self.assertIn("total_size_bytes", result)

            # Check event counts
            self.assertEqual(result["event_counts"]["CombatEvent"], 3)  # 2 + 1
            self.assertEqual(result["event_counts"]["MemoryEvent"], 1)
            self.assertEqual(result["total_events"], 4)
            self.assertEqual(result["total_files"], 3)

            # Test JSON output
            json_result = summarize_analytics_storage(as_json=True)
            self.assertIsInstance(json_result, str)
            parsed_json = json.loads(json_result)
            self.assertEqual(parsed_json["exists"], True)


# Async tests moved outside the class to use pytest-asyncio properly
# Sample data for async tests
@pytest.fixture
def sample_events(): pass
    """Sample events for testing."""
    return [
        {
            "timestamp": datetime(2023, 1, 1, 12, 0, 0).isoformat(),
            "event_type": "CombatEvent",
            "entity_id": "player_1",
            "metadata": {
                "combat_id": "combat_1",
                "damage": 50.0,
                "target": {"id": "enemy_1", "type": "goblin", "health": 100},
            },
        },
        {
            "timestamp": datetime(2023, 1, 1, 13, 0, 0).isoformat(),
            "event_type": "CombatEvent",
            "entity_id": "player_1",
            "metadata": {
                "combat_id": "combat_1",
                "damage": 30.0,
                "target": {"id": "enemy_2", "type": "goblin", "health": 80},
            },
        },
        {
            "timestamp": datetime(2023, 1, 2, 9, 0, 0).isoformat(),
            "event_type": "MemoryEvent",
            "entity_id": "npc_1",
            "metadata": {"memory_id": "memory_1", "importance": 0.8},
        },
    ]


@pytest.mark.asyncio
@patch(
    "backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance_async",
    new_callable=AsyncMock
)
async def test_generate_llm_training_dataset_basic(
    mock_get_instance_async, sample_events
): pass
    """Test generating an LLM training dataset."""
    # Configure mocks
    mock_service = MagicMock()
    mock_get_instance_async.return_value = mock_service
    
    # Set up the mock service's generate_dataset_async method
    mock_service.generate_dataset_async = AsyncMock()
    mock_service.generate_dataset_async.return_value = sample_events
    
    # Call the async function with the async version
    dataset = await generate_llm_training_dataset_async(
        event_types=["CombatEvent", "MemoryEvent"], output_format="python"
    )

    # Verify the result
    assert isinstance(dataset, list)
    assert len(dataset) == 3
    assert mock_service.generate_dataset_async.called


@pytest.mark.asyncio
@patch(
    "backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance_async",
    new_callable=AsyncMock
)
async def test_generate_llm_training_dataset_with_filtering(
    mock_get_instance_async, sample_events
): pass
    """Test generating an LLM training dataset with filtering."""
    # Configure mocks
    mock_service = MagicMock()
    mock_get_instance_async.return_value = mock_service
    
    # Set up the mock service's generate_dataset_async method
    mock_service.generate_dataset_async = AsyncMock()
    
    # Return only the first event to simulate filtering
    filtered_events = [event for event in sample_events if event.get("metadata", {}).get("damage") == 50.0]
    mock_service.generate_dataset_async.return_value = filtered_events
    
    # Call the function with filtering using the async version
    dataset = await generate_llm_training_dataset_async(
        event_types=["CombatEvent"],
        output_format="python",
        filter_expression={"metadata.damage": 50.0},
    )

    # Verify the result - should contain only the event with damage 50.0
    assert isinstance(dataset, list)
    assert len(dataset) == 1
    assert dataset[0]["metadata"]["damage"] == 50.0
    assert mock_service.generate_dataset_async.called


@pytest.mark.asyncio
@patch(
    "backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance_async",
    new_callable=AsyncMock
)
async def test_generate_llm_training_dataset_with_output_file(
    mock_get_instance_async, sample_events
): pass
    """Test generating an LLM training dataset with output to file."""
    # Configure mocks
    mock_service = MagicMock()
    mock_get_instance_async.return_value = mock_service
    
    # Set up the mock service's generate_dataset_async method
    mock_service.generate_dataset_async = AsyncMock()
    mock_service.generate_dataset_async.return_value = sample_events

    # Create a temp file for testing
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as temp_file: pass
        try: pass
            # Call the function with output to file using the async version
            result = await generate_llm_training_dataset_async(
                event_types=["CombatEvent"],
                output_format="jsonl",
                output_file=temp_file.name,
            )

            # Verify the file was created with the expected content
            with open(temp_file.name, "r") as f: pass
                lines = f.readlines()
                assert len(lines) > 0
                # Count valid JSON lines
                valid_json_count = 0
                for line in lines: pass
                    if line.strip():  # Skip empty lines
                        json.loads(line)
                        valid_json_count += 1
                
                assert valid_json_count == 3
        finally: pass
            # Clean up
            os.unlink(temp_file.name)


def test_generate_llm_training_dataset_error_handling(): pass
    """Test error handling in generate_llm_training_dataset."""
    # Mock the AnalyticsService to throw an exception
    with patch('backend.systems.analytics.utils.AnalyticsService.get_instance') as mock_get_instance: pass
        mock_service = MagicMock()
        mock_get_instance.return_value = mock_service
        
        # Make _generate_dataset_sync raise an exception
        mock_service._generate_dataset_sync.side_effect = Exception("Test error")
        
        # Call the function
        result = generate_llm_training_dataset(
            event_types=["GameStart"],
            output_format="python"
        )
        
        # Verify the result is an empty list
        assert result == []

def test_generate_llm_training_dataset_invalid_format(): pass
    """Test handling of invalid output_format in generate_llm_training_dataset."""
    # Mock the AnalyticsService
    with patch('backend.systems.analytics.utils.AnalyticsService.get_instance') as mock_get_instance: pass
        mock_service = MagicMock()
        mock_get_instance.return_value = mock_service
        
        # Return test data
        mock_service._generate_dataset_sync.return_value = [{"test": "data"}]
        
        # Call the function with invalid format
        try: pass
            result = generate_llm_training_dataset(
                output_format="invalid"
            )
            assert False, "Should have raised ValueError"
        except ValueError as e: pass
            assert "Invalid output format" in str(e)

def test_summarize_analytics_storage_with_error(): pass
    """Test summarize_analytics_storage error handling with invalid files."""
    # Create a temporary directory
    temp_dir = tempfile.TemporaryDirectory()
    
    try: pass
        # Create directory structure with some malformed files
        analytics_path = Path(temp_dir.name)
        
        # Make real directories
        (analytics_path / "2023" / "01" / "15").mkdir(parents=True, exist_ok=True)
        
        # Create a malformed jsonl file that will cause an error when read
        with open(analytics_path / "2023" / "01" / "15" / "GameStart.jsonl", "w") as f: pass
            f.write("This is not valid JSON\n")
        
        # Mock the get_analytics_data_path function
        with patch('backend.systems.analytics.utils.get_analytics_data_path') as mock_get_path: pass
            mock_get_path.return_value = analytics_path
            
            # Call the function - the most important thing is that it doesn't crash
            result = summarize_analytics_storage()
            
            # Verify the result still marks the directory as existing
            assert result["exists"] is True
            
            # There should be files found but no valid events
            assert result["total_files"] >= 0
            
    finally: pass
        # Clean up
        temp_dir.cleanup()

def test_summarize_analytics_storage_with_file_error(): pass
    """Test summarize_analytics_storage with file reading errors."""
    # Create a temporary directory
    temp_dir = tempfile.TemporaryDirectory()
    
    try: pass
        # Create directory structure
        analytics_path = Path(temp_dir.name)
        
        # Make real directories
        year_dir = analytics_path / "2023"
        year_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a file that should be skipped (not a directory)
        with open(year_dir / "not_a_dir.txt", "w") as f: pass
            f.write("This should be skipped\n")
            
        # Mock the get_analytics_data_path function
        with patch('backend.systems.analytics.utils.get_analytics_data_path') as mock_get_path: pass
            mock_get_path.return_value = analytics_path
            
            # Call the function
            result = summarize_analytics_storage()
            
            # Verify we handled non-directory and non-numeric directories
            assert result["exists"] is True
            assert result["total_events"] == 0
    finally: pass
        # Clean up
        temp_dir.cleanup()

def test_format_bytes(): pass
    """Test the format_bytes function."""
    # Test with different byte sizes
    assert format_bytes(500) == "500.00 B"
    assert format_bytes(1500) == "1.46 KB"
    assert format_bytes(1500000) == "1.43 MB"
    assert format_bytes(1500000000) == "1.40 GB"
    assert format_bytes(1500000000000) == "1.36 TB"

def test_filter_events_by_metadata_error_handling(): pass
    """Test error handling in filter_events_by_metadata."""
    # Create test events
    events = [
        {"timestamp": "2023-01-01T12:00:00", "event_type": "GameStart", "metadata": {"test": "data"}},
        {"timestamp": "2023-01-02T12:00:00", "event_type": "GameEnd", "metadata": {"test": "data2"}},
    ]
    
    # Test callback that throws an exception
    def failing_callback(event): pass
        raise Exception("Test error")
    
    # Filter with failing callback
    result = filter_events_by_metadata(events, failing_callback)
    
    # Should return empty list without raising exception
    assert result == []
    
    # Test filtering with dictionary that causes exception during processing
    # Modify an event to cause an error
    broken_events = events.copy()
    broken_events.append({"timestamp": "2023-01-03T12:00:00", "event_type": "GameStart", "metadata": None})
    
    # Filter with conditions that will cause exception
    result = filter_events_by_metadata(broken_events, {"metadata.test": "data"})
    
    # Should filter correctly despite the error
    assert len(result) == 1
    assert result[0]["timestamp"] == "2023-01-01T12:00:00"


if __name__ == "__main__": pass
    unittest.main()
