import pygame
from typing import List, Optional, Tuple
from visual_client.core.managers.config_manager import ConfigManager
from visual_client.core.utils.error_handler import handle_component_error
from app.core.models.character import Character
from .character_creation_ui import CharacterCreationRenderer
from visual_client.ui.components.panel import Panel
from visual_client.ui.components.label import Label
from visual_client.ui.components.button import Button

class CharacterBrowser:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.renderer = CharacterCreationRenderer(screen)
        self.characters: List[Character] = []
        self.selected_character: Optional[Character] = None
        self.page = 0
        self.characters_per_page = 6

    def load_characters(self) -> None:
        """Load characters from storage."""
        try:
            # TODO: Implement character loading from database
            pass
        except Exception as e:
            handle_component_error(f"Error loading characters: {str(e)}")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events and return True if the screen should be redrawn."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_click(event.pos)
        return False

    def _handle_mouse_click(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse click events."""
        # Check character selection
        start_y = 100
        card_width = 300
        card_height = 150
        padding = 20
        
        for i, character in enumerate(self.characters[self.page * self.characters_per_page:(self.page + 1) * self.characters_per_page]):
            row = i // 2
            col = i % 2
            x = padding + (col * (card_width + padding))
            y = start_y + (row * (card_height + padding))
            
            if (x <= pos[0] <= x + card_width and y <= pos[1] <= y + card_height):
                self.selected_character = character
                return True
        
        # Check navigation buttons
        if self._is_navigation_click(pos):
            return True
        
        return False

    def _is_navigation_click(self, pos: Tuple[int, int]) -> bool:
        """Check if the click was on a navigation button."""
        # Previous page button
        if (20 <= pos[0] <= 120 and ConfigManager.screen_height - 60 <= pos[1] <= ConfigManager.screen_height - 20):
            if self.page > 0:
                self.page -= 1
                return True
        
        # Next page button
        if (ConfigManager.screen_width - 120 <= pos[0] <= ConfigManager.screen_width - 20 and 
            ConfigManager.screen_height - 60 <= pos[1] <= ConfigManager.screen_height - 20):
            if (self.page + 1) * self.characters_per_page < len(self.characters):
                self.page += 1
                return True
        
        return False

    def draw(self) -> None:
        """Draw the character browser screen."""
        self.renderer.draw_step_background("Character Browser")
        
        # Draw character cards
        start_y = 100
        card_width = 300
        card_height = 150
        padding = 20
        
        for i, character in enumerate(self.characters[self.page * self.characters_per_page:(self.page + 1) * self.characters_per_page]):
            row = i // 2
            col = i % 2
            x = padding + (col * (card_width + padding))
            y = start_y + (row * (card_height + padding))
            
            # Draw character card
            self._draw_character_card(character, x, y, card_width, card_height, 
                                    character == self.selected_character)
        
        # Draw navigation buttons
        self._draw_navigation_buttons()

    def _draw_character_card(self, character: Character, x: int, y: int, 
                           width: int, height: int, is_selected: bool) -> None:
        """Draw a character card."""
        # Draw card background
        color = self.renderer.colors['highlight'] if is_selected else self.renderer.colors['panel']
        panel = Panel(x, y, width, height, color)
        panel.draw(self.screen)
        
        # Draw character name
        name_label = Label(
            x + 10,
            y + 10,
            character.name,
            self.renderer.fonts['subtitle'],
            self.renderer.colors['text']
        )
        name_label.draw(self.screen)
        
        # Draw character details
        details = [
            f"Race: {character.race}",
            f"Class: {character.character_class}",
            f"Level: {character.level}"
        ]
        
        for i, detail in enumerate(details):
            detail_label = Label(
                x + 10,
                y + 50 + (i * 25),
                detail,
                self.renderer.fonts['body'],
                self.renderer.colors['text']
            )
            detail_label.draw(self.screen)

    def _draw_navigation_buttons(self) -> None:
        """Draw navigation buttons."""
        # Previous page button
        prev_enabled = self.page > 0
        prev_button = Button(
            20,
            ConfigManager.screen_height - 60,
            100,
            40,
            "Previous",
            self.renderer.fonts['body'],
            self.renderer.colors['highlight'] if prev_enabled else (200, 200, 200)
        )
        prev_button.draw(self.screen)
        
        # Next page button
        next_enabled = (self.page + 1) * self.characters_per_page < len(self.characters)
        next_button = Button(
            ConfigManager.screen_width - 120,
            ConfigManager.screen_height - 60,
            100,
            40,
            "Next",
            self.renderer.fonts['body'],
            self.renderer.colors['highlight'] if next_enabled else (200, 200, 200)
        )
        next_button.draw(self.screen)
