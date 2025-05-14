import { BaseEntity } from '../types/entity';
import {
  ServiceResponse,
  ServiceConfig,
  PaginatedResponse,
  ValidationResult,
  QueryParams,
  PaginationParams,
  ID,
  CacheOptions
} from '../types/common';
import { CachedService } from '../services/cached.service';
import { AppError } from '../../../utils/errors';
import { z } from 'zod';

// Test entity interface
interface TestEntity extends BaseEntity {
  name: string;
  value: number;
}

// Test entity schema
const testEntitySchema = z.object({
  name: z.string().min(1),
  value: z.number().min(0)
});

// Test service class
class TestCachedService extends CachedService<TestEntity> {
  private entities: Map<ID, TestEntity> = new Map();
  private nextId = 1;

  constructor(cacheOptions?: CacheOptions) {
    super(cacheOptions);
  }

  // Implement required ICacheableService methods
  clearCache(): void {
    super.clearCache();
  }

  invalidateCache(id: ID): void {
    super.invalidateCache(id);
  }

  setCacheOptions(options: CacheOptions): void {
    super.setCacheOptions(options);
  }

  getCacheOptions(): CacheOptions {
    return super.getCacheOptions();
  }

  async hasCache(key: string): Promise<boolean> {
    return super.hasCache(key);
  }

  async getFromCache<R>(key: string): Promise<R | null> {
    return super.getFromCache<R>(key);
  }

  async setInCache<R>(key: string, value: R, ttl?: number): Promise<void> {
    return super.setInCache(key, value, ttl);
  }

  async removeFromCache(key: string): Promise<void> {
    return super.removeFromCache(key);
  }

  // Implement validation methods
  protected async executeValidate(data: unknown): Promise<ValidationResult> {
    const result = testEntitySchema.safeParse(data);
    if (!result.success) {
      return {
        isValid: false,
        errors: result.error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message
        }))
      };
    }
    return { isValid: true, errors: [] };
  }

  protected async executeValidateField(field: keyof Omit<TestEntity, keyof BaseEntity>, value: unknown): Promise<ValidationResult> {
    const fieldSchema = testEntitySchema.shape[field];
    if (!fieldSchema) {
      return {
        isValid: false,
        errors: [{ field: field.toString(), message: 'Invalid field' }]
      };
    }
    const result = fieldSchema.safeParse(value);
    if (!result.success) {
      return {
        isValid: false,
        errors: result.error.errors.map(error => ({
          field: field.toString(),
          message: error.message
        }))
      };
    }
    return { isValid: true, errors: [] };
  }

  protected async executeCreate(data: Omit<TestEntity, keyof BaseEntity>): Promise<TestEntity> {
    const id = this.nextId++;
    const entity: TestEntity = {
      id,
      createdAt: new Date(),
      updatedAt: new Date(),
      ...data
    };
    this.entities.set(id, entity);
    return entity;
  }

  protected async executeUpdate(id: ID, data: Partial<TestEntity>): Promise<TestEntity> {
    const entity = this.entities.get(id);
    if (!entity) {
      throw new AppError('Entity not found', 404);
    }
    const updatedEntity: TestEntity = {
      ...entity,
      ...data,
      updatedAt: new Date()
    };
    this.entities.set(id, updatedEntity);
    return updatedEntity;
  }

  protected async executeDelete(id: ID): Promise<void> {
    if (!this.entities.has(id)) {
      throw new AppError('Entity not found', 404);
    }
    this.entities.delete(id);
  }

  protected async executeFindById(id: ID): Promise<TestEntity | null> {
    const entity = this.entities.get(id);
    return entity || null;
  }

  protected async executeFindOne(params: QueryParams<TestEntity>): Promise<TestEntity | null> {
    const entities = Array.from(this.entities.values());
    if (params.filter) {
      const filtered = entities.filter(entity => {
        return Object.entries(params.filter as Partial<TestEntity>).every(([key, value]) => {
          const entityValue = entity[key as keyof TestEntity];
          return entityValue === value;
        });
      });
      return filtered[0] || null;
    }
    return entities[0] || null;
  }

  protected async executeFindAll(params?: QueryParams<TestEntity>): Promise<PaginatedResponse<TestEntity>> {
    let entities = Array.from(this.entities.values());

    // Apply filters
    if (params?.filter) {
      entities = entities.filter(entity => {
        return Object.entries(params.filter as Partial<TestEntity>).every(([key, value]) => {
          const entityValue = entity[key as keyof TestEntity];
          return entityValue === value;
        });
      });
    }

    // Apply sorting
    if (params?.sort) {
      const sortEntries = Object.entries(params.sort);
      if (sortEntries.length > 0) {
        const [field, order] = sortEntries[0] as [keyof TestEntity, 'asc' | 'desc'];
        entities.sort((a, b) => {
          const aValue = a[field];
          const bValue = b[field];
          
          if (typeof aValue === 'number' && typeof bValue === 'number') {
            return order === 'desc' ? bValue - aValue : aValue - bValue;
          }
          
          if (typeof aValue === 'string' && typeof bValue === 'string') {
            return order === 'desc' ? 
              bValue.localeCompare(aValue) :
              aValue.localeCompare(bValue);
          }
          
          // Default comparison for other types
          const aStr = String(aValue);
          const bStr = String(bValue);
          return order === 'desc' ? 
            bStr.localeCompare(aStr) :
            aStr.localeCompare(bStr);
        });
      }
    }

    // Apply pagination
    const page = (params as PaginationParams)?.page || 1;
    const limit = (params as PaginationParams)?.limit || 10;
    const start = (page - 1) * limit;
    const end = start + limit;
    const items = entities.slice(start, end);

    return {
      items,
      total: entities.length,
      page,
      limit,
      hasMore: end < entities.length
    };
  }
}

