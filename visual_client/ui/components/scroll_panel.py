"""
Reusable scrollable panel component for UI screens.
"""

import pygame
from typing import Tuple, Optional, List, Any
from dataclasses import dataclass
import logging

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ScrollPanelConfig:
    """Configuration for the scroll panel."""
    position: Tuple[int, int]
    width: int
    height: int
    background_color: Optional[Tuple[int, int, int]] = None
    border_color: Optional[Tuple[int, int, int]] = None
    border_width: int = 0
    padding: int = 5
    scrollbar_width: int = 10
    scrollbar_color: Tuple[int, int, int] = (100, 100, 100)
    scrollbar_handle_color: Tuple[int, int, int] = (150, 150, 150)

class ScrollPanel:
    """Reusable scrollable panel component."""
    
    def __init__(self, screen: pygame.Surface, config: ScrollPanelConfig):
        """Initialize the scroll panel.
        
        Args:
            screen: The pygame surface to draw on
            config: Scroll panel configuration
        """
        self.screen = screen
        self.config = config
        
        # Create main panel rect
        self.rect = pygame.Rect(
            config.position[0],
            config.position[1],
            config.width,
            config.height
        )
        
        # Create content rect (larger than panel to allow scrolling)
        self.content_rect = pygame.Rect(
            0,
            0,
            config.width - config.scrollbar_width - config.padding,
            config.height
        )
        
        # Create scrollbar rect
        self.scrollbar_rect = pygame.Rect(
            config.position[0] + config.width - config.scrollbar_width,
            config.position[1],
            config.scrollbar_width,
            config.height
        )
        
        # Initialize components list
        self.components: List[Any] = []
        
        # Scroll state
        self.scroll_y = 0
        self.scroll_dragging = False
        self.scroll_drag_start = 0
        
        self.dirty = True
        
    def draw(self) -> None:
        """Draw the scroll panel and its components."""
        if not self.dirty:
            return
            
        try:
            # Create a surface for the content
            content_surface = pygame.Surface(
                (self.content_rect.width, self.content_rect.height),
                pygame.SRCALPHA
            )
            
            # Draw background if specified
            if self.config.background_color:
                pygame.draw.rect(content_surface, self.config.background_color, content_surface.get_rect())
                
            # Draw border if specified
            if self.config.border_color and self.config.border_width > 0:
                pygame.draw.rect(
                    content_surface,
                    self.config.border_color,
                    content_surface.get_rect(),
                    self.config.border_width
                )
                
            # Draw components
            for component in self.components:
                if hasattr(component, 'draw'):
                    component.draw()
                    
            # Draw scrollbar
            pygame.draw.rect(
                self.screen,
                self.config.scrollbar_color,
                self.scrollbar_rect
            )
            
            # Calculate and draw scrollbar handle
            if self.content_rect.height > self.rect.height:
                handle_height = max(
                    self.rect.height * (self.rect.height / self.content_rect.height),
                    20
                )
                handle_y = self.scrollbar_rect.top + (
                    (self.scrollbar_rect.height - handle_height) *
                    (self.scroll_y / (self.content_rect.height - self.rect.height))
                )
                handle_rect = pygame.Rect(
                    self.scrollbar_rect.left,
                    handle_y,
                    self.scrollbar_rect.width,
                    handle_height
                )
                pygame.draw.rect(
                    self.screen,
                    self.config.scrollbar_handle_color,
                    handle_rect
                )
                
            # Blit content surface with scroll offset
            self.screen.blit(
                content_surface,
                (self.rect.left, self.rect.top - self.scroll_y)
            )
            
            self.dirty = False
            
        except Exception as e:
            logger.error(f"Error drawing scroll panel: {str(e)}")
            
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
                    
            # Handle scrollbar dragging
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.scrollbar_rect.collidepoint(event.pos):
                        self.scroll_dragging = True
                        self.scroll_drag_start = event.pos[1]
                        return True
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    self.scroll_dragging = False
                    return True
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.scroll_dragging:
                    # Calculate new scroll position
                    delta = event.pos[1] - self.scroll_drag_start
                    self.scroll_drag_start = event.pos[1]
                    
                    # Update scroll position
                    max_scroll = self.content_rect.height - self.rect.height
                    self.scroll_y = max(0, min(self.scroll_y + delta, max_scroll))
                    self.dirty = True
                    return True
                    
            # Handle mouse wheel
            elif event.type == pygame.MOUSEWHEEL:
                # Update scroll position
                max_scroll = self.content_rect.height - self.rect.height
                self.scroll_y = max(0, min(self.scroll_y - event.y * 20, max_scroll))
                self.dirty = True
                return True
                
            # Pass event to components
            for component in self.components:
                if hasattr(component, 'handle_event'):
                    if component.handle_event(event):
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error handling scroll panel event: {str(e)}")
            return False
            
    def add_component(self, component: Any) -> None:
        """Add a component to the scroll panel.
        
        Args:
            component: The component to add
        """
        self.components.append(component)
        self._update_content_size()
        self.dirty = True
        
    def remove_component(self, component: Any) -> None:
        """Remove a component from the scroll panel.
        
        Args:
            component: The component to remove
        """
        if component in self.components:
            self.components.remove(component)
            self._update_content_size()
            self.dirty = True
            
    def clear_components(self) -> None:
        """Remove all components from the scroll panel."""
        self.components.clear()
        self._update_content_size()
        self.dirty = True
        
    def _update_content_size(self) -> None:
        """Update the content size based on components."""
        max_height = 0
        for component in self.components:
            if hasattr(component, 'rect'):
                max_height = max(max_height, component.rect.bottom)
                
        self.content_rect.height = max_height + self.config.padding
        self.scroll_y = min(self.scroll_y, max(0, self.content_rect.height - self.rect.height)) 