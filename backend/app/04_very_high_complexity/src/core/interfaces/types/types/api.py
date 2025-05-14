from typing import Any, Dict, Union



/**
 * Base API Response interface
 */
interface IApiResponse<T = unknown> {
  status: (typeof API_RESPONSE_STATUS)[keyof typeof API_RESPONSE_STATUS]
  data: T
  message?: str
  timestamp: str
  requestId?: str
}
/**
 * Error Response interface
 */
class IApiErrorResponse:
    status: typeof API_RESPONSE_STATUS.ERROR
    error: Dict[str, Any]
/**
 * Paginated Response interface
 */
interface IPaginatedResponse<T> extends IApiResponse<T[]> {
  pagination: Dict[str, Any]
}
/**
 * Search Response interface
 */
interface ISearchResponse<T> extends IPaginatedResponse<T> {
  query: str
  filters?: Record<string, unknown>
  sortBy?: str
  sortOrder?: 'asc' | 'desc'
}
/**
 * Pagination Query Parameters
 */
class IPaginationQuery:
    page?: float
    limit?: float
/**
 * Search Query Parameters
 */
class ISearchQuery:
    query?: str
    filters?: Dict[str, unknown>
    sortBy?: str
    sortOrder?: Union['asc', 'desc']
/**
 * API Request Options
 */
class IApiRequestOptions:
    headers?: Dict[str, str>
    timeout?: float
    signal?: AbortSignal
    withCredentials?: bool
    responseType?: Union['json', 'blob', 'text', 'arraybuffer']
    cache?: bool
    retry?: bool
    maxRetries?: float
    retryDelay?: float
/**
 * File Upload Response
 */
class IFileUploadResponse:
    data: Dict[str, Any]
/**
 * Bulk Operation Response
 */
interface IBulkOperationResponse<T> extends IApiResponse {
  data: Dict[str, Any]>
    totalProcessed: float
    totalSuccessful: float
    totalFailed: float
  }
}
/**
 * WebSocket Message
 */
interface IWebSocketMessage<T = unknown> {
  type: str
  payload: T
  timestamp: str
}
/**
 * API Error Details
 */
class IApiErrorDetails:
    field?: str
    code: str
    message: str
    params?: Dict[str, unknown>
/**
 * Auth Tokens
 */
class IAuthTokens:
    accessToken: str
    refreshToken: str
    expiresIn: float
    tokenType: str
/**
 * API Health Check Response
 */
class IHealthCheckResponse:
    data: Union[{
    status: 'healthy', 'degraded', 'unhealthy']
    version: str
    uptime: float
    timestamp: str
    services: Union[Dict[
      str,
      {
        status: 'up', 'down']
    latency: float
    >
  }
}