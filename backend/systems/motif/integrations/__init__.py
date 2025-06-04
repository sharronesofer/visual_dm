"""
Motif System Integrations

This module provides deep integration connectors between the motif system
and other game systems as specified in the Development Bible.
"""

# System integrations
from .ai_integration import MotifAIConnector
from .npc_integration import MotifNPCConnector  
from .event_integration import MotifEventConnector
from .quest_integration import MotifQuestConnector
from .faction_integration import MotifFactionConnector

__all__ = [
    'MotifAIConnector',
    'MotifNPCConnector', 
    'MotifEventConnector',
    'MotifQuestConnector',
    'MotifFactionConnector'
] 