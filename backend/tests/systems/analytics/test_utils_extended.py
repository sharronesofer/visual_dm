"""
Extended tests for the analytics utility functions to improve coverage.
"""

import pytest
import tempfile
import shutil
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, mock_open
from unittest.mock import AsyncMock

from backend.systems.analytics.utils import (
    aggregate_events_by_time,
    filter_events_by_metadata,
    generate_llm_training_dataset,
    generate_llm_training_dataset_async,
    get_analytics_data_path,
    summarize_analytics_storage,
)


class TestAnalyticsUtilsExtended: pass
    """Extended tests for the analytics utility functions."""

    def test_aggregate_events_by_time_invalid_aggregation(self): pass
        """Test aggregate_events_by_time with invalid aggregation type."""
        # Sample events
        events = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity1",
                "metadata": {"value": 10},
            },
            {
                "timestamp": "2023-01-01T13:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity2",
                "metadata": {"value": 20},
            },
        ]
        
        # Test with invalid aggregation type
        with pytest.raises(ValueError): pass
            aggregate_events_by_time(
                events,
                interval="day",
                value_field="metadata.value",
                aggregation="invalid",
            )
    
    def test_aggregate_events_by_time_with_count(self): pass
        """Test aggregate_events_by_time with count aggregation."""
        # Sample events across multiple days
        events = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity1",
            },
            {
                "timestamp": "2023-01-01T13:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity2",
            },
            {
                "timestamp": "2023-01-02T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity3",
            },
        ]
        
        # Test with day interval
        result = aggregate_events_by_time(events, interval="day")
        
        # Should have two entries, one for each day
        assert len(result) == 2
        assert result["2023-01-01"] == 2  # Two events on Jan 1
        assert result["2023-01-02"] == 1  # One event on Jan 2
        
        # Test with hour interval
        result = aggregate_events_by_time(events, interval="hour")
        
        # Should have three entries, one for each hour
        assert len(result) == 3
        assert "2023-01-01T12" in result
        assert result["2023-01-01T12"] == 1
        assert "2023-01-01T13" in result
        assert result["2023-01-01T13"] == 1
        assert "2023-01-02T12" in result
        assert result["2023-01-02T12"] == 1
    
    def test_aggregate_events_by_time_with_sum(self): pass
        """Test aggregate_events_by_time with sum aggregation."""
        # Sample events
        events = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity1",
                "metadata": {"value": 10},
            },
            {
                "timestamp": "2023-01-01T13:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity2",
                "metadata": {"value": 20},
            },
            {
                "timestamp": "2023-01-02T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity3",
                "metadata": {"value": 30},
            },
        ]
        
        # Test with day interval and sum aggregation
        result = aggregate_events_by_time(
            events,
            interval="day",
            value_field="metadata.value",
            aggregation="sum",
        )
        
        # Should have two entries, summing values for each day
        assert len(result) == 2
        assert result["2023-01-01"] == 30  # Sum of 10 + 20
        assert result["2023-01-02"] == 30  # Just 30
    
    def test_aggregate_events_by_time_with_avg(self): pass
        """Test aggregate_events_by_time with avg aggregation."""
        # Sample events
        events = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity1",
                "metadata": {"value": 10},
            },
            {
                "timestamp": "2023-01-01T13:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity2",
                "metadata": {"value": 20},
            },
            {
                "timestamp": "2023-01-02T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity3",
                "metadata": {"value": 30},
            },
        ]
        
        # Test with day interval and avg aggregation
        result = aggregate_events_by_time(
            events,
            interval="day",
            value_field="metadata.value",
            aggregation="avg",
        )
        
        # Should have two entries, averaging values for each day
        assert len(result) == 2
        assert result["2023-01-01"] == 15  # Average of 10 and 20
        assert result["2023-01-02"] == 30  # Just 30
    
    def test_filter_events_by_metadata_with_dict(self): pass
        """Test filter_events_by_metadata with dictionary filter."""
        # Sample events
        events = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity1",
                "metadata": {"category": "test", "action": "action1", "nested": {"value": 10}},
            },
            {
                "timestamp": "2023-01-01T13:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity2",
                "metadata": {"category": "test", "action": "action2", "nested": {"value": 20}},
            },
            {
                "timestamp": "2023-01-02T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity3",
                "metadata": {"category": "other", "action": "action1", "nested": {"value": 30}},
            },
        ]
        
        # Test with simple filter
        result = filter_events_by_metadata(events, {"category": "test"})
        
        # Should have two events with category "test"
        assert len(result) == 2
        assert all(e["metadata"]["category"] == "test" for e in result)
        
        # Test with multiple conditions
        result = filter_events_by_metadata(
            events,
            {"category": "test", "action": "action1"},
        )
        
        # Should have one event matching both conditions
        assert len(result) == 1
        assert result[0]["entity_id"] == "entity1"
        
        # Test with nested path
        result = filter_events_by_metadata(events, {"nested.value": 20})
        
        # Should have one event with nested value 20
        assert len(result) == 1
        assert result[0]["entity_id"] == "entity2"
        
        # Test with non-existent path (should match nothing)
        result = filter_events_by_metadata(events, {"non_existent": "value"})
        assert len(result) == 0
    
    def test_filter_events_by_metadata_with_callback(self): pass
        """Test filter_events_by_metadata with callback function."""
        # Sample events
        events = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity1",
                "metadata": {"value": 10},
            },
            {
                "timestamp": "2023-01-01T13:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity2",
                "metadata": {"value": 20},
            },
            {
                "timestamp": "2023-01-02T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity3",
                "metadata": {"value": 30},
            },
        ]
        
        # Test with callback function
        result = filter_events_by_metadata(
            events,
            lambda metadata: metadata.get("value", 0) > 15,
        )
        
        # Should have two events with value > 15
        assert len(result) == 2
        assert all(e["metadata"]["value"] > 15 for e in result)
    
    @pytest.mark.asyncio
    async def test_generate_llm_training_dataset_basic(self): pass
        """Test generate_llm_training_dataset with basic functionality."""
        # Mock the generate_dataset_async method
        with patch("backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance_async") as mock_get_instance: pass
            mock_service = MagicMock()
            mock_get_instance.return_value = mock_service
            
            # Create an AsyncMock for generate_dataset_async
            mock_service.generate_dataset_async = AsyncMock()
            
            # Set up mock to return test data
            mock_service.generate_dataset_async.return_value = [
                {
                    "timestamp": "2023-01-01T12:00:00",
                    "event_type": "TestEvent",
                    "entity_id": "entity1",
                    "metadata": {"value": 10},
                },
                {
                    "timestamp": "2023-01-01T13:00:00",
                    "event_type": "TestEvent",
                    "entity_id": "entity2",
                    "metadata": {"value": 20},
                },
            ]
            
            # Call function
            result = await generate_llm_training_dataset_async(output_format="python")
            
            # Verify result
            assert len(result) == 2
            assert result[0]["metadata"]["value"] == 10
            assert result[1]["metadata"]["value"] == 20

    @pytest.mark.asyncio
    async def test_generate_llm_training_dataset_with_filtering(self): pass
        """Test generate_llm_training_dataset with filtering."""
        # Mock the generate_dataset_async method
        with patch("backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance_async") as mock_get_instance: pass
            mock_service = MagicMock()
            mock_get_instance.return_value = mock_service
            
            # Create an AsyncMock for generate_dataset_async
            mock_service.generate_dataset_async = AsyncMock()
            
            # Set up mock to return test data
            mock_service.generate_dataset_async.return_value = [
                {
                    "timestamp": "2023-01-01T12:00:00",
                    "event_type": "TestEvent",
                    "entity_id": "entity1",
                    "metadata": {"category": "test", "value": 10},
                },
                {
                    "timestamp": "2023-01-01T13:00:00",
                    "event_type": "TestEvent",
                    "entity_id": "entity2",
                    "metadata": {"category": "other", "value": 20},
                },
            ]
            
            # Call function with filtering
            result = await generate_llm_training_dataset_async(
                output_format="python",
                filter_expression={"metadata.category": "test"},
            )
            
            # Verify result
            assert len(result) == 1
            assert result[0]["metadata"]["category"] == "test"

    @pytest.mark.asyncio
    async def test_generate_llm_training_dataset_max_events(self): pass
        """Test generate_llm_training_dataset with max_events limit."""
        # Mock the generate_dataset_async method
        with patch("backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance_async") as mock_get_instance: pass
            mock_service = MagicMock()
            mock_get_instance.return_value = mock_service
            
            # Create an AsyncMock for generate_dataset_async
            mock_service.generate_dataset_async = AsyncMock()
            
            # Set up mock to return test data
            mock_service.generate_dataset_async.return_value = [
                {"id": 1, "value": "one"},
                {"id": 2, "value": "two"},
                {"id": 3, "value": "three"},
                {"id": 4, "value": "four"},
                {"id": 5, "value": "five"},
            ]
            
            # Call function with max_events=3
            result = await generate_llm_training_dataset_async(
                output_format="python",
                max_events=3,
            )
            
            # Verify result
            assert len(result) == 3
            assert result[0]["id"] == 1
            assert result[2]["id"] == 3

    @pytest.mark.asyncio
    async def test_generate_llm_training_dataset_output_formats(self): pass
        """Test generate_llm_training_dataset with different output formats."""
        # Mock the generate_dataset_async method
        with patch("backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance_async") as mock_get_instance: pass
            mock_service = MagicMock()
            mock_get_instance.return_value = mock_service
            
            # Create an AsyncMock for generate_dataset_async
            mock_service.generate_dataset_async = AsyncMock()
            
            # Set up mock to return test data
            mock_service.generate_dataset_async.return_value = [
                {"id": 1, "value": "test1"},
                {"id": 2, "value": "test2"},
            ]
            
            # Test JSON format
            result_json = await generate_llm_training_dataset_async(output_format="json")
            assert isinstance(result_json, str)
            parsed_json = json.loads(result_json)
            assert len(parsed_json) == 2
            
            # Test JSONL format
            result_jsonl = await generate_llm_training_dataset_async(output_format="jsonl")
            assert isinstance(result_jsonl, str)
            lines = result_jsonl.strip().split("\n")
            assert len(lines) == 2
            
            # Test Python format
            result_python = await generate_llm_training_dataset_async(output_format="python")
            assert isinstance(result_python, list)
            assert len(result_python) == 2

    @pytest.mark.asyncio
    async def test_generate_llm_training_dataset_output_file(self): pass
        """Test generate_llm_training_dataset with output to file."""
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir: pass
            # Create a test output file path
            output_path = os.path.join(temp_dir, "test_output.jsonl")
            
            # Mock the generate_dataset_async method
            with patch("backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance_async") as mock_get_instance: pass
                mock_service = MagicMock()
                mock_get_instance.return_value = mock_service
                
                # Create an AsyncMock for generate_dataset_async
                mock_service.generate_dataset_async = AsyncMock()
                
                # Set up mock to return test data
                mock_service.generate_dataset_async.return_value = [
                    {"id": 1, "value": "output_test1"},
                    {"id": 2, "value": "output_test2"},
                ]
                
                # Call function with output file
                result = await generate_llm_training_dataset_async(
                    output_format="jsonl",
                    output_file=output_path,
                )
                
                # Verify the file was created
                assert os.path.exists(output_path)
                
                # Verify the file contents
                with open(output_path, "r") as f: pass
                    lines = f.readlines()
                    assert len(lines) == 2
                    
                    # Parse each line and verify
                    parsed_line1 = json.loads(lines[0])
                    parsed_line2 = json.loads(lines[1])
                    assert parsed_line1["id"] == 1
                    assert parsed_line2["id"] == 2
    
    def test_get_analytics_data_path(self): pass
        """Test get_analytics_data_path function."""
        # Get the path
        path = get_analytics_data_path()
        
        # Should return a Path object
        assert isinstance(path, Path)
        
        # Should be an absolute path
        assert path.is_absolute()
        
        # Should end with analytics_data
        assert path.name == "analytics_data"
    
    def test_summarize_analytics_storage_nonexistent(self): pass
        """Test summarize_analytics_storage with non-existent directory."""
        # Mock the get_analytics_data_path function
        with patch("backend.systems.analytics.utils.get_analytics_data_path") as mock_get_path: pass
            # Set it to return a non-existent path
            mock_get_path.return_value = Path("/non/existent/path")
            
            # Call the function
            result = summarize_analytics_storage()
            
            # Should report that directory doesn't exist
            assert isinstance(result, dict)
            assert not result["exists"]
            assert "message" in result
            
            # Test with as_json=True
            result = summarize_analytics_storage(as_json=True)
            
            # Should be a JSON string
            assert isinstance(result, str)
            data = json.loads(result)
            assert not data["exists"]
    
    def test_summarize_analytics_storage_with_data(self): pass
        """Test summarize_analytics_storage with actual data."""
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir: pass
            temp_path = Path(temp_dir)
            
            # Create some directories and files
            day1_dir = temp_path / "2023" / "01" / "15"
            day2_dir = temp_path / "2023" / "01" / "16"
            day1_dir.mkdir(parents=True, exist_ok=True)
            day2_dir.mkdir(parents=True, exist_ok=True)
            
            # Create some event files
            with open(day1_dir / "GameStart.jsonl", "w") as f: pass
                f.write(json.dumps({"event_type": "GameStart"}) + "\n")
                f.write(json.dumps({"event_type": "GameStart"}) + "\n")
            
            with open(day1_dir / "MemoryEvent.jsonl", "w") as f: pass
                f.write(json.dumps({"event_type": "MemoryEvent"}) + "\n")
            
            with open(day2_dir / "GameStart.jsonl", "w") as f: pass
                f.write(json.dumps({"event_type": "GameStart"}) + "\n")
            
            # Mock the get_analytics_data_path function
            with patch("backend.systems.analytics.utils.get_analytics_data_path") as mock_get_path: pass
                # Set it to return our temp directory
                mock_get_path.return_value = temp_path
                
                # Call the function
                result = summarize_analytics_storage()
                
                # Should have found our files
                assert result["exists"]
                assert result["total_files"] == 3
                assert result["total_events"] == 4
                assert result["event_counts"]["GameStart"] == 3
                assert result["event_counts"]["MemoryEvent"] == 1
                assert result["oldest_date"] == "2023-01-15T00:00:00"
                assert result["newest_date"] == "2023-01-16T00:00:00"
                assert result["date_range_days"] == 1
                
                # Test with as_json=True
                result = summarize_analytics_storage(as_json=True)
                
                # Should be a JSON string
                assert isinstance(result, str)
                data = json.loads(result)
                assert data["total_events"] == 4

    @pytest.mark.asyncio
    async def test_generate_llm_training_dataset_async_error_handling(self): pass
        """Test error handling in generate_llm_training_dataset_async."""
        # Mock the get_instance_async method to throw an exception
        with patch("backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance_async") as mock_get_instance: pass
            mock_get_instance.side_effect = Exception("Test error")
            
            # Call the function
            result = await generate_llm_training_dataset_async(
                event_types=["GameStart"],
                output_format="python"
            )
            
            # Verify the result is an empty list
            assert result == []
            
    @pytest.mark.asyncio
    async def test_generate_llm_training_dataset_async_error_with_output_file(self): pass
        """Test error handling in generate_llm_training_dataset_async when output file is specified."""
        # Mock the get_instance_async method to throw an exception
        with patch("backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance_async") as mock_get_instance: pass
            mock_get_instance.side_effect = Exception("Test error")
            
            # Create a temporary file path
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.close()
            
            try: pass
                # Call the function with output file
                result = await generate_llm_training_dataset_async(
                    event_types=["GameStart"],
                    output_format="jsonl",
                    output_file=temp_file.name
                )
                
                # Verify the result is an error message
                assert "Error:" in result
            finally: pass
                # Clean up
                if os.path.exists(temp_file.name): pass
                    os.unlink(temp_file.name) 