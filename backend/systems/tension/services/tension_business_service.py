"""
Tension System Business Logic Service

Pure business logic for tension calculations, conflict triggers, and revolt mechanics
according to the Development Bible standards.
"""

from typing import Dict, List, Optional, Any, Tuple, Protocol, Union
from datetime import datetime, timedelta
from uuid import uuid4

# Import domain models from proper location
from backend.systems.tension.models.tension_state import (
    TensionModifier,
    TensionState,
    FactionRelationship,
    ConflictTrigger,
    TensionConfig,
    FactionTensionConfig,
    RevoltConfig,
    CalculationConstants
)
from backend.systems.tension.models.tension_events import TensionEvent, TensionEventType


# Business Logic Protocols (dependency injection)
class TensionConfigRepository(Protocol):
    """Protocol for tension configuration data access"""
    
    def get_location_config(self, region_id: str, poi_id: str) -> TensionConfig:
        """Get configuration for a specific location"""
        ...
    
    def get_event_impact_config(self, event_type: str) -> Dict[str, Any]:
        """Get impact configuration for an event type"""
        ...
    
    def get_revolt_config(self) -> RevoltConfig:
        """Get revolt configuration"""
        ...
    
    def get_conflict_triggers(self) -> List[ConflictTrigger]:
        """Get conflict trigger configurations"""
        ...
    
    def get_calculation_constants(self) -> CalculationConstants:
        """Get calculation constants"""
        ...


class TensionRepository(Protocol):
    """Protocol for tension state data access"""
    
    def get_tension_state(self, region_id: str, poi_id: str) -> Optional[TensionState]:
        """Get current tension state for a location"""
        ...
    
    def save_tension_state(self, region_id: str, poi_id: str, state: TensionState) -> None:
        """Save tension state for a location"""
        ...
    
    def get_all_tension_states(self) -> Dict[str, Dict[str, TensionState]]:
        """Get all tension states"""
        ...


class FactionService(Protocol):
    """Protocol for faction system integration"""
    
    def get_factions_in_region(self, region_id: str) -> List[Dict[str, Any]]:
        """Get factions present in a region"""
        ...


