"""
Layout management system for responsive design.
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from .error_handler import handle_component_error, ErrorSeverity

class LayoutManager:
    """Manages responsive layout and positioning."""
    
    def __init__(self):
        """Initialize the layout manager."""
        try:
            # Initialize breakpoints
            self.breakpoints = {
                "xs": 320,  # Extra small devices
                "sm": 576,  # Small devices
                "md": 768,  # Medium devices
                "lg": 992,  # Large devices
                "xl": 1200  # Extra large devices
            }
            
            # Initialize grid configuration
            self.grid_config = {
                "columns": 12,
                "gutter": 16,
                "margin": 16
            }
            
            # Initialize current breakpoint
            self.current_breakpoint = "md"
            
            # Initialize screen dimensions
            self.screen_width = 800
            self.screen_height = 600
            
            # Initialize layout cache
            self.layout_cache = {}
            
        except Exception as e:
            handle_component_error(
                "LayoutManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def update_screen_size(self, width: int, height: int) -> None:
        """Update screen dimensions and recalculate breakpoint.
        
        Args:
            width: New screen width
            height: New screen height
        """
        try:
            self.screen_width = width
            self.screen_height = height
            
            # Update current breakpoint
            for breakpoint, min_width in sorted(
                self.breakpoints.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                if width >= min_width:
                    self.current_breakpoint = breakpoint
                    break
                    
            # Clear layout cache
            self.layout_cache.clear()
            
        except Exception as e:
            handle_component_error(
                "LayoutManager",
                "update_screen_size",
                e,
                ErrorSeverity.ERROR
            )
            
    def get_grid_position(
        self,
        row: int,
        col: int,
        colspan: int = 1,
        rowspan: int = 1
    ) -> Tuple[int, int, int, int]:
        """Get grid cell position and dimensions.
        
        Args:
            row: Grid row
            col: Grid column
            colspan: Number of columns to span
            rowspan: Number of rows to span
            
        Returns:
            Tuple of (x, y, width, height)
        """
        try:
            # Calculate cell dimensions
            cell_width = (self.screen_width - 2 * self.grid_config["margin"]) / self.grid_config["columns"]
            cell_height = cell_width  # Square cells
            
            # Calculate position
            x = self.grid_config["margin"] + col * (cell_width + self.grid_config["gutter"])
            y = self.grid_config["margin"] + row * (cell_height + self.grid_config["gutter"])
            
            # Calculate dimensions
            width = colspan * cell_width + (colspan - 1) * self.grid_config["gutter"]
            height = rowspan * cell_height + (rowspan - 1) * self.grid_config["gutter"]
            
            return (int(x), int(y), int(width), int(height))
            
        except Exception as e:
            handle_component_error(
                "LayoutManager",
                "get_grid_position",
                e,
                ErrorSeverity.ERROR
            )
            return (0, 0, 0, 0)
            
    def get_responsive_font_size(self, base_size: int) -> int:
        """Get responsive font size based on current breakpoint.
        
        Args:
            base_size: Base font size
            
        Returns:
            Responsive font size
        """
        try:
            # Scale factors for different breakpoints
            scale_factors = {
                "xs": 0.8,
                "sm": 0.9,
                "md": 1.0,
                "lg": 1.1,
                "xl": 1.2
            }
            
            return int(base_size * scale_factors[self.current_breakpoint])
            
        except Exception as e:
            handle_component_error(
                "LayoutManager",
                "get_responsive_font_size",
                e,
                ErrorSeverity.ERROR
            )
            return base_size
            
    def get_responsive_spacing(self, base_spacing: int) -> int:
        """Get responsive spacing based on current breakpoint.
        
        Args:
            base_spacing: Base spacing value
            
        Returns:
            Responsive spacing value
        """
        try:
            # Scale factors for different breakpoints
            scale_factors = {
                "xs": 0.8,
                "sm": 0.9,
                "md": 1.0,
                "lg": 1.1,
                "xl": 1.2
            }
            
            return int(base_spacing * scale_factors[self.current_breakpoint])
            
        except Exception as e:
            handle_component_error(
                "LayoutManager",
                "get_responsive_spacing",
                e,
                ErrorSeverity.ERROR
            )
            return base_spacing
            
    def get_breakpoint_config(self) -> Dict[str, Any]:
        """Get current breakpoint configuration.
        
        Returns:
            Dictionary with breakpoint configuration
        """
        try:
            return {
                "breakpoint": self.current_breakpoint,
                "width": self.screen_width,
                "height": self.screen_height,
                "grid": self.grid_config,
                "is_mobile": self.current_breakpoint in ["xs", "sm"],
                "is_tablet": self.current_breakpoint == "md",
                "is_desktop": self.current_breakpoint in ["lg", "xl"]
            }
            
        except Exception as e:
            handle_component_error(
                "LayoutManager",
                "get_breakpoint_config",
                e,
                ErrorSeverity.ERROR
            )
            return {}
            
    def clear_cache(self) -> None:
        """Clear layout cache."""
        try:
            self.layout_cache.clear()
            
        except Exception as e:
            handle_component_error(
                "LayoutManager",
                "clear_cache",
                e,
                ErrorSeverity.ERROR
            )
            
# Create global layout manager instance
layout_manager = LayoutManager() 