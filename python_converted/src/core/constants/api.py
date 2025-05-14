from typing import Any, Dict


/**
 * API Endpoints
 */
const API_ENDPOINTS = {
  AUTH: Dict[str, Any],
  USER: Dict[str, Any],
  POI: Dict[str, Any]`,
    SEARCH: '/pois/search',
    NEARBY: '/pois/nearby',
    CATEGORIES: '/pois/categories',
  },
  CHARACTER: Dict[str, Any]`,
    INVENTORY: (id: str) => `/characters/${id}/inventory`,
    SKILLS: (id: str) => `/characters/${id}/skills`,
    STATS: (id: str) => `/characters/${id}/stats`,
  },
  WIZARD: Dict[str, Any]`,
    TEMPLATES: '/wizards/templates',
    STATE: (id: str) => `/wizards/${id}/state`,
    STEP: (id: str, step: float) => `/wizards/${id}/steps/${step}`,
  },
} as const
/**
 * HTTP Methods
 */
const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  PATCH: 'PATCH',
  DELETE: 'DELETE',
  HEAD: 'HEAD',
  OPTIONS: 'OPTIONS',
} as const
/**
 * HTTP Status Codes
 */
const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  MOVED_PERMANENTLY: 301,
  FOUND: 302,
  NOT_MODIFIED: 304,
  TEMPORARY_REDIRECT: 307,
  PERMANENT_REDIRECT: 308,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  CONFLICT: 409,
  GONE: 410,
  PRECONDITION_FAILED: 412,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  NOT_IMPLEMENTED: 501,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const
/**
 * API Configuration Constants
 * @description Defines all API-related configuration constants used throughout the application.
 */
/**
 * Base API configuration
 */
const API_CONFIG = {
  /** Base URL for API endpoints */
  BASE_URL: process.env.API_BASE_URL || 'http:
  /** WebSocket endpoint URL */
  SOCKET_URL: process.env.SOCKET_URL || 'ws:
  /** Default API version */
  API_VERSION: 'v1',
  /** Default request timeout in milliseconds */
  REQUEST_TIMEOUT: 30000,
  /** Maximum number of retries for failed requests */
  MAX_RETRIES: 3,
  /** Base delay between retries in milliseconds */
  RETRY_DELAY: 1000,
  /** Maximum backoff delay in milliseconds */
  MAX_RETRY_DELAY: 10000,
  /** Default headers */
  DEFAULT_HEADERS: Dict[str, Any] as const,
  /** Authentication header name */
  AUTH_HEADER: 'Authorization',
  /** Bearer token prefix */
  TOKEN_PREFIX: 'Bearer',
} as const
/**
 * API Response Status
 */
const API_RESPONSE_STATUS = {
  SUCCESS: 'success',
  ERROR: 'error',
  PENDING: 'pending',
} as const
/**
 * API Error Types
 */
const API_ERROR_TYPES = {
  NETWORK: 'network_error',
  VALIDATION: 'validation_error',
  AUTHENTICATION: 'authentication_error',
  AUTHORIZATION: 'authorization_error',
  NOT_FOUND: 'not_found_error',
  RATE_LIMIT: 'rate_limit_error',
  SERVER: 'server_error',
} as const
/**
 * WebSocket Events
 */
const WS_EVENTS = {
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  RECONNECT: 'reconnect',
  ERROR: 'error',
  USER_STATUS_CHANGE: 'user:status',
  USER_ACTIVITY: 'user:activity',
  NOTIFICATION_RECEIVED: 'notification:received',
  NOTIFICATION_READ: 'notification:read',
  DATA_UPDATED: 'data:updated',
  DATA_DELETED: 'data:deleted',
  DATA_CREATED: 'data:created',
} as const
/**
 * API Feature Flags
 */
const API_FEATURES = {
  ENABLE_CACHING: true,
  ENABLE_RETRY: true,
  ENABLE_COMPRESSION: true,
  ENABLE_RATE_LIMITING: true,
  ENABLE_METRICS: true,
} as const
/**
 * API Rate Limits
 */
const API_RATE_LIMITS = {
  DEFAULT: Dict[str, Any],
  AUTH: Dict[str, Any],
  SEARCH: Dict[str, Any],
} as const
/**
 * API Metrics
 */
const API_METRICS = {
  ENABLE_PERFORMANCE_TRACKING: true,
  ENABLE_ERROR_TRACKING: true,
  ENABLE_USAGE_TRACKING: true,
  ENABLE_API_METRICS: true,
  TRACKING_SAMPLE_RATE: 0.1,
} as const