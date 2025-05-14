"""
Base screen class with common functionality for all screens.
"""

import pygame
import logging
from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic
from enum import Enum
from dataclasses import dataclass
from visual_client.core.utils.error_utils import ScreenError
from visual_client.core.utils.screen_utils import ScreenManager
from visual_client.ui.components import (
    Button,
    Panel,
    ComponentStyle,
    BaseComponent,
    Label
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Enum)

@dataclass
class ScreenData:
    """Base data structure for screen information."""
    error_message: str = ""
    error_timer: float = 0.0

class StatefulScreen(Generic[T]):
    """Base class for screens with state management."""
    
    def __init__(self, screen_manager: ScreenManager, initial_state: T):
        """Initialize the screen.
        
        Args:
            screen_manager: Screen manager instance
            initial_state: Initial state of the screen
        """
        self.screen_manager = screen_manager
        self.state = initial_state
        self.screen_data = ScreenData()
        self.state_handlers: Dict[T, Callable] = {}
        self.current_components: List[BaseComponent] = []
        
        # Initialize UI components
        self._initialize_base_components()
        
    def _initialize_base_components(self) -> None:
        """Initialize base UI components."""
        try:
            screen_rect = self.screen_manager.get_screen_rect()
            
            # Main panel
            self.main_panel = Panel(
                pygame.Rect(0, 0, screen_rect.width, screen_rect.height),
                ComponentStyle(
                    background_color=(30, 30, 30),
                    gradient_start=(40, 40, 40),
                    gradient_end=(20, 20, 20),
                    gradient_direction="vertical"
                )
            )
            
            # Error message label
            self.error_label = Label(
                pygame.Rect(
                    screen_rect.width // 2 - 200,
                    screen_rect.height - 50,
                    400,
                    30
                ),
                "",
                ComponentStyle(
                    font_color=(255, 0, 0),
                    font_size=16,
                    alignment="center"
                ),
                self.main_panel
            )
            
        except Exception as e:
            logger.error(f"Error initializing base components: {str(e)}")
            raise ScreenError("Failed to initialize base components")
            
    def _transition_state(self, new_state: T) -> None:
        """Transition to a new state.
        
        Args:
            new_state: The state to transition to
        """
        try:
            # Validate transition
            if not self._validate_transition(new_state):
                return
                
            # Store current state data
            self._persist_state_data()
            
            # Clean up old state components
            self._cleanup_state_components()
                
            # Update state
            self.state = new_state
            
            # Update UI
            self._update_state_ui()
            
        except Exception as e:
            logger.error(f"Error during state transition: {str(e)}")
            self._show_error("Failed to transition state")
            
    def _validate_transition(self, new_state: T) -> bool:
        """Validate a state transition.
        
        Args:
            new_state: The state to transition to
            
        Returns:
            bool: True if the transition is valid
        """
        return True  # Override in derived classes
        
    def _persist_state_data(self) -> None:
        """Persist state-specific data before transition."""
        pass  # Override in derived classes
        
    def _update_state_ui(self) -> None:
        """Update UI based on current state."""
        try:
            # Clear state panel and remove old components
            self._cleanup_state_components()
            
            # Call state handler
            if self.state in self.state_handlers:
                self.state_handlers[self.state]()
                
        except Exception as e:
            logger.error(f"Error updating state UI: {str(e)}")
            self._show_error("Failed to update UI")
            
    def _cleanup_state_components(self) -> None:
        """Clean up state-specific components."""
        self.current_components.clear()
        
    def _show_error(self, message: str) -> None:
        """Show an error message.
        
        Args:
            message: Error message to display
        """
        try:
            self.screen_data.error_message = message
            self.screen_data.error_timer = 3.0  # Show error for 3 seconds
            self.error_label.text = message
            
        except Exception as e:
            logger.error(f"Error showing error message: {str(e)}")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events.
        
        Args:
            event: The event to handle
            
        Returns:
            bool: True if the event was handled
        """
        try:
            # Handle state-specific events
            for component in self.current_components:
                if component.handle_event(event):
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error handling event: {str(e)}")
            return False
            
    def update(self, dt: float) -> None:
        """Update the screen.
        
        Args:
            dt: Time delta since last update
        """
        try:
            # Update error timer
            if self.screen_data.error_timer > 0:
                self.screen_data.error_timer -= dt
                if self.screen_data.error_timer <= 0:
                    self.error_label.text = ""
                    
            # Update components
            for component in self.current_components:
                if hasattr(component, 'update'):
                    component.update(dt)
                    
        except Exception as e:
            logger.error(f"Error updating screen: {str(e)}")
            
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the screen.
        
        Args:
            surface: Surface to draw on
        """
        try:
            # Draw main panel
            self.main_panel.draw(surface)
            
            # Draw components
            for component in self.current_components:
                component.draw(surface)
                
        except Exception as e:
            logger.error(f"Error drawing screen: {str(e)}") 