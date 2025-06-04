"""
Equipment Usage Tracker Service

This service tracks actual equipment usage events and applies utilization-based 
durability loss. It integrates with the business logic service to ensure that 
equipment degrades based on actual usage rather than just time passing.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from uuid import UUID
import logging
from dataclasses import dataclass, asdict
from enum import Enum

from .business_logic_service import EquipmentBusinessLogicService

logger = logging.getLogger(__name__)


class UsageEventType(Enum):
    """Types of equipment usage events"""
    WEAPON_ATTACK = "weapon_attack"
    WEAPON_PARRY = "weapon_parry"
    ARMOR_HIT = "armor_hit" 
    SHIELD_BLOCK = "shield_block"
    TOOL_USE = "tool_use"
    ENVIRONMENTAL_EXPOSURE = "environmental_exposure"
    CRITICAL_EVENT = "critical_event"
    REPAIR_EVENT = "repair_event"


@dataclass
class UsageEvent:
    """Individual equipment usage event"""
    equipment_id: str
    character_id: str
    event_type: UsageEventType
    timestamp: datetime
    usage_intensity: float = 1.0  # Multiplier for wear amount
    is_critical: bool = False
    environmental_factor: float = 1.0
    context: Dict[str, Any] = None  # Additional event context
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass 
class EquipmentUsageSession:
    """A session of equipment usage (e.g., a combat encounter, crafting session)"""
    session_id: str
    character_id: str
    session_type: str  # combat, crafting, exploration, etc.
    start_time: datetime
    end_time: Optional[datetime] = None
    events: List[UsageEvent] = None
    
    def __post_init__(self):
        if self.events is None:
            self.events = []
    
    @property
    def duration_minutes(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return 0.0
    
    @property 
    def total_events(self) -> int:
        return len(self.events)


class EquipmentUsageTracker:
    """Service for tracking equipment usage and applying utilization-based durability loss"""
    
    def __init__(self, business_service: EquipmentBusinessLogicService):
        self.business_service = business_service
        self.active_sessions: Dict[str, EquipmentUsageSession] = {}
        self.usage_history: List[UsageEvent] = []
        self.equipment_usage_stats: Dict[str, Dict[str, Any]] = {}
        
    def start_usage_session(
        self, 
        character_id: str, 
        session_type: str,
        session_id: Optional[str] = None
    ) -> str:
        """Start a new equipment usage session"""
        if session_id is None:
            session_id = f"{character_id}_{session_type}_{datetime.utcnow().isoformat()}"
        
        session = EquipmentUsageSession(
            session_id=session_id,
            character_id=character_id,
            session_type=session_type,
            start_time=datetime.utcnow()
        )
        
        self.active_sessions[session_id] = session
        
        logger.info(f"Started usage session {session_id} for character {character_id}")
        return session_id
    
    def end_usage_session(self, session_id: str) -> Optional[EquipmentUsageSession]:
        """End an active usage session and return summary"""
        if session_id not in self.active_sessions:
            logger.warning(f"No active session found with ID {session_id}")
            return None
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.utcnow()
        
        # Move to history
        del self.active_sessions[session_id]
        
        logger.info(
            f"Ended usage session {session_id}: {session.total_events} events "
            f"over {session.duration_minutes:.1f} minutes"
        )
        
        return session
    
    def record_equipment_usage(
        self,
        equipment_id: str,
        character_id: str,
        event_type: UsageEventType,
        session_id: Optional[str] = None,
        usage_intensity: float = 1.0,
        is_critical: bool = False,
        environmental_factor: float = 1.0,
        context: Optional[Dict[str, Any]] = None
    ) -> UsageEvent:
        """Record a single equipment usage event"""
        event = UsageEvent(
            equipment_id=equipment_id,
            character_id=character_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            usage_intensity=usage_intensity,
            is_critical=is_critical,
            environmental_factor=environmental_factor,
            context=context or {}
        )
        
        # Add to session if one is active
        if session_id and session_id in self.active_sessions:
            self.active_sessions[session_id].events.append(event)
        
        # Add to general history
        self.usage_history.append(event)
        
        # Update equipment usage statistics
        self._update_equipment_stats(equipment_id, event)
        
        logger.debug(f"Recorded {event_type.value} for equipment {equipment_id}")
        return event
    
    def apply_usage_durability_loss(
        self,
        equipment_id: str,
        current_durability: float,
        quality_tier: str,
        usage_events: List[UsageEvent]
    ) -> Tuple[float, Dict[str, Any]]:
        """Apply durability loss based on actual usage events"""
        total_durability_loss = 0.0
        event_details = []
        
        for event in usage_events:
            # Map event type to usage type for business logic
            usage_type = self._map_event_to_usage_type(event.event_type)
            
            # Calculate durability loss for this event
            new_durability, breakdown = self.business_service.calculate_utilization_based_durability_loss(
                current_durability=current_durability - total_durability_loss,
                quality_tier=quality_tier,
                usage_type=usage_type,
                usage_count=1,
                environmental_factor=event.environmental_factor,
                is_critical=event.is_critical
            )
            
            event_loss = (current_durability - total_durability_loss) - new_durability
            total_durability_loss += event_loss
            
            event_details.append({
                'event_type': event.event_type.value,
                'timestamp': event.timestamp.isoformat(),
                'durability_loss': event_loss,
                'breakdown': breakdown
            })
            
            # Break if equipment is broken
            if new_durability <= 0:
                break
        
        final_durability = max(0.0, current_durability - total_durability_loss)
        
        return final_durability, {
            'initial_durability': current_durability,
            'final_durability': final_durability,
            'total_durability_loss': total_durability_loss,
            'events_processed': len(event_details),
            'event_details': event_details,
            'equipment_broke': final_durability <= 0
        }
    
    def process_session_durability_loss(
        self,
        session: EquipmentUsageSession,
        equipment_states: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process durability loss for all equipment used in a session"""
        results = {}
        
        # Group events by equipment
        equipment_events = {}
        for event in session.events:
            if event.equipment_id not in equipment_events:
                equipment_events[event.equipment_id] = []
            equipment_events[event.equipment_id].append(event)
        
        # Process durability for each piece of equipment
        for equipment_id, events in equipment_events.items():
            if equipment_id in equipment_states:
                equipment_state = equipment_states[equipment_id]
                
                final_durability, details = self.apply_usage_durability_loss(
                    equipment_id=equipment_id,
                    current_durability=equipment_state.get('current_durability', 100.0),
                    quality_tier=equipment_state.get('quality_tier', 'basic'),
                    usage_events=events
                )
                
                results[equipment_id] = {
                    'initial_durability': equipment_state.get('current_durability', 100.0),
                    'final_durability': final_durability,
                    'usage_events_count': len(events),
                    'details': details
                }
        
        return {
            'session_id': session.session_id,
            'session_type': session.session_type,
            'duration_minutes': session.duration_minutes,
            'total_events': session.total_events,
            'equipment_processed': len(results),
            'equipment_results': results
        }
    
    def get_equipment_usage_stats(self, equipment_id: str) -> Dict[str, Any]:
        """Get usage statistics for a specific piece of equipment"""
        return self.equipment_usage_stats.get(equipment_id, {
            'total_uses': 0,
            'critical_uses': 0,
            'event_type_counts': {},
            'first_use': None,
            'last_use': None,
            'average_intensity': 0.0
        })
    
    def get_character_usage_summary(
        self, 
        character_id: str, 
        time_period_hours: int = 24
    ) -> Dict[str, Any]:
        """Get usage summary for a character over a time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_period_hours)
        
        relevant_events = [
            event for event in self.usage_history 
            if event.character_id == character_id and event.timestamp >= cutoff_time
        ]
        
        # Group by equipment
        equipment_usage = {}
        for event in relevant_events:
            if event.equipment_id not in equipment_usage:
                equipment_usage[event.equipment_id] = {
                    'total_uses': 0,
                    'critical_uses': 0,
                    'event_types': {}
                }
            
            stats = equipment_usage[event.equipment_id]
            stats['total_uses'] += 1
            if event.is_critical:
                stats['critical_uses'] += 1
            
            event_type = event.event_type.value
            stats['event_types'][event_type] = stats['event_types'].get(event_type, 0) + 1
        
        return {
            'character_id': character_id,
            'time_period_hours': time_period_hours,
            'total_events': len(relevant_events),
            'unique_equipment_used': len(equipment_usage),
            'equipment_usage': equipment_usage
        }
    
    def predict_equipment_breakdown_risk(
        self,
        equipment_id: str,
        current_durability: float,
        quality_tier: str,
        projected_daily_uses: int = 24
    ) -> Dict[str, Any]:
        """Predict when equipment is likely to break based on usage patterns"""
        
        # Get historical usage pattern for this equipment
        stats = self.get_equipment_usage_stats(equipment_id)
        
        # Use business service to calculate expected lifespan
        lifespan_info = self.business_service.calculate_expected_item_lifespan(
            quality_tier=quality_tier,
            daily_usage_frequency=projected_daily_uses,
            usage_type='normal_use',  # Default assumption
            environmental_factor=1.0
        )
        
        # Calculate remaining uses based on current durability
        decay_params = self.business_service.UTILIZATION_DECAY_RATES.get(quality_tier, 
                                                                        self.business_service.UTILIZATION_DECAY_RATES['basic'])
        remaining_uses = int(current_durability / decay_params['base_decay_per_use'])
        remaining_days = remaining_uses / projected_daily_uses if projected_daily_uses > 0 else 0
        
        # Determine risk level
        risk_level = "low"
        if remaining_days <= 1:
            risk_level = "critical"
        elif remaining_days <= 3:
            risk_level = "high"
        elif remaining_days <= 7:
            risk_level = "medium"
        
        return {
            'equipment_id': equipment_id,
            'current_durability': current_durability,
            'quality_tier': quality_tier,
            'estimated_remaining_uses': remaining_uses,
            'estimated_remaining_days': round(remaining_days, 1),
            'risk_level': risk_level,
            'projected_daily_uses': projected_daily_uses,
            'historical_usage': stats,
            'lifespan_info': lifespan_info
        }
    
    def _map_event_to_usage_type(self, event_type: UsageEventType) -> str:
        """Map usage event types to business logic usage types"""
        mapping = {
            UsageEventType.WEAPON_ATTACK: 'normal_use',
            UsageEventType.WEAPON_PARRY: 'parrying',
            UsageEventType.ARMOR_HIT: 'normal_use',
            UsageEventType.SHIELD_BLOCK: 'blocking',
            UsageEventType.TOOL_USE: 'normal_use',
            UsageEventType.ENVIRONMENTAL_EXPOSURE: 'environmental',
            UsageEventType.CRITICAL_EVENT: 'critical_hit',
            UsageEventType.REPAIR_EVENT: 'light_use'  # Repair events are gentle
        }
        return mapping.get(event_type, 'normal_use')
    
    def _update_equipment_stats(self, equipment_id: str, event: UsageEvent):
        """Update internal usage statistics for equipment"""
        if equipment_id not in self.equipment_usage_stats:
            self.equipment_usage_stats[equipment_id] = {
                'total_uses': 0,
                'critical_uses': 0,
                'event_type_counts': {},
                'first_use': event.timestamp,
                'last_use': event.timestamp,
                'total_intensity': 0.0
            }
        
        stats = self.equipment_usage_stats[equipment_id]
        stats['total_uses'] += 1
        stats['last_use'] = event.timestamp
        stats['total_intensity'] += event.usage_intensity
        
        if event.is_critical:
            stats['critical_uses'] += 1
        
        event_type = event.event_type.value
        stats['event_type_counts'][event_type] = stats['event_type_counts'].get(event_type, 0) + 1
        
        # Calculate average intensity
        stats['average_intensity'] = stats['total_intensity'] / stats['total_uses'] 