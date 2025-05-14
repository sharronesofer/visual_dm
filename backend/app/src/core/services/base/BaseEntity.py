from typing import Any


/**
 * BaseEntity interface: foundational type for all entities in the system.
 * All entities should extend this interface for consistency.
 */
class BaseEntity:
    /** Unique identifier (UUID) */
  id: str
    /** Creation timestamp */
  createdAt: Date
    /** Last update timestamp */
  updatedAt: Date
    /** Whether the entity is active (default: true) */
  isActive: bool