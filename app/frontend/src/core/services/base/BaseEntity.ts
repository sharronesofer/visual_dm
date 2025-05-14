/**
 * BaseEntity interface: foundational type for all entities in the system.
 * All entities should extend this interface for consistency.
 */
export interface BaseEntity {
  /** Unique identifier (UUID) */
  id: string;
  /** Creation timestamp */
  createdAt: Date;
  /** Last update timestamp */
  updatedAt: Date;
  /** Whether the entity is active (default: true) */
  isActive: boolean;
}

// Example of extension:
// export interface User extends BaseEntity {
//   email: string;
//   ...
// } 