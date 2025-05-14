import { promises as fs } from 'fs';
import { join, dirname } from 'path';
import { BaseStorageProvider } from './base-provider';
import {
  StorageOperationOptions,
  StorageOperationResult,
  StorageMetadata,
  FileNotFoundError,
  StorageError,
  DirectoryOperationOptions,
  DirectoryOperationResult,
} from './interfaces';
import { mkdir, rm, readdir } from 'fs/promises';
import { lookup } from 'mime-types';

/**
 * File system storage provider implementation
 */
export class FileSystemStorageProvider extends BaseStorageProvider {
  /**
   * Initialize the file system provider and ensure base path exists
   */
  constructor(options?: { basePath?: string; permissions?: number }) {
    super(options);
    this.ensureBasePathExists();
  }

  /**
   * Create the base directory if it doesn't exist
   */
  private async ensureBasePathExists(): Promise<void> {
    try {
      await fs.mkdir(this.options.basePath, { recursive: true, mode: this.options.permissions });
    } catch (error) {
      throw new StorageError(
        `Failed to create base directory: ${this.options.basePath}`,
        'BASE_DIR_CREATE_FAILED',
        this.options.basePath,
        error instanceof Error ? error : undefined
      );
    }
  }

  /**
   * Ensure a directory exists for a given file path
   */
  private async ensureDirectoryExists(filePath: string): Promise<void> {
    const dir = dirname(filePath);
    try {
      await fs.mkdir(dir, { recursive: true, mode: this.options.permissions });
    } catch (error) {
      throw new StorageError(
        `Failed to create directory: ${dir}`,
        'DIR_CREATE_FAILED',
        dir,
        error instanceof Error ? error : undefined
      );
    }
  }

  /**
   * Save data to a file
   */
  async save(
    path: string,
    data: Buffer | string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    const normalizedPath = this.normalizePath(path);

    await this.withTimeout(
      async () => {
        // Validate overwrite
        await this.validateOverwrite(normalizedPath, options);

        // Ensure directory exists
        await this.ensureDirectoryExists(normalizedPath);

        // Write file
        try {
          const buffer = Buffer.isBuffer(data) ? data : Buffer.from(data);
          await fs.writeFile(normalizedPath, buffer, {
            mode: this.options.permissions,
            flag: options?.overwrite ? 'w' : 'wx',
          });
        } catch (error) {
          throw new StorageError(
            `Failed to write file: ${path}`,
            'FILE_WRITE_FAILED',
            path,
            error instanceof Error ? error : undefined
          );
        }
      },
      normalizedPath,
      'save',
      options?.timeout
    );

    // Get metadata for the saved file
    const metadata = await this.getMetadata(path);

    return {
      path: this.getRelativePath(normalizedPath),
      metadata,
    };
  }

