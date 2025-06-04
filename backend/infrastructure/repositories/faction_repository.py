"""
Faction Repository Implementation

SQLAlchemy-based repository for faction data access.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.models.faction.models import FactionEntity
from backend.systems.faction.services.services import FactionData, FactionRepository


class SQLAlchemyFactionRepository:
    """SQLAlchemy implementation of FactionRepository protocol"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_faction_by_id(self, faction_id: UUID) -> Optional[FactionData]:
        """Get faction by ID"""
        entity = self.db_session.query(FactionEntity).filter(
            FactionEntity.id == faction_id,
            FactionEntity.is_active == True
        ).first()
        
        if not entity:
            return None
            
        return self._entity_to_business_data(entity)
    
    def get_faction_by_name(self, name: str) -> Optional[FactionData]:
        """Get faction by name"""
        entity = self.db_session.query(FactionEntity).filter(
            FactionEntity.name == name,
            FactionEntity.is_active == True
        ).first()
        
        if not entity:
            return None
            
        return self._entity_to_business_data(entity)
    
    def create_faction(self, faction_data: FactionData) -> FactionData:
        """Create a new faction"""
        entity = FactionEntity(
            id=faction_data.id,
            name=faction_data.name,
            description=faction_data.description,
            status=faction_data.status,
            properties=faction_data.properties,
            hidden_ambition=faction_data.hidden_ambition,
            hidden_integrity=faction_data.hidden_integrity,
            hidden_discipline=faction_data.hidden_discipline,
            hidden_impulsivity=faction_data.hidden_impulsivity,
            hidden_pragmatism=faction_data.hidden_pragmatism,
            hidden_resilience=faction_data.hidden_resilience
        )
        
        self.db_session.add(entity)
        self.db_session.commit()
        self.db_session.refresh(entity)
        
        return self._entity_to_business_data(entity)
    
    def update_faction(self, faction_data: FactionData) -> FactionData:
        """Update existing faction"""
        entity = self.db_session.query(FactionEntity).filter(
            FactionEntity.id == faction_data.id
        ).first()
        
        if not entity:
            raise ValueError(f"Faction {faction_data.id} not found")
        
        # Update fields
        entity.name = faction_data.name
        entity.description = faction_data.description
        entity.status = faction_data.status
        entity.properties = faction_data.properties
        entity.hidden_ambition = faction_data.hidden_ambition
        entity.hidden_integrity = faction_data.hidden_integrity
        entity.hidden_discipline = faction_data.hidden_discipline
        entity.hidden_impulsivity = faction_data.hidden_impulsivity
        entity.hidden_pragmatism = faction_data.hidden_pragmatism
        entity.hidden_resilience = faction_data.hidden_resilience
        
        self.db_session.commit()
        self.db_session.refresh(entity)
        
        return self._entity_to_business_data(entity)
    
    def delete_faction(self, faction_id: UUID) -> bool:
        """Delete faction (soft delete)"""
        entity = self.db_session.query(FactionEntity).filter(
            FactionEntity.id == faction_id
        ).first()
        
        if not entity:
            return False
        
        # Soft delete by setting is_active to False
        entity.is_active = False
        self.db_session.commit()
        
        return True
    
    def list_factions(self, 
                     page: int = 1, 
                     size: int = 50, 
                     status: Optional[str] = None,
                     search: Optional[str] = None) -> Tuple[List[FactionData], int]:
        """List factions with pagination"""
        query = self.db_session.query(FactionEntity).filter(
            FactionEntity.is_active == True
        )
        
        # Apply filters
        if status:
            query = query.filter(FactionEntity.status == status)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    FactionEntity.name.ilike(search_term),
                    FactionEntity.description.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        entities = query.offset(offset).limit(size).all()
        
        # Convert to business data
        faction_data_list = [self._entity_to_business_data(entity) for entity in entities]
        
        return faction_data_list, total
    
    def get_faction_statistics(self) -> Dict[str, Any]:
        """Get faction statistics"""
        total_active = self.db_session.query(func.count(FactionEntity.id)).filter(
            FactionEntity.is_active == True
        ).scalar()
        
        total_inactive = self.db_session.query(func.count(FactionEntity.id)).filter(
            FactionEntity.is_active == False
        ).scalar()
        
        status_counts = {}
        status_query = self.db_session.query(
            FactionEntity.status, 
            func.count(FactionEntity.id)
        ).filter(
            FactionEntity.is_active == True
        ).group_by(FactionEntity.status).all()
        
        for status, count in status_query:
            status_counts[status] = count
        
        return {
            "total_active": total_active,
            "total_inactive": total_inactive,
            "total": total_active + total_inactive,
            "status_breakdown": status_counts
        }
    
    def _entity_to_business_data(self, entity: FactionEntity) -> FactionData:
        """Convert database entity to business data"""
        return FactionData(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            status=entity.status,
            properties=entity.properties or {},
            hidden_ambition=entity.hidden_ambition,
            hidden_integrity=entity.hidden_integrity,
            hidden_discipline=entity.hidden_discipline,
            hidden_impulsivity=entity.hidden_impulsivity,
            hidden_pragmatism=entity.hidden_pragmatism,
            hidden_resilience=entity.hidden_resilience
        ) 