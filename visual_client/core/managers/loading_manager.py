"""
Loading state management and progress indicators.
"""

import pygame
import time
from typing import Dict, Optional, Any, Callable
from .error_handler import handle_component_error, ErrorSeverity

class LoadingManager:
    """Manages loading states and progress indicators."""
    
    def __init__(self):
        """Initialize the loading manager."""
        self.loading_states: Dict[str, Dict[str, Any]] = {}
        self.progress_bars: Dict[str, Dict[str, Any]] = {}
        self.spinners: Dict[str, Dict[str, Any]] = {}
        self.callbacks: Dict[str, Callable] = {}
        
    def start_loading(
        self,
        id: str,
        total: int,
        description: str = "",
        show_progress: bool = True,
        show_spinner: bool = True
    ) -> None:
        """Start a loading operation.
        
        Args:
            id: Unique identifier for the loading operation
            total: Total number of items to load
            description: Description of the loading operation
            show_progress: Whether to show a progress bar
            show_spinner: Whether to show a loading spinner
        """
        try:
            self.loading_states[id] = {
                "start_time": time.time(),
                "current": 0,
                "total": total,
                "description": description,
                "show_progress": show_progress,
                "show_spinner": show_spinner
            }
            
            if show_progress:
                self._create_progress_bar(id)
                
            if show_spinner:
                self._create_spinner(id)
                
        except Exception as e:
            handle_component_error(
                "LoadingManager",
                "start_loading",
                e,
                ErrorSeverity.ERROR,
                {"id": id}
            )
            
    def update_progress(self, id: str, progress: int) -> None:
        """Update the progress of a loading operation.
        
        Args:
            id: Loading operation identifier
            progress: Current progress value
        """
        try:
            if id in self.loading_states:
                self.loading_states[id]["current"] = progress
                
                # Update progress bar if exists
                if id in self.progress_bars:
                    self._update_progress_bar(id)
                    
                # Check if loading is complete
                if progress >= self.loading_states[id]["total"]:
                    self._complete_loading(id)
                    
        except Exception as e:
            handle_component_error(
                "LoadingManager",
                "update_progress",
                e,
                ErrorSeverity.ERROR,
                {"id": id, "progress": progress}
            )
            
    def _create_progress_bar(self, id: str) -> None:
        """Create a progress bar for a loading operation.
        
        Args:
            id: Loading operation identifier
        """
        try:
            self.progress_bars[id] = {
                "rect": pygame.Rect(0, 0, 200, 20),
                "color": (0, 255, 0),
                "background": (50, 50, 50),
                "border": (100, 100, 100)
            }
        except Exception as e:
            handle_component_error(
                "LoadingManager",
                "_create_progress_bar",
                e,
                ErrorSeverity.ERROR,
                {"id": id}
            )
            
    def _update_progress_bar(self, id: str) -> None:
        """Update a progress bar's appearance.
        
        Args:
            id: Loading operation identifier
        """
        try:
            if id in self.progress_bars and id in self.loading_states:
                state = self.loading_states[id]
                progress = state["current"] / state["total"]
                
                # Update progress bar color based on progress
                if progress < 0.3:
                    self.progress_bars[id]["color"] = (255, 0, 0)
                elif progress < 0.7:
                    self.progress_bars[id]["color"] = (255, 255, 0)
                else:
                    self.progress_bars[id]["color"] = (0, 255, 0)
                    
        except Exception as e:
            handle_component_error(
                "LoadingManager",
                "_update_progress_bar",
                e,
                ErrorSeverity.ERROR,
                {"id": id}
            )
            
    def _create_spinner(self, id: str) -> None:
        """Create a loading spinner.
        
        Args:
            id: Loading operation identifier
        """
        try:
            self.spinners[id] = {
                "angle": 0,
                "speed": 5,
                "radius": 10,
                "color": (255, 255, 255),
                "segments": 8
            }
        except Exception as e:
            handle_component_error(
                "LoadingManager",
                "_create_spinner",
                e,
                ErrorSeverity.ERROR,
                {"id": id}
            )
            
    def _update_spinner(self, id: str) -> None:
        """Update a spinner's animation.
        
        Args:
            id: Loading operation identifier
        """
        try:
            if id in self.spinners:
                self.spinners[id]["angle"] = (
                    self.spinners[id]["angle"] + self.spinners[id]["speed"]
                ) % 360
        except Exception as e:
            handle_component_error(
                "LoadingManager",
                "_update_spinner",
                e,
                ErrorSeverity.ERROR,
                {"id": id}
            )
            
    def _complete_loading(self, id: str) -> None:
        """Complete a loading operation.
        
        Args:
            id: Loading operation identifier
        """
        try:
            if id in self.loading_states:
                # Calculate duration
                duration = time.time() - self.loading_states[id]["start_time"]
                
                # Clean up
                if id in self.progress_bars:
                    del self.progress_bars[id]
                if id in self.spinners:
                    del self.spinners[id]
                    
                # Call completion callback if exists
                if id in self.callbacks:
                    self.callbacks[id](duration)
                    del self.callbacks[id]
                    
                del self.loading_states[id]
                
        except Exception as e:
            handle_component_error(
                "LoadingManager",
                "_complete_loading",
                e,
                ErrorSeverity.ERROR,
                {"id": id}
            )
            
    def draw_loading(self, surface: pygame.Surface, id: str, position: tuple) -> None:
        """Draw loading indicators for an operation.
        
        Args:
            surface: Surface to draw on
            id: Loading operation identifier
            position: Position to draw at
        """
        try:
            if id in self.loading_states:
                state = self.loading_states[id]
                x, y = position
                
                # Draw description if exists
                if state["description"]:
                    font = pygame.font.Font(None, 24)
                    text = font.render(state["description"], True, (255, 255, 255))
                    surface.blit(text, (x, y))
                    y += 30
                    
                # Draw progress bar if enabled
                if state["show_progress"] and id in self.progress_bars:
                    bar = self.progress_bars[id]
                    progress = state["current"] / state["total"]
                    
                    # Draw background
                    pygame.draw.rect(
                        surface,
                        bar["background"],
                        (x, y, bar["rect"].width, bar["rect"].height)
                    )
                    
                    # Draw border
                    pygame.draw.rect(
                        surface,
                        bar["border"],
                        (x, y, bar["rect"].width, bar["rect"].height),
                        2
                    )
                    
                    # Draw progress
                    progress_width = int(bar["rect"].width * progress)
                    pygame.draw.rect(
                        surface,
                        bar["color"],
                        (x, y, progress_width, bar["rect"].height)
                    )
                    
                    y += bar["rect"].height + 10
                    
                # Draw spinner if enabled
                if state["show_spinner"] and id in self.spinners:
                    spinner = self.spinners[id]
                    center = (x + spinner["radius"], y + spinner["radius"])
                    
                    # Draw segments
                    for i in range(spinner["segments"]):
                        angle = spinner["angle"] + (i * 360 / spinner["segments"])
                        start_pos = (
                            center[0] + spinner["radius"] * pygame.math.Vector2(1, 0).rotate(angle),
                            center[1] + spinner["radius"] * pygame.math.Vector2(1, 0).rotate(angle)
                        )
                        end_pos = (
                            center[0] + spinner["radius"] * pygame.math.Vector2(1, 0).rotate(angle + 30),
                            center[1] + spinner["radius"] * pygame.math.Vector2(1, 0).rotate(angle + 30)
                        )
                        pygame.draw.line(
                            surface,
                            spinner["color"],
                            start_pos,
                            end_pos,
                            2
                        )
                        
        except Exception as e:
            handle_component_error(
                "LoadingManager",
                "draw_loading",
                e,
                ErrorSeverity.ERROR,
                {"id": id}
            )
            
    def set_completion_callback(self, id: str, callback: Callable) -> None:
        """Set a callback to be called when loading completes.
        
        Args:
            id: Loading operation identifier
            callback: Function to call on completion
        """
        try:
            self.callbacks[id] = callback
        except Exception as e:
            handle_component_error(
                "LoadingManager",
                "set_completion_callback",
                e,
                ErrorSeverity.ERROR,
                {"id": id}
            ) 