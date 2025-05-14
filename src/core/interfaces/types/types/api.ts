import { API_RESPONSE_STATUS } from '../constants/api';

/**
 * Base API Response interface
 */
export interface IApiResponse<T = unknown> {
  status: (typeof API_RESPONSE_STATUS)[keyof typeof API_RESPONSE_STATUS];
  data: T;
  message?: string;
  timestamp: string;
  requestId?: string;
}

/**
 * Error Response interface
 */
export interface IApiErrorResponse {
  status: typeof API_RESPONSE_STATUS.ERROR;
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  timestamp: string;
  requestId?: string;
}

/**
 * Paginated Response interface
 */
export interface IPaginatedResponse<T> extends IApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    totalItems: number;
    totalPages: number;
    hasNextPage: boolean;
    hasPrevPage: boolean;
  };
}

/**
 * Search Response interface
 */
export interface ISearchResponse<T> extends IPaginatedResponse<T> {
  query: string;
  filters?: Record<string, unknown>;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

/**
 * Pagination Query Parameters
 */
export interface IPaginationQuery {
  page?: number;
  limit?: number;
}

/**
 * Search Query Parameters
 */
export interface ISearchQuery extends IPaginationQuery {
  query?: string;
  filters?: Record<string, unknown>;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

/**
 * API Request Options
 */
export interface IApiRequestOptions {
  headers?: Record<string, string>;
  timeout?: number;
  signal?: AbortSignal;
  withCredentials?: boolean;
  responseType?: 'json' | 'blob' | 'text' | 'arraybuffer';
  cache?: boolean;
  retry?: boolean;
  maxRetries?: number;
  retryDelay?: number;
}

/**
 * File Upload Response
 */
export interface IFileUploadResponse extends IApiResponse {
  data: {
    url: string;
    filename: string;
    size: number;
    mimeType: string;
  };
}

/**
 * Bulk Operation Response
 */
export interface IBulkOperationResponse<T> extends IApiResponse {
  data: {
    successful: T[];
    failed: Array<{
      item: T;
      error: string;
    }>;
    totalProcessed: number;
    totalSuccessful: number;
    totalFailed: number;
  };
}

/**
 * WebSocket Message
 */
export interface IWebSocketMessage<T = unknown> {
  type: string;
  payload: T;
  timestamp: string;
}

/**
 * API Error Details
 */
export interface IApiErrorDetails {
  field?: string;
  code: string;
  message: string;
  params?: Record<string, unknown>;
}

/**
 * Auth Tokens
 */
export interface IAuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: string;
}

/**
 * API Health Check Response
 */
export interface IHealthCheckResponse extends IApiResponse {
  data: {
    status: 'healthy' | 'degraded' | 'unhealthy';
    version: string;
    uptime: number;
    timestamp: string;
    services: Record<
      string,
      {
        status: 'up' | 'down';
        latency: number;
      }
    >;
  };
}
