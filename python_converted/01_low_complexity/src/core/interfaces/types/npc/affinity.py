from typing import Any
from enum import Enum



class RelationshipType(Enum):
    STRANGER = 'stranger'
    ACQUAINTANCE = 'acquaintance'
    FRIEND = 'friend'
    CLOSE_FRIEND = 'close_friend'
    RIVAL = 'rival'
    ENEMY = 'enemy'
class NPCAffinity:
    npcId1: str
    npcId2: str
    score: float
    lastInteraction: Date
    interactionCount: float
    relationship: \'RelationshipType\' 