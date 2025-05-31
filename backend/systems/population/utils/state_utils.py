"""
Population State Management Utilities

Implements state transition validation and management for population systems.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PopulationState(Enum):
    """Population states"""
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"
    CRITICAL = "critical"
    RECOVERING = "recovering"
    EVACUATED = "evacuated"
    EXTINCT = "extinct"


class StateTransition(Enum):
    """Valid state transitions"""
    NATURAL_GROWTH = "natural_growth"
    NATURAL_DECLINE = "natural_decline"
    CRISIS_ONSET = "crisis_onset"
    RECOVERY_START = "recovery_start"
    EVACUATION = "evacuation"
    COLLAPSE = "collapse"
    RESTORATION = "restoration"


def is_valid_transition(
    current_state: PopulationState,
    target_state: PopulationState,
    transition_type: StateTransition
) -> bool:
    """
    Validate if a state transition is allowed
    
    Args:
        current_state: Current population state
        target_state: Desired target state
        transition_type: Type of transition
    
    Returns:
        True if transition is valid, False otherwise
    """
    try:
        # Define valid transitions
        valid_transitions = {
            PopulationState.GROWING: {
                StateTransition.NATURAL_GROWTH: [PopulationState.GROWING],
                StateTransition.NATURAL_DECLINE: [PopulationState.STABLE, PopulationState.DECLINING],
                StateTransition.CRISIS_ONSET: [PopulationState.DECLINING, PopulationState.CRITICAL],
                StateTransition.EVACUATION: [PopulationState.EVACUATED]
            },
            PopulationState.STABLE: {
                StateTransition.NATURAL_GROWTH: [PopulationState.GROWING],
                StateTransition.NATURAL_DECLINE: [PopulationState.DECLINING],
                StateTransition.CRISIS_ONSET: [PopulationState.DECLINING, PopulationState.CRITICAL],
                StateTransition.EVACUATION: [PopulationState.EVACUATED]
            },
            PopulationState.DECLINING: {
                StateTransition.NATURAL_DECLINE: [PopulationState.DECLINING, PopulationState.CRITICAL],
                StateTransition.RECOVERY_START: [PopulationState.RECOVERING, PopulationState.STABLE],
                StateTransition.CRISIS_ONSET: [PopulationState.CRITICAL],
                StateTransition.COLLAPSE: [PopulationState.EXTINCT],
                StateTransition.EVACUATION: [PopulationState.EVACUATED]
            },
            PopulationState.CRITICAL: {
                StateTransition.RECOVERY_START: [PopulationState.RECOVERING],
                StateTransition.COLLAPSE: [PopulationState.EXTINCT],
                StateTransition.EVACUATION: [PopulationState.EVACUATED]
            },
            PopulationState.RECOVERING: {
                StateTransition.RECOVERY_START: [PopulationState.STABLE, PopulationState.GROWING],
                StateTransition.NATURAL_DECLINE: [PopulationState.DECLINING],
                StateTransition.CRISIS_ONSET: [PopulationState.DECLINING, PopulationState.CRITICAL]
            },
            PopulationState.EVACUATED: {
                StateTransition.RESTORATION: [PopulationState.RECOVERING, PopulationState.STABLE],
                StateTransition.COLLAPSE: [PopulationState.EXTINCT]
            },
            PopulationState.EXTINCT: {
                StateTransition.RESTORATION: [PopulationState.RECOVERING]  # Very rare
            }
        }
        
        allowed_states = valid_transitions.get(current_state, {}).get(transition_type, [])
        return target_state in allowed_states
        
    except Exception as e:
        logger.error(f"Error validating transition: {e}")
        return False


def is_valid_state_progression(
    state_history: List[Tuple[PopulationState, datetime]],
    proposed_state: PopulationState
) -> bool:
    """
    Validate if a state progression makes sense given history
    
    Args:
        state_history: List of (state, timestamp) tuples
        proposed_state: State being proposed
    
    Returns:
        True if progression is valid
    """
    try:
        if not state_history:
            return True  # Any state is valid as first state
            
        current_state, current_time = state_history[-1]
        
        # Check for rapid oscillations (sign of instability)
        if len(state_history) >= 3:
            recent_states = [s for s, t in state_history[-3:]]
            if len(set(recent_states)) == 3:  # 3 different states in last 3 entries
                logger.warning("Rapid state oscillation detected")
                return False
                
        # Check time-based constraints
        time_since_last = datetime.utcnow() - current_time
        
        # Some transitions require minimum time
        minimum_time_constraints = {
            (PopulationState.RECOVERING, PopulationState.STABLE): timedelta(days=30),
            (PopulationState.CRITICAL, PopulationState.RECOVERING): timedelta(days=7),
            (PopulationState.EVACUATED, PopulationState.RECOVERING): timedelta(days=14)
        }
        
        min_time = minimum_time_constraints.get((current_state, proposed_state))
        if min_time and time_since_last < min_time:
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating state progression: {e}")
        return False


def estimate_time_to_state(
    current_state: PopulationState,
    target_state: PopulationState,
    current_conditions: Dict[str, Any]
) -> Optional[timedelta]:
    """
    Estimate time required to reach target state
    
    Args:
        current_state: Current population state
        target_state: Desired target state
        current_conditions: Current environmental/social conditions
    
    Returns:
        Estimated time as timedelta, or None if transition impossible
    """
    try:
        # Base transition times (in days)
        base_transition_times = {
            (PopulationState.DECLINING, PopulationState.RECOVERING): 14,
            (PopulationState.CRITICAL, PopulationState.RECOVERING): 30,
            (PopulationState.RECOVERING, PopulationState.STABLE): 60,
            (PopulationState.STABLE, PopulationState.GROWING): 90,
            (PopulationState.GROWING, PopulationState.STABLE): 45,
            (PopulationState.STABLE, PopulationState.DECLINING): 120,
            (PopulationState.EVACUATED, PopulationState.RECOVERING): 90,
            (PopulationState.RECOVERING, PopulationState.GROWING): 120
        }
        
        base_days = base_transition_times.get((current_state, target_state))
        if base_days is None:
            return None  # Invalid or impossible transition
            
        # Apply condition modifiers
        condition_modifiers = 1.0
        
        # Resource availability affects recovery time
        if 'resource_availability' in current_conditions:
            resource_factor = current_conditions['resource_availability']  # 0.0-1.0
            if target_state in [PopulationState.RECOVERING, PopulationState.STABLE, PopulationState.GROWING]:
                condition_modifiers *= (2.0 - resource_factor)  # More resources = faster recovery
                
        # Healthcare affects recovery
        if 'healthcare_level' in current_conditions:
            healthcare_factor = current_conditions['healthcare_level']  # 0.0-1.0
            if target_state in [PopulationState.RECOVERING, PopulationState.STABLE]:
                condition_modifiers *= (1.5 - (healthcare_factor * 0.5))
                
        # Political stability affects all transitions
        if 'political_stability' in current_conditions:
            stability_factor = current_conditions['political_stability']  # 0.0-1.0
            condition_modifiers *= (1.3 - (stability_factor * 0.3))
            
        # External aid affects positive transitions
        if 'external_aid' in current_conditions and target_state in [
            PopulationState.RECOVERING, PopulationState.STABLE, PopulationState.GROWING
        ]:
            aid_factor = current_conditions['external_aid']  # 0.0-1.0
            condition_modifiers *= (1.0 - (aid_factor * 0.4))  # Aid speeds recovery
            
        final_days = int(base_days * condition_modifiers)
        return timedelta(days=max(1, final_days))  # Minimum 1 day
        
    except Exception as e:
        logger.error(f"Error estimating time to state: {e}")
        return None


def get_poi_status_description(
    population: int,
    state: PopulationState,
    recent_events: List[str] = None,
    resources: Dict[str, float] = None
) -> str:
    """
    Generate human-readable status description for a POI
    
    Args:
        population: Current population count
        state: Current population state
        recent_events: List of recent event descriptions
        resources: Resource availability dict
    
    Returns:
        Formatted status description
    """
    try:
        if recent_events is None:
            recent_events = []
        if resources is None:
            resources = {}
            
        # Base status by state
        state_descriptions = {
            PopulationState.GROWING: f"Thriving community of {population:,} residents experiencing steady growth",
            PopulationState.STABLE: f"Stable settlement of {population:,} people maintaining steady population",
            PopulationState.DECLINING: f"Struggling community of {population:,} facing population decline",
            PopulationState.CRITICAL: f"Community in crisis with {population:,} remaining residents",
            PopulationState.RECOVERING: f"Recovering settlement of {population:,} people rebuilding",
            PopulationState.EVACUATED: f"Evacuated area with {population:,} displaced residents",
            PopulationState.EXTINCT: "Abandoned settlement with no remaining population"
        }
        
        base_description = state_descriptions.get(state, f"Settlement of {population:,} people")
        
        # Add resource context
        resource_context = []
        for resource_type, availability in resources.items():
            if availability < 0.3:
                resource_context.append(f"severe {resource_type} shortage")
            elif availability < 0.6:
                resource_context.append(f"limited {resource_type}")
            elif availability > 0.9:
                resource_context.append(f"abundant {resource_type}")
                
        # Add recent events context
        event_context = []
        if recent_events:
            if len(recent_events) > 3:
                event_context.append(f"experiencing multiple challenges including {', '.join(recent_events[:2])}")
            else:
                event_context.append(f"affected by {', '.join(recent_events)}")
                
        # Combine all context
        full_description = base_description
        
        if resource_context:
            full_description += f", facing {', '.join(resource_context)}"
            
        if event_context:
            full_description += f", {', '.join(event_context)}"
            
        return full_description + "."
        
    except Exception as e:
        logger.error(f"Error generating POI status description: {e}")
        return f"Settlement of {population:,} people (status unavailable)"
