from typing import Any, Dict, Union



/**
 * Storage provider configuration options
 */
class StorageOptions:
    /** Base path for storage operations */
  basePath?: str
    /** File system permissions for created files (e.g., 0o644) */
  permissions?: float
    /** Whether to create directories if they don't exist */
  createIfNotExists?: bool
    /** Maximum concurrent operations */
  maxConcurrent?: float
    /** Timeout for operations in milliseconds */
  operationTimeout?: float
/**
 * Metadata for stored items
 */
class StorageMetadata:
    /** Original file name */
  name: str
    /** MIME type of the file */
  mimeType: str
    /** Size in bytes */
  size: float
    /** Creation timestamp */
  createdAt: Date
    /** Last modification timestamp */
  modifiedAt: Date
    /** Custom metadata key-value pairs */
  metadata?: Dict[str, unknown>
/**
 * Options for storage operations
 */
class StorageOperationOptions:
    /** Whether to overwrite existing files */
  overwrite?: bool
    /** Custom metadata to store with the file */
  metadata?: Dict[str, unknown>
    /** Operation-specific timeout in milliseconds */
  timeout?: float
/**
 * Result of a storage operation
 */
class StorageOperationResult:
    /** Path to the stored file */
  path: str
    /** URL to access the file (if applicable) */
  url?: str
    /** File metadata */
  metadata: \'StorageMetadata\'
/**
 * Directory operation options
 */
class DirectoryOperationOptions:
    /** Whether to create parent directories if they don't exist */
  createParents?: bool
    /** Whether to fail if directory is not empty on delete */
  failIfNotEmpty?: bool
/**
 * Result of a directory operation
 */
class DirectoryOperationResult:
    /** Path to the directory */
  path: str
    /** Whether the operation was successful */
  success: bool
    /** Any errors that occurred during the operation */
  error?: Error
/**
 * Storage provider interface defining core storage operations
 */
class StorageProvider:
    /**
   * Save data to storage
   * @param path - Target path for the file
   * @param data - File content as Buffer or string
   * @param options - Storage operation options
   * @returns Promise resolving to operation result
   * @throws StorageError if operation fails
   */
  save(
    path: Union[str,
    data: Buffer, str,
    options?: \'StorageOperationOptions\'
  ): Awaitable[StorageOperationResult>]
    /**
   * Read data from storage
   * @param path - Path to the file
   * @returns Promise resolving to file content
   * @throws StorageError if file not found or operation fails
   */
  read(path: str): Awaitable[Buffer>
    /**
   * Delete a file from storage
   * @param path - Path to the file
   * @returns Promise resolving to true if file was deleted
   * @throws StorageError if operation fails
   */
  delete(path: str): Awaitable[bool>
    /**
   * Check if a file exists
   * @param path - Path to check
   * @returns Promise resolving to true if file exists
   */
  exists(path: str): Awaitable[bool>
    /**
   * List files in a directory
   * @param directory - Directory path
   * @param recursive - Whether to list files recursively
   * @returns Promise resolving to array of file paths
   * @throws StorageError if operation fails
   */
  list(directory: str, recursive?: bool): Awaitable[str[]>
    /**
   * Get metadata for a file
   * @param path - Path to the file
   * @returns Promise resolving to file metadata
   * @throws StorageError if file not found or operation fails
   */
  getMetadata(path: str): Awaitable[StorageMetadata>
    /**
   * Get a URL for accessing the file
   * @param path - Path to the file
   * @param options - URL generation options (e.g., expiry)
   * @returns Access URL for the file
   */
  getUrl(path: str, options?: { expires?: Date): str
  /**
   * Copy a file to a new location
   * @param sourcePath - Source file path
   * @param targetPath - Target file path
   * @param options - Storage operation options
   * @returns Promise resolving to operation result
   * @throws StorageError if operation fails
   */
  copy(
    sourcePath: str,
    targetPath: str,
    options?: \'StorageOperationOptions\'
  ): Promise<StorageOperationResult>
  /**
   * Move a file to a new location
   * @param sourcePath - Source file path
   * @param targetPath - Target file path
   * @param options - Storage operation options
   * @returns Promise resolving to operation result
   * @throws StorageError if operation fails
   */
  move(
    sourcePath: str,
    targetPath: str,
    options?: \'StorageOperationOptions\'
  ): Promise<StorageOperationResult>
  /**
   * Create a directory
   * @param path - Directory path to create
   * @param options - Directory operation options
   * @returns Promise resolving to operation result
   * @throws StorageError if operation fails
   */
  createDirectory(path: str, options?: DirectoryOperationOptions): Promise<DirectoryOperationResult>
  /**
   * Remove a directory
   * @param path - Directory path to remove
   * @param options - Directory operation options
   * @returns Promise resolving to operation result
   * @throws StorageError if operation fails
   */
  removeDirectory(path: str, options?: DirectoryOperationOptions): Promise<DirectoryOperationResult>
  /**
   * List directory contents with filtering
   * @param path - Directory path to list
   * @param options - List operation options
   * @returns Promise resolving to filtered file list
   * @throws StorageError if operation fails
   */
  listDirectory(path: str, options?: {
    recursive?: bool
    filter?: (path: str) => boolean
    includeDirectories?: bool
  }): Promise<string[]>
}
/**
 * Base class for storage-related errors
 */
class StorageError extends Error {
  constructor(
    message: str,
    public readonly code: str,
    public readonly path?: str,
    public readonly cause?: Error
  ) {
    super(message)
    this.name = 'StorageError'
  }
}
/**
 * Error thrown when a file is not found
 */
class FileNotFoundError extends StorageError {
  constructor(path: str, cause?: Error) {
    super(`File not found: ${path}`, 'FILE_NOT_FOUND', path, cause)
    this.name = 'FileNotFoundError'
  }
}
/**
 * Error thrown when a file already exists
 */
class FileExistsError extends StorageError {
  constructor(path: str) {
    super(`File already exists: ${path}`, 'FILE_EXISTS', path)
    this.name = 'FileExistsError'
  }
}
/**
 * Error thrown when a storage operation times out
 */
class StorageTimeoutError extends StorageError {
  constructor(operation: str, path: str, timeout: float) {
    super(
      `Storage operation '${operation}' timed out after ${timeout}ms for path: ${path}`,
      'OPERATION_TIMEOUT',
      path
    )
    this.name = 'StorageTimeoutError'
  }
}