  /**
   * Read file contents
   */
  async read(path: string): Promise<Buffer> {
    const normalizedPath = this.normalizePath(path);

    return this.withTimeout(
      async () => {
        try {
          return await fs.readFile(normalizedPath);
        } catch (error) {
          if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
            throw new FileNotFoundError(path);
          }
          throw new StorageError(
            `Failed to read file: ${path}`,
            'FILE_READ_FAILED',
            path,
            error instanceof Error ? error : undefined
          );
        }
      },
      normalizedPath,
      'read'
    );
  }

  /**
   * Delete a file
   */
  async delete(path: string): Promise<boolean> {
    const normalizedPath = this.normalizePath(path);

    return this.withTimeout(
      async () => {
        try {
          await fs.unlink(normalizedPath);
          return true;
        } catch (error) {
          if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
            return false;
          }
          throw new StorageError(
            `Failed to delete file: ${path}`,
            'FILE_DELETE_FAILED',
            path,
            error instanceof Error ? error : undefined
          );
        }
      },
      normalizedPath,
      'delete'
    );
  }

  /**
   * Check if a file exists
   */
  async exists(path: string): Promise<boolean> {
    const normalizedPath = this.normalizePath(path);

    try {
      await fs.access(normalizedPath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * List files in a directory
   */
  async list(directory: string, recursive = false): Promise<string[]> {
    const normalizedPath = this.normalizePath(directory);

    return this.withTimeout(
      async () => {
        try {
          if (recursive) {
            return this.listRecursive(normalizedPath);
          }

          const entries = await fs.readdir(normalizedPath);
          return entries.map(entry => join(directory, entry));
        } catch (error) {
          if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
            return [];
          }
          throw new StorageError(
            `Failed to list directory: ${directory}`,
            'DIR_LIST_FAILED',
            directory,
            error instanceof Error ? error : undefined
          );
        }
      },
      normalizedPath,
      'list'
    );
  }

  /**
   * Recursively list all files in a directory
   */
  private async listRecursive(directory: string): Promise<string[]> {
    const result: string[] = [];

    try {
      const entries = await fs.readdir(directory, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = join(directory, entry.name);
        if (entry.isDirectory()) {
          const subEntries = await this.listRecursive(fullPath);
          result.push(...subEntries);
        } else {
          result.push(this.getRelativePath(fullPath));
        }
      }
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
        throw new StorageError(
          `Failed to list directory recursively: ${directory}`,
          'DIR_LIST_FAILED',
          directory,
          error instanceof Error ? error : undefined
        );
      }
    }

    return result;
  }

  /**
   * Get file metadata
   */
  async getMetadata(path: string): Promise<StorageMetadata> {
    const normalizedPath = this.normalizePath(path);

    return this.withTimeout(
      async () => {
        try {
          const stats = await fs.stat(normalizedPath);
          return this.createMetadata(path, stats.size);
        } catch (error) {
          if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
            throw new FileNotFoundError(path);
          }
          throw new StorageError(
            `Failed to get file metadata: ${path}`,
            'METADATA_FAILED',
            path,
            error instanceof Error ? error : undefined
          );
        }
      },
      normalizedPath,
      'getMetadata'
    );
  }

  /**
   * Get a URL for accessing the file
   */
  getUrl(path: string): string {
    const normalizedPath = this.normalizePath(path);
    return `file://${normalizedPath}`;
  }

  /**
   * Copy a file to a new location
   */
  async copy(
    sourcePath: string,
    targetPath: string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    const normalizedSource = this.normalizePath(sourcePath);
    const normalizedTarget = this.normalizePath(targetPath);

    await this.withTimeout(
      async () => {
        // Check source exists
        if (!(await this.exists(sourcePath))) {
          throw new FileNotFoundError(sourcePath);
        }

        // Validate overwrite
        await this.validateOverwrite(normalizedTarget, options);

        // Ensure target directory exists
        await this.ensureDirectoryExists(normalizedTarget);

        // Copy file
        try {
          await fs.copyFile(normalizedSource, normalizedTarget);
        } catch (error) {
          throw new StorageError(
            `Failed to copy file from ${sourcePath} to ${targetPath}`,
            'FILE_COPY_FAILED',
            targetPath,
            error instanceof Error ? error : undefined
          );
        }
      },
      normalizedTarget,
      'copy',
      options?.timeout
    );

    // Get metadata for the copied file
    const metadata = await this.getMetadata(targetPath);

    return {
      path: this.getRelativePath(normalizedTarget),
      metadata,
    };
  }

  /**
   * Move a file to a new location
   */
  async move(
    sourcePath: string,
    targetPath: string,
    options?: StorageOperationOptions
  ): Promise<StorageOperationResult> {
    const normalizedSource = this.normalizePath(sourcePath);
    const normalizedTarget = this.normalizePath(targetPath);

    await this.withTimeout(
      async () => {
        // Check source exists
        if (!(await this.exists(sourcePath))) {
          throw new FileNotFoundError(sourcePath);
        }

        // Validate overwrite
        await this.validateOverwrite(normalizedTarget, options);

        // Ensure target directory exists
        await this.ensureDirectoryExists(normalizedTarget);

        // Move file
        try {
          await fs.rename(normalizedSource, normalizedTarget);
        } catch (error) {
          // If rename fails (e.g., across devices), fallback to copy + delete
          if ((error as NodeJS.ErrnoException).code === 'EXDEV') {
            await fs.copyFile(normalizedSource, normalizedTarget);
            await fs.unlink(normalizedSource);
          } else {
            throw new StorageError(
              `Failed to move file from ${sourcePath} to ${targetPath}`,
              'FILE_MOVE_FAILED',
              targetPath,
              error instanceof Error ? error : undefined
            );
          }
        }
      },
      normalizedTarget,
      'move',
      options?.timeout
    );

    // Get metadata for the moved file
    const metadata = await this.getMetadata(targetPath);

    return {
      path: this.getRelativePath(normalizedTarget),
      metadata,
    };
  }

  private resolvePath(path: string): string {
    return join(this.options.basePath, path);
  }

  async createDirectory(
    path: string,
    options: DirectoryOperationOptions = {}
  ): Promise<DirectoryOperationResult> {
    const fullPath = this.resolvePath(path);
    
    try {
      await mkdir(fullPath, { 
        recursive: options.createParents ?? true 
      });
      
      return {
        path,
        success: true
      };
    } catch (error: unknown) {
      if (error instanceof Error) {
        return {
          path,
          success: false,
          error: new StorageError(`Failed to create directory: ${error.message}`, 'DIR_CREATE_FAILED', path, error)
        };
      }
      return {
        path,
        success: false,
        error: new StorageError('Failed to create directory: Unknown error', 'DIR_CREATE_FAILED', path)
      };
    }
  }

  async removeDirectory(
    path: string,
    options: DirectoryOperationOptions = {}
  ): Promise<DirectoryOperationResult> {
    const fullPath = this.resolvePath(path);
    
    try {
      await rm(fullPath, { 
        recursive: !options.failIfNotEmpty,
        force: true
      });
      
      return {
        path,
        success: true
      };
    } catch (error: unknown) {
      if (error instanceof Error && 'code' in error && error.code === 'ENOENT') {
        return {
          path,
          success: false,
          error: new FileNotFoundError(path)
        };
      }
      
      if (error instanceof Error) {
        return {
          path,
          success: false,
          error: new StorageError(`Failed to remove directory: ${error.message}`, 'DIR_REMOVE_FAILED', path, error)
        };
      }

      return {
        path,
        success: false,
        error: new StorageError('Failed to remove directory: Unknown error', 'DIR_REMOVE_FAILED', path)
      };
    }
  }

  async listDirectory(
    path: string,
    options: {
      recursive?: boolean;
      filter?: (path: string) => boolean;
      includeDirectories?: boolean;
    } = {}
  ): Promise<string[]> {
    const fullPath = this.resolvePath(path);
    const { recursive = false, filter, includeDirectories = true } = options;
    
    try {
      const entries = await readdir(fullPath, { withFileTypes: true });
      let results: string[] = [];
      
      for (const entry of entries) {
        const relativePath = join(path, entry.name);
        
        if (entry.isDirectory()) {
          if (includeDirectories) {
            results.push(relativePath);
          }
          
          if (recursive) {
            const subEntries = await this.listDirectory(relativePath, options);
            results = results.concat(subEntries);
          }
        } else if (entry.isFile()) {
          if (!filter || filter(relativePath)) {
            results.push(relativePath);
          }
        }
      }
      
      return results;
    } catch (error: unknown) {
      if (error instanceof Error && 'code' in error && error.code === 'ENOENT') {
        throw new FileNotFoundError(path);
      }
      if (error instanceof Error) {
        throw new StorageError(`Failed to list directory: ${error.message}`, 'DIR_LIST_FAILED', path, error);
      }
      throw new StorageError('Failed to list directory: Unknown error', 'DIR_LIST_FAILED', path);
    }
  }
}
