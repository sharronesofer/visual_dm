"""
Specialized UI components with optimized implementations.

This module provides a hierarchy of UI components:
1. BaseComponent: Abstract base class with core functionality
2. InteractiveComponent: Base for components that handle user input
3. Specialized components for specific use cases:
   - Button: Clickable button with states
   - TextBox: Text input with validation
   - Panel: Container for other components
   - Label: Text display
   - ProgressBar: Progress indicator
   - ScrollablePanel: Scrollable container
   - Menu: Hierarchical menu system
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
import pygame
# from app.core.utils.error_utils import UIError
UIError = Exception
# from app.core.utils.screen_utils import ScreenManager
# from app.core.utils.input_utils import InputHandler
class ScreenManager:
    pass
class InputHandler:
    pass
# from app.core.utils.render_utils import Renderer
class Renderer:
    pass

@dataclass
class ComponentStyle:
    """Base style configuration for components."""
    background_color: Tuple[int, int, int] = (0, 0, 0)
    border_color: Tuple[int, int, int] = (255, 255, 255)
    border_width: int = 1
    padding: int = 5
    margin: int = 5
    font_size: int = 16
    font_color: Tuple[int, int, int] = (255, 255, 255)
    hover_color: Optional[Tuple[int, int, int]] = None
    active_color: Optional[Tuple[int, int, int]] = None
    disabled_color: Optional[Tuple[int, int, int]] = None

class BaseComponent(ABC):
    """Abstract base class for all UI components."""
    
    def __init__(
        self,
        rect: pygame.Rect,
        style: Optional[ComponentStyle] = None,
        parent: Optional['BaseComponent'] = None
    ):
        self.rect = rect
        self.style = style or ComponentStyle()
        self.parent = parent
        self.visible = True
        self.enabled = True
        self._dirty = True  # For rendering optimization
        self._children: List[BaseComponent] = []
        
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the component and its children.
        
        Args:
            surface: Surface to draw on
        """
        pass
        
    def update(self) -> None:
        """Update component state."""
        if self._dirty:
            self._update_layout()
            self._dirty = False
            
    def add_child(self, child: 'BaseComponent') -> None:
        """Add a child component.
        
        Args:
            child: Component to add
        """
        child.parent = self
        self._children.append(child)
        self._dirty = True
        
    def remove_child(self, child: 'BaseComponent') -> None:
        """Remove a child component.
        
        Args:
            child: Component to remove
        """
        if child in self._children:
            child.parent = None
            self._children.remove(child)
            self._dirty = True
            
    def _update_layout(self) -> None:
        """Update component layout."""
        for child in self._children:
            child.update()
            
    def mark_dirty(self) -> None:
        """Mark component as needing update."""
        self._dirty = True
        if self.parent:
            self.parent.mark_dirty()

