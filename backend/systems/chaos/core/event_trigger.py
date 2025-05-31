"""
Event Trigger - Handles chaos event triggering when thresholds are exceeded
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random

from backend.systems.chaos.models.chaos_events import ChaosEvent
from backend.systems.chaos.utils.chaos_calculator import ChaosCalculationResult
from backend.systems.chaos.core.config import ChaosConfig
# REMOVED: deprecated event_base import

logger = logging.getLogger(__name__)

class EventTrigger:
    """Handles triggering of chaos events when thresholds are exceeded"""
    
    def __init__(self, config: ChaosConfig, event_dispatcher: EventDispatcher):
        self.config = config
        self.event_dispatcher = event_dispatcher
        self.recent_events: List[Dict[str, Any]] = []
        self.cooldown_periods: Dict[str, datetime] = {}
        
        # Event definitions with cascading effects
        self.chaos_events = {
            'market_crash': {
                'severity': 'high',
                'duration_hours': 48,
                'cascading_events': ['trade_disruption', 'resource_shortage'],
                'affected_systems': ['economy', 'faction', 'population']
            },
            'leadership_crisis': {
                'severity': 'high', 
                'duration_hours': 72,
                'cascading_events': ['succession_dispute', 'diplomatic_breakdown'],
                'affected_systems': ['faction', 'diplomacy', 'region']
            },
            'natural_disaster': {
                'severity': 'extreme',
                'duration_hours': 24,
                'cascading_events': ['population_migration', 'resource_scarcity'],
                'affected_systems': ['region', 'population', 'economy']
            }
        }
    
    async def evaluate_and_trigger(self, chaos_result: ChaosCalculationResult,
                                 region_id: str) -> List[ChaosEvent]:
        """Evaluate chaos state and trigger appropriate events"""
        triggered_events = []
        
        if not chaos_result.threshold_exceeded:
            return triggered_events
        
        # Check event cooldowns
        if self._is_region_in_cooldown(region_id):
            logger.info(f"Region {region_id} in cooldown, skipping event trigger")
            return triggered_events
        
        # Select events based on recommendations
        selected_events = self._select_events(chaos_result, region_id)
        
        # Trigger selected events
        for event_type in selected_events:
            try:
                event = await self._trigger_chaos_event(event_type, region_id, chaos_result)
                if event:
                    triggered_events.append(event)
                    await self._schedule_cascading_events(event)
                    
            except Exception as e:
                logger.error(f"Failed to trigger chaos event {event_type}: {e}")
        
        # Update cooldowns
        if triggered_events:
            self._update_cooldowns(region_id)
        
        return triggered_events
    
    def _select_events(self, chaos_result: ChaosCalculationResult, 
                      region_id: str) -> List[str]:
        """Select appropriate events based on chaos calculation"""
        candidates = chaos_result.recommended_events
        
        # Filter out events in cooldown
        available_events = [
            event for event in candidates 
            if not self._is_event_in_cooldown(event, region_id)
        ]
        
        # Select 1-2 events based on chaos score
        if chaos_result.chaos_score > 0.9:
            num_events = min(2, len(available_events))
        else:
            num_events = min(1, len(available_events))
        
        return random.sample(available_events, num_events) if available_events else []
    
    async def _trigger_chaos_event(self, event_type: str, region_id: str,
                                 chaos_result: ChaosCalculationResult) -> Optional[ChaosEvent]:
        """Trigger a specific chaos event"""
        
        event_config = self.chaos_events.get(event_type, {})
        
        # Create chaos event
        chaos_event = ChaosEvent(
            event_type=event_type,
            region_id=region_id,
            severity=event_config.get('severity', 'moderate'),
            trigger_time=datetime.now(),
            duration_hours=event_config.get('duration_hours', 24),
            chaos_score=chaos_result.chaos_score,
            pressure_sources=chaos_result.pressure_sources,
            affected_systems=event_config.get('affected_systems', [])
        )
        
        # Dispatch to affected systems
        await self._dispatch_to_systems(chaos_event)
        
        # Log the event
        logger.info(f"Triggered chaos event {event_type} in region {region_id}")
        
        # Track recent events
        self.recent_events.append({
            'event_type': event_type,
            'region_id': region_id,
            'timestamp': datetime.now(),
            'chaos_score': chaos_result.chaos_score
        })
        
        return chaos_event
    
    async def _dispatch_to_systems(self, chaos_event: ChaosEvent):
        """Dispatch chaos event to all affected systems"""
        
        for system_name in chaos_event.affected_systems:
            try:
                await self.event_dispatcher.dispatch(
                    event_type=f"chaos_{chaos_event.event_type}",
                    data={
                        'chaos_event': chaos_event,
                        'region_id': chaos_event.region_id,
                        'severity': chaos_event.severity,
                        'chaos_score': chaos_event.chaos_score
                    },
                    target_system=system_name
                )
            except Exception as e:
                logger.error(f"Failed to dispatch chaos event to {system_name}: {e}")
    
    async def _schedule_cascading_events(self, primary_event: ChaosEvent):
        """Schedule cascading secondary events"""
        
        event_config = self.chaos_events.get(primary_event.event_type, {})
        cascading_events = event_config.get('cascading_events', [])
        
        if not cascading_events:
            return
        
        # Schedule each cascading event with delay
        for i, cascade_event in enumerate(cascading_events):
            delay_hours = random.uniform(1, 8)  # 1-8 hour delay
            
            # Schedule the cascading event
            asyncio.create_task(
                self._delayed_cascade_trigger(
                    cascade_event, 
                    primary_event.region_id,
                    delay_hours,
                    primary_event.chaos_score * 0.7  # Reduced intensity
                )
            )
    
    async def _delayed_cascade_trigger(self, event_type: str, region_id: str,
                                     delay_hours: float, chaos_score: float):
        """Trigger a cascading event after delay"""
        
        await asyncio.sleep(delay_hours * 3600)  # Convert to seconds
        
        # Create simplified chaos result for cascading event
        from backend.systems.chaos.utils.chaos_calculator import ChaosCalculationResult
        
        cascade_result = ChaosCalculationResult(
            chaos_score=chaos_score,
            pressure_sources={'cascade': chaos_score},
            weighted_factors={'cascade': chaos_score},
            threshold_exceeded=True,
            recommended_events=[event_type],
            mitigation_factors={}
        )
        
        await self._trigger_chaos_event(event_type, region_id, cascade_result)
    
    def _is_region_in_cooldown(self, region_id: str) -> bool:
        """Check if region is in cooldown period"""
        cooldown_key = f"region_{region_id}"
        
        if cooldown_key in self.cooldown_periods:
            return datetime.now() < self.cooldown_periods[cooldown_key]
        
        return False
    
    def _is_event_in_cooldown(self, event_type: str, region_id: str) -> bool:
        """Check if specific event type is in cooldown for region"""
        cooldown_key = f"{event_type}_{region_id}"
        
        if cooldown_key in self.cooldown_periods:
            return datetime.now() < self.cooldown_periods[cooldown_key]
        
        return False
    
    def _update_cooldowns(self, region_id: str):
        """Update cooldown periods after triggering events"""
        
        # Region-wide cooldown
        region_cooldown = datetime.now() + timedelta(
            hours=self.config.region_cooldown_hours
        )
        self.cooldown_periods[f"region_{region_id}"] = region_cooldown
        
        # Event-specific cooldowns
        for event in self.recent_events[-3:]:  # Last 3 events
            if event['region_id'] == region_id:
                event_cooldown = datetime.now() + timedelta(
                    hours=self.config.event_cooldown_hours
                )
                cooldown_key = f"{event['event_type']}_{region_id}"
                self.cooldown_periods[cooldown_key] = event_cooldown
    
    def get_recent_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent chaos events within specified time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            event for event in self.recent_events
            if event['timestamp'] > cutoff_time
        ]
    
    def clear_expired_cooldowns(self):
        """Remove expired cooldown entries"""
        current_time = datetime.now()
        
        expired_keys = [
            key for key, expiry_time in self.cooldown_periods.items()
            if current_time >= expiry_time
        ]
        
        for key in expired_keys:
            del self.cooldown_periods[key]
            
    def get_cooldown_status(self, region_id: str) -> Dict[str, Any]:
        """Get cooldown status for a region"""
        current_time = datetime.now()
        
        status = {
            'region_cooldown': False,
            'region_cooldown_expires': None,
            'event_cooldowns': {}
        }
        
        # Check region cooldown
        region_key = f"region_{region_id}"
        if region_key in self.cooldown_periods:
            if current_time < self.cooldown_periods[region_key]:
                status['region_cooldown'] = True
                status['region_cooldown_expires'] = self.cooldown_periods[region_key]
        
        # Check event-specific cooldowns
        for key, expiry_time in self.cooldown_periods.items():
            if key.endswith(f"_{region_id}") and current_time < expiry_time:
                event_type = key.replace(f"_{region_id}", "")
                status['event_cooldowns'][event_type] = expiry_time
        
        return status