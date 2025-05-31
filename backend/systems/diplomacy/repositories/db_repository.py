"""
SQLAlchemy Database Repository for Diplomacy System

This module provides database persistence for diplomatic entities,
replacing the file-based storage with proper SQLAlchemy operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Temporarily comment out problematic imports
# from backend.infrastructure.database import get_db, get_async_db
from backend.systems.diplomacy.db_models import (
    DiplomaticRelationship as DBDiplomaticRelationship,
    Treaty as DBTreaty,
    Negotiation as DBNegotiation,
    DiplomaticEvent as DBDiplomaticEvent,
    TreatyViolation as DBTreatyViolation,
    DiplomaticIncident as DBDiplomaticIncident,
    Ultimatum as DBUltimatum,
    Sanction as DBSanction
)
from backend.systems.diplomacy.models import (
    DiplomaticStatus, TreatyType, TreatyStatus, NegotiationStatus,
    DiplomaticEventType, TreatyViolationType, DiplomaticIncidentType,
    DiplomaticIncidentSeverity, UltimatumStatus, SanctionType, SanctionStatus,
    Treaty, Negotiation, DiplomaticEvent, TreatyViolation,
    DiplomaticIncident, Ultimatum, Sanction
)


class DiplomacyDatabaseRepository:
    """SQLAlchemy-based repository for managing diplomatic entities."""

    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the repository with a database session.
        
        Args:
            db_session: Optional SQLAlchemy session. If None, will use dependency injection.
        """
        self.db_session = db_session

    def _get_session(self) -> Session:
        """Get database session, using dependency injection if none provided."""
        if self.db_session:
            return self.db_session
        # This would typically be injected via FastAPI dependency
        # return next(get_db())
        raise Exception("Database session not provided and dependency injection not available")

    # Diplomatic Relationships
    def get_faction_relationship(self, faction_a_id: UUID, faction_b_id: UUID) -> Optional[Dict]:
        """Get relationship between two factions."""
        session = self._get_session()
        
        # Ensure consistent ordering (smaller UUID first)
        if str(faction_a_id) > str(faction_b_id):
            faction_a_id, faction_b_id = faction_b_id, faction_a_id
        
        relationship = session.query(DBDiplomaticRelationship).filter(
            and_(
                DBDiplomaticRelationship.faction_a_id == faction_a_id,
                DBDiplomaticRelationship.faction_b_id == faction_b_id
            )
        ).first()
        
        if not relationship:
            return None
            
        return {
            "id": relationship.id,
            "faction_a_id": relationship.faction_a_id,
            "faction_b_id": relationship.faction_b_id,
            "status": relationship.status,
            "trust_level": relationship.trust_level,
            "tension_level": relationship.tension_level,
            "last_interaction": relationship.last_interaction,
            "created_at": relationship.created_at,
            "updated_at": relationship.updated_at
        }

    def create_or_update_faction_relationship(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID,
        status: Optional[DiplomaticStatus] = None,
        trust_level: Optional[int] = None,
        tension_level: Optional[int] = None
    ) -> Dict:
        """Create or update relationship between two factions."""
        session = self._get_session()
        
        # Ensure consistent ordering
        if str(faction_a_id) > str(faction_b_id):
            faction_a_id, faction_b_id = faction_b_id, faction_a_id
        
        relationship = session.query(DBDiplomaticRelationship).filter(
            and_(
                DBDiplomaticRelationship.faction_a_id == faction_a_id,
                DBDiplomaticRelationship.faction_b_id == faction_b_id
            )
        ).first()
        
        if relationship:
            # Update existing
            if status is not None:
                relationship.status = status
            if trust_level is not None:
                relationship.trust_level = trust_level
            if tension_level is not None:
                relationship.tension_level = tension_level
            relationship.last_interaction = datetime.utcnow()
        else:
            # Create new
            relationship = DBDiplomaticRelationship(
                faction_a_id=faction_a_id,
                faction_b_id=faction_b_id,
                status=status or DiplomaticStatus.NEUTRAL,
                trust_level=trust_level or 50,
                tension_level=tension_level or 0
            )
            session.add(relationship)
        
        session.commit()
        session.refresh(relationship)
        
        return {
            "id": relationship.id,
            "faction_a_id": relationship.faction_a_id,
            "faction_b_id": relationship.faction_b_id,
            "status": relationship.status,
            "trust_level": relationship.trust_level,
            "tension_level": relationship.tension_level,
            "last_interaction": relationship.last_interaction,
            "created_at": relationship.created_at,
            "updated_at": relationship.updated_at
        }

    def get_faction_relationships(self, faction_id: UUID) -> List[Dict]:
        """Get all relationships for a faction."""
        session = self._get_session()
        
        relationships = session.query(DBDiplomaticRelationship).filter(
            or_(
                DBDiplomaticRelationship.faction_a_id == faction_id,
                DBDiplomaticRelationship.faction_b_id == faction_id
            )
        ).all()
        
        result = []
        for rel in relationships:
            other_faction_id = rel.faction_b_id if rel.faction_a_id == faction_id else rel.faction_a_id
            result.append({
                "id": rel.id,
                "other_faction_id": other_faction_id,
                "status": rel.status,
                "trust_level": rel.trust_level,
                "tension_level": rel.tension_level,
                "last_interaction": rel.last_interaction,
                "created_at": rel.created_at,
                "updated_at": rel.updated_at
            })
        
        return result

    # Treaties
    def create_treaty(self, treaty_data: Dict) -> Treaty:
        """Create a new treaty."""
        session = self._get_session()
        
        db_treaty = DBTreaty(
            name=treaty_data["name"],
            treaty_type=treaty_data["treaty_type"],
            status=treaty_data.get("status", TreatyStatus.DRAFT),
            terms=treaty_data.get("terms", {}),
            parties=treaty_data["parties"],
            start_date=treaty_data.get("start_date"),
            end_date=treaty_data.get("end_date"),
            is_public=treaty_data.get("is_public", True),
            negotiation_id=treaty_data.get("negotiation_id"),
            created_by=treaty_data.get("created_by")
        )
        
        session.add(db_treaty)
        session.commit()
        session.refresh(db_treaty)
        
        return self._db_treaty_to_pydantic(db_treaty)

    def get_treaty(self, treaty_id: UUID) -> Optional[Treaty]:
        """Get treaty by ID."""
        session = self._get_session()
        
        db_treaty = session.query(DBTreaty).filter(DBTreaty.id == treaty_id).first()
        if not db_treaty:
            return None
            
        return self._db_treaty_to_pydantic(db_treaty)

    def update_treaty(self, treaty_id: UUID, updates: Dict) -> Optional[Treaty]:
        """Update treaty."""
        session = self._get_session()
        
        db_treaty = session.query(DBTreaty).filter(DBTreaty.id == treaty_id).first()
        if not db_treaty:
            return None
        
        for key, value in updates.items():
            if hasattr(db_treaty, key):
                setattr(db_treaty, key, value)
        
        session.commit()
        session.refresh(db_treaty)
        
        return self._db_treaty_to_pydantic(db_treaty)

    def list_treaties(
        self, 
        faction_id: Optional[UUID] = None,
        active_only: bool = False,
        treaty_type: Optional[TreatyType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Treaty]:
        """List treaties with optional filters."""
        session = self._get_session()
        
        query = session.query(DBTreaty)
        
        if faction_id:
            # Filter by faction participation
            query = query.filter(DBTreaty.parties.contains([str(faction_id)]))
        
        if active_only:
            query = query.filter(DBTreaty.status == TreatyStatus.ACTIVE)
        
        if treaty_type:
            query = query.filter(DBTreaty.treaty_type == treaty_type)
        
        query = query.order_by(desc(DBTreaty.created_at))
        query = query.offset(offset).limit(limit)
        
        db_treaties = query.all()
        return [self._db_treaty_to_pydantic(t) for t in db_treaties]

    # Negotiations
    def create_negotiation(self, negotiation_data: Dict) -> Negotiation:
        """Create a new negotiation."""
        session = self._get_session()
        
        db_negotiation = DBNegotiation(
            parties=negotiation_data["parties"],
            initiator_id=negotiation_data["initiator_id"],
            status=negotiation_data.get("status", NegotiationStatus.PROPOSED),
            treaty_type=negotiation_data.get("treaty_type"),
            current_offer=negotiation_data.get("current_offer", {}),
            offers_history=negotiation_data.get("offers_history", []),
            meta_data=negotiation_data.get("meta_data", {}),
            deadline=negotiation_data.get("deadline")
        )
        
        session.add(db_negotiation)
        session.commit()
        session.refresh(db_negotiation)
        
        return self._db_negotiation_to_pydantic(db_negotiation)

    def get_negotiation(self, negotiation_id: UUID) -> Optional[Negotiation]:
        """Get negotiation by ID."""
        session = self._get_session()
        
        db_negotiation = session.query(DBNegotiation).filter(
            DBNegotiation.id == negotiation_id
        ).first()
        
        if not db_negotiation:
            return None
            
        return self._db_negotiation_to_pydantic(db_negotiation)

    def update_negotiation(self, negotiation_id: UUID, updates: Dict) -> Optional[Negotiation]:
        """Update negotiation."""
        session = self._get_session()
        
        db_negotiation = session.query(DBNegotiation).filter(
            DBNegotiation.id == negotiation_id
        ).first()
        
        if not db_negotiation:
            return None
        
        for key, value in updates.items():
            if hasattr(db_negotiation, key):
                setattr(db_negotiation, key, value)
        
        session.commit()
        session.refresh(db_negotiation)
        
        return self._db_negotiation_to_pydantic(db_negotiation)

    # Helper methods to convert between DB models and Pydantic models
    def _db_treaty_to_pydantic(self, db_treaty: DBTreaty) -> Treaty:
        """Convert database treaty to Pydantic model."""
        return Treaty(
            id=db_treaty.id,
            name=db_treaty.name,
            treaty_type=db_treaty.treaty_type,
            status=db_treaty.status,
            terms=db_treaty.terms,
            parties=[UUID(p) for p in db_treaty.parties],
            start_date=db_treaty.start_date,
            end_date=db_treaty.end_date,
            is_public=db_treaty.is_public,
            negotiation_id=db_treaty.negotiation_id,
            created_by=db_treaty.created_by,
            created_at=db_treaty.created_at,
            updated_at=db_treaty.updated_at
        )

    def _db_negotiation_to_pydantic(self, db_negotiation: DBNegotiation) -> Negotiation:
        """Convert database negotiation to Pydantic model."""
        return Negotiation(
            id=db_negotiation.id,
            parties=[UUID(p) for p in db_negotiation.parties],
            initiator_id=db_negotiation.initiator_id,
            status=db_negotiation.status,
            treaty_type=db_negotiation.treaty_type,
            current_offer=db_negotiation.current_offer,
            offers_history=db_negotiation.offers_history,
            meta_data=db_negotiation.meta_data,
            deadline=db_negotiation.deadline,
            created_at=db_negotiation.created_at,
            updated_at=db_negotiation.updated_at
        )

    # Additional methods for other entities would follow the same pattern...
    # (DiplomaticEvent, TreatyViolation, DiplomaticIncident, Ultimatum, Sanction)
    
    def create_diplomatic_event(self, event_data: Dict) -> DiplomaticEvent:
        """Create a new diplomatic event."""
        session = self._get_session()
        
        db_event = DBDiplomaticEvent(
            event_type=event_data["event_type"],
            description=event_data["description"],
            participants=event_data["participants"],
            event_data=event_data.get("event_data", {}),
            treaty_id=event_data.get("treaty_id"),
            negotiation_id=event_data.get("negotiation_id"),
            is_public=event_data.get("is_public", True)
        )
        
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        
        return self._db_event_to_pydantic(db_event)

    def _db_event_to_pydantic(self, db_event: DBDiplomaticEvent) -> DiplomaticEvent:
        """Convert database event to Pydantic model."""
        return DiplomaticEvent(
            id=db_event.id,
            event_type=db_event.event_type,
            description=db_event.description,
            participants=[UUID(p) for p in db_event.participants],
            event_data=db_event.event_data,
            treaty_id=db_event.treaty_id,
            negotiation_id=db_event.negotiation_id,
            timestamp=db_event.timestamp,
            is_public=db_event.is_public
        ) 