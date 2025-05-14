/**
 * Base service implementation
 * @module core/base/services/base
 */

import { BaseEntity } from '../types/entity';
import { 
  ServiceResponse, 
  PaginatedResponse, 
  QueryParams,
  ValidationResult,
  ServiceConfig,
  ServiceEvent,
  ServiceEventHandler,
  ServiceEventType
} from '../types/common';
import { IBaseService } from '../interfaces/base.interface';

/**
 * Abstract base service class that implements IBaseService
 */
export abstract class BaseService<T extends BaseEntity> implements IBaseService<T> {
  protected config: ServiceConfig;
  protected subscribers: Map<string, Set<ServiceEventHandler<T>>> = new Map();

  constructor(config: Partial<ServiceConfig> = {}) {
    this.config = {
      baseURL: config.baseURL || 'http://localhost:3000',
      timeout: config.timeout || 5000,
      headers: config.headers || {},
      ...config
    };
  }

  // Abstract methods that must be implemented by derived classes
  protected abstract executeCreate(data: Omit<T, keyof BaseEntity>): Promise<T>;
  protected abstract executeUpdate(id: T['id'], data: Partial<T>): Promise<T>;
  protected abstract executeDelete(id: T['id']): Promise<void>;
  protected abstract executeFindById(id: T['id']): Promise<T | null>;
  protected abstract executeFindAll(params?: QueryParams<T>): Promise<PaginatedResponse<T>>;
  protected abstract executeFindOne(params: QueryParams<T>): Promise<T | null>;
  protected abstract executeValidate(data: Partial<T>): Promise<ValidationResult>;
  protected abstract executeValidateField(field: keyof T, value: any): Promise<ValidationResult>;

  // CRUD Operations
  async findById(id: T['id']): Promise<ServiceResponse<T>> {
    try {
      const result = await this.executeFindById(id);
      if (!result) {
        return {
          success: false,
          error: new Error(`Entity with ID ${id} not found`)
        };
      }
      return { success: true, data: result };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async findAll(params?: QueryParams<T>): Promise<ServiceResponse<PaginatedResponse<T>>> {
    try {
      const result = await this.executeFindAll(params);
      return { success: true, data: result };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async findOne(params: QueryParams<T>): Promise<ServiceResponse<T | null>> {
    try {
      const result = await this.executeFindOne(params);
      return { success: true, data: result };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async create(data: Omit<T, keyof BaseEntity>): Promise<ServiceResponse<T>> {
    try {
      // Cast is safe: for creation, we only validate the provided fields (base fields are added after)
      const validationResult = await this.validate(data as Partial<T>);
      if (!validationResult.isValid) {
        return {
          success: false,
          error: new Error('Validation failed'),
          metadata: { validationErrors: validationResult.errors }
        };
      }

      const result = await this.executeCreate(data);
      this.emit({
        type: ServiceEventType.Created,
        data: result,
        timestamp: new Date()
      });
      return { success: true, data: result };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async update(id: T['id'], data: Partial<T>): Promise<ServiceResponse<T>> {
    try {
      const validationResult = await this.validate(data);
      if (!validationResult.isValid) {
        return {
          success: false,
          error: new Error('Validation failed'),
          metadata: { validationErrors: validationResult.errors }
        };
      }

      const result = await this.executeUpdate(id, data);
      this.emit({
        type: ServiceEventType.Updated,
        data: result,
        timestamp: new Date()
      });
      return { success: true, data: result };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async delete(id: T['id']): Promise<ServiceResponse<void>> {
    try {
      await this.executeDelete(id);
      this.emit({
        type: ServiceEventType.Deleted,
        data: { id } as any,
        timestamp: new Date()
      });
      return { success: true };
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Validation
  async validate(data: Partial<T>): Promise<ValidationResult> {
    return this.executeValidate(data);
  }

  async validateField(field: keyof T, value: any): Promise<ValidationResult> {
    return this.executeValidateField(field, value);
  }

  // Configuration
  getConfig(): ServiceConfig {
    return { ...this.config };
  }

  setConfig(config: Partial<ServiceConfig>): void {
    this.config = {
      ...this.config,
      ...config
    };
  }

  // Event handling
  on(event: string, handler: ServiceEventHandler<T>): void {
    if (!this.subscribers.has(event)) {
      this.subscribers.set(event, new Set());
    }
    this.subscribers.get(event)!.add(handler);
  }

  off(event: string, handler: ServiceEventHandler<T>): void {
    const handlers = this.subscribers.get(event);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.subscribers.delete(event);
      }
    }
  }

  emit(event: ServiceEvent<T>): void {
    const handlers = this.subscribers.get(event.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(event);
        } catch (error) {
          console.error('Error in event handler:', error);
        }
      });
    }
  }

  // Error handling
  protected handleError(error: any): ServiceResponse {
    console.error('Service error:', error);
    return {
      success: false,
      error: error instanceof Error ? error : new Error(String(error))
    };
  }
} 