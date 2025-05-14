from typing import Any, Dict, List, Union
from enum import Enum


/**
 * Common type definitions
 * @module core/base/types/common
 */
/**
 * Generic ID type that can be string or number
 */
ID = Union[str, float]
/**
 * Timestamp type alias for Date
 */
Timestamp = Date
/**
 * Generic response type for service operations
 */
interface ServiceResponse<T = any> {
  success: bool
  data?: T
  error?: Error
  metadata?: Record<string, any>
}
/**
 * Pagination parameters
 */
class PaginationParams:
    page?: float
    limit?: float
    offset?: float
/**
 * Paginated response
 */
interface PaginatedResponse<T> {
  items: List[T]
  total: float
  page: float
  limit: float
  hasMore: bool
}
/**
 * Query parameters for filtering and sorting
 */
interface QueryParams<T = any> {
  filter?: Partial<T>
  sort?: {
    [K in keyof T]?: 'asc' | 'desc'
  }
  search?: str
  include?: string[]
}
/**
 * Cache options
 */
class CacheOptions:
    ttl?: float
    key?: str
    namespace?: str
    version?: str
/**
 * Retry options
 */
class RetryOptions:
    maxRetries?: float
    retryDelay?: float
    retryableStatuses?: List[float]
/**
 * Service configuration
 */
class ServiceConfig:
    baseURL?: str
    timeout?: float
    headers?: Dict[str, str>
    cache?: \'CacheOptions\'
    retry?: \'RetryOptions\'
/**
 * Validation error
 */
class ValidationError:
    field: str
    message: str
    code?: str
    value?: Any
/**
 * Validation result
 */
class ValidationResult:
    isValid: bool
    errors: List[ValidationError]
/**
 * Service event types
 */
class ServiceEventType(Enum):
    Created = 'created'
    Updated = 'updated'
    Deleted = 'deleted'
    Error = 'error'
/**
 * Service event payload
 */
interface ServiceEvent<T = any> {
  type: \'ServiceEventType\'
  data?: T
  error?: Error
  metadata?: Record<string, any>
  timestamp: Date
}
/**
 * Service event handler
 */
type ServiceEventHandler<T = any> = (event: ServiceEvent<T>) => void | Promise<void> 