class InteractiveComponent(BaseComponent):
    """Base class for components that handle user input."""
    
    def __init__(
        self,
        rect: pygame.Rect,
        style: Optional[ComponentStyle] = None,
        parent: Optional[BaseComponent] = None
    ):
        super().__init__(rect, style, parent)
        self.hovered = False
        self.focused = False
        self._callbacks: Dict[str, List[Callable]] = {
            'click': [],
            'hover': [],
            'focus': [],
            'blur': []
        }
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events.
        
        Args:
            event: Event to handle
            
        Returns:
            bool: True if event was handled
        """
        if not self.enabled or not self.visible:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return self._handle_mouse_up(event)
            
        return False
        
    def _handle_mouse_motion(self, event: pygame.event.Event) -> None:
        """Handle mouse motion events."""
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(event.pos)
        
        if was_hovered != self.hovered:
            self._trigger_callbacks('hover')
            self.mark_dirty()
            
    def _handle_mouse_down(self, event: pygame.event.Event) -> bool:
        """Handle mouse button down events."""
        if self.rect.collidepoint(event.pos):
            self.focused = True
            self._trigger_callbacks('focus')
            self.mark_dirty()
            return True
        return False
        
    def _handle_mouse_up(self, event: pygame.event.Event) -> bool:
        """Handle mouse button up events."""
        if self.focused and self.rect.collidepoint(event.pos):
            self._trigger_callbacks('click')
            return True
        return False
        
    def add_callback(self, event_type: str, callback: Callable) -> None:
        """Add an event callback.
        
        Args:
            event_type: Type of event
            callback: Function to call
        """
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)
            
    def _trigger_callbacks(self, event_type: str) -> None:
        """Trigger callbacks for an event type.
        
        Args:
            event_type: Type of event
        """
        for callback in self._callbacks[event_type]:
            try:
                callback(self)
            except Exception as e:
                raise UIError(f"Callback error: {str(e)}")

class Button(InteractiveComponent):
    """Clickable button component."""
    
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        style: Optional[ComponentStyle] = None,
        parent: Optional[BaseComponent] = None
    ):
        super().__init__(rect, style, parent)
        self.text = text
        self.pressed = False
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button."""
        if not self.visible:
            return
            
        # Draw background
        color = self._get_current_color()
        pygame.draw.rect(surface, color, self.rect)
        
        # Draw border
        if self.style.border_width > 0:
            pygame.draw.rect(
                surface,
                self.style.border_color,
                self.rect,
                self.style.border_width
            )
            
        # Draw text
        font = pygame.font.SysFont(None, self.style.font_size)
        text_surface = font.render(self.text, True, self.style.font_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def _get_current_color(self) -> Tuple[int, int, int]:
        """Get the current background color based on state."""
        if not self.enabled:
            return self.style.disabled_color or self.style.background_color
        if self.pressed:
            return self.style.active_color or self.style.background_color
        if self.hovered:
            return self.style.hover_color or self.style.background_color
        return self.style.background_color

class Panel(BaseComponent):
    """Container component for organizing other components."""
    
    def __init__(
        self,
        rect: pygame.Rect,
        style: Optional[ComponentStyle] = None,
        parent: Optional[BaseComponent] = None
    ):
        super().__init__(rect, style, parent)
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the panel and its children."""
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(surface, self.style.background_color, self.rect)
        
        # Draw border
        if self.style.border_width > 0:
            pygame.draw.rect(
                surface,
                self.style.border_color,
                self.rect,
                self.style.border_width
            )
            
        # Draw children
        for child in self._children:
            child.draw(surface)

class ScrollablePanel(Panel):
    """Panel with scrollable content."""
    
    def __init__(
        self,
        rect: pygame.Rect,
        style: Optional[ComponentStyle] = None,
        parent: Optional[BaseComponent] = None
    ):
        super().__init__(rect, style, parent)
        self.scroll_position = 0
        self.scroll_speed = 20
        self._content_height = 0
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the scrollable panel."""
        if not self.visible:
            return
            
        # Create clipping region
        clip_rect = pygame.Rect(
            self.rect.x + self.style.padding,
            self.rect.y + self.style.padding,
            self.rect.width - 2 * self.style.padding,
            self.rect.height - 2 * self.style.padding
        )
        
        # Save current clipping region
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        
        # Draw background
        pygame.draw.rect(surface, self.style.background_color, self.rect)
        
        # Draw content with scroll offset
        for child in self._children:
            child_rect = child.rect.copy()
            child_rect.y -= self.scroll_position
            if child_rect.colliderect(clip_rect):
                child.draw(surface)
                
        # Restore clipping region
        surface.set_clip(old_clip)
        
        # Draw scrollbar
        self._draw_scrollbar(surface)
        
    def _draw_scrollbar(self, surface: pygame.Surface) -> None:
        """Draw the scrollbar."""
        if self._content_height <= self.rect.height:
            return
            
        # Calculate scrollbar dimensions
        scrollbar_width = 10
        scrollbar_rect = pygame.Rect(
            self.rect.right - scrollbar_width,
            self.rect.top,
            scrollbar_width,
            self.rect.height
        )
        
        # Draw scrollbar background
        pygame.draw.rect(surface, (50, 50, 50), scrollbar_rect)
        
        # Calculate thumb position and size
        thumb_height = max(
            20,
            int(self.rect.height * (self.rect.height / self._content_height))
        )
        thumb_y = int(
            self.rect.top + (self.scroll_position / self._content_height) *
            (self.rect.height - thumb_height)
        )
        
        # Draw scrollbar thumb
        thumb_rect = pygame.Rect(
            scrollbar_rect.x,
            thumb_y,
            scrollbar_width,
            thumb_height
        )
        pygame.draw.rect(surface, (100, 100, 100), thumb_rect)

class Menu(InteractiveComponent):
    """Hierarchical menu component."""
    
    def __init__(
        self,
        rect: pygame.Rect,
        items: List[Dict[str, Any]],
        style: Optional[ComponentStyle] = None,
        parent: Optional[BaseComponent] = None
    ):
        super().__init__(rect, style, parent)
        self.items = items
        self.selected_item = None
        self.submenu = None
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the menu and its items."""
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(surface, self.style.background_color, self.rect)
        
        # Draw items
        item_height = self.rect.height // len(self.items)
        for i, item in enumerate(self.items):
            item_rect = pygame.Rect(
                self.rect.x,
                self.rect.y + i * item_height,
                self.rect.width,
                item_height
            )
            
            # Draw item background
            if item == self.selected_item:
                pygame.draw.rect(
                    surface,
                    self.style.hover_color or self.style.background_color,
                    item_rect
                )
                
            # Draw item text
            font = pygame.font.SysFont(None, self.style.font_size)
            text_surface = font.render(
                item['text'],
                True,
                self.style.font_color
            )
            text_rect = text_surface.get_rect(
                center=item_rect.center
            )
            surface.blit(text_surface, text_rect)
            
        # Draw submenu if active
        if self.submenu:
            self.submenu.draw(surface)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle menu events."""
        if not super().handle_event(event):
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            item_height = self.rect.height // len(self.items)
            item_index = (event.pos[1] - self.rect.y) // item_height
            
            if 0 <= item_index < len(self.items):
                self.selected_item = self.items[item_index]
                if 'submenu' in self.selected_item:
                    self._show_submenu(item_index)
                elif 'action' in self.selected_item:
                    self.selected_item['action']()
                    
        return True
        
    def _show_submenu(self, item_index: int) -> None:
        """Show submenu for selected item."""
        if self.submenu:
            self.submenu.visible = False
            
        item = self.items[item_index]
        submenu_rect = pygame.Rect(
            self.rect.right,
            self.rect.y + item_index * (self.rect.height // len(self.items)),
            200,
            200
        )
        
        self.submenu = Menu(
            submenu_rect,
            item['submenu'],
            self.style,
            self
        )
        self.submenu.visible = True
