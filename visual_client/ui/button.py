"""
Button UI component with accessibility and responsive design support.
"""

import pygame
from typing import Optional, Callable, Tuple, Union, List
from .component import UIComponent
from .style import ComponentStyle

def validate_color(color: Optional[Union[Tuple[int, int, int], List[int]]], default: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Validate and convert a color value."""
    if color is None:
        return default
    if isinstance(color, list):
        color = tuple(color)
    if not isinstance(color, tuple) or len(color) != 3:
        return default
    return color

class Button(UIComponent):
    """Button UI component with accessibility and responsive features."""
    
    def __init__(
        self,
        text: str,
        callback: Callable,
        position: Tuple[int, int] = (0, 0),
        size: Tuple[int, int] = (200, 50),
        style: Optional[ComponentStyle] = None,
        icon: Optional[pygame.Surface] = None,
        tooltip: Optional[str] = None
    ):
        """Initialize the button with enhanced accessibility features."""
        super().__init__(position, size)
        self.text = text
        self.callback = callback
        self.style = style or ComponentStyle()
        self.icon = icon
        self.tooltip = tooltip
        
        # State management
        self.hovered = False
        self.focused = False
        self.pressed = False
        self.enabled = True
        
        # Animation state
        self.scale = 1.0
        self.animation_progress = 0.0
        self.target_scale = 1.0
        self.press_offset = 0
        
        # Ensure minimum touch target size
        min_size = self.style.get_touch_size(size)
        self.rect.width = min_size[0]
        self.rect.height = min_size[1]
        
        # Create font with proper size and weight
        self.font = pygame.font.Font(None, self.style.font_size)
        if hasattr(self.font, 'set_bold') and self.style.font_weight == "bold":
            self.font.set_bold(True)
        
        # Initialize surfaces
        self._update_text_surface()
        self._create_feedback_surfaces()
    
    def _create_feedback_surfaces(self):
        """Create surfaces for visual feedback effects."""
        self.ripple_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.highlight_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.shadow_surface = pygame.Surface(
            (self.rect.width + self.style.shadow_blur * 2,
             self.rect.height + self.style.shadow_blur * 2),
            pygame.SRCALPHA
        )
    
    def _update_text_surface(self):
        """Update text surface with current state and style."""
        color_scheme = self.style.get_color_scheme()
        text_color = color_scheme['text'] if self.enabled else self.style.disabled_color
        
        # Apply text rendering with subpixel antialiasing if available
        try:
            self.text_surface = self.font.render(self.text, True, text_color)
        except pygame.error:
            # Fallback to basic rendering if advanced features unavailable
            self.text_surface = self.font.render(self.text, False, text_color)
        
        # Center text in button
        self.text_rect = self.text_surface.get_rect()
        if self.icon:
            # Account for icon when positioning text
            icon_width = self.icon.get_width() + self.style.gap
            self.text_rect.centerx = self.rect.width // 2 + icon_width // 2
        else:
            self.text_rect.centerx = self.rect.width // 2
        self.text_rect.centery = self.rect.height // 2
    
    def update(self, dt: float):
        """Update button state and animations."""
        if not self.enabled:
            return
        
        # Update animations
        if self.style.animation_enabled and not self.style.reduced_motion:
            # Smooth scale animation
            scale_diff = self.target_scale - self.scale
            if abs(scale_diff) > 0.001:
                self.scale += scale_diff * (dt * 10)
            
            # Press animation
            if self.pressed:
                self.press_offset = min(4, self.press_offset + dt * 40)
            else:
                self.press_offset = max(0, self.press_offset - dt * 40)
            
            # Ripple effect
            if self.animation_progress < 1:
                self.animation_progress = min(1, self.animation_progress + dt * 5)
    
    def draw(self, surface: pygame.Surface):
        """Draw the button with visual effects and accessibility indicators."""
        if not self.visible:
            return
        
        # Create temporary surface for effects
        temp_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        
        # Draw shadow
        if self.style.shadow_color[3] > 0 and not self.pressed:
            shadow_offset = (
                self.style.shadow_offset[0],
                self.style.shadow_offset[1] + int(self.press_offset)
            )
            self._draw_shadow(temp_surface, shadow_offset)
        
        # Draw button background
        self._draw_background(temp_surface)
        
        # Draw ripple effect
        if self.animation_progress > 0:
            self._draw_ripple(temp_surface)
        
        # Draw border
        if self.style.border_width > 0:
            self._draw_border(temp_surface)
        
        # Draw icon and text
        if self.icon:
            icon_rect = self.icon.get_rect(
                centery=self.rect.height // 2,
                right=self.text_rect.left - self.style.gap
            )
            temp_surface.blit(self.icon, icon_rect)
        temp_surface.blit(self.text_surface, self.text_rect)
        
        # Draw focus indicator
        if self.focused and self.style.focus_visible:
            self._draw_focus_indicator(temp_surface)
        
        # Apply scaling and draw to main surface
        if self.scale != 1.0:
            scaled_size = (
                int(temp_surface.get_width() * self.scale),
                int(temp_surface.get_height() * self.scale)
            )
            scaled_surface = pygame.transform.smoothscale(temp_surface, scaled_size)
            scaled_rect = scaled_surface.get_rect(center=self.rect.center)
            surface.blit(scaled_surface, scaled_rect)
        else:
            surface.blit(temp_surface, self.rect)
        
        # Draw tooltip if hovered
        if self.tooltip and self.hovered:
            self._draw_tooltip(surface)
    
    def _draw_shadow(self, surface: pygame.Surface, offset: Tuple[int, int]):
        """Draw a soft shadow beneath the button."""
        shadow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            shadow,
            (*self.style.shadow_color[:3], int(self.style.shadow_color[3] * 255)),
            shadow.get_rect(),
            border_radius=self.style.corner_radius
        )
        surface.blit(shadow, offset)
    
    def _draw_background(self, surface: pygame.Surface):
        """Draw the button background with current state colors."""
        color_scheme = self.style.get_color_scheme()
        if self.pressed:
            color = self.style.active_color
        elif self.hovered:
            color = self.style.hover_color
        else:
            color = color_scheme['background']
        
        pygame.draw.rect(
            surface,
            color,
            surface.get_rect(),
            border_radius=self.style.corner_radius
        )
    
    def _draw_ripple(self, surface: pygame.Surface):
        """Draw ripple effect animation."""
        ripple_radius = int(self.rect.width * self.animation_progress)
        ripple_alpha = int((1 - self.animation_progress) * 50)
        pygame.draw.circle(
            self.ripple_surface,
            (255, 255, 255, ripple_alpha),
            (self.rect.width // 2, self.rect.height // 2),
            ripple_radius
        )
        surface.blit(self.ripple_surface, (0, 0))
    
    def _draw_border(self, surface: pygame.Surface):
        """Draw button border with appropriate color."""
        color_scheme = self.style.get_color_scheme()
        border_color = (
            color_scheme['focus'] if self.focused
            else color_scheme['border']
        )
        pygame.draw.rect(
            surface,
            border_color,
            surface.get_rect(),
            self.style.border_width,
            border_radius=self.style.corner_radius
        )
    
    def _draw_focus_indicator(self, surface: pygame.Surface):
        """Draw keyboard focus indicator."""
        focus_rect = surface.get_rect().inflate(
            self.style.focus_offset * 2,
            self.style.focus_offset * 2
        )
        pygame.draw.rect(
            surface,
            self.style.focus_color,
            focus_rect,
            self.style.focus_width,
            border_radius=self.style.corner_radius + self.style.focus_offset
        )
    
    def _draw_tooltip(self, surface: pygame.Surface):
        """Draw tooltip when button is hovered."""
        tooltip_surface = self.font.render(
            self.tooltip,
            True,
            self.style.font_color
        )
        tooltip_rect = tooltip_surface.get_rect()
        tooltip_rect.bottom = self.rect.top - 8
        tooltip_rect.centerx = self.rect.centerx
        
        # Draw tooltip background
        pygame.draw.rect(
            surface,
            self.style.background_color,
            tooltip_rect.inflate(16, 8),
            border_radius=4
        )
        surface.blit(tooltip_surface, tooltip_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events with enhanced accessibility support."""
        if not self.enabled or not self.visible:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.hovered
            self.hovered = self.rect.collidepoint(event.pos)
            
            if self.style.animation_enabled:
                self.target_scale = (
                    self.style.hover_scale if self.hovered
                    else 1.0
                )
            
            return was_hovered != self.hovered
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                self.animation_progress = 0
                return True
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.focused:
                self.pressed = True
                self.animation_progress = 0
                return True
        
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.focused:
                self.pressed = False
                if self.callback:
                    self.callback()
                return True
        
        return False
    
    def set_enabled(self, enabled: bool):
        """Set button enabled state with visual update."""
        if self.enabled != enabled:
            self.enabled = enabled
            self._update_text_surface()
    
    def set_focused(self, focused: bool):
        """Set button focus state with visual update."""
        if self.focused != focused:
            self.focused = focused
            if focused and self.style.haptic_feedback:
                # TODO: Implement haptic feedback for platforms that support it
                pass 