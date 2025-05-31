"""
Economy System Deployment - Production deployment preparation and utilities.

This module provides deployment configuration, health checks, monitoring,
and production utilities for the economy system.
"""

import logging
import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from backend.systems.economy.services.economy_manager import EconomyManager
from backend.systems.economy.database_service import get_database_service
from backend.systems.economy.events import get_event_bus, EconomyEventType, publish_system_event
from backend.systems.economy.websocket_events import economy_websocket_manager

# Set up logging
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    """Health check result."""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: float = 0.0

@dataclass
class DeploymentConfig:
    """Deployment configuration settings."""
    environment: str = "production"
    debug_mode: bool = False
    log_level: str = "INFO"
    database_url: str = ""
    redis_url: str = ""
    websocket_enabled: bool = True
    event_system_enabled: bool = True
    monitoring_enabled: bool = True
    health_check_interval: int = 60  # seconds
    max_connections: int = 1000
    request_timeout: int = 30
    worker_processes: int = 4
    
    @classmethod
    def from_environment(cls) -> 'DeploymentConfig':
        """Create deployment config from environment variables."""
        return cls(
            environment=os.getenv("ENVIRONMENT", "production"),
            debug_mode=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database_url=os.getenv("DATABASE_URL", ""),
            redis_url=os.getenv("REDIS_URL", ""),
            websocket_enabled=os.getenv("WEBSOCKET_ENABLED", "true").lower() == "true",
            event_system_enabled=os.getenv("EVENT_SYSTEM_ENABLED", "true").lower() == "true",
            monitoring_enabled=os.getenv("MONITORING_ENABLED", "true").lower() == "true",
            health_check_interval=int(os.getenv("HEALTH_CHECK_INTERVAL", "60")),
            max_connections=int(os.getenv("MAX_CONNECTIONS", "1000")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            worker_processes=int(os.getenv("WORKER_PROCESSES", "4"))
        )

class EconomyDeploymentManager:
    """
    Deployment manager for the economy system.
    
    Handles production deployment preparation, health checks, monitoring,
    and system management for the economy system.
    """
    
    def __init__(self, config: Optional[DeploymentConfig] = None):
        """
        Initialize the deployment manager.
        
        Args:
            config: Deployment configuration, defaults to environment-based config
        """
        self.config = config or DeploymentConfig.from_environment()
        self.economy_manager: Optional[EconomyManager] = None
        self.db_service = None
        self.event_bus = None
        self.websocket_manager = None
        self.health_checks: Dict[str, HealthCheck] = {}
        self.last_health_check = None
        self.startup_time = datetime.utcnow()
        self.is_ready = False
        
        # Configure logging
        self._configure_logging()
        
        logger.info(f"Economy deployment manager initialized for {self.config.environment}")
    
    def _configure_logging(self):
        """Configure logging for production deployment."""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set specific loggers
        logging.getLogger("backend.systems.economy").setLevel(log_level)
        
        if not self.config.debug_mode:
            # Reduce noise in production
            logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
            logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    async def initialize_system(self) -> bool:
        """
        Initialize the economy system for production deployment.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing economy system for deployment...")
            
            # Initialize database service
            if self.config.database_url:
                self.db_service = get_database_service(self.config.database_url)
                if not self.db_service.test_connection():
                    logger.error("Database connection failed")
                    return False
                logger.info("Database service initialized")
            
            # Initialize economy manager
            db_session = self.db_service.create_session() if self.db_service else None
            self.economy_manager = EconomyManager.get_instance(db_session)
            logger.info("Economy manager initialized")
            
            # Initialize event system
            if self.config.event_system_enabled:
                self.event_bus = get_event_bus()
                publish_system_event(EconomyEventType.ECONOMY_INITIALIZED, 
                                   data={"environment": self.config.environment})
                logger.info("Event system initialized")
            
            # Initialize WebSocket system
            if self.config.websocket_enabled:
                self.websocket_manager = economy_websocket_manager
                self.websocket_manager.economy_manager = self.economy_manager
                logger.info("WebSocket system initialized")
            
            # Run initial health checks
            await self.run_health_checks()
            
            self.is_ready = True
            logger.info("Economy system initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize economy system: {e}")
            return False
    
    async def shutdown_system(self):
        """Gracefully shutdown the economy system."""
        try:
            logger.info("Shutting down economy system...")
            
            # Publish shutdown event
            if self.event_bus:
                publish_system_event(EconomyEventType.ECONOMY_SHUTDOWN,
                                   data={"environment": self.config.environment})
            
            # Close database connections
            if self.db_service:
                self.db_service.close()
                logger.info("Database connections closed")
            
            # Clear WebSocket connections
            if self.websocket_manager:
                # Disconnect all WebSocket clients
                for websocket in list(self.websocket_manager.connections.keys()):
                    await self.websocket_manager.disconnect(websocket)
                logger.info("WebSocket connections closed")
            
            logger.info("Economy system shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during system shutdown: {e}")
    
    async def run_health_checks(self) -> Dict[str, HealthCheck]:
        """
        Run comprehensive health checks on the economy system.
        
        Returns:
            Dictionary of health check results
        """
        start_time = datetime.utcnow()
        health_checks = {}
        
        try:
            # Database health check
            health_checks["database"] = await self._check_database_health()
            
            # Economy manager health check
            health_checks["economy_manager"] = await self._check_economy_manager_health()
            
            # Event system health check
            if self.config.event_system_enabled:
                health_checks["event_system"] = await self._check_event_system_health()
            
            # WebSocket system health check
            if self.config.websocket_enabled:
                health_checks["websocket_system"] = await self._check_websocket_health()
            
            # Memory and performance check
            health_checks["performance"] = await self._check_performance_health()
            
            # Overall system health
            health_checks["system"] = await self._check_overall_health(health_checks)
            
            self.health_checks = health_checks
            self.last_health_check = datetime.utcnow()
            
            # Log health check summary
            healthy_count = sum(1 for check in health_checks.values() 
                              if check.status == HealthStatus.HEALTHY)
            total_count = len(health_checks)
            
            logger.info(f"Health checks completed: {healthy_count}/{total_count} healthy "
                       f"(took {(datetime.utcnow() - start_time).total_seconds():.2f}s)")
            
            return health_checks
            
        except Exception as e:
            logger.error(f"Error running health checks: {e}")
            return {"error": HealthCheck("error", HealthStatus.CRITICAL, str(e))}
    
    async def _check_database_health(self) -> HealthCheck:
        """Check database health."""
        start_time = datetime.utcnow()
        
        try:
            if not self.db_service:
                return HealthCheck(
                    "database", HealthStatus.WARNING, 
                    "Database service not configured"
                )
            
            # Test connection
            if not self.db_service.test_connection():
                return HealthCheck(
                    "database", HealthStatus.CRITICAL,
                    "Database connection failed"
                )
            
            # Get database stats
            stats = self.db_service.get_database_stats()
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return HealthCheck(
                "database", HealthStatus.HEALTHY,
                "Database connection successful",
                details=stats,
                response_time_ms=response_time
            )
            
        except Exception as e:
            return HealthCheck(
                "database", HealthStatus.CRITICAL,
                f"Database health check failed: {e}"
            )
    
    async def _check_economy_manager_health(self) -> HealthCheck:
        """Check economy manager health."""
        start_time = datetime.utcnow()
        
        try:
            if not self.economy_manager:
                return HealthCheck(
                    "economy_manager", HealthStatus.CRITICAL,
                    "Economy manager not initialized"
                )
            
            # Test basic operations
            status = self.economy_manager.get_economy_status()
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return HealthCheck(
                "economy_manager", HealthStatus.HEALTHY,
                "Economy manager operational",
                details=status,
                response_time_ms=response_time
            )
            
        except Exception as e:
            return HealthCheck(
                "economy_manager", HealthStatus.CRITICAL,
                f"Economy manager health check failed: {e}"
            )
    
    async def _check_event_system_health(self) -> HealthCheck:
        """Check event system health."""
        start_time = datetime.utcnow()
        
        try:
            if not self.event_bus:
                return HealthCheck(
                    "event_system", HealthStatus.WARNING,
                    "Event system not enabled"
                )
            
            # Get event system stats
            stats = self.event_bus.get_stats()
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return HealthCheck(
                "event_system", HealthStatus.HEALTHY,
                "Event system operational",
                details=stats,
                response_time_ms=response_time
            )
            
        except Exception as e:
            return HealthCheck(
                "event_system", HealthStatus.CRITICAL,
                f"Event system health check failed: {e}"
            )
    
    async def _check_websocket_health(self) -> HealthCheck:
        """Check WebSocket system health."""
        start_time = datetime.utcnow()
        
        try:
            if not self.websocket_manager:
                return HealthCheck(
                    "websocket_system", HealthStatus.WARNING,
                    "WebSocket system not enabled"
                )
            
            # Get WebSocket stats
            connection_count = len(self.websocket_manager.connections)
            channel_count = len(self.websocket_manager.channel_subscribers)
            
            stats = {
                "active_connections": connection_count,
                "available_channels": channel_count,
                "max_connections": self.config.max_connections
            }
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Check if approaching connection limits
            status = HealthStatus.HEALTHY
            message = "WebSocket system operational"
            
            if connection_count > self.config.max_connections * 0.8:
                status = HealthStatus.WARNING
                message = f"High connection count: {connection_count}/{self.config.max_connections}"
            
            return HealthCheck(
                "websocket_system", status, message,
                details=stats,
                response_time_ms=response_time
            )
            
        except Exception as e:
            return HealthCheck(
                "websocket_system", HealthStatus.CRITICAL,
                f"WebSocket system health check failed: {e}"
            )
    
    async def _check_performance_health(self) -> HealthCheck:
        """Check system performance metrics."""
        start_time = datetime.utcnow()
        
        try:
            import psutil
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            stats = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds()
            }
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Determine health status based on metrics
            status = HealthStatus.HEALTHY
            message = "System performance normal"
            
            if cpu_percent > 80 or memory.percent > 85:
                status = HealthStatus.WARNING
                message = "High resource usage detected"
            
            if cpu_percent > 95 or memory.percent > 95:
                status = HealthStatus.CRITICAL
                message = "Critical resource usage"
            
            return HealthCheck(
                "performance", status, message,
                details=stats,
                response_time_ms=response_time
            )
            
        except ImportError:
            return HealthCheck(
                "performance", HealthStatus.WARNING,
                "psutil not available for performance monitoring"
            )
        except Exception as e:
            return HealthCheck(
                "performance", HealthStatus.WARNING,
                f"Performance check failed: {e}"
            )
    
    async def _check_overall_health(self, health_checks: Dict[str, HealthCheck]) -> HealthCheck:
        """Determine overall system health."""
        start_time = datetime.utcnow()
        
        try:
            critical_count = sum(1 for check in health_checks.values() 
                               if check.status == HealthStatus.CRITICAL)
            warning_count = sum(1 for check in health_checks.values() 
                              if check.status == HealthStatus.WARNING)
            healthy_count = sum(1 for check in health_checks.values() 
                              if check.status == HealthStatus.HEALTHY)
            
            total_checks = len(health_checks)
            
            stats = {
                "total_checks": total_checks,
                "healthy": healthy_count,
                "warnings": warning_count,
                "critical": critical_count,
                "ready": self.is_ready
            }
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Determine overall status
            if critical_count > 0:
                status = HealthStatus.CRITICAL
                message = f"System critical: {critical_count} critical issues"
            elif warning_count > 0:
                status = HealthStatus.WARNING
                message = f"System warnings: {warning_count} warnings"
            else:
                status = HealthStatus.HEALTHY
                message = "All systems operational"
            
            return HealthCheck(
                "system", status, message,
                details=stats,
                response_time_ms=response_time
            )
            
        except Exception as e:
            return HealthCheck(
                "system", HealthStatus.CRITICAL,
                f"Overall health check failed: {e}"
            )
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get deployment information and status."""
        return {
            "environment": self.config.environment,
            "startup_time": self.startup_time.isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds(),
            "is_ready": self.is_ready,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "configuration": {
                "debug_mode": self.config.debug_mode,
                "log_level": self.config.log_level,
                "websocket_enabled": self.config.websocket_enabled,
                "event_system_enabled": self.config.event_system_enabled,
                "monitoring_enabled": self.config.monitoring_enabled,
                "max_connections": self.config.max_connections,
                "worker_processes": self.config.worker_processes
            },
            "health_summary": {
                check_name: {
                    "status": check.status.value,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms
                }
                for check_name, check in self.health_checks.items()
            }
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics for monitoring."""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds(),
            "is_ready": self.is_ready
        }
        
        # Add health check metrics
        if self.health_checks:
            for check_name, check in self.health_checks.items():
                metrics[f"health_{check_name}_status"] = check.status.value
                metrics[f"health_{check_name}_response_time_ms"] = check.response_time_ms
        
        # Add economy manager metrics
        if self.economy_manager:
            try:
                status = self.economy_manager.get_economy_status()
                metrics.update({
                    "economy_resources_count": status.get("total_resources", 0),
                    "economy_markets_count": status.get("total_markets", 0),
                    "economy_trade_routes_count": status.get("total_trade_routes", 0)
                })
            except Exception as e:
                logger.warning(f"Could not get economy metrics: {e}")
        
        # Add WebSocket metrics
        if self.websocket_manager:
            metrics.update({
                "websocket_connections": len(self.websocket_manager.connections),
                "websocket_channels": len(self.websocket_manager.channel_subscribers)
            })
        
        # Add event system metrics
        if self.event_bus:
            stats = self.event_bus.get_stats()
            metrics.update({
                "event_subscribers": stats.get("total_subscribers", 0),
                "event_history_size": stats.get("events_in_history", 0)
            })
        
        return metrics
    
    async def create_deployment_report(self) -> Dict[str, Any]:
        """Create a comprehensive deployment report."""
        # Run fresh health checks
        health_checks = await self.run_health_checks()
        
        return {
            "deployment_info": self.get_deployment_info(),
            "health_checks": {
                check_name: {
                    "status": check.status.value,
                    "message": check.message,
                    "details": check.details,
                    "response_time_ms": check.response_time_ms,
                    "timestamp": check.timestamp.isoformat()
                }
                for check_name, check in health_checks.items()
            },
            "metrics": self.get_metrics(),
            "recommendations": self._get_deployment_recommendations(health_checks)
        }
    
    def _get_deployment_recommendations(self, health_checks: Dict[str, HealthCheck]) -> List[str]:
        """Get deployment recommendations based on health checks."""
        recommendations = []
        
        # Check for critical issues
        critical_checks = [check for check in health_checks.values() 
                         if check.status == HealthStatus.CRITICAL]
        if critical_checks:
            recommendations.append("CRITICAL: Resolve critical health check failures before deployment")
        
        # Check for warnings
        warning_checks = [check for check in health_checks.values() 
                        if check.status == HealthStatus.WARNING]
        if warning_checks:
            recommendations.append("WARNING: Review and address warning conditions")
        
        # Performance recommendations
        if "performance" in health_checks:
            perf_check = health_checks["performance"]
            if "cpu_percent" in perf_check.details:
                cpu = perf_check.details["cpu_percent"]
                if cpu > 70:
                    recommendations.append(f"Consider increasing CPU resources (current: {cpu}%)")
            
            if "memory_percent" in perf_check.details:
                memory = perf_check.details["memory_percent"]
                if memory > 80:
                    recommendations.append(f"Consider increasing memory resources (current: {memory}%)")
        
        # WebSocket recommendations
        if "websocket_system" in health_checks:
            ws_check = health_checks["websocket_system"]
            if "active_connections" in ws_check.details:
                connections = ws_check.details["active_connections"]
                max_connections = ws_check.details.get("max_connections", 1000)
                if connections > max_connections * 0.7:
                    recommendations.append("Consider increasing WebSocket connection limits")
        
        # Database recommendations
        if "database" in health_checks:
            db_check = health_checks["database"]
            if db_check.response_time_ms > 1000:
                recommendations.append("Database response time is high, consider optimization")
        
        if not recommendations:
            recommendations.append("System is ready for production deployment")
        
        return recommendations

# Global deployment manager instance
_deployment_manager: Optional[EconomyDeploymentManager] = None

def get_deployment_manager(config: Optional[DeploymentConfig] = None) -> EconomyDeploymentManager:
    """Get the global deployment manager instance."""
    global _deployment_manager
    if _deployment_manager is None:
        _deployment_manager = EconomyDeploymentManager(config)
    return _deployment_manager

async def initialize_for_deployment(config: Optional[DeploymentConfig] = None) -> bool:
    """Initialize the economy system for production deployment."""
    deployment_manager = get_deployment_manager(config)
    return await deployment_manager.initialize_system()

async def shutdown_deployment():
    """Shutdown the economy system deployment."""
    if _deployment_manager:
        await _deployment_manager.shutdown_system()

async def health_check() -> Dict[str, Any]:
    """Run health checks and return results."""
    deployment_manager = get_deployment_manager()
    health_checks = await deployment_manager.run_health_checks()
    
    return {
        "status": "healthy" if all(check.status == HealthStatus.HEALTHY 
                                 for check in health_checks.values()) else "unhealthy",
        "checks": {
            name: {
                "status": check.status.value,
                "message": check.message,
                "response_time_ms": check.response_time_ms
            }
            for name, check in health_checks.items()
        },
        "timestamp": datetime.utcnow().isoformat()
    }

def get_deployment_metrics() -> Dict[str, Any]:
    """Get deployment metrics for monitoring."""
    deployment_manager = get_deployment_manager()
    return deployment_manager.get_metrics() 