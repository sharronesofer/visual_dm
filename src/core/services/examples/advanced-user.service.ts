// @deprecated This file previously used legacy base service imports. Now using consolidated base service and interfaces.
import { BaseService } from '../../core/base/services/base.service';
import { ICacheableService } from '../../core/base/interfaces/cached.interface';
import { IBulkService } from '../../core/base/interfaces/bulk.interface';
import { IPaginatedService } from '../../core/base/interfaces/base.interface';
import { ISearchableService } from '../../core/base/interfaces/searchable.interface';
import { ISoftDeletableService } from '../../core/base/interfaces/soft-deletable.interface';
import { IVersionableService } from '../../core/base/interfaces/versionable.interface';
import { IBulkOperationsService } from '../../core/base/interfaces/bulk-operations.interface';
import { IValidatableService } from '../../core/base/interfaces/validatable.interface';
import { IHookableService } from '../../core/base/interfaces/hookable.interface';
import { ITransactionalService } from '../../core/base/interfaces/transactional.interface';
import { IAdvancedCacheableService } from '../../core/base/interfaces/advanced-cacheable.interface';
import { IRateLimitedService } from '../../core/base/interfaces/rate-limited.interface';
import { ServiceResponse, PaginatedResponse, ValidationResult, ValidationError, QueryParams, ServiceConfig } from '../../core/base/types/common';
import { User, CreateUserDTO, UpdateUserDTO } from '../user/types';
import {
  ISoftDeletableService as OldISoftDeletableService,
  IVersionableService as OldIVersionableService,
  IBulkOperationsService as OldIBulkOperationsService,
  IValidatableService as OldIValidatableService,
  IHookableService as OldIHookableService,
  ITransactionalService as OldITransactionalService,
  IAdvancedCacheableService as OldIAdvancedCacheableService,
  IRateLimitedService as OldIRateLimitedService,
} from '../base/interfaces';
import { z } from 'zod';
import { EMAIL_REGEX, USERNAME_REGEX } from '../../constants/validation';

/**
 * Example of an advanced user service implementing multiple specialized interfaces
 * This demonstrates how to combine various service capabilities
 */
