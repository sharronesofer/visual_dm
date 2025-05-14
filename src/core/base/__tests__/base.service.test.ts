import { BaseEntity } from '../types/entity';
import {
  ServiceResponse,
  ServiceConfig,
  PaginatedResponse,
  ValidationResult,
  QueryParams,
  PaginationParams,
  ID
} from '../types/common';
import { ValidatableService } from '../services';
import { AppError } from '../../../utils/errors';
import { z } from 'zod';

// Test entity interface
interface TestEntity extends BaseEntity {
  name: string;
  value: number;
}

// Test validation schema
const testValidationSchema = z.object({
  name: z.string().min(1, 'Name is required and must be a string'),
  value: z.number().min(0, 'Value must be a non-negative number')
});

type TestValidationSchema = z.infer<typeof testValidationSchema>;

// Test service class
class TestService extends ValidatableService<TestEntity> {
  private entities: Map<ID, TestEntity> = new Map();
  private nextId = 1;

  constructor() {
    super();
    this.initializeValidationRules();
  }

  private initializeValidationRules() {
    // Add validation rules for name
    this.addValidationRule('name', {
      required: true,
      minLength: 1
    });

    // Add validation rules for value
    this.addValidationRule('value', {
      required: true,
      min: 0
    });
  }

  protected async applyValidationRule(
    field: keyof TestEntity,
    value: any,
    ruleName: string,
    ruleConfig: any
  ): Promise<boolean> {
    switch (ruleName) {
      case 'required':
        return value !== undefined && value !== null && value !== '';
      case 'minLength':
        return typeof value === 'string' && value.length >= ruleConfig;
      case 'min':
        return typeof value === 'number' && value >= ruleConfig;
      default:
        return true;
    }
  }

