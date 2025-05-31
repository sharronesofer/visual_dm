"""
Region Repository

SQLAlchemy-based repository for region system data access.
Implements the repository pattern with comprehensive CRUD operations.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_, func
from sqlalchemy.exc import SQLAlchemyError

from backend.infrastructure.shared.database import Base, get_db_session
from backend.infrastructure.shared.repositories import BaseRepository
from backend.infrastructure.shared.exceptions import (
    RegionNotFoundError,
    RegionValidationError,
    RegionConflictError,
    RepositoryError
)
# Import directly from models.py to avoid circular import issues
import backend.systems.region.models as region_models
RegionEntity = region_models.Region
ContinentEntity = region_models.Continent
RegionMetadata = region_models.RegionMetadata
ContinentMetadata = region_models.ContinentMetadata
HexCoordinate = region_models.HexCoordinate
RegionType = region_models.RegionType
ClimateType = region_models.ClimateType

logger = logging.getLogger(__name__)


class RegionRepository(BaseRepository[RegionEntity]):
    """Repository for region entities"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, RegionEntity)
        self.db = db_session

    def create_region(
        self,
        name: str,
        biome_type: str,
        coordinates: Optional[Dict[str, int]] = None,
        **kwargs
    ) -> RegionEntity:
        """Create a new region"""
        try:
            # Validate unique name
            existing = self.get_by_name(name)
            if existing:
                raise RegionConflictError(f"Region with name '{name}' already exists")
            
            # Process coordinates
            hex_q, hex_r, hex_s = 0, 0, 0
            cartesian_x, cartesian_y = 0.0, 0.0
            
            if coordinates:
                hex_q = coordinates.get('q', 0)
                hex_r = coordinates.get('r', 0) 
                hex_s = coordinates.get('s', 0)
                cartesian_x = coordinates.get('x', 0.0)
                cartesian_y = coordinates.get('y', 0.0)
            
            # Create entity
            entity = RegionEntity(
                name=name,
                biome_type=biome_type,
                hex_q=hex_q,
                hex_r=hex_r,
                hex_s=hex_s,
                cartesian_x=cartesian_x,
                cartesian_y=cartesian_y,
                **kwargs
            )
            
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created region {entity.id}: {name}")
            return entity
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating region: {str(e)}")
            raise RepositoryError(f"Failed to create region: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating region: {str(e)}")
            raise

    def get_by_name(self, name: str) -> Optional[RegionEntity]:
        """Get region by name"""
        try:
            return self.db.query(RegionEntity).filter(
                and_(
                    RegionEntity.name == name,
                    RegionEntity.is_active == True
                )
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting region by name {name}: {str(e)}")
            raise RepositoryError(f"Failed to get region by name: {str(e)}")

    def get_by_coordinates(self, hex_q: int, hex_r: int, hex_s: int) -> Optional[RegionEntity]:
        """Get region by hex coordinates"""
        try:
            return self.db.query(RegionEntity).filter(
                and_(
                    RegionEntity.hex_q == hex_q,
                    RegionEntity.hex_r == hex_r,
                    RegionEntity.hex_s == hex_s,
                    RegionEntity.is_active == True
                )
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting region by coordinates: {str(e)}")
            raise RepositoryError(f"Failed to get region by coordinates: {str(e)}")

    def get_by_continent(self, continent_id: str) -> List[RegionEntity]:
        """Get all regions in a continent"""
        try:
            return self.db.query(RegionEntity).filter(
                and_(
                    RegionEntity.continent_id == continent_id,
                    RegionEntity.is_active == True
                )
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting regions by continent: {str(e)}")
            raise RepositoryError(f"Failed to get regions by continent: {str(e)}")

    def get_by_biome_type(self, biome_type: str) -> List[RegionEntity]:
        """Get all regions of a specific biome type"""
        try:
            return self.db.query(RegionEntity).filter(
                and_(
                    RegionEntity.biome_type == biome_type,
                    RegionEntity.is_active == True
                )
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting regions by biome: {str(e)}")
            raise RepositoryError(f"Failed to get regions by biome: {str(e)}")

    def get_neighbors(self, region_id: UUID, radius: int = 1) -> List[RegionEntity]:
        """Get neighboring regions within specified radius"""
        try:
            # Get the source region
            source = self.get_by_id(region_id)
            if not source:
                return []
            
            # Calculate neighbor coordinates (simplified hexagon neighbors)
            neighbors = []
            directions = [
                (1, -1, 0), (1, 0, -1), (0, 1, -1),
                (-1, 1, 0), (-1, 0, 1), (0, -1, 1)
            ]
            
            for dr_q, dr_r, dr_s in directions:
                for r in range(1, radius + 1):
                    neighbor_q = source.hex_q + dr_q * r
                    neighbor_r = source.hex_r + dr_r * r
                    neighbor_s = source.hex_s + dr_s * r
                    
                    neighbor = self.get_by_coordinates(neighbor_q, neighbor_r, neighbor_s)
                    if neighbor:
                        neighbors.append(neighbor)
            
            return neighbors
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting neighbors: {str(e)}")
            raise RepositoryError(f"Failed to get neighbors: {str(e)}")

    def search_regions(
        self,
        name_filter: Optional[str] = None,
        biome_types: Optional[List[str]] = None,
        continent_id: Optional[str] = None,
        min_population: Optional[int] = None,
        max_population: Optional[int] = None,
        page: int = 1,
        size: int = 50
    ) -> Tuple[List[RegionEntity], int]:
        """Search regions with advanced filters"""
        try:
            query = self.db.query(RegionEntity).filter(
                RegionEntity.is_active == True
            )
            
            # Apply filters
            if name_filter:
                query = query.filter(
                    or_(
                        RegionEntity.name.ilike(f"%{name_filter}%"),
                        RegionEntity.description.ilike(f"%{name_filter}%")
                    )
                )
            
            if biome_types:
                query = query.filter(RegionEntity.biome_type.in_(biome_types))
            
            if continent_id:
                query = query.filter(RegionEntity.continent_id == continent_id)
            
            if min_population is not None:
                query = query.filter(RegionEntity.total_population >= min_population)
            
            if max_population is not None:
                query = query.filter(RegionEntity.total_population <= max_population)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            results = query.order_by(RegionEntity.created_at.desc()).offset(offset).limit(size).all()
            
            return results, total
            
        except SQLAlchemyError as e:
            logger.error(f"Database error searching regions: {str(e)}")
            raise RepositoryError(f"Failed to search regions: {str(e)}")

    def update_population(self, region_id: UUID, population: int) -> Optional[RegionEntity]:
        """Update region population"""
        try:
            entity = self.get_by_id(region_id)
            if not entity:
                raise RegionNotFoundError(f"Region {region_id} not found")
            
            entity.total_population = population
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(entity)
            
            return entity
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating population: {str(e)}")
            raise RepositoryError(f"Failed to update population: {str(e)}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get region statistics"""
        try:
            total_regions = self.db.query(func.count(RegionEntity.id)).filter(
                RegionEntity.is_active == True
            ).scalar()
            
            total_population = self.db.query(func.sum(RegionEntity.total_population)).filter(
                RegionEntity.is_active == True
            ).scalar() or 0
            
            biome_distribution = {}
            biome_results = self.db.query(
                RegionEntity.biome_type,
                func.count(RegionEntity.id)
            ).filter(
                RegionEntity.is_active == True
            ).group_by(RegionEntity.biome_type).all()
            
            for biome, count in biome_results:
                biome_distribution[biome] = count
            
            return {
                "total_regions": total_regions,
                "total_population": total_population,
                "average_population": total_population / max(total_regions, 1),
                "biome_distribution": biome_distribution
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting statistics: {str(e)}")
            raise RepositoryError(f"Failed to get statistics: {str(e)}")


class ContinentRepository(BaseRepository[ContinentEntity]):
    """Repository for continent entities"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, ContinentEntity)
        self.db = db_session

    def create_continent(
        self,
        name: str,
        size: int = 30,
        **kwargs
    ) -> ContinentEntity:
        """Create a new continent"""
        try:
            # Validate unique name
            existing = self.get_by_name(name)
            if existing:
                raise RegionConflictError(f"Continent with name '{name}' already exists")
            
            entity = ContinentEntity(
                name=name,
                size=size,
                **kwargs
            )
            
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created continent {entity.id}: {name}")
            return entity
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating continent: {str(e)}")
            raise RepositoryError(f"Failed to create continent: {str(e)}")

    def get_by_name(self, name: str) -> Optional[ContinentEntity]:
        """Get continent by name"""
        try:
            return self.db.query(ContinentEntity).filter(
                and_(
                    ContinentEntity.name == name,
                    ContinentEntity.is_active == True
                )
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting continent by name: {str(e)}")
            raise RepositoryError(f"Failed to get continent by name: {str(e)}")

    def add_region_to_continent(self, continent_id: UUID, region_id: UUID) -> bool:
        """Add a region to a continent"""
        try:
            continent = self.get_by_id(continent_id)
            if not continent:
                raise RegionNotFoundError(f"Continent {continent_id} not found")
            
            # Update region data in continent
            region_data = continent.region_data or {}
            region_ids = region_data.get("region_ids", [])
            
            if str(region_id) not in region_ids:
                region_ids.append(str(region_id))
                region_data["region_ids"] = region_ids
                continent.region_data = region_data
                continent.updated_at = datetime.utcnow()
                
                self.db.commit()
                return True
            
            return False  # Already exists
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error adding region to continent: {str(e)}")
            raise RepositoryError(f"Failed to add region to continent: {str(e)}")


# Factory functions for dependency injection
def get_region_repository(db_session: Optional[Session] = None) -> RegionRepository:
    """Get region repository instance"""
    if db_session is None:
        db_session = next(get_db())
    return RegionRepository(db_session)


def get_continent_repository(db_session: Optional[Session] = None) -> ContinentRepository:
    """Get continent repository instance"""
    if db_session is None:
        db_session = next(get_db())
    return ContinentRepository(db_session) 