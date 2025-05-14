import { ServiceResponse, ServiceConfig, ValidationError } from './types';

// Generic type for service parameters
export type ServiceParams = Record<string, string | number | boolean | null | undefined>;

/**
 * Standard interface that all services must implement.
 * Defines common patterns for CRUD operations, validation, and error handling.
 */
export interface IService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> {
  // CRUD Operations
  getById(id: string): Promise<ServiceResponse<T>>;
  list(params?: ServiceParams): Promise<ServiceResponse<T[]>>;
  create(data: CreateDTO): Promise<ServiceResponse<T>>;
  update(id: string, data: UpdateDTO): Promise<ServiceResponse<T>>;
  delete(id: string): Promise<ServiceResponse<boolean>>;

  // Validation
  validate(data: CreateDTO | UpdateDTO): Promise<ValidationError[]>;
  validateField(field: keyof (CreateDTO | UpdateDTO), value: unknown): Promise<ValidationError[]>;

  // Error Handling
  handleError(error: Error | unknown): ServiceResponse;
  handleValidationError(errors: ValidationError[]): ServiceResponse;

  // Configuration
  getConfig(): ServiceConfig;
  setConfig(config: Partial<ServiceConfig>): void;
}

/**
 * Optional interface for services that support pagination
 */
export interface IPaginatedService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> extends IService<T, CreateDTO, UpdateDTO> {
  listPaginated(
    page: number,
    limit: number,
    params?: ServiceParams
  ): Promise<
    ServiceResponse<{
      items: T[];
      total: number;
      page: number;
      limit: number;
    }>
  >;
}

/**
 * Optional interface for services that support search
 */
export interface ISearchableService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> extends IService<T, CreateDTO, UpdateDTO> {
  search(
    query: string,
    params?: ServiceParams
  ): Promise<ServiceResponse<T[]>>;
}

/**
 * Optional interface for services that support bulk operations
 */
export interface IBulkService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> extends IService<T, CreateDTO, UpdateDTO> {
  bulkCreate(data: CreateDTO[]): Promise<ServiceResponse<T[]>>;
  bulkUpdate(
    updates: { id: string; data: UpdateDTO }[]
  ): Promise<ServiceResponse<T[]>>;
  bulkDelete(ids: string[]): Promise<ServiceResponse<void>>;
}

/**
 * Optional interface for services that support caching
 */
export interface ICacheableService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> extends IService<T, CreateDTO, UpdateDTO> {
  clearCache(): void;
  getCacheKey(method: string, params: unknown[]): string;
  setCacheTimeout(timeout: number): void;
}

/**
 * Optional interface for services that support real-time updates
 */
export interface IRealtimeService<
  T extends Record<string, unknown>,
  CreateDTO extends Record<string, unknown>,
  UpdateDTO = Partial<CreateDTO>,
> extends IService<T, CreateDTO, UpdateDTO> {
  subscribe(callback: (data: T) => void): () => void;
  unsubscribe(callback: (data: T) => void): void;
  publish(data: T): void;
}
