"""
Infrastructure Deployment Manager

Manages deployment lifecycle, monitoring, and health checks.
"""

import time
import psutil
from datetime import datetime
from typing import List, Dict, Any

from .deployment_config import DeploymentConfig
from .health_checks import HealthCheck, HealthStatus


class DeploymentManager:
    """Manages deployment lifecycle and monitoring."""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self._start_time = datetime.utcnow()
        
    def get_system_health(self) -> List[HealthCheck]:
        """Get system health status."""
        checks = []
        
        # Memory check
        memory = psutil.virtual_memory()
        memory_status = HealthStatus.HEALTHY
        if memory.percent > 90:
            memory_status = HealthStatus.CRITICAL
        elif memory.percent > 75:
            memory_status = HealthStatus.WARNING
            
        checks.append(HealthCheck(
            name="memory",
            status=memory_status,
            message=f"Memory usage: {memory.percent:.1f}%",
            details={"percent": memory.percent, "total": memory.total, "used": memory.used}
        ))
        
        # CPU check
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_status = HealthStatus.HEALTHY
        if cpu_percent > 90:
            cpu_status = HealthStatus.CRITICAL
        elif cpu_percent > 75:
            cpu_status = HealthStatus.WARNING
            
        checks.append(HealthCheck(
            name="cpu",
            status=cpu_status,
            message=f"CPU usage: {cpu_percent:.1f}%",
            details={"percent": cpu_percent}
        ))
        
        # Disk check
        disk = psutil.disk_usage('/')
        disk_status = HealthStatus.HEALTHY
        if disk.percent > 90:
            disk_status = HealthStatus.CRITICAL
        elif disk.percent > 80:
            disk_status = HealthStatus.WARNING
            
        checks.append(HealthCheck(
            name="disk",
            status=disk_status,
            message=f"Disk usage: {disk.percent:.1f}%",
            details={"percent": disk.percent, "total": disk.total, "used": disk.used}
        ))
        
        return checks
    
    def get_uptime(self) -> Dict[str, Any]:
        """Get application uptime information."""
        uptime = datetime.utcnow() - self._start_time
        return {
            "start_time": self._start_time.isoformat(),
            "uptime_seconds": uptime.total_seconds(),
            "uptime_human": str(uptime)
        } 