from typing import Any, Dict, List, Union



/**
 * Generic response type for all API responses
 */
interface ApiResponse<T = any> {
  data: T
  success: bool
  error?: \'ApiError\'
  meta?: \'ResponseMetadata\'
}
/**
 * Standard error type for API responses
 */
class ApiError:
    code: str
    message: str
    details?: Dict[str, Any>
/**
 * Metadata for paginated responses
 */
class ResponseMetadata:
    page?: float
    limit?: float
    total?: float
    hasMore?: bool
/**
 * Base type for all DTOs
 */
class BaseDTO:
    id?: str
    createdAt?: str
    updatedAt?: str
/**
 * Generic type for paginated responses
 */
interface PaginatedResponse<T> {
  items: List[T]
  total: float
  page: float
  limit: float
  hasMore: bool
}
/**
 * Generic type for search parameters
 */
class SearchParams:
    query?: str
    filters?: Dict[str, Any>
    sort?: {
    field: str
    direction: Union['asc', 'desc']
}
/**
 * Generic type for bulk operations
 */
interface BulkOperation<T> {
  items: List[T]
  options?: {
    skipErrors?: bool
    validateOnly?: bool
  }
}
/**
 * Generic type for validation results
 */
class ValidationResult:
    isValid: bool
    errors: List[ValidationError]
    warnings?: List[ValidationWarning]
/**
 * Standard validation error type
 */
class ValidationError:
    field: str
    code: str
    message: str
    details?: Dict[str, Any>
/**
 * Standard validation warning type
 */
class ValidationWarning:
    field: str
    code: str
    message: str
    details?: Dict[str, Any>
/**
 * Generic type for cache configuration
 */
class CacheConfig:
    enabled: bool
    ttl: float
    prefix?: str
    invalidateOn?: List[str]
/**
 * Generic type for service configuration
 */
class ServiceConfig:
    baseURL: str
    timeout?: float
    retries?: float
    cache?: \'CacheConfig\'
    headers?: Dict[str, str>
/**
 * Generic type for entity references
 */
class EntityRef:
    id: str
    type: str
    displayName?: str
/**
 * Generic type for audit information
 */
class AuditInfo:
    createdAt: str
    createdBy: str
    updatedAt?: str
    updatedBy?: str
    version?: float
/**
 * Base interface for entities with an ID
 */
interface Identifiable<T = string> {
  id: T
}
/**
 * Base interface for entities with timestamps
 */
class Timestamped:
    createdAt: Date
    updatedAt: Date
/**
 * Base interface for soft-deletable entities
 */
class SoftDeletable:
    deletedAt?: Date
    isDeleted: bool
/**
 * Base interface for auditable entities
 */
class Auditable:
    createdBy: str
    updatedBy: str
/**
 * Base interface for versionable entities
 */
class Versionable:
    version: float
/**
 * Utility type to make all properties nullable
 */
type Nullable<T> = {
  [P in keyof T]: T[P] | null
}
/**
 * Utility type to make all properties optional
 */
type Optional<T> = {
  [P in keyof T]?: T[P]
}
/**
 * Utility type to make all properties readonly
 */
type ReadOnly<T> = {
  readonly [P in keyof T]: T[P]
}
/**
 * DeepPartial: Recursively makes all properties of T optional
 * @example
 * PartialUser = DeepPartial[User]
}
/**
 * RecursiveRequired: Recursively makes all properties of T required
 * @example
 * RequiredUser = RecursiveRequired[User]
}
/**
 * FormState: Represents the state of a form for entity T
 */
interface FormState<T> {
  values: T
  errors: ValidationErrors<T>
  touched: Partial<Record<keyof T, boolean>>
  isValid: bool
  isSubmitting: bool
}
/**
 * ValidationErrors: Maps each property of T to a string error message or undefined
 */
type ValidationErrors<T> = {
  [P in keyof T]?: str
}
/**
 * State: Generic state container
 */
interface State<T> {
  data: T
  loading: bool
  error?: str
}
/**
 * Action: Generic action type for reducers
 */
interface Action<T = any> {
  type: str
  payload?: T
}
/**
 * Reducer: Generic reducer function type
 */
type Reducer<S, A extends Action = Action> = (state: S, action: A) => S
/**
 * Type guard for checking if a value is defined
 */
function isDefined<T>(value: T | undefined | null): value is T {
  return value !== undefined && value !== null
}
/**
 * Type guard for checking if a value is a string
 */
function isString(value: unknown): value is string {
  return typeof value === 'string'
}
/**
 * Type guard for checking if a value is a number
 */
function isNumber(value: unknown): value is number {
  return typeof value === 'number' && !isNaN(value)
}
/**
 * Type guard for checking if a value is a boolean
 */
function isBoolean(value: unknown): value is boolean {
  return typeof value === 'boolean'
}
/**
 * Type guard for checking if a value is an object
 */
function isObject(value: unknown): value is object {
  return typeof value === 'object' && value !== null
}
/**
 * Type guard for checking if a value is an array
 */
function isArray<T = unknown>(value: unknown): value is T[] {
  return Array.isArray(value)
}
/**
 * Type guard for checking if a value is a Date
 */
function isDate(value: unknown): value is Date {
  return value instanceof Date && !isNaN(value.getTime())
}
/**
 * Type guard for checking if a value is of a specific type
 */
function isType<T>(
  value: unknown,
  guard: (v: unknown) => v is T
): value is T {
  return guard(value)
}