"""
Reusable toggle component for UI screens.
"""

import pygame
from typing import Optional, Tuple, Callable
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ToggleConfig:
    """Configuration for the toggle."""
    position: Tuple[int, int]
    size: int
    text: str
    font_size: int = 24
    text_color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Tuple[int, int, int] = (30, 30, 30)
    active_color: Tuple[int, int, int] = (100, 100, 100)
    border_color: Tuple[int, int, int] = (100, 100, 100)
    border_width: int = 2
    padding: int = 10
    checked: bool = False

class Toggle:
    """Reusable toggle component."""
    
    def __init__(self, screen: pygame.Surface, config: ToggleConfig, on_change: Optional[Callable] = None):
        """Initialize the toggle.
        
        Args:
            screen: The pygame surface to draw on
            config: Toggle configuration
            on_change: Optional callback function to call when state changes
        """
        self.screen = screen
        self.config = config
        self.on_change = on_change
        
        # Create toggle rect
        self.rect = pygame.Rect(
            config.position[0],
            config.position[1],
            config.size,
            config.size
        )
        
        # Initialize font
        self.font = pygame.font.SysFont(None, config.font_size)
        
        # Toggle state
        self.checked = config.checked
        self.hovered = False
        self.dirty = True
        
    def draw(self) -> None:
        """Draw the toggle."""
        if not self.dirty:
            return
            
        try:
            # Draw background
            color = self.config.active_color if self.checked else self.config.background_color
            pygame.draw.rect(self.screen, color, self.rect)
            pygame.draw.rect(
                self.screen,
                self.config.border_color,
                self.rect,
                self.config.border_width
            )
            
            # Draw check mark if checked
            if self.checked:
                check_size = self.rect.width // 2
                check_rect = pygame.Rect(
                    self.rect.centerx - check_size // 2,
                    self.rect.centery - check_size // 2,
                    check_size,
                    check_size
                )
                pygame.draw.line(
                    self.screen,
                    self.config.text_color,
                    (check_rect.left, check_rect.centery),
                    (check_rect.centerx, check_rect.bottom),
                    self.config.border_width
                )
                pygame.draw.line(
                    self.screen,
                    self.config.text_color,
                    (check_rect.centerx, check_rect.bottom),
                    (check_rect.right, check_rect.top),
                    self.config.border_width
                )
                
            # Draw text
            text_surface = self.font.render(self.config.text, True, self.config.text_color)
            text_rect = text_surface.get_rect(
                midleft=(self.rect.right + self.config.padding, self.rect.centery)
            )
            self.screen.blit(text_surface, text_rect)
            
            self.dirty = False
            
        except Exception as e:
            logger.error(f"Error drawing toggle: {str(e)}")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events.
        
        Args:
            event: The event to handle
            
        Returns:
            bool: True if the event was handled
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                self.dirty = True
                if self.on_change:
                    self.on_change(self.checked)
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            # Check if mouse is hovering over toggle
            was_hovered = self.hovered
            self.hovered = self.rect.collidepoint(event.pos)
            if was_hovered != self.hovered:
                self.dirty = True
            return self.hovered
            
        return False
        
    def is_checked(self) -> bool:
        """Get the toggle state.
        
        Returns:
            bool: True if checked, False otherwise
        """
        return self.checked
        
    def set_checked(self, checked: bool) -> None:
        """Set the toggle state.
        
        Args:
            checked: The new state
        """
        if checked != self.checked:
            self.checked = checked
            self.dirty = True
            if self.on_change:
                self.on_change(checked)
                
    def toggle(self) -> None:
        """Toggle the state."""
        self.set_checked(not self.checked)
        
    def set_text(self, text: str) -> None:
        """Set the toggle text.
        
        Args:
            text: The new text
        """
        self.config.text = text
        self.dirty = True 