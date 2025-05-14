"""
Reusable dropdown component for UI screens.
"""

import pygame
from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass
import logging

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class DropdownConfig:
    """Configuration for the dropdown."""
    position: Tuple[int, int]
    width: int
    height: int
    options: List[str]
    font_size: int = 24
    text_color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Tuple[int, int, int] = (30, 30, 30)
    hover_color: Tuple[int, int, int] = (50, 50, 50)
    border_color: Tuple[int, int, int] = (100, 100, 100)
    border_width: int = 2
    padding: int = 10
    option_height: int = 30
    z_index: int = 1000
    max_visible_options: int = 5
    highlight_color: Tuple[int, int, int] = (70, 70, 70)

class Dropdown:
    """Reusable dropdown component."""
    
    def __init__(self, screen: pygame.Surface, config: DropdownConfig, on_select: Optional[Callable] = None):
        """Initialize the dropdown.
        
        Args:
            screen: The pygame surface to draw on
            config: Dropdown configuration
            on_select: Optional callback function to call when an option is selected
        """
        self.screen = screen
        self.config = config
        self.on_select = on_select
        
        # Create main button rect
        self.rect = pygame.Rect(
            config.position[0],
            config.position[1],
            config.width,
            config.height
        )
        
        # Initialize font
        self.font = pygame.font.SysFont(None, config.font_size)
        
        # Dropdown state
        self.selected_index: Optional[int] = None
        self.hovered_index: Optional[int] = None
        self.expanded = False
        self.dirty = True
        self.visible = True
        self.enabled = True
        
        # Add z-index handling
        self.z_index = config.z_index
        self.expanded_z_index = config.z_index + 1000  # Expanded options should be on top
        
        # Add screen bounds tracking
        self.screen_rect = screen.get_rect()
        
        # Add keyboard navigation support
        self.keyboard_focus = False
        
        # Add highlighting support
        self.is_highlighted = False
        self.highlight_duration = 0.0
        self.highlight_timer = 0.0
        
        # Create options surface for expanded state
        self.options_surface = None
        self.options_rect = None
        
    def update(self, dt: float) -> None:
        """Update the dropdown.
        
        Args:
            dt: Time since last update in seconds
        """
        if not self.visible:
            return
            
        # Update hover state
        mouse_pos = pygame.mouse.get_pos()
        if self.expanded:
            for i, option in enumerate(self.config.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.rect.height * (i + 1),
                    self.rect.width,
                    self.rect.height
                )
                if option_rect.collidepoint(mouse_pos):
                    self.hovered_index = i
                    break
            else:
                self.hovered_index = None
                
        # Update highlight timer
        if self.is_highlighted:
            self.highlight_timer += dt
            if self.highlight_timer >= self.highlight_duration:
                self.is_highlighted = False
                self.highlight_timer = 0.0
                
        # Mark as dirty if state changed
        self.dirty = True
        
    def draw(self) -> None:
        """Draw the dropdown."""
        if not self.dirty or not self.visible:
            return
            
        try:
            # Calculate visible area
            visible_rect = self.screen_rect.clip(self.rect)
            if visible_rect.width <= 0 or visible_rect.height <= 0:
                return
                
            # Draw main button with clipping
            background_color = (
                self.config.highlight_color
                if self.is_highlighted
                else self.config.background_color
            )
            pygame.draw.rect(self.screen, background_color, visible_rect)
            pygame.draw.rect(self.screen, self.config.border_color, visible_rect, self.config.border_width)
            
            # Draw selected text or placeholder
            text = (
                self.config.options[self.selected_index]
                if self.selected_index is not None
                else "Select an option"
            )
            text_surface = self.font.render(text, True, self.config.text_color)
            text_rect = text_surface.get_rect(
                midleft=(
                    self.rect.left + self.config.padding,
                    self.rect.centery
                )
            )
            self.screen.blit(text_surface, text_rect)
            
            # Draw dropdown arrow
            arrow_points = [
                (self.rect.right - 20, self.rect.centery - 5),
                (self.rect.right - 10, self.rect.centery + 5),
                (self.rect.right - 30, self.rect.centery + 5)
            ]
            pygame.draw.polygon(self.screen, self.config.text_color, arrow_points)
            
            # Draw options if expanded
            if self.expanded:
                # Calculate max height to stay within screen bounds
                max_height = self.screen_rect.bottom - self.rect.bottom
                visible_options = min(
                    self.config.max_visible_options,
                    max(1, max_height // self.config.option_height)
                )
                
                # Create options surface with alpha for transparency
                self.options_surface = pygame.Surface(
                    (self.rect.width, visible_options * self.config.option_height),
                    pygame.SRCALPHA
                )
                
                # Fill with transparent background
                self.options_surface.fill((0, 0, 0, 0))
                
                # Draw options with clipping
                for i, option in enumerate(self.config.options[:visible_options]):
                    option_rect = pygame.Rect(
                        0,
                        i * self.config.option_height,
                        self.rect.width,
                        self.config.option_height
                    )
                    
                    # Draw option background with alpha
                    color = (
                        self.config.hover_color + (255,)
                        if i == self.hovered_index
                        else self.config.background_color + (255,)
                    )
                    pygame.draw.rect(self.options_surface, color, option_rect)
                    pygame.draw.rect(
                        self.options_surface,
                        self.config.border_color + (255,),
                        option_rect,
                        self.config.border_width
                    )
                    
                    # Draw option text
                    text_surface = self.font.render(option, True, self.config.text_color)
                    text_rect = text_surface.get_rect(
                        midleft=(
                            option_rect.left + self.config.padding,
                            option_rect.centery
                        )
                    )
                    self.options_surface.blit(text_surface, text_rect)
                
                # Store options rect for event handling
                self.options_rect = pygame.Rect(
                    self.rect.left,
                    self.rect.bottom,
                    self.rect.width,
                    visible_options * self.config.option_height
                )
                
            self.dirty = False
            
        except Exception as e:
            logger.error(f"Error drawing dropdown: {str(e)}")
            
    def draw_expanded(self) -> None:
        """Draw the expanded options with proper z-index."""
        if self.expanded and self.options_surface is not None:
            self.screen.blit(self.options_surface, (self.rect.left, self.rect.bottom))
            
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
                if self.expanded:
                    # Check options first (highest z-index)
                    if self.options_rect and self.options_rect.collidepoint(event.pos):
                        option_index = (event.pos[1] - self.options_rect.top) // self.config.option_height
                        if 0 <= option_index < len(self.config.options):
                            self.selected_index = option_index
                            self.expanded = False
                            self.dirty = True
                            if self.on_select:
                                self.on_select(self.config.options[option_index])
                            return True
                            
                    # Check main button
                    if self.rect.collidepoint(event.pos):
                        self.expanded = not self.expanded
                        self.dirty = True
                        return True
                        
                    # Click outside dropdown
                    self.expanded = False
                    self.dirty = True
                    return True
                    
                elif self.rect.collidepoint(event.pos):
                    self.expanded = True
                    self.dirty = True
                    return True
                    
            elif event.type == pygame.KEYDOWN and self.keyboard_focus:
                if event.key == pygame.K_RETURN:
                    self.expanded = not self.expanded
                    self.dirty = True
                    return True
                    
                elif event.key == pygame.K_UP and self.expanded:
                    self.hovered_index = (
                        len(self.config.options) - 1
                        if self.hovered_index is None
                        else (self.hovered_index - 1) % len(self.config.options)
                    )
                    self.dirty = True
                    return True
                    
                elif event.key == pygame.K_DOWN and self.expanded:
                    self.hovered_index = (
                        0
                        if self.hovered_index is None
                        else (self.hovered_index + 1) % len(self.config.options)
                    )
                    self.dirty = True
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error handling event in dropdown: {str(e)}")
            return False
            
    def get_selected(self) -> Optional[str]:
        """Get the currently selected option.
        
        Returns:
            Optional[str]: The selected option or None if nothing is selected
        """
        if self.selected_index is not None:
            return self.config.options[self.selected_index]
        return None
        
    def set_selected(self, option: str) -> None:
        """Set the selected option.
        
        Args:
            option: The option to select
        """
        try:
            index = self.config.options.index(option)
            self.selected_index = index
            self.dirty = True
        except ValueError:
            logger.warning(f"Option '{option}' not found in dropdown options")
            
    def add_option(self, option: str) -> None:
        """Add a new option to the dropdown.
        
        Args:
            option: The option to add
        """
        if option not in self.config.options:
            self.config.options.append(option)
            self.dirty = True
            
    def remove_option(self, option: str) -> None:
        """Remove an option from the dropdown.
        
        Args:
            option: The option to remove
        """
        try:
            index = self.config.options.index(option)
            self.config.options.pop(index)
            if self.selected_index == index:
                self.selected_index = None
            elif self.selected_index > index:
                self.selected_index -= 1
            self.dirty = True
        except ValueError:
            logger.warning(f"Option '{option}' not found in dropdown options")
            
    def highlight(self, duration: float = 1.0) -> None:
        """Highlight the dropdown for a specified duration.
        
        Args:
            duration: Duration in seconds to highlight the dropdown
        """
        self.is_highlighted = True
        self.highlight_duration = duration
        self.highlight_timer = 0.0
        self.dirty = True
            
    def cleanup(self) -> None:
        """Clean up resources."""
        self.screen = None
        self.font = None 