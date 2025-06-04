"""
Population Repository - Infrastructure

This module provides data access for the population system
according to the Development Bible standards, following the faction system pattern.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.population.models.population import (
    PopulationData,
    create_population_data_from_dict,
    population_data_to_dict
)
from backend.infrastructure.models.population.models import PopulationEntity


class SQLAlchemyPopulationRepository:
    """SQLAlchemy implementation of population repository"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_population_by_id(self, population_id: UUID) -> Optional[PopulationData]:
        """Get population by ID"""
        entity = self.db_session.query(PopulationEntity).filter(
            PopulationEntity.id == population_id
        ).first()
        
        if not entity:
            return None
        
        return self._entity_to_domain_model(entity)
    
    def get_population_by_name(self, name: str) -> Optional[PopulationData]:
        """Get population by name"""
        entity = self.db_session.query(PopulationEntity).filter(
            PopulationEntity.name == name
        ).first()
        
        if not entity:
            return None
        
        return self._entity_to_domain_model(entity)
    
    def create_population(self, population_data: PopulationData) -> PopulationData:
        """Create a new population"""
        entity = PopulationEntity(
            id=population_data.id,
            name=population_data.name,
            description=population_data.description,
            status=population_data.status,
            properties=population_data.properties,
            is_active=population_data.is_active,
            population_count=population_data.population_count,
            capacity=population_data.capacity,
            growth_rate=population_data.growth_rate,
            state=population_data.state,
            previous_state=population_data.previous_state,
            casualties=population_data.casualties,
            refugees=population_data.refugees,
            last_war_impact=population_data.last_war_impact,
            last_war_date=population_data.last_war_date,
            catastrophe_deaths=population_data.catastrophe_deaths,
            catastrophe_displaced=population_data.catastrophe_displaced,
            catastrophe_injured=population_data.catastrophe_injured,
            last_catastrophe_impact=population_data.last_catastrophe_impact,
            last_catastrophe_date=population_data.last_catastrophe_date,
            shortage_deaths=population_data.shortage_deaths,
            shortage_migrants=population_data.shortage_migrants,
            last_shortage_impact=population_data.last_shortage_impact,
            last_shortage_date=population_data.last_shortage_date,
            last_migration_in=population_data.last_migration_in,
            last_migration_out=population_data.last_migration_out,
            last_migration_date=population_data.last_migration_date,
            state_history=population_data.state_history,
            state_transition_date=population_data.state_transition_date,
            resources=population_data.resources,
            resource_modifier=population_data.resource_modifier,
            created_at=population_data.created_at or datetime.utcnow(),
            updated_at=population_data.updated_at
        )
        
        self.db_session.add(entity)
        self.db_session.commit()
        self.db_session.refresh(entity)
        
        return self._entity_to_domain_model(entity)
    
    def update_population(self, population_data: PopulationData) -> PopulationData:
        """Update existing population"""
        entity = self.db_session.query(PopulationEntity).filter(
            PopulationEntity.id == population_data.id
        ).first()
        
        if not entity:
            raise ValueError(f"Population {population_data.id} not found")
        
        # Update entity with new data
        entity.name = population_data.name
        entity.description = population_data.description
        entity.status = population_data.status
        entity.properties = population_data.properties
        entity.is_active = population_data.is_active
        entity.population_count = population_data.population_count
        entity.capacity = population_data.capacity
        entity.growth_rate = population_data.growth_rate
        entity.state = population_data.state
        entity.previous_state = population_data.previous_state
        entity.casualties = population_data.casualties
        entity.refugees = population_data.refugees
        entity.last_war_impact = population_data.last_war_impact
        entity.last_war_date = population_data.last_war_date
        entity.catastrophe_deaths = population_data.catastrophe_deaths
        entity.catastrophe_displaced = population_data.catastrophe_displaced
        entity.catastrophe_injured = population_data.catastrophe_injured
        entity.last_catastrophe_impact = population_data.last_catastrophe_impact
        entity.last_catastrophe_date = population_data.last_catastrophe_date
        entity.shortage_deaths = population_data.shortage_deaths
        entity.shortage_migrants = population_data.shortage_migrants
        entity.last_shortage_impact = population_data.last_shortage_impact
        entity.last_shortage_date = population_data.last_shortage_date
        entity.last_migration_in = population_data.last_migration_in
        entity.last_migration_out = population_data.last_migration_out
        entity.last_migration_date = population_data.last_migration_date
        entity.state_history = population_data.state_history
        entity.state_transition_date = population_data.state_transition_date
        entity.resources = population_data.resources
        entity.resource_modifier = population_data.resource_modifier
        entity.updated_at = population_data.updated_at or datetime.utcnow()
        
        self.db_session.commit()
        self.db_session.refresh(entity)
        
        return self._entity_to_domain_model(entity)
    
    def delete_population(self, population_id: UUID) -> bool:
        """Delete population"""
        entity = self.db_session.query(PopulationEntity).filter(
            PopulationEntity.id == population_id
        ).first()
        
        if not entity:
            return False
        
        # Soft delete by setting is_active to False
        entity.is_active = False
        entity.status = 'archived'
        entity.updated_at = datetime.utcnow()
        
        self.db_session.commit()
        return True
    
    def list_populations(self, 
                        page: int = 1, 
                        size: int = 50, 
                        status: Optional[str] = None,
                        search: Optional[str] = None) -> Tuple[List[PopulationData], int]:
        """List populations with pagination"""
        query = self.db_session.query(PopulationEntity)
        
        # Apply filters
        if status:
            query = query.filter(PopulationEntity.status == status)
        
        if search:
            query = query.filter(
                or_(
                    PopulationEntity.name.ilike(f"%{search}%"),
                    PopulationEntity.description.ilike(f"%{search}%")
                )
            )
        
        # Only active populations by default
        query = query.filter(PopulationEntity.is_active == True)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        entities = query.offset(offset).limit(size).all()
        
        # Convert to domain models
        populations = [self._entity_to_domain_model(entity) for entity in entities]
        
        return populations, total
    
    def get_population_statistics(self) -> Dict[str, Any]:
        """Get population statistics"""
        total_populations = self.db_session.query(PopulationEntity).filter(
            PopulationEntity.is_active == True
        ).count()
        
        active_populations = self.db_session.query(PopulationEntity).filter(
            and_(
                PopulationEntity.is_active == True,
                PopulationEntity.status == 'active'
            )
        ).count()
        
        inactive_populations = self.db_session.query(PopulationEntity).filter(
            and_(
                PopulationEntity.is_active == True,
                PopulationEntity.status == 'inactive'
            )
        ).count()
        
        # Calculate total population count
        total_population_count = self.db_session.query(
            func.sum(PopulationEntity.population_count)
        ).filter(
            and_(
                PopulationEntity.is_active == True,
                PopulationEntity.population_count.isnot(None)
            )
        ).scalar() or 0
        
        # Calculate average population count
        avg_population_count = self.db_session.query(
            func.avg(PopulationEntity.population_count)
        ).filter(
            and_(
                PopulationEntity.is_active == True,
                PopulationEntity.population_count.isnot(None)
            )
        ).scalar() or 0.0
        
        return {
            "total_populations": total_populations,
            "active_populations": active_populations,
            "inactive_populations": inactive_populations,
            "archived_populations": total_populations - active_populations - inactive_populations,
            "total_population_count": int(total_population_count),
            "average_population_count": float(avg_population_count),
            "system_health": "healthy" if active_populations > 0 else "needs_attention"
        }
    
    def _entity_to_domain_model(self, entity: PopulationEntity) -> PopulationData:
        """Convert database entity to domain model"""
        return PopulationData(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            status=entity.status,
            properties=entity.properties,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_active=entity.is_active,
            population_count=entity.population_count,
            capacity=entity.capacity,
            growth_rate=entity.growth_rate,
            state=entity.state,
            previous_state=entity.previous_state,
            casualties=entity.casualties,
            refugees=entity.refugees,
            last_war_impact=entity.last_war_impact,
            last_war_date=entity.last_war_date,
            catastrophe_deaths=entity.catastrophe_deaths,
            catastrophe_displaced=entity.catastrophe_displaced,
            catastrophe_injured=entity.catastrophe_injured,
            last_catastrophe_impact=entity.last_catastrophe_impact,
            last_catastrophe_date=entity.last_catastrophe_date,
            shortage_deaths=entity.shortage_deaths,
            shortage_migrants=entity.shortage_migrants,
            last_shortage_impact=entity.last_shortage_impact,
            last_shortage_date=entity.last_shortage_date,
            last_migration_in=entity.last_migration_in,
            last_migration_out=entity.last_migration_out,
            last_migration_date=entity.last_migration_date,
            state_history=entity.state_history,
            state_transition_date=entity.state_transition_date,
            resources=entity.resources,
            resource_modifier=entity.resource_modifier
        )


def create_population_repository(db_session: Session) -> SQLAlchemyPopulationRepository:
    """Factory function to create population repository"""
    return SQLAlchemyPopulationRepository(db_session) 