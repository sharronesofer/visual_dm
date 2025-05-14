"""
Dropdown UI component for selection menus.
"""

import pygame
from typing import Optional, Tuple, List
from .component import UIComponent

class Dropdown(UIComponent):
    """Dropdown UI component."""
    
    def __init__(
        self,
        options: List[str],
        size: Tuple[int, int] = (200, 30),
        position: Tuple[int, int] = (0, 0),
        color: Tuple[int, int, int] = (255, 255, 255),
        background_color: Tuple[int, int, int] = (40, 44, 52),
        border_color: Tuple[int, int, int] = (70, 70, 70),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        hover_color: Tuple[int, int, int] = (90, 90, 90)
    ):
        """Initialize the dropdown.
        
        Args:
            options: List of options
            size: Dropdown size
            position: Dropdown position
            color: Dropdown color
            background_color: Background color
            border_color: Border color
            text_color: Text color
            hover_color: Hover color
        """
        super().__init__(position, size)
        self.options = options
        self.value = options[0] if options else ""
        self.color = color
        self.background_color = background_color
        self.border_color = border_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.expanded = False
        self.hovered_option = None
        self.font = pygame.font.Font(None, 24)
        
    def update(self, dt: float) -> None:
        """Update the dropdown."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the dropdown."""
        # Draw main button
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surface, self.background_color, self.rect)
        pygame.draw.rect(surface, color, self.rect, 2)
        
        # Draw text
        text_surface = self.font.render(self.value, True, self.text_color)
        text_rect = text_surface.get_rect(
            left=self.rect.left + 5,
            centery=self.rect.centery
        )
        surface.blit(text_surface, text_rect)
        
        # Draw dropdown arrow
        arrow_points = [
            (self.rect.right - 10, self.rect.centery - 5),
            (self.rect.right - 10, self.rect.centery + 5),
            (self.rect.right - 5, self.rect.centery)
        ]
        pygame.draw.polygon(surface, self.text_color, arrow_points)
        
        # Draw expanded options if expanded
        if self.expanded:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.rect.height * (i + 1),
                    self.rect.width,
                    self.rect.height
                )
                
                # Draw option background
                color = self.hover_color if option_rect.collidepoint(pygame.mouse.get_pos()) else self.background_color
                pygame.draw.rect(surface, color, option_rect)
                pygame.draw.rect(surface, self.border_color, option_rect, 1)
                
                # Draw option text
                text_surface = self.font.render(option, True, self.text_color)
                text_rect = text_surface.get_rect(
                    left=option_rect.left + 5,
                    centery=option_rect.centery
                )
                surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return True
                
            elif self.expanded:
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(
                        self.rect.x,
                        self.rect.y + self.rect.height * (i + 1),
                        self.rect.width,
                        self.rect.height
                    )
                    if option_rect.collidepoint(event.pos):
                        self.value = option
                        self.expanded = False
                        return True
                        
                # Click outside expanded dropdown
                self.expanded = False
                return True
                
        return False 