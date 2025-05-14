"""
Rendering utilities for the Visual DM game client.
"""

import pygame
from typing import Tuple, Optional, Dict, Any
from .error_utils import handle_error

class Renderer:
    """Handles rendering operations."""
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the renderer.
        
        Args:
            screen: Pygame surface to render to
        """
        self.screen = screen
        self.font_cache: Dict[Tuple[int, str], pygame.font.Font] = {}
        
    def get_font(self, size: int, name: Optional[str] = None) -> pygame.font.Font:
        """Get a font from cache or create a new one.
        
        Args:
            size: Font size
            name: Font name (optional)
            
        Returns:
            pygame.font.Font: The requested font
        """
        try:
            key = (size, name or "")
            if key not in self.font_cache:
                self.font_cache[key] = pygame.font.SysFont(name, size)
            return self.font_cache[key]
        except Exception as e:
            handle_error(e, {"size": size, "name": name})
            return pygame.font.SysFont(None, size)
            
    def draw_text(
        self,
        text: str,
        position: Tuple[int, int],
        size: int = 24,
        color: Tuple[int, int, int] = (255, 255, 255),
        name: Optional[str] = None,
        antialias: bool = True
    ) -> None:
        """Draw text on the screen.
        
        Args:
            text: Text to draw
            position: (x, y) position
            size: Font size
            color: Text color
            name: Font name (optional)
            antialias: Whether to use antialiasing
        """
        try:
            font = self.get_font(size, name)
            surface = font.render(text, antialias, color)
            self.screen.blit(surface, position)
        except Exception as e:
            handle_error(e, {
                "text": text,
                "position": position,
                "size": size,
                "color": color,
                "name": name
            })
            
    def draw_rect(
        self,
        rect: pygame.Rect,
        color: Tuple[int, int, int],
        width: int = 0
    ) -> None:
        """Draw a rectangle.
        
        Args:
            rect: Rectangle to draw
            color: Fill color
            width: Border width (0 for filled)
        """
        try:
            pygame.draw.rect(self.screen, color, rect, width)
        except Exception as e:
            handle_error(e, {"rect": str(rect), "color": color, "width": width})
            
    def draw_circle(
        self,
        center: Tuple[int, int],
        radius: int,
        color: Tuple[int, int, int],
        width: int = 0
    ) -> None:
        """Draw a circle.
        
        Args:
            center: (x, y) center position
            radius: Circle radius
            color: Fill color
            width: Border width (0 for filled)
        """
        try:
            pygame.draw.circle(self.screen, color, center, radius, width)
        except Exception as e:
            handle_error(e, {"center": center, "radius": radius, "color": color, "width": width})
            
    def draw_line(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
        color: Tuple[int, int, int],
        width: int = 1
    ) -> None:
        """Draw a line.
        
        Args:
            start: (x, y) start position
            end: (x, y) end position
            color: Line color
            width: Line width
        """
        try:
            pygame.draw.line(self.screen, color, start, end, width)
        except Exception as e:
            handle_error(e, {"start": start, "end": end, "color": color, "width": width})
            
    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Clear the screen.
        
        Args:
            color: Background color
        """
        try:
            self.screen.fill(color)
        except Exception as e:
            handle_error(e, {"color": color}) 