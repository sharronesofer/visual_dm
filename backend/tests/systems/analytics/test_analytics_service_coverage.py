from typing import Type
"""
Test file specifically designed to improve analytics service coverage.
Focuses on testing uncovered lines and edge cases.
"""

import pytest
import asyncio
import unittest.mock
from pathlib import Path
from datetime import datetime, date, timedelta
import json
import tempfile
import shutil
from unittest.mock import Mock, MagicMock, patch, AsyncMock

from backend.systems.analytics.services.analytics_service import (
    AnalyticsService, 
    AnalyticsEventType,
    get_analytics_service
)


class TestAnalyticsServiceCoverage: pass
    """Test class focused on improving analytics service coverage."""

    @pytest.fixture
    def temp_storage(self): pass
        """Create a temporary storage directory for tests."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def analytics_service(self, temp_storage): pass
        """Create an analytics service instance for testing."""
        # Reset singleton
        AnalyticsService._instance = None
        service = AnalyticsService(storage_path=temp_storage, test_mode=True)
        return service

    def test_singleton_instance_creation(self, temp_storage): pass
        """Test singleton instance creation and reuse."""
        # Reset singleton
        AnalyticsService._instance = None
        
        # First instance
        service1 = AnalyticsService(storage_path=temp_storage, test_mode=True)
        
        # Second instance should be the same
        service2 = AnalyticsService(storage_path=temp_storage / "different", test_mode=False)
        
        assert service1 is service2
        # Should have updated properties from second call
        assert service2.test_mode == False
        assert service2.storage_path == temp_storage / "different"

    def test_get_instance_sync(self, temp_storage): pass
        """Test synchronous get_instance method."""
        # Reset singleton
        AnalyticsService._instance = None
        
        service = AnalyticsService.get_instance(storage_path=temp_storage, test_mode=True)
        assert isinstance(service, AnalyticsService)
        assert service.storage_path == temp_storage
        assert service.test_mode == True

    @pytest.mark.asyncio
    async def test_get_instance_async(self, temp_storage): pass
        """Test asynchronous get_instance method."""
        # Reset singleton
        AnalyticsService._instance = None
        
        service = await AnalyticsService.get_instance_async(storage_path=temp_storage, test_mode=True)
        assert isinstance(service, AnalyticsService)
        assert service.storage_path == temp_storage
        assert service.test_mode == True

    def test_storage_path_property(self, analytics_service): pass
        """Test storage path property getter and setter."""
        original_path = analytics_service.storage_path
        new_path = Path("/tmp/new_analytics")
        
        analytics_service.storage_path = new_path
        assert analytics_service.storage_path == new_path
        
        # Reset for cleanup
        analytics_service.storage_path = original_path

    def test_ensure_async_components_normal_mode(self, temp_storage): pass
        """Test _ensure_async_components in normal (non-test) mode."""
        # Reset singleton and create service in normal mode
        AnalyticsService._instance = None
        service = AnalyticsService(storage_path=temp_storage, test_mode=False)
        
        # Mock _start_worker to avoid actually starting a worker
        with patch.object(service, '_start_worker') as mock_start_worker: pass
            mock_start_worker.return_value = Mock()
            
            # Call _ensure_async_components
            service._ensure_async_components()
            
            # Should have created queue and called _start_worker
            assert service._event_queue is not None
            mock_start_worker.assert_called_once()

    def test_ensure_async_components_error_handling(self, analytics_service): pass
        """Test error handling in _ensure_async_components."""
        # Mock asyncio.Queue to raise an exception
        with patch('asyncio.Queue', side_effect=Exception("Queue creation failed")): pass
            analytics_service._ensure_async_components()
            
            # Should handle the error gracefully
            assert analytics_service._event_queue is None
            assert analytics_service._worker_task is None

    @pytest.mark.asyncio
    async def test_process_event_queue_normal_operation(self, analytics_service): pass
        """Test _process_event_queue normal operation."""
        # Set up queue with test data
        analytics_service._event_queue = asyncio.Queue()
        
        # Mock _store_event
        with patch.object(analytics_service, '_store_event', new_callable=AsyncMock) as mock_store: pass
            # Add test event and stop signal
            test_event = {"event_type": "TestEvent", "entity_id": "test"}
            await analytics_service._event_queue.put(test_event)
            await analytics_service._event_queue.put(None)  # Stop signal
            
            # Process the queue
            await analytics_service._process_event_queue()
            
            # Should have processed the event
            mock_store.assert_called_once_with(test_event)

    @pytest.mark.asyncio
    async def test_process_event_queue_error_handling(self, analytics_service): pass
        """Test _process_event_queue error handling."""
        # Set up queue
        analytics_service._event_queue = asyncio.Queue()
        
        # Mock _store_event to raise an exception
        with patch.object(analytics_service, '_store_event', new_callable=AsyncMock) as mock_store: pass
            mock_store.side_effect = Exception("Storage failed")
            
            # Add test event and stop signal
            test_event = {"event_type": "TestEvent", "entity_id": "test"}
            await analytics_service._event_queue.put(test_event)
            await analytics_service._event_queue.put(None)  # Stop signal
            
            # Process the queue - should handle error gracefully
            await analytics_service._process_event_queue()
            
            # Should have attempted to process the event
            mock_store.assert_called_once_with(test_event)

    @pytest.mark.asyncio
    async def test_process_event_queue_cancellation(self, analytics_service): pass
        """Test _process_event_queue cancellation."""
        # Set up queue
        analytics_service._event_queue = asyncio.Queue()
        
        # Start processing and cancel it
        task = asyncio.create_task(analytics_service._process_event_queue())
        await asyncio.sleep(0.01)  # Let it start
        task.cancel()
        
        # Should raise CancelledError
        with pytest.raises(asyncio.CancelledError): pass
            await task

    def test_register_with_dispatcher_no_dispatcher(self, analytics_service): pass
        """Test register_with_dispatcher when no dispatcher is provided."""
        # Mock get_dispatcher
        with patch('backend.systems.analytics.services.analytics_service.get_dispatcher') as mock_get_dispatcher: pass
            mock_dispatcher = Mock()
            mock_get_dispatcher.return_value = mock_dispatcher
            
            result = analytics_service.register_with_dispatcher()
            
            # Should have called get_dispatcher and added middleware
            mock_get_dispatcher.assert_called_once()
            mock_dispatcher.add_middleware.assert_called_once()
            assert result is analytics_service

    def test_register_with_dispatcher_with_dispatcher(self, analytics_service): pass
        """Test register_with_dispatcher when dispatcher is provided."""
        mock_dispatcher = Mock()
        
        result = analytics_service.register_with_dispatcher(mock_dispatcher)
        
        # Should have added middleware to provided dispatcher
        mock_dispatcher.add_middleware.assert_called_once()
        assert analytics_service._dispatcher is mock_dispatcher
        assert result is analytics_service

    def test_middleware_error_handling(self, analytics_service): pass
        """Test analytics middleware error handling."""
        mock_dispatcher = Mock()
        analytics_service.register_with_dispatcher(mock_dispatcher)
        
        # Get the middleware function
        middleware_call = mock_dispatcher.add_middleware.call_args[0][0]
        
        # Create a mock event that will cause an error
        mock_event = Mock()
        mock_event.model_dump.side_effect = Exception("Model dump failed")
        
        # Mock log_event to raise an error
        with patch.object(analytics_service, 'log_event', side_effect=Exception("Log failed")): pass
            # Should handle error gracefully and return the event
            result = middleware_call(mock_event)
            assert result is mock_event

    def test_middleware_next_handler_error(self, analytics_service): pass
        """Test analytics middleware when next handler raises an error."""
        mock_dispatcher = Mock()
        analytics_service.register_with_dispatcher(mock_dispatcher)
        
        # Get the middleware function
        middleware_call = mock_dispatcher.add_middleware.call_args[0][0]
        
        # Create a mock event and next handler that raises an error
        mock_event = Mock()
        mock_event.model_dump.return_value = {"test": "data"}
        
        def failing_next_handler(event): pass
            raise Exception("Next handler failed")
        
        # Should handle error gracefully and return the event
        result = middleware_call(mock_event, failing_next_handler)
        assert result is mock_event

    def test_map_event_to_analytics_type_object_events(self, analytics_service): pass
        """Test _map_event_to_analytics_type with object events."""
        # Test class name mappings
        class GameInitialized: pass
            pass
        
        class MemoryCreated: pass
            pass
        
        class CustomEvent: pass
            pass
        
        assert analytics_service._map_event_to_analytics_type(GameInitialized()) == AnalyticsEventType.GAME_START
        assert analytics_service._map_event_to_analytics_type(MemoryCreated()) == AnalyticsEventType.MEMORY_EVENT
        assert analytics_service._map_event_to_analytics_type(CustomEvent()) == AnalyticsEventType.CUSTOM_EVENT

    def test_map_event_to_analytics_type_with_attributes(self, analytics_service): pass
        """Test _map_event_to_analytics_type with events that have special attributes."""
        # Test events with special attributes
        class TestEvent: pass
            def __init__(self): pass
                self.is_motif_event = True
        
        class QuestEvent: pass
            def __init__(self): pass
                self.is_quest_event = True
        
        class RelationshipEvent: pass
            def __init__(self): pass
                self.relationship = "friend"
        
        assert analytics_service._map_event_to_analytics_type(TestEvent()) == AnalyticsEventType.MOTIF_EVENT
        assert analytics_service._map_event_to_analytics_type(QuestEvent()) == AnalyticsEventType.QUEST_EVENT
        assert analytics_service._map_event_to_analytics_type(RelationshipEvent()) == AnalyticsEventType.RELATIONSHIP_EVENT

    def test_map_event_to_analytics_type_error_handling(self, analytics_service): pass
        """Test _map_event_to_analytics_type error handling."""
        # Create an event that will cause an error
        class ProblematicEvent: pass
            @property
            def __class__(self): pass
                raise Exception("Class access failed")
        
        # Should handle error and return CUSTOM_EVENT
        result = analytics_service._map_event_to_analytics_type(ProblematicEvent())
        assert result == AnalyticsEventType.CUSTOM_EVENT

    @pytest.mark.asyncio
    async def test_log_event_async_with_source_event(self, analytics_service): pass
        """Test log_event_async with source event."""
        # Create a mock source event
        source_event = Mock()
        source_event.__class__.__name__ = "TestEvent"
        source_event.id = "test-id"
        
        with patch.object(analytics_service, '_store_event', new_callable=AsyncMock) as mock_store: pass
            await analytics_service.log_event_async(
                event_type="TestEvent",
                source_event=source_event,
                entity_id="test-entity",
                metadata={"test": True}
            )
            
            # Should have called _store_event
            mock_store.assert_called_once()

    def test_log_event_no_queue_async_context(self, analytics_service): pass
        """Test log_event when no queue and in async context."""
        analytics_service._event_queue = None
        
        # Mock asyncio.get_running_loop to simulate async context
        with patch('asyncio.get_running_loop'): pass
            with patch.object(analytics_service, '_store_event', return_value=True) as mock_store: pass
                result = analytics_service.log_event(
                    event_type="TestEvent",
                    entity_id="test-entity"
                )
                
                # Should have called async store
                mock_store.assert_called_once()

    def test_log_event_no_queue_sync_context(self, analytics_service): pass
        """Test log_event when no queue and in sync context."""
        analytics_service._event_queue = None
        
        # Mock asyncio.get_running_loop to raise RuntimeError (no async context)
        with patch('asyncio.get_running_loop', side_effect=RuntimeError("No running loop")): pass
            with patch.object(analytics_service, '_store_event_sync', return_value=True) as mock_store_sync: pass
                result = analytics_service.log_event(
                    event_type="TestEvent",
                    entity_id="test-entity"
                )
                
                # Should have called sync storage
                mock_store_sync.assert_called_once()

    def test_log_event_with_source_and_source_event(self, analytics_service): pass
        """Test log_event with both source and source_event parameters."""
        analytics_service._event_queue = asyncio.Queue()
        
        mock_source_event = Mock()
        
        with patch.object(analytics_service, '_queue_event_safely', return_value=True) as mock_queue: pass
            result = analytics_service.log_event(
                event_type="TestEvent",
                source="legacy_source",
                entity_id="test-entity",
                source_event=mock_source_event
            )
            
            # Should have called _queue_event_safely with both source fields
            mock_queue.assert_called_once()
            call_args = mock_queue.call_args[0][0]
            assert "source" in call_args
            assert "source_event" in call_args

    def test_store_event_sync_directory_creation_error(self, analytics_service): pass
        """Test _store_event_sync when directory creation fails."""
        event_data = {
            "event_type": "TestEvent",
            "entity_id": "test-entity",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {"test": True}
        }
        
        # Mock Path.mkdir to raise an exception
        with patch.object(Path, 'mkdir', side_effect=Exception("Permission denied")): pass
            result = analytics_service._store_event_sync(event_data)
            
            assert result == False

    def test_store_event_sync_file_write_error(self, analytics_service): pass
        """Test _store_event_sync when file writing fails."""
        event_data = {
            "event_type": "TestEvent",
            "entity_id": "test-entity",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {"test": True}
        }
        
        # Mock _append_to_file_sync to raise an exception
        with patch.object(analytics_service, '_append_to_file_sync', side_effect=Exception("Write failed")): pass
            result = analytics_service._store_event_sync(event_data)
            
            assert result == False

    @pytest.mark.asyncio
    async def test_stop_worker_no_task(self, analytics_service): pass
        """Test _stop_worker when no worker task exists."""
        analytics_service._worker_task = None
        
        # Should complete without error
        await analytics_service._stop_worker()
        assert analytics_service._worker_task is None

    @pytest.mark.asyncio
    async def test_stop_worker_already_done(self, analytics_service): pass
        """Test _stop_worker when worker task is already done."""
        # Create a completed task
        async def dummy_task(): pass
            return True
        
        task = asyncio.create_task(dummy_task())
        await task  # Complete the task
        analytics_service._worker_task = task
        
        # Should complete without error
        await analytics_service._stop_worker()
        assert analytics_service._worker_task is None

    def test_generate_dataset_with_entity_id_filter(self, analytics_service): pass
        """Test generate_dataset with entity_id filter."""
        # Create test data
        test_events = [
            {
                "timestamp": "2025-01-01T12:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity1",
                "metadata": {"test": True}
            },
            {
                "timestamp": "2025-01-01T13:00:00",
                "event_type": "TestEvent",
                "entity_id": "entity2",
                "metadata": {"test": True}
            }
        ]
        
        with patch.object(analytics_service, '_generate_dataset_sync', return_value=test_events) as mock_generate: pass
            result = analytics_service.generate_dataset(entity_id="entity1")
            
            mock_generate.assert_called_once()
            # Check that entity_id was passed
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs['entity_id'] == "entity1"

    def test_generate_dataset_sync_file_processing_error(self, analytics_service, temp_storage): pass
        """Test _generate_dataset_sync when file processing fails."""
        # Create a test directory structure
        date_dir = temp_storage / "2025" / "01" / "01"
        date_dir.mkdir(parents=True)
        
        # Create a test file with invalid JSON
        test_file = date_dir / "TestEvent.jsonl"
        test_file.write_text("invalid json\n{\"valid\": \"json\"}\n")
        
        # Mock get_event_directory to return our test directory
        with patch.object(analytics_service, 'get_event_directory', return_value=date_dir): pass
            result = analytics_service._generate_dataset_sync(
                start_date=date(2025, 1, 1),
                end_date=date(2025, 1, 1)
            )
            
            # Should have processed the valid JSON line and skipped the invalid one
            assert len(result) == 1
            assert result[0]["valid"] == "json"

    def test_generate_dataset_sync_file_read_error(self, analytics_service, temp_storage): pass
        """Test _generate_dataset_sync when file reading fails."""
        # Create a test directory structure
        date_dir = temp_storage / "2025" / "01" / "01"
        date_dir.mkdir(parents=True)
        
        # Create a test file
        test_file = date_dir / "TestEvent.jsonl"
        test_file.write_text("{\"test\": \"data\"}\n")
        
        # Mock get_event_directory to return our test directory
        with patch.object(analytics_service, 'get_event_directory', return_value=date_dir): pass
            # Mock open to raise an exception
            with patch('builtins.open', side_effect=Exception("File read error")): pass
                result = analytics_service._generate_dataset_sync(
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 1, 1)
                )
                
                # Should return empty list due to file read error
                assert result == []

    def test_get_event_directory_default_date(self, analytics_service): pass
        """Test get_event_directory with default date (today)."""
        today = datetime.now().date()
        expected_path = analytics_service.storage_path / today.strftime("%Y") / today.strftime("%m") / today.strftime("%d")
        
        result = analytics_service.get_event_directory()
        assert result == expected_path

    def test_get_event_directory_specific_date(self, analytics_service): pass
        """Test get_event_directory with specific date."""
        test_date = date(2025, 5, 15)
        expected_path = analytics_service.storage_path / "2025" / "05" / "15"
        
        result = analytics_service.get_event_directory(test_date)
        assert result == expected_path

    def test_start_worker_no_event_loop(self, analytics_service): pass
        """Test _start_worker when no event loop is running."""
        # Mock asyncio.get_running_loop to raise RuntimeError
        with patch('asyncio.get_running_loop', side_effect=RuntimeError("No running loop")): pass
            result = analytics_service._start_worker()
            
            assert result is None

    def test_start_worker_error(self, analytics_service): pass
        """Test _start_worker when an error occurs."""
        # Mock asyncio.create_task to raise an exception
        with patch('asyncio.create_task', side_effect=Exception("Task creation failed")): pass
            result = analytics_service._start_worker()
            
            assert result is None

    @pytest.mark.asyncio
    async def test_worker_process_normal_operation(self, analytics_service): pass
        """Test _worker_process normal operation."""
        # Set up queue with test data
        analytics_service._event_queue = asyncio.Queue()
        
        # Mock _store_event
        with patch.object(analytics_service, '_store_event', new_callable=AsyncMock) as mock_store: pass
            # Add test event and stop signal
            test_event = {"event_type": "TestEvent", "entity_id": "test"}
            await analytics_service._event_queue.put(test_event)
            await analytics_service._event_queue.put(None)  # Stop signal
            
            # Process the queue
            await analytics_service._worker_process()
            
            # Should have processed the event
            mock_store.assert_called_once_with(test_event)

    @pytest.mark.asyncio
    async def test_worker_process_unexpected_error(self, analytics_service): pass
        """Test _worker_process with unexpected error."""
        # Set up queue
        analytics_service._event_queue = asyncio.Queue()
        
        # Mock queue.get to raise an unexpected error
        with patch.object(analytics_service._event_queue, 'get', side_effect=Exception("Unexpected error")): pass
            # Should raise the exception
            with pytest.raises(Exception, match="Unexpected error"): pass
                await analytics_service._worker_process()

    def test_get_analytics_middleware_class_method(self): pass
        """Test get_analytics_middleware class method."""
        # Mock get_analytics_service
        with patch('backend.systems.analytics.services.analytics_service.get_analytics_service') as mock_get_service: pass
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            middleware = AnalyticsService.get_analytics_middleware()
            
            # Should be a callable
            assert callable(middleware)
            mock_get_service.assert_called_once()

    def test_get_analytics_middleware_function_call(self): pass
        """Test the middleware function returned by get_analytics_middleware."""
        # Mock get_analytics_service
        with patch('backend.systems.analytics.services.analytics_service.get_analytics_service') as mock_get_service: pass
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            middleware = AnalyticsService.get_analytics_middleware()
            
            # Test the middleware function
            mock_event = Mock()
            mock_event.model_dump.return_value = {"test": "data"}
            
            result = middleware(mock_event)
            
            # Should have called log_event on the service
            mock_service.log_event.assert_called_once()
            assert result is mock_event

    def test_queue_event_safely_sync_fallback(self, analytics_service): pass
        """Test _queue_event_safely sync fallback."""
        analytics_service._event_queue = None
        
        event_data = {"event_type": "TestEvent", "entity_id": "test"}
        
        with patch.object(analytics_service, '_store_event_sync', return_value=True) as mock_store_sync: pass
            result = analytics_service._queue_event_safely(event_data)
            
            mock_store_sync.assert_called_once_with(event_data)
            assert result == True

    def test_queue_event_safely_async_error(self, analytics_service): pass
        """Test _queue_event_safely when async queueing fails."""
        analytics_service._event_queue = asyncio.Queue(maxsize=1)
        
        # Fill the queue
        try: pass
            analytics_service._event_queue.put_nowait("dummy")
        except: pass
            pass
        
        event_data = {"event_type": "TestEvent", "entity_id": "test"}
        
        with patch.object(analytics_service, '_store_event_sync', return_value=True) as mock_store_sync: pass
            result = analytics_service._queue_event_safely(event_data)
            
            # Should fall back to sync storage
            mock_store_sync.assert_called_once_with(event_data)

    def test_event_matches_filters_callback(self, analytics_service): pass
        """Test _event_matches_filters with callback filter."""
        event = {"event_type": "TestEvent", "metadata": {"score": 85}}
        
        def score_filter(event_data): pass
            return event_data.get("metadata", {}).get("score", 0) > 80
        
        filters = {"callback": score_filter}
        
        assert analytics_service._event_matches_filters(event, filters) == True
        
        # Test with event that doesn't match
        event_low_score = {"event_type": "TestEvent", "metadata": {"score": 75}}
        assert analytics_service._event_matches_filters(event_low_score, filters) == False

    def test_event_matches_filters_dict_filter(self, analytics_service): pass
        """Test _event_matches_filters with dictionary filter."""
        event = {"event_type": "TestEvent", "metadata": {"category": "game", "action": "start"}}
        
        filters = {"metadata.category": "game", "metadata.action": "start"}
        
        assert analytics_service._event_matches_filters(event, filters) == True
        
        # Test with event that doesn't match
        event_no_match = {"event_type": "TestEvent", "metadata": {"category": "character"}}
        assert analytics_service._event_matches_filters(event_no_match, filters) == False

    def test_event_matches_filters_no_filters(self, analytics_service): pass
        """Test _event_matches_filters with no filters."""
        event = {"event_type": "TestEvent"}
        
        assert analytics_service._event_matches_filters(event, None) == True
        assert analytics_service._event_matches_filters(event, {}) == True

    def test_get_event_file_path_with_date(self, analytics_service): pass
        """Test get_event_file_path with specific date."""
        test_date = date(2025, 5, 15)
        expected_path = analytics_service.storage_path / "2025" / "05" / "15" / "TestEvent.jsonl"
        
        result = analytics_service.get_event_file_path("TestEvent", test_date)
        assert result == expected_path

    def test_get_event_file_path_default_date(self, analytics_service): pass
        """Test get_event_file_path with default date (today)."""
        today = datetime.now().date()
        expected_path = analytics_service.storage_path / today.strftime("%Y") / today.strftime("%m") / today.strftime("%d") / "TestEvent.jsonl"
        
        result = analytics_service.get_event_file_path("TestEvent")
        assert result == expected_path

    def test_get_event_file_path_internal(self, analytics_service): pass
        """Test _get_event_file_path internal method."""
        today = datetime.now().date()
        expected_path = analytics_service.storage_path / today.strftime("%Y") / today.strftime("%m") / today.strftime("%d") / "TestEvent.jsonl"
        
        result = analytics_service._get_event_file_path("TestEvent")
        assert result == expected_path

    @pytest.mark.asyncio
    async def test_append_to_file_async(self, analytics_service, temp_storage): pass
        """Test _append_to_file async method."""
        test_file = temp_storage / "test.jsonl"
        test_content = {"test": "data"}
        
        await analytics_service._append_to_file(test_file, test_content)
        
        # Check that file was created and content written
        assert test_file.exists()
        content = test_file.read_text()
        assert json.loads(content.strip()) == test_content

    @pytest.mark.asyncio
    async def test_append_to_file_async_error(self, analytics_service, temp_storage): pass
        """Test _append_to_file async method error handling."""
        # Try to write to a directory that doesn't exist and can't be created
        test_file = Path("/nonexistent/path/test.jsonl")
        test_content = {"test": "data"}
        
        # Should handle the error gracefully
        await analytics_service._append_to_file(test_file, test_content)

    def test_append_to_file_sync(self, analytics_service, temp_storage): pass
        """Test _append_to_file_sync method."""
        test_file = temp_storage / "test.jsonl"
        test_content = '{"test": "data"}'
        
        analytics_service._append_to_file_sync(test_file, test_content)
        
        # Check that file was created and content written
        assert test_file.exists()
        content = test_file.read_text()
        assert content.strip() == test_content

    def test_append_to_file_sync_error(self, analytics_service): pass
        """Test _append_to_file_sync method error handling."""
        # Try to write to a path that will cause an error
        test_file = Path("/nonexistent/path/test.jsonl")
        test_content = '{"test": "data"}'
        
        # Should handle the error gracefully (no exception raised)
        analytics_service._append_to_file_sync(test_file, test_content)

    def test_get_analytics_service_function(self): pass
        """Test the get_analytics_service module function."""
        # Reset singleton
        AnalyticsService._instance = None
        
        service = get_analytics_service()
        assert isinstance(service, AnalyticsService)
        
        # Second call should return the same instance
        service2 = get_analytics_service()
        assert service is service2


class TestAnalyticsServiceEdgeCases: pass
    """Test edge cases and error conditions."""

    @pytest.fixture
    def temp_storage(self): pass
        """Create a temporary storage directory for tests."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_analytics_event_type_get_all(self): pass
        """Test AnalyticsEventType.get_all() method."""
        all_types = AnalyticsEventType.get_all()
        
        # Should include all defined event types
        assert AnalyticsEventType.GAME_START in all_types
        assert AnalyticsEventType.GAME_END in all_types
        assert AnalyticsEventType.MEMORY_EVENT in all_types
        assert AnalyticsEventType.CUSTOM_EVENT in all_types
        
        # Should be a list
        assert isinstance(all_types, list)
        assert len(all_types) > 0

    def test_singleton_thread_safety(self, temp_storage): pass
        """Test singleton thread safety (basic test)."""
        import threading
        
        # Reset singleton
        AnalyticsService._instance = None
        
        instances = []
        
        def create_instance(): pass
            service = AnalyticsService(storage_path=temp_storage, test_mode=True)
            instances.append(service)
        
        # Create multiple threads
        threads = [threading.Thread(target=create_instance) for _ in range(5)]
        
        # Start all threads
        for thread in threads: pass
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads: pass
            thread.join()
        
        # All instances should be the same
        assert len(instances) == 5
        for instance in instances: pass
            assert instance is instances[0]

    def test_storage_path_with_special_characters(self, temp_storage): pass
        """Test storage path with special characters."""
        special_path = temp_storage / "test with spaces & symbols!"
        
        # Reset singleton
        AnalyticsService._instance = None
        service = AnalyticsService(storage_path=special_path, test_mode=True)
        
        assert service.storage_path == special_path

    def test_very_large_metadata(self, temp_storage): pass
        """Test handling of very large metadata."""
        # Reset singleton
        AnalyticsService._instance = None
        service = AnalyticsService(storage_path=temp_storage, test_mode=True)
        
        # Create large metadata
        large_metadata = {"data": "x" * 10000, "numbers": list(range(1000))}
        
        with patch.object(service, '_store_event_sync', return_value=True) as mock_store: pass
            result = service.log_event(
                event_type="TestEvent",
                entity_id="test",
                metadata=large_metadata
            )
            
            assert result == True
            mock_store.assert_called_once() 