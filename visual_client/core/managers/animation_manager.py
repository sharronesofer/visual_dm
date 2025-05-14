"""
Animation manager for handling common animations and transitions.
"""

import pygame
import math
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum, auto
from visual_client.ui.components import BaseComponent

class AnimationType(Enum):
    """Types of animations."""
    FADE = auto()
    SLIDE = auto()
    SCALE = auto()
    COLOR = auto()
    ROTATE = auto()

@dataclass
class Animation:
    """Animation data structure."""
    component: BaseComponent
    type: AnimationType
    start_value: Any
    end_value: Any
    duration: float
    elapsed: float = 0.0
    easing: str = "linear"
    callback: Optional[Callable] = None

class AnimationManager:
    """Manager for handling animations."""
    
    def __init__(self):
        """Initialize the animation manager."""
        self.animations: List[Animation] = []
        
    def add_animation(self, name: str, component: BaseComponent, 
                     animation_type: AnimationType, start_value: Any,
                     end_value: Any, duration: float, easing: str = "linear",
                     callback: Optional[Callable] = None) -> None:
        """Add an animation.
        
        Args:
            name: Animation name
            component: Component to animate
            animation_type: Type of animation
            start_value: Starting value
            end_value: Ending value
            duration: Animation duration in seconds
            easing: Easing function name
            callback: Callback function when animation completes
        """
        animation = Animation(
            component=component,
            type=animation_type,
            start_value=start_value,
            end_value=end_value,
            duration=duration,
            easing=easing,
            callback=callback
        )
        self.animations.append(animation)
        
    def update(self, dt: float) -> None:
        """Update animations.
        
        Args:
            dt: Time delta since last update
        """
        completed_animations = []
        
        for animation in self.animations:
            animation.elapsed += dt
            
            # Calculate progress (0 to 1)
            progress = min(1.0, animation.elapsed / animation.duration)
            
            # Apply easing
            progress = self._apply_easing(progress, animation.easing)
            
            # Update component based on animation type
            self._update_component(animation, progress)
            
            # Check if animation is complete
            if animation.elapsed >= animation.duration:
                completed_animations.append(animation)
                if animation.callback:
                    animation.callback()
                    
        # Remove completed animations
        for animation in completed_animations:
            self.animations.remove(animation)
            
    def _apply_easing(self, progress: float, easing: str) -> float:
        """Apply easing function to progress.
        
        Args:
            progress: Current progress (0 to 1)
            easing: Easing function name
            
        Returns:
            float: Eased progress
        """
        if easing == "linear":
            return progress
        elif easing == "ease_in":
            return progress * progress
        elif easing == "ease_out":
            return 1 - (1 - progress) * (1 - progress)
        elif easing == "ease_in_out":
            if progress < 0.5:
                return 2 * progress * progress
            else:
                return 1 - (-2 * progress + 2) ** 2 / 2
        elif easing == "bounce":
            if progress < 0.5:
                return 4 * progress * progress
            else:
                return 1 - (-2 * progress + 2) ** 2 / 2
        else:
            return progress
            
    def _update_component(self, animation: Animation, progress: float) -> None:
        """Update component based on animation type.
        
        Args:
            animation: Animation to apply
            progress: Current progress (0 to 1)
        """
        if animation.type == AnimationType.FADE:
            self._update_fade(animation, progress)
        elif animation.type == AnimationType.SLIDE:
            self._update_slide(animation, progress)
        elif animation.type == AnimationType.SCALE:
            self._update_scale(animation, progress)
        elif animation.type == AnimationType.COLOR:
            self._update_color(animation, progress)
        elif animation.type == AnimationType.ROTATE:
            self._update_rotate(animation, progress)
            
    def _update_fade(self, animation: Animation, progress: float) -> None:
        """Update fade animation.
        
        Args:
            animation: Animation to apply
            progress: Current progress (0 to 1)
        """
        alpha = int(255 * (1 - progress))
        if hasattr(animation.component, 'set_alpha'):
            animation.component.set_alpha(alpha)
            
    def _update_slide(self, animation: Animation, progress: float) -> None:
        """Update slide animation.
        
        Args:
            animation: Animation to apply
            progress: Current progress (0 to 1)
        """
        start_x, start_y = animation.start_value
        end_x, end_y = animation.end_value
        
        x = start_x + (end_x - start_x) * progress
        y = start_y + (end_y - start_y) * progress
        
        animation.component.rect.x = int(x)
        animation.component.rect.y = int(y)
        
    def _update_scale(self, animation: Animation, progress: float) -> None:
        """Update scale animation.
        
        Args:
            animation: Animation to apply
            progress: Current progress (0 to 1)
        """
        start_scale = animation.start_value
        end_scale = animation.end_value
        
        scale = start_scale + (end_scale - start_scale) * progress
        
        if hasattr(animation.component, 'set_scale'):
            animation.component.set_scale(scale)
            
    def _update_color(self, animation: Animation, progress: float) -> None:
        """Update color animation.
        
        Args:
            animation: Animation to apply
            progress: Current progress (0 to 1)
        """
        start_r, start_g, start_b = animation.start_value
        end_r, end_g, end_b = animation.end_value
        
        r = int(start_r + (end_r - start_r) * progress)
        g = int(start_g + (end_g - start_g) * progress)
        b = int(start_b + (end_b - start_b) * progress)
        
        if hasattr(animation.component, 'set_color'):
            animation.component.set_color((r, g, b))
            
    def _update_rotate(self, animation: Animation, progress: float) -> None:
        """Update rotate animation.
        
        Args:
            animation: Animation to apply
            progress: Current progress (0 to 1)
        """
        start_angle = animation.start_value
        end_angle = animation.end_value
        
        angle = start_angle + (end_angle - start_angle) * progress
        
        if hasattr(animation.component, 'set_rotation'):
            animation.component.set_rotation(angle)
            
    def stop_all(self) -> None:
        """Stop all animations."""
        self.animations.clear()
        
    def stop_animation(self, name: str) -> None:
        """Stop a specific animation.
        
        Args:
            name: Name of animation to stop
        """
        self.animations = [a for a in self.animations if a.name != name] 