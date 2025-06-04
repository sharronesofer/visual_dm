"""
Reputation Database Service

This module handles all database operations for faction reputation systems,
separating technical database concerns from business logic.
"""

from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.systems.faction.models.faction import Faction
from backend.infrastructure.shared.exceptions import (
    FactionNotFoundError,
    RepositoryError
)


class ReputationDatabaseService:
    """Database service for faction reputation operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_faction_for_reputation(self, faction_id: int) -> Optional[Faction]:
        """Get faction entity for reputation operations"""
        try:
            return self.db.query(Faction).filter(Faction.id == faction_id).first()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to retrieve faction {faction_id}: {e}")

    def update_faction_reputation(self, faction: Faction) -> None:
        """Update faction reputation in database"""
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to update faction reputation: {e}")

    def update_faction_state(self, faction: Faction, state_updates: Dict[str, Any]) -> None:
        """Update faction state with reputation data"""
        try:
            for key, value in state_updates.items():
                faction.state[key] = value
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to update faction state: {e}")

    def get_faction_memberships(self, faction_id: int) -> List[Any]:
        """Get faction memberships for reputation calculations"""
        try:
            from backend.systems.faction.models.faction import FactionMembership
            return self.db.query(FactionMembership).filter(
                FactionMembership.faction_id == faction_id,
                FactionMembership.active == True
            ).all()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to retrieve faction memberships: {e}")

    def get_all_factions(self) -> List[Faction]:
        """Get all factions for reputation calculations"""
        try:
            return self.db.query(Faction).all()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to retrieve all factions: {e}")

    def close(self):
        """Close database session"""
        if self.db:
            self.db.close()


def create_reputation_database_service(db_session: Session) -> ReputationDatabaseService:
    """Factory function to create reputation database service"""
    return ReputationDatabaseService(db_session) 