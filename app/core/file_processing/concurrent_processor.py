"""
Concurrent file processing system using worker threads.

This module implements a thread pool-based system for concurrent file operations,
with support for prioritization, error handling, and performance monitoring.
"""

import logging
import threading
import queue
import time
from typing import Dict, Any, Optional, Callable, List, Union
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import os
import shutil
import uuid
from app.core.file_processing.metrics import MetricsCollector

logger = logging.getLogger(__name__)

class FileOperationType(Enum):
    """Types of file operations supported by the processor."""
    READ = auto()
    WRITE = auto()
    COPY = auto()
    DELETE = auto()
    MOVE = auto()
    APPEND = auto()

class FileOperationPriority(Enum):
    """Priority levels for file operations."""
    LOW = 0
    NORMAL = 1
    HIGH = 2

class FileOperationStatus(Enum):
    """Status of a file operation."""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()

@dataclass
class FileOperation:
    """Represents a file operation with its metadata."""
    id: str
    type: FileOperationType
    source_path: Path
    target_path: Optional[Path]
    priority: FileOperationPriority
    content: Optional[Union[str, bytes]]
    max_retries: int
    status: FileOperationStatus
    result: Optional[Any]
    error: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    retry_count: int

class ConcurrentFileProcessor:
    """
    A thread pool-based system for concurrent file operations.
    
    Features:
    - Priority-based operation scheduling
    - Automatic retry mechanism
    - Operation cancellation
    - Performance metrics tracking
    - Thread-safe operation handling
    """
    
    def __init__(self, max_workers: int = 4, queue_size: int = 100):
        """
        Initialize the processor.
        
        Args:
            max_workers: Maximum number of worker threads
            queue_size: Maximum size of the operation queue
        """
        self.max_workers = max_workers
        self.queue_size = queue_size
        
        # Initialize queues for different priority levels
        self.queues = {
            FileOperationPriority.HIGH: queue.PriorityQueue(queue_size),
            FileOperationPriority.NORMAL: queue.PriorityQueue(queue_size),
            FileOperationPriority.LOW: queue.PriorityQueue(queue_size)
        }
        
        # Thread management
        self.workers: List[threading.Thread] = []
        self.stop_event = threading.Event()
        
        # Operation tracking
        self.operations: Dict[str, FileOperation] = {}
        self.operations_lock = threading.Lock()
        
        # Metrics
        self.metrics_collector = MetricsCollector()
    
    def start(self):
        """Start the worker threads."""
        logger.info(f"Starting {self.max_workers} worker threads")
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def cleanup(self):
        """Stop all workers and clean up resources."""
        logger.info("Stopping worker threads")
        self.stop_event.set()
        for worker in self.workers:
            worker.join()
        self.workers.clear()
    
    def submit_operation(
        self,
        operation_type: FileOperationType,
        source_path: Union[str, Path],
        target_path: Optional[Union[str, Path]] = None,
        priority: FileOperationPriority = FileOperationPriority.NORMAL,
        content: Optional[Union[str, bytes]] = None,
        max_retries: int = 3
    ) -> str:
        """
        Submit a file operation for processing.
        
        Args:
            operation_type: Type of operation to perform
            source_path: Path to the source file
            target_path: Path to the target file (for copy/move operations)
            priority: Operation priority
            content: Content to write (for write/append operations)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Operation ID for tracking the operation
        """
        # Convert paths to Path objects
        source_path = Path(source_path)
        target_path = Path(target_path) if target_path else None
        
        # Create operation object
        operation_id = str(uuid.uuid4())
        operation = FileOperation(
            id=operation_id,
            type=operation_type,
            source_path=source_path,
            target_path=target_path,
            priority=priority,
            content=content,
            max_retries=max_retries,
            status=FileOperationStatus.PENDING,
            result=None,
            error=None,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            retry_count=0
        )
        
        # Store operation
        with self.operations_lock:
            self.operations[operation_id] = operation
        
        # Add to appropriate queue with priority
        try:
            self.queues[priority].put((priority.value, operation_id))
            logger.debug(f"Submitted operation {operation_id} with priority {priority}")
            
            return operation_id
            
        except queue.Full:
            logger.error("Operation queue is full")
            with self.operations_lock:
                operation.status = FileOperationStatus.FAILED
                operation.error = "Queue is full"
            raise RuntimeError("Operation queue is full")
    
    def cancel_operation(self, operation_id: str) -> bool:
        """
        Attempt to cancel a pending operation.
        
        Args:
            operation_id: ID of the operation to cancel
            
        Returns:
            True if operation was cancelled, False if already in progress/completed
        """
        with self.operations_lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            if operation.status == FileOperationStatus.PENDING:
                operation.status = FileOperationStatus.CANCELLED
                operation.completed_at = datetime.now()
                
                return True
            
            return False
    
    def get_operation_status(self, operation_id: str) -> Optional[FileOperationStatus]:
        """Get the current status of an operation."""
        with self.operations_lock:
            operation = self.operations.get(operation_id)
            return operation.status if operation else None
    
    def get_operation_result(self, operation_id: str) -> Optional[Any]:
        """Get the result of a completed operation."""
        with self.operations_lock:
            operation = self.operations.get(operation_id)
            return operation.result if operation else None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics (rolling window, detailed)."""
        return self.metrics_collector.get_metrics()
    
    def _worker_loop(self):
        """Main worker thread loop."""
        while not self.stop_event.is_set():
            operation = None
            operation_id = None
            
            # Try to get operation from queues in priority order
            for priority in sorted(FileOperationPriority, key=lambda p: p.value, reverse=True):
                try:
                    _, operation_id = self.queues[priority].get_nowait()
                    break
                except queue.Empty:
                    continue
            
            if not operation_id:
                time.sleep(0.1)  # Prevent busy waiting
                continue
            
            # Get operation details
            with self.operations_lock:
                operation = self.operations.get(operation_id)
                if not operation or operation.status == FileOperationStatus.CANCELLED:
                    continue
                operation.status = FileOperationStatus.IN_PROGRESS
                operation.started_at = datetime.now()
            
            # Process operation with metrics
            op_metrics = self.metrics_collector.record_operation_start(str(operation.type))
            try:
                result = self._process_operation(operation)
                with self.operations_lock:
                    operation.status = FileOperationStatus.COMPLETED
                    operation.result = result
                    operation.completed_at = datetime.now()
                self.metrics_collector.record_operation_end(op_metrics, "completed")
            except Exception as e:
                logger.error(f"Error processing operation {operation_id}: {str(e)}")
                if operation.retry_count < operation.max_retries:
                    # Retry operation
                    operation.retry_count += 1
                    operation.status = FileOperationStatus.PENDING
                    self.metrics_collector.record_retry(op_metrics)
                    self.queues[operation.priority].put((operation.priority.value, operation_id))
                else:
                    # Mark as failed
                    with self.operations_lock:
                        operation.status = FileOperationStatus.FAILED
                        operation.error = str(e)
                        operation.completed_at = datetime.now()
                    self.metrics_collector.record_operation_end(op_metrics, "failed", error=str(e))
    
    def _process_operation(self, operation: FileOperation) -> Any:
        """
        Process a single file operation.
        
        Args:
            operation: Operation to process
            
        Returns:
            Operation result
            
        Raises:
            Various exceptions based on operation type and failures
        """
        if operation.type == FileOperationType.READ:
            return operation.source_path.read_bytes()
            
        elif operation.type == FileOperationType.WRITE:
            if isinstance(operation.content, str):
                operation.source_path.write_text(operation.content)
            else:
                operation.source_path.write_bytes(operation.content)
            return None
            
        elif operation.type == FileOperationType.COPY:
            shutil.copy2(operation.source_path, operation.target_path)
            return None
            
        elif operation.type == FileOperationType.MOVE:
            shutil.move(operation.source_path, operation.target_path)
            return None
            
        elif operation.type == FileOperationType.DELETE:
            operation.source_path.unlink()
            return None
            
        elif operation.type == FileOperationType.APPEND:
            mode = 'ab' if isinstance(operation.content, bytes) else 'a'
            with open(operation.source_path, mode) as f:
                f.write(operation.content)
            return None
            
        else:
            raise ValueError(f"Unsupported operation type: {operation.type}") 