"""
Multiline text input component with validation and sanitization.
"""

from typing import Optional, List
from .textbox import Textbox, TextboxConfig

class MultilineTextBox(Textbox):
    """Multiline text input component with validation and sanitization."""
    
    def __init__(self, config: Optional[TextboxConfig] = None):
        if config is None:
            config = TextboxConfig(
                multiline=True,
                max_length=1000,
                allowed_chars=r'[\w\s.,!?@#$%^&*()\-_=+\[\]{}|;:\'"<>/\\\\n]'
            )
        else:
            config.multiline = True
        super().__init__(config)
        
    def insert_text(self, text: str, position: Optional[int] = None) -> None:
        """Insert text at specified position with newline support.
        
        Args:
            text: Text to insert
            position: Position to insert at (defaults to cursor position)
            
        Raises:
            ValidationError: If resulting text fails validation
        """
        # Convert line endings to \n
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        super().insert_text(text, position)
        
    def get_lines(self) -> List[str]:
        """Get text as list of lines.
        
        Returns:
            List[str]: List of lines
        """
        return self.value.split('\n')
        
    def set_lines(self, lines: List[str]) -> None:
        """Set text from list of lines.
        
        Args:
            lines: List of lines
            
        Raises:
            ValidationError: If resulting text fails validation
        """
        self.set_text('\n'.join(lines)) 