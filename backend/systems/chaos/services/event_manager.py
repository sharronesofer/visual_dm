"""
Event Manager

Manages chaos events throughout their lifecycle - creation, execution, and resolution.
Handles event cascading, mitigation effects, and cross-system integration.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

from backend.systems.chaos.models.chaos_events import ChaosEvent, ChaosEventType, EventStatus
from backend.systems.chaos.models.chaos_state import ChaosState
from backend.systems.chaos.models.pressure_data import PressureData
from backend.systems.chaos.core.event_triggers import EventTriggerSystem
from backend.systems.chaos.services.mitigation_service import MitigationService
from backend.systems.chaos.utils.event_utils import EventUtils
from backend.systems.chaos.utils.chaos_math import ChaosCalculationResult
from backend.systems.chaos.core.config import ChaosConfig

logger = logging.getLogger(__name__)


class EventManager:
    """
    Coordinates chaos event triggering, management, and integration with other
    game systems. Handles event lifecycle, effect application, and system
    communication.
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.event_trigger_system = EventTriggerSystem(config)
        self.mitigation_service = MitigationService(config)
        self.event_utils = EventUtils()
        
        # Active events and tracking
        self.active_events: Dict[str, ChaosEvent] = {}
        self.event_history: List[ChaosEvent] = []
        self.event_statistics = {
            'total_triggered': 0,
            'total_resolved': 0,
            'total_failed': 0,
            'events_by_type': {},
            'average_duration': 0.0,
            'mitigation_applied': 0
        }
        
        # System connections for effect application
        self.system_connections: Dict[str, Any] = {}
        self.system_integrator = None
        
        # Performance tracking
        self.last_evaluation = datetime.now()
        self.evaluation_count = 0
        
        logger.info("Event Manager initialized")
    
    async def initialize(self) -> None:
        """Initialize the event manager and all its components"""
        try:
            logger.info("Initializing Event Manager components...")
            
            # Initialize event trigger system if needed
            await self.event_trigger_system.initialize()
            
            logger.info("Event Manager initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Event Manager: {e}")
            raise
    
    async def evaluate_and_trigger_events(self, chaos_result: ChaosCalculationResult,
                                        pressure_data: PressureData, 
                                        chaos_state: ChaosState) -> List[ChaosEvent]:
        """Evaluate conditions and trigger chaos events if thresholds are met"""
        triggered_events = []
        
        try:
            # Update tracking
            self.last_evaluation = datetime.now()
            self.evaluation_count += 1
            
            # Calculate mitigation effects on pressure
            mitigation_effects = self.mitigation_service.calculate_total_mitigation_effect(
                pressure_data, chaos_state
            )
            
            # Apply mitigation effects to chaos calculation
            mitigated_chaos_result = self._apply_mitigation_to_chaos_result(
                chaos_result, mitigation_effects
            )
            
            # Clean up completed/expired events
            await self._cleanup_completed_events()
            
            # Determine if conditions are right for triggering events
            if not self._should_trigger_events(mitigated_chaos_result, chaos_state):
                return triggered_events
            
            # Trigger events based on adjusted chaos conditions
            new_events = await self.event_trigger_system.evaluate_and_trigger(
                mitigated_chaos_result, pressure_data, chaos_state
            )
            
            # Process and validate new events
            for event in new_events:
                if await self._validate_and_process_event(event, chaos_state):
                    triggered_events.append(event)
                    
                    # Apply immediate effects
                    await self._apply_event_effects(event)
                    
                    # Dispatch event notification
                    await self._dispatch_event(event)
            
            # Update statistics
            self._update_event_statistics(triggered_events)
            
            logger.debug(f"Event evaluation complete: {len(triggered_events)} events triggered")
            
        except Exception as e:
            logger.error(f"Error in event evaluation: {e}")
        
        return triggered_events
    
    def _apply_mitigation_to_chaos_result(self, chaos_result: ChaosCalculationResult,
                                        mitigation_effects: Dict[str, float]) -> ChaosCalculationResult:
        """Apply mitigation effects to reduce chaos scores"""
        
        # Create a modified copy of the chaos result
        mitigated_result = ChaosCalculationResult(
            chaos_score=chaos_result.chaos_score,
            chaos_level=chaos_result.chaos_level,
            regional_scores=chaos_result.regional_scores.copy() if chaos_result.regional_scores else {},
            source_contributions=chaos_result.source_contributions.copy() if chaos_result.source_contributions else {},
            temporal_factors=chaos_result.temporal_factors.copy() if chaos_result.temporal_factors else {}
        )
        
        # Apply global mitigation to overall chaos score
        total_mitigation = 0.0
        mitigation_count = 0
        
        for source, mitigation_effect in mitigation_effects.items():
            if mitigation_effect > 0:
                total_mitigation += mitigation_effect
                mitigation_count += 1
        
        if mitigation_count > 0:
            average_mitigation = total_mitigation / mitigation_count
            # Apply logarithmic scaling to prevent over-mitigation
            effective_mitigation = min(0.8, average_mitigation * 0.7)  # Cap at 80% reduction
            
            mitigated_result.chaos_score *= (1.0 - effective_mitigation)
            
            # Update chaos level based on new score
            mitigated_result.chaos_level = self._determine_chaos_level_from_score(
                mitigated_result.chaos_score
            )
            
            # Apply source-specific mitigations
            if mitigated_result.source_contributions:
                for source, contribution in mitigated_result.source_contributions.items():
                    source_key = source.value if hasattr(source, 'value') else str(source)
                    if source_key in mitigation_effects:
                        mitigation = mitigation_effects[source_key]
                        mitigated_result.source_contributions[source] = contribution * (1.0 - mitigation)
            
            # Log mitigation effects
            logger.debug(f"Applied mitigation: {effective_mitigation:.3f} reduction "
                        f"(chaos score: {chaos_result.chaos_score:.3f} -> {mitigated_result.chaos_score:.3f})")
        
        return mitigated_result
    
    def _determine_chaos_level_from_score(self, score: float):
        """Determine chaos level from score - mirrors the main chaos engine logic"""
        from backend.systems.chaos.models.chaos_state import ChaosLevel
        
        if score >= 0.9:
            return ChaosLevel.EXTREME
        elif score >= 0.7:
            return ChaosLevel.CRITICAL
        elif score >= 0.5:
            return ChaosLevel.HIGH
        elif score >= 0.3:
            return ChaosLevel.ELEVATED
        elif score >= 0.1:
            return ChaosLevel.STABLE
        else:
            return ChaosLevel.DORMANT
    
    def _should_trigger_events(self, chaos_result: ChaosCalculationResult, 
                             chaos_state: ChaosState) -> bool:
        """Determine if conditions are right for triggering events"""
        
        # Don't trigger if chaos level is too low
        from backend.systems.chaos.models.chaos_state import ChaosLevel
        if chaos_result.chaos_level in [ChaosLevel.DORMANT, ChaosLevel.STABLE]:
            return False
        
        # Check active event limits
        active_count = len(self.active_events)
        max_concurrent = self.config.chaos_event_limits.get('max_concurrent_events', 5)
        if active_count >= max_concurrent:
            logger.debug(f"Maximum concurrent events reached ({active_count})")
            return False
        
        # Check timing constraints
        if self._check_event_spacing_constraints():
            return False
        
        # Check system load
        if self._check_system_load_constraints(chaos_state):
            return False
        
        return True
    
    def _check_event_spacing_constraints(self) -> bool:
        """Check if enough time has passed since last event"""
        if not self.event_history:
            return False
        
        last_event_time = max(event.created_at for event in self.event_history[-10:])
        time_since_last = (datetime.now() - last_event_time).total_seconds()
        
        min_spacing = self.config.chaos_event_limits.get('min_spacing_seconds', 300)  # 5 minutes
        
        return time_since_last < min_spacing
    
    def _check_system_load_constraints(self, chaos_state: ChaosState) -> bool:
        """Check if system load allows for new events"""
        # Don't trigger new events if system health is poor
        if chaos_state.system_health < 0.5:
            logger.debug("System health too low for new events")
            return True
        
        # Don't trigger if there are too many unresolved effects
        unresolved_effects = sum(1 for event in self.active_events.values() 
                               if event.status == EventStatus.ACTIVE)
        max_unresolved = self.config.chaos_event_limits.get('max_unresolved_effects', 10)
        
        if unresolved_effects >= max_unresolved:
            logger.debug("Too many unresolved effects")
            return True
        
        return False
    
    async def _validate_and_process_event(self, event: ChaosEvent, 
                                        chaos_state: ChaosState) -> bool:
        """Validate and process a new event before adding to active events"""
        try:
            # Check for event conflicts
            if self.event_utils.has_conflicting_events(event, list(self.active_events.values())):
                logger.debug(f"Event {event.event_id} conflicts with active events")
                return False
            
            # Check regional capacity
            if not self._check_regional_event_capacity(event):
                logger.debug(f"Regional capacity exceeded for event {event.event_id}")
                return False
            
            # Add to active events
            self.active_events[event.event_id] = event
            self.event_history.append(event)
            
            logger.info(f"New chaos event: {event.event_type.value} "
                       f"(severity: {event.severity.value}, regions: {len(event.affected_regions)})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {e}")
            return False
    
    def _check_regional_event_capacity(self, event: ChaosEvent) -> bool:
        """Check if regions can handle another event"""
        max_events_per_region = self.config.chaos_event_limits.get('max_events_per_region', 3)
        
        for region_id in event.affected_regions:
            region_event_count = sum(
                1 for active_event in self.active_events.values()
                if region_id in active_event.affected_regions
            )
            
            if region_event_count >= max_events_per_region:
                return False
        
        return True
    
    async def _apply_event_effects(self, event: ChaosEvent) -> None:
        """Apply immediate effects of a chaos event"""
        try:
            # Apply effects through connected systems
            for effect in event.effects:
                await self._apply_single_effect(effect, event)
            
            # Update event status
            event.status = EventStatus.ACTIVE
            
        except Exception as e:
            logger.error(f"Error applying effects for event {event.event_id}: {e}")
            event.status = EventStatus.FAILED
    
    async def _apply_single_effect(self, effect, event: ChaosEvent) -> None:
        """Apply a single event effect to appropriate systems"""
        try:
            effect_type = effect.get('type', 'unknown')
            target_system = effect.get('target_system')
            
            if target_system and target_system in self.system_connections:
                system_handler = self.system_connections[target_system]
                await system_handler.apply_chaos_effect(effect, event)
                logger.debug(f"Applied {effect_type} effect to {target_system}")
            else:
                logger.debug(f"No handler for effect {effect_type} on {target_system}")
                
        except Exception as e:
            logger.error(f"Error applying effect {effect}: {e}")
    
    async def _dispatch_event(self, event: ChaosEvent) -> None:
        """Dispatch event notification to other systems"""
        try:
            if self.system_integrator:
                await self.system_integrator.dispatch_chaos_event(event)
            else:
                logger.debug(f"No system integrator available for event {event.event_id}")
                
        except Exception as e:
            logger.error(f"Error dispatching event {event.event_id}: {e}")
    
    async def _cleanup_completed_events(self) -> None:
        """Clean up completed or expired events"""
        completed_events = []
        
        for event_id, event in list(self.active_events.items()):
            if self._is_event_completed(event):
                completed_events.append(event_id)
                
                # Apply resolution effects
                await self._resolve_event(event)
        
        # Remove completed events
        for event_id in completed_events:
            del self.active_events[event_id]
        
        if completed_events:
            logger.debug(f"Cleaned up {len(completed_events)} completed events")
    
    def _is_event_completed(self, event: ChaosEvent) -> bool:
        """Check if an event should be considered completed"""
        # Check if event has expired
        if event.duration_hours:
            elapsed_hours = (datetime.now() - event.created_at).total_seconds() / 3600.0
            if elapsed_hours >= event.duration_hours:
                return True
        
        # Check if event has been manually resolved
        if event.status in [EventStatus.RESOLVED, EventStatus.FAILED, EventStatus.CANCELLED]:
            return True
        
        return False
    
    async def _resolve_event(self, event: ChaosEvent) -> None:
        """Handle event resolution and apply appropriate mitigations"""
        try:
            # Determine resolution outcome
            if event.status == EventStatus.RESOLVED:
                # Successful resolution - apply mitigation
                await self._apply_resolution_mitigation(event)
                self.event_statistics['total_resolved'] += 1
            elif event.status == EventStatus.FAILED:
                # Failed resolution - may increase pressure
                await self._apply_failure_consequences(event)
                self.event_statistics['total_failed'] += 1
            
            # Log resolution
            logger.info(f"Event resolved: {event.event_type.value} "
                       f"(status: {event.status.value}, duration: {self._calculate_event_duration(event):.1f}h)")
            
        except Exception as e:
            logger.error(f"Error resolving event {event.event_id}: {e}")
    
    async def _apply_resolution_mitigation(self, event: ChaosEvent) -> None:
        """Apply mitigation effects when an event is successfully resolved"""
        try:
            # Determine appropriate mitigation type based on event
            mitigation_type = self._determine_mitigation_type(event)
            
            if mitigation_type:
                # Calculate mitigation magnitude based on event severity and resolution quality
                magnitude = self._calculate_mitigation_magnitude(event)
                
                # Apply mitigation
                mitigation = await self.mitigation_service.apply_mitigation(
                    mitigation_type=mitigation_type,
                    source_id=event.event_id,
                    source_type='chaos_event_resolution',
                    magnitude=magnitude,
                    affected_regions=event.affected_regions,
                    additional_context={
                        'event_type': event.event_type.value,
                        'resolution_quality': getattr(event, 'resolution_quality', 1.0),
                        'event_severity': event.severity.value
                    }
                )
                
                if mitigation:
                    self.event_statistics['mitigation_applied'] += 1
                    logger.info(f"Applied mitigation from event resolution: {mitigation_type} "
                               f"(effectiveness: {mitigation.effectiveness:.3f})")
                
        except Exception as e:
            logger.error(f"Error applying resolution mitigation for {event.event_id}: {e}")
    
    def _determine_mitigation_type(self, event: ChaosEvent) -> Optional[str]:
        """Determine appropriate mitigation type based on resolved event"""
        event_to_mitigation = {
            ChaosEventType.POLITICAL_UPHEAVAL: 'effective_leadership',
            ChaosEventType.LEADERSHIP_COUP: 'administrative_efficiency',
            ChaosEventType.REBELLION: 'diplomatic_treaty',
            ChaosEventType.NATURAL_DISASTER: 'disaster_relief',
            ChaosEventType.EARTHQUAKE: 'infrastructure_construction',
            ChaosEventType.FLOOD: 'disaster_relief',
            ChaosEventType.DROUGHT: 'agricultural_investment',
            ChaosEventType.PLAGUE: 'crisis_management',
            ChaosEventType.ECONOMIC_COLLAPSE: 'trade_agreement',
            ChaosEventType.MARKET_CRASH: 'economic_quest_completion',
            ChaosEventType.CURRENCY_DEVALUATION: 'trade_route_establishment',
            ChaosEventType.TRADE_DISRUPTION: 'trade_agreement',
            ChaosEventType.WAR_OUTBREAK: 'peace_negotiations',
            ChaosEventType.FACTION_WAR: 'alliance_formation',
            ChaosEventType.TERRITORIAL_CONFLICT: 'diplomatic_treaty',
            ChaosEventType.RESOURCE_WAR: 'resource_stockpiling',
            ChaosEventType.RESOURCE_SCARCITY: 'agricultural_investment',
            ChaosEventType.FOOD_SHORTAGE: 'agricultural_investment',
            ChaosEventType.MATERIAL_SCARCITY: 'mining_expansion',
            ChaosEventType.ENERGY_CRISIS: 'infrastructure_construction',
            ChaosEventType.FACTION_BETRAYAL: 'alliance_formation',
            ChaosEventType.ALLIANCE_BREAK: 'diplomatic_treaty',
            ChaosEventType.INTERNAL_CONFLICT: 'effective_leadership',
            ChaosEventType.LEADERSHIP_COUP: 'judicial_reform',
            ChaosEventType.CHARACTER_REVELATION: 'cultural_festival',
            ChaosEventType.SCANDAL: 'education_initiative',
            ChaosEventType.SECRET_DISCOVERY: 'crisis_management',
            ChaosEventType.DRAMATIC_REVEAL: 'cultural_festival'
        }
        
        return event_to_mitigation.get(event.event_type)
    
    def _calculate_mitigation_magnitude(self, event: ChaosEvent) -> float:
        """Calculate mitigation magnitude based on event characteristics"""
        # Base magnitude from event severity
        severity_multipliers = {
            'minor': 0.5,
            'moderate': 1.0,
            'major': 1.5,
            'severe': 2.0,
            'catastrophic': 2.5
        }
        
        base_magnitude = severity_multipliers.get(event.severity.value, 1.0)
        
        # Adjust based on resolution quality
        resolution_quality = getattr(event, 'resolution_quality', 1.0)
        
        # Adjust based on affected regions (more regions = larger impact)
        region_multiplier = min(2.0, 1.0 + len(event.affected_regions) * 0.1)
        
        return base_magnitude * resolution_quality * region_multiplier
    
    async def _apply_failure_consequences(self, event: ChaosEvent) -> None:
        """Apply consequences when an event fails to resolve properly"""
        try:
            # Failed events may increase pressure temporarily
            logger.warning(f"Event {event.event_type.value} failed to resolve properly")
            
            # This would integrate with the pressure monitoring system
            # to temporarily increase pressure in affected areas
            
        except Exception as e:
            logger.error(f"Error applying failure consequences for {event.event_id}: {e}")
    
    def _calculate_event_duration(self, event: ChaosEvent) -> float:
        """Calculate actual duration of an event in hours"""
        return (datetime.now() - event.created_at).total_seconds() / 3600.0
    
    def _update_event_statistics(self, triggered_events: List[ChaosEvent]) -> None:
        """Update event statistics"""
        self.event_statistics['total_triggered'] += len(triggered_events)
        
        for event in triggered_events:
            event_type = event.event_type.value
            if event_type not in self.event_statistics['events_by_type']:
                self.event_statistics['events_by_type'][event_type] = 0
            self.event_statistics['events_by_type'][event_type] += 1
        
        # Update average duration for completed events
        if self.event_history:
            completed_events = [e for e in self.event_history if self._is_event_completed(e)]
            if completed_events:
                total_duration = sum(self._calculate_event_duration(e) for e in completed_events)
                self.event_statistics['average_duration'] = total_duration / len(completed_events)
    
    # Public API methods
    
    def get_active_events(self) -> List[ChaosEvent]:
        """Get all currently active chaos events"""
        return list(self.active_events.values())
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about chaos events"""
        return {
            **self.event_statistics,
            'active_events': len(self.active_events),
            'last_evaluation': self.last_evaluation.isoformat(),
            'evaluation_count': self.evaluation_count,
            'mitigation_summary': self.mitigation_service.get_mitigation_summary()
        }
    
    def get_mitigation_recommendations(self, pressure_data: PressureData, 
                                     chaos_state: ChaosState) -> List[Dict[str, Any]]:
        """Get mitigation recommendations based on current state"""
        return self.mitigation_service.get_mitigation_recommendations(pressure_data, chaos_state)
    
    async def apply_mitigation(self, mitigation_type: str, source_id: str, 
                             source_type: str, magnitude: float = 1.0,
                             affected_regions: List[str] = None,
                             additional_context: Dict[str, Any] = None) -> bool:
        """Apply a mitigation factor"""
        mitigation = await self.mitigation_service.apply_mitigation(
            mitigation_type, source_id, source_type, magnitude, 
            affected_regions, additional_context
        )
        return mitigation is not None
    
    async def resolve_event(self, event_id: str, resolution_quality: float = 1.0) -> bool:
        """Manually resolve an event (for quest completions, etc.)"""
        if event_id in self.active_events:
            event = self.active_events[event_id]
            event.status = EventStatus.RESOLVED
            setattr(event, 'resolution_quality', resolution_quality)
            
            # Event will be processed in next cleanup cycle
            logger.info(f"Manually resolved event: {event.event_type.value} (quality: {resolution_quality})")
            return True
        
        return False
    
    async def cancel_event(self, event_id: str) -> bool:
        """Cancel an active event"""
        if event_id in self.active_events:
            event = self.active_events[event_id]
            event.status = EventStatus.CANCELLED
            
            logger.info(f"Cancelled event: {event.event_type.value}")
            return True
        
        return False
    
    def set_event_dispatcher(self, system_integrator) -> None:
        """Set the system integrator for event dispatching"""
        self.system_integrator = system_integrator
        logger.info("System integrator connected to event manager")
    
    def set_system_connection(self, system_name: str, system_handler) -> None:
        """Set up connection to a game system for effect application"""
        self.system_connections[system_name] = system_handler
        logger.info(f"Connected {system_name} system to event manager") 