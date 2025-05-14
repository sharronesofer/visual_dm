"""Initialize search indices and mappings."""

import logging
from typing import Optional

from .service import SearchService
from .entities import NPC, Item, Location, Quest
from .config import ES_SETTINGS, DEFAULT_MAPPINGS

logger = logging.getLogger(__name__)

def init_search(
    hosts: Optional[list[str]] = None,
    index_prefix: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> SearchService:
    """Initialize search service and create indices.
    
    Args:
        hosts: List of Elasticsearch hosts
        index_prefix: Prefix for index names
        username: Optional username for authentication
        password: Optional password for authentication
        
    Returns:
        Configured SearchService instance
    """
    logger.info("Initializing search service...")
    
    # Create search service instance
    service = SearchService(
        hosts=hosts or ES_SETTINGS['hosts'],
        index_prefix=index_prefix or ES_SETTINGS['index_prefix'],
        username=username,
        password=password
    )
    
    # Register entity types with their mappings
    entity_types = {
        'npc': NPC,
        'item': Item,
        'location': Location,
        'quest': Quest
    }
    
    for entity_type, entity_class in entity_types.items():
        logger.info(f"Registering entity type: {entity_type}")
        service.register_entity(
            entity_type=entity_type,
            entity_class=entity_class,
            mappings=DEFAULT_MAPPINGS[entity_type]
        )
    
    # Verify health
    health = service.health_check()
    logger.info(f"Elasticsearch cluster health: {health['status']}")
    
    return service 