"""
Base screen component for UI screens.
"""

from typing import Optional, Dict, Any, List
import pygame
import pygame_gui
from .base import Component

class BaseScreen(Component):
    """Base class for all UI screens."""
    
    def __init__(self,
                 rect: pygame.Rect,
                 manager: pygame_gui.UIManager,
                 container: Optional[Any] = None,
                 parent: Optional[Component] = None,
                 object_id: Optional[str] = None,
                 anchors: Optional[Dict[str, str]] = None):
        """
        Initialize a base screen.
        
        Args:
            rect: The position and size of the screen
            manager: The pygame_gui UIManager instance
            container: Optional container this screen belongs to
            parent: Optional parent component
            object_id: Optional unique identifier for the screen
            anchors: Optional anchor points for layout
        """
        super().__init__(rect, manager, container, parent, object_id, anchors)
        self.components: List[Component] = []
        self.is_active = False
        
    def show(self) -> None:
        """Show the screen and all its components."""
        self.is_active = True
        for component in self.components:
            component.show()
            
    def hide(self) -> None:
        """Hide the screen and all its components."""
        self.is_active = False
        for component in self.components:
            component.hide()
            
    def add_component(self, component: Component) -> None:
        """
        Add a component to the screen.
        
        Args:
            component: The component to add
        """
        self.components.append(component)
        
    def remove_component(self, component: Component) -> None:
        """
        Remove a component from the screen.
        
        Args:
            component: The component to remove
        """
        if component in self.components:
            self.components.remove(component)
            
    def clear_components(self) -> None:
        """Remove all components from the screen."""
        self.components.clear()
        
    def update(self, time_delta: float) -> None:
        """
        Update the screen and its components.
        
        Args:
            time_delta: Time passed since last update
        """
        if not self.is_active:
            return
            
        for component in self.components:
            component.update(time_delta)
            
    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process an event.
        
        Args:
            event: The event to process
            
        Returns:
            True if the event was handled
        """
        if not self.is_active:
            return False
            
        for component in self.components:
            if component.process_event(event):
                return True
                
        return False
        
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the screen and its components.
        
        Args:
            surface: The surface to draw on
        """
        if not self.is_active:
            return
            
        for component in self.components:
            component.draw(surface)
            
    def get_component_by_id(self, object_id: str) -> Optional[Component]:
        """
        Get a component by its ID.
        
        Args:
            object_id: The ID to search for
            
        Returns:
            The component if found, None otherwise
        """
        for component in self.components:
            if component.object_id == object_id:
                return component
        return None
        
    def resize(self, rect: pygame.Rect) -> None:
        """
        Resize the screen and its components.
        
        Args:
            rect: The new position and size
        """
        super().resize(rect)
        for component in self.components:
            component.resize(rect) 