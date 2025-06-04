"""
Region Repository Implementation

Concrete repository implementation for region data persistence.
Bridges the gap between region business logic and database storage.
Enhanced with performance optimizations: caching, query optimization, and bulk operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import and_, or_, func, text
from functools import lru_cache
from datetime import datetime, timedelta
import logging

from backend.infrastructure.database import get_db_session
from backend.infrastructure.systems.region.models import RegionDB, ResourceNodeDB
from backend.systems.region.models import RegionMetadata, ResourceNode, HexCoordinate
from backend.infrastructure.shared.exceptions import (
    RegionNotFoundError,
    RegionConflictError,
    RepositoryError
)

logger = logging.getLogger(__name__)

class RegionRepository:
    """
    Concrete repository for region data persistence with performance optimizations.
    
    Performance Features:
    - Query result caching for frequently accessed data
    - Bulk operations for efficient batch processing
    - Query optimization with eager loading
    - Connection pooling support
    - Index-optimized queries
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self._cache = {}
        self._cache_ttl = {}
        self._cache_timeout = 300  # 5 minutes default
        
        # Performance metrics
        self._query_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get item from cache if not expired"""
        if cache_key in self._cache:
            if cache_key in self._cache_ttl:
                if datetime.now() < self._cache_ttl[cache_key]:
                    self._cache_hits += 1
                    return self._cache[cache_key]
                else:
                    # Expired - remove from cache
                    del self._cache[cache_key]
                    del self._cache_ttl[cache_key]
        self._cache_misses += 1
        return None
    
    def _set_cache(self, cache_key: str, value: Any, ttl_seconds: int = None) -> None:
        """Set item in cache with TTL"""
        if ttl_seconds is None:
            ttl_seconds = self._cache_timeout
        
        self._cache[cache_key] = value
        self._cache_ttl[cache_key] = datetime.now() + timedelta(seconds=ttl_seconds)
        
        # Prevent cache from growing too large
        if len(self._cache) > 1000:
            self._cleanup_expired_cache()
    
    def _cleanup_expired_cache(self) -> None:
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = [k for k, ttl in self._cache_ttl.items() if now >= ttl]
        for key in expired_keys:
            del self._cache[key]
            del self._cache_ttl[key]
    
    def _invalidate_cache_pattern(self, pattern: str) -> None:
        """Invalidate cache entries matching pattern"""
        keys_to_remove = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self._cache[key]
            if key in self._cache_ttl:
                del self._cache_ttl[key]

    def create(self, region_data: RegionMetadata) -> RegionMetadata:
        """Create a new region in the database."""
        try:
            self._query_count += 1
            
            # Convert business model to database model
            region_db = self._to_db_model(region_data)
            
            self.db.add(region_db)
            self.db.commit()
            self.db.refresh(region_db)
            
            # Invalidate relevant cache
            self._invalidate_cache_pattern("regions_")
            self._invalidate_cache_pattern("stats_")
            
            # Convert back to business model
            result = self._to_business_model(region_db)
            
            # Cache the new region
            cache_key = f"region_by_id_{result.id}"
            self._set_cache(cache_key, result)
            
            return result
            
        except IntegrityError as e:
            self.db.rollback()
            if "regions_name_key" in str(e):
                raise RegionConflictError(f"Region with name '{region_data.name}' already exists")
            raise RepositoryError(f"Database constraint violation: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to create region: {str(e)}")
    
    def get_by_id(self, region_id: UUID) -> Optional[RegionMetadata]:
        """Retrieve a region by its ID with caching."""
        cache_key = f"region_by_id_{region_id}"
        
        # Try cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            self._query_count += 1
            
            # Optimized query with eager loading
            region_db = (
                self.db.query(RegionDB)
                .options(selectinload(RegionDB.resource_nodes))
                .filter(RegionDB.id == region_id)
                .first()
            )
            
            if not region_db:
                return None
            
            result = self._to_business_model(region_db)
            
            # Cache the result
            self._set_cache(cache_key, result)
            
            return result
            
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to retrieve region {region_id}: {str(e)}")
    
    def get_by_name(self, name: str) -> Optional[RegionMetadata]:
        """Retrieve a region by its name with caching."""
        cache_key = f"region_by_name_{name}"
        
        # Try cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            self._query_count += 1
            
            region_db = (
                self.db.query(RegionDB)
                .options(selectinload(RegionDB.resource_nodes))
                .filter(RegionDB.name == name)
                .first()
            )
            
            if not region_db:
                return None
            
            result = self._to_business_model(region_db)
            
            # Cache the result
            self._set_cache(cache_key, result)
            
            return result
            
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to retrieve region '{name}': {str(e)}")
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[RegionMetadata]:
        """Retrieve all regions with pagination and caching."""
        cache_key = f"regions_all_{limit}_{offset}"
        
        # Try cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            self._query_count += 1
            
            # Optimized query with eager loading
            regions_db = (
                self.db.query(RegionDB)
                .options(selectinload(RegionDB.resource_nodes))
                .offset(offset)
                .limit(limit)
                .all()
            )
            
            result = [self._to_business_model(region_db) for region_db in regions_db]
            
            # Cache the result with shorter TTL for paginated results
            self._set_cache(cache_key, result, ttl_seconds=60)
            
            return result
            
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to retrieve regions: {str(e)}")
    
    def get_by_filters(self, filters: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[RegionMetadata]:
        """Retrieve regions by various filters with query optimization."""
        # Create cache key from filters
        filter_str = "_".join(f"{k}:{v}" for k, v in sorted(filters.items()))
        cache_key = f"regions_filtered_{filter_str}_{limit}_{offset}"
        
        # Try cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            self._query_count += 1
            
            # Build optimized query
            query = (
                self.db.query(RegionDB)
                .options(selectinload(RegionDB.resource_nodes))
            )
            
            # Apply filters with index-optimized conditions
            if 'continent_id' in filters:
                query = query.filter(RegionDB.continent_id == filters['continent_id'])
            
            if 'region_type' in filters:
                query = query.filter(RegionDB.region_type == filters['region_type'])
            
            if 'dominant_biome' in filters:
                query = query.filter(RegionDB.dominant_biome == filters['dominant_biome'])
            
            if 'climate' in filters:
                query = query.filter(RegionDB.climate == filters['climate'])
            
            if 'danger_level' in filters:
                query = query.filter(RegionDB.danger_level == filters['danger_level'])
            
            if 'min_population' in filters:
                query = query.filter(RegionDB.population >= filters['min_population'])
            
            if 'max_population' in filters:
                query = query.filter(RegionDB.population <= filters['max_population'])
            
            if 'name_filter' in filters:
                # Use index-friendly LIKE operation
                query = query.filter(RegionDB.name.ilike(f"{filters['name_filter']}%"))
            
            # Apply pagination and execute
            regions_db = query.offset(offset).limit(limit).all()
            
            result = [self._to_business_model(region_db) for region_db in regions_db]
            
            # Cache filtered results with shorter TTL
            self._set_cache(cache_key, result, ttl_seconds=120)
            
            return result
            
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to filter regions: {str(e)}")
    
    def get_multiple_by_ids(self, region_ids: List[UUID]) -> List[RegionMetadata]:
        """Bulk retrieve multiple regions by IDs - optimized for performance."""
        if not region_ids:
            return []
        
        # Check cache for each ID
        cached_results = {}
        missing_ids = []
        
        for region_id in region_ids:
            cache_key = f"region_by_id_{region_id}"
            cached = self._get_from_cache(cache_key)
            if cached is not None:
                cached_results[region_id] = cached
            else:
                missing_ids.append(region_id)
        
        # Bulk query for missing regions
        if missing_ids:
            try:
                self._query_count += 1
                
                regions_db = (
                    self.db.query(RegionDB)
                    .options(selectinload(RegionDB.resource_nodes))
                    .filter(RegionDB.id.in_(missing_ids))
                    .all()
                )
                
                # Convert and cache results
                for region_db in regions_db:
                    result = self._to_business_model(region_db)
                    cached_results[region_db.id] = result
                    
                    # Cache individual result
                    cache_key = f"region_by_id_{region_db.id}"
                    self._set_cache(cache_key, result)
                    
            except SQLAlchemyError as e:
                raise RepositoryError(f"Failed to retrieve multiple regions: {str(e)}")
        
        # Return results in original order
        return [cached_results.get(region_id) for region_id in region_ids if region_id in cached_results]

    def update(self, region_id: UUID, update_data: Dict[str, Any]) -> Optional[RegionMetadata]:
        """Update an existing region with cache invalidation."""
        try:
            self._query_count += 1
            
            region_db = self.db.query(RegionDB).filter(RegionDB.id == region_id).first()
            
            if not region_db:
                return None
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(region_db, field) and value is not None:
                    setattr(region_db, field, value)
            
            self.db.commit()
            self.db.refresh(region_db)
            
            result = self._to_business_model(region_db)
            
            # Invalidate relevant cache entries
            self._invalidate_cache_pattern(f"region_by_id_{region_id}")
            self._invalidate_cache_pattern(f"region_by_name_{region_db.name}")
            self._invalidate_cache_pattern("regions_")
            self._invalidate_cache_pattern("stats_")
            
            # Cache updated result
            cache_key = f"region_by_id_{region_id}"
            self._set_cache(cache_key, result)
            
            return result
            
        except IntegrityError as e:
            self.db.rollback()
            if "regions_name_key" in str(e):
                raise RegionConflictError(f"Region name already exists")
            raise RepositoryError(f"Database constraint violation: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to update region {region_id}: {str(e)}")
    
    def delete(self, region_id: UUID) -> bool:
        """Delete a region with cache invalidation."""
        try:
            self._query_count += 1
            
            region_db = self.db.query(RegionDB).filter(RegionDB.id == region_id).first()
            
            if not region_db:
                return False
            
            # Get name before deletion for cache invalidation
            region_name = region_db.name
            
            self.db.delete(region_db)
            self.db.commit()
            
            # Invalidate cache
            self._invalidate_cache_pattern(f"region_by_id_{region_id}")
            self._invalidate_cache_pattern(f"region_by_name_{region_name}")
            self._invalidate_cache_pattern("regions_")
            self._invalidate_cache_pattern("stats_")
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to delete region {region_id}: {str(e)}")
    
    def search_by_name(self, search_term: str, limit: int = 50) -> List[RegionMetadata]:
        """Search regions by name pattern with caching."""
        cache_key = f"search_name_{search_term}_{limit}"
        
        # Try cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            self._query_count += 1
            
            # Use index-optimized search
            regions_db = (
                self.db.query(RegionDB)
                .options(selectinload(RegionDB.resource_nodes))
                .filter(RegionDB.name.ilike(f"%{search_term}%"))
                .order_by(RegionDB.name)  # Add ordering for consistent results
                .limit(limit)
                .all()
            )
            
            result = [self._to_business_model(region_db) for region_db in regions_db]
            
            # Cache search results
            self._set_cache(cache_key, result, ttl_seconds=180)
            
            return result
            
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to search regions: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics about regions with caching."""
        cache_key = "stats_regions_all"
        
        # Try cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            self._query_count += 1
            
            stats = {}
            
            # Use optimized aggregate queries
            # Total count
            stats['total_regions'] = self.db.query(func.count(RegionDB.id)).scalar()
            
            # Population stats - single query with multiple aggregates
            pop_stats = self.db.query(
                func.sum(RegionDB.population).label('total_pop'),
                func.avg(RegionDB.population).label('avg_pop'),
                func.min(RegionDB.population).label('min_pop'),
                func.max(RegionDB.population).label('max_pop')
            ).first()
            
            stats['total_population'] = int(pop_stats.total_pop or 0)
            stats['average_population'] = float(pop_stats.avg_pop or 0)
            stats['min_population'] = int(pop_stats.min_pop or 0)
            stats['max_population'] = int(pop_stats.max_pop or 0)
            
            # Biome distribution - optimized group by
            biome_counts = (
                self.db.query(RegionDB.dominant_biome, func.count(RegionDB.id))
                .group_by(RegionDB.dominant_biome)
                .all()
            )
            stats['biome_distribution'] = {biome: count for biome, count in biome_counts}
            
            # Region type distribution
            type_counts = (
                self.db.query(RegionDB.region_type, func.count(RegionDB.id))
                .group_by(RegionDB.region_type)
                .all()
            )
            stats['region_type_distribution'] = {rtype: count for rtype, count in type_counts}
            
            # Danger level distribution
            danger_counts = (
                self.db.query(RegionDB.danger_level, func.count(RegionDB.id))
                .group_by(RegionDB.danger_level)
                .all()
            )
            stats['danger_level_distribution'] = {level: count for level, count in danger_counts}
            
            # Cache statistics with longer TTL
            self._set_cache(cache_key, stats, ttl_seconds=600)
            
            return stats
            
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get region statistics: {str(e)}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get repository performance metrics."""
        total_cache_operations = self._cache_hits + self._cache_misses
        cache_hit_rate = (self._cache_hits / total_cache_operations * 100) if total_cache_operations > 0 else 0
        
        return {
            "query_count": self._query_count,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "cache_size": len(self._cache),
            "cache_entries": list(self._cache.keys())[:10]  # Sample of cache keys
        }
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._cache_ttl.clear()
        logger.info("Repository cache cleared")
    
    def _to_db_model(self, region: RegionMetadata) -> RegionDB:
        """Convert business model to database model."""
        # Convert hex coordinates to JSON
        hex_coords_json = [
            {"q": coord.q, "r": coord.r, "s": coord.s}
            for coord in region.hex_coordinates
        ] if region.hex_coordinates else []
        
        center_coord_json = None
        if region.center_coordinate:
            center_coord_json = {
                "q": region.center_coordinate.q,
                "r": region.center_coordinate.r,
                "s": region.center_coordinate.s
            }
        
        # Convert resource nodes to JSON
        resource_nodes_json = []
        if region.resource_nodes:
            for resource in region.resource_nodes:
                resource_dict = {
                    "resource_type": resource.resource_type,
                    "abundance": resource.abundance,
                    "quality": resource.quality,
                    "accessibility": resource.accessibility,
                    "depletion_rate": resource.depletion_rate,
                    "current_reserves": resource.current_reserves
                }
                if resource.location:
                    resource_dict["location"] = {
                        "q": resource.location.q,
                        "r": resource.location.r,
                        "s": resource.location.s
                    }
                resource_nodes_json.append(resource_dict)
        
        # Create database model
        region_db = RegionDB(
            id=region.id,
            name=region.name,
            description=region.description,
            region_type=region.region_type,
            dominant_biome=region.profile.dominant_biome if region.profile else 'temperate_forest',
            climate=region.profile.climate.value if region.profile and region.profile.climate else 'temperate',
            hex_coordinates=hex_coords_json,
            center_coordinate=center_coord_json,
            area_square_km=region.area_square_km,
            population=region.population,
            danger_level=region.danger_level.value if region.danger_level else 2,
            continent_id=region.continent_id,
            resource_nodes=resource_nodes_json
        )
        
        # Add profile data if available
        if region.profile:
            region_db.soil_fertility = region.profile.soil_fertility
            region_db.water_availability = region.profile.water_availability
            region_db.precipitation = region.profile.precipitation
            region_db.humidity = region.profile.humidity
            region_db.elevation = region.profile.elevation
            region_db.natural_hazards = region.profile.natural_hazards or []
        
        return region_db
    
    def _to_business_model(self, region_db: RegionDB) -> RegionMetadata:
        """Convert database model to business model."""
        from backend.systems.region.models import RegionProfile, DangerLevel, ClimateType
        
        # Convert hex coordinates from JSON
        hex_coordinates = []
        if region_db.hex_coordinates:
            for coord_dict in region_db.hex_coordinates:
                hex_coordinates.append(
                    HexCoordinate(coord_dict["q"], coord_dict["r"])
                )
        
        center_coordinate = None
        if region_db.center_coordinate:
            center_coordinate = HexCoordinate(
                region_db.center_coordinate["q"],
                region_db.center_coordinate["r"]
            )
        
        # Convert resource nodes from JSON
        resource_nodes = []
        if region_db.resource_nodes:
            for resource_dict in region_db.resource_nodes:
                location = None
                if "location" in resource_dict and resource_dict["location"]:
                    loc_dict = resource_dict["location"]
                    location = HexCoordinate(loc_dict["q"], loc_dict["r"])
                
                resource_nodes.append(ResourceNode(
                    resource_type=resource_dict["resource_type"],
                    abundance=resource_dict["abundance"],
                    quality=resource_dict["quality"],
                    accessibility=resource_dict["accessibility"],
                    depletion_rate=resource_dict.get("depletion_rate", 0.0),
                    current_reserves=resource_dict.get("current_reserves", 1.0),
                    location=location
                ))
        
        # Create profile
        climate = ClimateType.TEMPERATE
        try:
            climate = ClimateType(region_db.climate)
        except ValueError:
            pass  # Use default
        
        profile = RegionProfile(
            dominant_biome=region_db.dominant_biome,
            climate=climate,
            soil_fertility=region_db.soil_fertility,
            water_availability=region_db.water_availability,
            precipitation=region_db.precipitation,
            humidity=region_db.humidity,
            elevation=region_db.elevation,
            natural_hazards=region_db.natural_hazards or []
        )
        
        # Create danger level
        danger_level = DangerLevel.SAFE
        try:
            danger_level = DangerLevel(region_db.danger_level)
        except ValueError:
            pass  # Use default
        
        # Create business model
        region = RegionMetadata(
            id=region_db.id,
            name=region_db.name,
            description=region_db.description,
            region_type=region_db.region_type,
            profile=profile,
            hex_coordinates=hex_coordinates,
            center_coordinate=center_coordinate,
            area_square_km=region_db.area_square_km,
            population=region_db.population,
            danger_level=danger_level,
            continent_id=region_db.continent_id,
            resource_nodes=resource_nodes,
            created_at=region_db.created_at,
            updated_at=region_db.updated_at
        )
        
        return region


def get_region_repository(db: Session = None) -> RegionRepository:
    """Get region repository instance."""
    if db is None:
        db = get_db_session()
    return RegionRepository(db) 