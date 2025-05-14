"""
Game screen module.
"""

import pygame
from typing import Optional, Dict, Any
from core.screen import Screen
from core.ui.button import Button
from core.ui.text import Text
from core.ui.layout import Layout
from visual_client.ui.screens.game.npc_affinity_debug_panel import NPCAffinityDebugPanel
from visual_client.ui.screens.game.journal_screen import JournalScreen

class GameScreen(Screen):
    """Game screen."""
    
    def __init__(self, app):
        """Initialize the game screen."""
        super().__init__(app)
        self.title = Text("Game", 48, (255, 255, 255))
        self.back_button = Button("Back to Menu", lambda: self.app.set_screen('main_menu'))
        self.affinity_debug_button = Button("NPC Affinity Debug", lambda: self.app.screen_manager.set_screen('npc_affinity_debug'))
        self.journal_button = Button("Quest Journal", self.open_journal)
        self.journal_screen = None
        self.showing_journal = False
        # Create layout
        self.layout = Layout()
        self.layout.add(self.title, "center", 0.2)
        self.layout.add(self.back_button, "center", 0.8)
        self.layout.add(self.affinity_debug_button, "center", 0.6)
        self.layout.add(self.journal_button, "center", 0.4)
    
    def open_journal(self):
        # Example: get character_id and region_id from app state
        character_id = getattr(self.app, 'character_id', 1)
        region_id = getattr(self.app, 'region_id', 1)
        self.journal_screen = JournalScreen(self.app.screen, character_id, region_id)
        self.showing_journal = True
    
    def update(self, dt: float) -> None:
        """Update the screen."""
        if self.showing_journal and self.journal_screen:
            self.journal_screen.update()
        else:
            self.layout.update(dt)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the screen."""
        if self.showing_journal and self.journal_screen:
            self.journal_screen.draw()
        else:
            surface.fill((40, 44, 52))  # Dark background
            self.layout.draw(surface)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event."""
        if self.showing_journal and self.journal_screen:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.showing_journal = False
                return True
            return self.journal_screen.handle_event(event)
        return self.layout.handle_event(event) 