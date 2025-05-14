"""
Text input component with comprehensive input validation and sanitization.

This module provides a secure text input component that:
1. Validates input against configurable rules
2. Sanitizes input to prevent injection attacks
3. Handles special characters and formatting
4. Provides feedback for invalid input
"""

import re
from typing import Optional, Callable, List, Dict, Any, Tuple
from dataclasses import dataclass
from visual_client.core.utils.error_utils import ValidationError

@dataclass
class TextboxConfig:
    """Configuration for text input validation and formatting.
    
    Attributes:
        max_length: Maximum allowed input length
        min_length: Minimum required input length
        allowed_chars: Regex pattern for allowed characters
        required_format: Regex pattern for required format
        multiline: Whether to allow multiple lines
        trim_whitespace: Whether to trim leading/trailing whitespace
        escape_html: Whether to escape HTML characters
        strip_tags: Whether to remove HTML tags
        custom_validators: List of custom validation functions
    """
    max_length: int = 100
    min_length: int = 0
    allowed_chars: str = r'[\w\s.,!?@#$%^&*()\-_=+\[\]{}|;:\'"<>/\\]'
    required_format: Optional[str] = None
    multiline: bool = False
    trim_whitespace: bool = True
    escape_html: bool = True
    strip_tags: bool = True
    custom_validators: List[Callable[[str], bool]] = None

class Textbox:
    """Secure text input component with validation and sanitization."""
    
    def __init__(self, config: Optional[TextboxConfig] = None):
        self.config = config or TextboxConfig()
        self.value = ""
        self.error_message = None
        self._cursor_position = 0
        self._selection_start = None
        self._selection_end = None
        
    def set_text(self, text: str) -> None:
        """Set the textbox content with validation and sanitization.
        
        Args:
            text: Text to set
            
        Raises:
            ValidationError: If text fails validation
        """
        try:
            # Sanitize input
            sanitized = self._sanitize_input(text)
            
            # Validate input
            self._validate_input(sanitized)
            
            # Update value
            self.value = sanitized
            self.error_message = None
            
        except ValidationError as e:
            self.error_message = str(e)
            raise
            
    def insert_text(self, text: str, position: Optional[int] = None) -> None:
        """Insert text at specified position with validation.
        
        Args:
            text: Text to insert
            position: Position to insert at (defaults to cursor position)
            
        Raises:
            ValidationError: If resulting text fails validation
        """
        try:
            if position is None:
                position = self._cursor_position
                
            # Sanitize input
            sanitized = self._sanitize_input(text)
            
            # Create new text with insertion
            new_text = self.value[:position] + sanitized + self.value[position:]
            
            # Validate new text
            self._validate_input(new_text)
            
            # Update value
            self.value = new_text
            self._cursor_position = position + len(sanitized)
            self.error_message = None
            
        except ValidationError as e:
            self.error_message = str(e)
            raise
            
    def delete_text(self, start: int, end: Optional[int] = None) -> None:
        """Delete text between positions with validation.
        
        Args:
            start: Start position
            end: End position (defaults to cursor position)
            
        Raises:
            ValidationError: If resulting text fails validation
        """
        try:
            if end is None:
                end = self._cursor_position
                
            # Create new text with deletion
            new_text = self.value[:start] + self.value[end:]
            
            # Validate new text
            self._validate_input(new_text)
            
            # Update value
            self.value = new_text
            self._cursor_position = start
            self.error_message = None
            
        except ValidationError as e:
            self.error_message = str(e)
            raise
            
    def _sanitize_input(self, text: str) -> str:
        """Sanitize input text according to configuration.
        
        Args:
            text: Text to sanitize
            
        Returns:
            str: Sanitized text
        """
        # Trim whitespace if configured
        if self.config.trim_whitespace:
            text = text.strip()
            
        # Remove HTML tags if configured
        if self.config.strip_tags:
            text = re.sub(r'<[^>]+>', '', text)
            
        # Escape HTML characters if configured
        if self.config.escape_html:
            text = self._escape_html(text)
            
        # Remove disallowed characters
        if self.config.allowed_chars:
            text = re.sub(f'[^{self.config.allowed_chars}]', '', text)
            
        return text
        
    def _validate_input(self, text: str) -> None:
        """Validate input text according to configuration.
        
        Args:
            text: Text to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Check length
        if len(text) > self.config.max_length:
            raise ValidationError(
                f"Text exceeds maximum length of {self.config.max_length} characters"
            )
            
        if len(text) < self.config.min_length:
            raise ValidationError(
                f"Text must be at least {self.config.min_length} characters long"
            )
            
        # Check format
        if self.config.required_format and not re.match(
            self.config.required_format,
            text
        ):
            raise ValidationError("Text does not match required format")
            
        # Run custom validators
        if self.config.custom_validators:
            for validator in self.config.custom_validators:
                if not validator(text):
                    raise ValidationError("Text failed custom validation")
                    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters.
        
        Args:
            text: Text to escape
            
        Returns:
            str: Escaped text
        """
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
        }
        return "".join(html_escape_table.get(c, c) for c in text)
        
    def get_error(self) -> Optional[str]:
        """Get the current error message.
        
        Returns:
            Optional[str]: Error message if any, None otherwise
        """
        return self.error_message
        
    def is_valid(self) -> bool:
        """Check if current text is valid.
        
        Returns:
            bool: True if text is valid, False otherwise
        """
        try:
            self._validate_input(self.value)
            return True
        except ValidationError:
            return False
            
    def get_cursor_position(self) -> int:
        """Get current cursor position.
        
        Returns:
            int: Cursor position
        """
        return self._cursor_position
        
    def set_cursor_position(self, position: int) -> None:
        """Set cursor position.
        
        Args:
            position: New cursor position
        """
        self._cursor_position = max(0, min(position, len(self.value)))
        
    def get_selection(self) -> Optional[Tuple[int, int]]:
        """Get current text selection.
        
        Returns:
            Optional[Tuple[int, int]]: Selection start and end positions if any
        """
        if self._selection_start is not None and self._selection_end is not None:
            return (self._selection_start, self._selection_end)
        return None
        
    def set_selection(self, start: int, end: int) -> None:
        """Set text selection.
        
        Args:
            start: Selection start position
            end: Selection end position
        """
        self._selection_start = max(0, min(start, len(self.value)))
        self._selection_end = max(0, min(end, len(self.value)))
        
    def clear_selection(self) -> None:
        """Clear current text selection."""
        self._selection_start = None
        self._selection_end = None
