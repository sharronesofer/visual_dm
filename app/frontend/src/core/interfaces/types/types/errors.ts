import { AxiosError } from 'axios';

/**
 * Base error interface
 */
export interface BaseError {
  code: string;
  message: string;
  details?: Record<string, any>;
  stack?: string;
}

/**
 * API error interface
 */
export interface ApiError extends BaseError {
  status: number;
  path?: string;
  timestamp?: string;
}

/**
 * Validation error interface
 */
export interface ValidationError extends BaseError {
  field: string;
  value?: any;
  constraints?: Record<string, string>;
}

/**
 * Authentication error interface
 */
export interface AuthError extends BaseError {
  userId?: string;
  requiredRoles?: string[];
  requiredPermissions?: string[];
}

/**
 * Network error interface
 */
export interface NetworkError extends BaseError {
  url?: string;
  method?: string;
  retryCount?: number;
}

/**
 * Database error interface
 */
export interface DatabaseError extends BaseError {
  query?: string;
  params?: any[];
  table?: string;
}

/**
 * Cache error interface
 */
export interface CacheError extends BaseError {
  key?: string;
  operation?: 'get' | 'set' | 'delete' | 'clear';
  ttl?: number;
}

/**
 * Business logic error interface
 */
export interface BusinessError extends BaseError {
  entityId?: string;
  entityType?: string;
  operation?: string;
}

/**
 * Configuration error interface
 */
export interface ConfigError extends BaseError {
  configKey?: string;
  expectedType?: string;
  actualValue?: any;
}

/**
 * Integration error interface
 */
export interface IntegrationError extends BaseError {
  service?: string;
  endpoint?: string;
  responseData?: any;
}

/**
 * Rate limit error interface
 */
export interface RateLimitError extends BaseError {
  limit?: number;
  remaining?: number;
  resetTime?: string;
}

/**
 * File system error interface
 */
export interface FileSystemError extends BaseError {
  path?: string;
  operation?: 'read' | 'write' | 'delete' | 'move';
  permissions?: string;
}

/**
 * Timeout error interface
 */
export interface TimeoutError extends BaseError {
  timeout?: number;
  operation?: string;
  elapsedTime?: number;
}

/**
 * Dependency error interface
 */
export interface DependencyError extends BaseError {
  dependencyName?: string;
  requiredVersion?: string;
  installedVersion?: string;
}

/**
 * State error interface
 */
export interface StateError extends BaseError {
  currentState?: string;
  expectedState?: string;
  allowedTransitions?: string[];
}

/**
 * Base error class for all API errors
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Error class for network-related errors
 */
export class NetworkError extends Error {
  constructor(
    message: string,
    public originalError?: Error | AxiosError
  ) {
    super(message);
    this.name = 'NetworkError';
  }
}

/**
 * Error class for validation errors
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    public errors: Record<string, string[]>
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Error class for authentication errors
 */
export class AuthError extends ApiError {
  constructor(message: string = 'Authentication failed') {
    super(message, 401);
    this.name = 'AuthError';
  }
}

/**
 * Error class for authorization errors
 */
export class ForbiddenError extends ApiError {
  constructor(message: string = 'Access forbidden') {
    super(message, 403);
    this.name = 'ForbiddenError';
  }
}

/**
 * Error class for not found errors
 */
export class NotFoundError extends ApiError {
  constructor(message: string = 'Resource not found') {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

/**
 * Error class for rate limit errors
 */
export class RateLimitError extends ApiError {
  constructor(
    message: string = 'Rate limit exceeded',
    public retryAfter?: number
  ) {
    super(message, 429);
    this.name = 'RateLimitError';
  }
}

/**
 * Error class for server errors
 */
export class ServerError extends ApiError {
  constructor(message: string = 'Internal server error') {
    super(message, 500);
    this.name = 'ServerError';
  }
}

/**
 * Error class for timeout errors
 */
export class TimeoutError extends NetworkError {
  constructor(message: string = 'Request timed out') {
    super(message);
    this.name = 'TimeoutError';
  }
}

/**
 * Error class for offline errors
 */
export class OfflineError extends NetworkError {
  constructor(message: string = 'No internet connection') {
    super(message);
    this.name = 'OfflineError';
  }
}
