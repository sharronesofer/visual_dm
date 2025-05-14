/**
 * Generic response type for all API responses
 */
export interface ApiResponse<T = any> {
  data: T;
  success: boolean;
  error?: ApiError;
  meta?: ResponseMetadata;
}

/**
 * Standard error type for API responses
 */
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * Metadata for paginated responses
 */
export interface ResponseMetadata {
  page?: number;
  limit?: number;
  total?: number;
  hasMore?: boolean;
}

/**
 * Base type for all DTOs
 */
export interface BaseDTO {
  id?: string;
  createdAt?: string;
  updatedAt?: string;
}

/**
 * Generic type for paginated responses
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

/**
 * Generic type for search parameters
 */
export interface SearchParams {
  query?: string;
  filters?: Record<string, any>;
  sort?: {
    field: string;
    direction: 'asc' | 'desc';
  };
}

/**
 * Generic type for bulk operations
 */
export interface BulkOperation<T> {
  items: T[];
  options?: {
    skipErrors?: boolean;
    validateOnly?: boolean;
  };
}

/**
 * Generic type for validation results
 */
export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings?: ValidationWarning[];
}

/**
 * Standard validation error type
 */
export interface ValidationError {
  field: string;
  code: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * Standard validation warning type
 */
export interface ValidationWarning {
  field: string;
  code: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * Generic type for cache configuration
 */
export interface CacheConfig {
  enabled: boolean;
  ttl: number;
  prefix?: string;
  invalidateOn?: string[];
}

/**
 * Generic type for service configuration
 */
export interface ServiceConfig {
  baseURL: string;
  timeout?: number;
  retries?: number;
  cache?: CacheConfig;
  headers?: Record<string, string>;
}

/**
 * Generic type for entity references
 */
export interface EntityRef {
  id: string;
  type: string;
  displayName?: string;
}

/**
 * Generic type for audit information
 */
export interface AuditInfo {
  createdAt: string;
  createdBy: string;
  updatedAt?: string;
  updatedBy?: string;
  version?: number;
}

/**
 * Base interface for entities with an ID
 */
export interface Identifiable<T = string> {
  id: T;
}

/**
 * Base interface for entities with timestamps
 */
export interface Timestamped {
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Base interface for soft-deletable entities
 */
export interface SoftDeletable {
  deletedAt?: Date;
  isDeleted: boolean;
}

/**
 * Base interface for auditable entities
 */
export interface Auditable {
  createdBy: string;
  updatedBy: string;
}

/**
 * Base interface for versionable entities
 */
export interface Versionable {
  version: number;
}

/**
 * Utility type to make all properties nullable
 */
export type Nullable<T> = {
  [P in keyof T]: T[P] | null;
};

/**
 * Utility type to make all properties optional
 */
export type Optional<T> = {
  [P in keyof T]?: T[P];
};

/**
 * Utility type to make all properties readonly
 */
export type ReadOnly<T> = {
  readonly [P in keyof T]: T[P];
};

/**
 * DeepPartial: Recursively makes all properties of T optional
 * @example
 * type PartialUser = DeepPartial<User>
 */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * RecursiveRequired: Recursively makes all properties of T required
 * @example
 * type RequiredUser = RecursiveRequired<User>
 */
export type RecursiveRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? RecursiveRequired<T[P]> : T[P];
};

/**
 * FormState: Represents the state of a form for entity T
 */
export interface FormState<T> {
  values: T;
  errors: ValidationErrors<T>;
  touched: Partial<Record<keyof T, boolean>>;
  isValid: boolean;
  isSubmitting: boolean;
}

/**
 * ValidationErrors: Maps each property of T to a string error message or undefined
 */
export type ValidationErrors<T> = {
  [P in keyof T]?: string;
};

/**
 * State: Generic state container
 */
export interface State<T> {
  data: T;
  loading: boolean;
  error?: string;
}

/**
 * Action: Generic action type for reducers
 */
export interface Action<T = any> {
  type: string;
  payload?: T;
}

/**
 * Reducer: Generic reducer function type
 */
export type Reducer<S, A extends Action = Action> = (state: S, action: A) => S;

/**
 * Type guard for checking if a value is defined
 */
export function isDefined<T>(value: T | undefined | null): value is T {
  return value !== undefined && value !== null;
}

/**
 * Type guard for checking if a value is a string
 */
export function isString(value: unknown): value is string {
  return typeof value === 'string';
}

/**
 * Type guard for checking if a value is a number
 */
export function isNumber(value: unknown): value is number {
  return typeof value === 'number' && !isNaN(value);
}

/**
 * Type guard for checking if a value is a boolean
 */
export function isBoolean(value: unknown): value is boolean {
  return typeof value === 'boolean';
}

/**
 * Type guard for checking if a value is an object
 */
export function isObject(value: unknown): value is object {
  return typeof value === 'object' && value !== null;
}

/**
 * Type guard for checking if a value is an array
 */
export function isArray<T = unknown>(value: unknown): value is T[] {
  return Array.isArray(value);
}

/**
 * Type guard for checking if a value is a Date
 */
export function isDate(value: unknown): value is Date {
  return value instanceof Date && !isNaN(value.getTime());
}

/**
 * Type guard for checking if a value is of a specific type
 */
export function isType<T>(
  value: unknown,
  guard: (v: unknown) => v is T
): value is T {
  return guard(value);
}
