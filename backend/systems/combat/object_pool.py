"""
ObjectPool module for the Visual DM combat system.

This module implements an efficient memory management system for combat objects,
reducing allocation overhead by recycling instances. It helps optimize performance
during combat by minimizing memory churn from frequent object creation/destruction.

Following the design principles from the Development Bible, this implementation:
1. Provides a generic object pooling mechanism
2. Pre-allocates objects based on expected usage
3. Recycles objects rather than destroying them
4. Supports automatic expansion and cleanup
"""

import logging
from typing import Dict, List, Any, Type, TypeVar, Generic, Optional, Callable

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

class ObjectPool(Generic[T]):
    """
    Generic object pool for efficient memory management.
    
    Reduces allocation overhead by recycling instances of objects.
    Particularly useful for frequently created/destroyed objects in combat.
    """
    
    def __init__(self, object_type: Type[T], initial_size: int = 10, 
                 factory: Optional[Callable[[], T]] = None,
                 reset_func: Optional[Callable[[T], None]] = None,
                 max_size: int = 1000):
        """
        Initialize a new object pool.
        
        Args:
            object_type: The type of objects to pool
            initial_size: Number of objects to pre-allocate
            factory: Optional custom factory function for creating objects
            reset_func: Optional function to reset object state when recycled
            max_size: Maximum number of objects to keep in the pool
        """
        self._object_type = object_type
        self._factory = factory or (lambda: object_type())
        self._reset_func = reset_func
        self._max_size = max_size
        self._available: List[T] = []
        self._in_use: Dict[int, T] = {}
        
        # Pre-allocate objects
        self._expand_pool(initial_size)
        
        logger.debug(f"Initialized ObjectPool for {object_type.__name__} "
                    f"with {initial_size} instances")
    
    def _expand_pool(self, count: int) -> None:
        """
        Expand the pool by creating new objects.
        
        Args:
            count: Number of new objects to create
        """
        for _ in range(count):
            obj = self._factory()
            self._available.append(obj)
    
    def acquire(self) -> T:
        """
        Get an object from the pool.
        
        If no objects are available, the pool will expand automatically.
        
        Returns:
            An object of type T from the pool
        """
        if not self._available:
            # Double the pool size, but not beyond max_size
            current_total = len(self._in_use)
            expansion_size = min(current_total, self._max_size - current_total)
            
            # If we can't expand, create a temporary object
            if expansion_size <= 0:
                logger.warning(f"ObjectPool for {self._object_type.__name__} reached "
                              f"maximum size of {self._max_size}")
                return self._factory()
            
            self._expand_pool(expansion_size)
            logger.debug(f"Expanded ObjectPool for {self._object_type.__name__} "
                        f"by {expansion_size} instances")
        
        # Get an object from the available pool
        obj = self._available.pop()
        self._in_use[id(obj)] = obj
        
        return obj
    
    def release(self, obj: T) -> bool:
        """
        Return an object to the pool.
        
        Args:
            obj: The object to release back to the pool
            
        Returns:
            True if the object was released, False otherwise
        """
        obj_id = id(obj)
        
        # Check if this object is from our pool
        if obj_id not in self._in_use:
            logger.warning(f"Attempted to release an object not from this pool")
            return False
        
        # Reset the object if a reset function was provided
        if self._reset_func:
            self._reset_func(obj)
        
        # Remove from in-use and add to available
        del self._in_use[obj_id]
        
        # Only add back to available if we're not above max_size
        if len(self._available) < self._max_size:
            self._available.append(obj)
        
        return True
    
    def clear(self) -> None:
        """
        Clear the pool, removing all available objects.
        
        Note: This doesn't affect objects currently in use.
        """
        self._available.clear()
        logger.debug(f"Cleared available objects from {self._object_type.__name__} pool")
    
    def reset(self, initial_size: Optional[int] = None) -> None:
        """
        Reset the pool, clearing all available objects and pre-allocating new ones.
        
        Args:
            initial_size: Optional new initial size (defaults to original size)
        """
        self.clear()
        
        if initial_size is not None:
            self._expand_pool(initial_size)
            logger.debug(f"Reset {self._object_type.__name__} pool with {initial_size} instances")
    
    @property
    def available_count(self) -> int:
        """Get the number of available objects in the pool."""
        return len(self._available)
    
    @property
    def in_use_count(self) -> int:
        """Get the number of objects currently in use."""
        return len(self._in_use)
    
    @property
    def total_count(self) -> int:
        """Get the total number of objects managed by this pool."""
        return self.available_count + self.in_use_count


