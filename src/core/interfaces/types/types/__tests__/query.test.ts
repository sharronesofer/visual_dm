import {
  PaginationParams,
  SortDirection,
  SortingParams,
  ComparisonOperator,
  FilterCondition,
  LogicalOperator,
  FilterGroup,
  FilteringParams,
  QueryOptions,
  PaginatedResult,
  QueryBuilder,
  QueryUtils,
} from '../query';

// Test entity type
interface User {
  id: string;
  name: string;
  email: string;
  age: number;
  role: 'admin' | 'user';
  createdAt: Date;
}

describe('Query Types', () => {
  describe('PaginationParams', () => {
    it('should allow valid pagination parameters', () => {
      const params: PaginationParams = {
        page: 1,
        limit: 10,
        offset: 0,
      };
      expect(params).toBeDefined();
    });
  });

  describe('SortingParams', () => {
    it('should allow sorting by valid field', () => {
      const sort: SortingParams<User> = {
        field: 'name',
        direction: 'asc',
      };
      expect(sort).toBeDefined();
    });

    it('should not allow sorting by invalid field', () => {
      // @ts-expect-error - invalid field
      const sort: SortingParams<User> = {
        field: 'invalid',
        direction: 'asc',
      };
      expect(sort).toBeDefined();
    });
  });

  describe('FilterCondition', () => {
    it('should create valid filter condition', () => {
      const condition: FilterCondition<User> = {
        field: 'age',
        operator: 'gt',
        value: 18,
      };
      expect(condition).toBeDefined();
    });

    it('should not allow invalid field', () => {
      // @ts-expect-error - invalid field
      const condition: FilterCondition<User> = {
        field: 'invalid',
        operator: 'eq',
        value: 'test',
      };
      expect(condition).toBeDefined();
    });
  });

  describe('FilterGroup', () => {
    it('should create valid filter group', () => {
      const group: FilterGroup<User> = {
        operator: 'and',
        conditions: [
          {
            field: 'age',
            operator: 'gte',
            value: 18,
          },
          {
            field: 'role',
            operator: 'eq',
            value: 'user',
          },
        ],
      };
      expect(group).toBeDefined();
    });

    it('should allow nested groups', () => {
      const group: FilterGroup<User> = {
        operator: 'or',
        conditions: [
          {
            operator: 'and',
            conditions: [
              {
                field: 'age',
                operator: 'gte',
                value: 18,
              },
              {
                field: 'role',
                operator: 'eq',
                value: 'user',
              },
            ],
          },
          {
            field: 'role',
            operator: 'eq',
            value: 'admin',
          },
        ],
      };
      expect(group).toBeDefined();
    });
  });

  describe('QueryOptions', () => {
    it('should create complete query options', () => {
      const options: QueryOptions<User> = {
        page: 1,
        limit: 10,
        sort: {
          field: 'createdAt',
          direction: 'desc',
        },
        filter: {
          group: {
            operator: 'and',
            conditions: [
              {
                field: 'age',
                operator: 'gte',
                value: 18,
              },
              {
                field: 'role',
                operator: 'in',
                value: ['admin', 'user'],
              },
            ],
          },
        },
        include: ['posts', 'comments'],
        select: ['id', 'name', 'email'],
      };
      expect(options).toBeDefined();
    });
  });

  describe('QueryUtils', () => {
    describe('createCondition', () => {
      it('should create a filter condition', () => {
        const condition = QueryUtils.createCondition<User>('age', 'gt', 18);
        expect(condition).toEqual({
          field: 'age',
          operator: 'gt',
          value: 18,
        });
      });
    });

    describe('createGroup', () => {
      it('should create a filter group', () => {
        const conditions = [
          QueryUtils.createCondition<User>('age', 'gte', 18),
          QueryUtils.createCondition<User>('role', 'eq', 'user'),
        ];
        const group = QueryUtils.createGroup<User>('and', conditions);
        expect(group).toEqual({
          operator: 'and',
          conditions,
        });
      });
    });

    describe('createSort', () => {
      it('should create sorting parameters', () => {
        const sort = QueryUtils.createSort<User>('createdAt', 'desc');
        expect(sort).toEqual({
          field: 'createdAt',
          direction: 'desc',
        });
      });

      it('should use default ascending direction', () => {
        const sort = QueryUtils.createSort<User>('name');
        expect(sort).toEqual({
          field: 'name',
          direction: 'asc',
        });
      });
    });

    describe('calculatePagination', () => {
      it('should calculate pagination metadata', () => {
        const result = QueryUtils.calculatePagination(100, 2, 10);
        expect(result).toEqual({
          total: 100,
          page: 2,
          limit: 10,
          totalPages: 10,
          hasMore: true,
          hasNextPage: true,
          hasPrevPage: true,
        });
      });

      it('should handle last page', () => {
        const result = QueryUtils.calculatePagination(100, 10, 10);
        expect(result).toEqual({
          total: 100,
          page: 10,
          limit: 10,
          totalPages: 10,
          hasMore: false,
          hasNextPage: false,
          hasPrevPage: true,
        });
      });

      it('should handle first page', () => {
        const result = QueryUtils.calculatePagination(100, 1, 10);
        expect(result).toEqual({
          total: 100,
          page: 1,
          limit: 10,
          totalPages: 10,
          hasMore: true,
          hasNextPage: true,
          hasPrevPage: false,
        });
      });
    });
  });
});
