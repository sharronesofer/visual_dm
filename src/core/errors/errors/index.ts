import {
  BaseError,
  ApiError,
  ValidationError,
  AuthError,
  NetworkError,
  DatabaseError,
  CacheError,
  BusinessError,
  ConfigError,
  IntegrationError,
  RateLimitError,
  FileSystemError,
  TimeoutError,
  DependencyError,
  StateError,
} from '../types/errors';

/**
 * Base application error class
 */
export class ApplicationError extends Error implements BaseError {
  code: string;
  details?: Record<string, any>;

  constructor(code: string, message: string, details?: Record<string, any>) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.details = details;
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON() {
    return {
      code: this.code,
      message: this.message,
      details: this.details,
      stack: this.stack,
    };
  }
}

/**
 * API error class
 */
export class ApiErrorImpl extends ApplicationError implements ApiError {
  status: number;
  path?: string;
  timestamp: string;

  constructor(
    code: string,
    message: string,
    status: number,
    path?: string,
    details?: Record<string, any>
  ) {
    super(code, message, details);
    this.status = status;
    this.path = path;
    this.timestamp = new Date().toISOString();
  }
}

/**
 * Validation error class
 */
export class ValidationErrorImpl
  extends ApplicationError
  implements ValidationError
{
  field: string;
  value?: any;
  constraints?: Record<string, string>;

  constructor(
    field: string,
    message: string,
    value?: any,
    constraints?: Record<string, string>
  ) {
    super('VALIDATION_ERROR', message, { field, value, constraints });
    this.field = field;
    this.value = value;
    this.constraints = constraints;
  }
}

/**
 * Authentication error class
 */
export class AuthErrorImpl extends ApplicationError implements AuthError {
  userId?: string;
  requiredRoles?: string[];
  requiredPermissions?: string[];

  constructor(
    message: string,
    userId?: string,
    requiredRoles?: string[],
    requiredPermissions?: string[]
  ) {
    super('AUTH_ERROR', message, {
      userId,
      requiredRoles,
      requiredPermissions,
    });
    this.userId = userId;
    this.requiredRoles = requiredRoles;
    this.requiredPermissions = requiredPermissions;
  }
}

/**
 * Network error class
 */
export class NetworkErrorImpl extends ApplicationError implements NetworkError {
  url?: string;
  method?: string;
  retryCount?: number;

  constructor(
    message: string,
    url?: string,
    method?: string,
    retryCount?: number
  ) {
    super('NETWORK_ERROR', message, { url, method, retryCount });
    this.url = url;
    this.method = method;
    this.retryCount = retryCount;
  }
}

/**
 * Database error class
 */
export class DatabaseErrorImpl
  extends ApplicationError
  implements DatabaseError
{
  query?: string;
  params?: any[];
  table?: string;

  constructor(message: string, query?: string, params?: any[], table?: string) {
    super('DATABASE_ERROR', message, { query, params, table });
    this.query = query;
    this.params = params;
    this.table = table;
  }
}

/**
 * Cache error class
 */
export class CacheErrorImpl extends ApplicationError implements CacheError {
  key?: string;
  operation?: 'get' | 'set' | 'delete' | 'clear';
  ttl?: number;

  constructor(
    message: string,
    key?: string,
    operation?: 'get' | 'set' | 'delete' | 'clear',
    ttl?: number
  ) {
    super('CACHE_ERROR', message, { key, operation, ttl });
    this.key = key;
    this.operation = operation;
    this.ttl = ttl;
  }
}

/**
 * Business logic error class
 */
export class BusinessErrorImpl
  extends ApplicationError
  implements BusinessError
{
  entityId?: string;
  entityType?: string;
  operation?: string;

  constructor(
    message: string,
    entityId?: string,
    entityType?: string,
    operation?: string
  ) {
    super('BUSINESS_ERROR', message, { entityId, entityType, operation });
    this.entityId = entityId;
    this.entityType = entityType;
    this.operation = operation;
  }
}

/**
 * Configuration error class
 */
export class ConfigErrorImpl extends ApplicationError implements ConfigError {
  configKey?: string;
  expectedType?: string;
  actualValue?: any;

  constructor(
    message: string,
    configKey?: string,
    expectedType?: string,
    actualValue?: any
  ) {
    super('CONFIG_ERROR', message, { configKey, expectedType, actualValue });
    this.configKey = configKey;
    this.expectedType = expectedType;
    this.actualValue = actualValue;
  }
}

/**
 * Integration error class
 */
export class IntegrationErrorImpl
  extends ApplicationError
  implements IntegrationError
{
  service?: string;
  endpoint?: string;
  responseData?: any;

  constructor(
    message: string,
    service?: string,
    endpoint?: string,
    responseData?: any
  ) {
    super('INTEGRATION_ERROR', message, { service, endpoint, responseData });
    this.service = service;
    this.endpoint = endpoint;
    this.responseData = responseData;
  }
}

/**
 * Rate limit error class
 */
export class RateLimitErrorImpl
  extends ApplicationError
  implements RateLimitError
{
  limit?: number;
  remaining?: number;
  resetTime?: string;

  constructor(
    message: string,
    limit?: number,
    remaining?: number,
    resetTime?: string
  ) {
    super('RATE_LIMIT_ERROR', message, { limit, remaining, resetTime });
    this.limit = limit;
    this.remaining = remaining;
    this.resetTime = resetTime;
  }
}

/**
 * File system error class
 */
export class FileSystemErrorImpl
  extends ApplicationError
  implements FileSystemError
{
  path?: string;
  operation?: 'read' | 'write' | 'delete' | 'move';
  permissions?: string;

  constructor(
    message: string,
    path?: string,
    operation?: 'read' | 'write' | 'delete' | 'move',
    permissions?: string
  ) {
    super('FILE_SYSTEM_ERROR', message, { path, operation, permissions });
    this.path = path;
    this.operation = operation;
    this.permissions = permissions;
  }
}

/**
 * Timeout error class
 */
export class TimeoutErrorImpl extends ApplicationError implements TimeoutError {
  timeout?: number;
  operation?: string;
  elapsedTime?: number;

  constructor(
    message: string,
    timeout?: number,
    operation?: string,
    elapsedTime?: number
  ) {
    super('TIMEOUT_ERROR', message, { timeout, operation, elapsedTime });
    this.timeout = timeout;
    this.operation = operation;
    this.elapsedTime = elapsedTime;
  }
}

/**
 * Dependency error class
 */
export class DependencyErrorImpl
  extends ApplicationError
  implements DependencyError
{
  dependencyName?: string;
  requiredVersion?: string;
  installedVersion?: string;

  constructor(
    message: string,
    dependencyName?: string,
    requiredVersion?: string,
    installedVersion?: string
  ) {
    super('DEPENDENCY_ERROR', message, {
      dependencyName,
      requiredVersion,
      installedVersion,
    });
    this.dependencyName = dependencyName;
    this.requiredVersion = requiredVersion;
    this.installedVersion = installedVersion;
  }
}

/**
 * State error class
 */
export class StateErrorImpl extends ApplicationError implements StateError {
  currentState?: string;
  expectedState?: string;
  allowedTransitions?: string[];

  constructor(
    message: string,
    currentState?: string,
    expectedState?: string,
    allowedTransitions?: string[]
  ) {
    super('STATE_ERROR', message, {
      currentState,
      expectedState,
      allowedTransitions,
    });
    this.currentState = currentState;
    this.expectedState = expectedState;
    this.allowedTransitions = allowedTransitions;
  }
}
