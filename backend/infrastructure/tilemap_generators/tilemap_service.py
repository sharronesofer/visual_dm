"""
Tilemap Service for POI System

Generates tilemap data for POI interiors and exteriors, providing
spatial layout information for game client rendering.
"""

from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field
import logging
import random
import json

from backend.infrastructure.systems.poi.models import PoiEntity, POIType, POIInteractionType
from backend.infrastructure.database import get_db_session
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TileType(str, Enum):
    """Types of tiles in a tilemap"""
    FLOOR = "floor"
    WALL = "wall"
    DOOR = "door"
    WINDOW = "window"
    STAIRS = "stairs"
    WATER = "water"
    VEGETATION = "vegetation"
    FURNITURE = "furniture"
    DECORATION = "decoration"
    INTERACTIVE = "interactive"


class RoomType(str, Enum):
    """Types of rooms that can be generated"""
    ENTRANCE = "entrance"
    MAIN_HALL = "main_hall"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    STORAGE = "storage"
    WORKSHOP = "workshop"
    OFFICE = "office"
    TAVERN = "tavern"
    SHOP = "shop"
    TEMPLE_HALL = "temple_hall"
    DUNGEON_CHAMBER = "dungeon_chamber"
    CORRIDOR = "corridor"


@dataclass
class Tile:
    """Represents a single tile in the tilemap"""
    x: int
    y: int
    tile_type: TileType
    walkable: bool = True
    interactive: bool = False
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Room:
    """Represents a room in the tilemap"""
    id: str
    room_type: RoomType
    x: int
    y: int
    width: int
    height: int
    tiles: List[Tile] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)  # Connected room IDs
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tilemap:
    """Complete tilemap for a POI"""
    poi_id: UUID
    width: int
    height: int
    tiles: List[List[Tile]]
    rooms: List[Room] = field(default_factory=list)
    spawn_points: List[Tuple[int, int]] = field(default_factory=list)
    exit_points: List[Tuple[int, int]] = field(default_factory=list)
    interactive_objects: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TilemapService:
    """Service for generating and managing POI tilemaps"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db_session()
        
        # Generation parameters
        self.default_room_size = (8, 8)
        self.max_rooms = 20
        self.room_templates = self._initialize_room_templates()
    
    def generate_tilemap(self, poi_id: UUID, size: Optional[Tuple[int, int]] = None) -> Optional[Tilemap]:
        """Generate a tilemap for the specified POI"""
        try:
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
            if not poi:
                logger.error(f"POI {poi_id} not found")
                return None
            
            # Determine tilemap size based on POI type and population
            if size is None:
                size = self._calculate_tilemap_size(poi)
            
            width, height = size
            
            # Initialize empty tilemap
            tiles = [[Tile(x, y, TileType.FLOOR) for x in range(width)] for y in range(height)]
            
            tilemap = Tilemap(
                poi_id=poi_id,
                width=width,
                height=height,
                tiles=tiles
            )
            
            # Generate based on POI type and interaction type
            if poi.interaction_type == POIInteractionType.COMBAT:
                self._generate_combat_layout(tilemap, poi)
            elif poi.interaction_type == POIInteractionType.EXPLORATION:
                self._generate_exploration_layout(tilemap, poi)
            elif poi.interaction_type in [POIInteractionType.SOCIAL, POIInteractionType.TRADE]:
                self._generate_social_layout(tilemap, poi)
            else:
                self._generate_generic_layout(tilemap, poi)
            
            # Add interactive objects based on POI type
            self._add_interactive_objects(tilemap, poi)
            
            logger.info(f"Generated tilemap for POI {poi_id}: {width}x{height}")
            return tilemap
            
        except Exception as e:
            logger.error(f"Error generating tilemap for POI {poi_id}: {e}")
            return None
    
    def get_tilemap_json(self, tilemap: Tilemap) -> str:
        """Convert tilemap to JSON format for client"""
        try:
            data = {
                "poi_id": str(tilemap.poi_id),
                "width": tilemap.width,
                "height": tilemap.height,
                "tiles": [
                    [{"type": tile.tile_type, "walkable": tile.walkable, "interactive": tile.interactive}
                     for tile in row]
                    for row in tilemap.tiles
                ],
                "rooms": [
                    {
                        "id": room.id,
                        "type": room.room_type,
                        "x": room.x, "y": room.y,
                        "width": room.width, "height": room.height,
                        "connections": room.connections,
                        "properties": room.properties
                    }
                    for room in tilemap.rooms
                ],
                "spawn_points": tilemap.spawn_points,
                "exit_points": tilemap.exit_points,
                "interactive_objects": tilemap.interactive_objects,
                "metadata": tilemap.metadata
            }
            return json.dumps(data, indent=2)
            
        except Exception as e:
            logger.error(f"Error converting tilemap to JSON: {e}")
            return "{}"
    
    def _calculate_tilemap_size(self, poi: PoiEntity) -> Tuple[int, int]:
        """Calculate appropriate tilemap size based on POI characteristics"""
        base_size = 32
        
        # Size modifiers based on POI type
        type_modifiers = {
            POIType.CITY: 2.0,
            POIType.TOWN: 1.5,
            POIType.VILLAGE: 1.0,
            POIType.FORTRESS: 1.8,
            POIType.TEMPLE: 1.3,
            POIType.MINE: 1.2,
            POIType.MARKET: 1.4,
            POIType.OUTPOST: 0.8
        }
        
        modifier = type_modifiers.get(poi.poi_type, 1.0)
        
        # Additional modifier based on population
        if poi.population:
            population_modifier = min(2.0, 1.0 + (poi.population / 1000))
            modifier *= population_modifier
        
        size = int(base_size * modifier)
        return (size, size)
    
    def _generate_combat_layout(self, tilemap: Tilemap, poi: PoiEntity):
        """Generate layout optimized for combat encounters"""
        # Create interconnected chambers with tactical positioning
        self._create_room(tilemap, "entrance", RoomType.ENTRANCE, 2, 2, 8, 6)
        self._create_room(tilemap, "main_chamber", RoomType.DUNGEON_CHAMBER, 12, 8, 12, 10)
        self._create_room(tilemap, "side_chamber1", RoomType.DUNGEON_CHAMBER, 2, 12, 8, 8)
        self._create_room(tilemap, "side_chamber2", RoomType.DUNGEON_CHAMBER, 20, 2, 8, 8)
        
        # Add corridors connecting rooms
        self._create_corridor(tilemap, (6, 5), (12, 13))
        self._create_corridor(tilemap, (24, 8), (24, 10))
        
        # Add walls and obstacles for tactical positioning
        self._add_obstacles(tilemap)
    
    def _generate_exploration_layout(self, tilemap: Tilemap, poi: PoiEntity):
        """Generate layout focused on discovery and secrets"""
        # Create winding passages with hidden areas
        self._create_room(tilemap, "entrance", RoomType.ENTRANCE, 2, 2, 6, 6)
        self._create_room(tilemap, "main_hall", RoomType.MAIN_HALL, 10, 10, 10, 8)
        self._create_room(tilemap, "secret_chamber", RoomType.DUNGEON_CHAMBER, 25, 25, 6, 6)
        
        # Add winding corridors
        self._create_winding_path(tilemap, (5, 8), (15, 10))
        self._create_hidden_passage(tilemap, (20, 15), (25, 28))
        
        # Add interactive elements for exploration
        tilemap.interactive_objects.extend([
            {"type": "ancient_inscription", "x": 13, "y": 14, "requires_investigation": True},
            {"type": "hidden_switch", "x": 22, "y": 18, "reveals": "secret_chamber"},
            {"type": "puzzle_mechanism", "x": 28, "y": 28, "difficulty": "medium"}
        ])
    
    def _generate_social_layout(self, tilemap: Tilemap, poi: PoiEntity):
        """Generate layout optimized for NPC interactions and commerce"""
        # Create open areas with multiple rooms for different activities
        self._create_room(tilemap, "entrance", RoomType.ENTRANCE, 2, 2, 8, 6)
        self._create_room(tilemap, "main_hall", RoomType.MAIN_HALL, 12, 2, 16, 12)
        self._create_room(tilemap, "shop", RoomType.SHOP, 2, 10, 8, 8)
        self._create_room(tilemap, "tavern", RoomType.TAVERN, 12, 16, 16, 10)
        self._create_room(tilemap, "office", RoomType.OFFICE, 20, 28, 8, 6)
        
        # Wide corridors for movement
        self._create_wide_corridor(tilemap, (10, 5), (12, 5))
        self._create_wide_corridor(tilemap, (6, 18), (12, 18))
        
        # Add NPCs and interactive elements
        tilemap.interactive_objects.extend([
            {"type": "merchant_counter", "x": 6, "y": 14, "npc": "merchant"},
            {"type": "tavern_bar", "x": 20, "y": 20, "npc": "bartender"},
            {"type": "quest_board", "x": 16, "y": 8, "interactive": True},
            {"type": "town_hall_desk", "x": 24, "y": 31, "npc": "official"}
        ])
    
    def _generate_generic_layout(self, tilemap: Tilemap, poi: PoiEntity):
        """Generate basic layout for neutral POIs"""
        # Simple room structure
        self._create_room(tilemap, "entrance", RoomType.ENTRANCE, 2, 2, 8, 6)
        self._create_room(tilemap, "main_area", RoomType.MAIN_HALL, 12, 8, 12, 10)
        self._create_room(tilemap, "storage", RoomType.STORAGE, 2, 12, 6, 6)
        
        # Basic connections
        self._create_corridor(tilemap, (6, 5), (12, 13))
    
    def _create_room(self, tilemap: Tilemap, room_id: str, room_type: RoomType, 
                    x: int, y: int, width: int, height: int):
        """Create a room in the tilemap"""
        if x + width >= tilemap.width or y + height >= tilemap.height:
            return  # Room doesn't fit
        
        room = Room(room_id, room_type, x, y, width, height)
        
        # Set floor tiles
        for ry in range(y, y + height):
            for rx in range(x, x + width):
                if 0 <= rx < tilemap.width and 0 <= ry < tilemap.height:
                    tilemap.tiles[ry][rx] = Tile(rx, ry, TileType.FLOOR)
        
        # Add walls around the room
        for ry in range(y, y + height):
            for rx in range(x, x + width):
                if rx == x or rx == x + width - 1 or ry == y or ry == y + height - 1:
                    if 0 <= rx < tilemap.width and 0 <= ry < tilemap.height:
                        tilemap.tiles[ry][rx] = Tile(rx, ry, TileType.WALL, walkable=False)
        
        tilemap.rooms.append(room)
        
        # Add entry point for first room
        if room_id == "entrance":
            tilemap.spawn_points.append((x + width // 2, y + height // 2))
    
    def _create_corridor(self, tilemap: Tilemap, start: Tuple[int, int], end: Tuple[int, int]):
        """Create a corridor between two points"""
        x1, y1 = start
        x2, y2 = end
        
        # Simple L-shaped corridor
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < tilemap.width and 0 <= y1 < tilemap.height:
                tilemap.tiles[y1][x] = Tile(x, y1, TileType.FLOOR)
        
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x2 < tilemap.width and 0 <= y < tilemap.height:
                tilemap.tiles[y][x2] = Tile(x2, y, TileType.FLOOR)
    
    def _create_wide_corridor(self, tilemap: Tilemap, start: Tuple[int, int], end: Tuple[int, int]):
        """Create a wide corridor for social spaces"""
        self._create_corridor(tilemap, start, end)
        # Add parallel corridor for width
        x1, y1 = start
        x2, y2 = end
        self._create_corridor(tilemap, (x1, y1 + 1), (x2, y2 + 1))
    
    def _create_winding_path(self, tilemap: Tilemap, start: Tuple[int, int], end: Tuple[int, int]):
        """Create a winding path for exploration areas"""
        # Add some randomness to the path
        x1, y1 = start
        x2, y2 = end
        
        # Create path with random turns
        current_x, current_y = x1, y1
        while current_x != x2 or current_y != y2:
            if random.random() < 0.5 and current_x != x2:
                current_x += 1 if x2 > current_x else -1
            else:
                current_y += 1 if y2 > current_y else -1
            
            if 0 <= current_x < tilemap.width and 0 <= current_y < tilemap.height:
                tilemap.tiles[current_y][current_x] = Tile(current_x, current_y, TileType.FLOOR)
    
    def _create_hidden_passage(self, tilemap: Tilemap, start: Tuple[int, int], end: Tuple[int, int]):
        """Create a hidden passage that requires discovery"""
        self._create_corridor(tilemap, start, end)
        # Mark as hidden/interactive
        x1, y1 = start
        tilemap.tiles[y1][x1].interactive = True
        tilemap.tiles[y1][x1].properties["hidden"] = True
    
    def _add_obstacles(self, tilemap: Tilemap):
        """Add obstacles for tactical combat positioning"""
        # Add some walls and barriers in strategic positions
        obstacles = [(15, 12), (18, 15), (20, 10), (25, 15)]
        for x, y in obstacles:
            if 0 <= x < tilemap.width and 0 <= y < tilemap.height:
                tilemap.tiles[y][x] = Tile(x, y, TileType.WALL, walkable=False)
    
    def _add_interactive_objects(self, tilemap: Tilemap, poi: PoiEntity):
        """Add interactive objects based on POI type"""
        if poi.poi_type == POIType.TEMPLE:
            tilemap.interactive_objects.append({
                "type": "altar", "x": tilemap.width // 2, "y": tilemap.height // 2,
                "interaction": "pray", "blessing_available": True
            })
        elif poi.poi_type == POIType.MINE:
            tilemap.interactive_objects.extend([
                {"type": "mining_cart", "x": 10, "y": 15, "contains": "ore"},
                {"type": "pickaxe_rack", "x": 8, "y": 12, "tools_available": True}
            ])
    
    def _initialize_room_templates(self) -> Dict[RoomType, Dict[str, Any]]:
        """Initialize room generation templates"""
        return {
            RoomType.ENTRANCE: {"min_size": (6, 6), "max_size": (10, 8)},
            RoomType.MAIN_HALL: {"min_size": (10, 10), "max_size": (20, 15)},
            RoomType.BEDROOM: {"min_size": (6, 6), "max_size": (8, 8)},
            RoomType.KITCHEN: {"min_size": (6, 8), "max_size": (10, 10)},
            RoomType.STORAGE: {"min_size": (4, 4), "max_size": (8, 6)},
            RoomType.SHOP: {"min_size": (8, 8), "max_size": (12, 10)},
            RoomType.TAVERN: {"min_size": (12, 10), "max_size": (20, 15)},
            RoomType.DUNGEON_CHAMBER: {"min_size": (8, 8), "max_size": (15, 12)}
        }


def get_tilemap_service(db_session: Optional[Session] = None) -> TilemapService:
    """Get tilemap service instance"""
    return TilemapService(db_session)
