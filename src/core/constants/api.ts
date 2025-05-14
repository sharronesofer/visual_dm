/**
 * API Endpoints
 */
export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REGISTER: '/auth/register',
    REFRESH_TOKEN: '/auth/refresh',
    VERIFY_EMAIL: '/auth/verify-email',
    RESET_PASSWORD: '/auth/reset-password',
    CHANGE_PASSWORD: '/auth/change-password',
  },

  // User endpoints
  USER: {
    PROFILE: '/users/profile',
    SETTINGS: '/users/settings',
    PREFERENCES: '/users/preferences',
  },

  // POI endpoints
  POI: {
    BASE: '/pois',
    DETAILS: (id: string) => `/pois/${id}`,
    SEARCH: '/pois/search',
    NEARBY: '/pois/nearby',
    CATEGORIES: '/pois/categories',
  },

  // Character endpoints
  CHARACTER: {
    BASE: '/characters',
    DETAILS: (id: string) => `/characters/${id}`,
    INVENTORY: (id: string) => `/characters/${id}/inventory`,
    SKILLS: (id: string) => `/characters/${id}/skills`,
    STATS: (id: string) => `/characters/${id}/stats`,
  },

  // Wizard endpoints
  WIZARD: {
    BASE: '/wizards',
    DETAILS: (id: string) => `/wizards/${id}`,
    TEMPLATES: '/wizards/templates',
    STATE: (id: string) => `/wizards/${id}/state`,
    STEP: (id: string, step: number) => `/wizards/${id}/steps/${step}`,
  },
} as const;

/**
 * HTTP Methods
 */
export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  PATCH: 'PATCH',
  DELETE: 'DELETE',
  HEAD: 'HEAD',
  OPTIONS: 'OPTIONS',
} as const;

/**
 * HTTP Status Codes
 */
export const HTTP_STATUS = {
  // 2xx Success
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,

  // 3xx Redirection
  MOVED_PERMANENTLY: 301,
  FOUND: 302,
  NOT_MODIFIED: 304,
  TEMPORARY_REDIRECT: 307,
  PERMANENT_REDIRECT: 308,

  // 4xx Client Errors
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

  // 5xx Server Errors
  INTERNAL_SERVER_ERROR: 500,
  NOT_IMPLEMENTED: 501,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

/**
 * API Configuration Constants
 * @description Defines all API-related configuration constants used throughout the application.
 */

/**
 * Base API configuration
 */
export const API_CONFIG = {
  /** Base URL for API endpoints */
  BASE_URL: process.env.API_BASE_URL || 'http://localhost:3000/api',

  /** WebSocket endpoint URL */
  SOCKET_URL: process.env.SOCKET_URL || 'ws://localhost:3000/ws',

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
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  } as const,

  /** Authentication header name */
  AUTH_HEADER: 'Authorization',

  /** Bearer token prefix */
  TOKEN_PREFIX: 'Bearer',
} as const;

/**
 * API Response Status
 */
export const API_RESPONSE_STATUS = {
  SUCCESS: 'success',
  ERROR: 'error',
  PENDING: 'pending',
} as const;

/**
 * API Error Types
 */
export const API_ERROR_TYPES = {
  NETWORK: 'network_error',
  VALIDATION: 'validation_error',
  AUTHENTICATION: 'authentication_error',
  AUTHORIZATION: 'authorization_error',
  NOT_FOUND: 'not_found_error',
  RATE_LIMIT: 'rate_limit_error',
  SERVER: 'server_error',
} as const;

/**
 * WebSocket Events
 */
export const WS_EVENTS = {
  // Connection events
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  RECONNECT: 'reconnect',
  ERROR: 'error',

  // User events
  USER_STATUS_CHANGE: 'user:status',
  USER_ACTIVITY: 'user:activity',

  // Notification events
  NOTIFICATION_RECEIVED: 'notification:received',
  NOTIFICATION_READ: 'notification:read',

  // Real-time updates
  DATA_UPDATED: 'data:updated',
  DATA_DELETED: 'data:deleted',
  DATA_CREATED: 'data:created',
} as const;

/**
 * API Feature Flags
 */
export const API_FEATURES = {
  ENABLE_CACHING: true,
  ENABLE_RETRY: true,
  ENABLE_COMPRESSION: true,
  ENABLE_RATE_LIMITING: true,
  ENABLE_METRICS: true,
} as const;

/**
 * API Rate Limits
 */
export const API_RATE_LIMITS = {
  DEFAULT: {
    WINDOW_MS: 60000, // 1 minute
    MAX_REQUESTS: 100,
  },
  AUTH: {
    WINDOW_MS: 300000, // 5 minutes
    MAX_REQUESTS: 20,
  },
  SEARCH: {
    WINDOW_MS: 60000, // 1 minute
    MAX_REQUESTS: 50,
  },
} as const;

/**
 * API Metrics
 */
export const API_METRICS = {
  ENABLE_PERFORMANCE_TRACKING: true,
  ENABLE_ERROR_TRACKING: true,
  ENABLE_USAGE_TRACKING: true,
  ENABLE_API_METRICS: true,
  TRACKING_SAMPLE_RATE: 0.1,
} as const;
