"""
Accessibility management for UI components.
"""

from typing import Dict, List, Optional, Tuple
import pygame
from backend.infrastructure.events.middleware.error_handler import handle_component_error, ErrorSeverity

class AccessibilityManager:
    """Manages accessibility features for UI components."""
    
    def __init__(self):
        """Initialize the accessibility manager."""
        self.focus_order: List[str] = []
        self.current_focus_index = 0
        self.focus_rect_color = (255, 255, 0)  # Yellow focus indicator
        self.focus_rect_width = 2
        self.focus_rect_padding = 2
        
        # WCAG contrast ratios
        self.min_contrast_ratio = 4.5  # WCAG AA standard
        self.enhanced_contrast_ratio = 7.0  # WCAG AAA standard
        
    def add_to_focus_order(self, component_id: str) -> None:
        """Add a component to the focus order."""
        try:
            if component_id not in self.focus_order:
                self.focus_order.append(component_id)
        except Exception as e:
            handle_component_error(
                "AccessibilityManager",
                "add_to_focus_order",
                e,
                ErrorSeverity.ERROR,
                {"component_id": component_id}
            )
            
    def remove_from_focus_order(self, component_id: str) -> None:
        """Remove a component from the focus order."""
        try:
            if component_id in self.focus_order:
                self.focus_order.remove(component_id)
                if self.current_focus_index >= len(self.focus_order):
                    self.current_focus_index = max(0, len(self.focus_order) - 1)
        except Exception as e:
            handle_component_error(
                "AccessibilityManager",
                "remove_from_focus_order",
                e,
                ErrorSeverity.ERROR,
                {"component_id": component_id}
            )
            
    def move_focus(self, direction: int) -> str:
        """Move focus in the specified direction (1 for forward, -1 for backward)."""
        try:
            if not self.focus_order:
                return ""
                
            self.current_focus_index = (self.current_focus_index + direction) % len(self.focus_order)
            return self.focus_order[self.current_focus_index]
        except Exception as e:
            handle_component_error(
                "AccessibilityManager",
                "move_focus",
                e,
                ErrorSeverity.ERROR,
                {"direction": direction}
            )
            return ""
            
    def get_current_focus(self) -> str:
        """Get the currently focused component ID."""
        try:
            if not self.focus_order:
                return ""
            return self.focus_order[self.current_focus_index]
        except Exception as e:
            handle_component_error(
                "AccessibilityManager",
                "get_current_focus",
                e,
                ErrorSeverity.ERROR
            )
            return ""
            
    def draw_focus_indicator(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw a visible focus indicator around the component."""
        try:
            # Create padded rect for focus indicator
            focus_rect = pygame.Rect(
                rect.x - self.focus_rect_padding,
                rect.y - self.focus_rect_padding,
                rect.width + (2 * self.focus_rect_padding),
                rect.height + (2 * self.focus_rect_padding)
            )
            
            # Draw focus indicator
            pygame.draw.rect(
                surface,
                self.focus_rect_color,
                focus_rect,
                self.focus_rect_width
            )
        except Exception as e:
            handle_component_error(
                "AccessibilityManager",
                "draw_focus_indicator",
                e,
                ErrorSeverity.ERROR
            )
            
    def calculate_contrast_ratio(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """Calculate the contrast ratio between two colors."""
        try:
            def get_relative_luminance(color: Tuple[int, int, int]) -> float:
                r, g, b = [c / 255.0 for c in color]
                r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
                g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
                b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
                return 0.2126 * r + 0.7152 * g + 0.0722 * b
                
            l1 = get_relative_luminance(color1)
            l2 = get_relative_luminance(color2)
            
            lighter = max(l1, l2)
            darker = min(l1, l2)
            
            return (lighter + 0.05) / (darker + 0.05)
        except Exception as e:
            handle_component_error(
                "AccessibilityManager",
                "calculate_contrast_ratio",
                e,
                ErrorSeverity.ERROR,
                {"color1": color1, "color2": color2}
            )
            return 0.0
            
    def ensure_contrast_compliance(
        self,
        foreground: Tuple[int, int, int],
        background: Tuple[int, int, int],
        enhanced: bool = False
    ) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """Ensure colors meet WCAG contrast requirements."""
        try:
            target_ratio = self.enhanced_contrast_ratio if enhanced else self.min_contrast_ratio
            current_ratio = self.calculate_contrast_ratio(foreground, background)
            
            if current_ratio >= target_ratio:
                return foreground, background
                
            # Adjust colors to meet contrast requirements
            # This is a simple implementation - you might want to use a more sophisticated algorithm
            if current_ratio < target_ratio:
                # Make foreground darker or background lighter
                if sum(foreground) > sum(background):
                    # Foreground is lighter, make it darker
                    adjusted_foreground = tuple(max(0, c - 20) for c in foreground)
                    return self.ensure_contrast_compliance(adjusted_foreground, background, enhanced)
                else:
                    # Background is lighter, make it darker
                    adjusted_background = tuple(max(0, c - 20) for c in background)
                    return self.ensure_contrast_compliance(foreground, adjusted_background, enhanced)
                    
            return foreground, background
        except Exception as e:
            handle_component_error(
                "AccessibilityManager",
                "ensure_contrast_compliance",
                e,
                ErrorSeverity.ERROR,
                {"foreground": foreground, "background": background, "enhanced": enhanced}
            )
            return foreground, background
            
    def handle_keyboard_event(self, event: pygame.event.Event) -> bool:
        """Handle keyboard events for accessibility."""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    # Move focus forward (shift+tab for backward)
                    shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
                    self.move_focus(-1 if shift_pressed else 1)
                    return True
                elif event.key == pygame.K_RETURN:
                    # Activate focused component
                    focused_id = self.get_current_focus()
                    if focused_id:
                        # Trigger activation event
                        return True
            return False
        except Exception as e:
            handle_component_error(
                "AccessibilityManager",
                "handle_keyboard_event",
                e,
                ErrorSeverity.ERROR,
                {"event": str(event)}
            )
            return False

# Global accessibility manager instance
accessibility_manager = AccessibilityManager() 