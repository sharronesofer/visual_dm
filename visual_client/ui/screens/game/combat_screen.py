"""
Combat screen with optimized rendering and animation handling.
"""

import pygame
import requests
import math
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import logging

from visual_client.ui.screens.combat_action_menu import CombatActionMenu

# Configure logging
logger = logging.getLogger(__name__)

class AnimationState(Enum):
    """Enumeration of animation states."""
    IDLE = auto()
    MOVING = auto()
    ATTACKING = auto()
    CASTING = auto()
    DAMAGED = auto()

@dataclass
class Animation:
    """Represents a combat animation."""
    start_pos: Tuple[float, float]
    end_pos: Tuple[float, float]
    start_time: float
    duration: float
    type: str
    surface: Optional[pygame.Surface] = None
    is_complete: bool = False

class CombatScreen:
    """Combat screen with optimized rendering."""
    
    def __init__(self, screen, character_data):
        """Initialize the combat screen."""
        self.screen = screen
        self.character_data = character_data
        self.font = pygame.font.SysFont(None, 24)

        # Grid configuration
        self.grid_radius = 5
        self.tile_size = 40
        self.tiles = []
        self.build_hex_grid()

        # Combat state
        self.player_pos = (0, 0)
        self.enemy_pos = (2, -2)
        self.turn = "player"
        self.combat_over = False
        self.result_text = ""
        self.next_screen = None

        # Animation system
        self.animations: Dict[str, List[Animation]] = {
            "player": [],
            "enemy": []
        }
        self.dirty_rects: List[pygame.Rect] = []
        self.last_frame_time = pygame.time.get_ticks()
        self.frame_delay = 16  # Target 60 FPS
        self.animation_cache: Dict[str, pygame.Surface] = {}
        self.max_animation_cache = 16

        # Action menu
        self.action_menu = CombatActionMenu(self.screen)
        self.available_actions = {
            "Attack": True,
            "Cast": False,
            "Skill": True,
            "Item": False
        }

        # Cache for rendered elements
        self._grid_cache = None
        self._grid_cache_rect = None
        self._entity_cache: Dict[str, pygame.Surface] = {}
        self._max_entity_cache = 8

    def build_hex_grid(self):
        """Build the hex grid for combat."""
        self.tiles = []
        for q in range(-self.grid_radius, self.grid_radius + 1):
            for r in range(-self.grid_radius, self.grid_radius + 1):
                if -q - r >= -self.grid_radius and -q - r <= self.grid_radius:
                    self.tiles.append((q, r))

    def hex_to_pixel(self, q: int, r: int) -> Tuple[float, float]:
        """Convert hex coordinates to pixel coordinates using coordinate utilities."""
        # Use coordinate utilities for hex grid conversion if available
        # Otherwise, fallback to direct math
        # TODO: Replace with coordinate_utils.hex_to_pixel if available
        x = self.screen.get_width() / 2 + q * self.tile_size * 1.5
        y = self.screen.get_height() / 2 + (r + q / 2) * self.tile_size * math.sqrt(3)
        assert isinstance(x, float) and isinstance(y, float), "Pixel coordinates must be floats"
        return (x, y)

    def _render_grid(self):
        """Render the hex grid to a surface using coordinate utilities."""
        if self._grid_cache is None:
            # Create a surface for the grid
            width = self.screen.get_width()
            height = self.screen.get_height()
            self._grid_cache = pygame.Surface((width, height), pygame.SRCALPHA)
            self._grid_cache_rect = pygame.Rect(0, 0, width, height)
            # Draw hex grid
            for q, r in self.tiles:
                center = self.hex_to_pixel(q, r)
                assert isinstance(center, tuple) and len(center) == 2, "Center must be a tuple of length 2"
                points = []
                for i in range(6):
                    angle_deg = 60 * i
                    angle_rad = math.radians(angle_deg)
                    x = center[0] + self.tile_size * 0.9 * math.cos(angle_rad)
                    y = center[1] + self.tile_size * 0.9 * math.sin(angle_rad)
                    points.append((x, y))
                pygame.draw.polygon(self._grid_cache, (80, 80, 80), points, 1)

    def _get_entity_surface(self, entity_type: str) -> pygame.Surface:
        """Get or create a cached surface for an entity."""
        if entity_type in self._entity_cache:
            return self._entity_cache[entity_type]
            
        # Create new surface
        surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        color = (255, 0, 0) if entity_type == "enemy" else (0, 255, 0)
        pygame.draw.circle(surface, color, (self.tile_size // 2, self.tile_size // 2), self.tile_size // 3)
        
        # Cache the surface
        if len(self._entity_cache) >= self._max_entity_cache:
            # Remove oldest cached surface
            oldest_key = min(self._entity_cache.keys(), key=lambda k: self._entity_cache[k].get_at((0, 0)))
            del self._entity_cache[oldest_key]
            
        self._entity_cache[entity_type] = surface
        return surface

    def _draw_entity(self, entity_type: str, pos: Tuple[int, int]) -> None:
        """Draw an entity at the given position."""
        try:
            surface = self._get_entity_surface(entity_type)
            pixel_pos = self.hex_to_pixel(*pos)
            rect = surface.get_rect(center=pixel_pos)
            self.screen.blit(surface, rect)
            self.dirty_rects.append(rect)
        except Exception as e:
            logger.error(f"Error drawing entity {entity_type}: {str(e)}")

    def _update_animations(self) -> None:
        """Update all active animations."""
        current_time = pygame.time.get_ticks() / 1000.0
        
        for entity_type in ["player", "enemy"]:
            for animation in self.animations[entity_type][:]:
                if animation.is_complete:
                    continue
                    
                elapsed = current_time - animation.start_time
                if elapsed >= animation.duration:
                    animation.is_complete = True
                    continue
                    
                # Calculate current position
                progress = elapsed / animation.duration
                current_x = animation.start_pos[0] + (animation.end_pos[0] - animation.start_pos[0]) * progress
                current_y = animation.start_pos[1] + (animation.end_pos[1] - animation.start_pos[1]) * progress
                
                # Draw animation
                if animation.surface:
                    rect = animation.surface.get_rect(center=(current_x, current_y))
                    self.screen.blit(animation.surface, rect)
                    self.dirty_rects.append(rect)
                    
            # Remove completed animations
            self.animations[entity_type] = [a for a in self.animations[entity_type] if not a.is_complete]

    def handle_event(self, event):
        """Handle events."""
        if self.combat_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.next_screen = None
            return

        if self.turn == "player":
            action = self.action_menu.handle_event(event)
            if action:
                self.process_player_action(action)

    def process_player_action(self, action: str) -> None:
        """Process a player action."""
        try:
            if action == "Attack":
                # Create attack animation
                start_pos = self.hex_to_pixel(*self.player_pos)
                end_pos = self.hex_to_pixel(*self.enemy_pos)
                animation = Animation(
                    start_pos=start_pos,
                    end_pos=end_pos,
                    start_time=pygame.time.get_ticks() / 1000.0,
                    duration=0.5,
                    type="attack",
                    surface=self._get_entity_surface("player")
                )
                self.animations["player"].append(animation)
                
                # Update combat state
                self.turn = "enemy"
                
        except Exception as e:
            logger.error(f"Error processing player action: {str(e)}")

    def draw(self):
        """Draw the combat screen."""
        current_time = pygame.time.get_ticks()
        
        # Only redraw if enough time has passed
        if current_time - self.last_frame_time < self.frame_delay:
            return
            
        self.last_frame_time = current_time
        
        # Clear only dirty areas
        if self.dirty_rects:
            for rect in self.dirty_rects:
                self.screen.fill((0, 0, 0), rect)
            
            # Render grid if needed
            self._render_grid()
            if self._grid_cache:
                self.screen.blit(self._grid_cache, self._grid_cache_rect)
            
            # Update and draw animations
            self._update_animations()
            
            # Draw entities
            self._draw_entity("player", self.player_pos)
            self._draw_entity("enemy", self.enemy_pos)
            
            # Draw combat result if game is over
            if self.combat_over:
                result_surface = self.font.render(self.result_text, True, (255, 255, 0))
                self.screen.blit(result_surface, (300, 550))
                back_surface = self.font.render("Press ESC to return", True, (200, 200, 200))
                self.screen.blit(back_surface, (280, 580))
            
            # Draw action menu
            if not self.combat_over:
                self.action_menu.set_enabled_actions(self.available_actions)
                self.action_menu.draw()
            
            # Clear dirty rects after drawing
            self.dirty_rects = []
            
            pygame.display.flip()

    def distance(self, pos1, pos2):
        q1, r1 = pos1
        q2, r2 = pos2
        return max(abs(q1 - q2), abs(r1 - r2), abs((-q1 - r1) - (-q2 - r2)))
