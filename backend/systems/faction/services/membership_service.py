"""
Service layer for managing faction memberships.

This module provides the FactionMembershipService class for creating, retrieving,
and managing character/NPC memberships in factions.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from backend.systems.faction.models.faction import Faction, FactionMembership
from backend.systems.faction.services.faction_service import FactionNotFoundError

class MembershipNotFoundError(Exception):
    """Raised when a membership cannot be found."""

class InvalidMembershipError(Exception):
    """Raised when an invalid membership operation is attempted."""

class FactionMembershipService:
    """Service for managing character memberships in factions."""
    
    @staticmethod
    def add_member(
        db: Session,
        faction_id: int,
        character_id: int,
        role: str = "member",
        rank: int = 1,
        join_reason: str = None,
        metadata: Dict[str, Any] = None
    ) -> FactionMembership:
        """
        Add a character to a faction.
        
        Args:
            db: Database session
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
        # Check if faction exists
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        # Check if membership already exists
        existing = db.query(FactionMembership).filter(
            FactionMembership.faction_id == faction_id,
            FactionMembership.character_id == character_id
        ).first()
        
        if existing:
            # Update existing membership
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
            # Create new membership
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
            db.add(membership)
            
        db.commit()
        db.refresh(membership)
        return membership
    
    @staticmethod
    def get_membership(
        db: Session,
        faction_id: int,
        character_id: int
    ) -> Optional[FactionMembership]:
        """
        Get membership information for a character in a faction.
        
        Args:
            db: Database session
            faction_id: ID of the faction
            character_id: ID of the character
            
        Returns:
            FactionMembership instance or None if not found
        """
        return db.query(FactionMembership).filter(
            FactionMembership.faction_id == faction_id,
            FactionMembership.character_id == character_id
        ).first()
    
    @staticmethod
    def get_faction_members(
        db: Session,
        faction_id: int,
        active_only: bool = True,
        role: Optional[str] = None,
        min_rank: Optional[int] = None
    ) -> List[FactionMembership]:
        """
        Get all members of a faction with optional filters.
        
        Args:
            db: Database session
            faction_id: ID of the faction
            active_only: Only include active memberships (default: True)
            role: Filter by specific role (optional)
            min_rank: Filter by minimum rank (optional)
            
        Returns:
            List of FactionMembership instances matching filters
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        # Check if faction exists
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
        
        # Build query
        query = db.query(FactionMembership).filter(
            FactionMembership.faction_id == faction_id
        )
        
        if active_only:
            query = query.filter(FactionMembership.active == True)
            
        if role:
            query = query.filter(FactionMembership.role == role)
            
        if min_rank is not None:
            query = query.filter(FactionMembership.rank >= min_rank)
            
        # Order by rank (highest first) and then join date
        return query.order_by(
            FactionMembership.rank.desc(),
            FactionMembership.joined_at
        ).all()
    
    @staticmethod
    def get_character_factions(
        db: Session,
        character_id: int,
        active_only: bool = True
    ) -> List[Dict]:
        """
        Get all factions a character is a member of.
        
        Args:
            db: Database session
            character_id: ID of the character
            active_only: Only include active memberships (default: True)
            
        Returns:
            List of dicts with faction and membership details
        """
        query = db.query(
            FactionMembership, Faction
        ).join(
            Faction, Faction.id == FactionMembership.faction_id
        ).filter(
            FactionMembership.character_id == character_id
        )
        
        if active_only:
            query = query.filter(FactionMembership.active == True)
            
        results = []
        for membership, faction in query.all():
            results.append({
                "faction_id": faction.id,
                "faction_name": faction.name,
                "faction_type": faction.type,
                "role": membership.role,
                "rank": membership.rank,
                "joined_at": membership.joined_at.isoformat() if membership.joined_at else None,
                "active": membership.active
            })
            
        return results
    
    @staticmethod
    def update_membership(
        db: Session,
        faction_id: int,
        character_id: int,
        role: Optional[str] = None,
        rank: Optional[int] = None,
        active: Optional[bool] = None,
        metadata: Optional[Dict] = None,
        reason: Optional[str] = None
    ) -> FactionMembership:
        """
        Update a faction membership.
        
        Args:
            db: Database session
            faction_id: ID of the faction
            character_id: ID of the character
            role: New role (optional)
            rank: New rank (optional)
            active: Update active status (optional)
            metadata: Additional metadata to merge (optional)
            reason: Reason for the update (optional)
            
        Returns:
            Updated FactionMembership instance
            
        Raises:
            MembershipNotFoundError: If membership doesn't exist
        """
        membership = db.query(FactionMembership).filter(
            FactionMembership.faction_id == faction_id,
            FactionMembership.character_id == character_id
        ).first()
        
        if not membership:
            raise MembershipNotFoundError(f"Membership for character {character_id} in faction {faction_id} not found")
            
        # Create history event
        event = {
            "type": "updated",
            "timestamp": datetime.utcnow().isoformat()
        }
        changes = False
        
        if role is not None and role != membership.role:
            old_role = membership.role
            membership.role = role
            event["old_role"] = old_role
            event["new_role"] = role
            changes = True
            
        if rank is not None and rank != membership.rank:
            old_rank = membership.rank
            membership.rank = rank
            event["old_rank"] = old_rank
            event["new_rank"] = rank
            changes = True
            
        if active is not None and active != membership.active:
            old_active = membership.active
            membership.active = active
            event["old_active"] = old_active
            event["new_active"] = active
            
            # Special event types for activation/deactivation
            if active:
                event["type"] = "reactivated"
            else:
                event["type"] = "deactivated"
                
            changes = True
            
        # Only add history event if changes were made
        if changes:
            if reason:
                event["reason"] = reason
                
            membership.history.append(event)
            
        # Update metadata if provided
        if metadata:
            if not membership.metadata:
                membership.metadata = {}
            membership.metadata.update(metadata)
            changes = True
            
        if changes:
            membership.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(membership)
            
        return membership
    
    @staticmethod
    def remove_member(
        db: Session,
        faction_id: int,
        character_id: int,
        reason: str = None,
        permanent: bool = False
    ) -> None:
        """
        Remove a character from a faction.
        
        Args:
            db: Database session
            faction_id: ID of the faction
            character_id: ID of the character
            reason: Reason for removal (optional)
            permanent: Whether to permanently delete record (default: False)
            
        Raises:
            MembershipNotFoundError: If membership doesn't exist
        """
        membership = db.query(FactionMembership).filter(
            FactionMembership.faction_id == faction_id,
            FactionMembership.character_id == character_id
        ).first()
        
        if not membership:
            raise MembershipNotFoundError(f"Membership for character {character_id} in faction {faction_id} not found")
            
        if permanent:
            # Permanently delete the record
            db.delete(membership)
        else:
            # Just mark as inactive
            membership.active = False
            
            # Create left event
            event = {
                "type": "left",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if reason:
                event["reason"] = reason
                
            membership.history.append(event)
            membership.updated_at = datetime.utcnow()
            
        db.commit()
    
    @staticmethod
    def transfer_leader(
        db: Session,
        faction_id: int,
        new_leader_id: int,
        reason: str = None
    ) -> Dict:
        """
        Transfer leadership of a faction to a new character.
        
        Args:
            db: Database session
            faction_id: ID of the faction
            new_leader_id: ID of the new leader character
            reason: Reason for transfer (optional)
            
        Returns:
            Dict with transfer details
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
            InvalidMembershipError: If new leader isn't a member
        """
        # Check if faction exists
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        # Get old leader (if any)
        old_leader_id = faction.leader_id
        
        # Check if new leader is a member
        membership = db.query(FactionMembership).filter(
            FactionMembership.faction_id == faction_id,
            FactionMembership.character_id == new_leader_id,
            FactionMembership.active == True
        ).first()
        
        if not membership:
            raise InvalidMembershipError(f"Character {new_leader_id} is not an active member of faction {faction_id}")
            
        # Update faction
        faction.leader_id = new_leader_id
        faction.updated_at = datetime.utcnow()
        
        # Update membership
        membership.role = "leader"
        membership.rank = 10  # Highest rank
        
        # Record leadership change
        event = {
            "type": "became_leader",
            "timestamp": datetime.utcnow().isoformat(),
            "old_leader_id": old_leader_id
        }
        
        if reason:
            event["reason"] = reason
            
        membership.history.append(event)
        
        # If old leader existed and is different, update their membership
        if old_leader_id and old_leader_id != new_leader_id:
            old_leader = db.query(FactionMembership).filter(
                FactionMembership.faction_id == faction_id,
                FactionMembership.character_id == old_leader_id,
                FactionMembership.active == True
            ).first()
            
            if old_leader:
                old_leader.role = "former_leader"  # Or another appropriate role
                
                # Record change
                event = {
                    "type": "leadership_transferred",
                    "timestamp": datetime.utcnow().isoformat(),
                    "new_leader_id": new_leader_id
                }
                
                if reason:
                    event["reason"] = reason
                    
                old_leader.history.append(event)
        
        db.commit()
        
        # Return transfer details
        return {
            "faction_id": faction_id,
            "new_leader_id": new_leader_id,
            "old_leader_id": old_leader_id,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason
        }
    
    @staticmethod
    def switch_faction_by_affinity(
        db: Session,
        character_id: int,
        current_faction_id: int,
        target_faction_id: int,
        affinity_score: Optional[int] = None,
        min_affinity_threshold: int = 60,
        contextual_restrictions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Switch a character's faction membership based on affinity score.
        
        Implements affinity-based switching as described in the development bible,
        allowing characters to switch factions based on their affinity/alignment
        with different faction values and ideologies.
        
        Args:
            db: Database session
            character_id: Character making the switch
            current_faction_id: Current faction ID
            target_faction_id: Target faction ID
            affinity_score: Pre-calculated affinity score (optional)
            min_affinity_threshold: Minimum affinity needed to switch (default: 60)
            contextual_restrictions: Optional restrictions on switching
            
        Returns:
            Dict with switch details or error information
            
        Raises:
            ValueError: If the switch is not allowed due to restrictions
        """
        # Validate inputs
        current_membership = db.query(FactionMembership).filter(
            FactionMembership.faction_id == current_faction_id,
            FactionMembership.character_id == character_id,
            FactionMembership.is_active == True
        ).first()
        
        if not current_membership:
            return {
                "success": False,
                "error": "character_not_in_faction",
                "message": f"Character {character_id} is not an active member of faction {current_faction_id}"
            }
            
        target_faction = db.query(Faction).filter(Faction.id == target_faction_id).first()
        if not target_faction or not target_faction.is_active:
            return {
                "success": False,
                "error": "target_faction_not_found",
                "message": f"Target faction {target_faction_id} not found or inactive"
            }
            
        # Check if the character is already a member of the target faction
        existing_target_membership = db.query(FactionMembership).filter(
            FactionMembership.faction_id == target_faction_id,
            FactionMembership.character_id == character_id
        ).first()
        
        if existing_target_membership and existing_target_membership.is_active:
            return {
                "success": False,
                "error": "already_member",
                "message": f"Character {character_id} is already an active member of faction {target_faction_id}"
            }
            
        # Calculate affinity if not provided
        if affinity_score is None:
            # Import here to avoid circular imports
            from backend.systems.faction.faction_manager import FactionManager
            
            faction_manager = FactionManager(db)
            affinity_score = faction_manager.calculate_affinity(character_id, target_faction_id)
            
        # Check if affinity is high enough
        if affinity_score < min_affinity_threshold:
            return {
                "success": False,
                "error": "insufficient_affinity",
                "message": f"Affinity score {affinity_score} is below threshold {min_affinity_threshold}",
                "affinity_score": affinity_score,
                "threshold": min_affinity_threshold
            }
            
        # Check contextual restrictions
        if contextual_restrictions:
            # Check if war between factions prevents switching
            if contextual_restrictions.get("check_war", False):
                relationship = db.query(FactionRelationship).filter(
                    FactionRelationship.faction_id == current_faction_id,
                    FactionRelationship.other_faction_id == target_faction_id
                ).first()
                
                if relationship and relationship.diplomatic_stance == "at_war":
                    if not contextual_restrictions.get("allow_defection_during_war", False):
                        return {
                            "success": False,
                            "error": "at_war",
                            "message": "Cannot switch to an enemy faction during active war without defection approval"
                        }
                        
            # Check if character is a leader (leaders might be restricted)
            if contextual_restrictions.get("check_leadership", False):
                faction = db.query(Faction).filter(Faction.id == current_faction_id).first()
                if faction and faction.leader_id == character_id:
                    if not contextual_restrictions.get("allow_leader_switch", False):
                        return {
                            "success": False,
                            "error": "is_leader",
                            "message": "Faction leaders cannot switch factions without special approval"
                        }
                        
            # Check for loyalty lockout period
            if contextual_restrictions.get("check_loyalty_period", False):
                days_since_join = (datetime.utcnow() - current_membership.joined_at).days
                min_days = contextual_restrictions.get("min_days_before_switch", 30)
                
                if days_since_join < min_days:
                    return {
                        "success": False,
                        "error": "loyalty_period",
                        "message": f"Cannot switch factions within {min_days} days of joining",
                        "days_remaining": min_days - days_since_join
                    }
        
        # All checks passed, perform the switch
        # 1. Update the current membership
        current_membership.is_active = False
        current_membership.status = "switched"
        current_membership.history.append({
            "type": "faction_switch",
            "to_faction_id": target_faction_id,
            "affinity_score": affinity_score,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # 2. Create or reactivate membership in the target faction
        if existing_target_membership:
            # Reactivate and update existing membership
            existing_target_membership.is_active = True
            existing_target_membership.status = "active"
            existing_target_membership.joined_at = datetime.utcnow()
            existing_target_membership.history.append({
                "type": "rejoined",
                "from_faction_id": current_faction_id,
                "affinity_score": affinity_score,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            new_membership = existing_target_membership
        else:
            # Create new membership
            new_membership = FactionMembership(
                faction_id=target_faction_id,
                character_id=character_id,
                role="member",  # Default role for new members
                rank=0,  # Starting rank
                reputation=max(0, min(60, affinity_score - 20)),  # Initial reputation based on affinity
                is_active=True,
                status="active",
                joined_at=datetime.utcnow(),
                history=[{
                    "type": "joined",
                    "from_faction_id": current_faction_id,
                    "affinity_score": affinity_score,
                    "timestamp": datetime.utcnow().isoformat()
                }],
                metadata={
                    "previous_faction_id": current_faction_id,
                    "switch_date": datetime.utcnow().isoformat(),
                    "affinity_score": affinity_score
                }
            )
            db.add(new_membership)
            
        # Commit changes
        db.commit()
        db.refresh(current_membership)
        db.refresh(new_membership)
        
        # Return success with details
        return {
            "success": True,
            "character_id": character_id,
            "from_faction_id": current_faction_id,
            "to_faction_id": target_faction_id,
            "affinity_score": affinity_score,
            "timestamp": datetime.utcnow().isoformat(),
            "new_membership_id": new_membership.id
        } 