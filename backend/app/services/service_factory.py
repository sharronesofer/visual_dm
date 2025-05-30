"""Service factory for creating service instances."""

from typing import Dict, Type, TypeVar, Generic, Optional, Any, Callable
from fastapi import Depends
from sqlalchemy.orm import Session
import logging

from ..models.base import BaseModel
from .base_service import BaseService
from ..database import get_db

T = TypeVar('T', bound=BaseModel)
S = TypeVar('S', bound=BaseService)

logger = logging.getLogger(__name__)

class ServiceFactory:
    """Factory for creating service instances.
    
    This class follows the factory pattern to create services
    for different model types. It manages dependency injection
    and service lifecycle.
    """
    
    # Registry of service class by model class
    _service_registry: Dict[Type[BaseModel], Type[BaseService]] = {}
    
    # Cache of service instances
    _service_instances: Dict[Any, BaseService] = {}
    
    @classmethod
    def register(cls, model_class: Type[T], service_class: Type[S]) -> None:
        """Register a service class for a model class.
        
        Args:
            model_class: Model class
            service_class: Service class for the model
        """
        cls._service_registry[model_class] = service_class
        logger.debug(f"Registered {service_class.__name__} for {model_class.__name__}")
    
    @classmethod
    def register_service(cls, model_class: Type[T], service_class: Type[S]) -> None:
        """Alias for register, for backward compatibility."""
        return cls.register(model_class, service_class)
    
    @classmethod
    def get_service(cls, model_class: Type[T], db: Session = Depends(get_db)) -> S:
        """Get a service instance for the given model class.
        
        Args:
            model_class: Model class
            db: Database session
            
        Returns:
            Service instance for the model class
        
        Raises:
            ValueError: If no service is registered for the model class
        """
        if model_class not in cls._service_registry:
            raise ValueError(f"No service registered for {model_class.__name__}")
        
        service_class = cls._service_registry[model_class]
        
        # Use model class and db as cache key
        key = (model_class, db)
        
        if key not in cls._service_instances:
            # Create new service instance if not cached
            service_instance = service_class(model_class, db)
            cls._service_instances[key] = service_instance
            logger.debug(f"Created new {service_class.__name__} instance")
        
        return cls._service_instances[key]
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the service instance cache."""
        cls._service_instances.clear()
        logger.debug("Cleared service instance cache")
    
    @classmethod
    def get_service_class(cls, model_class: Type[T]) -> Optional[Type[S]]:
        """Get the service class registered for a model class.
        
        Args:
            model_class: Model class
            
        Returns:
            Service class if registered, None otherwise
        """
        return cls._service_registry.get(model_class) 