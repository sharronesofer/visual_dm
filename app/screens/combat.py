"""
Combat screen.
Displays combat information and controls.
"""

from typing import Dict, Any, Optional, Callable, List
import pygame
from app.core.screens.base import BaseScreen
from app.core.components.base import BaseComponent
from app.core.utils.screen_utils import ScreenUtils

class CombatScreen(BaseScreen):
    """Screen for displaying combat information and controls."""
    
    def __init__(self, width: int, height: int, combat_data: Dict[str, Any], **kwargs):
        super().__init__(width, height, **kwargs)
        self.combat_data = combat_data
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize the screen's components."""
        # Create header
        self.add_component(ScreenUtils.create_label(
            x=20,
            y=20,
            width=self.width - 40,
            height=40,
            text=f"Combat - Round {self.combat_data.get('round', 1)}",
            font=pygame.font.Font(None, 32),
            text_color=(255, 255, 255),
            background_color=(50, 50, 50),
            alignment='center'
        ))

        # Create combatants section
        combatants_y = 80
        combatants = self.combat_data.get('combatants', [])
        
        # Create scrollable container for combatants
        combatant_components = []
        for i, combatant in enumerate(combatants):
            combatant_components.append(ScreenUtils.create_label(
                x=0,
                y=i * 30,
                width=300,
                height=25,
                text=f"{combatant.get('name', 'Unknown')} - HP: {combatant.get('current_health', 0)}/{combatant.get('max_health', 0)}",
                text_color=(200, 200, 200)
            ))

        self.add_component(ScreenUtils.create_scrollable(
            x=20,
            y=combatants_y,
            width=320,
            height=200,
            content=combatant_components,
            background_color=(40, 40, 40)
        ))

        # Create action buttons
        actions_y = combatants_y + 220
        actions = [
            ('Attack', self._handle_attack),
            ('Cast Spell', self._handle_cast_spell),
            ('Use Item', self._handle_use_item),
            ('Flee', self._handle_flee)
        ]

        for i, (action_text, handler) in enumerate(actions):
            self.add_component(ScreenUtils.create_button(
                x=20 + (i * 160),
                y=actions_y,
                width=150,
                height=40,
                text=action_text,
                on_click=handler,
                background_color=(70, 70, 70),
                text_color=(255, 255, 255)
            ))

        # Create combat log
        self.add_component(ScreenUtils.create_scrollable(
            x=20,
            y=actions_y + 60,
            width=self.width - 40,
            height=200,
            content=[
                ScreenUtils.create_label(
                    x=0,
                    y=i * 20,
                    width=self.width - 40,
                    height=20,
                    text=log_entry,
                    text_color=(200, 200, 200)
                ) for i, log_entry in enumerate(self.combat_data.get('log', []))
            ],
            background_color=(40, 40, 40)
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

    def _handle_attack(self) -> None:
        """Handle attack button click."""
        if self._on_attack:
            self._on_attack()

    def _handle_cast_spell(self) -> None:
        """Handle cast spell button click."""
        if self._on_cast_spell:
            self._on_cast_spell()

    def _handle_use_item(self) -> None:
        """Handle use item button click."""
        if self._on_use_item:
            self._on_use_item()

    def _handle_flee(self) -> None:
        """Handle flee button click."""
        if self._on_flee:
            self._on_flee()

    def _handle_back(self) -> None:
        """Handle back button click."""
        if self._on_back:
            self._on_back()

    def set_on_attack(self, callback: Optional[Callable]) -> None:
        """Set the attack button callback."""
        self._on_attack = callback

    def set_on_cast_spell(self, callback: Optional[Callable]) -> None:
        """Set the cast spell button callback."""
        self._on_cast_spell = callback

    def set_on_use_item(self, callback: Optional[Callable]) -> None:
        """Set the use item button callback."""
        self._on_use_item = callback

    def set_on_flee(self, callback: Optional[Callable]) -> None:
        """Set the flee button callback."""
        self._on_flee = callback

    def set_on_back(self, callback: Optional[Callable]) -> None:
        """Set the back button callback."""
        self._on_back = callback 