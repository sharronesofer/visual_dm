from enum import Enum, auto

class EventType(Enum):
    COMBAT = auto()
    WORLD = auto()
    NPC = auto()
    QUEST = auto()
    # Add subtypes as needed, e.g., COMBAT_TURN, WORLD_WEATHER, etc. 