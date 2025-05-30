from typing import Any, Dict


/**
 * Error Constants
 * @description Defines error codes, messages, and categories used throughout the application.
 */
/**
 * Error Categories
 */
const ERROR_CATEGORIES = {
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
} as const
/**
 * Error Codes
 */
const ERROR_CODES = {
  VALIDATION: Dict[str, Any],
  AUTH: Dict[str, Any],
  PERMISSION: Dict[str, Any],
  NETWORK: Dict[str, Any],
  SERVER: Dict[str, Any],
  CLIENT: Dict[str, Any],
  BUSINESS: Dict[str, Any],
  EXTERNAL: Dict[str, Any],
} as const
/**
 * Error Messages
 */
const ERROR_MESSAGES = {
  VALIDATION: Dict[str, Any],
  AUTH: Dict[str, Any],
  PERMISSION: Dict[str, Any],
  NETWORK: Dict[str, Any],
  SERVER: Dict[str, Any],
  CLIENT: Dict[str, Any],
  BUSINESS: Dict[str, Any],
  EXTERNAL: Dict[str, Any],
} as const
/**
 * Error Severities
 */
const ERROR_SEVERITIES = {
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
} as const
/**
 * Error Recovery Actions
 */
const ERROR_RECOVERY_ACTIONS = {
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
} as const