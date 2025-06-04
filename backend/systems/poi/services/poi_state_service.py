"""
POI State Service - Pure Business Logic

Manages the state transitions and lifecycle of Points of Interest,
including population changes, economic shifts, and environmental factors.
Pure business logic without technical dependencies.
"""

from typing import Dict, List, Optional, Any, Tuple, Set, Protocol
from uuid import UUID
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field


# Business Domain Enums
class POIState(str, Enum):
    """POI lifecycle states"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ABANDONED = "abandoned"
    RUINED = "ruined"
    UNDER_CONSTRUCTION = "under_construction"
    DECLINING = "declining"
    GROWING = "growing"
    NORMAL = "normal"
    RUINS = "ruins"
    DUNGEON = "dungeon"
    REPOPULATING = "repopulating"
    SPECIAL = "special"


class POIType(str, Enum):
    """Types of POIs"""
    CITY = "city"
    VILLAGE = "village"
    TOWN = "town"
    SETTLEMENT = "settlement"
    OUTPOST = "outpost"
    FORTRESS = "fortress"
    TEMPLE = "temple"
    MARKET = "market"
    MINE = "mine"
    OTHER = "other"


# Business Domain Models
@dataclass
class StateTransitionRule:
    """Defines rules for state transitions"""
    from_state: POIState
    to_state: POIState
    required_conditions: List[str]
    population_threshold: Optional[Tuple[int, int]] = None  # (min, max)
    time_requirement: Optional[timedelta] = None
    faction_required: bool = False
    resources_required: Optional[Dict[str, int]] = None


@dataclass
class StateTransitionEvent:
    """Event data for state transitions"""
    poi_id: UUID
    from_state: POIState
    to_state: POIState
    timestamp: datetime
    reason: str
    metadata: Dict[str, Any]


@dataclass
class POIStateData:
    """Business domain POI state data"""
    id: UUID
    current_state: POIState
    poi_type: POIType
    population: int
    max_population: int
    resources: Dict[str, int]
    faction_control: Optional[UUID]
    last_state_change: datetime
    properties: Dict[str, Any]


# Business Logic Protocols (dependency injection)
class POIRepository(Protocol):
    """Protocol for POI data access"""
    
    def get_poi_by_id(self, poi_id: UUID) -> Optional[POIStateData]:
        """Get POI state data by ID"""
        ...
    
    def update_poi_state(self, poi_data: POIStateData) -> POIStateData:
        """Update POI state"""
        ...
    
    def get_pois_by_state(self, state: POIState) -> List[POIStateData]:
        """Get POIs by state"""
        ...


class StateTransitionConfigService(Protocol):
    """Protocol for state transition configuration"""
    
    def get_transition_rules(self) -> Dict[str, Any]:
        """Get state transition rules"""
        ...
    
    def get_condition_definitions(self) -> Dict[str, Any]:
        """Get condition definitions"""
        ...
    
    def get_poi_type_modifiers(self) -> Dict[str, Any]:
        """Get POI type modifiers"""
        ...


class EventDispatcher(Protocol):
    """Protocol for event dispatching"""
    
    def dispatch_event(self, event: StateTransitionEvent):
        """Dispatch state transition event"""
        ...


class StateTransitionValidator:
    """Validates state transitions based on rules and constraints - Pure Business Logic"""
    
    def __init__(self, config_service: StateTransitionConfigService):
        self.config_service = config_service
        self.transition_rules = self._initialize_transition_rules()
    
    def _initialize_transition_rules(self) -> Dict[Tuple[POIState, POIState], StateTransitionRule]:
        """Initialize state transition rules from configuration"""
        rules = {}
        config_rules = self.config_service.get_transition_rules()
        
        # Convert configuration to business rules
        for rule_name, rule_config in config_rules.items():
            # Parse rule name to extract states
            if "_to_" in rule_name:
                from_state_str, to_state_str = rule_name.split("_to_")
                try:
                    from_state = POIState(from_state_str.lower())
                    to_state = POIState(to_state_str.lower())
                    
                    # Convert time requirement
                    time_req = None
                    if "time_requirement_days" in rule_config:
                        time_req = timedelta(days=rule_config["time_requirement_days"])
                    
                    # Convert population threshold
                    pop_threshold = None
                    if "population_threshold" in rule_config:
                        threshold_config = rule_config["population_threshold"]
                        min_pop = threshold_config.get("min")
                        max_pop = threshold_config.get("max")
                        pop_threshold = (min_pop, max_pop)
                    
                    rule = StateTransitionRule(
                        from_state=from_state,
                        to_state=to_state,
                        required_conditions=rule_config.get("required_conditions", []),
                        population_threshold=pop_threshold,
                        time_requirement=time_req,
                        faction_required=rule_config.get("faction_influence_required", False),
                        resources_required=rule_config.get("resource_threshold")
                    )
                    
                    rules[(from_state, to_state)] = rule
                    
                except ValueError:
                    # Skip invalid state names
                    continue
        
        return rules
    
    def validate_transition(
        self, 
        poi: POIStateData, 
        target_state: POIState,
        conditions: List[str],
        metadata: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate if a state transition is allowed"""
        errors = []
        
        # Check if transition rule exists
        rule_key = (poi.current_state, target_state)
        if rule_key not in self.transition_rules:
            errors.append(f"No transition rule from {poi.current_state} to {target_state}")
            return False, errors
        
        rule = self.transition_rules[rule_key]
        
        # Check required conditions
        missing_conditions = []
        for condition in rule.required_conditions:
            if condition not in conditions:
                missing_conditions.append(condition)
        
        if missing_conditions:
            errors.append(f"Missing required conditions: {missing_conditions}")
        
        # Check population threshold
        if rule.population_threshold:
            min_pop, max_pop = rule.population_threshold
            if min_pop is not None and poi.population < min_pop:
                errors.append(f"Population {poi.population} below minimum {min_pop}")
            if max_pop is not None and poi.population > max_pop:
                errors.append(f"Population {poi.population} above maximum {max_pop}")
        
        # Check faction requirement
        if rule.faction_required and not poi.faction_control:
            errors.append("Faction control required for this transition")
        
        # Check resource requirements
        if rule.resources_required:
            for resource, required_amount in rule.resources_required.items():
                current_amount = poi.resources.get(resource, 0)
                if current_amount < required_amount:
                    errors.append(f"Insufficient {resource}: {current_amount} < {required_amount}")
        
        # Check time requirement
        if rule.time_requirement:
            time_since_change = datetime.utcnow() - poi.last_state_change
            if time_since_change < rule.time_requirement:
                errors.append(f"Time requirement not met: {time_since_change} < {rule.time_requirement}")
        
        return len(errors) == 0, errors


