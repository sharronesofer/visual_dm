"""
Tests for the centralized logging configuration system.

This module tests the functionality of the centralized logging configuration
system, including environment-based configuration, format selection, and metadata
inclusion.
"""

import os
import json
import logging
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from app.core.logging.config import (
    LoggingConfig, 
    LogLevel, 
    LogFormat, 
    JsonFormatter, 
    ColorizedFormatter,
    configure_logger,
    update_configuration
)
from app.core.logging.handlers import get_logger, log_with_context


class TestLoggingConfig(unittest.TestCase):
    """Test the logging configuration system."""
    
    def setUp(self):
        """Set up the test environment."""
        # Save original environment variables
        self.original_env = {}
        for key in os.environ:
            if key.startswith('LOG_'):
                self.original_env[key] = os.environ[key]
                
        # Clear environment variables for testing
        for key in list(os.environ.keys()):
            if key.startswith('LOG_'):
                del os.environ[key]
    
    def tearDown(self):
        """Restore the test environment."""
        # Restore original environment variables
        for key in list(os.environ.keys()):
            if key.startswith('LOG_'):
                del os.environ[key]
                
        for key, value in self.original_env.items():
            os.environ[key] = value
    
    def test_default_config_values(self):
        """Test that default configuration values are set correctly."""
        config = LoggingConfig()
        
        # Check default values
        self.assertEqual(config.level, logging.INFO)
        self.assertEqual(config.format, LogFormat.JSON)
        self.assertTrue(config.colorize)
        self.assertFalse(config.file_enabled)
        self.assertEqual(config.file_path, "logs/app.log")
        self.assertEqual(config.max_bytes, 10485760)  # 10MB
        self.assertEqual(config.backup_count, 5)
        self.assertTrue(config.console_enabled)
        
        # Check required fields
        self.assertIn("timestamp", config.required_fields)
        self.assertIn("level", config.required_fields)
        self.assertIn("message", config.required_fields)
        self.assertIn("logger_name", config.required_fields)
    
    def test_env_var_configuration(self):
        """Test that environment variables override default configuration."""
        # Set environment variables
        os.environ['LOG_LEVEL'] = 'debug'
        os.environ['LOG_FORMAT'] = 'pretty'
        os.environ['LOG_COLORIZE'] = 'false'
        os.environ['LOG_FILE_ENABLED'] = 'true'
        os.environ['LOG_FILE_PATH'] = 'test.log'
        os.environ['LOG_MAX_BYTES'] = '1000'
        os.environ['LOG_BACKUP_COUNT'] = '3'
        os.environ['LOG_CONSOLE_ENABLED'] = 'false'
        os.environ['LOG_ADDITIONAL_FIELDS'] = 'user_id,request_id,correlation_id'
        
        # Create new config that reads from environment
        config = LoggingConfig()
        
        # Check values from environment
        self.assertEqual(config.level, logging.DEBUG)
        self.assertEqual(config.format, LogFormat.PRETTY)
        self.assertFalse(config.colorize)
        self.assertTrue(config.file_enabled)
        self.assertEqual(config.file_path, "test.log")
        self.assertEqual(config.max_bytes, 1000)
        self.assertEqual(config.backup_count, 3)
        self.assertFalse(config.console_enabled)
        
        # Check additional fields
        self.assertEqual(len(config.additional_fields), 3)
        self.assertIn("user_id", config.additional_fields)
        self.assertIn("request_id", config.additional_fields)
        self.assertIn("correlation_id", config.additional_fields)
    
    def test_update_configuration(self):
        """Test updating configuration values."""
        config = LoggingConfig()
        
        # Original values
        self.assertEqual(config.level, logging.INFO)
        self.assertEqual(config.format, LogFormat.JSON)
        
        # Update configuration
        config.update(level="debug", format="pretty")
        
        # Check updated values
        self.assertEqual(config.level, logging.DEBUG)
        self.assertEqual(config.format, LogFormat.PRETTY)


