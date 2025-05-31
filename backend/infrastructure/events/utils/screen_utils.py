"""
Screen management utilities for the Visual DM game client.
"""

import pygame
from typing import Dict, Optional, Any
from backend.infrastructure.events.utils.error_utils import ScreenError, handle_error

class ScreenManager:
    """Manages screen transitions and state."""
    
    def __init__(self, width: int, height: int, title: str = "Visual DM"):
        """Initialize the screen manager.
        
        Args:
            width: Screen width
            height: Screen height
            title: Window title
        """
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption(title)
            self.current_screen = None
            self.screens: Dict[str, Any] = {}
            self.fullscreen = False
        except Exception as e:
            handle_error(e, {"width": width, "height": height, "title": title})
            raise ScreenError("Failed to initialize screen manager")
            
    def add_screen(self, name: str, screen: Any) -> None:
        """Add a screen to the manager.
        
        Args:
            name: Screen identifier
            screen: Screen instance
        """
        try:
            self.screens[name] = screen
        except Exception as e:
            handle_error(e, {"name": name})
            
    def set_screen(self, name: str) -> None:
        """Set the current screen.
        
        Args:
            name: Screen identifier
        """
        try:
            if name in self.screens:
                self.current_screen = self.screens[name]
            else:
                raise ScreenError(f"Screen not found: {name}")
        except Exception as e:
            handle_error(e, {"name": name})
            
    def get_screen_rect(self) -> pygame.Rect:
        """Get the screen rectangle.
        
        Returns:
            pygame.Rect: Screen rectangle
        """
        return self.screen.get_rect()
        
    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        try:
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode((800, 600))
        except Exception as e:
            handle_error(e)
            
    def update(self, dt: float) -> None:
        """Update the current screen.
        
        Args:
            dt: Time since last update in seconds
        """
        try:
            if self.current_screen:
                self.current_screen.update(dt)
        except Exception as e:
            handle_error(e)
            
    def draw(self) -> None:
        """Draw the current screen."""
        try:
            if self.current_screen:
                self.current_screen.draw(self.screen)
            pygame.display.flip()
        except Exception as e:
            handle_error(e)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events.
        
        Args:
            event: Event to handle
            
        Returns:
            bool: True if event was handled
        """
        try:
            if self.current_screen:
                return self.current_screen.handle_event(event)
            return False
        except Exception as e:
            handle_error(e, {"event": str(event)})
            return False
            
    def quit(self) -> None:
        """Quit the game."""
        try:
            pygame.quit()
        except Exception as e:
            handle_error(e) 