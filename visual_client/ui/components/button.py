"""
Reusable button component for UI screens.
"""

import pygame
from typing import Optional, Tuple, Callable
from dataclasses import dataclass
import logging

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ButtonConfig:
    """Configuration for the button."""
    position: Tuple[int, int]
    width: int
    height: int
    text: str
    font_size: int = 24
    text_color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Tuple[int, int, int] = (30, 30, 30)
    hover_color: Tuple[int, int, int] = (50, 50, 50)
    pressed_color: Tuple[int, int, int] = (70, 70, 70)
    disabled_color: Tuple[int, int, int] = (20, 20, 20)
    border_color: Tuple[int, int, int] = (100, 100, 100)
    border_width: int = 2
    padding: int = 10
    z_index: int = 100

class Button:
    """Reusable button component."""
    
    def __init__(self, screen: pygame.Surface, config: ButtonConfig, on_click: Optional[Callable] = None):
        """Initialize the button.
        
        Args:
            screen: The pygame surface to draw on
            config: Button configuration
            on_click: Optional callback function to call when the button is clicked
        """
        self.screen = screen
        self.config = config
        self.on_click = on_click
        
        # Create button rect
        self.rect = pygame.Rect(
            config.position[0],
            config.position[1],
            config.width,
            config.height
        )
        
        # Initialize font
        self.font = pygame.font.SysFont(None, config.font_size)
        
        # Button state
        self.enabled = True
        self.visible = True
        self.hovered = False
        self.pressed = False
        self.focused = False
        self.dirty = True
        
        # Add z-index handling
        self.z_index = config.z_index
        
        # Add screen bounds tracking
        self.screen_rect = screen.get_rect()
        
    def draw(self) -> None:
        """Draw the button."""
        if not self.dirty or not self.visible:
            return
            
        try:
            # Calculate visible area
            visible_rect = self.screen_rect.clip(self.rect)
            if visible_rect.width <= 0 or visible_rect.height <= 0:
                return
                
            # Draw button background
            if not self.enabled:
                color = self.config.disabled_color
            elif self.pressed:
                color = self.config.pressed_color
            elif self.hovered:
                color = self.config.hover_color
            else:
                color = self.config.background_color
                
            pygame.draw.rect(self.screen, color, visible_rect)
            pygame.draw.rect(self.screen, self.config.border_color, visible_rect, self.config.border_width)
            
            # Draw button text
            text_surface = self.font.render(self.config.text, True, self.config.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            self.screen.blit(text_surface, text_rect)
            
            # Draw focus indicator
            if self.focused:
                focus_rect = self.rect.inflate(4, 4)
                pygame.draw.rect(self.screen, self.config.border_color, focus_rect, 2)
                
            self.dirty = False
            
        except Exception as e:
            logger.error(f"Error drawing button: {str(e)}")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events.
        
        Args:
            event: The event to handle
            
        Returns:
            bool: True if the event was handled
        """
        if not self.visible or not self.enabled:
            return False
            
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.pressed = True
                    self.dirty = True
                    return True
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.pressed and self.rect.collidepoint(event.pos):
                    self.pressed = False
                    self.dirty = True
                    if self.on_click:
                        self.on_click()
                    return True
                elif self.pressed:
                    self.pressed = False
                    self.dirty = True
                    return True
                    
            elif event.type == pygame.MOUSEMOTION:
                was_hovered = self.hovered
                self.hovered = self.rect.collidepoint(event.pos)
                if was_hovered != self.hovered:
                    self.dirty = True
                    
            elif event.type == pygame.KEYDOWN:
                if self.focused and event.key == pygame.K_RETURN:
                    self.pressed = True
                    self.dirty = True
                    return True
                    
            elif event.type == pygame.KEYUP:
                if self.focused and event.key == pygame.K_RETURN and self.pressed:
                    self.pressed = False
                    self.dirty = True
                    if self.on_click:
                        self.on_click()
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error handling button event: {str(e)}")
            return False
            
    def set_enabled(self, enabled: bool) -> None:
        """Set the button's enabled state.
        
        Args:
            enabled: Whether the button should be enabled
        """
        if self.enabled != enabled:
            self.enabled = enabled
            self.dirty = True
            
    def set_visible(self, visible: bool) -> None:
        """Set the button's visibility.
        
        Args:
            visible: Whether the button should be visible
        """
        if self.visible != visible:
            self.visible = visible
            self.dirty = True
            
    def set_text(self, text: str) -> None:
        """Set the button's text.
        
        Args:
            text: The new text
        """
        if self.config.text != text:
            self.config.text = text
            self.dirty = True
            
    def set_click_handler(self, handler: Callable) -> None:
        """Set the button's click handler.
        
        Args:
            handler: The new click handler
        """
        self.on_click = handler
        
    def update(self) -> None:
        """Update the button's state."""
        if self.pressed and not pygame.mouse.get_pressed()[0]:
            self.pressed = False
            self.dirty = True
            
    def cleanup(self) -> None:
        """Clean up button resources."""
        self.enabled = True
        self.visible = True
        self.hovered = False
        self.pressed = False
        self.focused = False
        self.dirty = True 