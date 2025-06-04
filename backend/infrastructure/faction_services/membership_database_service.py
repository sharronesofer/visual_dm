"""
Faction Membership Database Service

This module provides database operations for faction membership,
separated from business logic according to clean architecture principles.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from backend.systems.faction.models.faction import Faction, FactionMembership


class MembershipNotFoundError(Exception):
    """Raised when a membership cannot be found."""


class InvalidMembershipError(Exception):
    """Raised when an invalid membership operation is attempted."""


class FactionMembershipDatabaseService:
    """Database service for managing character memberships in factions."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_membership(self, membership: FactionMembership) -> FactionMembership:
        """Create a new membership in the database"""
        self.db_session.add(membership)
        self.db_session.commit()
        self.db_session.refresh(membership)
        return membership

    def get_membership(
        self,
        faction_id: int,
        character_id: int
    ) -> Optional[FactionMembership]:
        """Get membership information for a character in a faction"""
        return self.db_session.query(FactionMembership).filter(
            FactionMembership.faction_id == faction_id,
            FactionMembership.character_id == character_id
        ).first()

    def get_faction_members(
        self,
        faction_id: int,
        active_only: bool = True,
        role: Optional[str] = None,
        min_rank: Optional[int] = None
    ) -> List[FactionMembership]:
        """Get all members of a faction with optional filters"""
        query = self.db_session.query(FactionMembership).filter(
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

    def get_character_factions(
        self,
        character_id: int,
        active_only: bool = True
    ) -> List[Dict]:
        """Get all factions a character is a member of"""
        query = self.db_session.query(FactionMembership).filter(
            FactionMembership.character_id == character_id
        )
        
        if active_only:
            query = query.filter(FactionMembership.active == True)
            
        memberships = query.all()
        
        # Get faction details for each membership
        result = []
        for membership in memberships:
            faction = self.db_session.query(Faction).filter(
                Faction.id == membership.faction_id
            ).first()
            
            if faction:
                result.append({
                    "faction": faction,
                    "membership": membership,
                    "role": membership.role,
                    "rank": membership.rank,
                    "joined_at": membership.joined_at,
                    "is_leader": membership.role == "leader"
                })
                
        return sorted(result, key=lambda x: (x["rank"], x["joined_at"]), reverse=True)

    def update_membership(self, membership: FactionMembership) -> FactionMembership:
        """Update membership in the database"""
        self.db_session.commit()
        self.db_session.refresh(membership)
        return membership

    def get_faction_by_id(self, faction_id: int) -> Optional[Faction]:
        """Get faction by ID"""
        return self.db_session.query(Faction).filter(Faction.id == faction_id).first()

    def delete_membership(self, membership: FactionMembership) -> None:
        """Delete membership from database"""
        self.db_session.delete(membership)
        self.db_session.commit()

    def commit_changes(self) -> None:
        """Commit pending changes"""
        self.db_session.commit()

    def rollback_changes(self) -> None:
        """Rollback pending changes"""
        self.db_session.rollback() 