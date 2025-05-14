"""
Settings screen module.
"""

import pygame
from typing import Optional, Dict, Any
from core.screen import Screen
from core.ui.button import Button
from core.ui.text import Text
from core.ui.layout import Layout

class SettingsScreen(Screen):
    """Settings screen."""
    
    def __init__(self, app):
        """Initialize the settings screen."""
        super().__init__(app)
        self.title = Text("Settings", 48, (255, 255, 255))
        self.back_button = Button("Back to Menu", lambda: self.app.set_screen('main_menu'))
        
        # Create layout
        self.layout = Layout()
        self.layout.add(self.title, "center", 0.2)
        self.layout.add(self.back_button, "center", 0.8)
    
    def update(self, dt: float) -> None:
        """Update the screen."""
        self.layout.update(dt)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the screen."""
        surface.fill((40, 44, 52))  # Dark background
        self.layout.draw(surface)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event."""
        return self.layout.handle_event(event) 