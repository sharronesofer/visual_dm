"""
Screen management system for handling different application screens.
"""

import pygame
import logging
from typing import Dict, Optional, Type, Any
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

class ScreenManager:
    """Manages application screens and transitions."""
    
    def __init__(self):
        """Initialize the screen manager."""
        self.screens: Dict[str, Any] = {}
        self.current_screen: Optional[Any] = None
        self.screen_stack: list[str] = []
        
    def register_screen(self, name: str, screen_class: Type) -> None:
        """Register a screen with the screen manager.
        
        Args:
            name: Unique identifier for the screen
            screen_class: Screen class to register
        """
        try:
            if name in self.screens:
                raise ValueError(f"Screen {name} already registered")
                
            self.screens[name] = screen_class
            logger.debug(f"Registered screen: {name}")
            
        except Exception as e:
            handle_component_error(
                "ScreenManager",
                "register_screen",
                e,
                ErrorSeverity.ERROR,
                {"screen_name": name}
            )
            
    def set_screen(self, name: str, *args, **kwargs) -> None:
        """Set the current active screen.
        
        Args:
            name: Name of the screen to set
            *args: Additional arguments for screen initialization
            **kwargs: Additional keyword arguments for screen initialization
        """
        try:
            if name not in self.screens:
                raise ValueError(f"Screen {name} not registered")
                
            # Clean up current screen
            if self.current_screen:
                self.current_screen.cleanup()
                
            # Create new screen instance
            self.current_screen = self.screens[name](*args, **kwargs)
            self.current_screen.initialize()
            
            # Update screen stack
            if self.screen_stack and self.screen_stack[-1] == name:
                self.screen_stack.pop()
            self.screen_stack.append(name)
            
            logger.debug(f"Set current screen to: {name}")
            
        except Exception as e:
            handle_component_error(
                "ScreenManager",
                "set_screen",
                e,
                ErrorSeverity.ERROR,
                {"screen_name": name}
            )
            
    def push_screen(self, name: str, *args, **kwargs) -> None:
        """Push a screen onto the stack.
        
        Args:
            name: Name of the screen to push
            *args: Additional arguments for screen initialization
            **kwargs: Additional keyword arguments for screen initialization
        """
        try:
            if name not in self.screens:
                raise ValueError(f"Screen {name} not registered")
                
            # Pause current screen
            if self.current_screen:
                self.current_screen.pause()
                
            # Create new screen instance
            self.current_screen = self.screens[name](*args, **kwargs)
            self.current_screen.initialize()
            
            # Update screen stack
            self.screen_stack.append(name)
            
            logger.debug(f"Pushed screen: {name}")
            
        except Exception as e:
            handle_component_error(
                "ScreenManager",
                "push_screen",
                e,
                ErrorSeverity.ERROR,
                {"screen_name": name}
            )
            
    def pop_screen(self) -> None:
        """Pop the current screen from the stack."""
        try:
            if len(self.screen_stack) <= 1:
                raise ValueError("Cannot pop the last screen")
                
            # Clean up current screen
            if self.current_screen:
                self.current_screen.cleanup()
                
            # Pop screen from stack
            self.screen_stack.pop()
            
            # Create previous screen instance
            prev_name = self.screen_stack[-1]
            self.current_screen = self.screens[prev_name]()
            self.current_screen.initialize()
            self.current_screen.resume()
            
            logger.debug(f"Popped screen, returned to: {prev_name}")
            
        except Exception as e:
            handle_component_error(
                "ScreenManager",
                "pop_screen",
                e,
                ErrorSeverity.ERROR
            )
            
    def update(self, dt: int) -> None:
        """Update the current screen.
        
        Args:
            dt: Time elapsed since last update
        """
        try:
            if self.current_screen:
                self.current_screen.update(dt)
                
        except Exception as e:
            handle_component_error(
                "ScreenManager",
                "update",
                e,
                ErrorSeverity.ERROR,
                {"dt": dt}
            )
            
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the current screen.
        
        Args:
            surface: Surface to draw on
        """
        try:
            if self.current_screen:
                self.current_screen.draw(surface)
                
        except Exception as e:
            handle_component_error(
                "ScreenManager",
                "draw",
                e,
                ErrorSeverity.ERROR
            )
            
    def update_responsive_properties(self) -> None:
        """Update responsive properties of the current screen."""
        try:
            if self.current_screen:
                self.current_screen._update_responsive_properties()
                
        except Exception as e:
            handle_component_error(
                "ScreenManager",
                "update_responsive_properties",
                e,
                ErrorSeverity.ERROR
            )
            
    def cleanup(self) -> None:
        """Clean up all screens."""
        try:
            if self.current_screen:
                self.current_screen.cleanup()
                
            self.screens.clear()
            self.screen_stack.clear()
            self.current_screen = None
            
            logger.debug("Cleaned up all screens")
            
        except Exception as e:
            handle_component_error(
                "ScreenManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            ) 