class TestLogFormatters(unittest.TestCase):
    """Test the log formatters."""
    
    def setUp(self):
        """Set up the test environment."""
        self.config = LoggingConfig()
        self.json_formatter = JsonFormatter(self.config)
        self.colorized_formatter = ColorizedFormatter(self.config)
        
        # Create a sample log record
        self.log_record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add extra data to the record
        self.log_record.extra = {
            "user_id": "user123",
            "request_id": "req456"
        }
    
    def test_json_formatter(self):
        """Test that the JSON formatter produces valid JSON with all required fields."""
        # Format the record
        formatted = self.json_formatter.format(self.log_record)
        
        # Parse the JSON to verify it's valid
        log_data = json.loads(formatted)
        
        # Check required fields
        self.assertIn("timestamp", log_data)
        self.assertIn("level", log_data)
        self.assertIn("message", log_data)
        self.assertIn("logger_name", log_data)
        
        # Check content
        self.assertEqual(log_data["level"], "info")
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["logger_name"], "test_logger")
        
        # Check extra fields
        self.assertIn("user_id", log_data)
        self.assertIn("request_id", log_data)
        self.assertEqual(log_data["user_id"], "user123")
        self.assertEqual(log_data["request_id"], "req456")
    
    def test_colorized_formatter(self):
        """Test that the colorized formatter produces a string with the required content."""
        # Format the record with colorization disabled for testing
        self.config.update(colorize=False)
        formatted = self.colorized_formatter.format(self.log_record)
        
        # Check content
        self.assertIn("Test message", formatted)
        self.assertIn("INFO", formatted)
        self.assertIn("test_logger", formatted)
        
        # Check extra fields
        self.assertIn("user_id=user123", formatted)
        self.assertIn("request_id=req456", formatted)


class TestLoggerConfiguration(unittest.TestCase):
    """Test configuring loggers with the logging system."""
    
    def test_configure_logger(self):
        """Test that loggers are properly configured."""
        # Create a logger
        logger = logging.getLogger("test_logger")
        
        # Configure it
        configure_logger(logger)
        
        # Check that it has the right level
        self.assertEqual(logger.level, logging.INFO)
        
        # Check that it has handlers
        self.assertTrue(logger.handlers)
        
        # Clean up
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    
    def test_get_logger(self):
        """Test getting a configured logger."""
        # Get a logger
        logger = get_logger("test_module")
        
        # Check that it's properly configured
        self.assertEqual(logger.level, logging.INFO)
        self.assertTrue(logger.handlers)
        
        # Check that getting the same logger returns the cached instance
        logger2 = get_logger("test_module")
        self.assertIs(logger, logger2)
        
        # Clean up
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)


class TestLoggingWithContext(unittest.TestCase):
    """Test logging with additional context."""
    
    def setUp(self):
        """Set up a StringIO handler for testing log output."""
        # Create a StringIO to capture log output
        self.log_stream = StringIO()
        
        # Create a handler that writes to the StringIO
        self.handler = logging.StreamHandler(self.log_stream)
        self.handler.setFormatter(JsonFormatter(LoggingConfig()))
        
        # Get a logger and add the handler
        self.logger = get_logger("test_context")
        
        # Remove any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            
        # Add our test handler
        self.logger.addHandler(self.handler)
        
        # Set level to DEBUG to capture all logs
        self.logger.setLevel(logging.DEBUG)
    
    def test_log_with_context(self):
        """Test that context data is included in log records."""
        # Log with context
        log_with_context(
            logging.INFO,
            "Test message with context",
            self.logger,
            user_id="user123",
            request_id="req456",
            extra_field="some_value"
        )
        
        # Get the log output
        log_output = self.log_stream.getvalue()
        
        # Parse the JSON
        log_data = json.loads(log_output)
        
        # Check message
        self.assertEqual(log_data["message"], "Test message with context")
        
        # Check context
        self.assertEqual(log_data["user_id"], "user123")
        self.assertEqual(log_data["request_id"], "req456")
        self.assertEqual(log_data["extra_field"], "some_value")


if __name__ == "__main__":
    unittest.main() 