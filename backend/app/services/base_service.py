"""Base service class for entity operations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import logging
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..models.base import BaseModel
from ..repositories.base_repository import BaseRepository
from ..repositories.repository_factory import RepositoryFactory
from ..core.cache import cache_manager
from ..database import get_db

T = TypeVar('T', bound=BaseModel)  # Type must be BaseModel or subclass

logger = logging.getLogger(__name__)

class BaseService(Generic[T], ABC):
    """Abstract base service for entity operations.
    
    This class provides a template for services that operate on entities.
    It includes common CRUD operations with caching support and follows
    the dependency injection pattern.
    """
    
    # Cache TTL in seconds
    CACHE_TTL = 1800  # 30 minutes
    
    def __init__(
        self,
        model_class: Type[T],
        db: Session = Depends(get_db),
        cache_enabled: bool = True
    ):
        """Initialize service with model class and dependencies.
        
        Args:
            model_class: Model class (must be a subclass of BaseModel)
            db: Database session
            cache_enabled: Whether to use caching for this service
        """
        self.model_class = model_class
        self.db = db
        self.repository = RepositoryFactory.get_repository(model_class, db)
        self.cache_enabled = cache_enabled
        self.model_name = model_class.__name__.lower()
    
    def _get_cache_key(self, key_part: Any) -> str:
        """Generate a cache key for the entity.
        
        Args:
            key_part: Unique part of the cache key (usually entity ID)
            
        Returns:
            Cache key string
        """
        return f"{self.model_name}:{key_part}"
    
    def _cache_get(self, cache_key: str) -> Optional[Any]:
        """Get value from cache if caching is enabled.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached value if found and caching is enabled, None otherwise
        """
        if not self.cache_enabled:
            return None
        
        return cache_manager.get(cache_key)
    
    def _cache_set(self, cache_key: str, value: Any) -> bool:
        """Set value in cache if caching is enabled.
        
        Args:
            cache_key: Cache key
            value: Value to cache
            
        Returns:
            True if value was cached, False otherwise
        """
        if not self.cache_enabled:
            return False
        
        return cache_manager.set(cache_key, value, self.CACHE_TTL)
    
    def _cache_delete(self, cache_key: str) -> bool:
        """Delete value from cache if caching is enabled.
        
        Args:
            cache_key: Cache key
            
        Returns:
            True if value was deleted, False otherwise
        """
        if not self.cache_enabled:
            return False
        
        return cache_manager.delete(cache_key)
    
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity if found, None otherwise
        """
        # Try to get from cache first
        cache_key = self._get_cache_key(f"id:{id}")
        cached_entity = self._cache_get(cache_key)
        if cached_entity:
            logger.debug(f"Cache hit for {self.model_name} with ID {id}")
            return cached_entity
        
        # If not in cache, get from repository
        entity = self.repository.get_by_id(id)
        if entity:
            # Cache the entity
            self._cache_set(cache_key, entity)
        
        return entity
    
    async def get_all(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities matching the filter criteria.
        
        Args:
            filters: Filter conditions as dictionary
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of entities matching the criteria
        """
        # For list endpoints, we typically don't cache to ensure fresh data
        filters = filters or {}
        return self.repository.get_all(skip=skip, limit=limit, **filters)
    
    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new entity.
        
        Args:
            data: Entity data as dictionary
            
        Returns:
            Created entity
            
        Raises:
            HTTPException: If entity creation fails
        """
        # Create in repository
        entity = self.repository.create(data)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create {self.model_name}"
            )
        
        # Cache the new entity
        cache_key = self._get_cache_key(f"id:{entity.id}")
        self._cache_set(cache_key, entity)
        
        return entity
    
    async def update(self, id: Any, data: Dict[str, Any]) -> T:
        """Update an entity.
        
        Args:
            id: Entity ID
            data: Updated entity data as dictionary
            
        Returns:
            Updated entity
            
        Raises:
            HTTPException: If entity not found or update fails
        """
        # Update in repository
        entity = self.repository.update(id, data)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model_name.capitalize()} with ID {id} not found"
            )
        
        # Update in cache
        cache_key = self._get_cache_key(f"id:{id}")
        self._cache_set(cache_key, entity)
        
        return entity
    
    async def delete(self, id: Any) -> bool:
        """Delete an entity.
        
        Args:
            id: Entity ID
            
        Returns:
            True if entity was deleted, False if not found
            
        Raises:
            HTTPException: If deletion fails
        """
        # Delete from repository
        result = self.repository.delete(id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model_name.capitalize()} with ID {id} not found"
            )
        
        # Delete from cache
        cache_key = self._get_cache_key(f"id:{id}")
        self._cache_delete(cache_key)
        
        return True 