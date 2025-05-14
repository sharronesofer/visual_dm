/**
 * Base pagination parameters
 */
export interface PaginationParams {
  /** Current page number (1-based) */
  page?: number;
  /** Number of items per page */
  limit?: number;
  /** Number of items to skip */
  offset?: number;
}

/**
 * Sorting direction
 */
export type SortDirection = 'asc' | 'desc';

/**
 * Sorting parameters
 */
export interface SortingParams<T = any> {
  /** Field to sort by */
  field: keyof T;
  /** Sort direction */
  direction: SortDirection;
}

/**
 * Comparison operators for filtering
 */
export type ComparisonOperator =
  | 'eq' // equals
  | 'neq' // not equals
  | 'gt' // greater than
  | 'gte' // greater than or equal
  | 'lt' // less than
  | 'lte' // less than or equal
  | 'in' // in array
  | 'nin' // not in array
  | 'like' // string contains
  | 'nlike' // string does not contain
  | 'regex' // matches regex pattern
  | 'null' // is null
  | 'nnull'; // is not null

/**
 * Logical operators for combining filter conditions
 */
export type LogicalOperator = 'and' | 'or' | 'not';

/**
 * Single filter condition
 */
export interface FilterCondition<T = any> {
  /** Field to filter on */
  field: keyof T;
  /** Comparison operator */
  operator: ComparisonOperator;
  /** Value to compare against */
  value: any;
}

/**
 * Group of filter conditions combined with a logical operator
 */
export interface FilterGroup<T = any> {
  /** Logical operator to combine conditions */
  operator: LogicalOperator;
  /** List of conditions or nested groups */
  conditions: (FilterCondition<T> | FilterGroup<T>)[];
}

/**
 * Complete filtering parameters
 */
export interface FilteringParams<T = any> {
  /** Root filter group */
  group: FilterGroup<T>;
}

/**
 * Complete query options
 */
export interface QueryOptions<T = any> extends PaginationParams {
  /** Sorting parameters */
  sort?: SortingParams<T>;
  /** Filtering parameters */
  filter?: FilteringParams<T>;
  /** Relations to include */
  include?: string[];
  /** Fields to select */
  select?: (keyof T)[];
}

/**
 * Pagination metadata
 */
export interface PaginationMeta {
  /** Total number of items */
  total: number;
  /** Current page number */
  page: number;
  /** Items per page */
  limit: number;
  /** Total number of pages */
  totalPages: number;
  /** Whether there are more items */
  hasMore: boolean;
  /** Whether there is a next page */
  hasNextPage: boolean;
  /** Whether there is a previous page */
  hasPrevPage: boolean;
}

/**
 * Paginated result wrapper
 */
export interface PaginatedResult<T> {
  /** List of items */
  items: T[];
  /** Pagination metadata */
  meta: PaginationMeta;
}

/**
 * Query builder interface for constructing complex queries
 */
export interface QueryBuilder<T = any> {
  /** Set pagination parameters */
  paginate(params: PaginationParams): this;
  /** Set sorting parameters */
  sort(params: SortingParams<T>): this;
  /** Add a filter condition */
  where(condition: FilterCondition<T>): this;
  /** Add a filter group */
  whereGroup(group: FilterGroup<T>): this;
  /** Specify relations to include */
  include(relations: string[]): this;
  /** Specify fields to select */
  select(fields: (keyof T)[]): this;
  /** Get the complete query options */
  getOptions(): QueryOptions<T>;
}

/**
 * Utility functions for working with queries
 */
export class QueryUtils {
  /**
   * Create a filter condition
   */
  static createCondition<T>(
    field: keyof T,
    operator: ComparisonOperator,
    value: any
  ): FilterCondition<T> {
    return { field, operator, value };
  }

  /**
   * Create a filter group
   */
  static createGroup<T>(
    operator: LogicalOperator,
    conditions: (FilterCondition<T> | FilterGroup<T>)[]
  ): FilterGroup<T> {
    return { operator, conditions };
  }

  /**
   * Create sorting parameters
   */
  static createSort<T>(
    field: keyof T,
    direction: SortDirection = 'asc'
  ): SortingParams<T> {
    return { field, direction };
  }

  /**
   * Calculate pagination metadata
   */
  static calculatePagination(
    total: number,
    page: number,
    limit: number
  ): PaginationMeta {
    const totalPages = Math.ceil(total / limit);
    const hasMore = page < totalPages;
    const hasNextPage = page < totalPages;
    const hasPrevPage = page > 1;

    return {
      total,
      page,
      limit,
      totalPages,
      hasMore,
      hasNextPage,
      hasPrevPage,
    };
  }
}
