"""
Faction integration service for the religion system.

This module provides services for integrating religions with factions,
handling synchronization, and managing cross-membership.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from .models import Religion, ReligionMembership

# Setup logging
logger = logging.getLogger(__name__)

# Try to import faction-related services if available
try:
    from backend.systems.faction import get_faction_service
    HAS_FACTION_SYSTEM = True
except ImportError:
    HAS_FACTION_SYSTEM = False
    logger.warning("Faction system not available, faction integration will be disabled")


class ReligionFactionService:
    """
    Service for handling religion-faction integration.
    
    Provides methods for syncing religions with factions, managing
    cross-membership, and handling faction-related events.
    """
    
    def __init__(self):
        """Initialize the faction integration service."""
        self.faction_service = None
        if HAS_FACTION_SYSTEM:
            self.faction_service = get_faction_service()
    
    def sync_with_faction(self, religion: Religion, faction_id: str) -> bool:
        """
        Associate a religion with a faction.
        
        Args:
            religion: Religion to associate
            faction_id: ID of the faction to associate with
        
        Returns:
            True if synced successfully, False otherwise
        """
        if not HAS_FACTION_SYSTEM or not self.faction_service:
            logger.warning("Cannot sync religion with faction: faction system not available")
            return False
        
        try:
            # Update the religion's faction ID
            religion.faction_id = faction_id
            
            # Get the faction for additional integration
            faction = self.faction_service.get_faction(faction_id)
            if not faction:
                logger.warning(f"Cannot sync religion with faction: faction {faction_id} not found")
                return False
            
            logger.info(f"Religion {religion.name} ({religion.id}) synced with faction {faction.name} ({faction_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing religion with faction: {str(e)}")
            return False
    
    def handle_membership_change(
        self, 
        entity_id: str, 
        religion: Religion, 
        action: str
    ) -> None:
        """
        Handle membership changes for faction integration.
        
        Args:
            entity_id: ID of the entity whose membership changed
            religion: Religion involved
            action: Action taken (joined, left, role_changed, etc.)
        """
        if not religion.faction_id or not HAS_FACTION_SYSTEM or not self.faction_service:
            return
        
        try:
            # If there's a linked faction, handle faction integration
            if action == "joined":
                # Check if the entity should automatically join the faction
                if religion.metadata.get("auto_faction_join", False):
                    logger.info(
                        f"Auto-joining entity {entity_id} to faction {religion.faction_id} "
                        f"due to religion membership"
                    )
                    self.faction_service.add_member(religion.faction_id, entity_id)
            
            elif action == "left":
                # Only handle faction leaving if configured
                if religion.metadata.get("auto_faction_leave", False):
                    logger.info(
                        f"Auto-removing entity {entity_id} from faction {religion.faction_id} "
                        f"due to leaving religion"
                    )
                    self.faction_service.remove_member(religion.faction_id, entity_id)
        
        except Exception as e:
            logger.error(f"Error handling religion-faction membership change: {str(e)}")


# Singleton instance
_faction_service_instance = None

def get_faction_service() -> ReligionFactionService:
    """Get the singleton instance of the ReligionFactionService."""
    global _faction_service_instance
    if _faction_service_instance is None:
        _faction_service_instance = ReligionFactionService()
    return _faction_service_instance 