"""
Integration tests for UI components.
"""

import pytest
import pygame
from typing import Tuple, Optional
from visual_client.ui.components.base_screen import BaseScreen, ScreenConfig
from visual_client.ui.components.panel import Panel, PanelConfig
from visual_client.ui.components.label import Label, LabelConfig
from visual_client.ui.components.button import Button, ButtonConfig
from visual_client.ui.components.text_input import TextInput, TextInputConfig
from visual_client.ui.components.dropdown import Dropdown, DropdownConfig
from visual_client.ui.components.slider import Slider, SliderConfig
from visual_client.ui.components.checkbox import Checkbox, CheckboxConfig
from visual_client.ui.components.scroll_panel import ScrollPanel, ScrollPanelConfig
from visual_client.ui.components.grid_layout import GridLayout, GridLayoutConfig

@pytest.fixture
def screen():
    """Create a test screen."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    yield screen
    pygame.quit()

@pytest.fixture
def screen_config():
    """Create a test screen configuration."""
    return ScreenConfig(
        width=800,
        height=600,
        background_color=(0, 0, 0),
        title="Test Screen",
        fps=60
    )

class TestComponentIntegration:
    """Test integration between UI components."""
    
    def test_panel_with_components(self, screen, screen_config):
        """Test panel containing multiple components."""
        # Create screen
        screen = BaseScreen(screen_config)
        
        # Create panel
        panel = Panel(screen.screen, PanelConfig(
            position=(100, 100),
            width=400,
            height=400,
            background_color=(30, 30, 30),
            border_color=(100, 100, 100),
            border_width=2,
            padding=10,
            title="Test Panel"
        ))
        
        # Add components to panel
        label = Label(screen.screen, LabelConfig(
            position=(20, 20),
            text="Test Label",
            font_size=24,
            text_color=(255, 255, 255)
        ))
        panel.add_component(label)
        
        button = Button(screen.screen, ButtonConfig(
            position=(20, 60),
            width=150,
            height=40,
            text="Test Button",
            font_size=24,
            text_color=(255, 255, 255),
            background_color=(50, 50, 50),
            hover_color=(70, 70, 70),
            border_color=(100, 100, 100),
            border_width=2,
            padding=10
        ))
        panel.add_component(button)
        
        # Test component interaction
        assert label in panel.components
        assert button in panel.components
        
        # Test event handling
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (120, 160)}
        )
        assert panel.handle_event(event) == False
        
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (120, 200)}
        )
        assert panel.handle_event(event) == True
        
    def test_scroll_panel_with_components(self, screen, screen_config):
        """Test scroll panel containing multiple components."""
        # Create screen
        screen = BaseScreen(screen_config)
        
        # Create scroll panel
        scroll_panel = ScrollPanel(screen.screen, ScrollPanelConfig(
            position=(100, 100),
            width=400,
            height=200,
            background_color=(30, 30, 30),
            border_color=(100, 100, 100),
            border_width=2,
            padding=10,
            scrollbar_width=10,
            scrollbar_color=(50, 50, 50),
            scrollbar_handle_color=(100, 100, 100)
        ))
        
        # Add components to scroll panel
        for i in range(10):
            label = Label(screen.screen, LabelConfig(
                position=(20, 20 + i * 40),
                text=f"Label {i}",
                font_size=24,
                text_color=(255, 255, 255)
            ))
            scroll_panel.add_component(label)
            
        # Test component interaction
        assert len(scroll_panel.components) == 10
        
        # Test scrolling
        event = pygame.event.Event(
            pygame.MOUSEWHEEL,
            {"y": 1}
        )
        assert scroll_panel.handle_event(event)
        assert scroll_panel.scroll_y > 0
        
        # Test component visibility
        scroll_panel.scroll_y = 100
        scroll_panel.draw()
        
    def test_grid_layout_with_components(self, screen, screen_config):
        """Test grid layout containing multiple components."""
        # Create screen
        screen = BaseScreen(screen_config)
        
        # Create grid layout
        grid_layout = GridLayout(screen.screen, GridLayoutConfig(
            position=(100, 100),
            width=400,
            height=400,
            rows=2,
            cols=2,
            background_color=(30, 30, 30),
            border_color=(100, 100, 100),
            border_width=2,
            padding=10,
            cell_padding=5
        ))
        
        # Add components to grid
        for row in range(2):
            for col in range(2):
                label = Label(screen.screen, LabelConfig(
                    position=(0, 0),
                    text=f"Cell {row},{col}",
                    font_size=24,
                    text_color=(255, 255, 255)
                ))
                grid_layout.add_component(label, row, col)
                
        # Test component interaction
        assert grid_layout.components[0][0] is not None
        assert grid_layout.components[0][1] is not None
        assert grid_layout.components[1][0] is not None
        assert grid_layout.components[1][1] is not None
        
        # Test cell rects
        cell_rect = grid_layout.get_cell_rect(0, 0)
        assert cell_rect.width > 0
        assert cell_rect.height > 0
        
    def test_complex_form(self, screen, screen_config):
        """Test a complex form with multiple interactive components."""
        # Create screen
        screen = BaseScreen(screen_config)
        
        # Create panel
        panel = Panel(screen.screen, PanelConfig(
            position=(100, 100),
            width=400,
            height=400,
            background_color=(30, 30, 30),
            border_color=(100, 100, 100),
            border_width=2,
            padding=10,
            title="Test Form"
        ))
        
        # Add form components
        y = 20
        
        # Text input
        text_input = TextInput(screen.screen, TextInputConfig(
            position=(20, y),
            width=360,
            height=40,
            font_size=24,
            text_color=(255, 255, 255),
            background_color=(30, 30, 30),
            border_color=(100, 100, 100),
            border_width=2,
            padding=10,
            placeholder="Enter text...",
            placeholder_color=(150, 150, 150),
            max_length=50
        ))
        panel.add_component(text_input)
        y += 60
        
        # Dropdown
        dropdown = Dropdown(screen.screen, DropdownConfig(
            position=(20, y),
            width=360,
            height=40,
            options=["Option 1", "Option 2", "Option 3"],
            font_size=24,
            text_color=(255, 255, 255),
            background_color=(30, 30, 30),
            hover_color=(50, 50, 50),
            border_color=(100, 100, 100),
            border_width=2,
            padding=10,
            option_height=30
        ))
        panel.add_component(dropdown)
        y += 60
        
        # Slider
        slider = Slider(screen.screen, SliderConfig(
            position=(20, y),
            width=360,
            height=20,
            min_value=0,
            max_value=100,
            initial_value=50,
            step=1,
            font_size=24,
            text_color=(255, 255, 255),
            background_color=(30, 30, 30),
            fill_color=(100, 100, 100),
            handle_color=(200, 200, 200),
            border_color=(100, 100, 100),
            border_width=2,
            padding=10,
            show_value=True
        ))
        panel.add_component(slider)
        y += 40
        
        # Checkbox
        checkbox = Checkbox(screen.screen, CheckboxConfig(
            position=(20, y),
            size=20,
            text="Test Checkbox",
            font_size=24,
            text_color=(255, 255, 255),
            background_color=(30, 30, 30),
            border_color=(100, 100, 100),
            check_color=(200, 200, 200),
            border_width=2,
            padding=10,
            checked=False
        ))
        panel.add_component(checkbox)
        y += 40
        
        # Submit button
        button = Button(screen.screen, ButtonConfig(
            position=(20, y),
            width=360,
            height=40,
            text="Submit",
            font_size=24,
            text_color=(255, 255, 255),
            background_color=(50, 50, 50),
            hover_color=(70, 70, 70),
            border_color=(100, 100, 100),
            border_width=2,
            padding=10
        ))
        panel.add_component(button)
        
        # Test component interaction
        assert text_input in panel.components
        assert dropdown in panel.components
        assert slider in panel.components
        assert checkbox in panel.components
        assert button in panel.components
        
        # Test form interaction
        # Focus text input
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (120, 120)}
        )
        assert panel.handle_event(event)
        assert text_input.focused
        
        # Type in text input
        event = pygame.event.Event(
            pygame.KEYDOWN,
            {"unicode": "a", "key": pygame.K_a}
        )
        assert panel.handle_event(event)
        assert text_input.get_text() == "a"
        
        # Select dropdown option
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (120, 180)}
        )
        assert panel.handle_event(event)
        assert dropdown.expanded
        
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (120, 210)}
        )
        assert panel.handle_event(event)
        assert dropdown.get_selected() == "Option 1"
        
        # Adjust slider
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (120, 240)}
        )
        assert panel.handle_event(event)
        assert slider.dragging
        
        event = pygame.event.Event(
            pygame.MOUSEMOTION,
            {"pos": (200, 240)}
        )
        assert panel.handle_event(event)
        assert slider.get_value() > 50
        
        # Toggle checkbox
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (120, 280)}
        )
        assert panel.handle_event(event)
        assert checkbox.is_checked()
        
        # Click submit button
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (120, 320)}
        )
        assert panel.handle_event(event)
        assert button.hovered 