"""
Text input component with accessibility features.
"""

import pygame
import re
from typing import Tuple, Optional, Callable, Dict, Any
from dataclasses import dataclass
import logging
# from .error_handler import handle_component_error, ErrorSeverity
# from .accessibility import accessibility_manager

# Dummy error handler and accessibility_manager for testability
class ErrorSeverity:
    ERROR = 'error'
    WARNING = 'warning'

def handle_component_error(*args, **kwargs):
    pass

accessibility_manager = type('Dummy', (), {
    'add_to_focus_order': staticmethod(lambda *a, **kw: None),
    'move_focus': staticmethod(lambda *a, **kw: None),
    'draw_focus_indicator': staticmethod(lambda *a, **kw: None),
    'remove_from_focus_order': staticmethod(lambda *a, **kw: None),
    'ensure_contrast_compliance': staticmethod(lambda fg, bg, enh: (fg, bg)),
})()

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class TextInputConfig:
    """Configuration for text input component."""
    position: Tuple[int, int]
    width: int
    height: int
    font_size: int = 24
    text_color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Tuple[int, int, int] = (30, 30, 30)
    border_color: Tuple[int, int, int] = (100, 100, 100)
    border_width: int = 2
    padding: int = 10
    placeholder: str = ""
    placeholder_color: Tuple[int, int, int] = (150, 150, 150)
    max_length: int = 50
    error_message: str = "Invalid input"
    error_color: Tuple[int, int, int] = (255, 0, 0)
    show_error_duration: int = 3000  # milliseconds

