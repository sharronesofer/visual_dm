from typing import Any, Dict, List, Union



/**
 * Common type definitions used across the application
 */
/**
 * Generic ID type that can be either string or number
 */
ID = Union[str, float]
/**
 * Generic type for pagination parameters
 */
class PaginationParams:
    page?: float
    limit?: float
    offset?: float
/**
 * Generic type for sort parameters
 */
class SortParams:
    field: str
    order: Union['asc', 'desc']
/**
 * Generic type for query filters
 */
class QueryFilters:
    [key: Union[str]: str, float, bool, List[str, float>, None]
/**
 * Generic type for API response
 */
interface ApiResponse<T> {
  data: T
  meta?: {
    page?: float
    limit?: float
    total?: float
    [key: string]: Any
  }
}
/**
 * Generic type for error response
 */
class ErrorResponse:
    code: str
    message: str
    details?: Dict[str, Any>
/**
 * Type for file upload metadata
 */
class FileUploadMetadata:
    originalName: str
    size: float
    mimeType: str
    encoding: str
    [key: str]: Any
/**
 * Type for audit information
 */
class AuditInfo:
    createdBy?: str
    createdAt: Date
    updatedBy?: str
    updatedAt: Date
    version?: float
/**
 * Type for geolocation coordinates
 */
class GeoCoordinates:
    latitude: float
    longitude: float
/**
 * Type for search parameters
 */
class SearchParams:
    query: str
    filters?: \'QueryFilters\'
    sort?: \'SortParams\'
    pagination?: \'PaginationParams\'
/**
 * Type for configuration options
 */
class ConfigOptions:
    [key: Union[str]: str, float, bool, None, ConfigOptions] 