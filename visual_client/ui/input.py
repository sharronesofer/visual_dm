"""
Input UI component for text input.
"""

import pygame
from typing import Optional, Tuple
from .component import UIComponent

class Input(UIComponent):
    """Input UI component."""
    
    def __init__(
        self,
        default_text: str = "",
        size: Tuple[int, int] = (200, 30),
        position: Tuple[int, int] = (0, 0),
        color: Tuple[int, int, int] = (255, 255, 255),
        background_color: Tuple[int, int, int] = (40, 44, 52),
        border_color: Tuple[int, int, int] = (70, 70, 70),
        text_color: Tuple[int, int, int] = (255, 255, 255)
    ):
        """Initialize the input.
        
        Args:
            default_text: Default text
            size: Input size
            position: Input position
            color: Input color
            background_color: Background color
            border_color: Border color
            text_color: Text color
        """
        super().__init__(position, size)
        self.text = default_text
        self.color = color
        self.background_color = background_color
        self.border_color = border_color
        self.text_color = text_color
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = pygame.font.Font(None, 24)
        
    def update(self, dt: float) -> None:
        """Update the input."""
        # Update cursor blink
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:  # Blink every 0.5 seconds
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the input."""
        # Draw background
        pygame.draw.rect(surface, self.background_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(
            left=self.rect.left + 5,
            centery=self.rect.centery
        )
        surface.blit(text_surface, text_rect)
        
        # Draw cursor if active
        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            pygame.draw.line(
                surface,
                self.text_color,
                (cursor_x, self.rect.top + 5),
                (cursor_x, self.rect.bottom - 5)
            )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return True
            
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                self.text += event.unicode
            return True
            
        return False 