class EventDispatcher(Protocol):
    """Protocol for event system integration"""
    
    def dispatch_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Dispatch an event to other systems"""
        ...


class FactionRelationshipRepository(Protocol):
    """Protocol for faction relationship data access"""
    
    def get_faction_relationship(self, faction_a_id: str, faction_b_id: str) -> Optional[FactionRelationship]:
        """Get relationship between two factions"""
        ...
    
    def save_faction_relationship(self, relationship: FactionRelationship) -> None:
        """Save faction relationship"""
        ...
    
    def get_all_faction_relationships(self) -> List[FactionRelationship]:
        """Get all faction relationships"""
        ...
    
    def get_faction_relationships_for_faction(self, faction_id: str) -> List[FactionRelationship]:
        """Get all relationships involving a specific faction"""
        ...
    
    def get_relationships_above_threshold(self, threshold: int) -> List[FactionRelationship]:
        """Get relationships above specified tension threshold (for war detection)"""
        ...
    
    def get_relationships_below_threshold(self, threshold: int) -> List[FactionRelationship]:
        """Get relationships below specified tension threshold (for alliance detection)"""
        ...


class TensionBusinessService:
    """Service class for tension business logic - pure business rules"""
    
    def __init__(self, 
                 config_repository: TensionConfigRepository,
                 tension_repository: TensionRepository,
                 faction_relationship_repository: Optional[FactionRelationshipRepository] = None,
                 faction_service: Optional[FactionService] = None,
                 event_dispatcher: Optional[EventDispatcher] = None):
        self.config_repository = config_repository
        self.tension_repository = tension_repository
        self.faction_relationship_repository = faction_relationship_repository
        self.faction_service = faction_service
        self.event_dispatcher = event_dispatcher
        
        # Statistics and monitoring
        self.stats = {
            'total_tension_updates': 0,
            'total_faction_updates': 0,
            'conflicts_triggered': 0,
            'wars_triggered': 0,
            'alliances_formed': 0,
            'revolts_triggered': 0,
            'modifiers_expired': 0,
            'last_global_update': datetime.utcnow(),
            'last_modifier_cleanup': datetime.utcnow()
        }

    def calculate_tension(
        self,
        region_id: str,
        poi_id: str,
        current_time: Optional[datetime] = None
    ) -> float:
        """
        Calculate current tension for a location with proper decay and modifiers.
        Pure business logic - no I/O operations.
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Get or initialize tension state
        state = self.tension_repository.get_tension_state(region_id, poi_id)
        if state is None:
            state = self._initialize_tension_state(region_id, poi_id, current_time)
        
        # Get location configuration
        config = self.config_repository.get_location_config(region_id, poi_id)
        
        # Calculate time-based decay
        time_delta = current_time - state.last_updated
        decay_amount = self._calculate_decay(time_delta, config.decay_rate)
        
        # Apply decay
        decayed_tension = max(config.min_tension, state.current_level - decay_amount)
        
        # Apply active modifiers
        modified_tension = self._apply_tension_modifiers(decayed_tension, state.modifiers)
        
        # Clamp to valid range
        final_tension = max(config.min_tension, min(config.max_tension, modified_tension))
        
        # Update state
        state.current_level = final_tension
        state.last_updated = current_time
        
        # Clean up expired modifiers
        self._clean_expired_modifiers(state, current_time)
        
        # Save updated state
        self.tension_repository.save_tension_state(region_id, poi_id, state)
        
        self.stats['total_tension_updates'] += 1
        
        return final_tension

    def update_tension_from_event(
        self,
        region_id: str,
        poi_id: str,
        event_type: Union[TensionEventType, str],
        event_data: Dict[str, Any],
        current_time: Optional[datetime] = None
    ) -> float:
        """
        Update tension based on a specific event.
        Pure business logic implementation.
        
        Args:
            event_type: Can be TensionEventType enum or string
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Handle string to enum conversion for external compatibility
        if isinstance(event_type, str):
            try:
                # Try to convert string to enum
                event_type = TensionEventType(event_type.lower())
            except (ValueError, AttributeError):
                # If conversion fails, create a generic event type
                event_type = TensionEventType.PLAYER_COMBAT  # Default fallback
        
        # Calculate base tension first
        current_tension = self.calculate_tension(region_id, poi_id, current_time)
        
        # Calculate impact based on event type
        impact = self._calculate_event_impact(region_id, poi_id, event_type, event_data)
        
        # Apply the tension change
        self._apply_tension_change(region_id, poi_id, impact, current_time)
        
        # Record the event (fix: remove impact parameter that doesn't exist)
        tension_event = TensionEvent(
            event_type=event_type,
            region_id=region_id,
            poi_id=poi_id,
            timestamp=current_time,
            data=event_data,
            event_id=str(uuid4())
        )
        self._record_tension_event(region_id, poi_id, tension_event)
        
        # Return new tension level
        return self.calculate_tension(region_id, poi_id, current_time)

    def check_conflict_triggers(
        self,
        region_id: str,
        current_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Check if any conflict triggers are activated for a region.
        Pure business logic - evaluates conditions based on current state.
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        triggered_conflicts = []
        
        # Get region summary
        region_summary = self._get_region_tension_summary(region_id, current_time)
        
        # Check each conflict trigger
        conflict_triggers = self.config_repository.get_conflict_triggers()
        for trigger in conflict_triggers:
            if self._evaluate_conflict_trigger(region_id, trigger, region_summary, current_time):
                conflict_data = self._create_conflict(region_id, trigger, current_time)
                triggered_conflicts.append(conflict_data)
                self.stats['conflicts_triggered'] += 1
        
        return triggered_conflicts

    def simulate_revolt(
        self,
        region_id: str,
        poi_id: str,
        factions_present: List[Dict],
        tension_level: float,
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Simulate a potential revolt based on tension and faction dynamics.
        Pure business logic - no external calls.
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Calculate revolt probability
        revolt_probability = self._calculate_revolt_probability(tension_level, factions_present)
        
        # Determine if revolt occurs
        revolt_occurs = self._roll_for_revolt(revolt_probability)
        
        if revolt_occurs:
            revolt_data = self._execute_revolt(region_id, poi_id, factions_present, tension_level, current_time)
            self.stats['revolts_triggered'] += 1
            return revolt_data
        else:
            return {
                'revolt_occurred': False,
                'probability': revolt_probability,
                'tension_level': tension_level,
                'timestamp': current_time
            }

    def get_regions_by_tension(
        self,
        min_tension: float = 0.0,
        max_tension: float = 1.0,
        current_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get regions filtered by tension level range.
        Pure business logic - processes existing state data.
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        matching_regions = []
        all_states = self.tension_repository.get_all_tension_states()
        
        for region_id, poi_states in all_states.items():
            region_tensions = []
            for poi_id, state in poi_states.items():
                # Calculate current tension for this POI
                current_tension = self.calculate_tension(region_id, poi_id, current_time)
                if min_tension <= current_tension <= max_tension:
                    region_tensions.append({
                        'poi_id': poi_id,
                        'tension': current_tension,
                        'last_updated': state.last_updated
                    })
            
            if region_tensions:
                avg_tension = sum(poi['tension'] for poi in region_tensions) / len(region_tensions)
                matching_regions.append({
                    'region_id': region_id,
                    'average_tension': avg_tension,
                    'poi_count': len(region_tensions),
                    'pois': region_tensions
                })
        
        # Sort by average tension (highest first)
        matching_regions.sort(key=lambda x: x['average_tension'], reverse=True)
        return matching_regions

    def decay_all_tension(self, current_time: Optional[datetime] = None) -> Dict[str, int]:
        """
        Apply decay to all tension states globally.
        Pure business logic - processes all states.
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        decay_stats = {
            'regions_processed': 0,
            'pois_processed': 0,
            'modifiers_expired': 0
        }
        
        all_states = self.tension_repository.get_all_tension_states()
        
        for region_id, poi_states in all_states.items():
            decay_stats['regions_processed'] += 1
            for poi_id in poi_states.keys():
                # Calculate tension (which applies decay and saves state)
                self.calculate_tension(region_id, poi_id, current_time)
                decay_stats['pois_processed'] += 1
        
        self.stats['last_global_update'] = current_time
        return decay_stats

    def add_tension_modifier(
        self, 
        region_id: str, 
        poi_id: str, 
        modifier_type: str, 
        value: float, 
        duration_hours: float,
        source: str = "unknown"
    ) -> None:
        """
        Add a temporary tension modifier.
        Pure business logic - modifies state data.
        """
        current_time = datetime.utcnow()
        expiration_time = current_time + timedelta(hours=duration_hours)
        
        modifier = TensionModifier(
            modifier_type=modifier_type,
            value=value,
            expiration_time=expiration_time,
            source=source
        )
        
        # Get or create tension state
        state = self.tension_repository.get_tension_state(region_id, poi_id)
        if state is None:
            state = self._initialize_tension_state(region_id, poi_id, current_time)
        
        # Add modifier
        state.modifiers[modifier_type] = modifier
        
        # Save updated state
        self.tension_repository.save_tension_state(region_id, poi_id, state)

    def calculate_faction_power_score(self, faction_data: Dict[str, Any]) -> float:
        """Business logic: Calculate overall power score for a faction"""
        # Business rule: Power is combination of hidden attributes
        attributes = faction_data.get('hidden_attributes', {})
        
        # Default values if attributes are missing
        ambition = attributes.get('hidden_ambition', 5)
        discipline = attributes.get('hidden_discipline', 5) 
        pragmatism = attributes.get('hidden_pragmatism', 5)
        resilience = attributes.get('hidden_resilience', 5)
        integrity = attributes.get('hidden_integrity', 5)
        impulsivity = attributes.get('hidden_impulsivity', 5)
        
        # Weighted scoring based on faction attributes
        power_score = (
            ambition * 0.25 +           # Drive to expand
            discipline * 0.2 +          # Organization effectiveness
            pragmatism * 0.2 +          # Strategic flexibility
            resilience * 0.2 +          # Ability to withstand setbacks
            integrity * 0.1 +           # Internal stability
            (10 - impulsivity) * 0.05   # Strategic patience
        )
        
        return round(power_score, 2)

    def get_faction_relationship(
        self,
        faction_a_id: str,
        faction_b_id: str,
        current_time: Optional[datetime] = None
    ) -> Optional[FactionRelationship]:
        """Get current faction relationship with decay applied"""
        if not self.faction_relationship_repository:
            return None
        
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Normalize faction IDs (always put lexicographically smaller ID first)
        if faction_a_id > faction_b_id:
            faction_a_id, faction_b_id = faction_b_id, faction_a_id
        
        relationship = self.faction_relationship_repository.get_faction_relationship(faction_a_id, faction_b_id)
        if not relationship:
            return None
        
        # Apply decay towards neutral (0)
        self._apply_faction_tension_decay(relationship, current_time)
        
        return relationship

    def update_faction_tension(
        self,
        faction_a_id: str,
        faction_b_id: str,
        tension_change: int,
        source: str = "unknown",
        current_time: Optional[datetime] = None
    ) -> FactionRelationship:
        """Update tension between two factions (Development Bible: -100 to +100 scale)"""
        if not self.faction_relationship_repository:
            raise ValueError("Faction relationship repository not available")
        
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Normalize faction IDs
        if faction_a_id > faction_b_id:
            faction_a_id, faction_b_id = faction_b_id, faction_a_id
        
        # Get or create relationship
        relationship = self.faction_relationship_repository.get_faction_relationship(faction_a_id, faction_b_id)
        if not relationship:
            relationship = self._create_initial_faction_relationship(faction_a_id, faction_b_id, current_time)
        
        # Apply decay first
        self._apply_faction_tension_decay(relationship, current_time)
        
        # Apply tension change
        old_tension = relationship.tension_level
        new_tension = max(-100, min(100, relationship.tension_level + tension_change))
        relationship.tension_level = new_tension
        relationship.last_updated = current_time
        
        # Update relationship type based on new tension
        relationship.relationship_type = self._determine_relationship_type(new_tension)
        
        # Record the event
        event_id = str(uuid4())
        relationship.recent_events.append(f"{current_time.isoformat()}:{source}:{tension_change}")
        
        # Keep only recent events (last 24 hours)
        cutoff_time = current_time - timedelta(hours=24)
        relationship.recent_events = [
            event for event in relationship.recent_events 
            if datetime.fromisoformat(event.split(':')[0]) > cutoff_time
        ]
        
        # Save relationship
        self.faction_relationship_repository.save_faction_relationship(relationship)
        
        # Check for war triggers or alliance formation
        self._check_faction_relationship_triggers(relationship, old_tension, current_time)
        
        self.stats['total_faction_updates'] += 1
        
        return relationship

    def check_war_status(self, faction_a_id: str, faction_b_id: str) -> bool:
        """Check if two factions are at war (Development Bible: war at 70+ tension)"""
        relationship = self.get_faction_relationship(faction_a_id, faction_b_id)
        if not relationship:
            return False
        
        return relationship.tension_level >= relationship.war_threshold

    def get_faction_wars(self) -> List[FactionRelationship]:
        """Get all faction relationships currently at war"""
        if not self.faction_relationship_repository:
            return []
        
        constants = self.config_repository.get_calculation_constants()
        war_threshold = constants.faction_tension_limits.get('war_threshold', 70)
        
        return self.faction_relationship_repository.get_relationships_above_threshold(war_threshold)

    def get_faction_alliances(self) -> List[FactionRelationship]:
        """Get all faction relationships that are alliances (negative tension)"""
        if not self.faction_relationship_repository:
            return []
        
        constants = self.config_repository.get_calculation_constants()
        alliance_threshold = constants.faction_tension_limits.get('alliance_threshold', -50)
        
        return self.faction_relationship_repository.get_relationships_below_threshold(alliance_threshold)

    def decay_all_faction_tension(self, current_time: Optional[datetime] = None) -> Dict[str, int]:
        """Apply daily decay to all faction relationships towards neutral"""
        if not self.faction_relationship_repository:
            return {'processed': 0, 'decayed': 0}
        
        if current_time is None:
            current_time = datetime.utcnow()
        
        relationships = self.faction_relationship_repository.get_all_faction_relationships()
        processed = 0
        decayed = 0
        
        for relationship in relationships:
            old_tension = relationship.tension_level
            self._apply_faction_tension_decay(relationship, current_time)
            
            if relationship.tension_level != old_tension:
                self.faction_relationship_repository.save_faction_relationship(relationship)
                decayed += 1
            
            processed += 1
        
        return {'processed': processed, 'decayed': decayed}

    def _create_initial_faction_relationship(
        self, 
        faction_a_id: str, 
        faction_b_id: str, 
        current_time: datetime
    ) -> FactionRelationship:
        """Create initial neutral faction relationship"""
        return FactionRelationship(
            faction_a_id=faction_a_id,
            faction_b_id=faction_b_id,
            tension_level=0,  # Start neutral
            last_updated=current_time,
            relationship_type='neutral',
            recent_events=[],
            modifiers={}
        )

    def _apply_faction_tension_decay(
        self, 
        relationship: FactionRelationship, 
        current_time: datetime
    ) -> None:
        """Apply natural decay towards neutral (0) for faction relationships"""
        constants = self.config_repository.get_calculation_constants()
        decay_config = constants.faction_tension_decay
        
        # Calculate time since last update
        time_delta = current_time - relationship.last_updated
        days_passed = time_delta.total_seconds() / (24 * 3600)
        
        if days_passed < 1.0:
            return  # Don't decay if less than a day has passed
        
        # Calculate decay amount
        base_decay = decay_config.get('base_decay_rate', 1)
        daily_decay = int(days_passed * base_decay)
        
        if daily_decay == 0:
            return
        
        # Apply decay towards neutral (0)
        old_tension = relationship.tension_level
        if relationship.tension_level > 0:
            # Positive tension decays towards 0
            relationship.tension_level = max(0, relationship.tension_level - daily_decay)
        elif relationship.tension_level < 0:
            # Negative tension (alliances) decay towards 0 but slower
            alliance_decay_slower = decay_config.get('alliance_decay_slower', True)
            if alliance_decay_slower:
                daily_decay = max(1, daily_decay // 2)  # Alliances decay half as fast
            relationship.tension_level = min(0, relationship.tension_level + daily_decay)
        
        # Update relationship type if tension changed significantly
        if abs(old_tension - relationship.tension_level) >= 5:
            relationship.relationship_type = self._determine_relationship_type(relationship.tension_level)
        
        relationship.last_updated = current_time

    def _determine_relationship_type(self, tension_level: int) -> str:
        """Determine relationship type based on tension level"""
        if tension_level >= 70:
            return 'war'
        elif tension_level >= 30:
            return 'hostile'
        elif tension_level >= -30:
            return 'neutral'
        elif tension_level >= -60:
            return 'friendly'
        else:
            return 'alliance'

    def _check_faction_relationship_triggers(
        self,
        relationship: FactionRelationship,
        old_tension: int,
        current_time: datetime
    ) -> None:
        """Check if relationship changes trigger wars, alliances, or other events"""
        new_tension = relationship.tension_level
        
        # War trigger check (Development Bible: war at 70+ tension)
        if old_tension < 70 and new_tension >= 70:
            self._trigger_war(relationship, current_time)
        
        # Alliance formation check (strong negative tension)
        elif old_tension > -50 and new_tension <= -50:
            self._trigger_alliance_formation(relationship, current_time)
        
        # Peace opportunity check (tension dropping below war threshold)
        elif old_tension >= 70 and new_tension < 70:
            self._check_peace_opportunity(relationship, current_time)

    def _trigger_war(self, relationship: FactionRelationship, current_time: datetime) -> None:
        """Trigger war between factions"""
        if self.event_dispatcher:
            war_event = {
                'event_type': 'faction_war_declared',
                'faction_a_id': relationship.faction_a_id,
                'faction_b_id': relationship.faction_b_id,
                'tension_level': relationship.tension_level,
                'timestamp': current_time.isoformat()
            }
            self.event_dispatcher.dispatch_event('faction_war_declared', war_event)
        
        self.stats['wars_triggered'] += 1

    def _trigger_alliance_formation(self, relationship: FactionRelationship, current_time: datetime) -> None:
        """Trigger alliance formation between factions"""
        if self.event_dispatcher:
            alliance_event = {
                'event_type': 'faction_alliance_formed',
                'faction_a_id': relationship.faction_a_id,
                'faction_b_id': relationship.faction_b_id,
                'tension_level': relationship.tension_level,
                'timestamp': current_time.isoformat()
            }
            self.event_dispatcher.dispatch_event('faction_alliance_formed', alliance_event)
        
        self.stats['alliances_formed'] += 1

    def _check_peace_opportunity(self, relationship: FactionRelationship, current_time: datetime) -> None:
        """Check if factions might make peace"""
        if self.event_dispatcher:
            peace_event = {
                'event_type': 'faction_peace_opportunity',
                'faction_a_id': relationship.faction_a_id,
                'faction_b_id': relationship.faction_b_id,
                'tension_level': relationship.tension_level,
                'timestamp': current_time.isoformat()
            }
            self.event_dispatcher.dispatch_event('faction_peace_opportunity', peace_event)

    # Private helper methods for business logic
    def _initialize_tension_state(self, region_id: str, poi_id: str, current_time: datetime) -> TensionState:
        """Initialize a new tension state for a location."""
        config = self.config_repository.get_location_config(region_id, poi_id)
        
        state = TensionState(
            current_level=config.base_tension,
            base_level=config.base_tension,
            last_updated=current_time,
            recent_events=[],
            modifiers={}
        )
        
        self.tension_repository.save_tension_state(region_id, poi_id, state)
        return state

    def _calculate_decay(self, time_delta: timedelta, decay_rate: float) -> float:
        """Calculate decay amount based on time elapsed and decay rate."""
        return time_delta.total_seconds() / 3600.0 * decay_rate

    def _apply_tension_modifiers(self, base_tension: float, modifiers: Dict[str, TensionModifier]) -> float:
        """Apply active modifiers to base tension."""
        modified_tension = base_tension
        
        for modifier in modifiers.values():
            # Apply modifier value
            modified_tension += modifier.value
        
        return modified_tension

    def _clean_expired_modifiers(self, state: TensionState, current_time: datetime) -> None:
        """Remove expired modifiers from tension state."""
        expired_modifiers = []
        
        for modifier_type, modifier in state.modifiers.items():
            if modifier.expiration_time <= current_time:
                expired_modifiers.append(modifier_type)
        
        for modifier_type in expired_modifiers:
            del state.modifiers[modifier_type]
            self.stats['modifiers_expired'] += 1

    def _calculate_event_impact(
        self,
        region_id: str,
        poi_id: str,
        event_type: TensionEventType,
        event_data: Dict[str, Any]
    ) -> float:
        """Calculate the tension impact of a specific event."""
        impact_config = self.config_repository.get_event_impact_config(event_type.value)
        base_impact = impact_config.get('base_impact', 0.1)
        
        # Apply event-specific modifiers
        impact = base_impact
        
        if event_type == TensionEventType.PLAYER_COMBAT:
            if event_data.get('lethal', False):
                impact *= impact_config.get('lethal_modifier', 1.5)
            if event_data.get('stealth', False):
                impact *= impact_config.get('stealth_modifier', 0.5)
            enemies_defeated = event_data.get('enemies_defeated', 1)
            impact *= min(2.0, 1.0 + (enemies_defeated - 1) * 0.2)
        
        elif event_type == TensionEventType.NPC_DEATH:
            if event_data.get('important', False):
                impact *= 2.0
            if event_data.get('civilian', True):
                impact *= 1.5
        
        elif event_type == TensionEventType.FESTIVAL:
            # Festivals reduce tension
            success_level = event_data.get('success_level', 1.0)
            impact = -abs(base_impact) * success_level
        
        # Add more event type specific logic as needed
        
        return impact

    def _apply_tension_change(self, region_id: str, poi_id: str, change: float, current_time: datetime) -> None:
        """Apply a tension change to a location."""
        state = self.tension_repository.get_tension_state(region_id, poi_id)
        if state is None:
            state = self._initialize_tension_state(region_id, poi_id, current_time)
        
        # Apply change
        state.current_level += change
        
        # Get bounds from config
        config = self.config_repository.get_location_config(region_id, poi_id)
        state.current_level = max(config.min_tension, min(config.max_tension, state.current_level))
        
        # Update timestamp
        state.last_updated = current_time
        
        # Save state
        self.tension_repository.save_tension_state(region_id, poi_id, state)

    def _record_tension_event(self, region_id: str, poi_id: str, event: TensionEvent) -> None:
        """Record a tension event in the location's history."""
        state = self.tension_repository.get_tension_state(region_id, poi_id)
        if state is not None:
            # Add to recent events (keep last 10)
            state.recent_events.append(event.event_id)
            if len(state.recent_events) > 10:
                state.recent_events = state.recent_events[-10:]
            
            # Save state
            self.tension_repository.save_tension_state(region_id, poi_id, state)

    def _get_region_tension_summary(self, region_id: str, current_time: datetime) -> Dict[str, Any]:
        """Get summary of tension levels across all POIs in a region."""
        all_states = self.tension_repository.get_all_tension_states()
        region_states = all_states.get(region_id, {})
        
        if not region_states:
            return {
                'region_id': region_id,
                'poi_count': 0,
                'average_tension': 0.0,
                'max_tension': 0.0,
                'high_tension_pois': []
            }
        
        tensions = []
        high_tension_pois = []
        
        for poi_id in region_states.keys():
            tension = self.calculate_tension(region_id, poi_id, current_time)
            tensions.append(tension)
            
            if tension >= 0.7:  # High tension threshold
                high_tension_pois.append({
                    'poi_id': poi_id,
                    'tension': tension
                })
        
        return {
            'region_id': region_id,
            'poi_count': len(region_states),
            'average_tension': sum(tensions) / len(tensions) if tensions else 0.0,
            'max_tension': max(tensions) if tensions else 0.0,
            'high_tension_pois': high_tension_pois
        }

    def _evaluate_conflict_trigger(
        self,
        region_id: str,
        trigger: ConflictTrigger,
        region_summary: Dict[str, Any],
        current_time: datetime
    ) -> bool:
        """Evaluate if a conflict trigger should activate."""
        # Check if max tension exceeds threshold
        if region_summary['max_tension'] < trigger.tension_threshold:
            return False
        
        # Check faction requirements if faction service is available
        if self.faction_service and trigger.faction_requirements:
            try:
                factions = self.faction_service.get_factions_in_region(region_id)
                
                # Handle different types of faction requirements
                for requirement_key, requirement_value in trigger.faction_requirements.items():
                    if requirement_key == 'min_factions':
                        # Minimum number of factions required
                        if len(factions) < requirement_value:
                            return False
                    elif requirement_key == 'power_imbalance':
                        # Check for power imbalance between factions
                        if len(factions) < 2:
                            return False
                        power_scores = [self.calculate_faction_power_score(f) for f in factions]
                        max_power = max(power_scores)
                        min_power = min(power_scores)
                        if max_power - min_power < requirement_value * 10:  # Scale to 0-10 range
                            return False
                    else:
                        # Specific faction ID with required strength
                        faction_present = any(f.get('id') == requirement_key for f in factions)
                        if not faction_present:
                            return False
                        
                        faction_data = next((f for f in factions if f.get('id') == requirement_key), {})
                        faction_strength = self.calculate_faction_power_score(faction_data)
                        if faction_strength < requirement_value:
                            return False
            except Exception:
                # If faction service fails, ignore faction requirements
                pass
        
        return True

    def _create_conflict(self, region_id: str, trigger: ConflictTrigger, current_time: datetime) -> Dict[str, Any]:
        """Create conflict data when a trigger activates."""
        return {
            'trigger_name': trigger.name,
            'triggered': True,  # Fix: Add missing 'triggered' field
            'region_id': region_id,
            'tension_threshold': trigger.tension_threshold,
            'duration_hours': trigger.duration_hours,
            'probability_modifier': trigger.probability_modifier,
            'start_time': current_time.isoformat(),
            'estimated_end': (current_time + timedelta(hours=trigger.duration_hours)).isoformat()
        }

    def _calculate_revolt_probability(self, tension_level: float, factions: List[Dict]) -> float:
        """Calculate probability of revolt based on tension and faction dynamics."""
        revolt_config = self.config_repository.get_revolt_config()
        
        base_probability = tension_level * revolt_config.base_probability_threshold
        
        # Factor in faction influence
        faction_modifier = len(factions) * revolt_config.faction_influence_modifier
        
        total_probability = min(1.0, base_probability + faction_modifier)
        return total_probability

    def _roll_for_revolt(self, probability: float) -> bool:
        """Determine if revolt occurs based on probability."""
        import random
        return random.random() < probability

    def _execute_revolt(
        self,
        region_id: str,
        poi_id: str,
        factions: List[Dict],
        tension_level: float,
        current_time: datetime
    ) -> Dict[str, Any]:
        """Execute revolt logic and return results."""
        revolt_config = self.config_repository.get_revolt_config()
        
        # Calculate duration
        min_duration, max_duration = revolt_config.duration_range_hours
        import random
        duration_hours = random.randint(min_duration, max_duration)
        
        # Calculate casualties
        casualties = self._calculate_revolt_casualties(tension_level, len(factions))
        
        # Create revolt data
        revolt_data = {
            'revolt_occurred': True,
            'region_id': region_id,
            'poi_id': poi_id,
            'start_time': current_time.isoformat(),
            'duration_hours': duration_hours,
            'estimated_end': (current_time + timedelta(hours=duration_hours)).isoformat(),
            'participating_factions': [f.get('id', 'unknown') for f in factions],
            'casualties': casualties,
            'tension_at_start': tension_level
        }
        
        # Apply revolt consequences
        self._apply_revolt_consequences(region_id, poi_id, revolt_data, current_time)
        
        return revolt_data

    def _calculate_revolt_casualties(self, tension_level: float, faction_count: int) -> Dict[str, int]:
        """Calculate revolt casualties based on tension and participants."""
        revolt_config = self.config_repository.get_revolt_config()
        
        base_casualties = int(tension_level * 10 * faction_count)
        multiplied_casualties = int(base_casualties * revolt_config.casualty_multiplier)
        
        return {
            'civilian': max(1, multiplied_casualties // 2),
            'faction_members': max(0, multiplied_casualties // 4),
            'authorities': max(0, multiplied_casualties // 8)
        }

    def _apply_revolt_consequences(
        self,
        region_id: str,
        poi_id: str,
        revolt_data: Dict[str, Any],
        current_time: datetime
    ) -> None:
        """Apply consequences of revolt to tension state."""
        # Temporarily reduce tension due to venting of frustrations
        tension_reduction = 0.3  # Significant reduction after revolt
        
        self.add_tension_modifier(
            region_id=region_id,
            poi_id=poi_id,
            modifier_type="post_revolt_relief",
            value=-tension_reduction,
            duration_hours=72,  # 3 days of reduced tension
            source=f"Revolt aftermath: {revolt_data.get('start_time', 'unknown')}"
        )
        
        # Dispatch revolt event if event dispatcher available
        if self.event_dispatcher:
            self.event_dispatcher.dispatch_event('revolt_occurred', revolt_data)


def create_tension_business_service(
    config_repository: TensionConfigRepository,
    tension_repository: TensionRepository,
    faction_relationship_repository: Optional[FactionRelationshipRepository] = None,
    faction_service: Optional[FactionService] = None,
    event_dispatcher: Optional[EventDispatcher] = None
) -> TensionBusinessService:
    """Factory function for creating tension business service with injected dependencies."""
    return TensionBusinessService(
        config_repository=config_repository,
        tension_repository=tension_repository,
        faction_relationship_repository=faction_relationship_repository,
        faction_service=faction_service,
        event_dispatcher=event_dispatcher
    ) 