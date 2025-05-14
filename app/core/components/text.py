"""
Base text component class.
Provides common functionality for text-based components.
"""

from typing import Optional, Tuple
import pygame
from app.core.components.base import BaseComponent

class TextComponent(BaseComponent):
    """Base class for text-based components."""
    
    def __init__(self, x: int, y: int, width: int, height: int, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        self._text_surface: Optional[pygame.Surface] = None
        self._text_rect: Optional[pygame.Rect] = None
        self._alignment = kwargs.get('alignment', 'left')  # left, center, right
        self._vertical_alignment = kwargs.get('vertical_alignment', 'top')  # top, middle, bottom
        self._wrap_text = kwargs.get('wrap_text', True)
        self._max_lines = kwargs.get('max_lines', 0)  # 0 for unlimited
        self._line_height = kwargs.get('line_height', self._font.get_linesize())
        self._update_text_surface()

    def _update_text_surface(self) -> None:
        """Update the text surface when text properties change."""
        if not self._text:
            self._text_surface = None
            self._text_rect = None
            return

        # Split text into lines if wrapping is enabled
        if self._wrap_text:
            words = self._text.split()
            lines = []
            current_line = []
            current_width = 0
            max_width = self.rect.width - (2 * self._padding)

            for word in words:
                word_surface = self._font.render(word, True, self._text_color)
                word_width = word_surface.get_width()

                if current_width + word_width <= max_width:
                    current_line.append(word)
                    current_width += word_width + self._font.size(' ')[0]
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                    current_width = word_width

            if current_line:
                lines.append(' '.join(current_line))

            # Limit number of lines if specified
            if self._max_lines > 0:
                lines = lines[:self._max_lines]
        else:
            lines = [self._text]

        # Create text surface
        line_surfaces = [self._font.render(line, True, self._text_color) for line in lines]
        max_line_width = max(surface.get_width() for surface in line_surfaces)
        total_height = len(lines) * self._line_height

        self._text_surface = pygame.Surface((max_line_width, total_height), pygame.SRCALPHA)
        self._text_rect = self._text_surface.get_rect()

        # Position text based on alignment
        for i, line_surface in enumerate(line_surfaces):
            y = i * self._line_height
            if self._alignment == 'left':
                x = 0
            elif self._alignment == 'center':
                x = (max_line_width - line_surface.get_width()) // 2
            else:  # right
                x = max_line_width - line_surface.get_width()
            self._text_surface.blit(line_surface, (x, y))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the text component."""
        if not self.visible:
            return

        # Draw background
        if self._background_color:
            pygame.draw.rect(surface, self._background_color, self.rect)

        # Draw border
        if self._border_color and self._border_width > 0:
            pygame.draw.rect(surface, self._border_color, self.rect, self._border_width)

        # Draw text
        if self._text_surface:
            # Calculate text position based on vertical alignment
            if self._vertical_alignment == 'top':
                y = self.rect.y + self._padding
            elif self._vertical_alignment == 'middle':
                y = self.rect.y + (self.rect.height - self._text_rect.height) // 2
            else:  # bottom
                y = self.rect.y + self.rect.height - self._text_rect.height - self._padding

            # Calculate text position based on horizontal alignment
            if self._alignment == 'left':
                x = self.rect.x + self._padding
            elif self._alignment == 'center':
                x = self.rect.x + (self.rect.width - self._text_rect.width) // 2
            else:  # right
                x = self.rect.x + self.rect.width - self._text_rect.width - self._padding

            surface.blit(self._text_surface, (x, y))

    def update(self) -> None:
        """Update the text component."""
        pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for the text component."""
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(event.pos):
                if self._on_click:
                    self._on_click()
                    return True

        elif event.type == pygame.MOUSEMOTION:
            if self.contains_point(event.pos):
                if self._on_hover:
                    self._on_hover(True)
                    return True
            else:
                if self._on_hover:
                    self._on_hover(False)
                    return True

        return False

    def set_alignment(self, alignment: str) -> None:
        """Set the text alignment."""
        self._alignment = alignment
        self._update_text_surface()

    def set_vertical_alignment(self, alignment: str) -> None:
        """Set the vertical text alignment."""
        self._vertical_alignment = alignment
        self._update_text_surface()

    def set_wrap_text(self, wrap: bool) -> None:
        """Set whether text should wrap."""
        self._wrap_text = wrap
        self._update_text_surface()

    def set_max_lines(self, max_lines: int) -> None:
        """Set the maximum number of lines."""
        self._max_lines = max_lines
        self._update_text_surface()

    def set_line_height(self, height: int) -> None:
        """Set the line height."""
        self._line_height = height
        self._update_text_surface() 