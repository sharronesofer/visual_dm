"""
Base screen component for UI screens.
"""

import pygame
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ScreenConfig:
    """Configuration for the screen."""
    width: int
    height: int
    background_color: Optional[Tuple[int, int, int]] = None
    title: Optional[str] = None
    fps: int = 60

class BaseScreen(ABC):
    """Base screen component."""
    
    def __init__(self, config: ScreenConfig):
        """Initialize the screen.
        
        Args:
            config: Screen configuration
        """
        self.config = config
        
        # Initialize pygame
        pygame.init()
        
        # Create screen
        self.screen = pygame.display.set_mode((config.width, config.height))
        
        # Set title if specified
        if config.title:
            pygame.display.set_caption(config.title)
            
        # Initialize clock
        self.clock = pygame.time.Clock()
        
        # Initialize components list
        self.components: List[Any] = []
        
        # Initialize state
        self.running = False
        self.dirty = True
        
    def _initialize_components(self) -> None:
        """Initialize screen components."""
        try:
            # Create main panel
            self.main_panel = pygame.Rect(0, 0, self.config.width, self.config.height)
            
            # Initialize any additional components
            self._setup_components()
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {str(e)}")
            raise
            
    @abstractmethod
    def _setup_components(self) -> None:
        """Setup screen-specific components."""
        pass
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        try:
            # Pass event to components
            for component in self.components:
                if hasattr(component, 'handle_event'):
                    if component.handle_event(event):
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error handling screen event: {str(e)}")
            return False
            
    def update(self) -> None:
        """Update screen state."""
        try:
            # Update components
            for component in self.components:
                if hasattr(component, 'update'):
                    component.update()
                    
        except Exception as e:
            logger.error(f"Error updating screen: {str(e)}")
            
    def draw(self) -> None:
        """Draw the screen and its components."""
        if not self.dirty:
            return
            
        try:
            # Draw background if specified
            if self.config.background_color:
                self.screen.fill(self.config.background_color)
                
            # Draw components
            for component in self.components:
                if hasattr(component, 'draw'):
                    component.draw()
                    
            # Update display
            pygame.display.flip()
            
            self.dirty = False
            
        except Exception as e:
            logger.error(f"Error drawing screen: {str(e)}")
            
    def run(self) -> None:
        """Run the screen."""
        try:
            # Initialize components
            self._initialize_components()
            
            # Set running state
            self.running = True
            
            # Main loop
            while self.running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    else:
                        self.handle_event(event)
                        
                # Update
                self.update()
                
                # Draw
                self.draw()
                
                # Cap FPS
                self.clock.tick(self.config.fps)
                
        except Exception as e:
            logger.error(f"Error running screen: {str(e)}")
            
        finally:
            # Clean up
            pygame.quit()
            
    def add_component(self, component: Any) -> None:
        """Add a component to the screen.
        
        Args:
            component: The component to add
        """
        self.components.append(component)
        self.dirty = True
        
    def remove_component(self, component: Any) -> None:
        """Remove a component from the screen.
        
        Args:
            component: The component to remove
        """
        if component in self.components:
            self.components.remove(component)
            self.dirty = True
            
    def clear_components(self) -> None:
        """Remove all components from the screen."""
        self.components.clear()
        self.dirty = True
        
    def quit(self) -> None:
        """Quit the screen."""
        self.running = False
        
    def mark_dirty(self, rect: Optional[pygame.Rect] = None) -> None:
        """Mark an area as dirty for redraw.
        
        Args:
            rect: The rectangle to mark as dirty, or None for the entire screen
        """
        if rect is None:
            rect = self.main_panel
        self.dirty_rects.append(rect)
        
    def draw_text(self, text: str, position: tuple, color: tuple = (255, 255, 255),
                 font: Optional[pygame.font.Font] = None) -> None:
        """Draw text on the screen.
        
        Args:
            text: The text to draw
            position: The (x, y) position to draw at
            color: The text color
            font: The font to use, or None for default
        """
        if font is None:
            font = self.font
        surface = font.render(text, True, color)
        self.screen.blit(surface, position)
        self.mark_dirty(surface.get_rect(topleft=position))
        
    def draw_button(self, rect: pygame.Rect, text: str, color: tuple = (100, 100, 100),
                   hover_color: tuple = (150, 150, 150), text_color: tuple = (255, 255, 255)) -> bool:
        """Draw a button and handle hover state.
        
        Args:
            rect: The button rectangle
            text: The button text
            color: The normal button color
            hover_color: The hover button color
            text_color: The text color
            
        Returns:
            bool: True if the button is being hovered
        """
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mouse_pos)
        
        # Draw button
        button_color = hover_color if is_hovered else color
        pygame.draw.rect(self.screen, button_color, rect)
        
        # Draw text
        text_surface = self.font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
        self.mark_dirty(rect)
        return is_hovered 