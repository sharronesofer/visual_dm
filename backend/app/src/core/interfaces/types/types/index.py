from typing import Any


/**
 * Shared Types Barrel File
 *
 * This is the main entry point for all shared type definitions used throughout the application.
 * Types are organized into logical groups for better maintainability and discoverability.
 *
 * @module SharedTypes
 */
* from './common'
* from './models'
* from './api'
* from './services'
* from './errors'
* from './map'
* from './statistics'
* from './storage'
* from './selection'
* from './validation'
* from './common/geometry'
/**
 * Re-specific types that are commonly used
 * This provides a convenient way to import frequently used types
 */
type {
  Identifiable,
  Timestamped,
  ApiResponse,
  ValidationResult,
  ValidationWarning,
  ServiceConfig,
  CacheConfig,
  EntityRef,
  AuditInfo,
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
} from './common'
type {
  BaseEntity,
  FullEntity,
  Model,
  HasOne,
  HasMany,
  BelongsTo,
  BelongsToMany,
} from './models'
type {
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
} from './services'
type {
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
} from './errors'