describe('TestCachedService', () => {
  let service: TestCachedService;

  beforeEach(() => {
    service = new TestCachedService({
      ttl: 5, // 5 seconds TTL for testing
      namespace: 'test',
      version: '1.0'
    });
  });

  afterEach(() => {
    service.clearCache();
  });

  describe('cache management', () => {
    it('should set and get cache options', () => {
      const options: CacheOptions = {
        ttl: 10,
        namespace: 'new-test',
        version: '2.0'
      };

      service.setCacheOptions(options);
      const currentOptions = service.getCacheOptions();

      expect(currentOptions).toEqual(options);
    });

    it('should clear cache', async () => {
      // Create and cache an entity
      const createResult = await service.create({ name: 'Test', value: 100 });
      expect(createResult.success).toBe(true);
      const findResult = await service.findById(createResult.data!.id);
      expect(findResult.success).toBe(true);

      // Clear cache
      service.clearCache();

      // Verify cache is cleared by checking if a new DB call is made
      const spy = jest.spyOn(service as any, 'executeFindById');
      await service.findById(createResult.data!.id);
      expect(spy).toHaveBeenCalled();
    });

    it('should invalidate cache for specific entity', async () => {
      // Create and cache two entities
      const entity1 = await service.create({ name: 'Test 1', value: 100 });
      const entity2 = await service.create({ name: 'Test 2', value: 200 });
      expect(entity1.success).toBe(true);
      expect(entity2.success).toBe(true);

      // Cache both entities
      await service.findById(entity1.data!.id);
      await service.findById(entity2.data!.id);

      // Invalidate cache for entity1
      service.invalidateCache(entity1.data!.id);

      // Verify entity1 cache is invalidated but entity2 cache remains
      const spy = jest.spyOn(service as any, 'executeFindById');
      
      await service.findById(entity1.data!.id);
      expect(spy).toHaveBeenCalledWith(entity1.data!.id);

      await service.findById(entity2.data!.id);
      expect(spy).toHaveBeenCalledTimes(1); // Only called for entity1
    });
  });

  describe('cached operations', () => {
    describe('findById', () => {
      it('should cache findById results', async () => {
        // Create an entity
        const createResult = await service.create({ name: 'Test', value: 100 });
        expect(createResult.success).toBe(true);
        const id = createResult.data!.id;

        // First call should hit the database
        const spy = jest.spyOn(service as any, 'executeFindById');
        const findResult = await service.findById(id);
        expect(findResult.success).toBe(true);
        expect(spy).toHaveBeenCalledTimes(1);

        // Second call should use cache
        const cachedResult = await service.findById(id);
        expect(cachedResult.success).toBe(true);
        expect(spy).toHaveBeenCalledTimes(1); // Still 1, indicating cache hit
      });

      it('should respect cache TTL', async () => {
        // Create service with 1 second TTL
        const shortTTLService = new TestCachedService({ ttl: 1 });
        
        // Create and cache an entity
        const entity = await shortTTLService.create({ name: 'Test', value: 100 });
        expect(entity.success).toBe(true);
        const spy = jest.spyOn(shortTTLService as any, 'executeFindById');
        
        // First call - cache it
        const findResult = await shortTTLService.findById(entity.data!.id);
        expect(findResult.success).toBe(true);
        expect(spy).toHaveBeenCalledTimes(1);

        // Wait for TTL to expire
        await new Promise(resolve => setTimeout(resolve, 1100));

        // Should hit database again after TTL expires
        const expiredResult = await shortTTLService.findById(entity.data!.id);
        expect(expiredResult.success).toBe(true);
        expect(spy).toHaveBeenCalledTimes(2);
      });
    });

    describe('findAll', () => {
      it('should cache findAll results with query parameters', async () => {
        // Create test data
        const create1 = await service.create({ name: 'Test 1', value: 100 });
        const create2 = await service.create({ name: 'Test 2', value: 200 });
        expect(create1.success).toBe(true);
        expect(create2.success).toBe(true);

        const params: QueryParams<TestEntity> & PaginationParams = {
          filter: { value: 200 },
          sort: { name: 'asc' },
          page: 1,
          limit: 10
        };

        // First call should hit the database
        const spy = jest.spyOn(service as any, 'executeFindAll');
        const findResult = await service.findAll(params);
        expect(findResult.success).toBe(true);
        expect(spy).toHaveBeenCalledTimes(1);

        // Second call with same parameters should use cache
        const cachedResult = await service.findAll(params);
        expect(cachedResult.success).toBe(true);
        expect(spy).toHaveBeenCalledTimes(1); // Still 1, indicating cache hit

        // Different parameters should hit database again
        const newParams: QueryParams<TestEntity> & PaginationParams = {
          ...params,
          page: 2
        };
        const newResult = await service.findAll(newParams);
        expect(newResult.success).toBe(true);
        expect(spy).toHaveBeenCalledTimes(2);
      });
    });

    describe('findOne', () => {
      it('should cache findOne results', async () => {
        // Create test data
        const create1 = await service.create({ name: 'Test 1', value: 100 });
        const create2 = await service.create({ name: 'Test 2', value: 200 });
        expect(create1.success).toBe(true);
        expect(create2.success).toBe(true);

        const params = {
          filter: { value: 200 }
        };

        // First call should hit the database
        const spy = jest.spyOn(service as any, 'executeFindOne');
        const findResult = await service.findOne(params);
        expect(findResult.success).toBe(true);
        expect(spy).toHaveBeenCalledTimes(1);

        // Second call with same parameters should use cache
        const cachedResult = await service.findOne(params);
        expect(cachedResult.success).toBe(true);
        expect(spy).toHaveBeenCalledTimes(1); // Still 1, indicating cache hit
      });
    });

    describe('cache invalidation on write operations', () => {
      it('should invalidate cache on create', async () => {
        // Create and cache initial data
        const entity = await service.create({ name: 'Test 1', value: 100 });
        expect(entity.success).toBe(true);
        const findAllResult = await service.findAll();
        expect(findAllResult.success).toBe(true);
        
        const spy = jest.spyOn(service as any, 'executeFindAll');
        
        // Create new entity should invalidate findAll cache
        const newEntity = await service.create({ name: 'Test 2', value: 200 });
        expect(newEntity.success).toBe(true);
        
        // Subsequent findAll should hit database
        const newFindResult = await service.findAll();
        expect(newFindResult.success).toBe(true);
        expect(spy).toHaveBeenCalled();
      });

      it('should invalidate cache on update', async () => {
        // Create and cache an entity
        const entity = await service.create({ name: 'Test', value: 100 });
        expect(entity.success).toBe(true);
        const findResult = await service.findById(entity.data!.id);
        expect(findResult.success).toBe(true);
        
        const spy = jest.spyOn(service as any, 'executeFindById');
        
        // Update should invalidate cache
        const updateResult = await service.update(entity.data!.id, { value: 200 });
        expect(updateResult.success).toBe(true);
        
        // Subsequent findById should hit database
        const newFindResult = await service.findById(entity.data!.id);
        expect(newFindResult.success).toBe(true);
        expect(spy).toHaveBeenCalled();
      });

      it('should invalidate cache on delete', async () => {
        // Create and cache an entity
        const entity = await service.create({ name: 'Test', value: 100 });
        expect(entity.success).toBe(true);
        const findAllResult = await service.findAll();
        expect(findAllResult.success).toBe(true);
        
        const spy = jest.spyOn(service as any, 'executeFindAll');
        
        // Delete should invalidate cache
        const deleteResult = await service.delete(entity.data!.id);
        expect(deleteResult.success).toBe(true);
        
        // Subsequent findAll should hit database
        const newFindResult = await service.findAll();
        expect(newFindResult.success).toBe(true);
        expect(spy).toHaveBeenCalled();
      });
    });
  });
}); 