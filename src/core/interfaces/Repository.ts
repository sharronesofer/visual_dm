import { ID, PaginationParams, SortParams, QueryFilters } from '../types/common';
import { BaseEntity } from './BaseEntity';

/**
 * Repository response with pagination
 */
export interface RepositoryResponse<T> {
  data: T[];
  total: number;
}

/**
 * Generic repository interface
 */
export interface Repository<T extends BaseEntity> {
  findById(id: ID): Promise<T | null>;
  findAll(
    pagination?: PaginationParams,
    sort?: SortParams,
    filters?: QueryFilters
  ): Promise<RepositoryResponse<T>>;
  create(entity: T): Promise<T>;
  update(id: ID, entity: T): Promise<T | null>;
  delete(id: ID): Promise<boolean>;
} 