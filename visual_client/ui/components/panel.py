"""
Reusable panel component for UI screens.
"""

import pygame
from typing import Tuple, Optional, List, Any
from dataclasses import dataclass
import logging

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class PanelConfig:
    """Configuration for the panel."""
    position: Tuple[int, int]
    width: int
    height: int
    background_color: Optional[Tuple[int, int, int]] = None
    border_color: Optional[Tuple[int, int, int]] = None
    border_width: int = 0
    padding: int = 5
    title: Optional[str] = None
    title_font_size: int = 24
    title_color: Tuple[int, int, int] = (255, 255, 255)

class Panel:
    """Reusable panel component."""
    
    def __init__(self, screen: pygame.Surface, config: PanelConfig):
        """Initialize the panel.
        
        Args:
            screen: The pygame surface to draw on
            config: Panel configuration
        """
        self.screen = screen
        self.config = config
        
        # Initialize font for title
        self.title_font = pygame.font.SysFont(None, config.title_font_size)
        
        # Create rect
        self.rect = pygame.Rect(
            config.position[0],
            config.position[1],
            config.width,
            config.height
        )
        
        # Initialize components list
        self.components: List[Any] = []
        
        self.dirty = True
        
    def draw(self) -> None:
        """Draw the panel and its components."""
        if not self.dirty:
            return
            
        try:
            # Draw background if specified
            if self.config.background_color:
                pygame.draw.rect(self.screen, self.config.background_color, self.rect)
                
            # Draw border if specified
            if self.config.border_color and self.config.border_width > 0:
                pygame.draw.rect(
                    self.screen,
                    self.config.border_color,
                    self.rect,
                    self.config.border_width
                )
                
            # Draw title if specified
            if self.config.title:
                title_surface = self.title_font.render(
                    self.config.title,
                    True,
                    self.config.title_color
                )
                title_rect = title_surface.get_rect()
                title_rect.midtop = (
                    self.rect.centerx,
                    self.rect.top + self.config.padding
                )
                self.screen.blit(title_surface, title_rect)
                
            # Draw components
            for component in self.components:
                if hasattr(component, 'draw'):
                    component.draw()
                    
            self.dirty = False
            
        except Exception as e:
            logger.error(f"Error drawing panel: {str(e)}")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        try:
            # Check if event is within panel bounds
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                if not self.rect.collidepoint(event.pos):
                    return False
                    
            # Pass event to components
            for component in self.components:
                if hasattr(component, 'handle_event'):
                    if component.handle_event(event):
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error handling panel event: {str(e)}")
            return False
            
    def add_component(self, component: Any) -> None:
        """Add a component to the panel.
        
        Args:
            component: The component to add
        """
        self.components.append(component)
        self.dirty = True
        
    def remove_component(self, component: Any) -> None:
        """Remove a component from the panel.
        
        Args:
            component: The component to remove
        """
        if component in self.components:
            self.components.remove(component)
            self.dirty = True
            
    def clear_components(self) -> None:
        """Remove all components from the panel."""
        self.components.clear()
        self.dirty = True
        
    def set_title(self, title: Optional[str]) -> None:
        """Set the panel title.
        
        Args:
            title: The new title or None to remove title
        """
        if title != self.config.title:
            self.config.title = title
            self.dirty = True
            
    def set_background(self, color: Optional[Tuple[int, int, int]]) -> None:
        """Set the background color.
        
        Args:
            color: The new background color or None to remove background
        """
        if color != self.config.background_color:
            self.config.background_color = color
            self.dirty = True
            
    def set_border(self, color: Optional[Tuple[int, int, int]], width: int = 1) -> None:
        """Set the border.
        
        Args:
            color: The new border color or None to remove border
            width: The border width
        """
        if color != self.config.border_color or width != self.config.border_width:
            self.config.border_color = color
            self.config.border_width = width
            self.dirty = True
            
    def set_padding(self, padding: int) -> None:
        """Set the padding.
        
        Args:
            padding: The new padding value
        """
        if padding != self.config.padding:
            self.config.padding = padding
            self.dirty = True 