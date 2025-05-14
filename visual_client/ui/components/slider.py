"""
Reusable slider component for UI screens.
"""

import pygame
from typing import Optional, Tuple, Callable
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SliderConfig:
    """Configuration for the slider."""
    position: Tuple[int, int]
    width: int
    height: int
    min_value: float
    max_value: float
    initial_value: float
    step: float = 1.0
    font_size: int = 24
    text_color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Tuple[int, int, int] = (30, 30, 30)
    fill_color: Tuple[int, int, int] = (100, 100, 100)
    handle_color: Tuple[int, int, int] = (200, 200, 200)
    border_color: Tuple[int, int, int] = (100, 100, 100)
    border_width: int = 2
    padding: int = 10
    show_value: bool = True

class Slider:
    """Reusable slider component."""
    
    def __init__(self, screen: pygame.Surface, config: SliderConfig, on_change: Optional[Callable] = None):
        """Initialize the slider.
        
        Args:
            screen: The pygame surface to draw on
            config: Slider configuration
            on_change: Optional callback function to call when value changes
        """
        self.screen = screen
        self.config = config
        self.on_change = on_change
        
        # Create slider rect
        self.rect = pygame.Rect(
            config.position[0],
            config.position[1],
            config.width,
            config.height
        )
        
        # Initialize font
        self.font = pygame.font.SysFont(None, config.font_size)
        
        # Slider state
        self.value = max(config.min_value, min(config.max_value, config.initial_value))
        self.dragging = False
        self.dirty = True
        
        # Calculate handle size
        self.handle_width = self.rect.height
        self.handle_height = self.rect.height * 1.5
        
    def draw(self) -> None:
        """Draw the slider."""
        if not self.dirty:
            return
            
        try:
            # Draw background
            pygame.draw.rect(self.screen, self.config.background_color, self.rect)
            pygame.draw.rect(
                self.screen,
                self.config.border_color,
                self.rect,
                self.config.border_width
            )
            
            # Calculate fill width
            fill_width = int(
                (self.value - self.config.min_value)
                / (self.config.max_value - self.config.min_value)
                * (self.rect.width - self.handle_width)
            )
            
            # Draw fill
            fill_rect = pygame.Rect(
                self.rect.left,
                self.rect.top,
                fill_width + self.handle_width // 2,
                self.rect.height
            )
            pygame.draw.rect(self.screen, self.config.fill_color, fill_rect)
            
            # Calculate handle position
            handle_x = (
                self.rect.left
                + (self.value - self.config.min_value)
                / (self.config.max_value - self.config.min_value)
                * (self.rect.width - self.handle_width)
            )
            
            # Draw handle
            handle_rect = pygame.Rect(
                handle_x,
                self.rect.centery - self.handle_height // 2,
                self.handle_width,
                self.handle_height
            )
            pygame.draw.rect(self.screen, self.config.handle_color, handle_rect)
            pygame.draw.rect(
                self.screen,
                self.config.border_color,
                handle_rect,
                self.config.border_width
            )
            
            # Draw value if enabled
            if self.config.show_value:
                value_text = f"{self.value:.1f}"
                text_surface = self.font.render(value_text, True, self.config.text_color)
                text_rect = text_surface.get_rect(
                    midright=(self.rect.right - self.config.padding, self.rect.centery)
                )
                self.screen.blit(text_surface, text_rect)
                
            self.dirty = False
            
        except Exception as e:
            logger.error(f"Error drawing slider: {str(e)}")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events.
        
        Args:
            event: The event to handle
            
        Returns:
            bool: True if the event was handled
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if handle was clicked
            handle_x = (
                self.rect.left
                + (self.value - self.config.min_value)
                / (self.config.max_value - self.config.min_value)
                * (self.rect.width - self.handle_width)
            )
            handle_rect = pygame.Rect(
                handle_x,
                self.rect.centery - self.handle_height // 2,
                self.handle_width,
                self.handle_height
            )
            
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update value based on mouse position
            mouse_x = max(self.rect.left, min(event.pos[0], self.rect.right))
            new_value = (
                self.config.min_value
                + (mouse_x - self.rect.left)
                / (self.rect.width - self.handle_width)
                * (self.config.max_value - self.config.min_value)
            )
            
            # Apply step
            if self.config.step > 0:
                new_value = round(new_value / self.config.step) * self.config.step
                
            # Clamp value
            new_value = max(self.config.min_value, min(self.config.max_value, new_value))
            
            if new_value != self.value:
                self.value = new_value
                self.dirty = True
                if self.on_change:
                    self.on_change(self.value)
                return True
                
        return False
        
    def get_value(self) -> float:
        """Get the current value.
        
        Returns:
            float: The current value
        """
        return self.value
        
    def set_value(self, value: float) -> None:
        """Set the current value.
        
        Args:
            value: The new value
        """
        new_value = max(self.config.min_value, min(self.config.max_value, value))
        if self.config.step > 0:
            new_value = round(new_value / self.config.step) * self.config.step
            
        if new_value != self.value:
            self.value = new_value
            self.dirty = True
            if self.on_change:
                self.on_change(self.value)
                
    def set_range(self, min_value: float, max_value: float) -> None:
        """Set the value range.
        
        Args:
            min_value: The new minimum value
            max_value: The new maximum value
        """
        if min_value >= max_value:
            logger.warning("Minimum value must be less than maximum value")
            return
            
        self.config.min_value = min_value
        self.config.max_value = max_value
        self.value = max(min_value, min(max_value, self.value))
        self.dirty = True 