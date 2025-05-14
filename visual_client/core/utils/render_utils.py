"""
Rendering utilities for the Visual DM game client.
Uses standardized coordinate system for consistent rendering.
"""

import pygame
from typing import Tuple, Optional, Dict, Any, Union
from .error_utils import handle_error
from .coordinates import GlobalCoord, LocalCoord
from . import coordinate_utils as cu

class Renderer:
    """Handles rendering operations with coordinate system awareness."""
    
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
        position: Union[Tuple[int, int], GlobalCoord, LocalCoord],
        size: int = 24,
        color: Tuple[int, int, int] = (255, 255, 255),
        name: Optional[str] = None,
        antialias: bool = True
    ) -> None:
        """Draw text on the screen.
        
        Args:
            text: Text to draw
            position: Position as tuple or coordinate object
            size: Font size
            color: Text color
            name: Font name (optional)
            antialias: Whether to use antialiasing
        """
        try:
            # Convert position to tuple if it's a coordinate object
            if isinstance(position, (GlobalCoord, LocalCoord)):
                pos = (int(position.x), int(position.y))
            else:
                pos = position
                
            font = self.get_font(size, name)
            surface = font.render(text, antialias, color)
            self.screen.blit(surface, pos)
        except Exception as e:
            handle_error(e, {
                "text": text,
                "position": str(position),
                "size": size,
                "color": color,
                "name": name
            })
            
    def draw_rect(
        self,
        rect: Union[pygame.Rect, Tuple[Union[int, float], Union[int, float], Union[int, float], Union[int, float]]],
        color: Tuple[int, int, int],
        width: int = 0
    ) -> None:
        """Draw a rectangle.
        
        Args:
            rect: Rectangle as pygame.Rect or (x, y, width, height)
            color: Fill color
            width: Border width (0 for filled)
        """
        try:
            # Convert tuple to Rect if needed
            if not isinstance(rect, pygame.Rect):
                rect = pygame.Rect(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
            pygame.draw.rect(self.screen, color, rect, width)
        except Exception as e:
            handle_error(e, {"rect": str(rect), "color": color, "width": width})
            
    def draw_circle(
        self,
        center: Union[Tuple[int, int], GlobalCoord, LocalCoord],
        radius: int,
        color: Tuple[int, int, int],
        width: int = 0
    ) -> None:
        """Draw a circle.
        
        Args:
            center: Center position as tuple or coordinate object
            radius: Circle radius
            color: Fill color
            width: Border width (0 for filled)
        """
        try:
            # Convert position to tuple if it's a coordinate object
            if isinstance(center, (GlobalCoord, LocalCoord)):
                center_pos = (int(center.x), int(center.y))
            else:
                center_pos = center
                
            pygame.draw.circle(self.screen, color, center_pos, radius, width)
        except Exception as e:
            handle_error(e, {"center": str(center), "radius": radius, "color": color, "width": width})
            
    def draw_line(
        self,
        start: Union[Tuple[int, int], GlobalCoord, LocalCoord],
        end: Union[Tuple[int, int], GlobalCoord, LocalCoord],
        color: Tuple[int, int, int],
        width: int = 1
    ) -> None:
        """Draw a line.
        
        Args:
            start: Start position as tuple or coordinate object
            end: End position as tuple or coordinate object
            color: Line color
            width: Line width
        """
        try:
            # Convert positions to tuples if they're coordinate objects
            if isinstance(start, (GlobalCoord, LocalCoord)):
                start_pos = (int(start.x), int(start.y))
            else:
                start_pos = start
                
            if isinstance(end, (GlobalCoord, LocalCoord)):
                end_pos = (int(end.x), int(end.y))
            else:
                end_pos = end
                
            pygame.draw.line(self.screen, color, start_pos, end_pos, width)
        except Exception as e:
            handle_error(e, {"start": str(start), "end": str(end), "color": color, "width": width})
    
    def draw_polygon(
        self,
        points: list[Union[Tuple[int, int], GlobalCoord, LocalCoord]],
        color: Tuple[int, int, int],
        width: int = 0
    ) -> None:
        """Draw a polygon.
        
        Args:
            points: List of points (vertices)
            color: Fill or line color
            width: Border width (0 for filled)
        """
        try:
            # Convert points to tuples if they're coordinate objects
            converted_points = []
            for point in points:
                if isinstance(point, (GlobalCoord, LocalCoord)):
                    converted_points.append((int(point.x), int(point.y)))
                else:
                    converted_points.append(point)
            
            pygame.draw.polygon(self.screen, color, converted_points, width)
        except Exception as e:
            handle_error(e, {"points": str(points), "color": color, "width": width})
            
    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Clear the screen.
        
        Args:
            color: Background color
        """
        try:
            self.screen.fill(color)
        except Exception as e:
            handle_error(e, {"color": color}) 