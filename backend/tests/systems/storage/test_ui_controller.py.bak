"""
Unit tests for the SaveLoadUIController class.

These tests verify that:
1. The singleton pattern works correctly
2. Callback registration works correctly
3. UI methods work correctly with and without callbacks
"""

import pytest
import logging
from unittest.mock import patch, MagicMock, call

from backend.systems.storage.ui_controller import SaveLoadUIController

class TestSaveLoadUIController:
    """Test suite for the SaveLoadUIController class."""
    
    @pytest.fixture
    def ui_controller(self):
        """Create a fresh SaveLoadUIController instance for testing."""
        # Create controller
        controller = SaveLoadUIController.get_instance()
        
        # Reset callbacks
        controller.callbacks = {
            'show_progress': None,
            'update_progress': None,
            'hide_progress': None,
            'show_error': None,
            'show_notification': None
        }
        
        yield controller
        
        # Reset singleton for other tests
        SaveLoadUIController._instance = None
    
    def test_singleton_pattern(self):
        """Test that the singleton pattern works correctly."""
        instance1 = SaveLoadUIController.get_instance()
        instance2 = SaveLoadUIController.get_instance()
        
        assert instance1 is instance2
    
    def test_register_callback(self, ui_controller):
        """Test that registering callbacks works correctly."""
        # Create mock callbacks
        mock_show_progress = MagicMock()
        mock_update_progress = MagicMock()
        
        # Register callbacks
        ui_controller.register_callback('show_progress', mock_show_progress)
        ui_controller.register_callback('update_progress', mock_update_progress)
        
        # Verify callbacks were registered
        assert ui_controller.callbacks['show_progress'] == mock_show_progress
        assert ui_controller.callbacks['update_progress'] == mock_update_progress
    
    def test_register_invalid_callback(self, ui_controller):
        """Test that registering an invalid callback type logs a warning."""
        with patch.object(logging.getLogger('backend.systems.storage.ui_controller'), 'warning') as mock_warning:
            # Register invalid callback
            ui_controller.register_callback('invalid_type', MagicMock())
            
            # Verify warning was logged
            mock_warning.assert_called_once()
            assert "Unknown callback type" in mock_warning.call_args[0][0]
    
    def test_show_progress_with_callback(self, ui_controller):
        """Test that show_progress calls the callback when registered."""
        # Create mock callback
        mock_callback = MagicMock()
        
        # Register callback
        ui_controller.register_callback('show_progress', mock_callback)
        
        # Call method
        ui_controller.show_progress("Test Title", "Test Message")
        
        # Verify callback was called with correct args
        mock_callback.assert_called_once_with("Test Title", "Test Message")
    
    def test_show_progress_without_callback(self, ui_controller):
        """Test that show_progress logs a message when no callback is registered."""
        with patch.object(logging.getLogger('backend.systems.storage.ui_controller'), 'info') as mock_info:
            # Call method without registering callback
            ui_controller.show_progress("Test Title", "Test Message")
            
            # Verify log message
            mock_info.assert_called_once()
            assert "Progress: Test Title - Test Message" in mock_info.call_args[0][0]
    
    def test_update_progress_with_callback(self, ui_controller):
        """Test that update_progress calls the callback when registered."""
        # Create mock callback
        mock_callback = MagicMock()
        
        # Register callback
        ui_controller.register_callback('update_progress', mock_callback)
        
        # Call method
        ui_controller.update_progress(0.5, "Halfway done")
        
        # Verify callback was called with correct args
        mock_callback.assert_called_once_with(0.5, "Halfway done")
    
    def test_update_progress_without_message(self, ui_controller):
        """Test that update_progress works without a message."""
        # Create mock callback
        mock_callback = MagicMock()
        
        # Register callback
        ui_controller.register_callback('update_progress', mock_callback)
        
        # Call method without message
        ui_controller.update_progress(0.75)
        
        # Verify callback was called with correct args
        mock_callback.assert_called_once_with(0.75, None)
    
    def test_update_progress_without_callback(self, ui_controller):
        """Test that update_progress logs a message when no callback is registered."""
        with patch.object(logging.getLogger('backend.systems.storage.ui_controller'), 'info') as mock_info:
            # Call method without registering callback
            ui_controller.update_progress(0.5, "Halfway done")
            
            # Verify log message
            mock_info.assert_called_once()
            assert "Progress: 50.0% - Halfway done" in mock_info.call_args[0][0]
    
    def test_hide_progress_with_callback(self, ui_controller):
        """Test that hide_progress calls the callback when registered."""
        # Create mock callback
        mock_callback = MagicMock()
        
        # Register callback
        ui_controller.register_callback('hide_progress', mock_callback)
        
        # Call method
        ui_controller.hide_progress()
        
        # Verify callback was called
        mock_callback.assert_called_once()
    
    def test_hide_progress_without_callback(self, ui_controller):
        """Test that hide_progress logs a message when no callback is registered."""
        with patch.object(logging.getLogger('backend.systems.storage.ui_controller'), 'info') as mock_info:
            # Call method without registering callback
            ui_controller.hide_progress()
            
            # Verify log message
            mock_info.assert_called_once_with("Progress hidden")
    
    def test_show_error_with_callback(self, ui_controller):
        """Test that show_error calls the callback when registered."""
        # Create mock callback
        mock_callback = MagicMock()
        
        # Register callback
        ui_controller.register_callback('show_error', mock_callback)
        
        # Call method
        ui_controller.show_error("Error Title", "Error Message")
        
        # Verify callback was called with correct args
        mock_callback.assert_called_once_with("Error Title", "Error Message")
    
    def test_show_error_without_callback(self, ui_controller):
        """Test that show_error logs a message when no callback is registered."""
        with patch.object(logging.getLogger('backend.systems.storage.ui_controller'), 'error') as mock_error:
            # Call method without registering callback
            ui_controller.show_error("Error Title", "Error Message")
            
            # Verify log message
            mock_error.assert_called_once()
            assert "Error: Error Title - Error Message" in mock_error.call_args[0][0]
    
    def test_show_notification_with_callback(self, ui_controller):
        """Test that show_notification calls the callback when registered."""
        # Create mock callback
        mock_callback = MagicMock()
        
        # Register callback
        ui_controller.register_callback('show_notification', mock_callback)
        
        # Call method
        ui_controller.show_notification("Notification Title", "Notification Message", 5000)
        
        # Verify callback was called with correct args
        mock_callback.assert_called_once_with("Notification Title", "Notification Message", 5000)
    
    def test_show_notification_without_callback(self, ui_controller):
        """Test that show_notification logs a message when no callback is registered."""
        with patch.object(logging.getLogger('backend.systems.storage.ui_controller'), 'info') as mock_info:
            # Call method without registering callback
            ui_controller.show_notification("Notification Title", "Notification Message", 5000)
            
            # Verify log message
            mock_info.assert_called_once()
            assert "Notification: Notification Title - Notification Message" in mock_info.call_args[0][0]
    
    def test_show_notification_default_duration(self, ui_controller):
        """Test that show_notification uses default duration when not specified."""
        # Create mock callback
        mock_callback = MagicMock()
        
        # Register callback
        ui_controller.register_callback('show_notification', mock_callback)
        
        # Call method without duration
        ui_controller.show_notification("Notification Title", "Notification Message")
        
        # Verify callback was called with default duration
        mock_callback.assert_called_once_with("Notification Title", "Notification Message", 3000)
    
    def test_show_autosave_notification(self, ui_controller):
        """Test that show_autosave_notification calls show_notification with appropriate args."""
        # Patch show_notification
        with patch.object(ui_controller, 'show_notification') as mock_notification:
            # Call method
            ui_controller.show_autosave_notification("12:34:56")
            
            # Verify show_notification was called with correct args
            mock_notification.assert_called_once_with(
                "Autosave",
                "Game autosaved at 12:34:56",
                2000
            )
    
    def test_show_checkpoint_notification(self, ui_controller):
        """Test that show_checkpoint_notification calls show_notification with appropriate args."""
        # Patch show_notification
        with patch.object(ui_controller, 'show_notification') as mock_notification:
            # Call method
            ui_controller.show_checkpoint_notification("Boss Fight")
            
            # Verify show_notification was called with correct args
            mock_notification.assert_called_once_with(
                "Checkpoint",
                "Checkpoint 'Boss Fight' created",
                3000
            ) 