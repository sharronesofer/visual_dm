import { BaseService } from '../BaseService';
import { BaseEntity } from '../../interfaces/BaseEntity';
import { Repository, RepositoryResponse } from '../../interfaces/Repository';
import { AppError } from '../../utils/errors';
import { ID, PaginationParams, SortParams, QueryFilters } from '../../types/common';

// Mock entity for testing
interface TestEntity extends BaseEntity {
  name: string;
  value: number;
}

// Mock repository implementation
class MockRepository implements Repository<TestEntity> {
  private entities: TestEntity[] = [];

  async findById(id: ID): Promise<TestEntity | null> {
    return this.entities.find(e => e.id === id) || null;
  }

  async findAll(
    pagination?: PaginationParams,
    sort?: SortParams,
    filters?: QueryFilters
  ): Promise<RepositoryResponse<TestEntity>> {
    let result = [...this.entities];

    // Apply filters if provided
    if (filters) {
      result = result.filter(entity => {
        return Object.entries(filters).every(([key, value]) => {
          return entity[key as keyof TestEntity] === value;
        });
      });
    }

    // Apply sorting if provided
    if (sort) {
      result.sort((a, b) => {
        const aValue = a[sort.field as keyof TestEntity];
        const bValue = b[sort.field as keyof TestEntity];
        if (aValue === undefined || bValue === undefined) return 0;
        return sort.order === 'asc' ? 
          (aValue < bValue ? -1 : 1) : 
          (aValue > bValue ? -1 : 1);
      });
    }

    // Apply pagination
    const { page = 1, limit = 10 } = pagination || {};
    const start = (page - 1) * limit;
    const paginatedData = result.slice(start, start + limit);

    return {
      data: paginatedData,
      total: result.length
    };
  }

  async create(entity: TestEntity): Promise<TestEntity> {
    this.entities.push(entity);
    return entity;
  }

  async update(id: ID, entity: TestEntity): Promise<TestEntity | null> {
    const index = this.entities.findIndex(e => e.id === id);
    if (index === -1) return null;
    this.entities[index] = entity;
    return entity;
  }

  async delete(id: ID): Promise<boolean> {
    const index = this.entities.findIndex(e => e.id === id);
    if (index === -1) return false;
    this.entities.splice(index, 1);
    return true;
  }
}

// Concrete implementation of BaseService for testing
class TestService extends BaseService<TestEntity> {
  constructor(repository: Repository<TestEntity>) {
    super(repository);
  }
}

describe('BaseService', () => {
  let service: TestService;
  let repository: MockRepository;

  beforeEach(() => {
    repository = new MockRepository();
    service = new TestService(repository);
  });

  describe('findById', () => {
    it('should find entity by ID', async () => {
      const entity: TestEntity = {
        id: 1,
        name: 'Test',
        value: 42,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      await repository.create(entity);

      const result = await service.findById(1);
      expect(result).toEqual(entity);
    });

    it('should return null for non-existent ID', async () => {
      const result = await service.findById(999);
      expect(result).toBeNull();
    });

    it('should handle errors', async () => {
      jest.spyOn(repository, 'findById').mockRejectedValue(new Error('DB Error'));
      await expect(service.findById(1)).rejects.toThrow(AppError);
    });
  });

  describe('findAll', () => {
    beforeEach(async () => {
      await repository.create({
        id: 1,
        name: 'First',
        value: 10,
        createdAt: new Date(),
        updatedAt: new Date()
      });
      await repository.create({
        id: 2,
        name: 'Second',
        value: 20,
        createdAt: new Date(),
        updatedAt: new Date()
      });
    });

    it('should return paginated results', async () => {
      const result = await service.findAll({
        pagination: { page: 1, limit: 1 }
      });

      expect(result.data.length).toBe(1);
      expect(result.meta?.total).toBe(2);
      expect(result.meta?.page).toBe(1);
      expect(result.meta?.limit).toBe(1);
    });

    it('should apply sorting', async () => {
      const result = await service.findAll({
        sort: { field: 'value', order: 'desc' }
      });

      expect(result.data[0].value).toBe(20);
    });

    it('should apply filters', async () => {
      const result = await service.findAll({
        filters: { value: 10 }
      });

      expect(result.data.length).toBe(1);
      expect(result.data[0].name).toBe('First');
    });

    it('should handle errors', async () => {
      jest.spyOn(repository, 'findAll').mockRejectedValue(new Error('DB Error'));
      await expect(service.findAll({})).rejects.toThrow(AppError);
    });
  });

  describe('create', () => {
    it('should create new entity', async () => {
      const newEntity = {
        name: 'New',
        value: 30
      };

      const result = await service.create(newEntity);
      expect(result.name).toBe('New');
      expect(result.createdAt).toBeDefined();
      expect(result.updatedAt).toBeDefined();
    });

    it('should handle errors', async () => {
      jest.spyOn(repository, 'create').mockRejectedValue(new Error('DB Error'));
      await expect(service.create({ name: 'Test', value: 1 })).rejects.toThrow(AppError);
    });
  });

  describe('update', () => {
    it('should update existing entity', async () => {
      const entity = await repository.create({
        id: 1,
        name: 'Original',
        value: 10,
        createdAt: new Date(),
        updatedAt: new Date()
      });

      const result = await service.update(1, { ...entity, name: 'Updated' });
      expect(result?.name).toBe('Updated');
      expect(result?.updatedAt).toBeDefined();
      const resultTime = result?.updatedAt?.getTime() ?? 0;
      const entityTime = entity.updatedAt?.getTime() ?? 0;
      expect(resultTime).toBeGreaterThan(entityTime);
    });

    it('should return null for non-existent entity', async () => {
      const result = await service.update(999, { name: 'Updated', value: 1 });
      expect(result).toBeNull();
    });

    it('should handle errors', async () => {
      jest.spyOn(repository, 'update').mockRejectedValue(new Error('DB Error'));
      await expect(service.update(1, { name: 'Test', value: 1 })).rejects.toThrow(AppError);
    });
  });

  describe('delete', () => {
    it('should delete existing entity', async () => {
      await repository.create({
        id: 1,
        name: 'ToDelete',
        value: 10,
        createdAt: new Date(),
        updatedAt: new Date()
      });

      const result = await service.delete(1);
      expect(result).toBe(true);
      expect(await service.findById(1)).toBeNull();
    });

    it('should return false for non-existent entity', async () => {
      const result = await service.delete(999);
      expect(result).toBe(false);
    });

    it('should handle errors', async () => {
      jest.spyOn(repository, 'delete').mockRejectedValue(new Error('DB Error'));
      await expect(service.delete(1)).rejects.toThrow(AppError);
    });
  });

  describe('exists', () => {
    it('should return true for existing entity', async () => {
      await repository.create({
        id: 1,
        name: 'Test',
        value: 10,
        createdAt: new Date(),
        updatedAt: new Date()
      });

      const result = await service.exists(1);
      expect(result).toBe(true);
    });

    it('should return false for non-existent entity', async () => {
      const result = await service.exists(999);
      expect(result).toBe(false);
    });

    it('should handle errors', async () => {
      jest.spyOn(repository, 'findById').mockRejectedValue(new Error('DB Error'));
      await expect(service.exists(1)).rejects.toThrow(AppError);
    });
  });
}); 