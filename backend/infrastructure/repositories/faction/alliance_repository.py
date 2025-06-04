"""
Alliance Repository

This module provides data access layer for alliance and betrayal data persistence.
"""

from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from enum import Enum

# Define enums locally to avoid circular imports
class AllianceStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DISSOLVED = "dissolved"
    BETRAYED = "betrayed"

class AllianceType(Enum):
    MUTUAL_DEFENSE = "mutual_defense"
    NON_AGGRESSION = "non_aggression"
    TRADE = "trade"
    MILITARY = "military"

from backend.infrastructure.database import get_db_session
from backend.infrastructure.models.faction.models import (
    AllianceEntity, 
    BetrayalEntity, 
    AllianceStatus, 
    AllianceType,
    BetrayalReason
)

class AllianceRepository:
    """Repository for alliance data persistence"""
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the alliance repository.
        
        Args:
            db_session: Database session. If None, creates a new one.
        """
        self.db = db_session or get_db_session()

    # Alliance CRUD operations
    def get_alliance_by_id(self, alliance_id: UUID) -> Optional[AllianceEntity]:
        """
        Get an alliance by ID.
        
        Args:
            alliance_id: ID of the alliance to retrieve
            
        Returns:
            Alliance entity or None if not found
        """
        return self.db.query(AllianceEntity).filter(
            AllianceEntity.id == alliance_id
        ).first()

    def get_alliances_by_faction(self, faction_id: UUID) -> List[AllianceEntity]:
        """
        Get all alliances involving a specific faction.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            List of alliance entities
        """
        return self.db.query(AllianceEntity).filter(
            or_(
                AllianceEntity.leader_faction_id == faction_id,
                AllianceEntity.member_faction_ids.contains([faction_id])
            )
        ).all()

    def get_active_alliances(self) -> List[AllianceEntity]:
        """
        Get all active alliances.
        
        Returns:
            List of active alliance entities
        """
        return self.db.query(AllianceEntity).filter(
            AllianceEntity.status == AllianceStatus.ACTIVE.value,
            AllianceEntity.is_active == True
        ).all()

    def get_alliances_by_status(self, status: AllianceStatus) -> List[AllianceEntity]:
        """
        Get all alliances with a specific status.
        
        Args:
            status: Alliance status to filter by
            
        Returns:
            List of alliance entities
        """
        return self.db.query(AllianceEntity).filter(
            AllianceEntity.status == status.value
        ).all()

    def get_alliances_by_type(self, alliance_type: AllianceType) -> List[AllianceEntity]:
        """
        Get all alliances of a specific type.
        
        Args:
            alliance_type: Alliance type to filter by
            
        Returns:
            List of alliance entities
        """
        return self.db.query(AllianceEntity).filter(
            AllianceEntity.alliance_type == alliance_type.value
        ).all()

    def get_alliances_with_shared_enemy(self, enemy_faction_id: UUID) -> List[AllianceEntity]:
        """
        Get all alliances that have a specific faction as a shared enemy.
        
        Args:
            enemy_faction_id: ID of the enemy faction
            
        Returns:
            List of alliance entities
        """
        return self.db.query(AllianceEntity).filter(
            AllianceEntity.shared_enemies.contains([enemy_faction_id])
        ).all()

    def create_alliance(self, alliance: AllianceEntity) -> AllianceEntity:
        """
        Create a new alliance.
        
        Args:
            alliance: Alliance entity to create
            
        Returns:
            Created alliance entity
        """
        try:
            self.db.add(alliance)
            self.db.commit()
            self.db.refresh(alliance)
            return alliance
        except Exception as e:
            self.db.rollback()
            raise e

    def update_alliance(self, alliance: AllianceEntity) -> AllianceEntity:
        """
        Update an existing alliance.
        
        Args:
            alliance: Alliance entity to update
            
        Returns:
            Updated alliance entity
        """
        alliance.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(alliance)
        return alliance

    def delete_alliance(self, alliance_id: UUID) -> bool:
        """
        Delete an alliance.
        
        Args:
            alliance_id: ID of the alliance to delete
            
        Returns:
            True if alliance was deleted, False if not found
        """
        alliance = self.get_alliance_by_id(alliance_id)
        if alliance:
            self.db.delete(alliance)
            self.db.commit()
            return True
        return False

    def update_alliance_status(self, alliance_id: UUID, status: AllianceStatus) -> bool:
        """
        Update the status of an alliance.
        
        Args:
            alliance_id: ID of the alliance
            status: New status
            
        Returns:
            True if updated, False if not found
        """
        try:
            alliance = self.get_alliance_by_id(alliance_id)
            if alliance:
                alliance.status = status.value
                alliance.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e

    def add_faction_to_alliance(self, alliance_id: UUID, faction_id: UUID) -> bool:
        """
        Add a faction to an existing alliance.
        
        Args:
            alliance_id: ID of the alliance
            faction_id: ID of the faction to add
            
        Returns:
            True if added, False if not found or already a member
        """
        alliance = self.get_alliance_by_id(alliance_id)
        if not alliance:
            return False
        
        # Check if faction is already in alliance
        all_faction_ids = [alliance.leader_faction_id] + (alliance.member_faction_ids or [])
        if faction_id in all_faction_ids:
            return False
        
        # Add to member list
        if alliance.member_faction_ids is None:
            alliance.member_faction_ids = []
        alliance.member_faction_ids.append(faction_id)
        
        alliance.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def remove_faction_from_alliance(self, alliance_id: UUID, faction_id: UUID) -> bool:
        """
        Remove a faction from an alliance.
        
        Args:
            alliance_id: ID of the alliance
            faction_id: ID of the faction to remove
            
        Returns:
            True if removed, False if not found or not a member
        """
        alliance = self.get_alliance_by_id(alliance_id)
        if not alliance:
            return False
        
        # Cannot remove leader faction
        if alliance.leader_faction_id == faction_id:
            return False
        
        # Remove from member list
        if alliance.member_faction_ids and faction_id in alliance.member_faction_ids:
            alliance.member_faction_ids.remove(faction_id)
            alliance.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False

    def update_alliance_trust_levels(
        self, 
        alliance_id: UUID, 
        trust_levels: Dict[str, float]
    ) -> bool:
        """
        Update trust levels in an alliance.
        
        Args:
            alliance_id: ID of the alliance
            trust_levels: New trust level data
            
        Returns:
            True if updated, False if not found
        """
        try:
            alliance = self.get_alliance_by_id(alliance_id)
            if alliance:
                alliance.trust_levels = trust_levels
                alliance.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e

    def update_alliance_betrayal_risks(
        self, 
        alliance_id: UUID, 
        betrayal_risks: Dict[str, float]
    ) -> bool:
        """
        Update betrayal risks in an alliance.
        
        Args:
            alliance_id: ID of the alliance
            betrayal_risks: New betrayal risk data
            
        Returns:
            True if updated, False if not found
        """
        try:
            alliance = self.get_alliance_by_id(alliance_id)
            if alliance:
                alliance.betrayal_risks = betrayal_risks
                alliance.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e

    # Betrayal operations
    def get_betrayal_by_id(self, betrayal_id: UUID) -> Optional[BetrayalEntity]:
        """
        Get a betrayal event by ID.
        
        Args:
            betrayal_id: ID of the betrayal to retrieve
            
        Returns:
            Betrayal entity or None if not found
        """
        return self.db.query(BetrayalEntity).filter(
            BetrayalEntity.id == betrayal_id
        ).first()

    def get_betrayals_by_alliance(self, alliance_id: UUID) -> List[BetrayalEntity]:
        """
        Get all betrayal events for a specific alliance.
        
        Args:
            alliance_id: ID of the alliance
            
        Returns:
            List of betrayal entities
        """
        return self.db.query(BetrayalEntity).filter(
            BetrayalEntity.alliance_id == alliance_id
        ).order_by(desc(BetrayalEntity.created_at)).all()

    def get_betrayals_by_faction(self, faction_id: UUID) -> List[BetrayalEntity]:
        """
        Get all betrayal events involving a specific faction (as victim).
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            List of betrayal entities where faction was a victim
        """
        return self.db.query(BetrayalEntity).filter(
            BetrayalEntity.victim_faction_ids.contains([faction_id])
        ).order_by(desc(BetrayalEntity.created_at)).all()

    def get_betrayals_by_betrayer(self, betrayer_faction_id: UUID) -> List[BetrayalEntity]:
        """
        Get all betrayal events committed by a specific faction.
        
        Args:
            betrayer_faction_id: ID of the betrayer faction
            
        Returns:
            List of betrayal entities committed by the faction
        """
        return self.db.query(BetrayalEntity).filter(
            BetrayalEntity.betrayer_faction_id == betrayer_faction_id
        ).order_by(desc(BetrayalEntity.created_at)).all()

    def get_recent_betrayals(self, limit: int = 10) -> List[BetrayalEntity]:
        """
        Get recent betrayal events.
        
        Args:
            limit: Maximum number of betrayals to return
            
        Returns:
            List of recent betrayal entities
        """
        return self.db.query(BetrayalEntity).order_by(
            desc(BetrayalEntity.created_at)
        ).limit(limit).all()

    def create_betrayal(self, betrayal: BetrayalEntity) -> BetrayalEntity:
        """
        Create a new betrayal event.
        
        Args:
            betrayal: Betrayal entity to create
            
        Returns:
            Created betrayal entity
        """
        try:
            self.db.add(betrayal)
            self.db.commit()
            self.db.refresh(betrayal)
            return betrayal
        except Exception as e:
            self.db.rollback()
            raise e

    def update_betrayal(self, betrayal: BetrayalEntity) -> BetrayalEntity:
        """
        Update an existing betrayal event.
        
        Args:
            betrayal: Betrayal entity to update
            
        Returns:
            Updated betrayal entity
        """
        betrayal.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(betrayal)
        return betrayal

    def delete_betrayal(self, betrayal_id: UUID) -> bool:
        """
        Delete a betrayal event.
        
        Args:
            betrayal_id: ID of the betrayal to delete
            
        Returns:
            True if betrayal was deleted, False if not found
        """
        betrayal = self.get_betrayal_by_id(betrayal_id)
        if betrayal:
            self.db.delete(betrayal)
            self.db.commit()
            return True
        return False

    # Statistics and analysis
    def get_faction_alliance_count(self, faction_id: UUID) -> int:
        """
        Get the number of active alliances for a faction.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            Number of active alliances
        """
        return len(self.get_alliances_by_faction(faction_id))

    def get_faction_betrayal_count(self, faction_id: UUID) -> int:
        """
        Get the number of betrayals committed by a faction.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            Number of betrayals committed
        """
        return self.db.query(BetrayalEntity).filter(
            BetrayalEntity.betrayer_faction_id == faction_id
        ).count()

    def get_alliance_statistics(self) -> Dict[str, Any]:
        """
        Get general statistics about alliances.
        
        Returns:
            Dictionary containing alliance statistics
        """
        total_alliances = self.db.query(AllianceEntity).count()
        active_alliances = self.db.query(AllianceEntity).filter(
            AllianceEntity.status == AllianceStatus.ACTIVE.value
        ).count()
        betrayed_alliances = self.db.query(AllianceEntity).filter(
            AllianceEntity.status == AllianceStatus.BETRAYED.value
        ).count()
        
        total_betrayals = self.db.query(BetrayalEntity).count()
        
        # Calculate average alliance duration for dissolved alliances
        dissolved_alliances = self.db.query(AllianceEntity).filter(
            AllianceEntity.status == AllianceStatus.DISSOLVED.value,
            AllianceEntity.start_date.isnot(None),
            AllianceEntity.updated_at.isnot(None)
        ).all()
        
        avg_duration_days = 0
        if dissolved_alliances:
            total_duration = sum([
                (alliance.updated_at - alliance.start_date).days
                for alliance in dissolved_alliances
                if alliance.start_date and alliance.updated_at
            ])
            avg_duration_days = total_duration / len(dissolved_alliances)
        
        return {
            "total_alliances": total_alliances,
            "active_alliances": active_alliances,
            "betrayed_alliances": betrayed_alliances,
            "dissolved_alliances": len(dissolved_alliances),
            "total_betrayals": total_betrayals,
            "betrayal_rate": (betrayed_alliances / total_alliances) if total_alliances > 0 else 0,
            "average_alliance_duration_days": avg_duration_days
        }

    def find_potential_alliance_partners(
        self, 
        faction_id: UUID, 
        shared_enemy_id: Optional[UUID] = None
    ) -> List[UUID]:
        """
        Find potential alliance partners for a faction.
        
        Args:
            faction_id: ID of the faction seeking partners
            shared_enemy_id: Optional shared enemy to look for
            
        Returns:
            List of potential partner faction IDs
        """
        # Get alliances where the faction is already a member
        existing_alliances = self.get_alliances_by_faction(faction_id)
        
        # Extract faction IDs that are already allies
        allied_faction_ids = set()
        for alliance in existing_alliances:
            if alliance.status == AllianceStatus.ACTIVE.value:
                all_members = [alliance.leader_faction_id] + (alliance.member_faction_ids or [])
                allied_faction_ids.update(all_members)
        
        # Remove the faction itself from allies
        allied_faction_ids.discard(faction_id)
        
        # If looking for factions with a shared enemy
        if shared_enemy_id:
            potential_partners = []
            alliances_against_enemy = self.get_alliances_with_shared_enemy(shared_enemy_id)
            
            for alliance in alliances_against_enemy:
                all_members = [alliance.leader_faction_id] + (alliance.member_faction_ids or [])
                for member_id in all_members:
                    if member_id != faction_id and member_id not in allied_faction_ids:
                        potential_partners.append(member_id)
            
            return list(set(potential_partners))  # Remove duplicates
        
        # For now, return empty list if no shared enemy specified
        # This could be enhanced to consider other factors like:
        # - Geographic proximity
        # - Similar faction types
        # - Complementary strengths
        return [] 