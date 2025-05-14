import { BaseService } from '../base';
import {
  ApiResponse,
  ValidationResult,
  ServiceConfig,
  ValidationError,
} from '../../types/common';
import { ApplicationError } from '../../errors';
import { logger } from '../../utils/logger';

// Mock logger
jest.mock('../../utils/logger', () => ({
  logger: {
    error: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
  },
}));

// Test entity type
interface TestEntity {
  id: string;
  name: string;
  value: number;
}

// Test DTO types
interface CreateTestDTO {
  name: string;
  value: number;
}

interface UpdateTestDTO extends Partial<CreateTestDTO> {}

// Concrete implementation for testing
class TestService extends BaseService<
  TestEntity,
  CreateTestDTO,
  UpdateTestDTO
> {
  private entities: Map<string, TestEntity> = new Map();

  protected async executeCreate(
    data: CreateTestDTO
  ): Promise<ApiResponse<TestEntity>> {
    const entity: TestEntity = {
      id: Math.random().toString(36).substring(7),
      ...data,
    };
    this.entities.set(entity.id, entity);
    return this.createSuccessResponse(entity);
  }

  protected async executeUpdate(
    id: string,
    data: UpdateTestDTO
  ): Promise<ApiResponse<TestEntity>> {
    const entity = this.entities.get(id);
    if (!entity) {
      return this.createErrorResponse(
        new ApplicationError('NOT_FOUND', `Entity with id ${id} not found`)
      );
    }
    const updated = { ...entity, ...data };
    this.entities.set(id, updated);
    return this.createSuccessResponse(updated);
  }

  protected async executeDelete(id: string): Promise<ApiResponse<void>> {
    if (!this.entities.has(id)) {
      return this.createErrorResponse(
        new ApplicationError('NOT_FOUND', `Entity with id ${id} not found`)
      );
    }
    this.entities.delete(id);
    return this.createSuccessResponse(undefined);
  }

  async getById(id: string): Promise<ApiResponse<TestEntity>> {
    const entity = this.entities.get(id);
    if (!entity) {
      return this.createErrorResponse(
        new ApplicationError('NOT_FOUND', `Entity with id ${id} not found`)
      );
    }
    return this.createSuccessResponse(entity);
  }

  async getAll(): Promise<ApiResponse<TestEntity[]>> {
    return this.createSuccessResponse(Array.from(this.entities.values()));
  }

  async list(): Promise<ApiResponse<TestEntity[]>> {
    return this.getAll();
  }

  // Override validateField for testing
  async validateField(field: string, value: any): Promise<ValidationResult> {
    const errors: ValidationError[] = [];

    switch (field) {
      case 'name':
        if (typeof value !== 'string' || value.length < 3) {
          errors.push({
            field: 'name',
            code: 'INVALID_NAME',
            message: 'Name must be at least 3 characters long',
          });
        }
        break;
      case 'value':
        if (typeof value !== 'number' || value < 0) {
          errors.push({
            field: 'value',
            code: 'INVALID_VALUE',
            message: 'Value must be a positive number',
          });
        }
        break;
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }
}

describe('BaseService', () => {
  let service: TestService;
  let mockBeforeCreate: jest.Mock;
  let mockAfterCreate: jest.Mock;
  let mockBeforeUpdate: jest.Mock;
  let mockAfterUpdate: jest.Mock;
  let mockBeforeDelete: jest.Mock;
  let mockAfterDelete: jest.Mock;

  beforeEach(() => {
    mockBeforeCreate = jest.fn(data => data);
    mockAfterCreate = jest.fn(entity => entity);
    mockBeforeUpdate = jest.fn((id, data) => data);
    mockAfterUpdate = jest.fn(entity => entity);
    mockBeforeDelete = jest.fn();
    mockAfterDelete = jest.fn();

    service = new TestService(undefined, {
      beforeCreate: mockBeforeCreate,
      afterCreate: mockAfterCreate,
      beforeUpdate: mockBeforeUpdate,
      afterUpdate: mockAfterUpdate,
      beforeDelete: mockBeforeDelete,
      afterDelete: mockAfterDelete,
    });

    // Clear mock calls
    (logger.error as jest.Mock).mockClear();
  });

  describe('Configuration', () => {
    it('should initialize with default config', () => {
      const config = service.getConfig();
      expect(config).toEqual({
        baseURL: 'http://localhost:3000',
        timeout: 5000,
        headers: {},
      });
    });

    it('should update config', async () => {
      const newConfig: Partial<ServiceConfig> = {
        baseURL: 'http://api.example.com',
        timeout: 10000,
      };
      await service.setConfig(newConfig);
      const config = service.getConfig();
      expect(config).toEqual({
        baseURL: 'http://api.example.com',
        timeout: 10000,
        headers: {},
      });
    });
  });

  describe('CRUD Operations with Hooks', () => {
    it('should execute hooks during create', async () => {
      const data: CreateTestDTO = { name: 'Test', value: 42 };
      const response = await service.create(data);

      expect(response.success).toBe(true);
      expect(response.data).toMatchObject(data);
      expect(response.data.id).toBeDefined();

      expect(mockBeforeCreate).toHaveBeenCalledWith(data);
      expect(mockAfterCreate).toHaveBeenCalledWith(response.data);
    });

    it('should execute hooks during update', async () => {
      const data: CreateTestDTO = { name: 'Test', value: 42 };
      const created = await service.create(data);
      const updateData: UpdateTestDTO = { name: 'Updated' };
      const response = await service.update(created.data.id, updateData);

      expect(response.success).toBe(true);
      expect(response.data).toMatchObject({
        id: created.data.id,
        name: 'Updated',
        value: 42,
      });

      expect(mockBeforeUpdate).toHaveBeenCalledWith(
        created.data.id,
        updateData
      );
      expect(mockAfterUpdate).toHaveBeenCalledWith(response.data);
    });

    it('should execute hooks during delete', async () => {
      const data: CreateTestDTO = { name: 'Test', value: 42 };
      const created = await service.create(data);
      const response = await service.delete(created.data.id);

      expect(response.success).toBe(true);
      expect(mockBeforeDelete).toHaveBeenCalledWith(created.data.id);
      expect(mockAfterDelete).toHaveBeenCalledWith(created.data.id);
    });
  });

  describe('Validation', () => {
    it('should validate create data', async () => {
      const data: CreateTestDTO = { name: 'ab', value: -1 };
      const response = await service.create(data);

      expect(response.success).toBe(false);
      expect(response.error).toBeDefined();
      expect(response.error?.message).toBe('Validation failed');
      expect(logger.error).toHaveBeenCalled();
    });

    it('should validate update data', async () => {
      const data: UpdateTestDTO = { name: 'ab' };
      const response = await service.update('123', data);

      expect(response.success).toBe(false);
      expect(response.error).toBeDefined();
      expect(response.error?.message).toBe('Validation failed');
      expect(logger.error).toHaveBeenCalled();
    });

    it('should validate individual fields', async () => {
      const result = await service.validateField('name', 'ab');
      expect(result.isValid).toBe(false);
      expect(result.errors[0].code).toBe('INVALID_NAME');
    });
  });

  describe('Error Handling', () => {
    it('should handle not found error', async () => {
      const response = await service.getById('non-existent');
      expect(response.success).toBe(false);
      expect(response.error).toBeDefined();
      expect(response.error?.code).toBe('NOT_FOUND');
      expect(logger.error).not.toHaveBeenCalled();
    });

    it('should handle validation error', async () => {
      const data: CreateTestDTO = { name: 'ab', value: -1 };
      const result = await service.validate(data);
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(2);
    });

    it('should handle unexpected errors', async () => {
      const error = new Error('Unexpected error');
      jest.spyOn(service as any, 'executeCreate').mockRejectedValueOnce(error);

      const data: CreateTestDTO = { name: 'Test', value: 42 };
      const response = await service.create(data);

      expect(response.success).toBe(false);
      expect(response.error).toBeDefined();
      expect(response.error?.message).toBe('Unexpected error');
      expect(response.error?.code).toBe('UNKNOWN_ERROR');
      expect(logger.error).toHaveBeenCalledWith(
        'Create operation failed',
        error,
        { data }
      );
    });
  });

  describe('Request Cancellation', () => {
    it('should create new cancellation token after canceling requests', () => {
      const initialToken = service['cancellationToken'];
      service.cancelRequests();
      const newToken = service['cancellationToken'];
      expect(newToken).not.toBe(initialToken);
    });
  });
});
