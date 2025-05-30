from typing import Any
from enum import Enum


class EntityType(Enum):
    NPC = 'npc'
    ITEM = 'item'
    LOCATION = 'location'
    QUEST = 'quest'
    FACTION = 'faction' 