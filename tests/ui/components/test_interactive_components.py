"""
Tests for interactive UI components.
"""

import pytest
import pygame
from typing import Tuple, Optional
from visual_client.ui.components.text_input import TextInput, TextInputConfig
from visual_client.ui.components.dropdown import Dropdown, DropdownConfig
from visual_client.ui.components.slider import Slider, SliderConfig
from visual_client.ui.components.checkbox import Checkbox, CheckboxConfig
from visual_client.ui.components.scroll_panel import ScrollPanel, ScrollPanelConfig

@pytest.fixture
def screen():
    """Create a test screen."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    yield screen
    pygame.quit()

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

class TestTextInput:
    """Test the text input component with complex interactions."""
    
    def test_text_input_focus(self, screen, text_input_config):
        """Test text input focus behavior."""
        text_input = TextInput(screen, text_input_config)
        
        # Test initial state
        assert not text_input.focused
        
        # Test focus on click
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 120)}
        )
        assert text_input.handle_event(event)
        assert text_input.focused
        
        # Test unfocus on click outside
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (50, 50)}
        )
        assert not text_input.handle_event(event)
        assert not text_input.focused
        
    def test_text_input_typing(self, screen, text_input_config):
        """Test text input typing behavior."""
        text_input = TextInput(screen, text_input_config)
        
        # Focus the input
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 120)}
        )
        text_input.handle_event(event)
        
        # Test typing
        event = pygame.event.Event(
            pygame.KEYDOWN,
            {"unicode": "a", "key": pygame.K_a}
        )
        assert text_input.handle_event(event)
        assert text_input.get_text() == "a"
        
        # Test backspace
        event = pygame.event.Event(
            pygame.KEYDOWN,
            {"key": pygame.K_BACKSPACE}
        )
        assert text_input.handle_event(event)
        assert text_input.get_text() == ""
        
    def test_text_input_max_length(self, screen, text_input_config):
        """Test text input maximum length enforcement."""
        text_input = TextInput(screen, text_input_config)
        
        # Focus the input
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 120)}
        )
        text_input.handle_event(event)
        
        # Test typing beyond max length
        for _ in range(text_input_config.max_length + 1):
            event = pygame.event.Event(
                pygame.KEYDOWN,
                {"unicode": "a", "key": pygame.K_a}
            )
            text_input.handle_event(event)
            
        assert len(text_input.get_text()) == text_input_config.max_length
        
    def test_text_input_placeholder(self, screen, text_input_config):
        """Test text input placeholder behavior."""
        text_input = TextInput(screen, text_input_config)
        
        # Test initial placeholder
        assert text_input.get_text() == ""
        
        # Test placeholder disappears on focus
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 120)}
        )
        text_input.handle_event(event)
        assert text_input.get_text() == ""
        
        # Test placeholder reappears on unfocus with no text
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (50, 50)}
        )
        text_input.handle_event(event)
        assert text_input.get_text() == ""

class TestDropdown:
    """Test the dropdown component with complex interactions."""
    
    def test_dropdown_selection(self, screen, dropdown_config):
        """Test dropdown selection behavior."""
        dropdown = Dropdown(screen, dropdown_config)
        
        # Test initial state
        assert dropdown.get_selected() is None
        
        # Test expanding dropdown
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 120)}
        )
        assert dropdown.handle_event(event)
        assert dropdown.expanded
        
        # Test selecting an option
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 170)}
        )
        assert dropdown.handle_event(event)
        assert not dropdown.expanded
        assert dropdown.get_selected() == "Option 1"
        
    def test_dropdown_hover(self, screen, dropdown_config):
        """Test dropdown hover behavior."""
        dropdown = Dropdown(screen, dropdown_config)
        
        # Expand dropdown
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 120)}
        )
        dropdown.handle_event(event)
        
        # Test hovering over options
        event = pygame.event.Event(
            pygame.MOUSEMOTION,
            {"pos": (150, 170)}
        )
        assert dropdown.handle_event(event)
        assert dropdown.hovered_index == 0
        
        event = pygame.event.Event(
            pygame.MOUSEMOTION,
            {"pos": (150, 200)}
        )
        assert dropdown.handle_event(event)
        assert dropdown.hovered_index == 1
        
    def test_dropdown_add_remove(self, screen, dropdown_config):
        """Test adding and removing dropdown options."""
        dropdown = Dropdown(screen, dropdown_config)
        
        # Test adding option
        dropdown.add_option("Option 4")
        assert "Option 4" in dropdown.config.options
        
        # Test removing option
        dropdown.remove_option("Option 2")
        assert "Option 2" not in dropdown.config.options
        
        # Test removing selected option
        dropdown.set_selected("Option 1")
        dropdown.remove_option("Option 1")
        assert dropdown.get_selected() is None

class TestSlider:
    """Test the slider component with complex interactions."""
    
    def test_slider_dragging(self, screen, slider_config):
        """Test slider dragging behavior."""
        slider = Slider(screen, slider_config)
        
        # Test initial value
        assert slider.get_value() == slider_config.initial_value
        
        # Test start dragging
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 110)}
        )
        assert slider.handle_event(event)
        assert slider.dragging
        
        # Test dragging
        event = pygame.event.Event(
            pygame.MOUSEMOTION,
            {"pos": (200, 110)}
        )
        assert slider.handle_event(event)
        assert slider.get_value() > slider_config.initial_value
        
        # Test stop dragging
        event = pygame.event.Event(
            pygame.MOUSEBUTTONUP,
            {"pos": (200, 110)}
        )
        assert slider.handle_event(event)
        assert not slider.dragging
        
    def test_slider_range(self, screen, slider_config):
        """Test slider value range enforcement."""
        slider = Slider(screen, slider_config)
        
        # Test setting value below minimum
        slider.set_value(slider_config.min_value - 10)
        assert slider.get_value() == slider_config.min_value
        
        # Test setting value above maximum
        slider.set_value(slider_config.max_value + 10)
        assert slider.get_value() == slider_config.max_value
        
    def test_slider_step(self, screen, slider_config):
        """Test slider step enforcement."""
        slider = Slider(screen, slider_config)
        
        # Test setting value with step
        slider.set_value(55.5)
        assert slider.get_value() == 56  # Rounded to nearest step
        
        # Test dragging with step
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (150, 110)}
        )
        slider.handle_event(event)
        
        event = pygame.event.Event(
            pygame.MOUSEMOTION,
            {"pos": (155, 110)}
        )
        slider.handle_event(event)
        assert slider.get_value() % slider_config.step == 0

class TestCheckbox:
    """Test the checkbox component with complex interactions."""
    
    def test_checkbox_toggle(self, screen, checkbox_config):
        """Test checkbox toggle behavior."""
        checkbox = Checkbox(screen, checkbox_config)
        
        # Test initial state
        assert not checkbox.is_checked()
        
        # Test clicking to check
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (110, 110)}
        )
        assert checkbox.handle_event(event)
        assert checkbox.is_checked()
        
        # Test clicking to uncheck
        assert checkbox.handle_event(event)
        assert not checkbox.is_checked()
        
    def test_checkbox_hover(self, screen, checkbox_config):
        """Test checkbox hover behavior."""
        checkbox = Checkbox(screen, checkbox_config)
        
        # Test hovering
        event = pygame.event.Event(
            pygame.MOUSEMOTION,
            {"pos": (110, 110)}
        )
        assert checkbox.handle_event(event)
        assert checkbox.hovered
        
        # Test unhovering
        event = pygame.event.Event(
            pygame.MOUSEMOTION,
            {"pos": (50, 50)}
        )
        assert not checkbox.handle_event(event)
        assert not checkbox.hovered
        
    def test_checkbox_programmatic(self, screen, checkbox_config):
        """Test programmatic checkbox state changes."""
        checkbox = Checkbox(screen, checkbox_config)
        
        # Test set_checked
        checkbox.set_checked(True)
        assert checkbox.is_checked()
        
        checkbox.set_checked(False)
        assert not checkbox.is_checked()
        
        # Test toggle
        checkbox.toggle()
        assert checkbox.is_checked()
        
        checkbox.toggle()
        assert not checkbox.is_checked()

class TestScrollPanel:
    """Test the scroll panel component with complex interactions."""
    
    def test_scroll_panel_scrolling(self, screen, scroll_panel_config):
        """Test scroll panel scrolling behavior."""
        scroll_panel = ScrollPanel(screen, scroll_panel_config)
        
        # Test initial scroll position
        assert scroll_panel.scroll_y == 0
        
        # Test mouse wheel scrolling
        event = pygame.event.Event(
            pygame.MOUSEWHEEL,
            {"y": 1}
        )
        assert scroll_panel.handle_event(event)
        assert scroll_panel.scroll_y > 0
        
        # Test scrollbar dragging
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (290, 150)}
        )
        assert scroll_panel.handle_event(event)
        assert scroll_panel.scroll_dragging
        
        event = pygame.event.Event(
            pygame.MOUSEMOTION,
            {"pos": (290, 200)}
        )
        assert scroll_panel.handle_event(event)
        assert scroll_panel.scroll_y > 0
        
        event = pygame.event.Event(
            pygame.MOUSEBUTTONUP,
            {"pos": (290, 200)}
        )
        assert scroll_panel.handle_event(event)
        assert not scroll_panel.scroll_dragging
        
    def test_scroll_panel_bounds(self, screen, scroll_panel_config):
        """Test scroll panel scroll bounds."""
        scroll_panel = ScrollPanel(screen, scroll_panel_config)
        
        # Test scrolling beyond content
        scroll_panel.scroll_y = 1000
        scroll_panel._update_content_size()
        assert scroll_panel.scroll_y <= scroll_panel.content_rect.height - scroll_panel.rect.height
        
        # Test scrolling below zero
        scroll_panel.scroll_y = -100
        scroll_panel._update_content_size()
        assert scroll_panel.scroll_y >= 0
        
    def test_scroll_panel_components(self, screen, scroll_panel_config):
        """Test scroll panel component management."""
        scroll_panel = ScrollPanel(screen, scroll_panel_config)
        
        # Test adding component
        label = Label(screen, LabelConfig(
            position=(0, 0),
            text="Test"
        ))
        scroll_panel.add_component(label)
        assert label in scroll_panel.components
        
        # Test removing component
        scroll_panel.remove_component(label)
        assert label not in scroll_panel.components
        
        # Test clearing components
        scroll_panel.add_component(label)
        scroll_panel.clear_components()
        assert len(scroll_panel.components) == 0 