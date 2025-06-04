"""
Continent Repository Implementation

Concrete repository implementation for continent data persistence.
Manages continent entities and their relationships with regions.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func

from backend.infrastructure.database import get_db_session
from backend.infrastructure.systems.region.models import ContinentDB
from backend.systems.region.models import ContinentMetadata, ClimateType, BiomeType
from backend.infrastructure.shared.exceptions import (
    RegionNotFoundError,
    RegionConflictError,
    RepositoryError
)


class ContinentRepository:
    """Concrete repository for continent data persistence."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create(self, continent_data: ContinentMetadata) -> ContinentMetadata:
        """Create a new continent in the database."""
        try:
            # Convert business model to database model
            continent_db = self._to_db_model(continent_data)
            
            self.db.add(continent_db)
            self.db.commit()
            self.db.refresh(continent_db)
            
            # Convert back to business model
            return self._to_business_model(continent_db)
            
        except IntegrityError as e:
            self.db.rollback()
            if "continents_name_key" in str(e):
                raise RegionConflictError(f"Continent with name '{continent_data.name}' already exists")
            raise RepositoryError(f"Database constraint violation: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to create continent: {str(e)}")
    
    def create_continent(self, name: str, description: str = None, generation_seed: int = None) -> ContinentMetadata:
        """Create a new continent with basic parameters."""
        continent_data = ContinentMetadata(
            name=name,
            description=description,
            generation_seed=generation_seed
        )
        return self.create(continent_data)
    
    def get_by_id(self, continent_id: UUID) -> Optional[ContinentMetadata]:
        """Retrieve a continent by its ID."""
        try:
            continent_db = self.db.query(ContinentDB).filter(ContinentDB.id == continent_id).first()
            
            if not continent_db:
                return None
            
            return self._to_business_model(continent_db)
            
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to retrieve continent {continent_id}: {str(e)}")
    
    def get_by_name(self, name: str) -> Optional[ContinentMetadata]:
        """Retrieve a continent by its name."""
        try:
            continent_db = self.db.query(ContinentDB).filter(ContinentDB.name == name).first()
            
            if not continent_db:
                return None
            
            return self._to_business_model(continent_db)
            
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to retrieve continent '{name}': {str(e)}")
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[ContinentMetadata]:
        """Retrieve all continents with pagination."""
        try:
            continents_db = (
                self.db.query(ContinentDB)
                .offset(offset)
                .limit(limit)
                .all()
            )
            
            return [self._to_business_model(continent_db) for continent_db in continents_db]
            
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to retrieve continents: {str(e)}")
    
    def update(self, continent_id: UUID, update_data: Dict[str, Any]) -> Optional[ContinentMetadata]:
        """Update an existing continent."""
        try:
            continent_db = self.db.query(ContinentDB).filter(ContinentDB.id == continent_id).first()
            
            if not continent_db:
                return None
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(continent_db, field) and value is not None:
                    setattr(continent_db, field, value)
            
            self.db.commit()
            self.db.refresh(continent_db)
            
            return self._to_business_model(continent_db)
            
        except IntegrityError as e:
            self.db.rollback()
            if "continents_name_key" in str(e):
                raise RegionConflictError(f"Continent name already exists")
            raise RepositoryError(f"Database constraint violation: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to update continent {continent_id}: {str(e)}")
    
    def delete(self, continent_id: UUID) -> bool:
        """Delete a continent."""
        try:
            continent_db = self.db.query(ContinentDB).filter(ContinentDB.id == continent_id).first()
            
            if not continent_db:
                return False
            
            self.db.delete(continent_db)
            self.db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to delete continent {continent_id}: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics about continents."""
        try:
            stats = {}
            
            # Total count
            stats['total_continents'] = self.db.query(func.count(ContinentDB.id)).scalar()
            
            # Area stats
            area_stats = self.db.query(
                func.sum(ContinentDB.total_area_square_km),
                func.avg(ContinentDB.total_area_square_km),
                func.max(ContinentDB.total_area_square_km),
                func.min(ContinentDB.total_area_square_km)
            ).first()
            
            stats['total_area'] = area_stats[0] or 0
            stats['average_area'] = float(area_stats[1] or 0)
            stats['max_area'] = area_stats[2] or 0
            stats['min_area'] = area_stats[3] or 0
            
            # Political situation distribution
            political_dist = (
                self.db.query(ContinentDB.political_situation, func.count(ContinentDB.id))
                .group_by(ContinentDB.political_situation)
                .all()
            )
            stats['political_distribution'] = {situation: count for situation, count in political_dist}
            
            return stats
            
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get continent statistics: {str(e)}")
    
    def _to_db_model(self, continent: ContinentMetadata) -> ContinentDB:
        """Convert business model to database model."""
        # Convert climate zones to strings
        climate_zones = []
        if continent.climate_zones:
            for climate in continent.climate_zones:
                if isinstance(climate, ClimateType):
                    climate_zones.append(climate.value)
                else:
                    climate_zones.append(str(climate))
        
        # Convert major biomes to strings
        major_biomes = []
        if continent.major_biomes:
            for biome in continent.major_biomes:
                if isinstance(biome, BiomeType):
                    major_biomes.append(biome.value)
                else:
                    major_biomes.append(str(biome))
        
        # Convert major powers to strings
        major_powers = []
        if continent.major_powers:
            for power in continent.major_powers:
                major_powers.append(str(power))
        
        # Create database model
        continent_db = ContinentDB(
            id=continent.id,
            name=continent.name,
            description=continent.description,
            total_area_square_km=continent.total_area_square_km,
            climate_zones=climate_zones,
            major_biomes=major_biomes,
            major_powers=major_powers,
            political_situation=continent.political_situation,
            generation_seed=continent.generation_seed,
            generation_parameters=continent.generation_parameters or {}
        )
        
        return continent_db
    
    def _to_business_model(self, continent_db: ContinentDB) -> ContinentMetadata:
        """Convert database model to business model."""
        # Convert climate zones from strings
        climate_zones = []
        if continent_db.climate_zones:
            for climate_str in continent_db.climate_zones:
                try:
                    climate_zones.append(ClimateType(climate_str))
                except ValueError:
                    # Skip invalid climate types
                    pass
        
        # Convert major biomes from strings
        major_biomes = []
        if continent_db.major_biomes:
            for biome_str in continent_db.major_biomes:
                try:
                    major_biomes.append(BiomeType(biome_str))
                except ValueError:
                    # Skip invalid biome types
                    pass
        
        # Convert major powers from strings to UUIDs
        major_powers = []
        if continent_db.major_powers:
            for power_str in continent_db.major_powers:
                try:
                    major_powers.append(UUID(power_str))
                except ValueError:
                    # Skip invalid UUIDs
                    pass
        
        # Create business model
        continent = ContinentMetadata(
            id=continent_db.id,
            name=continent_db.name,
            description=continent_db.description,
            total_area_square_km=continent_db.total_area_square_km,
            climate_zones=climate_zones,
            major_biomes=major_biomes,
            major_powers=major_powers,
            political_situation=continent_db.political_situation,
            generation_seed=continent_db.generation_seed,
            generation_parameters=continent_db.generation_parameters or {},
            created_at=continent_db.created_at,
            updated_at=continent_db.updated_at
        )
        
        return continent


def get_continent_repository(db: Session = None) -> ContinentRepository:
    """Get continent repository instance."""
    if db is None:
        db = get_db_session()
    return ContinentRepository(db) 