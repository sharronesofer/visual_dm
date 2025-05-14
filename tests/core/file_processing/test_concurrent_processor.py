"""Tests for the concurrent file processor."""

import pytest
import tempfile
import time
from pathlib import Path
from app.core.file_processing.concurrent_processor import (
    ConcurrentFileProcessor,
    FileOperationType,
    FileOperationPriority,
    FileOperationStatus
)
from app.core.file_processing.exceptions import (
    FileOperationError,
    QueueFullError,
    InvalidOperationError,
    OperationCancelledError,
    OperationTimeoutError,
    RetryExhaustedError
)

@pytest.fixture
def processor():
    """Create a file processor instance."""
    processor = ConcurrentFileProcessor(max_workers=2)
    processor.start()
    yield processor
    processor.cleanup()

@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

def test_basic_operations(processor, temp_dir):
    """Test basic file operations."""
    # Write
    test_content = "Hello, World!"
    test_file = temp_dir / "test.txt"
    op_id = processor.submit_operation(
        FileOperationType.WRITE,
        test_file,
        content=test_content
    )
    result = processor.wait_for_operation(op_id)
    assert result.status == FileOperationStatus.COMPLETED
    assert test_file.read_text() == test_content

    # Read
    op_id = processor.submit_operation(
        FileOperationType.READ,
        test_file
    )
    result = processor.wait_for_operation(op_id)
    assert result.status == FileOperationStatus.COMPLETED
    assert result.result == test_content

    # Copy
    copy_file = temp_dir / "test_copy.txt"
    op_id = processor.submit_operation(
        FileOperationType.COPY,
        test_file,
        destination=copy_file
    )
    result = processor.wait_for_operation(op_id)
    assert result.status == FileOperationStatus.COMPLETED
    assert copy_file.read_text() == test_content

    # Delete
    op_id = processor.submit_operation(
        FileOperationType.DELETE,
        test_file
    )
    result = processor.wait_for_operation(op_id)
    assert result.status == FileOperationStatus.COMPLETED
    assert not test_file.exists()

def test_error_handling(processor, temp_dir):
    """Test error handling scenarios."""
    non_existent = temp_dir / "non_existent.txt"
    
    # Try to read non-existent file
    op_id = processor.submit_operation(
        FileOperationType.READ,
        non_existent
    )
    result = processor.wait_for_operation(op_id)
    assert result.status == FileOperationStatus.FAILED
    assert isinstance(result.error, FileOperationError)
    
    # Try to write to invalid path
    invalid_path = temp_dir / "invalid" / "path.txt"
    op_id = processor.submit_operation(
        FileOperationType.WRITE,
        invalid_path,
        content="test"
    )
    result = processor.wait_for_operation(op_id)
    assert result.status == FileOperationStatus.FAILED
    assert isinstance(result.error, FileOperationError)

    # Test operation cancellation
    test_file = temp_dir / "cancel_test.txt"
    op_id = processor.submit_operation(
        FileOperationType.WRITE,
        test_file,
        content="test",
        priority=FileOperationPriority.LOW
    )
    processor.cancel_operation(op_id)
    result = processor.wait_for_operation(op_id)
    assert result.status == FileOperationStatus.CANCELLED
    assert isinstance(result.error, OperationCancelledError)

def test_retry_mechanism(processor, temp_dir):
    """Test operation retry mechanism."""
    test_file = temp_dir / "retry_test.txt"
    
    # Create a file that will fail on first attempt
    test_file.write_text("original")
    test_file.chmod(0o000)  # Make file unreadable
    
    op_id = processor.submit_operation(
        FileOperationType.READ,
        test_file,
        retry_count=3
    )
    
    time.sleep(0.1)  # Let first attempt fail
    test_file.chmod(0o644)  # Make file readable again
    
    result = processor.wait_for_operation(op_id)
    assert result.status == FileOperationStatus.COMPLETED
    assert result.result == "original"
    assert result.retries > 0

def test_performance_metrics(processor, temp_dir):
    """Test performance metrics collection."""
    # Generate some load
    files = []
    for i in range(10):
        test_file = temp_dir / f"test_{i}.txt"
        op_id = processor.submit_operation(
            FileOperationType.WRITE,
            test_file,
            content=f"Content {i}"
        )
        files.append((op_id, test_file))
    
    # Wait for all operations
    for op_id, _ in files:
        processor.wait_for_operation(op_id)
    
    # Check metrics
    metrics = processor.get_metrics()
    assert metrics["operations"]["total"] == 10
    assert metrics["operations"]["completed"] == 10
    assert metrics["operations"]["failed"] == 0
    assert metrics["performance"]["avg_duration"] > 0
    assert metrics["performance"]["operations_per_second"] > 0
    
    # Test error metrics
    non_existent = temp_dir / "non_existent.txt"
    op_id = processor.submit_operation(
        FileOperationType.READ,
        non_existent
    )
    processor.wait_for_operation(op_id)
    
    metrics = processor.get_metrics()
    assert metrics["operations"]["failed"] == 1
    assert len(metrics["errors"]["recent_errors"]) == 1
    assert metrics["errors"]["retry_rate"] >= 0

def test_priority_handling(processor, temp_dir):
    """Test priority-based operation handling."""
    results = []
    
    # Submit low priority operation first
    low_file = temp_dir / "low.txt"
    low_id = processor.submit_operation(
        FileOperationType.WRITE,
        low_file,
        content="low",
        priority=FileOperationPriority.LOW
    )
    
    # Submit high priority operation
    high_file = temp_dir / "high.txt"
    high_id = processor.submit_operation(
        FileOperationType.WRITE,
        high_file,
        content="high",
        priority=FileOperationPriority.HIGH
    )
    
    # High priority should complete first
    high_result = processor.wait_for_operation(high_id)
    assert high_result.status == FileOperationStatus.COMPLETED
    assert high_file.exists()
    
    low_result = processor.wait_for_operation(low_id)
    assert low_result.status == FileOperationStatus.COMPLETED
    assert low_file.exists()
    
    # Check metrics for priority distribution
    metrics = processor.get_metrics()
    assert metrics["operations"]["total"] == 2
    assert metrics["operations"]["completed"] == 2 