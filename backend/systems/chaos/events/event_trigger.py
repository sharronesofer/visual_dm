"""
Event Trigger

Handles triggering and management of chaos events based on pressure thresholds
and Bible-compliant event configurations.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field

from backend.systems.chaos.core.config import ChaosConfig, EventConfig
from backend.infrastructure.systems.chaos.models.chaos_state import ChaosState, ChaosLevel
from backend.infrastructure.systems.chaos.models.chaos_events import ChaosEvent, EventSeverity
from backend.infrastructure.systems.chaos.utils.chaos_math import ChaosMath

@dataclass
class EventTriggerResult:
    """Result of an event trigger check"""
    event_type: str
    triggered: bool
    probability: float
    severity: EventSeverity
    regions: List[str] = field(default_factory=list)
    reason: str = ""
    cascade_source: Optional[str] = None

class EventTrigger:
    """
    Handles event triggering based on chaos state and pressure levels.
    
    Implements Bible-compliant event management including:
    - Pressure-based event triggering
    - Event cooldown management
    - Cascade event processing
    - Regional event targeting
    """
    
    def __init__(self, config: ChaosConfig):
        """Initialize the event trigger"""
        self.config = config
        
        # Event cooldown tracking
        self.event_cooldowns: Dict[str, datetime] = {}
        
        # Active event tracking
        self.active_events: Dict[str, ChaosEvent] = {}
        
        # Event history for analysis
        self.event_history: List[ChaosEvent] = []
        
        # Cascade tracking
        self.pending_cascades: List[Dict[str, Any]] = []
        
        # Math utility for probability calculations
        self.chaos_math = ChaosMath(config)
        
        # Initialize state
        self._initialized = False
        self.trigger_count = 0
    
    async def initialize(self) -> None:
        """Initialize the event trigger"""
        # Load event configurations - use simple dict approach since EventConfig is a dataclass
        event_types_list = self.config.get_all_event_types()
        
        # Convert list to dict with basic configurations
        self.event_configs = {}
        for event_type in event_types_list:
            # Use simple dict for event config instead of EventConfig object
            self.event_configs[event_type] = {
                "cooldown_hours": 24,
                "concurrent_limit": 1,
                "required_pressure_types": [],
                "min_chaos_level": ChaosLevel.LOW,
                "weight": 1.0
            }
        
        # Initialize event cooldowns
        for event_type in self.event_configs.keys():
            self.event_cooldowns[event_type] = datetime.now() - timedelta(days=1)
        
        self._initialized = True
        print(f"Event trigger initialized with {len(self.event_configs)} event types")
    
    async def check_triggers(self, chaos_state: ChaosState, 
                           event_types: Optional[Dict[str, Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Check if any events should be triggered based on current chaos state.
        
        Args:
            chaos_state: Current chaos state of the system
            event_types: Optional event types to check (uses all if None)
            
        Returns:
            List of triggered events
        """
        if not self._initialized:
            await self.initialize()
        
        event_types = event_types or self.event_configs
        triggered_events = []
        
        for event_type, event_config in event_types.items():
            # Check if event can trigger
            trigger_result = await self._check_event_trigger(event_type, event_config, chaos_state)
            
            if trigger_result.triggered:
                # Create and process the event
                event = await self._create_chaos_event(trigger_result, chaos_state)
                triggered_events.append(event)
                
                # Update cooldown
                self.event_cooldowns[event_type] = datetime.now()
                
                # Store active event
                event_id = f"{event_type}_{datetime.now().timestamp()}"
                self.active_events[event_id] = event
                
                # Add to history
                self.event_history.append(event)
                
                print(f"Triggered {event_type} event with {trigger_result.severity.value} severity")
        
        self.trigger_count += len(triggered_events)
        return triggered_events
    
    async def force_trigger_event(self, event_type: str, severity: str = "moderate", 
                                regions: Optional[List[str]] = None) -> bool:
        """
        Force trigger a specific event (for testing or special circumstances).
        
        Args:
            event_type: Type of event to trigger
            severity: Severity level for the event
            regions: Regions to affect (optional)
            
        Returns:
            True if event was triggered successfully
        """
        try:
            # Get event configuration
            event_config = self.config.get_event_config(event_type)
            if not event_config:
                return False
            
            # Convert severity string to enum
            severity_enum = EventSeverity.MODERATE
            if severity.lower() == "minor":
                severity_enum = EventSeverity.MINOR
            elif severity.lower() == "major":
                severity_enum = EventSeverity.MAJOR
            elif severity.lower() == "critical":
                severity_enum = EventSeverity.CRITICAL
            
            # Create forced trigger result
            trigger_result = EventTriggerResult(
                event_type=event_type,
                triggered=True,
                probability=1.0,
                severity=severity_enum,
                regions=regions or ["global"],
                reason="Force triggered"
            )
            
            # Create dummy chaos state for event creation
            dummy_state = ChaosState(
                current_chaos_level=ChaosLevel.MODERATE,
                current_chaos_score=0.5
            )
            
            # Create and process the event
            event = await self._create_chaos_event(trigger_result, dummy_state)
            
            # Store the event
            event_id = f"{event_type}_{datetime.now().timestamp()}"
            self.active_events[event_id] = event
            self.event_history.append(event)
            
            # Update cooldown
            self.event_cooldowns[event_type] = datetime.now()
            
            self.trigger_count += 1
            return True
            
        except Exception as e:
            print(f"Error force triggering event: {e}")
            return False
    
    async def _check_event_trigger(self, event_type: str, event_config: Dict[str, Any], 
                                 chaos_state: ChaosState) -> EventTriggerResult:
        """
        Check if a specific event should trigger based on conditions.
        
        Args:
            event_type: Type of event to check
            event_config: Configuration dict for the event type
            chaos_state: Current chaos state
            
        Returns:
            EventTriggerResult with trigger decision and details
        """
        # Check cooldown
        if not self._is_event_off_cooldown(event_type, event_config):
            return EventTriggerResult(
                event_type=event_type,
                triggered=False,
                probability=0.0,
                severity=EventSeverity.MINOR,
                reason="Event on cooldown"
            )
        
        # Check concurrent event limit
        if not self._can_trigger_concurrent_event(event_type, event_config):
            return EventTriggerResult(
                event_type=event_type,
                triggered=False,
                probability=0.0,
                severity=EventSeverity.MINOR,
                reason="Concurrent event limit reached"
            )
        
        # Check pressure requirements
        if not self._check_pressure_requirements(event_config, chaos_state):
            return EventTriggerResult(
                event_type=event_type,
                triggered=False,
                probability=0.0,
                severity=EventSeverity.MINOR,
                reason="Pressure requirements not met"
            )
        
        # Calculate trigger probability
        probability = self.chaos_math.calculate_event_probability(
            event_type, 
            self._chaos_state_to_pressure_data(chaos_state),
            chaos_state.current_chaos_level
        )
        
        # Determine if event should trigger
        should_trigger = random.random() < probability
        
        if should_trigger:
            # Determine severity based on chaos level and pressure
            severity = self._determine_event_severity(chaos_state, event_config)
            
            # Determine affected regions
            regions = self._determine_affected_regions(chaos_state, event_config)
            
            return EventTriggerResult(
                event_type=event_type,
                triggered=True,
                probability=probability,
                severity=severity,
                regions=regions,
                reason=f"Probability check passed ({probability:.2%})"
            )
        else:
            return EventTriggerResult(
                event_type=event_type,
                triggered=False,
                probability=probability,
                severity=EventSeverity.MINOR,
                reason=f"Probability check failed ({probability:.2%})"
            )
    
    def _is_event_off_cooldown(self, event_type: str, event_config: Dict[str, Any]) -> bool:
        """Check if an event is off cooldown"""
        if event_type not in self.event_cooldowns:
            return True
        
        last_trigger = self.event_cooldowns[event_type]
        cooldown_duration = timedelta(hours=event_config.get("cooldown_hours", 24))
        
        return datetime.now() >= last_trigger + cooldown_duration
    
    def _can_trigger_concurrent_event(self, event_type: str, event_config: Dict[str, Any]) -> bool:
        """Check if event can trigger based on concurrent limits"""
        # Check global concurrent event limit
        active_count = len(self.active_events)
        if active_count >= self.config.max_concurrent_events:
            return False
        
        # Check event-specific concurrent limit
        same_type_count = sum(
            1 for event in self.active_events.values() 
            if event.event_type == event_type
        )
        concurrent_limit = event_config.get("concurrent_limit", 1)
        if same_type_count >= concurrent_limit:
            return False
        
        return True
    
    def _check_pressure_requirements(self, event_config: Dict[str, Any], chaos_state: ChaosState) -> bool:
        """Check if pressure requirements are met for event triggering"""
        pressure_requirements = event_config.get("required_pressure_types", [])
        if not pressure_requirements:
            return True
        
        # Convert chaos state to pressure data for checking
        pressure_data = self._chaos_state_to_pressure_data(chaos_state)
        
        # For now, just return True since we don't have detailed pressure requirements setup
        return True
    
    def _determine_event_severity(self, chaos_state: ChaosState, event_config: Dict[str, Any]) -> EventSeverity:
        """Determine event severity based on chaos state"""
        chaos_score = chaos_state.current_chaos_score
        
        # Use a basic scaling factor since severity_scaling isn't in our simple config
        scaling_factor = event_config.get("weight", 1.0)
        scaled_severity = chaos_score * scaling_factor
        
        if scaled_severity >= 0.8:
            return EventSeverity.CRITICAL
        elif scaled_severity >= 0.6:
            return EventSeverity.MAJOR
        elif scaled_severity >= 0.3:
            return EventSeverity.MODERATE
        else:
            return EventSeverity.MINOR
    
    def _determine_affected_regions(self, chaos_state: ChaosState, event_config: Dict[str, Any]) -> List[str]:
        """Determine which regions should be affected by the event"""
        # For now, use global region
        # In full implementation, this would analyze regional pressure data
        return ["global"]
    
    def _chaos_state_to_pressure_data(self, chaos_state: ChaosState):
        """Convert ChaosState to PressureData for compatibility"""
        from backend.infrastructure.systems.chaos.models.pressure_data import PressureData
        
        return PressureData(
            region_id="global",
            pressure_sources=chaos_state.pressure_source_contributions or {},
            calculation_timestamp=datetime.now(),
            calculation_time_ms=0.0
        )
    
    async def _create_chaos_event(self, trigger_result: EventTriggerResult, 
                                chaos_state: ChaosState) -> Dict[str, Any]:
        """
        Create a chaos event from trigger result.
        
        Args:
            trigger_result: Result of trigger check
            chaos_state: Current chaos state
            
        Returns:
            Dict representing the triggered event
        """
        event_data = {
            'type': trigger_result.event_type,
            'severity': trigger_result.severity.value,
            'regions': trigger_result.regions,
            'trigger_probability': trigger_result.probability,
            'trigger_reason': trigger_result.reason,
            'timestamp': datetime.now().isoformat(),
            'chaos_level': chaos_state.current_chaos_level.value,
            'chaos_score': chaos_state.current_chaos_score,
            'cascade_source': trigger_result.cascade_source
        }
        
        # Get event configuration for additional details
        event_config = self.config.get_event_config(trigger_result.event_type)
        if event_config:
            event_data.update({
                'display_name': event_config.display_name,
                'description': event_config.description,
                'base_probability': event_config.base_probability
            })
        
        return event_data
    
    def get_active_events(self) -> Dict[str, ChaosEvent]:
        """Get all currently active events"""
        return self.active_events.copy()
    
    def get_event_history(self, hours: int = 24) -> List[ChaosEvent]:
        """Get event history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            event for event in self.event_history 
            if event.trigger_timestamp >= cutoff_time
        ]
    
    def get_event_cooldowns(self) -> Dict[str, float]:
        """Get remaining cooldown times for all events (in hours)"""
        current_time = datetime.now()
        cooldowns = {}
        
        for event_type, last_trigger in self.event_cooldowns.items():
            # Use our own event configs instead of calling config.get_event_config
            event_config = self.event_configs.get(event_type)
            if event_config:
                cooldown_duration = timedelta(hours=event_config.get("cooldown_hours", 24))
                time_remaining = last_trigger + cooldown_duration - current_time
                
                if time_remaining.total_seconds() > 0:
                    cooldowns[event_type] = time_remaining.total_seconds() / 3600
                else:
                    cooldowns[event_type] = 0.0
        
        return cooldowns
    
    def get_trigger_metrics(self) -> Dict[str, Any]:
        """Get event trigger performance metrics"""
        return {
            'trigger_count': self.trigger_count,
            'active_events_count': len(self.active_events),
            'event_history_size': len(self.event_history),
            'event_types_configured': len(self.event_configs),
            'events_on_cooldown': sum(1 for cd in self.get_event_cooldowns().values() if cd > 0),
            'pending_cascades': len(self.pending_cascades)
        }
    
    def clear_event_history(self, older_than_hours: int = 168) -> int:
        """Clear event history older than specified hours (default: 1 week)"""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        original_count = len(self.event_history)
        
        self.event_history = [
            event for event in self.event_history 
            if event.trigger_timestamp >= cutoff_time
        ]
        
        cleared_count = original_count - len(self.event_history)
        return cleared_count
    
    def force_clear_cooldown(self, event_type: str) -> bool:
        """Force clear cooldown for a specific event type (for testing)"""
        if event_type in self.event_cooldowns:
            self.event_cooldowns[event_type] = datetime.now() - timedelta(days=1)
            return True
        return False 