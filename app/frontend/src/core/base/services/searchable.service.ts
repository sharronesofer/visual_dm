/**
 * Searchable service implementation
 * @module core/base/services/searchable
 */

import { BaseEntity } from '../types/entity';
import { BaseService } from './base.service';
import { ISearchableService, SearchParams } from '../interfaces/searchable.interface';
import { ServiceResponse, PaginatedResponse } from '../types/common';

/**
 * Abstract searchable service class that extends BaseService and implements ISearchableService
 */
export abstract class SearchableService<T extends BaseEntity> extends BaseService<T> implements ISearchableService<T> {
  // Abstract methods that must be implemented by derived classes
  protected abstract executeSearch(params: SearchParams<T>): Promise<PaginatedResponse<T>>;
  protected abstract executeGetSuggestions(query: string, field: keyof T): Promise<string[]>;
  protected abstract getDefaultSearchableFields(): Array<keyof T>;
  protected abstract getDefaultFilterableFields(): Array<keyof T>;
  protected abstract getDefaultSortableFields(): Array<keyof T>;

  /**
   * Search for entities
   */
  async search(params: SearchParams<T>): Promise<ServiceResponse<PaginatedResponse<T>>> {
    try {
      // Validate search parameters
      if (!params.query && !params.filters) {
        return {
          success: false,
          error: new Error('Either query or filters must be provided')
        };
      }

      // Set default fields if not provided
      if (!params.fields || params.fields.length === 0) {
        params.fields = this.getSearchableFields();
      }

      // Validate fields are searchable
      const invalidFields = params.fields.filter(field => !this.getSearchableFields().includes(field));
      if (invalidFields.length > 0) {
        return {
          success: false,
          error: new Error(`Invalid search fields: ${invalidFields.join(', ')}`)
        };
      }

      // Execute search
      const result = await this.executeSearch(params);
      return {
        success: true,
        data: result
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Get search suggestions
   */
  async getSuggestions(query: string, field: keyof T): Promise<ServiceResponse<string[]>> {
    try {
      // Validate field is searchable
      if (!this.getSearchableFields().includes(field)) {
        return {
          success: false,
          error: new Error(`Field ${String(field)} is not searchable`)
        };
      }

      // Get suggestions
      const suggestions = await this.executeGetSuggestions(query, field);
      return {
        success: true,
        data: suggestions
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Get available search fields
   */
  getSearchableFields(): Array<keyof T> {
    return this.getDefaultSearchableFields();
  }

  /**
   * Get available filter fields
   */
  getFilterableFields(): Array<keyof T> {
    return this.getDefaultFilterableFields();
  }

  /**
   * Get available sort fields
   */
  getSortableFields(): Array<keyof T> {
    return this.getDefaultSortableFields();
  }

  /**
   * Helper method to validate search parameters
   */
  protected validateSearchParams(params: SearchParams<T>): ServiceResponse<void> {
    // Validate page and limit
    if (params.page !== undefined && params.page < 1) {
      return {
        success: false,
        error: new Error('Page must be greater than 0')
      };
    }

    if (params.limit !== undefined && params.limit < 1) {
      return {
        success: false,
        error: new Error('Limit must be greater than 0')
      };
    }

    // Validate sort fields
    if (params.sort) {
      const sortFields = Object.keys(params.sort) as Array<keyof T>;
      const invalidSortFields = sortFields.filter(field => !this.getSortableFields().includes(field));
      if (invalidSortFields.length > 0) {
        return {
          success: false,
          error: new Error(`Invalid sort fields: ${invalidSortFields.join(', ')}`)
        };
      }
    }

    // Validate filter fields
    if (params.filters) {
      const filterFields = Object.keys(params.filters) as Array<keyof T>;
      const invalidFilterFields = filterFields.filter(field => !this.getFilterableFields().includes(field));
      if (invalidFilterFields.length > 0) {
        return {
          success: false,
          error: new Error(`Invalid filter fields: ${invalidFilterFields.join(', ')}`)
        };
      }
    }

    return { success: true };
  }
} 