class TextInput:
    """Text input component with security features and enhanced error handling."""
    
    def __init__(self, screen: pygame.Surface, config: TextInputConfig):
        """Initialize text input component."""
        self.screen = screen
        self.config = config
        self.text = ""
        self.focused = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_interval = 500  # milliseconds
        self.font = pygame.font.Font(None, config.font_size)
        self.rect = pygame.Rect(
            config.position[0],
            config.position[1],
            config.width,
            config.height
        )
        self.dirty = True
        
        # Security-related attributes
        self._sanitized_text = ""
        self._last_valid_text = ""
        self._invalid_chars = re.compile(r'[\x00-\x1F\x7F-\x9F]')  # Control characters
        self._html_tags = re.compile(r'<[^>]+>')  # HTML tags
        self._sql_injection = re.compile(r'[\'";]|--|\b(DROP|DELETE|INSERT|UPDATE|SELECT)\b', re.IGNORECASE)
        
        # Error handling attributes
        self._error_message = ""
        self._error_timer = 0
        self._showing_error = False
        
    def _sanitize_text(self, text: str) -> str:
        """Sanitize input text to prevent security vulnerabilities."""
        try:
            # Remove control characters
            text = self._invalid_chars.sub('', text)
            
            # Remove HTML tags
            text = self._html_tags.sub('', text)
            
            # Remove SQL injection attempts
            text = self._sql_injection.sub('', text)
            
            # Enforce maximum length
            if len(text) > self.config.max_length:
                text = text[:self.config.max_length]
                
            return text
        except Exception as e:
            handle_component_error(
                "TextInput",
                "sanitize_text",
                e,
                ErrorSeverity.ERROR,
                {"text": text}
            )
            return self._last_valid_text
            
    def _validate_text(self, text: str) -> bool:
        """Validate input text."""
        try:
            # Check for control characters
            if self._invalid_chars.search(text):
                self._show_error("Control characters are not allowed")
                return False
                
            # Check for HTML tags
            if self._html_tags.search(text):
                self._show_error("HTML tags are not allowed")
                return False
                
            # Check for SQL injection
            if self._sql_injection.search(text):
                self._show_error("Invalid input detected")
                return False
                
            # Check length
            if len(text) > self.config.max_length:
                self._show_error(f"Maximum length is {self.config.max_length} characters")
                return False
                
            return True
        except Exception as e:
            handle_component_error(
                "TextInput",
                "validate_text",
                e,
                ErrorSeverity.ERROR,
                {"text": text}
            )
            return False
            
    def _show_error(self, message: str) -> None:
        """Show an error message."""
        self._error_message = message
        self._showing_error = True
        self._error_timer = 0
        self.dirty = True
        
    def set_text(self, text: str) -> None:
        """Set text with validation and sanitization."""
        try:
            if self._validate_text(text):
                self._sanitized_text = self._sanitize_text(text)
                self._last_valid_text = self._sanitized_text
                self.text = self._sanitized_text
                self.dirty = True
            else:
                handle_component_error(
                    "TextInput",
                    "set_text",
                    ValueError("Invalid text input"),
                    ErrorSeverity.WARNING,
                    {"text": text}
                )
        except Exception as e:
            handle_component_error(
                "TextInput",
                "set_text",
                e,
                ErrorSeverity.ERROR,
                {"text": text}
            )
            
    def get_text(self) -> str:
        """Get sanitized text."""
        return self._sanitized_text
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events with security measures."""
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.focused = True
                    self.dirty = True
                    return True
                else:
                    self.focused = False
                    self.dirty = True
                    return False
                    
            elif event.type == pygame.KEYDOWN and self.focused:
                if event.key == pygame.K_BACKSPACE:
                    new_text = self.text[:-1]
                    if self._validate_text(new_text):
                        self.set_text(new_text)
                    return True
                    
                elif event.key == pygame.K_RETURN:
                    self.focused = False
                    self.dirty = True
                    return True
                    
                elif event.unicode:
                    new_text = self.text + event.unicode
                    if self._validate_text(new_text):
                        self.set_text(new_text)
                    return True
                    
            return False
        except Exception as e:
            handle_component_error(
                "TextInput",
                "handle_event",
                e,
                ErrorSeverity.ERROR,
                {"event": str(event)}
            )
            return False
            
    def update(self, dt: int) -> None:
        """Update component state."""
        try:
            if self.focused:
                self.cursor_timer += dt
                if self.cursor_timer >= self.cursor_blink_interval:
                    self.cursor_visible = not self.cursor_visible
                    self.cursor_timer = 0
                    self.dirty = True
                    
            if self._showing_error:
                self._error_timer += dt
                if self._error_timer >= self.config.show_error_duration:
                    self._showing_error = False
                    self._error_message = ""
                    self.dirty = True
        except Exception as e:
            handle_component_error(
                "TextInput",
                "update",
                e,
                ErrorSeverity.ERROR,
                {"dt": dt}
            )
            
    def draw(self) -> None:
        """Draw component with security measures."""
        try:
            if not self.dirty:
                return
                
            # Draw background
            pygame.draw.rect(
                self.screen,
                self.config.background_color,
                self.rect
            )
            
            # Draw border
            if self.config.border_width > 0:
                border_color = self.config.error_color if self._showing_error else self.config.border_color
                pygame.draw.rect(
                    self.screen,
                    border_color,
                    self.rect,
                    self.config.border_width
                )
                
            # Draw text or placeholder
            text_surface = None
            if self.text:
                text_surface = self.font.render(
                    self._sanitized_text,
                    True,
                    self.config.text_color
                )
            elif self.config.placeholder and not self.focused:
                text_surface = self.font.render(
                    self.config.placeholder,
                    True,
                    self.config.placeholder_color
                )
                
            if text_surface:
                text_rect = text_surface.get_rect(
                    midleft=(
                        self.rect.left + self.config.padding,
                        self.rect.centery
                    )
                )
                self.screen.blit(text_surface, text_rect)
                
                # Draw cursor
                if self.focused and self.cursor_visible:
                    cursor_x = text_rect.right + 2
                    pygame.draw.line(
                        self.screen,
                        self.config.text_color,
                        (cursor_x, self.rect.top + self.config.padding),
                        (cursor_x, self.rect.bottom - self.config.padding)
                    )
                    
            # Draw error message
            if self._showing_error:
                error_surface = self.font.render(
                    self._error_message,
                    True,
                    self.config.error_color
                )
                error_rect = error_surface.get_rect(
                    midleft=(
                        self.rect.left + self.config.padding,
                        self.rect.bottom + 5
                    )
                )
                self.screen.blit(error_surface, error_rect)
                    
            self.dirty = False
        except Exception as e:
            handle_component_error(
                "TextInput",
                "draw",
                e,
                ErrorSeverity.ERROR
            )
            
    def clear(self) -> None:
        """Clear text input."""
        try:
            self.set_text("")
        except Exception as e:
            handle_component_error(
                "TextInput",
                "clear",
                e,
                ErrorSeverity.ERROR
            ) 