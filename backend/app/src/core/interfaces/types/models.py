from typing import Any, Dict, List, Union


/**
 * Domain models and DTOs for the application.
 * @module types/models
 */
/**
 * User roles in the system
 */
UserRole = Union['admin', 'user', 'guest']
/**
 * User status in the system
 */
UserStatus = Union['active', 'inactive', 'suspended']
/**
 * Base user interface representing a user in the system
 */
class User:
    email: str
    username: str
    role: UserRole
    status: UserStatus
    lastLoginAt?: Timestamp
/**
 * DTO for creating a new user
 */
class CreateUserDTO:
    email: str
    username: str
    password: str
    role?: UserRole
/**
 * DTO for updating an existing user
 */
class UpdateUserDTO:
    email?: str
    username?: str
    role?: UserRole
    status?: UserStatus
/**
 * Resource type in the system
 */
ResourceType = Union['file', 'folder', 'document', 'image']
/**
 * Resource access level
 */
AccessLevel = Union['read', 'write', 'admin']
/**
 * Base resource interface
 */
class Resource:
    name: str
    type: ResourceType
    ownerId: ID
    parentId?: ID
    metadata?: Dict[str, unknown>
/**
 * DTO for creating a new resource
 */
class CreateResourceDTO:
    name: str
    type: ResourceType
    parentId?: ID
    metadata?: Dict[str, unknown>
/**
 * DTO for updating an existing resource
 */
class UpdateResourceDTO:
    name?: str
    parentId?: ID
    metadata?: Dict[str, unknown>
/**
 * Permission interface for resource access control
 */
class Permission:
    resourceId: ID
    userId: ID
    level: AccessLevel
/**
 * DTO for creating a new permission
 */
class CreatePermissionDTO:
    resourceId: ID
    userId: ID
    level: AccessLevel
/**
 * DTO for updating an existing permission
 */
class UpdatePermissionDTO:
    level: AccessLevel
/**
 * Tag interface for resource categorization
 */
class Tag:
    name: str
    color?: str
    description?: str
/**
 * DTO for creating a new tag
 */
class CreateTagDTO:
    name: str
    color?: str
    description?: str
/**
 * DTO for updating an existing tag
 */
class UpdateTagDTO:
    name?: str
    color?: str
    description?: str
/**
 * Comment interface for resource discussions
 */
class Comment:
    resourceId: ID
    userId: ID
    content: str
    parentId?: ID
    editedAt?: Timestamp
/**
 * DTO for creating a new comment
 */
class CreateCommentDTO:
    resourceId: ID
    content: str
    parentId?: ID
/**
 * DTO for updating an existing comment
 */
class UpdateCommentDTO:
    content: str
/**
 * Activity type in the system
 */
ActivityType = Union['create', 'update', 'delete', 'share', 'comment', 'tag']
/**
 * Activity interface for tracking user actions
 */
class Activity:
    userId: ID
    resourceId: ID
    type: ActivityType
    metadata?: Dict[str, unknown>
/**
 * Notification type in the system
 */
NotificationType = Union['mention', 'share', 'comment', 'system']
/**
 * Notification status
 */
NotificationStatus = Union['unread', 'read', 'archived']
/**
 * Notification interface for user notifications
 */
class Notification:
    userId: ID
    type: NotificationType
    status: NotificationStatus
    title: str
    message: str
    metadata?: Dict[str, unknown>
    readAt?: Timestamp
/**
 * DTO for creating a new notification
 */
class CreateNotificationDTO:
    userId: ID
    type: NotificationType
    title: str
    message: str
    metadata?: Dict[str, unknown>
/**
 * DTO for updating an existing notification
 */
class UpdateNotificationDTO:
    status?: NotificationStatus
    readAt?: Timestamp
/**
 * Search result interface
 */
interface SearchResult<T extends BaseEntity> {
  entity: T
  score: float
  highlights?: Record<string, string[]>
}
/**
 * Bulk operation result interface
 */
class BulkOperationResult:
    successful: List[ID]
    failed: List[{
    id: ID
    error: str>
  total: float
  successCount: float
  failureCount: float
}