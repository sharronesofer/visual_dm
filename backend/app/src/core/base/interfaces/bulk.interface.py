from typing import Any


/**
 * Bulk operations interface
 * @module core/base/interfaces/bulk
 */
/**
 * Interface for services that support bulk operations
 */
interface IBulkService<T extends BaseEntity> {
  /** Create multiple entities */
  bulkCreate(data: Array<Omit<T, keyof BaseEntity>>): Promise<ServiceResponse<T[]>>
  /** Update multiple entities */
  bulkUpdate(updates: Array<{ id: T['id']; data: Partial<T> }>): Promise<ServiceResponse<T[]>>
  /** Delete multiple entities */
  bulkDelete(ids: Array<T['id']>): Promise<ServiceResponse<void>>
  /** Validate multiple entities */
  bulkValidate(data: Array<Partial<T>>): Promise<ServiceResponse<boolean>>
} 