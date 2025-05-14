"""
Base component class.
Provides common functionality for all UI components.
"""

from typing import Optional, Dict, Any, Callable
import pygame
from abc import ABC, abstractmethod

class BaseComponent(ABC):
    """Base class for all UI components."""
    
    def __init__(self, x: int, y: int, width: int, height: int, **kwargs):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = kwargs.get('visible', True)
        self.enabled = kwargs.get('enabled', True)
        self._text = kwargs.get('text', '')
        self._font = kwargs.get('font', pygame.font.Font(None, 24))
        self._text_color = kwargs.get('text_color', (0, 0, 0))
        self._background_color = kwargs.get('background_color', None)
        self._border_color = kwargs.get('border_color', None)
        self._border_width = kwargs.get('border_width', 0)
        self._padding = kwargs.get('padding', 5)
        self._on_click = kwargs.get('on_click', None)
        self._on_hover = kwargs.get('on_hover', None)
        self._tooltip = kwargs.get('tooltip', None)
        self._data = kwargs.get('data', {})

    def set_text(self, text: str) -> None:
        """Set the text content of the component."""
        self._text = text
        self._update_text_surface()

    def get_text(self) -> str:
        """Get the text content of the component."""
        return self._text

    def set_font(self, font: pygame.font.Font) -> None:
        """Set the font for the component."""
        self._font = font
        self._update_text_surface()

    def set_text_color(self, color: tuple) -> None:
        """Set the text color."""
        self._text_color = color
        self._update_text_surface()

    def set_background_color(self, color: Optional[tuple]) -> None:
        """Set the background color."""
        self._background_color = color

    def set_border(self, color: Optional[tuple], width: int = 1) -> None:
        """Set the border properties."""
        self._border_color = color
        self._border_width = width

    def set_padding(self, padding: int) -> None:
        """Set the padding around the content."""
        self._padding = padding
        self._update_layout()

    def set_tooltip(self, tooltip: Optional[str]) -> None:
        """Set the tooltip text."""
        self._tooltip = tooltip

    def set_data(self, data: Dict[str, Any]) -> None:
        """Set additional data for the component."""
        self._data = data

    def get_data(self) -> Dict[str, Any]:
        """Get the component's data."""
        return self._data

    def set_on_click(self, callback: Optional[Callable]) -> None:
        """Set the click handler."""
        self._on_click = callback

    def set_on_hover(self, callback: Optional[Callable]) -> None:
        """Set the hover handler."""
        self._on_hover = callback

    def show(self) -> None:
        """Show the component."""
        self.visible = True

    def hide(self) -> None:
        """Hide the component."""
        self.visible = False

    def enable(self) -> None:
        """Enable the component."""
        self.enabled = True

    def disable(self) -> None:
        """Disable the component."""
        self.enabled = False

    def is_visible(self) -> bool:
        """Check if the component is visible."""
        return self.visible

    def is_enabled(self) -> bool:
        """Check if the component is enabled."""
        return self.enabled

    def contains_point(self, point: tuple) -> bool:
        """Check if a point is within the component's bounds."""
        return self.rect.collidepoint(point)

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the component on the given surface."""
        pass

    @abstractmethod
    def update(self) -> None:
        """Update the component's state."""
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle a pygame event."""
        pass

    def _update_text_surface(self) -> None:
        """Update the text surface when text properties change."""
        pass

    def _update_layout(self) -> None:
        """Update the component's layout when properties change."""
        pass 