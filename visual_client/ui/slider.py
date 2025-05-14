"""
Slider UI component for numeric input.
"""

import pygame
from typing import Optional, Tuple
from .component import UIComponent

class Slider(UIComponent):
    """Slider UI component."""
    
    def __init__(
        self,
        min_value: int,
        max_value: int,
        default_value: int,
        size: Tuple[int, int] = (200, 30),
        position: Tuple[int, int] = (0, 0),
        color: Tuple[int, int, int] = (255, 255, 255),
        background_color: Tuple[int, int, int] = (40, 44, 52),
        border_color: Tuple[int, int, int] = (70, 70, 70),
        text_color: Tuple[int, int, int] = (255, 255, 255)
    ):
        """Initialize the slider.
        
        Args:
            min_value: Minimum value
            max_value: Maximum value
            default_value: Default value
            size: Slider size
            position: Slider position
            color: Slider color
            background_color: Background color
            border_color: Border color
            text_color: Text color
        """
        super().__init__(position, size)
        self.min_value = min_value
        self.max_value = max_value
        self.value = default_value
        self.color = color
        self.background_color = background_color
        self.border_color = border_color
        self.text_color = text_color
        self.dragging = False
        self.font = pygame.font.Font(None, 24)
        
    def update(self, dt: float) -> None:
        """Update the slider."""
        if self.dragging:
            mouse_x = pygame.mouse.get_pos()[0]
            # Calculate value based on mouse position
            relative_x = mouse_x - self.rect.x
            percentage = max(0, min(1, relative_x / self.rect.width))
            self.value = int(self.min_value + percentage * (self.max_value - self.min_value))
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the slider."""
        # Draw background
        pygame.draw.rect(surface, self.background_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        # Draw filled portion
        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        filled_width = int(self.rect.width * percentage)
        filled_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            filled_width,
            self.rect.height
        )
        pygame.draw.rect(surface, self.color, filled_rect)
        
        # Draw handle
        handle_x = self.rect.x + filled_width
        handle_rect = pygame.Rect(
            handle_x - 5,
            self.rect.y - 5,
            10,
            self.rect.height + 10
        )
        pygame.draw.rect(surface, self.color, handle_rect)
        pygame.draw.rect(surface, self.border_color, handle_rect, 2)
        
        # Draw value
        value_text = str(self.value)
        text_surface = self.font.render(value_text, True, self.text_color)
        text_rect = text_surface.get_rect(
            centerx=handle_rect.centerx,
            top=handle_rect.bottom + 5
        )
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            return True
            
        return False 