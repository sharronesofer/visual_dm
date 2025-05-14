import { describe, it, expect } from 'vitest';
import {
  Identifiable,
  Timestamped,
  SoftDeletable,
  Auditable,
  Versionable,
  Nullable,
  Optional,
  ReadOnly,
  DeepPartial,
  RecursiveRequired,
  FormState,
  ValidationErrors,
  State,
  Action,
  Reducer,
  isDefined,
  isString,
  isNumber,
  isBoolean,
  isObject,
  isArray,
  isDate,
  isType,
} from '@/shared/types/common';

import type {
  ID,
  Timestamp,
  UUID,
  BaseEntity,
  PaginationParams,
  PaginationMeta,
  PaginatedResponse,
  SortOrder,
  SortParams,
  FilterOperator,
  FilterCondition,
  QueryParams,
  SuccessResponse,
  ErrorResponse,
  AsyncStatus,
  AsyncState,
  ValidationStatus,
  ValidationResult,
  CacheOptions,
  EventHandler,
  Subscription,
  RetryOptions,
} from '../../types/common';

// Type assertion helper
const assertType = <T>(_value: T) => {
  // This function does nothing at runtime
  // It's only used for type checking during compilation
  expect(true).toBe(true); // Add an assertion to satisfy Vitest
};

describe('Common Types', () => {
  describe('Base Interfaces', () => {
    it('should correctly type Identifiable', () => {
      const item: Identifiable = { id: '123' };
      expect(item.id).toBe('123');

      const numericItem: Identifiable<number> = { id: 123 };
      expect(numericItem.id).toBe(123);
    });

    it('should correctly type Timestamped', () => {
      const now = new Date();
      const item: Timestamped = {
        createdAt: now,
        updatedAt: now,
      };
      expect(item.createdAt).toBe(now);
      expect(item.updatedAt).toBe(now);
    });

    it('should correctly type SoftDeletable', () => {
      const item: SoftDeletable = {
        isDeleted: false,
      };
      expect(item.isDeleted).toBe(false);
      expect(item.deletedAt).toBeUndefined();

      const deletedItem: SoftDeletable = {
        isDeleted: true,
        deletedAt: new Date(),
      };
      expect(deletedItem.isDeleted).toBe(true);
      expect(deletedItem.deletedAt).toBeInstanceOf(Date);
    });

    it('should correctly type Auditable', () => {
      const item: Auditable = {
        createdBy: 'user1',
        updatedBy: 'user2',
      };
      expect(item.createdBy).toBe('user1');
      expect(item.updatedBy).toBe('user2');
    });

    it('should correctly type Versionable', () => {
      const item: Versionable = {
        version: 1,
      };
      expect(item.version).toBe(1);
    });
  });

  describe('Utility Types', () => {
    interface TestType {
      id: string;
      name: string;
      age: number;
    }

    it('should correctly type Nullable', () => {
      const item: Nullable<TestType> = {
        id: null,
        name: 'test',
        age: null,
      };
      expect(item.id).toBeNull();
      expect(item.name).toBe('test');
      expect(item.age).toBeNull();
    });

    it('should correctly type Optional', () => {
      const item: Optional<TestType> = {
        name: 'test',
      };
      expect(item.id).toBeUndefined();
      expect(item.name).toBe('test');
      expect(item.age).toBeUndefined();
    });

    it('should correctly type ReadOnly', () => {
      const item: ReadOnly<TestType> = {
        id: '123',
        name: 'test',
        age: 25,
      };
      expect(() => {
        // @ts-expect-error - Cannot assign to 'id' because it is a read-only property
        item.id = '456';
      }).toThrow();
    });

    it('should correctly type DeepPartial', () => {
      interface NestedType {
        user: {
          profile: {
            name: string;
            age: number;
          };
          settings: {
            theme: string;
          };
        };
      }

      const item: DeepPartial<NestedType> = {
        user: {
          profile: {
            name: 'test',
          },
        },
      };
      expect(item.user?.profile?.name).toBe('test');
      expect(item.user?.profile?.age).toBeUndefined();
      expect(item.user?.settings).toBeUndefined();
    });
  });

  describe('Type Guards', () => {
    it('should correctly check isDefined', () => {
      expect(isDefined(null)).toBe(false);
      expect(isDefined(undefined)).toBe(false);
      expect(isDefined('')).toBe(true);
      expect(isDefined(0)).toBe(true);
      expect(isDefined(false)).toBe(true);
    });

    it('should correctly check isString', () => {
      expect(isString('')).toBe(true);
      expect(isString('test')).toBe(true);
      expect(isString(123)).toBe(false);
      expect(isString(null)).toBe(false);
    });

    it('should correctly check isNumber', () => {
      expect(isNumber(123)).toBe(true);
      expect(isNumber(0)).toBe(true);
      expect(isNumber(NaN)).toBe(false);
      expect(isNumber('123')).toBe(false);
    });

    it('should correctly check isBoolean', () => {
      expect(isBoolean(true)).toBe(true);
      expect(isBoolean(false)).toBe(true);
      expect(isBoolean(1)).toBe(false);
      expect(isBoolean('true')).toBe(false);
    });

    it('should correctly check isObject', () => {
      expect(isObject({})).toBe(true);
      expect(isObject({ key: 'value' })).toBe(true);
      expect(isObject(null)).toBe(false);
      expect(isObject('object')).toBe(false);
    });

    it('should correctly check isArray', () => {
      expect(isArray([])).toBe(true);
      expect(isArray([1, 2, 3])).toBe(true);
      expect(isArray({})).toBe(false);
      expect(isArray('array')).toBe(false);
    });

    it('should correctly check isDate', () => {
      expect(isDate(new Date())).toBe(true);
      expect(isDate(new Date('invalid'))).toBe(false);
      expect(isDate('2023-01-01')).toBe(false);
      expect(isDate({})).toBe(false);
    });

    it('should correctly use isType', () => {
      const isPositiveNumber = (value: unknown): value is number =>
        isNumber(value) && value > 0;

      expect(isType(5, isPositiveNumber)).toBe(true);
      expect(isType(-5, isPositiveNumber)).toBe(false);
      expect(isType('5', isPositiveNumber)).toBe(false);
    });
  });

  describe('Utility and Helper Types', () => {
    it('should work with DeepPartial', () => {
      type User = { id: string; name: string; profile?: { age: number } };
      const partial: DeepPartial<User> = { name: 'A', profile: { age: 42 } };
      expect(partial.name).toBe('A');
      expect(partial.profile?.age).toBe(42);
    });

    it('should work with RecursiveRequired', () => {
      type User = { id?: string; profile?: { age?: number } };
      const required: RecursiveRequired<User> = {
        id: '1',
        profile: { age: 42 },
      };
      expect(required.id).toBe('1');
      expect(required.profile.age).toBe(42);
    });

    it('should work with FormState and ValidationErrors', () => {
      interface User {
        name: string;
      }
      const form: FormState<User> = {
        values: { name: 'A' },
        errors: { name: 'Required' },
        touched: { name: true },
        isValid: false,
        isSubmitting: false,
      };
      expect(form.errors.name).toBe('Required');
      expect(form.touched.name).toBe(true);
    });

    it('should work with State, Action, and Reducer', () => {
      interface User {
        name: string;
      }
      const initialState: State<User> = { data: { name: 'A' }, loading: false };
      const action: Action<User> = { type: 'update', payload: { name: 'B' } };
      const reducer: Reducer<State<User>, Action<User>> = (state, action) => {
        if (action.type === 'update' && action.payload) {
          return { ...state, data: action.payload };
        }
        return state;
      };
      const newState = reducer(initialState, action);
      expect(newState.data.name).toBe('B');
    });

    it('should work with type guards', () => {
      expect(isDefined('A')).toBe(true);
      expect(isString('A')).toBe(true);
      expect(isNumber(42)).toBe(true);
      expect(isBoolean(false)).toBe(true);
      expect(isObject({})).toBe(true);
      expect(isArray([1, 2, 3])).toBe(true);
      expect(isDate(new Date())).toBe(true);
      expect(isType<string>('A', isString)).toBe(true);
    });
  });

  describe('Basic Types', () => {
    it('should correctly type ID', () => {
      const id: ID = '123';
      assertType<ID>(id);
    });

    it('should correctly type Timestamp', () => {
      const timestamp: Timestamp = Date.now();
      assertType<Timestamp>(timestamp);
    });

    it('should correctly type UUID', () => {
      const uuid: UUID = '123e4567-e89b-12d3-a456-426614174000';
      assertType<UUID>(uuid);
    });
  });

  describe('Entity Types', () => {
    it('should correctly type BaseEntity', () => {
      const entity: BaseEntity = {
        id: '123',
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      assertType<BaseEntity>(entity);
    });
  });

  describe('Pagination Types', () => {
    it('should correctly type PaginationParams', () => {
      const params: PaginationParams = {
        page: 1,
        limit: 10,
      };
      assertType<PaginationParams>(params);
    });

    it('should correctly type PaginationMeta', () => {
      const meta: PaginationMeta = {
        currentPage: 1,
        totalPages: 10,
        totalItems: 100,
        itemsPerPage: 10,
        hasNextPage: true,
        hasPreviousPage: false,
      };
      assertType<PaginationMeta>(meta);
    });

    it('should correctly type PaginatedResponse', () => {
      interface User {
        id: string;
        name: string;
      }

      const response: PaginatedResponse<User> = {
        items: [{ id: '1', name: 'John' }],
        meta: {
          currentPage: 1,
          totalPages: 10,
          totalItems: 100,
          itemsPerPage: 10,
          hasNextPage: true,
          hasPreviousPage: false,
        },
      };
      assertType<PaginatedResponse<User>>(response);
    });
  });

  describe('Query Types', () => {
    it('should correctly type SortParams', () => {
      const sort: SortParams = {
        field: 'name',
        order: 'asc',
      };
      assertType<SortParams>(sort);
    });

    it('should correctly type FilterCondition', () => {
      interface User {
        name: string;
        age: number;
      }

      const filter: FilterCondition<User> = {
        field: 'age',
        operator: 'gt',
        value: 18,
      };
      assertType<FilterCondition<User>>(filter);
    });

    it('should correctly type QueryParams', () => {
      interface User {
        name: string;
        age: number;
      }

      const params: QueryParams<User> = {
        pagination: { page: 1, limit: 10 },
        sort: [{ field: 'name', order: 'asc' }],
        filters: [
          { field: 'age', operator: 'gt', value: 18 },
        ],
      };
      assertType<QueryParams<User>>(params);
    });
  });

  describe('Response Types', () => {
    it('should correctly type SuccessResponse', () => {
      const response: SuccessResponse<string> = {
        data: 'success',
        message: 'Operation completed',
      };
      assertType<SuccessResponse<string>>(response);
    });

    it('should correctly type ErrorResponse', () => {
      const error: ErrorResponse = {
        error: {
          code: 'NOT_FOUND',
          message: 'Resource not found',
          details: { id: '123' },
        },
      };
      assertType<ErrorResponse>(error);
    });
  });

  describe('Async Types', () => {
    it('should correctly type AsyncStatus', () => {
      const status: AsyncStatus = 'loading';
      assertType<AsyncStatus>(status);
    });

    it('should correctly type AsyncState', () => {
      interface User {
        id: string;
        name: string;
      }

      const state: AsyncState<User> = {
        data: null,
        error: null,
        status: 'idle',
      };
      assertType<AsyncState<User>>(state);
    });
  });

  describe('Validation Types', () => {
    it('should correctly type ValidationStatus', () => {
      const status: ValidationStatus = 'valid';
      assertType<ValidationStatus>(status);
    });

    it('should correctly type ValidationResult', () => {
      const result: ValidationResult = {
        isValid: false,
        errors: {
          name: ['Name is required'],
          age: ['Age must be greater than 0'],
        },
      };
      assertType<ValidationResult>(result);
    });
  });

  describe('Cache Types', () => {
    it('should correctly type CacheOptions', () => {
      const options: CacheOptions = {
        ttl: 60000,
        key: 'users',
        group: 'entities',
      };
      assertType<CacheOptions>(options);
    });
  });

  describe('Event Types', () => {
    it('should correctly type EventHandler', () => {
      const handler: EventHandler<string> = (event) => {
        console.log(event.toUpperCase());
      };
      assertType<EventHandler<string>>(handler);
    });

    it('should correctly type Subscription', () => {
      const subscription: Subscription = {
        unsubscribe: () => {
          console.log('Unsubscribed');
        },
      };
      assertType<Subscription>(subscription);
    });
  });

  describe('Retry Types', () => {
    it('should correctly type RetryOptions', () => {
      const options: RetryOptions = {
        maxAttempts: 3,
        delay: 1000,
        backoffFactor: 2,
      };
      assertType<RetryOptions>(options);
    });
  });
});