  protected getValidationMessage(
    field: keyof TestEntity,
    ruleName: string,
    ruleConfig: any
  ): string {
    switch (ruleName) {
      case 'required':
        return `${String(field)} is required`;
      case 'minLength':
        return `${String(field)} must be at least ${ruleConfig} characters long`;
      case 'min':
        return `${String(field)} must be at least ${ruleConfig}`;
      default:
        return `Invalid ${String(field)}`;
    }
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

  protected async executeFindById(id: ID): Promise<TestEntity> {
    const entity = this.entities.get(id);
    if (!entity) {
      throw new AppError('Entity not found', 404);
    }
    return entity;
  }

  /**
   * Execute find one operation
   */
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

  /**
   * Execute find all operation
   */
  protected async executeFindAll(params?: QueryParams<TestEntity> & PaginationParams): Promise<PaginatedResponse<TestEntity>> {
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

    // Apply search (case-insensitive substring match on name)
    if (params?.search) {
      const searchStr = params.search.toLowerCase();
      entities = entities.filter(entity =>
        entity.name.toLowerCase().includes(searchStr)
      );
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
    const page = params?.page || 1;
    const limit = params?.limit || 10;
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

  /**
   * Execute validate operation
   */
  protected async executeValidate(data: Partial<TestEntity>): Promise<ValidationResult> {
    try {
      await testValidationSchema.parseAsync(data);
      return { isValid: true, errors: [] };
    } catch (error) {
      if (error instanceof z.ZodError) {
        return {
          isValid: false,
          errors: error.errors.map(err => ({
            field: err.path.join('.'),
            message: err.message,
            code: 'VALIDATION_ERROR'
          }))
        };
      }
      return {
        isValid: false,
        errors: [{
          field: '*',
          message: 'Validation failed unexpectedly',
          code: 'VALIDATION_ERROR'
        }]
      };
    }
  }

  /**
   * Execute validate field operation
   */
  protected async executeValidateField(field: keyof TestEntity, value: any): Promise<ValidationResult> {
    try {
      const fieldSchema = testValidationSchema.shape[field as keyof TestValidationSchema];
      if (!fieldSchema) {
        return {
          isValid: false,
          errors: [{
            field: String(field),
            message: 'Field does not exist in validation schema',
            code: 'VALIDATION_ERROR'
          }]
        };
      }

      await fieldSchema.parseAsync(value);
      return { isValid: true, errors: [] };
    } catch (error) {
      if (error instanceof z.ZodError) {
        return {
          isValid: false,
          errors: error.errors.map(err => ({
            field: String(field),
            message: err.message,
            code: 'VALIDATION_ERROR'
          }))
        };
      }
      return {
        isValid: false,
        errors: [{
          field: String(field),
          message: 'Field validation failed unexpectedly',
          code: 'VALIDATION_ERROR'
        }]
      };
    }
  }

  /**
   * Get default filterable fields
   */
  protected getDefaultFilterableFields(): Array<keyof TestEntity> {
    return ['name', 'value', 'createdAt', 'updatedAt'];
  }

  /**
   * Get default sortable fields
   */
  protected getDefaultSortableFields(): Array<keyof TestEntity> {
    return ['name', 'value', 'createdAt', 'updatedAt'];
  }

  /**
   * Check if entity matches query parameters
   */
  private matchesParams(entity: TestEntity, params: QueryParams<TestEntity>): boolean {
    if (!params.filter) {
      return true;
    }

    return Object.entries(params.filter).every(([key, value]) => {
      const entityValue = entity[key as keyof TestEntity];
      return entityValue === value;
    });
  }

  // Bulk operations
  async createMany(data: Array<Omit<TestEntity, keyof BaseEntity>>): Promise<ServiceResponse<TestEntity[]>> {
    try {
      // Validate all entities first
      const validationResults = await Promise.all(
        data.map(item => this.validateCreate(item))
      );

      const validationErrors = validationResults.flatMap((result, index) => 
        result.isValid ? [] : result.errors.map(error => ({
          ...error,
          index,
          data: data[index]
        }))
      );

      if (validationErrors.length > 0) {
        throw new AppError('Validation failed', 400);
      }

      // Create all entities
      const entities = await Promise.all(
        data.map(item => this.executeCreate(item))
      );

      return {
        success: true,
        data: entities
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error : new Error('Unknown error')
      };
    }
  }

  async updateMany(updates: Array<{ id: ID; data: Partial<TestEntity> }>): Promise<ServiceResponse<TestEntity[]>> {
    try {
      // Check if all entities exist
      const entities = await Promise.all(
        updates.map(async ({ id }) => {
          const entity = await this.executeFindById(id).catch(() => null);
          if (!entity) {
            throw new AppError(`Entity with id ${id} not found`, 404);
          }
          return entity;
        })
      );

      // Validate all updates
      const validationResults = await Promise.all(
        updates.map(({ id, data }) => this.validateUpdate(id, data))
      );

      const validationErrors = validationResults.flatMap((result, index) => 
        result.isValid ? [] : result.errors.map(error => ({
          ...error,
          index,
          data: updates[index].data
        }))
      );

      if (validationErrors.length > 0) {
        throw new AppError('Validation failed', 400);
      }

      // Update all entities
      const updatedEntities = await Promise.all(
        updates.map(({ id, data }) => this.executeUpdate(id, data))
      );

      return {
        success: true,
        data: updatedEntities
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error : new Error('Unknown error')
      };
    }
  }

  async deleteMany(ids: ID[]): Promise<ServiceResponse<void>> {
    try {
      // Check if all entities exist
      await Promise.all(
        ids.map(async id => {
          const entity = await this.executeFindById(id).catch(() => null);
          if (!entity) {
            throw new AppError(`Entity with id ${id} not found`, 404);
          }
          return entity;
        })
      );

      // Delete all entities
      await Promise.all(
        ids.map(id => this.executeDelete(id))
      );

      return {
        success: true
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error : new Error('Unknown error')
      };
    }
  }
}

describe('TestService', () => {
  let service: TestService;

  beforeEach(() => {
    service = new TestService();
  });

  describe('validation', () => {
    it('should validate required fields', async () => {
      const result = await service.validateCreate({
        name: '',
        value: 100
      });

      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(2);
      expect(result.errors.map(e => e.field)).toContain('name');
      expect(result.errors.map(e => e.message)).toEqual(
        expect.arrayContaining([
          expect.stringMatching(/required/i),
          expect.stringMatching(/at least 1/i)
        ])
      );
    });

    it('should validate minimum value', async () => {
      const result = await service.validateCreate({
        name: 'Test',
        value: -1
      });

      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].field).toBe('value');
      expect(result.errors[0].message).toBe('value must be at least 0');
    });

    it('should pass validation for valid data', async () => {
      const result = await service.validateCreate({
        name: 'Test',
        value: 100
      });

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should validate partial updates', async () => {
      const result = await service.validateUpdate(1, {
        name: ''
      });

      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(2);
      expect(result.errors.map(e => e.field)).toContain('name');
      expect(result.errors.map(e => e.message)).toEqual(
        expect.arrayContaining([
          expect.stringMatching(/required/i),
          expect.stringMatching(/at least 1/i)
        ])
      );
    });
  });

  describe('create', () => {
    it('should create a new entity', async () => {
      const data = { name: 'Test', value: 100 };
      const result = await service.create(data);

      expect(result.success).toBe(true);
      expect(result.data).toMatchObject({
        ...data,
        id: expect.any(Number),
        createdAt: expect.any(Date),
        updatedAt: expect.any(Date)
      });
    });

    it('should validate data before creation', async () => {
      const data = { name: '', value: -1 };
      const result = await service.create(data);

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.error?.message).toContain('Validation failed');
    });
  });

  describe('update', () => {
    let entityId: ID;

    beforeEach(async () => {
      const result = await service.create({ name: 'Test', value: 100 });
      entityId = result.data!.id;
    });

    it('should update an existing entity', async () => {
      const data = { name: 'Updated', value: 200 };
      const result = await service.update(entityId, data);

      expect(result.success).toBe(true);
      expect(result.data).toMatchObject({
        ...data,
        id: entityId
      });
    });

    it('should validate data before update', async () => {
      const data = { name: '', value: -1 };
      const result = await service.update(entityId, data);

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.error?.message).toContain('Validation failed');
    });

    it('should handle non-existent entity', async () => {
      const result = await service.update(999, { name: 'Updated' });

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.error?.message).toContain('Validation failed');
    });
  });

  describe('delete', () => {
    let entityId: ID;

    beforeEach(async () => {
      const result = await service.create({ name: 'Test', value: 100 });
      entityId = result.data!.id;
    });

    it('should delete an existing entity', async () => {
      const result = await service.delete(entityId);
      expect(result.success).toBe(true);

      const findResult = await service.findById(entityId);
      expect(findResult.success).toBe(false);
    });
  });

  describe('findById', () => {
    let entityId: ID;

    beforeEach(async () => {
      const result = await service.create({ name: 'Test', value: 100 });
      entityId = result.data!.id;
    });

    it('should find an entity by id', async () => {
      const result = await service.findById(entityId);

      expect(result.success).toBe(true);
      expect(result.data).toMatchObject({
        id: entityId,
        name: 'Test',
        value: 100
      });
    });
  });

  describe('findAll', () => {
    beforeEach(async () => {
      await service.create({ name: 'Test 1', value: 100 });
      await service.create({ name: 'Test 2', value: 200 });
      await service.create({ name: 'Test 3', value: 300 });
    });

    it('should return all entities with pagination', async () => {
      const result = await service.findAll({
        page: 1,
        limit: 2
      } as QueryParams<TestEntity> & PaginationParams);

      expect(result.success).toBe(true);
      expect(result.data?.items).toHaveLength(2);
      expect(result.data?.total).toBe(3);
      expect(result.data?.page).toBe(1);
      expect(result.data?.limit).toBe(2);
      expect(result.data?.hasMore).toBe(true);
    });

    it('should filter entities', async () => {
      const result = await service.findAll({
        filter: { value: 200 }
      } as QueryParams<TestEntity> & PaginationParams);

      expect(result.success).toBe(true);
      expect(result.data?.items).toHaveLength(1);
      expect(result.data?.items[0].value).toBe(200);
    });

    it('should sort entities', async () => {
      const result = await service.findAll({
        sort: { value: 'desc' }
      } as QueryParams<TestEntity> & PaginationParams);

      expect(result.success).toBe(true);
      expect(result.data?.items[0].value).toBe(300);
      expect(result.data?.items[2].value).toBe(100);
    });

    it('should handle empty filter', async () => {
      const result = await service.findAll({
        filter: {}
      } as QueryParams<TestEntity> & PaginationParams);

      expect(result.success).toBe(true);
      expect(result.data?.items).toHaveLength(3);
    });

    it('should handle non-existent filter field', async () => {
      const result = await service.findAll({
        filter: { nonexistent: 'value' }
      } as QueryParams<TestEntity> & PaginationParams);

      expect(result.success).toBe(true);
      expect(result.data?.items).toHaveLength(0);
    });

    it('should handle invalid sort field', async () => {
      const result = await service.findAll({
        sort: { nonexistent: 'desc' }
      } as QueryParams<TestEntity> & PaginationParams);

      expect(result.success).toBe(true);
      expect(result.data?.items).toHaveLength(3);
    });

    it('should handle search parameter', async () => {
      const result = await service.findAll({
        search: 'Test 2'
      } as QueryParams<TestEntity> & PaginationParams);

      expect(result.success).toBe(true);
      expect(result.data?.items).toHaveLength(1);
      expect(result.data?.items[0].name).toBe('Test 2');
    });

    it('should handle combined filter, sort, and search', async () => {
      const result = await service.findAll({
        filter: { value: 200 },
        sort: { name: 'asc' },
        search: 'Test'
      } as QueryParams<TestEntity> & PaginationParams);

      expect(result.success).toBe(true);
      expect(result.data?.items).toHaveLength(1);
      expect(result.data?.items[0].value).toBe(200);
    });
  });

  describe('bulk operations', () => {
    describe('createMany', () => {
      it('should create multiple entities', async () => {
        const entities = [
          { name: 'Bulk 1', value: 100 },
          { name: 'Bulk 2', value: 200 },
          { name: 'Bulk 3', value: 300 }
        ];

        const result = await service.createMany(entities);

        expect(result.success).toBe(true);
        expect(result.data).toHaveLength(3);
        expect(result.data?.map(e => e.name)).toEqual(['Bulk 1', 'Bulk 2', 'Bulk 3']);
      });

      it('should validate all entities before creation', async () => {
        const entities = [
          { name: 'Valid', value: 100 },
          { name: '', value: -1 },
          { name: 'Also Invalid', value: -2 }
        ];

        const result = await service.createMany(entities);

        expect(result.success).toBe(false);
        expect(result.error).toBeDefined();
        expect(result.error?.message).toContain('Validation failed');
      });
    });

    describe('updateMany', () => {
      let entityIds: ID[];

      beforeEach(async () => {
        const results = await Promise.all([
          service.create({ name: 'Test 1', value: 100 }),
          service.create({ name: 'Test 2', value: 200 }),
          service.create({ name: 'Test 3', value: 300 })
        ]);
        entityIds = results.map(r => r.data!.id);
      });

      it('should update multiple entities', async () => {
        const updates = entityIds.map(id => ({
          id,
          data: { value: 1000 }
        }));

        const result = await service.updateMany(updates);

        expect(result.success).toBe(true);
        expect(result.data).toHaveLength(3);
        expect(result.data?.every(e => e.value === 1000)).toBe(true);
      });

      it('should validate all updates before applying', async () => {
        const updates = entityIds.map(id => ({
          id,
          data: { value: -1 }
        }));

        const result = await service.updateMany(updates);

        expect(result.success).toBe(false);
        expect(result.error).toBeDefined();
        expect(result.error?.message).toContain('Validation failed');
      });

      it('should handle non-existent entities', async () => {
        const updates = [
          { id: 999, data: { value: 1000 } },
          { id: entityIds[0], data: { value: 1000 } }
        ];

        const result = await service.updateMany(updates);

        expect(result.success).toBe(false);
        expect(result.error).toBeDefined();
        expect(result.error?.message).toContain('not found');
      });
    });

    describe('deleteMany', () => {
      let entityIds: ID[];

      beforeEach(async () => {
        const results = await Promise.all([
          service.create({ name: 'Test 1', value: 100 }),
          service.create({ name: 'Test 2', value: 200 }),
          service.create({ name: 'Test 3', value: 300 })
        ]);
        entityIds = results.map(r => r.data!.id);
      });

      it('should delete multiple entities', async () => {
        const result = await service.deleteMany(entityIds);

        expect(result.success).toBe(true);
        
        // Verify entities are deleted
        const findResult = await service.findAll();
        expect(findResult.data?.items).toHaveLength(0);
      });

      it('should handle non-existent entities', async () => {
        const result = await service.deleteMany([...entityIds, 999]);

        expect(result.success).toBe(false);
        expect(result.error).toBeDefined();
        expect(result.error?.message).toContain('not found');
      });
    });
  });

  describe('findOne', () => {
    beforeEach(async () => {
      await service.create({ name: 'Test 1', value: 100 });
      await service.create({ name: 'Test 2', value: 200 });
    });

    it('should find one entity matching the filter', async () => {
      const result = await service.findOne({
        filter: { value: 200 }
      });

      expect(result.success).toBe(true);
      expect(result.data?.value).toBe(200);
    });
  });
});

