"""
Rumor System Technical Services - Database Operations with Caching

This module provides technical database services for the rumor system
that implement the business logic protocols correctly with performance optimizations.
"""

import logging
import json
import hashlib
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

# Try to import Redis for caching (optional dependency)
try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from backend.infrastructure.systems.rumor.models.models import (
    RumorEntity,
    CreateRumorRequest,
    UpdateRumorRequest,
    RumorResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    RumorNotFoundError,
    RumorValidationError,
    RumorConflictError
)

logger = logging.getLogger(__name__)


class RumorCacheManager:
    """Manages Redis caching for rumor operations"""
    
    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis_client = redis_client
        self.enabled = redis_client is not None and REDIS_AVAILABLE
        self.default_ttl = 300  # 5 minutes default TTL
        self.stats_ttl = 600    # 10 minutes for statistics
        
    def _make_key(self, prefix: str, identifier: str) -> str:
        """Create a cache key with prefix"""
        return f"rumor:{prefix}:{identifier}"
    
    def get_rumor(self, rumor_id: str) -> Optional[Dict[str, Any]]:
        """Get cached rumor by ID"""
        if not self.enabled:
            return None
            
        try:
            key = self._make_key("rumor", rumor_id)
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get failed for rumor {rumor_id}: {e}")
        
        return None
    
    def set_rumor(self, rumor_id: str, rumor_data: Dict[str, Any], ttl: Optional[int] = None):
        """Cache a rumor"""
        if not self.enabled:
            return
            
        try:
            key = self._make_key("rumor", rumor_id)
            ttl = ttl or self.default_ttl
            self.redis_client.setex(key, ttl, json.dumps(rumor_data, default=str))
        except Exception as e:
            logger.warning(f"Cache set failed for rumor {rumor_id}: {e}")
    
    def delete_rumor(self, rumor_id: str):
        """Remove rumor from cache"""
        if not self.enabled:
            return
            
        try:
            key = self._make_key("rumor", rumor_id)
            self.redis_client.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete failed for rumor {rumor_id}: {e}")
    
    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """Get cached statistics"""
        if not self.enabled:
            return None
            
        try:
            key = self._make_key("stats", "summary")
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get failed for statistics: {e}")
        
        return None
    
    def set_statistics(self, stats_data: Dict[str, Any]):
        """Cache statistics"""
        if not self.enabled:
            return
            
        try:
            key = self._make_key("stats", "summary")
            self.redis_client.setex(key, self.stats_ttl, json.dumps(stats_data, default=str))
        except Exception as e:
            logger.warning(f"Cache set failed for statistics: {e}")
    
    def get_list_cache(self, cache_params: Dict[str, Any]) -> Optional[Tuple[List[Dict], int]]:
        """Get cached list results"""
        if not self.enabled:
            return None
            
        try:
            # Create cache key from parameters
            params_str = json.dumps(cache_params, sort_keys=True)
            cache_hash = hashlib.md5(params_str.encode()).hexdigest()
            key = self._make_key("list", cache_hash)
            
            cached = self.redis_client.get(key)
            if cached:
                data = json.loads(cached)
                return data['items'], data['total']
        except Exception as e:
            logger.warning(f"Cache get failed for list: {e}")
        
        return None
    
    def set_list_cache(self, cache_params: Dict[str, Any], items: List[Dict], total: int):
        """Cache list results"""
        if not self.enabled:
            return
            
        try:
            # Create cache key from parameters
            params_str = json.dumps(cache_params, sort_keys=True)
            cache_hash = hashlib.md5(params_str.encode()).hexdigest()
            key = self._make_key("list", cache_hash)
            
            cache_data = {
                'items': items,
                'total': total,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            # Shorter TTL for lists since they change more frequently
            list_ttl = min(self.default_ttl, 120)  # 2 minutes max
            self.redis_client.setex(key, list_ttl, json.dumps(cache_data, default=str))
        except Exception as e:
            logger.warning(f"Cache set failed for list: {e}")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching a pattern"""
        if not self.enabled:
            return
            
        try:
            pattern_key = self._make_key("*", pattern)
            keys = self.redis_client.keys(pattern_key)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.warning(f"Cache invalidation failed for pattern {pattern}: {e}")


class RumorDatabaseService(BaseService[RumorEntity]):
    """Technical service class for rumor database operations with caching"""
    
    def __init__(self, db_session: Session, redis_client: Optional[Redis] = None):
        super().__init__(db_session, RumorEntity)
        self.db = db_session
        self.cache = RumorCacheManager(redis_client)

    async def create_rumor(
        self, 
        request: CreateRumorRequest,
        user_id: Optional[UUID] = None
    ) -> RumorResponse:
        """Create a new rumor in database with cache invalidation"""
        try:
            logger.info(f"Creating rumor for originator: {request.originator_id}")
            
            # Create entity using business logic fields
            entity_data = {
                "content": request.content,
                "originator_id": request.originator_id,
                "categories": request.categories or [],
                "severity": request.severity,
                "truth_value": request.truth_value,
                "believability": 1.0,  # Start with full believability for originator
                "spread_count": 0,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = RumorEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            # Create response
            response = RumorResponse.from_orm(entity)
            
            # Cache the new rumor
            self.cache.set_rumor(str(entity.id), response.dict())
            
            # Invalidate statistics and list caches
            self.cache.invalidate_pattern("stats:*")
            self.cache.invalidate_pattern("list:*")
            
            logger.info(f"Created rumor {entity.id} successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error creating rumor: {str(e)}")
            self.db.rollback()
            raise

    async def get_rumor_by_id(self, rumor_id: UUID) -> Optional[RumorResponse]:
        """Get rumor by ID with caching"""
        try:
            rumor_id_str = str(rumor_id)
            
            # Try cache first
            cached_data = self.cache.get_rumor(rumor_id_str)
            if cached_data:
                logger.debug(f"Cache hit for rumor {rumor_id}")
                return RumorResponse(**cached_data)
            
            # Fetch from database
            entity = self.db.query(RumorEntity).filter(
                RumorEntity.id == rumor_id
            ).first()
            
            if not entity:
                return None
            
            response = RumorResponse.from_orm(entity)
            
            # Cache the result
            self.cache.set_rumor(rumor_id_str, response.dict())
            
            logger.debug(f"Database hit for rumor {rumor_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting rumor {rumor_id}: {str(e)}")
            raise

    async def update_rumor(
        self, 
        rumor_id: UUID, 
        request: UpdateRumorRequest
    ) -> RumorResponse:
        """Update existing rumor with cache invalidation"""
        try:
            entity = await self._get_entity_by_id(rumor_id)
            if not entity:
                raise RumorNotFoundError(f"Rumor {rumor_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    if hasattr(entity, field):
                        setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            response = RumorResponse.from_orm(entity)
            
            # Update cache
            rumor_id_str = str(rumor_id)
            self.cache.set_rumor(rumor_id_str, response.dict())
            
            # Invalidate related caches
            self.cache.invalidate_pattern("stats:*")
            self.cache.invalidate_pattern("list:*")
            
            logger.info(f"Updated rumor {entity.id} successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error updating rumor {rumor_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_rumor(self, rumor_id: UUID) -> bool:
        """Delete rumor with cache invalidation"""
        try:
            entity = await self._get_entity_by_id(rumor_id)
            if not entity:
                return False
            
            self.db.delete(entity)
            self.db.commit()
            
            # Remove from cache
            rumor_id_str = str(rumor_id)
            self.cache.delete_rumor(rumor_id_str)
            
            # Invalidate related caches
            self.cache.invalidate_pattern("stats:*")
            self.cache.invalidate_pattern("list:*")
            
            logger.info(f"Deleted rumor {rumor_id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting rumor {rumor_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_rumors(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None,
        originator_id: Optional[str] = None
    ) -> Tuple[List[RumorResponse], int]:
        """List rumors with caching for better performance"""
        try:
            # Create cache parameters
            cache_params = {
                'page': page,
                'size': size,
                'status': status,
                'search': search,
                'originator_id': originator_id
            }
            
            # Try cache first
            cached_result = self.cache.get_list_cache(cache_params)
            if cached_result:
                items_data, total = cached_result
                logger.debug(f"Cache hit for rumors list (page={page}, size={size})")
                return [RumorResponse(**item) for item in items_data], total
            
            # Build query with optimized indexes
            query = self.db.query(RumorEntity)
            
            # Apply filters (using indexed columns)
            if status:
                query = query.filter(RumorEntity.status == status)
            
            if originator_id:
                query = query.filter(RumorEntity.originator_id == originator_id)
            
            if search:
                query = query.filter(
                    or_(
                        RumorEntity.content.ilike(f"%{search}%"),
                        RumorEntity.originator_id.ilike(f"%{search}%")
                    )
                )
            
            # Get total count efficiently
            total = query.count()
            
            # Apply pagination and ordering (using indexed columns)
            offset = (page - 1) * size
            entities = query.order_by(RumorEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [RumorResponse.from_orm(entity) for entity in entities]
            response_data = [response.dict() for response in responses]
            
            # Cache the results
            self.cache.set_list_cache(cache_params, response_data, total)
            
            logger.debug(f"Database hit for rumors list (page={page}, size={size})")
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing rumors: {str(e)}")
            raise

    async def get_rumor_statistics(self) -> Dict[str, Any]:
        """Get rumor system statistics with caching"""
        try:
            # Try cache first
            cached_stats = self.cache.get_statistics()
            if cached_stats:
                logger.debug("Cache hit for rumor statistics")
                return cached_stats
            
            # Calculate statistics from database (using indexed columns for performance)
            total_count = self.db.query(func.count(RumorEntity.id)).scalar()
            
            active_count = self.db.query(func.count(RumorEntity.id)).filter(
                RumorEntity.status == "active"
            ).scalar()
            
            # Get severity distribution
            severity_stats = self.db.query(
                RumorEntity.severity,
                func.count(RumorEntity.id)
            ).group_by(RumorEntity.severity).all()
            
            severity_distribution = {severity: count for severity, count in severity_stats}
            
            # Get average metrics
            avg_truth = self.db.query(
                func.avg(RumorEntity.truth_value)
            ).scalar() or 0.0
            
            avg_believability = self.db.query(
                func.avg(RumorEntity.believability)
            ).scalar() or 0.0
            
            avg_spread = self.db.query(
                func.avg(RumorEntity.spread_count)
            ).scalar() or 0.0
            
            stats = {
                "total_rumors": total_count,
                "active_rumors": active_count,
                "severity_distribution": severity_distribution,
                "average_truth_value": round(float(avg_truth), 2),
                "average_believability": round(float(avg_believability), 2),
                "average_spread_count": round(float(avg_spread), 2),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Cache the statistics
            self.cache.set_statistics(stats)
            
            logger.debug("Database hit for rumor statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting rumor statistics: {str(e)}")
            raise

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[RumorEntity]:
        """Get entity by ID from database"""
        return self.db.query(RumorEntity).filter(
            RumorEntity.id == entity_id
        ).first()


# Factory function for dependency injection
def create_rumor_database_service(
    db_session: Session, 
    redis_client: Optional[Redis] = None
) -> RumorDatabaseService:
    """Create rumor database service instance with optional caching"""
    return RumorDatabaseService(db_session, redis_client)


"""
Infrastructure Validation Services for Rumor System

This module provides concrete implementations of validation services
that implement the business logic protocols.
"""

from typing import Dict, Any, List
from backend.systems.rumor.services.services import RumorValidationService as ValidationServiceProtocol
from backend.systems.rumor.utils.rumor_rules import get_rumor_config


class DefaultRumorValidationService(ValidationServiceProtocol):
    """
    Default implementation of rumor validation service.
    Uses configuration from JSON files for validation rules.
    """
    
    def validate_rumor_data(self, rumor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate rumor creation/update data"""
        validated = rumor_data.copy()
        
        # Get validation config
        config = get_rumor_config()
        validation_config = config.get('validation', {})
        
        # Validate content length
        content = validated.get('content', '')
        max_length = validation_config.get('max_content_length', 500)
        min_length = validation_config.get('min_content_length', 10)
        
        if len(content) > max_length:
            raise ValueError(f"Content too long. Maximum {max_length} characters.")
        if len(content) < min_length:
            raise ValueError(f"Content too short. Minimum {min_length} characters.")
        
        # Validate originator_id
        originator_id = validated.get('originator_id', '')
        if not originator_id or len(originator_id.strip()) == 0:
            raise ValueError("Originator ID is required")
        
        # Validate truth_value
        truth_value = validated.get('truth_value', 0.5)
        if not isinstance(truth_value, (int, float)) or truth_value < 0.0 or truth_value > 1.0:
            raise ValueError("Truth value must be between 0.0 and 1.0")
        
        return validated
    
    def validate_severity(self, severity: str) -> str:
        """Validate rumor severity"""
        config = get_rumor_config()
        validation_config = config.get('validation', {})
        valid_severities = validation_config.get('severity_levels', [
            'trivial', 'minor', 'moderate', 'major', 'critical'
        ])
        
        if severity not in valid_severities:
            raise ValueError(f"Invalid severity '{severity}'. Must be one of: {valid_severities}")
        
        return severity
    
    def validate_categories(self, categories: List[str]) -> List[str]:
        """Validate rumor categories"""
        if not isinstance(categories, list):
            raise ValueError("Categories must be a list")
        
        # Ensure all categories are strings
        validated_categories = []
        for category in categories:
            if not isinstance(category, str):
                raise ValueError("All categories must be strings")
            
            # Clean and validate category
            clean_category = category.strip().lower()
            if clean_category:
                validated_categories.append(clean_category)
        
        return validated_categories


# Factory function for dependency injection
def create_rumor_validation_service() -> DefaultRumorValidationService:
    """Factory function to create rumor validation service"""
    return DefaultRumorValidationService() 