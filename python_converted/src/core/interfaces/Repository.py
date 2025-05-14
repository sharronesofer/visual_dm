from typing import Any, List


/**
 * Repository response with pagination
 */
interface RepositoryResponse<T> {
  data: List[T]
  total: float
}
/**
 * Generic repository interface
 */
interface Repository<T extends BaseEntity> {
  findById(id: ID): Promise<T | null>
  findAll(
    pagination?: PaginationParams,
    sort?: SortParams,
    filters?: QueryFilters
  ): Promise<RepositoryResponse<T>>
  create(entity: T): Promise<T>
  update(id: ID, entity: T): Promise<T | null>
  delete(id: ID): Promise<boolean>
} 