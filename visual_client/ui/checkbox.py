"""
Checkbox UI component for boolean selection.
"""

import pygame
from typing import Optional, Tuple
from .component import UIComponent

class Checkbox(UIComponent):
    """Checkbox UI component."""
    
    def __init__(
        self,
        label: str,
        size: Tuple[int, int] = (200, 30),
        position: Tuple[int, int] = (0, 0),
        color: Tuple[int, int, int] = (255, 255, 255),
        background_color: Tuple[int, int, int] = (40, 44, 52),
        border_color: Tuple[int, int, int] = (70, 70, 70),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        hover_color: Tuple[int, int, int] = (90, 90, 90)
    ):
        """Initialize the checkbox.
        
        Args:
            label: Checkbox label
            size: Checkbox size
            position: Checkbox position
            color: Checkbox color
            background_color: Background color
            border_color: Border color
            text_color: Text color
            hover_color: Hover color
        """
        super().__init__(position, size)
        self.label = label
        self.color = color
        self.background_color = background_color
        self.border_color = border_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.checked = False
        self.font = pygame.font.Font(None, 24)
        
    def update(self, dt: float) -> None:
        """Update the checkbox."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the checkbox."""
        # Draw checkbox box
        box_size = 20
        box_rect = pygame.Rect(
            self.rect.x,
            self.rect.centery - box_size // 2,
            box_size,
            box_size
        )
        
        # Draw background
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.background_color
        pygame.draw.rect(surface, color, box_rect)
        pygame.draw.rect(surface, self.border_color, box_rect, 2)
        
        # Draw checkmark if checked
        if self.checked:
            check_points = [
                (box_rect.left + 5, box_rect.centery),
                (box_rect.centerx - 2, box_rect.bottom - 5),
                (box_rect.right - 5, box_rect.top + 5)
            ]
            pygame.draw.lines(surface, self.color, False, check_points, 2)
        
        # Draw label
        text_surface = self.font.render(self.label, True, self.text_color)
        text_rect = text_surface.get_rect(
            left=box_rect.right + 10,
            centery=box_rect.centery
        )
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True
                
        return False 