class PooledObjectMixin:
    """
    Mixin for objects that can be pooled.
    
    Adds functionality to track the pool an object belongs to and
    simplify returning the object to its pool.
    """
    
    def __init__(self):
        """Initialize with no pool reference."""
        self._pool = None
    
    def _set_pool(self, pool: ObjectPool) -> None:
        """
        Set the pool this object belongs to.
        
        Args:
            pool: The object pool
        """
        self._pool = pool
    
    def release(self) -> bool:
        """
        Release this object back to its pool.
        
        Returns:
            True if the object was released, False otherwise
        """
        if self._pool is None:
            return False
        
        return self._pool.release(self)


class CombatObjectPoolManager:
    """
    Manages multiple object pools for different types of combat objects.
    
    Provides a centralized way to access different pools for combat-related objects.
    """
    
    def __init__(self):
        """Initialize with empty pools dictionary."""
        self._pools: Dict[Type, ObjectPool] = {}
    
    def register_pool(self, object_type: Type, initial_size: int = 10,
                     factory: Optional[Callable[[], Any]] = None,
                     reset_func: Optional[Callable[[Any], None]] = None,
                     max_size: int = 1000) -> ObjectPool:
        """
        Register a new object pool for a type.
        
        Args:
            object_type: The type of objects to pool
            initial_size: Number of objects to pre-allocate
            factory: Optional custom factory function for creating objects
            reset_func: Optional function to reset object state when recycled
            max_size: Maximum number of objects to keep in the pool
            
        Returns:
            The created ObjectPool
        """
        pool = ObjectPool(object_type, initial_size, factory, reset_func, max_size)
        self._pools[object_type] = pool
        
        logger.info(f"Registered pool for {object_type.__name__} with "
                  f"initial size {initial_size}")
        
        return pool
    
    def get_pool(self, object_type: Type) -> Optional[ObjectPool]:
        """
        Get the pool for a specific object type.
        
        Args:
            object_type: The type of objects in the pool
            
        Returns:
            The ObjectPool for the type, or None if not registered
        """
        return self._pools.get(object_type)
    
    def acquire(self, object_type: Type) -> Any:
        """
        Acquire an object from the pool for a specific type.
        
        Args:
            object_type: The type of object to acquire
            
        Returns:
            An object from the pool
            
        Raises:
            KeyError: If no pool is registered for the type
        """
        if object_type not in self._pools:
            raise KeyError(f"No pool registered for type {object_type.__name__}")
        
        obj = self._pools[object_type].acquire()
        
        # If the object supports the PooledObjectMixin, set its pool
        if isinstance(obj, PooledObjectMixin):
            obj._set_pool(self._pools[object_type])
        
        return obj
    
    def release(self, obj: Any) -> bool:
        """
        Release an object back to its pool.
        
        Args:
            obj: The object to release
            
        Returns:
            True if the object was released, False otherwise
        """
        object_type = type(obj)
        
        if object_type not in self._pools:
            logger.warning(f"No pool registered for type {object_type.__name__}")
            return False
        
        return self._pools[object_type].release(obj)
    
    def reset_all_pools(self) -> None:
        """Reset all registered pools."""
        for pool in self._pools.values():
            pool.reset()
        
        logger.info(f"Reset all {len(self._pools)} object pools")
    
    def clear_all_pools(self) -> None:
        """Clear all registered pools."""
        for pool in self._pools.values():
            pool.clear()
        
        logger.info(f"Cleared all {len(self._pools)} object pools")
    
    def get_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Get statistics about all pools.
        
        Returns:
            Dictionary with pool statistics
        """
        stats = {}
        
        for obj_type, pool in self._pools.items():
            stats[obj_type.__name__] = {
                'available': pool.available_count,
                'in_use': pool.in_use_count,
                'total': pool.total_count
            }
        
        return stats


# Global instance for use throughout the combat system
combat_pool_manager = CombatObjectPoolManager() 