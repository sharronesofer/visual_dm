"""
Population System Services

This module provides business logic services for the population system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.population.models import (
    PopulationEntity,
    PopulationModel,
    CreatePopulationRequest,
    UpdatePopulationRequest,
    PopulationResponse
)
from backend.systems.population.utils.population_utils import (
    calculate_war_impact,
    calculate_catastrophe_impact,
    calculate_resource_consumption,
    calculate_resource_shortage_impact,
    calculate_migration_impact,
    calculate_seasonal_growth_modifier,
    calculate_seasonal_death_rate_modifier,
    WarImpactSeverity,
    CatastropheType
)
from backend.systems.population.utils.state_utils import (
    is_valid_transition,
    is_valid_state_progression,
    estimate_time_to_state,
    get_poi_status_description,
    PopulationState,
    StateTransition
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    PopulationNotFoundError,
    PopulationValidationError,
    PopulationConflictError
)

logger = logging.getLogger(__name__)


class PopulationService(BaseService[PopulationEntity]):
    """Service class for population business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, PopulationEntity)
        self.db = db_session

    async def create_population(
        self, 
        request: CreatePopulationRequest,
        user_id: Optional[UUID] = None
    ) -> PopulationResponse:
        """Create a new population"""
        try:
            logger.info(f"Creating population: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise PopulationConflictError(f"Population with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = PopulationEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created population {entity.id} successfully")
            return PopulationResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating population: {str(e)}")
            self.db.rollback()
            raise

    async def get_population_by_id(self, population_id: UUID) -> Optional[PopulationResponse]:
        """Get population by ID"""
        try:
            entity = self.db.query(PopulationEntity).filter(
                PopulationEntity.id == population_id,
                PopulationEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return PopulationResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting population {population_id}: {str(e)}")
            raise

    async def update_population(
        self, 
        population_id: UUID, 
        request: UpdatePopulationRequest
    ) -> PopulationResponse:
        """Update existing population"""
        try:
            entity = await self._get_entity_by_id(population_id)
            if not entity:
                raise PopulationNotFoundError(f"Population {population_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated population {entity.id} successfully")
            return PopulationResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating population {population_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_population(self, population_id: UUID) -> bool:
        """Soft delete population"""
        try:
            entity = await self._get_entity_by_id(population_id)
            if not entity:
                raise PopulationNotFoundError(f"Population {population_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted population {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting population {population_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_populations(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[PopulationResponse], int]:
        """List populations with pagination and filters"""
        try:
            query = self.db.query(PopulationEntity).filter(
                PopulationEntity.is_active == True
            )
            
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
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(PopulationEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [PopulationResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing populations: {str(e)}")
            raise

    async def get_population_statistics(self) -> Dict[str, Any]:
        """Get population system statistics"""
        try:
            total_count = self.db.query(func.count(PopulationEntity.id)).filter(
                PopulationEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(PopulationEntity.id)).filter(
                PopulationEntity.is_active == True,
                PopulationEntity.status == "active"
            ).scalar()
            
            return {
                "total_populations": total_count,
                "active_populations": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting population statistics: {e}")
            raise

    # ============================================================================
    # WAR IMPACT SERVICE METHODS
    # ============================================================================

    async def handle_war_impact(self, population_id: UUID, war_intensity: float, 
                               duration_days: int, defensive_strength: float = 0.5) -> Dict[str, Any]:
        """Handle war impact on a population"""
        try:
            # Import utility function
            from backend.systems.population.utils import calculate_war_impact
            
            # Get current population
            entity = await self._get_entity_by_id(population_id)
            if not entity:
                raise PopulationNotFoundError(f"Population {population_id} not found")
            
            current_population = entity.properties.get("population_count", 1000)
            
            # Calculate impact
            impact_result = calculate_war_impact(
                population=current_population,
                war_intensity=war_intensity,
                duration_days=duration_days,
                defensive_strength=defensive_strength
            )
            
            # Update population entity
            entity.properties.update({
                "population_count": impact_result["remaining_population"],
                "casualties": impact_result["casualties"],
                "refugees": impact_result["refugees"],
                "last_war_impact": impact_result,
                "last_war_date": datetime.utcnow().isoformat()
            })
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"War impact applied to population {population_id}: {impact_result['casualties']} casualties")
            
            return {
                "population_id": str(population_id),
                "impact_result": impact_result,
                "updated_entity": PopulationResponse.from_orm(entity)
            }
            
        except Exception as e:
            logger.error(f"Error handling war impact: {e}")
            self.db.rollback()
            raise

    # ============================================================================
    # CATASTROPHE SERVICE METHODS
    # ============================================================================

    async def handle_catastrophe(self, population_id: UUID, catastrophe_type: str,
                               severity: float, preparedness: float = 0.3) -> Dict[str, Any]:
        """Handle catastrophe impact on a population"""
        try:
            # Import utility function
            from backend.systems.population.utils import calculate_catastrophe_impact
            
            # Get current population
            entity = await self._get_entity_by_id(population_id)
            if not entity:
                raise PopulationNotFoundError(f"Population {population_id} not found")
            
            current_population = entity.properties.get("population_count", 1000)
            
            # Calculate impact
            impact_result = calculate_catastrophe_impact(
                population=current_population,
                catastrophe_type=catastrophe_type,
                severity=severity,
                preparedness=preparedness
            )
            
            # Update population entity
            entity.properties.update({
                "population_count": impact_result["remaining_population"],
                "catastrophe_deaths": impact_result["deaths"],
                "catastrophe_displaced": impact_result["displaced"],
                "catastrophe_injured": impact_result["injured"],
                "last_catastrophe_impact": impact_result,
                "last_catastrophe_date": datetime.utcnow().isoformat()
            })
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Catastrophe impact applied to population {population_id}: {catastrophe_type} caused {impact_result['deaths']} deaths")
            
            return {
                "population_id": str(population_id),
                "impact_result": impact_result,
                "updated_entity": PopulationResponse.from_orm(entity)
            }
            
        except Exception as e:
            logger.error(f"Error handling catastrophe: {e}")
            self.db.rollback()
            raise

    # ============================================================================
    # RESOURCE MANAGEMENT SERVICE METHODS
    # ============================================================================

    async def handle_resource_shortage(self, population_id: UUID, resource_type: str,
                                     shortage_percentage: float, duration_days: int) -> Dict[str, Any]:
        """Handle resource shortage impact on a population"""
        try:
            # Import utility function
            from backend.systems.population.utils import calculate_resource_shortage_impact
            
            # Get current population
            entity = await self._get_entity_by_id(population_id)
            if not entity:
                raise PopulationNotFoundError(f"Population {population_id} not found")
            
            current_population = entity.properties.get("population_count", 1000)
            
            # Calculate impact
            impact_result = calculate_resource_shortage_impact(
                population=current_population,
                resource_type=resource_type,
                shortage_percentage=shortage_percentage,
                duration_days=duration_days
            )
            
            # Update population entity
            entity.properties.update({
                "population_count": impact_result["remaining_population"],
                "shortage_deaths": impact_result["deaths"],
                "shortage_migrants": impact_result["migrants"],
                "last_shortage_impact": impact_result,
                "last_shortage_date": datetime.utcnow().isoformat()
            })
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Resource shortage impact applied to population {population_id}: {resource_type} shortage caused {impact_result['deaths']} deaths")
            
            return {
                "population_id": str(population_id),
                "impact_result": impact_result,
                "updated_entity": PopulationResponse.from_orm(entity)
            }
            
        except Exception as e:
            logger.error(f"Error handling resource shortage: {e}")
            self.db.rollback()
            raise

    # ============================================================================
    # MIGRATION SERVICE METHODS
    # ============================================================================

    async def handle_migration(self, origin_id: UUID, destination_id: UUID,
                             push_factors: Dict[str, float], pull_factors: Dict[str, float],
                             distance_km: float = 100.0) -> Dict[str, Any]:
        """Handle population migration between locations"""
        try:
            # Import utility function
            from backend.systems.population.utils import calculate_migration_impact
            
            # Get origin and destination populations
            origin_entity = await self._get_entity_by_id(origin_id)
            destination_entity = await self._get_entity_by_id(destination_id)
            
            if not origin_entity:
                raise PopulationNotFoundError(f"Origin population {origin_id} not found")
            if not destination_entity:
                raise PopulationNotFoundError(f"Destination population {destination_id} not found")
            
            origin_population = origin_entity.properties.get("population_count", 1000)
            destination_capacity = destination_entity.properties.get("capacity", 2000)
            destination_current = destination_entity.properties.get("population_count", 500)
            available_capacity = max(0, destination_capacity - destination_current)
            
            # Calculate migration
            migration_result = calculate_migration_impact(
                origin_population=origin_population,
                destination_capacity=available_capacity,
                push_factors=push_factors,
                pull_factors=pull_factors,
                distance_km=distance_km
            )
            
            # Update both entities
            origin_entity.properties.update({
                "population_count": migration_result["remaining_at_origin"],
                "last_migration_out": migration_result["actual_migrants"],
                "last_migration_date": datetime.utcnow().isoformat()
            })
            
            destination_entity.properties.update({
                "population_count": destination_current + migration_result["actual_migrants"],
                "last_migration_in": migration_result["actual_migrants"],
                "last_migration_date": datetime.utcnow().isoformat()
            })
            
            origin_entity.updated_at = datetime.utcnow()
            destination_entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(origin_entity)
            self.db.refresh(destination_entity)
            
            logger.info(f"Migration handled: {migration_result['actual_migrants']} people moved from {origin_id} to {destination_id}")
            
            return {
                "migration_result": migration_result,
                "origin_entity": PopulationResponse.from_orm(origin_entity),
                "destination_entity": PopulationResponse.from_orm(destination_entity)
            }
            
        except Exception as e:
            logger.error(f"Error handling migration: {e}")
            self.db.rollback()
            raise

    # ============================================================================
    # STATE MANAGEMENT SERVICE METHODS
    # ============================================================================

    async def transition_population_state(self, population_id: UUID, target_state: str) -> PopulationResponse:
        """Transition population to a new state with validation"""
        try:
            # Import utility functions
            from backend.systems.population.utils import is_valid_transition, is_valid_state_progression
            
            entity = await self._get_entity_by_id(population_id)
            if not entity:
                raise PopulationNotFoundError(f"Population {population_id} not found")
            
            current_state = entity.properties.get("state", "small")
            current_population = entity.properties.get("population_count", 1000)
            resources = entity.properties.get("resources", {})
            state_history = entity.properties.get("state_history", [])
            
            # Validate transition
            if not is_valid_transition(current_state, target_state, current_population, resources):
                raise PopulationValidationError(f"Invalid state transition from {current_state} to {target_state}")
            
            # Check state progression validity
            updated_history = state_history + [{
                "state": target_state,
                "timestamp": datetime.utcnow().isoformat(),
                "population": current_population
            }]
            
            if not is_valid_state_progression(updated_history):
                raise PopulationValidationError("State progression too rapid or invalid pattern")
            
            # Update entity
            entity.properties.update({
                "state": target_state,
                "previous_state": current_state,
                "state_history": updated_history,
                "state_transition_date": datetime.utcnow().isoformat()
            })
            entity.status = target_state
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Population {population_id} transitioned from {current_state} to {target_state}")
            return PopulationResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error transitioning population state: {e}")
            self.db.rollback()
            raise

    async def estimate_state_transition_time(self, population_id: UUID, target_state: str) -> Optional[int]:
        """Estimate time required for state transition"""
        try:
            # Import utility function
            from backend.systems.population.utils import estimate_time_to_state
            
            entity = await self._get_entity_by_id(population_id)
            if not entity:
                raise PopulationNotFoundError(f"Population {population_id} not found")
            
            current_state = entity.properties.get("state", "small")
            current_population = entity.properties.get("population_count", 1000)
            growth_rate = entity.properties.get("growth_rate", 0.02)
            resource_modifier = entity.properties.get("resource_modifier", 1.0)
            
            # Calculate estimate
            estimated_days = estimate_time_to_state(
                current_population=current_population,
                current_state=current_state,
                target_state=target_state,
                growth_rate=growth_rate,
                resource_modifier=resource_modifier
            )
            
            logger.info(f"State transition estimate for {population_id}: {estimated_days} days to reach {target_state}")
            return estimated_days
            
        except Exception as e:
            logger.error(f"Error estimating state transition time: {e}")
            raise

    async def _get_by_name(self, name: str) -> Optional[PopulationEntity]:
        """Get entity by name"""
        return self.db.query(PopulationEntity).filter(
            PopulationEntity.name == name,
            PopulationEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[PopulationEntity]:
        """Get entity by ID"""
        return self.db.query(PopulationEntity).filter(
            PopulationEntity.id == entity_id,
            PopulationEntity.is_active == True
        ).first()


def create_population_service(db_session: Session) -> PopulationService:
    """Create and return a PopulationService instance"""
    return PopulationService(db_session)
