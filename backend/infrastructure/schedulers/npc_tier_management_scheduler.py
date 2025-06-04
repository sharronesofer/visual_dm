"""
Revolutionary NPC Tier System Background Scheduler

Manages automated tier promotion/demotion cycles and handles periodic
maintenance of the tier system for optimal performance.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from uuid import UUID

from backend.infrastructure.shared.database.manager import DatabaseManager
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
from backend.systems.npc.services.tier_manager import NPCTierManager

logger = logging.getLogger(__name__)


class TierManagementScheduler:
    """
    Background scheduler for the Revolutionary NPC Tier System.
    
    Handles automated tier management cycles, performance monitoring,
    and system optimization for MMO-scale NPC populations.
    """
    
    def __init__(self, db_manager: DatabaseManager, event_dispatcher: EventDispatcher):
        self.db_manager = db_manager
        self.event_dispatcher = event_dispatcher
        self.tier_manager = NPCTierManager(db_manager, event_dispatcher)
        
        # Scheduling configuration
        self.is_running = False
        self.cycle_interval_seconds = 300  # 5 minutes default
        self.maintenance_interval_seconds = 3600  # 1 hour default
        self.optimization_interval_seconds = 7200  # 2 hours default
        
        # Performance tracking
        self.last_cycle_time = None
        self.last_maintenance_time = None
        self.last_optimization_time = None
        self.cycle_count = 0
        self.error_count = 0
        
        # Async tasks
        self._cycle_task: Optional[asyncio.Task] = None
        self._maintenance_task: Optional[asyncio.Task] = None
        self._optimization_task: Optional[asyncio.Task] = None
        
        logger.info("TierManagementScheduler initialized")

    async def start(self) -> None:
        """Start all background tasks for tier management"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        self.is_running = True
        logger.info("Starting Revolutionary NPC Tier Management Scheduler")
        
        # Start main tier management cycle
        self._cycle_task = asyncio.create_task(self._tier_management_cycle_loop())
        
        # Start maintenance cycle
        self._maintenance_task = asyncio.create_task(self._maintenance_cycle_loop())
        
        # Start optimization cycle
        self._optimization_task = asyncio.create_task(self._optimization_cycle_loop())
        
        logger.info("All tier management tasks started successfully")

    async def stop(self) -> None:
        """Stop all background tasks"""
        if not self.is_running:
            logger.warning("Scheduler not running")
            return
        
        self.is_running = False
        logger.info("Stopping Revolutionary NPC Tier Management Scheduler")
        
        # Cancel all tasks
        tasks = [self._cycle_task, self._maintenance_task, self._optimization_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("All tier management tasks stopped")

    async def _tier_management_cycle_loop(self) -> None:
        """Main tier management cycle loop"""
        logger.info(f"Starting tier management cycle loop (interval: {self.cycle_interval_seconds}s)")
        
        while self.is_running:
            try:
                await self._run_tier_management_cycle()
                await asyncio.sleep(self.cycle_interval_seconds)
                
            except asyncio.CancelledError:
                logger.info("Tier management cycle loop cancelled")
                break
            except Exception as e:
                self.error_count += 1
                logger.error(f"Error in tier management cycle: {str(e)}")
                
                # Exponential backoff on errors (max 5 minutes)
                error_backoff = min(60 * (2 ** min(self.error_count, 5)), 300)
                await asyncio.sleep(error_backoff)

    async def _maintenance_cycle_loop(self) -> None:
        """Maintenance cycle loop for system health"""
        logger.info(f"Starting maintenance cycle loop (interval: {self.maintenance_interval_seconds}s)")
        
        while self.is_running:
            try:
                await self._run_maintenance_cycle()
                await asyncio.sleep(self.maintenance_interval_seconds)
                
            except asyncio.CancelledError:
                logger.info("Maintenance cycle loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in maintenance cycle: {str(e)}")
                await asyncio.sleep(600)  # 10 minute backoff on maintenance errors

    async def _optimization_cycle_loop(self) -> None:
        """Optimization cycle loop for performance tuning"""
        logger.info(f"Starting optimization cycle loop (interval: {self.optimization_interval_seconds}s)")
        
        while self.is_running:
            try:
                await self._run_optimization_cycle()
                await asyncio.sleep(self.optimization_interval_seconds)
                
            except asyncio.CancelledError:
                logger.info("Optimization cycle loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in optimization cycle: {str(e)}")
                await asyncio.sleep(1200)  # 20 minute backoff on optimization errors

    async def _run_tier_management_cycle(self) -> None:
        """Execute a single tier management cycle"""
        cycle_start = datetime.utcnow()
        
        try:
            # Run the tier manager cycle
            cycle_results = await self.tier_manager.run_tier_management_cycle()
            
            self.cycle_count += 1
            self.last_cycle_time = cycle_start
            self.error_count = max(0, self.error_count - 1)  # Reduce error count on success
            
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            
            logger.info(
                f"Tier management cycle #{self.cycle_count} completed in {cycle_duration:.2f}s: "
                f"Promoted: {cycle_results.get('promoted_count', 0)}, "
                f"Demoted: {cycle_results.get('demoted_count', 0)}"
            )
            
            # Publish cycle completed event
            self.event_dispatcher.publish(
                "tier_management_cycle_completed",
                {
                    "cycle_number": self.cycle_count,
                    "duration_seconds": cycle_duration,
                    "results": cycle_results,
                    "timestamp": cycle_start.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to run tier management cycle: {str(e)}")
            raise

    async def _run_maintenance_cycle(self) -> None:
        """Execute maintenance tasks for system health"""
        maintenance_start = datetime.utcnow()
        
        try:
            logger.info("Running tier system maintenance cycle")
            
            # Get current system status
            budget_status = self.tier_manager.get_computational_budget_status()
            
            # Check for system health issues
            health_issues = []
            
            # Memory usage check
            memory_usage = budget_status['metrics'].memory_usage_mb
            if memory_usage > 1000:  # Over 1GB
                health_issues.append(f"High memory usage: {memory_usage:.1f} MB")
            
            # CPU usage check
            cpu_usage = budget_status['metrics'].computational_load
            if cpu_usage > 5000:  # Over 5000 CPU units/hour
                health_issues.append(f"High CPU usage: {cpu_usage:.1f} units/hour")
            
            # Tier distribution check
            metrics = budget_status['metrics']
            if metrics.tier_1_count > 1000:  # Too many Tier 1 NPCs
                health_issues.append(f"Too many Tier 1 NPCs: {metrics.tier_1_count}")
            
            # Log health status
            if health_issues:
                logger.warning(f"Tier system health issues detected: {', '.join(health_issues)}")
                
                # Publish health warning event
                self.event_dispatcher.publish(
                    "tier_system_health_warning",
                    {
                        "issues": health_issues,
                        "metrics": budget_status['metrics'],
                        "timestamp": maintenance_start.isoformat()
                    }
                )
            else:
                logger.info("Tier system health check passed")
            
            # Clean up stale data if needed
            await self._cleanup_stale_data()
            
            self.last_maintenance_time = maintenance_start
            maintenance_duration = (datetime.utcnow() - maintenance_start).total_seconds()
            
            logger.info(f"Maintenance cycle completed in {maintenance_duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to run maintenance cycle: {str(e)}")
            raise

    async def _run_optimization_cycle(self) -> None:
        """Execute optimization tasks for performance tuning"""
        optimization_start = datetime.utcnow()
        
        try:
            logger.info("Running tier system optimization cycle")
            
            # Get current metrics
            budget_status = self.tier_manager.get_computational_budget_status()
            metrics = budget_status['metrics']
            
            # Analyze tier distribution efficiency
            total_visible = metrics.tier_1_count + metrics.tier_2_count + metrics.tier_3_count + metrics.tier_3_5_count
            total_npcs = metrics.total_npcs
            efficiency_ratio = total_visible / max(1, total_npcs)
            
            optimizations_performed = []
            
            # Tier distribution optimization
            if efficiency_ratio > 0.5:  # More than 50% visible
                logger.info("High visibility ratio detected - considering tier compression")
                # Could implement automatic tier compression here
                optimizations_performed.append("tier_compression_analysis")
            
            # Memory optimization
            if metrics.memory_usage_mb > 500:  # Over 500MB
                logger.info("High memory usage - analyzing compression opportunities")
                # Could implement memory optimization here
                optimizations_performed.append("memory_analysis")
            
            # Performance recommendations
            recommendations = budget_status.get('recommendations', [])
            if recommendations:
                logger.info(f"Performance recommendations: {', '.join(recommendations)}")
                optimizations_performed.append("performance_analysis")
            
            # Update interval optimization based on load
            if metrics.computational_load > 3000:
                # Increase cycle interval under high load
                new_interval = min(self.cycle_interval_seconds * 1.2, 600)  # Max 10 minutes
                if new_interval != self.cycle_interval_seconds:
                    logger.info(f"Adjusting cycle interval: {self.cycle_interval_seconds}s -> {new_interval}s")
                    self.cycle_interval_seconds = int(new_interval)
                    optimizations_performed.append("cycle_interval_adjustment")
            elif metrics.computational_load < 1000:
                # Decrease cycle interval under low load
                new_interval = max(self.cycle_interval_seconds * 0.9, 60)  # Min 1 minute
                if new_interval != self.cycle_interval_seconds:
                    logger.info(f"Adjusting cycle interval: {self.cycle_interval_seconds}s -> {new_interval}s")
                    self.cycle_interval_seconds = int(new_interval)
                    optimizations_performed.append("cycle_interval_adjustment")
            
            self.last_optimization_time = optimization_start
            optimization_duration = (datetime.utcnow() - optimization_start).total_seconds()
            
            logger.info(
                f"Optimization cycle completed in {optimization_duration:.2f}s. "
                f"Optimizations: {', '.join(optimizations_performed) if optimizations_performed else 'none'}"
            )
            
            # Publish optimization completed event
            self.event_dispatcher.publish(
                "tier_system_optimization_completed",
                {
                    "optimizations_performed": optimizations_performed,
                    "efficiency_ratio": efficiency_ratio,
                    "metrics": metrics,
                    "duration_seconds": optimization_duration,
                    "timestamp": optimization_start.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to run optimization cycle: {str(e)}")
            raise

    async def _cleanup_stale_data(self) -> None:
        """Clean up stale data and optimize storage"""
        try:
            logger.debug("Running stale data cleanup")
            
            # This could include:
            # - Removing very old interaction records
            # - Compressing historical tier data
            # - Cleaning up orphaned NPC instances
            # - Optimizing database indexes
            
            # For now, just log that cleanup would happen here
            logger.debug("Stale data cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during stale data cleanup: {str(e)}")

    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current status of the scheduler"""
        return {
            "is_running": self.is_running,
            "cycle_count": self.cycle_count,
            "error_count": self.error_count,
            "last_cycle_time": self.last_cycle_time.isoformat() if self.last_cycle_time else None,
            "last_maintenance_time": self.last_maintenance_time.isoformat() if self.last_maintenance_time else None,
            "last_optimization_time": self.last_optimization_time.isoformat() if self.last_optimization_time else None,
            "intervals": {
                "cycle_seconds": self.cycle_interval_seconds,
                "maintenance_seconds": self.maintenance_interval_seconds,
                "optimization_seconds": self.optimization_interval_seconds
            },
            "next_scheduled": {
                "cycle": (self.last_cycle_time + timedelta(seconds=self.cycle_interval_seconds)).isoformat() if self.last_cycle_time else None,
                "maintenance": (self.last_maintenance_time + timedelta(seconds=self.maintenance_interval_seconds)).isoformat() if self.last_maintenance_time else None,
                "optimization": (self.last_optimization_time + timedelta(seconds=self.optimization_interval_seconds)).isoformat() if self.last_optimization_time else None
            }
        }

    def update_intervals(
        self, 
        cycle_interval: Optional[int] = None,
        maintenance_interval: Optional[int] = None,
        optimization_interval: Optional[int] = None
    ) -> None:
        """Update scheduling intervals"""
        if cycle_interval is not None:
            self.cycle_interval_seconds = max(60, cycle_interval)  # Min 1 minute
            logger.info(f"Updated cycle interval to {self.cycle_interval_seconds}s")
        
        if maintenance_interval is not None:
            self.maintenance_interval_seconds = max(300, maintenance_interval)  # Min 5 minutes
            logger.info(f"Updated maintenance interval to {self.maintenance_interval_seconds}s")
        
        if optimization_interval is not None:
            self.optimization_interval_seconds = max(600, optimization_interval)  # Min 10 minutes
            logger.info(f"Updated optimization interval to {self.optimization_interval_seconds}s")

    async def force_cycle(self, cycle_type: str = "management") -> Dict[str, Any]:
        """Force execution of a specific cycle type"""
        if cycle_type == "management":
            await self._run_tier_management_cycle()
            return {"cycle_type": "management", "status": "completed"}
        elif cycle_type == "maintenance":
            await self._run_maintenance_cycle()
            return {"cycle_type": "maintenance", "status": "completed"}
        elif cycle_type == "optimization":
            await self._run_optimization_cycle()
            return {"cycle_type": "optimization", "status": "completed"}
        else:
            raise ValueError(f"Invalid cycle type: {cycle_type}")


# ============================================================================
# Singleton and Factory Functions
# ============================================================================

_scheduler_instance: Optional[TierManagementScheduler] = None

def get_tier_scheduler(
    db_manager: DatabaseManager,
    event_dispatcher: EventDispatcher
) -> TierManagementScheduler:
    """Get or create tier management scheduler instance"""
    global _scheduler_instance
    
    if _scheduler_instance is None:
        _scheduler_instance = TierManagementScheduler(db_manager, event_dispatcher)
    
    return _scheduler_instance

async def start_tier_management_scheduler(
    db_manager: DatabaseManager,
    event_dispatcher: EventDispatcher
) -> TierManagementScheduler:
    """Start the tier management scheduler"""
    scheduler = get_tier_scheduler(db_manager, event_dispatcher)
    await scheduler.start()
    return scheduler

async def stop_tier_management_scheduler() -> None:
    """Stop the tier management scheduler"""
    global _scheduler_instance
    
    if _scheduler_instance:
        await _scheduler_instance.stop()
        _scheduler_instance = None 