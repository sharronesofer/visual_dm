"""
Reusable label component for UI screens.
"""

import pygame
from typing import Optional, Tuple, List
from dataclasses import dataclass
import logging

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class LabelConfig:
    """Configuration for the label."""
    position: Tuple[int, int]
    width: int
    height: int
    text: str
    font_size: int = 24
    text_color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Optional[Tuple[int, int, int]] = None
    border_color: Optional[Tuple[int, int, int]] = None
    border_width: int = 0
    padding: int = 10
    alignment: str = 'left'  # 'left', 'center', 'right'
    wrap_text: bool = True
    z_index: int = 0

class Label:
    """Reusable label component."""
    
    def __init__(self, screen: pygame.Surface, config: LabelConfig):
        """Initialize the label.
        
        Args:
            screen: The pygame surface to draw on
            config: Label configuration
        """
        self.screen = screen
        self.config = config
        
        # Create label rect
        self.rect = pygame.Rect(
            config.position[0],
            config.position[1],
            config.width,
            config.height
        )
        
        # Initialize font
        self.font = pygame.font.SysFont(None, config.font_size)
        
        # Label state
        self.visible = True
        self.dirty = True
        
        # Add z-index handling
        self.z_index = config.z_index
        
        # Add screen bounds tracking
        self.screen_rect = screen.get_rect()
        
        # Initialize text lines
        self._lines: List[str] = []
        self._update_text_lines()
        
    def _update_text_lines(self) -> None:
        """Update the text lines based on the current text and width."""
        if not self.config.wrap_text:
            self._lines = [self.config.text]
            return
            
        words = self.config.text.split()
        if not words:
            self._lines = []
            return
            
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = self.font.render(word, True, self.config.text_color)
            word_width = word_surface.get_width()
            
            if current_width + word_width <= self.rect.width - 2 * self.config.padding:
                current_line.append(word)
                current_width += word_width + self.font.size(' ')[0]
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
                
        if current_line:
            lines.append(' '.join(current_line))
            
        self._lines = lines
        self.dirty = True
        
    def draw(self) -> None:
        """Draw the label."""
        if not self.dirty or not self.visible:
            return
            
        try:
            # Calculate visible area
            visible_rect = self.screen_rect.clip(self.rect)
            if visible_rect.width <= 0 or visible_rect.height <= 0:
                return
                
            # Draw background if specified
            if self.config.background_color:
                pygame.draw.rect(self.screen, self.config.background_color, visible_rect)
                
            # Draw border if specified
            if self.config.border_color and self.config.border_width > 0:
                pygame.draw.rect(self.screen, self.config.border_color, visible_rect, self.config.border_width)
                
            # Draw text lines
            y = self.rect.top + self.config.padding
            for line in self._lines:
                text_surface = self.font.render(line, True, self.config.text_color)
                
                # Calculate x position based on alignment
                if self.config.alignment == 'left':
                    x = self.rect.left + self.config.padding
                elif self.config.alignment == 'center':
                    x = self.rect.centerx - text_surface.get_width() // 2
                else:  # right
                    x = self.rect.right - text_surface.get_width() - self.config.padding
                    
                self.screen.blit(text_surface, (x, y))
                y += text_surface.get_height() + 2
                
            self.dirty = False
            
        except Exception as e:
            logger.error(f"Error drawing label: {str(e)}")
            
    def set_text(self, text: str) -> None:
        """Set the label's text.
        
        Args:
            text: The new text
        """
        if self.config.text != text:
            self.config.text = text
            self._update_text_lines()
            
    def set_visible(self, visible: bool) -> None:
        """Set the label's visibility.
        
        Args:
            visible: Whether the label should be visible
        """
        if self.visible != visible:
            self.visible = visible
            self.dirty = True
            
    def set_alignment(self, alignment: str) -> None:
        """Set the text alignment.
        
        Args:
            alignment: The new alignment ('left', 'center', 'right')
        """
        if alignment in ('left', 'center', 'right') and self.config.alignment != alignment:
            self.config.alignment = alignment
            self.dirty = True
            
    def set_wrap_text(self, wrap_text: bool) -> None:
        """Set whether text should be wrapped.
        
        Args:
            wrap_text: Whether text should be wrapped
        """
        if self.config.wrap_text != wrap_text:
            self.config.wrap_text = wrap_text
            self._update_text_lines()
            
    def cleanup(self) -> None:
        """Clean up label resources."""
        self.visible = True
        self.dirty = True 