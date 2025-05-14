/**
 * Common type definitions and utility types used across the application.
 * @module types/common
 */

/**
 * Represents a unique identifier string
 */
export type ID = string;

/**
 * Represents a Unix timestamp in milliseconds
 */
export type Timestamp = number;

/**
 * Represents a UUID string
 */
export type UUID = string;

/**
 * Makes all properties in T nullable (T | null)
 */
export type Nullable<T> = { [P in keyof T]: T[P] | null };

/**
 * Makes all properties in T optional
 */
export type Optional<T> = { [P in keyof T]?: T[P] };

/**
 * Makes all properties in T readonly
 */
export type ReadOnly<T> = { readonly [P in keyof T]: T[P] };

/**
 * Base interface for all entities with common fields
 */
export interface BaseEntity {
  id: ID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

/**
 * Standard pagination parameters
 */
export interface PaginationParams {
  page: number;
  limit: number;
}

/**
 * Standard pagination metadata
 */
export interface PaginationMeta {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

/**
 * Generic paginated response
 */
export interface PaginatedResponse<T> {
  items: T[];
  meta: PaginationMeta;
}

/**
 * Sort order options
 */
export type SortOrder = 'asc' | 'desc';

/**
 * Sort parameters for queries
 */
export interface SortParams {
  field: string;
  order: SortOrder;
}

/**
 * Generic filter operator types
 */
export type FilterOperator =
  | 'eq' // equals
  | 'neq' // not equals
  | 'gt' // greater than
  | 'gte' // greater than or equal
  | 'lt' // less than
  | 'lte' // less than or equal
  | 'in' // in array
  | 'nin' // not in array
  | 'like' // string contains
  | 'nlike'; // string does not contain;

/**
 * Generic filter condition
 */
export interface FilterCondition<T = any> {
  field: keyof T;
  operator: FilterOperator;
  value: any;
}

/**
 * Generic query parameters including pagination, sorting, and filtering
 */
export interface QueryParams<T = any> {
  pagination?: PaginationParams;
  sort?: SortParams[];
  filters?: FilterCondition<T>[];
}

/**
 * Generic success response
 */
export interface SuccessResponse<T> {
  data: T;
  message?: string;
}

/**
 * Generic error response
 */
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

/**
 * Generic async operation status
 */
export type AsyncStatus = 'idle' | 'loading' | 'succeeded' | 'failed';

/**
 * Generic async state with data, error, and status
 */
export interface AsyncState<T, E = Error> {
  data: T | null;
  error: E | null;
  status: AsyncStatus;
}

/**
 * Deep partial type for nested objects
 */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * Record validation status
 */
export type ValidationStatus = 'valid' | 'invalid' | 'pending';

/**
 * Generic validation result
 */
export interface ValidationResult {
  isValid: boolean;
  errors?: Record<string, string[]>;
}

/**
 * Generic cache options
 */
export interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  key?: string; // Custom cache key
  group?: string; // Cache group for bulk operations
}

/**
 * Generic event handler type
 */
export type EventHandler<T = unknown> = (event: T) => void | Promise<void>;

/**
 * Generic subscription handler
 */
export interface Subscription {
  unsubscribe: () => void;
}

/**
 * Generic retry options
 */
export interface RetryOptions {
  maxAttempts: number;
  delay: number;
  backoffFactor?: number;
}

/** Basic position interface */
export interface Position {
  x: number;
  y: number;
}

/** Common viewport interface */
export interface Viewport {
  x: number;
  y: number;
  width: number;
  height: number;
  zoom: number;
}

/** Direction types */
export type Direction = 'north' | 'south' | 'east' | 'west';
export type BorderType = 'normal' | 'difficult' | 'impassable' | 'bridge' | 'gate';

/** Border interface */
export interface Border {
  type: BorderType;
  direction: Direction;
  position: Position;
}

/** Validation related types */
export interface ValidationError {
  field: string;
  message: string;
  type: 'error' | 'warning';
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

/** Asset types */
export interface Asset {
  id: string;
  type: string;
  url: string;
  metadata?: Record<string, unknown>;
}

/** Common state types */
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

/** Common event types */
export interface InteractionEvent {
  type: string;
  target: string;
  data?: Record<string, unknown>;
  timestamp: number;
}

/** Common configuration types */
export interface Config {
  apiUrl: string;
  assetsPath: string;
  debug: boolean;
  features: Record<string, boolean>;
}

export interface Size {
  width: number;
  height: number;
}

export interface Dimensions extends Size {
  x: number;
  y: number;
}

export interface Rectangle extends Dimensions {
  right: number;
  bottom: number;
}

export type AspectRatio = `${number}:${number}`;

export interface ImageMetadata {
  size: Size;
  aspectRatio: AspectRatio;
  format: string;
  quality?: number;
}

export type TerrainType = 'plains' | 'forest' | 'mountain' | 'water' | 'desert' | 'swamp';

export type POIType = 'city' | 'dungeon' | 'quest' | 'landmark';
