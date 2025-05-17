import time
import random
import string
import uuid
import threading
from typing import Optional, Dict, Set

class IDGenerator:
    """
    Enhanced ID generator class with improved uniqueness guarantees,
    sortability, and collision detection/resolution.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._generated_ids: Set[str] = set()
        self._collision_count = 0
        self._sequence_counter = 0

    def generate_unique_id(self, prefix: str = "") -> str:
        """
        Generates a unique, sortable identifier using timestamp, sequence counter,
        and random string with collision detection.
        
        Args:
            prefix: Optional string prefix to identify the source/type of ID
        
        Returns:
            A unique string identifier guaranteed to be unique even under high concurrency
        """
        with self._lock:
            # Increment sequence to ensure uniqueness even if generated in same millisecond
            self._sequence_counter = (self._sequence_counter + 1) % 10000
            
            # Get current timestamp (milliseconds since epoch)
            timestamp = int(time.time() * 1000)
            
            # Generate base ID with sortable timestamp prefix
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            base_id = f"{prefix}{timestamp:015d}_{self._sequence_counter:04d}_{random_str}"
            
            # Check for collisions (extremely unlikely but handled for robustness)
            if base_id in self._generated_ids:
                self._collision_count += 1
                # Add collision count to ensure uniqueness
                base_id = f"{base_id}_{self._collision_count}"
                
            # Store ID to detect any future collisions
            self._generated_ids.add(base_id)
            return base_id
    
    def generate_uuid(self, namespace: Optional[uuid.UUID] = None, 
                     name: Optional[str] = None) -> str:
        """
        Generates a UUID (v4 by default, or v5 if namespace and name are provided).
        More robust than the simple ID generator, especially for distributed systems.
        
        Args:
            namespace: Optional UUID namespace for v5 UUID generation
            name: Optional name string for v5 UUID generation
        
        Returns:
            A string representation of the UUID.
        """
        if namespace and name:
            # Generate a v5 UUID (deterministic based on namespace and name)
            return str(uuid.uuid5(namespace, name))
        else:
            # Generate a random v4 UUID
            return str(uuid.uuid4())

    def clear_id_cache(self):
        """
        Clears the cache of generated IDs.
        Should be used carefully, typically for testing or when ID history is no longer needed.
        """
        with self._lock:
            self._generated_ids.clear()
            self._collision_count = 0

# Create a singleton instance of the ID generator
_id_generator = IDGenerator()

# Provide module-level functions for backward compatibility
def generate_unique_id(prefix: str = "") -> str:
    """
    Backward-compatible function for generating unique IDs.
    Uses the singleton ID generator instance.
    """
    return _id_generator.generate_unique_id(prefix)

def generate_uuid(namespace: Optional[uuid.UUID] = None, name: Optional[str] = None) -> str:
    """
    Backward-compatible function for generating UUIDs.
    Uses the singleton ID generator instance.
    """
    return _id_generator.generate_uuid(namespace, name) 