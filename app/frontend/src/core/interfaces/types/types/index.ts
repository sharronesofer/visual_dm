/**
 * Shared Types Barrel File
 *
 * This is the main entry point for all shared type definitions used throughout the application.
 * Types are organized into logical groups for better maintainability and discoverability.
 *
 * @module SharedTypes
 */

// Core Types
// Basic type definitions and interfaces used across the application
export * from './common';
export * from './models';

// API & Services
// Types related to API communication and service layer
export * from './api';
export * from './services';
export * from './errors';

// Feature-Specific Types
// Types organized by feature or domain
export * from './map';
export * from './statistics';
export * from './storage';
export * from './selection';

// Utility Types
// Types for validation, common operations, and shared functionality
export * from './validation';
export * from './common/geometry';

/**
 * Re-export specific types that are commonly used
 * This provides a convenient way to import frequently used types
 */
export type {
  // Common Types
  Identifiable,
  Timestamped,
  ApiResponse,
  ValidationResult,
  ValidationWarning,
  ServiceConfig,
  CacheConfig,
  EntityRef,
  AuditInfo,
  // Utility Types
  Nullable,
  Optional,
  ReadOnly,
  DeepPartial,
  RecursiveRequired,
  FormState,
  ValidationErrors,
  State,
  Action,
  Reducer,
} from './common';

export type {
  // Model Types
  BaseEntity,
  FullEntity,
  Model,
  // Relationship Types
  HasOne,
  HasMany,
  BelongsTo,
  BelongsToMany,
} from './models';

export type {
  // Service Interfaces
  IBaseService,
  IPaginatedService,
  ISearchableService,
  IBulkService,
  ICacheableService,
  IRealtimeService,
  IValidatableService,
  IActionableService,
  IRelationalService,
  IVersionedService,
} from './services';

export type {
  // Error Types
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
} from './errors';
