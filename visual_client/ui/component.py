"""
Base component class for UI elements.
"""

from typing import Optional, Dict, Any, Tuple, List
import pygame
import pygame_gui

class Component:
    """Base class for all UI components."""
    
    def __init__(self, 
                 rect: pygame.Rect,
                 manager: pygame_gui.UIManager,
                 container: Optional[pygame_gui.elements.UIContainer] = None,
                 parent: Optional['Component'] = None,
                 object_id: Optional[str] = None,
                 anchors: Optional[Dict[str, str]] = None):
        """
        Initialize a UI component.
        
        Args:
            rect: The position and size of the component
            manager: The pygame_gui UIManager instance
            container: Optional container this component belongs to
            parent: Optional parent component
            object_id: Optional unique identifier for the component
            anchors: Optional dictionary defining anchor points
        """
        self.rect = rect
        self.manager = manager
        self.container = container
        self.parent = parent
        self.object_id = object_id
        self.anchors = anchors or {}
        self.children: List[Component] = []
        self.visible = True
        self.enabled = True
        
        if parent:
            parent.add_child(self)
    
    def add_child(self, child: 'Component') -> None:
        """Add a child component."""
        if child not in self.children:
            self.children.append(child)
            child.parent = self
    
    def remove_child(self, child: 'Component') -> None:
        """Remove a child component."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def show(self) -> None:
        """Make the component visible."""
        self.visible = True
        for child in self.children:
            child.show()
    
    def hide(self) -> None:
        """Hide the component."""
        self.visible = False
        for child in self.children:
            child.hide()
    
    def enable(self) -> None:
        """Enable the component."""
        self.enabled = True
        for child in self.children:
            child.enable()
    
    def disable(self) -> None:
        """Disable the component."""
        self.enabled = False
        for child in self.children:
            child.disable()
    
    def update(self, time_delta: float) -> None:
        """
        Update the component's state.
        
        Args:
            time_delta: Time passed since last update in seconds
        """
        for child in self.children:
            child.update(time_delta)
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the component.
        
        Args:
            surface: Surface to draw on
        """
        if self.visible:
            for child in self.children:
                child.draw(surface)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle an event.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            True if the event was handled, False otherwise
        """
        if not self.enabled:
            return False
            
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        return False
    
    def get_relative_rect(self) -> pygame.Rect:
        """Get the component's rectangle relative to its container."""
        if self.container:
            container_rect = self.container.get_rect()
            return pygame.Rect(
                self.rect.x - container_rect.x,
                self.rect.y - container_rect.y,
                self.rect.width,
                self.rect.height
            )
        return self.rect
    
    def set_position(self, position: Tuple[int, int]) -> None:
        """
        Set the component's position.
        
        Args:
            position: New (x, y) position
        """
        self.rect.x, self.rect.y = position
        
    def set_dimensions(self, dimensions: Tuple[int, int]) -> None:
        """
        Set the component's dimensions.
        
        Args:
            dimensions: New (width, height)
        """
        self.rect.width, self.rect.height = dimensions 