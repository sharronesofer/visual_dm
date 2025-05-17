import pytest
import os
import json
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logger import Logger, LogLevel, ConsoleLogHandler, JsonLogHandler, AsyncLogHandler

def test_logger_initialization():
    """Test basic logger initialization"""
    logger = Logger()
    assert logger is not None
    assert logger.level == LogLevel.INFO
    
def test_log_levels():
    """Test that log levels work correctly"""
    logger = Logger(level=LogLevel.DEBUG)
    assert logger.level == LogLevel.DEBUG
    
    logger.set_level(LogLevel.WARNING)
    assert logger.level == LogLevel.WARNING
    
def test_child_logger():
    """Test that child loggers inherit from parent"""
    parent = Logger(level=LogLevel.INFO, prefix="parent")
    child = parent.child("child", {"extra": "data"})
    
    assert child.level == parent.level
    assert child.prefix == "parent:child"
    assert "extra" in child.metadata
    
@patch('sys.stdout')
def test_console_logging(mock_stdout):
    """Test console logging functionality"""
    logger = Logger(level=LogLevel.DEBUG, enable_console=True)
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warn("Warning message")
    logger.error("Error message")
    
    # Check that calls were made to stdout
    assert mock_stdout.write.call_count > 0
    
def test_json_logging():
    """Test JSON logging functionality"""
    # Create temp file for log output
    temp_dir = tempfile.mkdtemp()
    log_path = os.path.join(temp_dir, "test.log")
    
    # Configure logger with JSON output
    logger = Logger(
        level=LogLevel.DEBUG,
        enable_console=False,
        enable_json=True,
        json_log_path=log_path
    )
    
    # Log some messages
    logger.debug("Debug message", {"context": "test"})
    logger.info("Info message")
    logger.warn("Warning message")
    logger.error("Error message", Exception("Test error"))
    
    # Check log file exists and has content
    assert os.path.exists(log_path)
    
    with open(log_path, 'r') as f:
        log_lines = f.readlines()
    
    # Check that we have at least 3 log entries (debug might be filtered)
    assert len(log_lines) >= 3
    
    # Check that the log entries are valid JSON
    for line in log_lines:
        entry = json.loads(line)
        assert 'level' in entry
        assert 'message' in entry
        assert 'timestamp' in entry
    
    # Clean up
    os.remove(log_path)
    os.rmdir(temp_dir)
    
@pytest.mark.asyncio
async def test_async_logging():
    """Test async logging functionality"""
    # Create a mock handler to check calls
    mock_handler = MagicMock()
    
    # Create an async wrapper around it
    async_handler = AsyncLogHandler(mock_handler)
    
    # Create the entry to log
    entry = {
        'level': 'info',
        'message': 'Test message',
        'timestamp': '2023-01-01T00:00:00Z'
    }
    
    # Handle the entry
    async_handler.handle(entry)
    
    # Need to wait a bit for the async handling to complete
    await asyncio.sleep(0.1)
    
    # Stop the handler
    async_handler.stop()
    
    # Wait a bit more for cleanup
    await asyncio.sleep(0.1)
    
    # Check that the wrapped handler was called
    mock_handler.handle.assert_called_with(entry)
    
def test_error_handling():
    """Test error logging with exceptions"""
    logger = Logger(level=LogLevel.DEBUG, enable_console=True)
    
    try:
        # Generate an exception
        raise ValueError("Test exception")
    except Exception as e:
        # Log the exception
        logger.error("An error occurred", error=e)
        
    # No assertion needed, just checking it doesn't crash

if __name__ == "__main__":
    # Run the tests directly
    test_logger_initialization()
    test_log_levels()
    test_child_logger()
    
    # Can't run patched methods directly in main
    # Create a mock for console test to use manually
    stdout_mock = MagicMock()
    with patch('sys.stdout', stdout_mock):
        test_console_logging()
        
    test_json_logging()
    
    # Can't run async test directly
    # test_async_logging()
    
    test_error_handling()
    
    print("All tests passed!") 