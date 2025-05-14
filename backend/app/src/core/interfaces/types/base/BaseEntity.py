from typing import Any


/**
 * Base interface for all entities in the system
 */
class BaseEntity:
    /** Unique identifier for the entity */
  id: str
    /** Creation timestamp */
  createdAt: Date
    /** Last update timestamp */
  updatedAt: Date
    /** Optional deletion timestamp */
  deletedAt?: Date
    /** Version number for optimistic concurrency */
  version: float 