export class AdvancedUserService extends BaseService<User>
  implements
    ICacheableService<User>,
    IBulkService<User>,
    IPaginatedService<User>,
    ISearchableService<User>,
    ISoftDeletableService<User>,
    IVersionableService<User>,
    IBulkOperationsService<User>,
    IValidatableService<User>,
    IHookableService<User>,
    ITransactionalService,
    IAdvancedCacheableService,
    IRateLimitedService {
  
  private hooks: {
    beforeCreate: ((data: Partial<User>) => Promise<void>)[];
    afterCreate: ((entity: User) => Promise<void>)[];
    beforeUpdate: ((id: User['id'], data: Partial<User>) => Promise<void>)[];
    afterUpdate: ((entity: User) => Promise<void>)[];
    beforeDelete: ((id: User['id']) => Promise<void>)[];
    afterDelete: ((id: User['id']) => Promise<void>)[];
  };

  private rateLimit: {
    windowMs: number;
    maxRequests: number;
    errorMessage: string;
  };

  constructor() {
    super({ baseURL: '/users' });
    this.hooks = {
      beforeCreate: [],
      afterCreate: [],
      beforeUpdate: [],
      afterUpdate: [],
      beforeDelete: [],
      afterDelete: [],
    };
    this.rateLimit = {
      windowMs: 60000, // 1 minute
      maxRequests: 100,
      errorMessage: 'Too many requests',
    };
  }

  // #region ICacheableService Implementation
  async clearCache(pattern?: string): Promise<void> {
    // TODO: Implement cache clearing logic
  }

  getCacheKey(method: string, params: any[] = []): string {
    return `users:${method}:${JSON.stringify(params)}`;
  }

  setCacheConfig(config: {
    ttl?: number;
    policy?: 'memory' | 'session' | 'none';
    bypassCache?: boolean;
  }): void {
    // TODO: Implement cache config logic
  }

  invalidateCache(id: User['id']): void {}
  setCacheOptions(options: any): void {}
  getCacheOptions(): any { return {}; }
  hasCache(key: string): Promise<boolean> { return Promise.resolve(false); }
  getFromCache<R>(key: string): Promise<R | null> { return Promise.resolve(null); }
  setInCache<R>(key: string, value: R, ttl?: number): Promise<void> { return Promise.resolve(); }
  removeFromCache(key: string): Promise<void> { return Promise.resolve(); }
  // #endregion

  // #region IPaginatedService Implementation
  async listPaginated(
    page: number,
    limit: number,
    params?: Record<string, any>
  ): Promise<ServiceResponse<{
    items: User[];
    total: number;
    page: number;
    limit: number;
  }>> {
    // Use findAll from BaseService
    const result = await this.findAll({ ...params, page, limit });
    return {
      data: {
        items: result.items,
        total: result.total,
        page,
        limit,
      },
    };
  }
  // #endregion

  // #region ISearchableService Implementation
  async search(
    params: Record<string, any>,
    config?: ServiceConfig
  ): Promise<ServiceResponse<User[]>> {
    // Use findAll or findOne from BaseService as appropriate
    const result = await this.findAll(params);
    return { data: result.items };
  }
  // #endregion

  // #region ISoftDeletableService Implementation
  async softDelete(id: User['id']): Promise<ServiceResponse<void>> {
    // Use executeUpdate to set isDeleted flag
    await this.executeUpdate(id, { isDeleted: true } as Partial<User>);
    return { data: undefined };
  }

  async restore(id: User['id']): Promise<ServiceResponse<User>> {
    // Use executeUpdate to unset isDeleted flag
    const user = await this.executeUpdate(id, { isDeleted: false } as Partial<User>);
    return { data: user };
  }

  async listDeleted(params?: Record<string, any>): Promise<ServiceResponse<User[]>> {
    // Use findAll with filter for deleted users
    const result = await this.findAll({ ...params, isDeleted: true });
    return { data: result.items };
  }
  // #endregion

  // #region IVersionableService Implementation
  async getVersions(id: User['id']): Promise<ServiceResponse<User[]>> {
    // Placeholder: implement versioning logic as needed
    return { data: [] };
  }

  async revertToVersion(id: User['id'], version: number): Promise<ServiceResponse<User>> {
    // TODO: Replace with real implementation
    return { data: { id, /* add required User fields with dummy values */ } as User };
  }
  // #endregion

  // #region IBulkOperationsService Implementation
  async bulkCreate(data: Array<Omit<User, keyof User>>): Promise<ServiceResponse<User[]>> {
    // Return dummy users with required fields
    const now = new Date();
    const users = data.map((d, i) => ({
      ...d,
      id: d.id || i,
      createdAt: d.createdAt || now,
      updatedAt: d.updatedAt || now,
      email: d.email || '',
      username: d.username || '',
      isActive: true,
      role: 'user',
    }));
    return { success: true, data: users };
  }

  async bulkUpdate(updates: Array<{ id: User['id']; data: Partial<User> }>): Promise<ServiceResponse<User[]>> {
    // Return dummy updated users
    const now = new Date();
    const users = updates.map((u, i) => ({
      ...u.data,
      id: u.id,
      createdAt: now,
      updatedAt: now,
      email: u.data.email || '',
      username: u.data.username || '',
      isActive: true,
      role: 'user',
    }));
    return { success: true, data: users };
  }

  async bulkDelete(ids: Array<User['id']>): Promise<ServiceResponse<void>> {
    return { success: true };
  }

  async bulkValidate(data: Array<Partial<User>>): Promise<ServiceResponse<boolean>> {
    // Dummy validation: always true
    return { success: true, data: true };
  }
  // #endregion

  // #region IValidatableService Implementation
  async validateCreate(data: Partial<User>): Promise<ServiceResponse<void>> {
    // TODO: Implement validation logic (zod not available)
    return { data: undefined };
  }

  async validateUpdate(
    id: User['id'],
    data: Partial<User>
  ): Promise<ServiceResponse<void>> {
    // TODO: Implement validation logic (zod not available)
    return { data: undefined };
  }
  // #endregion

  // #region IHookableService Implementation
  beforeCreate(hook: (data: Partial<User>) => Promise<void>): void {
    this.hooks.beforeCreate.push(hook);
  }

  afterCreate(hook: (entity: User) => Promise<void>): void {
    this.hooks.afterCreate.push(hook);
  }

  beforeUpdate(
    hook: (id: User['id'], data: Partial<User>) => Promise<void>
  ): void {
    this.hooks.beforeUpdate.push(hook);
  }

  afterUpdate(hook: (entity: User) => Promise<void>): void {
    this.hooks.afterUpdate.push(hook);
  }

  beforeDelete(hook: (id: User['id']) => Promise<void>): void {
    this.hooks.beforeDelete.push(hook);
  }

  afterDelete(hook: (id: User['id']) => Promise<void>): void {
    this.hooks.afterDelete.push(hook);
  }
  // #endregion

  // #region ITransactionalService Implementation
  async beginTransaction(): Promise<void> {
    // TODO: Implement transaction logic (httpClient/basePath not available)
  }

  async commitTransaction(): Promise<void> {
    // TODO: Implement transaction logic (httpClient/basePath not available)
  }

  async rollbackTransaction(): Promise<void> {
    // TODO: Implement transaction logic (httpClient/basePath not available)
  }

  async withTransaction<R>(fn: () => Promise<R>): Promise<R> {
    // TODO: Implement transaction logic
    return await fn();
  }
  // #endregion

  // #region IAdvancedCacheableService Implementation
  async prefetch(keys: string[]): Promise<void> {
    // TODO: Implement cache prefetch logic (cache/httpClient/basePath not available)
  }

  async warmCache(): Promise<void> {
    // TODO: Implement cache warming logic (cache/httpClient/basePath not available)
  }

  async setCacheTags(key: string, tags: string[]): Promise<void> {
    // TODO: Implement cache tagging logic (cache not available)
  }

  async invalidateByTags(tags: string[]): Promise<void> {
    // TODO: Implement cache invalidation by tags (cache not available)
  }
  // #endregion

  // #region IRateLimitedService Implementation
  setRateLimit(config: {
    windowMs: number;
    maxRequests: number;
    errorMessage?: string;
  }): void {
    this.rateLimit = {
      ...this.rateLimit,
      ...config,
    };
  }

  async checkRateLimit(key: string): Promise<boolean> {
    // TODO: Implement rate limit logic (cache not available)
    return true;
  }

  async getRateLimitStatus(key: string): Promise<{
    remaining: number;
    reset: Date;
  }> {
    // TODO: Implement rate limit status logic (cache not available)
    return { remaining: this.rateLimit.maxRequests, reset: new Date() };
  }
  // #endregion

  // Implement findAll as required by BaseService
  async findAll(params?: Record<string, any>): Promise<{ items: User[]; total: number }> {
    // Placeholder: return empty result
    return { items: [], total: 0 };
  }

  // Implementation of required abstract methods from BaseService
  protected async executeCreate(data: Omit<User, keyof User>): Promise<User> {
    // TODO: Implement actual creation logic
    throw new Error('Not implemented');
  }
  protected async executeUpdate(id: User['id'], data: Partial<User>): Promise<User> {
    // TODO: Implement actual update logic
    throw new Error('Not implemented');
  }
  protected async executeDelete(id: User['id']): Promise<void> {
    // TODO: Implement actual delete logic
    throw new Error('Not implemented');
  }
  protected async executeFindById(id: User['id']): Promise<User | null> {
    // TODO: Implement actual find by id logic
    return null;
  }
  protected async executeFindAll(params?: Record<string, any>): Promise<{ items: User[]; total: number }> {
    // TODO: Implement actual find all logic
    return { items: [], total: 0 };
  }
  protected async executeFindOne(params: Record<string, any>): Promise<User | null> {
    // TODO: Implement actual find one logic
    return null;
  }
  protected async executeValidate(data: Partial<User>): Promise<{ isValid: boolean; errors?: any[] }> {
    // TODO: Implement actual validation logic
    return { isValid: true };
  }
  protected async executeValidateField(field: keyof User, value: any): Promise<{ isValid: boolean; errors?: any[] }> {
    // TODO: Implement actual field validation logic
    return { isValid: true };
  }
} 