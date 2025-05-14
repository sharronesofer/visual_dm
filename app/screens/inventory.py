"""
Inventory screen.
Displays character inventory and equipment.
"""

from typing import Dict, Any, Optional, Callable, List
import pygame
from app.core.screens.base import BaseScreen
from app.core.components.base import BaseComponent
from app.core.utils.screen_utils import ScreenUtils

class InventoryScreen(BaseScreen):
    """Screen for displaying character inventory."""
    
    def __init__(self, width: int, height: int, inventory_data: Dict[str, Any], **kwargs):
        super().__init__(width, height, **kwargs)
        self.inventory_data = inventory_data
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize the screen's components."""
        # Create header
        self.add_component(ScreenUtils.create_label(
            x=20,
            y=20,
            width=self.width - 40,
            height=40,
            text="Inventory",
            font=pygame.font.Font(None, 32),
            text_color=(255, 255, 255),
            background_color=(50, 50, 50),
            alignment='center'
        ))

        # Create equipment section
        equipment_y = 80
        equipment = [
            ('Head', self.inventory_data.get('equipment', {}).get('head')),
            ('Chest', self.inventory_data.get('equipment', {}).get('chest')),
            ('Hands', self.inventory_data.get('equipment', {}).get('hands')),
            ('Legs', self.inventory_data.get('equipment', {}).get('legs')),
            ('Feet', self.inventory_data.get('equipment', {}).get('feet')),
            ('Main Hand', self.inventory_data.get('equipment', {}).get('main_hand')),
            ('Off Hand', self.inventory_data.get('equipment', {}).get('off_hand'))
        ]

        for i, (slot, item) in enumerate(equipment):
            self.add_component(ScreenUtils.create_label(
                x=20,
                y=equipment_y + (i * 30),
                width=200,
                height=25,
                text=f"{slot}: {item.get('name', 'Empty') if item else 'Empty'}",
                text_color=(200, 200, 200)
            ))

        # Create inventory items section
        items_y = equipment_y + (len(equipment) * 30) + 20
        items = self.inventory_data.get('items', [])
        
        # Create scrollable container for items
        item_components = []
        for i, item in enumerate(items):
            item_components.append(ScreenUtils.create_label(
                x=0,
                y=i * 30,
                width=300,
                height=25,
                text=f"{item.get('name', 'Unknown')} x{item.get('quantity', 1)}",
                text_color=(200, 200, 200)
            ))

        self.add_component(ScreenUtils.create_scrollable(
            x=20,
            y=items_y,
            width=320,
            height=200,
            content=item_components,
            background_color=(40, 40, 40)
        ))

        # Create use item button
        self.add_component(ScreenUtils.create_button(
            x=self.width - 220,
            y=items_y,
            width=200,
            height=40,
            text="Use Selected Item",
            on_click=self._handle_use_item,
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

    def _handle_use_item(self) -> None:
        """Handle use item button click."""
        if self._on_use_item:
            self._on_use_item()

    def _handle_back(self) -> None:
        """Handle back button click."""
        if self._on_back:
            self._on_back()

    def set_on_use_item(self, callback: Optional[Callable]) -> None:
        """Set the use item button callback."""
        self._on_use_item = callback

    def set_on_back(self, callback: Optional[Callable]) -> None:
        """Set the back button callback."""
        self._on_back = callback 