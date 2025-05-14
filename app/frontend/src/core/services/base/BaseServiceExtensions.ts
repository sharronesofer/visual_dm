import { BaseService } from './BaseService';
import {
  IPaginatedService,
  ISearchableService,
  IBulkService,
  ICacheableService,
  IRealtimeService,
} from './IService';

/**
 * Base implementation of paginated service functionality
 */
// Commented out: BasePaginatedService<
//     T = any,
//     CreateDTO = any,
//     UpdateDTO = Partial<CreateDTO>,
//   >
//   extends BaseService<T, CreateDTO, UpdateDTO>
//   implements IPaginatedService<T>
// {
//   async listPaginated(
//     page: number,
//     limit: number,
export abstract class BasePaginatedService<
    T = any,
    CreateDTO = any,
    UpdateDTO = Partial<CreateDTO>,
  >
  extends BaseService<T, CreateDTO, UpdateDTO>
  implements IPaginatedService<T>
{
  async listPaginated(
    page: number,
    limit: number,
    params?: Record<string, any>
  ): Promise<
    ServiceResponse<{
      items: T[];
      total: number;
      page: number;
      limit: number;
    }>
  > {
    return this.get('/', {
      params: {
        page,
        limit,
        ...params,
      },
    });
  }
}

/**
 * Base implementation of searchable service functionality
 */
export abstract class BaseSearchableService<
    T = any,
    CreateDTO = any,
    UpdateDTO = Partial<CreateDTO>,
  >
  extends BaseService<T, CreateDTO, UpdateDTO>
  implements ISearchableService<T>
{
  async search(
    query: string,
    params?: Record<string, any>
  ): Promise<ServiceResponse<T[]>> {
    return this.get('/search', {
      params: {
        q: query,
        ...params,
      },
    });
  }
}

/**
 * Base implementation of bulk operation service functionality
 */
export abstract class BaseBulkService<
    T = any,
    CreateDTO = any,
    UpdateDTO = Partial<CreateDTO>,
  >
  extends BaseService<T, CreateDTO, UpdateDTO>
  implements IBulkService<T, CreateDTO, UpdateDTO>
{
  async bulkCreate(data: CreateDTO[]): Promise<ServiceResponse<T[]>> {
    const errors = await Promise.all(data.map(item => this.validate(item)));
    const allErrors = errors.flat();
    if (allErrors.length > 0) {
      return this.handleValidationError(allErrors);
    }
    return this.post<T[]>('/bulk', data);
  }

  async bulkUpdate(
    updates: { id: string; data: UpdateDTO }[]
  ): Promise<ServiceResponse<T[]>> {
    const errors = await Promise.all(
      updates.map(update => this.validate(update.data))
    );
    const allErrors = errors.flat();
    if (allErrors.length > 0) {
      return this.handleValidationError(allErrors);
    }
    return this.put<T[]>('/bulk', updates);
  }

  async bulkDelete(ids: string[]): Promise<ServiceResponse<void>> {
    return this.delete<void>('/bulk', { data: { ids } });
  }
}

/**
 * Base implementation of cacheable service functionality
 */
export abstract class BaseCacheableService<
    T = any,
    CreateDTO = any,
    UpdateDTO = Partial<CreateDTO>,
  >
  extends BaseService<T, CreateDTO, UpdateDTO>
  implements ICacheableService<T>
{
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private cacheTimeout: number;

  constructor(baseURL: string, config?: Partial<ServiceConfig>) {
    super(baseURL, config);
    this.cacheTimeout = config?.cacheTimeout || 5 * 60 * 1000; // 5 minutes default
  }

  clearCache(): void {
    this.cache.clear();
  }

  getCacheKey(method: string, params: any[]): string {
    return `${method}:${JSON.stringify(params)}`;
  }

  setCacheTimeout(timeout: number): void {
    this.cacheTimeout = timeout;
  }

  protected async get<R>(
    path: string,
    config?: ServiceConfig
  ): Promise<ServiceResponse<R>> {
    const cacheKey = this.getCacheKey('get', [path, config]);
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    const response = await super.get<R>(path, config);
    if (response.success) {
      this.cache.set(cacheKey, { data: response, timestamp: Date.now() });
    }
    return response;
  }
}

/**
 * Base implementation of realtime service functionality
 */
export abstract class BaseRealtimeService<
    T = any,
    CreateDTO = any,
    UpdateDTO = Partial<CreateDTO>,
  >
  extends BaseService<T, CreateDTO, UpdateDTO>
  implements IRealtimeService<T>
{
  private subscribers: Set<(data: T) => void> = new Set();

  subscribe(callback: (data: T) => void): () => void {
    this.subscribers.add(callback);
    return () => this.unsubscribe(callback);
  }

  unsubscribe(callback: (data: T) => void): void {
    this.subscribers.delete(callback);
  }

  publish(data: T): void {
    this.subscribers.forEach(callback => callback(data));
  }

  protected async post<R>(
    path: string,
    data?: any,
    config?: ServiceConfig
  ): Promise<ServiceResponse<R>> {
    const response = await super.post<R>(path, data, config);
    if (response.success && this.config.enableRealtime) {
      this.publish(response.data as unknown as T);
    }
    return response;
  }

  protected async put<R>(
    path: string,
    data?: any,
    config?: ServiceConfig
  ): Promise<ServiceResponse<R>> {
    const response = await super.put<R>(path, data, config);
    if (response.success && this.config.enableRealtime) {
      this.publish(response.data as unknown as T);
    }
    return response;
  }

  protected async delete<R>(
    path: string,
    config?: ServiceConfig
  ): Promise<ServiceResponse<R>> {
    const response = await super.delete<R>(path, config);
    if (response.success && this.config.enableRealtime) {
      this.publish(null as unknown as T);
    }
    return response;
  }
}

/**
 * Registers base and derived services in the provided DI container.
 * Extend this function to register additional services as needed.
 * @param container The DI container instance (e.g., from inversify, tsyringe, or custom)
 */
export function registerBaseServices(container: any): void {
  // Example: container.register('BaseService', { useClass: BaseService });
  // Register additional services here, e.g.:
  // container.register('UserService', { useClass: UserService });
  // container.register('Repository', { useClass: UserRepository });
  // container.register('Logger', { useClass: Logger });
}

/**
 * Usage example:
 *
 * import { container } from 'tsyringe';
 * import { registerBaseServices } from './BaseServiceExtensions';
 *
 * registerBaseServices(container);
 * const userService = container.resolve('UserService');
 */