describe('Boundary and Large Dataset Tests', () => {
  let service: TestService;

  beforeEach(() => {
    service = new TestService();
  });

  it('should allow maximum allowed value for "value"', async () => {
    const max = Number.MAX_SAFE_INTEGER;
    const result = await service.create({ name: 'Max', value: max });
    expect(result.success).toBe(true);
    expect(result.data?.value).toBe(max);
  });

  it('should handle pagination at the last page', async () => {
    for (let i = 0; i < 15; i++) {
      await service.create({ name: `Entity ${i + 1}`, value: i });
    }
    const result = await service.findAll({ page: 2, limit: 10 } as any);
    expect(result.success).toBe(true);
    expect(result.data?.items.length).toBe(5);
    expect(result.data?.page).toBe(2);
    expect(result.data?.hasMore).toBe(false);
  });

  it('should handle large datasets (100+ entities) with pagination', async () => {
    for (let i = 0; i < 120; i++) {
      await service.create({ name: `Entity ${i + 1}`, value: i });
    }
    const result = await service.findAll({ page: 5, limit: 25 } as any);
    expect(result.success).toBe(true);
    expect(result.data?.items.length).toBe(20);
    expect(result.data?.total).toBe(120);
    expect(result.data?.page).toBe(5);
    expect(result.data?.hasMore).toBe(false);
  });

  // Placeholder for event handling (if implemented)
  it.skip('should emit events on create/update/delete', () => {
    // Implement if event system is present in ValidatableService
  });

  // Placeholder for caching (if implemented)
  it.skip('should hit/miss cache appropriately', () => {
    // Implement if caching is present in ValidatableService
  });
}); 