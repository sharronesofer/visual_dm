"""
Pressure Monitor

Core component responsible for monitoring pressure across all game systems
and feeding data to the chaos calculation engine.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from uuid import UUID

from backend.systems.chaos.models.pressure_data import (
    PressureData, PressureReading, PressureSource, RegionalPressure
)
from backend.systems.chaos.core.config import ChaosConfig, chaos_config
from backend.systems.chaos.utils.pressure_calculations import PressureCalculations

logger = logging.getLogger(__name__)

class PressureMonitor:
    """
    Monitors pressure across all game systems in real-time.
    
    This component:
    - Collects pressure data from faction, economy, diplomacy, and other systems
    - Calculates weighted pressure values for different regions
    - Maintains historical pressure data for trend analysis
    - Provides real-time pressure alerts when thresholds are exceeded
    """
    
    def __init__(self, config: Optional[ChaosConfig] = None):
        self.config = config or chaos_config
        self.pressure_data = PressureData()
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # System connections - will be initialized during start()
        self._faction_service = None
        self._economy_service = None
        self._diplomacy_service = None
        self._region_service = None
        self._population_service = None
        self._npc_service = None
        
        # Performance tracking
        self._last_update_time = datetime.now()
        self._update_count = 0
        self._error_count = 0
        
        logger.info("PressureMonitor initialized")
    
    async def start(self) -> None:
        """Start pressure monitoring"""
        if self.is_monitoring:
            logger.warning("PressureMonitor already running")
            return
        
        logger.info("Starting pressure monitoring...")
        
        # Initialize system connections
        await self._initialize_system_connections()
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Pressure monitoring started successfully")
    
    async def stop(self) -> None:
        """Stop pressure monitoring"""
        if not self.is_monitoring:
            return
        
        logger.info("Stopping pressure monitoring...")
        
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Pressure monitoring stopped")
    
    async def _initialize_system_connections(self) -> None:
        """Initialize connections to other game systems"""
        try:
            # Import and initialize system services
            # Note: These imports are done here to avoid circular dependencies
            
            # Faction system
            try:
                from backend.systems.faction.services import faction_service
                self._faction_service = faction_service
            except ImportError:
                logger.warning("Could not import faction service")
            
            # Economy system
            try:
                from backend.systems.economy.services import economy_service
                self._economy_service = economy_service
            except ImportError:
                logger.warning("Could not import economy service")
            
            # Diplomacy system
            try:
                from backend.systems.diplomacy.services import diplomacy_service
                self._diplomacy_service = diplomacy_service
            except ImportError:
                logger.warning("Could not import diplomacy service")
            
            # Region system
            try:
                from backend.systems.region.services import region_service
                self._region_service = region_service
            except ImportError:
                logger.warning("Could not import region service")
            
            # Population system
            try:
                from backend.systems.population.services import population_service
                self._population_service = population_service
            except ImportError:
                logger.warning("Could not import population service")
            
            # NPC system
            try:
                from backend.systems.npc.services import npc_service
                self._npc_service = npc_service
            except ImportError:
                logger.warning("Could not import npc service")
            
            logger.info("System connections initialized")
            
        except Exception as e:
            logger.error(f"Error initializing system connections: {e}")
            # Continue with monitoring even if some systems are unavailable
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                start_time = datetime.now()
                
                # Collect pressure data from all systems
                await self._collect_pressure_data()
                
                # Calculate aggregated metrics
                self._calculate_pressure_metrics()
                
                # Clean up old data
                self._cleanup_old_data()
                
                # Update performance metrics
                end_time = datetime.now()
                self.pressure_data.calculation_time_ms = (end_time - start_time).total_seconds() * 1000
                self._update_count += 1
                self._last_update_time = end_time
                
                # Wait for next update cycle
                await asyncio.sleep(self.config.pressure_update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._error_count += 1
                self.pressure_data.errors_encountered += 1
                logger.error(f"Error in pressure monitoring loop: {e}")
                
                # Brief pause before retrying
                await asyncio.sleep(5.0)
    
    async def _collect_pressure_data(self) -> None:
        """Collect pressure data from all game systems"""
        
        # Collect from different systems in parallel for performance
        collection_tasks = [
            self._collect_faction_pressure(),
            self._collect_economic_pressure(),
            self._collect_diplomatic_pressure(),
            self._collect_population_pressure(),
            self._collect_military_pressure(),
            self._collect_environmental_pressure()
        ]
        
        # Execute all collection tasks
        results = await asyncio.gather(*collection_tasks, return_exceptions=True)
        
        # Log any collection errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Pressure collection task {i} failed: {result}")
    
    async def _collect_faction_pressure(self) -> None:
        """Collect pressure data from faction conflicts and tensions"""
        if not self._faction_service:
            return
        
        try:
            # Get all factions and their relationships
            factions = await self._faction_service.get_all_factions()
            
            for faction in factions:
                # Calculate faction conflict pressure
                conflict_pressure = await self._calculate_faction_conflict_pressure(faction)
                
                if conflict_pressure > 0:
                    reading = PressureReading(
                        source=PressureSource.FACTION_CONFLICT,
                        value=conflict_pressure,
                        location_id=faction.region_id if hasattr(faction, 'region_id') else None,
                        details={
                            'faction_id': str(faction.id),
                            'faction_name': faction.name if hasattr(faction, 'name') else 'Unknown',
                            'conflict_level': conflict_pressure
                        }
                    )
                    self.pressure_data.add_pressure_reading(reading)
        
        except Exception as e:
            logger.error(f"Error collecting faction pressure: {e}")
    
    async def _collect_economic_pressure(self) -> None:
        """Collect pressure data from economic instability"""
        if not self._economy_service:
            return
        
        try:
            # Get economic indicators by region
            regions = await self._get_all_regions()
            
            for region in regions:
                # Calculate economic instability pressure
                instability_pressure = await self._calculate_economic_instability(region)
                
                if instability_pressure > 0:
                    reading = PressureReading(
                        source=PressureSource.ECONOMIC_INSTABILITY,
                        value=instability_pressure,
                        location_id=region.id,
                        details={
                            'region_id': str(region.id),
                            'instability_level': instability_pressure,
                            'economic_factors': {}  # TODO: Add specific economic metrics
                        }
                    )
                    self.pressure_data.add_pressure_reading(reading)
        
        except Exception as e:
            logger.error(f"Error collecting economic pressure: {e}")
    
    async def _collect_diplomatic_pressure(self) -> None:
        """Collect pressure data from diplomatic tensions"""
        if not self._diplomacy_service:
            return
        
        try:
            # Get diplomatic relationships and tensions
            tensions = await self._get_diplomatic_tensions()
            
            for tension in tensions:
                diplomatic_pressure = self._calculate_diplomatic_pressure(tension)
                
                if diplomatic_pressure > 0:
                    reading = PressureReading(
                        source=PressureSource.DIPLOMATIC_TENSION,
                        value=diplomatic_pressure,
                        location_id=tension.get('region_id'),
                        details={
                            'tension_type': tension.get('type', 'unknown'),
                            'parties_involved': tension.get('parties', []),
                            'tension_level': diplomatic_pressure
                        }
                    )
                    self.pressure_data.add_pressure_reading(reading)
        
        except Exception as e:
            logger.error(f"Error collecting diplomatic pressure: {e}")
    
    async def _collect_population_pressure(self) -> None:
        """Collect pressure data from population stress"""
        if not self._population_service:
            return
        
        try:
            regions = await self._get_all_regions()
            
            for region in regions:
                # Calculate population stress indicators
                population_pressure = await self._calculate_population_pressure(region)
                
                if population_pressure > 0:
                    reading = PressureReading(
                        source=PressureSource.POPULATION_STRESS,
                        value=population_pressure,
                        location_id=region.id,
                        details={
                            'region_id': str(region.id),
                            'stress_factors': {},  # TODO: Add specific population metrics
                            'stress_level': population_pressure
                        }
                    )
                    self.pressure_data.add_pressure_reading(reading)
        
        except Exception as e:
            logger.error(f"Error collecting population pressure: {e}")
    
    async def _collect_military_pressure(self) -> None:
        """Collect pressure data from military buildups and conflicts"""
        try:
            # Get military activity data
            military_activities = await self._get_military_activities()
            
            for activity in military_activities:
                military_pressure = self._calculate_military_pressure(activity)
                
                if military_pressure > 0:
                    reading = PressureReading(
                        source=PressureSource.MILITARY_BUILDUP,
                        value=military_pressure,
                        location_id=activity.get('region_id'),
                        details={
                            'activity_type': activity.get('type', 'unknown'),
                            'scale': activity.get('scale', 0),
                            'pressure_level': military_pressure
                        }
                    )
                    self.pressure_data.add_pressure_reading(reading)
        
        except Exception as e:
            logger.error(f"Error collecting military pressure: {e}")
    
    async def _collect_environmental_pressure(self) -> None:
        """Collect pressure data from environmental factors"""
        try:
            regions = await self._get_all_regions()
            
            for region in regions:
                # Calculate environmental pressure factors
                env_pressure = await self._calculate_environmental_pressure(region)
                
                if env_pressure > 0:
                    reading = PressureReading(
                        source=PressureSource.ENVIRONMENTAL_PRESSURE,
                        value=env_pressure,
                        location_id=region.id,
                        details={
                            'region_id': str(region.id),
                            'environmental_factors': {},  # TODO: Add specific environmental metrics
                            'pressure_level': env_pressure
                        }
                    )
                    self.pressure_data.add_pressure_reading(reading)
        
        except Exception as e:
            logger.error(f"Error collecting environmental pressure: {e}")
    
    # Helper methods for pressure calculations
    
    async def _calculate_faction_conflict_pressure(self, faction) -> float:
        """Calculate pressure from faction conflicts"""
        # TODO: Implement actual faction conflict calculation
        # For now, return a placeholder value
        return 0.1  # Low baseline conflict
    
    async def _calculate_economic_instability(self, region) -> float:
        """Calculate economic instability pressure"""
        # TODO: Implement actual economic analysis
        return 0.05  # Low baseline instability
    
    def _calculate_diplomatic_pressure(self, tension: Dict[str, Any]) -> float:
        """Calculate diplomatic tension pressure"""
        # TODO: Implement actual diplomatic tension calculation
        return tension.get('level', 0.0)
    
    async def _calculate_population_pressure(self, region) -> float:
        """Calculate population stress pressure"""
        # TODO: Implement actual population stress calculation
        return 0.02  # Low baseline stress
    
    def _calculate_military_pressure(self, activity: Dict[str, Any]) -> float:
        """Calculate military buildup pressure"""
        # TODO: Implement actual military pressure calculation
        return activity.get('pressure_level', 0.0)
    
    async def _calculate_environmental_pressure(self, region) -> float:
        """Calculate environmental pressure"""
        # TODO: Implement actual environmental pressure calculation
        return 0.01  # Low baseline environmental pressure
    
    # Helper methods for data retrieval
    
    async def _get_all_regions(self) -> List[Any]:
        """Get all regions from the region system"""
        if self._region_service:
            try:
                return await self._region_service.get_all_regions()
            except Exception as e:
                logger.warning(f"Could not get regions: {e}")
        
        # Return empty list if region service unavailable
        return []
    
    async def _get_diplomatic_tensions(self) -> List[Dict[str, Any]]:
        """Get diplomatic tensions from diplomacy system"""
        if self._diplomacy_service:
            try:
                return await self._diplomacy_service.get_tensions()
            except Exception as e:
                logger.warning(f"Could not get diplomatic tensions: {e}")
        
        return []
    
    async def _get_military_activities(self) -> List[Dict[str, Any]]:
        """Get military activities"""
        # TODO: Implement military activity retrieval
        return []
    
    def _calculate_pressure_metrics(self) -> None:
        """Calculate aggregated pressure metrics for all regions"""
        # Get pressure source weights from config
        weights = {
            PressureSource.FACTION_CONFLICT: self.config.faction_conflict_weight,
            PressureSource.ECONOMIC_INSTABILITY: self.config.economic_instability_weight,
            PressureSource.POPULATION_STRESS: self.config.population_stress_weight,
            PressureSource.DIPLOMATIC_TENSION: self.config.diplomatic_tension_weight,
            PressureSource.MILITARY_BUILDUP: self.config.military_buildup_weight,
            PressureSource.ENVIRONMENTAL_PRESSURE: self.config.environmental_pressure_weight,
        }
        
        # Calculate global pressure
        self.pressure_data.global_pressure.calculate_global_pressure(weights)
        
        # Update pressure history
        self.pressure_data.global_pressure.update_pressure_history()
        
        # Calculate metrics for each region
        for region_pressure in self.pressure_data.global_pressure.regional_pressures.values():
            PressureCalculations.calculate_regional_metrics(region_pressure, weights)
    
    def _cleanup_old_data(self) -> None:
        """Clean up old pressure readings"""
        max_age_hours = 24  # Keep 24 hours of data
        removed_count = self.pressure_data.cleanup_old_readings(max_age_hours)
        
        if removed_count > 0:
            logger.debug(f"Cleaned up {removed_count} old pressure readings")
    
    # Public interface methods
    
    def get_current_pressure_data(self) -> PressureData:
        """Get current pressure data"""
        return self.pressure_data
    
    def get_global_pressure(self) -> float:
        """Get current global pressure level"""
        return self.pressure_data.global_pressure.weighted_pressure
    
    def get_regional_pressure(self, region_id: Union[str, UUID]) -> Optional[RegionalPressure]:
        """Get pressure data for a specific region"""
        return self.pressure_data.get_region_pressure(region_id)
    
    def get_pressure_trend(self) -> float:
        """Get current pressure trend (positive = increasing, negative = decreasing)"""
        return self.pressure_data.global_pressure.pressure_trend
    
    def get_crisis_regions(self, threshold: float = 0.7) -> List[RegionalPressure]:
        """Get regions with pressure above crisis threshold"""
        return self.pressure_data.global_pressure.get_crisis_regions(threshold)
    
    def is_pressure_above_threshold(self, threshold: float) -> bool:
        """Check if global pressure is above specified threshold"""
        return self.get_global_pressure() >= threshold
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        return {
            "is_monitoring": self.is_monitoring,
            "last_update": self._last_update_time.isoformat(),
            "update_count": self._update_count,
            "error_count": self._error_count,
            "total_readings": self.pressure_data.get_total_readings(),
            "global_pressure": self.get_global_pressure(),
            "pressure_trend": self.get_pressure_trend(),
            "system_connections": {
                "faction": self._faction_service is not None,
                "economy": self._economy_service is not None,
                "diplomacy": self._diplomacy_service is not None,
                "region": self._region_service is not None,
                "population": self._population_service is not None,
                "npc": self._npc_service is not None
            }
        }

# Global instance
pressure_monitor = PressureMonitor() 