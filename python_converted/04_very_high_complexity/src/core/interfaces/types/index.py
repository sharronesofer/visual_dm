from typing import Any, Dict, List, Union



/**
 * Base interface for all entities
 */
class BaseEntity:
    id: Union[str, float]
    createdAt?: Date
    updatedAt?: Date
    deletedAt?: Union[Date, None]
/**
 * Base query parameters interface with enhanced filtering and sorting
 */
class BaseQueryParams:
    page?: float
    limit?: float
    sort?: List[Union[str, str]]
    order?: List[Union['asc', 'desc', ('asc', 'desc')]]
    filter?: Dict[str, Any>
    search?: str
    include?: List[str]
    fields?: List[str]
/**
 * Service response interface with enhanced metadata
 */
interface ServiceResponse<T> {
  success: bool
  data?: T
  error?: Error
  meta?: {
    total?: float
    page?: float
    limit?: float
    [key: string]: Any
  }
}
/**
 * Bulk operation response interface
 */
interface BulkOperationResponse<T> {
  successful: List[T]
  failed: Array<{
    item: Partial<T>
    error: Error
  }>
  totalProcessed: float
  totalSuccessful: float
  totalFailed: float
}
interface ApiResponse<T> {
  data: T
  status: float
  message?: str
}
interface PaginatedResponse<T> extends ApiResponse<T[]> {
  total: float
  page: float
  limit: float
}
class ErrorResponse:
    message: str
    code: str
    details?: Dict[str, unknown>
class AppConfig:
    apiUrl: str
    wsUrl: str
    environment: Union['development', 'staging', 'production']
    version: str
class User:
    id: str
    email: str
    username: str
    role: Union['admin', 'user']
    createdAt: str
    updatedAt: str
class AuthState:
    user: Union[User, None]
    token: Union[str, None]
    isAuthenticated: bool
    isLoading: bool
class MediaAsset:
    id: str
    filename: str
    size: float
    type: str
    mimeType: str
    thumbnailUrl: Union[str, None]
    url: str
    createdAt: str
    updatedAt: str
Theme = Union['light', 'dark']