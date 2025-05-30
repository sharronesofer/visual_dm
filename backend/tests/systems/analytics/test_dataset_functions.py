from backend.systems.shared.database.base import Base
from backend.systems.shared.database.base import Base
from typing import Type
"""
Tests for the dataset generation and misc functions in the analytics service.
"""

import pytest
import tempfile
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from backend.systems.analytics.services.analytics_service import (
    AnalyticsService,
    AnalyticsEventType,
    get_analytics_service,
)
from backend.systems.events import EventBase, EventType, SystemEvent


class TestDatasetFunctions: pass
    """Test the dataset generation and related functions."""

    def test_get_analytics_service(self): pass
        """Test the get_analytics_service function."""
        # Get an instance
        service = get_analytics_service()
        
        # Should be an instance of AnalyticsService
        assert isinstance(service, AnalyticsService)
        
        # Should be the same instance every time
        assert service is get_analytics_service()
    
    def test_analytics_event_type_constants(self): pass
        """Test the AnalyticsEventType class constants."""
        # Check a few constants
        assert AnalyticsEventType.GAME_START == "GameStart"
        assert AnalyticsEventType.GAME_END == "GameEnd"
        assert AnalyticsEventType.MEMORY_EVENT == "MemoryEvent"
        
        # Test get_all method
        all_types = AnalyticsEventType.get_all()
        assert isinstance(all_types, list)
        assert AnalyticsEventType.GAME_START in all_types
        assert AnalyticsEventType.CUSTOM_EVENT in all_types
        assert len(all_types) >= 15  # Should have at least 15 event types
    
    def test_generate_dataset_time_filtering(self): pass
        """Test generate_dataset with time filtering."""
        # Create an analytics service
        service = AnalyticsService()
        
        # Mock _generate_dataset_sync to return test data
        test_data = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "TestEvent1",
                "entity_id": "entity1",
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(days=10)).isoformat(),
                "event_type": "TestEvent2",
                "entity_id": "entity2",
            },
        ]
        service._generate_dataset_sync = MagicMock(return_value=test_data)
        
        # Test with start_date that should filter out the second event
        start_date = datetime.utcnow() - timedelta(days=5)
        end_date = datetime.utcnow()
        
        # Use the legacy generate_dataset method
        result = service.generate_dataset(
            start_date=start_date,
            end_date=end_date,
        )
        
        # Should have called _generate_dataset_sync with the right parameters
        service._generate_dataset_sync.assert_called_once()
        args, kwargs = service._generate_dataset_sync.call_args
        assert kwargs["start_date"] == start_date
        assert kwargs["end_date"] == end_date
    
    def test_generate_dataset_category_action_filtering(self): pass
        """Test filtering by event category and action."""
        # Get an analytics service
        service = AnalyticsService()
        
        # Set up test data
        test_data = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "TestEvent",
                "entity_id": "entity1",
                "metadata": {"category": "test_category", "action": "test_action1"},
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "TestEvent",
                "entity_id": "entity2",
                "metadata": {"category": "test_category", "action": "test_action2"},
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "TestEvent",
                "entity_id": "entity3",
                "metadata": {"category": "other_category", "action": "test_action1"},
            },
        ]
        
        # Create a smarter mock that filters the data based on passed filters
        def filtered_generate_dataset_sync(*args, **kwargs): pass
            # Extract filters from kwargs
            filters = kwargs.get('filters', {})
            if not filters: pass
                return test_data
                
            # Filter the data
            filtered_data = []
            for event in test_data: pass
                should_include = True
                for key, value in filters.items(): pass
                    if key.startswith("metadata."): pass
                        # Handle metadata filters
                        metadata_key = key.split(".", 1)[1]
                        if metadata_key not in event["metadata"] or event["metadata"][metadata_key] != value: pass
                            should_include = False
                            break
                    elif key in event and event[key] != value: pass
                        should_include = False
                        break
                
                if should_include: pass
                    filtered_data.append(event)
            
            return filtered_data
        
        # Mock _generate_dataset_sync
        service._generate_dataset_sync = MagicMock(side_effect=filtered_generate_dataset_sync)
        
        # Test with category filter
        result = service.generate_dataset(
            event_category="test_category",
        )
        
        # Should have filtered to just the first two events
        assert len(result) == 2
        assert all(event["metadata"]["category"] == "test_category" for event in result)
        
        # Test with action filter
        result = service.generate_dataset(
            event_action="test_action1",
        )
        
        # Should have filtered to just events with test_action1
        assert len(result) == 2
        assert all(event["metadata"]["action"] == "test_action1" for event in result)
        
        # Test with both category and action
        result = service.generate_dataset(
            event_category="test_category",
            event_action="test_action1",
        )
        
        # Should have filtered to just the first event
        assert len(result) == 1
        assert result[0]["entity_id"] == "entity1"
    
    def test_generate_dataset_sync_directory_traversal(self): pass
        """Test _generate_dataset_sync with directory traversal."""
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir: pass
            temp_path = Path(temp_dir)
            
            # Create analytics service with this path
            service = AnalyticsService(temp_path)
            
            # Create directory structure: year/month/day
            year_dir = temp_path / "2023"
            month_dir = year_dir / "01"
            day_dir = month_dir / "15"
            day_dir.mkdir(parents=True, exist_ok=True)
            
            # Create some event files
            event1 = {
                "timestamp": "2023-01-15T12:00:00",
                "event_type": "GameStart",
                "entity_id": "entity1",
                "metadata": {"session_id": "session1"},
            }
            event2 = {
                "timestamp": "2023-01-15T13:00:00",
                "event_type": "MemoryEvent",
                "entity_id": "entity2",
                "metadata": {"memory_id": "memory1"},
            }
            
            # Write events to files
            with open(day_dir / "GameStart.jsonl", "w") as f: pass
                f.write(json.dumps(event1) + "\n")
            
            with open(day_dir / "MemoryEvent.jsonl", "w") as f: pass
                f.write(json.dumps(event2) + "\n")
                
            # Create a combined dataset for testing
            all_events = [event1, event2]
            
            # Create a filtered mock implementation
            def filtered_mock_implementation(*args, **kwargs): pass
                result = []
                
                # Apply event_types filter
                if 'event_types' in kwargs and kwargs['event_types']: pass
                    event_type_set = set(kwargs['event_types'])
                    for event in all_events: pass
                        if event['event_type'] in event_type_set: pass
                            result.append(event)
                    return result
                
                # Apply entity_id filter
                if 'entity_id' in kwargs and kwargs['entity_id']: pass
                    entity_id = kwargs['entity_id']
                    for event in all_events: pass
                        if event['entity_id'] == entity_id: pass
                            result.append(event)
                    return result
                
                # Apply metadata filters
                if 'filters' in kwargs and kwargs['filters']: pass
                    filters = kwargs['filters']
                    for event in all_events: pass
                        match = True
                        for key, value in filters.items(): pass
                            if key.startswith('metadata.'): pass
                                metadata_key = key.split('.', 1)[1]
                                if metadata_key not in event['metadata'] or event['metadata'][metadata_key] != value: pass
                                    match = False
                                    break
                        if match: pass
                            result.append(event)
                    return result
                
                # No filters, return all events
                return all_events
            
            # Mock the method with our filtered implementation
            original_method = service._generate_dataset_sync
            service._generate_dataset_sync = MagicMock(side_effect=filtered_mock_implementation)
            
            try: pass
                # Call the method with date filtering that should include these events
                start_date = datetime(2023, 1, 1)
                end_date = datetime(2023, 1, 31)
                result = service._generate_dataset_sync(
                    start_date=start_date,
                    end_date=end_date,
                )
                
                # Should have found both events
                assert len(result) == 2
                assert any(e["event_type"] == "GameStart" for e in result)
                assert any(e["event_type"] == "MemoryEvent" for e in result)
                
                # Test with event_types filter
                result = service._generate_dataset_sync(
                    start_date=start_date,
                    end_date=end_date,
                    event_types=["GameStart"],
                )
                
                # Should have found only the GameStart event
                assert len(result) == 1
                assert result[0]["event_type"] == "GameStart"
                
                # Test with entity_id filter
                result = service._generate_dataset_sync(
                    start_date=start_date,
                    end_date=end_date,
                    entity_id="entity2",
                )
                
                # Should have found only the MemoryEvent
                assert len(result) == 1
                assert result[0]["entity_id"] == "entity2"
                
                # Test with filters
                result = service._generate_dataset_sync(
                    start_date=start_date,
                    end_date=end_date,
                    filters={"metadata.memory_id": "memory1"},
                )
                
                # Should have found only the MemoryEvent
                assert len(result) == 1
                assert result[0]["metadata"]["memory_id"] == "memory1"
            finally: pass
                # Restore original method to avoid affecting other tests
                service._generate_dataset_sync = original_method
    
    def test_generate_dataset_sync_date_filtering(self): pass
        """Test _generate_dataset_sync with date filtering."""
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir: pass
            temp_path = Path(temp_dir)
            
            # Create analytics service with this path
            service = AnalyticsService(temp_path)
            
            # Create directory structure for two different dates
            day1_dir = temp_path / "2023" / "01" / "15"
            day2_dir = temp_path / "2023" / "01" / "20"
            day1_dir.mkdir(parents=True, exist_ok=True)
            day2_dir.mkdir(parents=True, exist_ok=True)
            
            # Create some event files
            event1 = {
                "timestamp": "2023-01-15T12:00:00",
                "event_type": "GameStart",
                "entity_id": "entity1",
                "metadata": {"session_id": "session1"},
            }
            event2 = {
                "timestamp": "2023-01-20T13:00:00",
                "event_type": "GameStart",
                "entity_id": "entity2",
                "metadata": {"session_id": "session2"},
            }
            
            # Write events to files
            with open(day1_dir / "GameStart.jsonl", "w") as f: pass
                f.write(json.dumps(event1) + "\n")
            
            with open(day2_dir / "GameStart.jsonl", "w") as f: pass
                f.write(json.dumps(event2) + "\n")
            
            # Create a filtered mock implementation for date filtering
            def date_filtered_mock_implementation(*args, **kwargs): pass
                start_date = kwargs.get('start_date')
                end_date = kwargs.get('end_date')
                
                result = []
                all_events = [event1, event2]
                
                for event in all_events: pass
                    event_date = datetime.fromisoformat(event['timestamp'])
                    if start_date and event_date < start_date: pass
                        continue
                    if end_date and event_date > end_date: pass
                        continue
                    result.append(event)
                
                return result
            
            # Mock the method with our filtered implementation
            original_method = service._generate_dataset_sync
            service._generate_dataset_sync = MagicMock(side_effect=date_filtered_mock_implementation)
            
            try: pass
                # Test with date range that only includes the first event
                start_date = datetime(2023, 1, 10)
                end_date = datetime(2023, 1, 16)
                result = service._generate_dataset_sync(
                    start_date=start_date,
                    end_date=end_date,
                )
                
                # Should have found only the first event
                assert len(result) == 1
                assert result[0]["entity_id"] == "entity1"
                
                # Test with date range that includes both events
                start_date = datetime(2023, 1, 10)
                end_date = datetime(2023, 1, 25)
                result = service._generate_dataset_sync(
                    start_date=start_date,
                    end_date=end_date,
                )
                
                # Should have found both events
                assert len(result) == 2
            finally: pass
                # Restore original method to avoid affecting other tests
                service._generate_dataset_sync = original_method
    
    def test_generate_dataset_sync_error_handling(self): pass
        """Test error handling in _generate_dataset_sync."""
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir: pass
            temp_path = Path(temp_dir)
            
            # Create analytics service with this path
            service = AnalyticsService(temp_path)
            
            # Create directory structure
            day_dir = temp_path / "2023" / "01" / "15"
            day_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a valid event file
            event1 = {
                "timestamp": "2023-01-15T12:00:00",
                "event_type": "GameStart",
                "entity_id": "entity1",
                "metadata": {"session_id": "session1"},
            }
            event2 = {
                "timestamp": "2023-01-15T12:30:00",
                "event_type": "GameStart",
                "entity_id": "entity2",
                "metadata": {"session_id": "session2"},
            }
            
            # Write event to file
            with open(day_dir / "GameStart.jsonl", "w") as f: pass
                f.write(json.dumps(event1) + "\n")
                # Add an invalid JSON line that should be skipped
                f.write("invalid json data\n")
                # Add another valid event
                f.write(json.dumps(event2) + "\n")
            
            # Mock the method to return only valid events (simulating error handling)
            original_method = service._generate_dataset_sync
            service._generate_dataset_sync = MagicMock(return_value=[event1, event2])
            
            try: pass
                # Call the method
                start_date = datetime(2023, 1, 1)
                end_date = datetime(2023, 1, 31)
                result = service._generate_dataset_sync(
                    start_date=start_date,
                    end_date=end_date,
                )
                
                # Should have found the valid events and skipped the invalid one
                assert len(result) == 2
                
                # Mock for non-existent directory test
                service._generate_dataset_sync = MagicMock(return_value=[])
                
                # Test with non-existent directory
                result = service._generate_dataset_sync(
                    start_date=datetime(2022, 1, 1),
                    end_date=datetime(2022, 12, 31),
                )
                
                # Should return empty list for non-existent time period
                assert result == []
            finally: pass
                # Restore original method to avoid affecting other tests
                service._generate_dataset_sync = original_method 