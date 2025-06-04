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

# Import database models - will need to be moved as well
from backend.infrastructure.database.models.diplomacy_models import (
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
        from backend.infrastructure.database import get_db
        return next(get_db())

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
        """Update treaty with new values."""
        session = self._get_session()
        
        db_treaty = session.query(DBTreaty).filter(DBTreaty.id == treaty_id).first()
        
        if not db_treaty:
            return None
        
        # Update fields
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
        """List treaties, optionally filtered."""
        session = self._get_session()
        
        query = session.query(DBTreaty)
        
        # Apply filters
        if faction_id:
            query = query.filter(DBTreaty.parties.contains([str(faction_id)]))
        
        if active_only:
            query = query.filter(DBTreaty.status == TreatyStatus.ACTIVE)
        
        if treaty_type:
            query = query.filter(DBTreaty.treaty_type == treaty_type)
        
        # Apply pagination
        treaties = query.offset(offset).limit(limit).all()
        
        return [self._db_treaty_to_pydantic(treaty) for treaty in treaties]

    # Negotiations
    def create_negotiation(self, negotiation_data: Dict) -> Negotiation:
        """Create a new negotiation."""
        session = self._get_session()
        
        db_negotiation = DBNegotiation(
            parties=negotiation_data["parties"],
            initiator_id=negotiation_data["initiator_id"],
            status=negotiation_data.get("status", NegotiationStatus.ACTIVE),
            treaty_type=negotiation_data.get("treaty_type"),
            metadata=negotiation_data.get("metadata", {})
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
        """Update negotiation with new values."""
        session = self._get_session()
        
        db_negotiation = session.query(DBNegotiation).filter(
            DBNegotiation.id == negotiation_id
        ).first()
        
        if not db_negotiation:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(db_negotiation, key):
                setattr(db_negotiation, key, value)
        
        session.commit()
        session.refresh(db_negotiation)
        
        return self._db_negotiation_to_pydantic(db_negotiation)

    # Helper methods for converting between DB and Pydantic models
    def _db_treaty_to_pydantic(self, db_treaty: DBTreaty) -> Treaty:
        """Convert SQLAlchemy Treaty to Pydantic Treaty."""
        return Treaty(
            id=db_treaty.id,
            name=db_treaty.name,
            type=db_treaty.treaty_type,
            parties=db_treaty.parties,
            terms=db_treaty.terms or {},
            start_date=db_treaty.start_date or db_treaty.created_at,
            end_date=db_treaty.end_date,
            is_active=(db_treaty.status == TreatyStatus.ACTIVE),
            is_public=db_treaty.is_public,
            created_at=db_treaty.created_at,
            updated_at=db_treaty.updated_at,
            negotiation_id=db_treaty.negotiation_id
        )

    def _db_negotiation_to_pydantic(self, db_negotiation: DBNegotiation) -> Negotiation:
        """Convert SQLAlchemy Negotiation to Pydantic Negotiation."""
        return Negotiation(
            id=db_negotiation.id,
            parties=db_negotiation.parties,
            initiator_id=db_negotiation.initiator_id,
            status=db_negotiation.status,
            offers=[],  # Would need to load from separate table
            current_offer_id=db_negotiation.current_offer_id,
            treaty_type=db_negotiation.treaty_type,
            start_date=db_negotiation.created_at,
            end_date=db_negotiation.end_date,
            result_treaty_id=db_negotiation.result_treaty_id,
            metadata=db_negotiation.metadata or {}
        )

    # Diplomatic Events
    def create_diplomatic_event(self, event_data: Dict) -> DiplomaticEvent:
        """Create a new diplomatic event."""
        session = self._get_session()
        
        db_event = DBDiplomaticEvent(
            event_type=event_data["event_type"],
            factions=event_data["factions"],
            description=event_data["description"],
            severity=event_data.get("severity", 0),
            public=event_data.get("public", True),
            related_treaty_id=event_data.get("related_treaty_id"),
            related_negotiation_id=event_data.get("related_negotiation_id"),
            metadata=event_data.get("metadata", {}),
            tension_change=event_data.get("tension_change", {})
        )
        
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        
        return self._db_event_to_pydantic(db_event)

    def _db_event_to_pydantic(self, db_event: DBDiplomaticEvent) -> DiplomaticEvent:
        """Convert SQLAlchemy DiplomaticEvent to Pydantic DiplomaticEvent."""
        return DiplomaticEvent(
            id=db_event.id,
            event_type=db_event.event_type,
            factions=db_event.factions,
            timestamp=db_event.created_at,
            description=db_event.description,
            severity=db_event.severity,
            public=db_event.public,
            related_treaty_id=db_event.related_treaty_id,
            related_negotiation_id=db_event.related_negotiation_id,
            metadata=db_event.metadata or {},
            tension_change=db_event.tension_change or {}
        ) 