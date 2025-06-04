"""
Pressure Monitor

Core component responsible for monitoring pressure across all game systems
and feeding data to the chaos calculation engine.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from uuid import UUID

from backend.infrastructure.systems.chaos.models.pressure_data import (
    PressureData, PressureReading, PressureSource, RegionalPressure
)
from backend.systems.chaos.core.config import ChaosConfig, chaos_config
from backend.infrastructure.systems.chaos.utils.pressure_calculations import PressureCalculations

class SystemConnectionError(Exception):
    """Raised when a system connection fails"""
    pass

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
        self._paused = False
        self._initialized = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # System connections - properly initialized with error tracking
        self._system_connections = {}
        self._connection_errors = {}
        self._failed_systems = set()
        
        # Performance tracking
        self._last_update_time = datetime.now()
        self._update_count = 0
        self._error_count = 0
        
        # Temporal pressure tracking (Bible 6th pressure type)
        self._temporal_pressure_sources = {}
        self._temporal_anomalies = []
    
    async def initialize(self) -> None:
        """Initialize the pressure monitor"""
        if self._initialized:
            return
        
        # Initialize system connections with proper error handling
        await self._initialize_system_connections()
        self._initialized = True
    
    async def start(self) -> None:
        """Start pressure monitoring"""
        if not self._initialized:
            await self.initialize()
            
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop(self) -> None:
        """Stop pressure monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self._paused = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
    
    async def pause(self) -> None:
        """Pause pressure monitoring without stopping"""
        if not self.is_monitoring:
            return
        self._paused = True
    
    async def resume(self) -> None:
        """Resume pressure monitoring after pause"""
        if not self.is_monitoring:
            return
        self._paused = False
    
    async def _initialize_system_connections(self) -> None:
        """Initialize connections to other game systems with proper error handling"""
        system_imports = {
            'faction': ('backend.systems.faction.services', 'faction_service'),
            'economy': ('backend.systems.economy.services', 'economy_service'),
            'diplomacy': ('backend.systems.diplomacy.services', 'diplomacy_service'),
            'region': ('backend.systems.region.services', 'region_service'),
            'population': ('backend.systems.population.services', 'population_service'),
            'npc': ('backend.systems.npc.services', 'npc_service'),
            'tension': ('backend.systems.tension.services', 'tension_service'),
            'game_time': ('backend.systems.game_time.services', 'time_service')
        }
        
        for system_name, (module_path, service_name) in system_imports.items():
            try:
                module = __import__(module_path, fromlist=[service_name])
                service = getattr(module, service_name)
                self._system_connections[system_name] = service
                print(f"Successfully connected to {system_name} system")
                
            except ImportError as e:
                error_msg = f"Could not import {system_name} system: {e}"
                self._connection_errors[system_name] = error_msg
                self._failed_systems.add(system_name)
                print(f"Warning: {error_msg}")
                
            except AttributeError as e:
                error_msg = f"Service {service_name} not found in {system_name} system: {e}"
                self._connection_errors[system_name] = error_msg
                self._failed_systems.add(system_name)
                print(f"Warning: {error_msg}")
                
            except Exception as e:
                error_msg = f"Unexpected error connecting to {system_name} system: {e}"
                self._connection_errors[system_name] = error_msg
                self._failed_systems.add(system_name)
                print(f"Error: {error_msg}")
        
        # Report connection status
        connected_systems = len(self._system_connections)
        total_systems = len(system_imports)
        print(f"Pressure monitor initialized: {connected_systems}/{total_systems} systems connected")
        
        if self._failed_systems:
            print(f"Failed to connect to systems: {', '.join(self._failed_systems)}")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get the status of all system connections"""
        return {
            'connected_systems': list(self._system_connections.keys()),
            'failed_systems': list(self._failed_systems),
            'connection_errors': self._connection_errors.copy(),
            'total_connections': len(self._system_connections),
            'success_rate': len(self._system_connections) / (len(self._system_connections) + len(self._failed_systems)) if (self._system_connections or self._failed_systems) else 0.0
        }
    
    async def retry_failed_connections(self) -> Dict[str, bool]:
        """Retry connections to failed systems"""
        retry_results = {}
        
        for system_name in list(self._failed_systems):
            try:
                # Re-attempt connection
                await self._connect_single_system(system_name)
                self._failed_systems.discard(system_name)
                if system_name in self._connection_errors:
                    del self._connection_errors[system_name]
                retry_results[system_name] = True
                
            except Exception as e:
                retry_results[system_name] = False
                self._connection_errors[system_name] = str(e)
        
        return retry_results
    
    async def _connect_single_system(self, system_name: str) -> None:
        """Connect to a single system (helper for retry logic)"""
        system_imports = {
            'faction': ('backend.systems.faction.services', 'faction_service'),
            'economy': ('backend.systems.economy.services', 'economy_service'),
            'diplomacy': ('backend.systems.diplomacy.services', 'diplomacy_service'),
            'region': ('backend.systems.region.services', 'region_service'),
            'population': ('backend.systems.population.services', 'population_service'),
            'npc': ('backend.systems.npc.services', 'npc_service'),
            'tension': ('backend.systems.tension.services', 'tension_service'),
            'game_time': ('backend.systems.game_time.services', 'time_service')
        }
        
        if system_name not in system_imports:
            raise SystemConnectionError(f"Unknown system: {system_name}")
        
        module_path, service_name = system_imports[system_name]
        module = __import__(module_path, fromlist=[service_name])
        service = getattr(module, service_name)
        self._system_connections[system_name] = service

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Skip processing if paused, but keep the loop running
                if self._paused:
                    await asyncio.sleep(1.0)  # Short sleep when paused
                    continue
                
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
                print(f"Error in pressure monitoring loop: {e}")
                
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
            self._collect_environmental_pressure(),
            self._collect_temporal_pressure()  # Bible 6th pressure type
        ]
        
        # Execute all collection tasks
        results = await asyncio.gather(*collection_tasks, return_exceptions=True)
        
        # Handle any collection errors with proper logging
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                task_names = ['faction', 'economic', 'diplomatic', 'population', 'military', 'environmental', 'temporal']
                task_name = task_names[i] if i < len(task_names) else f"task_{i}"
                print(f"Error collecting {task_name} pressure: {result}")
                self._error_count += 1
    
    async def _collect_temporal_pressure(self) -> None:
        """Collect temporal pressure data (Bible 6th pressure type)"""
        if not self.config.is_temporal_pressure_enabled():
            return
        
        try:
            # Get time system connection
            time_service = self._system_connections.get('game_time')
            if not time_service:
                return
            
            # Collect temporal anomalies and time distortions
            temporal_anomalies = await self._get_temporal_anomalies(time_service)
            
            for anomaly in temporal_anomalies:
                temporal_pressure = self._calculate_temporal_pressure(anomaly)
                
                if temporal_pressure > 0:
                    reading = PressureReading(
                        source=PressureSource.TEMPORAL,
                        value=temporal_pressure,
                        location_id=anomaly.get('region_id'),
                        details={
                            'anomaly_type': anomaly.get('type', 'unknown'),
                            'severity': anomaly.get('severity', 1.0),
                            'duration': anomaly.get('duration_hours', 0),
                            'source': 'temporal_monitor'
                        },
                        timestamp=datetime.now()
                    )
                    
                    self.pressure_data.add_pressure_reading(reading)
                    
        except Exception as e:
            # Don't let temporal pressure collection failure stop other monitoring
            print(f"Warning: Temporal pressure collection failed: {e}")
    
    async def _get_temporal_anomalies(self, time_service) -> List[Dict[str, Any]]:
        """Get temporal anomalies from time system"""
        try:
            if hasattr(time_service, 'get_temporal_anomalies'):
                return await time_service.get_temporal_anomalies()
            elif hasattr(time_service, 'get_time_distortions'):
                return await time_service.get_time_distortions()
            else:
                # Fallback: generate synthetic temporal pressure
                return self._generate_synthetic_temporal_pressure()
                
        except Exception as e:
            print(f"Error getting temporal anomalies: {e}")
            return []
    
    def _generate_synthetic_temporal_pressure(self) -> List[Dict[str, Any]]:
        """Generate synthetic temporal pressure when time system unavailable"""
        # This provides baseline temporal pressure for testing
        import random
        
        # Low-level ambient temporal pressure
        base_pressure = random.uniform(0.01, 0.05)
        
        return [{
            'type': 'ambient_temporal_drift',
            'severity': base_pressure,
            'duration_hours': 24,
            'region_id': None,  # Global effect
            'source': 'synthetic'
        }]
    
    def _calculate_temporal_pressure(self, anomaly: Dict[str, Any]) -> float:
        """Calculate pressure contribution from temporal anomaly"""
        base_severity = anomaly.get('severity', 0.0)
        anomaly_type = anomaly.get('type', 'unknown')
        
        # Different temporal anomaly types have different pressure impacts
        type_multipliers = {
            'time_loop': 0.8,
            'temporal_storm': 1.2,
            'chronological_drift': 0.6,
            'timeline_fracture': 1.5,
            'age_acceleration': 0.7,
            'temporal_void': 1.8,
            'ambient_temporal_drift': 0.1
        }
        
        multiplier = type_multipliers.get(anomaly_type, 1.0)
        return min(1.0, base_severity * multiplier)

    async def _collect_faction_pressure(self) -> None:
        """Collect pressure data from faction conflicts and tensions"""
        faction_service = self._system_connections.get('faction')
        if not faction_service:
            return
        
        try:
            # Get all factions and their relationships
            if hasattr(faction_service, 'get_all_factions'):
                factions = await faction_service.get_all_factions()
            else:
                # Fallback method
                factions = getattr(faction_service, 'factions', [])
            
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
                            'faction_name': getattr(faction, 'name', 'Unknown'),
                            'conflict_type': 'territorial_dispute',
                            'escalation_level': 'moderate'
                        },
                        timestamp=datetime.now()
                    )
                    
                    self.pressure_data.add_pressure_reading(reading)
                    
        except Exception as e:
            raise SystemConnectionError(f"Faction pressure collection failed: {e}")

    async def _collect_economic_pressure(self) -> None:
        """Collect pressure data from economic instability"""
        try:
            regions = await self._get_all_regions()
            
            for region in regions:
                # Calculate economic instability
                economic_pressure = await self._calculate_economic_instability(region)
                
                if economic_pressure > 0:
                    # Get detailed economic factors for reporting
                    economic_factors = {}
                    
                    if self._system_connections.get('economy'):
                        try:
                            economic_data = await self._system_connections['economy'].get_region_economic_status(region.id)
                            economic_factors = {
                                'market_volatility': economic_data.get('market_volatility', 0.0),
                                'trade_disruption': economic_data.get('trade_disruption', 0.0),
                                'resource_scarcity': economic_data.get('resource_scarcity', 0.0),
                                'inflation_rate': economic_data.get('inflation_rate', 0.0),
                                'unemployment_rate': economic_data.get('unemployment_rate', 0.0),
                                'economic_status': economic_data.get('status', 'unknown')
                            }
                        except Exception as e:
                            pass
                            # Fallback to basic region data
                            if hasattr(region, 'economic_status'):
                                economic_factors['status'] = region.economic_status
                    else:
                        # Use region-level data if available
                        if hasattr(region, 'economic_status'):
                            economic_factors['status'] = region.economic_status
                        if hasattr(region, 'trade_routes'):
                            economic_factors['trade_route_count'] = len(region.trade_routes)
                    
                    reading = PressureReading(
                        source=PressureSource.ECONOMIC_INSTABILITY,
                        value=economic_pressure,
                        location_id=region.id,
                        details={
                            'region_id': str(region.id),
                            'economic_factors': economic_factors,
                            'instability_level': economic_pressure
                        }
                    )
                    self.pressure_data.add_pressure_reading(reading)
        
        except Exception as e:
            pass
    
    async def _collect_diplomatic_pressure(self) -> None:
        """Collect pressure data from diplomatic tensions"""
        try:
            # Get diplomatic tensions
            tensions = await self._get_diplomatic_tensions()
            
            for tension in tensions:
                diplomatic_pressure = self._calculate_diplomatic_pressure(tension)
                
                if diplomatic_pressure > 0:
                    reading = PressureReading(
                        source=PressureSource.DIPLOMATIC_TENSION,
                        value=diplomatic_pressure,
                        location_id=tension.get('region_id'),
                        details={
                            'faction_a_id': tension.get('faction_a_id'),
                            'faction_b_id': tension.get('faction_b_id'),
                            'tension_level': tension.get('tension', 0),
                            'diplomatic_status': tension.get('status', 'neutral'),
                            'last_updated': tension.get('last_updated'),
                            'pressure_level': diplomatic_pressure
                        }
                    )
                    self.pressure_data.add_pressure_reading(reading)
        
        except Exception as e:
            pass
    
    async def _collect_population_pressure(self) -> None:
        """Collect pressure data from population stress"""
        try:
            regions = await self._get_all_regions()
            
            for region in regions:
                # Calculate population pressure
                population_pressure = await self._calculate_population_pressure(region)
                
                if population_pressure > 0:
                    # Get detailed population factors
                    stress_factors = {}
                    
                    if self._system_connections.get('population'):
                        try:
                            population_data = await self._system_connections['population'].get_region_population_status(region.id)
                            stress_factors = {
                                'population_density': population_data.get('density', 0.0),
                                'max_capacity': population_data.get('max_capacity', 1.0),
                                'food_security': population_data.get('food_security', 1.0),
                                'employment_rate': population_data.get('employment_rate', 0.8),
                                'health_index': population_data.get('health_index', 0.8),
                                'crime_rate': population_data.get('crime_rate', 0.1),
                                'total_population': population_data.get('total_population', 0)
                            }
                        except Exception as e:
                            pass
                            # Fallback to region attributes
                            if hasattr(region, 'population_density'):
                                stress_factors['population_density'] = region.population_density
                            if hasattr(region, 'stability'):
                                stress_factors['stability'] = region.stability
                    else:
                        # Use basic region data
                        if hasattr(region, 'population_density'):
                            stress_factors['population_density'] = region.population_density
                        if hasattr(region, 'stability'):
                            stress_factors['stability'] = region.stability
                        if hasattr(region, 'population'):
                            stress_factors['total_population'] = region.population
                    
                    reading = PressureReading(
                        source=PressureSource.POPULATION_STRESS,
                        value=population_pressure,
                        location_id=region.id,
                        details={
                            'region_id': str(region.id),
                            'stress_factors': stress_factors,
                            'stress_level': population_pressure
                        }
                    )
                    self.pressure_data.add_pressure_reading(reading)
        
        except Exception as e:
            pass
    
    async def _collect_military_pressure(self) -> None:
        """Collect pressure data from military buildups and conflicts"""
        try:
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
                            'urgency': activity.get('urgency', 0),
                            'threat_level': activity.get('threat_level', 0),
                            'faction_id': activity.get('faction_id'),
                            'pressure_level': military_pressure
                        }
                    )
                    self.pressure_data.add_pressure_reading(reading)
        
        except Exception as e:
            pass
    
    async def _collect_environmental_pressure(self) -> None:
        """Collect pressure data from environmental factors"""
        try:
            regions = await self._get_all_regions()
            
            for region in regions:
                # Calculate environmental pressure factors
                env_pressure = await self._calculate_environmental_pressure(region)
                
                if env_pressure > 0:
                    # Get detailed environmental factors
                    environmental_factors = {}
                    
                    if hasattr(region, 'environmental_status'):
                        env_status = region.environmental_status
                        environmental_factors = {
                            'weather_severity': env_status.get('weather_severity', 0.0),
                            'disaster_risk': env_status.get('disaster_risk', 0.0),
                            'resource_depletion': env_status.get('resource_depletion', 0.0),
                            'pollution_level': env_status.get('pollution_level', 0.0),
                            'climate_impact': env_status.get('climate_impact', 0.0)
                        }
                    
                    if hasattr(region, 'natural_disasters'):
                        environmental_factors['active_disasters'] = region.natural_disasters.get('active', [])
                        environmental_factors['disaster_count'] = len(region.natural_disasters.get('active', []))
                    
                    if hasattr(region, 'season'):
                        environmental_factors['current_season'] = region.season
                    
                    # Add resource availability if available
                    if hasattr(region, 'resources'):
                        environmental_factors['resource_availability'] = region.resources
                    
                    reading = PressureReading(
                        source=PressureSource.ENVIRONMENTAL_PRESSURE,
                        value=env_pressure,
                        location_id=region.id,
                        details={
                            'region_id': str(region.id),
                            'environmental_factors': environmental_factors,
                            'pressure_level': env_pressure
                        }
                    )
                    self.pressure_data.add_pressure_reading(reading)
        
        except Exception as e:
            pass
    
    # Helper methods for pressure calculations
    
    async def _calculate_faction_conflict_pressure(self, faction) -> float:
        """Calculate pressure from faction conflicts"""
        try:
            # Get faction's relationships if diplomacy service is available
            if self._system_connections.get('diplomacy'):
                relationships = self._system_connections['diplomacy'].get_faction_relationships(faction.id)
                
                total_tension = 0.0
                conflict_count = 0
                war_count = 0
                
                for relationship in relationships:
                    tension = relationship.get('tension', 0)
                    status = relationship.get('status', 'neutral')
                    
                    # Weight different relationship types
                    if status == 'war':
                        war_count += 1
                        total_tension += abs(tension) * 2.0  # Wars contribute double
                    elif status == 'hostile':
                        total_tension += abs(tension) * 1.5  # Hostile relations contribute more
                    elif tension > 50:  # High positive tension indicates conflict
                        conflict_count += 1
                        total_tension += tension
                    
                # Calculate normalized pressure (0.0 to 1.0)
                if relationships:
                    # Base pressure from average tension
                    avg_tension = total_tension / len(relationships) / 100.0  # Normalize to 0-1
                    
                    # Additional pressure from active wars
                    war_pressure = min(war_count * 0.3, 0.9)  # Each war adds 30%, max 90%
                    
                    # Additional pressure from number of conflicts
                    conflict_pressure = min(conflict_count * 0.1, 0.5)  # Each conflict adds 10%, max 50%
                    
                    # Combine pressures with diminishing returns
                    total_pressure = min(avg_tension + war_pressure + conflict_pressure, 1.0)
                    
                    return total_pressure
                else:
                    return 0.1  # Low baseline if no relationships
            else:
                # Fallback calculation based on faction metadata if available
                if hasattr(faction, 'metadata') and faction.metadata:
                    conflict_level = faction.metadata.get('conflict_level', 0.1)
                    return min(conflict_level, 1.0)
                
                return 0.1  # Low baseline conflict
                
        except Exception as e:
            return 0.1  # Fallback to low pressure

    async def _calculate_economic_instability(self, region) -> float:
        """Calculate economic instability pressure"""
        try:
            # Get economic data if economy service is available
            if self._system_connections.get('economy'):
                # Try to get economic indicators
                economic_data = await self._system_connections['economy'].get_region_economic_status(region.id)
                
                instability_factors = []
                
                # Market volatility
                market_volatility = economic_data.get('market_volatility', 0.0)
                instability_factors.append(market_volatility)
                
                # Trade disruption
                trade_disruption = economic_data.get('trade_disruption', 0.0)
                instability_factors.append(trade_disruption)
                
                # Resource scarcity
                resource_scarcity = economic_data.get('resource_scarcity', 0.0)
                instability_factors.append(resource_scarcity)
                
                # Inflation rate
                inflation_rate = economic_data.get('inflation_rate', 0.0)
                # Convert inflation to instability (high inflation = high instability)
                inflation_instability = min(abs(inflation_rate) / 10.0, 1.0)  # 10%+ inflation = max instability
                instability_factors.append(inflation_instability)
                
                # Unemployment rate
                unemployment_rate = economic_data.get('unemployment_rate', 0.0)
                unemployment_instability = min(unemployment_rate / 20.0, 1.0)  # 20%+ unemployment = max instability
                instability_factors.append(unemployment_instability)
                
                # Calculate weighted average of all factors
                if instability_factors:
                    return sum(instability_factors) / len(instability_factors)
                else:
                    return 0.05  # Low baseline
            else:
                # Fallback calculation based on region data
                if hasattr(region, 'economic_status'):
                    status = region.economic_status.lower()
                    if status in ['crisis', 'recession']:
                        return 0.8
                    elif status in ['unstable', 'volatile']:
                        return 0.6
                    elif status in ['declining', 'troubled']:
                        return 0.4
                    elif status in ['stable']:
                        return 0.1
                    elif status in ['growing', 'prosperous']:
                        return 0.05
                
                return 0.05  # Low baseline instability
                
        except Exception as e:
            return 0.05  # Fallback to low instability

    def _calculate_diplomatic_pressure(self, tension: Dict[str, Any]) -> float:
        """Calculate diplomatic tension pressure"""
        try:
            # Extract tension level and normalize
            tension_level = tension.get('tension', 0.0)
            
            # Normalize tension value (assuming range -100 to +100)
            normalized_tension = abs(tension_level) / 100.0
            
            # Get diplomatic status for additional weighting
            status = tension.get('status', 'neutral')
            status_multiplier = {
                'war': 2.0,
                'hostile': 1.5,
                'unfriendly': 1.2,
                'neutral': 1.0,
                'friendly': 0.8,
                'allied': 0.5
            }.get(status, 1.0)
            
            # Calculate final pressure
            diplomatic_pressure = min(normalized_tension * status_multiplier, 1.0)
            
            return diplomatic_pressure
            
        except Exception as e:
            return 0.0

    async def _calculate_population_pressure(self, region) -> float:
        """Calculate population stress pressure"""
        try:
            # Get population data if population service is available
            if self._system_connections.get('population'):
                population_data = await self._system_connections['population'].get_region_population_status(region.id)
                
                stress_factors = []
                
                # Population density stress
                density = population_data.get('density', 0.0)
                max_capacity = population_data.get('max_capacity', 1.0)
                if max_capacity > 0:
                    density_stress = min(density / max_capacity, 2.0) / 2.0  # Normalize to 0-1
                    stress_factors.append(density_stress)
                
                # Food security
                food_security = population_data.get('food_security', 1.0)  # 1.0 = secure, 0.0 = famine
                food_stress = 1.0 - food_security
                stress_factors.append(food_stress)
                
                # Employment rate
                employment_rate = population_data.get('employment_rate', 0.8)
                unemployment_stress = 1.0 - employment_rate
                stress_factors.append(unemployment_stress)
                
                # Health indicators
                health_index = population_data.get('health_index', 0.8)  # 0.0 = poor health, 1.0 = excellent
                health_stress = 1.0 - health_index
                stress_factors.append(health_stress)
                
                # Safety and crime rates
                crime_rate = population_data.get('crime_rate', 0.1)  # 0.0 = no crime, 1.0 = very high crime
                stress_factors.append(crime_rate)
                
                # Calculate weighted average
                if stress_factors:
                    return sum(stress_factors) / len(stress_factors)
                else:
                    return 0.02  # Low baseline
            else:
                # Fallback calculation based on region attributes
                population_stress = 0.02  # Low baseline
                
                if hasattr(region, 'population_density'):
                    # High density can cause stress
                    if region.population_density > 1000:  # Arbitrary threshold
                        population_stress += 0.3
                    elif region.population_density > 500:
                        population_stress += 0.15
                
                if hasattr(region, 'stability'):
                    # Lower stability = higher stress
                    stability = region.stability if region.stability else 0.5
                    population_stress += (1.0 - stability) * 0.4
                
                return min(population_stress, 1.0)
                
        except Exception as e:
            return 0.02  # Fallback to low stress

    def _calculate_military_pressure(self, activity: Dict[str, Any]) -> float:
        """Calculate military buildup pressure"""
        try:
            # Extract military activity data
            activity_type = activity.get('type', 'unknown')
            scale = activity.get('scale', 0.0)  # 0.0 to 1.0
            urgency = activity.get('urgency', 0.0)  # 0.0 to 1.0
            threat_level = activity.get('threat_level', 0.0)  # 0.0 to 1.0
            
            # Weight different activity types
            type_weights = {
                'troop_movement': 0.7,
                'weapons_buildup': 0.9,
                'fortification': 0.5,
                'military_exercise': 0.3,
                'mobilization': 1.0,
                'deployment': 0.8,
                'border_patrol': 0.4,
                'unknown': 0.5
            }
            
            base_pressure = type_weights.get(activity_type, 0.5)
            
            # Combine factors with base pressure
            military_pressure = base_pressure * (
                0.4 * scale +
                0.3 * urgency +
                0.3 * threat_level
            )
            
            return min(military_pressure, 1.0)
            
        except Exception as e:
            return 0.0

    async def _calculate_environmental_pressure(self, region) -> float:
        """Calculate environmental pressure"""
        try:
            # Initialize environmental factors
            environmental_factors = []
            
            # Check for environmental data sources
            if hasattr(region, 'environmental_status'):
                env_status = region.environmental_status
                
                # Weather-related stress
                weather_stress = env_status.get('weather_severity', 0.0)  # 0.0 = normal, 1.0 = extreme
                environmental_factors.append(weather_stress)
                
                # Natural disaster risk
                disaster_risk = env_status.get('disaster_risk', 0.0)  # 0.0 = low risk, 1.0 = high risk
                environmental_factors.append(disaster_risk)
                
                # Resource depletion
                resource_depletion = env_status.get('resource_depletion', 0.0)  # 0.0 = abundant, 1.0 = depleted
                environmental_factors.append(resource_depletion)
                
                # Pollution levels
                pollution_level = env_status.get('pollution_level', 0.0)  # 0.0 = clean, 1.0 = heavily polluted
                environmental_factors.append(pollution_level)
                
                # Climate change impact
                climate_impact = env_status.get('climate_impact', 0.0)  # 0.0 = no impact, 1.0 = severe impact
                environmental_factors.append(climate_impact)
            
            # Check for specific environmental threats
            if hasattr(region, 'natural_disasters'):
                active_disasters = region.natural_disasters.get('active', [])
                disaster_pressure = min(len(active_disasters) * 0.3, 1.0)
                environmental_factors.append(disaster_pressure)
            
            # Seasonal factors (if available)
            if hasattr(region, 'season'):
                season = region.season.lower()
                seasonal_stress = {
                    'winter': 0.2,  # Harsh winters can add stress
                    'summer': 0.1,  # Hot summers less stressful
                    'spring': 0.05, # Generally low stress
                    'autumn': 0.05  # Generally low stress
                }.get(season, 0.05)
                environmental_factors.append(seasonal_stress)
            
            # Calculate final environmental pressure
            if environmental_factors:
                return sum(environmental_factors) / len(environmental_factors)
            else:
                return 0.01  # Very low baseline environmental pressure
                
        except Exception as e:
            return 0.01  # Fallback to low environmental pressure
    
    # Helper methods for data retrieval
    
    async def _get_all_regions(self) -> List[Any]:
        """Get all regions from the region system"""
        if self._system_connections.get('region'):
            try:
                return await self._system_connections['region'].get_all_regions()
            except Exception as e:
                pass
        
        # Return empty list if region service unavailable
        return []
    
    async def _get_diplomatic_tensions(self) -> List[Dict[str, Any]]:
        """Get diplomatic tensions from diplomacy system"""
        if self._system_connections.get('diplomacy'):
            try:
                return await self._system_connections['diplomacy'].get_tensions()
            except Exception as e:
                pass
        
        return []
    
    async def _get_military_activities(self) -> List[Dict[str, Any]]:
        """Get military activities"""
        try:
            military_activities = []
            
            # Try to get from military/faction services
            if self._system_connections.get('faction'):
                # Get all factions and check for military activities
                factions = await self._system_connections['faction'].get_all_factions()
                
                for faction in factions:
                    # Check for military buildup indicators in faction data
                    if hasattr(faction, 'military_status'):
                        mil_status = faction.military_status
                        
                        activity = {
                            'type': mil_status.get('current_activity', 'unknown'),
                            'scale': mil_status.get('activity_scale', 0.0),
                            'urgency': mil_status.get('urgency', 0.0),
                            'threat_level': mil_status.get('threat_level', 0.0),
                            'region_id': faction.region_id if hasattr(faction, 'region_id') else None,
                            'faction_id': str(faction.id)
                        }
                        military_activities.append(activity)
                    
                    # Check for war status
                    if hasattr(faction, 'at_war') and faction.at_war:
                        war_activity = {
                            'type': 'mobilization',
                            'scale': 0.8,  # War mobilization is high scale
                            'urgency': 0.9,  # War is urgent
                            'threat_level': 0.9,  # War is high threat
                            'region_id': faction.region_id if hasattr(faction, 'region_id') else None,
                            'faction_id': str(faction.id)
                        }
                        military_activities.append(war_activity)
                    
                    # Check diplomacy service for wars
                    if self._system_connections.get('diplomacy'):
                        relationships = self._system_connections['diplomacy'].get_faction_relationships(faction.id)
                        
                        for relationship in relationships:
                            if relationship.get('status') == 'war':
                                war_activity = {
                                    'type': 'troop_movement',
                                    'scale': min(abs(relationship.get('tension', 0)) / 100.0, 1.0),
                                    'urgency': 0.8,
                                    'threat_level': 0.9,
                                    'region_id': faction.region_id if hasattr(faction, 'region_id') else None,
                                    'faction_id': str(faction.id)
                                }
                                military_activities.append(war_activity)
            
            # If no specific military service, generate activities based on diplomatic tensions
            if not military_activities and self._system_connections.get('diplomacy'):
                # Find high-tension relationships that might lead to military activity
                try:
                    # This might need adjustment based on actual diplomacy service API
                    all_relationships = []
                    if hasattr(self._system_connections['diplomacy'], 'get_all_relationships'):
                        all_relationships = self._system_connections['diplomacy'].get_all_relationships()
                    
                    for relationship in all_relationships:
                        tension = relationship.get('tension', 0)
                        if tension > 70:  # High tension threshold
                            activity = {
                                'type': 'military_exercise' if tension < 85 else 'troop_movement',
                                'scale': min(tension / 100.0, 1.0),
                                'urgency': min((tension - 50) / 50.0, 1.0),
                                'threat_level': min(tension / 100.0, 1.0),
                                'region_id': None,  # Would need faction location lookup
                                'faction_id': relationship.get('faction_a_id')
                            }
                            military_activities.append(activity)
                except Exception as e:
                    pass
            
            return military_activities
            
        except Exception as e:
            pass
            return []
    
    def _calculate_pressure_metrics(self) -> None:
        """Calculate aggregated pressure metrics for all regions"""
        # Get pressure source weights from config
        pressure_weights = self.config.get_pressure_weights()
        weights = {
            PressureSource.FACTION_CONFLICT: pressure_weights.get('faction_conflict', 0.25),
            PressureSource.ECONOMIC_INSTABILITY: pressure_weights.get('economic_instability', 0.20),
            PressureSource.POPULATION_STRESS: pressure_weights.get('population_stress', 0.15),
            PressureSource.DIPLOMATIC_TENSION: pressure_weights.get('diplomatic_tension', 0.15),
            PressureSource.MILITARY_BUILDUP: pressure_weights.get('military_buildup', 0.15),
            PressureSource.ENVIRONMENTAL_PRESSURE: pressure_weights.get('environmental_pressure', 0.10),
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
            pass
    
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
            "system_connections": self.get_connection_status(),
        }

# Global instance
pressure_monitor = PressureMonitor() 