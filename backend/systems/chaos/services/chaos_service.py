"""
Chaos Service

High-level service interface for the chaos system.
Now uses the unified ChaosManager for all operations.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.systems.chaos.core.config import ChaosConfig, chaos_config
from backend.systems.chaos.core.chaos_manager import ChaosManager

class ChaosService:
    """
    High-level service for chaos system operations.
    
    This service provides a simplified interface for other game systems
    to interact with the chaos system through the unified ChaosManager.
    """
    
    def __init__(self, config: Optional[ChaosConfig] = None):
        """Initialize the chaos service."""
        self.config = config or chaos_config
        self._chaos_manager: Optional[ChaosManager] = None
        
    @property
    def chaos_manager(self) -> ChaosManager:
        """Get the chaos manager instance."""
        if self._chaos_manager is None:
            self._chaos_manager = ChaosManager(self.config)
        return self._chaos_manager
    
    async def initialize(self) -> None:
        """Initialize the chaos service."""
        await self.chaos_manager.initialize()
        
    async def start(self) -> None:
        """Start the chaos system."""
        await self.chaos_manager.start()
        
    async def stop(self) -> None:
        """Stop the chaos system."""
        await self.chaos_manager.stop()
        
    def pause(self) -> None:
        """Pause chaos monitoring."""
        asyncio.create_task(self.chaos_manager.pause())
        
    def resume(self) -> None:
        """Resume chaos monitoring."""
        asyncio.create_task(self.chaos_manager.resume())
    
    def get_chaos_state(self, region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current chaos state for a region or globally.
        
        Args:
            region_id: Optional region ID to get specific regional state
            
        Returns:
            Dict containing chaos state information
        """
        # Use async wrapper for the manager call
        return asyncio.create_task(self.chaos_manager.get_chaos_state(region_id))
    
    def get_pressure_summary(self) -> Dict[str, Any]:
        """Get summary of current pressure across all systems."""
        return asyncio.create_task(self.chaos_manager.get_pressure_summary())
    
    def get_active_events(self) -> List[Dict[str, Any]]:
        """Get list of currently active chaos events."""
        if self.chaos_manager.chaos_engine:
            events = self.chaos_manager.chaos_engine.get_active_events()
            return [event.to_dict() for event in events.values()]
        return []
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about chaos events."""
        if self.chaos_manager.chaos_engine and hasattr(self.chaos_manager.chaos_engine, 'get_event_statistics'):
            return self.chaos_manager.chaos_engine.get_event_statistics()
        return {}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get chaos system performance metrics."""
        return self.chaos_manager.get_performance_metrics()
    
    # Warning System Interface (Bible three-tier escalation)
    async def get_warning_phases(self, region_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current warning phases for region(s)"""
        return await self.chaos_manager.get_warning_status()
    
    async def trigger_warning_phase(self, region_id: str, phase: str, event_type: str) -> bool:
        """Manually trigger a warning phase (rumor, early, imminent)"""
        if not self.chaos_manager.warning_system:
            return False
        
        return await self.chaos_manager.warning_system.trigger_warning(
            region_id, phase, event_type
        )
    
    async def clear_warning_phase(self, region_id: str, phase: str) -> bool:
        """Clear a warning phase"""
        if not self.chaos_manager.warning_system:
            return False
        
        return await self.chaos_manager.warning_system.clear_warning(region_id, phase)
    
    # Cascade Control Interface (Bible cascading effects)
    async def get_cascade_status(self) -> Dict[str, Any]:
        """Get status of cascading events"""
        if not self.chaos_manager.chaos_engine or not self.chaos_manager.chaos_engine.cascade_engine:
            return {'cascade_system_available': False}
        
        return {
            'cascade_system_available': True,
            'active_cascades': len(self.chaos_manager.chaos_engine.active_cascades),
            'cascade_history_count': len(self.chaos_manager.chaos_engine.cascade_history),
            'pending_cascades': await self.chaos_manager.chaos_engine.cascade_engine.get_pending_cascades() if hasattr(self.chaos_manager.chaos_engine.cascade_engine, 'get_pending_cascades') else []
        }
    
    async def force_cascade_event(self, source_event_id: str, target_event_type: str, 
                                  delay_hours: float = 1.0) -> bool:
        """Force trigger a cascade event"""
        if not self.chaos_manager.chaos_engine or not self.chaos_manager.chaos_engine.cascade_engine:
            return False
        
        return await self.chaos_manager.chaos_engine.cascade_engine.force_cascade(
            source_event_id, target_event_type, delay_hours
        )
    
    async def cancel_cascade(self, cascade_id: str) -> bool:
        """Cancel a pending cascade"""
        if not self.chaos_manager.chaos_engine or not self.chaos_manager.chaos_engine.cascade_engine:
            return False
        
        return await self.chaos_manager.chaos_engine.cascade_engine.cancel_cascade(cascade_id)
    
    # Narrative Intelligence Interface (Bible narrative weighting)
    async def update_narrative_context(self, 
                                      dramatic_tension: Optional[float] = None,
                                      player_engagement: Optional[float] = None,
                                      story_beats: Optional[List[str]] = None,
                                      themes: Optional[List[str]] = None) -> bool:
        """Update narrative context for intelligent chaos weighting"""
        if not self.chaos_manager.narrative_moderator:
            return False
        
        success = True
        
        try:
            if dramatic_tension is not None:
                success &= await self.chaos_manager.narrative_moderator.update_tension_level(dramatic_tension)
            if player_engagement is not None:
                success &= await self.chaos_manager.narrative_moderator.update_engagement_level(player_engagement)
            if story_beats is not None:
                # Add story beats
                for i, beat in enumerate(story_beats):
                    await self.chaos_manager.narrative_moderator.add_story_beat(
                        f"beat_{i}_{int(datetime.now().timestamp())}", 
                        beat, 
                        f"Story beat: {beat}",
                        0.5, 0.1, 1.0, 24.0
                    )
            if themes is not None:
                # Add themes
                for theme in themes:
                    await self.chaos_manager.narrative_moderator.add_narrative_theme(
                        theme.lower().replace(' ', '_'),
                        theme,
                        f"Narrative theme: {theme}",
                        "supporting",
                        1.2,
                        [],
                        24.0
                    )
            
            return success
            
        except Exception as e:
            print(f"Error updating narrative context: {e}")
            return False
    
    async def get_narrative_event_weights(self, pressure_data: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """Get narrative intelligence weights for event types"""
        if not self.chaos_manager.narrative_moderator:
            return {}
        
        narrative_context = await self.chaos_manager.get_narrative_status()
        
        if pressure_data is None:
            pressure_data = await self.chaos_manager.get_pressure_summary()
        
        return await self.chaos_manager.narrative_moderator.get_event_weights(
            narrative_context, pressure_data
        )
    
    async def set_narrative_theme_priority(self, theme: str, priority: float) -> bool:
        """Set priority for a narrative theme"""
        if not self.chaos_manager.narrative_moderator:
            return False
        
        return await self.chaos_manager.narrative_moderator.set_theme_priority(theme, priority)
    
    # Fatigue Management Interface (Bible distribution management)
    def get_fatigue_status(self) -> Dict[str, Any]:
        """Get current fatigue levels across all regions"""
        if not self.chaos_manager.chaos_engine:
            return {'error': 'ChaosEngine not available'}
        
        return {
            'global_fatigue': getattr(self.chaos_manager.chaos_engine, 'global_event_fatigue', 0.0),
            'regional_fatigue': getattr(self.chaos_manager.chaos_engine, 'regional_event_fatigue', {}).copy(),
            'fatigue_threshold': 0.7,  # Configurable
            'fatigued_regions': [
                region_id for region_id, fatigue in getattr(self.chaos_manager.chaos_engine, 'regional_event_fatigue', {}).items()
                if fatigue > 0.7
            ],
            'fatigue_decay_rate': getattr(self.chaos_manager.chaos_engine, 'fatigue_decay_rate', 0.1)
        }
    
    async def apply_fatigue_override(self, region_id: str, fatigue_level: float) -> bool:
        """Override fatigue level for a specific region"""
        if not self.chaos_manager.chaos_engine:
            return False
        
        try:
            if not hasattr(self.chaos_manager.chaos_engine, 'regional_event_fatigue'):
                self.chaos_manager.chaos_engine.regional_event_fatigue = {}
            
            self.chaos_manager.chaos_engine.regional_event_fatigue[region_id] = max(0.0, min(1.0, fatigue_level))
            return True
        except Exception as e:
            print(f"Error applying fatigue override: {e}")
            return False
    
    async def reset_fatigue(self, region_id: Optional[str] = None) -> bool:
        """Reset fatigue levels (region-specific or global)"""
        if not self.chaos_manager.chaos_engine:
            return False
        
        try:
            if region_id:
                if hasattr(self.chaos_manager.chaos_engine, 'regional_event_fatigue'):
                    self.chaos_manager.chaos_engine.regional_event_fatigue.pop(region_id, None)
            else:
                if hasattr(self.chaos_manager.chaos_engine, 'regional_event_fatigue'):
                    self.chaos_manager.chaos_engine.regional_event_fatigue.clear()
                if hasattr(self.chaos_manager.chaos_engine, 'global_event_fatigue'):
                    self.chaos_manager.chaos_engine.global_event_fatigue = 0.0
            return True
        except Exception as e:
            print(f"Error resetting fatigue: {e}")
            return False
    
    # Temporal Pressure Interface (Bible 6th pressure type)
    async def get_temporal_pressure_status(self) -> Dict[str, Any]:
        """Get status of temporal pressure monitoring"""
        return {
            'temporal_pressure_enabled': self.config.is_temporal_pressure_enabled(),
            'temporal_sources': self.config.get_temporal_pressure_sources(),
            'active_temporal_anomalies': len(getattr(self.chaos_manager.chaos_engine, 'temporal_anomalies', [])) if self.chaos_manager.chaos_engine else 0,
            'temporal_pressure_sources': len(getattr(self.chaos_manager.chaos_engine, 'temporal_pressure_sources', [])) if self.chaos_manager.chaos_engine else 0
        }
    
    async def inject_temporal_anomaly(self, anomaly_type: str, severity: float, 
                                     region_id: Optional[str] = None, 
                                     duration_hours: float = 24.0) -> bool:
        """Inject a temporal anomaly for testing or special events"""
        if not self.chaos_manager.chaos_engine:
            return False
        
        try:
            anomaly = {
                'type': anomaly_type,
                'severity': max(0.0, min(1.0, severity)),
                'region_id': region_id,
                'duration_hours': duration_hours,
                'created_at': datetime.now(),
                'source': 'manual_injection'
            }
            
            if not hasattr(self.chaos_manager.chaos_engine, 'temporal_anomalies'):
                self.chaos_manager.chaos_engine.temporal_anomalies = []
            
            self.chaos_manager.chaos_engine.temporal_anomalies.append(anomaly)
            return True
            
        except Exception as e:
            print(f"Error injecting temporal anomaly: {e}")
            return False
    
    # System Integration Interface
    async def get_system_connection_status(self) -> Dict[str, Any]:
        """Get status of connections to other game systems"""
        if not self.chaos_manager.pressure_monitor:
            return {'error': 'PressureMonitor not available'}
        
        return self.chaos_manager.pressure_monitor.get_connection_status()
    
    async def retry_system_connections(self) -> Dict[str, bool]:
        """Retry failed system connections"""
        if not self.chaos_manager.pressure_monitor:
            return {}
        
        return await self.chaos_manager.pressure_monitor.retry_failed_connections()

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
        """Apply a mitigation factor to reduce chaos pressure."""
        return await self.chaos_manager.apply_mitigation(
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
        """Force trigger a chaos event (for testing or special circumstances)."""
        return await self.chaos_manager.force_trigger_event(
            event_type=event_type,
            severity=severity,
            regions=regions
        )
    
    def connect_system(self, system_name: str, system_handler) -> None:
        """Connect another game system to the chaos system."""
        if self.chaos_manager.chaos_engine and hasattr(self.chaos_manager.chaos_engine, 'connect_system'):
            self.chaos_manager.chaos_engine.connect_system(system_name, system_handler)
    
    def update_config(self, **kwargs) -> None:
        """Update chaos system configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall health status of the chaos system."""
        return self.chaos_manager.get_system_status()
    
    async def shutdown(self) -> None:
        """Shutdown the chaos service."""
        await self.stop() 