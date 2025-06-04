"""
Pressure Service

Service layer for pressure monitoring and analysis.
Provides high-level interface for collecting, analyzing, and reporting pressure data.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.systems.chaos.core.pressure_monitor import PressureMonitor
from backend.systems.chaos.core.config import ChaosConfig
from backend.infrastructure.systems.chaos.models.pressure_data import PressureData


class PressureService:
    """
    Service for managing pressure monitoring across game systems.
    
    This service provides a high-level interface for collecting,
    analyzing, and reporting on pressure data from various game systems.
    """
    
    def __init__(self, config: Optional[ChaosConfig] = None):
        """Initialize the pressure service."""
        self.config = config or ChaosConfig()
        self.pressure_monitor = PressureMonitor(self.config)
        
    async def initialize(self) -> None:
        """Initialize the pressure service."""
        try:
            await self.pressure_monitor.initialize()
        except Exception as e:
            raise
    
    async def collect_all_pressure(self) -> PressureData:
        """Collect pressure data from all connected systems."""
        return await self.pressure_monitor.collect_all_pressure()
    
    async def collect_system_pressure(self, system_name: str) -> Dict[str, float]:
        """Collect pressure data from a specific system."""
        return await self.pressure_monitor.collect_system_pressure(system_name)
    
    async def collect_regional_pressure(self, region_id: str) -> PressureData:
        """Collect pressure data for a specific region."""
        return await self.pressure_monitor.collect_regional_pressure(region_id)
    
    def register_pressure_source(
        self,
        system_name: str,
        pressure_collector_func
    ) -> None:
        """
        Register a pressure collection function for a system.
        
        Args:
            system_name: Name of the system
            pressure_collector_func: Async function that returns pressure data
        """
        self.pressure_monitor.register_pressure_source(
            system_name, pressure_collector_func
        )
    
    def unregister_pressure_source(self, system_name: str) -> None:
        """Unregister a pressure source."""
        self.pressure_monitor.unregister_pressure_source(system_name)
    
    def get_pressure_thresholds(self) -> Dict[str, float]:
        """Get current pressure thresholds for all sources."""
        return self.pressure_monitor.get_pressure_thresholds()
    
    def update_pressure_thresholds(self, thresholds: Dict[str, float]) -> None:
        """Update pressure thresholds."""
        self.pressure_monitor.update_pressure_thresholds(thresholds)
    
    def get_pressure_history(
        self,
        hours: int = 24,
        system_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical pressure data.
        
        Args:
            hours: Number of hours of history to retrieve
            system_name: Optional system to filter by
            
        Returns:
            List of pressure data points
        """
        return self.pressure_monitor.get_pressure_history(hours, system_name)
    
    def get_pressure_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get pressure trend analysis.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dict containing trend analysis
        """
        return self.pressure_monitor.get_pressure_trends(hours)
    
    def get_connected_systems(self) -> List[str]:
        """Get list of systems providing pressure data."""
        return self.pressure_monitor.get_connected_systems()
    
    async def stop(self) -> None:
        """Stop the pressure service."""
        await self.pressure_monitor.stop() 