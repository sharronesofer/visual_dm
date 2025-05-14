"""
Tests for base UI components.
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

@pytest.fixture
def panel_config():
    """Create a test panel configuration."""
    return PanelConfig(
        position=(100, 100),
        width=200,
        height=200,
        background_color=(30, 30, 30),
        border_color=(100, 100, 100),
        border_width=2,
        padding=10,
        title="Test Panel",
        title_font_size=24,
        title_color=(255, 255, 255)
    )

@pytest.fixture
def label_config():
    """Create a test label configuration."""
    return LabelConfig(
        position=(100, 100),
        text="Test Label",
        font_size=24,
        text_color=(255, 255, 255),
        background_color=(30, 30, 30),
        border_color=(100, 100, 100),
        border_width=2,
        padding=10,
        alignment="left"
    )

@pytest.fixture
def button_config():
    """Create a test button configuration."""
    return ButtonConfig(
        position=(100, 100),
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
    )

@pytest.fixture
def text_input_config():
    """Create a test text input configuration."""
    return TextInputConfig(
        position=(100, 100),
        width=200,
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
    )

@pytest.fixture
def dropdown_config():
    """Create a test dropdown configuration."""
    return DropdownConfig(
        position=(100, 100),
        width=200,
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
    )

@pytest.fixture
def slider_config():
    """Create a test slider configuration."""
    return SliderConfig(
        position=(100, 100),
        width=200,
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
    )

@pytest.fixture
def checkbox_config():
    """Create a test checkbox configuration."""
    return CheckboxConfig(
        position=(100, 100),
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
    )

@pytest.fixture
def scroll_panel_config():
    """Create a test scroll panel configuration."""
    return ScrollPanelConfig(
        position=(100, 100),
        width=200,
        height=200,
        background_color=(30, 30, 30),
        border_color=(100, 100, 100),
        border_width=2,
        padding=10,
        scrollbar_width=10,
        scrollbar_color=(50, 50, 50),
        scrollbar_handle_color=(100, 100, 100)
    )

@pytest.fixture
def grid_layout_config():
    """Create a test grid layout configuration."""
    return GridLayoutConfig(
        position=(100, 100),
        width=200,
        height=200,
        rows=2,
        cols=2,
        background_color=(30, 30, 30),
        border_color=(100, 100, 100),
        border_width=2,
        padding=10,
        cell_padding=5
    )

class TestBaseScreen:
    """Test the base screen component."""
    
    def test_initialization(self, screen_config):
        """Test screen initialization."""
        screen = BaseScreen(screen_config)
        assert screen.config == screen_config
        assert screen.running == False
        assert screen.dirty == True
        
    def test_add_component(self, screen_config):
        """Test adding a component."""
        screen = BaseScreen(screen_config)
        panel = Panel(screen.screen, PanelConfig(
            position=(0, 0),
            width=100,
            height=100
        ))
        screen.add_component(panel)
        assert panel in screen.components
        assert screen.dirty == True
        
    def test_remove_component(self, screen_config):
        """Test removing a component."""
        screen = BaseScreen(screen_config)
        panel = Panel(screen.screen, PanelConfig(
            position=(0, 0),
            width=100,
            height=100
        ))
        screen.add_component(panel)
        screen.remove_component(panel)
        assert panel not in screen.components
        assert screen.dirty == True
        
    def test_clear_components(self, screen_config):
        """Test clearing all components."""
        screen = BaseScreen(screen_config)
        panel1 = Panel(screen.screen, PanelConfig(
            position=(0, 0),
            width=100,
            height=100
        ))
        panel2 = Panel(screen.screen, PanelConfig(
            position=(100, 100),
            width=100,
            height=100
        ))
        screen.add_component(panel1)
        screen.add_component(panel2)
        screen.clear_components()
        assert len(screen.components) == 0
        assert screen.dirty == True

class TestPanel:
    """Test the panel component."""
    
    def test_initialization(self, screen, panel_config):
        """Test panel initialization."""
        panel = Panel(screen, panel_config)
        assert panel.config == panel_config
        assert panel.rect == pygame.Rect(
            panel_config.position[0],
            panel_config.position[1],
            panel_config.width,
            panel_config.height
        )
        assert panel.dirty == True
        
    def test_draw(self, screen, panel_config):
        """Test drawing the panel."""
        panel = Panel(screen, panel_config)
        panel.draw()
        assert panel.dirty == False
        
    def test_add_component(self, screen, panel_config):
        """Test adding a component."""
        panel = Panel(screen, panel_config)
        label = Label(screen, LabelConfig(
            position=(0, 0),
            text="Test"
        ))
        panel.add_component(label)
        assert label in panel.components
        assert panel.dirty == True
        
    def test_handle_event(self, screen, panel_config):
        """Test handling events."""
        panel = Panel(screen, panel_config)
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 150)}
        )
        assert panel.handle_event(event) == False

class TestLabel:
    """Test the label component."""
    
    def test_initialization(self, screen, label_config):
        """Test label initialization."""
        label = Label(screen, label_config)
        assert label.config == label_config
        assert label.dirty == True
        
    def test_draw(self, screen, label_config):
        """Test drawing the label."""
        label = Label(screen, label_config)
        label.draw()
        assert label.dirty == False
        
    def test_set_text(self, screen, label_config):
        """Test setting the label text."""
        label = Label(screen, label_config)
        label.set_text("New Text")
        assert label.config.text == "New Text"
        assert label.dirty == True
        
    def test_set_color(self, screen, label_config):
        """Test setting the label color."""
        label = Label(screen, label_config)
        label.set_color((255, 0, 0))
        assert label.config.text_color == (255, 0, 0)
        assert label.dirty == True

class TestButton:
    """Test the button component."""
    
    def test_initialization(self, screen, button_config):
        """Test button initialization."""
        button = Button(screen, button_config)
        assert button.config == button_config
        assert button.rect == pygame.Rect(
            button_config.position[0],
            button_config.position[1],
            button_config.width,
            button_config.height
        )
        assert button.dirty == True
        
    def test_draw(self, screen, button_config):
        """Test drawing the button."""
        button = Button(screen, button_config)
        button.draw()
        assert button.dirty == False
        
    def test_handle_event(self, screen, button_config):
        """Test handling events."""
        button = Button(screen, button_config)
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 120)}
        )
        assert button.handle_event(event) == False

class TestTextInput:
    """Test the text input component."""
    
    def test_initialization(self, screen, text_input_config):
        """Test text input initialization."""
        text_input = TextInput(screen, text_input_config)
        assert text_input.config == text_input_config
        assert text_input.rect == pygame.Rect(
            text_input_config.position[0],
            text_input_config.position[1],
            text_input_config.width,
            text_input_config.height
        )
        assert text_input.dirty == True
        
    def test_draw(self, screen, text_input_config):
        """Test drawing the text input."""
        text_input = TextInput(screen, text_input_config)
        text_input.draw()
        assert text_input.dirty == False
        
    def test_handle_event(self, screen, text_input_config):
        """Test handling events."""
        text_input = TextInput(screen, text_input_config)
        event = pygame.event.Event(
            pygame.KEYDOWN,
            {"unicode": "a", "key": pygame.K_a}
        )
        assert text_input.handle_event(event) == False

class TestDropdown:
    """Test the dropdown component."""
    
    def test_initialization(self, screen, dropdown_config):
        """Test dropdown initialization."""
        dropdown = Dropdown(screen, dropdown_config)
        assert dropdown.config == dropdown_config
        assert dropdown.rect == pygame.Rect(
            dropdown_config.position[0],
            dropdown_config.position[1],
            dropdown_config.width,
            dropdown_config.height
        )
        assert dropdown.dirty == True
        
    def test_draw(self, screen, dropdown_config):
        """Test drawing the dropdown."""
        dropdown = Dropdown(screen, dropdown_config)
        dropdown.draw()
        assert dropdown.dirty == False
        
    def test_handle_event(self, screen, dropdown_config):
        """Test handling events."""
        dropdown = Dropdown(screen, dropdown_config)
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 120)}
        )
        assert dropdown.handle_event(event) == True

class TestSlider:
    """Test the slider component."""
    
    def test_initialization(self, screen, slider_config):
        """Test slider initialization."""
        slider = Slider(screen, slider_config)
        assert slider.config == slider_config
        assert slider.rect == pygame.Rect(
            slider_config.position[0],
            slider_config.position[1],
            slider_config.width,
            slider_config.height
        )
        assert slider.dirty == True
        
    def test_draw(self, screen, slider_config):
        """Test drawing the slider."""
        slider = Slider(screen, slider_config)
        slider.draw()
        assert slider.dirty == False
        
    def test_handle_event(self, screen, slider_config):
        """Test handling events."""
        slider = Slider(screen, slider_config)
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 110)}
        )
        assert slider.handle_event(event) == False

class TestCheckbox:
    """Test the checkbox component."""
    
    def test_initialization(self, screen, checkbox_config):
        """Test checkbox initialization."""
        checkbox = Checkbox(screen, checkbox_config)
        assert checkbox.config == checkbox_config
        assert checkbox.rect == pygame.Rect(
            checkbox_config.position[0],
            checkbox_config.position[1],
            checkbox_config.size,
            checkbox_config.size
        )
        assert checkbox.dirty == True
        
    def test_draw(self, screen, checkbox_config):
        """Test drawing the checkbox."""
        checkbox = Checkbox(screen, checkbox_config)
        checkbox.draw()
        assert checkbox.dirty == False
        
    def test_handle_event(self, screen, checkbox_config):
        """Test handling events."""
        checkbox = Checkbox(screen, checkbox_config)
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (110, 110)}
        )
        assert checkbox.handle_event(event) == True

class TestScrollPanel:
    """Test the scroll panel component."""
    
    def test_initialization(self, screen, scroll_panel_config):
        """Test scroll panel initialization."""
        scroll_panel = ScrollPanel(screen, scroll_panel_config)
        assert scroll_panel.config == scroll_panel_config
        assert scroll_panel.rect == pygame.Rect(
            scroll_panel_config.position[0],
            scroll_panel_config.position[1],
            scroll_panel_config.width,
            scroll_panel_config.height
        )
        assert scroll_panel.dirty == True
        
    def test_draw(self, screen, scroll_panel_config):
        """Test drawing the scroll panel."""
        scroll_panel = ScrollPanel(screen, scroll_panel_config)
        scroll_panel.draw()
        assert scroll_panel.dirty == False
        
    def test_handle_event(self, screen, scroll_panel_config):
        """Test handling events."""
        scroll_panel = ScrollPanel(screen, scroll_panel_config)
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (290, 150)}
        )
        assert scroll_panel.handle_event(event) == True

class TestGridLayout:
    """Test the grid layout component."""
    
    def test_initialization(self, screen, grid_layout_config):
        """Test grid layout initialization."""
        grid_layout = GridLayout(screen, grid_layout_config)
        assert grid_layout.config == grid_layout_config
        assert grid_layout.rect == pygame.Rect(
            grid_layout_config.position[0],
            grid_layout_config.position[1],
            grid_layout_config.width,
            grid_layout_config.height
        )
        assert grid_layout.dirty == True
        
    def test_draw(self, screen, grid_layout_config):
        """Test drawing the grid layout."""
        grid_layout = GridLayout(screen, grid_layout_config)
        grid_layout.draw()
        assert grid_layout.dirty == False
        
    def test_add_component(self, screen, grid_layout_config):
        """Test adding a component."""
        grid_layout = GridLayout(screen, grid_layout_config)
        label = Label(screen, LabelConfig(
            position=(0, 0),
            text="Test"
        ))
        grid_layout.add_component(label, 0, 0)
        assert grid_layout.components[0][0] == label
        assert grid_layout.dirty == True 