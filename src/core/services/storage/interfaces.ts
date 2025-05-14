/**
 * Storage provider configuration options
 */
export interface StorageOptions {
  /** Base path for storage operations */
  basePath?: string;
  /** File system permissions for created files (e.g., 0o644) */
  permissions?: number;
  /** Whether to create directories if they don't exist */
  createIfNotExists?: boolean;
  /** Maximum concurrent operations */
  maxConcurrent?: number;
  /** Timeout for operations in milliseconds */
  operationTimeout?: number;
}

/**
 * Metadata for stored items
 */
export interface StorageMetadata {
  /** Original file name */
  name: string;
  /** MIME type of the file */
  mimeType: string;
  /** Size in bytes */
  size: number;
  /** Creation timestamp */
  createdAt: Date;
  /** Last modification timestamp */
  modifiedAt: Date;
  /** Custom metadata key-value pairs */
  metadata?: Record<string, unknown>;
}

/**
 * Options for storage operations
 */
export interface StorageOperationOptions {
  /** Whether to overwrite existing files */
  overwrite?: boolean;
  /** Custom metadata to store with the file */
  metadata?: Record<string, unknown>;
  /** Operation-specific timeout in milliseconds */
  timeout?: number;
}

/**
 * Result of a storage operation
 */
export interface StorageOperationResult {
  /** Path to the stored file */
  path: string;
  /** URL to access the file (if applicable) */
  url?: string;
  /** File metadata */
  metadata: StorageMetadata;
}

/**
 * Directory operation options
 */
export interface DirectoryOperationOptions extends StorageOperationOptions {
  /** Whether to create parent directories if they don't exist */
  createParents?: boolean;
  /** Whether to fail if directory is not empty on delete */
  failIfNotEmpty?: boolean;
}

/**
 * Result of a directory operation
 */
export interface DirectoryOperationResult {
  /** Path to the directory */
  path: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Any errors that occurred during the operation */
  error?: Error;
}

/**
 * Storage provider interface defining core storage operations
 */
export interface StorageProvider {
  /**
   * Save data to storage
   * @param path - Target path for the file
   * @param data - File content as Buffer or string
   * @param options - Storage operation options
   * @returns Promise resolving to operation result
   * @throws StorageError if operation fails
   */
  save(
    path: string,
    data: Buffer | string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult>;

  /**
   * Read data from storage
   * @param path - Path to the file
   * @returns Promise resolving to file content
   * @throws StorageError if file not found or operation fails
   */
  read(path: string): Promise<Buffer>;

  /**
   * Delete a file from storage
   * @param path - Path to the file
   * @returns Promise resolving to true if file was deleted
   * @throws StorageError if operation fails
   */
  delete(path: string): Promise<boolean>;

  /**
   * Check if a file exists
   * @param path - Path to check
   * @returns Promise resolving to true if file exists
   */
  exists(path: string): Promise<boolean>;

  /**
   * List files in a directory
   * @param directory - Directory path
   * @param recursive - Whether to list files recursively
   * @returns Promise resolving to array of file paths
   * @throws StorageError if operation fails
   */
  list(directory: string, recursive?: boolean): Promise<string[]>;

  /**
   * Get metadata for a file
   * @param path - Path to the file
   * @returns Promise resolving to file metadata
   * @throws StorageError if file not found or operation fails
   */
  getMetadata(path: string): Promise<StorageMetadata>;

  /**
   * Get a URL for accessing the file
   * @param path - Path to the file
   * @param options - URL generation options (e.g., expiry)
   * @returns Access URL for the file
   */
  getUrl(path: string, options?: { expires?: Date }): string;

  /**
   * Copy a file to a new location
   * @param sourcePath - Source file path
   * @param targetPath - Target file path
   * @param options - Storage operation options
   * @returns Promise resolving to operation result
   * @throws StorageError if operation fails
   */
  copy(
    sourcePath: string,
    targetPath: string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult>;

  /**
   * Move a file to a new location
   * @param sourcePath - Source file path
   * @param targetPath - Target file path
   * @param options - Storage operation options
   * @returns Promise resolving to operation result
   * @throws StorageError if operation fails
   */
  move(
    sourcePath: string,
    targetPath: string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult>;

  /**
   * Create a directory
   * @param path - Directory path to create
   * @param options - Directory operation options
   * @returns Promise resolving to operation result
   * @throws StorageError if operation fails
   */
  createDirectory(path: string, options?: DirectoryOperationOptions): Promise<DirectoryOperationResult>;

  /**
   * Remove a directory
   * @param path - Directory path to remove
   * @param options - Directory operation options
   * @returns Promise resolving to operation result
   * @throws StorageError if operation fails
   */
  removeDirectory(path: string, options?: DirectoryOperationOptions): Promise<DirectoryOperationResult>;

  /**
   * List directory contents with filtering
   * @param path - Directory path to list
   * @param options - List operation options
   * @returns Promise resolving to filtered file list
   * @throws StorageError if operation fails
   */
  listDirectory(path: string, options?: {
    recursive?: boolean;
    filter?: (path: string) => boolean;
    includeDirectories?: boolean;
  }): Promise<string[]>;
}

/**
 * Base class for storage-related errors
 */
export class StorageError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly path?: string,
    public readonly cause?: Error
  ) {
    super(message);
    this.name = 'StorageError';
  }
}

/**
 * Error thrown when a file is not found
 */
export class FileNotFoundError extends StorageError {
  constructor(path: string, cause?: Error) {
    super(`File not found: ${path}`, 'FILE_NOT_FOUND', path, cause);
    this.name = 'FileNotFoundError';
  }
}

/**
 * Error thrown when a file already exists
 */
export class FileExistsError extends StorageError {
  constructor(path: string) {
    super(`File already exists: ${path}`, 'FILE_EXISTS', path);
    this.name = 'FileExistsError';
  }
}

/**
 * Error thrown when a storage operation times out
 */
export class StorageTimeoutError extends StorageError {
  constructor(operation: string, path: string, timeout: number) {
    super(
      `Storage operation '${operation}' timed out after ${timeout}ms for path: ${path}`,
      'OPERATION_TIMEOUT',
      path
    );
    this.name = 'StorageTimeoutError';
  }
}
