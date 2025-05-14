/**
 * Base entity types and interfaces
 * @module core/base/types/entity
 */

import { Timestamp, ID } from './common';

/**
 * Base entity interface with core properties
 */
export interface BaseEntity {
  id: string | number;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Entity supporting soft deletion
 */
export interface SoftDeletableEntity extends BaseEntity {
  deletedAt?: Date | null;
  isDeleted?: boolean;
}

/**
 * Entity supporting versioning
 */
export interface VersionedEntity extends BaseEntity {
  version: number;
}

/**
 * Entity supporting status tracking
 */
export interface StatusEntity extends BaseEntity {
  status: string;
  statusUpdatedAt?: Date;
}

/**
 * Entity supporting audit information
 */
export interface AuditableEntity extends BaseEntity {
  createdBy?: string | number;
  updatedBy?: string | number;
}

/**
 * Entity supporting publishing
 */
export interface PublishableEntity extends BaseEntity {
  isPublished?: boolean;
  publishedAt?: Date;
  publishedBy?: string | number;
}

/**
 * Comprehensive entity interface for advanced use cases
 */
export interface FullEntity extends
  BaseEntity,
  SoftDeletableEntity,
  VersionedEntity,
  StatusEntity,
  AuditableEntity,
  PublishableEntity {} 