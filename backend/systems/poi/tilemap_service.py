"""
Service for POI tilemap operations.
Provides functionality for generating, enriching, and rendering tilemaps.
"""

import random
import json
from typing import List, Dict, Any, Tuple

from .models import PointOfInterest, POIState, POIType

# Constants
SIZE_CLASS_RANGES = {
    "tiny": (4, 6),
    "small": (8, 12),
    "medium": (15, 25),
    "large": (30, 50)
}

# Approved object and monster pools
APPROVED_OBJECTS = {
    "altar", "brazier", "cracked statue", "bone pile", "lever", "sealed door",
    "blood smear", "old scroll", "broken weapon", "corpse", "trap plate", "sarcophagus"
}

APPROVED_MONSTERS = {
    "ghost", "cultist", "rat swarm", "echo priest", "revenant", "mimic"
}

class TilemapService:
    """
    Service for generating, enriching, and rendering POI tilemaps.
    
    Provides methods for creating tilemap structures, populating with objects/npcs,
    and rendering map data for client consumption.
    """
    
    @staticmethod
    def generate_tilemap(poi: PointOfInterest) -> List[Dict]:
        """
        Generate a tilemap structure for a POI.
        
        Args:
            poi: The POI to generate a tilemap for
            
        Returns:
            List of room dictionaries representing the tilemap
        """
        # Use metadata for seed if available, otherwise use POI ID
        seed_value = poi.metadata.get("map_seed", poi.id)
        random.seed(seed_value)
        
        # Determine size class based on POI type or metadata
        size_class = poi.metadata.get("size_class", "small")
        if size_class not in SIZE_CLASS_RANGES:
            # Default size class based on POI type
            size_class_by_type = {
                POIType.CITY: "large",
                POIType.TOWN: "medium",
                POIType.VILLAGE: "small",
                POIType.DUNGEON: "medium",
                POIType.RUINS: "medium",
                POIType.TEMPLE: "small",
                POIType.CASTLE: "medium",
                POIType.FORTRESS: "medium",
                POIType.TOWER: "small",
                POIType.CAVE: "medium",
            }
            size_class = size_class_by_type.get(poi.poi_type, "small")
        
        # Determine number of rooms based on size class
        num_rooms = {
            "tiny": random.randint(3, 5),
            "small": random.randint(6, 10),
            "medium": random.randint(10, 15),
            "large": random.randint(16, 25)
        }.get(size_class, 8)
        
        # Generate rooms
        rooms = []
        for i in range(num_rooms):
            room_id = f"R{i+1}"
            width = random.randint(4, 10)
            height = random.randint(4, 10)
            
            # Determine room type (plain/special) with 20% chance of special
            room_type = None
            if random.random() < 0.2:
                room_type = random.choice(["boss", "shrine", "treasure", "library", "prison"])
                
            room = {
                "id": room_id,
                "size": [width, height],
                "connections": [],
                "type": room_type
            }
            rooms.append(room)
        
        # Connect rooms (simple chain + some branches)
        for i in range(1, len(rooms)):
            prev = rooms[i - 1]
            curr = rooms[i]
            prev["connections"].append(curr["id"])
            curr["connections"].append(prev["id"])
            
            # Random extra connection
            if i > 1 and random.random() < 0.4:
                j = random.randint(0, i - 2)
                curr["connections"].append(rooms[j]["id"])
                rooms[j]["connections"].append(curr["id"])
        
        return rooms
    
    @staticmethod
    def enrich_tilemap(poi: PointOfInterest, rooms: List[Dict]) -> Dict[str, Any]:
        """
        Enrich a tilemap with objects, NPCs, and monsters.
        
        Args:
            poi: The POI the tilemap belongs to
            rooms: The room structure to enrich
            
        Returns:
            Dictionary with enrichment data for each room
        """
        # Build the enrichment data structure
        enrichment = {
            "theme": TilemapService._generate_theme(poi),
            "room_enrichment": {}
        }
        
        for room in rooms:
            room_id = room["id"]
            room_type = room.get("type")
            
            # Base quantities based on room size
            width, height = room["size"]
            room_area = width * height
            num_objects = max(1, random.randint(1, room_area // 16))
            num_monsters = max(1, random.randint(1, room_area // 25))
            
            # Adjust for room type
            if room_type == "boss":
                num_monsters = 1  # Just the boss
                num_objects = random.randint(2, 4)  # Some objects for the boss room
            elif room_type == "shrine":
                num_monsters = 0  # No monsters in shrine
                num_objects = random.randint(3, 5)  # Ritual objects
            elif room_type == "treasure":
                num_monsters = random.randint(2, 3)  # Guards
                num_objects = random.randint(3, 5)  # Treasure!
            elif room_type == "library":
                num_monsters = random.randint(0, 1)  # Maybe a guardian
                num_objects = random.randint(4, 6)  # Books and scrolls
            elif room_type == "prison":
                num_monsters = random.randint(1, 2)  # Guards
                num_objects = random.randint(2, 4)  # Cells and chains
            
            # Generate objects based on room type
            objects = TilemapService._generate_objects(num_objects, room_type)
            
            # Generate monsters based on room type
            monsters = TilemapService._generate_monsters(num_monsters, room_type, poi.level)
            
            # Add room to enrichment data
            enrichment["room_enrichment"][room_id] = {
                "objects": objects,
                "monsters": monsters,
                "note": TilemapService._generate_room_note(room_type)
            }
        
        return enrichment
    
    @staticmethod
    def _generate_theme(poi: PointOfInterest) -> str:
        """Generate a theme based on POI type and tags."""
        themes_by_type = {
            POIType.DUNGEON: ["dark", "haunted", "infested", "corrupted", "ancient"],
            POIType.RUINS: ["abandoned", "destroyed", "overgrown", "crumbling", "desolate"],
            POIType.TEMPLE: ["sacred", "forgotten", "blessed", "profaned", "celestial"],
            POIType.CAVE: ["damp", "crystalline", "fungal", "echoing", "labyrinthine"],
            POIType.FORTRESS: ["military", "strategic", "fortified", "defensive", "imposing"],
        }
        
        themes_by_tag = {
            "forest": ["overgrown", "verdant", "sylvan", "wild", "treebound"],
            "swamp": ["fetid", "diseased", "misty", "marshy", "rotten"],
            "mountain": ["steep", "rocky", "windswept", "elevated", "treacherous"],
            "desert": ["sandy", "scorching", "arid", "barren", "parched"],
            "undead": ["necromantic", "ghostly", "spectral", "deathly", "tomb-like"],
            "holy": ["divine", "blessed", "sacred", "hallowed", "purified"],
            "cursed": ["defiled", "corrupted", "tainted", "hexed", "doomed"],
        }
        
        # Choose from type themes first
        type_themes = themes_by_type.get(poi.poi_type, ["mysterious", "intriguing", "peculiar"])
        theme = random.choice(type_themes)
        
        # If POI has tags, consider tag themes
        if poi.tags:
            for tag in poi.tags:
                if tag in themes_by_tag:
                    # 50% chance to use a tag theme instead
                    if random.random() < 0.5:
                        theme = random.choice(themes_by_tag[tag])
                        break
        
        return theme
    
    @staticmethod
    def _generate_objects(num_objects: int, room_type: str = None) -> List[str]:
        """Generate a list of objects for a room."""
        objects = []
        
        # Special objects by room type
        special_objects = {
            "boss": ["throne", "altar", "ritual circle", "huge statue", "sacrificial pit"],
            "shrine": ["offering bowl", "prayer mat", "holy symbol", "incense burner", "blessed water"],
            "treasure": ["treasure chest", "gold pile", "jeweled crown", "ancient artifact", "gemstone"],
            "library": ["bookshelf", "scroll rack", "writing desk", "ancient tome", "magic codex"],
            "prison": ["chains", "cell door", "torture device", "iron cage", "prisoner remains"]
        }
        
        # Add at least one special object for special rooms
        if room_type and room_type in special_objects:
            objects.append(random.choice(special_objects[room_type]))
            num_objects -= 1  # One less generic object
        
        # Add generic objects
        approved_objects_list = list(APPROVED_OBJECTS)
        for _ in range(num_objects):
            if approved_objects_list:
                obj = random.choice(approved_objects_list)
                objects.append(obj)
                # Remove to avoid duplicates
                if obj in approved_objects_list:
                    approved_objects_list.remove(obj)
        
        return objects
    
    @staticmethod
    def _generate_monsters(num_monsters: int, room_type: str = None, poi_level: int = 1) -> List[str]:
        """Generate a list of monsters for a room."""
        monsters = []
        
        # Special monsters by room type
        special_monsters = {
            "boss": [f"level {poi_level + 2} boss", "ancient guardian", "corrupted warden", "elder entity"],
            "shrine": ["shrine keeper", "corrupted priest", "living idol", "summoned spirit"],
            "treasure": ["treasure guardian", "animated armor", "mimic", "greed spirit"],
            "library": ["tome keeper", "knowledge wraith", "animated book", "ink elemental"],
            "prison": ["jailer", "torturer", "escaped prisoner", "vengeful spirit"]
        }
        
        # Add special monster for special rooms
        if room_type and room_type in special_monsters and num_monsters > 0:
            monsters.append(random.choice(special_monsters[room_type]))
            num_monsters -= 1  # One less generic monster
        
        # Add generic monsters
        approved_monsters_list = list(APPROVED_MONSTERS)
        for _ in range(num_monsters):
            if approved_monsters_list:
                monster = random.choice(approved_monsters_list)
                monsters.append(monster)
                # Remove to avoid duplicates in same room
                if monster in approved_monsters_list:
                    approved_monsters_list.remove(monster)
        
        return monsters
    
    @staticmethod
    def _generate_room_note(room_type: str = None) -> str:
        """Generate a note for a room."""
        if not room_type:
            return "A simple room with stone walls."
            
        notes = {
            "boss": "An imposing chamber with signs of a powerful presence.",
            "shrine": "A place of ritual and worship, with sacred symbols adorning the walls.",
            "treasure": "Glints of gold and riches catch your eye in this secured chamber.",
            "library": "Shelves line the walls, filled with knowledge both mundane and arcane.",
            "prison": "The stench of suffering lingers in this place of confinement."
        }
        
        return notes.get(room_type, "A room with distinctive features.")
    
    @staticmethod
    def render_tilemap(rooms: List[Dict], enrichment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a tilemap with enrichment data for client consumption.
        
        Args:
            rooms: The room structure 
            enrichment: The enrichment data
            
        Returns:
            Dictionary with fully rendered tilemap
        """
        rendered = {
            "theme": enrichment.get("theme", "mysterious"),
            "rooms": {}
        }
        
        # Process each room
        for room in rooms:
            room_id = room["id"]
            width, height = room["size"]
            
            # Create grid for room
            grid = []
            for y in range(height):
                row = []
                for x in range(width):
                    cell = {
                        "x": x, 
                        "y": y,
                        "terrain": "floor",
                        "object": None,
                        "monster": None
                    }
                    row.append(cell)
                grid.append(row)
            
            # Place objects and monsters
            room_enrichment = enrichment.get("room_enrichment", {}).get(room_id, {})
            objects = room_enrichment.get("objects", [])
            monsters = room_enrichment.get("monsters", [])
            
            # Place objects
            for obj in objects:
                # Try to find a free spot
                for _ in range(10):  # Try 10 times
                    x = random.randint(0, width - 1)
                    y = random.randint(0, height - 1)
                    if not grid[y][x]["object"] and not grid[y][x]["monster"]:
                        grid[y][x]["object"] = obj
                        break
            
            # Place monsters
            for monster in monsters:
                # Try to find a free spot
                for _ in range(10):  # Try 10 times
                    x = random.randint(0, width - 1)
                    y = random.randint(0, height - 1)
                    if not grid[y][x]["object"] and not grid[y][x]["monster"]:
                        grid[y][x]["monster"] = monster
                        break
            
            # Add room to rendered result
            rendered["rooms"][room_id] = {
                "grid": grid,
                "size": room["size"],
                "connections": room["connections"],
                "type": room.get("type"),
                "note": room_enrichment.get("note", "")
            }
        
        return rendered 