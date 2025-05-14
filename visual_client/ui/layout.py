"""
Layout UI component for organizing other components.
"""

import pygame
from typing import Optional, Dict, Any, List
from .component import UIComponent

class Layout(UIComponent):
    """Layout UI component."""
    
    def __init__(self, position: tuple = (0, 0), size: tuple = (0, 0)):
        """Initialize the layout."""
        super().__init__(position, size)
        self.components: List[tuple] = []  # (component, alignment, y_position)
        
    def add(self, component: UIComponent, alignment: str = "left", y_position: float = 0.0) -> None:
        """Add a component to the layout.
        
        Args:
            component: Component to add
            alignment: Component alignment ("left", "center", "right")
            y_position: Vertical position (0.0 to 1.0)
        """
        self.components.append((component, alignment, y_position))
        
    def update(self, dt: float) -> None:
        """Update the layout and its components."""
        for component, _, _ in self.components:
            component.update(dt)
            
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the layout and its components."""
        for component, alignment, y_position in self.components:
            # Calculate position
            x = 0
            if alignment == "center":
                x = (surface.get_width() - component.rect.width) // 2
            elif alignment == "right":
                x = surface.get_width() - component.rect.width
                
            y = int(surface.get_height() * y_position)
            
            # Update component position
            component.rect.x = x
            component.rect.y = y
            
            # Draw component
            component.draw(surface)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event."""
        for component, _, _ in reversed(self.components):
            if component.handle_event(event):
                return True
        return False 