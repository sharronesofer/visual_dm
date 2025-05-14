/**
 * Searchable interface
 * @module core/base/interfaces/searchable
 */

import { BaseEntity } from '../types/entity';
import { ServiceResponse, PaginatedResponse } from '../types/common';

/**
 * Search parameters interface
 */
export interface SearchParams<T> {
  query: string;
  fields?: Array<keyof T>;
  filters?: Partial<T>;
  sort?: {
    [K in keyof T]?: 'asc' | 'desc';
  };
  page?: number;
  limit?: number;
}

/**
 * Interface for services that support search operations
 */
export interface ISearchableService<T extends BaseEntity> {
  /**
   * Search for entities
   * @param params Search parameters
   */
  search(params: SearchParams<T>): Promise<ServiceResponse<PaginatedResponse<T>>>;

  /**
   * Get search suggestions
   * @param query Search query
   * @param field Field to get suggestions for
   */
  getSuggestions(query: string, field: keyof T): Promise<ServiceResponse<string[]>>;

  /**
   * Get available search fields
   */
  getSearchableFields(): Array<keyof T>;

  /**
   * Get available filter fields
   */
  getFilterableFields(): Array<keyof T>;

  /**
   * Get available sort fields
   */
  getSortableFields(): Array<keyof T>;
} 