class POIStateBusinessService:
    """Service class for POI state business logic - pure business rules"""
    
    def __init__(self, 
                 poi_repository: POIRepository,
                 config_service: StateTransitionConfigService,
                 event_dispatcher: Optional[EventDispatcher] = None):
        self.poi_repository = poi_repository
        self.config_service = config_service
        self.event_dispatcher = event_dispatcher
        self.validator = StateTransitionValidator(config_service)
        self.event_handlers: List[callable] = []

    def add_event_handler(self, handler: callable):
        """Add event handler for state transitions"""
        self.event_handlers.append(handler)

    def remove_event_handler(self, handler: callable):
        """Remove event handler"""
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)

    def _dispatch_event(self, event: StateTransitionEvent):
        """Dispatch state transition event"""
        # Notify registered handlers
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception:
                # Continue with other handlers even if one fails
                pass
        
        # Use external event dispatcher if available
        if self.event_dispatcher:
            self.event_dispatcher.dispatch_event(event)

    def transition_state(
        self,
        poi_id: UUID,
        target_state: POIState,
        reason: str,
        conditions: Optional[List[str]] = None,
        force: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Transition POI to a new state with business validation"""
        # Business rule: POI must exist
        poi = self.poi_repository.get_poi_by_id(poi_id)
        if not poi:
            raise ValueError(f"POI {poi_id} not found")
        
        # Business rule: No transition to same state
        if poi.current_state == target_state:
            return True  # Already in target state
        
        conditions = conditions or []
        metadata = metadata or {}
        
        # Business rule: Validate transition unless forced
        if not force:
            is_valid, errors = self.validator.validate_transition(poi, target_state, conditions, metadata)
            if not is_valid:
                raise ValueError(f"Invalid state transition: {'; '.join(errors)}")
        
        # Perform state transition
        old_state = poi.current_state
        poi.current_state = target_state
        poi.last_state_change = datetime.utcnow()
        
        # Update via repository
        updated_poi = self.poi_repository.update_poi_state(poi)
        
        # Create and dispatch event
        event = StateTransitionEvent(
            poi_id=poi_id,
            from_state=old_state,
            to_state=target_state,
            timestamp=datetime.utcnow(),
            reason=reason,
            metadata=metadata
        )
        
        self._dispatch_event(event)
        
        return True

    def evaluate_automatic_transitions(self, poi_id: UUID) -> List[StateTransitionEvent]:
        """Evaluate and execute automatic state transitions"""
        poi = self.poi_repository.get_poi_by_id(poi_id)
        if not poi:
            return []
        
        # Analyze current conditions
        conditions = self._analyze_poi_conditions(poi)
        
        # Get potential transitions
        potential_transitions = self._get_potential_transitions(poi.current_state, conditions)
        
        executed_transitions = []
        
        for target_state, reason in potential_transitions:
            try:
                # Attempt automatic transition
                if self.transition_state(poi_id, target_state, reason, conditions):
                    event = StateTransitionEvent(
                        poi_id=poi_id,
                        from_state=poi.current_state,
                        to_state=target_state,
                        timestamp=datetime.utcnow(),
                        reason=f"Automatic: {reason}",
                        metadata={"conditions": conditions, "automatic": True}
                    )
                    executed_transitions.append(event)
                    break  # Only one transition per evaluation
            except ValueError:
                # Transition not valid, continue to next
                continue
        
        return executed_transitions

    def _analyze_poi_conditions(self, poi: POIStateData) -> List[str]:
        """Analyze POI conditions to determine applicable state transition conditions"""
        conditions = []
        
        # Population-based conditions
        if poi.population == 0:
            conditions.append("zero_population")
        elif poi.population < poi.max_population * 0.3:
            conditions.append("critical_population")
        elif poi.population > poi.max_population * 0.9:
            conditions.append("population_increase")
        
        # Resource-based conditions
        total_resources = sum(poi.resources.values())
        if total_resources < 100:  # Arbitrary threshold
            conditions.append("resource_shortage")
        elif total_resources > 1000:
            conditions.append("resource_abundance")
        
        # Faction-based conditions
        if not poi.faction_control:
            conditions.append("no_faction_control")
        else:
            conditions.append("faction_investment")
        
        # Time-based conditions
        time_since_change = datetime.utcnow() - poi.last_state_change
        if time_since_change > timedelta(days=365):
            conditions.append("time_passage")
        
        return conditions

    def _get_potential_transitions(
        self, 
        current_state: POIState, 
        conditions: List[str]
    ) -> List[Tuple[POIState, str]]:
        """Get potential state transitions based on current conditions"""
        potential_transitions = []
        
        # Business rules for automatic transitions
        if current_state == POIState.ACTIVE:
            if "zero_population" in conditions:
                potential_transitions.append((POIState.ABANDONED, "Population reached zero"))
            elif "critical_population" in conditions and "resource_shortage" in conditions:
                potential_transitions.append((POIState.DECLINING, "Population and resource crisis"))
            elif "population_increase" in conditions and "resource_abundance" in conditions:
                potential_transitions.append((POIState.GROWING, "Population and resource growth"))
        
        elif current_state == POIState.GROWING:
            if "resource_shortage" in conditions:
                potential_transitions.append((POIState.DECLINING, "Resource depletion during growth"))
        
        elif current_state == POIState.DECLINING:
            if "zero_population" in conditions:
                potential_transitions.append((POIState.ABANDONED, "Population completely fled"))
            elif "faction_investment" in conditions and "population_increase" in conditions:
                potential_transitions.append((POIState.ACTIVE, "Recovery through faction investment"))
        
        elif current_state == POIState.ABANDONED:
            if "time_passage" in conditions:
                potential_transitions.append((POIState.RUINS, "Natural decay over time"))
            elif "faction_investment" in conditions:
                potential_transitions.append((POIState.REPOPULATING, "Faction-led repopulation effort"))
        
        return potential_transitions

    def get_state_statistics(self) -> Dict[str, Any]:
        """Get statistics about POI states"""
        statistics = {}
        
        for state in POIState:
            pois_in_state = self.poi_repository.get_pois_by_state(state)
            statistics[state.value] = len(pois_in_state)
        
        return {
            "state_counts": statistics,
            "total_pois": sum(statistics.values()),
            "last_updated": datetime.utcnow().isoformat()
        }

    def force_state_change(
        self,
        poi_id: UUID,
        target_state: POIState,
        reason: str,
        admin_user_id: Optional[UUID] = None
    ) -> bool:
        """Force a state change bypassing validation (admin function)"""
        metadata = {"forced": True}
        if admin_user_id:
            metadata["admin_user_id"] = str(admin_user_id)
        
        return self.transition_state(
            poi_id=poi_id,
            target_state=target_state,
            reason=f"Admin override: {reason}",
            force=True,
            metadata=metadata
        )

    def get_available_transitions(self, poi_id: UUID) -> List[Dict[str, Any]]:
        """Get available state transitions for a POI"""
        poi = self.poi_repository.get_poi_by_id(poi_id)
        if not poi:
            return []
        
        conditions = self._analyze_poi_conditions(poi)
        available_transitions = []
        
        # Check all possible transitions from current state
        for (from_state, to_state), rule in self.validator.transition_rules.items():
            if from_state == poi.current_state:
                is_valid, errors = self.validator.validate_transition(poi, to_state, conditions, {})
                
                available_transitions.append({
                    "target_state": to_state.value,
                    "valid": is_valid,
                    "errors": errors,
                    "required_conditions": rule.required_conditions,
                    "current_conditions": conditions
                })
        
        return available_transitions


def create_poi_state_business_service(
    poi_repository: POIRepository,
    config_service: StateTransitionConfigService,
    event_dispatcher: Optional[EventDispatcher] = None
) -> POIStateBusinessService:
    """Factory function to create POI state business service"""
    return POIStateBusinessService(poi_repository, config_service, event_dispatcher) 