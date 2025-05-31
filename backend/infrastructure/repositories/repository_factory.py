"""Repository factory for creating repositories."""

from typing import Dict, Type, TypeVar
from sqlalchemy.orm import Session
import logging

from backend.infrastructure.models import BaseModel
from backend.infrastructure.repositories import BaseRepository

T = TypeVar('T', bound=BaseModel)
R = TypeVar('R', bound=BaseRepository)

logger = logging.getLogger(__name__)

class RepositoryFactory:
    """Factory for creating repositories.
    
    This class follows the factory pattern to create repositories
    for different model types. It caches repository instances
    by model type for efficient reuse.
    """
    
    _repositories: Dict[Type, BaseRepository] = {}
    
    @classmethod
    def get_repository(cls, model_class: Type[T], db: Session) -> BaseRepository[T]:
        """Get a repository instance for the given model class.
        
        Args:
            model_class: Model class (must be a subclass of BaseModel)
            db: Database session
            
        Returns:
            Repository instance for the model class
        """
        # Use model class and db as cache key
        key = (model_class, db)
        
        if key not in cls._repositories:
            # Create new repository instance if not cached
            cls._repositories[key] = BaseRepository(model_class, db)
            logger.debug(f"Created new repository for {model_class.__name__}")
        
        return cls._repositories[key]
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the repository cache."""
        cls._repositories.clear()
        logger.debug("Cleared repository cache") 