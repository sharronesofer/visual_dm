from typing import Any, List, Union


/**
 * Base pagination parameters
 */
class PaginationParams:
    /** Current page number (1-based) */
  page?: float
    /** Number of items per page */
  limit?: float
    /** Number of items to skip */
  offset?: float
/**
 * Sorting direction
 */
SortDirection = Union['asc', 'desc']
/**
 * Sorting parameters
 */
interface SortingParams<T = any> {
  /** Field to sort by */
  field: keyof T
  /** Sort direction */
  direction: SortDirection
}
/**
 * Comparison operators for filtering
 */
ComparisonOperator = Union[, 'eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'in', 'nin', 'like', 'nlike', 'regex', 'None', 'nNone'] 
/**
 * Logical operators for combining filter conditions
 */
LogicalOperator = Union['and', 'or', 'not']
/**
 * Single filter condition
 */
interface FilterCondition<T = any> {
  /** Field to filter on */
  field: keyof T
  /** Comparison operator */
  operator: ComparisonOperator
  /** Value to compare against */
  value: Any
}
/**
 * Group of filter conditions combined with a logical operator
 */
interface FilterGroup<T = any> {
  /** Logical operator to combine conditions */
  operator: LogicalOperator
  /** List of conditions or nested groups */
  conditions: (FilterCondition<T> | FilterGroup<T>)[]
}
/**
 * Complete filtering parameters
 */
interface FilteringParams<T = any> {
  /** Root filter group */
  group: FilterGroup<T>
}
/**
 * Complete query options
 */
interface QueryOptions<T = any> extends PaginationParams {
  /** Sorting parameters */
  sort?: SortingParams<T>
  /** Filtering parameters */
  filter?: FilteringParams<T>
  /** Relations to include */
  include?: string[]
  /** Fields to select */
  select?: (keyof T)[]
}
/**
 * Pagination metadata
 */
class PaginationMeta:
    /** Total number of items */
  total: float
    /** Current page number */
  page: float
    /** Items per page */
  limit: float
    /** Total number of pages */
  totalPages: float
    /** Whether there are more items */
  hasMore: bool
    /** Whether there is a next page */
  hasNextPage: bool
    /** Whether there is a previous page */
  hasPrevPage: bool
/**
 * Paginated result wrapper
 */
interface PaginatedResult<T> {
  /** List of items */
  items: List[T]
  /** Pagination metadata */
  meta: \'PaginationMeta\'
}
/**
 * Query builder interface for constructing complex queries
 */
interface QueryBuilder<T = any> {
  /** Set pagination parameters */
  paginate(params: PaginationParams): this
  /** Set sorting parameters */
  sort(params: SortingParams<T>): this
  /** Add a filter condition */
  where(condition: FilterCondition<T>): this
  /** Add a filter group */
  whereGroup(group: FilterGroup<T>): this
  /** Specify relations to include */
  include(relations: List[string]): this
  /** Specify fields to select */
  select(fields: (keyof T)[]): this
  /** Get the complete query options */
  getOptions(): QueryOptions<T>
}
/**
 * Utility functions for working with queries
 */
class QueryUtils {
  /**
   * Create a filter condition
   */
  static createCondition<T>(
    field: keyof T,
    operator: ComparisonOperator,
    value: Any
  ): FilterCondition<T> {
    return { field, operator, value }
  }
  /**
   * Create a filter group
   */
  static createGroup<T>(
    operator: LogicalOperator,
    conditions: (FilterCondition<T> | FilterGroup<T>)[]
  ): FilterGroup<T> {
    return { operator, conditions }
  }
  /**
   * Create sorting parameters
   */
  static createSort<T>(
    field: keyof T,
    direction: SortDirection = 'asc'
  ): SortingParams<T> {
    return { field, direction }
  }
  /**
   * Calculate pagination metadata
   */
  static calculatePagination(
    total: float,
    page: float,
    limit: float
  ): \'PaginationMeta\' {
    const totalPages = Math.ceil(total / limit)
    const hasMore = page < totalPages
    const hasNextPage = page < totalPages
    const hasPrevPage = page > 1
    return {
      total,
      page,
      limit,
      totalPages,
      hasMore,
      hasNextPage,
      hasPrevPage,
    }
  }
}