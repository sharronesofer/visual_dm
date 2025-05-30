from typing import Any



/**
 * Searchable interface
 * @module core/base/interfaces/searchable
 */
/**
 * Search parameters interface
 */
interface SearchParams<T> {
  query: str
  fields?: Array<keyof T>
  filters?: Partial<T>
  sort?: {
    [K in keyof T]?: 'asc' | 'desc'
  }
  page?: float
  limit?: float
}
/**
 * Interface for services that support search operations
 */
interface ISearchableService<T extends BaseEntity> {
  /**
   * Search for entities
   * @param params Search parameters
   */
  search(params: SearchParams<T>): Promise<ServiceResponse<PaginatedResponse<T>>>
  /**
   * Get search suggestions
   * @param query Search query
   * @param field Field to get suggestions for
   */
  getSuggestions(query: str, field: keyof T): Promise<ServiceResponse<string[]>>
  /**
   * Get available search fields
   */
  getSearchableFields(): Array<keyof T>
  /**
   * Get available filter fields
   */
  getFilterableFields(): Array<keyof T>
  /**
   * Get available sort fields
   */
  getSortableFields(): Array<keyof T>
} 