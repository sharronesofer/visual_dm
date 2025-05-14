/**
 * Error Constants
 * @description Defines error codes, messages, and categories used throughout the application.
 */

/**
 * Error Categories
 */
export const ERROR_CATEGORIES = {
  /** Validation errors */
  VALIDATION: 'validation',

  /** Authentication errors */
  AUTH: 'authentication',

  /** Authorization errors */
  PERMISSION: 'authorization',

  /** Network errors */
  NETWORK: 'network',

  /** Server errors */
  SERVER: 'server',

  /** Client errors */
  CLIENT: 'client',

  /** Database errors */
  DATABASE: 'database',

  /** Business logic errors */
  BUSINESS: 'business',

  /** External service errors */
  EXTERNAL: 'external',
} as const;

/**
 * Error Codes
 */
export const ERROR_CODES = {
  // Validation Errors (1xxx)
  VALIDATION: {
    INVALID_INPUT: 1000,
    REQUIRED_FIELD: 1001,
    INVALID_FORMAT: 1002,
    INVALID_TYPE: 1003,
    OUT_OF_RANGE: 1004,
    TOO_SHORT: 1005,
    TOO_LONG: 1006,
    DUPLICATE_VALUE: 1007,
    INVALID_ENUM: 1008,
    INVALID_DATE: 1009,
  },

  // Authentication Errors (2xxx)
  AUTH: {
    UNAUTHORIZED: 2000,
    INVALID_CREDENTIALS: 2001,
    EXPIRED_TOKEN: 2002,
    INVALID_TOKEN: 2003,
    ACCOUNT_LOCKED: 2004,
    ACCOUNT_DISABLED: 2005,
    INVALID_REFRESH_TOKEN: 2006,
    SESSION_EXPIRED: 2007,
    INVALID_MFA_CODE: 2008,
    MFA_REQUIRED: 2009,
  },

  // Authorization Errors (3xxx)
  PERMISSION: {
    FORBIDDEN: 3000,
    INSUFFICIENT_PERMISSIONS: 3001,
    INVALID_ROLE: 3002,
    RESOURCE_ACCESS_DENIED: 3003,
    QUOTA_EXCEEDED: 3004,
    RATE_LIMITED: 3005,
    LICENSE_EXPIRED: 3006,
    SUBSCRIPTION_REQUIRED: 3007,
    FEATURE_DISABLED: 3008,
    IP_BLOCKED: 3009,
  },

  // Network Errors (4xxx)
  NETWORK: {
    REQUEST_FAILED: 4000,
    TIMEOUT: 4001,
    CONNECTION_LOST: 4002,
    INVALID_RESPONSE: 4003,
    DNS_ERROR: 4004,
    SSL_ERROR: 4005,
    CORS_ERROR: 4006,
    OFFLINE: 4007,
    SOCKET_ERROR: 4008,
    TOO_MANY_REDIRECTS: 4009,
  },

  // Server Errors (5xxx)
  SERVER: {
    INTERNAL_ERROR: 5000,
    SERVICE_UNAVAILABLE: 5001,
    DATABASE_ERROR: 5002,
    CACHE_ERROR: 5003,
    QUEUE_ERROR: 5004,
    JOB_FAILED: 5005,
    CONFIGURATION_ERROR: 5006,
    DEPENDENCY_ERROR: 5007,
    RESOURCE_EXHAUSTED: 5008,
    MAINTENANCE_MODE: 5009,
  },

  // Client Errors (6xxx)
  CLIENT: {
    INVALID_STATE: 6000,
    UNSUPPORTED_OPERATION: 6001,
    INVALID_CONFIGURATION: 6002,
    RESOURCE_NOT_FOUND: 6003,
    DUPLICATE_REQUEST: 6004,
    INVALID_OPERATION: 6005,
    ABORTED_OPERATION: 6006,
    UNSUPPORTED_BROWSER: 6007,
    STORAGE_ERROR: 6008,
    RENDER_ERROR: 6009,
  },

  // Business Logic Errors (7xxx)
  BUSINESS: {
    INVALID_WORKFLOW: 7000,
    INVALID_TRANSITION: 7001,
    BUSINESS_RULE_VIOLATION: 7002,
    DEPENDENCY_CONFLICT: 7003,
    INVALID_STATUS: 7004,
    OPERATION_NOT_ALLOWED: 7005,
    RESOURCE_LOCKED: 7006,
    QUOTA_EXCEEDED: 7007,
    DUPLICATE_ENTITY: 7008,
    INVALID_REFERENCE: 7009,
  },

  // External Service Errors (8xxx)
  EXTERNAL: {
    SERVICE_ERROR: 8000,
    INTEGRATION_ERROR: 8001,
    API_ERROR: 8002,
    GATEWAY_ERROR: 8003,
    PROVIDER_ERROR: 8004,
    WEBHOOK_ERROR: 8005,
    THIRD_PARTY_ERROR: 8006,
    PAYMENT_ERROR: 8007,
    NOTIFICATION_ERROR: 8008,
    EXTERNAL_DEPENDENCY_ERROR: 8009,
  },
} as const;

