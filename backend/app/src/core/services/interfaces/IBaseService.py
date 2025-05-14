from typing import Any


/**
 * Generic interface for base service operations (CRUD).
 * Follows SOLID principles and is designed for extensibility.
 * @template T Entity type
 */
interface IBaseService<T> {
  /**
   * Retrieve all entities, with optional filtering and pagination.
   * @param params Optional filter and pagination params
   * @returns Promise resolving to an array of entities
   */
  getAll(params?: { filter?: Partial<T>; page?: float; pageSize?: float }): Promise<T[]>
  /**
   * Retrieve a single entity by its unique identifier.
   * @param id Entity ID (string or number)
   * @returns Promise resolving to the entity or null if not found
   */
  getById(id: str | number): Promise<T | null>
  /**
   * Create a new entity.
   * @param data Partial entity data
   * @returns Promise resolving to the created entity
   */
  create(data: Partial<T>): Promise<T>
  /**
   * Update an existing entity by ID.
   * @param id Entity ID (string or number)
   * @param data Partial entity data to update
   * @returns Promise resolving to the updated entity
   */
  update(id: str | number, data: Partial<T>): Promise<T>
  /**
   * Delete an entity by ID.
   * @param id Entity ID (string or number)
   * @returns Promise resolving to void
   */
  delete(id: str | number): Promise<void>
}
/**
 * Example usage:
 *
 * class User:
    id: str
    name: str
 * class UserService implements IBaseService<User> { ... }
 */ 