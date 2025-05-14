"""
Region map screen with optimized rendering.

This module provides a region map screen that:
1. Implements viewport culling to only render visible sections
2. Uses lazy-loading for map sections to reduce memory usage
3. Optimizes rendering with surface caching
4. Provides smooth scrolling and zooming
5. Implements efficient collision detection
"""

import pygame
import requests
import json
from typing import Dict, Tuple, Optional, Set
from visual_client.core.utils.terrain_manager import TerrainManager
from visual_client.core.utils.tile_loader import build_terrain_tile_map
import logging
from functools import lru_cache
from dataclasses import dataclass
from app.core.utils.error_utils import ScreenError
from app.core.utils.screen_utils import ScreenManager
from app.core.utils.render_utils import Renderer
from app.ui.components import (
    Panel,
    ComponentStyle,
    BaseComponent
)
from visual_client.core.utils.coordinates import GlobalCoord, LocalCoord
from visual_client.core.utils import coordinate_utils as cu

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
HTTP_TIMEOUT = 10
VIEW_RADIUS = 3
TILE_SIZE = 32
BACKGROUND_COLOR = (34, 139, 34)  # Forest green
FOG_COLOR = (100, 100, 100, 160)  # Lighter fog

def _safe_get(url: str, timeout: int = HTTP_TIMEOUT) -> Optional[dict]:
    """Safely make a GET request with error handling."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error in GET request to {url}: {e}")
        return None

def _safe_post(url: str, json_data: dict, timeout: int = HTTP_TIMEOUT) -> Optional[dict]:
    """Safely make a POST request with error handling."""
    try:
        response = requests.post(url, json=json_data, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error in POST request to {url}: {e}")
        return None

@dataclass
class MapSection:
    """Represents a section of the map that can be loaded/unloaded."""
    x: int
    y: int
    width: int
    height: int
    surface: Optional[pygame.Surface] = None
    is_loaded: bool = False
    last_accessed: float = 0.0
    is_visible: bool = False
    priority: int = 0  # Higher priority means more likely to be kept in memory

@dataclass
class Viewport:
    """Represents the visible area of the map."""
    x: float
    y: float
    width: int
    height: int
    scale: float = 1.0
    dirty: bool = True  # Whether the viewport needs redrawing
    
    @property
    def position(self) -> GlobalCoord:
        """Get the viewport position as a GlobalCoord."""
        return GlobalCoord(self.x, self.y)
    
    @position.setter
    def position(self, pos: GlobalCoord) -> None:
        """Set the viewport position from a GlobalCoord."""
        self.x = pos.x
        self.y = pos.y
        self.dirty = True
    
    def get_visible_rect_tuple(self) -> Tuple[float, float, float, float]:
        """Get the viewport rectangle as a tuple."""
        return (
            self.x,
            self.y,
            self.width / self.scale,
            self.height / self.scale
        )
    
    def get_visible_bounds(self) -> Tuple[GlobalCoord, GlobalCoord]:
        """Get the top-left and bottom-right points of the visible area."""
        return (
            GlobalCoord(self.x, self.y),
            GlobalCoord(
                self.x + (self.width / self.scale),
                self.y + (self.height / self.scale)
            )
        )

class RegionMapScreen:
    """Region map screen with optimized rendering."""
    
    def __init__(self, screen_manager: ScreenManager):
        """Initialize the region map screen.
        
        Args:
            screen_manager: Screen manager instance
        """
        self.screen_manager = screen_manager
        self.viewport = Viewport(0, 0, 800, 600)
        self.map_sections: Dict[Tuple[int, int], MapSection] = {}
        self.visible_sections: Set[Tuple[int, int]] = set()
        self.section_size = 512  # Size of each map section in pixels
        self.max_loaded_sections = 16  # Maximum number of sections to keep in memory
        self.scroll_speed = 10
        self.zoom_speed = 0.1
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        
        # Initialize UI components
        self._initialize_components()
        
        # Initialize caches
        self._surface_cache: Dict[Tuple[int, int], pygame.Surface] = {}
        self._max_surface_cache = 32  # Maximum number of surfaces to cache
        
        # Initialize terrain manager
        self.terrain_manager = TerrainManager()
        
    def _initialize_components(self) -> None:
        """Initialize UI components."""
        try:
            screen_rect = self.screen_manager.get_screen_rect()
            
            # Main panel
            self.main_panel = Panel(
                pygame.Rect(0, 0, screen_rect.width, screen_rect.height),
                ComponentStyle(background_color=(30, 30, 30))
            )
            
            # Map panel
            self.map_panel = Panel(
                pygame.Rect(0, 0, screen_rect.width, screen_rect.height),
                ComponentStyle(background_color=(20, 20, 20))
            )
            
        except Exception as e:
            raise ScreenError(f"Failed to initialize components: {str(e)}")
            
    def _get_section_key(self, x: float, y: float) -> Tuple[int, int]:
        """Get the section key for given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple[int, int]: Section key
        """
        # Convert to int to ensure consistent section keys
        return (
            int(x // self.section_size),
            int(y // self.section_size)
        )
        
    def _get_visible_sections(self) -> Set[Tuple[int, int]]:
        """Get the set of section keys that are currently visible.
        
        Returns:
            Set[Tuple[int, int]]: Set of visible section keys
        """
        visible = set()
        
        # Get viewport bounds using GlobalCoords
        top_left, bottom_right = self.viewport.get_visible_bounds()
        
        # Add buffer for smoother scrolling
        buffer_size = self.section_size
        
        # Calculate the range of sections to check
        start_x = int((top_left.x - buffer_size) // self.section_size)
        start_y = int((top_left.y - buffer_size) // self.section_size)
        end_x = int((bottom_right.x + buffer_size) // self.section_size) + 1
        end_y = int((bottom_right.y + buffer_size) // self.section_size) + 1
        
        # Add sections in the visible range
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                visible.add((x, y))
                
        return visible
        
    def _load_section(self, section_key: Tuple[int, int]) -> None:
        """Load a map section into memory.
        
        Args:
            section_key: Section key to load
        """
        if section_key in self.map_sections and self.map_sections[section_key].is_loaded:
            return
            
        # Unload least recently used section if we're at the limit
        if len(self.map_sections) >= self.max_loaded_sections:
            self._unload_least_recent_section()
            
        # Create new section
        section = MapSection(
            x=section_key[0] * self.section_size,
            y=section_key[1] * self.section_size,
            width=self.section_size,
            height=self.section_size
        )
        
        # Load section data
        try:
            section.surface = self._generate_section_surface(section)
            section.is_loaded = True
            section.last_accessed = pygame.time.get_ticks() / 1000.0
            section.is_visible = section_key in self.visible_sections
            section.priority = self._calculate_section_priority(section_key)
            self.map_sections[section_key] = section
        except Exception as e:
            logger.error(f"Failed to load section {section_key}: {str(e)}")
            
    def _calculate_section_priority(self, section_key: Tuple[int, int]) -> int:
        """Calculate the priority of a section for memory management."""
        priority = 0
        if section_key in self.visible_sections:
            priority += 100  # Visible sections have highest priority
        if abs(section_key[0]) <= 1 and abs(section_key[1]) <= 1:
            priority += 50  # Sections near the center have higher priority
        return priority
            
    def _unload_least_recent_section(self) -> None:
        """Unload the least recently accessed section."""
        if not self.map_sections:
            return
            
        # Find the section with lowest priority and least recent access
        lru_section = None
        lru_score = float('inf')
        
        for key, section in self.map_sections.items():
            if not section.is_visible:
                score = section.last_accessed - section.priority
                if score < lru_score:
                    lru_section = key
                    lru_score = score
                    
        if lru_section:
            del self.map_sections[lru_section]
            
    def _generate_section_surface(self, section: MapSection) -> pygame.Surface:
        """Generate the surface for a map section.
        
        Args:
            section: Section to generate surface for
            
        Returns:
            pygame.Surface: Generated surface
        """
        # Check cache first
        cache_key = (section.x, section.y)
        if cache_key in self._surface_cache:
            return self._surface_cache[cache_key]
            
        surface = pygame.Surface((section.width, section.height), pygame.SRCALPHA)
        
        # Get terrain data for this section
        terrain_data = self.terrain_manager.get_viewport_terrain(
            section.x // TILE_SIZE,
            section.y // TILE_SIZE,
            VIEW_RADIUS
        )
        
        # Draw terrain
        for tile_key, tile_data in terrain_data.items():
            x, y = map(int, tile_key.split('_'))
            tile_x = (x * TILE_SIZE) - section.x
            tile_y = (y * TILE_SIZE) - section.y
            
            # Only draw tiles that are within the section bounds
            if (0 <= tile_x < section.width and 0 <= tile_y < section.height):
                self._draw_tile(surface, tile_x, tile_y, tile_data)
                
        # Cache the surface
        if len(self._surface_cache) >= self._max_surface_cache:
            # Remove oldest cached surface
            oldest_key = min(self._surface_cache.keys(), key=lambda k: self._surface_cache[k].get_at((0, 0)))
            del self._surface_cache[oldest_key]
            
        self._surface_cache[cache_key] = surface
        return surface
        
    def _draw_tile(self, surface: pygame.Surface, x: int, y: int, tile_data: dict) -> None:
        """Draw a single tile on the surface."""
        terrain_type = tile_data.get('type', 'grass')
        color = self._get_terrain_color(terrain_type)
        pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))
        
    def _get_terrain_color(self, terrain_type: str) -> Tuple[int, int, int]:
        """Get the color for a terrain type."""
        colors = {
            'grass': (34, 139, 34),
            'water': (0, 105, 148),
            'sand': (194, 178, 128),
            'mountain': (139, 137, 137),
            'forest': (0, 100, 0)
        }
        return colors.get(terrain_type, (100, 100, 100))
        
    def _handle_scroll(self, dx: float, dy: float) -> None:
        """Handle scrolling the viewport.
        
        Args:
            dx: Change in x
            dy: Change in y
        """
        # Convert the current position to a GlobalCoord
        current_pos = self.viewport.position
        
        # Create a movement vector and apply it
        movement = (dx, dy)
        new_pos_tuple = cu.vec_add(cu.global_to_tuple(current_pos), movement + (0.0,))  # Add z component
        
        # Update the viewport position
        self.viewport.x = new_pos_tuple[0]
        self.viewport.y = new_pos_tuple[1]
        
        # Mark viewport as dirty
        self.viewport.dirty = True
        
        # Recalculate visible sections
        self.visible_sections = self._get_visible_sections()
        
    def _handle_zoom(self, factor: float) -> None:
        """Handle map zooming.
        
        Args:
            factor: Zoom factor
        """
        old_scale = self.viewport.scale
        self.viewport.scale = max(
            self.min_zoom,
            min(self.max_zoom, self.viewport.scale * (1 + factor * self.zoom_speed))
        )
        
        # Adjust viewport position to zoom towards mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.viewport.x += (mouse_x / old_scale - mouse_x / self.viewport.scale)
        self.viewport.y += (mouse_y / old_scale - mouse_y / self.viewport.scale)
        
        self.viewport.dirty = True
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events with error handling.
        
        Args:
            event: Event to handle
            
        Returns:
            bool: True if event was handled
        """
        try:
            if event.type == pygame.QUIT:
                return True
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    self._handle_zoom(1)
                elif event.button == 5:  # Scroll down
                    self._handle_zoom(-1)
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self._handle_scroll(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self._handle_scroll(1, 0)
                elif event.key == pygame.K_UP:
                    self._handle_scroll(0, -1)
                elif event.key == pygame.K_DOWN:
                    self._handle_scroll(0, 1)
                    
            return False
            
        except Exception as e:
            logger.error(f"Error handling event: {str(e)}")
            return True
            
    def update(self) -> None:
        """Update screen state."""
        try:
            # Update visible sections
            new_visible = self._get_visible_sections()
            if new_visible != self.visible_sections:
                self.visible_sections = new_visible
                self.viewport.dirty = True
                
            # Update section visibility and priority
            for section_key, section in self.map_sections.items():
                section.is_visible = section_key in self.visible_sections
                section.priority = self._calculate_section_priority(section_key)
                
            # Load newly visible sections
            for section_key in self.visible_sections:
                self._load_section(section_key)
                
            # Update components
            self.main_panel.update()
            self.map_panel.update()
            
        except Exception as e:
            logger.error(f"Error during update: {str(e)}")
            
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the screen with error handling.
        
        Args:
            surface: Surface to draw on
        """
        try:
            if not self.viewport.dirty:
                return
                
            # Draw background
            surface.fill((30, 30, 30))
            
            # Draw map sections
            for section_key in self.visible_sections:
                if section_key in self.map_sections:
                    section = self.map_sections[section_key]
                    if section.is_loaded and section.surface:
                        # Calculate screen position
                        screen_x = (section.x - self.viewport.x) * self.viewport.scale
                        screen_y = (section.y - self.viewport.y) * self.viewport.scale
                        
                        # Scale and draw section
                        scaled_surface = pygame.transform.scale(
                            section.surface,
                            (
                                int(section.width * self.viewport.scale),
                                int(section.height * self.viewport.scale)
                            )
                        )
                        surface.blit(scaled_surface, (screen_x, screen_y))
                        
            # Draw UI components
            self.main_panel.draw(surface)
            self.map_panel.draw(surface)
            
            self.viewport.dirty = False
            
        except Exception as e:
            logger.error(f"Error during draw: {str(e)}")
            # Draw fallback error screen
            surface.fill((0, 0, 0))
            font = pygame.font.SysFont(None, 24)
            text = font.render(
                "Error rendering map. Please try again.",
                True,
                (255, 0, 0)
            )
            text_rect = text.get_rect(center=surface.get_rect().center)
            surface.blit(text, text_rect)
