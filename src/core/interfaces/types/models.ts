/**
 * Domain models and DTOs for the application.
 * @module types/models
 */

import type { BaseEntity, ID, Timestamp } from './common';

/**
 * User roles in the system
 */
export type UserRole = 'admin' | 'user' | 'guest';

/**
 * User status in the system
 */
export type UserStatus = 'active' | 'inactive' | 'suspended';

/**
 * Base user interface representing a user in the system
 */
export interface User extends BaseEntity {
  email: string;
  username: string;
  role: UserRole;
  status: UserStatus;
  lastLoginAt?: Timestamp;
}

/**
 * DTO for creating a new user
 */
export interface CreateUserDTO {
  email: string;
  username: string;
  password: string;
  role?: UserRole;
}

/**
 * DTO for updating an existing user
 */
export interface UpdateUserDTO {
  email?: string;
  username?: string;
  role?: UserRole;
  status?: UserStatus;
}

/**
 * Resource type in the system
 */
export type ResourceType = 'file' | 'folder' | 'document' | 'image';

/**
 * Resource access level
 */
export type AccessLevel = 'read' | 'write' | 'admin';

/**
 * Base resource interface
 */
export interface Resource extends BaseEntity {
  name: string;
  type: ResourceType;
  ownerId: ID;
  parentId?: ID;
  metadata?: Record<string, unknown>;
}

/**
 * DTO for creating a new resource
 */
export interface CreateResourceDTO {
  name: string;
  type: ResourceType;
  parentId?: ID;
  metadata?: Record<string, unknown>;
}

/**
 * DTO for updating an existing resource
 */
export interface UpdateResourceDTO {
  name?: string;
  parentId?: ID;
  metadata?: Record<string, unknown>;
}

/**
 * Permission interface for resource access control
 */
export interface Permission extends BaseEntity {
  resourceId: ID;
  userId: ID;
  level: AccessLevel;
}

/**
 * DTO for creating a new permission
 */
export interface CreatePermissionDTO {
  resourceId: ID;
  userId: ID;
  level: AccessLevel;
}

/**
 * DTO for updating an existing permission
 */
export interface UpdatePermissionDTO {
  level: AccessLevel;
}

/**
 * Tag interface for resource categorization
 */
export interface Tag extends BaseEntity {
  name: string;
  color?: string;
  description?: string;
}

/**
 * DTO for creating a new tag
 */
export interface CreateTagDTO {
  name: string;
  color?: string;
  description?: string;
}

/**
 * DTO for updating an existing tag
 */
export interface UpdateTagDTO {
  name?: string;
  color?: string;
  description?: string;
}

/**
 * Comment interface for resource discussions
 */
export interface Comment extends BaseEntity {
  resourceId: ID;
  userId: ID;
  content: string;
  parentId?: ID;
  editedAt?: Timestamp;
}

/**
 * DTO for creating a new comment
 */
export interface CreateCommentDTO {
  resourceId: ID;
  content: string;
  parentId?: ID;
}

/**
 * DTO for updating an existing comment
 */
export interface UpdateCommentDTO {
  content: string;
}

/**
 * Activity type in the system
 */
export type ActivityType = 'create' | 'update' | 'delete' | 'share' | 'comment' | 'tag';

/**
 * Activity interface for tracking user actions
 */
export interface Activity extends BaseEntity {
  userId: ID;
  resourceId: ID;
  type: ActivityType;
  metadata?: Record<string, unknown>;
}

/**
 * Notification type in the system
 */
export type NotificationType = 'mention' | 'share' | 'comment' | 'system' | 'material_refund';

/**
 * Notification status
 */
export type NotificationStatus = 'unread' | 'read' | 'archived';

/**
 * Notification interface for user notifications
 */
export interface Notification extends BaseEntity {
  userId: ID;
  type: NotificationType;
  status: NotificationStatus;
  title: string;
  message: string;
  metadata?: Record<string, unknown>;
  readAt?: Timestamp;
}

/**
 * DTO for creating a new notification
 */
export interface CreateNotificationDTO {
  userId: ID;
  type: NotificationType;
  title: string;
  message: string;
  metadata?: Record<string, unknown>;
}

/**
 * DTO for updating an existing notification
 */
export interface UpdateNotificationDTO {
  status?: NotificationStatus;
  readAt?: Timestamp;
}

/**
 * Search result interface
 */
export interface SearchResult<T extends BaseEntity> {
  entity: T;
  score: number;
  highlights?: Record<string, string[]>;
}

/**
 * Bulk operation result interface
 */
export interface BulkOperationResult {
  successful: ID[];
  failed: Array<{
    id: ID;
    error: string;
  }>;
  total: number;
  successCount: number;
  failureCount: number;
}

export function createMaterialRefundNotification(userId: ID, refunded: Record<string, number>): CreateNotificationDTO {
  return {
    userId,
    type: 'material_refund',
    title: 'Building Materials Refunded',
    message: `You have received refunded materials: ${Object.entries(refunded)
      .map(([mat, qty]) => `${qty}x ${mat}`)
      .join(', ')}`,
    metadata: { refunded }
  };
}
