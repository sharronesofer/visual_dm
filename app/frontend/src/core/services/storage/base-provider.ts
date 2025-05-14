import { join, normalize, relative, isAbsolute } from 'path';
import { lookup } from 'mime-types';
import {
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
} from './interfaces';
import { Logger } from '../../utils/logger';

/**
 * Abstract base class implementing common storage provider functionality
 */
export abstract class BaseStorageProvider implements StorageProvider {
  protected readonly logger: Logger;
  protected readonly options: Required<StorageOptions>;

  constructor(options?: StorageOptions) {
    this.logger = Logger.getInstance().child(this.constructor.name);
    this.options = {
      basePath: options?.basePath ?? process.cwd(),
      permissions: options?.permissions ?? 0o644,
      createIfNotExists: options?.createIfNotExists ?? true,
      maxConcurrent: options?.maxConcurrent ?? 10,
      operationTimeout: options?.operationTimeout ?? 30000,
    };
  }

  /**
   * Normalize and validate a file path
   * @param path - Path to normalize
   * @returns Normalized absolute path
   * @throws StorageError if path is invalid
   */
  protected normalizePath(path: string): string {
    try {
      // Remove any parent directory references for security
      const normalizedPath = normalize(path).replace(/^(\.\.(\/|\\|$))+/, '');

      // Convert to absolute path if relative
      const absolutePath = isAbsolute(normalizedPath)
        ? normalizedPath
        : join(this.options.basePath, normalizedPath);

      return absolutePath;
    } catch (error) {
      throw new StorageError(
        `Invalid path: ${path}`,
        'INVALID_PATH',
        path,
        error instanceof Error ? error : undefined
      );
    }
  }

  /**
   * Get relative path from base path
   * @param absolutePath - Absolute path
   * @returns Path relative to base path
   */
  protected getRelativePath(absolutePath: string): string {
    return relative(this.options.basePath, absolutePath);
  }

  /**
   * Create metadata for a file
   * @param path - File path
   * @param size - File size in bytes
   * @param customMetadata - Additional metadata
   * @returns Storage metadata object
   */
  protected createMetadata(
    path: string,
    size: number,
    customMetadata?: Record<string, unknown>
  ): StorageMetadata {
    const name = path.split(/[/\\]/).pop() || path;
    const mimeType = lookup(name) || 'application/octet-stream';
    const now = new Date();

    return {
      name,
      mimeType,
      size,
      createdAt: now,
      modifiedAt: now,
      metadata: customMetadata,
    };
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
    path: string,
    operationName: string,
    timeout?: number
  ): Promise<T> {
    const timeoutMs = timeout ?? this.options.operationTimeout;

    try {
      const result = await Promise.race([
        operation(),
        new Promise<never>((_, reject) => {
          setTimeout(() => {
            reject(new StorageTimeoutError(operationName, path, timeoutMs));
          }, timeoutMs);
        }),
      ]);

      return result;
    } catch (error) {
      if (error instanceof StorageTimeoutError) {
        throw error;
      }
      throw new StorageError(
        `Operation '${operationName}' failed for path: ${path}`,
        'OPERATION_FAILED',
        path,
        error instanceof Error ? error : undefined
      );
    }
  }

  /**
   * Check if a file exists and validate overwrite option
   * @param path - Path to check
   * @param options - Operation options
   * @throws FileExistsError if file exists and overwrite is false
   */
  protected async validateOverwrite(
    path: string,
    options?: StorageOperationOptions
  ): Promise<void> {
    if ((await this.exists(path)) && !options?.overwrite) {
      throw new FileExistsError(path);
    }
  }

  // Abstract methods that must be implemented by concrete providers

  abstract save(
    path: string,
    data: Buffer | string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult>;
  abstract read(path: string): Promise<Buffer>;
  abstract delete(path: string): Promise<boolean>;
  abstract exists(path: string): Promise<boolean>;
  abstract list(directory: string, recursive?: boolean): Promise<string[]>;
  abstract getMetadata(path: string): Promise<StorageMetadata>;
  abstract getUrl(path: string, options?: { expires?: Date }): string;
  abstract copy(
    sourcePath: string,
    targetPath: string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult>;
  abstract move(
    sourcePath: string,
    targetPath: string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult>;

  abstract createDirectory(
    path: string,
    options?: DirectoryOperationOptions
  ): Promise<DirectoryOperationResult>;

  abstract removeDirectory(
    path: string,
    options?: DirectoryOperationOptions
  ): Promise<DirectoryOperationResult>;

  abstract listDirectory(
    path: string,
    options?: {
      recursive?: boolean;
      filter?: (path: string) => boolean;
      includeDirectories?: boolean;
    }
  ): Promise<string[]>;
}