/**
 * Error Messages
 */
export const ERROR_MESSAGES = {
  // Validation Error Messages
  VALIDATION: {
    [ERROR_CODES.VALIDATION.INVALID_INPUT]: 'Invalid input provided',
    [ERROR_CODES.VALIDATION.REQUIRED_FIELD]: 'Required field missing',
    [ERROR_CODES.VALIDATION.INVALID_FORMAT]: 'Invalid format',
    [ERROR_CODES.VALIDATION.INVALID_TYPE]: 'Invalid type',
    [ERROR_CODES.VALIDATION.OUT_OF_RANGE]: 'Value out of allowed range',
    [ERROR_CODES.VALIDATION.TOO_SHORT]: 'Value too short',
    [ERROR_CODES.VALIDATION.TOO_LONG]: 'Value too long',
    [ERROR_CODES.VALIDATION.DUPLICATE_VALUE]: 'Duplicate value not allowed',
    [ERROR_CODES.VALIDATION.INVALID_ENUM]: 'Invalid enum value',
    [ERROR_CODES.VALIDATION.INVALID_DATE]: 'Invalid date',
  },

  // Authentication Error Messages
  AUTH: {
    [ERROR_CODES.AUTH.UNAUTHORIZED]: 'Authentication required',
    [ERROR_CODES.AUTH.INVALID_CREDENTIALS]: 'Invalid credentials',
    [ERROR_CODES.AUTH.EXPIRED_TOKEN]: 'Authentication token expired',
    [ERROR_CODES.AUTH.INVALID_TOKEN]: 'Invalid authentication token',
    [ERROR_CODES.AUTH.ACCOUNT_LOCKED]: 'Account locked',
    [ERROR_CODES.AUTH.ACCOUNT_DISABLED]: 'Account disabled',
    [ERROR_CODES.AUTH.INVALID_REFRESH_TOKEN]: 'Invalid refresh token',
    [ERROR_CODES.AUTH.SESSION_EXPIRED]: 'Session expired',
    [ERROR_CODES.AUTH.INVALID_MFA_CODE]: 'Invalid MFA code',
    [ERROR_CODES.AUTH.MFA_REQUIRED]: 'MFA verification required',
  },

  // Authorization Error Messages
  PERMISSION: {
    [ERROR_CODES.PERMISSION.FORBIDDEN]: 'Access forbidden',
    [ERROR_CODES.PERMISSION.INSUFFICIENT_PERMISSIONS]:
      'Insufficient permissions',
    [ERROR_CODES.PERMISSION.INVALID_ROLE]: 'Invalid role',
    [ERROR_CODES.PERMISSION.RESOURCE_ACCESS_DENIED]: 'Resource access denied',
    [ERROR_CODES.PERMISSION.QUOTA_EXCEEDED]: 'Quota exceeded',
    [ERROR_CODES.PERMISSION.RATE_LIMITED]: 'Rate limit exceeded',
    [ERROR_CODES.PERMISSION.LICENSE_EXPIRED]: 'License expired',
    [ERROR_CODES.PERMISSION.SUBSCRIPTION_REQUIRED]: 'Subscription required',
    [ERROR_CODES.PERMISSION.FEATURE_DISABLED]: 'Feature disabled',
    [ERROR_CODES.PERMISSION.IP_BLOCKED]: 'IP address blocked',
  },

  // Network Error Messages
  NETWORK: {
    [ERROR_CODES.NETWORK.REQUEST_FAILED]: 'Network request failed',
    [ERROR_CODES.NETWORK.TIMEOUT]: 'Network request timeout',
    [ERROR_CODES.NETWORK.CONNECTION_LOST]: 'Connection lost',
    [ERROR_CODES.NETWORK.INVALID_RESPONSE]: 'Invalid server response',
    [ERROR_CODES.NETWORK.DNS_ERROR]: 'DNS resolution failed',
    [ERROR_CODES.NETWORK.SSL_ERROR]: 'SSL/TLS error',
    [ERROR_CODES.NETWORK.CORS_ERROR]: 'CORS policy violation',
    [ERROR_CODES.NETWORK.OFFLINE]: 'No internet connection',
    [ERROR_CODES.NETWORK.SOCKET_ERROR]: 'WebSocket error',
    [ERROR_CODES.NETWORK.TOO_MANY_REDIRECTS]: 'Too many redirects',
  },

  // Server Error Messages
  SERVER: {
    [ERROR_CODES.SERVER.INTERNAL_ERROR]: 'Internal server error',
    [ERROR_CODES.SERVER.SERVICE_UNAVAILABLE]: 'Service unavailable',
    [ERROR_CODES.SERVER.DATABASE_ERROR]: 'Database error',
    [ERROR_CODES.SERVER.CACHE_ERROR]: 'Cache error',
    [ERROR_CODES.SERVER.QUEUE_ERROR]: 'Queue processing error',
    [ERROR_CODES.SERVER.JOB_FAILED]: 'Background job failed',
    [ERROR_CODES.SERVER.CONFIGURATION_ERROR]: 'Server configuration error',
    [ERROR_CODES.SERVER.DEPENDENCY_ERROR]: 'Server dependency error',
    [ERROR_CODES.SERVER.RESOURCE_EXHAUSTED]: 'Server resources exhausted',
    [ERROR_CODES.SERVER.MAINTENANCE_MODE]: 'Server in maintenance mode',
  },

  // Client Error Messages
  CLIENT: {
    [ERROR_CODES.CLIENT.INVALID_STATE]: 'Invalid client state',
    [ERROR_CODES.CLIENT.UNSUPPORTED_OPERATION]: 'Operation not supported',
    [ERROR_CODES.CLIENT.INVALID_CONFIGURATION]: 'Invalid client configuration',
    [ERROR_CODES.CLIENT.RESOURCE_NOT_FOUND]: 'Resource not found',
    [ERROR_CODES.CLIENT.DUPLICATE_REQUEST]: 'Duplicate request',
    [ERROR_CODES.CLIENT.INVALID_OPERATION]: 'Invalid operation',
    [ERROR_CODES.CLIENT.ABORTED_OPERATION]: 'Operation aborted',
    [ERROR_CODES.CLIENT.UNSUPPORTED_BROWSER]: 'Browser not supported',
    [ERROR_CODES.CLIENT.STORAGE_ERROR]: 'Local storage error',
    [ERROR_CODES.CLIENT.RENDER_ERROR]: 'Rendering error',
  },

  // Business Logic Error Messages
  BUSINESS: {
    [ERROR_CODES.BUSINESS.INVALID_WORKFLOW]: 'Invalid workflow state',
    [ERROR_CODES.BUSINESS.INVALID_TRANSITION]: 'Invalid state transition',
    [ERROR_CODES.BUSINESS.BUSINESS_RULE_VIOLATION]: 'Business rule violation',
    [ERROR_CODES.BUSINESS.DEPENDENCY_CONFLICT]: 'Dependency conflict',
    [ERROR_CODES.BUSINESS.INVALID_STATUS]: 'Invalid status',
    [ERROR_CODES.BUSINESS.OPERATION_NOT_ALLOWED]: 'Operation not allowed',
    [ERROR_CODES.BUSINESS.RESOURCE_LOCKED]: 'Resource locked',
    [ERROR_CODES.BUSINESS.QUOTA_EXCEEDED]: 'Business quota exceeded',
    [ERROR_CODES.BUSINESS.DUPLICATE_ENTITY]: 'Duplicate entity',
    [ERROR_CODES.BUSINESS.INVALID_REFERENCE]: 'Invalid reference',
  },

  // External Service Error Messages
  EXTERNAL: {
    [ERROR_CODES.EXTERNAL.SERVICE_ERROR]: 'External service error',
    [ERROR_CODES.EXTERNAL.INTEGRATION_ERROR]: 'Integration error',
    [ERROR_CODES.EXTERNAL.API_ERROR]: 'External API error',
    [ERROR_CODES.EXTERNAL.GATEWAY_ERROR]: 'Gateway error',
    [ERROR_CODES.EXTERNAL.PROVIDER_ERROR]: 'Provider error',
    [ERROR_CODES.EXTERNAL.WEBHOOK_ERROR]: 'Webhook error',
    [ERROR_CODES.EXTERNAL.THIRD_PARTY_ERROR]: 'Third-party service error',
    [ERROR_CODES.EXTERNAL.PAYMENT_ERROR]: 'Payment processing error',
    [ERROR_CODES.EXTERNAL.NOTIFICATION_ERROR]: 'Notification delivery error',
    [ERROR_CODES.EXTERNAL.EXTERNAL_DEPENDENCY_ERROR]:
      'External dependency error',
  },
} as const;

/**
 * Error Severities
 */
export const ERROR_SEVERITIES = {
  /** Fatal errors that require immediate attention */
  FATAL: 'fatal',

  /** Critical errors that should be addressed soon */
  CRITICAL: 'critical',

  /** Errors that affect functionality but aren't critical */
  ERROR: 'error',

  /** Warning conditions */
  WARNING: 'warning',

  /** Informational messages about errors */
  INFO: 'info',

  /** Debug-level error information */
  DEBUG: 'debug',
} as const;

/**
 * Error Recovery Actions
 */
export const ERROR_RECOVERY_ACTIONS = {
  /** Retry the failed operation */
  RETRY: 'retry',

  /** Refresh the page */
  REFRESH: 'refresh',

  /** Clear local data and retry */
  CLEAR_AND_RETRY: 'clear_and_retry',

  /** Log out and redirect to login */
  LOGOUT: 'logout',

  /** Contact support */
  CONTACT_SUPPORT: 'contact_support',

  /** No recovery action available */
  NONE: 'none',
} as const;
