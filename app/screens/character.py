"""
Character screen.
Displays character information and stats.
"""

from typing import Dict, Any, Optional, Callable
import pygame
from app.core.screens.base import BaseScreen
from app.core.components.base import BaseComponent
from app.core.utils.screen_utils import ScreenUtils

class CharacterScreen(BaseScreen):
    """Screen for displaying character information."""
    
    def __init__(self, width: int, height: int, character_data: Dict[str, Any], **kwargs):
        super().__init__(width, height, **kwargs)
        self.character_data = character_data
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize the screen's components."""
        # Create header
        self.add_component(ScreenUtils.create_label(
            x=20,
            y=20,
            width=self.width - 40,
            height=40,
            text=f"Character: {self.character_data.get('name', 'Unknown')}",
            font=pygame.font.Font(None, 32),
            text_color=(255, 255, 255),
            background_color=(50, 50, 50),
            alignment='center'
        ))

        # Create stats section
        stats_y = 80
        stats = [
            ('Level', str(self.character_data.get('level', 1))),
            ('Race', self.character_data.get('race', 'Unknown')),
            ('Class', self.character_data.get('class', 'Unknown')),
            ('Health', f"{self.character_data.get('current_health', 0)}/{self.character_data.get('max_health', 0)}"),
            ('Mana', f"{self.character_data.get('current_mana', 0)}/{self.character_data.get('max_mana', 0)}"),
            ('Strength', str(self.character_data.get('strength', 0))),
            ('Dexterity', str(self.character_data.get('dexterity', 0))),
            ('Constitution', str(self.character_data.get('constitution', 0))),
            ('Intelligence', str(self.character_data.get('intelligence', 0))),
            ('Wisdom', str(self.character_data.get('wisdom', 0))),
            ('Charisma', str(self.character_data.get('charisma', 0)))
        ]

        for i, (stat_name, stat_value) in enumerate(stats):
            self.add_component(ScreenUtils.create_label(
                x=20,
                y=stats_y + (i * 30),
                width=200,
                height=25,
                text=f"{stat_name}: {stat_value}",
                text_color=(200, 200, 200)
            ))

        # Create inventory button
        self.add_component(ScreenUtils.create_button(
            x=self.width - 220,
            y=stats_y,
            width=200,
            height=40,
            text="View Inventory",
            on_click=self._handle_inventory,
            background_color=(70, 70, 70),
            text_color=(255, 255, 255)
        ))

        # Create back button
        self.add_component(ScreenUtils.create_button(
            x=20,
            y=self.height - 60,
            width=100,
            height=40,
            text="Back",
            on_click=self._handle_back,
            background_color=(70, 70, 70),
            text_color=(255, 255, 255)
        ))

    def _handle_inventory(self) -> None:
        """Handle inventory button click."""
        if self._on_inventory:
            self._on_inventory()

    def _handle_back(self) -> None:
        """Handle back button click."""
        if self._on_back:
            self._on_back()

    def set_on_inventory(self, callback: Optional[Callable]) -> None:
        """Set the inventory button callback."""
        self._on_inventory = callback

    def set_on_back(self, callback: Optional[Callable]) -> None:
        """Set the back button callback."""
        self._on_back = callback 