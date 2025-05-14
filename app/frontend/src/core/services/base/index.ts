import { ServiceResponse, ServiceConfig } from '../base.service';

// Service Interfaces
export * from './IService';

// Base Service and Types
export * from './BaseService';

// Service Extensions
export * from './BaseServiceExtensions';

export interface BaseEntity {
  id: string | number;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface ICacheableService {
  clearCache(pattern?: string): void;
  getCacheKey(method: string, params: any[]): string;
  setCacheConfig(config: {
    ttl?: number;
    policy?: 'memory' | 'session' | 'none';
    bypassCache?: boolean;
  }): void;
}

export interface BasePaginatedService<T> {
  listPaginated(
    page: number,
    limit: number,
    params?: Record<string, any>
  ): Promise<ServiceResponse<{
    items: T[];
    total: number;
    page: number;
    limit: number;
  }>>;
}

export interface BaseSearchableService<T, P> {
  search(params: P, config?: ServiceConfig): Promise<ServiceResponse<T[]>>;
}

export interface BaseServiceInterface<T extends BaseEntity> {
  get(id: string | number): Promise<ServiceResponse<T>>;
  list(params?: Record<string, any>): Promise<ServiceResponse<T[]>>;
  create(data: Partial<T>): Promise<ServiceResponse<T>>;
  update(id: string | number, data: Partial<Omit<T, 'id'>>): Promise<ServiceResponse<T>>;
  delete(id: string | number): Promise<ServiceResponse<void>>;
}
