from typing import Any



/**
 * Generic response type for service operations
 */
interface ServiceResponse<T> {
  /**
   * Whether the operation was successful
   */
  success: bool
  /**
   * Response data if operation was successful
   */
  data: T | null
  /**
   * Error information if operation failed
   */
  error?: Error & {
    code?: str
    status?: float
    details?: Record<string, any>
  }
} 