"""
POI State Service

This service manages POI state transitions, validation, constraints, 
event dispatching, and threshold logic for the POI system.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from uuid import UUID
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from backend.systems.poi.models import (
    PoiEntity,
    POIState,
    POIType,
    POIInteractionType
)
from backend.systems.poi.repositories.poi_repository import PoiRepository
from backend.infrastructure.shared.exceptions import (
    PoiValidationError,
    PoiNotFoundError,
    PoiConflictError
)

logger = logging.getLogger(__name__)


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


class StateTransitionValidator:
    """Validates state transitions based on rules and constraints"""
    
    def __init__(self):
        self.transition_rules = self._initialize_transition_rules()
    
    def _initialize_transition_rules(self) -> Dict[Tuple[POIState, POIState], StateTransitionRule]:
        """Initialize state transition rules"""
        rules = {}
        
        # Active state transitions
        rules[(POIState.ACTIVE, POIState.GROWING)] = StateTransitionRule(
            from_state=POIState.ACTIVE,
            to_state=POIState.GROWING,
            required_conditions=["population_increase", "resource_surplus"],
            population_threshold=(100, None),
            time_requirement=timedelta(days=30)
        )
        
        rules[(POIState.ACTIVE, POIState.DECLINING)] = StateTransitionRule(
            from_state=POIState.ACTIVE,
            to_state=POIState.DECLINING,
            required_conditions=["population_decrease", "resource_shortage"],
            population_threshold=(None, 50),
            time_requirement=timedelta(days=14)
        )
        
        rules[(POIState.ACTIVE, POIState.ABANDONED)] = StateTransitionRule(
            from_state=POIState.ACTIVE,
            to_state=POIState.ABANDONED,
            required_conditions=["zero_population", "no_faction_control"],
            population_threshold=(0, 0),
            faction_required=False
        )
        
        # Growing state transitions
        rules[(POIState.GROWING, POIState.ACTIVE)] = StateTransitionRule(
            from_state=POIState.GROWING,
            to_state=POIState.ACTIVE,
            required_conditions=["stable_population"],
            time_requirement=timedelta(days=60)
        )
        
        rules[(POIState.GROWING, POIState.DECLINING)] = StateTransitionRule(
            from_state=POIState.GROWING,
            to_state=POIState.DECLINING,
            required_conditions=["growth_reversal", "resource_crisis"],
            time_requirement=timedelta(days=7)
        )
        
        # Declining state transitions
        rules[(POIState.DECLINING, POIState.ACTIVE)] = StateTransitionRule(
            from_state=POIState.DECLINING,
            to_state=POIState.ACTIVE,
            required_conditions=["population_recovery", "resource_improvement"],
            population_threshold=(75, None),
            time_requirement=timedelta(days=45)
        )
        
        rules[(POIState.DECLINING, POIState.ABANDONED)] = StateTransitionRule(
            from_state=POIState.DECLINING,
            to_state=POIState.ABANDONED,
            required_conditions=["critical_population_loss"],
            population_threshold=(0, 10),
            time_requirement=timedelta(days=30)
        )
        
        rules[(POIState.DECLINING, POIState.RUINED)] = StateTransitionRule(
            from_state=POIState.DECLINING,
            to_state=POIState.RUINED,
            required_conditions=["infrastructure_collapse", "disaster"],
            time_requirement=timedelta(days=90)
        )
        
        # Abandoned state transitions
        rules[(POIState.ABANDONED, POIState.REPOPULATING)] = StateTransitionRule(
            from_state=POIState.ABANDONED,
            to_state=POIState.REPOPULATING,
            required_conditions=["new_settlers", "faction_investment"],
            population_threshold=(1, None),
            faction_required=True
        )
        
        rules[(POIState.ABANDONED, POIState.RUINS)] = StateTransitionRule(
            from_state=POIState.ABANDONED,
            to_state=POIState.RUINS,
            required_conditions=["structural_decay"],
            time_requirement=timedelta(days=365)
        )
        
        # Repopulating state transitions
        rules[(POIState.REPOPULATING, POIState.ACTIVE)] = StateTransitionRule(
            from_state=POIState.REPOPULATING,
            to_state=POIState.ACTIVE,
            required_conditions=["stable_population_growth"],
            population_threshold=(50, None),
            time_requirement=timedelta(days=90)
        )
        
        rules[(POIState.REPOPULATING, POIState.ABANDONED)] = StateTransitionRule(
            from_state=POIState.REPOPULATING,
            to_state=POIState.ABANDONED,
            required_conditions=["repopulation_failure"],
            population_threshold=(0, 5),
            time_requirement=timedelta(days=60)
        )
        
        # Under construction transitions
        rules[(POIState.UNDER_CONSTRUCTION, POIState.ACTIVE)] = StateTransitionRule(
            from_state=POIState.UNDER_CONSTRUCTION,
            to_state=POIState.ACTIVE,
            required_conditions=["construction_complete", "initial_population"],
            population_threshold=(10, None),
            resources_required={"materials": 100, "workers": 20}
        )
        
        rules[(POIState.UNDER_CONSTRUCTION, POIState.ABANDONED)] = StateTransitionRule(
            from_state=POIState.UNDER_CONSTRUCTION,
            to_state=POIState.ABANDONED,
            required_conditions=["construction_abandoned", "funding_loss"],
            time_requirement=timedelta(days=180)
        )
        
        # Special state transitions
        rules[(POIState.RUINS, POIState.UNDER_CONSTRUCTION)] = StateTransitionRule(
            from_state=POIState.RUINS,
            to_state=POIState.UNDER_CONSTRUCTION,
            required_conditions=["restoration_project", "faction_investment"],
            faction_required=True,
            resources_required={"materials": 200, "workers": 50}
        )
        
        return rules
    
    def validate_transition(
        self, 
        poi: PoiEntity, 
        target_state: POIState,
        conditions: List[str],
        metadata: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate if a state transition is allowed.
        
        Args:
            poi: POI entity
            target_state: Target state to transition to
            conditions: Current conditions that triggered the transition
            metadata: Additional context data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        current_state = POIState(poi.state)
        transition_key = (current_state, target_state)
        
        if transition_key not in self.transition_rules:
            return False, [f"No transition rule defined from {current_state.value} to {target_state.value}"]
        
        rule = self.transition_rules[transition_key]
        errors = []
        
        # Check required conditions
        missing_conditions = set(rule.required_conditions) - set(conditions)
        if missing_conditions:
            errors.append(f"Missing required conditions: {', '.join(missing_conditions)}")
        
        # Check population thresholds
        if rule.population_threshold and poi.population is not None:
            min_pop, max_pop = rule.population_threshold
            if min_pop is not None and poi.population < min_pop:
                errors.append(f"Population {poi.population} below minimum threshold {min_pop}")
            if max_pop is not None and poi.population > max_pop:
                errors.append(f"Population {poi.population} above maximum threshold {max_pop}")
        
        # Check faction requirements
        if rule.faction_required and not poi.faction_id:
            errors.append("Faction control required for this transition")
        
        # Check resource requirements
        if rule.resources_required:
            poi_resources = poi.resources or {}
            for resource, required_amount in rule.resources_required.items():
                available = poi_resources.get(resource, 0)
                if available < required_amount:
                    errors.append(f"Insufficient {resource}: {available}/{required_amount}")
        
        # Check time requirements (would need additional tracking in metadata)
        if rule.time_requirement:
            last_transition = metadata.get("last_state_change")
            if last_transition:
                time_since = datetime.utcnow() - datetime.fromisoformat(last_transition)
                if time_since < rule.time_requirement:
                    remaining = rule.time_requirement - time_since
                    errors.append(f"Time requirement not met: {remaining.days} days remaining")
        
        return len(errors) == 0, errors


class POIStateService:
    """
    Service for managing POI state transitions and lifecycle.
    
    Handles state validation, transitions, event dispatching, and threshold monitoring.
    """
    
    def __init__(self, poi_repository: PoiRepository):
        """
        Initialize POI state service.
        
        Args:
            poi_repository: Repository for POI data access
        """
        self.repository = poi_repository
        self.validator = StateTransitionValidator()
        self.event_handlers: List[callable] = []
        
    def add_event_handler(self, handler: callable):
        """Add event handler for state transitions"""
        self.event_handlers.append(handler)
    
    def remove_event_handler(self, handler: callable):
        """Remove event handler"""
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)
    
    def _dispatch_event(self, event: StateTransitionEvent):
        """Dispatch state transition event to all handlers"""
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {str(e)}")
    
    def transition_state(
        self,
        poi_id: UUID,
        target_state: POIState,
        reason: str,
        conditions: Optional[List[str]] = None,
        force: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Transition POI to a new state.
        
        Args:
            poi_id: POI ID
            target_state: Target state
            reason: Reason for transition
            conditions: Current conditions
            force: Force transition without validation
            metadata: Additional context data
            
        Returns:
            True if transition successful
            
        Raises:
            PoiNotFoundError: If POI not found
            PoiValidationError: If transition invalid
        """
        try:
            poi = self.repository.get(poi_id)
            if not poi:
                raise PoiNotFoundError(f"POI {poi_id} not found")
            
            current_state = POIState(poi.state)
            conditions = conditions or []
            metadata = metadata or {}
            
            # Skip validation if forced
            if not force:
                is_valid, errors = self.validator.validate_transition(
                    poi, target_state, conditions, metadata
                )
                if not is_valid:
                    raise PoiValidationError(f"Invalid state transition: {'; '.join(errors)}")
            
            # Perform transition
            old_state = current_state
            success = self.repository.change_state(poi_id, target_state)
            
            if success:
                # Create and dispatch event
                event = StateTransitionEvent(
                    poi_id=poi_id,
                    from_state=old_state,
                    to_state=target_state,
                    timestamp=datetime.utcnow(),
                    reason=reason,
                    metadata={
                        **metadata,
                        "conditions": conditions,
                        "forced": force
                    }
                )
                self._dispatch_event(event)
                
                logger.info(f"POI {poi_id} transitioned from {old_state.value} to {target_state.value}: {reason}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error transitioning POI state: {str(e)}")
            raise
    
    def evaluate_automatic_transitions(self, poi_id: UUID) -> List[StateTransitionEvent]:
        """
        Evaluate and execute automatic state transitions based on current conditions.
        
        Args:
            poi_id: POI ID to evaluate
            
        Returns:
            List of executed transition events
        """
        try:
            poi = self.repository.get(poi_id)
            if not poi:
                return []
            
            current_state = POIState(poi.state)
            executed_transitions = []
            
            # Analyze current conditions
            conditions = self._analyze_poi_conditions(poi)
            
            # Check for automatic transitions
            potential_transitions = self._get_potential_transitions(current_state, conditions)
            
            for target_state, reason in potential_transitions:
                try:
                    success = self.transition_state(
                        poi_id=poi_id,
                        target_state=target_state,
                        reason=f"Automatic transition: {reason}",
                        conditions=conditions,
                        force=False,
                        metadata={"automatic": True}
                    )
                    
                    if success:
                        event = StateTransitionEvent(
                            poi_id=poi_id,
                            from_state=current_state,
                            to_state=target_state,
                            timestamp=datetime.utcnow(),
                            reason=reason,
                            metadata={"automatic": True, "conditions": conditions}
                        )
                        executed_transitions.append(event)
                        break  # Only execute one transition per evaluation
                        
                except PoiValidationError:
                    # Transition not valid, continue to next
                    continue
            
            return executed_transitions
            
        except Exception as e:
            logger.error(f"Error evaluating automatic transitions: {str(e)}")
            return []
    
    def _analyze_poi_conditions(self, poi: PoiEntity) -> List[str]:
        """Analyze POI to determine current conditions"""
        conditions = []
        
        # Population analysis
        if poi.population is not None:
            if poi.population == 0:
                conditions.append("zero_population")
            elif poi.population < 25:
                conditions.append("low_population")
            elif poi.population > 200:
                conditions.append("high_population")
            
            # Population growth/decline would need historical data
            # For now, we'll use simple thresholds
            if poi.population > 100:
                conditions.append("population_increase")
            elif poi.population < 50:
                conditions.append("population_decrease")
        
        # Faction control
        if poi.faction_id:
            conditions.append("faction_control")
        else:
            conditions.append("no_faction_control")
        
        # Resource analysis
        resources = poi.resources or {}
        total_resources = sum(resources.values()) if resources else 0
        
        if total_resources > 1000:
            conditions.append("resource_surplus")
        elif total_resources < 100:
            conditions.append("resource_shortage")
        
        # Infrastructure analysis (based on POI type)
        poi_type = POIType(poi.poi_type)
        if poi_type in [POIType.CITY, POIType.FORTRESS]:
            conditions.append("major_infrastructure")
        elif poi_type in [POIType.VILLAGE, POIType.OUTPOST]:
            conditions.append("minor_infrastructure")
        
        return conditions
    
    def _get_potential_transitions(
        self, 
        current_state: POIState, 
        conditions: List[str]
    ) -> List[Tuple[POIState, str]]:
        """Get potential automatic transitions based on conditions"""
        transitions = []
        
        if current_state == POIState.ACTIVE:
            if "zero_population" in conditions:
                transitions.append((POIState.ABANDONED, "Population reached zero"))
            elif "low_population" in conditions and "resource_shortage" in conditions:
                transitions.append((POIState.DECLINING, "Low population and resource shortage"))
            elif "high_population" in conditions and "resource_surplus" in conditions:
                transitions.append((POIState.GROWING, "High population and resource surplus"))
        
        elif current_state == POIState.GROWING:
            if "population_decrease" in conditions:
                transitions.append((POIState.DECLINING, "Population growth reversed"))
        
        elif current_state == POIState.DECLINING:
            if "zero_population" in conditions:
                transitions.append((POIState.ABANDONED, "Population completely declined"))
            elif "population_increase" in conditions and "resource_surplus" in conditions:
                transitions.append((POIState.ACTIVE, "Population and resources recovered"))
        
        elif current_state == POIState.ABANDONED:
            if "faction_control" in conditions and "population_increase" in conditions:
                transitions.append((POIState.REPOPULATING, "New faction investment and settlers"))
        
        elif current_state == POIState.REPOPULATING:
            if "high_population" in conditions:
                transitions.append((POIState.ACTIVE, "Repopulation successful"))
            elif "zero_population" in conditions:
                transitions.append((POIState.ABANDONED, "Repopulation failed"))
        
        return transitions
    
    def get_state_statistics(self) -> Dict[str, Any]:
        """Get statistics about POI states"""
        try:
            stats = self.repository.get_statistics()
            
            # Add state-specific analysis
            state_analysis = {}
            for state in POIState:
                pois = self.repository.get_by_state(state)
                state_analysis[state.value] = {
                    "count": len(pois),
                    "avg_population": sum(poi.population or 0 for poi in pois) / len(pois) if pois else 0,
                    "faction_controlled": sum(1 for poi in pois if poi.faction_id),
                    "resource_rich": sum(1 for poi in pois if sum((poi.resources or {}).values()) > 500)
                }
            
            return {
                **stats,
                "state_analysis": state_analysis,
                "transition_rules_count": len(self.validator.transition_rules)
            }
            
        except Exception as e:
            logger.error(f"Error getting state statistics: {str(e)}")
            return {}
    
    def force_state_change(
        self,
        poi_id: UUID,
        target_state: POIState,
        reason: str,
        admin_user_id: Optional[UUID] = None
    ) -> bool:
        """
        Force a state change without validation (admin function).
        
        Args:
            poi_id: POI ID
            target_state: Target state
            reason: Reason for forced change
            admin_user_id: ID of admin user making the change
            
        Returns:
            True if successful
        """
        return self.transition_state(
            poi_id=poi_id,
            target_state=target_state,
            reason=f"Admin override: {reason}",
            force=True,
            metadata={
                "admin_override": True,
                "admin_user_id": str(admin_user_id) if admin_user_id else None
            }
        )
    
    def get_available_transitions(self, poi_id: UUID) -> List[Dict[str, Any]]:
        """
        Get list of available transitions for a POI.
        
        Args:
            poi_id: POI ID
            
        Returns:
            List of available transitions with validation info
        """
        try:
            poi = self.repository.get(poi_id)
            if not poi:
                return []
            
            current_state = POIState(poi.state)
            conditions = self._analyze_poi_conditions(poi)
            available_transitions = []
            
            # Check all possible transitions from current state
            for (from_state, to_state), rule in self.validator.transition_rules.items():
                if from_state == current_state:
                    is_valid, errors = self.validator.validate_transition(
                        poi, to_state, conditions, {}
                    )
                    
                    available_transitions.append({
                        "target_state": to_state.value,
                        "is_valid": is_valid,
                        "errors": errors,
                        "required_conditions": rule.required_conditions,
                        "population_threshold": rule.population_threshold,
                        "time_requirement": rule.time_requirement.days if rule.time_requirement else None,
                        "faction_required": rule.faction_required,
                        "resources_required": rule.resources_required
                    })
            
            return available_transitions
            
        except Exception as e:
            logger.error(f"Error getting available transitions: {str(e)}")
            return [] 