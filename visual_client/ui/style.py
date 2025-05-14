"""
UI component styling.
"""

from typing import Optional, Tuple, Union, List, Dict
from dataclasses import dataclass, field

@dataclass
class ComponentStyle:
    """Style configuration for UI components with accessibility and responsive design support."""
    # Design Tokens - Colors
    primary_color: Tuple[int, int, int] = (74, 144, 226)     # Brand blue
    secondary_color: Tuple[int, int, int] = (45, 156, 219)   # Secondary accent
    success_color: Tuple[int, int, int] = (72, 199, 116)     # Success green
    warning_color: Tuple[int, int, int] = (255, 159, 67)     # Warning orange
    danger_color: Tuple[int, int, int] = (242, 78, 78)       # Error red
    
    # Base colors with high contrast ratios
    font_color: Union[Tuple[int, int, int], List[int]] = (255, 255, 255)  # WCAG AAA compliant
    background_color: Optional[Union[Tuple[int, int, int], List[int]]] = (40, 40, 40)
    hover_color: Optional[Union[Tuple[int, int, int], List[int]]] = (60, 60, 60)
    active_color: Optional[Union[Tuple[int, int, int], List[int]]] = (80, 80, 80)
    disabled_color: Optional[Union[Tuple[int, int, int], List[int]]] = (30, 30, 30)
    
    # Typography
    font_size: int = 24
    font_weight: str = "normal"
    line_height: float = 1.5
    letter_spacing: float = 0.5
    
    # Spacing and Layout
    padding: int = 16
    margin: int = 16
    gap: int = 16
    border_width: int = 2
    border_color: Optional[Union[Tuple[int, int, int], List[int]]] = (100, 100, 100)
    corner_radius: int = 8
    
    # Elevation and Depth
    shadow_color: Optional[Union[Tuple[int, int, int, float], List[float]]] = (0, 0, 0, 0.2)
    shadow_offset: Tuple[int, int] = (0, 4)
    shadow_blur: int = 8
    
    # Animation and Interaction
    transition_duration: int = 200
    animation_enabled: bool = True
    hover_scale: float = 1.05
    active_scale: float = 0.98
    
    # Accessibility
    aria_label: Optional[str] = None
    aria_role: Optional[str] = None
    aria_description: Optional[str] = None
    focus_visible: bool = True
    focus_color: Tuple[int, int, int] = (0, 120, 215)
    focus_width: int = 3
    focus_offset: int = 2
    
    # Touch and Mobile
    touch_target_size: int = 44  # iOS HIG minimum
    touch_feedback: bool = True
    haptic_feedback: bool = True
    
    # Responsive Design
    min_width: Optional[int] = None
    max_width: Optional[int] = None
    min_height: Optional[int] = None
    max_height: Optional[int] = None
    scale_factor: float = 1.0
    breakpoints: Dict[str, int] = field(default_factory=lambda: {
        'sm': 640,   # Small devices
        'md': 768,   # Medium devices
        'lg': 1024,  # Large devices
        'xl': 1280,  # Extra large devices
        '2xl': 1536  # 2X Extra large devices
    })
    
    # High Contrast Mode Support
    high_contrast_enabled: bool = False
    high_contrast_colors: Dict[str, Tuple[int, int, int]] = field(default_factory=lambda: {
        'text': (255, 255, 255),
        'background': (0, 0, 0),
        'border': (255, 255, 255),
        'focus': (255, 255, 0)
    })
    
    # Reduced Motion Support
    reduced_motion: bool = False
    
    def get_color_scheme(self, high_contrast: bool = False) -> Dict[str, Tuple[int, int, int]]:
        """Get the appropriate color scheme based on contrast preferences."""
        if high_contrast or self.high_contrast_enabled:
            return self.high_contrast_colors
        return {
            'text': self.font_color,
            'background': self.background_color,
            'border': self.border_color,
            'focus': self.focus_color
        }
    
    def get_animation_duration(self, reduced_motion: bool = False) -> int:
        """Get appropriate animation duration based on motion preferences."""
        if reduced_motion or self.reduced_motion:
            return 0
        return self.transition_duration
    
    def get_touch_size(self, element_size: Tuple[int, int]) -> Tuple[int, int]:
        """Ensure element meets minimum touch target size requirements."""
        width, height = element_size
        return (
            max(width, self.touch_target_size),
            max(height, self.touch_target_size)
        )
    
    def get_responsive_size(self, size: Tuple[int, int], viewport_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate responsive size based on viewport and constraints."""
        width, height = size
        viewport_width, viewport_height = viewport_size
        
        # Apply scale factor
        width *= self.scale_factor
        height *= self.scale_factor
        
        # Apply min/max constraints
        if self.min_width:
            width = max(width, self.min_width)
        if self.max_width:
            width = min(width, self.max_width)
        if self.min_height:
            height = max(height, self.min_height)
        if self.max_height:
            height = min(height, self.max_height)
        
        return (int(width), int(height))

    def __post_init__(self):
        """Convert color lists to tuples after initialization."""
        self.font_color = tuple(self.font_color) if isinstance(self.font_color, list) else self.font_color
        self.background_color = tuple(self.background_color) if isinstance(self.background_color, list) else self.background_color
        self.hover_color = tuple(self.hover_color) if isinstance(self.hover_color, list) else self.hover_color
        self.active_color = tuple(self.active_color) if isinstance(self.active_color, list) else self.active_color
        self.disabled_color = tuple(self.disabled_color) if isinstance(self.disabled_color, list) else self.disabled_color
        self.border_color = tuple(self.border_color) if isinstance(self.border_color, list) else self.border_color
        self.shadow_color = tuple(self.shadow_color) if isinstance(self.shadow_color, list) else self.shadow_color 