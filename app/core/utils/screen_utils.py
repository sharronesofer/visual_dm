"""
Screen utilities.
Provides common functionality for screen operations.
"""

from typing import List, Dict, Any, Optional, Callable
import pygame
from app.core.components.base import BaseComponent
from app.core.screens.base import BaseScreen

class ScreenUtils:
    """Utility class for screen operations."""
    
    @staticmethod
    def create_button(
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        on_click: Optional[Callable] = None,
        **kwargs
    ) -> BaseComponent:
        """Create a button component."""
        from app.core.components.button import Button
        return Button(x, y, width, height, text, on_click, **kwargs)

    @staticmethod
    def create_textbox(
        x: int,
        y: int,
        width: int,
        height: int,
        text: str = '',
        **kwargs
    ) -> BaseComponent:
        """Create a textbox component."""
        from app.core.components.textbox import Textbox
        return Textbox(x, y, width, height, text, **kwargs)

    @staticmethod
    def create_tooltip(
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        **kwargs
    ) -> BaseComponent:
        """Create a tooltip component."""
        from app.core.components.tooltip import Tooltip
        return Tooltip(x, y, width, height, text, **kwargs)

    @staticmethod
    def create_label(
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        **kwargs
    ) -> BaseComponent:
        """Create a label component."""
        from app.core.components.label import Label
        return Label(x, y, width, height, text, **kwargs)

    @staticmethod
    def create_menu(
        x: int,
        y: int,
        width: int,
        height: int,
        items: List[Dict[str, Any]],
        on_select: Optional[Callable] = None,
        **kwargs
    ) -> BaseComponent:
        """Create a menu component."""
        from app.core.components.menu import Menu
        return Menu(x, y, width, height, items, on_select, **kwargs)

    @staticmethod
    def create_scrollable(
        x: int,
        y: int,
        width: int,
        height: int,
        content: List[BaseComponent],
        **kwargs
    ) -> BaseComponent:
        """Create a scrollable component."""
        from app.core.components.scrollable import Scrollable
        return Scrollable(x, y, width, height, content, **kwargs)

    @staticmethod
    def create_character_screen(
        width: int,
        height: int,
        character_data: Dict[str, Any],
        **kwargs
    ) -> BaseScreen:
        """Create a character screen."""
        from app.screens.character import CharacterScreen
        return CharacterScreen(width, height, character_data, **kwargs)

    @staticmethod
    def create_inventory_screen(
        width: int,
        height: int,
        inventory_data: Dict[str, Any],
        **kwargs
    ) -> BaseScreen:
        """Create an inventory screen."""
        from app.screens.inventory import InventoryScreen
        return InventoryScreen(width, height, inventory_data, **kwargs)

    @staticmethod
    def create_combat_screen(
        width: int,
        height: int,
        combat_data: Dict[str, Any],
        **kwargs
    ) -> BaseScreen:
        """Create a combat screen."""
        from app.screens.combat import CombatScreen
        return CombatScreen(width, height, combat_data, **kwargs)

    @staticmethod
    def create_dialog_screen(
        width: int,
        height: int,
        dialog_data: Dict[str, Any],
        **kwargs
    ) -> BaseScreen:
        """Create a dialog screen."""
        from app.screens.dialog import DialogScreen
        return DialogScreen(width, height, dialog_data, **kwargs)

    @staticmethod
    def create_quest_screen(
        width: int,
        height: int,
        quest_data: Dict[str, Any],
        **kwargs
    ) -> BaseScreen:
        """Create a quest screen."""
        from app.screens.quest import QuestScreen
        return QuestScreen(width, height, quest_data, **kwargs)

    @staticmethod
    def create_map_screen(
        width: int,
        height: int,
        map_data: Dict[str, Any],
        **kwargs
    ) -> BaseScreen:
        """Create a map screen."""
        from app.screens.map import MapScreen
        return MapScreen(width, height, map_data, **kwargs)

    @staticmethod
    def create_settings_screen(
        width: int,
        height: int,
        settings_data: Dict[str, Any],
        **kwargs
    ) -> BaseScreen:
        """Create a settings screen."""
        from app.screens.settings import SettingsScreen
        return SettingsScreen(width, height, settings_data, **kwargs)

    @staticmethod
    def create_loading_screen(
        width: int,
        height: int,
        loading_data: Dict[str, Any],
        **kwargs
    ) -> BaseScreen:
        """Create a loading screen."""
        from app.screens.loading import LoadingScreen
        return LoadingScreen(width, height, loading_data, **kwargs)

    @staticmethod
    def create_error_screen(
        width: int,
        height: int,
        error_data: Dict[str, Any],
        **kwargs
    ) -> BaseScreen:
        """Create an error screen."""
        from app.screens.error import ErrorScreen
        return ErrorScreen(width, height, error_data, **kwargs) 