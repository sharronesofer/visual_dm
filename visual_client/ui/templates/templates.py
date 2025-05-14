"""
UI template manager for common UI patterns and components.
"""

import pygame
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from visual_client.ui.components import (
    Button,
    Panel,
    ComponentStyle,
    BaseComponent,
    Label,
    Dropdown,
    Textbox,
    ProgressBar,
    ScrollPanel
)
from visual_client.core.utils.screen_utils import ScreenManager

@dataclass
class TemplateConfig:
    """Configuration for UI templates."""
    width: int
    height: int
    position: Tuple[int, int]
    parent: Optional[BaseComponent] = None
    style: Optional[ComponentStyle] = None

class UITemplateManager:
    """Manager for UI templates and common patterns."""
    
    def __init__(self, screen_manager: ScreenManager):
        """Initialize the template manager.
        
        Args:
            screen_manager: Screen manager instance
        """
        self.screen_manager = screen_manager
        self.screen_rect = screen_manager.get_screen_rect()
        
    def create_centered_panel(self, config: TemplateConfig) -> Panel:
        """Create a centered panel.
        
        Args:
            config: Panel configuration
            
        Returns:
            Panel: Created panel
        """
        x = (self.screen_rect.width - config.width) // 2
        y = (self.screen_rect.height - config.height) // 2
        
        return Panel(
            pygame.Rect(x, y, config.width, config.height),
            config.style or ComponentStyle(
                background_color=(40, 40, 40),
                border_color=(80, 80, 80),
                border_width=2,
                corner_radius=10
            ),
            config.parent
        )
        
    def create_title_label(self, text: str, config: TemplateConfig) -> Label:
        """Create a title label.
        
        Args:
            text: Label text
            config: Label configuration
            
        Returns:
            Label: Created label
        """
        return Label(
            pygame.Rect(
                config.position[0],
                config.position[1],
                config.width,
                config.height
            ),
            text,
            config.style or ComponentStyle(
                font_color=(255, 255, 255),
                font_size=36,
                font_weight="bold",
                alignment="center"
            ),
            config.parent
        )
        
    def create_button(self, text: str, config: TemplateConfig, callback: Callable) -> Button:
        """Create a button.
        
        Args:
            text: Button text
            config: Button configuration
            callback: Button click callback
            
        Returns:
            Button: Created button
        """
        button = Button(
            pygame.Rect(
                config.position[0],
                config.position[1],
                config.width,
                config.height
            ),
            text,
            config.style or ComponentStyle(
                background_color=(50, 50, 50),
                hover_color=(70, 70, 70),
                active_color=(90, 90, 90),
                font_color=(255, 255, 255),
                font_size=18,
                corner_radius=5,
                border_width=1,
                border_color=(100, 100, 100)
            ),
            config.parent
        )
        button.on_click = callback
        return button
        
    def create_dropdown(self, options: List[str], config: TemplateConfig, callback: Callable) -> Dropdown:
        """Create a dropdown.
        
        Args:
            options: Dropdown options
            config: Dropdown configuration
            callback: Selection callback
            
        Returns:
            Dropdown: Created dropdown
        """
        dropdown = Dropdown(
            pygame.Rect(
                config.position[0],
                config.position[1],
                config.width,
                config.height
            ),
            options,
            config.style or ComponentStyle(
                background_color=(40, 40, 40),
                hover_color=(60, 60, 60),
                font_color=(255, 255, 255),
                font_size=16,
                corner_radius=5,
                border_width=1,
                border_color=(100, 100, 100)
            ),
            config.parent
        )
        dropdown.on_select = callback
        return dropdown
        
    def create_textbox(self, config: TemplateConfig, callback: Callable) -> Textbox:
        """Create a textbox.
        
        Args:
            config: Textbox configuration
            callback: Text change callback
            
        Returns:
            Textbox: Created textbox
        """
        textbox = Textbox(
            pygame.Rect(
                config.position[0],
                config.position[1],
                config.width,
                config.height
            ),
            config.style or ComponentStyle(
                background_color=(40, 40, 40),
                hover_color=(60, 60, 60),
                font_color=(255, 255, 255),
                font_size=16,
                corner_radius=5,
                border_width=1,
                border_color=(100, 100, 100)
            ),
            config.parent
        )
        textbox.on_change = callback
        return textbox
        
    def create_progress_bar(self, config: TemplateConfig) -> ProgressBar:
        """Create a progress bar.
        
        Args:
            config: Progress bar configuration
            
        Returns:
            ProgressBar: Created progress bar
        """
        return ProgressBar(
            pygame.Rect(
                config.position[0],
                config.position[1],
                config.width,
                config.height
            ),
            config.style or ComponentStyle(
                background_color=(30, 30, 30),
                active_color=(0, 200, 255),
                border_color=(100, 100, 100),
                border_width=1
            ),
            config.parent
        )
        
    def create_scroll_panel(self, config: TemplateConfig) -> ScrollPanel:
        """Create a scroll panel.
        
        Args:
            config: Scroll panel configuration
            
        Returns:
            ScrollPanel: Created scroll panel
        """
        return ScrollPanel(
            pygame.Rect(
                config.position[0],
                config.position[1],
                config.width,
                config.height
            ),
            config.style or ComponentStyle(
                background_color=(30, 30, 30),
                border_color=(80, 80, 80),
                border_width=1,
                corner_radius=5,
                scrollbar_color=(60, 60, 60),
                scrollbar_hover_color=(80, 80, 80),
                scrollbar_width=10
            ),
            config.parent
        )
        
    def create_form_layout(self, components: List[BaseComponent], spacing: int = 10) -> None:
        """Create a vertical form layout.
        
        Args:
            components: List of components to layout
            spacing: Spacing between components
        """
        if not components:
            return
            
        # Get the first component's position as reference
        x, y = components[0].rect.x, components[0].rect.y
        
        # Position each component vertically
        for component in components:
            component.rect.x = x
            component.rect.y = y
            y += component.rect.height + spacing 