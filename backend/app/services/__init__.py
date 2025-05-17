# Auto-generated during TypeScript to Python migration

"""Services module for the application."""

from .base_service import BaseService
from .service_factory import ServiceFactory
from .character_service import CharacterService
from .world_service import WorldService
from .campaign_service import CampaignService
from .map_service import MapService
from .npc_service import NPCService

# Register model-specific service classes with ServiceFactory
from ..models.character import Character
from ..models.world import World
from ..models.campaign import Campaign
from ..models.map import Map
from ..models.npc import NPC

# Register service classes with the factory for auto-creation
ServiceFactory.register_service(Character, CharacterService)
ServiceFactory.register_service(World, WorldService)
ServiceFactory.register_service(Campaign, CampaignService)
ServiceFactory.register_service(Map, MapService)
ServiceFactory.register_service(NPC, NPCService)

__all__ = [
    'BaseService',
    'ServiceFactory',
    'CharacterService',
    'WorldService',
    'CampaignService',
    'MapService',
    'NPCService',
]
