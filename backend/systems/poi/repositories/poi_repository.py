"""
POI Repository for database operations.

Provides data access layer for Point of Interest entities with specialized
queries and operations.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.systems.poi.models import (
    PoiEntity,
    POIType,
    POIState,
    POIInteractionType,
    CreatePoiRequest,
    UpdatePoiRequest
)
from backend.systems.poi.repositories.base_repository import PoiBaseRepository
from backend.infrastructure.shared.exceptions import RepositoryError

logger = logging.getLogger(__name__)


class PoiRepository(PoiBaseRepository[PoiEntity, CreatePoiRequest, UpdatePoiRequest]):
    """
    Repository for POI entity operations.
    
    Provides specialized database operations for Points of Interest including
    location-based queries, faction and region filtering, and population management.
    """
    
    def __init__(self, db_session: Session):
        """Initialize POI repository with database session."""
        super().__init__(PoiEntity, db_session)
    
    def get_by_name(self, name: str) -> Optional[PoiEntity]:
        """
        Get POI by exact name.
        
        Args:
            name: POI name
            
        Returns:
            POI entity if found, None otherwise
        """
        return self.get_by_field("name", name)
    
    def get_by_region(self, region_id: UUID) -> List[PoiEntity]:
        """
        Get all POIs in a specific region.
        
        Args:
            region_id: Region ID
            
        Returns:
            List of POI entities in the region
        """
        try:
            query = self.db.query(self.model).filter(
                and_(
                    self.model.region_id == region_id,
                    self.model.is_active == True
                )
            )
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting POIs by region {region_id}: {str(e)}")
            raise RepositoryError(f"Failed to get POIs by region: {str(e)}")
    
    def get_by_faction(self, faction_id: UUID) -> List[PoiEntity]:
        """
        Get all POIs controlled by a specific faction.
        
        Args:
            faction_id: Faction ID
            
        Returns:
            List of POI entities controlled by the faction
        """
        try:
            query = self.db.query(self.model).filter(
                and_(
                    self.model.faction_id == faction_id,
                    self.model.is_active == True
                )
            )
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting POIs by faction {faction_id}: {str(e)}")
            raise RepositoryError(f"Failed to get POIs by faction: {str(e)}")
    
    def get_by_type(self, poi_type: POIType) -> List[PoiEntity]:
        """
        Get all POIs of a specific type.
        
        Args:
            poi_type: POI type
            
        Returns:
            List of POI entities of the specified type
        """
        try:
            query = self.db.query(self.model).filter(
                and_(
                    self.model.poi_type == poi_type.value,
                    self.model.is_active == True
                )
            )
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting POIs by type {poi_type}: {str(e)}")
            raise RepositoryError(f"Failed to get POIs by type: {str(e)}")
    
    def get_by_state(self, state: POIState) -> List[PoiEntity]:
        """
        Get all POIs in a specific state.
        
        Args:
            state: POI state
            
        Returns:
            List of POI entities in the specified state
        """
        try:
            query = self.db.query(self.model).filter(
                and_(
                    self.model.state == state.value,
                    self.model.is_active == True
                )
            )
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting POIs by state {state}: {str(e)}")
            raise RepositoryError(f"Failed to get POIs by state: {str(e)}")
    
    def get_by_interaction_type(self, interaction_type: POIInteractionType) -> List[PoiEntity]:
        """
        Get all POIs with a specific interaction type.
        
        Args:
            interaction_type: POI interaction type
            
        Returns:
            List of POI entities with the specified interaction type
        """
        try:
            query = self.db.query(self.model).filter(
                and_(
                    self.model.interaction_type == interaction_type.value,
                    self.model.is_active == True
                )
            )
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting POIs by interaction type {interaction_type}: {str(e)}")
            raise RepositoryError(f"Failed to get POIs by interaction type: {str(e)}")
    
    def get_nearby_pois(
        self, 
        x: float, 
        y: float, 
        radius: float,
        poi_types: Optional[List[POIType]] = None,
        exclude_self: Optional[UUID] = None
    ) -> List[PoiEntity]:
        """
        Get POIs within a specific radius of coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            radius: Search radius
            poi_types: Optional list of POI types to filter by
            exclude_self: Optional POI ID to exclude from results
            
        Returns:
            List of POI entities within radius
        """
        try:
            # Calculate distance using Pythagorean theorem
            distance_expr = func.sqrt(
                func.pow(self.model.location_x - x, 2) + 
                func.pow(self.model.location_y - y, 2)
            )
            
            query = self.db.query(self.model).filter(
                and_(
                    distance_expr <= radius,
                    self.model.is_active == True,
                    self.model.location_x.isnot(None),
                    self.model.location_y.isnot(None)
                )
            )
            
            if poi_types:
                type_values = [poi_type.value for poi_type in poi_types]
                query = query.filter(self.model.poi_type.in_(type_values))
            
            if exclude_self:
                query = query.filter(self.model.id != exclude_self)
            
            # Order by distance
            query = query.order_by(distance_expr)
            
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting nearby POIs: {str(e)}")
            raise RepositoryError(f"Failed to get nearby POIs: {str(e)}")
    
    def get_population_range(
        self, 
        min_population: Optional[int] = None,
        max_population: Optional[int] = None
    ) -> List[PoiEntity]:
        """
        Get POIs within a population range.
        
        Args:
            min_population: Minimum population (optional)
            max_population: Maximum population (optional)
            
        Returns:
            List of POI entities within population range
        """
        try:
            query = self.db.query(self.model).filter(
                and_(
                    self.model.is_active == True,
                    self.model.population.isnot(None)
                )
            )
            
            if min_population is not None:
                query = query.filter(self.model.population >= min_population)
                
            if max_population is not None:
                query = query.filter(self.model.population <= max_population)
            
            return query.order_by(self.model.population.desc()).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting POIs by population range: {str(e)}")
            raise RepositoryError(f"Failed to get POIs by population range: {str(e)}")
    
    def search_advanced(
        self,
        *,
        name_pattern: Optional[str] = None,
        poi_types: Optional[List[POIType]] = None,
        states: Optional[List[POIState]] = None,
        interaction_types: Optional[List[POIInteractionType]] = None,
        region_id: Optional[UUID] = None,
        faction_id: Optional[UUID] = None,
        min_population: Optional[int] = None,
        max_population: Optional[int] = None,
        location_bounds: Optional[Tuple[float, float, float, float]] = None,  # (min_x, min_y, max_x, max_y)
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> Tuple[List[PoiEntity], int]:
        """
        Advanced search with multiple filters.
        
        Args:
            name_pattern: Name pattern to search for
            poi_types: List of POI types to filter by
            states: List of POI states to filter by  
            interaction_types: List of interaction types to filter by
            region_id: Region ID to filter by
            faction_id: Faction ID to filter by
            min_population: Minimum population
            max_population: Maximum population
            location_bounds: Bounding box for location filtering
            skip: Number of records to skip
            limit: Maximum records to return
            order_by: Field to order by
            order_desc: Whether to order in descending order
            
        Returns:
            Tuple of (POI entities, total count)
        """
        try:
            query = self.db.query(self.model).filter(self.model.is_active == True)
            
            # Name pattern search
            if name_pattern:
                query = query.filter(
                    or_(
                        self.model.name.ilike(f"%{name_pattern}%"),
                        self.model.description.ilike(f"%{name_pattern}%")
                    )
                )
            
            # POI type filter
            if poi_types:
                type_values = [poi_type.value for poi_type in poi_types]
                query = query.filter(self.model.poi_type.in_(type_values))
            
            # State filter
            if states:
                state_values = [state.value for state in states]
                query = query.filter(self.model.state.in_(state_values))
            
            # Interaction type filter
            if interaction_types:
                interaction_values = [it.value for it in interaction_types]
                query = query.filter(self.model.interaction_type.in_(interaction_values))
            
            # Region filter
            if region_id:
                query = query.filter(self.model.region_id == region_id)
            
            # Faction filter
            if faction_id:
                query = query.filter(self.model.faction_id == faction_id)
            
            # Population range filter
            if min_population is not None:
                query = query.filter(self.model.population >= min_population)
            if max_population is not None:
                query = query.filter(self.model.population <= max_population)
            
            # Location bounds filter
            if location_bounds:
                min_x, min_y, max_x, max_y = location_bounds
                query = query.filter(
                    and_(
                        self.model.location_x >= min_x,
                        self.model.location_x <= max_x,
                        self.model.location_y >= min_y,
                        self.model.location_y <= max_y
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply ordering
            if hasattr(self.model, order_by):
                order_field = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(order_field.desc())
                else:
                    query = query.order_by(order_field.asc())
            
            # Apply pagination
            entities = query.offset(skip).limit(limit).all()
            
            return entities, total
            
        except SQLAlchemyError as e:
            logger.error(f"Error in advanced POI search: {str(e)}")
            raise RepositoryError(f"Failed to perform advanced POI search: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get POI system statistics.
        
        Returns:
            Dictionary with POI statistics
        """
        try:
            total_pois = self.count({"is_active": True})
            
            # Count by type
            type_counts = {}
            for poi_type in POIType:
                count = self.count({"poi_type": poi_type.value, "is_active": True})
                type_counts[poi_type.value] = count
            
            # Count by state
            state_counts = {}
            for state in POIState:
                count = self.count({"state": state.value, "is_active": True})
                state_counts[state.value] = count
            
            # Count by interaction type
            interaction_counts = {}
            for interaction_type in POIInteractionType:
                count = self.count({"interaction_type": interaction_type.value, "is_active": True})
                interaction_counts[interaction_type.value] = count
            
            # Population statistics
            population_query = self.db.query(
                func.avg(self.model.population),
                func.min(self.model.population),
                func.max(self.model.population),
                func.sum(self.model.population)
            ).filter(
                and_(
                    self.model.is_active == True,
                    self.model.population.isnot(None)
                )
            ).first()
            
            avg_pop, min_pop, max_pop, total_pop = population_query or (0, 0, 0, 0)
            
            return {
                "total_pois": total_pois,
                "by_type": type_counts,
                "by_state": state_counts,
                "by_interaction_type": interaction_counts,
                "population": {
                    "total": int(total_pop) if total_pop else 0,
                    "average": float(avg_pop) if avg_pop else 0.0,
                    "minimum": int(min_pop) if min_pop else 0,
                    "maximum": int(max_pop) if max_pop else 0
                }
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting POI statistics: {str(e)}")
            raise RepositoryError(f"Failed to get POI statistics: {str(e)}")
    
    def update_population(self, poi_id: UUID, new_population: int) -> bool:
        """
        Update POI population.
        
        Args:
            poi_id: POI ID
            new_population: New population value
            
        Returns:
            True if updated successfully
        """
        try:
            poi = self.get(poi_id)
            if not poi:
                return False
            
            poi.population = new_population
            poi.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.debug(f"Updated POI {poi_id} population to {new_population}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating POI population: {str(e)}")
            raise RepositoryError(f"Failed to update POI population: {str(e)}")
    
    def change_state(self, poi_id: UUID, new_state: POIState) -> bool:
        """
        Change POI state.
        
        Args:
            poi_id: POI ID
            new_state: New POI state
            
        Returns:
            True if changed successfully
        """
        try:
            poi = self.get(poi_id)
            if not poi:
                return False
            
            old_state = poi.state
            poi.state = new_state.value
            poi.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Changed POI {poi_id} state from {old_state} to {new_state.value}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error changing POI state: {str(e)}")
            raise RepositoryError(f"Failed to change POI state: {str(e)}")
    
    def transfer_faction_control(self, poi_id: UUID, new_faction_id: Optional[UUID]) -> bool:
        """
        Transfer POI control to a different faction.
        
        Args:
            poi_id: POI ID
            new_faction_id: New controlling faction ID (None for neutral)
            
        Returns:
            True if transferred successfully
        """
        try:
            poi = self.get(poi_id)
            if not poi:
                return False
            
            old_faction = poi.faction_id
            poi.faction_id = new_faction_id
            poi.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Transferred POI {poi_id} control from faction {old_faction} to {new_faction_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error transferring POI faction control: {str(e)}")
            raise RepositoryError(f"Failed to transfer POI faction control: {str(e)}") 