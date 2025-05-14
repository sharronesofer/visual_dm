import { StorageProvider, StorageOptions, UrlOptions, StorageResult, StorageItem, StorageError, StorageErrorCode } from '../../interfaces/storage/StorageProvider';
import { Readable } from 'stream';
import { EventEmitter } from 'events';
import path from 'path';

/**
 * Progress event data
 */
export interface ProgressData {
  bytesTransferred: number;
  totalBytes?: number;
  percent?: number;
}

/**
 * Base configuration for storage providers
 */
export interface BaseStorageConfig {
  /**
   * Base path/prefix for all operations
   */
  basePath?: string;

  /**
   * Default options for storage operations
   */
  defaultOptions?: StorageOptions;

  /**
   * Whether to emit progress events
   */
  enableProgress?: boolean;
}

/**
 * Abstract base class for storage providers
 * Implements common functionality and provides hooks for specific implementations
 */
export abstract class BaseStorageProvider extends EventEmitter implements StorageProvider {
  protected config: Required<BaseStorageConfig>;

  constructor(config: BaseStorageConfig = {}) {
    super();
    this.config = {
      basePath: '',
      defaultOptions: {},
      enableProgress: true,
      ...config
    };
  }

  /**
   * Save data to storage
   */
  async save(data: Buffer | Readable, path: string, options?: StorageOptions): Promise<StorageResult> {
    const fullPath = this.resolvePath(path);
    const mergedOptions = this.mergeOptions(options);

    try {
      // Ensure parent directory exists
      await this.ensureParentDirectory(fullPath);

      // Perform the actual save operation
      const result = await this.performSave(data, fullPath, mergedOptions);

      // Generate URL if the provider supports it
      if (mergedOptions.isPublic) {
        result.url = await this.getUrl(path);
      }

      return result;
    } catch (err) {
      throw this.mapError(err);
    }
  }

  /**
   * Retrieve data from storage
   */
  async get(path: string): Promise<Buffer | Readable> {
    try {
      const fullPath = this.resolvePath(path);
      return await this.performGet(fullPath);
    } catch (err) {
      throw this.mapError(err);
    }
  }

  /**
   * Delete item from storage
   */
  async delete(path: string): Promise<boolean> {
    try {
      const fullPath = this.resolvePath(path);
      return await this.performDelete(fullPath);
    } catch (err) {
      throw this.mapError(err);
    }
  }

  /**
   * Check if item exists in storage
   */
  async exists(path: string): Promise<boolean> {
    try {
      const fullPath = this.resolvePath(path);
      return await this.performExists(fullPath);
    } catch (err) {
      throw this.mapError(err);
    }
  }

  /**
   * Generate URL for accessing the item
   */
  async getUrl(path: string, options?: UrlOptions): Promise<string> {
    try {
      const fullPath = this.resolvePath(path);
      return await this.performGetUrl(fullPath, options);
    } catch (err) {
      throw this.mapError(err);
    }
  }

  /**
   * List items in storage with given prefix
   */
  async list(prefix: string = ''): Promise<StorageItem[]> {
    try {
      const fullPath = this.resolvePath(prefix);
      return await this.performList(fullPath);
    } catch (err) {
      throw this.mapError(err);
    }
  }

  /**
   * Copy item within storage
   */
  async copy(sourcePath: string, destinationPath: string): Promise<boolean> {
    try {
      const fullSourcePath = this.resolvePath(sourcePath);
      const fullDestPath = this.resolvePath(destinationPath);
      return await this.performCopy(fullSourcePath, fullDestPath);
    } catch (err) {
      throw this.mapError(err);
    }
  }

  /**
   * Move item within storage
   */
  async move(sourcePath: string, destinationPath: string): Promise<boolean> {
    try {
      const fullSourcePath = this.resolvePath(sourcePath);
      const fullDestPath = this.resolvePath(destinationPath);
      return await this.performMove(fullSourcePath, fullDestPath);
    } catch (err) {
      throw this.mapError(err);
    }
  }

  /**
   * Get metadata for an item
   */
  async getMetadata(path: string): Promise<Record<string, any>> {
    try {
      const fullPath = this.resolvePath(path);
      return await this.performGetMetadata(fullPath);
    } catch (err) {
      throw this.mapError(err);
    }
  }

  /**
   * Update metadata for an item
   */
  async updateMetadata(path: string, metadata: Record<string, any>): Promise<Record<string, any>> {
    try {
      const fullPath = this.resolvePath(path);
      return await this.performUpdateMetadata(fullPath, metadata);
    } catch (err) {
      throw this.mapError(err);
    }
  }

  // Abstract methods that must be implemented by concrete providers

  protected abstract performSave(
    data: Buffer | Readable,
    fullPath: string,
    options: StorageOptions
  ): Promise<StorageResult>;

  protected abstract performGet(fullPath: string): Promise<Buffer | Readable>;

  protected abstract performDelete(fullPath: string): Promise<boolean>;

  protected abstract performExists(fullPath: string): Promise<boolean>;

  protected abstract performGetUrl(fullPath: string, options?: UrlOptions): Promise<string>;

  protected abstract performList(fullPath: string): Promise<StorageItem[]>;

  protected abstract performCopy(fullSourcePath: string, fullDestPath: string): Promise<boolean>;

  protected abstract performMove(fullSourcePath: string, fullDestPath: string): Promise<boolean>;

  protected abstract performGetMetadata(fullPath: string): Promise<Record<string, any>>;

  protected abstract performUpdateMetadata(
    fullPath: string,
    metadata: Record<string, any>
  ): Promise<Record<string, any>>;

  protected abstract ensureParentDirectory(fullPath: string): Promise<void>;

  protected abstract mapError(error: unknown): StorageError;

  // Utility methods

  /**
   * Resolve a path relative to the base path
   */
  protected resolvePath(inputPath: string): string {
    // Normalize path separators and remove leading/trailing slashes
    const normalizedPath = inputPath.replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
    
    if (!this.config.basePath) {
      return normalizedPath;
    }

    const normalizedBase = this.config.basePath.replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
    return path.join(normalizedBase, normalizedPath).replace(/\\/g, '/');
  }

  /**
   * Merge provided options with defaults
   */
  protected mergeOptions(options?: StorageOptions): Required<StorageOptions> {
    return {
      contentType: 'application/octet-stream',
      metadata: {},
      cacheControl: 'public, max-age=3600',
      isPublic: false,
      ...this.config.defaultOptions,
      ...options
    };
  }

  /**
   * Emit a progress event if enabled
   */
  protected emitProgress(data: ProgressData): void {
    if (this.config.enableProgress) {
      this.emit('progress', data);
    }
  }
} 