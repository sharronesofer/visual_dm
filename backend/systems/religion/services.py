"""
Main service layer for the religion system.

This module provides the main ReligionService which integrates all the
specialized services and exposes a unified interface for the religion system.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .models import Religion, ReligionType, ReligionMembership
from .repository import ReligionRepository
from .membership_service import ReligionMembershipService
from .narrative_service import get_narrative_service
from .faction_service import get_faction_service
from .utils import calculate_religion_compatibility, calculate_schism_probability

# Setup logging
logger = logging.getLogger(__name__)

# Singleton instance
_religion_service_instance = None


class ReligionService:
    """
    Main service for the religion system.
    
    Integrates all the specialized services and provides a unified
    interface for working with religions and memberships.
    """
    
    def __init__(self, storage_dir: str = "data/religion"):
        """
        Initialize the religion service.
        
        Args:
            storage_dir: Directory for storing religion data
        """
        self.repository = ReligionRepository(storage_dir)
        self.membership_service = ReligionMembershipService(self.repository)
        self.narrative_service = get_narrative_service()
        self.faction_service = get_faction_service()
    
    # Religion operations
    
    def create_religion(self, religion_data: Dict[str, Any]) -> Religion:
        """
        Create a new religion.
        
        Args:
            religion_data: Dict containing religion data
            
        Returns:
            The created Religion object
        """
        religion = Religion(**religion_data)
        return self.repository.create_religion(religion)
    
    def get_religion(self, religion_id: str) -> Optional[Religion]:
        """
        Get a religion by ID.
        
        Args:
            religion_id: The ID of the religion to retrieve
            
        Returns:
            The Religion object, or None if not found
        """
        return self.repository.get_religion(religion_id)
    
    def get_religions(
        self, 
        region_id: Optional[str] = None,
        faction_id: Optional[str] = None,
        religion_type: Optional[ReligionType] = None
    ) -> List[Religion]:
        """
        Get religions, optionally filtered.
        
        Args:
            region_id: Optional region ID filter
            faction_id: Optional faction ID filter
            religion_type: Optional religion type filter
            
        Returns:
            List of Religion objects matching filters
        """
        religions = self.repository.get_all_religions()
        
        # Apply filters
        if region_id:
            religions = [r for r in religions if region_id in r.region_ids]
        
        if faction_id:
            religions = [r for r in religions if r.faction_id == faction_id]
        
        if religion_type:
            religions = [r for r in religions if r.type == religion_type]
        
        return religions
    
    def update_religion(self, religion_id: str, update_data: Dict[str, Any]) -> Optional[Religion]:
        """
        Update an existing religion.
        
        Args:
            religion_id: ID of the religion to update
            update_data: Dict containing fields to update
            
        Returns:
            The updated Religion object, or None if not found
        """
        religion = self.repository.get_religion(religion_id)
        if not religion:
            return None
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(religion, key) and value is not None:
                setattr(religion, key, value)
        
        # Update timestamp
        religion.updated_at = datetime.utcnow()
        
        return self.repository.update_religion(religion)
    
    def delete_religion(self, religion_id: str) -> bool:
        """
        Delete a religion by ID.
        
        Args:
            religion_id: ID of the religion to delete
            
        Returns:
            True if deleted, False if not found
        """
        if not self.repository.get_religion(religion_id):
            return False
        
        # Delete memberships first
        self.repository.delete_memberships_by_religion(religion_id)
        
        # Then delete the religion
        return self.repository.delete_religion(religion_id)
    
    # Membership operations - delegate to membership service
    
    def create_membership(self, membership_data: Dict[str, Any]) -> ReligionMembership:
        """
        Create a new religion membership.
        
        Args:
            membership_data: Dict containing membership data
            
        Returns:
            The created ReligionMembership object
        """
        return self.membership_service.create_membership(membership_data)
    
    def get_membership(self, membership_id: str) -> Optional[ReligionMembership]:
        """
        Get a membership by ID.
        
        Args:
            membership_id: The ID of the membership to retrieve
            
        Returns:
            The ReligionMembership object, or None if not found
        """
        return self.membership_service.get_membership(membership_id)
    
    def get_entity_memberships(self, entity_id: str) -> List[ReligionMembership]:
        """
        Get all religion memberships for an entity.
        
        Args:
            entity_id: The entity ID to get memberships for
            
        Returns:
            List of ReligionMembership objects for the entity
        """
        return self.membership_service.get_entity_memberships(entity_id)
    
    def get_religion_members(self, religion_id: str) -> List[ReligionMembership]:
        """
        Get all members of a religion.
        
        Args:
            religion_id: The religion ID to get members for
            
        Returns:
            List of ReligionMembership objects for the religion
        """
        return self.membership_service.get_religion_members(religion_id)
    
    def update_membership(
        self, 
        membership_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[ReligionMembership]:
        """
        Update an existing membership.
        
        Args:
            membership_id: ID of the membership to update
            update_data: Dict containing fields to update
            
        Returns:
            The updated ReligionMembership object, or None if not found
        """
        return self.membership_service.update_membership(membership_id, update_data)
    
    def update_devotion(
        self, 
        entity_id: str, 
        religion_id: str, 
        change: int,
        factors: Optional[Dict[str, float]] = None
    ) -> Optional[ReligionMembership]:
        """
        Update devotion level for an entity's membership.
        
        Args:
            entity_id: ID of the entity
            religion_id: ID of the religion
            change: Base amount of devotion change
            factors: Optional factors influencing change
            
        Returns:
            The updated ReligionMembership, or None if not found
        """
        return self.membership_service.update_devotion(
            entity_id, religion_id, change, factors
        )
    
    def delete_membership(self, membership_id: str) -> bool:
        """
        Delete a membership by ID.
        
        Args:
            membership_id: ID of the membership to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.membership_service.delete_membership(membership_id)
    
    # Integration operations
    
    def sync_with_faction(self, faction_id: str, religion_id: str) -> bool:
        """
        Associate a religion with a faction.
        
        Args:
            faction_id: ID of the faction
            religion_id: ID of the religion
            
        Returns:
            True if successful, False otherwise
        """
        religion = self.repository.get_religion(religion_id)
        if not religion:
            logger.warning(f"Cannot sync with faction: religion {religion_id} not found")
            return False
        
        success = self.faction_service.sync_with_faction(religion, faction_id)
        if success:
            # Update the religion object with the faction ID
            religion.faction_id = faction_id
            self.repository.update_religion(religion)
        
        return success
    
    def trigger_narrative_hook(
        self, 
        entity_id: str, 
        religion_id: str, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> None:
        """
        Trigger a narrative event for a religion.
        
        Args:
            entity_id: ID of the entity involved
            religion_id: ID of the religion
            event_type: Type of event
            event_data: Additional data for the event
        """
        religion = self.repository.get_religion(religion_id)
        if not religion:
            logger.warning(f"Cannot trigger narrative hook: religion {religion_id} not found")
            return
        
        self.narrative_service.trigger_narrative_hook(
            entity_id, religion, event_type, event_data
        )
    
    # Analytics and helper methods
    
    def get_religion_summary(self, religion_id: str) -> Dict[str, Any]:
        """
        Get a rich summary of a religion for narrative context.
        
        Args:
            religion_id: ID of the religion
            
        Returns:
            Dict with religion summary data, or empty dict if not found
        """
        religion = self.repository.get_religion(religion_id)
        if not religion:
            return {}
        
        return self.narrative_service.get_religion_summary(religion)
    
    def calculate_compatibility(self, religion_id1: str, religion_id2: str) -> float:
        """
        Calculate compatibility between two religions.
        
        Args:
            religion_id1: ID of first religion
            religion_id2: ID of second religion
            
        Returns:
            Compatibility score (0.0 to 1.0), or 0.0 if not found
        """
        religion1 = self.repository.get_religion(religion_id1)
        religion2 = self.repository.get_religion(religion_id2)
        
        if not religion1 or not religion2:
            return 0.0
        
        return calculate_religion_compatibility(religion1, religion2)
    
    def calculate_schism_probability(
        self, 
        religion_id: str,
        factors: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate probability of a schism in a religion.
        
        Args:
            religion_id: ID of the religion
            factors: Optional factors influencing schism
            
        Returns:
            Probability of schism (0.0 to 1.0), or 0.0 if not found
        """
        religion = self.repository.get_religion(religion_id)
        if not religion:
            return 0.0
        
        devotees = self.repository.get_memberships_by_religion(religion_id)
        
        if factors is None:
            factors = {}
        
        return calculate_schism_probability(religion, devotees, factors)


def get_religion_service(storage_dir: str = "data/religion") -> ReligionService:
    """
    Get the singleton instance of the ReligionService.
    
    Args:
        storage_dir: Optional custom storage directory
        
    Returns:
        Singleton ReligionService instance
    """
    global _religion_service_instance
    if _religion_service_instance is None:
        _religion_service_instance = ReligionService(storage_dir)
    return _religion_service_instance 