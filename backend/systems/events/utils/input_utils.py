"""
Input handling utilities for the Visual DM game client.
"""

import pygame
from typing import Dict, Optional, Any, Callable
from .error_utils import handle_error

class InputHandler:
    """Handles input events and key bindings."""
    
    def __init__(self):
        """Initialize the input handler."""
        self.key_bindings: Dict[int, Callable] = {}
        self.mouse_bindings: Dict[int, Callable] = {}
        self.mouse_pos = (0, 0)
        
    def bind_key(self, key: int, callback: Callable) -> None:
        """Bind a key to a callback function.
        
        Args:
            key: Pygame key constant
            callback: Function to call when key is pressed
        """
        try:
            self.key_bindings[key] = callback
        except Exception as e:
            handle_error(e, {"key": key})
            
    def bind_mouse_button(self, button: int, callback: Callable) -> None:
        """Bind a mouse button to a callback function.
        
        Args:
            button: Mouse button number
            callback: Function to call when button is clicked
        """
        try:
            self.mouse_bindings[button] = callback
        except Exception as e:
            handle_error(e, {"button": button})
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events.
        
        Args:
            event: Event to handle
            
        Returns:
            bool: True if event was handled
        """
        try:
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_bindings:
                    self.key_bindings[event.key]()
                    return True
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in self.mouse_bindings:
                    self.mouse_bindings[event.button](event.pos)
                    return True
                    
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                
            return False
        except Exception as e:
            handle_error(e, {"event": str(event)})
            return False
            
    def get_mouse_pos(self) -> tuple:
        """Get the current mouse position.
        
        Returns:
            tuple: (x, y) coordinates
        """
        return self.mouse_pos 