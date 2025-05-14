"""
Button component.
Provides interactive button functionality.
"""

from typing import Optional, Callable, Tuple
import pygame
from app.core.components.base import BaseComponent
from app.core.utils.event_utils import EventUtils

class Button(BaseComponent):
    """Interactive button component."""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(x, y, width, height, **kwargs)
        self._text = text
        self._on_click = on_click
        self._hovered = False
        self._pressed = False
        self._normal_color = kwargs.get('background_color', (70, 70, 70))
        self._hover_color = kwargs.get('hover_color', (90, 90, 90))
        self._pressed_color = kwargs.get('pressed_color', (50, 50, 50))
        self._text_color = kwargs.get('text_color', (255, 255, 255))
        self._font = kwargs.get('font', pygame.font.Font(None, 24))
        self._border_radius = kwargs.get('border_radius', 5)
        self._update_text_surface()

    def _update_text_surface(self) -> None:
        """Update the text surface when text properties change."""
        self._text_surface = self._font.render(self._text, True, self._text_color)
        self._text_rect = self._text_surface.get_rect(center=self.rect.center)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button on the given surface."""
        if not self.visible:
            return

        # Draw background
        color = self._pressed_color if self._pressed else self._hover_color if self._hovered else self._normal_color
        pygame.draw.rect(surface, color, self.rect, border_radius=self._border_radius)

        # Draw border
        if self._border_color and self._border_width > 0:
            pygame.draw.rect(surface, self._border_color, self.rect, self._border_width, border_radius=self._border_radius)

        # Draw text
        if self._text_surface:
            surface.blit(self._text_surface, self._text_rect)

    def update(self) -> None:
        """Update the button's state."""
        if not self.enabled:
            self._hovered = False
            self._pressed = False
            return

        mouse_pos = pygame.mouse.get_pos()
        self._hovered = self.rect.collidepoint(mouse_pos)

        if self._hovered and pygame.mouse.get_pressed()[0]:
            self._pressed = True
        else:
            self._pressed = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle a pygame event."""
        if not self.enabled or not self.visible:
            return False

        # Handle mouse motion
        if EventUtils.handle_mouse_motion(
            self,
            event,
            on_hover_enter=lambda _: setattr(self, '_hovered', True),
            on_hover_leave=lambda _: setattr(self, '_hovered', False)
        ):
            return True

        # Handle mouse button
        if EventUtils.handle_mouse_button(
            self,
            event,
            on_click=self._on_click,
            on_press=lambda _: setattr(self, '_pressed', True),
            on_release=lambda _: setattr(self, '_pressed', False)
        ):
            return True

        return False

    def set_text(self, text: str) -> None:
        """Set the button's text."""
        self._text = text
        self._update_text_surface()

    def set_on_click(self, callback: Optional[Callable]) -> None:
        """Set the click handler."""
        self._on_click = callback

    def set_colors(
        self,
        normal: Optional[Tuple[int, int, int]] = None,
        hover: Optional[Tuple[int, int, int]] = None,
        pressed: Optional[Tuple[int, int, int]] = None
    ) -> None:
        """Set the button's colors."""
        if normal:
            self._normal_color = normal
        if hover:
            self._hover_color = hover
        if pressed:
            self._pressed_color = pressed 