"""
Visual DM Backend Systems

This package contains all the core game domain systems for Visual DM.
Each system is organized in its own directory following the canonical structure.
Infrastructure concerns have been moved to backend.infrastructure.
"""

# Version information
__version__ = "1.0.0"

# Available game domain systems (canonical structure)
CANONICAL_SYSTEMS = [
    "arc", "character", "combat", "crafting", "dialogue", "diplomacy", 
    "economy", "equipment", "faction", "inventory", "llm", "loot", 
    "magic", "memory", "motif", "npc", "poi", "population", "quest", 
    "region", "religion", "rumor", "tension_war", "time", 
    "world_generation", "world_state", "world"
]

# New domain-specific packages
DOMAIN_PACKAGES = [
    "models", "schemas", "rules", "repositories"
]

# Package metadata
__all__ = CANONICAL_SYSTEMS + DOMAIN_PACKAGES

# Import core domain models for proper module resolution
try:
    from .models import (
        Character, Skill, NPC, PersonalityTrait,
        Quest, QuestStatus, ConditionType,
        Faction, FactionAlignment,
        Item, ItemType, ItemRarity,
        Location, LocationType,
        World, Season, WeatherCondition,
        MarketItem, TradeOffer, Transaction, PriceHistory
    )
except ImportError:
    pass

# Import domain schemas
try:
    from .schemas import WorldData, Event
except ImportError:
    pass

# Import game rules
try:
    from .rules import (
        balance_constants, load_data, get_default_data,
        calculate_ability_modifier, calculate_proficiency_bonus,
        calculate_hp_for_level, get_starting_equipment
    )
except ImportError:
    pass

# Import domain repositories - repositories are in infrastructure/repositories, not systems
# try:
#     from .repositories import MarketItemRepository, TradeOfferRepository, TransactionRepository, PriceHistoryRepository
# except ImportError:
#     pass

# Import core systems for proper module resolution
try:
    # Temporarily disabled due to import chain issues - needs fixing
    # from . import motif
    pass
except ImportError:
    motif = None

# Temporarily disabled to avoid circular import issues during Task 26 fixes
# from backend.systems.__init__.py.events import (
#     # Re-export core event system
#     EventBase, EventDispatcher, 
#     
#     # Re-export event types
#     SystemEvent, SystemEventType,
#     MemoryEvent, MemoryEventType,
#     RumorEvent, RumorEventType,
#     MotifEvent, MotifEventType,
#     PopulationEvent, PopulationEventType,
#     FactionEvent, FactionEventType,
#     QuestEvent, QuestEventType,
#     CombatEvent, CombatEventType,
#     
#     # Re-export utilities
#     EventManager,
#     
#     # Re-export middleware
#     logging_middleware,
#     error_handling_middleware,
#     analytics_middleware
# )

# Import other systems as needed
# from backend.systems.__init__.py.memory import MemorySystem
# from backend.systems.__init__.py.rumors import RumorSystem
# from backend.systems.__init__.py.motifs import MotifSystem 