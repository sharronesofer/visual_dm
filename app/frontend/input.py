"""
Frontend input handling system.
"""

from typing import Callable, Dict, Optional

class InputHandler:
    """Handles user input and input mapping."""
    
    def __init__(self):
        self.key_bindings: Dict[str, Callable] = {}
        self.mouse_bindings: Dict[str, Callable] = {}
        self.gamepad_bindings: Dict[str, Callable] = {}
        
    def bind_key(self, key: str, action: Callable) -> None:
        """Bind a key to an action."""
        self.key_bindings[key] = action
        
    def bind_mouse(self, button: str, action: Callable) -> None:
        """Bind a mouse button to an action."""
        self.mouse_bindings[button] = action
        
    def bind_gamepad(self, button: str, action: Callable) -> None:
        """Bind a gamepad button to an action."""
        self.gamepad_bindings[button] = action
        
    def handle_key(self, key: str) -> Optional[bool]:
        """Handle a key press."""
        if key in self.key_bindings:
            return self.key_bindings[key]()
        return None
        
    def handle_mouse(self, button: str, x: int, y: int) -> Optional[bool]:
        """Handle a mouse action."""
        if button in self.mouse_bindings:
            return self.mouse_bindings[button](x, y)
        return None
        
    def handle_gamepad(self, button: str) -> Optional[bool]:
        """Handle a gamepad button press."""
        if button in self.gamepad_bindings:
            return self.gamepad_bindings[button]()
        return None
        
    def clear_bindings(self) -> None:
        """Clear all input bindings."""
        self.key_bindings.clear()
        self.mouse_bindings.clear()
        self.gamepad_bindings.clear() 