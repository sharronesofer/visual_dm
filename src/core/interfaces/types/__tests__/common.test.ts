import { describe, it, expect } from 'vitest';
import type {
  ID,
  UUID,
  Timestamp,
  Nullable,
  Optional,
  ReadOnly,
  BaseEntity,
  PaginationParams,
  PaginatedResponse,
  PaginationMeta,
  SortOrder,
  SortParams,
  FilterOperator,
  FilterCondition,
  QueryParams,
} from '../common';

describe('Common Types', () => {
  describe('ID Type', () => {
    it('should accept string', () => {
      const id: ID = 'abc123';
      expect(typeof id).toBe('string');
    });
  });

  describe('UUID Type', () => {
    it('should be a string', () => {
      const uuid: UUID = '123e4567-e89b-12d3-a456-426614174000';
      expect(typeof uuid).toBe('string');
    });
  });

  describe('Timestamp Type', () => {
    it('should accept number', () => {
      const timestamp: Timestamp = Date.now();
      expect(typeof timestamp).toBe('number');
    });
  });

  describe('Nullable Type', () => {
    it('should allow null value', () => {
      const nullableStr: Nullable<{ value: string }> = { value: null };
      const validStr: Nullable<{ value: string }> = { value: 'test' };
      expect(nullableStr.value === null || typeof nullableStr.value === 'string').toBe(true);
      expect(validStr.value === null || typeof validStr.value === 'string').toBe(true);
    });
  });

  describe('Optional Type', () => {
    it('should allow undefined value', () => {
      const optionalNum: Optional<{ value: number }> = {};
      const validNum: Optional<{ value: number }> = { value: 42 };
      expect('value' in optionalNum === false || typeof optionalNum.value === 'number').toBe(true);
      expect('value' in validNum === false || typeof validNum.value === 'number').toBe(true);
    });
  });

  describe('ReadOnly Type', () => {
    it('should create readonly properties', () => {
      const readOnlyObj: ReadOnly<{ name: string; age: number }> = {
        name: 'John',
        age: 30,
      };
      expect(() => {
        // @ts-expect-error - Cannot assign to 'name' because it is a read-only property
        readOnlyObj.name = 'Jane';
      }).toThrow();
    });
  });

  describe('BaseEntity Interface', () => {
    it('should have required properties', () => {
      const entity: BaseEntity = {
        id: '123',
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      expect(entity).toHaveProperty('id');
      expect(entity).toHaveProperty('createdAt');
      expect(entity).toHaveProperty('updatedAt');
      expect(typeof entity.id).toBe('string');
      expect(typeof entity.createdAt).toBe('number');
      expect(typeof entity.updatedAt).toBe('number');
    });
  });

  describe('Pagination Types', () => {
    it('should validate PaginationParams', () => {
      const params: PaginationParams = {
        page: 1,
        limit: 10,
      };
      expect(params).toHaveProperty('page');
      expect(params).toHaveProperty('limit');
      expect(typeof params.page).toBe('number');
      expect(typeof params.limit).toBe('number');
    });

    it('should validate PaginatedResponse', () => {
      const meta: PaginationMeta = {
        currentPage: 1,
        totalPages: 5,
        totalItems: 50,
        itemsPerPage: 10,
        hasNextPage: true,
        hasPreviousPage: false,
      };

      const response: PaginatedResponse<{ name: string }> = {
        items: [{ name: 'Test' }],
        meta,
      };
      expect(response).toHaveProperty('items');
      expect(response).toHaveProperty('meta');
      expect(Array.isArray(response.items)).toBe(true);
      expect(response.meta).toEqual(meta);
    });
  });

  describe('Query Types', () => {
    it('should validate SortParams', () => {
      const sort: SortParams = {
        field: 'name',
        order: 'asc',
      };
      expect(sort).toHaveProperty('field');
      expect(sort).toHaveProperty('order');
      expect(typeof sort.field).toBe('string');
      expect(['asc', 'desc'] as SortOrder[]).toContain(sort.order);
    });

    it('should validate FilterCondition', () => {
      const filter: FilterCondition<{ name: string }> = {
        field: 'name',
        operator: 'eq',
        value: 'test',
      };
      expect(filter).toHaveProperty('field');
      expect(filter).toHaveProperty('operator');
      expect(filter).toHaveProperty('value');
    });

    it('should validate QueryParams', () => {
      const query: QueryParams<{ name: string }> = {
        pagination: { page: 1, limit: 10 },
        sort: [{ field: 'name', order: 'asc' }],
        filters: [{ field: 'name', operator: 'eq', value: 'test' }],
      };
      expect(query).toHaveProperty('pagination');
      expect(query).toHaveProperty('sort');
      expect(query).toHaveProperty('filters');
    });
  });
}); 