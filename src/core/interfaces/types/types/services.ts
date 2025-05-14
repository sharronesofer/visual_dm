import {
  ApiResponse,
  ValidationResult,
  SearchParams,
  BulkOperation,
  ServiceConfig,
} from './common';

/**
 * Base interface for all services
 */
export interface IBaseService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> {
  // CRUD Operations
  getById(id: string): Promise<ApiResponse<T>>;
  list(params?: Record<string, any>): Promise<ApiResponse<T[]>>;
  create(data: CreateDTO): Promise<ApiResponse<T>>;
  update(id: string, data: UpdateDTO): Promise<ApiResponse<T>>;
  delete(id: string): Promise<ApiResponse<void>>;

  // Validation
  validate(data: CreateDTO | UpdateDTO): Promise<ValidationResult>;
  validateField(field: string, value: any): Promise<ValidationResult>;

  // Configuration
  getConfig(): ServiceConfig;
  setConfig(config: Partial<ServiceConfig>): void;
}

/**
 * Interface for services that support pagination
 */
export interface IPaginatedService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  listPaginated(
    page: number,
    limit: number,
    params?: Record<string, any>
  ): Promise<
    ApiResponse<{
      items: T[];
      total: number;
      page: number;
      limit: number;
      hasMore: boolean;
    }>
  >;
}

/**
 * Interface for services that support search operations
 */
export interface ISearchableService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  search(params: SearchParams): Promise<ApiResponse<T[]>>;
}

/**
 * Interface for services that support bulk operations
 */
export interface IBulkService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  bulkCreate(operation: BulkOperation<CreateDTO>): Promise<ApiResponse<T[]>>;
  bulkUpdate(
    operation: BulkOperation<{ id: string; data: UpdateDTO }>
  ): Promise<ApiResponse<T[]>>;
  bulkDelete(ids: string[]): Promise<ApiResponse<void>>;
}

/**
 * Interface for services that support caching
 */
export interface ICacheableService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  clearCache(): void;
  getCacheKey(method: string, params: any[]): string;
  setCacheTimeout(timeout: number): void;
}

/**
 * Interface for services that support real-time updates
 */
export interface IRealtimeService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  subscribe(callback: (data: T) => void): () => void;
  unsubscribe(callback: (data: T) => void): void;
  publish(data: T): void;
}

/**
 * Interface for services that support validation rules
 */
export interface IValidatableService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  getValidationRules(): Record<string, any>;
  setValidationRules(rules: Record<string, any>): void;
}

/**
 * Interface for services that support custom actions
 */
export interface IActionableService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  executeAction<R = any>(
    action: string,
    params?: Record<string, any>
  ): Promise<ApiResponse<R>>;
  getAvailableActions(): string[];
}

/**
 * Interface for services that support entity relationships
 */
export interface IRelationalService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  getRelated(id: string, relation: string): Promise<ApiResponse<any>>;
  updateRelation(
    id: string,
    relation: string,
    relatedId: string
  ): Promise<ApiResponse<void>>;
  removeRelation(
    id: string,
    relation: string,
    relatedId: string
  ): Promise<ApiResponse<void>>;
}

/**
 * Interface for services that support versioning
 */
export interface IVersionedService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> extends IBaseService<T, CreateDTO, UpdateDTO> {
  getVersion(id: string, version: number): Promise<ApiResponse<T>>;
  getVersions(id: string): Promise<ApiResponse<number[]>>;
  revertToVersion(id: string, version: number): Promise<ApiResponse<T>>;
}

/**
 * Utility type to extract the entity type from a service interface
 */
export type ServiceEntity<T> =
  T extends IBaseService<infer E, any, any> ? E : never;

/**
 * Utility type to extract the create DTO type from a service interface
 */
export type ServiceCreateDTO<T> =
  T extends IBaseService<any, infer C, any> ? C : never;

/**
 * Utility type to extract the update DTO type from a service interface
 */
export type ServiceUpdateDTO<T> =
  T extends IBaseService<any, any, infer U> ? U : never;

/**
 * Utility type to create a fully featured service interface
 */
export type FullService<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> = IBaseService<T, CreateDTO, UpdateDTO> &
  IPaginatedService<T, CreateDTO, UpdateDTO> &
  ISearchableService<T, CreateDTO, UpdateDTO> &
  IBulkService<T, CreateDTO, UpdateDTO> &
  ICacheableService<T, CreateDTO, UpdateDTO> &
  IRealtimeService<T, CreateDTO, UpdateDTO> &
  IValidatableService<T, CreateDTO, UpdateDTO> &
  IActionableService<T, CreateDTO, UpdateDTO> &
  IRelationalService<T, CreateDTO, UpdateDTO> &
  IVersionedService<T, CreateDTO, UpdateDTO>;

/**
 * Type for service factory functions
 */
export type ServiceFactory<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> = {
  create(
    config?: Partial<ServiceConfig>
  ): IBaseService<T, CreateDTO, UpdateDTO>;
};

/**
 * Type for service decorator functions
 */
export type ServiceDecorator<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> = {
  (
    service: IBaseService<T, CreateDTO, UpdateDTO>
  ): IBaseService<T, CreateDTO, UpdateDTO>;
};

/**
 * Type for service event handlers
 */
export type ServiceEventHandler<T = any> = {
  onCreated?: (entity: T) => void | Promise<void>;
  onUpdated?: (entity: T) => void | Promise<void>;
  onDeleted?: (id: string) => void | Promise<void>;
  onError?: (error: Error) => void | Promise<void>;
};

/**
 * Type for service middleware
 */
export type ServiceMiddleware<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> = {
  before?: (method: keyof IBaseService, args: any[]) => void | Promise<void>;
  after?: (method: keyof IBaseService, result: any) => void | Promise<void>;
  error?: (method: keyof IBaseService, error: Error) => void | Promise<void>;
};

/**
 * Type for service query builders
 */
export type ServiceQueryBuilder<T = any> = {
  where(conditions: Partial<T>): ServiceQueryBuilder<T>;
  orderBy(field: keyof T, direction: 'asc' | 'desc'): ServiceQueryBuilder<T>;
  limit(count: number): ServiceQueryBuilder<T>;
  offset(count: number): ServiceQueryBuilder<T>;
  include(relations: string[]): ServiceQueryBuilder<T>;
  build(): Record<string, any>;
};

/**
 * Type for service hooks
 */
export type ServiceHooks<
  T = any,
  CreateDTO = any,
  UpdateDTO = Partial<CreateDTO>,
> = {
  beforeCreate?: (data: CreateDTO) => CreateDTO | Promise<CreateDTO>;
  afterCreate?: (entity: T) => T | Promise<T>;
  beforeUpdate?: (
    id: string,
    data: UpdateDTO
  ) => UpdateDTO | Promise<UpdateDTO>;
  afterUpdate?: (entity: T) => T | Promise<T>;
  beforeDelete?: (id: string) => void | Promise<void>;
  afterDelete?: (id: string) => void | Promise<void>;
};
