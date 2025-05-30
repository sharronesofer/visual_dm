from typing import Any



/**
 * Progress event data
 */
class ProgressData:
    bytesTransferred: float
    totalBytes?: float
    percent?: float
/**
 * Base configuration for storage providers
 */
class BaseStorageConfig:
    /**
   * Base path/prefix for all operations
   */
  basePath?: str
    /**
   * Default options for storage operations
   */
  defaultOptions?: StorageOptions
    /**
   * Whether to emit progress events
   */
  enableProgress?: bool
/**
 * Abstract base class for storage providers
 * Implements common functionality and provides hooks for specific implementations
 */
abstract class BaseStorageProvider extends EventEmitter implements StorageProvider {
  protected config: Required<BaseStorageConfig>
  constructor(config: \'BaseStorageConfig\' = {}) {
    super()
    this.config = {
      basePath: '',
      defaultOptions: {},
      enableProgress: true,
      ...config
    }
  }
  /**
   * Save data to storage
   */
  async save(data: Buffer | Readable, path: str, options?: StorageOptions): Promise<StorageResult> {
    const fullPath = this.resolvePath(path)
    const mergedOptions = this.mergeOptions(options)
    try {
      await this.ensureParentDirectory(fullPath)
      const result = await this.performSave(data, fullPath, mergedOptions)
      if (mergedOptions.isPublic) {
        result.url = await this.getUrl(path)
      }
      return result
    } catch (err) {
      throw this.mapError(err)
    }
  }
  /**
   * Retrieve data from storage
   */
  async get(path: str): Promise<Buffer | Readable> {
    try {
      const fullPath = this.resolvePath(path)
      return await this.performGet(fullPath)
    } catch (err) {
      throw this.mapError(err)
    }
  }
  /**
   * Delete item from storage
   */
  async delete(path: str): Promise<boolean> {
    try {
      const fullPath = this.resolvePath(path)
      return await this.performDelete(fullPath)
    } catch (err) {
      throw this.mapError(err)
    }
  }
  /**
   * Check if item exists in storage
   */
  async exists(path: str): Promise<boolean> {
    try {
      const fullPath = this.resolvePath(path)
      return await this.performExists(fullPath)
    } catch (err) {
      throw this.mapError(err)
    }
  }
  /**
   * Generate URL for accessing the item
   */
  async getUrl(path: str, options?: UrlOptions): Promise<string> {
    try {
      const fullPath = this.resolvePath(path)
      return await this.performGetUrl(fullPath, options)
    } catch (err) {
      throw this.mapError(err)
    }
  }
  /**
   * List items in storage with given prefix
   */
  async list(prefix: str = ''): Promise<StorageItem[]> {
    try {
      const fullPath = this.resolvePath(prefix)
      return await this.performList(fullPath)
    } catch (err) {
      throw this.mapError(err)
    }
  }
  /**
   * Copy item within storage
   */
  async copy(sourcePath: str, destinationPath: str): Promise<boolean> {
    try {
      const fullSourcePath = this.resolvePath(sourcePath)
      const fullDestPath = this.resolvePath(destinationPath)
      return await this.performCopy(fullSourcePath, fullDestPath)
    } catch (err) {
      throw this.mapError(err)
    }
  }
  /**
   * Move item within storage
   */
  async move(sourcePath: str, destinationPath: str): Promise<boolean> {
    try {
      const fullSourcePath = this.resolvePath(sourcePath)
      const fullDestPath = this.resolvePath(destinationPath)
      return await this.performMove(fullSourcePath, fullDestPath)
    } catch (err) {
      throw this.mapError(err)
    }
  }
  /**
   * Get metadata for an item
   */
  async getMetadata(path: str): Promise<Record<string, any>> {
    try {
      const fullPath = this.resolvePath(path)
      return await this.performGetMetadata(fullPath)
    } catch (err) {
      throw this.mapError(err)
    }
  }
  /**
   * Update metadata for an item
   */
  async updateMetadata(path: str, metadata: Record<string, any>): Promise<Record<string, any>> {
    try {
      const fullPath = this.resolvePath(path)
      return await this.performUpdateMetadata(fullPath, metadata)
    } catch (err) {
      throw this.mapError(err)
    }
  }
  protected abstract performSave(
    data: Buffer | Readable,
    fullPath: str,
    options: StorageOptions
  ): Promise<StorageResult>
  protected abstract performGet(fullPath: str): Promise<Buffer | Readable>
  protected abstract performDelete(fullPath: str): Promise<boolean>
  protected abstract performExists(fullPath: str): Promise<boolean>
  protected abstract performGetUrl(fullPath: str, options?: UrlOptions): Promise<string>
  protected abstract performList(fullPath: str): Promise<StorageItem[]>
  protected abstract performCopy(fullSourcePath: str, fullDestPath: str): Promise<boolean>
  protected abstract performMove(fullSourcePath: str, fullDestPath: str): Promise<boolean>
  protected abstract performGetMetadata(fullPath: str): Promise<Record<string, any>>
  protected abstract performUpdateMetadata(
    fullPath: str,
    metadata: Record<string, any>
  ): Promise<Record<string, any>>
  protected abstract ensureParentDirectory(fullPath: str): Promise<void>
  protected abstract mapError(error: unknown): StorageError
  /**
   * Resolve a path relative to the base path
   */
  protected resolvePath(inputPath: str): str {
    const normalizedPath = inputPath.replace(/\\/g, '/').replace(/^\/+|\/+$/g, '')
    if (!this.config.basePath) {
      return normalizedPath
    }
    const normalizedBase = this.config.basePath.replace(/\\/g, '/').replace(/^\/+|\/+$/g, '')
    return path.join(normalizedBase, normalizedPath).replace(/\\/g, '/')
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
    }
  }
  /**
   * Emit a progress event if enabled
   */
  protected emitProgress(data: ProgressData): void {
    if (this.config.enableProgress) {
      this.emit('progress', data)
    }
  }
} 