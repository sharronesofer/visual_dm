"""
Base screen class.
Provides common functionality for all screens.
"""

from typing import List, Dict, Any, Optional, Callable
import pygame
from abc import ABC, abstractmethod
from app.core.components.base import BaseComponent

class BaseScreen(ABC):
    """Base class for all screens."""
    
    def __init__(self, width: int, height: int, **kwargs):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.components: List[BaseComponent] = []
        self._fallback_components: List[BaseComponent] = []
        self._background_color = kwargs.get('background_color', (0, 0, 0))
        self._on_back = kwargs.get('on_back', None)
        self._on_race_selection = kwargs.get('on_race_selection', None)
        self._data = kwargs.get('data', {})
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the screen and its components."""
        if not self._initialized:
            self._initialize_components()
            self._create_fallback_components()
            self._initialized = True

    def _initialize_components(self) -> None:
        """Initialize the screen's components."""
        pass

    def _create_fallback_components(self) -> None:
        """Create fallback components for the screen."""
        pass

    def add_component(self, component: BaseComponent) -> None:
        """Add a component to the screen."""
        self.components.append(component)

    def remove_component(self, component: BaseComponent) -> None:
        """Remove a component from the screen."""
        if component in self.components:
            self.components.remove(component)

    def get_component(self, component_id: str) -> Optional[BaseComponent]:
        """Get a component by its ID."""
        for component in self.components:
            if component.get_data().get('id') == component_id:
                return component
        return None

    def set_background_color(self, color: tuple) -> None:
        """Set the background color."""
        self._background_color = color

    def set_on_back(self, callback: Optional[Callable]) -> None:
        """Set the back button handler."""
        self._on_back = callback

    def set_on_race_selection(self, callback: Optional[Callable]) -> None:
        """Set the race selection handler."""
        self._on_race_selection = callback

    def set_data(self, data: Dict[str, Any]) -> None:
        """Set additional data for the screen."""
        self._data = data

    def get_data(self) -> Dict[str, Any]:
        """Get the screen's data."""
        return self._data

    def _handle_back(self) -> None:
        """Handle the back button press."""
        if self._on_back:
            self._on_back()

    def _handle_race_selection(self, race: str) -> None:
        """Handle race selection."""
        if self._on_race_selection:
            self._on_race_selection(race)

    def draw(self) -> pygame.Surface:
        """Draw the screen and its components."""
        self.surface.fill(self._background_color)
        
        # Draw main components
        for component in self.components:
            if component.is_visible():
                component.draw(self.surface)
        
        # Draw fallback components
        for component in self._fallback_components:
            if component.is_visible():
                component.draw(self.surface)
        
        return self.surface

    def update(self) -> None:
        """Update the screen and its components."""
        for component in self.components:
            if component.is_enabled():
                component.update()
        
        for component in self._fallback_components:
            if component.is_enabled():
                component.update()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle a pygame event."""
        # Handle back button
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._handle_back()
            return True
        
        # Handle mouse events
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mouse_pos = pygame.mouse.get_pos()
            
            # Check components in reverse order (top to bottom)
            for component in reversed(self.components):
                if component.is_enabled() and component.contains_point(mouse_pos):
                    if component.handle_event(event):
                        return True
            
            # Check fallback components
            for component in reversed(self._fallback_components):
                if component.is_enabled() and component.contains_point(mouse_pos):
                    if component.handle_event(event):
                        return True
        
        return False 