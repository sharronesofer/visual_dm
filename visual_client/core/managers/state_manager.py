"""
State management system for handling application state.
"""

import logging
from typing import Dict, Any, Optional, Callable, Union
from .error_handler import handle_component_error, ErrorSeverity

# Type hints for state management (import after standard imports)
try:
    from map_system.src.types.state import RegionState, ViewportState, POIData
except ImportError:
    RegionState = Any
    ViewportState = Any
    POIData = Any

logger = logging.getLogger(__name__)

class StateManager:
    """
    Manages application state and state transitions.
    Explicitly supports RegionState, ViewportState, and POIState for core backend state management.
    """
    
    def __init__(self):
        """Initialize the state manager."""
        self.states: Dict[str, Any] = {}
        self.current_state: Optional[str] = None
        self.state_stack: list[str] = []
        self.state_callbacks: Dict[str, Dict[str, Callable]] = {}
        
    def register_state(self, name: str, state: Any) -> None:
        """Register a state with the state manager.
        
        Args:
            name: Unique identifier for the state
            state: State object to register
        """
        try:
            if name in self.states:
                raise ValueError(f"State {name} already registered")
                
            self.states[name] = state
            self.state_callbacks[name] = {
                "enter": None,
                "exit": None,
                "update": None
            }
            logger.debug(f"Registered state: {name}")
            
        except Exception as e:
            handle_component_error(
                "StateManager",
                "register_state",
                e,
                ErrorSeverity.ERROR,
                {"state_name": name}
            )
            
    def set_state(self, name: str) -> None:
        """Set the current active state.
        
        Args:
            name: Name of the state to set
        """
        try:
            if name not in self.states:
                raise ValueError(f"State {name} not registered")
                
            # Call exit callback for current state
            if self.current_state and self.state_callbacks[self.current_state]["exit"]:
                self.state_callbacks[self.current_state]["exit"]()
                
            # Update current state
            self.current_state = name
            
            # Call enter callback for new state
            if self.state_callbacks[name]["enter"]:
                self.state_callbacks[name]["enter"]()
                
            # Update state stack
            if self.state_stack and self.state_stack[-1] == name:
                self.state_stack.pop()
            self.state_stack.append(name)
            
            logger.debug(f"Set current state to: {name}")
            
        except Exception as e:
            handle_component_error(
                "StateManager",
                "set_state",
                e,
                ErrorSeverity.ERROR,
                {"state_name": name}
            )
            
    def push_state(self, name: str) -> None:
        """Push a state onto the stack.
        
        Args:
            name: Name of the state to push
        """
        try:
            if name not in self.states:
                raise ValueError(f"State {name} not registered")
                
            # Pause current state
            if self.current_state and self.state_callbacks[self.current_state]["exit"]:
                self.state_callbacks[self.current_state]["exit"]()
                
            # Update current state
            self.current_state = name
            
            # Call enter callback for new state
            if self.state_callbacks[name]["enter"]:
                self.state_callbacks[name]["enter"]()
                
            # Update state stack
            self.state_stack.append(name)
            
            logger.debug(f"Pushed state: {name}")
            
        except Exception as e:
            handle_component_error(
                "StateManager",
                "push_state",
                e,
                ErrorSeverity.ERROR,
                {"state_name": name}
            )
            
    def pop_state(self) -> None:
        """Pop the current state from the stack."""
        try:
            if len(self.state_stack) <= 1:
                raise ValueError("Cannot pop the last state")
                
            # Call exit callback for current state
            if self.current_state and self.state_callbacks[self.current_state]["exit"]:
                self.state_callbacks[self.current_state]["exit"]()
                
            # Pop state from stack
            self.state_stack.pop()
            
            # Set previous state
            prev_name = self.state_stack[-1]
            self.current_state = prev_name
            
            # Call enter callback for previous state
            if self.state_callbacks[prev_name]["enter"]:
                self.state_callbacks[prev_name]["enter"]()
                
            logger.debug(f"Popped state, returned to: {prev_name}")
            
        except Exception as e:
            handle_component_error(
                "StateManager",
                "pop_state",
                e,
                ErrorSeverity.ERROR
            )
            
    def set_state_callback(self, state_name: str, callback_type: str, callback: Callable) -> None:
        """Set a callback for a state.
        
        Args:
            state_name: Name of the state
            callback_type: Type of callback ("enter", "exit", or "update")
            callback: Function to call
        """
        try:
            if state_name not in self.states:
                raise ValueError(f"State {state_name} not registered")
                
            if callback_type not in ["enter", "exit", "update"]:
                raise ValueError(f"Invalid callback type: {callback_type}")
                
            self.state_callbacks[state_name][callback_type] = callback
            logger.debug(f"Set {callback_type} callback for state: {state_name}")
            
        except Exception as e:
            handle_component_error(
                "StateManager",
                "set_state_callback",
                e,
                ErrorSeverity.ERROR,
                {"state_name": state_name, "callback_type": callback_type}
            )
            
    def update(self, dt: int) -> None:
        """Update the current state.
        
        Args:
            dt: Time elapsed since last update
        """
        try:
            if self.current_state and self.state_callbacks[self.current_state]["update"]:
                self.state_callbacks[self.current_state]["update"](dt)
                
        except Exception as e:
            handle_component_error(
                "StateManager",
                "update",
                e,
                ErrorSeverity.ERROR,
                {"dt": dt}
            )
            
    def get_state(self, name: str) -> Optional[Any]:
        """Get a state by name.
        
        Args:
            name: Name of the state to get
            
        Returns:
            The state object if found, None otherwise
        """
        try:
            return self.states.get(name)
            
        except Exception as e:
            handle_component_error(
                "StateManager",
                "get_state",
                e,
                ErrorSeverity.ERROR,
                {"state_name": name}
            )
            return None
            
    def cleanup(self) -> None:
        """Clean up all states."""
        try:
            # Call exit callback for current state
            if self.current_state and self.state_callbacks[self.current_state]["exit"]:
                self.state_callbacks[self.current_state]["exit"]()
                
            self.states.clear()
            self.state_stack.clear()
            self.state_callbacks.clear()
            self.current_state = None
            
            logger.debug("Cleaned up all states")
            
        except Exception as e:
            handle_component_error(
                "StateManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            )

    def register_region_state(self, state: RegionState) -> None:
        """Register the region state object."""
        self.register_state("region", state)

    def update_region_state(self, new_state: Union[RegionState, Dict[str, Any]]) -> None:
        """Update the region state object."""
        if "region" in self.states:
            if isinstance(new_state, dict):
                self.states["region"].update(new_state)
            else:
                self.states["region"] = new_state
        else:
            self.register_region_state(new_state)

    def get_region_state(self) -> Optional[RegionState]:
        """Get the current region state object."""
        return self.states.get("region")

    def register_viewport_state(self, state: ViewportState) -> None:
        """Register the viewport state object."""
        self.register_state("viewport", state)

    def update_viewport_state(self, new_state: Union[ViewportState, Dict[str, Any]]) -> None:
        """Update the viewport state object."""
        if "viewport" in self.states:
            if isinstance(new_state, dict):
                self.states["viewport"].update(new_state)
            else:
                self.states["viewport"] = new_state
        else:
            self.register_viewport_state(new_state)

    def get_viewport_state(self) -> Optional[ViewportState]:
        """Get the current viewport state object."""
        return self.states.get("viewport")

    def register_poi_state(self, state: Dict[str, POIData]) -> None:
        """Register the POI state object (dict of POIData)."""
        self.register_state("pois", state)

    def update_poi_state(self, new_state: Union[Dict[str, POIData], Dict[str, Any]]) -> None:
        """Update the POI state object."""
        if "pois" in self.states:
            self.states["pois"].update(new_state)
        else:
            self.register_poi_state(new_state)

    def get_poi_state(self) -> Optional[Dict[str, POIData]]:
        """Get the current POI state object."""
        return self.states.get("pois") 