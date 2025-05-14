"""
Reusable character panel component for displaying character information.
"""

import pygame
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class CharacterPanelConfig:
    """Configuration for the character panel."""
    width: int
    height: int
    position: Tuple[int, int]
    background_color: Tuple[int, int, int] = (30, 30, 30)
    border_color: Tuple[int, int, int] = (100, 100, 100)
    border_width: int = 2
    padding: int = 10
    font_size: int = 24
    title_font_size: int = 32

class CharacterPanel:
    """Reusable character panel component."""
    
    def __init__(self, screen: pygame.Surface, config: CharacterPanelConfig):
        """Initialize the character panel.
        
        Args:
            screen: The pygame surface to draw on
            config: Panel configuration
        """
        self.screen = screen
        self.config = config
        self.rect = pygame.Rect(
            config.position[0],
            config.position[1],
            config.width,
            config.height
        )
        
        # Initialize fonts
        self.font = pygame.font.SysFont(None, config.font_size)
        self.title_font = pygame.font.SysFont(None, config.title_font_size)
        
        # Character data
        self.character_data: Optional[Dict[str, Any]] = None
        self.dirty = True
        
    def set_character_data(self, data: Dict[str, Any]) -> None:
        """Set the character data to display.
        
        Args:
            data: Character data dictionary
        """
        self.character_data = data
        self.dirty = True
        
    def draw(self) -> None:
        """Draw the character panel."""
        if not self.dirty or not self.character_data:
            return
            
        try:
            # Draw background
            pygame.draw.rect(self.screen, self.config.background_color, self.rect)
            pygame.draw.rect(
                self.screen,
                self.config.border_color,
                self.rect,
                self.config.border_width
            )
            
            # Draw character information
            self._draw_character_info()
            
            self.dirty = False
            
        except Exception as e:
            logger.error(f"Error drawing character panel: {str(e)}")
            
    def _draw_character_info(self) -> None:
        """Draw the character information."""
        if not self.character_data:
            return
            
        try:
            x = self.rect.left + self.config.padding
            y = self.rect.top + self.config.padding
            
            # Draw title
            title = self.character_data.get("name", "Unknown Character")
            title_surface = self.title_font.render(title, True, (255, 255, 255))
            self.screen.blit(title_surface, (x, y))
            y += title_surface.get_height() + self.config.padding
            
            # Draw basic info
            info_items = [
                ("Race", self.character_data.get("race", "Unknown")),
                ("Class", self.character_data.get("class", "Unknown")),
                ("Level", str(self.character_data.get("level", 1))),
                ("Background", self.character_data.get("background", "Unknown"))
            ]
            
            for label, value in info_items:
                text = f"{label}: {value}"
                surface = self.font.render(text, True, (200, 200, 200))
                self.screen.blit(surface, (x, y))
                y += surface.get_height() + self.config.padding
                
            # Draw stats
            y += self.config.padding
            stats_title = self.font.render("Stats:", True, (255, 255, 255))
            self.screen.blit(stats_title, (x, y))
            y += stats_title.get_height() + self.config.padding
            
            stats = self.character_data.get("stats", {})
            stat_items = [
                ("STR", stats.get("strength", 10)),
                ("DEX", stats.get("dexterity", 10)),
                ("CON", stats.get("constitution", 10)),
                ("INT", stats.get("intelligence", 10)),
                ("WIS", stats.get("wisdom", 10)),
                ("CHA", stats.get("charisma", 10))
            ]
            
            for label, value in stat_items:
                text = f"{label}: {value}"
                surface = self.font.render(text, True, (200, 200, 200))
                self.screen.blit(surface, (x, y))
                y += surface.get_height() + self.config.padding
                
            # Draw equipment
            y += self.config.padding
            equipment_title = self.font.render("Equipment:", True, (255, 255, 255))
            self.screen.blit(equipment_title, (x, y))
            y += equipment_title.get_height() + self.config.padding
            
            equipment = self.character_data.get("equipment", {})
            for slot, item in equipment.items():
                if item:
                    text = f"{slot}: {item.get('name', 'Unknown')}"
                    surface = self.font.render(text, True, (200, 200, 200))
                    self.screen.blit(surface, (x, y))
                    y += surface.get_height() + self.config.padding
                    
        except Exception as e:
            logger.error(f"Error drawing character info: {str(e)}")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events.
        
        Args:
            event: The event to handle
            
        Returns:
            bool: True if the event was handled
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False 