"""
TextArea UI component for multi-line text input.
"""

import pygame
from typing import Optional, Tuple
from .component import UIComponent

class TextArea(UIComponent):
    """TextArea UI component."""
    
    def __init__(
        self,
        default_text: str = "",
        size: Tuple[int, int] = (400, 200),
        position: Tuple[int, int] = (0, 0),
        color: Tuple[int, int, int] = (255, 255, 255),
        background_color: Tuple[int, int, int] = (40, 44, 52),
        border_color: Tuple[int, int, int] = (70, 70, 70),
        text_color: Tuple[int, int, int] = (255, 255, 255)
    ):
        """Initialize the text area.
        
        Args:
            default_text: Default text
            size: Text area size
            position: Text area position
            color: Text area color
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
        self.line_height = self.font.get_linesize()
        self.padding = 5
        self.scroll_y = 0
        
    def update(self, dt: float) -> None:
        """Update the text area."""
        # Update cursor blink
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:  # Blink every 0.5 seconds
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the text area."""
        # Draw background
        pygame.draw.rect(surface, self.background_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        # Create a clipping area
        clip_rect = pygame.Rect(
            self.rect.x + self.padding,
            self.rect.y + self.padding,
            self.rect.width - 2 * self.padding,
            self.rect.height - 2 * self.padding
        )
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        
        # Draw text
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, self.text_color)
            text_rect = text_surface.get_rect(
                left=self.rect.x + self.padding,
                top=self.rect.y + self.padding + i * self.line_height - self.scroll_y
            )
            surface.blit(text_surface, text_rect)
        
        # Draw cursor if active
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + self.padding
            cursor_y = self.rect.y + self.padding + len(lines) * self.line_height - self.scroll_y
            pygame.draw.line(
                surface,
                self.text_color,
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + self.line_height)
            )
        
        # Restore clipping area
        surface.set_clip(old_clip)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return True
            
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.text += '\n'
            elif event.key == pygame.K_TAB:
                self.text += '    '  # 4 spaces for tab
            else:
                self.text += event.unicode
            return True
            
        return False 