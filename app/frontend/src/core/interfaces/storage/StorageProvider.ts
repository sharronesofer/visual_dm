import { Readable } from 'stream';

/**
 * Options for storage operations
 */
export interface StorageOptions {
  contentType?: string;
  metadata?: Record<string, string>;
  cacheControl?: string;
  isPublic?: boolean;
}

/**
 * Options for URL generation
 */
export interface UrlOptions {
  expiresIn?: number; // Seconds
  download?: boolean;
  filename?: string;
}

/**
 * Result of a storage operation
 */
export interface StorageResult {
  path: string;
  size: number;
  url?: string;
  metadata?: Record<string, any>;
}

/**
 * Represents a stored item (file or directory)
 */
export interface StorageItem {
  path: string;
  size: number;
  lastModified: Date;
  isDirectory: boolean;
}

/**
 * Error codes for storage operations
 */
export enum StorageErrorCode {
  NOT_FOUND = 'NOT_FOUND',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  ALREADY_EXISTS = 'ALREADY_EXISTS',
  INVALID_ARGUMENT = 'INVALID_ARGUMENT',
  NETWORK_ERROR = 'NETWORK_ERROR',
  NOT_SUPPORTED = 'NOT_SUPPORTED',
  INSUFFICIENT_SPACE = 'INSUFFICIENT_SPACE',
  UNKNOWN = 'UNKNOWN'
}

/**
 * Custom error class for storage operations
 */
export class StorageError extends Error {
  constructor(
    public readonly code: StorageErrorCode,
    message: string,
    public readonly details?: Record<string, any>
  ) {
    super(message);
    this.name = 'StorageError';
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
export interface StorageProvider {
  /**
   * Save data to storage
   * @throws {StorageError}
   */
  save(data: Buffer | Readable, path: string, options?: StorageOptions): Promise<StorageResult>;

  /**
   * Retrieve data from storage
   * @throws {StorageError}
   */
  get(path: string): Promise<Buffer | Readable>;

  /**
   * Delete item from storage
   * @throws {StorageError}
   */
  delete(path: string): Promise<boolean>;

  /**
   * Check if item exists in storage
   */
  exists(path: string): Promise<boolean>;

  /**
   * Generate URL for accessing the item
   * @throws {StorageError}
   */
  getUrl(path: string, options?: UrlOptions): Promise<string>;

  /**
   * List items in storage with given prefix
   * @throws {StorageError}
   */
  list?(prefix: string): Promise<StorageItem[]>;

  /**
   * Copy item within storage
   * @throws {StorageError}
   */
  copy?(sourcePath: string, destinationPath: string): Promise<boolean>;

  /**
   * Move item within storage
   * @throws {StorageError}
   */
  move?(sourcePath: string, destinationPath: string): Promise<boolean>;

  /**
   * Get metadata for an item
   * @throws {StorageError}
   */
  getMetadata?(path: string): Promise<Record<string, any>>;

  /**
   * Update metadata for an item
   * @throws {StorageError}
   */
  updateMetadata?(path: string, metadata: Record<string, any>): Promise<Record<string, any>>;
} 