"""Base models and repository classes for all backend systems"""

from typing import Dict, List, Optional, Any, TypeVar, Generic, Type
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# Type variable for generic repository and service
T = TypeVar('T')

class BaseModel:
    """Base model class for all system models"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {}
    
    def update(self, **kwargs) -> None:
        """Update model attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

class CoreBaseModel(BaseModel):
    """Core base model class - alias for BaseModel to maintain compatibility"""
    pass

class BaseRepository(ABC):
    """Base repository class for data access operations"""
    
    def __init__(self):
        self.logger = logger
    
    async def health_check(self) -> Dict[str, Any]:
        """Check repository health"""
        return {"status": "healthy", "repository": self.__class__.__name__}

class BaseService(Generic[T], ABC):
    """Base service class for business logic operations with generic typing support"""
    
    def __init__(self, db_session: Session, entity_class: Type[T]):
        self.logger = logger
        self.db = db_session
        self.entity_class = entity_class
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {"status": "healthy", "service": self.__class__.__name__}
    
    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Get entity by ID - to be implemented by subclasses"""
        return None
    
    async def create(self, **kwargs) -> T:
        """Create entity - to be implemented by subclasses"""
        pass
    
    async def update(self, entity_id: Any, **kwargs) -> Optional[T]:
        """Update entity - to be implemented by subclasses"""
        return None
    
    async def delete(self, entity_id: Any) -> bool:
        """Delete entity - to be implemented by subclasses"""
        return False
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """List entities - to be implemented by subclasses"""
        return [] 