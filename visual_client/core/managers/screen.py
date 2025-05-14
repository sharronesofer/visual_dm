"""
Base screen class for all screens.
"""

import pygame
from typing import Optional, Dict, Any
from .error_handler import handle_component_error, ErrorSeverity

class Screen:
    """Base screen class."""
    
    def __init__(self, app):
        """Initialize the screen."""
        self.app = app
        self.running = True
    
    def update(self, dt: float) -> None:
        """Update the screen.
        
        Args:
            dt: Time since last update in seconds
        """
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the screen.
        
        Args:
            surface: Surface to draw on
        """
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event.
        
        Args:
            event: Event to handle
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        return False
    
    def on_enter(self) -> None:
        """Called when the screen is entered."""
        pass
    
    def on_exit(self) -> None:
        """Called when the screen is exited."""
        pass 