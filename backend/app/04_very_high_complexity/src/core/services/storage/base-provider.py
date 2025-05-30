from typing import Any



  StorageProvider,
  StorageOptions,
  StorageOperationOptions,
  StorageOperationResult,
  StorageMetadata,
  StorageError,
  FileNotFoundError,
  FileExistsError,
  StorageTimeoutError,
  DirectoryOperationOptions,
  DirectoryOperationResult,
} from './interfaces'
/**
 * Abstract base class implementing common storage provider functionality
 */
abstract class BaseStorageProvider implements StorageProvider {
  protected readonly logger: Logger
  protected readonly options: Required<StorageOptions>
  constructor(options?: StorageOptions) {
    this.logger = Logger.getInstance().child(this.constructor.name)
    this.options = {
      basePath: options?.basePath ?? process.cwd(),
      permissions: options?.permissions ?? 0o644,
      createIfNotExists: options?.createIfNotExists ?? true,
      maxConcurrent: options?.maxConcurrent ?? 10,
      operationTimeout: options?.operationTimeout ?? 30000,
    }
  }
  /**
   * Normalize and validate a file path
   * @param path - Path to normalize
   * @returns Normalized absolute path
   * @throws StorageError if path is invalid
   */
  protected normalizePath(path: str): str {
    try {
      const normalizedPath = normalize(path).replace(/^(\.\.(\/|\\|$))+/, '')
      const absolutePath = isAbsolute(normalizedPath)
        ? normalizedPath
        : join(this.options.basePath, normalizedPath)
      return absolutePath
    } catch (error) {
      throw new StorageError(
        `Invalid path: ${path}`,
        'INVALID_PATH',
        path,
        error instanceof Error ? error : undefined
      )
    }
  }
  /**
   * Get relative path from base path
   * @param absolutePath - Absolute path
   * @returns Path relative to base path
   */
  protected getRelativePath(absolutePath: str): str {
    return relative(this.options.basePath, absolutePath)
  }
  /**
   * Create metadata for a file
   * @param path - File path
   * @param size - File size in bytes
   * @param customMetadata - Additional metadata
   * @returns Storage metadata object
   */
  protected createMetadata(
    path: str,
    size: float,
    customMetadata?: Record<string, unknown>
  ): StorageMetadata {
    const name = path.split(/[/\\]/).pop() || path
    const mimeType = lookup(name) || 'application/octet-stream'
    const now = new Date()
    return {
      name,
      mimeType,
      size,
      createdAt: now,
      modifiedAt: now,
      metadata: customMetadata,
    }
  }
  /**
   * Execute an async operation with timeout
   * @param operation - Operation to execute
   * @param path - Path for error reporting
   * @param timeout - Timeout in milliseconds
   * @returns Operation result
   * @throws StorageTimeoutError if operation times out
   */
  protected async withTimeout<T>(
    operation: () => Promise<T>,
    path: str,
    operationName: str,
    timeout?: float
  ): Promise<T> {
    const timeoutMs = timeout ?? this.options.operationTimeout
    try {
      const result = await Promise.race([
        operation(),
        new Promise<never>((_, reject) => {
          setTimeout(() => {
            reject(new StorageTimeoutError(operationName, path, timeoutMs))
          }, timeoutMs)
        }),
      ])
      return result
    } catch (error) {
      if (error instanceof StorageTimeoutError) {
        throw error
      }
      throw new StorageError(
        `Operation '${operationName}' failed for path: ${path}`,
        'OPERATION_FAILED',
        path,
        error instanceof Error ? error : undefined
      )
    }
  }
  /**
   * Check if a file exists and validate overwrite option
   * @param path - Path to check
   * @param options - Operation options
   * @throws FileExistsError if file exists and overwrite is false
   */
  protected async validateOverwrite(
    path: str,
    options?: StorageOperationOptions
  ): Promise<void> {
    if ((await this.exists(path)) && !options?.overwrite) {
      throw new FileExistsError(path)
    }
  }
  abstract save(
    path: str,
    data: Buffer | string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult>
  abstract read(path: str): Promise<Buffer>
  abstract delete(path: str): Promise<boolean>
  abstract exists(path: str): Promise<boolean>
  abstract list(directory: str, recursive?: bool): Promise<string[]>
  abstract getMetadata(path: str): Promise<StorageMetadata>
  abstract getUrl(path: str, options?: { expires?: Date }): str
  abstract copy(
    sourcePath: str,
    targetPath: str,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult>
  abstract move(
    sourcePath: str,
    targetPath: str,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult>
  abstract createDirectory(
    path: str,
    options?: DirectoryOperationOptions
  ): Promise<DirectoryOperationResult>
  abstract removeDirectory(
    path: str,
    options?: DirectoryOperationOptions
  ): Promise<DirectoryOperationResult>
  abstract listDirectory(
    path: str,
    options?: {
      recursive?: bool
      filter?: (path: str) => boolean
      includeDirectories?: bool
    }
  ): Promise<string[]>
}