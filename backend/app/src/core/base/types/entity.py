from typing import Any, Union


/**
 * Base entity types and interfaces
 * @module core/base/types/entity
 */
/**
 * Base entity interface with core properties
 */
class BaseEntity:
    id: Union[str, float]
    createdAt: Date
    updatedAt: Date
/**
 * Entity supporting soft deletion
 */
class SoftDeletableEntity:
    deletedAt?: Union[Date, None]
    isDeleted?: bool
/**
 * Entity supporting versioning
 */
class VersionedEntity:
    version: float
/**
 * Entity supporting status tracking
 */
class StatusEntity:
    status: str
    statusUpdatedAt?: Date
/**
 * Entity supporting audit information
 */
class AuditableEntity:
    createdBy?: Union[str, float]
    updatedBy?: Union[str, float]
/**
 * Entity supporting publishing
 */
class PublishableEntity:
    isPublished?: bool
    publishedAt?: Date
    publishedBy?: Union[str, float]
/**
 * Comprehensive entity interface for advanced use cases
 */
interface FullEntity extends
  BaseEntity,
  SoftDeletableEntity,
  VersionedEntity,
  StatusEntity,
  AuditableEntity,
  PublishableEntity {} 