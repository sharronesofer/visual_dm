"""
Frontend models for UI components and game state.
Originally located in app/frontend/frontend_models.py
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class UIPosition:
    """Represents a position in the UI."""
    x: int
    y: int
    z: int = 0

@dataclass
class UISize:
    """Represents the size of a UI element."""
    width: int
    height: int

@dataclass
class UIElement:
    """Base class for UI elements."""
    id: str
    position: UIPosition
    size: UISize
    visible: bool = True
    enabled: bool = True
    style: Dict = None

@dataclass
class Button(UIElement):
    """Represents a clickable button."""
    text: str
    action: str
    hover_text: Optional[str] = None

@dataclass
class Panel(UIElement):
    """Represents a container panel."""
    title: Optional[str] = None
    children: List[UIElement] = None

@dataclass
class CharacterCard(UIElement):
    """Represents a character display card."""
    character_id: str
    name: str
    level: int
    class_name: str
    race: str
    stats: Dict[str, int]
    portrait: Optional[str] = None

@dataclass
class QuestCard(UIElement):
    """Represents a quest display card."""
    quest_id: str
    title: str
    description: str
    status: str
    progress: Dict[str, int]
    rewards: Dict[str, int]

@dataclass
class NPCCard(UIElement):
    """Represents an NPC display card."""
    npc_id: str
    name: str
    role: str
    relationship: float
    portrait: Optional[str] = None

@dataclass
class InventorySlot(UIElement):
    """Represents an inventory slot."""
    slot_id: str
    item_id: Optional[str] = None
    quantity: int = 0
    item_type: Optional[str] = None

@dataclass
class CombatLog(UIElement):
    """Represents a combat log display."""
    entries: List[Dict[str, str]] = None
    max_entries: int = 100

@dataclass
class MapTile(UIElement):
    """Represents a map tile."""
    terrain_type: str
    elevation: int
    features: List[str] = None
    explored: bool = False

@dataclass
class DialogBox(UIElement):
    """Represents a dialog box."""
    speaker: str
    text: str
    options: List[Button] = None
    portrait: Optional[str] = None

@dataclass
class StatusBar(UIElement):
    """Represents a status bar."""
    current_value: int
    max_value: int
    label: str
    color: str = "green"

@dataclass
class Tooltip(UIElement):
    """Represents a tooltip."""
    text: str
    target_element: str
    position: str = "bottom"  # top, bottom, left, right

@dataclass
class Notification(UIElement):
    """Represents a notification."""
    message: str
    type: str  # info, warning, error, success
    duration: int = 3000  # milliseconds
    created_at: datetime = None 