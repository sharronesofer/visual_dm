"""NPC Events

Event publishing infrastructure for NPC system operations.
"""

from .event_publisher import get_npc_event_publisher
from .events import (
    NPCCreated, NPCUpdated, NPCDeleted, NPCStatusChanged,
    NPCMoved, NPCMemoryCreated, NPCFactionJoined,
    NPCRumorLearned, NPCMotifApplied, NPCError
)

__all__ = [
    'get_npc_event_publisher',
    'NPCCreated', 'NPCUpdated', 'NPCDeleted', 'NPCStatusChanged',
    'NPCMoved', 'NPCMemoryCreated', 'NPCFactionJoined',
    'NPCRumorLearned', 'NPCMotifApplied', 'NPCError'
]
