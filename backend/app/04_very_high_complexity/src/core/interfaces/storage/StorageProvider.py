from typing import Any, Dict
from enum import Enum



/**
 * Options for storage operations
 */
class StorageOptions:
    contentType?: str
    metadata?: Dict[str, str>
    cacheControl?: str
    isPublic?: bool
/**
 * Options for URL generation
 */
class UrlOptions:
    expiresIn?: float
    download?: bool
    filename?: str
/**
 * Result of a storage operation
 */
class StorageResult:
    path: str
    size: float
    url?: str
    metadata?: Dict[str, Any>
/**
 * Represents a stored item (file or directory)
 */
class StorageItem:
    path: str
    size: float
    lastModified: Date
    isDirectory: bool
/**
 * Error codes for storage operations
 */
class StorageErrorCode(Enum):
    NOT_FOUND = 'NOT_FOUND'
    PERMISSION_DENIED = 'PERMISSION_DENIED'
    ALREADY_EXISTS = 'ALREADY_EXISTS'
    INVALID_ARGUMENT = 'INVALID_ARGUMENT'
    NETWORK_ERROR = 'NETWORK_ERROR'
    NOT_SUPPORTED = 'NOT_SUPPORTED'
    INSUFFICIENT_SPACE = 'INSUFFICIENT_SPACE'
    UNKNOWN = 'UNKNOWN'
/**
 * Custom error class for storage operations
 */
class StorageError extends Error {
  constructor(
    public readonly code: \'StorageErrorCode\',
    message: str,
    public readonly details?: Record<string, any>
  ) {
    super(message)
    this.name = 'StorageError'
  }
}
/**
 * Interface for storage providers
 * Implementations should handle:
 * - Path normalization
 * - Error mapping to StorageError types
 * - Proper cleanup of resources
 * - Streaming support for large files
 */
class StorageProvider:
    pass
   */
  save(data: Buffer | Readable, path: str, options?: StorageOptions): Promise<StorageResult>
  /**
   * Retrieve data from storage
   * @throws {StorageError}
   */
  get(path: str): Promise<Buffer | Readable>
  /**
   * Delete item from storage
   * @throws {StorageError}
   */
  delete(path: str): Promise<boolean>
  /**
   * Check if item exists in storage
   */
  exists(path: str): Promise<boolean>
  /**
   * Generate URL for accessing the item
   * @throws {StorageError}
   */
  getUrl(path: str, options?: UrlOptions): Promise<string>
  /**
   * List items in storage with given prefix
   * @throws {StorageError}
   */
  list?(prefix: str): Promise<StorageItem[]>
  /**
   * Copy item within storage
   * @throws {StorageError}
   */
  copy?(sourcePath: str, destinationPath: str): Promise<boolean>
  /**
   * Move item within storage
   * @throws {StorageError}
   */
  move?(sourcePath: str, destinationPath: str): Promise<boolean>
  /**
   * Get metadata for an item
   * @throws {StorageError}
   */
  getMetadata?(path: str): Promise<Record<string, any>>
  /**
   * Update metadata for an item
   * @throws {StorageError}
   */
  updateMetadata?(path: str, metadata: Record<string, any>): Promise<Record<string, any>>
} 