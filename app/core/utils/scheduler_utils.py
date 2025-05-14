import logging
from typing import Dict, Any, Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from flask import Flask

logger = logging.getLogger(__name__)

class SchedulerManager:
    """Manager for background scheduler"""
    
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.scheduler = BackgroundScheduler(
            jobstores={
                'default': MemoryJobStore()
            },
            executors={
                'default': ThreadPoolExecutor(20)
            },
            job_defaults={
                'coalesce': False,
                'max_instances': 3
            }
        )
        self.setup_event_listeners()
        self.scheduler.start()
    
    def setup_event_listeners(self) -> None:
        """Setup event listeners for the scheduler"""
        
        def job_error_listener(event: Any) -> None:
            if event.exception:
                logger.error(
                    f"Job {event.job_id} failed: {str(event.exception)}",
                    exc_info=event.exception
                )
            else:
                logger.error(f"Job {event.job_id} failed for unknown reason")
        
        def job_executed_listener(event: Any) -> None:
            logger.info(f"Job {event.job_id} executed successfully")
        
        self.scheduler.add_listener(
            job_error_listener,
            EVENT_JOB_ERROR
        )
        self.scheduler.add_listener(
            job_executed_listener,
            EVENT_JOB_EXECUTED
        )
    
    def add_job(
        self,
        func: Callable,
        trigger: str,
        **kwargs: Any
    ) -> None:
        """Add a new job to the scheduler"""
        try:
            self.scheduler.add_job(
                func,
                trigger=trigger,
                **kwargs
            )
            logger.info(f"Added job {func.__name__} with trigger {trigger}")
        except Exception as e:
            logger.error(f"Failed to add job {func.__name__}: {str(e)}")
            raise
    
    def remove_job(self, job_id: str) -> None:
        """Remove a job from the scheduler"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {str(e)}")
            raise
    
    def pause_job(self, job_id: str) -> None:
        """Pause a job"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job {job_id}")
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {str(e)}")
            raise
    
    def resume_job(self, job_id: str) -> None:
        """Resume a paused job"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job {job_id}")
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {str(e)}")
            raise
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job information"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                return {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time,
                    'trigger': str(job.trigger),
                    'paused': job.paused
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {str(e)}")
            raise
    
    def get_all_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all jobs"""
        try:
            jobs = {}
            for job in self.scheduler.get_jobs():
                jobs[job.id] = {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time,
                    'trigger': str(job.trigger),
                    'paused': job.paused
                }
            return jobs
        except Exception as e:
            logger.error(f"Failed to get all jobs: {str(e)}")
            raise
    
    def shutdown(self) -> None:
        """Shutdown the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler shut down successfully")
        except Exception as e:
            logger.error(f"Failed to shut down scheduler: {str(e)}")
            raise 