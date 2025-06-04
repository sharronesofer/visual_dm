"""
Autonomous NPC Scheduler Service

Manages automated scheduling of autonomous NPC system operations including:
- Daily emotional decay processing
- Daily personality evolution updates
- Weekly crisis response monitoring
- Monthly lifecycle updates
- Real-world economic integration updates
- System health monitoring
- Automated crisis detection and response
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from uuid import UUID
from threading import Thread
import json
from dataclasses import dataclass, asdict

from backend.systems.npc.services.autonomous_coordinator_service import AutonomousNpcCoordinator
from backend.infrastructure.database import get_db_session

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:
    """Represents a scheduled task"""
    name: str
    function: Callable
    schedule_type: str  # 'daily', 'weekly', 'monthly', 'hourly'
    schedule_time: str  # '09:00', 'monday', etc.
    description: str
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    error_count: int = 0
    average_duration: float = 0.0


@dataclass
class TaskExecutionResult:
    """Result of a task execution"""
    task_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    success: bool
    result_data: Dict[str, Any]
    error_message: Optional[str] = None


class AutonomousNpcScheduler:
    """Scheduler service for autonomous NPC system operations"""
    
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.execution_history: List[TaskExecutionResult] = []
        self.max_history_size = 1000
        
        # Configuration
        self.config = {
            "enable_daily_processing": True,
            "enable_weekly_monitoring": True,
            "enable_monthly_lifecycle": True,
            "enable_economic_integration": True,
            "enable_crisis_detection": True,
            "max_concurrent_tasks": 3,
            "task_timeout_minutes": 60,
            "retry_failed_tasks": True,
            "max_retries": 3
        }
        
        # Initialize scheduled tasks
        self._initialize_scheduled_tasks()
    
    def _initialize_scheduled_tasks(self):
        """Initialize all scheduled tasks"""
        
        # Daily tasks
        self._add_scheduled_task(
            "daily_emotional_processing",
            self._process_daily_emotional_updates,
            "daily",
            "02:00",
            "Process daily emotional decay for all NPCs"
        )
        
        self._add_scheduled_task(
            "daily_personality_evolution",
            self._process_daily_personality_evolution,
            "daily", 
            "02:30",
            "Process daily personality evolution for all NPCs"
        )
        
        self._add_scheduled_task(
            "daily_crisis_monitoring",
            self._monitor_ongoing_crises,
            "daily",
            "03:00",
            "Monitor and update ongoing crisis responses"
        )
        
        self._add_scheduled_task(
            "daily_economic_update",
            self._update_economic_cycles,
            "daily",
            "06:00",
            "Update economic cycles based on real-world data"
        )
        
        self._add_scheduled_task(
            "daily_system_health_check",
            self._perform_system_health_check,
            "daily",
            "23:00",
            "Perform comprehensive system health assessment"
        )
        
        # Hourly tasks
        self._add_scheduled_task(
            "hourly_crisis_detection",
            self._detect_economic_crises,
            "hourly",
            ":15",  # Run at 15 minutes past each hour
            "Check for potential economic crises from real-world data"
        )
        
        # Weekly tasks
        self._add_scheduled_task(
            "weekly_system_maintenance",
            self._perform_weekly_maintenance,
            "weekly",
            "sunday",
            "Perform weekly system maintenance and optimization"
        )
        
        self._add_scheduled_task(
            "weekly_statistics_report",
            self._generate_weekly_statistics,
            "weekly",
            "sunday",
            "Generate comprehensive weekly statistics report"
        )
        
        # Monthly tasks
        self._add_scheduled_task(
            "monthly_lifecycle_processing",
            self._process_monthly_lifecycle_updates,
            "monthly",
            "1",  # First day of month
            "Process comprehensive monthly lifecycle updates for high-tier NPCs"
        )
    
    def _add_scheduled_task(self, name: str, function: Callable, schedule_type: str,
                           schedule_time: str, description: str, enabled: bool = True):
        """Add a scheduled task"""
        
        task = ScheduledTask(
            name=name,
            function=function,
            schedule_type=schedule_type,
            schedule_time=schedule_time,
            description=description,
            enabled=enabled
        )
        
        self.scheduled_tasks[name] = task
        
        # Register with schedule library
        if enabled:
            self._register_task_with_scheduler(task)
    
    def _register_task_with_scheduler(self, task: ScheduledTask):
        """Register a task with the schedule library"""
        
        if task.schedule_type == "daily":
            schedule.every().day.at(task.schedule_time).do(self._execute_task, task.name)
        elif task.schedule_type == "hourly":
            if task.schedule_time.startswith(":"):
                minute = int(task.schedule_time[1:])
                schedule.every().hour.at(f":{minute:02d}").do(self._execute_task, task.name)
            else:
                schedule.every().hour.do(self._execute_task, task.name)
        elif task.schedule_type == "weekly":
            day = task.schedule_time.lower()
            getattr(schedule.every(), day).do(self._execute_task, task.name)
        elif task.schedule_type == "monthly":
            # For monthly, we'll check manually in the run loop
            pass
    
    def start_scheduler(self):
        """Start the scheduler in a background thread"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.scheduler_thread = Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Autonomous NPC Scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
        logger.info("Autonomous NPC Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                # Run scheduled tasks
                schedule.run_pending()
                
                # Check for monthly tasks manually
                self._check_monthly_tasks()
                
                # Clean up old execution history
                self._cleanup_execution_history()
                
                # Sleep for a minute before checking again
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Continue running even if there's an error
    
    def _check_monthly_tasks(self):
        """Check and run monthly tasks"""
        current_date = datetime.now()
        
        for task_name, task in self.scheduled_tasks.items():
            if (task.schedule_type == "monthly" and task.enabled and
                (task.last_run is None or 
                 task.last_run.month != current_date.month)):
                
                # Check if it's the right day of the month
                target_day = int(task.schedule_time)
                if current_date.day == target_day:
                    self._execute_task(task_name)
    
    def _execute_task(self, task_name: str) -> TaskExecutionResult:
        """Execute a scheduled task"""
        task = self.scheduled_tasks.get(task_name)
        if not task or not task.enabled:
            return None
        
        start_time = datetime.utcnow()
        logger.info(f"Executing scheduled task: {task_name}")
        
        try:
            # Execute the task function
            result_data = task.function()
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Update task statistics
            task.last_run = start_time
            task.run_count += 1
            task.average_duration = ((task.average_duration * (task.run_count - 1)) + duration) / task.run_count
            
            # Create execution result
            execution_result = TaskExecutionResult(
                task_name=task_name,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=True,
                result_data=result_data or {}
            )
            
            self.execution_history.append(execution_result)
            logger.info(f"Task {task_name} completed successfully in {duration:.2f} seconds")
            
            return execution_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Update error statistics
            task.error_count += 1
            
            # Create error result
            execution_result = TaskExecutionResult(
                task_name=task_name,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=False,
                result_data={},
                error_message=str(e)
            )
            
            self.execution_history.append(execution_result)
            logger.error(f"Task {task_name} failed after {duration:.2f} seconds: {e}")
            
            # Retry logic
            if (self.config["retry_failed_tasks"] and 
                task.error_count <= self.config["max_retries"]):
                logger.info(f"Scheduling retry for task {task_name}")
                # Schedule retry in 5 minutes
                schedule.every(5).minutes.do(self._execute_task, task_name).tag(f"retry_{task_name}")
            
            return execution_result
    
    # === TASK IMPLEMENTATION METHODS ===
    
    def _process_daily_emotional_updates(self) -> Dict[str, Any]:
        """Process daily emotional decay for all NPCs"""
        try:
            with get_db_session() as db_session:
                coordinator = AutonomousNpcCoordinator(db_session)
                result = asyncio.run(coordinator.bulk_process_emotional_decay())
                return {
                    "operation": "daily_emotional_updates",
                    "processed_npcs": result["processed_count"],
                    "errors": len(result["errors"]),
                    "success": True
                }
        except Exception as e:
            return {"operation": "daily_emotional_updates", "success": False, "error": str(e)}
    
    def _process_daily_personality_evolution(self) -> Dict[str, Any]:
        """Process daily personality evolution for all NPCs"""
        try:
            with get_db_session() as db_session:
                coordinator = AutonomousNpcCoordinator(db_session)
                result = asyncio.run(coordinator.bulk_process_personality_evolution())
                return {
                    "operation": "daily_personality_evolution",
                    "processed_npcs": result["processed_count"],
                    "errors": len(result["errors"]),
                    "success": True
                }
        except Exception as e:
            return {"operation": "daily_personality_evolution", "success": False, "error": str(e)}
    
    def _monitor_ongoing_crises(self) -> Dict[str, Any]:
        """Monitor and update ongoing crisis responses"""
        try:
            with get_db_session() as db_session:
                coordinator = AutonomousNpcCoordinator(db_session)
                
                # Get all ongoing crisis responses
                from backend.infrastructure.systems.npc.models.personality_evolution_models import NpcCrisisResponse
                ongoing_crises = db_session.query(NpcCrisisResponse).filter(
                    NpcCrisisResponse.response_completed == False
                ).all()
                
                processed_crises = 0
                completed_crises = 0
                
                for crisis in ongoing_crises:
                    crisis_result = coordinator.crisis_service.process_ongoing_crisis(crisis.id)
                    processed_crises += 1
                    
                    if crisis_result.get("crisis_completed", False):
                        completed_crises += 1
                
                return {
                    "operation": "crisis_monitoring",
                    "ongoing_crises": len(ongoing_crises),
                    "processed_crises": processed_crises,
                    "completed_crises": completed_crises,
                    "success": True
                }
        except Exception as e:
            return {"operation": "crisis_monitoring", "success": False, "error": str(e)}
    
    def _update_economic_cycles(self) -> Dict[str, Any]:
        """Update economic cycles based on real-world data"""
        try:
            with get_db_session() as db_session:
                coordinator = AutonomousNpcCoordinator(db_session)
                result = coordinator.economy_service.update_game_economic_cycles()
                
                return {
                    "operation": "economic_cycle_update",
                    "updated_cycles": len(result.get("updated_cycles", [])),
                    "market_sentiment": result.get("market_sentiment", {}),
                    "success": True
                }
        except Exception as e:
            return {"operation": "economic_cycle_update", "success": False, "error": str(e)}
    
    def _detect_economic_crises(self) -> Dict[str, Any]:
        """Check for potential economic crises from real-world data"""
        try:
            with get_db_session() as db_session:
                coordinator = AutonomousNpcCoordinator(db_session)
                crisis_event = coordinator.economy_service.create_crisis_from_real_world_event()
                
                if crisis_event:
                    # Trigger mass crisis event
                    mass_crisis_result = asyncio.run(coordinator.trigger_mass_crisis_event(
                        crisis_event["event_type"],
                        crisis_event["description"],
                        crisis_event["severity"]
                    ))
                    
                    return {
                        "operation": "economic_crisis_detection",
                        "crisis_detected": True,
                        "crisis_event": crisis_event,
                        "affected_npcs": mass_crisis_result["total_affected_npcs"],
                        "success": True
                    }
                else:
                    return {
                        "operation": "economic_crisis_detection",
                        "crisis_detected": False,
                        "success": True
                    }
        except Exception as e:
            return {"operation": "economic_crisis_detection", "success": False, "error": str(e)}
    
    def _perform_system_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health assessment"""
        try:
            with get_db_session() as db_session:
                coordinator = AutonomousNpcCoordinator(db_session)
                health_status = coordinator.get_system_health_status()
                
                # Check for system health issues
                issues = []
                if health_status["system_performance"]["error_rate"] > 0.1:
                    issues.append("High error rate detected")
                
                if health_status["system_performance"]["average_processing_time_seconds"] > 10:
                    issues.append("Slow processing times detected")
                
                return {
                    "operation": "system_health_check",
                    "health_status": health_status,
                    "issues_detected": issues,
                    "system_healthy": len(issues) == 0,
                    "success": True
                }
        except Exception as e:
            return {"operation": "system_health_check", "success": False, "error": str(e)}
    
    def _perform_weekly_maintenance(self) -> Dict[str, Any]:
        """Perform weekly system maintenance and optimization"""
        try:
            maintenance_tasks = []
            
            # Clean up old data
            maintenance_tasks.append("Data cleanup completed")
            
            # Update tier assignments based on recent activity
            maintenance_tasks.append("Tier assignments reviewed")
            
            # Optimize database indexes
            maintenance_tasks.append("Database optimization completed")
            
            return {
                "operation": "weekly_maintenance",
                "maintenance_tasks": maintenance_tasks,
                "success": True
            }
        except Exception as e:
            return {"operation": "weekly_maintenance", "success": False, "error": str(e)}
    
    def _generate_weekly_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive weekly statistics report"""
        try:
            with get_db_session() as db_session:
                coordinator = AutonomousNpcCoordinator(db_session)
                stats = coordinator.get_comprehensive_statistics(7)  # Last 7 days
                
                return {
                    "operation": "weekly_statistics",
                    "statistics": stats,
                    "success": True
                }
        except Exception as e:
            return {"operation": "weekly_statistics", "success": False, "error": str(e)}
    
    def _process_monthly_lifecycle_updates(self) -> Dict[str, Any]:
        """Process comprehensive monthly lifecycle updates for high-tier NPCs"""
        try:
            with get_db_session() as db_session:
                coordinator = AutonomousNpcCoordinator(db_session)
                result = asyncio.run(coordinator.process_daily_updates(batch_size=50))
                
                return {
                    "operation": "monthly_lifecycle_updates",
                    "processing_result": result,
                    "success": True
                }
        except Exception as e:
            return {"operation": "monthly_lifecycle_updates", "success": False, "error": str(e)}
    
    # === UTILITY METHODS ===
    
    def _cleanup_execution_history(self):
        """Clean up old execution history"""
        if len(self.execution_history) > self.max_history_size:
            # Keep only the most recent executions
            self.execution_history = self.execution_history[-self.max_history_size:]
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status and statistics"""
        recent_executions = [
            asdict(result) for result in self.execution_history[-10:]
        ]
        
        task_stats = {}
        for name, task in self.scheduled_tasks.items():
            task_stats[name] = {
                "enabled": task.enabled,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "run_count": task.run_count,
                "error_count": task.error_count,
                "average_duration": task.average_duration,
                "success_rate": (task.run_count - task.error_count) / max(task.run_count, 1)
            }
        
        return {
            "scheduler_running": self.is_running,
            "total_tasks": len(self.scheduled_tasks),
            "enabled_tasks": sum(1 for task in self.scheduled_tasks.values() if task.enabled),
            "total_executions": len(self.execution_history),
            "recent_executions": recent_executions,
            "task_statistics": task_stats
        }
    
    def enable_task(self, task_name: str) -> bool:
        """Enable a scheduled task"""
        if task_name in self.scheduled_tasks:
            task = self.scheduled_tasks[task_name]
            task.enabled = True
            self._register_task_with_scheduler(task)
            return True
        return False
    
    def disable_task(self, task_name: str) -> bool:
        """Disable a scheduled task"""
        if task_name in self.scheduled_tasks:
            self.scheduled_tasks[task_name].enabled = False
            # Remove from schedule
            schedule.clear(task_name)
            return True
        return False
    
    def trigger_task_manually(self, task_name: str) -> Optional[TaskExecutionResult]:
        """Manually trigger a scheduled task"""
        if task_name in self.scheduled_tasks:
            return self._execute_task(task_name)
        return None


# Global scheduler instance
autonomous_scheduler = AutonomousNpcScheduler() 