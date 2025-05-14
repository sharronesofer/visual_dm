# This file marks the 'services' directory as a Python package.

from abc import ABC, abstractmethod
from .quest_service import QuestService
from .reward_service import RewardService
from .world_impact_manager import WorldImpactManager

_service_registry = {}

# Register a service provider instance by name
# Example: register_service('redis', RedisService())
def register_service(name, provider):
    """Register a service provider instance for dependency injection."""
    _service_registry[name] = provider

# Retrieve a service provider by name
# Example: redis = get_service('redis')
def get_service(name):
    """Retrieve a registered service provider by name."""
    provider = _service_registry.get(name)
    if provider is None:
        raise ValueError(f'Service {name} not registered')
    return provider

# Example usage:
# from app.services import register_service, get_service
# register_service('redis', RedisService())
# redis = get_service('redis')

class ServiceProvider(ABC):
    """
    Abstract base class for service providers (for dependency injection).
    All services should inherit from this for type safety and test mocking.
    """
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the service is healthy/available."""
        pass



