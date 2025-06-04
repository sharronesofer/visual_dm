"""
Infrastructure Deployment Configuration

Centralized deployment configuration for all systems.
"""

import os
from dataclasses import dataclass


@dataclass
class DeploymentConfig:
    """Deployment configuration settings for all systems."""
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
    
    def __init__(self, environment: str = "production", **kwargs):
        """
        Initialize DeploymentConfig with environment and other settings.
        
        Args:
            environment: Deployment environment (e.g., "production", "test", "development")
            **kwargs: Other configuration options
        """
        self.environment = environment
        self.debug_mode = kwargs.get('debug_mode', False)
        self.log_level = kwargs.get('log_level', "INFO")
        self.database_url = kwargs.get('database_url', "")
        self.redis_url = kwargs.get('redis_url', "")
        self.websocket_enabled = kwargs.get('websocket_enabled', True)
        self.event_system_enabled = kwargs.get('event_system_enabled', True)
        self.monitoring_enabled = kwargs.get('monitoring_enabled', True)
        self.health_check_interval = kwargs.get('health_check_interval', 60)
        self.max_connections = kwargs.get('max_connections', 1000)
        self.request_timeout = kwargs.get('request_timeout', 30)
        self.worker_processes = kwargs.get('worker_processes', 4)
    
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