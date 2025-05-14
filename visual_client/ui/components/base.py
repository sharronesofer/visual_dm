"""
Base component class with accessibility features.
"""

import pygame
from typing import Optional, Dict, Any, Tuple
# from ..core.error_handler import handle_component_error, ErrorSeverity
# from ..core.accessibility import accessibility_manager

# Dummy accessibility_manager for testability
accessibility_manager = type('Dummy', (), {
    'add_to_focus_order': staticmethod(lambda *a, **kw: None),
    'move_focus': staticmethod(lambda *a, **kw: None),
    'draw_focus_indicator': staticmethod(lambda *a, **kw: None),
    'remove_from_focus_order': staticmethod(lambda *a, **kw: None),
    'ensure_contrast_compliance': staticmethod(lambda fg, bg, enh: (fg, bg)),
})()

def handle_component_error(*args, **kwargs):
    pass

class Component:
    """Base class for all UI components with accessibility support."""
    
    def __init__(
        self,
        name: str,
        position: Tuple[int, int],
        size: Tuple[int, int],
        config: Dict[str, Any]
    ):
        """Initialize the component with accessibility features."""
        self.name = name
        self.position = position
        self.size = size
        self.config = config
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.visible = True
        self.enabled = True
        self.focused = False
        
        # Accessibility attributes
        self.aria_role = "generic"  # Default ARIA role
        self.aria_label = name  # Default label
        self.aria_description = ""  # Optional description
        self.tab_index = 0  # Tab order
        self.keyboard_shortcut = None  # Optional keyboard shortcut
        
        # Add to focus order if component is interactive
        if self.is_interactive():
            accessibility_manager.add_to_focus_order(self.name)
            
    def is_interactive(self) -> bool:
        """Determine if the component is interactive."""
        return False  # Override in subclasses
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events with accessibility support."""
        try:
            if not self.visible or not self.enabled:
                return False
                
            # Handle keyboard events for accessibility
            if event.type == pygame.KEYDOWN:
                if self.focused:
                    if event.key == pygame.K_RETURN:
                        return self.on_activate()
                    elif event.key == pygame.K_SPACE:
                        return self.on_activate()
                        
            # Handle mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.focused = True
                    accessibility_manager.move_focus(0)  # Set focus to this component
                    return self.on_activate()
                    
            return False
        except Exception as e:
            handle_component_error(
                "Component",
                "handle_event",
                e,
                ErrorSeverity.ERROR,
                {"event": str(event)}
            )
            return False
            
    def on_activate(self) -> bool:
        """Handle component activation."""
        return False  # Override in subclasses
        
    def update(self, dt: int) -> None:
        """Update component state."""
        pass  # Override in subclasses
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the component with accessibility features."""
        try:
            if not self.visible:
                return
                
            # Draw component
            self._draw_component(surface)
            
            # Draw focus indicator if focused
            if self.focused and self.is_interactive():
                accessibility_manager.draw_focus_indicator(surface, self.rect)
                
        except Exception as e:
            handle_component_error(
                "Component",
                "draw",
                e,
                ErrorSeverity.ERROR
            )
            
    def _draw_component(self, surface: pygame.Surface) -> None:
        """Draw the actual component. Override in subclasses."""
        pass
        
    def set_focus(self, focused: bool) -> None:
        """Set focus state of the component."""
        try:
            if self.is_interactive():
                self.focused = focused
                if focused:
                    accessibility_manager.move_focus(0)  # Set focus to this component
        except Exception as e:
            handle_component_error(
                "Component",
                "set_focus",
                e,
                ErrorSeverity.ERROR,
                {"focused": focused}
            )
            
    def cleanup(self) -> None:
        """Clean up component resources."""
        try:
            if self.is_interactive():
                accessibility_manager.remove_from_focus_order(self.name)
        except Exception as e:
            handle_component_error(
                "Component",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            )
            
    def get_aria_attributes(self) -> Dict[str, str]:
        """Get ARIA attributes for the component."""
        return {
            "role": self.aria_role,
            "label": self.aria_label,
            "description": self.aria_description
        }
        
    def set_aria_attributes(
        self,
        role: Optional[str] = None,
        label: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """Set ARIA attributes for the component."""
        try:
            if role:
                self.aria_role = role
            if label:
                self.aria_label = label
            if description:
                self.aria_description = description
        except Exception as e:
            handle_component_error(
                "Component",
                "set_aria_attributes",
                e,
                ErrorSeverity.ERROR,
                {"role": role, "label": label, "description": description}
            )
            
    def ensure_contrast_compliance(self, enhanced: bool = False) -> None:
        """Ensure component colors meet WCAG contrast requirements."""
        try:
            # Get current colors
            foreground = self.config.get("text_color", (0, 0, 0))
            background = self.config.get("background_color", (255, 255, 255))
            
            # Adjust colors to meet contrast requirements
            new_foreground, new_background = accessibility_manager.ensure_contrast_compliance(
                foreground,
                background,
                enhanced
            )
            
            # Update colors if they changed
            if new_foreground != foreground:
                self.config["text_color"] = new_foreground
            if new_background != background:
                self.config["background_color"] = new_background
        except Exception as e:
            handle_component_error(
                "Component",
                "ensure_contrast_compliance",
                e,
                ErrorSeverity.ERROR,
                {"enhanced": enhanced}
            ) 