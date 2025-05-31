"""
Chaos Service

High-level service interface for the chaos system.
Provides a clean API for other systems to interact with chaos functionality.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from backend.systems.chaos.core.chaos_engine import ChaosEngine

from backend.systems.chaos.core.config import ChaosConfig
from backend.systems.chaos.models.chaos_state import ChaosState
from backend.systems.chaos.models.pressure_data import PressureData

logger = logging.getLogger(__name__)

class ChaosService:
    """
    High-level service for chaos system operations.
    
    This service provides a simplified interface for other game systems
    to interact with the chaos system without needing to understand
    the internal complexity.
    """
    
    def __init__(self, config: Optional[ChaosConfig] = None):
        """Initialize the chaos service."""
        self.config = config or ChaosConfig()
        self._chaos_engine: Optional['ChaosEngine'] = None
        
    @property
    def chaos_engine(self) -> 'ChaosEngine':
        """Get the chaos engine instance."""
        if self._chaos_engine is None:
            # Lazy import to avoid circular dependency
            from backend.systems.chaos.core.chaos_engine import ChaosEngine
            self._chaos_engine = ChaosEngine.get_instance(self.config)
        return self._chaos_engine
    
    async def initialize(self) -> None:
        """Initialize the chaos service."""
        try:
            await self.chaos_engine.initialize()
            logger.info("Chaos Service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Chaos Service: {e}")
            raise
    
    async def start(self) -> None:
        """Start the chaos system."""
        await self.chaos_engine.start()
        
    async def stop(self) -> None:
        """Stop the chaos system."""
        await self.chaos_engine.stop()
        
    def pause(self) -> None:
        """Pause chaos monitoring."""
        self.chaos_engine.pause()
        
    def resume(self) -> None:
        """Resume chaos monitoring."""
        self.chaos_engine.resume()
    
    def get_chaos_state(self, region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current chaos state for a region or globally.
        
        Args:
            region_id: Optional region ID to get specific regional state
            
        Returns:
            Dict containing chaos state information
        """
        if region_id:
            return self.chaos_engine.get_regional_chaos_state(region_id)
        return self.chaos_engine.get_current_chaos_state()
    
    def get_pressure_summary(self) -> Dict[str, Any]:
        """Get summary of current pressure across all systems."""
        return self.chaos_engine.get_pressure_summary()
    
    def get_active_events(self) -> List[Dict[str, Any]]:
        """Get list of currently active chaos events."""
        events = self.chaos_engine.get_active_events()
        return [event.to_dict() for event in events]
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about chaos events."""
        return self.chaos_engine.get_event_statistics()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get chaos system performance metrics."""
        return self.chaos_engine.get_system_metrics()
    
    async def apply_mitigation(
        self,
        mitigation_type: str,
        effectiveness: float,
        duration_hours: float,
        source_id: str,
        source_type: str,
        description: str = "",
        affected_regions: Optional[List[str]] = None,
        affected_sources: Optional[List[str]] = None
    ) -> bool:
        """
        Apply a mitigation factor to reduce chaos pressure.
        
        Args:
            mitigation_type: Type of mitigation (diplomatic, economic, etc.)
            effectiveness: How effective the mitigation is (0.0 to 1.0)
            duration_hours: How long the mitigation lasts
            source_id: ID of the entity applying mitigation
            source_type: Type of entity (quest, npc, player, etc.)
            description: Human-readable description
            affected_regions: Regions this mitigation affects
            affected_sources: Pressure sources this mitigation affects
            
        Returns:
            True if mitigation was applied successfully
        """
        return await self.chaos_engine.apply_mitigation(
            mitigation_type=mitigation_type,
            effectiveness=effectiveness,
            duration_hours=duration_hours,
            source_id=source_id,
            source_type=source_type,
            description=description,
            affected_regions=affected_regions,
            affected_sources=affected_sources
        )
    
    async def force_trigger_event(
        self,
        event_type: str,
        severity: str = "moderate",
        regions: Optional[List[str]] = None
    ) -> bool:
        """
        Force trigger a chaos event (for testing or special circumstances).
        
        Args:
            event_type: Type of event to trigger
            severity: Severity level of the event
            regions: Regions to affect (None for global)
            
        Returns:
            True if event was triggered successfully
        """
        return await self.chaos_engine.force_trigger_event(
            event_type=event_type,
            severity=severity,
            regions=regions
        )
    
    def connect_system(self, system_name: str, system_handler) -> None:
        """
        Connect another game system to the chaos system.
        
        Args:
            system_name: Name of the system to connect
            system_handler: Handler for processing chaos events
        """
        self.chaos_engine.connect_system(system_name, system_handler)
    
    def update_config(self, **kwargs) -> None:
        """Update chaos system configuration."""
        self.chaos_engine.update_config(**kwargs)
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall health status of the chaos system."""
        return await self.chaos_engine.get_system_health()
    
    async def shutdown(self) -> None:
        """Shutdown the chaos service."""
        await self.chaos_engine.shutdown() 