"""
Membership service for the religion system.

This module provides services for managing religion memberships,
including devotion changes, status updates, and role management.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from .models import Religion, ReligionMembership
from .utils import calculate_devotion_change
from .repository import ReligionRepository
from .faction_service import get_faction_service
from .narrative_service import get_narrative_service

# Setup logging
logger = logging.getLogger(__name__)


class ReligionMembershipService:
    """
    Service for managing religion memberships.
    
    Provides methods for creating, updating, and deleting memberships,
    as well as managing devotion levels and member roles.
    """
    
    def __init__(self, repository: ReligionRepository):
        """
        Initialize the membership service.
        
        Args:
            repository: Repository for data access
        """
        self.repository = repository
        self.narrative_service = get_narrative_service()
        self.faction_service = get_faction_service()
    
    def create_membership(self, membership_data: Dict[str, Any]) -> ReligionMembership:
        """
        Create a new religion membership.
        
        Args:
            membership_data: Dict containing membership data
            
        Returns:
            The created ReligionMembership object
        """
        # Create the membership object
        membership = ReligionMembership(**membership_data)
        
        # Get the religion for integration hooks
        religion = self.repository.get_religion(membership.religion_id)
        if not religion:
            logger.warning(
                f"Creating membership for unknown religion: {membership.religion_id}"
            )
        else:
            # Handle faction integration
            self.faction_service.handle_membership_change(
                membership.entity_id, 
                religion, 
                "joined"
            )
            
            # Trigger narrative hook
            self.narrative_service.trigger_narrative_hook(
                membership.entity_id,
                religion,
                "joined",
                {
                    "status": membership.status,
                    "devotion_level": membership.devotion_level,
                    "is_public": membership.is_public
                }
            )
        
        # Save to repository
        return self.repository.create_membership(membership)
    
    def get_membership(self, membership_id: str) -> Optional[ReligionMembership]:
        """
        Get a membership by ID.
        
        Args:
            membership_id: The ID of the membership to retrieve
            
        Returns:
            The ReligionMembership object, or None if not found
        """
        return self.repository.get_membership(membership_id)
    
    def get_entity_memberships(self, entity_id: str) -> List[ReligionMembership]:
        """
        Get all religion memberships for an entity.
        
        Args:
            entity_id: The entity ID to get memberships for
            
        Returns:
            List of ReligionMembership objects for the entity
        """
        return self.repository.get_memberships_by_entity(entity_id)
    
    def get_religion_members(self, religion_id: str) -> List[ReligionMembership]:
        """
        Get all members of a religion.
        
        Args:
            religion_id: The religion ID to get members for
            
        Returns:
            List of ReligionMembership objects for the religion
        """
        return self.repository.get_memberships_by_religion(religion_id)
    
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
        membership = self.repository.get_membership(membership_id)
        if not membership:
            return None
        
        # Store old values for comparison
        old_status = membership.status
        old_role = membership.role
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(membership, key) and value is not None:
                setattr(membership, key, value)
        
        # Get the religion for integration hooks
        religion = self.repository.get_religion(membership.religion_id)
        if religion:
            # Check if status or role changed
            if old_status != membership.status or old_role != membership.role:
                # Trigger narrative hook
                self.narrative_service.trigger_narrative_hook(
                    membership.entity_id,
                    religion,
                    "role_changed",
                    {
                        "old_status": old_status,
                        "new_status": membership.status,
                        "old_role": old_role,
                        "new_role": membership.role
                    }
                )
        
        # Save to repository
        return self.repository.update_membership(membership)
    
    def update_devotion(
        self, 
        entity_id: str, 
        religion_id: str, 
        change: int,
        factors: Optional[Dict[str, float]] = None
    ) -> Optional[ReligionMembership]:
        """
        Update the devotion level for an entity's membership in a religion.
        
        Args:
            entity_id: ID of the entity
            religion_id: ID of the religion
            change: Base amount of devotion change (positive or negative)
            factors: Optional factors influencing devotion change
            
        Returns:
            The updated ReligionMembership object, or None if not found
        """
        # Find the membership
        memberships = self.repository.get_memberships_by_entity(entity_id)
        membership = next((m for m in memberships if m.religion_id == religion_id), None)
        if not membership:
            logger.warning(
                f"Cannot update devotion: membership not found for entity {entity_id} "
                f"and religion {religion_id}"
            )
            return None
        
        # Apply factors to calculate actual change
        if factors is None:
            factors = {}
        
        actual_change = calculate_devotion_change(change, factors)
        
        # Update devotion level, clamping between 0 and 100
        old_devotion = membership.devotion_level
        membership.devotion_level = max(0, min(100, membership.devotion_level + actual_change))
        
        # Get the religion for narrative hooks
        religion = self.repository.get_religion(religion_id)
        if religion:
            # Determine the type of devotion change
            if old_devotion < membership.devotion_level:
                event_type = "devotion_increased"
            else:
                event_type = "devotion_decreased"
            
            # Trigger narrative hook
            self.narrative_service.trigger_narrative_hook(
                entity_id,
                religion,
                event_type,
                {
                    "old_devotion": old_devotion,
                    "new_devotion": membership.devotion_level,
                    "change": actual_change,
                    "factors": factors
                }
            )
        
        # Save to repository
        return self.repository.update_membership(membership)
    
    def delete_membership(self, membership_id: str) -> bool:
        """
        Delete a membership by ID.
        
        Args:
            membership_id: ID of the membership to delete
            
        Returns:
            True if deleted, False if not found
        """
        membership = self.repository.get_membership(membership_id)
        if not membership:
            return False
        
        # Get the religion for integration hooks
        religion = self.repository.get_religion(membership.religion_id)
        if religion:
            # Handle faction integration
            self.faction_service.handle_membership_change(
                membership.entity_id, 
                religion, 
                "left"
            )
            
            # Trigger narrative hook
            self.narrative_service.trigger_narrative_hook(
                membership.entity_id,
                religion,
                "left",
                {
                    "status": membership.status,
                    "devotion_level": membership.devotion_level
                }
            )
        
        # Delete from repository
        return self.repository.delete_membership(membership_id) 