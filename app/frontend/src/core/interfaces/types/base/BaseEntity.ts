/**
 * Base interface for all entities in the system
 */
export interface BaseEntity {
  /** Unique identifier for the entity */
  id: string;
  
  /** Creation timestamp */
  createdAt: Date;
  
  /** Last update timestamp */
  updatedAt: Date;
  
  /** Optional deletion timestamp */
  deletedAt?: Date;
  
  /** Version number for optimistic concurrency */
  version: number;
} 