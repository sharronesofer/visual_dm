"""Shared State Management Infrastructure"""

from .population_state_utils import (
    PopulationState,
    StateTransition,
    is_valid_transition,
    is_valid_state_progression,
    estimate_time_to_state,
    get_poi_status_description
)

__all__ = [
    "PopulationState",
    "StateTransition", 
    "is_valid_transition",
    "is_valid_state_progression",
    "estimate_time_to_state",
    "get_poi_status_description"
] 