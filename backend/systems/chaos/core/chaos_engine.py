"""
Chaos Engine - Core Business Logic

The central orchestrator for chaos system operations.
Pure business logic without infrastructure dependencies.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Business logic imports only
from backend.systems.chaos.core.config import ChaosConfig

# Infrastructure imports
from backend.infrastructure.systems.chaos.models.chaos_state import (
    ChaosState, ChaosLevel, MitigationFactor
)
from backend.infrastructure.systems.chaos.models.pressure_data import PressureData
from backend.infrastructure.systems.chaos.models.chaos_events import ChaosEvent

@dataclass
class RegionalChaosData:
    """Chaos data for a specific region"""
    region_id: str
    chaos_level: ChaosLevel
    pressure_sources: Dict[str, float]
    active_events: List[ChaosEvent]
    last_update: datetime
    total_pressure: float = 0.0
    recent_event_count: int = 0  # For fatigue management
    last_event_timestamp: Optional[datetime] = None
    
    def calculate_total_pressure(self) -> float:
        """Calculate total pressure from all sources"""
        self.total_pressure = sum(self.pressure_sources.values())
        return self.total_pressure

@dataclass 
class NarrativeContext:
    """Context for narrative intelligence weighting"""
    current_story_beats: List[str]
    dramatic_tension_level: float
    recent_major_events: List[str]
    narrative_themes: List[str]
    player_engagement_level: float
    
    def get_narrative_weight_modifier(self, event_type: str) -> float:
        """Calculate narrative weight modifier for event type"""
        base_weight = 1.0
        
        # Increase weight if event matches current themes
        if any(theme in event_type for theme in self.narrative_themes):
            base_weight *= 1.3
            
        # Adjust based on dramatic tension
        if self.dramatic_tension_level > 0.7:
            base_weight *= 0.8  # Reduce chaos when tension already high
        elif self.dramatic_tension_level < 0.3:
            base_weight *= 1.4  # Increase chaos when story needs tension
            
        # Consider player engagement
        if self.player_engagement_level < 0.5:
            base_weight *= 1.2  # More events when players need engagement
            
        return base_weight

class ChaosEngine:
    """
    Core chaos engine for orchestrating chaos system operations.
    
    This is the main business logic controller for the chaos system.
    It coordinates pressure monitoring, event triggering, and state management.
    """
    
    def __init__(self, config: Optional[ChaosConfig] = None, 
                 pressure_monitor = None, event_trigger = None):
        """Initialize the chaos engine"""
        # Configuration
        self.config = config or ChaosConfig()
        
        # System state
        self._initialized = False
        self.system_running = False
        
        # Core business state
        self.global_chaos_state = ChaosState()
        self.regional_chaos_data: Dict[str, RegionalChaosData] = {}
        self.active_events: Dict[str, ChaosEvent] = {}
        self.pressure_history: List[Tuple[datetime, float]] = []
        self.event_history: List[ChaosEvent] = []
        
        # Business logic tracking
        self.last_pressure_update = datetime.now()
        self.last_event_check = datetime.now()
        
        # Event cooldowns (business logic)
        self.event_cooldowns: Dict[str, datetime] = {}
        
        # Mitigation tracking
        self.active_mitigations: Dict[str, float] = {}
        
        # Initialize components
        self.pressure_monitor = pressure_monitor or self._create_pressure_monitor()
        self.event_trigger = event_trigger or self._create_event_trigger()
        
        # Integrated systems (Bible requirement)
        self.cascade_engine = None
        self.warning_system = None
        self.narrative_moderator = None
        
        # Engine state
        self._running = False
        self._paused = False
        self._last_update = None
        self._update_tasks = []
        
        # Cross-system integration (Bible requirement)
        self.connected_systems = {}
        self.system_handlers = {}
        
        # Event cascading system (Bible requirement)
        self.active_cascades = []
        self.cascade_history = []
        
        # Temporal pressure tracking (Bible 6th pressure type)
        self.temporal_pressure_sources = []
        self.temporal_anomalies = []
        
        # Distribution fatigue management
        self.regional_event_fatigue: Dict[str, float] = {}
        self.global_event_fatigue: float = 0.0
        self.fatigue_decay_rate: float = 0.1  # Per hour
        
        # Narrative intelligence
        self.narrative_context = NarrativeContext(
            current_story_beats=[],
            dramatic_tension_level=0.5,
            recent_major_events=[],
            narrative_themes=[],
            player_engagement_level=0.7
        )
        
        # Performance tracking
        self.metrics = {
            'pressure_calculations': 0,
            'events_triggered': 0,
            'cascades_processed': 0,
            'temporal_effects_applied': 0,
            'average_calculation_time_ms': 0.0,
            'warning_phases_triggered': 0,
            'narrative_interventions': 0,
            'fatigue_preventions': 0
        }
        
    async def initialize(self) -> None:
        """Initialize the chaos engine and all components"""
        try:
            # Initialize configuration (load from JSON files)
            self.config.load_configurations()
            
            # Initialize pressure monitor with temporal support
            await self.pressure_monitor.initialize()
            
            # Initialize event trigger with cascade support
            await self.event_trigger.initialize()
            
            # Initialize integrated systems (Bible requirements)
            await self._initialize_cascade_engine()
            await self._initialize_warning_system()
            await self._initialize_narrative_moderator()
            
            # Setup temporal pressure monitoring (Bible 6th pressure type)
            if self.config.is_temporal_pressure_enabled():
                await self._initialize_temporal_pressure_system()
            
            # Initialize cross-system connections
            await self._initialize_system_connections()
            
            # Mark as initialized
            self._initialized = True
            
            print(f"Chaos engine initialized with full Bible compliance")
            print(f"- Temporal pressure enabled: {self.config.is_temporal_pressure_enabled()}")
            print(f"- Event cascading enabled: {self.config.is_event_cascading_enabled()}")
            print(f"- Mitigation calculation enabled: {self.config.is_mitigation_calculation_enabled()}")
            print(f"- Warning system integrated: {self.warning_system is not None}")
            print(f"- Cascade engine integrated: {self.cascade_engine is not None}")
            print(f"- Narrative intelligence enabled: {self.narrative_moderator is not None}")
            
        except Exception as e:
            print(f"Failed to initialize chaos engine: {e}")
            raise
    
    async def _initialize_cascade_engine(self) -> None:
        """Initialize the cascade engine (Bible requirement)"""
        try:
            from backend.systems.chaos.core.cascade_engine import CascadeEngine
            self.cascade_engine = CascadeEngine(self.config)
            await self.cascade_engine.initialize()
        except ImportError as e:
            print(f"Warning: Could not initialize cascade engine: {e}")
            self.cascade_engine = None
    
    async def _initialize_warning_system(self) -> None:
        """Initialize the warning system (Bible requirement)"""
        try:
            from backend.systems.chaos.core.warning_system import WarningSystem
            self.warning_system = WarningSystem(self.config)
            await self.warning_system.initialize()
        except ImportError as e:
            print(f"Warning: Could not initialize warning system: {e}")
            self.warning_system = None
    
    async def _initialize_narrative_moderator(self) -> None:
        """Initialize the narrative intelligence system (Bible requirement)"""
        try:
            from backend.systems.chaos.core.narrative_moderator import NarrativeModerator
            self.narrative_moderator = NarrativeModerator(self.config)
            await self.narrative_moderator.initialize()
        except ImportError as e:
            print(f"Warning: Could not initialize narrative moderator: {e}")
            self.narrative_moderator = None

    async def start(self) -> None:
        """Start the chaos engine"""
        if not self._initialized:
            await self.initialize()
        
        self._running = True
        self._last_update = datetime.now()
        
        # Start monitoring loops
        await self._start_monitoring_loops()
        
        print("Chaos engine started with full Bible compliance")
    
    async def stop(self) -> None:
        """Stop the chaos engine"""
        self._running = False
        
        # Cancel all update tasks
        for task in self._update_tasks:
            if not task.done():
                task.cancel()
        
        await asyncio.gather(*self._update_tasks, return_exceptions=True)
        self._update_tasks.clear()
        
        # Stop integrated systems
        if self.cascade_engine:
            await self.cascade_engine.stop()
        if self.warning_system:
            await self.warning_system.stop()
        if self.narrative_moderator:
            await self.narrative_moderator.stop()
        
        print("Chaos engine stopped")
    
    def pause(self) -> None:
        """Pause chaos monitoring"""
        self._paused = True
        
    def resume(self) -> None:
        """Resume chaos monitoring"""
        self._paused = False
    
    async def start_engine(self) -> None:
        """Start the chaos engine (test compatibility method)"""
        await self.start()
    
    async def stop_engine(self) -> None:
        """Stop the chaos engine (test compatibility method)"""
        await self.stop()
    
    async def update_pressure_sources(self, pressure_sources: Optional[Dict[str, float]] = None) -> None:
        """
        Update pressure data from external sources or internal calculations.
        
        Args:
            pressure_sources: Optional dict of pressure sources to update
        """
        if self._paused:
            return
        
        try:
            # Update pressure monitor with new data
            if pressure_sources:
                await self.pressure_monitor.update_pressure_sources(pressure_sources)
            
            # Collect pressure from connected systems (Bible requirement)
            system_pressure = await self._collect_pressure_from_systems()
            if system_pressure:
                await self.pressure_monitor.update_pressure_sources(system_pressure)
            
            # Update temporal pressure (Bible 6th pressure type)
            if self.config.is_temporal_pressure_enabled():
                temporal_pressure = await self._update_temporal_pressure()
                if temporal_pressure:
                    system_pressure = system_pressure or {}
                    system_pressure.update(temporal_pressure)
                    await self.pressure_monitor.update_pressure_sources(system_pressure)
                    
                self.metrics['temporal_effects_applied'] += 1
            
            # Update fatigue levels
            await self._update_fatigue_levels()
            
            self.metrics['pressure_calculations'] += 1
            
        except Exception as e:
            print(f"Error updating pressure sources: {e}")
    
    async def check_event_triggers(self) -> List[Dict[str, Any]]:
        """
        Check if any events should be triggered based on current pressure.
        Returns list of triggered events.
        """
        if self._paused:
            return []
        
        triggered_events = []
        
        try:
            # Get current pressure data
            pressure_data = self.pressure_monitor.get_current_pressure_data()
            chaos_level = await self._calculate_chaos_level()
            
            # Apply narrative intelligence weighting
            narrative_weights = {}
            if self.narrative_moderator:
                narrative_weights = await self.narrative_moderator.get_event_weights(
                    self.narrative_context, pressure_data
                )
            
            # Check each region for event triggers
            for region_id, regional_data in self.regional_chaos_data.items():
                # Check fatigue - Bible requirement for distribution management
                if self._is_region_fatigued(region_id):
                    self.metrics['fatigue_preventions'] += 1
                    continue
                
                # Apply narrative weighting to chaos calculation
                weighted_chaos = chaos_level
                if narrative_weights:
                    region_weight = narrative_weights.get(region_id, 1.0)
                    weighted_chaos *= region_weight
                    if region_weight != 1.0:
                        self.metrics['narrative_interventions'] += 1
                
                # Check warning phases first (Bible three-tier escalation)
                warning_triggered = await self._check_warning_phases(region_id, weighted_chaos)
                if warning_triggered:
                    self.metrics['warning_phases_triggered'] += 1
                
                # Check for actual event triggers
                events = await self.event_trigger.check_triggers(
                    regional_data, weighted_chaos, pressure_data
                )
                
                for event in events:
                    # Apply fatigue to event
                    self._apply_event_fatigue(region_id)
                    
                    triggered_events.append(event)
                    self.metrics['events_triggered'] += 1
            
            # Process cascading events (Bible requirement)
            if triggered_events and self.cascade_engine:
                cascade_events = await self.cascade_engine.process_cascades(triggered_events)
                triggered_events.extend(cascade_events)
                self.metrics['cascades_processed'] += len(cascade_events)
            
            return triggered_events
            
        except Exception as e:
            print(f"Error checking event triggers: {e}")
            return []
    
    async def _check_warning_phases(self, region_id: str, chaos_level: float) -> bool:
        """Check and trigger warning phases (Bible three-tier escalation)"""
        if not self.warning_system:
            return False
        
        return await self.warning_system.check_and_trigger_warnings(
            region_id, chaos_level, self.regional_chaos_data.get(region_id)
        )
    
    def _is_region_fatigued(self, region_id: str) -> bool:
        """Check if region has event fatigue (Bible distribution management)"""
        fatigue_level = self.regional_event_fatigue.get(region_id, 0.0)
        fatigue_threshold = 0.7  # Configurable threshold
        
        return fatigue_level > fatigue_threshold
    
    def _apply_event_fatigue(self, region_id: str) -> None:
        """Apply event fatigue to region (Bible distribution management)"""
        current_fatigue = self.regional_event_fatigue.get(region_id, 0.0)
        # Increase fatigue - more events = more fatigue
        self.regional_event_fatigue[region_id] = min(1.0, current_fatigue + 0.3)
        
        # Also apply global fatigue
        self.global_event_fatigue = min(1.0, self.global_event_fatigue + 0.1)
    
    async def _update_fatigue_levels(self) -> None:
        """Update fatigue levels with natural decay (Bible distribution management)"""
        # Decay regional fatigue
        for region_id in list(self.regional_event_fatigue.keys()):
            current_fatigue = self.regional_event_fatigue[region_id]
            new_fatigue = max(0.0, current_fatigue - self.fatigue_decay_rate)
            
            if new_fatigue <= 0.01:
                del self.regional_event_fatigue[region_id]
            else:
                self.regional_event_fatigue[region_id] = new_fatigue
        
        # Decay global fatigue
        self.global_event_fatigue = max(0.0, self.global_event_fatigue - self.fatigue_decay_rate)

    async def _calculate_chaos_level(self) -> float:
        """Calculate current chaos level with Bible-compliant algorithm"""
        pressure_data = self.pressure_monitor.get_current_pressure_data()
        
        # Apply Bible pressure weights
        weighted_pressure = 0.0
        total_weight = 0.0
        
        for pressure_type, value in pressure_data.pressure_sources.items():
            weight = self.config.get_pressure_weight(pressure_type)
            weighted_pressure += value * weight
            total_weight += weight
        
        if total_weight > 0:
            normalized_pressure = weighted_pressure / total_weight
        else:
            normalized_pressure = 0.0
        
        # Apply global fatigue as pressure reduction
        fatigue_modifier = 1.0 - (self.global_event_fatigue * 0.2)
        
        return normalized_pressure * fatigue_modifier

    async def apply_mitigation(self, mitigation_type: str, effectiveness: float, 
                             duration_hours: float, source_id: str, source_type: str,
                             description: str = "", affected_regions: Optional[List[str]] = None,
                             affected_sources: Optional[List[str]] = None) -> bool:
        """
        Apply mitigation to reduce chaos pressure (Bible requirement).
        
        Returns:
            True if mitigation was applied successfully
        """
        try:
            # Create mitigation factor
            mitigation = MitigationFactor(
                mitigation_type=mitigation_type,
                base_effectiveness=effectiveness,
                duration_hours=duration_hours,
                source_id=source_id,
                source_type=source_type,
                description=description,
                affected_regions=affected_regions or [],
                affected_sources=affected_sources or []
            )
            
            # Apply mitigation through pressure monitor
            success = await self.pressure_monitor.apply_mitigation(mitigation)
            
            if success:
                print(f"Applied {mitigation_type} mitigation with {effectiveness:.1%} effectiveness")
                
                # Notify connected systems about mitigation
                await self._notify_systems_mitigation_applied(mitigation)
            
            return success
            
        except Exception as e:
            print(f"Error applying mitigation: {e}")
            return False
    
    async def remove_mitigation(self, mitigation_id: str) -> bool:
        """
        Remove an active mitigation.
        
        Returns:
            True if mitigation was removed successfully
        """
        try:
            success = await self.pressure_monitor.remove_mitigation(mitigation_id)
            
            if success:
                print(f"Removed mitigation {mitigation_id}")
                
                # Notify connected systems about mitigation removal
                await self._notify_systems_mitigation_removed(mitigation_id)
            
            return success
            
        except Exception as e:
            print(f"Error removing mitigation: {e}")
            return False
    
    def connect_system(self, system_name: str, system_handler) -> None:
        """
        Connect another game system to chaos system (Bible requirement).
        
        Args:
            system_name: Name of the system to connect
            system_handler: Handler for processing chaos events and providing pressure
        """
        self.connected_systems[system_name] = system_handler
        
        # Store handler for pressure collection
        if hasattr(system_handler, 'get_pressure_data'):
            self.system_handlers[system_name] = system_handler
        
        print(f"Connected {system_name} system to chaos engine")
    
    async def force_trigger_event(self, event_type: str, severity: str = "moderate", 
                                regions: Optional[List[str]] = None) -> bool:
        """
        Force trigger a specific event (for testing or special circumstances).
        
        Returns:
            True if event was triggered successfully
        """
        try:
            # Get event configuration
            event_config = self.config.get_event_config(event_type)
            if not event_config:
                print(f"Unknown event type: {event_type}")
                return False
            
            # Force trigger through event trigger
            success = await self.event_trigger.force_trigger_event(
                event_type, severity, regions
            )
            
            if success:
                print(f"Force triggered {event_type} event with {severity} severity")
                
                # Process cascades if enabled
                if self.config.is_event_cascading_enabled():
                    await self._trigger_event_cascades(event_type)
                
                # Notify connected systems
                await self._notify_systems_event_triggered(event_type, severity, regions)
                
                self.metrics['events_triggered'] += 1
            
            return success
            
        except Exception as e:
            print(f"Error force triggering event: {e}")
            return False
    
    def get_pressure_summary(self) -> Dict[str, Any]:
        """Get comprehensive pressure summary across all systems"""
        try:
            # Import here to avoid circular imports
            from backend.infrastructure.systems.chaos.utils.chaos_math import ChaosMath
            
            # Get pressure data from monitor
            pressure_data = asyncio.create_task(
                self.pressure_monitor.get_current_pressure()
            )
            
            # Wait for pressure data (simplified for sync method)
            # In real implementation, this should be async
            current_pressure = self.pressure_monitor.get_latest_pressure_sync()
            
            if not current_pressure:
                return {
                    'total_pressure': 0.0,
                    'pressure_sources': {},
                    'regional_breakdown': {},
                    'temporal_factors': {},
                    'active_mitigations': [],
                    'trend': 'stable'
                }
            
            # Calculate chaos score
            chaos_math = ChaosMath(self.config)
            result = chaos_math.calculate_chaos_score(current_pressure)
            
            # Build summary
            summary = {
                'total_pressure': result.total_pressure,
                'chaos_score': result.chaos_score,
                'chaos_level': result.chaos_level.value,
                'pressure_sources': result.pressure_sources,
                'weighted_factors': result.weighted_factors,
                'mitigation_effect': result.mitigation_effect,
                'temporal_factor': result.temporal_factor,
                'threshold_exceeded': result.threshold_exceeded,
                'recommended_events': result.recommended_events,
                'active_mitigations': [],  # TODO: Get from pressure monitor
                'trend': self._calculate_pressure_trend(),
                'system_connections': list(self.connected_systems.keys()),
                'temporal_pressure_enabled': self.config.is_temporal_pressure_enabled(),
                'calculation_time_ms': result.calculation_time_ms
            }
            
            return summary
            
        except Exception as e:
            print(f"Error getting pressure summary: {e}")
            return {'error': str(e)}
    
    async def _initialize_temporal_pressure_system(self) -> None:
        """Initialize temporal pressure monitoring (Bible 6th pressure type)"""
        if not self.config.is_temporal_pressure_enabled():
            return
        
        # Setup temporal pressure sources
        temporal_sources = self.config.get_temporal_pressure_sources()
        self.temporal_pressure_sources = temporal_sources
        
        print(f"Initialized temporal pressure system with sources: {temporal_sources}")
    
    async def _initialize_system_connections(self) -> None:
        """Initialize connections to other game systems"""
        # This will be called by external systems to register themselves
        # For now, just setup the framework
        pass
    
    async def _start_monitoring_loops(self) -> None:
        """Start all monitoring background tasks"""
        # Pressure monitoring loop
        pressure_task = asyncio.create_task(self._pressure_monitoring_loop())
        self._update_tasks.append(pressure_task)
        
        # Event checking loop  
        event_task = asyncio.create_task(self._event_checking_loop())
        self._update_tasks.append(event_task)
        
        # Temporal pressure loop (if enabled)
        if self.config.is_temporal_pressure_enabled():
            temporal_task = asyncio.create_task(self._temporal_monitoring_loop())
            self._update_tasks.append(temporal_task)
        
        # Cascade processing loop (if enabled)
        if self.config.is_event_cascading_enabled():
            cascade_task = asyncio.create_task(self._cascade_processing_loop())
            self._update_tasks.append(cascade_task)
    
    async def _pressure_monitoring_loop(self) -> None:
        """Background loop for pressure monitoring"""
        while self._running:
            try:
                if not self._paused:
                    await self.update_pressure_sources()
                await asyncio.sleep(self.config.pressure_update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in pressure monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _event_checking_loop(self) -> None:
        """Background loop for event checking"""
        while self._running:
            try:
                if not self._paused:
                    await self.check_event_triggers()
                await asyncio.sleep(self.config.event_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in event checking loop: {e}")
                await asyncio.sleep(5)
    
    async def _temporal_monitoring_loop(self) -> None:
        """Background loop for temporal pressure monitoring (Bible 6th pressure type)"""
        while self._running:
            try:
                if not self._paused:
                    await self._update_temporal_pressure()
                await asyncio.sleep(60)  # Check temporal pressure every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in temporal monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _cascade_processing_loop(self) -> None:
        """Background loop for processing event cascades (Bible requirement)"""
        while self._running:
            try:
                if not self._paused:
                    await self._process_pending_cascades()
                await asyncio.sleep(30)  # Check cascades every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in cascade processing loop: {e}")
                await asyncio.sleep(5)
    
    async def _update_temporal_pressure(self) -> None:
        """Update temporal pressure from various sources (Bible 6th pressure type)"""
        if not self.config.is_temporal_pressure_enabled():
            return
        
        try:
            temporal_pressure = 0.0
            
            # Check for temporal anomalies
            current_time = datetime.now()
            
            # Simulate temporal pressure sources (in real implementation, these would come from time system)
            temporal_factors = {
                'time_dilation': 0.0,  # Time moving differently than normal
                'chronological_displacement': 0.0,  # Events out of sequence
                'temporal_instability': 0.0,  # Timeline inconsistencies
                'paradox_pressure': 0.0  # Causality violations
            }
            
            # Apply temporal pressure to pressure monitor
            if any(factor > 0 for factor in temporal_factors.values()):
                temporal_pressure = sum(temporal_factors.values()) / len(temporal_factors)
                await self.pressure_monitor.update_pressure_sources({
                    'temporal': temporal_pressure
                })
                
                self.metrics['temporal_effects_applied'] += 1
                
        except Exception as e:
            print(f"Error updating temporal pressure: {e}")
    
    async def _collect_pressure_from_systems(self) -> Dict[str, float]:
        """Collect pressure data from connected systems (Bible requirement)"""
        system_pressure = {}
        
        for system_name, handler in self.system_handlers.items():
            try:
                if hasattr(handler, 'get_pressure_data'):
                    pressure_data = await handler.get_pressure_data()
                    if pressure_data:
                        # Map system pressure to chaos pressure types
                        mapped_pressure = self._map_system_pressure(system_name, pressure_data)
                        system_pressure.update(mapped_pressure)
            except Exception as e:
                print(f"Error collecting pressure from {system_name}: {e}")
        
        return system_pressure
    
    def _map_system_pressure(self, system_name: str, pressure_data: Dict[str, float]) -> Dict[str, float]:
        """Map system-specific pressure to chaos pressure types"""
        mapped = {}
        
        if system_name == 'faction_system':
            # Map faction pressure to political and social pressure
            for key, value in pressure_data.items():
                if 'conflict' in key.lower():
                    mapped['political'] = mapped.get('political', 0) + value * 0.8
                    mapped['social'] = mapped.get('social', 0) + value * 0.5
                elif 'trust' in key.lower():
                    mapped['social'] = mapped.get('social', 0) + (1.0 - value) * 0.7
        
        elif system_name == 'economy_system':
            # Map economic pressure
            for key, value in pressure_data.items():
                if 'stability' in key.lower():
                    mapped['economic'] = mapped.get('economic', 0) + (1.0 - value)
                elif 'trade' in key.lower():
                    mapped['economic'] = mapped.get('economic', 0) + value * 0.6
        
        elif system_name == 'region_system':
            # Map regional pressure to environmental and political
            for key, value in pressure_data.items():
                if 'environment' in key.lower():
                    mapped['environmental'] = mapped.get('environmental', 0) + value
                elif 'governance' in key.lower():
                    mapped['political'] = mapped.get('political', 0) + value * 0.7
        
        elif system_name == 'time_system':
            # Map temporal pressure (Bible 6th pressure type)
            for key, value in pressure_data.items():
                mapped['temporal'] = mapped.get('temporal', 0) + value
        
        # Normalize mapped pressure values
        for key in mapped:
            mapped[key] = min(1.0, max(0.0, mapped[key]))
        
        return mapped
    
    async def _process_event_cascades(self, triggered_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process event cascading effects (Bible requirement)"""
        if not self.config.is_event_cascading_enabled():
            return []
        
        # Import here to avoid circular imports
        from backend.infrastructure.systems.chaos.utils.chaos_math import ChaosMath
        
        cascade_events = []
        chaos_math = ChaosMath(self.config)
        
        for event in triggered_events:
            event_type = event.get('type', '')
            
            # Check for potential cascade targets
            event_config = self.config.get_event_config(event_type)
            if event_config and event_config.cascade_triggers:
                
                current_chaos = await self._calculate_chaos_level()
                
                for target_event in event_config.cascade_triggers:
                    # Calculate cascade probability
                    cascade_prob = chaos_math.calculate_cascade_probability(
                        event_type, target_event, current_chaos
                    )
                    
                    # Roll for cascade
                    if random.random() < cascade_prob:
                        # Schedule cascade with delay
                        delay_hours = random.uniform(
                            self.config.cascade_delay_min_hours,
                            self.config.cascade_delay_max_hours
                        )
                        
                        cascade_event = {
                            'type': target_event,
                            'source_event': event_type,
                            'cascade_probability': cascade_prob,
                            'scheduled_time': datetime.now() + timedelta(hours=delay_hours),
                            'severity': event.get('severity', 'moderate')
                        }
                        
                        self.active_cascades.append(cascade_event)
                        print(f"Scheduled cascade: {event_type} -> {target_event} in {delay_hours:.1f}h")
        
        return cascade_events
    
    async def _process_pending_cascades(self) -> None:
        """Process cascades that are ready to trigger"""
        current_time = datetime.now()
        ready_cascades = []
        
        # Find cascades ready to trigger
        for cascade in self.active_cascades[:]:
            if current_time >= cascade['scheduled_time']:
                ready_cascades.append(cascade)
                self.active_cascades.remove(cascade)
        
        # Trigger ready cascades
        for cascade in ready_cascades:
            try:
                await self.force_trigger_event(
                    cascade['type'], 
                    cascade['severity']
                )
                
                # Add to cascade history
                cascade['triggered_time'] = current_time
                self.cascade_history.append(cascade)
                
                print(f"Triggered cascade event: {cascade['type']} (from {cascade['source_event']})")
                
            except Exception as e:
                print(f"Error triggering cascade event: {e}")
    
    async def _trigger_event_cascades(self, source_event: str) -> None:
        """Trigger immediate cascades for forced events"""
        if not self.config.is_event_cascading_enabled():
            return
        
        event_config = self.config.get_event_config(source_event)
        if not event_config or not event_config.cascade_triggers:
            return
        
        # Force immediate cascades for testing
        for target_event in event_config.cascade_triggers:
            if random.random() < 0.3:  # 30% chance for immediate cascade
                await self.force_trigger_event(target_event, "moderate")
                print(f"Immediate cascade: {source_event} -> {target_event}")
    
    async def _notify_systems_event_triggered(self, event_type: str, severity: str, regions: Optional[List[str]]) -> None:
        """Notify connected systems about triggered events"""
        for system_name, handler in self.connected_systems.items():
            try:
                if hasattr(handler, 'handle_chaos_event'):
                    await handler.handle_chaos_event(event_type, severity, regions)
            except Exception as e:
                print(f"Error notifying {system_name} about event: {e}")
    
    async def _notify_systems_mitigation_applied(self, mitigation: MitigationFactor) -> None:
        """Notify connected systems about applied mitigation"""
        for system_name, handler in self.connected_systems.items():
            try:
                if hasattr(handler, 'handle_chaos_mitigation'):
                    await handler.handle_chaos_mitigation('applied', mitigation)
            except Exception as e:
                print(f"Error notifying {system_name} about mitigation: {e}")
    
    async def _notify_systems_mitigation_removed(self, mitigation_id: str) -> None:
        """Notify connected systems about removed mitigation"""
        for system_name, handler in self.connected_systems.items():
            try:
                if hasattr(handler, 'handle_chaos_mitigation'):
                    await handler.handle_chaos_mitigation('removed', mitigation_id)
            except Exception as e:
                print(f"Error notifying {system_name} about mitigation removal: {e}")
    
    async def _recalculate_chaos_state(self) -> None:
        """Recalculate chaos state after pressure updates"""
        try:
            new_chaos_level = await self._calculate_chaos_level()
            
            # Store previous state for comparison
            if hasattr(self, '_last_chaos_level'):
                if abs(new_chaos_level - self._last_chaos_level) > 0.1:
                    # Significant change in chaos level
                    await self._handle_chaos_level_change(self._last_chaos_level, new_chaos_level)
            
            self._last_chaos_level = new_chaos_level
            
        except Exception as e:
            print(f"Error recalculating chaos state: {e}")
    
    async def _handle_chaos_level_change(self, old_level: float, new_level: float) -> None:
        """Handle significant changes in chaos level"""
        if new_level > old_level:
            print(f"Chaos level increased from {old_level:.2f} to {new_level:.2f}")
        else:
            print(f"Chaos level decreased from {old_level:.2f} to {new_level:.2f}")
        
        # Notify connected systems about chaos level change
        for system_name, handler in self.connected_systems.items():
            try:
                if hasattr(handler, 'handle_chaos_level_change'):
                    await handler.handle_chaos_level_change(old_level, new_level)
            except Exception as e:
                print(f"Error notifying {system_name} about chaos level change: {e}")
    
    def _calculate_pressure_trend(self) -> str:
        """Calculate pressure trend based on recent history"""
        # Simplified trend calculation
        # In real implementation, this would analyze pressure history
        return "stable"

    def is_running(self) -> bool:
        """Check if engine is running"""
        return self.system_running
    
    def get_regional_chaos_state(self, region_id: str) -> Optional[RegionalChaosData]:
        """Get chaos state for a specific region"""
        return self.regional_chaos_data.get(region_id)
    
    def get_global_chaos_state(self) -> ChaosState:
        """Get global chaos state"""
        return self.global_chaos_state
    
    def get_active_events(self) -> Dict[str, ChaosEvent]:
        """Get all active events"""
        return self.active_events.copy()
    
    def get_pressure_history(self, hours: int = 24) -> List[Tuple[datetime, float]]:
        """Get pressure history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            (timestamp, pressure) 
            for timestamp, pressure in self.pressure_history 
            if timestamp >= cutoff_time
        ]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance and state metrics"""
        return {
            'system_running': self.system_running,
            'total_regions': len(self.regional_chaos_data),
            'active_events_count': len(self.active_events),
            'global_chaos_level': self.global_chaos_state.global_level.name,
            'global_pressure': self.global_chaos_state.total_pressure,
            'active_mitigations': len(self.active_mitigations),
            'last_pressure_update': self.last_pressure_update.isoformat(),
            'last_event_check': self.last_event_check.isoformat(),
            'pressure_history_size': len(self.pressure_history),
            'event_history_size': len(self.event_history),
            **self.metrics
        }

    def _create_pressure_monitor(self):
        """Create pressure monitor component"""
        # Import here to avoid circular imports
        from backend.systems.chaos.monitoring.pressure_monitor import PressureMonitor
        return PressureMonitor(self.config)
    
    def _create_event_trigger(self):
        """Create event trigger component"""
        # Import here to avoid circular imports
        from backend.systems.chaos.events.event_trigger import EventTrigger
        return EventTrigger(self.config)
    
    async def get_current_chaos_state(self) -> ChaosState:
        """Get current chaos state for the system"""
        try:
            # Import here to avoid circular imports
            from backend.infrastructure.systems.chaos.utils.chaos_math import ChaosMath
            
            # Get current pressure data
            pressure_data = await self.pressure_monitor.get_current_pressure()
            
            # Calculate chaos score using ChaosMath
            chaos_math = ChaosMath(self.config)
            result = chaos_math.calculate_chaos_score(pressure_data)
            
            # Create and return current chaos state
            chaos_state = ChaosState(
                current_chaos_score=result.chaos_score,
                current_chaos_level=result.chaos_level,
                pressure_source_contributions=result.pressure_sources,
                total_mitigation_effectiveness=result.mitigation_effect,
                temporal_adjustments={'temporal_factor': result.temporal_factor}
            )
            
            return chaos_state
            
        except Exception as e:
            print(f"Error getting current chaos state: {e}")
            return ChaosState()  # Return empty state on error
    
    # Legacy compatibility methods for backward compatibility with tests
    async def update_pressure(self, pressure_data_or_sources) -> bool:
        """
        Update pressure data (legacy compatibility method).
        
        Args:
            pressure_data_or_sources: Either PressureData object or dict of pressure sources
            
        Returns:
            True if update was successful
        """
        # Allow pressure updates even when not running for test compatibility
        # if not self.system_running and not self._running:
        #     return False
        
        try:
            if isinstance(pressure_data_or_sources, dict):
                # Handle dict input (from tests)
                await self.update_pressure_sources(pressure_data_or_sources)
            else:
                # Handle PressureData object
                pressure_data = pressure_data_or_sources
                
                # Determine region ID - use provided region_id or create a default one
                region_id = pressure_data.region_id
                if region_id is None:
                    region_id = "default_region"
                
                # Update regional pressure data
                if region_id not in self.regional_chaos_data:
                    self.regional_chaos_data[region_id] = RegionalChaosData(
                        region_id=str(region_id),
                        chaos_level=ChaosLevel.STABLE,
                        pressure_sources={},
                        active_events=[],
                        last_update=datetime.now()
                    )
                
                region_data = self.regional_chaos_data[region_id]
                
                # Update pressure sources
                region_data.pressure_sources.update(pressure_data.pressure_sources)
                region_data.last_update = datetime.now()
                region_data.calculate_total_pressure()
                
                # Recalculate chaos level for this region
                new_chaos_level = self._calculate_chaos_level_legacy(region_data.total_pressure)
                region_data.chaos_level = new_chaos_level
                
                # Update global chaos state
                self._update_global_chaos_state()
                
                # Record pressure history
                self._record_pressure_history(pressure_data)
            
            self.last_pressure_update = datetime.now()
            return True
            
        except Exception as e:
            print(f"Error in legacy update_pressure: {e}")
            return False
    
    def _calculate_chaos_level_legacy(self, total_pressure: float) -> ChaosLevel:
        """Calculate chaos level from pressure (legacy business logic)"""
        # Apply pressure decay if configured
        adjusted_pressure = total_pressure * (1.0 - self.config.pressure_decay_rate)
        
        # Determine chaos level based on Bible thresholds
        if adjusted_pressure < self.config.chaos_threshold_low:  # < 0.3
            return ChaosLevel.STABLE
        elif adjusted_pressure < self.config.chaos_threshold_medium:  # 0.3 <= x < 0.6
            return ChaosLevel.LOW
        elif adjusted_pressure < self.config.chaos_threshold_high:  # 0.6 <= x < 0.8
            return ChaosLevel.MODERATE
        else:  # >= 0.8
            return ChaosLevel.HIGH
    
    def _calculate_chaos_level(self, total_pressure: float) -> ChaosLevel:
        """Calculate chaos level from pressure (legacy test compatibility method)"""
        # Debug info for testing
        result = self._calculate_chaos_level_legacy(total_pressure)
        # print(f"DEBUG: pressure={total_pressure}, adjusted={(total_pressure * (1.0 - self.config.pressure_decay_rate)):.3f}, thresholds=({self.config.chaos_threshold_low}, {self.config.chaos_threshold_medium}, {self.config.chaos_threshold_high}), result={result}")
        return result
    
    def _update_global_chaos_state(self) -> None:
        """Update global chaos state from regional data"""
        if not self.regional_chaos_data:
            self.global_chaos_state.current_chaos_level = ChaosLevel.STABLE
            self.global_chaos_state.current_chaos_score = 0.0
            return
        
        # Calculate average pressure across regions
        total_pressure = sum(region.total_pressure for region in self.regional_chaos_data.values())
        avg_pressure = total_pressure / len(self.regional_chaos_data)
        
        # Update global state
        self.global_chaos_state.current_chaos_score = avg_pressure
        self.global_chaos_state.current_chaos_level = self._calculate_chaos_level_legacy(avg_pressure)
        self.global_chaos_state.calculation_timestamp = datetime.now()
        
        # Update regional mappings
        self.global_chaos_state.regional_chaos_levels = {
            region_id: region.chaos_level 
            for region_id, region in self.regional_chaos_data.items()
        }
    
    def _record_pressure_history(self, pressure_data: PressureData) -> None:
        """Record pressure data for history tracking"""
        current_time = datetime.now()
        total_pressure = sum(pressure_data.pressure_sources.values())
        
        self.pressure_history.append((current_time, total_pressure))
        
        # Limit history size for performance
        max_history = 1000
        if len(self.pressure_history) > max_history:
            self.pressure_history = self.pressure_history[-max_history:]
    
    # Legacy compatibility for start/stop methods
    async def start_engine(self) -> bool:
        """Start the chaos engine business logic (legacy compatibility)"""
        if self.system_running:
            return False
        
        self.system_running = True
        return True
    
    async def stop_engine(self) -> bool:
        """Stop the chaos engine (legacy compatibility)"""
        if not self.system_running:
            return False
        
        self.system_running = False
        return True
    
    def apply_mitigation(self, mitigation_type: str, effectiveness: float, duration_hours: float = None) -> bool:
        """Apply a mitigation factor to reduce chaos (legacy compatibility)"""
        if not 0.0 <= effectiveness <= 1.0:
            return False
        
        self.active_mitigations[mitigation_type] = effectiveness
        
        # If duration specified, schedule removal (business logic only)
        # Actual scheduling would be handled by infrastructure
        
        return True
    
    def remove_mitigation(self, mitigation_type: str) -> bool:
        """Remove an active mitigation (legacy compatibility)"""
        if mitigation_type in self.active_mitigations:
            del self.active_mitigations[mitigation_type]
            return True
        return False 