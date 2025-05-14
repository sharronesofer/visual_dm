"""
Background task management system with prioritization and error handling.
"""

import logging
import threading
import queue
import time
from typing import Dict, Any, Optional, Callable, List
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime, timedelta
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = auto()  # Must be executed immediately
    HIGH = auto()      # High priority tasks
    NORMAL = auto()    # Regular priority tasks
    LOW = auto()       # Low priority tasks
    BACKGROUND = auto() # Background tasks that can be delayed

class TaskStatus(Enum):
    """Task status states."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()

@dataclass
class Task:
    """Task data structure."""
    id: str
    func: Callable
    args: tuple
    kwargs: Dict[str, Any]
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    scheduled_for: Optional[datetime]
    retry_count: int
    max_retries: int
    error: Optional[Exception]
    result: Optional[Any]

class TaskManager:
    """Manages background tasks with prioritization and error handling."""
    
    def __init__(self, max_workers: int = 4):
        """Initialize the task manager.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        try:
            self.max_workers = max_workers
            self.task_queue = queue.PriorityQueue()
            self.tasks: Dict[str, Task] = {}
            self.workers: List[threading.Thread] = []
            self.running = False
            self.lock = threading.Lock()
            
            # Initialize worker threads
            self._init_workers()
            
            logger.info("Task manager initialized successfully")
            
        except Exception as e:
            handle_component_error(
                "TaskManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def _init_workers(self) -> None:
        """Initialize worker threads."""
        try:
            for i in range(self.max_workers):
                worker = threading.Thread(
                    target=self._worker_loop,
                    name=f"TaskWorker-{i}",
                    daemon=True
                )
                self.workers.append(worker)
                
        except Exception as e:
            handle_component_error(
                "TaskManager",
                "_init_workers",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def _worker_loop(self) -> None:
        """Worker thread main loop."""
        try:
            while self.running:
                try:
                    # Get task from queue with timeout
                    priority, task_id = self.task_queue.get(timeout=1)
                    task = self.tasks.get(task_id)
                    
                    if task is None:
                        continue
                        
                    # Update task status
                    with self.lock:
                        task.status = TaskStatus.RUNNING
                        
                    try:
                        # Execute task
                        result = task.func(*task.args, **task.kwargs)
                        
                        # Update task status and result
                        with self.lock:
                            task.status = TaskStatus.COMPLETED
                            task.result = result
                            
                    except Exception as e:
                        # Handle task failure
                        with self.lock:
                            task.status = TaskStatus.FAILED
                            task.error = e
                            
                            # Retry if possible
                            if task.retry_count < task.max_retries:
                                task.retry_count += 1
                                task.status = TaskStatus.PENDING
                                self._schedule_task(task)
                                
                    finally:
                        self.task_queue.task_done()
                        
                except queue.Empty:
                    continue
                    
        except Exception as e:
            handle_component_error(
                "TaskManager",
                "_worker_loop",
                e,
                ErrorSeverity.ERROR
            )
            
    def _schedule_task(self, task: Task) -> None:
        """Schedule a task for execution.
        
        Args:
            task: Task to schedule
        """
        try:
            # Calculate priority score
            priority_score = (
                task.priority.value * 1000 +  # Priority weight
                (datetime.now() - task.created_at).total_seconds()  # Age weight
            )
            
            # Add to queue
            self.task_queue.put((priority_score, task.id))
            
        except Exception as e:
            handle_component_error(
                "TaskManager",
                "_schedule_task",
                e,
                ErrorSeverity.ERROR
            )
            
    def submit_task(
        self,
        func: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        scheduled_for: Optional[datetime] = None,
        **kwargs
    ) -> str:
        """Submit a new task for execution.
        
        Args:
            func: Function to execute
            args: Positional arguments
            priority: Task priority
            max_retries: Maximum number of retries
            scheduled_for: Scheduled execution time
            kwargs: Keyword arguments
            
        Returns:
            Task ID
        """
        try:
            # Create task
            task_id = f"task-{time.time()}-{len(self.tasks)}"
            task = Task(
                id=task_id,
                func=func,
                args=args,
                kwargs=kwargs,
                priority=priority,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                scheduled_for=scheduled_for,
                retry_count=0,
                max_retries=max_retries,
                error=None,
                result=None
            )
            
            # Add to tasks
            with self.lock:
                self.tasks[task_id] = task
                
            # Schedule task
            self._schedule_task(task)
            
            return task_id
            
        except Exception as e:
            handle_component_error(
                "TaskManager",
                "submit_task",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get task status.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status if found, None otherwise
        """
        try:
            with self.lock:
                task = self.tasks.get(task_id)
                return task.status if task else None
                
        except Exception as e:
            handle_component_error(
                "TaskManager",
                "get_task_status",
                e,
                ErrorSeverity.ERROR
            )
            return None
            
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get task result.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task result if completed, None otherwise
        """
        try:
            with self.lock:
                task = self.tasks.get(task_id)
                return task.result if task and task.status == TaskStatus.COMPLETED else None
                
        except Exception as e:
            handle_component_error(
                "TaskManager",
                "get_task_result",
                e,
                ErrorSeverity.ERROR
            )
            return None
            
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if task was cancelled, False otherwise
        """
        try:
            with self.lock:
                task = self.tasks.get(task_id)
                if task and task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.CANCELLED
                    return True
                return False
                
        except Exception as e:
            handle_component_error(
                "TaskManager",
                "cancel_task",
                e,
                ErrorSeverity.ERROR
            )
            return False
            
    def start(self) -> None:
        """Start the task manager."""
        try:
            self.running = True
            for worker in self.workers:
                worker.start()
                
            logger.info("Task manager started")
            
        except Exception as e:
            handle_component_error(
                "TaskManager",
                "start",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def stop(self) -> None:
        """Stop the task manager."""
        try:
            self.running = False
            for worker in self.workers:
                worker.join()
                
            logger.info("Task manager stopped")
            
        except Exception as e:
            handle_component_error(
                "TaskManager",
                "stop",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def cleanup(self) -> None:
        """Clean up task manager resources."""
        try:
            self.stop()
            with self.lock:
                self.tasks.clear()
                
            logger.info("Task manager cleaned up")
            
        except Exception as e:
            handle_component_error(
                "TaskManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            ) 