"""
Text UI component.
"""

import pygame
from typing import Optional, Tuple, Union, List
from .component import UIComponent

class Text(UIComponent):
    """Text UI component."""
    
    def __init__(
        self,
        text: str,
        size: int = 32,
        color: Union[Tuple[int, int, int], List[int]] = (255, 255, 255),
        position: Tuple[int, int] = (0, 0)
    ):
        """Initialize the text.
        
        Args:
            text: Text to display
            size: Font size
            color: Text color (RGB tuple or list)
            position: Text position
        """
        # Validate and convert color
        if isinstance(color, list):
            color = tuple(color)
        if not isinstance(color, tuple) or len(color) != 3:
            color = (255, 255, 255)  # Default to white if invalid
            
        # Create font and get text size
        self.font = pygame.font.Font(None, size)
        self.text_surface = self.font.render(text, True, color)
        size = self.text_surface.get_size()
        
        super().__init__(position, size)
        self.text = text
        self.color = color
        
    def update(self, dt: float) -> None:
        """Update the text."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the text."""
        surface.blit(self.text_surface, self.rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event."""
        return False 