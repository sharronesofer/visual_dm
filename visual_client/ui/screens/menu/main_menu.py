"""
Main menu screen module with accessibility and responsive design.
"""

import pygame
from typing import Optional, Dict, Any, Tuple, List
from core.screen import Screen
from core.ui.button import Button
from core.ui.text import Text
from core.ui.layout import Layout
from core.ui.style import ComponentStyle

class MainMenuScreen(Screen):
    """Main menu screen with accessibility and responsive features."""
    
    def __init__(self, app):
        """Initialize the main menu screen."""
        super().__init__(app)
        
        # Create default style with accessibility features
        self.style = ComponentStyle(
            background_color=(40, 44, 52),
            font_color=(255, 255, 255),
            hover_color=(60, 64, 72),
            active_color=(80, 84, 92),
            disabled_color=(30, 34, 42),
            border_color=(70, 74, 82),
            font_size=24,
            font_weight="normal",
            padding=(20, 10),
            border_radius=8,
            haptic_feedback=True
        )
        
        # Initialize responsive layout manager
        self.layout = Layout(
            min_width=800,
            min_height=600,
            padding=20,
            gap=16
        )
        
        # Create UI elements with accessibility features
        self.create_ui_elements()
        
        # Set up keyboard navigation
        self.focusable_elements: List[Button] = []
        self.current_focus_index = 0
        
        # Initialize screen reader text
        self.screen_reader_text = ""
        
    def create_ui_elements(self):
        """Create UI elements with accessibility support."""
        # Title with proper heading role
        self.title = Text(
            "Visual DM",
            position=(400, 100),
            style=self.style,
            role="heading",
            level=1
        )
        
        # Main menu buttons with ARIA labels and keyboard support
        button_configs = [
            ("New Game", self.new_game, "Start a new game session"),
            ("Load Game", self.load_game, "Load a previously saved game"),
            ("Settings", self.settings, "Adjust game settings and preferences"),
            ("Template Editor", self.template_editor, "Open the Building Type Template Editor"),
            ("Credits", self.credits, "View game credits and acknowledgments"),
            ("Exit", self.exit, "Exit the game")
        ]
        
        self.buttons = []
        y_position = 200
        
        for text, callback, aria_label in button_configs:
            button = Button(
                text=text,
                callback=callback,
                position=(400, y_position),
                size=(200, 50),
                style=self.style,
                aria_label=aria_label,
                role="button",
                tabindex=0
            )
            self.buttons.append(button)
            self.focusable_elements.append(button)
            y_position += 70
            
    def handle_event(self, event: pygame.event.Event):
        """Handle events with keyboard navigation support."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                # Handle tab navigation
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.focus_previous()
                else:
                    self.focus_next()
            elif event.key == pygame.K_RETURN:
                # Activate focused element
                if self.focusable_elements and self.current_focus_index >= 0:
                    focused = self.focusable_elements[self.current_focus_index]
                    focused.trigger()
                    
        # Handle regular button events
        for button in self.buttons:
            button.handle_event(event)
            
    def focus_next(self):
        """Move focus to next element."""
        if self.focusable_elements:
            self.current_focus_index = (self.current_focus_index + 1) % len(self.focusable_elements)
            self.update_focus()
            
    def focus_previous(self):
        """Move focus to previous element."""
        if self.focusable_elements:
            self.current_focus_index = (self.current_focus_index - 1) % len(self.focusable_elements)
            self.update_focus()
            
    def update_focus(self):
        """Update focus state of elements."""
        for i, element in enumerate(self.focusable_elements):
            element.set_focused(i == self.current_focus_index)
            if i == self.current_focus_index:
                self.screen_reader_text = f"Focused on {element.text} button. {element.aria_label}"
                
    def update(self, dt: float):
        """Update screen elements."""
        super().update(dt)
        
        # Update button positions based on layout
        self.layout.update(pygame.display.get_surface().get_size())
        
        # Update UI elements
        for button in self.buttons:
            button.update(dt)
            
    def draw(self, surface: pygame.Surface):
        """Draw screen elements with high contrast support."""
        # Draw background
        surface.fill(self.style.background_color)
        
        # Draw title
        self.title.draw(surface)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
            
        # Draw focus indicator if using keyboard navigation
        if pygame.key.get_focused() and self.current_focus_index >= 0:
            focused = self.focusable_elements[self.current_focus_index]
            rect = focused.get_rect()
            pygame.draw.rect(
                surface,
                self.style.primary_color,
                rect.inflate(4, 4),
                2,
                border_radius=self.style.border_radius
            )
            
    def new_game(self):
        """Start a new game."""
        self.app.set_screen("character_creation")
        
    def load_game(self):
        """Load a saved game."""
        self.app.set_screen("load_game")
        
    def settings(self):
        """Open settings screen."""
        self.app.set_screen("settings")
        
    def template_editor(self):
        """Open the Building Type Template Editor screen."""
        self.app.set_screen("template_editor")
        
    def credits(self):
        """Show credits screen."""
        self.app.set_screen("credits")
        
    def exit(self):
        """Exit the game."""
        self.app.quit() 