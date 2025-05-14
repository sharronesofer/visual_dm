import { BaseEntity } from '../../types/base/BaseEntity';

/**
 * Base service interface defining common CRUD operations
 * @template T - Type of entity extending BaseEntity
 * @template C - Type for creation DTO
 * @template U - Type for update DTO
 */
export interface IBaseService<T extends BaseEntity, C = Partial<T>, U = Partial<T>> {
  /**
   * Create a new entity
   * @param data Creation data
   * @returns Promise resolving to created entity
   */
  create(data: C): Promise<T>;

  /**
   * Retrieve an entity by ID
   * @param id Entity ID
   * @returns Promise resolving to found entity or null
   */
  findById(id: string): Promise<T | null>;

  /**
   * Retrieve multiple entities by their IDs
   * @param ids Array of entity IDs
   * @returns Promise resolving to array of found entities
   */
  findByIds(ids: string[]): Promise<T[]>;

  /**
   * Update an existing entity
   * @param id Entity ID
   * @param data Update data
   * @returns Promise resolving to updated entity
   */
  update(id: string, data: U): Promise<T>;

  /**
   * Delete an entity by ID (soft delete)
   * @param id Entity ID
   * @returns Promise resolving to boolean indicating success
   */
  delete(id: string): Promise<boolean>;

  /**
   * Hard delete an entity by ID (permanent deletion)
   * @param id Entity ID
   * @returns Promise resolving to boolean indicating success
   */
  hardDelete(id: string): Promise<boolean>;

  /**
   * Check if an entity exists
   * @param id Entity ID
   * @returns Promise resolving to boolean indicating existence
   */
  exists(id: string): Promise<boolean>;

  /**
   * Validate entity data
   * @param data Entity data to validate
   * @returns Promise resolving to validation result
   */
  validate(data: Partial<T>): Promise<boolean>;
} 