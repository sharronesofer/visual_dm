"""
Service layer for managing faction memberships.

This module provides the FactionMembershipService class for creating, retrieving,
and managing character/NPC memberships in factions with business logic only.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from backend.systems.faction.models.faction import FactionMembership
from backend.infrastructure.faction_services import (
    FactionMembershipDatabaseService,
    MembershipNotFoundError,
    InvalidMembershipError
)


class FactionMembershipService:
    """Service for managing character memberships in factions with business logic."""
    
    def __init__(self, database_service: FactionMembershipDatabaseService):
        self.db_service = database_service

    def add_member(
        self,
        faction_id: int,
        character_id: int,
        role: str = "member",
        rank: int = 1,
        join_reason: str = None,
        metadata: Dict[str, Any] = None
    ) -> FactionMembership:
        """
        Add a character to a faction with business rules validation.
        
        Args:
            faction_id: ID of the faction
            character_id: ID of the character to add
            role: Role within faction (e.g., "leader", "member", "recruit")
            rank: Numeric rank within faction hierarchy (higher = more important)
            join_reason: Reason for joining (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            FactionMembership instance
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        # Validate business rules
        if rank < 1 or rank > 100:
            raise InvalidMembershipError("Rank must be between 1 and 100")
        
        if role not in ["leader", "officer", "member", "recruit", "exile"]:
            raise InvalidMembershipError(f"Invalid role: {role}")
        
        # Check if faction exists
        faction = self.db_service.get_faction_by_id(faction_id)
        if not faction:
            raise MembershipNotFoundError(f"Faction {faction_id} not found")
            
        # Check if membership already exists
        existing = self.db_service.get_membership(faction_id, character_id)
        
        if existing:
            # Business logic: Update existing membership
            existing.active = True
            existing.role = role
            existing.rank = rank
            
            # Add rejoining event to history
            event = {
                "type": "rejoined",
                "timestamp": datetime.utcnow().isoformat(),
                "role": role,
                "rank": rank
            }
            
            if join_reason:
                event["reason"] = join_reason
                
            existing.history.append(event)
            
            # Update metadata if provided
            if metadata:
                if not existing.metadata:
                    existing.metadata = {}
                existing.metadata.update(metadata)
            
            membership = existing
        else:
            # Business logic: Create new membership
            history = [{
                "type": "joined",
                "timestamp": datetime.utcnow().isoformat(),
                "role": role,
                "rank": rank
            }]
            
            if join_reason:
                history[0]["reason"] = join_reason
                
            membership = FactionMembership(
                faction_id=faction_id,
                character_id=character_id,
                active=True,
                role=role,
                rank=rank,
                joined_at=datetime.utcnow(),
                history=history,
                metadata=metadata or {}
            )
        
        # Delegate to database service
        return self.db_service.create_membership(membership) if not existing else self.db_service.update_membership(membership)

    def get_membership(
        self,
        faction_id: int,
        character_id: int
    ) -> Optional[FactionMembership]:
        """Get membership information for a character in a faction"""
        return self.db_service.get_membership(faction_id, character_id)

    def get_faction_members(
        self,
        faction_id: int,
        active_only: bool = True,
        role: Optional[str] = None,
        min_rank: Optional[int] = None
    ) -> List[FactionMembership]:
        """
        Get all members of a faction with optional filters and business rules.
        
        Args:
            faction_id: ID of the faction
            active_only: Only include active memberships (default: True)
            role: Filter by specific role (optional)
            min_rank: Filter by minimum rank (optional)
            
        Returns:
            List of FactionMembership instances matching filters
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        # Check if faction exists (business rule)
        faction = self.db_service.get_faction_by_id(faction_id)
        if not faction:
            raise MembershipNotFoundError(f"Faction {faction_id} not found")
        
        return self.db_service.get_faction_members(faction_id, active_only, role, min_rank)

    def get_character_factions(
        self,
        character_id: int,
        active_only: bool = True
    ) -> List[Dict]:
        """Get all factions a character is a member of"""
        return self.db_service.get_character_factions(character_id, active_only)

    def update_membership(
        self,
        faction_id: int,
        character_id: int,
        role: Optional[str] = None,
        rank: Optional[int] = None,
        active: Optional[bool] = None,
        metadata: Optional[Dict] = None,
        reason: Optional[str] = None
    ) -> FactionMembership:
        """
        Update membership with business rules validation.
        
        Args:
            faction_id: ID of the faction
            character_id: ID of the character
            role: New role (optional)
            rank: New rank (optional)
            active: New active status (optional) 
            metadata: Metadata to merge (optional)
            reason: Reason for the change (optional)
            
        Returns:
            Updated FactionMembership instance
            
        Raises:
            MembershipNotFoundError: If membership doesn't exist
        """
        membership = self.db_service.get_membership(faction_id, character_id)
        if not membership:
            raise MembershipNotFoundError(f"Membership not found for character {character_id} in faction {faction_id}")
        
        # Business rules validation
        if rank is not None and (rank < 1 or rank > 100):
            raise InvalidMembershipError("Rank must be between 1 and 100")
        
        if role is not None and role not in ["leader", "officer", "member", "recruit", "exile"]:
            raise InvalidMembershipError(f"Invalid role: {role}")
        
        # Track changes for history
        changes = {}
        if role is not None and role != membership.role:
            changes["role"] = {"from": membership.role, "to": role}
            membership.role = role
            
        if rank is not None and rank != membership.rank:
            changes["rank"] = {"from": membership.rank, "to": rank}
            membership.rank = rank
            
        if active is not None and active != membership.active:
            changes["active"] = {"from": membership.active, "to": active}
            membership.active = active
        
        # Update metadata with business logic
        if metadata:
            if not membership.metadata:
                membership.metadata = {}
            membership.metadata.update(metadata)
        
        # Add history entry if there were changes
        if changes:
            history_entry = {
                "type": "updated",
                "timestamp": datetime.utcnow().isoformat(),
                "changes": changes
            }
            
            if reason:
                history_entry["reason"] = reason
                
            membership.history.append(history_entry)
        
        return self.db_service.update_membership(membership)

    def remove_member(
        self,
        faction_id: int,
        character_id: int,
        reason: str = None,
        permanent: bool = False
    ) -> None:
        """
        Remove a character from a faction.
        
        Args:
            faction_id: ID of the faction
            character_id: ID of the character to remove
            reason: Reason for removal (optional)
            permanent: Whether to permanently delete (True) or deactivate (False)
        """
        membership = self.db_service.get_membership(faction_id, character_id)
        if not membership:
            raise MembershipNotFoundError(f"Membership not found for character {character_id} in faction {faction_id}")
        
        if permanent:
            # Business rule: Permanent deletion
            self.db_service.delete_membership(membership)
        else:
            # Business rule: Soft deletion
            membership.active = False
            
            # Add history entry
            history_entry = {
                "type": "removed",
                "timestamp": datetime.utcnow().isoformat(),
                "active": False
            }
            
            if reason:
                history_entry["reason"] = reason
                
            membership.history.append(history_entry)
            
            self.db_service.update_membership(membership)

    def transfer_leader(
        self,
        faction_id: int,
        new_leader_id: int,
        reason: str = None
    ) -> Dict:
        """
        Transfer faction leadership with business rules.
        
        Args:
            faction_id: ID of the faction
            new_leader_id: ID of the character to become new leader
            reason: Reason for transfer (optional)
            
        Returns:
            Dict with transfer results
        """
        # Business rule: Validate new leader exists and is a member
        new_leader_membership = self.db_service.get_membership(faction_id, new_leader_id)
        if not new_leader_membership or not new_leader_membership.active:
            raise InvalidMembershipError(f"Character {new_leader_id} is not an active member of faction {faction_id}")
        
        # Business rule: Find current leader
        current_leaders = self.db_service.get_faction_members(faction_id, active_only=True, role="leader")
        
        results = {
            "old_leader": None,
            "new_leader": new_leader_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Step down current leader(s)
        for leader in current_leaders:
            leader.role = "officer"  # Business rule: demote to officer
            leader.rank = max(leader.rank - 10, 1)  # Business rule: reduce rank
            
            # Add history
            history_entry = {
                "type": "demoted",
                "timestamp": datetime.utcnow().isoformat(),
                "from_role": "leader",
                "to_role": "officer",
                "reason": reason or "Leadership transfer"
            }
            leader.history.append(history_entry)
            
            self.db_service.update_membership(leader)
            results["old_leader"] = leader.character_id
        
        # Promote new leader
        new_leader_membership.role = "leader"
        new_leader_membership.rank = 100  # Business rule: leaders get max rank
        
        # Add history
        history_entry = {
            "type": "promoted",
            "timestamp": datetime.utcnow().isoformat(),
            "to_role": "leader",
            "reason": reason or "Leadership transfer"
        }
        new_leader_membership.history.append(history_entry)
        
        self.db_service.update_membership(new_leader_membership)
        
        return results

    def switch_faction_by_affinity(
        self,
        character_id: int,
        current_faction_id: int,
        target_faction_id: int,
        affinity_score: Optional[int] = None,
        min_affinity_threshold: int = 60,
        contextual_restrictions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Switch faction membership based on affinity and business rules.
        
        Args:
            character_id: ID of the character
            current_faction_id: Current faction ID
            target_faction_id: Target faction ID
            affinity_score: Character's affinity to target faction
            min_affinity_threshold: Minimum affinity required
            contextual_restrictions: Additional business rule restrictions
            
        Returns:
            Dict with switch results
        """
        # Business rules validation
        if affinity_score is not None and affinity_score < min_affinity_threshold:
            return {
                "success": False,
                "reason": f"Affinity score {affinity_score} below threshold {min_affinity_threshold}"
            }
        
        # Check current membership
        current_membership = self.db_service.get_membership(current_faction_id, character_id)
        if not current_membership:
            return {
                "success": False,
                "reason": f"Character not a member of faction {current_faction_id}"
            }
        
        # Business rule: Leaders cannot easily switch factions
        if current_membership.role == "leader":
            return {
                "success": False,
                "reason": "Leaders cannot switch factions without transferring leadership first"
            }
        
        # Check target faction exists
        target_faction = self.db_service.get_faction_by_id(target_faction_id)
        if not target_faction:
            return {
                "success": False,
                "reason": f"Target faction {target_faction_id} not found"
            }
        
        try:
            # Remove from current faction
            self.remove_member(
                current_faction_id, 
                character_id, 
                reason=f"Switched to faction {target_faction_id}"
            )
            
            # Add to target faction
            new_membership = self.add_member(
                target_faction_id,
                character_id,
                role="recruit",  # Business rule: start as recruit
                rank=1,  # Business rule: start with lowest rank
                join_reason=f"Switched from faction {current_faction_id}",
                metadata={"previous_faction": current_faction_id, "affinity_score": affinity_score}
            )
            
            return {
                "success": True,
                "old_faction": current_faction_id,
                "new_faction": target_faction_id,
                "new_membership": new_membership,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Rollback on error
            self.db_service.rollback_changes()
            return {
                "success": False,
                "reason": f"Switch failed: {str(e)}"
            } 