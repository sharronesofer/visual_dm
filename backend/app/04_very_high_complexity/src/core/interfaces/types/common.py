from typing import Any, Dict, List, Union



/**
 * Common type definitions and utility types used across the application.
 * @module types/common
 */
/**
 * Represents a unique identifier string
 */
ID = str
/**
 * Represents a Unix timestamp in milliseconds
 */
Timestamp = float
/**
 * Represents a UUID string
 */
UUID = str
/**
 * Makes all properties in T nullable (T | null)
 */
type Nullable<T> = { [P in keyof T]: T[P] | null }
/**
 * Makes all properties in T optional
 */
type Optional<T> = { [P in keyof T]?: T[P] }
/**
 * Makes all properties in T readonly
 */
type ReadOnly<T> = { readonly [P in keyof T]: T[P] }
/**
 * Base interface for all entities with common fields
 */
class BaseEntity:
    id: ID
    createdAt: Timestamp
    updatedAt: Timestamp
/**
 * Standard pagination parameters
 */
class PaginationParams:
    page: float
    limit: float
/**
 * Standard pagination metadata
 */
class PaginationMeta:
    currentPage: float
    totalPages: float
    totalItems: float
    itemsPerPage: float
    hasNextPage: bool
    hasPreviousPage: bool
/**
 * Generic paginated response
 */
interface PaginatedResponse<T> {
  items: List[T]
  meta: \'PaginationMeta\'
}
/**
 * Sort order options
 */
SortOrder = Union['asc', 'desc']
/**
 * Sort parameters for queries
 */
class SortParams:
    field: str
    order: SortOrder
/**
 * Generic filter operator types
 */
FilterOperator = Union[, 'eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'in', 'nin', 'like', 'nlike'] 
/**
 * Generic filter condition
 */
interface FilterCondition<T = any> {
  field: keyof T
  operator: FilterOperator
  value: Any
}
/**
 * Generic query parameters including pagination, sorting, and filtering
 */
interface QueryParams<T = any> {
  pagination?: \'PaginationParams\'
  sort?: SortParams[]
  filters?: FilterCondition<T>[]
}
/**
 * Generic success response
 */
interface SuccessResponse<T> {
  data: T
  message?: str
}
/**
 * Generic error response
 */
class ErrorResponse:
    error: Dict[str, Any]
/**
 * Generic async operation status
 */
AsyncStatus = Union['idle', 'loading', 'succeeded', 'failed']
/**
 * Generic async state with data, error, and status
 */
interface AsyncState<T, E = Error> {
  data: T | null
  error: E | null
  status: AsyncStatus
}
/**
 * Deep partial type for nested objects
 */
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}
/**
 * Record validation status
 */
ValidationStatus = Union['valid', 'invalid', 'pending']
/**
 * Generic validation result
 */
class ValidationResult:
    isValid: bool
    errors?: Dict[str, str[]>
/**
 * Generic cache options
 */
class CacheOptions:
    ttl?: float
    key?: str
    group?: str
/**
 * Generic event handler type
 */
type EventHandler<T = unknown> = (event: T) => void | Promise<void>
/**
 * Generic subscription handler
 */
class Subscription:
    unsubscribe: () => None
/**
 * Generic retry options
 */
class RetryOptions:
    maxAttempts: float
    delay: float
    backoffFactor?: float
/** Basic position interface */
class Position:
    x: float
    y: float
/** Common viewport interface */
class Viewport:
    x: float
    y: float
    width: float
    height: float
    zoom: float
/** Direction types */
Direction = Union['north', 'south', 'east', 'west']
BorderType = Union['normal', 'difficult', 'impassable', 'bridge', 'gate']
/** Border interface */
class Border:
    type: BorderType
    direction: Direction
    position: \'Position\'
/** Validation related types */
class ValidationError:
    field: str
    message: str
    type: Union['error', 'warning']
interface ApiResponse<T> {
  success: bool
  data?: T
  error?: str
}
/** Asset types */
class Asset:
    id: str
    type: str
    url: str
    metadata?: Dict[str, unknown>
/** Common state types */
class LoadingState:
    isLoading: bool
    error?: str
/** Common event types */
class InteractionEvent:
    type: str
    target: str
    data?: Dict[str, unknown>
    timestamp: float
/** Common configuration types */
class Config:
    apiUrl: str
    assetsPath: str
    debug: bool
    features: Dict[str, bool>
class Size:
    width: float
    height: float
class Dimensions:
    x: float
    y: float
class Rectangle:
    right: float
    bottom: float
AspectRatio = `${float}:${float}`
class ImageMetadata:
    size: \'Size\'
    aspectRatio: AspectRatio
    format: str
    quality?: float
TerrainType = Union['plains', 'forest', 'mountain', 'water', 'desert', 'swamp']
POIType = Union['city', 'dungeon', 'quest', 'landmark']