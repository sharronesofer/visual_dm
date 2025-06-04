"""
SQLAlchemy Repository Implementation for Rumor System

This module provides the concrete implementation of the RumorRepository protocol
using SQLAlchemy for database operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

# Business layer imports
from backend.systems.rumor.services.services import (
    RumorData, 
    RumorRepository as RumorRepositoryProtocol
)

# Infrastructure imports
from backend.infrastructure.systems.rumor.models.models import RumorEntity


class SQLAlchemyRumorRepository(RumorRepositoryProtocol):
    """
    SQLAlchemy implementation of the rumor repository.
    Provides database persistence for rumors using the business logic protocol.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize repository with database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
    
    def get_rumor_by_id(self, rumor_id: UUID) -> Optional[RumorData]:
        """Get rumor by ID"""
        entity = self.db_session.query(RumorEntity).filter(
            RumorEntity.id == rumor_id
        ).first()
        
        if not entity:
            return None
        
        return self._entity_to_business_data(entity)
    
    def create_rumor(self, rumor_data: RumorData) -> RumorData:
        """Create a new rumor"""
        entity = self._business_data_to_entity(rumor_data)
        
        self.db_session.add(entity)
        self.db_session.commit()
        self.db_session.refresh(entity)
        
        return self._entity_to_business_data(entity)
    
    def update_rumor(self, rumor_data: RumorData) -> RumorData:
        """Update existing rumor"""
        entity = self.db_session.query(RumorEntity).filter(
            RumorEntity.id == rumor_data.id
        ).first()
        
        if not entity:
            raise ValueError(f"Rumor {rumor_data.id} not found")
        
        # Update fields
        entity.content = rumor_data.content
        entity.originator_id = rumor_data.originator_id
        entity.categories = rumor_data.categories
        entity.severity = rumor_data.severity
        entity.truth_value = rumor_data.truth_value
        entity.believability = rumor_data.believability
        entity.spread_count = rumor_data.spread_count
        entity.properties = rumor_data.properties
        entity.status = rumor_data.status
        
        self.db_session.commit()
        self.db_session.refresh(entity)
        
        return self._entity_to_business_data(entity)
    
    def delete_rumor(self, rumor_id: UUID) -> bool:
        """Delete rumor"""
        entity = self.db_session.query(RumorEntity).filter(
            RumorEntity.id == rumor_id
        ).first()
        
        if not entity:
            return False
        
        self.db_session.delete(entity)
        self.db_session.commit()
        
        return True
    
    def list_rumors(
        self, 
        page: int = 1, 
        size: int = 50, 
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[RumorData], int]:
        """List rumors with pagination"""
        query = self.db_session.query(RumorEntity)
        
        # Apply filters
        if status:
            query = query.filter(RumorEntity.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    RumorEntity.content.ilike(search_term),
                    RumorEntity.originator_id.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        entities = query.offset(offset).limit(size).all()
        
        # Convert to business data
        rumors = [self._entity_to_business_data(entity) for entity in entities]
        
        return rumors, total
    
    def get_rumor_statistics(self) -> Dict[str, Any]:
        """Get rumor statistics"""
        total_rumors = self.db_session.query(RumorEntity).count()
        active_rumors = self.db_session.query(RumorEntity).filter(
            RumorEntity.status == 'active'
        ).count()
        
        # Get severity distribution
        severity_stats = self.db_session.query(
            RumorEntity.severity,
            func.count(RumorEntity.id)
        ).group_by(RumorEntity.severity).all()
        
        severity_distribution = {severity: count for severity, count in severity_stats}
        
        # Get average metrics
        avg_truth = self.db_session.query(
            func.avg(RumorEntity.truth_value)
        ).scalar() or 0.0
        
        avg_believability = self.db_session.query(
            func.avg(RumorEntity.believability)
        ).scalar() or 0.0
        
        avg_spread = self.db_session.query(
            func.avg(RumorEntity.spread_count)
        ).scalar() or 0.0
        
        return {
            "total_rumors": total_rumors,
            "active_rumors": active_rumors,
            "severity_distribution": severity_distribution,
            "average_truth_value": round(float(avg_truth), 2),
            "average_believability": round(float(avg_believability), 2),
            "average_spread_count": round(float(avg_spread), 2)
        }
    
    def _entity_to_business_data(self, entity: RumorEntity) -> RumorData:
        """Convert database entity to business data"""
        return RumorData(
            id=entity.id,
            content=entity.content,
            originator_id=entity.originator_id,
            categories=entity.categories or [],
            severity=entity.severity,
            truth_value=entity.truth_value,
            believability=entity.believability,
            spread_count=entity.spread_count,
            properties=entity.properties or {},
            status=entity.status,
            created_at=entity.created_at
        )
    
    def _business_data_to_entity(self, rumor_data: RumorData) -> RumorEntity:
        """Convert business data to database entity"""
        return RumorEntity(
            id=rumor_data.id,
            content=rumor_data.content,
            originator_id=rumor_data.originator_id,
            categories=rumor_data.categories,
            severity=rumor_data.severity,
            truth_value=rumor_data.truth_value,
            believability=rumor_data.believability,
            spread_count=rumor_data.spread_count,
            properties=rumor_data.properties,
            status=rumor_data.status,
            created_at=rumor_data.created_at
        )


# Factory function for dependency injection
def create_rumor_repository(db_session: Session) -> SQLAlchemyRumorRepository:
    """Factory function to create rumor repository"""
    return SQLAlchemyRumorRepository(db_session) 