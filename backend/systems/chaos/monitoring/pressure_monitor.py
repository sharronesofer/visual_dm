"""
Pressure Monitor

Monitors and tracks pressure data across different systems and regions.
Handles Bible-compliant pressure collection including temporal pressure.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from backend.systems.chaos.core.config import ChaosConfig
from backend.infrastructure.systems.chaos.models.pressure_data import PressureData
from backend.infrastructure.systems.chaos.models.chaos_state import MitigationFactor

@dataclass
class PressureSnapshot:
    """A snapshot of pressure data at a specific time"""
    timestamp: datetime
    region_id: str
    pressure_sources: Dict[str, float]
    total_pressure: float
    temporal_pressure: float = 0.0
    active_mitigations: List[str] = field(default_factory=list)

class PressureMonitor:
    """
    Monitors pressure data across all systems and regions.
    
    Handles Bible-compliant pressure collection including:
    - 5 traditional pressure types (economic, political, social, environmental, diplomatic)
    - 6th pressure type: temporal pressure (Bible requirement)
    - Cross-system pressure collection
    - Mitigation tracking and effects
    """
    
    def __init__(self, config: ChaosConfig):
        """Initialize the pressure monitor"""
        self.config = config
        
        # Current pressure data by region
        self.regional_pressure: Dict[str, PressureData] = {}
        
        # Pressure history for trend analysis
        self.pressure_history: List[PressureSnapshot] = []
        
        # Active mitigations
        self.active_mitigations: Dict[str, MitigationFactor] = {}
        
        # Temporal pressure tracking (Bible 6th pressure type)
        self.temporal_pressure_data: Dict[str, float] = {}
        
        # System integration handlers
        self.external_pressure_sources: Dict[str, Any] = {}
        
        # Monitoring state
        self._initialized = False
        self._monitoring_active = False
        
        # Performance tracking
        self.update_count = 0
        self.last_update = datetime.now()
    
    async def initialize(self) -> None:
        """Initialize the pressure monitor"""
        # Setup temporal pressure monitoring if enabled
        if self.config.is_temporal_pressure_enabled():
            await self._initialize_temporal_pressure_monitoring()
        
        # Initialize pressure collection systems
        await self._initialize_pressure_collection()
        
        self._initialized = True
        print("Pressure monitor initialized")
    
    async def get_current_pressure(self, region_id: str = "global") -> PressureData:
        """
        Get current pressure data for a region or globally.
        
        Args:
            region_id: Region to get pressure for, or "global" for aggregated data
            
        Returns:
            PressureData object with current pressure information
        """
        if region_id == "global":
            return await self._get_global_pressure_data()
        
        # Get regional pressure data
        if region_id in self.regional_pressure:
            return self.regional_pressure[region_id]
        
        # Return empty pressure data if region not found
        return PressureData(
            region_id=region_id,
            pressure_sources={},
            calculation_timestamp=datetime.now(),
            calculation_time_ms=0.0
        )
    
    async def update_pressure_sources(self, pressure_sources: Dict[str, float], 
                                    region_id: str = "global") -> None:
        """
        Update pressure sources for a specific region.
        
        Args:
            pressure_sources: Dict of pressure type -> value
            region_id: Region to update pressure for
        """
        current_time = datetime.now()
        
        # Ensure region exists
        if region_id not in self.regional_pressure:
            self.regional_pressure[region_id] = PressureData(
                region_id=region_id,
                pressure_sources={},
                calculation_timestamp=current_time,
                calculation_time_ms=0.0
            )
        
        # Update pressure sources
        regional_data = self.regional_pressure[region_id]
        regional_data.pressure_sources.update(pressure_sources)
        regional_data.calculation_timestamp = current_time
        
        # Apply pressure decay if configured
        if self.config.pressure_decay_rate > 0:
            await self._apply_pressure_decay(region_id)
        
        # Apply mitigation effects
        await self._apply_mitigation_effects(region_id)
        
        # Update temporal pressure if enabled
        if self.config.is_temporal_pressure_enabled():
            await self._update_temporal_pressure(region_id)
        
        # Record pressure snapshot for history
        await self._record_pressure_snapshot(region_id)
        
        self.update_count += 1
        self.last_update = current_time
    
    async def apply_mitigation(self, mitigation: MitigationFactor) -> bool:
        """
        Apply a mitigation factor to reduce pressure.
        
        Args:
            mitigation: MitigationFactor object with mitigation details
            
        Returns:
            True if mitigation was applied successfully
        """
        try:
            # Store the mitigation
            mitigation_id = f"{mitigation.mitigation_type}_{mitigation.source_id}_{datetime.now().timestamp()}"
            self.active_mitigations[mitigation_id] = mitigation
            
            # Apply immediate mitigation effects to affected regions
            affected_regions = mitigation.affected_regions or ["global"]
            for region_id in affected_regions:
                await self._apply_mitigation_to_region(mitigation, region_id)
            
            print(f"Applied mitigation {mitigation_id} with {mitigation.base_effectiveness:.1%} effectiveness")
            return True
            
        except Exception as e:
            print(f"Error applying mitigation: {e}")
            return False
    
    async def remove_mitigation(self, mitigation_id: str) -> bool:
        """
        Remove an active mitigation.
        
        Args:
            mitigation_id: ID of the mitigation to remove
            
        Returns:
            True if mitigation was removed successfully
        """
        if mitigation_id in self.active_mitigations:
            del self.active_mitigations[mitigation_id]
            print(f"Removed mitigation {mitigation_id}")
            return True
        return False
    
    def get_latest_pressure_sync(self, region_id: str = "global") -> Optional[PressureData]:
        """
        Get latest pressure data synchronously (for compatibility).
        
        Args:
            region_id: Region to get pressure for
            
        Returns:
            PressureData object or None if not available
        """
        if region_id == "global":
            # Return aggregated pressure from all regions
            if not self.regional_pressure:
                return None
            
            # Aggregate pressure sources
            aggregated_sources = {}
            total_regions = len(self.regional_pressure)
            
            for region_data in self.regional_pressure.values():
                for source, value in region_data.pressure_sources.items():
                    aggregated_sources[source] = aggregated_sources.get(source, 0) + value
            
            # Average the aggregated values
            for source in aggregated_sources:
                aggregated_sources[source] /= total_regions
            
            return PressureData(
                region_id="global",
                pressure_sources=aggregated_sources,
                calculation_timestamp=datetime.now(),
                calculation_time_ms=0.0
            )
        
        return self.regional_pressure.get(region_id)
    
    def get_current_pressure_data(self, region_id: str = "global") -> PressureData:
        """
        Get current pressure data synchronously (test compatibility method).
        
        Args:
            region_id: Region to get pressure for
            
        Returns:
            PressureData object with current pressure information
        """
        # For test compatibility, create a simple PressureData object
        pressure_data = PressureData(
            region_id=region_id,
            pressure_sources={
                'economic': 0.0,
                'political': 0.0,
                'social': 0.0,
                'environmental': 0.0,
                'diplomatic': 0.0
            },
            calculation_timestamp=datetime.now(),
            calculation_time_ms=1.0,
            global_pressure=0.0
        )
        
        # If we have regional data, use it
        if region_id in self.regional_pressure:
            existing_data = self.regional_pressure[region_id]
            pressure_data.pressure_sources.update(existing_data.pressure_sources)
            pressure_data.calculation_timestamp = existing_data.calculation_timestamp
            pressure_data.calculation_time_ms = existing_data.calculation_time_ms
        
        return pressure_data
    
    async def _get_global_pressure_data(self) -> PressureData:
        """Get aggregated global pressure data from all regions"""
        if not self.regional_pressure:
            return PressureData(
                region_id="global",
                pressure_sources={},
                calculation_timestamp=datetime.now(),
                calculation_time_ms=0.0
            )
        
        # Aggregate pressure sources across all regions
        aggregated_sources = {}
        total_regions = len(self.regional_pressure)
        
        for region_data in self.regional_pressure.values():
            for source, value in region_data.pressure_sources.items():
                aggregated_sources[source] = aggregated_sources.get(source, 0) + value
        
        # Average the aggregated values
        for source in aggregated_sources:
            aggregated_sources[source] /= total_regions
        
        # Add temporal pressure if enabled
        if self.config.is_temporal_pressure_enabled():
            temporal_pressure = sum(self.temporal_pressure_data.values()) / max(1, len(self.temporal_pressure_data))
            aggregated_sources['temporal'] = temporal_pressure
        
        return PressureData(
            region_id="global",
            pressure_sources=aggregated_sources,
            calculation_timestamp=datetime.now(),
            calculation_time_ms=0.0
        )
    
    async def _apply_pressure_decay(self, region_id: str) -> None:
        """Apply natural pressure decay over time (Bible requirement)"""
        if region_id not in self.regional_pressure:
            return
        
        regional_data = self.regional_pressure[region_id]
        decay_rate = self.config.pressure_decay_rate
        
        # Apply decay to all pressure sources
        for source in regional_data.pressure_sources:
            current_value = regional_data.pressure_sources[source]
            decayed_value = current_value * (1.0 - decay_rate)
            regional_data.pressure_sources[source] = max(0.0, decayed_value)
    
    async def _apply_mitigation_effects(self, region_id: str) -> None:
        """Apply mitigation effects to pressure values"""
        if region_id not in self.regional_pressure:
            return
        
        regional_data = self.regional_pressure[region_id]
        
        # Apply effects from all active mitigations
        for mitigation in self.active_mitigations.values():
            # Check if mitigation affects this region
            if region_id in mitigation.affected_regions or "global" in mitigation.affected_regions:
                await self._apply_mitigation_to_region(mitigation, region_id)
    
    async def _apply_mitigation_to_region(self, mitigation: MitigationFactor, region_id: str) -> None:
        """Apply a specific mitigation to a region's pressure"""
        if region_id not in self.regional_pressure:
            return
        
        regional_data = self.regional_pressure[region_id]
        current_effectiveness = mitigation.get_current_effectiveness()
        
        # Apply mitigation to affected pressure sources
        affected_sources = mitigation.affected_sources or list(regional_data.pressure_sources.keys())
        
        for source in affected_sources:
            if source in regional_data.pressure_sources:
                current_value = regional_data.pressure_sources[source]
                mitigated_value = current_value * (1.0 - current_effectiveness)
                regional_data.pressure_sources[source] = max(0.0, mitigated_value)
    
    async def _update_temporal_pressure(self, region_id: str) -> None:
        """Update temporal pressure for a region (Bible 6th pressure type)"""
        if not self.config.is_temporal_pressure_enabled():
            return
        
        # Simulate temporal pressure (in real implementation, this would come from time system)
        temporal_sources = self.config.get_temporal_pressure_sources()
        temporal_pressure = 0.0
        
        # Calculate temporal pressure from various sources
        for source in temporal_sources:
            # In real implementation, this would query the time system
            # For now, simulate low baseline temporal pressure
            source_pressure = 0.01  # Low baseline temporal instability
            temporal_pressure += source_pressure
        
        # Store temporal pressure for this region
        self.temporal_pressure_data[region_id] = temporal_pressure
        
        # Add temporal pressure to regional data
        if region_id in self.regional_pressure:
            self.regional_pressure[region_id].pressure_sources['temporal'] = temporal_pressure
    
    async def _record_pressure_snapshot(self, region_id: str) -> None:
        """Record a pressure snapshot for history tracking"""
        if region_id not in self.regional_pressure:
            return
        
        regional_data = self.regional_pressure[region_id]
        total_pressure = sum(regional_data.pressure_sources.values())
        temporal_pressure = regional_data.pressure_sources.get('temporal', 0.0)
        
        snapshot = PressureSnapshot(
            timestamp=datetime.now(),
            region_id=region_id,
            pressure_sources=regional_data.pressure_sources.copy(),
            total_pressure=total_pressure,
            temporal_pressure=temporal_pressure,
            active_mitigations=list(self.active_mitigations.keys())
        )
        
        self.pressure_history.append(snapshot)
        
        # Limit history size for performance
        max_history = self.config.pressure_history_max_entries
        if len(self.pressure_history) > max_history:
            self.pressure_history = self.pressure_history[-max_history:]
    
    async def _initialize_temporal_pressure_monitoring(self) -> None:
        """Initialize temporal pressure monitoring (Bible 6th pressure type)"""
        temporal_sources = self.config.get_temporal_pressure_sources()
        print(f"Initialized temporal pressure monitoring for sources: {temporal_sources}")
        
        # Initialize temporal pressure data
        for source in temporal_sources:
            self.temporal_pressure_data[source] = 0.0
    
    async def _initialize_pressure_collection(self) -> None:
        """Initialize pressure collection from external systems"""
        # Setup framework for external system integration
        # External systems will register themselves via the chaos engine
        pass
    
    def get_pressure_history(self, region_id: str = "global", hours: int = 24) -> List[PressureSnapshot]:
        """
        Get pressure history for a region.
        
        Args:
            region_id: Region to get history for
            hours: Number of hours of history to retrieve
            
        Returns:
            List of pressure snapshots
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if region_id == "global":
            # Return all history for global view
            return [
                snapshot for snapshot in self.pressure_history 
                if snapshot.timestamp >= cutoff_time
            ]
        else:
            # Return history for specific region
            return [
                snapshot for snapshot in self.pressure_history 
                if snapshot.region_id == region_id and snapshot.timestamp >= cutoff_time
            ]
    
    def get_monitoring_metrics(self) -> Dict[str, Any]:
        """Get monitoring performance metrics"""
        return {
            'update_count': self.update_count,
            'last_update': self.last_update.isoformat(),
            'regions_monitored': len(self.regional_pressure),
            'active_mitigations': len(self.active_mitigations),
            'pressure_history_size': len(self.pressure_history),
            'temporal_pressure_enabled': self.config.is_temporal_pressure_enabled(),
            'temporal_sources_count': len(self.temporal_pressure_data),
            'monitoring_active': self._monitoring_active
        }
    
    def register_external_pressure_source(self, source_name: str, handler: Any) -> None:
        """Register an external system as a pressure source"""
        self.external_pressure_sources[source_name] = handler
        print(f"Registered external pressure source: {source_name}")
    
    async def collect_external_pressure(self) -> Dict[str, float]:
        """Collect pressure data from all registered external sources"""
        external_pressure = {}
        
        for source_name, handler in self.external_pressure_sources.items():
            try:
                if hasattr(handler, 'get_pressure_data'):
                    pressure_data = await handler.get_pressure_data()
                    if pressure_data:
                        external_pressure.update(pressure_data)
            except Exception as e:
                print(f"Error collecting pressure from {source_name}: {e}")
        
        return external_pressure 