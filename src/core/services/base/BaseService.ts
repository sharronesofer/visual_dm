import { Repository } from '../../core/interfaces/Repository';
import { BaseEntity } from '../../core/interfaces/BaseEntity';
import { Logger } from '../../utils/logger';
import { IBaseService } from '../interfaces/IBaseService';
import { ServiceError, NotFoundError, ValidationError, DatabaseError } from '../../errors/ServiceError';
import { Transaction } from '../../types/Transaction';
import { ILogger } from '../../interfaces/ILogger';

/**
 * Abstract base class for generic service operations.
 * Implements IBaseService<T> and provides default CRUD logic.
 * @template T Entity type
 */
export abstract class BaseService<T extends BaseEntity> implements IBaseService<T> {
  protected readonly repository: Repository<T>;
  protected readonly logger: Logger;
  protected abstract readonly entityName: string;
  protected abstract tableName: string;

  constructor(repository: Repository<T>, logger?: Logger) {
    this.repository = repository;
    this.logger = logger || new Logger({ prefix: 'BaseService' });
  }

  /**
   * Retrieve all entities, with optional filtering and pagination.
   */
  async getAll(params?: { filter?: Partial<T>; page?: number; pageSize?: number }): Promise<T[]> {
    try {
      // Map params to repository's expected arguments if needed
      return (await this.repository.findAll()).data;
    } catch (error) {
      this.logger.error('BaseService.getAll error', error);
      throw error;
    }
  }

  /**
   * Retrieve a single entity by its unique identifier.
   */
  async getById(id: string | number): Promise<T | null> {
    try {
      return await this.repository.findById(id);
    } catch (error) {
      this.logger.error('BaseService.getById error', error);
      throw error;
    }
  }

  /**
   * Create a new entity.
   */
  async create(data: Partial<T>): Promise<T> {
    try {
      // Type assertion: repository expects a full T, so concrete services should validate/construct T
      return await this.repository.create(data as T);
    } catch (error) {
      this.logger.error('BaseService.create error', error);
      throw error;
    }
  }

  /**
   * Update an existing entity by ID.
   */
  async update(id: string | number, data: Partial<T>): Promise<T> {
    try {
      // Type assertion: repository expects a full T, so concrete services should validate/construct T
      const updated = await this.repository.update(id, data as T);
      if (!updated) throw new Error('Entity not found');
      return updated;
    } catch (error) {
      this.logger.error('BaseService.update error', error);
      throw error;
    }
  }

  /**
   * Delete an entity by ID.
   */
  async delete(id: string | number): Promise<void> {
    try {
      const result = await this.repository.delete(id);
      if (!result) throw new Error('Entity not found or could not be deleted');
    } catch (error) {
      this.logger.error('BaseService.delete error', error);
      throw error;
    }
  }

  /**
   * Retrieve multiple entities by their IDs
   * @param ids Array of entity IDs
   * @returns Promise resolving to array of found entities
   * @throws DatabaseError if retrieval fails
   */
  async findByIds(ids: string[]): Promise<T[]> {
    try {
      const results = await Promise.all(
        ids.map(id => this.repository.findById(id))
      );
      // Type assertion is safe here because we filter out null values
      return results.filter((entity): entity is T => entity !== null);
    } catch (error) {
      this.logger.error(`Failed to find ${this.entityName}s by ids`, { ids, error });
      throw this.handleError(error);
    }
  }

  /**
   * Check if an entity exists
   * @param id Entity ID
   * @returns Promise resolving to boolean indicating existence
   */
  async exists(id: string): Promise<boolean> {
    const entity = await this.getById(id);
    return entity !== null;
  }

  /**
   * Validate entity data
   * @param data Entity data to validate
   * @returns Promise resolving to validation result
   * @throws ValidationError if validation fails
   */
  async validate(data: Partial<T>): Promise<boolean> {
    try {
      await this.validateEntity(data);
      return true;
    } catch (error) {
      if (error instanceof Error) {
        throw new ValidationError(`Invalid ${this.entityName} data: ${error.message}`);
      }
      throw new ValidationError(`Invalid ${this.entityName} data: Unknown error`);
    }
  }

  /**
   * Helper method to get current timestamp
   * @returns Current Date object
   */
  protected getCurrentTimestamp(): Date {
    return new Date();
  }

  /**
   * Helper method to generate a new version number
   * @returns Incremented version number
   */
  protected getNextVersion(currentVersion: number): number {
    return currentVersion + 1;
  }

  /**
   * Helper method to handle errors
   * @param error Error to handle
   * @returns Appropriate error type
   */
  protected handleError(error: unknown): Error {
    if (error instanceof ServiceError) {
      return error;
    }
    if (error instanceof Error) {
      return new DatabaseError(`Database operation failed: ${error.message}`);
    }
    return new DatabaseError('Database operation failed: Unknown error');
  }

  /**
   * Validate entity data
   * @param entity Entity data to validate
   * @throws ValidationError if validation fails
   */
  protected abstract validateEntity(data: Partial<T>): Promise<void>;

  async findAll(options?: { limit?: number; offset?: number }, transaction?: Transaction): Promise<T[]> {
    try {
      return await this.repository.getAll(options);
    } catch (error) {
      this.logger.error(`Error finding all ${this.tableName} entities`, { error });
      throw this.handleError(error);
    }
  }

  async delete(id: string | number, transaction?: Transaction): Promise<void> {
    try {
      await this.getById(id);
      await this.repository.delete(id, transaction);
      this.logger.info(`Deleted ${this.tableName} entity`, { id });
    } catch (error) {
      this.logger.error(`Error deleting ${this.tableName} entity`, { id, error });
      throw this.handleError(error);
    }
  }
}
