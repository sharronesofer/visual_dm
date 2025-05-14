"""
Reusable checkbox component for UI screens.
"""

import pygame
from typing import Optional, Tuple, Callable
from dataclasses import dataclass
import logging

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class CheckboxConfig:
    """Configuration for the checkbox."""
    position: Tuple[int, int]
    size: int
    text: str
    font_size: int = 24
    text_color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Tuple[int, int, int] = (30, 30, 30)
    border_color: Tuple[int, int, int] = (100, 100, 100)
    check_color: Tuple[int, int, int] = (200, 200, 200)
    border_width: int = 2
    padding: int = 10
    checked: bool = False

class Checkbox:
    """Reusable checkbox component."""
    
    def __init__(self, screen: pygame.Surface, config: CheckboxConfig, on_change: Optional[Callable] = None):
        """Initialize the checkbox.
        
        Args:
            screen: The pygame surface to draw on
            config: Checkbox configuration
            on_change: Optional callback function to call when state changes
        """
        self.screen = screen
        self.config = config
        self.on_change = on_change
        
        # Create checkbox rect
        self.rect = pygame.Rect(
            config.position[0],
            config.position[1],
            config.size,
            config.size
        )
        
        # Initialize font
        self.font = pygame.font.SysFont(None, config.font_size)
        
        # Checkbox state
        self.checked = config.checked
        self.hovered = False
        self.dirty = True
        
    def draw(self) -> None:
        """Draw the checkbox."""
        if not self.dirty:
            return
            
        try:
            # Draw checkbox background
            pygame.draw.rect(self.screen, self.config.background_color, self.rect)
            pygame.draw.rect(
                self.screen,
                self.config.border_color,
                self.rect,
                self.config.border_width
            )
            
            # Draw check if checked
            if self.checked:
                # Draw check mark
                check_points = [
                    (self.rect.left + self.rect.width * 0.2, self.rect.centery),
                    (self.rect.left + self.rect.width * 0.4, self.rect.bottom - self.rect.height * 0.2),
                    (self.rect.right - self.rect.width * 0.2, self.rect.top + self.rect.height * 0.2)
                ]
                pygame.draw.lines(
                    self.screen,
                    self.config.check_color,
                    False,
                    check_points,
                    self.config.border_width
                )
                
            # Draw text
            text_surface = self.font.render(self.config.text, True, self.config.text_color)
            text_rect = text_surface.get_rect(
                midleft=(
                    self.rect.right + self.config.padding,
                    self.rect.centery
                )
            )
            self.screen.blit(text_surface, text_rect)
            
            self.dirty = False
            
        except Exception as e:
            logger.error(f"Error drawing checkbox: {str(e)}")
            
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
            # Check if mouse is hovering over checkbox
            was_hovered = self.hovered
            self.hovered = self.rect.collidepoint(event.pos)
            if was_hovered != self.hovered:
                self.dirty = True
            return self.hovered
            
        return False
        
    def is_checked(self) -> bool:
        """Get the checkbox state.
        
        Returns:
            bool: True if checked, False otherwise
        """
        return self.checked
        
    def set_checked(self, checked: bool) -> None:
        """Set the checkbox state.
        
        Args:
            checked: The new state
        """
        if checked != self.checked:
            self.checked = checked
            self.dirty = True
            if self.on_change:
                self.on_change(checked)
                
    def toggle(self) -> None:
        """Toggle the checkbox state."""
        self.set_checked(not self.checked)
        
    def set_text(self, text: str) -> None:
        """Set the checkbox text.
        
        Args:
            text: The new text
        """
        self.config.text = text
        self.dirty = True 