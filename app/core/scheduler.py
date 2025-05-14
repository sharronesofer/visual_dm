"""
Scheduler module for managing background tasks.
"""

import logging
from typing import Callable, Dict, List, Optional
from datetime import datetime, timedelta
import threading
import time

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Manages scheduled tasks and their execution."""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
    def add_task(self, task_id: str, func: Callable, interval: int, *args, **kwargs) -> bool:
        """Add a task to be executed periodically."""
        if task_id in self.tasks:
            logger.warning(f"Task {task_id} already exists")
            return False
            
        self.tasks[task_id] = {
            'function': func,
            'interval': interval,
            'last_run': None,
            'args': args,
            'kwargs': kwargs,
            'enabled': True
        }
        logger.info(f"Added task {task_id} with interval {interval}s")
        return True
        
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the scheduler."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Removed task {task_id}")
            return True
        return False
        
    def enable_task(self, task_id: str) -> bool:
        """Enable a task."""
        if task_id in self.tasks:
            self.tasks[task_id]['enabled'] = True
            logger.info(f"Enabled task {task_id}")
            return True
        return False
        
    def disable_task(self, task_id: str) -> bool:
        """Disable a task."""
        if task_id in self.tasks:
            self.tasks[task_id]['enabled'] = False
            logger.info(f"Disabled task {task_id}")
            return True
        return False
        
    def _run_task(self, task_id: str, task: Dict) -> None:
        """Execute a single task."""
        try:
            task['function'](*task['args'], **task['kwargs'])
            task['last_run'] = datetime.utcnow()
            logger.debug(f"Successfully executed task {task_id}")
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self.running:
            now = datetime.utcnow()
            
            for task_id, task in self.tasks.items():
                if not task['enabled']:
                    continue
                    
                if task['last_run'] is None or \
                   (now - task['last_run']).total_seconds() >= task['interval']:
                    self._run_task(task_id, task)
                    
            time.sleep(1)  # Sleep for 1 second between checks
            
    def start(self) -> None:
        """Start the scheduler."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Scheduler started")
        
    def stop(self) -> None:
        """Stop the scheduler."""
        if not self.running:
            logger.warning("Scheduler is not running")
            return
            
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Scheduler stopped")

# Global scheduler instance
scheduler = TaskScheduler()

def init_scheduler(app=None) -> None:
    """Initialize and start the scheduler."""
    scheduler.start()

def cleanup_scheduler() -> None:
    """Stop the scheduler and clean up."""
    scheduler.stop() 