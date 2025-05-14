"""
Reusable grid layout component for UI screens.
"""

import pygame
from typing import Tuple, List, Optional
from dataclasses import dataclass
import logging

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class GridLayoutConfig:
    """Configuration for the grid layout."""
    position: Tuple[int, int]
    width: int
    height: int
    rows: int
    cols: int
    background_color: Tuple[int, int, int] = (30, 30, 30)
    border_color: Tuple[int, int, int] = (100, 100, 100)
    border_width: int = 2
    padding: int = 10
    cell_padding: int = 5

class GridLayout:
    """Reusable grid layout component."""
    
    def __init__(self, screen: pygame.Surface, config: GridLayoutConfig):
        """Initialize the grid layout.
        
        Args:
            screen: The pygame surface to draw on
            config: Grid layout configuration
        """
        self.screen = screen
        self.config = config
        
        # Create grid rect
        self.rect = pygame.Rect(
            config.position[0],
            config.position[1],
            config.width,
            config.height
        )
        
        # Calculate cell size
        self.cell_width = (
            config.width
            - 2 * config.padding
            - (config.cols - 1) * config.cell_padding
        ) // config.cols
        
        self.cell_height = (
            config.height
            - 2 * config.padding
            - (config.rows - 1) * config.cell_padding
        ) // config.rows
        
        # Grid state
        self.cells: List[List[Optional[object]]] = [
            [None for _ in range(config.cols)]
            for _ in range(config.rows)
        ]
        self.dirty = True
        
    def draw(self) -> None:
        """Draw the grid layout and its components."""
        if not self.dirty:
            return
            
        try:
            # Draw background
            pygame.draw.rect(self.screen, self.config.background_color, self.rect)
            pygame.draw.rect(
                self.screen,
                self.config.border_color,
                self.rect,
                self.config.border_width
            )
            
            # Draw cells and components
            for row in range(self.config.rows):
                for col in range(self.config.cols):
                    # Calculate cell position
                    cell_x = (
                        self.rect.left
                        + self.config.padding
                        + col * (self.cell_width + self.config.cell_padding)
                    )
                    cell_y = (
                        self.rect.top
                        + self.config.padding
                        + row * (self.cell_height + self.config.cell_padding)
                    )
                    
                    # Draw cell border
                    cell_rect = pygame.Rect(
                        cell_x,
                        cell_y,
                        self.cell_width,
                        self.cell_height
                    )
                    pygame.draw.rect(
                        self.screen,
                        self.config.border_color,
                        cell_rect,
                        self.config.border_width
                    )
                    
                    # Draw component if present
                    component = self.cells[row][col]
                    if component is not None and hasattr(component, 'draw'):
                        # Save component's original screen reference
                        original_screen = getattr(component, 'screen', None)
                        
                        # Temporarily set component's screen to cell surface
                        if hasattr(component, 'screen'):
                            component.screen = self.screen
                            
                        # Draw component
                        component.draw()
                        
                        # Restore component's original screen reference
                        if hasattr(component, 'screen'):
                            component.screen = original_screen
                            
            self.dirty = False
            
        except Exception as e:
            logger.error(f"Error drawing grid layout: {str(e)}")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events.
        
        Args:
            event: The event to handle
            
        Returns:
            bool: True if the event was handled
        """
        # Check if event is within grid bounds
        if not self.rect.collidepoint(event.pos):
            return False
            
        # Calculate cell position
        col = (
            (event.pos[0] - self.rect.left - self.config.padding)
            // (self.cell_width + self.config.cell_padding)
        )
        row = (
            (event.pos[1] - self.rect.top - self.config.padding)
            // (self.cell_height + self.config.cell_padding)
        )
        
        # Check if cell is valid
        if 0 <= row < self.config.rows and 0 <= col < self.config.cols:
            component = self.cells[row][col]
            if component is not None and hasattr(component, 'handle_event'):
                return component.handle_event(event)
                
        return False
        
    def add_component(self, component: object, row: int, col: int) -> None:
        """Add a component to the grid.
        
        Args:
            component: The component to add
            row: The row index
            col: The column index
        """
        if 0 <= row < self.config.rows and 0 <= col < self.config.cols:
            self.cells[row][col] = component
            self.dirty = True
        else:
            logger.warning(f"Invalid grid position: ({row}, {col})")
            
    def remove_component(self, row: int, col: int) -> None:
        """Remove a component from the grid.
        
        Args:
            row: The row index
            col: The column index
        """
        if 0 <= row < self.config.rows and 0 <= col < self.config.cols:
            self.cells[row][col] = None
            self.dirty = True
        else:
            logger.warning(f"Invalid grid position: ({row}, {col})")
            
    def clear_components(self) -> None:
        """Remove all components from the grid."""
        self.cells = [
            [None for _ in range(self.config.cols)]
            for _ in range(self.config.rows)
        ]
        self.dirty = True
        
    def get_component(self, row: int, col: int) -> Optional[object]:
        """Get the component at the specified position.
        
        Args:
            row: The row index
            col: The column index
            
        Returns:
            Optional[object]: The component or None if no component exists
        """
        if 0 <= row < self.config.rows and 0 <= col < self.config.cols:
            return self.cells[row][col]
        return None
        
    def get_cell_rect(self, row: int, col: int) -> Optional[pygame.Rect]:
        """Get the rectangle of a cell.
        
        Args:
            row: The row index
            col: The column index
            
        Returns:
            Optional[pygame.Rect]: The cell rectangle or None if position is invalid
        """
        if 0 <= row < self.config.rows and 0 <= col < self.config.cols:
            cell_x = (
                self.rect.left
                + self.config.padding
                + col * (self.cell_width + self.config.cell_padding)
            )
            cell_y = (
                self.rect.top
                + self.config.padding
                + row * (self.cell_height + self.config.cell_padding)
            )
            return pygame.Rect(
                cell_x,
                cell_y,
                self.cell_width,
                self.cell_height
            )
        return None 