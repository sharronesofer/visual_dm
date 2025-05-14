"""
Security tests for UI components.
"""

import pytest
import pygame
from typing import Tuple, Optional
from visual_client.ui.components.text_input import TextInput, TextInputConfig
from visual_client.ui.components.dropdown import Dropdown, DropdownConfig

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

class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_text_input_max_length(self, screen, text_input_config):
        """Test text input maximum length enforcement."""
        text_input = TextInput(screen, text_input_config)
        
        # Test typing beyond max length
        for _ in range(text_input_config.max_length + 1):
            event = pygame.event.Event(
                pygame.KEYDOWN,
                {"unicode": "a", "key": pygame.K_a}
            )
            text_input.handle_event(event)
            
        assert len(text_input.get_text()) == text_input_config.max_length
        
    def test_text_input_special_characters(self, screen, text_input_config):
        """Test handling of special characters."""
        text_input = TextInput(screen, text_input_config)
        
        # Test control characters
        event = pygame.event.Event(
            pygame.KEYDOWN,
            {"unicode": "\x00", "key": pygame.K_a}
        )
        text_input.handle_event(event)
        assert "\x00" not in text_input.get_text()
        
        # Test escape sequences
        event = pygame.event.Event(
            pygame.KEYDOWN,
            {"unicode": "\n", "key": pygame.K_RETURN}
        )
        text_input.handle_event(event)
        assert "\n" not in text_input.get_text()
        
    def test_text_input_html_tags(self, screen, text_input_config):
        """Test sanitization of HTML tags."""
        text_input = TextInput(screen, text_input_config)
        
        # Test HTML tags
        html = "<script>alert('xss')</script>"
        for char in html:
            event = pygame.event.Event(
                pygame.KEYDOWN,
                {"unicode": char, "key": pygame.K_a}
            )
            text_input.handle_event(event)
            
        assert "<script>" not in text_input.get_text()
        assert "alert" not in text_input.get_text()
        
    def test_text_input_sql_injection(self, screen, text_input_config):
        """Test sanitization of SQL injection attempts."""
        text_input = TextInput(screen, text_input_config)
        
        # Test SQL injection
        sql = "'; DROP TABLE users; --"
        for char in sql:
            event = pygame.event.Event(
                pygame.KEYDOWN,
                {"unicode": char, "key": pygame.K_a}
            )
            text_input.handle_event(event)
            
        assert "DROP TABLE" not in text_input.get_text()
        assert "--" not in text_input.get_text()
        
    def test_text_input_unicode(self, screen, text_input_config):
        """Test handling of Unicode characters."""
        text_input = TextInput(screen, text_input_config)
        
        # Test Unicode characters
        unicode_chars = "你好世界"
        for char in unicode_chars:
            event = pygame.event.Event(
                pygame.KEYDOWN,
                {"unicode": char, "key": pygame.K_a}
            )
            text_input.handle_event(event)
            
        assert text_input.get_text() == unicode_chars
        
    def test_text_input_paste(self, screen, text_input_config):
        """Test handling of pasted text."""
        text_input = TextInput(screen, text_input_config)
        
        # Test pasting text
        clipboard_text = "Test text with <script>alert('xss')</script>"
        text_input.set_text(clipboard_text)
        
        assert "<script>" not in text_input.get_text()
        assert "alert" not in text_input.get_text()
        assert len(text_input.get_text()) <= text_input_config.max_length

class TestDropdownSecurity:
    """Test dropdown security features."""
    
    def test_dropdown_option_validation(self, screen, dropdown_config):
        """Test validation of dropdown options."""
        dropdown = Dropdown(screen, dropdown_config)
        
        # Test adding invalid option
        dropdown.add_option("<script>alert('xss')</script>")
        assert "<script>" not in dropdown.config.options[-1]
        
        # Test adding option with special characters
        dropdown.add_option("Option with \n newline")
        assert "\n" not in dropdown.config.options[-1]
        
    def test_dropdown_selection_validation(self, screen, dropdown_config):
        """Test validation of dropdown selection."""
        dropdown = Dropdown(screen, dropdown_config)
        
        # Test selecting invalid option
        dropdown.set_selected("<script>alert('xss')</script>")
        assert dropdown.get_selected() is None
        
        # Test selecting option with special characters
        dropdown.set_selected("Option with \n newline")
        assert dropdown.get_selected() is None
        
    def test_dropdown_option_removal(self, screen, dropdown_config):
        """Test secure removal of dropdown options."""
        dropdown = Dropdown(screen, dropdown_config)
        
        # Test removing non-existent option
        dropdown.remove_option("Non-existent option")
        assert len(dropdown.config.options) == len(dropdown_config.options)
        
        # Test removing option with special characters
        dropdown.remove_option("<script>alert('xss')</script>")
        assert len(dropdown.config.options) == len(dropdown_config.options) 