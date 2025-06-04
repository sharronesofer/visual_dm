"""
Tension System Game Integrations

Connects the tension system with other game systems to maximize gameplay impact:
- NPC behavior modifications based on tension levels
- Dynamic quest generation in high-tension areas
- Combat difficulty scaling with regional tension
- Economic effects on trade and prices
- Faction relationship impacts from tension
- Population migration and settlement patterns

This module follows integration patterns established in the NPC and economy systems.
"""

from .npc_integration import TensionNPCIntegration
from .quest_integration import TensionQuestIntegration  
from .combat_integration import TensionCombatIntegration
from .economy_integration import TensionEconomyIntegration
from .faction_integration import TensionFactionIntegration
from .population_integration import TensionPopulationIntegration
from .integration_manager import TensionIntegrationManager

__all__ = [
    'TensionNPCIntegration',
    'TensionQuestIntegration',
    'TensionCombatIntegration', 
    'TensionEconomyIntegration',
    'TensionFactionIntegration',
    'TensionPopulationIntegration',
    'TensionIntegrationManager'
] 